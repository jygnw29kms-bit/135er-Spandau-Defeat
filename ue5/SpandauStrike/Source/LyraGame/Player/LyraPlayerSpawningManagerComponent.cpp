// Copyright Epic Games, Inc. All Rights Reserved.

#include "LyraPlayerSpawningManagerComponent.h"
#include "GameFramework/PlayerState.h"
#include "GameFramework/PlayerController.h"
#include "Camera/PlayerCameraManager.h"
#include "Components/CapsuleComponent.h"
#include "Components/PrimitiveComponent.h"
#include "GameFramework/Character.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "Engine/World.h"
#include "Misc/CommandLine.h"
#include "Misc/Parse.h"
#include "EngineUtils.h"
#include "Engine/PlayerStartPIE.h"
#include "LyraPlayerStart.h"
#include "Player/LyraPlayerState.h"
#include "SpandauStrike/SpandauCaptureDirector.h"

#include UE_INLINE_GENERATED_CPP_BY_NAME(LyraPlayerSpawningManagerComponent)

DEFINE_LOG_CATEGORY_STATIC(LogPlayerSpawning, Log, All);

ULyraPlayerSpawningManagerComponent::ULyraPlayerSpawningManagerComponent(const FObjectInitializer& ObjectInitializer)
: Super(ObjectInitializer)
{
	SetIsReplicatedByDefault(false);
	bAutoRegister = true;
	bAutoActivate = true;
	bWantsInitializeComponent = true;
	PrimaryComponentTick.TickGroup = TG_PrePhysics;
	PrimaryComponentTick.bCanEverTick = true;
	PrimaryComponentTick.bAllowTickOnDedicatedServer = true;
	PrimaryComponentTick.bStartWithTickEnabled = false;
}

void ULyraPlayerSpawningManagerComponent::InitializeComponent()
{
	Super::InitializeComponent();

	// Only enable sampling when explicitly requested. Never alter gameplay physics.
	SetComponentTickEnabled(FParse::Param(FCommandLine::Get(), TEXT("SpandauGroundProbe")));

	FWorldDelegates::LevelAddedToWorld.AddUObject(this, &ThisClass::OnLevelAdded);

	UWorld* World = GetWorld();
	World->AddOnActorSpawnedHandler(FOnActorSpawned::FDelegate::CreateUObject(this, &ThisClass::HandleOnActorSpawned));

	for (TActorIterator<ALyraPlayerStart> It(World); It; ++It)
	{
		if (ALyraPlayerStart* PlayerStart = *It)
		{
			CachedPlayerStarts.Add(PlayerStart);
		}
	}
}

void ULyraPlayerSpawningManagerComponent::OnLevelAdded(ULevel* InLevel, UWorld* InWorld)
{
	if (InWorld == GetWorld())
	{
		for (AActor* Actor : InLevel->Actors)
		{
			if (ALyraPlayerStart* PlayerStart = Cast<ALyraPlayerStart>(Actor))
			{
				ensure(!CachedPlayerStarts.Contains(PlayerStart));
				CachedPlayerStarts.Add(PlayerStart);
			}
		}
	}
}

void ULyraPlayerSpawningManagerComponent::HandleOnActorSpawned(AActor* SpawnedActor)
{
	if (ALyraPlayerStart* PlayerStart = Cast<ALyraPlayerStart>(SpawnedActor))
	{
		CachedPlayerStarts.Add(PlayerStart);
	}
}

// ALyraGameMode Proxied Calls - Need to handle when someone chooses
// to restart a player the normal way in the engine.
//======================================================================

