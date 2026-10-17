#include "SpandauStrike/SpandauCapturePoint.h"

#include "Components/SphereComponent.h"
#include "Components/TextRenderComponent.h"
#include "DrawDebugHelpers.h"
#include "GameFramework/Pawn.h"
#include "LyraLogChannels.h"
#include "Net/UnrealNetwork.h"
#include "Player/LyraPlayerState.h"

ASpandauCapturePoint::ASpandauCapturePoint()
{
    PrimaryActorTick.bCanEverTick = true;
    bReplicates = true;
    bAlwaysRelevant = true;
    SetNetUpdateFrequency(10.0f);
    SetReplicateMovement(false);

    CaptureSphere = CreateDefaultSubobject<USphereComponent>(TEXT("CaptureSphere"));
    SetRootComponent(CaptureSphere);
    CaptureSphere->InitSphereRadius(550.0f);
    CaptureSphere->SetCollisionEnabled(ECollisionEnabled::QueryOnly);
    CaptureSphere->SetGenerateOverlapEvents(true);
    CaptureSphere->SetCollisionResponseToAllChannels(ECR_Ignore);
    CaptureSphere->SetCollisionResponseToChannel(ECC_Pawn, ECR_Overlap);

    DebugLabel = CreateDefaultSubobject<UTextRenderComponent>(TEXT("DebugLabel"));
    DebugLabel->SetupAttachment(CaptureSphere);
    DebugLabel->SetRelativeLocation(FVector(0.0, 0.0, 150.0));
    DebugLabel->SetHorizontalAlignment(EHorizTextAligment::EHTA_Center);
    DebugLabel->SetWorldSize(55.0f);
}

void ASpandauCapturePoint::BeginPlay()
{
    Super::BeginPlay();
    UpdateVisuals();
    UE_LOG(LogLyra, Log, TEXT("SpandauCapturePoint runtime ready: %s sector=%d point=%d"), *GetName(), SectorIndex, PointIndex);
}

void ASpandauCapturePoint::Tick(float DeltaSeconds)
{
    Super::Tick(DeltaSeconds);

    if (HasAuthority())
    {
        UpdateAuthority(DeltaSeconds);
    }

    UpdateVisuals();

#if !(UE_BUILD_SHIPPING || UE_BUILD_TEST)
    if (bDrawRuntimeDebug && GetWorld())
    {
        FColor Color = FColor(160, 160, 160);
        switch (CaptureState)
        {
            case ESpandauCaptureState::Locked: Color = FColor(90, 90, 90); break;
            case ESpandauCaptureState::Active: Color = FColor::White; break;
            case ESpandauCaptureState::Capturing: Color = FColor::Yellow; break;
            case ESpandauCaptureState::Contested: Color = FColor::Red; break;
            case ESpandauCaptureState::Captured: Color = FColor::Green; break;
            default: break;
        }
        DrawDebugCylinder(GetWorld(), GetActorLocation() - FVector(0,0,30), GetActorLocation() + FVector(0,0,30), CaptureSphere->GetScaledSphereRadius(), 32, Color, false, 0.0f, 0, 5.0f);
    }
#endif
}

void ASpandauCapturePoint::SetCaptureActive(bool bNewActive)
{
    if (!HasAuthority())
    {
        return;
    }

    bCaptureActive = bNewActive;
    if (CaptureState != ESpandauCaptureState::Captured)
    {
        CaptureState = bCaptureActive ? ESpandauCaptureState::Active : ESpandauCaptureState::Locked;
    }
    ForceNetUpdate();
    UpdateVisuals();
}

void ASpandauCapturePoint::ResetCapture()
{
    if (!HasAuthority())
    {
        return;
    }

    CaptureProgress = 0.0f;
    CapturedByTeamId = INDEX_NONE;
    TimeSinceLastAttacker = 0.0f;
    CaptureState = bCaptureActive ? ESpandauCaptureState::Active : ESpandauCaptureState::Locked;
    ForceNetUpdate();
    UpdateVisuals();
}

