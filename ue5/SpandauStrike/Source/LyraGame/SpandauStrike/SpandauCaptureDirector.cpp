#include "SpandauStrike/SpandauCaptureDirector.h"

#include "AIController.h"
#include "Components/TextRenderComponent.h"
#include "EngineUtils.h"
#include "GameFramework/Controller.h"
#include "GameFramework/GameModeBase.h"
#include "GameFramework/GameStateBase.h"
#include "GameFramework/Pawn.h"
#include "GameFramework/PlayerState.h"
#include "LyraLogChannels.h"
#include "Net/UnrealNetwork.h"
#include "Navigation/PathFollowingComponent.h"
#include "Player/LyraPlayerState.h"
#include "Character/LyraHealthComponent.h"
#include "Misc/CommandLine.h"
#include "Misc/Parse.h"
#include "SpandauStrike/SpandauCapturePoint.h"

ASpandauCaptureDirector::ASpandauCaptureDirector()
{
    PrimaryActorTick.bCanEverTick = true;
    bReplicates = true;
    bAlwaysRelevant = true;
    SetNetUpdateFrequency(10.0f);
    SetReplicateMovement(false);

    StatusText = CreateDefaultSubobject<UTextRenderComponent>(TEXT("StatusText"));
    SetRootComponent(StatusText);
    StatusText->SetHorizontalAlignment(EHorizTextAligment::EHTA_Center);
    StatusText->SetWorldSize(65.0f);
}

void ASpandauCaptureDirector::BeginPlay()
{
    Super::BeginPlay();

    if (HasAuthority())
    {
        ActiveSector = FMath::Max(1, StartingSector);
        AttackerTickets = FMath::Max(0, StartingAttackerTickets);
        TransitionRemaining = 0.0f;
        RespawnWaveRemaining = FMath::Max(1.0f, RespawnWaveSeconds);
        BotObjectivePulseRemaining = 0.0f;
        bMatchEnded = false;
        bAttackersWon = false;
        bInTransition = false;

        DiscoverCapturePoints();
        RefreshSectorActivation();
        UE_LOG(LogLyra, Log, TEXT("SpandauCaptureDirector runtime ready: points=%d sectors=%d tickets=%d wave=%.1fs"), CapturePoints.Num(), TotalSectors, AttackerTickets, RespawnWaveSeconds);
        ForceNetUpdate();
    }

    UpdateStatusText();
}

void ASpandauCaptureDirector::Tick(float DeltaSeconds)
{
    Super::Tick(DeltaSeconds);

    if (HasAuthority() && !bTeamsResolved)
    {
        ResolveRuntimeTeams();
    }

    if (HasAuthority() && bTeamsResolved && !bMatchEnded)
    {
        if (bRespawnProbeArmed && !bRespawnProbeTriggered && FParse::Param(FCommandLine::Get(), TEXT("SpandauRespawnProbe")))
        {
            for (FConstControllerIterator It = GetWorld()->GetControllerIterator(); It; ++It)
            {
                AController* Controller = It->Get();
                if (!Controller || !Controller->GetPawn() || !Controller->PlayerState || !Controller->PlayerState->IsABot())
                {
                    continue;
                }

                if (ULyraHealthComponent* HealthComponent = ULyraHealthComponent::FindHealthComponent(Controller->GetPawn()))
                {
                    bRespawnProbeTriggered = true;
                    UE_LOG(LogLyra, Log, TEXT("Spandau respawn probe trigger: controller=%s team=%d sector=%d"), *GetNameSafe(Controller), GetControllerTeamId(Controller), ActiveSector);
                    HealthComponent->DamageSelfDestruct(false);
                }
                break;
            }
        }

        RespawnWaveRemaining = FMath::Max(0.0f, RespawnWaveRemaining - DeltaSeconds);
        if (RespawnWaveRemaining <= KINDA_SMALL_NUMBER)
        {
            ProcessRespawnWave();
            RespawnWaveRemaining = FMath::Max(1.0f, RespawnWaveSeconds);
        }

        if (bRouteBotsToObjectives)
        {
            BotObjectivePulseRemaining -= DeltaSeconds;
            if (BotObjectivePulseRemaining <= 0.0f)
            {
                RouteBotsToActiveObjectives();
                BotObjectivePulseRemaining = FMath::Max(0.25f, BotObjectivePulseSeconds);
            }
        }
    }

    if (HasAuthority() && bInTransition && !bMatchEnded)
    {
        TransitionRemaining = FMath::Max(0.0f, TransitionRemaining - DeltaSeconds);
        if (TransitionRemaining <= KINDA_SMALL_NUMBER)
        {
            CompleteSectorTransition();
        }
    }

    UpdateStatusText();
}