AActor* ULyraPlayerSpawningManagerComponent::ChoosePlayerStart(AController* Player)
{
	if (Player)
	{
#if WITH_EDITOR
		if (APlayerStart* PlayerStart = FindPlayFromHereStart(Player))
		{
			return PlayerStart;
		}
#endif

		TArray<ALyraPlayerStart*> StarterPoints;
		for (auto StartIt = CachedPlayerStarts.CreateIterator(); StartIt; ++StartIt)
		{
			if (ALyraPlayerStart* Start = (*StartIt).Get())
			{
				StarterPoints.Add(Start);
			}
			else
			{
				StartIt.RemoveCurrent();
			}
		}

		if (APlayerState* PlayerState = Player->GetPlayerState<APlayerState>())
		{
			// start dedicated spectators at any random starting location, but they do not claim it
			if (PlayerState->IsOnlyASpectator())
			{
				if (!StarterPoints.IsEmpty())
				{
					return StarterPoints[FMath::RandRange(0, StarterPoints.Num() - 1)];
				}

				return nullptr;
			}
		}

		// Spandau Strike Capture: prefer team/sector-tagged front spawns.
		TArray<ALyraPlayerStart*> EffectiveStartPoints = StarterPoints;
		bool bUsingSpandauFrontStarts = false;
		for (TActorIterator<ASpandauCaptureDirector> It(GetWorld()); It; ++It)
		{
			ASpandauCaptureDirector* Director = *It;
			if (!Director || !Director->AreTeamsResolved())
			{
				continue;
			}

			const ALyraPlayerState* LyraPS = Player->GetPlayerState<ALyraPlayerState>();
			const int32 TeamId = LyraPS ? LyraPS->GetTeamId() : INDEX_NONE;
			const bool bAttacker = TeamId == Director->GetAttackerTeamId();
			const bool bDefender = TeamId == Director->GetDefenderTeamId();
			if (!bAttacker && !bDefender)
			{
				break;
			}

			const FName RoleTag = bAttacker ? FName(TEXT("SSSpawn.Attacker")) : FName(TEXT("SSSpawn.Defender"));
			const FName SectorTag(*FString::Printf(TEXT("SSSpawn.Sector.%d"), Director->GetActiveSector()));
			TArray<ALyraPlayerStart*> FrontStarts;
			for (ALyraPlayerStart* Start : StarterPoints)
			{
				if (Start && Start->Tags.Contains(RoleTag) && Start->Tags.Contains(SectorTag))
				{
					FrontStarts.Add(Start);
				}
			}

			if (!FrontStarts.IsEmpty())
			{
				EffectiveStartPoints = MoveTemp(FrontStarts);
				bUsingSpandauFrontStarts = true;
				UE_LOG(LogPlayerSpawning, Log, TEXT("Spandau front spawn candidates: team=%d sector=%d count=%d"), TeamId, Director->GetActiveSector(), EffectiveStartPoints.Num());
			}
			break;
		}

		AActor* PlayerStart = nullptr;

		if (bUsingSpandauFrontStarts)
		{
			PlayerStart = GetFirstRandomUnoccupiedPlayerStart(Player, EffectiveStartPoints, true);
			if (!PlayerStart)
			{
				UE_LOG(LogPlayerSpawning, Warning, TEXT("Spandau front spawn safety rejected all candidates; falling back to base starts: candidates=%d"), EffectiveStartPoints.Num());
				EffectiveStartPoints = StarterPoints;
			}
		}

		if (!PlayerStart)
		{
			PlayerStart = OnChoosePlayerStart(Player, EffectiveStartPoints);
		}

		if (!PlayerStart)
		{
			PlayerStart = GetFirstRandomUnoccupiedPlayerStart(Player, EffectiveStartPoints);
		}

		if (ALyraPlayerStart* LyraStart = Cast<ALyraPlayerStart>(PlayerStart))
		{
			LyraStart->TryClaim(Player);
		}

		return PlayerStart;
	}

	return nullptr;
}

#if WITH_EDITOR
APlayerStart* ULyraPlayerSpawningManagerComponent::FindPlayFromHereStart(AController* Player)
{
	// Only 'Play From Here' for a player controller, bots etc. should all spawn from normal spawn points.
	if (Player->IsA<APlayerController>())
	{
		if (UWorld* World = GetWorld())
		{
			for (TActorIterator<APlayerStart> It(World); It; ++It)
			{
				if (APlayerStart* PlayerStart = *It)
				{
					if (PlayerStart->IsA<APlayerStartPIE>())
					{
						// Always prefer the first "Play from Here" PlayerStart, if we find one while in PIE mode
						return PlayerStart;
					}
				}
			}
		}
	}

	return nullptr;
}
#endif

