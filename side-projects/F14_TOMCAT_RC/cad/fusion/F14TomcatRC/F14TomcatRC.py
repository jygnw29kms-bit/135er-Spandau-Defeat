import adsk.core, adsk.fusion, traceback, math, os, json, threading, importlib.util

_app = None
_ui = None
_created = False
_handlers = []
_worker_stop = threading.Event()
_event_id = 'com.jl1976.f14tomcatrc.controlled_build'

def mm(v): return v/10.0

def model_point(sketch, x, y, z):
    """Convert explicit aircraft coordinates to Fusion's actual sketch frame."""
    world = adsk.core.Point3D.create(mm(x), mm(y), mm(z))
    local = sketch.modelToSketchSpace(world)
    if abs(local.z) > 1e-6:
        raise RuntimeError('Point is not on sketch plane: '+sketch.name)
    restored = sketch.sketchToModelSpace(local)
    if world.distanceTo(restored) > 1e-6:
        raise RuntimeError('Sketch coordinate round-trip failed: '+sketch.name)
    return local

def axis_plane(comp, axis, coordinate):
    """Offset the matching origin plane using its measured normal, not its name."""
    for base in [comp.xYConstructionPlane, comp.xZConstructionPlane, comp.yZConstructionPlane]:
        normal=base.geometry.normal
        component=getattr(normal,axis)
        if abs(abs(component)-1.0)<1e-8:
            origin=getattr(base.geometry.origin,axis)*10.0
            return offset_plane(comp,base,(coordinate-origin)/component)
    raise RuntimeError('No origin plane normal to '+axis)

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

def polygon_profile(comp, plane, pts, z0=0):
    sk = comp.sketches.add(plane)
    lines = sk.sketchCurves.sketchLines
    ps = [model_point(sk,x,y,z0) for x,y in pts]
    for i in range(len(ps)):
        lines.addByTwoPoints(ps[i], ps[(i+1)%len(ps)])
    return sk.profiles.item(0)

