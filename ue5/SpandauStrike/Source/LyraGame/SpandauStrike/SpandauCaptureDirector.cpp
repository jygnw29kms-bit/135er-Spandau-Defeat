#include "SpandauStrike/SpandauCaptureDirector.h"

#include "Components/TextRenderComponent.h"
#include "EngineUtils.h"
#include "GameFramework/GameStateBase.h"
#include "GameFramework/PlayerState.h"
#include "Player/LyraPlayerState.h"
#include "LyraLogChannels.h"
#include "Net/UnrealNetwork.h"
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
        bMatchEnded = false;
        bAttackersWon = false;
        bInTransition = false;

        DiscoverCapturePoints();
        RefreshSectorActivation();
        UE_LOG(LogLyra, Log, TEXT("SpandauCaptureDirector runtime ready: points=%d sectors=%d tickets=%d"), CapturePoints.Num(), TotalSectors, AttackerTickets);
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

void ASpandauCaptureDirector::NotifyAttackerRespawn()
{
    if (!HasAuthority() || bMatchEnded)
    {
        return;
    }

    AttackerTickets = FMath::Max(0, AttackerTickets - 1);
    if (AttackerTickets <= 0)
    {
        bMatchEnded = true;
        bAttackersWon = false;
        bInTransition = false;
        TransitionRemaining = 0.0f;
        RefreshSectorActivation();
    }

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

    if (CapturePoint->GetSectorIndex() != ActiveSector)
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

    return PointCount > 0;
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
    ForceNetUpdate();
}

void ASpandauCaptureDirector::UpdateStatusText()
{
    if (!StatusText)
    {
        return;
    }

    FString State;
    if (bMatchEnded)
    {
        State = bAttackersWon ? TEXT("ANGREIFER SIEG") : TEXT("VERTEIDIGER SIEG");
    }
    else if (bInTransition)
    {
        State = FString::Printf(TEXT("SEKTORWECHSEL %.0fs"), TransitionRemaining);
    }
    else
    {
        State = FString::Printf(TEXT("SEKTOR %d/%d"), ActiveSector, FMath::Max(1, TotalSectors));
    }

    StatusText->SetText(FText::FromString(FString::Printf(TEXT("%s\nTICKETS %d"), *State, AttackerTickets)));
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
    DOREPLIFETIME(ASpandauCaptureDirector, bMatchEnded);
    DOREPLIFETIME(ASpandauCaptureDirector, bAttackersWon);
}

