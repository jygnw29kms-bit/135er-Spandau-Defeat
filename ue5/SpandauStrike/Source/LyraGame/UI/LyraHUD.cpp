// Copyright Epic Games, Inc. All Rights Reserved.

#include "LyraHUD.h"

#include "AbilitySystemComponent.h"
#include "AbilitySystemGlobals.h"
#include "Async/TaskGraphInterfaces.h"
#include "Components/GameFrameworkComponentManager.h"
#include "Engine/Canvas.h"
#include "Engine/Engine.h"
#include "EngineUtils.h"
#include "SpandauStrike/SpandauCaptureDirector.h"
#include "SpandauStrike/SpandauCapturePoint.h"
#include "UObject/UObjectIterator.h"

#include UE_INLINE_GENERATED_CPP_BY_NAME(LyraHUD)

class AActor;
class UWorld;

ALyraHUD::ALyraHUD(const FObjectInitializer& ObjectInitializer)
    : Super(ObjectInitializer)
{
    PrimaryActorTick.bStartWithTickEnabled = false;
}

void ALyraHUD::PreInitializeComponents()
{
    Super::PreInitializeComponents();
    UGameFrameworkComponentManager::AddGameFrameworkComponentReceiver(this);
}

void ALyraHUD::BeginPlay()
{
    UGameFrameworkComponentManager::SendGameFrameworkComponentExtensionEvent(this, UGameFrameworkComponentManager::NAME_GameActorReady);
    Super::BeginPlay();
}

void ALyraHUD::EndPlay(const EEndPlayReason::Type EndPlayReason)
{
    UGameFrameworkComponentManager::RemoveGameFrameworkComponentReceiver(this);
    Super::EndPlay(EndPlayReason);
}

void ALyraHUD::DrawHUD()
{
    Super::DrawHUD();

    if (!Canvas || !GEngine || !GetWorld())
    {
        return;
    }

    ASpandauCaptureDirector* Director = nullptr;
    for (TActorIterator<ASpandauCaptureDirector> It(GetWorld()); It; ++It)
    {
        Director = *It;
        break;
    }

    if (!Director)
    {
        return;
    }

    UFont* Font = GEngine->GetSmallFont();
    if (!Font)
    {
        return;
    }

    const float CenterX = Canvas->ClipX * 0.5f;
    const float TopY = 42.0f;
    const FString Header = FString::Printf(TEXT("SPANDAU STRIKE   %s"), *Director->GetHUDSummary());
    float XL = 0.0f;
    float YL = 0.0f;
    Canvas->StrLen(Font, Header, XL, YL);
    Canvas->DrawText(Font, Header, CenterX - XL * 0.5f, TopY, 1.0f, 1.0f);

    TArray<ASpandauCapturePoint*> ActivePoints;
    for (TActorIterator<ASpandauCapturePoint> It(GetWorld()); It; ++It)
    {
        ASpandauCapturePoint* Point = *It;
        if (Point && Point->GetSectorIndex() == Director->GetActiveSector())
        {
            ActivePoints.Add(Point);
        }
    }

    ActivePoints.Sort([](const ASpandauCapturePoint& A, const ASpandauCapturePoint& B)
    {
        return A.GetPointIndex() < B.GetPointIndex();
    });

    float Y = TopY + 24.0f;
    for (const ASpandauCapturePoint* Point : ActivePoints)
    {
        if (!Point)
        {
            continue;
        }

        const TCHAR Letter = Point->GetPointIndex() == 1 ? TEXT('A') : TEXT('B');
        const int32 Percent = FMath::RoundToInt(Point->GetCaptureProgress() * 100.0f);
        FString State = TEXT("LOCKED");
        switch (Point->GetCaptureState())
        {
            case ESpandauCaptureState::Active: State = TEXT("ACTIVE"); break;
            case ESpandauCaptureState::Capturing: State = TEXT("CAPTURING"); break;
            case ESpandauCaptureState::Contested: State = TEXT("CONTESTED"); break;
            case ESpandauCaptureState::Captured: State = TEXT("CAPTURED"); break;
            default: break;
        }

        const FString Line = FString::Printf(TEXT("%c  %s  %d%%"), Letter, *State, Percent);
        Canvas->StrLen(Font, Line, XL, YL);
        Canvas->DrawText(Font, Line, CenterX - XL * 0.5f, Y, 1.0f, 1.0f);
        Y += 18.0f;
    }
}

void ALyraHUD::GetDebugActorList(TArray<AActor*>& InOutList)
{
    UWorld* World = GetWorld();
    Super::GetDebugActorList(InOutList);

    for (TObjectIterator<UAbilitySystemComponent> It; It; ++It)
    {
        if (UAbilitySystemComponent* ASC = *It)
        {
            if (!ASC->HasAnyFlags(RF_ClassDefaultObject | RF_ArchetypeObject))
            {
                AActor* AvatarActor = ASC->GetAvatarActor();
                AActor* OwnerActor = ASC->GetOwnerActor();

                if (AvatarActor && UAbilitySystemGlobals::GetAbilitySystemComponentFromActor(AvatarActor))
                {
                    AddActorToDebugList(AvatarActor, InOutList, World);
                }
                else if (OwnerActor && UAbilitySystemGlobals::GetAbilitySystemComponentFromActor(OwnerActor))
                {
                    AddActorToDebugList(OwnerActor, InOutList, World);
                }
            }
        }
    }
}
