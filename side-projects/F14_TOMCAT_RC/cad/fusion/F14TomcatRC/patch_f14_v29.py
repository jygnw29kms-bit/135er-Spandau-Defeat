from pathlib import Path
files=[Path(r'C:\Users\dezen\AppData\Roaming\Autodesk\Autodesk Fusion 360\API\AddIns\F14TomcatRC\F14TomcatRC.py'),Path(r'C:\Users\dezen\AppData\Roaming\Autodesk\Autodesk Fusion 360\API\AddIns\F14TomcatRC_v18\F14TomcatRC_v18.py')]
for path in files:
    s=path.read_text(encoding='utf-8')
    start=s.index('def build_robust_datum_clearance_review_v28():')
    end=s.index('def build_project_revision():',start)
    block=s[start:end]
    new=block.replace('build_robust_datum_clearance_review_v28','build_robust_datum_clearance_review_v29')
    new=new.replace("F14_v28_ROBUST_DATUM_CLEARANCE_REVIEW","F14_v29_ROBUST_DATUM_CLEARANCE_REVIEW")
    new=new.replace("mxy=2.0\n        mz=3.0 if rec['sweep_deg']==68 and rec['kind']=='outer_wing' else 2.0","mxy=3.0 if rec['sweep_deg']==68 and rec['kind']=='outer_wing' else 2.0\n        mz=3.0 if rec['sweep_deg']==68 and rec['kind']=='outer_wing' else 2.0")
    new=new.replace('_v28','_v29').replace('robust_clearance_v28','robust_clearance_v29').replace('F14_v28_robust_datum_clearance','F14_v29_robust_datum_clearance').replace("targeted_extra_z_margin_mm=1.0","targeted_extra_xyz_margin_mm=1.0")
    if 'def build_robust_datum_clearance_review_v29()' not in s: s=s[:end]+new+'\n'+s[end:]
    s=s.replace('return build_robust_datum_clearance_review_v28()','return build_robust_datum_clearance_review_v29()',1)
    path.write_text(s,encoding='utf-8'); print('patched',path)
