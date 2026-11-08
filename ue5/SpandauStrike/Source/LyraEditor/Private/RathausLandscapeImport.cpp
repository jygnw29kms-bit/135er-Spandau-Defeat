#include "Landscape.h"
#include "LandscapeProxy.h"
#include "Editor.h"
#include "HAL/IConsoleManager.h"
#include "Misc/FileHelper.h"
#include "Misc/Paths.h"
#include "Engine/World.h"
#include "EngineUtils.h"

// Editor-only, explicit command. Never modifies an existing landscape or saves a map.
static void ImportRathausR16(const TArray<FString>& Args)
{
    if (!GEditor || !GEditor->GetEditorWorldContext().World() || Args.Num() != 1)
    {
        UE_LOG(LogTemp, Error, TEXT("Rathaus.ImportLandscapeR16 requires one absolute .r16 path and an editor world"));
        return;
    }
    UWorld* World = GEditor->GetEditorWorldContext().World();
    for (TActorIterator<ALandscape> It(World); It; ++It)
    {
        UE_LOG(LogTemp, Error, TEXT("Rathaus landscape already exists; refusing duplicate"));
        return;
    }
    TArray<uint8> Raw;
    if (!FFileHelper::LoadFileToArray(Raw, *Args[0]) || Raw.Num() != 513 * 513 * 2)
    {
        UE_LOG(LogTemp, Error, TEXT("Rathaus R16 missing or wrong size: %s"), *Args[0]);
        return;
    }
    TArray<uint16> Heights;
    Heights.SetNumUninitialized(513 * 513);
    for (int32 I = 0; I < Heights.Num(); ++I)
    {
        Heights[I] = static_cast<uint16>(Raw[2 * I] | (Raw[2 * I + 1] << 8));
    }
    // UE Landscape supports 8 x 8 components of 63 quads: 505 vertices. Resample 513 source.
    TArray<uint16> Resampled;
    Resampled.SetNumUninitialized(505 * 505);
    for (int32 Y = 0; Y < 505; ++Y)
    {
        for (int32 X = 0; X < 505; ++X)
        {
            const int32 SrcX = FMath::RoundToInt(X * 512.0 / 504.0);
            const int32 SrcY = FMath::RoundToInt(Y * 512.0 / 504.0);
            Resampled[Y * 505 + X] = Heights[SrcY * 513 + SrcX];
        }
    }
    ALandscape* Landscape = World->SpawnActor<ALandscape>();
    if (!Landscape)
    {
        UE_LOG(LogTemp, Error, TEXT("Rathaus Landscape spawn failed"));
        return;
    }
    Landscape->SetActorLabel(TEXT("Rathaus_R16_NativeLandscape_Collision"));
    Landscape->SetActorLocation(FVector(-50000.0, -50000.0, 0.0));
    // 504 quads at 198.412698 cm cover exactly 1000 m in X/Y.
    // UE landscape vertices use centimetres, not metres: 100000 cm / 504 quads.
    // UE height encoding: (R16 - 32768) * ZScale / 128; ZScale=100 matches source.
    Landscape->SetActorScale3D(FVector((100000.0 / 504.0), (100000.0 / 504.0), 100.0));
    const FGuid Guid = FGuid::NewGuid();
    TMap<FGuid, TArray<uint16>> HeightMap;
    HeightMap.Add(FGuid(), MoveTemp(Resampled));
    TMap<FGuid, TArray<FLandscapeImportLayerInfo>> Layers;
    Layers.Add(FGuid(), TArray<FLandscapeImportLayerInfo>());
    const TArray<FLandscapeLayer> EditLayers;
    Landscape->Import(Guid, 0, 0, 504, 504, 1, 63, HeightMap, nullptr, Layers,
        ELandscapeImportAlphamapType::Additive, MakeArrayView(EditLayers));
    Landscape->SetActorEnableCollision(true);
    Landscape->MarkPackageDirty();
    UE_LOG(LogTemp, Display, TEXT("Rathaus native R16 Landscape imported (unsaved); validate collision before saving"));
}

static FAutoConsoleCommand RathausImportCommand(
    TEXT("Rathaus.ImportLandscapeR16"),
    TEXT("Import 513x513 R16 into current editor world; refuses existing Landscape, does not save"),
    FConsoleCommandWithArgsDelegate::CreateStatic(&ImportRathausR16));