bool ASpandauCaptureDirector::QueueRespawn(AController* Controller)
{
    if (!HasAuthority() || !bTeamsResolved || bMatchEnded || !IsValid(Controller))
    {
        return false;
    }

    if (Controller->GetPawn())
    {
        return false;
    }

    const int32 TeamId = GetControllerTeamId(Controller);
    if (TeamId != ResolvedAttackerTeamId && TeamId != ResolvedDefenderTeamId)
    {
        return false;
    }

    if (TeamId == ResolvedAttackerTeamId && AttackerTickets <= 0)
    {
        return true;
    }

    RespawnQueue.AddUnique(Controller);
    if (GetWorld() && !RespawnQueuedAtSeconds.Contains(Controller))
    {
        RespawnQueuedAtSeconds.Add(Controller, GetWorld()->GetTimeSeconds());
    }
    UE_LOG(LogLyra, Log, TEXT("Spandau respawn queued: controller=%s team=%d sector=%d wave=%.2f tickets=%d"), *GetNameSafe(Controller), TeamId, ActiveSector, RespawnWaveRemaining, AttackerTickets);
    return true;
}

void ASpandauCaptureDirector::RecordRecentDeathLocation(const FVector& Location)
{
    if (!HasAuthority() || !GetWorld())
    {
        return;
    }

    const float Now = GetWorld()->GetTimeSeconds();
    RecentDeaths.RemoveAll([Now](const FRecentDeathEntry& Entry)
    {
        return (Now - Entry.TimeSeconds) > 15.0f;
    });
    RecentDeaths.Add({Location, Now});
    UE_LOG(LogLyra, Log, TEXT("Spandau death heat event: x=%.0f y=%.0f z=%.0f active=%d"), Location.X, Location.Y, Location.Z, RecentDeaths.Num());
}

float ASpandauCaptureDirector::GetRecentDeathHeat(const FVector& Location) const
{
    if (!GetWorld())
    {
        return 0.0f;
    }

    const float Now = GetWorld()->GetTimeSeconds();
    float Heat = 0.0f;
    for (const FRecentDeathEntry& Entry : RecentDeaths)
    {
        const float Age = Now - Entry.TimeSeconds;
        if (Age < 0.0f || Age > 15.0f) continue;
        const float Dist = FVector::Dist(Location, Entry.Location);
        if (Dist > 2500.0f) continue;
        Heat += (1.0f - Age / 15.0f) * (1.0f - Dist / 2500.0f);
    }
    return Heat;
}

void ASpandauCaptureDirector::NotifyAttackerRespawn()
{
    if (!HasAuthority() || bMatchEnded)
    {
        return;
    }

    AttackerTickets = FMath::Max(0, AttackerTickets - 1);
    if (AttackerTickets <= 0)
    {
        UE_LOG(LogLyra, Log, TEXT("Spandau attackers exhausted tickets"));
    }
    ForceNetUpdate();
}

