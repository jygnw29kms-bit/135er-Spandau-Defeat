# 135er – Spandau Defeat

**Current engine direction:** Counter-Strike 2 / Source 2 · free, non-commercial custom game/mod content.

135er – Spandau Defeat is a multiplayer FPS project centered on recognizable locations in Berlin-Spandau and selected historical Berlin scenarios. The gameplay target remains fast objective combat with a classic Day-of-Defeat-like immediacy, now implemented on the CS2 / Source 2 toolchain instead of Unreal Engine.

![135er – Spandau Defeat Source 2 optical masters](media/source2/source2-optical-masters-gallery.jpg)

> **Image status:** the gallery above is AI-generated **optical-master/reference art** created from the current Spandau map brief and the verified Source 2 / CS2 visual/tooling direction. It is **not** presented as an actual engine capture.

## Current technical baseline

- CS2 / Source 2 runtime
- Linux CS2 Dedicated Server
- CounterStrikeSharp server plugin: `source2/plugin/SpandauDefeat.cs`
- configurable tickets, objective state, map loading and Spandau game-mode base rules
- PufferPanel / JL76 portal integration
- Hammer / CS2 Workshop Tools for authored maps
- no redistribution of Valve engine binaries as a standalone engine fork

## Maps

Core Spandau set: Rathaus Spandau, Zitadelle, Staaken, Rodelberg, Kiesteich, Falkenhagener Feld, Lynarstraße, Wröhmännerpark, Freiheit, Martin-Buber-Schule, Askanier-Schule and B.-Traven-Schule.

Historical/special set: Fort Hahneberg 1945, Teufelsberg Cold War, Flugplatz Gatow 1945, Gatow Luftbrücke 1948, Radelandstraße 1945, Hakenfelde/Heeresamt 1944, Zitadelle 1. Mai 1945 and Britischer Sektor Spandau.

Historical material is labeled so documented events are not confused with gameplay fiction. See [docs/HISTORY_MAPS.md](docs/HISTORY_MAPS.md).

## Visual direction

The new Source 2 optical masters replace the old Unreal-era concept imagery. Their purpose is to define:
- cleaner/brighter competitive readability
- Source 2-like material and lighting targets
- restrained post-processing
- sharp environmental detail
- practical FPS sightlines and cover silhouettes
- recognizable Spandau landmarks and local urban character

They are art-direction references only. Final screenshots labeled **in-game** must be captured from the actual Source 2 maps after they are built in Hammer / CS2 Workshop Tools.

## Source references used for the visual direction

Valve's current Counter-Strike documentation confirms that CS2 uses Source 2, that the CS2 authoring package includes an updated Hammer editor, and that the Source 2 transition introduced updated lighting, materials and higher-resolution visual effects. These properties are used as guidance for the optical-master images; no official CS2 map is copied.

> This repository is the canonical project source for 135er – Spandau Defeat.
