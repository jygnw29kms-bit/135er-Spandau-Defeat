# Playermodel 2030 pipeline

The four production character identities are fixed by `playermodel_contract.json`.

SourceArt belongs under `ue5/SpandauStrike/SourceArt/Characters/2030/` and must contain the Blender master plus the four named FBX exports. Do not import ad-hoc character files from user-specific paths.

UE should stay closed while modeling, rig auditing, FBX export, naming checks and Git/LFS work are performed. Open UE only for skeleton/retarget/import/runtime validation, then close it again.

The required bone contract intentionally matches the stable Spandau Strike rig naming used for Lyra retarget preparation. Additional twist/finger/accessory bones are allowed; required bones may not be renamed or removed.
