#!/usr/bin/env python3
"""Bootstrap acceptance on an EMPTY local installation. Never prints credentials/tokens."""
import argparse
import json
from pathlib import Path
import sqlite3
import subprocess
import sys
import urllib.error
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
BASE = "http://127.0.0.1:8014/api"
OPENER = urllib.request.build_opener(urllib.request.ProxyHandler({}))


def request(path, method="GET", data=None, token=None):
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = "Bearer " + token
    req = urllib.request.Request(BASE + path, method=method, headers=headers,
                                 data=json.dumps(data).encode() if data is not None else None)
    try:
        with OPENER.open(req, timeout=20) as response:
            return response.status, json.load(response)
    except urllib.error.HTTPError as error:
        return error.code, None


def snapshot_ids():
    with sqlite3.connect((ROOT / "backend/data/tracker.db").as_uri() + "?mode=ro", uri=True) as db:
        return {row[0] for row in db.execute("SELECT id FROM balance_snapshots")}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--restart", action="store_true", help="Reinicia solo los servicios gestionados por local.py")
    args = parser.parse_args()
    config = ROOT / ".env.local"
    original = config.read_bytes()
    password = next(line.split("=", 1)[1] for line in original.decode().splitlines()
                    if line.startswith("RECKONER_PASSWORD="))
    status, health = request("/health")
    assert status == 200 and health["status"] == "ok" and health["db_connected"] is True, "Health inválida"
    status, auth = request("/auth/status")
    assert status == 200 and auth["auth_enabled"] and auth["dashboard_protected"], "Auth no protegida"
    for path in ("/credits/", "/credits/providers", "/settings/providers"):
        assert request(path)[0] == 401, "Ruta anónima inesperada: " + path
    assert request("/settings/providers/openrouter", "PUT", {})[0] == 401, "Mutación anónima permitida"
    assert request("/auth/login", "POST", {"password": "intentionally-invalid"})[0] == 401, "Login incorrecto permitido"
    status, login = request("/auth/login", "POST", {"password": password})
    assert status == 200 and login["token"], "Login válido rechazado"
    token = login["token"]
    status, providers = request("/credits/providers", token=token)
    assert status == 200 and len(providers) == 19, "Catálogo distinto del baseline"
    assert all(p["is_configured"] is False for p in providers), "Hay proveedores configurados; no se hará refresh"
    status, dashboard = request("/credits/", token=token)
    assert status == 200 and len(dashboard["providers"]) == 19
    assert all(p["status"] == "unconfigured" for p in dashboard["providers"]), "Este test exige una instalación vacía"
    assert dashboard["total_usd_balance"] is None, "Saldo ficticio en panel vacío"
    # With no credentials, refresh creates real unconfigured snapshots, never fabricated balances.
    assert request("/credits/refresh", "POST", token=token)[0] == 200, "Refresh fallido"
    ids_before = snapshot_ids()
    assert ids_before, "No hay snapshots de estado para verificar persistencia"
    checks = {"health": "PASS", "auth_and_protected_routes": "PASS", "catalogue": 19,
              "empty_dashboard": "PASS", "unconfigured_snapshots": "PASS"}
    if args.restart:
        subprocess.run([sys.executable, str(ROOT / "scripts/local.py"), "restart"], check=True)
        assert config.read_bytes() == original, "La contraseña cambió al reiniciar"
        assert ids_before <= snapshot_ids(), "Snapshots perdidos al reiniciar"
        assert request("/credits/", token=token)[0] == 401, "JWT antiguo sigue válido tras reinicio upstream"
        assert request("/auth/login", "POST", {"password": password})[0] == 200, "Contraseña no persiste"
        checks["restart_password_sqlite_and_jwt"] = "PASS"
    print(json.dumps(checks, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