bool ULyraPlayerSpawningManagerComponent::ControllerCanRestart(AController* Player)
{
	bool bCanRestart = true;

	// TODO Can they restart?

	return bCanRestart;
}

void ULyraPlayerSpawningManagerComponent::FinishRestartPlayer(AController* NewPlayer, const FRotator& StartRotation)
{
	OnFinishRestartPlayer(NewPlayer, StartRotation);
	K2_OnFinishRestartPlayer(NewPlayer, StartRotation);

	if (NewPlayer)
	{
		const APawn* Pawn = NewPlayer->GetPawn();
		const ALyraPlayerState* PlayerPS = NewPlayer->GetPlayerState<ALyraPlayerState>();
		const FVector Location = Pawn ? Pawn->GetActorLocation() : FVector::ZeroVector;
		const FRotator ControlRotation = NewPlayer->GetControlRotation();
		FVector CameraLocation = FVector::ZeroVector;
		FRotator CameraRotation = FRotator::ZeroRotator;
		if (const APlayerController* PC = Cast<APlayerController>(NewPlayer))
		{
			if (PC->PlayerCameraManager)
			{
				CameraLocation = PC->PlayerCameraManager->GetCameraLocation();
				CameraRotation = PC->PlayerCameraManager->GetCameraRotation();
			}
		}
		UE_LOG(LogPlayerSpawning, Log, TEXT("Spandau restart finished: controller=%s human=%d team=%d pawn=%s loc=(%.0f,%.0f,%.0f) startRot=(%.1f,%.1f,%.1f) controlRot=(%.1f,%.1f,%.1f) camLoc=(%.0f,%.0f,%.0f) camRot=(%.1f,%.1f,%.1f)"),
			*GetNameSafe(NewPlayer), NewPlayer->IsPlayerController() ? 1 : 0, PlayerPS ? PlayerPS->GetTeamId() : INDEX_NONE,
			*GetNameSafe(Pawn), Location.X, Location.Y, Location.Z,
			StartRotation.Pitch, StartRotation.Yaw, StartRotation.Roll,
			ControlRotation.Pitch, ControlRotation.Yaw, ControlRotation.Roll,
			CameraLocation.X, CameraLocation.Y, CameraLocation.Z,
			CameraRotation.Pitch, CameraRotation.Yaw, CameraRotation.Roll);
	}
}

//================================================================

