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


def _sgn(v):
    return -1.0 if v < 0 else 1.0

def upc_section_profile(comp, x_mm, half_w, ztop, zbot, frac, name):
    pl = offset_plane(comp, comp.yZConstructionPlane, x_mm)
    sk = comp.sketches.add(pl)
    sk.name = name
    pts = []

    # Forward fuselage: rounded / teardrop sections based on UPC examples 1-3.
    if frac < 0.30:
        n = 24
        cx = 0.0
        cz = (ztop + zbot) * 0.5
        h = max(1.0, (ztop - zbot) * 0.5)
        expo = 2.0 + max(0.0, (frac-0.18)/0.12) * 0.6
        pear = max(0.0, min(1.0, (frac-0.10)/0.18)) * 0.16
        for i in range(n):
            t = 2.0*math.pi*i/n
            ct, st = math.cos(t), math.sin(t)
            y = half_w * _sgn(ct) * (abs(ct) ** (2.0/expo))
            z = cz + h * _sgn(st) * (abs(st) ** (2.0/2.15))
            # UPC section 3 is slightly broader in the lower half.
            if st < 0:
                y *= (1.0 + pear * abs(st))
            pts.append((y,z))
    else:
        # Center/aft body: broad upper deck with twin lower nacelle lobes,
        # matching UPC section examples 4-7 and Grumman cutaway architecture.
        count = 15
        H = max(2.0, ztop-zbot)
        lobe = max(0.0, min(1.0, (frac-0.32)/0.18))
        aft = max(0.0, min(1.0, (frac-0.68)/0.20))
        # upper surface left -> right
        for i in range(count):
            u = -1.0 + 2.0*i/(count-1)
            edge_drop = H*(0.12 + 0.05*aft)*(abs(u)**2.8)
            center_crown = H*0.025*(1.0-aft)*math.exp(-((u)/0.28)**2)
            z = ztop - edge_drop + center_crown
            pts.append((u*half_w,z))
        # lower surface right -> left
        for i in range(count):
            u = 1.0 - 2.0*i/(count-1)
            # Elliptic baseline for transition from nose/body.
            ell = zbot + H*0.28*(1.0-math.sqrt(max(0.0,1.0-u*u)))
            # Twin nacelle lobes: minima around +/- 0.55 span.
            bell = math.exp(-((abs(u)-0.55)/0.23)**2)
            twins = zbot + H*(0.36*(1.0-bell))
            z = ell*(1.0-lobe) + twins*lobe
            pts.append((u*half_w,z))

    lines = sk.sketchCurves.sketchLines
    p3=[adsk.core.Point3D.create(mm(y),mm(z),0) for y,z in pts]
    for i in range(len(p3)):
        lines.addByTwoPoints(p3[i], p3[(i+1)%len(p3)])
    if sk.profiles.count < 1:
        raise RuntimeError('No closed profile at '+name)
    return sk.profiles.item(0)

