#!/usr/bin/env python3
"""Local lifecycle for Reckoner4MM. Standard library only; no provider credentials inherited."""

import argparse
import fcntl
import json
import os
from pathlib import Path
import secrets
import shutil
import signal
import socket
import subprocess
import sys
import time
import urllib.error
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
RUNTIME = ROOT / ".local-runtime"
STATE = RUNTIME / "processes.json"
CONFIG = ROOT / ".env.local"
API = "http://127.0.0.1:8014"
WEB = "http://127.0.0.1:5174"


def local_password():
    if not CONFIG.exists():
        # Never silently replace a missing encryption key for an existing database.
        if (ROOT / "backend/data/tracker.db").exists():
            raise RuntimeError("Falta .env.local y ya existe una base de datos. Restaura su contraseña original.")
        fd = os.open(CONFIG, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        with os.fdopen(fd, "w") as stream:
            stream.write("# Contraseña local: conservar junto con la copia de seguridad de SQLite.\n")
            stream.write("RECKONER_PASSWORD=" + secrets.token_urlsafe(24) + "\n")
    if CONFIG.is_symlink():
        raise RuntimeError(".env.local debe ser un archivo local, no un enlace simbólico.")
    CONFIG.chmod(0o600)
    values = {}
    for line in CONFIG.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            key, value = line.split("=", 1)
            values[key.strip()] = value.strip()
    password = values.get("RECKONER_PASSWORD", "")
    if not password:
        raise RuntimeError("RECKONER_PASSWORD está vacía en .env.local; no se arrancará sin protección.")
    return password


def clean_environment():
    # Allowlist, rather than a list of known secrets that could miss a new provider.
    allowed = ("PATH", "HOME", "USER", "LOGNAME", "TMPDIR", "LANG", "LC_ALL")
    env = {key: os.environ[key] for key in allowed if key in os.environ}
    user_dir = Path.home()
    env["PATH"] = os.pathsep.join([
        str(user_dir / ".local/bin"), "/opt/homebrew/bin", "/usr/local/bin",
        env.get("PATH", "/usr/bin:/bin"),
    ])
    env["PYTHONUNBUFFERED"] = "1"
    env["AWS_EC2_METADATA_DISABLED"] = "true"
    return env


def identity(pid):
    result = subprocess.run(
        ["/bin/ps", "-p", str(pid), "-o", "lstart=", "-o", "command="],
        capture_output=True, text=True, check=False,
    )
    return result.stdout.strip() if result.returncode == 0 else ""


def owned(record):
    try:
        pid = record["pid"]
        return (isinstance(pid, int) and pid > 1 and
                identity(pid) == record["identity"] and bool(record["identity"]) and
                os.getpgid(pid) == pid)
    except (KeyError, OSError, TypeError):
        return False


def load_state():
    if not STATE.exists():
        return {}
    data = json.loads(STATE.read_text())
    if data.get("root") != str(ROOT):
        raise RuntimeError("El registro de procesos pertenece a otra carpeta; no se tocará.")
    return data.get("services", {})


def save_state(services):
    pending = STATE.with_suffix(".tmp")
    pending.write_text(json.dumps({"root": str(ROOT), "services": services}, indent=2) + "\n")
    pending.chmod(0o600)
    pending.replace(STATE)


def healthy():
    try:
        opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
        with opener.open(API + "/api/health", timeout=2) as response:
            health = json.load(response)
        with opener.open(WEB, timeout=2) as response:
            page_ok = response.status == 200
        return health.get("status") == "ok" and health.get("db_connected") is True and page_ok
    except (OSError, ValueError, urllib.error.URLError):
        return False


def stop_services(services):
    for name, record in services.items():
        if owned(record):
            try:
                os.killpg(record["pid"], signal.SIGTERM)
            except ProcessLookupError:
                pass
    deadline = time.monotonic() + 8
    while time.monotonic() < deadline and any(owned(r) for r in services.values()):
        time.sleep(0.1)
    for name, record in services.items():
        if owned(record):
            raise RuntimeError("El servicio " + name + " no se ha detenido; revisa su log local.")
    STATE.unlink(missing_ok=True)
    print("Servicios propios detenidos. Los datos y la contraseña se conservan.")


def stop():
    stop_services(load_state())


def require_free_port(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        # Match server bind semantics: TIME_WAIT after a clean stop is not a listener.
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            sock.bind(("127.0.0.1", port))
        except OSError:
            raise RuntimeError("El puerto " + str(port) + " está ocupado. No se ha detenido el proceso que lo usa.")


def start():
    services = load_state()
    if set(services) == {"backend", "frontend"} and all(owned(r) for r in services.values()):
        if healthy():
            print("Reckoner4MM ya está funcionando: " + WEB)
            return
        raise RuntimeError("Los servicios propios están activos pero no saludables. Revisa los logs o usa restart.")
    if services:
        stop()
    for port in (8014, 5174):
        require_free_port(port)
    python = ROOT / "backend/.venv/bin/python"
    vite = ROOT / "frontend/node_modules/vite/bin/vite.js"
    env = clean_environment()
    node = shutil.which("node", path=env["PATH"])
    if not python.exists() or not vite.exists() or not node:
        raise RuntimeError("Faltan dependencias. Sigue la instalación uv/pnpm del README.")
    password = local_password()
    backend_env = dict(env, RECKONER_PASSWORD=password, RECKONER_PROTECT_DASHBOARD="true",
                       FRONTEND_URL=WEB, LOG_LEVEL="INFO")
    frontend_env = dict(env, VITE_API_URL=API)
    specs = (
        ("backend", [str(python), "-m", "uvicorn", "main:app", "--host", "127.0.0.1",
                     "--port", "8014"], ROOT / "backend", backend_env),
        ("frontend", [node, str(vite), "--host", "127.0.0.1", "--port", "5174", "--strictPort"],
         ROOT / "frontend", frontend_env),
    )
    services = {}
    try:
        for name, command, cwd, child_env in specs:
            with (RUNTIME / (name + ".log")).open("ab") as log:
                process = subprocess.Popen(command, cwd=cwd, env=child_env, stdin=subprocess.DEVNULL,
                                           stdout=log, stderr=subprocess.STDOUT, start_new_session=True)
            services[name] = {"pid": process.pid, "identity": identity(process.pid)}
            save_state(services)
        deadline = time.monotonic() + 35
        while time.monotonic() < deadline:
            if not all(owned(r) for r in services.values()):
                raise RuntimeError("Un servicio terminó durante el arranque; revisa .local-runtime/*.log.")
            if healthy():
                print("Reckoner4MM disponible: " + WEB)
                print("Contraseña guardada solo en .env.local; consulta con: python3 scripts/local.py password")
                return
            time.sleep(0.3)
        raise RuntimeError("El arranque no pasó la comprobación de salud; revisa los logs locales.")
    except BaseException:
        # A disk write may have failed after Popen: the in-memory map is complete.
        stop_services(services)
        raise


def main():
    parser = argparse.ArgumentParser(description="Reckoner4MM local: servicios aislados y contraseña persistente.")
    parser.add_argument("action", choices=("start", "stop", "restart", "status", "open", "password"))
    action = parser.parse_args().action
    os.umask(0o077)
    RUNTIME.mkdir(exist_ok=True, mode=0o700)
    with (RUNTIME / "launcher.lock").open("a") as lock:
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            raise RuntimeError("Hay otra operación de inicio/parada en curso.")
        if action == "password":
            if not sys.stdout.isatty():
                raise RuntimeError("La contraseña solo se muestra en una terminal interactiva, nunca en logs o tuberías.")
            print(local_password())
        elif action == "status":
            services = load_state()
            active = set(services) == {"backend", "frontend"} and all(owned(r) for r in services.values())
            if active and healthy():
                print("ACTIVO " + WEB + " — backend y SQLite saludables")
            else:
                print("DETENIDO o PARCIAL — consulta los logs locales")
                return 1
        elif action == "stop":
            stop()
        else:
            if action == "restart":
                stop()
            start()
            if action == "open":
                subprocess.run(["/usr/bin/open", WEB], check=True, env=clean_environment())
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (RuntimeError, OSError, ValueError) as error:
        print("Reckoner4MM: " + str(error), file=sys.stderr)
        sys.exit(1)
