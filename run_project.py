"""
CreatorIQ Unified Project Orchestrator
Runs Backend (FastAPI / Django) and Frontend (Vite React SPA) concurrently.
"""

import sys
import subprocess
import os
import time
import signal
import urllib.request
from pathlib import Path

# Fix Windows console encoding for UTF-8 emojis
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

ROOT_DIR = Path(__file__).resolve().parent
BACKEND_DIR = ROOT_DIR / "backend"
FRONTEND_DIR = ROOT_DIR / "frontend"

processes = []

def cleanup(signum=None, frame=None):
    print("\n\n [CreatorIQ Orchestrator] Shutting down all services gracefully...")
    for proc in processes:
        try:
            if sys.platform == "win32":
                subprocess.call(["taskkill", "/F", "/T", "/PID", str(proc.pid)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            else:
                proc.terminate()
        except Exception:
            pass
    print(" [CreatorIQ Orchestrator] All services stopped.")
    sys.exit(0)

signal.signal(signal.SIGINT, cleanup)
signal.signal(signal.SIGTERM, cleanup)

def check_backend_alive():
    try:
        req = urllib.request.urlopen("http://127.0.0.1:8000/api/health", timeout=1)
        return req.getcode() == 200
    except Exception:
        try:
            req = urllib.request.urlopen("http://localhost:8000/api/health", timeout=1)
            return req.getcode() == 200
        except Exception:
            return False

def main():
    print("================================================================")
    print(" [START] Starting CreatorIQ Unified Workspace (Backend + Frontend)")
    print("================================================================")

    python_exe = sys.executable
    # Verify Python has FastAPI and uvicorn, otherwise check venv
    try:
        subprocess.run([python_exe, "-c", "import fastapi, uvicorn"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
    except Exception:
        venv_python_win = BACKEND_DIR / "venv" / "Scripts" / "python.exe"
        venv_python_posix = BACKEND_DIR / "venv" / "bin" / "python"
        if venv_python_win.exists():
            python_exe = str(venv_python_win)
        elif venv_python_posix.exists():
            python_exe = str(venv_python_posix)

    # 1. Database Migrations
    print(" [1/3] Checking database migrations...")
    try:
        subprocess.run([python_exe, "manage.py", "migrate"], cwd=BACKEND_DIR, check=True)
        print(" [OK] Database ready.")
    except Exception as e:
        print(f" [INFO] Database migration notice: {e}")

    # 2. Check if Backend is already running on port 8000
    if check_backend_alive():
        print("\n [2/3] [OK] Backend API is already running at http://127.0.0.1:8000/api/health")
    else:
        print("\n [2/3] Launching Backend Server (FastAPI uvicorn)...")
        backend_cmd = [
            python_exe, "-m", "uvicorn", "main:app",
            "--host", "127.0.0.1",
            "--port", "8000"
        ]
        backend_proc = subprocess.Popen(backend_cmd, cwd=BACKEND_DIR)
        processes.append(backend_proc)

        # Poll until backend is responsive (up to 10 seconds)
        print(" Waiting for Backend server to start on http://127.0.0.1:8000...")
        for _ in range(20):
            time.sleep(0.5)
            if check_backend_alive():
                print(" [OK] Backend API ready!")
                break
        else:
            print(" [INFO] Backend process started; waiting for full initialization...")

    # 3. Launch Frontend (Vite Dev Server)
    print("\n [3/3] Launching Frontend SPA at http://localhost:5173...")
    npm_cmd = "npm.cmd" if sys.platform == "win32" else "npm"
    frontend_cmd = [npm_cmd, "run", "dev"]
    frontend_proc = subprocess.Popen(frontend_cmd, cwd=FRONTEND_DIR)
    processes.append(frontend_proc)

    print("\n================================================================")
    print(" [SUCCESS] CreatorIQ is running successfully!")
    print(" Frontend UI:  http://localhost:5173")
    print(" Backend API:  http://127.0.0.1:8000/api/")
    print(" Health API:   http://127.0.0.1:8000/api/health")
    print(" Agency Route: http://localhost:5173/agency")
    print(" Press Ctrl+C to stop servers.")
    print("================================================================\n")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        cleanup()

if __name__ == "__main__":
    main()
