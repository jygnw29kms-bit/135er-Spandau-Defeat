import unreal, os, glob, math, traceback
LAT=52.5524034
LON=13.1668941
HALF=900.0
STEP=10
DGM=r"C:\Users\dezen\Documents\Unreal Projects\SpandauStrike\DerivedData\DGM1_FalkenhagenerFeld"
EXT="/ShooterMaps/__ExternalActors__/Maps/SpandauStrikeGIS/falkenhagener_feld"
MR="/ShooterMaps/Maps/SpandauStrikeGIS/Assets/M_Falkenhagener_Road"
MW="/ShooterMaps/Maps/SpandauStrikeGIS/Assets/M_Falkenhagener_Water"
def log(s): unreal.log("[OSMZ] "+str(s))
def utm(lat,lon):
    a=6378137.0; f=1/298.257223563; k=.9996
    e2=f*(2-f); ep=e2/(1-e2); p=math.radians(lat); l=math.radians(lon); l0=math.radians(15)
    n=a/math.sqrt(1-e2*math.sin(p)**2); t=math.tan(p)**2; c=ep*math.cos(p)**2; aa=math.cos(p)*(l-l0)
    m=a*((1-e2/4-3*e2**2/64-5*e2**3/256)*p-(3*e2/8+3*e2**2/32+45*e2**3/1024)*math.sin(2*p)+(15*e2**2/256+45*e2**3/1024)*math.sin(4*p)-(35*e2**3/3072)*math.sin(6*p))
    return (k*n*(aa+(1-t+c)*aa**3/6+(5-18*t+t*t+72*c-58*ep)*aa**5/120)+500000,
            k*(m+n*math.tan(p)*(aa*aa/2+(5-t+9*c+4*c*c)*aa**4/24+(61-58*t+t*t+600*c-330*ep)*aa**6/720)))
OE,ON=utm(LAT,LON)
def load_dgm():
    pts={}
    emin,emax=OE-HALF-30,OE+HALF+30
    nmin,nmax=ON-HALF-30,ON+HALF+30
    for fn in glob.glob(os.path.join(DGM,"**","*.xyz"),recursive=True):
        with open(fn,"r",encoding="utf-8",errors="ignore") as f:
            for line in f:
                try: e,n,z=map(float,line.split()[:3])
                except: continue
                if not (emin<=e<=emax and nmin<=n<=nmax): continue
                ei=int(round(e-0.5)); ni=int(round(n-0.5))
                if ei%STEP or ni%STEP: continue
                pts[(ei,ni)]=z
    ck=min(pts,key=lambda q:(q[0]-OE)**2+(q[1]-ON)**2)
    return pts,pts[ck]
def terrain_z(grid,e,n,default):
    ex=int(round(e/STEP)*STEP); ny=int(round(n/STEP)*STEP)
    v=grid.get((ex,ny))
    if v is not None: return v
    best=None; bd=1e30
    for dx in (-STEP,0,STEP):
        for dy in (-STEP,0,STEP):
            q=grid.get((ex+dx,ny+dy))
            if q is not None and dx*dx+dy*dy<bd: best=q; bd=dx*dx+dy*dy
    return default if best is None else best
def main():
    grid,zref=load_dgm()
    log("grid=%d zref=%.3f"%(len(grid),zref))
    reg=unreal.AssetRegistryHelpers.get_asset_registry()
    assets=reg.get_assets_by_path(EXT,recursive=True)
    roadmat=unreal.EditorAssetLibrary.load_asset(MR)
    watermat=unreal.EditorAssetLibrary.load_asset(MW)
    roads=waters=changed=0
    zmin=1e30; zmax=-1e30
    for a in assets:
        lab=str(a.get_tag_value("ActorLabel") or "")
        isroad=lab.startswith("GIS_Road_")
        iswater=lab.startswith("GIS_Water_")
        if not (isroad or iswater): continue
        obj=a.get_asset()
        if not obj: continue
        loc=obj.get_actor_location()
        e=OE+loc.x/100.0
        n=ON-loc.y/100.0
        ground=(terrain_z(grid,e,n,zref)-zref)*100.0
        target=ground+(4.5 if isroad else 2.0)
        obj.set_actor_location(unreal.Vector(loc.x,loc.y,target),False,True)
        comp=obj.static_mesh_component
        comp.set_material(0,roadmat if isroad else watermat)
        comp.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION)
        comp.set_collision_profile_name("NoCollision")
        obj.modify(); comp.modify()
        changed+=1
        roads+=1 if isroad else 0
        waters+=1 if iswater else 0
        zmin=min(zmin,target); zmax=max(zmax,target)
        if changed%500==0:
            unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True,True)
            log("saved batch %d"%changed)
    ok=unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True,True)
    log("roads=%d water=%d changed=%d zrange_cm=%.1f..%.1f save=%s"%(roads,waters,changed,zmin,zmax,ok))
    log("OSMZ_READY")
if __name__=="__main__":
    try: main()
    except Exception as e:
        unreal.log_error("[OSMZ] FAILED "+str(e)); unreal.log_error(traceback.format_exc()); raise