void ASpandauCaptureDirector::ProcessRespawnWave()
{
    if (!HasAuthority() || bMatchEnded || RespawnQueue.IsEmpty())
    {
        return;
    }

    AGameModeBase* GameMode = GetWorld() ? GetWorld()->GetAuthGameMode() : nullptr;
    if (!GameMode)
    {
        return;
    }

    int32 Spawned = 0;
    int32 TicketSpawns = 0;
    TArray<TObjectPtr<AController>> Pending = MoveTemp(RespawnQueue);
    RespawnQueue.Reset();

    for (AController* Controller : Pending)
    {
        if (!IsValid(Controller) || Controller->GetPawn())
        {
            continue;
        }

        const int32 TeamId = GetControllerTeamId(Controller);
        if (TeamId == ResolvedAttackerTeamId && AttackerTickets <= 0)
        {
            continue;
        }

        const float QueuedAt = RespawnQueuedAtSeconds.FindRef(Controller);
        GameMode->RestartPlayer(Controller);
        if (Controller->GetPawn())
        {
            ++Spawned;
            const float WaitSeconds = (GetWorld() && QueuedAt > 0.0f) ? FMath::Max(0.0f, GetWorld()->GetTimeSeconds() - QueuedAt) : 0.0f;
            UE_LOG(LogLyra, Log, TEXT("Spandau respawn completed: controller=%s team=%d sector=%d wait=%.2fs x=%.0f y=%.0f z=%.0f"), *GetNameSafe(Controller), TeamId, ActiveSector, WaitSeconds, Controller->GetPawn()->GetActorLocation().X, Controller->GetPawn()->GetActorLocation().Y, Controller->GetPawn()->GetActorLocation().Z);
            RespawnQueuedAtSeconds.Remove(Controller);
            if (GetWorld())
            {
                RespawnedAtSeconds.Add(Controller, GetWorld()->GetTimeSeconds());
            }
            if (TeamId == ResolvedAttackerTeamId)
            {
                NotifyAttackerRespawn();
                ++TicketSpawns;
            }
        }
        else
        {
            RespawnQueue.AddUnique(Controller);
        }
    }

    UE_LOG(LogLyra, Log, TEXT("Spandau respawn wave: spawned=%d attackerTicketSpawns=%d queued=%d tickets=%d"), Spawned, TicketSpawns, RespawnQueue.Num(), AttackerTickets);
    ForceNetUpdate();
}

void ASpandauCaptureDirector::DiscoverCapturePoints()
{
    CapturePoints.Reset();

    for (TActorIterator<ASpandauCapturePoint> It(GetWorld()); It; ++It)
    {
        ASpandauCapturePoint* Point = *It;
        if (!IsValid(Point))
        {
            continue;
        }

        CapturePoints.Add(Point);
        Point->OnCaptured.AddDynamic(this, &ASpandauCaptureDirector::HandlePointCaptured);
        Point->ResetCapture();
    }

    CapturePoints.Sort([](const ASpandauCapturePoint& A, const ASpandauCapturePoint& B)
    {
        if (A.GetSectorIndex() != B.GetSectorIndex())
        {
            return A.GetSectorIndex() < B.GetSectorIndex();
        }
        return A.GetPointIndex() < B.GetPointIndex();
    });

    int32 HighestSector = 0;
    for (const ASpandauCapturePoint* Point : CapturePoints)
    {
        if (Point)
        {
            HighestSector = FMath::Max(HighestSector, Point->GetSectorIndex());
        }
    }

    if (HighestSector > 0)
    {
        TotalSectors = HighestSector;
    }
}

void ASpandauCaptureDirector::ResolveRuntimeTeams()
{
    if (!HasAuthority() || bTeamsResolved || !GetWorld())
    {
        return;
    }

    const AGameStateBase* GameState = GetWorld()->GetGameState();
    if (!GameState)
    {
        return;
    }

    TArray<int32> TeamIds;
    int32 HumanTeamId = INDEX_NONE;

    for (APlayerState* BasePlayerState : GameState->PlayerArray)
    {
        const ALyraPlayerState* LyraPlayerState = Cast<ALyraPlayerState>(BasePlayerState);
        if (!LyraPlayerState)
        {
            continue;
        }

        const int32 TeamId = LyraPlayerState->GetTeamId();
        if (TeamId < 0 || TeamId == 255)
        {
            continue;
        }

        TeamIds.AddUnique(TeamId);
        if (!BasePlayerState->IsABot())
        {
            HumanTeamId = TeamId;
        }
    }

    if (TeamIds.Num() < 2)
    {
        return;
    }

    TeamIds.Sort();
    ResolvedAttackerTeamId = TeamIds.Contains(HumanTeamId) ? HumanTeamId : TeamIds[0];
    ResolvedDefenderTeamId = INDEX_NONE;
    for (const int32 TeamId : TeamIds)
    {
        if (TeamId != ResolvedAttackerTeamId)
        {
            ResolvedDefenderTeamId = TeamId;
            break;
        }
    }

    if (ResolvedDefenderTeamId == INDEX_NONE)
    {
        return;
    }

    for (ASpandauCapturePoint* Point : CapturePoints)
    {
        if (Point)
        {
            Point->SetTeamIds(ResolvedAttackerTeamId, ResolvedDefenderTeamId);
        }
    }

    bTeamsResolved = true;
    UE_LOG(LogLyra, Log, TEXT("SpandauCaptureDirector teams resolved: attacker=%d defender=%d humanTeam=%d"), ResolvedAttackerTeamId, ResolvedDefenderTeamId, HumanTeamId);
    RefreshSectorActivation();
}

