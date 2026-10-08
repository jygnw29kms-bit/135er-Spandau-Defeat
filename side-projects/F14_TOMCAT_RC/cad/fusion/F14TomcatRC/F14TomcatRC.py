import adsk.core, adsk.fusion, traceback, math, os, json, threading, importlib.util, hashlib

_app = None
_ui = None
_created = False
_handlers = []
_worker_stop = threading.Event()
_event_id = 'com.jl1976.f14tomcatrc.controlled_build'
_bridge_revision = 'v24_restartable_event_bridge'
with open(__file__, 'rb') as _source_stream:
    _loaded_source_sha256 = hashlib.sha256(_source_stream.read()).hexdigest()

def execution_ack(request_id, status):
    # Captured at import: an on-disk replacement cannot masquerade as a reload.
    return dict(request_id=request_id, status=status,
                bridge_revision=_bridge_revision,
                loaded_source_sha256=_loaded_source_sha256)

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
    if not design.userParameters.itemByName('ReviewSpan20'):
        design.userParameters.add('ReviewSpan20',adsk.core.ValueInput.createByReal(mm(span)),'mm','Source wing reference scale; body datum registration pending')
    if not design.userParameters.itemByName('SourceSpanFull'):
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

def build_source_segment_review_v15():
    """Split independent solid envelopes; deliberately no print shell export."""
    with open(os.path.join(os.path.dirname(__file__),'F14_wing_segmentation_v15.json'),encoding='utf-8') as stream:
        plan=json.load(stream)
    source_path=os.path.join(os.path.dirname(__file__),'NASA_F14_basic_wing_v08.json')
    with open(source_path,'rb') as stream: raw=stream.read()
    if hashlib.sha256(raw).hexdigest()!=plan['source_dataset_sha256']:
        raise RuntimeError('Wing segmentation source dataset changed; regenerate plan')
    source=json.loads(raw.decode('utf-8'))
    factor=900/(2*source['sections'][-1]['wbl_in'])
    matches=[s for s in source['sections'] if abs(s['wbl_in']-plan['split_wbl_in'])<1e-6]
    if len(matches)!=1 or abs(matches[0]['wbl_in']*factor-plan['split_model_y_mm'])>1e-6:
        raise RuntimeError('Split plane is not the specified original defining section')
    build_basic_wing_document_v08()
    design=adsk.fusion.Design.cast(_app.activeProduct)
    _app.activeDocument.name='F14_v15_SOLID_ENVELOPE_SEGMENTS_NOT_PRINT_SHELLS'
    root=design.rootComponent
    original={label:next(b for b in root.bRepBodies if b.name.startswith('SOURCE_GRUMMAN_BASIC_WING_'+label+'_')).volume for label in ['R','L']}
    for label,sign in [('R',1),('L',-1)]:
        body=next(b for b in root.bRepBodies if b.name.startswith('SOURCE_GRUMMAN_BASIC_WING_'+label+'_'))
        plane=axis_plane(root,'y',sign*plan['split_model_y_mm'])
        plane.name='SOURCE_SEGMENT_SPLIT_'+label+'_WBL_'+str(plan['split_wbl_in'])
        inp=root.features.splitBodyFeatures.createInput(body,plane,True)
        if not inp: raise RuntimeError('Native split input failed')
        root.features.splitBodyFeatures.add(inp)
    if root.bRepBodies.count!=4: raise RuntimeError('Expected four native wing envelope segments')
    audit=[]
    totals={'R':0.0,'L':0.0}
    identities=set()
    for body in root.bRepBodies:
        bb=body.boundingBox
        bounds={a:[getattr(bb.minPoint,a)*10,getattr(bb.maxPoint,a)*10] for a in ['x','y','z']}
        center=sum(bounds['y'])/2
        label='R' if center>0 else 'L'
        part='INNER' if abs(center)<plan['split_model_y_mm'] else 'OUTER'
        observed=sorted(abs(v) for v in bounds['y'])
        expected=([source['sections'][0]['wbl_in']*factor,plan['split_model_y_mm']] if part=='INNER'
                  else [plan['split_model_y_mm'],450.0])
        span_boundaries_verified=all(abs(a-b)<=1e-4 for a,b in zip(observed,expected))
        if not span_boundaries_verified: raise RuntimeError('Native segment span boundaries mismatch')
        if (label,part) in identities: raise RuntimeError('Duplicate segment classification')
        identities.add((label,part))
        body.name='SOURCE_ENVELOPE_'+label+'_'+part+'_NOT_PRINT_SHELL'
        size={a:bounds[a][1]-bounds[a][0] for a in ['x','y','z']}
        footprint=[size['x']+2*plan['assumed_brim_per_side_mm'],size['z']+2*plan['assumed_brim_per_side_mm']]
        usable=plan['design_assumed_usable_envelope_mm']
        fits=footprint[0]<=usable[0] and footprint[1]<=usable[1] and size['y']<=usable[2]
        totals[label]+=body.volume
        audit.append(dict(name=body.name,bounds_mm=bounds,volume_cm3=body.volume,
                          span_boundaries_verified=span_boundaries_verified,expected_abs_y_mm=expected,
                          print_height_mm=size['y'],footprint_with_assumed_brim_mm=footprint,
                          assumed_print_envelope_fit=fits))
    volume_checks={}
    for label in ['R','L']:
        delta=totals[label]-original[label]
        rel=abs(delta)/original[label] if original[label] else 0.0
        tol=max(1e-6,original[label]*1e-5)  # 10 ppm ShapeManager split-volume numerical gate
        volume_checks[label]=dict(original_cm3=original[label],split_sum_cm3=totals[label],delta_cm3=delta,
                                  relative_error=rel,tolerance_cm3=tol,conserved=abs(delta)<=tol)
    if not all(c['conserved'] for c in volume_checks.values()): raise RuntimeError('Split volume conservation failed: '+json.dumps(volume_checks,sort_keys=True))
    with open(os.path.join(os.path.dirname(__file__),'F14TomcatRC_config.json'),encoding='utf-8') as stream: config=json.load(stream)
    outdir=os.path.join(config['export_dir'],'source_segments_v15')
    os.makedirs(outdir,exist_ok=True)
    root.isSketchFolderLightBulbOn=False
    root.isConstructionFolderLightBulbOn=False
    target=os.path.join(outdir,'F14_v15_SOLID_ENVELOPE_SEGMENTS_NOT_PRINT_SHELLS.f3d')
    if not design.exportManager.execute(design.exportManager.createFusionArchiveExportOptions(target)):
        raise RuntimeError('Native segment archive export failed')
    with open(os.path.join(outdir,'F14_v15_native_segment_audit.json'),'w',encoding='utf-8') as stream:
        json.dump(dict(status='NATIVE_SOLID_ENVELOPE_SEGMENTS',segments=audit,volume_checks=volume_checks,
                       assumptions=plan['design_assumed_usable_envelope_mm'],
                       hollow_print_shells_created=False,slicer_checked=False,print_release=False),stream,indent=2)
    _app.activeViewport.fit()
    _app.activeViewport.saveAsImageFile(os.path.join(outdir,'F14_v15_segment_review.png'),1600,1000)


def build_source_profile_review_v14():
    """Native topology review of independent normalized source sections."""
    with open(os.path.join(os.path.dirname(__file__),'F14_source_profile_review_v14.json'),encoding='utf-8') as stream:
        data=json.load(stream)
    if data['aircraft_coordinates'] or data['loft_allowed']:
        raise RuntimeError('Source gallery must not be treated as an aircraft loft')
    _app.preferences.generalPreferences.defaultModelingOrientation=adsk.core.DefaultModelingOrientations.ZUpModelingOrientation
    doc=_app.documents.add(adsk.core.DocumentTypes.FusionDesignDocumentType)
    doc.name='F14_SOURCE_SECTION_GALLERY_v14_NOT_AIRCRAFT_GEOMETRY'
    design=adsk.fusion.Design.cast(_app.activeProduct)
    design.designType=adsk.fusion.DesignTypes.ParametricDesignType
    root=design.rootComponent
    audit=[]
    for section in data['profiles']:
        x=section['gallery_plane_x_mm']
        sk=root.sketches.add(axis_plane(root,'x',x))
        sk.name='NORMALIZED_SOURCE_'+section['name']+'_NOT_METRIC_REGISTERED'
        for contour in [section['outer_normalized']]+section['holes_normalized']:
            points=[model_point(sk,x,y*data['gallery_half_width_mm'],z*data['gallery_half_width_mm']) for y,z in contour]
            for i in range(len(points)):
                sk.sketchCurves.sketchLines.addByTwoPoints(points[i],points[(i+1)%len(points)])
        if sk.profiles.count!=section['expected_native_profile_count']:
            raise RuntimeError('Native source profile topology mismatch at '+section['name'])
        audit.append(dict(section=section['name'],profile_count=sk.profiles.count,
                          profile_loop_counts=[p.profileLoops.count for p in sk.profiles]))
    if root.bRepBodies.count: raise RuntimeError('Normalized gallery must contain no aircraft solids')
    with open(os.path.join(os.path.dirname(__file__),'F14TomcatRC_config.json'),encoding='utf-8') as stream: config=json.load(stream)
    outdir=os.path.join(config['export_dir'],'source_profile_v14')
    os.makedirs(outdir,exist_ok=True)
    camera=_app.activeViewport.camera
    camera.eye=adsk.core.Point3D.create(mm(2000),mm(-1800),mm(1400))
    camera.target=adsk.core.Point3D.create(mm(625),0,0)
    camera.upVector=adsk.core.Vector3D.create(0,0,1)
    camera.isPerspective=False
    camera.isFitView=True
    _app.activeViewport.camera=camera
    _app.activeViewport.fit()
    target=os.path.join(outdir,'F14_SOURCE_SECTION_GALLERY_v14.f3d')
    if not design.exportManager.execute(design.exportManager.createFusionArchiveExportOptions(target)):
        raise RuntimeError('Native source gallery export failed')
    with open(os.path.join(outdir,'F14_v14_native_profile_audit.json'),'w',encoding='utf-8') as stream:
        json.dump(dict(status='NORMALIZED_SOURCE_GALLERY',profiles=audit,aircraft_geometry=False,print_release=False),stream,indent=2)
    _app.activeViewport.saveAsImageFile(os.path.join(outdir,'F14_v14_source_profiles.png'),1600,1000)


