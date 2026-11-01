from __future__ import annotations

import importlib
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from contextlib import ExitStack, redirect_stderr, redirect_stdout
from io import StringIO
from pathlib import Path
from unittest.mock import patch

TOOLS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TOOLS))
workflow = importlib.import_module("rathaus_finalization_workflow")
headless = importlib.import_module("run_rathaus_v75_front_spawn_headless_check")
target = importlib.import_module("rathaus_validation_target")
matrix = importlib.import_module("collect_spawn_to_combat_distance_matrix")


class FinalizationWorkflowTests(unittest.TestCase):
    def run_workflow(self, args=(), changed_revision=False, failing_phase=None):
        phases = []
        def run_phase(name, command):
            phases.append((name, command))
            if name == failing_phase:
                raise RuntimeError("simulated build failure")
        with tempfile.TemporaryDirectory() as tmp, ExitStack() as stack:
            state_file = Path(tmp) / "state.json"
            stack.enter_context(patch.object(workflow, "STATE_FILE", state_file))
            stack.enter_context(patch.object(workflow, "REPORT_DIR", Path(tmp)))
            stack.enter_context(patch.object(workflow, "git_head", return_value="test-source"))
            revisions = [{"git_head": "test-source"}, {"git_head": "different" if changed_revision else "test-source"}]
            stack.enter_context(patch.object(workflow, "source_revision", side_effect=revisions))
            stack.enter_context(patch.object(workflow, "run", side_effect=run_phase))
            stack.enter_context(redirect_stdout(StringIO()))
            stack.enter_context(redirect_stderr(StringIO()))
            code = workflow.main(list(args))
            state = json.loads(state_file.read_text(encoding="utf-8"))
        return code, state, phases

    def test_build_precedes_all_engine_gates(self):
        code, state, phases = self.run_workflow()
        self.assertEqual(code, 0)
        self.assertEqual(state["next_required"], "interactive_visual_and_playability_qa")
        names = [name for name, _ in phases]
        for name in ("rathaus_mapcheck", "rathaus_normal_runtime_gate", "spawn_to_combat_distance_matrix", "rathaus_round_probe", "rathaus_ticket_exhaustion_probe"):
            self.assertLess(names.index("ue5_lyra_editor_build"), names.index(name))

    def test_every_gate_receives_the_same_explicit_map(self):
        candidate = "/Game/Test/AcceptanceCandidate"
        code, state, phases = self.run_workflow(["--map-path", candidate])
        self.assertEqual(code, 0)
        self.assertEqual(state["map"], candidate)
        gates = [command for _, command in phases if "--map-path" in command]
        self.assertEqual(len(gates), 5)
        for command in gates:
            self.assertEqual(command[command.index("--map-path") + 1], candidate)

    def test_skipped_gates_cannot_produce_green(self):
        for flag in ("--skip-build", "--skip-matrix"):
            with self.subTest(flag=flag):
                code, state, _ = self.run_workflow([flag])
                self.assertNotEqual(code, 0)
                self.assertEqual(state["status"], "partial")
                self.assertTrue(state["skipped_checks"])

    def test_source_change_invalidates_successful_gates(self):
        code, state, _ = self.run_workflow(changed_revision=True)
        self.assertNotEqual(code, 0)
        self.assertEqual(state["status"], "blocked")
        self.assertIn("Source revision changed", state["error"])

    def test_failed_build_never_launches_engine_gates(self):
        code, state, phases = self.run_workflow(failing_phase="ue5_lyra_editor_build")
        self.assertNotEqual(code, 0)
        self.assertEqual(state["status"], "blocked")
        self.assertEqual(phases[-1][0], "ue5_lyra_editor_build")