int32 ASpandauCaptureDirector::GetControllerTeamId(const AController* Controller) const
{
    if (!Controller)
    {
        return INDEX_NONE;
    }
    const ALyraPlayerState* LyraPlayerState = Controller->GetPlayerState<ALyraPlayerState>();
    return LyraPlayerState ? LyraPlayerState->GetTeamId() : INDEX_NONE;
}

ASpandauCapturePoint* ASpandauCaptureDirector::FindObjectiveForTeam(int32 TeamId, const FVector& FromLocation) const
{
    ASpandauCapturePoint* Best = nullptr;
    float BestDistSq = TNumericLimits<float>::Max();

    for (ASpandauCapturePoint* Point : CapturePoints)
    {
        if (!Point || Point->GetSectorIndex() != ActiveSector || Point->IsCaptured())
        {
            continue;
        }

        const float DistSq = FVector::DistSquared(FromLocation, Point->GetActorLocation());
        if (DistSq < BestDistSq)
        {
            BestDistSq = DistSq;
            Best = Point;
        }
    }
    return Best;
}

void ASpandauCaptureDirector::RouteBotsToActiveObjectives()
{
    if (!GetWorld() || bInTransition || bMatchEnded)
    {
        return;
    }

    int32 Routed = 0;
    int32 Failed = 0;
    for (FConstControllerIterator It = GetWorld()->GetControllerIterator(); It; ++It)
    {
        AAIController* AI = Cast<AAIController>(It->Get());
        if (!AI || !AI->GetPawn() || !AI->PlayerState || !AI->PlayerState->IsABot())
        {
            continue;
        }

        const int32 TeamId = GetControllerTeamId(AI);
        if (TeamId != ResolvedAttackerTeamId && TeamId != ResolvedDefenderTeamId)
        {
            continue;
        }

        ASpandauCapturePoint* Objective = FindObjectiveForTeam(TeamId, AI->GetPawn()->GetActorLocation());
        if (!Objective)
        {
            continue;
        }

        const float Acceptance = TeamId == ResolvedDefenderTeamId ? 350.0f : 180.0f;
        EPathFollowingRequestResult::Type Result = AI->MoveToLocation(Objective->GetActorLocation(), Acceptance, true, true, true, false, nullptr, true);
        if (Result == EPathFollowingRequestResult::Failed)
        {
            Result = AI->MoveToLocation(Objective->GetActorLocation(), Acceptance, true, false, false, false, nullptr, true);
        }
        if (Result == EPathFollowingRequestResult::Failed)
        {
            ++Failed;
        }
        else
        {
            ++Routed;
            const TWeakObjectPtr<AController> ControllerKey(AI);
            if (const float* RespawnedAt = RespawnedAtSeconds.Find(ControllerKey))
            {
                const float SpawnToActionSeconds = FMath::Max(0.0f, GetWorld()->GetTimeSeconds() - *RespawnedAt);
                UE_LOG(LogLyra, Log, TEXT("Spandau spawn-to-action: controller=%s team=%d sector=%d seconds=%.2f objective=%s result=%d"), *GetNameSafe(AI), TeamId, ActiveSector, SpawnToActionSeconds, *GetNameSafe(Objective), static_cast<int32>(Result));
                RespawnedAtSeconds.Remove(ControllerKey);
            }
        }
    }

    if (!bBotRouteDiagnosticsLogged || Routed > 0)
    {
        UE_LOG(LogLyra, Log, TEXT("Spandau objective routing: sector=%d routed=%d failed=%d"), ActiveSector, Routed, Failed);
        bBotRouteDiagnosticsLogged = true;
    }

    if (!bRespawnProbeArmed && FParse::Param(FCommandLine::Get(), TEXT("SpandauRespawnProbe")) && Routed >= 15 && Failed == 0)
    {
        bRespawnProbeArmed = true;
        UE_LOG(LogLyra, Log, TEXT("Spandau respawn probe armed: routed=%d failed=%d sector=%d"), Routed, Failed, ActiveSector);
    }
}