void ASpandauCapturePoint::UpdateAuthority(float DeltaSeconds)
{
    if (!bCaptureActive || CaptureState == ESpandauCaptureState::Captured)
    {
        return;
    }

    int32 Attackers = 0;
    int32 Defenders = 0;
    CountTeams(Attackers, Defenders);

    if (Attackers > 0)
    {
        TimeSinceLastAttacker = 0.0f;
    }
    else
    {
        TimeSinceLastAttacker += DeltaSeconds;
    }

    if (Attackers > 0 && Defenders > 0)
    {
        CaptureState = ESpandauCaptureState::Contested;
        return;
    }

    if (Attackers > 0)
    {
        CaptureState = ESpandauCaptureState::Capturing;
        const float SpeedMultiplier = GetCaptureSpeedMultiplier(Attackers);
        CaptureProgress = FMath::Clamp(CaptureProgress + (DeltaSeconds * SpeedMultiplier / FMath::Max(1.0f, CaptureDurationSeconds)), 0.0f, 1.0f);

        if (CaptureProgress >= 1.0f)
        {
            CaptureProgress = 1.0f;
            CapturedByTeamId = AttackerTeamId;
            CaptureState = ESpandauCaptureState::Captured;
            OnCaptured.Broadcast(this, AttackerTeamId);
            ForceNetUpdate();
        }
        return;
    }

    CaptureState = ESpandauCaptureState::Active;
    if (CaptureProgress > 0.0f && TimeSinceLastAttacker >= DecayDelaySeconds)
    {
        CaptureProgress = FMath::Max(0.0f, CaptureProgress - DecayPerSecond * DeltaSeconds);
    }
}

void ASpandauCapturePoint::CountTeams(int32& OutAttackers, int32& OutDefenders) const
{
    OutAttackers = 0;
    OutDefenders = 0;

    TArray<AActor*> OverlappingActors;
    CaptureSphere->GetOverlappingActors(OverlappingActors, APawn::StaticClass());

    for (AActor* Actor : OverlappingActors)
    {
        const APawn* Pawn = Cast<APawn>(Actor);
        if (!Pawn)
        {
            continue;
        }

        const ALyraPlayerState* PlayerState = Pawn->GetPlayerState<ALyraPlayerState>();
        if (!PlayerState)
        {
            continue;
        }

        const int32 TeamId = PlayerState->GetTeamId();
        if (TeamId == AttackerTeamId)
        {
            ++OutAttackers;
        }
        else if (TeamId == DefenderTeamId)
        {
            ++OutDefenders;
        }
    }
}

float ASpandauCapturePoint::GetCaptureSpeedMultiplier(int32 AttackerCount) const
{
    const int32 Count = FMath::Clamp(AttackerCount, 1, FMath::Max(1, SpeedupCapPlayers));
    switch (Count)
    {
        case 1: return 1.0f;
        case 2: return 45.0f / 33.0f;
        case 3: return 45.0f / 28.0f;
        default: return 45.0f / 25.0f;
    }
}

void ASpandauCapturePoint::UpdateVisuals()
{
    if (!DebugLabel)
    {
        return;
    }

    const TCHAR* StateText = TEXT("LOCKED");
    switch (CaptureState)
    {
        case ESpandauCaptureState::Active: StateText = TEXT("ACTIVE"); break;
        case ESpandauCaptureState::Capturing: StateText = TEXT("CAPTURING"); break;
        case ESpandauCaptureState::Contested: StateText = TEXT("CONTESTED"); break;
        case ESpandauCaptureState::Captured: StateText = TEXT("CAPTURED"); break;
        default: break;
    }

    DebugLabel->SetText(FText::FromString(FString::Printf(TEXT("S%d-%c  %s  %d%%"), SectorIndex, PointIndex == 1 ? 'A' : 'B', StateText, FMath::RoundToInt(CaptureProgress * 100.0f))));
}

void ASpandauCapturePoint::OnRep_CaptureState()
{
    UpdateVisuals();
}

void ASpandauCapturePoint::OnRep_Progress()
{
    UpdateVisuals();
}

void ASpandauCapturePoint::GetLifetimeReplicatedProps(TArray<FLifetimeProperty>& OutLifetimeProps) const
{
    Super::GetLifetimeReplicatedProps(OutLifetimeProps);

    DOREPLIFETIME(ASpandauCapturePoint, SectorIndex);
    DOREPLIFETIME(ASpandauCapturePoint, PointIndex);
    DOREPLIFETIME(ASpandauCapturePoint, CaptureState);
    DOREPLIFETIME(ASpandauCapturePoint, CaptureProgress);
    DOREPLIFETIME(ASpandauCapturePoint, CapturedByTeamId);
    DOREPLIFETIME(ASpandauCapturePoint, bCaptureActive);
}


