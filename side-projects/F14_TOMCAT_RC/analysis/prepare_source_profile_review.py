"""Build a normalized Fusion profile gallery dataset, never an aircraft loft."""
import json
from pathlib import Path
from validate_source_contours import validate

ROOT=Path(__file__).resolve().parents[1]


def run():
    folder=ROOT/'analysis'
    original=json.loads((folder/'upc_source_section_candidates_v07.json').read_text())
    corrected_c=json.loads((folder/'upc_C_intake_topology_v13.json').read_text())
    corrected_f=json.loads((folder/'upc_F_connected_section_v11.json').read_text())
    profiles=[]
    for index,name in enumerate(['A','B','C','D','E','F']):
        base=next(s for s in original['profiles'] if s['name']==('F_R' if name=='F' else name))
        if name=='C':
            outer=corrected_c['outer_skin_pixel_outline']; holes=corrected_c['inner_opening_pixel_loops']
        elif name=='F':
            outer=corrected_f['pixel_outline']; holes=[]
        else:
            outer=base['pixel_outline']; holes=[]
        validation=validate(outer,holes)
        cx,cy=base['source_section_axis_pixel']
        radius=(max(p[0] for p in outer)-min(p[0] for p in outer))/2
        normalize=lambda loop:[[(x-cx)/radius,(cy-y)/radius] for x,y in loop]
        profiles.append(dict(name=name,gallery_plane_x_mm=index*250,
                             candidate_station_fraction=base['station_fraction_candidate'],
                             outer_normalized=normalize(outer),holes_normalized=[normalize(h) for h in holes],
                             expected_native_profile_count=1+len(holes),topology_validation=validation))
    data=dict(status='NORMALIZED_SOURCE_PROFILE_GALLERY_ONLY',
              source_image_sha256=original['source_image_sha256'],
              gallery_half_width_mm=100,gallery_spacing_mm=250,
              aircraft_coordinates=False,aircraft_metric_registration=False,
              aircraft_waterline_registration=False,loft_allowed=False,
              warning='Each section independently normalized to 200 mm width; spacing is gallery layout, not aircraft stations.',
              profiles=profiles)
    target=ROOT/'cad/fusion/F14TomcatRC/F14_source_profile_review_v14.json'
    target.write_text(json.dumps(data,indent=2)+'\n')
    print(json.dumps({'status':data['status'],'validated_sections':len(profiles),'target':str(target)}))


if __name__=='__main__': run()
