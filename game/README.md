# Unreal source snapshots

Current repository graphics pass: **0.5.1-sharp-ingame**

- Engine target: Unreal Engine 5.8 C++
- Game target: `SpandauDefeat`
- Dedicated server target: `SpandauDefeatServer`
- Dedicated server platform target: Linux x86_64
- default gameplay port: 27135

Current packed archive:
- `releases/135er-spandau-defeat-unreal-0.5.0-visual-master-code.tar.xz`

Repository-side 0.5.1 additions:
- `config/SharpIngame.ini` — production client rendering/sharpness profile
- `../docs/INGAME_CAPTURE_STANDARD.md` — requirements for real gameplay screenshots
- `../media/ingame/` — dedicated location for captured UE5 gameplay images

0.5.0 introduced the visual-master implementation layer: live HUD, ticket state, ammunition/reload, master-look post processing/fog/lighting defaults and high-quality renderer/scalability configuration.

0.5.1 tightens image clarity and capture quality without changing the render-free dedicated-server path.

A new packed source archive should be generated from the full UE5 source tree rather than fabricating a partial archive from repository-side documentation/config only.
