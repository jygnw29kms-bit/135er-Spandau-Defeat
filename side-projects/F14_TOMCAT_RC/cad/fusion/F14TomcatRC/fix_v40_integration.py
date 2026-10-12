from pathlib import Path

FILES = [
    Path(r'C:\Users\dezen\Desktop\135er-Spandau-Defeat\side-projects\F14_TOMCAT_RC\cad\fusion\F14TomcatRC\F14TomcatRC.py'),
    Path(r'C:\Users\dezen\AppData\Roaming\Autodesk\Autodesk Fusion 360\API\AddIns\F14TomcatRC\F14TomcatRC.py'),
]

HELPER = r'''

def _link_rod_body_v37(root,name,p1,p2,zcenter,width=4.0,height=4.0):
    x1,y1=p1; x2,y2=p2; dx=x2-x1; dy=y2-y1; L=math.hypot(dx,dy)
    if L<1e-6: raise RuntimeError('zero length linkage')
    nx=-dy/L*width/2.0; ny=dx/L*width/2.0
    poly=[(x1+nx,y1+ny),(x2+nx,y2+ny),(x2-nx,y2-ny),(x1-nx,y1-ny)]
    return extrude_poly(root,name,poly,zcenter-height/2.0,height)
'''

for path in FILES:
    s = path.read_text(encoding='utf-8-sig')
    if 'def _link_rod_body_v37(' not in s:
        pos = s.index('def build_inboard_sweep_crank_scan_v38():')
        s = s[:pos] + HELPER + '\n' + s[pos:]

    start = s.index('def build_moment_arm_optimized_packaging_v40():')
    after = s.index('\ndef build_project_revision():', start)
    block = s[start:after]

    old = """    design=adsk.fusion.Design.cast(_app.activeProduct); root=design.rootComponent if design else None\n    if not root or not any(b.name=='REF_UPC_FUSELAGE_OUTER_OML_v37' for b in root.bRepBodies):\n        build_inboard_sweep_crank_scan_v38()\n        design=adsk.fusion.Design.cast(_app.activeProduct); root=design.rootComponent\n    _app.activeDocument.name='F14_v40_MOMENT_ARM_OPTIMIZED_PACKAGING'\n"""
    new = """    # Rebuild the verified fixed structure directly; v40 no longer depends on the removed v37 scan function.\n    build_sweep_servo_packaging_review_v35()\n    design=adsk.fusion.Design.cast(_app.activeProduct); root=design.rootComponent\n    _app.activeDocument.name='F14_v40_MOMENT_ARM_OPTIMIZED_PACKAGING'\n"""
    if old in block:
        block = block.replace(old, new, 1)

    old2 = """    factor=900.0/(2.0*data['sections'][-1]['wbl_in']); px=pivot['derived_full_scale_pivot_fs_in']*factor; py=pivot['derived_full_scale_pivot_bl_in']*factor\n    outer=next(b for b in root.bRepBodies if b.name=='REF_UPC_FUSELAGE_OUTER_OML_v37')\n"""
    new2 = """    factor=900.0/(2.0*data['sections'][-1]['wbl_in']); px=pivot['derived_full_scale_pivot_fs_in']*factor; py=pivot['derived_full_scale_pivot_bl_in']*factor\n    s0,s1=data['sections'][0],data['sections'][1]; dz=(s1['reference_vertical_wl_in']-s0['reference_vertical_wl_in'])/(s1['wbl_in']-s0['wbl_in']); pz=(s0['reference_vertical_wl_in']+(pivot['derived_full_scale_pivot_bl_in']-s0['wbl_in'])*dz)*factor\n    outer=build_upc_fuselage_oml(root); outer.name='REF_UPC_FUSELAGE_OUTER_OML_v40'; move=root.features.moveFeatures; coll=adsk.core.ObjectCollection.create(); coll.add(outer); tr=adsk.core.Matrix3D.create(); tr.translation=adsk.core.Vector3D.create(0,0,mm(pz)); mi=move.createInput2(coll); mi.defineAsFreeMove(tr); move.add(mi); outer.opacity=0.03\n"""
    if old2 in block:
        block = block.replace(old2, new2, 1)
    else:
        block = block.replace("outer=next(b for b in root.bRepBodies if b.name=='REF_UPC_FUSELAGE_OUTER_OML_v37')", "outer=next(b for b in root.bRepBodies if b.name=='REF_UPC_FUSELAGE_OUTER_OML_v40')")

    s = s[:start] + block + s[after:]
    path.write_text(s, encoding='utf-8')
    print('fixed', path)
