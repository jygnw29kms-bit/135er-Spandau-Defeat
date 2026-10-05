"""Reproducible topology checks for raster-derived source contours, not fidelity."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def orient(a, b, c):
    return (b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0])


def on_segment(a, b, p):
    return abs(orient(a, b, p)) < 1e-9 and all(min(a[i], b[i])-1e-9 <= p[i] <= max(a[i], b[i])+1e-9 for i in (0, 1))


def contact(a, b, c, d):
    return (orient(a,b,c)*orient(a,b,d)<0 and orient(c,d,a)*orient(c,d,b)<0) or any([
        on_segment(a,b,c), on_segment(a,b,d), on_segment(c,d,a), on_segment(c,d,b)])


def edges(loop):
    return list(zip(loop, loop[1:]+loop[:1]))


def strictly_inside(point, loop):
    if any(on_segment(a,b,point) for a,b in edges(loop)):
        return False
    return sum(1 for a,b in edges(loop) if (a[1]>point[1])!=(b[1]>point[1]) and
               point[0]<(b[0]-a[0])*(point[1]-a[1])/(b[1]-a[1])+a[0]) % 2 == 1


def validate(outer, holes):
    for loop in [outer]+holes:
        if len(loop)<3 or len(set(map(tuple,loop)))!=len(loop):
            raise ValueError('Degenerate or repeated vertices')
        n=len(loop)
        pairs=edges(loop)
        for i,(a,b) in enumerate(pairs):
            for j,(c,d) in enumerate(pairs[i+1:],i+1):
                if j==i+1 or (i==0 and j==n-1): continue
                if contact(a,b,c,d): raise ValueError('Non-adjacent edge contact')
    for index,hole in enumerate(holes):
        if not all(strictly_inside(p,outer) for p in hole):
            raise ValueError('Opening outside or touching outer contour')
        for other in [outer]+holes[:index]:
            if any(contact(a,b,c,d) for a,b in edges(hole) for c,d in edges(other)):
                raise ValueError('Opening contours intersect or touch')
        for other in holes[:index]:
            if strictly_inside(hole[0],other) or strictly_inside(other[0],hole):
                raise ValueError('Nested openings')
    return dict(vertices=[len(v) for v in [outer]+holes], opening_count=len(holes),
                status='PASS', source_fidelity_verified=False, metric_registration_verified=False)


def run():
    box=[[0,0],[10,0],[10,10],[0,10]]
    hole=[[2,2],[3,2],[3,3],[2,3]]
    validate(box,[hole])
    assert strictly_inside([5,5],box)==strictly_inside([5,5],box[::-1])
    assert not strictly_inside([0,5],box)
    for bad in [[[0,0],[10,10],[0,10],[10,0]], [[0,0],[10,0],[10,10],[10,0]]]:
        try: validate(bad,[])
        except ValueError: pass
        else: raise AssertionError('Invalid loop was accepted')
    report=dict(independent_checks='PASS: interior, reversed winding, boundary, crossed loop, duplicate vertex', contours={})
    for filename in ['upc_C_intake_topology_v13.json','upc_F_connected_section_v11.json']:
        data=json.loads((ROOT/filename).read_text())
        outer=data.get('outer_skin_pixel_outline',data.get('pixel_outline'))
        report['contours'][filename]=validate(outer,data.get('inner_opening_pixel_loops',[]))
    (ROOT/'source_contour_topology_v13.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report))


if __name__=='__main__': run()
