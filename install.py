import os
import subprocess
import sys

def install_requirements():
    try:
        print("Installing Python dependencies from requirements.txt...")
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'])
    except subprocess.CalledProcessError as e:
        print(f"Error installing requirements: {e}")
        sys.exit(1)

def install_playwright():
    try:
        print("Installing Playwright...")
        if os.name == 'nt':
            subprocess.check_call(['npx.cmd', 'playwright', 'install'])
        else:
            subprocess.check_call(['npx', 'playwright', 'install'])
    except subprocess.CalledProcessError as e:
        print(f"Error installing Playwright: {e}")
        sys.exit(1)

if __name__ == '__main__':
    install_requirements()
    install_playwright()
    print("Installation complete.")