void ASpandauCaptureDirector::RefreshSectorActivation()
{
    if (!HasAuthority())
    {
        return;
    }

    for (ASpandauCapturePoint* Point : CapturePoints)
    {
        if (!Point)
        {
            continue;
        }

        const bool bShouldBeActive = bTeamsResolved && !bMatchEnded && !bInTransition && Point->GetSectorIndex() == ActiveSector && !Point->IsCaptured();
        Point->SetCaptureActive(bShouldBeActive);
    }
}

void ASpandauCaptureDirector::HandlePointCaptured(ASpandauCapturePoint* CapturePoint, int32 CapturingTeamId)
{
    if (!HasAuthority() || bMatchEnded || bInTransition || !CapturePoint)
    {
        return;
    }

    if (CapturingTeamId != ResolvedAttackerTeamId || CapturePoint->GetSectorIndex() != ActiveSector)
    {
        return;
    }

    UE_LOG(LogLyra, Log, TEXT("SpandauCapturePoint captured: sector=%d point=%d team=%d"), CapturePoint->GetSectorIndex(), CapturePoint->GetPointIndex(), CapturingTeamId);

    if (IsCurrentSectorComplete())
    {
        BeginSectorTransition();
    }
}

bool ASpandauCaptureDirector::IsCurrentSectorComplete() const
{
    int32 PointCount = 0;

    for (const ASpandauCapturePoint* Point : CapturePoints)
    {
        if (!Point || Point->GetSectorIndex() != ActiveSector)
        {
            continue;
        }

        ++PointCount;
        if (!Point->IsCaptured())
        {
            return false;
        }
    }

    return PointCount >= 2;
}

void ASpandauCaptureDirector::BeginSectorTransition()
{
    if (!HasAuthority() || bInTransition || bMatchEnded)
    {
        return;
    }

    if (ActiveSector >= TotalSectors)
    {
        bMatchEnded = true;
        bAttackersWon = true;
        bInTransition = false;
        TransitionRemaining = 0.0f;
        RefreshSectorActivation();
        ForceNetUpdate();
        return;
    }

    bInTransition = true;
    TransitionRemaining = FMath::Max(0.0f, SectorTransitionSeconds);
    RefreshSectorActivation();
    ForceNetUpdate();
}

void ASpandauCaptureDirector::CompleteSectorTransition()
{
    if (!HasAuthority() || bMatchEnded)
    {
        return;
    }

    ++ActiveSector;
    AttackerTickets += FMath::Max(0, SectorTicketRefund);
    bInTransition = false;
    TransitionRemaining = 0.0f;
    RefreshSectorActivation();
    RouteBotsToActiveObjectives();
    UE_LOG(LogLyra, Log, TEXT("Spandau sector advanced: sector=%d tickets=%d"), ActiveSector, AttackerTickets);
    ForceNetUpdate();
}

FString ASpandauCaptureDirector::GetHUDSummary() const
{
    if (bMatchEnded)
    {
        return bAttackersWon ? TEXT("ANGREIFER SIEG") : TEXT("VERTEIDIGER SIEG");
    }
    if (bInTransition)
    {
        return FString::Printf(TEXT("SEKTORWECHSEL %.0fs | TICKETS %d"), TransitionRemaining, AttackerTickets);
    }
    return FString::Printf(TEXT("SEKTOR %d/%d | TICKETS %d | WELLE %.0fs"), ActiveSector, FMath::Max(1, TotalSectors), AttackerTickets, RespawnWaveRemaining);
}

void ASpandauCaptureDirector::UpdateStatusText()
{
    if (StatusText)
    {
        StatusText->SetText(FText::FromString(GetHUDSummary()));
    }
}

void ASpandauCaptureDirector::OnRep_RuntimeState()
{
    UpdateStatusText();
}

void ASpandauCaptureDirector::GetLifetimeReplicatedProps(TArray<FLifetimeProperty>& OutLifetimeProps) const
{
    Super::GetLifetimeReplicatedProps(OutLifetimeProps);

    DOREPLIFETIME(ASpandauCaptureDirector, ActiveSector);
    DOREPLIFETIME(ASpandauCaptureDirector, AttackerTickets);
    DOREPLIFETIME(ASpandauCaptureDirector, TransitionRemaining);
    DOREPLIFETIME(ASpandauCaptureDirector, RespawnWaveRemaining);
    DOREPLIFETIME(ASpandauCaptureDirector, bMatchEnded);
    DOREPLIFETIME(ASpandauCaptureDirector, bAttackersWon);
}
