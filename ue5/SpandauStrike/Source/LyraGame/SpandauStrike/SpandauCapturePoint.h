#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "SpandauCapturePoint.generated.h"

class USphereComponent;
class UTextRenderComponent;
class ASpandauCapturePoint;
class FLifetimeProperty;

UENUM(BlueprintType)
enum class ESpandauCaptureState : uint8
{
    Locked,
    Active,
    Capturing,
    Contested,
    Captured
};

DECLARE_DYNAMIC_MULTICAST_DELEGATE_TwoParams(FSpandauCapturePointCaptured, ASpandauCapturePoint*, CapturePoint, int32, CapturingTeamId);

UCLASS(Blueprintable)
class LYRAGAME_API ASpandauCapturePoint : public AActor
{
    GENERATED_BODY()

public:
    ASpandauCapturePoint();

    virtual void Tick(float DeltaSeconds) override;
    virtual void GetLifetimeReplicatedProps(TArray<FLifetimeProperty>& OutLifetimeProps) const override;

    UFUNCTION(BlueprintCallable, Category="Spandau Strike|Capture")
    void SetCaptureActive(bool bNewActive);

    UFUNCTION(BlueprintCallable, Category="Spandau Strike|Capture")
    void ResetCapture();

    UFUNCTION(BlueprintCallable, Category="Spandau Strike|Capture")
    void SetTeamIds(int32 NewAttackerTeamId, int32 NewDefenderTeamId);

    UFUNCTION(BlueprintPure, Category="Spandau Strike|Capture")
    bool IsCaptured() const { return CaptureState == ESpandauCaptureState::Captured; }

    UFUNCTION(BlueprintPure, Category="Spandau Strike|Capture")
    int32 GetSectorIndex() const { return SectorIndex; }

    UFUNCTION(BlueprintPure, Category="Spandau Strike|Capture")
    int32 GetPointIndex() const { return PointIndex; }

    UFUNCTION(BlueprintPure, Category="Spandau Strike|Capture")
    float GetCaptureProgress() const { return CaptureProgress; }

    UFUNCTION(BlueprintPure, Category="Spandau Strike|Capture")
    ESpandauCaptureState GetCaptureState() const { return CaptureState; }

    UPROPERTY(BlueprintAssignable, Category="Spandau Strike|Capture")
    FSpandauCapturePointCaptured OnCaptured;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Replicated, Category="Spandau Strike|Capture")
    int32 SectorIndex = 1;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Replicated, Category="Spandau Strike|Capture")
    int32 PointIndex = 1;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Spandau Strike|Capture")
    int32 AttackerTeamId = 1;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Spandau Strike|Capture")
    int32 DefenderTeamId = 2;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Spandau Strike|Capture", meta=(ClampMin="1.0"))
    float CaptureDurationSeconds = 45.0f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Spandau Strike|Capture", meta=(ClampMin="1", ClampMax="8"))
    int32 SpeedupCapPlayers = 4;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Spandau Strike|Capture", meta=(ClampMin="0.0"))
    float DecayDelaySeconds = 3.0f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Spandau Strike|Capture", meta=(ClampMin="0.0"))
    float DecayPerSecond = 0.035f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Spandau Strike|Capture")
    bool bDrawRuntimeDebug = true;

    UPROPERTY(BlueprintReadOnly, ReplicatedUsing=OnRep_CaptureState, Category="Spandau Strike|Capture")
    ESpandauCaptureState CaptureState = ESpandauCaptureState::Locked;

    UPROPERTY(BlueprintReadOnly, ReplicatedUsing=OnRep_Progress, Category="Spandau Strike|Capture")
    float CaptureProgress = 0.0f;

    UPROPERTY(BlueprintReadOnly, Replicated, Category="Spandau Strike|Capture")
    int32 CapturedByTeamId = INDEX_NONE;

    UPROPERTY(BlueprintReadOnly, Replicated, Category="Spandau Strike|Capture")
    bool bCaptureActive = false;

protected:
    virtual void BeginPlay() override;

    UFUNCTION()
    void OnRep_CaptureState();

    UFUNCTION()
    void OnRep_Progress();

private:
    UPROPERTY(VisibleAnywhere)
    TObjectPtr<USphereComponent> CaptureSphere;

    UPROPERTY(VisibleAnywhere)
    TObjectPtr<UTextRenderComponent> DebugLabel;

    float TimeSinceLastAttacker = 0.0f;

    void UpdateAuthority(float DeltaSeconds);
    void UpdateVisuals();
    void CountTeams(int32& OutAttackers, int32& OutDefenders) const;
    float GetCaptureSpeedMultiplier(int32 AttackerCount) const;
};
