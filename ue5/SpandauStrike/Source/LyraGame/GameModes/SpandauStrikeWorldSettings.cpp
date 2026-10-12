// Copyright Epic Games, Inc. All Rights Reserved.

#include "SpandauStrikeWorldSettings.h"
#include "LyraExperienceDefinition.h"

ASpandauStrikeWorldSettings::ASpandauStrikeWorldSettings(const FObjectInitializer& ObjectInitializer)
    : Super(ObjectInitializer)
{
    DefaultGameplayExperience = TSoftClassPtr<ULyraExperienceDefinition>(
        FSoftObjectPath(TEXT("/ShooterCore/Experiences/B_LyraShooterGame_ControlPoints.B_LyraShooterGame_ControlPoints_C")));
}
