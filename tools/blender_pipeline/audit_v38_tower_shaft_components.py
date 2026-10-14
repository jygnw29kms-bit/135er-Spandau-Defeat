import bpy
from collections import defaultdict, deque
o=bpy.data.objects.get('SM_TowerShaft')
me=o.data
adj=defaultdict(set)
for p in me.polygons:
    vs=list(p.vertices)
    for a,b in zip(vs,vs[1:]+vs[:1]): adj[a].add(b);adj[b].add(a)
un=set(range(len(me.vertices))); comps=[]
while un:
    s=next(iter(un));q=[s];un.remove(s);cc=[]
    while q:
        i=q.pop();cc.append(i)
        for j in adj[i]:
            if j in un:un.remove(j);q.append(j)
    comps.append(cc)
print('SHAFT', 'verts',len(me.vertices),'polys',len(me.polygons),'mats',[m.name if m else None for m in me.materials],'components',len(comps))
for k,cc in enumerate(sorted(comps,key=len,reverse=True)[:50]):
    pts=[me.vertices[i].co for i in cc]
    mins=[min(p[a] for p in pts) for a in range(3)];maxs=[max(p[a] for p in pts) for a in range(3)]
    print('COMP',k,'verts',len(cc),'min',tuple(round(x,3) for x in mins),'max',tuple(round(x,3) for x in maxs),'size',tuple(round(maxs[a]-mins[a],3) for a in range(3)))
