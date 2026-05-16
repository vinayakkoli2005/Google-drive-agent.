import subprocess
import sys
import time

def main():
    print("Starting FastAPI backend...")
    python_exe = "venv/Scripts/python.exe"
    backend = subprocess.Popen(
        [python_exe, "-m", "uvicorn", "backend.main:app", "--reload", "--port", "8000"],
    )
    
    # Wait a bit for backend to start
    time.sleep(2)
    
    print("Starting Streamlit frontend...")
    frontend = subprocess.Popen(
        [python_exe, "-m", "streamlit", "run", "frontend/app.py"]
    )
    
    try:
        backend.wait()
        frontend.wait()
    except KeyboardInterrupt:
        print("Shutting down...")
        backend.terminate()
        frontend.terminate()

if __name__ == "__main__":
    main()