def extrude_poly(comp, name, pts, z0, th):
    pl = axis_plane(comp, 'z', z0)
    prof = polygon_profile(comp, pl, pts, z0)
    exts = comp.features.extrudeFeatures
    ei = exts.createInput(prof, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
    ei.setDistanceExtent(False, adsk.core.ValueInput.createByReal(mm(th)*pl.geometry.normal.z))
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
            ps.append(model_point(sk,a,b,0))
        else:
            ps.append(model_point(sk,a,0,b))
    for i in range(len(ps)-1):
        ln=lines.addByTwoPoints(ps[i], ps[i+1])
        ln.isConstruction = True
    if len(ps)>2:
        ln=lines.addByTwoPoints(ps[-1], ps[0])
        ln.isConstruction = True
    return sk

def nasa_reference_sketches(comp):
    """Independent manually digitized NASA silhouettes; not 3D section data."""
    path=os.path.join(os.path.dirname(__file__),'NASA_F14_reference_trace_v06.json')
    with open(path,encoding='utf-8') as stream:
        data=json.load(stream)
    c=data['calibration']
    length=c['airframe_length_model_mm']
    ax,ay=c['plan_longitudinal_pixel_vector']
    bx,by=c['plan_span_pixel_vector']
    det=ax*by-ay*bx
    nx,ny=c['plan_nose_pixel']
    result=[]
    for name,points in data['traces'].items():
        if name.startswith('plan_'):
            mapped=[]
            for x,y in points:
                dx,dy=x-nx,y-ny
                u=(dx*by-dy*bx)/det
                v=(ax*dy-ay*dx)/det
                mapped.append((u*length,-v*c['span_model_mm']))
            plane=comp.xYConstructionPlane
            axes='xy'
        else:
            x0,x1=c['side_length_dimension_pixels']
            zscale=c['vertical_tail_above_waterline_mm']/(c['side_waterline_pixel_y']-c['side_tail_top_pixel_y'])
            mapped=[((x-x0)*length/(x1-x0),(c['side_waterline_pixel_y']-y)*zscale) for x,y in points]
            plane=comp.xZConstructionPlane
            axes='xz'
        result.append(add_reference_polyline(comp,plane,'REF_NASA_v06_'+name+'_PROVISIONAL',mapped,axes))
    return result


def _sgn(v):
    return -1.0 if v < 0 else 1.0

def upc_section_profile(comp, x_mm, half_w, ztop, zbot, frac, name):
    pl = axis_plane(comp, 'x', x_mm)
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
    p3=[model_point(sk,x_mm,y,z) for y,z in pts]
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
    pl=axis_plane(comp, 'y', y_mm)
    sk=comp.sketches.add(pl)
    sk.name=name
    pts=_airfoil_points_64a2(chord,target_tc,base_tc,upper_w,lower_w,x_le,z0,1)
    lines=sk.sketchCurves.sketchLines
    p3=[model_point(sk,x,y_mm,z) for x,z in pts]
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
        pl=axis_plane(comp,'z',8.0)
        sk=comp.sketches.add(pl)
        c=model_point(sk,x_pivot,sign*y_root,8.0)
        sk.sketchCurves.sketchCircles.addByCenterRadius(c,mm(6.0))
        if sk.profiles.count:
            ex=comp.features.extrudeFeatures
            ei=ex.createInput(sk.profiles.item(0),adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
            ei.setDistanceExtent(False,adsk.core.ValueInput.createByReal(mm(32.0)*pl.geometry.normal.z))
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
        pl=axis_plane(comp,'y',y-2.25)
        sk=comp.sketches.add(pl)
        sk.name='OML_VTail_'+label+'_Profile'
        p3=[model_point(sk,x,y-2.25,z) for x,z in vtail]
        ln=sk.sketchCurves.sketchLines
        for i in range(len(p3)):
            ln.addByTwoPoints(p3[i],p3[(i+1)%len(p3)])
        if sk.profiles.count:
            ex=comp.features.extrudeFeatures
            ei=ex.createInput(sk.profiles.item(0),adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
            ei.setDistanceExtent(False,adsk.core.ValueInput.createByReal(mm(4.5)*pl.geometry.normal.y))
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
        pl=axis_plane(comp,'y',y-1.6)
        sk=comp.sketches.add(pl)
        sk.name='OML_VentralFin_'+label+'_Profile'
        p3=[model_point(sk,x,y-1.6,z) for x,z in vf]
        ln=sk.sketchCurves.sketchLines
        for i in range(len(p3)):
            ln.addByTwoPoints(p3[i],p3[(i+1)%len(p3)])
        if sk.profiles.count:
            ex=comp.features.extrudeFeatures
            ei=ex.createInput(sk.profiles.item(0),adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
            ei.setDistanceExtent(False,adsk.core.ValueInput.createByReal(mm(3.2)*pl.geometry.normal.y))
            f=ex.add(ei)
            f.bodies.item(0).name='OML_VentralFin_'+label
            bodies.append(f.bodies.item(0))
    return bodies

def build_model():
    global _app,_ui
    # Aircraft coordinates: X longitudinal, Y lateral, Z vertical.
    _app.preferences.generalPreferences.defaultModelingOrientation = adsk.core.DefaultModelingOrientations.ZUpModelingOrientation
    doc = _app.documents.add(adsk.core.DocumentTypes.FusionDesignDocumentType)
    design = adsk.fusion.Design.cast(_app.activeProduct)
    design.designType = adsk.fusion.DesignTypes.ParametricDesignType
    root = design.rootComponent
    try:
        doc.name = 'F14_Tomcat_RC_OML_v05_COORDINATE_REPAIR_PROVISIONAL'
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
    addp('InheritedSpan68Unverified', round(span_swept,2), 'mm', 'Conflicting legacy Navy figure; NOT a production target')
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

    config_path=os.path.join(os.path.dirname(__file__),'F14TomcatRC_config.json')
    with open(config_path,encoding='utf-8') as stream:
        config=json.load(stream)
    outdir=config['export_dir']
    os.makedirs(outdir,exist_ok=True)
    root.isSketchFolderLightBulbOn=False
    root.isConstructionFolderLightBulbOn=False
    root.isOriginFolderLightBulbOn=False
    audit=[]
    for body in root.bRepBodies:
        bb=body.boundingBox
        bounds={a:[getattr(bb.minPoint,a)*10,getattr(bb.maxPoint,a)*10] for a in ['x','y','z']}
        audit.append(dict(name=body.name,bounds_mm=bounds,volume_cm3=body.volume))
        if body.name.startswith('OML_Wing_'):
            if abs((bounds['y'][1]-bounds['y'][0])-319)>0.1 or bounds['z'][1]-bounds['z'][0]>25:
                raise RuntimeError('Wing axis/orientation validation failed: '+body.name)
    with open(os.path.join(outdir,'Fusion_v05_geometry_audit.json'),'w',encoding='utf-8') as stream:
        json.dump(dict(status='PROVISIONAL_OML_COORDINATE_REPAIR',bodies=audit,source_fidelity_verified=False),stream,indent=2)
    vp=_app.activeViewport
    camera=vp.camera
    camera.eye=adsk.core.Point3D.create(mm(1300),mm(-1300),mm(1000))
    camera.target=adsk.core.Point3D.create(mm(440),0,mm(20))
    camera.upVector=adsk.core.Vector3D.create(0,0,1)
    camera.isPerspective=False
    camera.isFitView=True
    vp.camera=camera
    vp.fit()
    em=design.exportManager
    opt=em.createFusionArchiveExportOptions(os.path.join(outdir,'F14_Tomcat_RC_OML_v05_PROVISIONAL.f3d'))
    if not em.execute(opt):
        raise RuntimeError('Fusion archive export failed')
    return

def build_reference_model_v06():
    _app.preferences.generalPreferences.defaultModelingOrientation=adsk.core.DefaultModelingOrientations.ZUpModelingOrientation
    doc=_app.documents.add(adsk.core.DocumentTypes.FusionDesignDocumentType)
    doc.name='F14_Tomcat_RC_v06_NASA_REFERENCE_REVIEW'
    design=adsk.fusion.Design.cast(_app.activeProduct)
    design.designType=adsk.fusion.DesignTypes.ParametricDesignType
    root=design.rootComponent
    sketches=nasa_reference_sketches(root)
    root.isSketchFolderLightBulbOn=True
    for sk in sketches:
        sk.isVisible=True
    camera=_app.activeViewport.camera
    camera.eye=adsk.core.Point3D.create(mm(440),0,mm(1200))
    camera.target=adsk.core.Point3D.create(mm(440),0,0)
    camera.upVector=adsk.core.Vector3D.create(1,0,0)
    camera.isPerspective=False
    camera.isFitView=True
    _app.activeViewport.camera=camera
    _app.activeViewport.fit()
    with open(os.path.join(os.path.dirname(__file__),'F14TomcatRC_config.json'),encoding='utf-8') as stream:
        config=json.load(stream)
    outdir=config['export_dir']
    os.makedirs(outdir,exist_ok=True)
    export=os.path.join(outdir,'F14_Tomcat_RC_v06_NASA_REFERENCE_REVIEW.f3d')
    if not design.exportManager.execute(design.exportManager.createFusionArchiveExportOptions(export)):
        raise RuntimeError('Reference archive export failed')
    if not _app.activeViewport.saveAsImageFile(os.path.join(outdir,'F14_v06_reference_plan.png'),1600,1000):
        raise RuntimeError('Reference viewport export failed')

def build_basic_wing_document_v08():
    """Source-table wing in aircraft FS/WBL/WL coordinates; not body-integrated."""
    with open(os.path.join(os.path.dirname(__file__),'NASA_F14_basic_wing_v08.json'),encoding='utf-8') as stream:
        data=json.load(stream)
    if len(data['sections'])!=8 or data['experimental_gloves_included']:
        raise RuntimeError('Invalid original wing source dataset')
    _app.preferences.generalPreferences.defaultModelingOrientation=adsk.core.DefaultModelingOrientations.ZUpModelingOrientation
    doc=_app.documents.add(adsk.core.DocumentTypes.FusionDesignDocumentType)
    doc.name='F14_Tomcat_RC_v08_GRUMMAN_BASIC_WINGS_SOURCE_REVIEW'
    design=adsk.fusion.Design.cast(_app.activeProduct)
    design.designType=adsk.fusion.DesignTypes.ParametricDesignType
    root=design.rootComponent
    span=900.0
    source_span_in=2*data['sections'][-1]['wbl_in']
    factor=span/source_span_in
    design.userParameters.add('ReviewSpan20',adsk.core.ValueInput.createByReal(mm(span)),'mm','Source wing reference scale; body datum registration pending')
    design.userParameters.add('SourceSpanFull',adsk.core.ValueInput.createByReal(mm(source_span_in*25.4)),'mm','Grumman basic-wing defining-table tip WBL times two')
    audit=[]
    for label,sign in [('R',1),('L',-1)]:
        sections=[]
        for index,st in enumerate(data['sections']):
            lateral=sign*st['wbl_in']*factor
            plane=axis_plane(root,'y',lateral)
            sk=root.sketches.add(plane)
            sk.name='SOURCE_BASIC_'+label+'_WBL_'+str(st['wbl_in'])
            chord=st['trailing_edge_fs_in']-st['leading_edge_fs_in']
            rows=st['ordinates_xc_upper_lower']
            # Keep the published trailing-edge thickness and incidence.
            contour=[(x,u) for x,u,l in rows]+[(x,l) for x,u,l in rows[:0:-1]]
            pts=[model_point(sk,(st['leading_edge_fs_in']+x*chord)*factor,lateral,(st['reference_vertical_wl_in']+z*chord)*factor) for x,z in contour]
            lines=sk.sketchCurves.sketchLines
            for i in range(len(pts)):
                lines.addByTwoPoints(pts[i],pts[(i+1)%len(pts)])
            if sk.profiles.count!=1:
                raise RuntimeError('Source wing contour must have one profile at WBL '+str(st['wbl_in']))
            sections.append(sk.profiles.item(0))
        features=root.features.loftFeatures
        inp=features.createInput(adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
        inp.isSolid=True
        for profile in sections: inp.loftSections.add(profile)
        feature=features.add(inp)
        body=feature.bodies.item(0)
        body.name='SOURCE_GRUMMAN_BASIC_WING_'+label+'_NOT_BODY_REGISTERED'
        bb=body.boundingBox
        audit.append(dict(name=body.name,bounds_mm={a:[getattr(bb.minPoint,a)*10,getattr(bb.maxPoint,a)*10] for a in ['x','y','z']}))
    root.isSketchFolderLightBulbOn=False
    root.isConstructionFolderLightBulbOn=False
    vp=_app.activeViewport
    camera=vp.camera
    camera.eye=adsk.core.Point3D.create(mm(1200),mm(-1000),mm(1000))
    camera.target=adsk.core.Point3D.create(mm(680),0,mm(180))
    camera.upVector=adsk.core.Vector3D.create(0,0,1)
    camera.isPerspective=False
    camera.isFitView=True
    vp.camera=camera
    vp.fit()
    with open(os.path.join(os.path.dirname(__file__),'F14TomcatRC_config.json'),encoding='utf-8') as stream: config=json.load(stream)
    outdir=config['export_dir']
    os.makedirs(outdir,exist_ok=True)
    if not design.exportManager.execute(design.exportManager.createFusionArchiveExportOptions(os.path.join(outdir,'F14_v08_GRUMMAN_BASIC_WINGS_SOURCE_REVIEW.f3d'))):
        raise RuntimeError('Source wing archive export failed')
    with open(os.path.join(outdir,'F14_v08_source_wing_native_audit.json'),'w',encoding='utf-8') as stream:
        json.dump(dict(status='SOURCE_WING_LOFT_PROVISIONAL',body_datum_registered=False,source_span_full_mm=source_span_in*25.4,bodies=audit),stream,indent=2)
    vp.saveAsImageFile(os.path.join(outdir,'F14_v08_source_wings.png'),1600,1000)

def build_project_revision():
    # Fixed CAD entry point. Subsequent checked-in revisions can change this
    # implementation without accepting code, paths or shell commands in requests.
    return build_basic_wing_document_v08()

class BuildRequestHandler(adsk.core.CustomEventHandler):
    def notify(self,args):
        request=json.loads(args.additionalInfo)
        response=dict(request_id=request['request_id'],status='failed')
        try:
            if request['operation']=='build_project_revision':
                path=os.path.join(os.path.dirname(__file__),'F14TomcatRC.py')
                spec=importlib.util.spec_from_file_location('f14_checked_cad_revision',path)
                revision=importlib.util.module_from_spec(spec)
                spec.loader.exec_module(revision)
                revision._app=_app
                revision._ui=_ui
                revision.build_project_revision()
            elif request['operation']=='build_basic_wings_v08':
                build_basic_wing_document_v08()
            elif request['operation']=='build_reference_v06':
                build_reference_model_v06()
            elif request['operation']=='rebuild':
                build_model()
            elif request['operation']=='export_active':
                design=adsk.fusion.Design.cast(_app.activeProduct)
                if not design or not _app.activeDocument.name.startswith('F14_'):
                    raise RuntimeError('Active document is not the F-14 project')
                with open(os.path.join(os.path.dirname(__file__),'F14TomcatRC_config.json'),encoding='utf-8') as stream:
                    config=json.load(stream)
                export=os.path.join(config['export_dir'],'F14_active_snapshot.f3d')
                if not design.exportManager.execute(design.exportManager.createFusionArchiveExportOptions(export)):
                    raise RuntimeError('Snapshot export failed')
            else:
                raise RuntimeError('Unsupported controlled CAD operation')
            response['status']='completed'
        except:
            response['error']=traceback.format_exc()
        with open(os.path.join(os.path.dirname(__file__),'F14_build_response.json'),'w',encoding='utf-8') as stream:
            json.dump(response,stream,indent=2)

def start_build_requests():
    event=_app.registerCustomEvent(_event_id)
    handler=BuildRequestHandler()
    event.add(handler)
    _handlers.append(handler)
    def poll():
        previous=None
        path=os.path.join(os.path.dirname(__file__),'F14_build_request.json')
        while not _worker_stop.wait(1.0):
            try:
                with open(path,encoding='utf-8') as stream: request=json.load(stream)
                if request['request_id']!=previous:
                    previous=request['request_id']
                    _app.fireCustomEvent(_event_id,json.dumps(request))
            except (FileNotFoundError,ValueError,KeyError):
                continue
    threading.Thread(target=poll,daemon=True).start()


def run(context):
    global _app,_ui,_created
    try:
        _app=adsk.core.Application.get()
        _ui=_app.userInterface
        if not _created:
            with open(os.path.join(os.path.dirname(__file__),'F14TomcatRC_config.json'),encoding='utf-8') as stream:
                config=json.load(stream)
            if config.get('startup_mode')=='basic_wings_v08':
                build_basic_wing_document_v08()
            elif config.get('startup_mode')=='reference_v06':
                build_reference_model_v06()
            else:
                build_model()
            start_build_requests()
            _created=True
            with open(os.path.join(os.path.dirname(__file__),'F14_build_response.json'),'w',encoding='utf-8') as stream:
                json.dump(dict(request_id='startup',status='completed'),stream)
    except:
        try:
            with open(os.path.join(os.path.dirname(__file__),'F14TomcatRC_error.log'),'w',encoding='utf-8') as stream:
                stream.write(traceback.format_exc())
        except:
            pass
        if _ui:
            _ui.messageBox('F14TomcatRC error:\n'+traceback.format_exc())

def stop(context):
    _worker_stop.set()
    if _app:
        _app.unregisterCustomEvent(_event_id)
