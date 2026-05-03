#!/usr/bin/env python3
"""Convenience launcher for the FastAPI backend.

Usage:
    python run.py                    # alembic upgrade + uvicorn with autoreload on :8000
    python run.py --port 9000
    python run.py --no-reload
    python run.py --skip-migrate

Requires `uv` on PATH and a reachable Postgres (e.g. `docker compose up -d db`).
"""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path

BACKEND = Path(__file__).resolve().parent / "backend"


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the ChatTemplate FastAPI backend")
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--port", type=int, default=8000)
    parser.add_argument("--no-reload", action="store_true", help="Disable autoreload")
    parser.add_argument("--skip-migrate", action="store_true", help="Skip alembic upgrade head")
    args = parser.parse_args()

    if shutil.which("uv") is None:
        print("error: `uv` not found on PATH. Install from https://docs.astral.sh/uv/", file=sys.stderr)
        return 1

    os.chdir(BACKEND)

    if not args.skip_migrate:
        rc = subprocess.call(["uv", "run", "alembic", "upgrade", "head"])
        if rc != 0:
            print("error: alembic upgrade failed (is Postgres up?)", file=sys.stderr)
            return rc

    cmd = ["uv", "run", "uvicorn", "api.main:app", "--host", args.host, "--port", str(args.port)]
    if not args.no_reload:
        cmd.append("--reload")
    os.execvp(cmd[0], cmd)


if __name__ == "__main__":
    sys.exit(main())
