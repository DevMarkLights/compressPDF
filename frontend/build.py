import os
import sys
import shutil
import subprocess
from pathlib import Path

def run_command(command, cwd=None):
    """Run a command and handle errors"""
    try:
        result = subprocess.run(
            command, 
            shell=True, 
            cwd=cwd, 
            check=True,
            capture_output=True, text=True
        )
        return result
    except subprocess.CalledProcessError as e:
        print(f"Command failed: {command}")
        print(f"Error: {e.stderr}")
        sys.exit(1)

def main():
    # Get directories
    frontend_dir = Path(__file__).parent
    backend_dir = frontend_dir.parent / "backend"
    dist_dir = frontend_dir / "dist"
    backend_dist = backend_dir / "dist"
    
    print(f"Frontend directory: {frontend_dir}")
    print(f"Backend directory: {backend_dir}")
    
    # Change to frontend directory
    os.chdir(frontend_dir)
    
    # Remove old dist in backend
    if backend_dist.exists():
        print("Removing old backend dist...")
        shutil.rmtree(backend_dist)
    
    # Build frontend
    print("Building frontend...")
    run_command("npm run build", cwd=frontend_dir)
    
    # Copy dist to backend
    if dist_dir.exists():
        print("Copying dist to backend...")
        shutil.copytree(dist_dir, backend_dist)
        print("Build completed successfully!")
    else:
        print("Error: Frontend build failed: dist directory not found")
        sys.exit(1)

if __name__ == "__main__":
    main()