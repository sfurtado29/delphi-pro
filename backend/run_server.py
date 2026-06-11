"""
Run the FastAPI app without the multiprocessing reload behavior.

On Windows the `uvicorn --reload` reloader uses subprocesses which can
produce CancelledError / KeyboardInterrupt traces during reloads. Use
this script during development when you want a stable single-process
run. It does NOT enable auto-reload.

Usage:
    python run_server.py

To get auto-reload behavior, continue to use:
    python -m uvicorn main:app --reload
but be aware the reloader spawns subprocesses and may show the traces
you reported (these are usually benign restarts).
"""
import uvicorn

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=False)
