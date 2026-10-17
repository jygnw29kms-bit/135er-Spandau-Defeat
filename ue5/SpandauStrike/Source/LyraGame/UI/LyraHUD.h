// Copyright Epic Games, Inc. All Rights Reserved.

#pragma once

#include "GameFramework/HUD.h"
#include "LyraHUD.generated.h"

namespace EEndPlayReason { enum Type : int; }

class AActor;
class UObject;

UCLASS(Config = Game)
class ALyraHUD : public AHUD
{
    GENERATED_BODY()

public:
    ALyraHUD(const FObjectInitializer& ObjectInitializer = FObjectInitializer::Get());

protected:
    virtual void PreInitializeComponents() override;
    virtual void BeginPlay() override;
    virtual void EndPlay(const EEndPlayReason::Type EndPlayReason) override;
    virtual void GetDebugActorList(TArray<AActor*>& InOutList) override;
    virtual void DrawHUD() override;
};
