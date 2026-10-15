# Rathaus architecture recovery review

## Decision

`SpandauStrike_Rathaus_WORLD_MASTER_v15_OPTIMIZED.blend` remains the production baseline. `RathausSpandau_REAL_Integrated_Master_v4.blend` must not be wholesale-merged.

The v15 master already contains substantially richer Rathaus geometry than the recovered v4 file: 5,139 Rathaus candidates / 40,502 polygons versus 365 candidates / 5,707 polygons in v4. v15 already has stronger equivalents for the central risalit, facade bands, pilasters, doors/arches, windows, plinth, tram and shelter detail.

## Confirmed review candidates from v4

The recovered v4 file is useful only as a targeted source for elements that currently have no convincing v15 counterpart:

- entrance stair run (`Step_0` through `Step_5`)
- Rathausplatz/plaza slab
- statue/plinth area
- upper tower termination above the current top cornice: crown/octagon/cupola/finial
- central gable, pending visual confirmation

## Alignment evidence

The three v4 entrance portals map to the three v15 production doors with an effectively exact translation:

`[-5.1978047689, +4.7629114787, +0.1000001431] m`

Residual RMS is about `0.0000013 m`, so the entrance frame is safe enough for a controlled stair-only candidate merge.

The tower frame is not safe yet. Best clock-face permutation still leaves about `3.57 m RMS` residual despite a clear approximately -90 degree XY rotation and -3.70 m Z shift. No cupola/finial merge is allowed until a better tower alignment is proven from shaft/corner geometry.

## v16 policy

The first v16 candidate may add only the six entrance steps using the proven entrance transform. Existing v15 doors, risalit, windows, roofs, tower shaft and facade detail remain untouched. Plaza/statue and tower-top elements require separate validation before inclusion.
