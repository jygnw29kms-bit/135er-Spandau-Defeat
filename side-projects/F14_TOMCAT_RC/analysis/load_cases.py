import csv, math, os

G=9.80665
MASS_KG=1.05
SEMISPAN_M=0.45
# Conservative resultant lift arm from centre structure/pivot region.
ROOT_ARM_M=0.25
BATTERY_KG=0.22
BATTERY_DECEL_G=20.0
EDF_THRUST_N_EACH=5.0
SWEEP_ACTUATOR_STALL_NM=2.0

rows=[]
for n in (3,6,8):
    total=MASS_KG*G*n
    half=total/2
    root_moment=half*ROOT_ARM_M
    rows.append({
        "case":f"LC_MANEUVER_{n}G",
        "load_factor_g":n,
        "total_vertical_N":round(total,3),
        "per_side_vertical_N":round(half,3),
        "root_bending_moment_Nm":round(root_moment,3),
        "notes":"Symmetric positive maneuver, conservative half-aircraft load per wing side"
    })

rows += [
    {
        "case":"LC_ASYMMETRIC_8G_70_30",
        "load_factor_g":8,
        "total_vertical_N":round(MASS_KG*G*8,3),
        "per_side_vertical_N":round(MASS_KG*G*8*0.70,3),
        "root_bending_moment_Nm":round(MASS_KG*G*8*0.70*ROOT_ARM_M,3),
        "notes":"70/30 asymmetric distribution; reported side is high-load wing"
    },
    {
        "case":"LC_BATTERY_20G_FORWARD",
        "load_factor_g":20,
        "total_vertical_N":round(BATTERY_KG*G*20,3),
        "per_side_vertical_N":0,
        "root_bending_moment_Nm":0,
        "notes":"Battery restraint forward inertial proof load"
    },
    {
        "case":"LC_EDF_THRUST",
        "load_factor_g":0,
        "total_vertical_N":round(2*EDF_THRUST_N_EACH,3),
        "per_side_vertical_N":round(EDF_THRUST_N_EACH,3),
        "root_bending_moment_Nm":0,
        "notes":"Twin EDF axial mount load; vibration handled as separate bench test"
    },
    {
        "case":"LC_SWEEP_JAM",
        "load_factor_g":0,
        "total_vertical_N":0,
        "per_side_vertical_N":0,
        "root_bending_moment_Nm":round(SWEEP_ACTUATOR_STALL_NM,3),
        "notes":"Actuator stall torque into hard stop / linkage; aerodynamic load superposed in Fusion study"
    },
]

out=os.path.join(os.path.dirname(__file__),"load_cases.csv")
with open(out,"w",newline="",encoding="utf-8") as f:
    w=csv.DictWriter(f,fieldnames=rows[0].keys())
    w.writeheader(); w.writerows(rows)

print("Baseline mass",MASS_KG,"kg")
for r in rows:
    print(r)
print("Wrote",out)
