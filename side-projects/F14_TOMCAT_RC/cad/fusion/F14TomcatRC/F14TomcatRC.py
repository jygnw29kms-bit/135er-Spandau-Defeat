import adsk.core, adsk.fusion, traceback, math, os

_app = None
_ui = None
_created = False

def mm(v): return v/10.0

def offset_plane(comp, base_plane, dist_mm):
    planes = comp.constructionPlanes
    inp = planes.createInput()
    inp.setByOffset(base_plane, adsk.core.ValueInput.createByReal(mm(dist_mm)))
    return planes.add(inp)

def ellipse_profile(comp, plane, cy, cz, ry, rz):
    sk = comp.sketches.add(plane)
    sk.name = 'section'
    c = adsk.core.Point3D.create(0, mm(cy), mm(cz))
    major = adsk.core.Point3D.create(0, mm(cy+ry), mm(cz))
    p = adsk.core.Point3D.create(0, mm(cy), mm(cz+rz))
    sk.sketchCurves.sketchEllipses.add(c, major, p)
    return sk.profiles.item(0)

def loft_ellipses(comp, name, stations):
    lofts = comp.features.loftFeatures
    li = lofts.createInput(adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
    for x,cy,cz,ry,rz in stations:
        pl = offset_plane(comp, comp.yZConstructionPlane, x)
        li.loftSections.add(ellipse_profile(comp, pl, cy, cz, ry, rz))
    feat = lofts.add(li)
    feat.bodies.item(0).name = name
    return feat.bodies.item(0)

def polygon_profile(comp, plane, pts):
    sk = comp.sketches.add(plane)
    lines = sk.sketchCurves.sketchLines
    ps = [adsk.core.Point3D.create(mm(x),mm(y),0) for x,y in pts]
    for i in range(len(ps)):
        lines.addByTwoPoints(ps[i], ps[(i+1)%len(ps)])
    return sk.profiles.item(0)

def extrude_poly(comp, name, pts, z0, th):
    pl = offset_plane(comp, comp.xYConstructionPlane, z0)
    prof = polygon_profile(comp, pl, pts)
    exts = comp.features.extrudeFeatures
    ei = exts.createInput(prof, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
    ei.setDistanceExtent(False, adsk.core.ValueInput.createByReal(mm(th)))
    f = exts.add(ei)
    f.bodies.item(0).name = name
    return f.bodies.item(0)


def add_reference_polyline(comp, plane, name, pts_mm, axes='xy'):
    sk = comp.sketches.add(plane)
    sk.name = name
    lines = sk.sketchCurves.sketchLines
    ps=[]
    for a,b in pts_mm:
        if axes == 'xy':
            ps.append(adsk.core.Point3D.create(mm(a), mm(b), 0))
        else:
            ps.append(adsk.core.Point3D.create(mm(a), mm(b), 0))
    for i in range(len(ps)-1):
        ln=lines.addByTwoPoints(ps[i], ps[i+1])
        ln.isConstruction = True
    if len(ps)>2:
        ln=lines.addByTwoPoints(ps[-1], ps[0])
        ln.isConstruction = True
    return sk

def nasa_reference_sketches(comp):
    # Digitized directly from NASA CR-163098 Figure 4 raster. Scan distortion is
    # corrected independently in longitudinal and lateral/vertical axes using
    # the printed 26.19 cm, 27.14 cm and 4.09 cm dimensions.
    plan_px=[(788,37),(740,52),(720,86),(734,74),(720,135),(732,64),(789,42),(757,96),(717,341),(643,312),(668,300),(635,300),(631,318),(442,385),(438,425),(279,434),(172,465),(267,492),(441,499),(444,534),(641,602),(736,847),(805,880),(780,556),(826,556),(972,673),(1018,655),(999,558),(973,543),(1018,527),(976,491),(1014,475),(1020,440),(974,415),(1015,382),(964,364),(996,341),(1012,251),(995,236),(1039,230),(969,234),(820,356),(774,360)]
    px0=172.0
    py0=(37.0+880.0)/2.0
    sx=(900.0*(261.9/271.4))/(1039.0-172.0)
    sy=900.0/(880.0-37.0)
    plan=[((x-px0)*sx, -(y-py0)*sy) for x,y in plan_px]
    add_reference_polyline(comp, comp.xYConstructionPlane, 'REF_NASA_F14_PLAN_20DEG', plan, 'xy')

    side_px=[(1179,329),(1005,329),(1039,215),(1017,207),(977,217),(870,312),(807,315),(728,302),(656,307),(585,295),(580,285),(564,292),(426,277),(372,287),(325,313),(245,331),(196,356),(227,370),(280,375),(290,389),(331,388),(353,376),(486,377),(508,395),(511,377),(571,375),(586,387),(591,379),(612,381),(626,393),(629,382),(796,389),(826,411),(1013,371),(1015,356),(1041,352),(1037,334)]
    sx2=(900.0*(261.9/271.4))/(1179.0-196.0)
    waterline_y=329.0
    tail_top_y=207.0
    z_tail=900.0*(40.9/271.4)
    sz=z_tail/(waterline_y-tail_top_y)
    side=[((x-196.0)*sx2, -(y-waterline_y)*sz) for x,y in side_px]
    add_reference_polyline(comp, comp.xZConstructionPlane, 'REF_NASA_F14_SIDE', side, 'xz')

def build_model():
    global _app,_ui
    doc = _app.documents.add(adsk.core.DocumentTypes.FusionDesignDocumentType)
    design = adsk.fusion.Design.cast(_app.activeProduct)
    design.designType = adsk.fusion.DesignTypes.ParametricDesignType
    root = design.rootComponent
    try:
        doc.name = 'F14_Tomcat_RC_4S_900mm'
    except:
        pass

    # Authoritative scale baseline.
    # US Navy: 64 ft 1 in span, 62 ft 8 in overall length, 48 ft 2 in span fully swept.
    # NASA CR-163098 Fig.4: 1/72 model = 27.14 cm span and 26.19 cm aerodynamic airframe length.
    span_full_mm = 19532.6
    length_full_mm = 19100.8
    swept_span_full_mm = 14681.2
    height_full_mm = 4876.8
    span_open = 900.0
    S = span_open/span_full_mm
    L_total = length_full_mm*S
    L = span_open*(261.9/271.4)  # NASA drawing airframe datum, excludes small length-datum discrepancy
    span_swept = swept_span_full_mm*S
    h = height_full_mm*S
    stabilator_span = span_open*(138.5/271.4)

    # User parameters for RC architecture.
    up = design.userParameters
    def addp(n,val,unit,comment):
        try: up.add(n, adsk.core.ValueInput.createByString(str(val)+' '+unit), unit, comment)
        except: pass
    addp('ScaleLengthAirframe', round(L,2), 'mm', 'NASA Fig.4 aerodynamic airframe length')
    addp('ScaleLengthOverall', round(L_total,2), 'mm', 'US Navy scaled overall length')
    addp('ScaleHeight', round(h,2), 'mm', 'US Navy scaled overall height')
    addp('ScaleStabilatorSpan', round(stabilator_span,2), 'mm', 'NASA Fig.4 scaled horizontal-tail span')
    addp('ScaleSpan20', round(span_open,2), 'mm', 'Wing span at 20 deg')
    addp('ScaleSpan68', round(span_swept,2), 'mm', 'Wing span at 68 deg')
    addp('EDF_Diameter', 50, 'mm', 'Twin EDF nominal diameter')
    addp('Battery_Length', 150, 'mm', '4S battery envelope')
    addp('Battery_Width', 45, 'mm', '4S battery envelope')
    addp('Battery_Height', 38, 'mm', '4S battery envelope')
    addp('Skin', 0.8, 'mm', 'Target lightweight FDM skin')
    addp('Carbon_Spar', 6, 'mm', 'Main carbon tube OD')
    addp('Design_AUW', 1050, 'g', 'Baseline design all-up mass')
    addp('Proof_Load_Factor', 6, '', 'Primary proof load factor')
    addp('Design_Check_Load_Factor', 8, '', 'Structural design check load factor')
    addp('Wing_Root_Arm', 250, 'mm', 'Conservative half-aircraft lift resultant arm')
    addp('Battery_Proof_G', 20, '', 'Forward battery restraint proof load')
    addp('Sweep_Stall_Torque', 2.0, 'N*m', 'Conservative sweep actuator stall torque envelope')

    # Authoritative NASA master outlines. These are construction-only references
    # and remain visible for continuous OML comparison while the 3D body is rebuilt.
    nasa_reference_sketches(root)

    # The retired/free-form scaffold is intentionally not generated anymore.
    # From this point onward the 3D OML is rebuilt only from the NASA master
    # outlines and verified cross-sections. Until those sections are frozen,
    # Fusion shows the calibrated master geometry rather than an inaccurate body.
    outdir=r'C:\Users\dezen\Desktop\135er-Spandau-Defeat\side-projects\F14_TOMCAT_RC\cad\exports'
    os.makedirs(outdir,exist_ok=True)
    try:
        em=design.exportManager
        opt=em.createFusionArchiveExportOptions(os.path.join(outdir,'F14_Tomcat_RC_NASA_Master_Ref_v01.f3d'))
        em.execute(opt)
    except:
        pass
    try:
        _app.activeViewport.fit()
    except:
        pass
    return

    # Legacy scaffold below retained temporarily as disabled source only and will
    # be deleted once the true OML surface model replaces it.
    # Longitudinal coordinates: nose x=0, tail x=L.
    # Scale-faithful silhouette scaffold based on F-14 three-view proportions.
    # Nose/cockpit/center-body loft.
    center = [
        (0.0,0,6,1.0,1.0),
        (0.055*L,0,8,18,16),
        (0.14*L,0,12,30,27),
        (0.24*L,0,17,44,34),
        (0.34*L,0,13,58,34),
        (0.45*L,0,7,72,29),
        (0.57*L,0,2,80,24),
        (0.68*L,0,0,67,20)
    ]
    loft_ellipses(root,'OML_Center_Fuselage',center)

    # Twin engine nacelles, spaced and tapered.
    yeng = 79
    for side,label in [(-1,'L'),(1,'R')]:
        st=[
            (0.39*L, side*yeng, -8, 28, 31),
            (0.50*L, side*yeng, -9, 31, 34),
            (0.64*L, side*yeng, -8, 32, 35),
            (0.78*L, side*yeng, -5, 31, 32),
            (0.90*L, side*yeng, 0, 27, 27),
            (0.985*L, side*yeng, 2, 22, 22)
        ]
        loft_ellipses(root,'OML_Engine_'+label,st)

    # Fixed gloves / chines.
    gloveL=[(0.31*L,-42),(0.48*L,-105),(0.64*L,-120),(0.72*L,-72),(0.47*L,-54)]
    gloveR=[(x,-y) for x,y in gloveL]
    extrude_poly(root,'OML_Glove_L',gloveL,-8,15)
    extrude_poly(root,'OML_Glove_R',gloveR,-8,15)

    # Variable-geometry wing planforms at 20 deg; pivot at ~53% length.
    xp=0.525*L
    yp=111
    semi=span_open/2.0
    # Coordinates chosen to preserve F-14 planform proportions at 20 deg.
    left=[(xp,-yp),(0.64*L,-semi),(0.75*L,-semi+35),(0.69*L,-150),(0.56*L,-120)]
    right=[(x,-y) for x,y in left]
    extrude_poly(root,'OML_Wing_L_20deg',left,-2.8,5.6)
    extrude_poly(root,'OML_Wing_R_20deg',right,-2.8,5.6)

    # Horizontal stabilators.
    stab_tip = stabilator_span/2.0
    stabL=[(0.77*L,-62),(0.89*L,-stab_tip),(0.985*L,-0.87*stab_tip),(0.94*L,-64)]
    stabR=[(x,-y) for x,y in stabL]
    extrude_poly(root,'OML_Stabilator_L',stabL,2,4.0)
    extrude_poly(root,'OML_Stabilator_R',stabR,2,4.0)

    # Vertical tails as side silhouettes extruded laterally.
    for side,label in [(-1,'L'),(1,'R')]:
        y = side*83
        pl = offset_plane(root, root.xZConstructionPlane, y-2.2 if side>0 else -y-2.2)
        sk=root.sketches.add(pl)
        p=[(0.70*L,8),(0.79*L,124),(0.89*L,118),(0.92*L,12)]
        ln=sk.sketchCurves.sketchLines
        pts=[adsk.core.Point3D.create(mm(x),mm(z),0) for x,z in p]
        for i in range(len(pts)): ln.addByTwoPoints(pts[i],pts[(i+1)%len(pts)])
        ex=root.features.extrudeFeatures
        ei=ex.createInput(sk.profiles.item(0),adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
        ei.setDistanceExtent(False, adsk.core.ValueInput.createByReal(mm(4.4)))
        f=ex.add(ei); f.bodies.item(0).name='OML_VTail_'+label

    # RC installation envelopes: intentionally separate bodies, hidden-ready.
    # Battery bay near target CG range.
    batt_pts=[(0.42*L,-22),(0.42*L,22),(0.42*L+150,22),(0.42*L+150,-22)]
    b=extrude_poly(root,'RC_Battery_4S_Envelope',batt_pts,-19,38)
    b.opacity=0.35

    # EDF cylinder envelopes (50 mm) aligned longitudinally.
    for side,label in [(-1,'L'),(1,'R')]:
        pl=offset_plane(root,root.yZConstructionPlane,0.59*L)
        sk=root.sketches.add(pl)
        c=adsk.core.Point3D.create(0,mm(side*yeng),mm(-7))
        sk.sketchCurves.sketchCircles.addByCenterRadius(c,mm(25))
        prof=sk.profiles.item(0)
        ex=root.features.extrudeFeatures
        ei=ex.createInput(prof,adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
        ei.setDistanceExtent(False,adsk.core.ValueInput.createByReal(mm(0.26*L)))
        f=ex.add(ei); f.bodies.item(0).name='RC_EDF50_'+label
        f.bodies.item(0).opacity=0.28

    # Wing pivot and carbon spar reference cylinders.
    for side,label in [(-1,'L'),(1,'R')]:
        pl=offset_plane(root,root.xYConstructionPlane,-15)
        sk=root.sketches.add(pl)
        c=adsk.core.Point3D.create(mm(xp),mm(side*yp),0)
        sk.sketchCurves.sketchCircles.addByCenterRadius(c,mm(6))
        prof=sk.profiles.item(0)
        ex=root.features.extrudeFeatures
        ei=ex.createInput(prof,adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
        ei.setDistanceExtent(False,adsk.core.ValueInput.createByReal(mm(30)))
        f=ex.add(ei); f.bodies.item(0).name='RC_WingPivot_'+label

    # Save local F3D snapshot for robust handoff.
    outdir=r'C:\Users\dezen\Desktop\F14_Tomcat_RC'
    os.makedirs(outdir,exist_ok=True)
    try:
        em=design.exportManager
        opt=em.createFusionArchiveExportOptions(os.path.join(outdir,'F14_Tomcat_RC_4S_900mm_v01.f3d'))
        em.execute(opt)
    except:
        pass

    try:
        vp=_app.activeViewport
        vp.fit()
    except:
        pass

def run(context):
    global _app,_ui,_created
    try:
        _app=adsk.core.Application.get()
        _ui=_app.userInterface
        if not _created:
            build_model()
            _created=True
    except:
        if _ui:
            _ui.messageBox('F14TomcatRC error:\n'+traceback.format_exc())

def stop(context):
    pass
