import unreal
cls=unreal.WorldPartitionEditorSubsystem
for n in sorted(dir(cls)):
    if "load" in n.lower() or "region" in n.lower() or "actor" in n.lower():
        unreal.log("[WPAPI] "+n)