void ULyraPlayerSpawningManagerComponent::TickComponent(float DeltaTime, enum ELevelTick TickType, FActorComponentTickFunction* ThisTickFunction)
{
	Super::TickComponent(DeltaTime, TickType, ThisTickFunction);
	if (!FParse::Param(FCommandLine::Get(), TEXT("SpandauGroundProbe"))) return;
	UWorld* World = GetWorld();
	if (!World || !World->IsGameWorld()) return;
	GroundProbeElapsedSeconds += DeltaTime;
	if (GroundProbeElapsedSeconds - GroundProbeLastSampleSeconds < 5.0f) return;
	GroundProbeLastSampleSeconds = GroundProbeElapsedSeconds;
	int32 Sampled = 0;
	int32 Failed = 0;
	for (FConstControllerIterator It = World->GetControllerIterator(); It; ++It)
	{
		AController* Controller = It->Get();
		ACharacter* Character = Controller ? Cast<ACharacter>(Controller->GetPawn()) : nullptr;
		if (!Character) continue;
		++Sampled;
		const FVector Center = Character->GetActorLocation();
		const UCapsuleComponent* Capsule = Character->GetCapsuleComponent();
		const float HalfHeight = Capsule ? Capsule->GetScaledCapsuleHalfHeight() : 0.0f;
		const FVector Feet = Center - FVector(0, 0, HalfHeight);
		FCollisionQueryParams Params(SCENE_QUERY_STAT(SpandauGroundProbe), false, Character);
		FHitResult Hit;
		const bool bHit = World->LineTraceSingleByChannel(Hit, Center + FVector(0, 0, 30.0f), Center - FVector(0, 0, 10000.0f), ECC_Visibility, Params);
		const float FootGap = bHit ? Feet.Z - Hit.ImpactPoint.Z : 999999.0f;
		const UCharacterMovementComponent* Movement = Character->GetCharacterMovement();
		const bool bFalling = Movement && Movement->IsFalling();
		const bool bFail = !bHit || FootGap < -40.0f || FootGap > 250.0f || (bFalling && GroundProbeElapsedSeconds > 10.0f);
		Failed += bFail ? 1 : 0;
		UE_LOG(LogPlayerSpawning, Log, TEXT("Spandau ground probe: t=%.1f pawn=%s human=%d centerZ=%.1f feetZ=%.1f hit=%d groundZ=%.1f gap=%.1f falling=%d hitActor=%s result=%s"),
			GroundProbeElapsedSeconds, *GetNameSafe(Character), Controller->IsPlayerController() ? 1 : 0,
			Center.Z, Feet.Z, bHit ? 1 : 0, bHit ? Hit.ImpactPoint.Z : 0.0f, FootGap, bFalling ? 1 : 0,
			bHit ? *GetNameSafe(Hit.GetActor()) : TEXT("None"), bFail ? TEXT("FAIL") : TEXT("OK"));
		if (bHit && (bFail || GroundProbeElapsedSeconds < 1.0f))
		{
			const UPrimitiveComponent* HitComp = Hit.GetComponent();
			UE_LOG(LogPlayerSpawning, Warning, TEXT("Spandau ground collision detail: pawn=%s actor=%s comp=%s profile=%s enabled=%d pawnResponse=%d blockingHit=%d"),
				*GetNameSafe(Character), *GetNameSafe(Hit.GetActor()), *GetNameSafe(HitComp),
				HitComp ? *HitComp->GetCollisionProfileName().ToString() : TEXT("None"),
				HitComp ? int32(HitComp->GetCollisionEnabled()) : -1,
				HitComp ? int32(HitComp->GetCollisionResponseToChannel(ECC_Pawn)) : -1,
				Hit.bBlockingHit ? 1 : 0);
		}
	}
	UE_LOG(LogPlayerSpawning, Log, TEXT("Spandau ground probe summary: t=%.1f sampled=%d failed=%d"), GroundProbeElapsedSeconds, Sampled, Failed);
}

