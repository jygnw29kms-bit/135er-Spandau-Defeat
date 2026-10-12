import unreal
for n in sorted(dir(unreal)):
    if "hlod" in n.lower():
        unreal.log("[HLODAPI] "+n)
try:
    cls=unreal.HLODLayer
    unreal.log("[HLODAPI] HLODLayer props="+str([x for x in dir(cls) if "layer" in x.lower() or "builder" in x.lower() or "hlod" in x.lower()]))
except Exception as e:
    unreal.log_error("[HLODAPI] "+str(e))
