import unreal
for n in sorted(dir(unreal)):
    if "WorldPartition" in n or "Partition" in n and "World" in n:
        unreal.log("[WPNAME] "+n)
