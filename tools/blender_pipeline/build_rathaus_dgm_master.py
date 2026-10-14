import os, json, time, argparse
from pathlib import Path
ap=argparse.ArgumentParser(); ap.add_argument('--extent',type=float,default=1000); ap.add_argument('--grid',type=int,default=513); ap.add_argument('--origin-e',type=float,default=377931.576); ap.add_argument('--origin-n',type=float,default=5822067.058); ap.add_argument('--ground',type=float,default=31.0); ap.add_argument('--label',default='mastercenter'); args=ap.parse_args()
ROOT=Path(r"C:\Users\dezen\Documents\Unreal Projects\SpandauStrike\SourceData\DGM1")
ORIGIN_E=args.origin_e; ORIGIN_N=args.origin_n; GROUND=args.ground; EXT=float(args.extent); HALF=EXT/2; N=int(args.grid)
name=f'rathaus_dgm_{args.label}_{int(EXT)}m_{N}'; OUT=ROOT/(name+'.obj'); META=ROOT/(name+'.json')
MIN_E=ORIGIN_E-HALF;MAX_E=ORIGIN_E+HALF;MIN_N=ORIGIN_N-HALF;MAX_N=ORIGIN_N+HALF;STEP=EXT/(N-1)
FILES=[ROOT/'376_5820'/'dgm1_33_376_5820_2_be.xyz',ROOT/'378_5820'/'dgm1_33_378_5820_2_be.xyz',ROOT/'376_5822'/'dgm1_33_376_5822_2_be.xyz',ROOT/'378_5822'/'dgm1_33_378_5822_2_be.xyz']
sums=[[0.0]*N for _ in range(N)];counts=[[0]*N for _ in range(N)];t0=time.time();per=[]
for fn in FILES:
    kept=scanned=0
    with open(fn,'r',encoding='ascii',errors='ignore',buffering=4*1024*1024) as f:
        for line in f:
            scanned+=1
            try: xs,ys,zs=line.split();x=float(xs);y=float(ys)
            except: continue
            if x<MIN_E or x>MAX_E or y<MIN_N or y>MAX_N: continue
            z=float(zs);i=int(round((x-MIN_E)/STEP));j=int(round((y-MIN_N)/STEP))
            if 0<=i<N and 0<=j<N:sums[j][i]+=z;counts[j][i]+=1;kept+=1
    per.append({'file':str(fn),'scanned':scanned,'kept':kept});print(fn.name,'kept',kept,flush=True)
heights=[[sums[j][i]/counts[j][i] if counts[j][i] else None for i in range(N)] for j in range(N)]
missing0=sum(h is None for row in heights for h in row)
for _ in range(12):
    changed=0;nxt=[row[:] for row in heights]
    for j in range(N):
        for i in range(N):
            if heights[j][i] is not None:continue
            vals=[]
            for dj in (-1,0,1):
                for di in (-1,0,1):
                    if di==0 and dj==0:continue
                    yy=j+dj;xx=i+di
                    if 0<=xx<N and 0<=yy<N and heights[yy][xx] is not None:vals.append(heights[yy][xx])
            if vals:nxt[j][i]=sum(vals)/len(vals);changed+=1
    heights=nxt
    if not changed:break
valid=[h for row in heights for h in row if h is not None];fallback=sum(valid)/len(valid)
for j in range(N):
    for i in range(N):
        if heights[j][i] is None:heights[j][i]=fallback
ci=(N-1)//2;center=heights[ci][ci]
with open(OUT,'w',encoding='ascii',newline='\n',buffering=4*1024*1024) as o:
    o.write(f'# 135er Spandau Strike Rathaus DGM1 {int(EXT)}m master terrain; local origin EPSG25833 {ORIGIN_E},{ORIGIN_N}\n');o.write(f'o SM_Rathaus_DGM1_{args.label}_{int(EXT)}m_{N}\n')
    for j in range(N):
        y=MIN_N+j*STEP-ORIGIN_N
        for i in range(N):
            x=MIN_E+i*STEP-ORIGIN_E;z=heights[j][i]-GROUND;o.write(f'v {x:.4f} {y:.4f} {z:.4f}\n')
    for j in range(N):
        v=j/(N-1)
        for i in range(N):o.write(f'vt {i/(N-1):.7f} {v:.7f}\n')
    for j in range(N-1):
        for i in range(N-1):
            a=j*N+i+1;b=a+1;c=a+N;d=c+1;o.write(f'f {a}/{a} {c}/{c} {b}/{b}\n');o.write(f'f {b}/{b} {c}/{c} {d}/{d}\n')
meta={'coordinate_frame':'local X=E-originE, Y=N-originN, Z=height-ground','origin_utm_epsg25833':[ORIGIN_E,ORIGIN_N],'ground_reference_m':GROUND,'extent_m':[EXT,EXT],'grid':[N,N],'step_m':STEP,'vertices':N*N,'triangles':2*(N-1)*(N-1),'center_height_abs_m':center,'center_z_world_m':center-GROUND,'min_height_abs_m':min(valid),'max_height_abs_m':max(valid),'initial_missing_cells':missing0,'files':per,'elapsed_s':round(time.time()-t0,2),'obj_bytes':OUT.stat().st_size}
META.write_text(json.dumps(meta,indent=2),encoding='utf-8');print('DGM_MASTER_READY',json.dumps(meta),flush=True)
