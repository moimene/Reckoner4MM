"""Regression tests for the local launcher; isolated files and simulated processes."""
import contextlib
import importlib.util
import io
import os
from pathlib import Path
import signal
import socket
import tempfile
import unittest
from unittest.mock import Mock, patch

spec = importlib.util.spec_from_file_location("launcher", Path(__file__).parents[1] / "scripts/local.py")
launcher = importlib.util.module_from_spec(spec)
spec.loader.exec_module(launcher)


class LauncherTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        root = Path(self.temp.name)
        for name, value in {"ROOT": root, "RUNTIME": root / ".local-runtime",
                            "STATE": root / ".local-runtime/processes.json", "CONFIG": root / ".env.local"}.items():
            p = patch.object(launcher, name, value)
            p.start()
            self.addCleanup(p.stop)
        launcher.RUNTIME.mkdir()

    def test_environment_does_not_inherit_provider_secrets(self):
        with patch.dict(os.environ, {"OPENAI_API_KEY": "synthetic", "AWS_PROFILE": "synthetic",
                                     "GCP_SERVICE_ACCOUNT_JSON": "synthetic", "NODE_OPTIONS": "synthetic",
                                     "HTTPS_PROXY": "synthetic", "RECKONER_PASSWORD": "synthetic"}):
            env = launcher.clean_environment()
        self.assertTrue(set(env) <= {"PATH", "HOME", "USER", "LOGNAME", "TMPDIR", "LANG", "LC_ALL",
                                    "PYTHONUNBUFFERED", "AWS_EC2_METADATA_DISABLED"})

    def test_password_is_stable_and_private(self):
        first = launcher.local_password()
        self.assertEqual(first, launcher.local_password())
        self.assertEqual(launcher.CONFIG.stat().st_mode & 0o777, 0o600)
        self.assertGreaterEqual(len(first), 24)

    def test_lost_key_is_not_replaced_for_existing_database(self):
        database = launcher.ROOT / "backend/data/tracker.db"
        database.parent.mkdir(parents=True)
        database.touch()
        with self.assertRaises(RuntimeError):
            launcher.local_password()
        self.assertFalse(launcher.CONFIG.exists())

    def test_empty_password_is_rejected(self):
        launcher.CONFIG.write_text("RECKONER_PASSWORD=\n")
        with self.assertRaises(RuntimeError):
            launcher.local_password()

    def test_other_checkout_state_is_rejected(self):
        launcher.STATE.write_text('{"root":"/different-checkout","services":{}}')
        with self.assertRaises(RuntimeError):
            launcher.load_state()

    def test_busy_port_is_left_untouched(self):
        with socket.socket() as listener:
            listener.bind(("127.0.0.1", 0))
            listener.listen()
            port = listener.getsockname()[1]
            with self.assertRaises(RuntimeError):
                launcher.require_free_port(port)
            with socket.create_connection(("127.0.0.1", port)):
                pass

    def test_reused_pid_is_never_signalled(self):
        record = {"pid": 999991, "identity": "old process"}
        with patch.object(launcher, "identity", return_value="another process"), \
             patch.object(launcher.os, "killpg") as kill, contextlib.redirect_stdout(io.StringIO()):
            launcher.stop_services({"backend": record})
        kill.assert_not_called()

    def test_start_is_idempotent(self):
        with patch.object(launcher, "load_state", return_value={"backend": {}, "frontend": {}}), \
             patch.object(launcher, "owned", return_value=True), patch.object(launcher, "healthy", return_value=True), \
             patch.object(launcher.subprocess, "Popen") as spawn, contextlib.redirect_stdout(io.StringIO()):
            launcher.start()
        spawn.assert_not_called()

    def test_state_write_failure_stops_new_process_from_memory(self):
        for path in ("backend/.venv/bin/python", "frontend/node_modules/vite/bin/vite.js"):
            target = launcher.ROOT / path
            target.parent.mkdir(parents=True, exist_ok=True)
            target.touch()
        with patch.object(launcher, "require_free_port"), patch.object(launcher.shutil, "which", return_value="/node"), \
             patch.object(launcher.subprocess, "Popen", return_value=Mock(pid=999991)), \
             patch.object(launcher, "identity", return_value="new process"), \
             patch.object(launcher, "save_state", side_effect=OSError("simulated full disk")), \
             patch.object(launcher, "owned", side_effect=[True, False, False]), \
             patch.object(launcher.os, "killpg") as kill, contextlib.redirect_stdout(io.StringIO()):
            with self.assertRaises(OSError):
                launcher.start()
        kill.assert_called_once_with(999991, signal.SIGTERM)


if __name__ == "__main__":
    unittest.main()
