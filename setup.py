#!/usr/bin/env python3
"""
Setup script for GramSetu development environment
Automates installation and configuration
"""
import os
import sys
import subprocess
import platform
from pathlib import Path

def print_header(text):
    """Print formatted header"""
    print("\n" + "="*60)
    print(f"  {text}")
    print("="*60 + "\n")

def run_command(cmd, description):
    """Run shell command with error handling"""
    print(f"⏳ {description}...")
    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} - Success")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} - Failed")
        print(f"Error: {e.stderr}")
        return False

def check_prerequisites():
    """Check if required tools are installed"""
    print_header("Checking Prerequisites")
    
    checks = {
        "Python 3.11+": ["python", "--version"],
        "Docker": ["docker", "--version"],
        "Node.js": ["node", "--version"],
        "Git": ["git", "--version"]
    }
    
    all_ok = True
    for name, cmd in checks.items():
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            version = result.stdout.strip()
            print(f"✅ {name}: {version}")
        except (subprocess.CalledProcessError, FileNotFoundError):
            print(f"❌ {name}: Not found")
            all_ok = False
    
    return all_ok

def setup_python_environment():
    """Set up Python virtual environment and install dependencies"""
    print_header("Setting Up Python Environment")
    
    # Create virtual environment
    if not os.path.exists("venv"):
        run_command(f"{sys.executable} -m venv venv", "Creating virtual environment")
    
    # Determine activation script based on OS
    if platform.system() == "Windows":
        pip_cmd = "venv\\Scripts\\pip"
        python_cmd = "venv\\Scripts\\python"
    else:
        pip_cmd = "venv/bin/pip"
        python_cmd = "venv/bin/python"
    
    # Upgrade pip
    run_command(f"{pip_cmd} install --upgrade pip", "Upgrading pip")
    
    # Install requirements
    run_command(f"{pip_cmd} install -r requirements.txt", "Installing Python dependencies")
    
    # Install Playwright browsers
    run_command(f"{python_cmd} -m playwright install chromium", "Installing Playwright browsers")
    
    return True

def setup_environment_file():
    """Create .env file from template"""
    print_header("Setting Up Environment File")
    
    if os.path.exists(".env"):
        print("⚠️  .env file already exists, skipping...")
        return True
    
    if os.path.exists(".env.example"):
        import shutil
        shutil.copy(".env.example", ".env")
        print("✅ Created .env from template")
        print("\n⚠️  IMPORTANT: Edit .env and add your API keys!")
        print("   - AWS_ACCESS_KEY_ID")
        print("   - AWS_SECRET_ACCESS_KEY")
        print("   - BHASHINI_API_KEY")
        print("   - TWILIO_ACCOUNT_SID")
        print("   - TWILIO_AUTH_TOKEN")
        return True
    else:
        print("❌ .env.example not found")
        return False

def setup_docker_infrastructure():
    """Start Docker containers for PostgreSQL and Redis"""
    print_header("Starting Docker Infrastructure")
    
    # Check if Docker is running
    try:
        subprocess.run(["docker", "ps"], capture_output=True, check=True)
    except subprocess.CalledProcessError:
        print("❌ Docker is not running. Please start Docker Desktop.")
        return False
    
    # Start infrastructure services
    run_command("docker-compose up -d postgres redis", "Starting PostgreSQL and Redis")
    
    # Wait for services to be healthy
    print("⏳ Waiting for services to be healthy (30 seconds)...")
    import time
    time.sleep(30)
    
    run_command("docker-compose ps", "Checking service status")
    
    return True

def setup_mobile_app():
    """Install mobile app dependencies"""
    print_header("Setting Up Mobile App")
    
    if not os.path.exists("mobile-app"):
        print("⚠️  mobile-app directory not found, skipping...")
        return True
    
    os.chdir("mobile-app")
    run_command("npm install", "Installing Node.js dependencies")
    os.chdir("..")
    
    return True

def create_directories():
    """Create necessary directories"""
    print_header("Creating Directories")
    
    directories = [
        "logs",
        "storage",
        "browser-data",
        "infrastructure/mock-portals"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"✅ Created {directory}")
    
    return True

def verify_setup():
    """Verify the setup by testing service health"""
    print_header("Verifying Setup")
    
    print("To verify the setup, run the following commands in separate terminals:")
    print("\n1. Voice Service:")
    print("   python -m services.voice.main")
    print("\n2. Agent Service:")
    print("   python -m services.agent.main")
    print("\n3. Document Service:")
    print("   python -m services.document.main")
    print("\n4. Orchestrator:")
    print("   python -m services.orchestrator.main")
    print("\nThen test with:")
    print("   curl http://localhost:8000/health")
    
    return True

def main():
    """Main setup function"""
    print_header("GramSetu Setup Script")
    print("This script will set up your development environment")
    
    # Change to project root
    script_dir = Path(__file__).parent
    os.chdir(script_dir)
    
    steps = [
        ("Prerequisites Check", check_prerequisites),
        ("Environment File", setup_environment_file),
        ("Python Environment", setup_python_environment),
        ("Docker Infrastructure", setup_docker_infrastructure),
        ("Mobile App", setup_mobile_app),
        ("Directories", create_directories),
        ("Verification Info", verify_setup)
    ]
    
    for step_name, step_func in steps:
        if not step_func():
            print(f"\n❌ Setup failed at: {step_name}")
            print("Please fix the errors and run the script again.")
            sys.exit(1)
    
    print_header("Setup Complete! 🎉")
    print("Next steps:")
    print("1. Edit .env and add your API keys")
    print("2. Start the services (see verification info above)")
    print("3. Read QUICKSTART.md for detailed instructions")
    print("\nHappy hacking! 🚀")

if __name__ == "__main__":
    main()