class SourceRevisionTests(unittest.TestCase):
    def test_new_sources_invalidate_revision_but_generated_reports_do_not(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for command in (["git", "init", "-q"], ["git", "-c", "user.name=Test", "-c", "user.email=test@example.invalid", "commit", "--allow-empty", "-qm", "test"]):
                subprocess.run(command, cwd=root, check=True, capture_output=True)
            first = target.source_revision(root)
            source = root / "new_runtime.cpp"
            source.write_text("int version = 1;\n")
            second = target.source_revision(root)
            self.assertNotEqual(first, second)
            source.write_text("int version = 2;\n")
            third = target.source_revision(root)
            self.assertNotEqual(second, third)
            report = root / "ue5" / "Saved" / "Reports" / "run.json"
            report.parent.mkdir(parents=True)
            report.write_text('{"passed": true}')
            self.assertEqual(third, target.source_revision(root))


class DistanceMatrixTests(unittest.TestCase):
    def run_matrix(self, exit_code=0, actual=350.0, wrong_map=False, write_report=True):
        with tempfile.TemporaryDirectory() as tmp, ExitStack() as stack:
            root = Path(tmp)
            report_dir = root / "ue5" / "SpandauStrike" / "Saved" / "Reports"
            report_dir.mkdir(parents=True)
            report_path = report_dir / "v75_front_spawn_headless_workflow.json"
            payload = {"passed": True, "map": ("/Game/WrongMap" if wrong_map else target.DEFAULT_MAP) + "?Experience=test", "combat_probe_distance_cm": actual}
            report_path.write_text(json.dumps(payload))
            commands = []
            def run(command, **kwargs):
                commands.append(command)
                if write_report:
                    report_path.write_text(json.dumps(payload))
                return subprocess.CompletedProcess(command, exit_code)
            stack.enter_context(patch.object(matrix, "__file__", str(root / "tools" / "ue5" / "matrix.py")))
            stack.enter_context(patch.object(matrix.subprocess, "run", side_effect=run))
            stack.enter_context(patch.object(matrix, "source_revision", return_value={"git_head": "test"}))
            stack.enter_context(redirect_stdout(StringIO()))
            code = matrix.main(["--distances-cm", "350"])
            summary = json.loads((report_dir / "spawn_to_combat_distance_matrix.json").read_text())
            return code, summary, commands

    def test_fresh_matching_success(self):
        code, summary, commands = self.run_matrix()
        self.assertEqual(code, 0)
        self.assertTrue(summary["all_passed"])
        self.assertEqual(commands[0][commands[0].index("--map-path") + 1], target.DEFAULT_MAP)

    def test_failed_process_cannot_reuse_passed_report(self):
        self.assertNotEqual(self.run_matrix(exit_code=1)[0], 0)

    def test_old_report_is_not_reused_when_runner_writes_nothing(self):
        self.assertNotEqual(self.run_matrix(write_report=False)[0], 0)

    def test_wrong_distance_or_map_fails(self):
        self.assertNotEqual(self.run_matrix(actual=700.0)[0], 0)
        self.assertNotEqual(self.run_matrix(actual="350")[0], 0)
        self.assertNotEqual(self.run_matrix(wrong_map=True)[0], 0)


class TicketExhaustionLogTests(unittest.TestCase):
    END = "Spandau capture match ended: attackersWon=0 tickets=0 sector=1 reason=tickets-exhausted\n"

    def test_terminal_defender_win(self):
        self.assertTrue(headless.ticket_exhaustion_passed("Spandau respawn completed: bot\n" + self.END))

    def test_ticket_warning_alone_is_not_a_finished_match(self):
        self.assertFalse(headless.ticket_exhaustion_passed("Spandau attackers exhausted tickets\n"))

    def test_respawn_after_match_end_fails(self):
        self.assertFalse(headless.ticket_exhaustion_passed(self.END + "Spandau respawn completed: bot\n"))

    def test_duplicate_or_wrong_winner_fails(self):
        self.assertFalse(headless.ticket_exhaustion_passed(self.END * 2))
        self.assertFalse(headless.ticket_exhaustion_passed(self.END.replace("attackersWon=0", "attackersWon=1")))


@unittest.skipUnless(shutil.which("node"), "Node.js is required for the actual CSV analyzer")
class CsvAnalyzerTests(unittest.TestCase):
    def analyze(self, frames, ready=True, warmup="1", measure="2"):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            csv = root / "profile.csv"
            rows = ["FrameTime,GameThreadTime,RenderThreadTime,GPUTime,Events"]
            rows += ["16.666667,4,5,6," + ("LoadingScreen/Hide" if ready and i == 0 else "") for i in range(frames)]
            csv.write_text("\n".join(rows), encoding="utf-8")
            result = subprocess.run(["node", str(TOOLS / "analyze_rathaus_csv_profile.js"), str(csv), "--warmup", warmup, "--measure", measure, "--out-dir", str(root / "out")], capture_output=True, text=True)
            report_path = root / "out" / "profile_analysis.json"
            report = json.loads(report_path.read_text()) if report_path.exists() else None
            return result, report

    def test_complete_post_ready_window(self):
        result, report = self.analyze(600)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue(report["measurement_complete"])
        self.assertAlmostEqual(report["frame"]["avg_fps"], 60, places=3)

    def test_short_window_fails_but_preserves_report(self):
        result, report = self.analyze(120)
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse(report["measurement_complete"])

    def test_capture_without_ready_marker_fails(self):
        result, _ = self.analyze(600, ready=False)
        self.assertNotEqual(result.returncode, 0)

    def test_nonpositive_or_invalid_window_fails(self):
        for warmup, measure in (("-1", "2"), ("1", "0"), ("1", "NaN")):
            with self.subTest(warmup=warmup, measure=measure):
                result, _ = self.analyze(600, warmup=warmup, measure=measure)
                self.assertNotEqual(result.returncode, 0)


if __name__ == "__main__":
    unittest.main()