def build_upc_fuselage_oml(comp):
    # 30 stations extracted from UPC Figure 5.3 fuselage-only guide contours,
    # with drawing scale derived from longitudinal dimension. Selected stations
    # below preserve all geometry changes while keeping the loft numerically stable.
    st = [
      (8.793,8.401,25.046,-23.248,0.010000),
      (38.507,19.602,36.703,-23.248,0.043793),
      (68.220,25.202,41.699,-24.913,0.077586),
      (97.934,32.670,53.357,-23.248,0.111379),
      (127.648,34.537,70.010,-23.248,0.145172),
      (157.362,38.270,81.667,-21.582,0.178966),
      (187.075,38.270,88.328,-21.582,0.212759),
      (216.789,38.270,89.993,-21.582,0.246552),
      (246.503,40.137,89.993,-19.917,0.280345),
      (276.216,83.075,86.663,-18.252,0.314138),
      (305.930,86.808,83.332,-16.586,0.347931),
      (335.644,96.143,76.671,-16.586,0.381724),
      (365.358,107.344,71.675,-14.921,0.415517),
      (395.071,120.411,65.014,-28.244,0.449310),
      (424.785,133.479,60.018,-31.574,0.483103),
      (454.499,144.680,56.687,-33.240,0.516897),
      (484.213,159.615,53.357,-34.905,0.550690),
      (513.926,159.615,56.687,-36.570,0.584483),
      (543.640,150.281,56.687,-36.570,0.618276),
      (573.354,135.346,53.357,-38.236,0.652069),
      (603.067,114.811,46.695,-39.901,0.685862),
      (632.781,109.210,45.030,-39.901,0.719655),
      (662.495,109.210,38.369,-39.901,0.753448),
      (692.209,112.944,45.030,-36.570,0.787241),
      (721.922,112.944,50.026,-34.905,0.821034),
      (751.636,112.944,51.691,-31.574,0.854828),
      (781.350,111.077,53.357,-29.909,0.888621),
      (811.064,105.477,51.691,-28.244,0.922414),
      (840.777,98.009,40.034,-24.913,0.956207),
      (870.491,19.602,33.373,-19.917,0.990000)
    ]

    # Add explicit nose/tail closure stations derived from the same guide.
    sections=[]
    sections.append(upc_section_profile(comp, 0.5, 0.8, 1.0, -1.0, 0.0, 'OML_STA_00_NOSE'))
    # Stable first-pass loft: preserve all major shape transitions with 16 stations.
    # The remaining source stations stay in the dataset for the later refinement pass.
    selected=[0,2,4,6,8,9,11,13,15,17,19,21,23,25,27,29]
    for idx in selected:
        x,w,zt,zb,f=st[idx]
        sections.append(upc_section_profile(comp,x,w,zt,zb,f,'OML_STA_%02d'%(idx+1)))
    sections.append(upc_section_profile(comp, 879.0, 1.2, 1.2, -1.2, 1.0, 'OML_STA_31_TAIL'))

    lofts=comp.features.loftFeatures
    li=lofts.createInput(adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
    try:
        li.isSolid=True
    except:
        pass
    for prof in sections:
        li.loftSections.add(prof)
    feat=lofts.add(li)
    body=feat.bodies.item(0)
    body.name='OML_F14_Fuselage_UPC_NASA_v02'
    return body


def _bernstein_shape(weights, x):
    n=len(weights)-1
    s=0.0
    for i,a in enumerate(weights):
        s += math.comb(n,i)*(x**i)*((1.0-x)**(n-i))*a
    return s

def _kulfan_surface(weights, x, te=0.0):
    c=(x**0.5)*(1.0-x)
    return c*_bernstein_shape(weights,x) + x*te

def _airfoil_points_64a2(chord, target_tc, base_tc, upper_w, lower_w, x_le, z0, side_sign):
    # Preserve the source 64A2xx mean line while scaling only thickness to the
    # F-14 modified t/c value. Coordinates are returned in local X/Z, LE->TE.
    n=28
    xs=[0.5*(1.0-math.cos(math.pi*i/(n-1))) for i in range(n)]
    upper=[]; lower=[]
    thick_scale=target_tc/base_tc
    for x in xs:
        zu=_kulfan_surface(upper_w,x)
        zl=_kulfan_surface(lower_w,x)
        cam=0.5*(zu+zl)
        ht=0.5*(zu-zl)*thick_scale
        upper.append((x_le+x*chord, z0+(cam+ht)*chord))
        lower.append((x_le+x*chord, z0+(cam-ht)*chord))
    # closed loop: upper LE->TE, lower TE->LE
    return upper + list(reversed(lower[1:-1]))

def _wing_profile(comp, y_mm, chord, x_le, z0, target_tc, base_tc, upper_w, lower_w, name):
    pl=offset_plane(comp, comp.xZConstructionPlane, y_mm)
    sk=comp.sketches.add(pl)
    sk.name=name
    pts=_airfoil_points_64a2(chord,target_tc,base_tc,upper_w,lower_w,x_le,z0,1)
    lines=sk.sketchCurves.sketchLines
    p3=[adsk.core.Point3D.create(mm(x),mm(z),0) for x,z in pts]
    for i in range(len(p3)):
        lines.addByTwoPoints(p3[i],p3[(i+1)%len(p3)])
    if sk.profiles.count < 1:
        raise RuntimeError('Wing profile failed: '+name)
    return sk.profiles.item(0)

def build_f14_wings_20deg(comp):
    # Source-derived planform at 20 deg:
    # model semi-span 450 mm, pivot ~131 mm off centerline,
    # moving panel span ~319 mm. Root/tip chords are scaled from UPC R16/R1.
    y_root=131.0
    y_tip=450.0
    x_pivot=456.5
    root_chord=150.15
    tip_chord=55.03
    root_le=x_pivot-20.4
    tip_le=root_le + math.tan(math.radians(20.0))*(y_tip-y_root)
    z0=24.0

    # NACA 64-209 / 64-208 source CST fits; thickness retargeted to
    # F-14 documented 9.65% root / 8.91% tip.
    uw209=[0.11603056427596212,0.1221831985903175,0.14569445059273395,0.15187329121866566,0.16821063372565392,0.12581229172102626,0.14460556285103654,0.09572214274084084]
    lw209=[-0.09252580099967013,-0.04411757018853195,-0.1468033219647228,-0.025619131557749503,-0.17924222156450426,0.017548471454630912,-0.1093358596796878,0.06891061845030363]
    uw208=[0.1037483013223243,0.11163882731154225,0.13100860020540298,0.13929561348524827,0.15206889414828856,0.11841801406862197,0.13243804132932127,0.09458996022426132]
    lw208=[-0.07974653747374771,-0.04151259245179602,-0.1184791315732224,-0.031231426490673352,-0.14504634440409728,0.01196214257455671,-0.09080186678104861,0.06779684153442182]

    bodies=[]
    for sign,label in [(1,'R'),(-1,'L')]:
        yr=sign*y_root
        yt=sign*y_tip
        pr=_wing_profile(comp,yr,root_chord,root_le,z0,0.0965,0.090,uw209,lw209,'WING_'+label+'_ROOT_64A20965')
        pt=_wing_profile(comp,yt,tip_chord,tip_le,z0,0.0891,0.080,uw208,lw208,'WING_'+label+'_TIP_64A20891')
        lofts=comp.features.loftFeatures
        li=lofts.createInput(adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
        li.loftSections.add(pr)
        li.loftSections.add(pt)
        feat=lofts.add(li)
        body=feat.bodies.item(0)
        body.name='OML_Wing_'+label+'_20deg_64A2xx'
        bodies.append(body)

    # Pivot reference cylinders: 12 mm nominal metallic pivot envelope.
    for sign,label in [(1,'R'),(-1,'L')]:
        pl=offset_plane(comp,comp.xYConstructionPlane,8.0)
        sk=comp.sketches.add(pl)
        c=adsk.core.Point3D.create(mm(x_pivot),mm(sign*y_root),0)
        sk.sketchCurves.sketchCircles.addByCenterRadius(c,mm(6.0))
        if sk.profiles.count:
            ex=comp.features.extrudeFeatures
            ei=ex.createInput(sk.profiles.item(0),adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
            ei.setDistanceExtent(False,adsk.core.ValueInput.createByReal(mm(32.0)))
            f=ex.add(ei)
            f.bodies.item(0).name='REF_WingPivot_'+label+'_12mm'
            f.bodies.item(0).opacity=0.25
    return bodies


def build_f14_tail_surfaces(comp):
    bodies=[]

    # NASA CR-163098 Fig.4 stabilator outline, lower side extracted from the
    # calibrated plan view. Mirrored about aircraft centerline for the opposite side.
    stab_lower=[
        (841.45,-209.79),
        (802.38,-224.73),
        (662.14,-104.09),
        (750.29,-72.06),
        (804.39,-76.33),
        (825.42,-112.63)
    ]
    stab_upper=[(x,-y) for x,y in stab_lower]
    for pts,label in [(stab_lower,'L'),(stab_upper,'R')]:
        b=extrude_poly(comp,'OML_Stabilator_'+label,pts,-2.75,5.5)
        bodies.append(b)

    # NASA side-view outer fin outline. Values are calibrated in model mm.
    # Twin fins are placed using the NASA front-view spacing (~78 mm from CL).
    vtail=[(595.5,18.9),(690.0,124.4),(725.3,135.6),(742.8,-5.6)]
    for side,label in [(-1,'L'),(1,'R')]:
        y=side*78.0
        pl=offset_plane(comp,comp.xZConstructionPlane,y-2.25)
        sk=comp.sketches.add(pl)
        sk.name='OML_VTail_'+label+'_Profile'
        p3=[adsk.core.Point3D.create(mm(x),mm(z),0) for x,z in vtail]
        ln=sk.sketchCurves.sketchLines
        for i in range(len(p3)):
            ln.addByTwoPoints(p3[i],p3[(i+1)%len(p3)])
        if sk.profiles.count:
            ex=comp.features.extrudeFeatures
            ei=ex.createInput(sk.profiles.item(0),adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
            ei.setDistanceExtent(False,adsk.core.ValueInput.createByReal(mm(4.5)))
            f=ex.add(ei)
            f.bodies.item(0).name='OML_VTail_'+label
            bodies.append(f.bodies.item(0))

    # Ventral-fin external envelope scaled from UPC VF-1 and placed under nacelles.
    # Outer geometry is conservative and will be cross-checked against NASA side photos.
    sf=900.0/1629.17
    vf_len=239.75*sf
    vf_depth=35.39*sf
    # planform in XZ side view, aft of nacelles
    x0=690.0
    vf=[(x0, -31.0),(x0+0.15*vf_len,-31.0-vf_depth),
        (x0+0.92*vf_len,-31.0-0.25*vf_depth),(x0+vf_len,-31.0)]
    for side,label in [(-1,'L'),(1,'R')]:
        y=side*76.0
        pl=offset_plane(comp,comp.xZConstructionPlane,y-1.6)
        sk=comp.sketches.add(pl)
        sk.name='OML_VentralFin_'+label+'_Profile'
        p3=[adsk.core.Point3D.create(mm(x),mm(z),0) for x,z in vf]
        ln=sk.sketchCurves.sketchLines
        for i in range(len(p3)):
            ln.addByTwoPoints(p3[i],p3[(i+1)%len(p3)])
        if sk.profiles.count:
            ex=comp.features.extrudeFeatures
            ei=ex.createInput(sk.profiles.item(0),adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
            ei.setDistanceExtent(False,adsk.core.ValueInput.createByReal(mm(3.2)))
            f=ex.add(ei)
            f.bodies.item(0).name='OML_VentralFin_'+label
            bodies.append(f.bodies.item(0))
    return bodies

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

    # Build the first source-derived 3D fuselage OML from UPC/NASA station data.
    fuselage = build_upc_fuselage_oml(root)
    wings = build_f14_wings_20deg(root)
    tails = build_f14_tail_surfaces(root)
    # Hide construction sketches after OML creation so the solids can be inspected.
    for sk in root.sketches:
        try: sk.isVisible = False
        except: pass

    outdir=r'C:\Users\dezen\Desktop\135er-Spandau-Defeat\side-projects\F14_TOMCAT_RC\cad\exports'
    os.makedirs(outdir,exist_ok=True)
    try:
        em=design.exportManager
        opt=em.createFusionArchiveExportOptions(os.path.join(outdir,'F14_Tomcat_RC_OML_Tails_v04.f3d'))
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
