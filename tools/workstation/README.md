# Workstation guards

`lucas_user_activity_guard.ps1` is a read-only preflight gate for unattended work on the Lucas workstation.

It samples Windows last-input time and cursor position. Exit code `0` means the machine is idle enough for light automated work; exit code `10` means user activity was detected and automation must stop.

Before heavy work such as Unreal Editor, Blender rendering, shader compilation or bulk export, run the guard again immediately and also check for foreground gaming/rendering processes. Heavy work must not start while the user is active or a game such as OMSI is using the machine.

The guard never injects input and never changes system settings.