# Bambu Lab P2S - PETG R2 print setup

The generated 3MF files contain tested plate layouts and separate objects. Filament temperature/flow must still be calibrated for the actual PETG spool.

## Baseline
- 0.4 mm nozzle
- 0.20 mm layers; 0.16 mm for pivot/mechanism plates
- Start around 245 C nozzle / 80 C bed
- Max volumetric flow about 8 mm3/s shell, 7 mm3/s structural
- Outer wall about 60 mm/s
- Inner wall about 90-100 mm/s
- 5-8 mm brim for narrow/high parts

## Profile groups
- LIGHT_SHELL: 3 walls, 3 top/bottom, 5% gyroid
- WING_LIGHT: 3 walls, 4 top/bottom, 7% gyroid
- STRUCTURAL: 6 walls, 6 top/bottom, 45% gyroid, 0.16-0.20 mm
- STRUCTURAL_LIGHT: 4 walls, 15% gyroid
- DUCT: 3 walls, 10% gyroid, favor smooth inner wall
- CONTROL_SURFACE: 3 walls, 9% gyroid; identical settings left/right
- MIXED: per-object settings