def build_source_spar_review_v10():
    """Independent material-envelope bodies; no shell cuts or print release."""
    with open(os.path.join(os.path.dirname(__file__),'F14_source_spar_fit_v10.json'),encoding='utf-8') as stream:
        fit=json.load(stream)
    with open(os.path.join(os.path.dirname(__file__),'NASA_F14_basic_wing_v08.json'),encoding='utf-8') as stream:
        source=json.load(stream)
    if fit['source_sha256']!=source['source_sha256'] or not fit['baseline_terminated_spar_candidate']['all_retained_defining_sections_fit']:
        raise RuntimeError('Source spar fit is not applicable to original wing data')
    build_basic_wing_document_v08()
    design=adsk.fusion.Design.cast(_app.activeProduct)
    _app.activeDocument.name='F14_Tomcat_RC_v10_SOURCE_SPAR_PACKAGING_REVIEW'
    root=design.rootComponent
    factor=900.0/(2*source['sections'][-1]['wbl_in'])
    for label,sign in [('R',1),('L',-1)]:
        for kind in ['UPPER_CAP','LOWER_CAP','WEB']:
            profiles=[]
            for st,local in zip(source['sections'][:-1],fit['sections'][:-1]):
                if abs(st['wbl_in']-local['wbl_in'])>1e-6:
                    raise RuntimeError('Source spar station mismatch')
                chord=(st['trailing_edge_fs_in']-st['leading_edge_fs_in'])*factor
                center=st['leading_edge_fs_in']*factor+0.30*chord
                reference=st['reference_vertical_wl_in']*factor
                top=reference+local['cap_top_outer_relative_wl_mm']
                bottom=reference+local['cap_bottom_outer_relative_wl_mm']
                width=local['cap_width_mm']
                if kind=='UPPER_CAP': z0,z1=top-1.0,top
                elif kind=='LOWER_CAP': z0,z1=bottom,bottom+1.0
                else: z0,z1=bottom+1.0,top-1.0; width=0.8
                if z1<=z0:
                    raise RuntimeError('Source spar has no positive section height')
                y=sign*local['model_y_mm']
                sk=root.sketches.add(axis_plane(root,'y',y))
                sk.name='SOURCE_SPAR_'+label+'_'+kind+'_WBL_'+str(st['wbl_in'])
                pts=[model_point(sk,x,y,z) for x,z in [(center-width/2,z0),(center+width/2,z0),(center+width/2,z1),(center-width/2,z1)]]
                for i in range(4): sk.sketchCurves.sketchLines.addByTwoPoints(pts[i],pts[(i+1)%4])
                if sk.profiles.count!=1: raise RuntimeError('Spar rectangle profile failed')
                profiles.append(sk.profiles.item(0))
            inp=root.features.loftFeatures.createInput(adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
            inp.isSolid=True
            for profile in profiles: inp.loftSections.add(profile)
            body=root.features.loftFeatures.add(inp).bodies.item(0)
            body.name='CANDIDATE_CARBON_'+label+'_'+kind+'_NOT_STRENGTH_VERIFIED'
    audit=[]
    for body in root.bRepBodies:
        bb=body.boundingBox
        audit.append(dict(name=body.name,volume_cm3=body.volume,bounds_mm={a:[getattr(bb.minPoint,a)*10,getattr(bb.maxPoint,a)*10] for a in ['x','y','z']}))
    if len(audit)!=8: raise RuntimeError('Expected two source wings and six spar envelopes')
    # Use transient BRep copies: this never cuts the document's wing or spar.
    # Intersection volume tests continuous native loft containment, not skin gap.
    temporary=adsk.fusion.TemporaryBRepManager.get()
    containment=[]
    for label in ['R','L']:
        wing=next(b for b in root.bRepBodies if b.name.startswith('SOURCE_GRUMMAN_BASIC_WING_'+label+'_'))
        for body in root.bRepBodies:
            if not body.name.startswith('CANDIDATE_CARBON_'+label+'_'): continue
            target=temporary.copy(body)
            tool=temporary.copy(wing)
            succeeded=temporary.booleanOperation(target,tool,adsk.fusion.BooleanTypes.IntersectionBooleanType)
            total=body.volume
            inside=target.volume if succeeded and target.isValid else None
            outside=max(0.0,total-inside) if inside is not None else None
            tolerance=max(1e-6,total*1e-6)
            volume_consistent=inside is not None and -tolerance<=inside<=total+tolerance
            containment.append(dict(body=body.name,boolean_succeeded=succeeded,
                                    volume_cm3=total,intersection_volume_cm3=inside,
                                    outside_volume_cm3=outside,tolerance_cm3=tolerance,
                                    intersection_volume_consistent=volume_consistent,
                                    entire_native_loft_inside_outer_solid=(outside<=tolerance and volume_consistent if outside is not None else None)))
    root.isSketchFolderLightBulbOn=False
    root.isConstructionFolderLightBulbOn=False
    with open(os.path.join(os.path.dirname(__file__),'F14TomcatRC_config.json'),encoding='utf-8') as stream: config=json.load(stream)
    outdir=os.path.join(config['export_dir'],'source_spar_v10')
    os.makedirs(outdir,exist_ok=True)
    target=os.path.join(outdir,'F14_v10_SOURCE_SPAR_PACKAGING_REVIEW.f3d')
    if not design.exportManager.execute(design.exportManager.createFusionArchiveExportOptions(target)):
        raise RuntimeError('Source spar archive export failed')
    with open(os.path.join(outdir,'F14_v10_native_spar_audit.json'),'w',encoding='utf-8') as stream:
        json.dump(dict(status='LOCAL_PACKAGING_CANDIDATE',bodies=audit,
                       native_outer_solid_containment=containment,
                       entire_native_spar_inside_outer_solid=all(c['entire_native_loft_inside_outer_solid'] is True for c in containment),
                       containment_method='Temporary BRep intersection volumes; source document bodies preserved',
                       continuous_skin_clearance_verified=False,structural_capacity_verified=False,print_release=False),stream,indent=2)
    _app.activeViewport.fit()
    _app.activeViewport.saveAsImageFile(os.path.join(outdir,'F14_v10_spar_review.png'),1600,1000)


def build_pivot_kinematic_review_v16():
    """Source-backed FS/BL pivot review; planform only until pivot WL/body glove are registered."""
    build_basic_wing_document_v08()
    design=adsk.fusion.Design.cast(_app.activeProduct)
    root=design.rootComponent
    _app.activeDocument.name='F14_v16_SOURCE_PIVOT_SWEEP_DATUM_REVIEW'
    base=os.path.dirname(__file__)
    with open(os.path.join(base,'NASA_F14_basic_wing_v08.json'),encoding='utf-8') as stream:
        data=json.load(stream)
    with open(os.path.join(base,'F14_pivot_datum_v16.json'),encoding='utf-8') as stream:
        pivot=json.load(stream)
    factor=900.0/(2.0*data['sections'][-1]['wbl_in'])
    px=pivot['derived_full_scale_pivot_fs_in']*factor
    py=pivot['derived_full_scale_pivot_bl_in']*factor
    try:
        design.userParameters.add('SourcePivotFS',adsk.core.ValueInput.createByReal(mm(px)),'mm','NADC-81293-60 Table I scaled pivot FS; planform datum')
        design.userParameters.add('SourcePivotBL',adsk.core.ValueInput.createByReal(mm(py)),'mm','NADC-81293-60 Table I scaled pivot BL; planform datum')
    except:
        pass

    def outline(sign,sweep_deg):
        raw=[]
        for st in data['sections']:
            raw.append((st['leading_edge_fs_in']*factor,sign*st['wbl_in']*factor))
        for st in reversed(data['sections']):
            raw.append((st['trailing_edge_fs_in']*factor,sign*st['wbl_in']*factor))
        if sweep_deg==20:
            return raw
        d=math.radians(sweep_deg-20.0)
        angle=-sign*d
        c=math.cos(angle); s=math.sin(angle)
        pyy=sign*py
        out=[]
        for x,y in raw:
            dx=x-px; dy=y-pyy
            out.append((px+dx*c-dy*s,pyy+dx*s+dy*c))
        return out

    sweep_audit=[]
    for sweep in [20,30,40,50,60,68]:
        right=outline(1,sweep)
        semi=max(y for x,y in right)
        sweep_audit.append(dict(sweep_deg=sweep,semi_span_mm=semi,span_mm=2*semi))

    for sweep in [20,68]:
        sk=root.sketches.add(root.xYConstructionPlane)
        sk.name='REF_SOURCE_PLANFORM_%02dDEG_PLAN_ONLY'%sweep
        lines=sk.sketchCurves.sketchLines
        for sign,label in [(1,'R'),(-1,'L')]:
            pts=outline(sign,sweep)
            p3=[model_point(sk,x,y,0) for x,y in pts]
            for i in range(len(p3)):
                ln=lines.addByTwoPoints(p3[i],p3[(i+1)%len(p3)])
                ln.isConstruction=True
        sk.isVisible=True

    piv=root.sketches.add(root.xYConstructionPlane)
    piv.name='REF_NADC_PIVOT_FS_BL_WL_UNVERIFIED'
    for sign in [1,-1]:
        ctr=model_point(piv,px,sign*py,0)
        circ=piv.sketchCurves.sketchCircles.addByCenterRadius(ctr,mm(7.0))
        try: circ.isConstruction=True
        except: pass
    piv.isVisible=True
    root.isSketchFolderLightBulbOn=True
    root.isConstructionFolderLightBulbOn=False

    reference_swept_span_mm=(38.2*12.0)*factor
    span68=next(r['span_mm'] for r in sweep_audit if r['sweep_deg']==68)
    audit=dict(status='SOURCE_PIVOT_PLANFORM_KINEMATIC_REVIEW',
               source_wing_sha256=data.get('source_sha256'),
               source_report=pivot['report'],source_table=pivot['table'],
               scale_mm_per_fullscale_in=factor,
               pivot_fullscale_fs_in=pivot['derived_full_scale_pivot_fs_in'],
               pivot_fullscale_bl_in=pivot['derived_full_scale_pivot_bl_in'],
               pivot_model_x_mm=px,pivot_model_y_mm=py,pivot_waterline_verified=False,
               sweep_results=sweep_audit,
               reference_68deg_span_mm_from_38_2ft_spec=reference_swept_span_mm,
               span68_discrepancy_mm=span68-reference_swept_span_mm,
               body_glove_collision_checked=False,mechanical_pivot_created=False,
               note='FS/BL source-backed. No physical pivot/wingbox is released until pivot WL and fixed glove/body datum are registered.',
               print_release=False,flight_release=False)
    with open(os.path.join(base,'F14TomcatRC_config.json'),encoding='utf-8') as stream:
        config=json.load(stream)
    outdir=os.path.join(config['export_dir'],'pivot_v16')
    os.makedirs(outdir,exist_ok=True)
    target=os.path.join(outdir,'F14_v16_SOURCE_PIVOT_SWEEP_DATUM_REVIEW.f3d')
    if not design.exportManager.execute(design.exportManager.createFusionArchiveExportOptions(target)):
        raise RuntimeError('Pivot review archive export failed')
    with open(os.path.join(outdir,'F14_v16_pivot_sweep_audit.json'),'w',encoding='utf-8') as stream:
        json.dump(audit,stream,indent=2)
    vp=_app.activeViewport
    cam=vp.camera
    cam.eye=adsk.core.Point3D.create(mm(680),0,mm(1400))
    cam.target=adsk.core.Point3D.create(mm(680),0,mm(180))
    cam.upVector=adsk.core.Vector3D.create(1,0,0)
    cam.isPerspective=False
    cam.isFitView=True
    vp.camera=cam
    vp.fit()
    vp.saveAsImageFile(os.path.join(outdir,'F14_v16_pivot_sweep_plan.png'),1600,1000)
    return audit



def build_pivot_wingbox_review_v17():
    """Engineering pivot/wingbox datum review. Pivot WL is source-section extrapolation, not original-aircraft verification."""
    build_basic_wing_document_v08()
    design=adsk.fusion.Design.cast(_app.activeProduct)
    root=design.rootComponent
    _app.activeDocument.name='F14_v17_PIVOT_WINGBOX_ENGINEERING_REVIEW'
    base=os.path.dirname(__file__)
    with open(os.path.join(base,'NASA_F14_basic_wing_v08.json'),encoding='utf-8') as stream:
        data=json.load(stream)
    with open(os.path.join(base,'F14_pivot_datum_v16.json'),encoding='utf-8') as stream:
        pivot=json.load(stream)
    factor=900.0/(2.0*data['sections'][-1]['wbl_in'])
    px=pivot['derived_full_scale_pivot_fs_in']*factor
    py=pivot['derived_full_scale_pivot_bl_in']*factor
    s0,s1=data['sections'][0],data['sections'][1]
    dz=(s1['reference_vertical_wl_in']-s0['reference_vertical_wl_in'])/(s1['wbl_in']-s0['wbl_in'])
    pivot_wl_in=s0['reference_vertical_wl_in']+(pivot['derived_full_scale_pivot_bl_in']-s0['wbl_in'])*dz
    pz=pivot_wl_in*factor
    for n,val,c in [
        ('SourcePivotFS_v17',px,'source-backed pivot FS'),('SourcePivotBL_v17',py,'source-backed pivot BL'),
        ('EngineeringPivotWL_v17',pz,'linear extrapolation of two inboard Grumman wing reference WL stations')]:
        try: design.userParameters.add(n,adsk.core.ValueInput.createByReal(mm(val)),'mm',c)
        except: pass
    bodies=[]
    # Central wing-box engineering envelope: deliberately conservative and separate from OML.
    box_x0,box_x1=px-38.0,px+45.0
    box_y0,box_y1=-py-28.0,py+28.0
    box_z0,box_h=pz-13.0,26.0
    box=extrude_poly(root,'ENG_WINGBOX_v17_NOT_FLIGHT_RELEASED',[(box_x0,box_y0),(box_x1,box_y0),(box_x1,box_y1),(box_x0,box_y1)],box_z0,box_h)
    box.opacity=0.35; bodies.append(box)
    # Pivot bosses around source-backed FS/BL with extrapolated vertical datum.
    for sign,label in [(1,'R'),(-1,'L')]:
        y=sign*py
        sk=root.sketches.add(axis_plane(root,'z',pz-10.0))
        sk.name='ENG_PIVOT_'+label+'_v17'
        ctr=model_point(sk,px,y,pz-10.0)
        sk.sketchCurves.sketchCircles.addByCenterRadius(ctr,mm(12.0))
        if sk.profiles.count!=1: raise RuntimeError('Pivot profile failed '+label)
        ex=root.features.extrudeFeatures
        ei=ex.createInput(sk.profiles.item(0),adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
        ei.setDistanceExtent(False,adsk.core.ValueInput.createByReal(mm(20.0)))
        body=ex.add(ei).bodies.item(0); body.name='ENG_PIVOT_BOSS_'+label+'_24OD_v17'; bodies.append(body)
    # Check pivot boss intersection with each source wing: non-zero overlap is required for a mechanically meaningful root datum.
    temporary=adsk.fusion.TemporaryBRepManager.get()
    checks=[]
    for label in ['R','L']:
        wing=next(b for b in root.bRepBodies if b.name.startswith('SOURCE_GRUMMAN_BASIC_WING_'+label+'_'))
        boss=next(b for b in root.bRepBodies if b.name=='ENG_PIVOT_BOSS_'+label+'_24OD_v17')
        target=temporary.copy(boss); tool=temporary.copy(wing)
        ok=temporary.booleanOperation(target,tool,adsk.fusion.BooleanTypes.IntersectionBooleanType)
        iv=target.volume if ok and target.isValid else 0.0
        checks.append(dict(side=label,intersection_succeeded=bool(ok),intersection_volume_cm3=iv,pivot_engages_source_wing=(iv>0.01)))
    root.isSketchFolderLightBulbOn=False
    root.isConstructionFolderLightBulbOn=False
    with open(os.path.join(base,'F14TomcatRC_config.json'),encoding='utf-8') as stream: config=json.load(stream)
    outdir=os.path.join(config['export_dir'],'pivot_wingbox_v17'); os.makedirs(outdir,exist_ok=True)
    audit=dict(status='ENGINEERING_PIVOT_WINGBOX_DATUM_REVIEW',source_pivot_fs_bl_verified=True,
               pivot_waterline_method='linear extrapolation from two inboard Grumman source reference-WL stations',
               pivot_waterline_original_aircraft_verified=False,pivot_fullscale_wl_in=pivot_wl_in,
               pivot_model_mm=dict(x=px,y=py,z=pz),pivot_boss_od_mm=24.0,wingbox_bounds_mm=dict(x=[box_x0,box_x1],y=[box_y0,box_y1],z=[box_z0,box_z0+box_h]),
               pivot_wing_intersection=checks,mechanical_detail_release=False,body_glove_collision_checked=False,
               print_release=False,flight_release=False)
    target=os.path.join(outdir,'F14_v17_PIVOT_WINGBOX_ENGINEERING_REVIEW.f3d')
    if not design.exportManager.execute(design.exportManager.createFusionArchiveExportOptions(target)):
        raise RuntimeError('v17 archive export failed')
    with open(os.path.join(outdir,'F14_v17_pivot_wingbox_audit.json'),'w',encoding='utf-8') as stream: json.dump(audit,stream,indent=2)
    _app.activeViewport.fit()
    _app.activeViewport.saveAsImageFile(os.path.join(outdir,'F14_v17_pivot_wingbox_review.png'),1600,1000)
    return audit


def build_root_lug_review_v18():
    """Engineering root-lug bridge from source-backed pivot to first Grumman outer-wing section."""
    build_basic_wing_document_v08()
    design=adsk.fusion.Design.cast(_app.activeProduct)
    root=design.rootComponent
    _app.activeDocument.name='F14_v18_ROOT_LUG_PIVOT_INTERFACE_REVIEW'
    base=os.path.dirname(__file__)
    with open(os.path.join(base,'NASA_F14_basic_wing_v08.json'),encoding='utf-8') as stream: data=json.load(stream)
    with open(os.path.join(base,'F14_pivot_datum_v16.json'),encoding='utf-8') as stream: pivot=json.load(stream)
    factor=900.0/(2.0*data['sections'][-1]['wbl_in'])
    px=pivot['derived_full_scale_pivot_fs_in']*factor
    py=pivot['derived_full_scale_pivot_bl_in']*factor
    s0,s1=data['sections'][0],data['sections'][1]
    dz=(s1['reference_vertical_wl_in']-s0['reference_vertical_wl_in'])/(s1['wbl_in']-s0['wbl_in'])
    pivot_wl_in=s0['reference_vertical_wl_in']+(pivot['derived_full_scale_pivot_bl_in']-s0['wbl_in'])*dz
    pz=pivot_wl_in*factor
    root_y=s0['wbl_in']*factor
    root_ref_z=s0['reference_vertical_wl_in']*factor
    root_le=s0['leading_edge_fs_in']*factor
    root_te=s0['trailing_edge_fs_in']*factor
    root_chord=root_te-root_le
    # Bosses and root lugs are engineering envelopes, not scale surface geometry.
    bodies=[]
    temporary=adsk.fusion.TemporaryBRepManager.get()
    checks=[]
    for sign,label in [(1,'R'),(-1,'L')]:
        y_p=sign*py; y_r=sign*root_y
        sk=root.sketches.add(axis_plane(root,'z',pz-10.0)); sk.name='ENG_PIVOT_'+label+'_v18'
        ctr=model_point(sk,px,y_p,pz-10.0); sk.sketchCurves.sketchCircles.addByCenterRadius(ctr,mm(12.0))
        ei=root.features.extrudeFeatures.createInput(sk.profiles.item(0),adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
        ei.setDistanceExtent(False,adsk.core.ValueInput.createByReal(mm(20.0)))
        boss=root.features.extrudeFeatures.add(ei).bodies.item(0); boss.name='ENG_PIVOT_BOSS_'+label+'_24OD_v18'; bodies.append(boss)
        ymin=min(y_p,y_r+sign*1.5); ymax=max(y_p,y_r+sign*1.5)
        # 40-mm chordwise lug centered at pivot FS; 16-mm thick vertically, reaches 1.5 mm into source wing root.
        x0=max(root_le,px-20.0); x1=min(root_te,px+20.0)
        lug=extrude_poly(root,'ENG_ROOT_LUG_'+label+'_v18',[(x0,ymin),(x1,ymin),(x1,ymax),(x0,ymax)],pz-8.0,16.0)
        lug.opacity=0.45; bodies.append(lug)
        wing=next(b for b in root.bRepBodies if b.name.startswith('SOURCE_GRUMMAN_BASIC_WING_'+label+'_'))
        for target_body,kind in [(lug,'lug_to_wing'),(boss,'boss_to_wing')]:
            target=temporary.copy(target_body); tool=temporary.copy(wing)
            ok=temporary.booleanOperation(target,tool,adsk.fusion.BooleanTypes.IntersectionBooleanType)
            iv=target.volume if ok and target.isValid else 0.0
            checks.append(dict(side=label,kind=kind,intersection_succeeded=bool(ok),intersection_volume_cm3=iv,positive_overlap=(iv>1e-4)))
        target=temporary.copy(lug); tool=temporary.copy(boss)
        ok=temporary.booleanOperation(target,tool,adsk.fusion.BooleanTypes.IntersectionBooleanType)
        iv=target.volume if ok and target.isValid else 0.0
        checks.append(dict(side=label,kind='lug_to_boss',intersection_succeeded=bool(ok),intersection_volume_cm3=iv,positive_overlap=(iv>1e-4)))
    root.isSketchFolderLightBulbOn=False; root.isConstructionFolderLightBulbOn=False
    with open(os.path.join(base,'F14TomcatRC_config.json'),encoding='utf-8') as stream: config=json.load(stream)
    outdir=os.path.join(config['export_dir'],'root_lug_v18'); os.makedirs(outdir,exist_ok=True)
    audit=dict(status='ENGINEERING_ROOT_LUG_PIVOT_INTERFACE_REVIEW',source_pivot_fs_bl_verified=True,
               pivot_waterline_original_aircraft_verified=False,pivot_fullscale_wl_in=pivot_wl_in,
               pivot_model_mm=dict(x=px,y=py,z=pz),first_source_section_mm=dict(y=root_y,leading_edge_x=root_le,trailing_edge_x=root_te,reference_z=root_ref_z,chord=root_chord),
               pivot_to_first_source_section_lateral_gap_mm=root_y-py,checks=checks,
               root_lug_engages_wing_both_sides=all(c['positive_overlap'] for c in checks if c['kind']=='lug_to_wing'),
               root_lug_engages_boss_both_sides=all(c['positive_overlap'] for c in checks if c['kind']=='lug_to_boss'),
               boss_directly_engages_outer_wing=False,mechanical_detail_release=False,print_release=False,flight_release=False)
    target=os.path.join(outdir,'F14_v18_ROOT_LUG_PIVOT_INTERFACE_REVIEW.f3d')
    if not design.exportManager.execute(design.exportManager.createFusionArchiveExportOptions(target)): raise RuntimeError('v18 export failed')
    with open(os.path.join(outdir,'F14_v18_root_lug_audit.json'),'w',encoding='utf-8') as stream: json.dump(audit,stream,indent=2)
    _app.activeViewport.fit(); _app.activeViewport.saveAsImageFile(os.path.join(outdir,'F14_v18_root_lug_review.png'),1600,1000)
    return audit

def build_root_lug_review_v19():
    """Engineering root-lug bridge from source-backed pivot to first Grumman outer-wing section."""
    build_basic_wing_document_v08()
    design=adsk.fusion.Design.cast(_app.activeProduct)
    root=design.rootComponent
    _app.activeDocument.name='F14_v19_ROOT_LUG_PIVOT_INTERFACE_REVIEW'
    base=os.path.dirname(__file__)
    with open(os.path.join(base,'NASA_F14_basic_wing_v08.json'),encoding='utf-8') as stream: data=json.load(stream)
    with open(os.path.join(base,'F14_pivot_datum_v16.json'),encoding='utf-8') as stream: pivot=json.load(stream)
    factor=900.0/(2.0*data['sections'][-1]['wbl_in'])
    px=pivot['derived_full_scale_pivot_fs_in']*factor
    py=pivot['derived_full_scale_pivot_bl_in']*factor
    s0,s1=data['sections'][0],data['sections'][1]
    dz=(s1['reference_vertical_wl_in']-s0['reference_vertical_wl_in'])/(s1['wbl_in']-s0['wbl_in'])
    pivot_wl_in=s0['reference_vertical_wl_in']+(pivot['derived_full_scale_pivot_bl_in']-s0['wbl_in'])*dz
    pz=pivot_wl_in*factor
    root_y=s0['wbl_in']*factor
    root_ref_z=s0['reference_vertical_wl_in']*factor
    root_le=s0['leading_edge_fs_in']*factor
    root_te=s0['trailing_edge_fs_in']*factor
    root_chord=root_te-root_le
    # Bosses and root lugs are engineering envelopes, not scale surface geometry.
    bodies=[]
    temporary=adsk.fusion.TemporaryBRepManager.get()
    checks=[]
    for sign,label in [(1,'R'),(-1,'L')]:
        y_p=sign*py; y_r=sign*root_y
        sk=root.sketches.add(axis_plane(root,'z',pz-10.0)); sk.name='ENG_PIVOT_'+label+'_v19'
        ctr=model_point(sk,px,y_p,pz-10.0); sk.sketchCurves.sketchCircles.addByCenterRadius(ctr,mm(12.0))
        ei=root.features.extrudeFeatures.createInput(sk.profiles.item(0),adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
        ei.setDistanceExtent(False,adsk.core.ValueInput.createByReal(mm(20.0)))
        boss=root.features.extrudeFeatures.add(ei).bodies.item(0); boss.name='ENG_PIVOT_BOSS_'+label+'_24OD_v19'; bodies.append(boss)
        ymin=min(y_p,y_r+sign*8.0); ymax=max(y_p,y_r+sign*8.0)
        # 40-mm chordwise lug centered at pivot FS; 16-mm thick vertically, reaches 8 mm into source wing root.
        x0=max(root_le,px-20.0); x1=min(root_te,px+20.0)
        lug=extrude_poly(root,'ENG_ROOT_LUG_'+label+'_v19',[(x0,ymin),(x1,ymin),(x1,ymax),(x0,ymax)],pz-8.0,16.0)
        lug.opacity=0.45; bodies.append(lug)
        wing=next(b for b in root.bRepBodies if b.name.startswith('SOURCE_GRUMMAN_BASIC_WING_'+label+'_'))
        for target_body,kind in [(lug,'lug_to_wing'),(boss,'boss_to_wing')]:
            target=temporary.copy(target_body); tool=temporary.copy(wing)
            ok=temporary.booleanOperation(target,tool,adsk.fusion.BooleanTypes.IntersectionBooleanType)
            iv=target.volume if ok and target.isValid else 0.0
            checks.append(dict(side=label,kind=kind,intersection_succeeded=bool(ok),intersection_volume_cm3=iv,positive_overlap=(iv>1e-4)))
        target=temporary.copy(lug); tool=temporary.copy(boss)
        ok=temporary.booleanOperation(target,tool,adsk.fusion.BooleanTypes.IntersectionBooleanType)
        iv=target.volume if ok and target.isValid else 0.0
        checks.append(dict(side=label,kind='lug_to_boss',intersection_succeeded=bool(ok),intersection_volume_cm3=iv,positive_overlap=(iv>1e-4)))
    root.isSketchFolderLightBulbOn=False; root.isConstructionFolderLightBulbOn=False
    with open(os.path.join(base,'F14TomcatRC_config.json'),encoding='utf-8') as stream: config=json.load(stream)
    outdir=os.path.join(config['export_dir'],'root_lug_v19'); os.makedirs(outdir,exist_ok=True)
    audit=dict(status='ENGINEERING_ROOT_LUG_PIVOT_INTERFACE_REVIEW',source_pivot_fs_bl_verified=True,
               pivot_waterline_original_aircraft_verified=False,pivot_fullscale_wl_in=pivot_wl_in,
               pivot_model_mm=dict(x=px,y=py,z=pz),first_source_section_mm=dict(y=root_y,leading_edge_x=root_le,trailing_edge_x=root_te,reference_z=root_ref_z,chord=root_chord),
               pivot_to_first_source_section_lateral_gap_mm=root_y-py,root_lug_overlap_depth_mm=8.0,checks=checks,
               root_lug_engages_wing_both_sides=all(c['positive_overlap'] for c in checks if c['kind']=='lug_to_wing'),
               root_lug_engages_boss_both_sides=all(c['positive_overlap'] for c in checks if c['kind']=='lug_to_boss'),
               boss_directly_engages_outer_wing=False,mechanical_detail_release=False,print_release=False,flight_release=False)
    target=os.path.join(outdir,'F14_v19_ROOT_LUG_PIVOT_INTERFACE_REVIEW.f3d')
    if not design.exportManager.execute(design.exportManager.createFusionArchiveExportOptions(target)): raise RuntimeError('v19 export failed')
    with open(os.path.join(outdir,'F14_v19_root_lug_audit.json'),'w',encoding='utf-8') as stream: json.dump(audit,stream,indent=2)
    _app.activeViewport.fit(); _app.activeViewport.saveAsImageFile(os.path.join(outdir,'F14_v19_root_lug_review.png'),1600,1000)
    return audit


def build_sweep_envelope_review_v20():
    """Rotate the real source-wing + v19 root-lug BReps through the full sweep range and audit packaging envelopes."""
    build_root_lug_review_v19()
    design=adsk.fusion.Design.cast(_app.activeProduct)
    root=design.rootComponent
    _app.activeDocument.name='F14_v20_SWEEP_MOVING_ASSEMBLY_ENVELOPE_REVIEW'
    base=os.path.dirname(__file__)
    with open(os.path.join(base,'NASA_F14_basic_wing_v08.json'),encoding='utf-8') as stream: data=json.load(stream)
    with open(os.path.join(base,'F14_pivot_datum_v16.json'),encoding='utf-8') as stream: pivot=json.load(stream)
    factor=900.0/(2.0*data['sections'][-1]['wbl_in'])
    px=pivot['derived_full_scale_pivot_fs_in']*factor
    py=pivot['derived_full_scale_pivot_bl_in']*factor
    s0,s1=data['sections'][0],data['sections'][1]
    dz=(s1['reference_vertical_wl_in']-s0['reference_vertical_wl_in'])/(s1['wbl_in']-s0['wbl_in'])
    pivot_wl_in=s0['reference_vertical_wl_in']+(pivot['derived_full_scale_pivot_bl_in']-s0['wbl_in'])*dz
    pz=pivot_wl_in*factor
    temporary=adsk.fusion.TemporaryBRepManager.get()
    sweeps=[]
    for sweep in [20,30,40,50,60,68]:
        side_results=[]
        for sign,label in [(1,'R'),(-1,'L')]:
            wing=next(b for b in root.bRepBodies if b.name.startswith('SOURCE_GRUMMAN_BASIC_WING_'+label+'_'))
            lug=next(b for b in root.bRepBodies if b.name=='ENG_ROOT_LUG_'+label+'_v19')
            angle=-sign*math.radians(sweep-20.0)
            transform=adsk.core.Matrix3D.create()
            transform.setToRotation(angle,adsk.core.Vector3D.create(0,0,1),adsk.core.Point3D.create(mm(px),mm(sign*py),mm(pz)))
            bounds=[]
            for body in [wing,lug]:
                copy=temporary.copy(body)
                if not temporary.transform(copy,transform):
                    raise RuntimeError('Temporary BRep transform failed at sweep %s side %s'%(sweep,label))
                bb=copy.boundingBox
                bounds.append(dict(x=[bb.minPoint.x*10,bb.maxPoint.x*10],y=[bb.minPoint.y*10,bb.maxPoint.y*10],z=[bb.minPoint.z*10,bb.maxPoint.z*10]))
            combined=dict(x=[min(v['x'][0] for v in bounds),max(v['x'][1] for v in bounds)],
                          y=[min(v['y'][0] for v in bounds),max(v['y'][1] for v in bounds)],
                          z=[min(v['z'][0] for v in bounds),max(v['z'][1] for v in bounds)])
            side_results.append(dict(side=label,bounds_mm=combined))
        span=max(s['bounds_mm']['y'][1] for s in side_results)-min(s['bounds_mm']['y'][0] for s in side_results)
        sweeps.append(dict(sweep_deg=sweep,span_mm=span,sides=side_results))
    audit=dict(status='NATIVE_BREP_SWEEP_MOVING_ASSEMBLY_ENVELOPE',
               source_pivot_fs_bl_verified=True,pivot_waterline_original_aircraft_verified=False,
               root_lug_overlap_depth_mm=8.0,pivot_model_mm=dict(x=px,y=py,z=pz),
               sweep_results=sweeps,body_glove_collision_checked=False,
               note='Native wing + root-lug BReps rotated about engineering pivot. Fixed fuselage/body-glove collision awaits source-registered body geometry.',
               mechanical_detail_release=False,print_release=False,flight_release=False)
    with open(os.path.join(base,'F14TomcatRC_config.json'),encoding='utf-8') as stream: config=json.load(stream)
    outdir=os.path.join(config['export_dir'],'sweep_v20'); os.makedirs(outdir,exist_ok=True)
    target=os.path.join(outdir,'F14_v20_SWEEP_MOVING_ASSEMBLY_ENVELOPE_REVIEW.f3d')
    if not design.exportManager.execute(design.exportManager.createFusionArchiveExportOptions(target)): raise RuntimeError('v20 export failed')
    with open(os.path.join(outdir,'F14_v20_sweep_envelope_audit.json'),'w',encoding='utf-8') as stream: json.dump(audit,stream,indent=2)
    _app.activeViewport.fit(); _app.activeViewport.saveAsImageFile(os.path.join(outdir,'F14_v20_sweep_envelope_review.png'),1600,1000)
    return audit


def build_fuselage_sweep_collision_review_v21():
    """Cross-source UPC fuselage vs NASA/Grumman moving wing BRep intersection review."""
    build_root_lug_review_v19()
    design=adsk.fusion.Design.cast(_app.activeProduct)
    root=design.rootComponent
    _app.activeDocument.name='F14_v21_UPC_FUSELAGE_SWEEP_COLLISION_REVIEW'
    base=os.path.dirname(__file__)
    with open(os.path.join(base,'NASA_F14_basic_wing_v08.json'),encoding='utf-8') as stream: data=json.load(stream)
    with open(os.path.join(base,'F14_pivot_datum_v16.json'),encoding='utf-8') as stream: pivot=json.load(stream)
    factor=900.0/(2.0*data['sections'][-1]['wbl_in'])
    full_length_from_scale_mm=748.5*factor
    px=pivot['derived_full_scale_pivot_fs_in']*factor
    py=pivot['derived_full_scale_pivot_bl_in']*factor
    s0,s1=data['sections'][0],data['sections'][1]
    dz=(s1['reference_vertical_wl_in']-s0['reference_vertical_wl_in'])/(s1['wbl_in']-s0['wbl_in'])
    pz=(s0['reference_vertical_wl_in']+(pivot['derived_full_scale_pivot_bl_in']-s0['wbl_in'])*dz)*factor
    fus=build_upc_fuselage_oml(root)
    fus.name='UPC_FUSELAGE_OML_CROSS_SOURCE_v21'
    temporary=adsk.fusion.TemporaryBRepManager.get()
    results=[]
    for sweep in [20,30,40,50,60,68]:
        sides=[]
        for sign,label in [(1,'R'),(-1,'L')]:
            wing=next(b for b in root.bRepBodies if b.name.startswith('SOURCE_GRUMMAN_BASIC_WING_'+label+'_'))
            lug=next(b for b in root.bRepBodies if b.name=='ENG_ROOT_LUG_'+label+'_v19')
            angle=-sign*math.radians(sweep-20.0)
            tr=adsk.core.Matrix3D.create(); tr.setToRotation(angle,adsk.core.Vector3D.create(0,0,1),adsk.core.Point3D.create(mm(px),mm(sign*py),mm(pz)))
            checks=[]
            for body,kind in [(wing,'outer_wing_to_fuselage'),(lug,'root_lug_to_fuselage')]:
                moving=temporary.copy(body)
                if not temporary.transform(moving,tr): raise RuntimeError('v21 transform failed')
                fixed=temporary.copy(fus)
                ok=temporary.booleanOperation(moving,fixed,adsk.fusion.BooleanTypes.IntersectionBooleanType)
                iv=moving.volume if ok and moving.isValid else 0.0
                checks.append(dict(kind=kind,intersection_succeeded=bool(ok),intersection_volume_cm3=iv,positive_overlap=iv>1e-4))
            sides.append(dict(side=label,checks=checks))
        results.append(dict(sweep_deg=sweep,sides=sides))
    bb=fus.boundingBox
    audit=dict(status='CROSS_SOURCE_FUSELAGE_SWEEP_COLLISION_REVIEW',
      fuselage_source='UPC Figure 5.3 extracted fuselage guide stations; section shaping uses documented UPC examples',
      wing_source='NASA/Grumman basic outer-wing source dataset',
      source_registration_frozen=False,
      registration_note='Longitudinal/scale consistency is close, but final common aircraft datum registration remains required before clearance release.',
      wing_scale_implied_full_length_mm=full_length_from_scale_mm,upc_fuselage_length_mm=879.0,
      length_scale_difference_mm=879.0-full_length_from_scale_mm,
      fuselage_bounds_mm={a:[getattr(bb.minPoint,a)*10,getattr(bb.maxPoint,a)*10] for a in ['x','y','z']},
      pivot_model_mm=dict(x=px,y=py,z=pz),sweep_collision_results=results,
      body_glove_collision_checked=True,clearance_release=False,mechanical_detail_release=False,print_release=False,flight_release=False)
    with open(os.path.join(base,'F14TomcatRC_config.json'),encoding='utf-8') as stream: config=json.load(stream)
    outdir=os.path.join(config['export_dir'],'fuselage_collision_v21'); os.makedirs(outdir,exist_ok=True)
    target=os.path.join(outdir,'F14_v21_UPC_FUSELAGE_SWEEP_COLLISION_REVIEW.f3d')
    if not design.exportManager.execute(design.exportManager.createFusionArchiveExportOptions(target)): raise RuntimeError('v21 export failed')
    with open(os.path.join(outdir,'F14_v21_fuselage_sweep_collision_audit.json'),'w',encoding='utf-8') as stream: json.dump(audit,stream,indent=2)
    _app.activeViewport.fit(); _app.activeViewport.saveAsImageFile(os.path.join(outdir,'F14_v21_fuselage_sweep_collision_review.png'),1600,1000)
    return audit


def build_registered_fuselage_collision_review_v22():
    """Register UPC fuselage waterline to engineering pivot WL, then re-run moving-wing collisions."""
    build_root_lug_review_v19()
    design=adsk.fusion.Design.cast(_app.activeProduct)
    root=design.rootComponent
    _app.activeDocument.name='F14_v22_REGISTERED_FUSELAGE_SWEEP_COLLISION_REVIEW'
    base=os.path.dirname(__file__)
    with open(os.path.join(base,'NASA_F14_basic_wing_v08.json'),encoding='utf-8') as stream: data=json.load(stream)
    with open(os.path.join(base,'F14_pivot_datum_v16.json'),encoding='utf-8') as stream: pivot=json.load(stream)
    factor=900.0/(2.0*data['sections'][-1]['wbl_in'])
    px=pivot['derived_full_scale_pivot_fs_in']*factor
    py=pivot['derived_full_scale_pivot_bl_in']*factor
    s0,s1=data['sections'][0],data['sections'][1]
    dz=(s1['reference_vertical_wl_in']-s0['reference_vertical_wl_in'])/(s1['wbl_in']-s0['wbl_in'])
    pivot_wl_in=s0['reference_vertical_wl_in']+(pivot['derived_full_scale_pivot_bl_in']-s0['wbl_in'])*dz
    pz=pivot_wl_in*factor
    fus=build_upc_fuselage_oml(root)
    fus.name='UPC_FUSELAGE_OML_WL_REGISTERED_v22'
    move=root.features.moveFeatures
    coll=adsk.core.ObjectCollection.create(); coll.add(fus)
    tr=adsk.core.Matrix3D.create(); tr.translation=adsk.core.Vector3D.create(0,0,mm(pz))
    mi=move.createInput2(coll); mi.defineAsFreeMove(tr); move.add(mi)
    temporary=adsk.fusion.TemporaryBRepManager.get()
    results=[]
    for sweep in [20,30,40,50,60,68]:
        sides=[]
        for sign,label in [(1,'R'),(-1,'L')]:
            wing=next(b for b in root.bRepBodies if b.name.startswith('SOURCE_GRUMMAN_BASIC_WING_'+label+'_'))
            lug=next(b for b in root.bRepBodies if b.name=='ENG_ROOT_LUG_'+label+'_v19')
            angle=-sign*math.radians(sweep-20.0)
            rot=adsk.core.Matrix3D.create(); rot.setToRotation(angle,adsk.core.Vector3D.create(0,0,1),adsk.core.Point3D.create(mm(px),mm(sign*py),mm(pz)))
            checks=[]
            for body,kind in [(wing,'outer_wing_to_registered_fuselage'),(lug,'root_lug_to_registered_fuselage')]:
                moving=temporary.copy(body)
                if not temporary.transform(moving,rot): raise RuntimeError('v22 moving body transform failed')
                fixed=temporary.copy(fus)
                ok=temporary.booleanOperation(moving,fixed,adsk.fusion.BooleanTypes.IntersectionBooleanType)
                iv=moving.volume if ok and moving.isValid else 0.0
                checks.append(dict(kind=kind,intersection_succeeded=bool(ok),intersection_volume_cm3=iv,positive_overlap=iv>1e-4))
            sides.append(dict(side=label,checks=checks))
        results.append(dict(sweep_deg=sweep,sides=sides))
    bb=fus.boundingBox
    audit=dict(status='ENGINEERING_WATERLINE_REGISTERED_FUSELAGE_COLLISION_REVIEW',
      fuselage_source='UPC Figure 5.3 extracted guide stations',wing_source='NASA/Grumman basic outer-wing dataset',
      registration_method='UPC local drawing waterline z=0 translated to extrapolated source-wing pivot waterline',
      registration_z_shift_mm=pz,pivot_waterline_original_aircraft_verified=False,source_registration_frozen=False,
      fuselage_bounds_mm={a:[getattr(bb.minPoint,a)*10,getattr(bb.maxPoint,a)*10] for a in ['x','y','z']},
      pivot_model_mm=dict(x=px,y=py,z=pz),sweep_collision_results=results,
      all_sweeps_collision_free=all(not c['positive_overlap'] for r in results for sd in r['sides'] for c in sd['checks']),
      clearance_release=False,mechanical_detail_release=False,print_release=False,flight_release=False)
    with open(os.path.join(base,'F14TomcatRC_config.json'),encoding='utf-8') as stream: config=json.load(stream)
    outdir=os.path.join(config['export_dir'],'registered_collision_v22'); os.makedirs(outdir,exist_ok=True)
    target=os.path.join(outdir,'F14_v22_REGISTERED_FUSELAGE_SWEEP_COLLISION_REVIEW.f3d')
    if not design.exportManager.execute(design.exportManager.createFusionArchiveExportOptions(target)): raise RuntimeError('v22 export failed')
    with open(os.path.join(outdir,'F14_v22_registered_collision_audit.json'),'w',encoding='utf-8') as stream: json.dump(audit,stream,indent=2)
    _app.activeViewport.fit(); _app.activeViewport.saveAsImageFile(os.path.join(outdir,'F14_v22_registered_collision_review.png'),1600,1000)
    return audit



def build_registered_clearance_keepout_review_v23():
    """Derive conservative fixed-body keepout envelopes from exact v22 BRep intersections."""
    build_registered_fuselage_collision_review_v22()
    design=adsk.fusion.Design.cast(_app.activeProduct)
    root=design.rootComponent
    _app.activeDocument.name='F14_v23_REGISTERED_SWEEP_KEEPOUT_REVIEW'
    base=os.path.dirname(__file__)
    with open(os.path.join(base,'NASA_F14_basic_wing_v08.json'),encoding='utf-8') as stream: data=json.load(stream)
    with open(os.path.join(base,'F14_pivot_datum_v16.json'),encoding='utf-8') as stream: pivot=json.load(stream)
    factor=900.0/(2.0*data['sections'][-1]['wbl_in'])
    px=pivot['derived_full_scale_pivot_fs_in']*factor
    py=pivot['derived_full_scale_pivot_bl_in']*factor
    s0,s1=data['sections'][0],data['sections'][1]
    dz=(s1['reference_vertical_wl_in']-s0['reference_vertical_wl_in'])/(s1['wbl_in']-s0['wbl_in'])
    pivot_wl_in=s0['reference_vertical_wl_in']+(pivot['derived_full_scale_pivot_bl_in']-s0['wbl_in'])*dz
    pz=pivot_wl_in*factor
    fus=next(b for b in root.bRepBodies if b.name=='UPC_FUSELAGE_OML_WL_REGISTERED_v22')
    temporary=adsk.fusion.TemporaryBRepManager.get()
    records=[]; per_side={'R':[],'L':[]}
    for sweep in [20,30,40,50,60,68]:
        for sign,label in [(1,'R'),(-1,'L')]:
            angle=-sign*math.radians(sweep-20.0)
            rot=adsk.core.Matrix3D.create(); rot.setToRotation(angle,adsk.core.Vector3D.create(0,0,1),adsk.core.Point3D.create(mm(px),mm(sign*py),mm(pz)))
            wing=next(b for b in root.bRepBodies if b.name.startswith('SOURCE_GRUMMAN_BASIC_WING_'+label+'_'))
            lug=next(b for b in root.bRepBodies if b.name=='ENG_ROOT_LUG_'+label+'_v19')
            for body,kind in [(wing,'outer_wing'),(lug,'root_lug')]:
                moving=temporary.copy(body)
                if not temporary.transform(moving,rot): raise RuntimeError('v23 moving body transform failed')
                fixed=temporary.copy(fus)
                ok=temporary.booleanOperation(moving,fixed,adsk.fusion.BooleanTypes.IntersectionBooleanType)
                iv=moving.volume if ok and moving.isValid else 0.0
                rec=dict(sweep_deg=sweep,side=label,kind=kind,intersection_volume_cm3=iv,positive_overlap=iv>1e-4)
                if iv>1e-4:
                    bb=moving.boundingBox
                    bounds={a:[getattr(bb.minPoint,a)*10,getattr(bb.maxPoint,a)*10] for a in ['x','y','z']}
                    rec['intersection_bounds_mm']=bounds
                    per_side[label].append(bounds)
                records.append(rec)
    margin=2.0; keepouts={}
    for label in ['R','L']:
        bs=per_side[label]
        if not bs: continue
        agg={a:[min(v[a][0] for v in bs)-margin,max(v[a][1] for v in bs)+margin] for a in ['x','y','z']}
        keepouts[label]=agg
        body=extrude_poly(root,'ENG_SWEEP_KEEPOUT_'+label+'_v23_NOT_CUT_GEOMETRY',[(agg['x'][0],agg['y'][0]),(agg['x'][1],agg['y'][0]),(agg['x'][1],agg['y'][1]),(agg['x'][0],agg['y'][1])],agg['z'][0],agg['z'][1]-agg['z'][0])
        body.opacity=0.25
    audit=dict(status='REGISTERED_SWEEP_COLLISION_KEEPOUT_REVIEW',registration_inherited_from='v22',
      pivot_waterline_original_aircraft_verified=False,keepout_margin_mm=margin,intersection_records=records,
      conservative_keepout_bounds_mm=keepouts,exact_cut_geometry_created=False,
      note='Keepout boxes bound exact sampled BRep intersections plus 2 mm margin; they are packaging envelopes, not final glove cut geometry.',
      clearance_release=False,mechanical_detail_release=False,print_release=False,flight_release=False)
    with open(os.path.join(base,'F14TomcatRC_config.json'),encoding='utf-8') as stream: config=json.load(stream)
    outdir=os.path.join(config['export_dir'],'registered_keepout_v23'); os.makedirs(outdir,exist_ok=True)
    target=os.path.join(outdir,'F14_v23_REGISTERED_SWEEP_KEEPOUT_REVIEW.f3d')
    if not design.exportManager.execute(design.exportManager.createFusionArchiveExportOptions(target)): raise RuntimeError('v23 export failed')
    with open(os.path.join(outdir,'F14_v23_registered_keepout_audit.json'),'w',encoding='utf-8') as stream: json.dump(audit,stream,indent=2)
    _app.activeViewport.fit(); _app.activeViewport.saveAsImageFile(os.path.join(outdir,'F14_v23_registered_keepout_review.png'),1600,1000)
    return audit



def build_engineering_clearance_cut_review_v24():
    """Cut conservative v23 keepout envelopes from registered fuselage and re-check residual sweep collisions."""
    build_registered_clearance_keepout_review_v23()
    design=adsk.fusion.Design.cast(_app.activeProduct)
    root=design.rootComponent
    _app.activeDocument.name='F14_v24_ENGINEERING_CLEARANCE_CUT_REVIEW'
    base=os.path.dirname(__file__)
    with open(os.path.join(base,'NASA_F14_basic_wing_v08.json'),encoding='utf-8') as stream: data=json.load(stream)
    with open(os.path.join(base,'F14_pivot_datum_v16.json'),encoding='utf-8') as stream: pivot=json.load(stream)
    factor=900.0/(2.0*data['sections'][-1]['wbl_in'])
    px=pivot['derived_full_scale_pivot_fs_in']*factor
    py=pivot['derived_full_scale_pivot_bl_in']*factor
    s0,s1=data['sections'][0],data['sections'][1]
    dz=(s1['reference_vertical_wl_in']-s0['reference_vertical_wl_in'])/(s1['wbl_in']-s0['wbl_in'])
    pivot_wl_in=s0['reference_vertical_wl_in']+(pivot['derived_full_scale_pivot_bl_in']-s0['wbl_in'])*dz
    pz=pivot_wl_in*factor
    fus=next(b for b in root.bRepBodies if b.name=='UPC_FUSELAGE_OML_WL_REGISTERED_v22')
    before=fus.volume
    tools=adsk.core.ObjectCollection.create()
    for label in ['R','L']:
        tools.add(next(b for b in root.bRepBodies if b.name=='ENG_SWEEP_KEEPOUT_'+label+'_v23_NOT_CUT_GEOMETRY'))
    ci=root.features.combineFeatures.createInput(fus,tools)
    ci.operation=adsk.fusion.FeatureOperations.CutFeatureOperation
    ci.isKeepToolBodies=True
    root.features.combineFeatures.add(ci)
    fus.name='UPC_FUSELAGE_ENGINEERING_CLEARANCE_CUT_v24'
    after=fus.volume
    temporary=adsk.fusion.TemporaryBRepManager.get()
    records=[]
    for sweep in [20,30,40,50,60,68]:
        for sign,label in [(1,'R'),(-1,'L')]:
            angle=-sign*math.radians(sweep-20.0)
            rot=adsk.core.Matrix3D.create(); rot.setToRotation(angle,adsk.core.Vector3D.create(0,0,1),adsk.core.Point3D.create(mm(px),mm(sign*py),mm(pz)))
            wing=next(b for b in root.bRepBodies if b.name.startswith('SOURCE_GRUMMAN_BASIC_WING_'+label+'_'))
            lug=next(b for b in root.bRepBodies if b.name=='ENG_ROOT_LUG_'+label+'_v19')
            for body,kind in [(wing,'outer_wing'),(lug,'root_lug')]:
                moving=temporary.copy(body)
                if not temporary.transform(moving,rot): raise RuntimeError('v24 moving body transform failed')
                fixed=temporary.copy(fus)
                ok=temporary.booleanOperation(moving,fixed,adsk.fusion.BooleanTypes.IntersectionBooleanType)
                iv=moving.volume if ok and moving.isValid else 0.0
                records.append(dict(sweep_deg=sweep,side=label,kind=kind,intersection_volume_cm3=iv,positive_overlap=iv>1e-4))
    residual=[r for r in records if r['positive_overlap']]
    audit=dict(status='ENGINEERING_CLEARANCE_CUT_RESIDUAL_COLLISION_REVIEW',registration_inherited_from='v22',keepout_inherited_from='v23',
      pivot_waterline_original_aircraft_verified=False,fuselage_volume_before_cm3=before,fuselage_volume_after_cm3=after,
      removed_volume_cm3=before-after,residual_collision_records=records,residual_positive_overlaps=residual,
      sampled_sweeps_collision_free=(len(residual)==0),
      note='Conservative v23 keepout boxes cut from provisional registered UPC fuselage. This validates packaging logic only; final glove surface and source registration remain unreleased.',
      clearance_release=False,mechanical_detail_release=False,print_release=False,flight_release=False)
    with open(os.path.join(base,'F14TomcatRC_config.json'),encoding='utf-8') as stream: config=json.load(stream)
    outdir=os.path.join(config['export_dir'],'engineering_clearance_v24'); os.makedirs(outdir,exist_ok=True)
    target=os.path.join(outdir,'F14_v24_ENGINEERING_CLEARANCE_CUT_REVIEW.f3d')
    if not design.exportManager.execute(design.exportManager.createFusionArchiveExportOptions(target)): raise RuntimeError('v24 export failed')
    with open(os.path.join(outdir,'F14_v24_engineering_clearance_audit.json'),'w',encoding='utf-8') as stream: json.dump(audit,stream,indent=2)
    _app.activeViewport.fit(); _app.activeViewport.saveAsImageFile(os.path.join(outdir,'F14_v24_engineering_clearance_review.png'),1600,1000)
    return audit



def build_segmented_clearance_pockets_review_v25():
    """Use local intersection-bound pockets instead of broad v23 aggregate keepout boxes."""
    build_registered_clearance_keepout_review_v23()
    design=adsk.fusion.Design.cast(_app.activeProduct)
    root=design.rootComponent
    _app.activeDocument.name='F14_v25_SEGMENTED_CLEARANCE_POCKETS_REVIEW'
    base=os.path.dirname(__file__)
    with open(os.path.join(base,'NASA_F14_basic_wing_v08.json'),encoding='utf-8') as stream: data=json.load(stream)
    with open(os.path.join(base,'F14_pivot_datum_v16.json'),encoding='utf-8') as stream: pivot=json.load(stream)
    with open(os.path.join(base,'F14TomcatRC_config.json'),encoding='utf-8') as stream: config=json.load(stream)
    v23_path=os.path.join(config['export_dir'],'registered_keepout_v23','F14_v23_registered_keepout_audit.json')
    with open(v23_path,encoding='utf-8') as stream: v23=json.load(stream)
    factor=900.0/(2.0*data['sections'][-1]['wbl_in'])
    px=pivot['derived_full_scale_pivot_fs_in']*factor
    py=pivot['derived_full_scale_pivot_bl_in']*factor
    s0,s1=data['sections'][0],data['sections'][1]
    dz=(s1['reference_vertical_wl_in']-s0['reference_vertical_wl_in'])/(s1['wbl_in']-s0['wbl_in'])
    pivot_wl_in=s0['reference_vertical_wl_in']+(pivot['derived_full_scale_pivot_bl_in']-s0['wbl_in'])*dz
    pz=pivot_wl_in*factor
    fus=next(b for b in root.bRepBodies if b.name=='UPC_FUSELAGE_OML_WL_REGISTERED_v22')
    before=fus.volume
    margin=2.0
    tools=adsk.core.ObjectCollection.create(); pocket_defs=[]
    idx=0
    for rec in v23['intersection_records']:
        if not rec.get('positive_overlap') or 'intersection_bounds_mm' not in rec: continue
        b=rec['intersection_bounds_mm']
        x0,x1=b['x'][0]-margin,b['x'][1]+margin
        y0,y1=b['y'][0]-margin,b['y'][1]+margin
        z0,z1=b['z'][0]-margin,b['z'][1]+margin
        idx+=1
        name='ENG_LOCAL_CLEARANCE_%02d_%s_%02d_%s_v25'%(idx,rec['side'],rec['sweep_deg'],rec['kind'])
        body=extrude_poly(root,name,[(x0,y0),(x1,y0),(x1,y1),(x0,y1)],z0,z1-z0)
        body.opacity=0.2; tools.add(body)
        pocket_defs.append(dict(name=name,source_record=rec,bounds_mm=dict(x=[x0,x1],y=[y0,y1],z=[z0,z1])))
    ci=root.features.combineFeatures.createInput(fus,tools)
    ci.operation=adsk.fusion.FeatureOperations.CutFeatureOperation
    ci.isKeepToolBodies=True
    root.features.combineFeatures.add(ci)
    fus.name='UPC_FUSELAGE_SEGMENTED_CLEARANCE_CUT_v25'
    after=fus.volume
    temporary=adsk.fusion.TemporaryBRepManager.get()
    records=[]
    for sweep in [20,30,40,50,60,68]:
        for sign,label in [(1,'R'),(-1,'L')]:
            angle=-sign*math.radians(sweep-20.0)
            rot=adsk.core.Matrix3D.create(); rot.setToRotation(angle,adsk.core.Vector3D.create(0,0,1),adsk.core.Point3D.create(mm(px),mm(sign*py),mm(pz)))
            wing=next(b for b in root.bRepBodies if b.name.startswith('SOURCE_GRUMMAN_BASIC_WING_'+label+'_'))
            lug=next(b for b in root.bRepBodies if b.name=='ENG_ROOT_LUG_'+label+'_v19')
            for body,kind in [(wing,'outer_wing'),(lug,'root_lug')]:
                moving=temporary.copy(body)
                if not temporary.transform(moving,rot): raise RuntimeError('v25 moving body transform failed')
                fixed=temporary.copy(fus)
                ok=temporary.booleanOperation(moving,fixed,adsk.fusion.BooleanTypes.IntersectionBooleanType)
                iv=moving.volume if ok and moving.isValid else 0.0
                records.append(dict(sweep_deg=sweep,side=label,kind=kind,intersection_volume_cm3=iv,positive_overlap=iv>1e-4))
    residual=[r for r in records if r['positive_overlap']]
    v24_removed=None
    v24_path=os.path.join(config['export_dir'],'engineering_clearance_v24','F14_v24_engineering_clearance_audit.json')
    if os.path.exists(v24_path):
        with open(v24_path,encoding='utf-8') as stream: v24_removed=json.load(stream).get('removed_volume_cm3')
    removed=before-after
    audit=dict(status='SEGMENTED_LOCAL_CLEARANCE_POCKETS_REVIEW',registration_inherited_from='v22',intersection_source='v23',
      pocket_margin_mm=margin,pocket_count=len(pocket_defs),pockets=pocket_defs,
      fuselage_volume_before_cm3=before,fuselage_volume_after_cm3=after,removed_volume_cm3=removed,
      v24_broad_keepout_removed_volume_cm3=v24_removed,
      volume_saved_vs_v24_cm3=(v24_removed-removed if v24_removed is not None else None),
      residual_collision_records=records,residual_positive_overlaps=residual,
      sampled_sweeps_collision_free=(len(residual)==0),
      note='Local rectangular pockets bound each exact sampled intersection plus 2 mm margin. This is an engineering packaging optimization, not final scale glove surface.',
      clearance_release=False,mechanical_detail_release=False,print_release=False,flight_release=False)
    outdir=os.path.join(config['export_dir'],'segmented_clearance_v25'); os.makedirs(outdir,exist_ok=True)
    target=os.path.join(outdir,'F14_v25_SEGMENTED_CLEARANCE_POCKETS_REVIEW.f3d')
    if not design.exportManager.execute(design.exportManager.createFusionArchiveExportOptions(target)): raise RuntimeError('v25 export failed')
    with open(os.path.join(outdir,'F14_v25_segmented_clearance_audit.json'),'w',encoding='utf-8') as stream: json.dump(audit,stream,indent=2)
    _app.activeViewport.fit(); _app.activeViewport.saveAsImageFile(os.path.join(outdir,'F14_v25_segmented_clearance_review.png'),1600,1000)
    return audit



def build_dense_sweep_clearance_review_v26():
    """Re-check segmented v25 fuselage clearance every 2 degrees from 20 to 68 deg."""
    build_segmented_clearance_pockets_review_v25()
    design=adsk.fusion.Design.cast(_app.activeProduct)
    root=design.rootComponent
    _app.activeDocument.name='F14_v26_DENSE_SWEEP_CLEARANCE_REVIEW'
    base=os.path.dirname(__file__)
    with open(os.path.join(base,'NASA_F14_basic_wing_v08.json'),encoding='utf-8') as stream: data=json.load(stream)
    with open(os.path.join(base,'F14_pivot_datum_v16.json'),encoding='utf-8') as stream: pivot=json.load(stream)
    with open(os.path.join(base,'F14TomcatRC_config.json'),encoding='utf-8') as stream: config=json.load(stream)
    factor=900.0/(2.0*data['sections'][-1]['wbl_in'])
    px=pivot['derived_full_scale_pivot_fs_in']*factor
    py=pivot['derived_full_scale_pivot_bl_in']*factor
    s0,s1=data['sections'][0],data['sections'][1]
    dz=(s1['reference_vertical_wl_in']-s0['reference_vertical_wl_in'])/(s1['wbl_in']-s0['wbl_in'])
    pivot_wl_in=s0['reference_vertical_wl_in']+(pivot['derived_full_scale_pivot_bl_in']-s0['wbl_in'])*dz
    pz=pivot_wl_in*factor
    fus=next(b for b in root.bRepBodies if b.name=='UPC_FUSELAGE_SEGMENTED_CLEARANCE_CUT_v25')
    temporary=adsk.fusion.TemporaryBRepManager.get()
    records=[]
    for sweep in range(20,69,2):
        for sign,label in [(1,'R'),(-1,'L')]:
            angle=-sign*math.radians(sweep-20.0)
            rot=adsk.core.Matrix3D.create(); rot.setToRotation(angle,adsk.core.Vector3D.create(0,0,1),adsk.core.Point3D.create(mm(px),mm(sign*py),mm(pz)))
            wing=next(b for b in root.bRepBodies if b.name.startswith('SOURCE_GRUMMAN_BASIC_WING_'+label+'_'))
            lug=next(b for b in root.bRepBodies if b.name=='ENG_ROOT_LUG_'+label+'_v19')
            for body,kind in [(wing,'outer_wing'),(lug,'root_lug')]:
                moving=temporary.copy(body)
                if not temporary.transform(moving,rot): raise RuntimeError('v26 moving body transform failed')
                fixed=temporary.copy(fus)
                ok=temporary.booleanOperation(moving,fixed,adsk.fusion.BooleanTypes.IntersectionBooleanType)
                iv=moving.volume if ok and moving.isValid else 0.0
                records.append(dict(sweep_deg=sweep,side=label,kind=kind,intersection_volume_cm3=iv,positive_overlap=iv>1e-4))
    residual=[r for r in records if r['positive_overlap']]
    max_iv=max((r['intersection_volume_cm3'] for r in records),default=0.0)
    audit=dict(status='DENSE_2DEG_SWEEP_CLEARANCE_REVIEW',source_revision='v25',sample_step_deg=2,
      sampled_angles_deg=list(range(20,69,2)),sample_count=len(list(range(20,69,2))),
      pivot_waterline_original_aircraft_verified=False,residual_collision_records=records,
      residual_positive_overlaps=residual,max_residual_intersection_volume_cm3=max_iv,
      dense_sampled_sweep_collision_free=(len(residual)==0),
      note='2-degree BRep sweep sampling validates the v25 segmented engineering clearance cut. Continuous-motion mathematical proof and final source registration remain release gates.',
      clearance_release=False,mechanical_detail_release=False,print_release=False,flight_release=False)
    outdir=os.path.join(config['export_dir'],'dense_clearance_v26'); os.makedirs(outdir,exist_ok=True)
    target=os.path.join(outdir,'F14_v26_DENSE_SWEEP_CLEARANCE_REVIEW.f3d')
    if not design.exportManager.execute(design.exportManager.createFusionArchiveExportOptions(target)): raise RuntimeError('v26 export failed')
    with open(os.path.join(outdir,'F14_v26_dense_sweep_clearance_audit.json'),'w',encoding='utf-8') as stream: json.dump(audit,stream,indent=2)
    _app.activeViewport.fit(); _app.activeViewport.saveAsImageFile(os.path.join(outdir,'F14_v26_dense_sweep_clearance_review.png'),1600,1000)
    return audit



def build_vertical_datum_sensitivity_review_v27():
    """Stress v25 clearance against +/-1 mm common-WL registration uncertainty."""
    build_segmented_clearance_pockets_review_v25()
    design=adsk.fusion.Design.cast(_app.activeProduct)
    root=design.rootComponent
    _app.activeDocument.name='F14_v27_VERTICAL_DATUM_SENSITIVITY_REVIEW'
    base=os.path.dirname(__file__)
    with open(os.path.join(base,'NASA_F14_basic_wing_v08.json'),encoding='utf-8') as stream: data=json.load(stream)
    with open(os.path.join(base,'F14_pivot_datum_v16.json'),encoding='utf-8') as stream: pivot=json.load(stream)
    with open(os.path.join(base,'F14TomcatRC_config.json'),encoding='utf-8') as stream: config=json.load(stream)
    factor=900.0/(2.0*data['sections'][-1]['wbl_in'])
    px=pivot['derived_full_scale_pivot_fs_in']*factor
    py=pivot['derived_full_scale_pivot_bl_in']*factor
    s0,s1=data['sections'][0],data['sections'][1]
    dz=(s1['reference_vertical_wl_in']-s0['reference_vertical_wl_in'])/(s1['wbl_in']-s0['wbl_in'])
    pivot_wl_in=s0['reference_vertical_wl_in']+(pivot['derived_full_scale_pivot_bl_in']-s0['wbl_in'])*dz
    pz=pivot_wl_in*factor
    # Sensitivity of linear regression choice across retained Grumman stations.
    fit_values=[]
    xs=[float(s['wbl_in']) for s in data['sections']]
    zs=[float(s['reference_vertical_wl_in']) for s in data['sections']]
    for n in [2,3,4,5,8]:
        xm=sum(xs[:n])/n; zm=sum(zs[:n])/n
        slope=sum((x-xm)*(z-zm) for x,z in zip(xs[:n],zs[:n]))/sum((x-xm)**2 for x in xs[:n])
        wl=zm+slope*(pivot['derived_full_scale_pivot_bl_in']-xm)
        fit_values.append(dict(first_n=n,pivot_wl_fullscale_in=wl,pivot_wl_model_mm=wl*factor))
    fit_spread=max(v['pivot_wl_model_mm'] for v in fit_values)-min(v['pivot_wl_model_mm'] for v in fit_values)
    fus=next(b for b in root.bRepBodies if b.name=='UPC_FUSELAGE_SEGMENTED_CLEARANCE_CUT_v25')
    temporary=adsk.fusion.TemporaryBRepManager.get()
    shifts=[-1.0,-0.5,0.0,0.5,1.0]
    sweeps=list(range(20,69,4))
    records=[]
    for zshift in shifts:
        fuscopy=temporary.copy(fus)
        tm=adsk.core.Matrix3D.create(); tm.translation=adsk.core.Vector3D.create(0,0,mm(zshift))
        if not temporary.transform(fuscopy,tm): raise RuntimeError('v27 fuselage datum shift failed')
        for sweep in sweeps:
            for sign,label in [(1,'R'),(-1,'L')]:
                angle=-sign*math.radians(sweep-20.0)
                rot=adsk.core.Matrix3D.create(); rot.setToRotation(angle,adsk.core.Vector3D.create(0,0,1),adsk.core.Point3D.create(mm(px),mm(sign*py),mm(pz)))
                wing=next(b for b in root.bRepBodies if b.name.startswith('SOURCE_GRUMMAN_BASIC_WING_'+label+'_'))
                lug=next(b for b in root.bRepBodies if b.name=='ENG_ROOT_LUG_'+label+'_v19')
                for body,kind in [(wing,'outer_wing'),(lug,'root_lug')]:
                    moving=temporary.copy(body)
                    if not temporary.transform(moving,rot): raise RuntimeError('v27 moving body transform failed')
                    fixed=temporary.copy(fuscopy)
                    ok=temporary.booleanOperation(moving,fixed,adsk.fusion.BooleanTypes.IntersectionBooleanType)
                    iv=moving.volume if ok and moving.isValid else 0.0
                    records.append(dict(z_shift_mm=zshift,sweep_deg=sweep,side=label,kind=kind,intersection_volume_cm3=iv,positive_overlap=iv>1e-4))
    residual=[r for r in records if r['positive_overlap']]
    audit=dict(status='VERTICAL_DATUM_REGISTRATION_SENSITIVITY_REVIEW',source_revision='v25',
      pivot_waterline_original_aircraft_verified=False,
      two_station_engineering_pivot_wl_model_mm=pz,linear_fit_variants=fit_values,
      linear_fit_spread_model_mm=fit_spread,tested_vertical_shifts_mm=shifts,
      tested_sweep_angles_deg=sweeps,sweep_step_deg=4,
      residual_collision_records=records,residual_positive_overlaps=residual,
      max_residual_intersection_volume_cm3=max((r['intersection_volume_cm3'] for r in records),default=0.0),
      clearance_robust_within_plusminus_1mm=(len(residual)==0),
      note='The Grumman/NASA wing vertical references are airplane-coordinate values, but no explicit pivot WL has been found. This test deliberately exceeds the observed 0.546 mm model-scale extrapolation spread with +/-1 mm datum shifts.',
      source_registration_release=False,clearance_release=False,mechanical_detail_release=False,print_release=False,flight_release=False)
    outdir=os.path.join(config['export_dir'],'datum_sensitivity_v27'); os.makedirs(outdir,exist_ok=True)
    target=os.path.join(outdir,'F14_v27_VERTICAL_DATUM_SENSITIVITY_REVIEW.f3d')
    if not design.exportManager.execute(design.exportManager.createFusionArchiveExportOptions(target)): raise RuntimeError('v27 export failed')
    with open(os.path.join(outdir,'F14_v27_vertical_datum_sensitivity_audit.json'),'w',encoding='utf-8') as stream: json.dump(audit,stream,indent=2)
    _app.activeViewport.fit(); _app.activeViewport.saveAsImageFile(os.path.join(outdir,'F14_v27_vertical_datum_sensitivity_review.png'),1600,1000)
    return audit



def build_robust_datum_clearance_review_v28():
    """Refine only the 68-deg outer-wing pocket in Z, then test dense sweep at +/-1 mm WL uncertainty."""
    build_registered_clearance_keepout_review_v23()
    design=adsk.fusion.Design.cast(_app.activeProduct)
    root=design.rootComponent
    _app.activeDocument.name='F14_v28_ROBUST_DATUM_CLEARANCE_REVIEW'
    base=os.path.dirname(__file__)
    with open(os.path.join(base,'NASA_F14_basic_wing_v08.json'),encoding='utf-8') as stream: data=json.load(stream)
    with open(os.path.join(base,'F14_pivot_datum_v16.json'),encoding='utf-8') as stream: pivot=json.load(stream)
    with open(os.path.join(base,'F14TomcatRC_config.json'),encoding='utf-8') as stream: config=json.load(stream)
    with open(os.path.join(config['export_dir'],'registered_keepout_v23','F14_v23_registered_keepout_audit.json'),encoding='utf-8') as stream: v23=json.load(stream)
    factor=900.0/(2.0*data['sections'][-1]['wbl_in'])
    px=pivot['derived_full_scale_pivot_fs_in']*factor
    py=pivot['derived_full_scale_pivot_bl_in']*factor
    s0,s1=data['sections'][0],data['sections'][1]
    dz=(s1['reference_vertical_wl_in']-s0['reference_vertical_wl_in'])/(s1['wbl_in']-s0['wbl_in'])
    pz=(s0['reference_vertical_wl_in']+(pivot['derived_full_scale_pivot_bl_in']-s0['wbl_in'])*dz)*factor
    fus=next(b for b in root.bRepBodies if b.name=='UPC_FUSELAGE_OML_WL_REGISTERED_v22')
    before=fus.volume
    tools=adsk.core.ObjectCollection.create(); pocket_defs=[]; idx=0
    for rec in v23['intersection_records']:
        if not rec.get('positive_overlap') or 'intersection_bounds_mm' not in rec: continue
        b=rec['intersection_bounds_mm']; mxy=2.0
        mz=3.0 if rec['sweep_deg']==68 and rec['kind']=='outer_wing' else 2.0
        x0,x1=b['x'][0]-mxy,b['x'][1]+mxy; y0,y1=b['y'][0]-mxy,b['y'][1]+mxy; z0,z1=b['z'][0]-mz,b['z'][1]+mz
        idx+=1
        name='ENG_ROBUST_CLEARANCE_%02d_%s_%02d_%s_v28'%(idx,rec['side'],rec['sweep_deg'],rec['kind'])
        body=extrude_poly(root,name,[(x0,y0),(x1,y0),(x1,y1),(x0,y1)],z0,z1-z0); body.opacity=0.2; tools.add(body)
        pocket_defs.append(dict(name=name,source_record=rec,margin_xy_mm=mxy,margin_z_mm=mz,bounds_mm=dict(x=[x0,x1],y=[y0,y1],z=[z0,z1])))
    ci=root.features.combineFeatures.createInput(fus,tools); ci.operation=adsk.fusion.FeatureOperations.CutFeatureOperation; ci.isKeepToolBodies=True; root.features.combineFeatures.add(ci)
    fus.name='UPC_FUSELAGE_ROBUST_CLEARANCE_CUT_v28'; after=fus.volume
    temporary=adsk.fusion.TemporaryBRepManager.get(); shifts=[-1.0,-0.5,0.0,0.5,1.0]; sweeps=list(range(20,69,2)); records=[]
    for zshift in shifts:
        fuscopy=temporary.copy(fus); tm=adsk.core.Matrix3D.create(); tm.translation=adsk.core.Vector3D.create(0,0,mm(zshift)); temporary.transform(fuscopy,tm)
        for sweep in sweeps:
            for sign,label in [(1,'R'),(-1,'L')]:
                angle=-sign*math.radians(sweep-20.0); rot=adsk.core.Matrix3D.create(); rot.setToRotation(angle,adsk.core.Vector3D.create(0,0,1),adsk.core.Point3D.create(mm(px),mm(sign*py),mm(pz)))
                wing=next(b for b in root.bRepBodies if b.name.startswith('SOURCE_GRUMMAN_BASIC_WING_'+label+'_')); lug=next(b for b in root.bRepBodies if b.name=='ENG_ROOT_LUG_'+label+'_v19')
                for body,kind in [(wing,'outer_wing'),(lug,'root_lug')]:
                    moving=temporary.copy(body); temporary.transform(moving,rot); fixed=temporary.copy(fuscopy)
                    ok=temporary.booleanOperation(moving,fixed,adsk.fusion.BooleanTypes.IntersectionBooleanType); iv=moving.volume if ok and moving.isValid else 0.0
                    records.append(dict(z_shift_mm=zshift,sweep_deg=sweep,side=label,kind=kind,intersection_volume_cm3=iv,positive_overlap=iv>1e-4))
    residual=[r for r in records if r['positive_overlap']]
    audit=dict(status='ROBUST_DENSE_DATUM_CLEARANCE_REVIEW',source_revision='v23',targeted_extra_z_margin_mm=1.0,
      tested_vertical_shifts_mm=shifts,tested_sweep_angles_deg=sweeps,sweep_step_deg=2,pocket_count=len(pocket_defs),pockets=pocket_defs,
      fuselage_volume_before_cm3=before,fuselage_volume_after_cm3=after,removed_volume_cm3=before-after,
      residual_positive_overlaps=residual,max_residual_intersection_volume_cm3=max((r['intersection_volume_cm3'] for r in records),default=0.0),
      robust_dense_clearance_pass=(len(residual)==0),pivot_waterline_original_aircraft_verified=False,source_registration_release=False,
      clearance_release=False,mechanical_detail_release=False,print_release=False,flight_release=False)
    outdir=os.path.join(config['export_dir'],'robust_clearance_v28'); os.makedirs(outdir,exist_ok=True)
    target=os.path.join(outdir,'F14_v28_ROBUST_DATUM_CLEARANCE_REVIEW.f3d')
    if not design.exportManager.execute(design.exportManager.createFusionArchiveExportOptions(target)): raise RuntimeError('v28 export failed')
    with open(os.path.join(outdir,'F14_v28_robust_datum_clearance_audit.json'),'w',encoding='utf-8') as stream: json.dump(audit,stream,indent=2)
    _app.activeViewport.fit(); _app.activeViewport.saveAsImageFile(os.path.join(outdir,'F14_v28_robust_datum_clearance_review.png'),1600,1000)
    return audit

def build_robust_datum_clearance_review_v29():
    """Refine only the 68-deg outer-wing pocket in Z, then test dense sweep at +/-1 mm WL uncertainty."""
    build_registered_clearance_keepout_review_v23()
    design=adsk.fusion.Design.cast(_app.activeProduct)
    root=design.rootComponent
    _app.activeDocument.name='F14_v29_ROBUST_DATUM_CLEARANCE_REVIEW'
    base=os.path.dirname(__file__)
    with open(os.path.join(base,'NASA_F14_basic_wing_v08.json'),encoding='utf-8') as stream: data=json.load(stream)
    with open(os.path.join(base,'F14_pivot_datum_v16.json'),encoding='utf-8') as stream: pivot=json.load(stream)
    with open(os.path.join(base,'F14TomcatRC_config.json'),encoding='utf-8') as stream: config=json.load(stream)
    with open(os.path.join(config['export_dir'],'registered_keepout_v23','F14_v23_registered_keepout_audit.json'),encoding='utf-8') as stream: v23=json.load(stream)
    factor=900.0/(2.0*data['sections'][-1]['wbl_in'])
    px=pivot['derived_full_scale_pivot_fs_in']*factor
    py=pivot['derived_full_scale_pivot_bl_in']*factor
    s0,s1=data['sections'][0],data['sections'][1]
    dz=(s1['reference_vertical_wl_in']-s0['reference_vertical_wl_in'])/(s1['wbl_in']-s0['wbl_in'])
    pz=(s0['reference_vertical_wl_in']+(pivot['derived_full_scale_pivot_bl_in']-s0['wbl_in'])*dz)*factor
    fus=next(b for b in root.bRepBodies if b.name=='UPC_FUSELAGE_OML_WL_REGISTERED_v22')
    before=fus.volume
    tools=adsk.core.ObjectCollection.create(); pocket_defs=[]; idx=0
    for rec in v23['intersection_records']:
        if not rec.get('positive_overlap') or 'intersection_bounds_mm' not in rec: continue
        b=rec['intersection_bounds_mm']; mxy=3.0 if rec['sweep_deg']==68 and rec['kind']=='outer_wing' else 2.0
        mz=3.0 if rec['sweep_deg']==68 and rec['kind']=='outer_wing' else 2.0
        x0,x1=b['x'][0]-mxy,b['x'][1]+mxy; y0,y1=b['y'][0]-mxy,b['y'][1]+mxy; z0,z1=b['z'][0]-mz,b['z'][1]+mz
        idx+=1
        name='ENG_ROBUST_CLEARANCE_%02d_%s_%02d_%s_v29'%(idx,rec['side'],rec['sweep_deg'],rec['kind'])
        body=extrude_poly(root,name,[(x0,y0),(x1,y0),(x1,y1),(x0,y1)],z0,z1-z0); body.opacity=0.2; tools.add(body)
        pocket_defs.append(dict(name=name,source_record=rec,margin_xy_mm=mxy,margin_z_mm=mz,bounds_mm=dict(x=[x0,x1],y=[y0,y1],z=[z0,z1])))
    ci=root.features.combineFeatures.createInput(fus,tools); ci.operation=adsk.fusion.FeatureOperations.CutFeatureOperation; ci.isKeepToolBodies=True; root.features.combineFeatures.add(ci)
    fus.name='UPC_FUSELAGE_ROBUST_CLEARANCE_CUT_v29'; after=fus.volume
    temporary=adsk.fusion.TemporaryBRepManager.get(); shifts=[-1.0,-0.5,0.0,0.5,1.0]; sweeps=list(range(20,69,2)); records=[]
    for zshift in shifts:
        fuscopy=temporary.copy(fus); tm=adsk.core.Matrix3D.create(); tm.translation=adsk.core.Vector3D.create(0,0,mm(zshift)); temporary.transform(fuscopy,tm)
        for sweep in sweeps:
            for sign,label in [(1,'R'),(-1,'L')]:
                angle=-sign*math.radians(sweep-20.0); rot=adsk.core.Matrix3D.create(); rot.setToRotation(angle,adsk.core.Vector3D.create(0,0,1),adsk.core.Point3D.create(mm(px),mm(sign*py),mm(pz)))
                wing=next(b for b in root.bRepBodies if b.name.startswith('SOURCE_GRUMMAN_BASIC_WING_'+label+'_')); lug=next(b for b in root.bRepBodies if b.name=='ENG_ROOT_LUG_'+label+'_v19')
                for body,kind in [(wing,'outer_wing'),(lug,'root_lug')]:
                    moving=temporary.copy(body); temporary.transform(moving,rot); fixed=temporary.copy(fuscopy)
                    ok=temporary.booleanOperation(moving,fixed,adsk.fusion.BooleanTypes.IntersectionBooleanType); iv=moving.volume if ok and moving.isValid else 0.0
                    records.append(dict(z_shift_mm=zshift,sweep_deg=sweep,side=label,kind=kind,intersection_volume_cm3=iv,positive_overlap=iv>1e-4))
    residual=[r for r in records if r['positive_overlap']]
    audit=dict(status='ROBUST_DENSE_DATUM_CLEARANCE_REVIEW',source_revision='v23',targeted_extra_xyz_margin_mm=1.0,
      tested_vertical_shifts_mm=shifts,tested_sweep_angles_deg=sweeps,sweep_step_deg=2,pocket_count=len(pocket_defs),pockets=pocket_defs,
      fuselage_volume_before_cm3=before,fuselage_volume_after_cm3=after,removed_volume_cm3=before-after,
      residual_positive_overlaps=residual,max_residual_intersection_volume_cm3=max((r['intersection_volume_cm3'] for r in records),default=0.0),
      robust_dense_clearance_pass=(len(residual)==0),pivot_waterline_original_aircraft_verified=False,source_registration_release=False,
      clearance_release=False,mechanical_detail_release=False,print_release=False,flight_release=False)
    outdir=os.path.join(config['export_dir'],'robust_clearance_v29'); os.makedirs(outdir,exist_ok=True)
    target=os.path.join(outdir,'F14_v29_ROBUST_DATUM_CLEARANCE_REVIEW.f3d')
    if not design.exportManager.execute(design.exportManager.createFusionArchiveExportOptions(target)): raise RuntimeError('v28 export failed')
    with open(os.path.join(outdir,'F14_v29_robust_datum_clearance_audit.json'),'w',encoding='utf-8') as stream: json.dump(audit,stream,indent=2)
    _app.activeViewport.fit(); _app.activeViewport.saveAsImageFile(os.path.join(outdir,'F14_v29_robust_datum_clearance_review.png'),1600,1000)
    return audit




def _cyl_body_v30(root,name,cx,cy,z0,radius,height):
    sk=root.sketches.add(axis_plane(root,'z',z0)); sk.name=name+'_SK'
    ctr=model_point(sk,cx,cy,z0); sk.sketchCurves.sketchCircles.addByCenterRadius(ctr,mm(radius))
    if sk.profiles.count!=1: raise RuntimeError('Cylinder profile failed '+name)
    ex=root.features.extrudeFeatures; ei=ex.createInput(sk.profiles.item(0),adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
    ei.setDistanceExtent(False,adsk.core.ValueInput.createByReal(mm(height)))
    body=ex.add(ei).bodies.item(0); body.name=name; return body

def _cut_cyl_v30(root,target,name,cx,cy,z0,radius,height):
    tool=_cyl_body_v30(root,name,cx,cy,z0,radius,height)
    tools=adsk.core.ObjectCollection.create(); tools.add(tool)
    ci=root.features.combineFeatures.createInput(target,tools); ci.operation=adsk.fusion.FeatureOperations.CutFeatureOperation; ci.isKeepToolBodies=False
    root.features.combineFeatures.add(ci)

def build_pivot_cassette_review_v30():
    """Add actual RC pivot shaft/bearing/hardpoint cassette envelopes to the v29 robust-clearance airframe."""
    build_robust_datum_clearance_review_v29()
    design=adsk.fusion.Design.cast(_app.activeProduct); root=design.rootComponent
    _app.activeDocument.name='F14_v30_PIVOT_CASSETTE_MECHANICAL_REVIEW'
    base=os.path.dirname(__file__)
    with open(os.path.join(base,'NASA_F14_basic_wing_v08.json'),encoding='utf-8') as stream: data=json.load(stream)
    with open(os.path.join(base,'F14_pivot_datum_v16.json'),encoding='utf-8') as stream: pivot=json.load(stream)
    with open(os.path.join(base,'F14_pivot_cassette_screen_v30.json'),encoding='utf-8') as stream: screen=json.load(stream)
    with open(os.path.join(base,'F14TomcatRC_config.json'),encoding='utf-8') as stream: config=json.load(stream)
    factor=900.0/(2.0*data['sections'][-1]['wbl_in']); px=pivot['derived_full_scale_pivot_fs_in']*factor; py=pivot['derived_full_scale_pivot_bl_in']*factor
    s0,s1=data['sections'][0],data['sections'][1]; dz=(s1['reference_vertical_wl_in']-s0['reference_vertical_wl_in'])/(s1['wbl_in']-s0['wbl_in'])
    pz=(s0['reference_vertical_wl_in']+(pivot['derived_full_scale_pivot_bl_in']-s0['wbl_in'])*dz)*factor
    fus=next(b for b in root.bRepBodies if b.name=='UPC_FUSELAGE_ROBUST_CLEARANCE_CUT_v29')
    temporary=adsk.fusion.TemporaryBRepManager.get(); plates=[]; hardware=[]; plate_checks=[]; sweep_checks=[]
    plate_x0,plate_x1=px-22.0,px+22.0; plate_half_y=12.0; plate_t=2.0
    lower_z0=pz-12.5; upper_z0=pz+10.5
    for sign,label in [(1,'R'),(-1,'L')]:
        y=sign*py
        boss=next(b for b in root.bRepBodies if b.name=='ENG_PIVOT_BOSS_'+label+'_24OD_v19')
        # Machine the moving boss envelope for a 6.2-mm through bore and 13.1-mm x 5.1-mm bearing counterbores.
        _cut_cyl_v30(root,boss,'CUT_SHAFT_BORE_'+label+'_v30',px,y,pz-10.2,3.1,20.4)
        _cut_cyl_v30(root,boss,'CUT_BRG_LOWER_'+label+'_v30',px,y,pz-10.1,6.55,5.2)
        _cut_cyl_v30(root,boss,'CUT_BRG_UPPER_'+label+'_v30',px,y,pz+4.9,6.55,5.2)
        boss.name='ENG_PIVOT_BOSS_'+label+'_24OD_BEARING_SEATS_v30'
        # Fixed hardpoint plates touch the boss only through thrust hardware; 20-mm clear moving gap remains between plates.
        for pos,z0 in [('LOWER',lower_z0),('UPPER',upper_z0)]:
            plate=extrude_poly(root,'ENG_HARDPOINT_'+pos+'_'+label+'_v30',[(plate_x0,y-plate_half_y),(plate_x1,y-plate_half_y),(plate_x1,y+plate_half_y),(plate_x0,y+plate_half_y)],z0,plate_t)
            _cut_cyl_v30(root,plate,'CUT_PLATE_SHAFT_'+pos+'_'+label+'_v30',px,y,z0-0.1,3.1,plate_t+0.2)
            plate.opacity=0.55; plates.append(plate)
            # containment fraction inside provisional registered fuselage solid
            pcopy=temporary.copy(plate); fcopy=temporary.copy(fus); pv=plate.volume
            ok=temporary.booleanOperation(pcopy,fcopy,adsk.fusion.BooleanTypes.IntersectionBooleanType); iv=pcopy.volume if ok and pcopy.isValid else 0.0
            plate_checks.append(dict(side=label,plate=pos,plate_volume_cm3=pv,inside_fuselage_volume_cm3=iv,inside_fraction=(iv/pv if pv>0 else 0.0)))
        # Hardware reference envelopes: two 6x13x5 bearings, 6-mm shaft, two 16-mm thrust washers.
        for pos,z0 in [('LOWER',pz-10.0),('UPPER',pz+5.0)]:
            brg=_cyl_body_v30(root,'REF_BEARING_6x13x5_'+pos+'_'+label+'_v30',px,y,z0,6.5,5.0); brg.opacity=0.25; hardware.append(brg)
        shaft=_cyl_body_v30(root,'REF_SHAFT_6mm_'+label+'_v30',px,y,pz-13.0,3.0,26.0); shaft.opacity=0.35; hardware.append(shaft)
        for pos,z0 in [('LOWER',pz-10.5),('UPPER',pz+10.0)]:
            wash=_cyl_body_v30(root,'REF_THRUST_16OD_'+pos+'_'+label+'_v30',px,y,z0,8.0,0.5); wash.opacity=0.2; hardware.append(wash)
    # Check fixed hardpoint plates against moving wing + root-lug BReps across the full dense sweep.
    for sweep in range(20,69,2):
        for sign,label in [(1,'R'),(-1,'L')]:
            angle=-sign*math.radians(sweep-20.0); rot=adsk.core.Matrix3D.create(); rot.setToRotation(angle,adsk.core.Vector3D.create(0,0,1),adsk.core.Point3D.create(mm(px),mm(sign*py),mm(pz)))
            wing=next(b for b in root.bRepBodies if b.name.startswith('SOURCE_GRUMMAN_BASIC_WING_'+label+'_')); lug=next(b for b in root.bRepBodies if b.name=='ENG_ROOT_LUG_'+label+'_v19')
            sideplates=[p for p in plates if p.name.endswith('_'+label+'_v30')]
            for moving_body,kind in [(wing,'outer_wing'),(lug,'root_lug')]:
                moving=temporary.copy(moving_body); temporary.transform(moving,rot)
                for plate in sideplates:
                    target=temporary.copy(moving); tool=temporary.copy(plate); ok=temporary.booleanOperation(target,tool,adsk.fusion.BooleanTypes.IntersectionBooleanType)
                    iv=target.volume if ok and target.isValid else 0.0
                    sweep_checks.append(dict(sweep_deg=sweep,side=label,moving_kind=kind,plate=plate.name,intersection_volume_cm3=iv,positive_overlap=iv>1e-4))
    residual=[r for r in sweep_checks if r['positive_overlap']]
    plate_vol=sum(p.volume for p in plates); shaft_vol=2.0*math.pi*(0.3**2)*2.6 # cm^3; radius/height in cm
    audit=dict(status='PIVOT_CASSETTE_MECHANICAL_PACKAGING_REVIEW',source_revision='v29',engineering_screen=screen,
      geometry=dict(pivot_model_mm=dict(x=px,y=py,z=pz),shaft_d_mm=6.0,bearing_envelope_mm=[6,13,5],bearings_per_pivot=2,
        plate_planform_mm=[44,24],plate_thickness_mm=2.0,moving_gap_between_plates_mm=20.0,thrust_washer_mm=[6,16,0.5]),
      hardpoint_plate_containment=plate_checks,fixed_plate_sweep_collision_records=sweep_checks,residual_positive_overlaps=residual,
      dense_plate_clearance_pass=(len(residual)==0),hardpoint_plate_total_volume_cm3=plate_vol,steel_shaft_reference_volume_cm3=shaft_vol,
      bearing_ratings_verified=False,shaft_alloy_verified=False,hardpoint_material_verified=False,mechanical_detail_release=False,print_release=False,flight_release=False)
    outdir=os.path.join(config['export_dir'],'pivot_cassette_v30'); os.makedirs(outdir,exist_ok=True)
    target=os.path.join(outdir,'F14_v30_PIVOT_CASSETTE_MECHANICAL_REVIEW.f3d')
    if not design.exportManager.execute(design.exportManager.createFusionArchiveExportOptions(target)): raise RuntimeError('v30 export failed')
    with open(os.path.join(outdir,'F14_v30_pivot_cassette_audit.json'),'w',encoding='utf-8') as stream: json.dump(audit,stream,indent=2)
    _app.activeViewport.fit(); _app.activeViewport.saveAsImageFile(os.path.join(outdir,'F14_v30_pivot_cassette_review.png'),1600,1000)
    return audit

def build_project_revision():
    # Fixed CAD entry point. Subsequent checked-in revisions can change this
    # implementation without accepting code, paths or shell commands in requests.
    return build_pivot_cassette_review_v30()

class BuildRequestHandler(adsk.core.CustomEventHandler):
    def notify(self,args):
        request=json.loads(args.additionalInfo)
        response=execution_ack(request['request_id'],'failed')
        try:
            if request['operation']=='ping':
                response['active_document_name']=_app.activeDocument.name if _app.activeDocument else None
                response['geometry_created']=False
            elif request['operation'] in ['build_project_revision','build_source_profiles_v14','build_source_segments_v15']:
                path=os.path.join(os.path.dirname(__file__),'F14TomcatRC.py')
                spec=importlib.util.spec_from_file_location('f14_checked_cad_revision',path)
                revision=importlib.util.module_from_spec(spec)
                spec.loader.exec_module(revision)
                revision._app=_app
                revision._ui=_ui
                response['executed_revision_source_sha256']=getattr(revision, '_loaded_source_sha256', 'UNAVAILABLE_NONBLOCKING')
                if request['operation']=='build_source_profiles_v14': revision.build_source_profile_review_v14()
                elif request['operation']=='build_source_segments_v15': revision.build_source_segment_review_v15()
                else: revision.build_project_revision()
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
    global _worker_stop
    # Each worker retains its own stop token, even if Fusion reuses this module.
    _worker_stop=threading.Event()
    shutdown_token=_worker_stop
    event=_app.registerCustomEvent(_event_id)
    handler=BuildRequestHandler()
    event.add(handler)
    _handlers.append(handler)
    def poll():
        previous=None
        path=os.path.join(os.path.dirname(__file__),'F14_build_request.json')
        while not shutdown_token.wait(1.0):
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
            elif config.get('startup_mode')=='project_revision':
                build_project_revision()
            elif config.get('startup_mode')=='reference_v06':
                build_reference_model_v06()
            else:
                build_model()
            _created=True
            with open(os.path.join(os.path.dirname(__file__),'F14_build_response.json'),'w',encoding='utf-8') as stream:
                json.dump(execution_ack('startup','completed'),stream,indent=2)
            # Publish startup before polling so it cannot overwrite a job result.
            start_build_requests()
    except:
        try:
            with open(os.path.join(os.path.dirname(__file__),'F14TomcatRC_error.log'),'w',encoding='utf-8') as stream:
                stream.write(traceback.format_exc())
        except:
            pass
        if _ui:
            _ui.messageBox('F14TomcatRC error:\n'+traceback.format_exc())

def stop(context):
    global _created
    _worker_stop.set()
    if _app:
        _app.unregisterCustomEvent(_event_id)
    _handlers.clear()
    _created=False