APlayerStart* ULyraPlayerSpawningManagerComponent::GetFirstRandomUnoccupiedPlayerStart(AController* Controller, const TArray<ALyraPlayerStart*>& StartPoints, bool bRequireSpandauSafeStart) const
{
	if (Controller)
	{
		TArray<ALyraPlayerStart*> UnOccupiedStartPoints;
		TArray<ALyraPlayerStart*> OccupiedStartPoints;

		for (ALyraPlayerStart* StartPoint : StartPoints)
		{
			ELyraPlayerStartLocationOccupancy State = StartPoint->GetLocationOccupancy(Controller);

			switch (State)
			{
				case ELyraPlayerStartLocationOccupancy::Empty:
					UnOccupiedStartPoints.Add(StartPoint);
					break;
				case ELyraPlayerStartLocationOccupancy::Partial:
					OccupiedStartPoints.Add(StartPoint);
					break;

			}
		}

		ASpandauCaptureDirector* CaptureDirector = nullptr;
		if (UWorld* World = GetWorld())
		{
			for (TActorIterator<ASpandauCaptureDirector> It(World); It; ++It)
			{
				CaptureDirector = *It;
				break;
			}
		}

		if (CaptureDirector && CaptureDirector->AreTeamsResolved())
		{
			const ALyraPlayerState* PlayerPS = Controller->GetPlayerState<ALyraPlayerState>();
			const int32 PlayerTeamId = PlayerPS ? PlayerPS->GetTeamId() : INDEX_NONE;
			const float HardEnemyRadiusSq = FMath::Square(1200.0f);
			const float HardLosRadiusSq = FMath::Square(6000.0f);

			auto ChooseSafest = [this, Controller, PlayerTeamId, HardEnemyRadiusSq, HardLosRadiusSq, CaptureDirector](const TArray<ALyraPlayerStart*>& Candidates) -> ALyraPlayerStart*
			{
				ALyraPlayerStart* BestStart = nullptr;
				float BestScore = -TNumericLimits<float>::Max();
				float BestHeat = 0.0f;
				float BestEnemyDistance = 0.0f;
				int32 RejectNear = 0;
				int32 RejectLos = 0;
				UWorld* World = GetWorld();
				if (!World || PlayerTeamId == INDEX_NONE)
				{
					return nullptr;
				}

				for (ALyraPlayerStart* Start : Candidates)
				{
					if (!Start) continue;
					bool bUnsafe = false;
					float MinEnemyDistSq = TNumericLimits<float>::Max();
					for (FConstControllerIterator It = World->GetControllerIterator(); It; ++It)
					{
						AController* Other = It->Get();
						if (!Other || Other == Controller || !Other->GetPawn()) continue;
						const ALyraPlayerState* OtherPS = Other->GetPlayerState<ALyraPlayerState>();
						const int32 OtherTeamId = OtherPS ? OtherPS->GetTeamId() : INDEX_NONE;
						if (OtherTeamId == INDEX_NONE || OtherTeamId == PlayerTeamId) continue;

						const float DistSq = FVector::DistSquared(Start->GetActorLocation(), Other->GetPawn()->GetActorLocation());
						MinEnemyDistSq = FMath::Min(MinEnemyDistSq, DistSq);
						if (DistSq < HardEnemyRadiusSq)
						{
							++RejectNear;
							bUnsafe = true;
							break;
						}
						// Long sightlines across Rathaus must not invalidate a spawn hundreds of metres away.
						if (DistSq < HardLosRadiusSq && Other->LineOfSightTo(Start))
						{
							++RejectLos;
							bUnsafe = true;
							break;
						}
					}

					if (!bUnsafe)
					{
						const float DistanceScore = FMath::Min(MinEnemyDistSq, FMath::Square(20000.0f));
						const float DeathHeat = CaptureDirector ? CaptureDirector->GetRecentDeathHeat(Start->GetActorLocation()) : 0.0f;
						const float Score = DistanceScore - DeathHeat * FMath::Square(5000.0f);
						if (Score > BestScore)
						{
							BestScore = Score;
							BestHeat = DeathHeat;
							BestEnemyDistance = MinEnemyDistSq < TNumericLimits<float>::Max() ? FMath::Sqrt(MinEnemyDistSq) : 99999.0f;
							BestStart = Start;
						}
					}
				}
				if (BestStart)
				{
					UE_LOG(LogPlayerSpawning, Log, TEXT("Spandau spawn selected: start=%s team=%d sector=%d enemyDist=%.0fcm deathHeat=%.2f rejectNear=%d rejectLOS=%d candidates=%d"), *GetNameSafe(BestStart), PlayerTeamId, CaptureDirector->GetActiveSector(), BestEnemyDistance, BestHeat, RejectNear, RejectLos, Candidates.Num());
				}
				return BestStart;
			};

			if (ALyraPlayerStart* SafeStart = ChooseSafest(UnOccupiedStartPoints))
			{
				return SafeStart;
			}
			if (ALyraPlayerStart* SafePartial = ChooseSafest(OccupiedStartPoints))
			{
				return SafePartial;
			}

			if (bRequireSpandauSafeStart)
			{
				UE_LOG(LogPlayerSpawning, Warning, TEXT("Spandau spawn safety rejected all candidates: team=%d sector=%d candidates=%d"), PlayerTeamId, CaptureDirector->GetActiveSector(), StartPoints.Num());
				return nullptr;
			}
		}

		if (UnOccupiedStartPoints.Num() > 0)
		{
			return UnOccupiedStartPoints[FMath::RandRange(0, UnOccupiedStartPoints.Num() - 1)];
		}
		else if (OccupiedStartPoints.Num() > 0)
		{
			return OccupiedStartPoints[FMath::RandRange(0, OccupiedStartPoints.Num() - 1)];
		}
	}

	return nullptr;
}

