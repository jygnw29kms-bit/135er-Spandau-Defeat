# Workstation guards

Spandau Strike work is performed only on Lucas' workstation `DESKTOP-SMN4ATU`.

`lucas_spandau_preflight.cmd` verifies the local repo, Git, Blender 4.5.10 LTS, Unreal Engine 5.8, the `.uproject` and the current v51 Blender master. It also reports whether the Git working tree is dirty.

`lucas_user_activity_guard.ps1` is a read-only gate for unattended light work. Exit code `0` means the machine is idle enough; exit code `10` means user activity was detected and automation must stop.

`lucas_heavy_work_guard.ps1` must be used immediately before Unreal Editor, Blender rendering, shader compilation or bulk exports. Heavy work must not start while Lucas is actively using the PC or a game/rendering workload is consuming the machine.

The guards never inject user input and do not change system settings.
