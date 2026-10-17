#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "SpandauCaptureDirector.generated.h"

class AController;
class ASpandauCapturePoint;
class UTextRenderComponent;
class FLifetimeProperty;

UCLASS(Blueprintable)
class LYRAGAME_API ASpandauCaptureDirector : public AActor
{
    GENERATED_BODY()

public:
    ASpandauCaptureDirector();

    virtual void Tick(float DeltaSeconds) override;
    virtual void GetLifetimeReplicatedProps(TArray<FLifetimeProperty>& OutLifetimeProps) const override;

    UFUNCTION(BlueprintCallable, Category="Spandau Strike|Capture")
    bool QueueRespawn(AController* Controller);

    UFUNCTION(BlueprintCallable, Category="Spandau Strike|Capture")
    void NotifyAttackerRespawn();

    void RecordRecentDeathLocation(const FVector& Location);
    float GetRecentDeathHeat(const FVector& Location) const;

    UFUNCTION(BlueprintPure, Category="Spandau Strike|Capture")
    int32 GetActiveSector() const { return ActiveSector; }

    UFUNCTION(BlueprintPure, Category="Spandau Strike|Capture")
    int32 GetAttackerTickets() const { return AttackerTickets; }

    UFUNCTION(BlueprintPure, Category="Spandau Strike|Capture")
    int32 GetAttackerTeamId() const { return ResolvedAttackerTeamId; }

    UFUNCTION(BlueprintPure, Category="Spandau Strike|Capture")
    int32 GetDefenderTeamId() const { return ResolvedDefenderTeamId; }

    UFUNCTION(BlueprintPure, Category="Spandau Strike|Capture")
    bool AreTeamsResolved() const { return bTeamsResolved; }

    UFUNCTION(BlueprintPure, Category="Spandau Strike|Capture")
    float GetRespawnWaveRemaining() const { return RespawnWaveRemaining; }

    UFUNCTION(BlueprintPure, Category="Spandau Strike|Capture")
    FString GetHUDSummary() const;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Spandau Strike|Capture")
    int32 StartingSector = 1;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Spandau Strike|Capture")
    int32 TotalSectors = 4;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Spandau Strike|Capture")
    int32 StartingAttackerTickets = 300;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Spandau Strike|Capture")
    int32 SectorTicketRefund = 50;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Spandau Strike|Capture")
    float SectorTransitionSeconds = 20.0f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Spandau Strike|Respawn", meta=(ClampMin="4.0", ClampMax="20.0"))
    float RespawnWaveSeconds = 10.0f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Spandau Strike|Bots", meta=(ClampMin="0.25", ClampMax="10.0"))
    float BotObjectivePulseSeconds = 2.0f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Spandau Strike|Bots")
    bool bRouteBotsToObjectives = true;

    UPROPERTY(BlueprintReadOnly, ReplicatedUsing=OnRep_RuntimeState, Category="Spandau Strike|Capture")
    int32 ActiveSector = 1;

    UPROPERTY(BlueprintReadOnly, ReplicatedUsing=OnRep_RuntimeState, Category="Spandau Strike|Capture")
    int32 AttackerTickets = 300;

    UPROPERTY(BlueprintReadOnly, ReplicatedUsing=OnRep_RuntimeState, Category="Spandau Strike|Capture")
    float TransitionRemaining = 0.0f;

    UPROPERTY(BlueprintReadOnly, ReplicatedUsing=OnRep_RuntimeState, Category="Spandau Strike|Respawn")
    float RespawnWaveRemaining = 10.0f;

    UPROPERTY(BlueprintReadOnly, ReplicatedUsing=OnRep_RuntimeState, Category="Spandau Strike|Capture")
    bool bMatchEnded = false;

    UPROPERTY(BlueprintReadOnly, ReplicatedUsing=OnRep_RuntimeState, Category="Spandau Strike|Capture")
    bool bAttackersWon = false;

protected:
    virtual void BeginPlay() override;

    UFUNCTION()
    void HandlePointCaptured(ASpandauCapturePoint* CapturePoint, int32 CapturingTeamId);

    UFUNCTION()
    void OnRep_RuntimeState();

private:
    UPROPERTY(VisibleAnywhere)
    TObjectPtr<UTextRenderComponent> StatusText;

    UPROPERTY()
    TArray<TObjectPtr<ASpandauCapturePoint>> CapturePoints;

    UPROPERTY()
    TArray<TObjectPtr<AController>> RespawnQueue;

    struct FRecentDeathEntry
    {
        FVector Location = FVector::ZeroVector;
        float TimeSeconds = 0.0f;
    };

    TArray<FRecentDeathEntry> RecentDeaths;
    TMap<TWeakObjectPtr<AController>, float> RespawnQueuedAtSeconds;
    bool bInTransition = false;
    bool bTeamsResolved = false;
    int32 ResolvedAttackerTeamId = INDEX_NONE;
    int32 ResolvedDefenderTeamId = INDEX_NONE;
    float BotObjectivePulseRemaining = 0.0f;
    bool bBotRouteDiagnosticsLogged = false;

    void DiscoverCapturePoints();
    void ResolveRuntimeTeams();
    void RefreshSectorActivation();
    void BeginSectorTransition();
    void CompleteSectorTransition();
    bool IsCurrentSectorComplete() const;
    void ProcessRespawnWave();
    void RouteBotsToActiveObjectives();
    ASpandauCapturePoint* FindObjectiveForTeam(int32 TeamId, const FVector& FromLocation) const;
    int32 GetControllerTeamId(const AController* Controller) const;
    void UpdateStatusText();
};
