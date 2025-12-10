"""
Script to run the FastAPI server
"""
import uvicorn
import os
import sys
import time
import socket
import subprocess
from pathlib import Path
from dotenv import load_dotenv

def is_port_in_use(port):
    """Check if a port is already in use"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0

def kill_process_on_port(port):
    """Kill any process using the specified port"""
    if sys.platform == "win32":
        command = f'netstat -ano | findstr :{port}'
        result = subprocess.run(command, capture_output=True, text=True, shell=True)
        for line in result.stdout.splitlines():
            if 'LISTENING' in line:
                try:
                    pid = int(line.strip().split()[-1])
                    subprocess.run(f'taskkill /F /PID {pid}', capture_output=True, shell=True)
                    print(f"Killed process {pid} on port {port}")
                except (ValueError, IndexError):
                    pass
    else:  # Linux/macOS
        command = f'lsof -i :{port} | grep LISTEN | awk \'{{print $2}}\''
        result = subprocess.run(command, capture_output=True, text=True, shell=True)
        for pid in result.stdout.strip().splitlines():
            if pid.isdigit():
                subprocess.run(f'kill -9 {pid}', capture_output=True, shell=True)
                print(f"Killed process {pid} on port {port}")

if __name__ == "__main__":
    # Load .env file FIRST before checking for API key
    env_path = Path(__file__).parent / '.env'
    load_dotenv(dotenv_path=env_path)
    
    print("=" * 70)
    print("Mathematical Question Refinement Chatbot - Server")
    print("=" * 70)
    
    # Check for API key (now it will check after loading .env)
    if not os.getenv("GROQ_API_KEY"):
        print("\nWARNING: GROQ_API_KEY environment variable is not set!")
        print("Please set it before using the API endpoints:")
        print("  Windows (PowerShell): $env:GROQ_API_KEY='your-key-here'")
        print("  Windows (CMD): set GROQ_API_KEY=your-key-here")
        print("  Linux/Mac: export GROQ_API_KEY='your-key-here'")
        print("\nGet your free API key from: https://console.groq.com/")
        print("\nContinuing anyway... (API calls will fail without the key)")
    else:
        print("\nGROQ_API_KEY is set. Server ready!")
    
    print("\n" + "=" * 70)
    print("Starting server on http://0.0.0.0:8000")
    print("API Documentation: http://localhost:8000/docs")
    print("Press CTRL+C to stop the server")
    print("=" * 70 + "\n")
    
    # Add project root and backend to Python path so backend imports work
    project_root = Path(__file__).parent
    backend_dir = project_root / "backend"
    
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))
    if str(backend_dir) not in sys.path:
        sys.path.insert(0, str(backend_dir))
    
    # Ensure port is free
    if is_port_in_use(8000):
        print(f"Port 8000 is already in use. Attempting to kill process...")
        kill_process_on_port(8000)
        time.sleep(1)  # Give OS a moment to release the port
        if is_port_in_use(8000):
            print(f"WARNING: Port 8000 is still in use after attempt to kill. Server might not start.")
    
    # Run the server
    try:
        uvicorn.run(
            "backend.main:app",
            host="0.0.0.0",
            port=8000,
            reload=False,  # Set to False to avoid issues
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\n\nServer stopped by user.")
    except Exception as e:
        print(f"\n\nError starting server: {e}")
        sys.exit(1)

