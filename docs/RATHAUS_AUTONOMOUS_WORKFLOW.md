# Rathaus Autonomous Workflow

## Ziel
Rathaus wird nicht nach einzelnen Tests als "fertig" behandelt. Der Arbeitsblock läuft von einem verifizierten Zustand zum nächsten, bis alle technischen Gates grün sind und die interaktive Visual-/Playability-QA abgeschlossen ist.

## Verbindliche Regeln
1. Arbeitsrechner ist ausschließlich Lucas (`DESKTOP-SMN4ATU`).
2. Ein roter Test ist ein Diagnose-Ereignis, kein Haltepunkt. Ursache eingrenzen, beheben, denselben Gate erneut ausführen.
3. Statusmeldungen zählen nur verifizierte Artefakte: Git-Commit, Report, Screenshot, Test-/Build-Ausgabe.
4. Headless-UE, Validator und Visual-UE verwenden getrennte Logdateien. Kein gemeinsames `SpandauStrike.log` mehr als Workflow-Abhängigkeit.
5. Visual-UE darf nur in der interaktiven Benutzer-Session laufen. Headless-Builds/Gates dürfen über DCO/LocalSystem laufen.
6. Temporäre Scheduled Tasks, Startup-Hooks und Testdateien werden nach dem Versuch entfernt oder sauber ins Repo übernommen.
7. Vor einem Commit: `py_compile`, `git diff --check`, Gameplay-Validatoren, Unit-Tests, relevanter UE-Runtime-Gate und UE-Build.
8. Nach einem grünen Teilblock unmittelbar den nächsten Block beginnen. Kein Zustand "grün und warten".

## Resumierbarer technischer Gate
`tools/ue5/rathaus_finalization_workflow.py`

Der Runner schreibt seinen Zustand nach:
`ue5/SpandauStrike/Saved/Reports/rathaus_finalization_state.json`

Phasen:
- Python-Compile
- `git diff --check`
- Runtime-Combat-Validator
- Gameplay-Bundle-Validator
- Unit-Tests
- normaler Rathaus-v75 Runtime-Gate
- 350/700/1200 Spawn-to-Combat-Matrix
- LyraEditor Build

Jede Phase schreibt Exitcode und Ausgabe-Tail in die Zustandsdatei. Ein Fehler markiert `status=blocked` und nennt `next_required=diagnose_last_failed_phase_then_resume`. Nach Behebung wird derselbe Workflow erneut gestartet.

## Final-Definition Rathaus
Technisch grün reicht nicht. Final spielbar verlangt zusätzlich:
- sichtbaren Start im echten Editor/Game-Viewport
- Frontspawn-Laufwege und tatsächliche LOS visuell geprüft
- Rathaus-Fassade/Readability aus Spielerperspektive geprüft
- keine Durchfall-/KillZ-/Kollisionsfehler
- Navigation der Bots durch die vier Frontsektoren
- Capture, Sektorwechsel, Tickets und Respawns im echten Rundenfluss
- Combat-Handoff ShooterCore ↔ Objective-Routing
- keine unerwarteten Runtime-Fehler
- Performance-Prüfung im echten Rendering-Pfad
- finaler Screenshot-/Visual-QA-Stand gespeichert
- finaler Commit und Push

## Arbeitspriorität
1. Blocker beseitigen, der mehrere Gates verhindert.
2. Gameplay-/Runtime-Gates grün halten.
3. Visual- und Playability-QA.
4. Map-Polish nur mit Vergleichsscreenshot und Regressionstest.
5. Commit/Push kleiner, stabiler Blöcke.

Damit ersetzt ein einziger fortsetzbarer Ablauf die bisherige Folge aus Statusprüfungen, Einzelkommandos und vergessenen Zwischenständen.
