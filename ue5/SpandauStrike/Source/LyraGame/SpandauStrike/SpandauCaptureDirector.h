#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "SpandauCaptureDirector.generated.h"

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
    void NotifyAttackerRespawn();

    UFUNCTION(BlueprintPure, Category="Spandau Strike|Capture")
    int32 GetActiveSector() const { return ActiveSector; }

    UFUNCTION(BlueprintPure, Category="Spandau Strike|Capture")
    int32 GetAttackerTickets() const { return AttackerTickets; }

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Spandau Strike|Capture")
    int32 StartingSector = 1;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Spandau Strike|Capture")
    int32 TotalSectors = 1;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Spandau Strike|Capture")
    int32 StartingAttackerTickets = 300;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Spandau Strike|Capture")
    int32 SectorTicketRefund = 50;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Spandau Strike|Capture")
    float SectorTransitionSeconds = 20.0f;

    UPROPERTY(BlueprintReadOnly, ReplicatedUsing=OnRep_RuntimeState, Category="Spandau Strike|Capture")
    int32 ActiveSector = 1;

    UPROPERTY(BlueprintReadOnly, ReplicatedUsing=OnRep_RuntimeState, Category="Spandau Strike|Capture")
    int32 AttackerTickets = 300;

    UPROPERTY(BlueprintReadOnly, ReplicatedUsing=OnRep_RuntimeState, Category="Spandau Strike|Capture")
    float TransitionRemaining = 0.0f;

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

    bool bInTransition = false;

    void DiscoverCapturePoints();
    void RefreshSectorActivation();
    void BeginSectorTransition();
    void CompleteSectorTransition();
    bool IsCurrentSectorComplete() const;
    void UpdateStatusText();
};
