#!/usr/bin/env python3
"""
Torrent Bot Installer
Sets up the environment and configuration for the Telegram Torrent Bot
"""

import os
import sys
import subprocess
import configparser
from pathlib import Path

def print_banner():
    """Print installation banner"""
    banner = """
╔══════════════════════════════════════════════════════════╗
║              TELEGRAM TORRENT BOT INSTALLER              ║
║                                                          ║
║  This script will install and configure the torrent     ║
║  download bot for Telegram.                             ║
╚══════════════════════════════════════════════════════════╝
    """
    print(banner)

def check_python_version():
    """Check if Python version is adequate"""
    if sys.version_info < (3, 8):
        print("❌ Error: Python 3.8 or higher is required")
        print(f"Current version: {sys.version}")
        sys.exit(1)
    print(f"✅ Python version: {sys.version.split()[0]}")

def install_system_packages():
    """Install required system packages"""
    print("\n📦 Installing system packages...")
    
    try:
        # Update package list
        subprocess.run(["sudo", "apt", "update"], check=True, capture_output=True)
        
        # Install required packages
        packages = [
            "python3-pip",
            "python3-venv",
            "libtorrent-rasterbar-dev",
            "pkg-config"
        ]
        
        for package in packages:
            print(f"Installing {package}...")
            result = subprocess.run(
                ["sudo", "apt", "install", "-y", package], 
                capture_output=True, text=True
            )
            if result.returncode != 0:
                print(f"⚠️  Warning: Failed to install {package}")
            else:
                print(f"✅ {package} installed")
                
    except subprocess.CalledProcessError as e:
        print(f"❌ Error installing system packages: {e}")
        print("Please install manually: sudo apt update && sudo apt install python3-pip python3-venv libtorrent-rasterbar-dev pkg-config")

def create_virtual_environment():
    """Create and activate virtual environment"""
    print("\n🐍 Setting up Python virtual environment...")
    
    venv_path = Path("venv")
    
    if venv_path.exists():
        print("✅ Virtual environment already exists")
        return
    
    try:
        subprocess.run([sys.executable, "-m", "venv", "venv"], check=True)
        print("✅ Virtual environment created")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error creating virtual environment: {e}")
        sys.exit(1)

def install_python_packages():
    """Install required Python packages"""
    print("\n📚 Installing Python packages...")
    
    # Determine pip path
    pip_path = "venv/bin/pip" if os.name != 'nt' else "venv\\Scripts\\pip.exe"
    
    packages = [
        "python-telegram-bot[all]",
        "libtorrent",
        "asyncio",
        "configparser"
    ]
    
    for package in packages:
        print(f"Installing {package}...")
        try:
            result = subprocess.run(
                [pip_path, "install", package], 
                capture_output=True, text=True, check=True
            )
            print(f"✅ {package} installed")
        except subprocess.CalledProcessError as e:
            print(f"❌ Error installing {package}: {e.stderr}")
            if package == "libtorrent":
                print("Trying alternative installation method...")
                try:
                    subprocess.run([pip_path, "install", "python-libtorrent"], check=True)
                    print("✅ python-libtorrent installed")
                except:
                    print("⚠️  Warning: Could not install libtorrent. You may need to install it manually.")

def get_user_input():
    """Get configuration from user"""
    print("\n⚙️  Configuration Setup")
    print("=" * 50)
    
    config = {}
    
    # Bot token
    while True:
        bot_token = input("🤖 Enter your Telegram Bot Token: ").strip()
        if bot_token:
            config['bot_token'] = bot_token
            break
        print("❌ Bot token cannot be empty!")
    
    # Group ID
    while True:
        group_id = input("👥 Enter your Telegram Group ID (with -): ").strip()
        if group_id:
            try:
                int(group_id)
                config['group_id'] = group_id
                break
            except ValueError:
                print("❌ Group ID must be a number (e.g., -1001234567890)")
        else:
            print("❌ Group ID cannot be empty!")
    
    # Download directory
    while True:
        download_dir = input("📁 Enter download directory path [./downloads]: ").strip()
        if not download_dir:
            download_dir = "./downloads"
        
        download_path = Path(download_dir).resolve()
        
        try:
            download_path.mkdir(parents=True, exist_ok=True)
            config['download_dir'] = str(download_path)
            print(f"✅ Download directory: {download_path}")
            break
        except Exception as e:
            print(f"❌ Error creating directory: {e}")
    
    return config

def create_config_file(config_data):
    """Create configuration file"""
    print("\n📝 Creating configuration file...")
    
    config = configparser.ConfigParser()
    
    config['telegram'] = {
        'bot_token': config_data['bot_token'],
        'group_id': config_data['group_id']
    }
    
    config['paths'] = {
        'download_dir': config_data['download_dir']
    }
    
    config['settings'] = {
        'max_concurrent_downloads': '3',
        'max_download_speed': '0',  # 0 = unlimited
        'max_upload_speed': '0'     # 0 = unlimited
    }
    
    try:
        with open('config.ini', 'w') as configfile:
            config.write(configfile)
        print("✅ Configuration file created: config.ini")
    except Exception as e:
        print(f"❌ Error creating config file: {e}")
        sys.exit(1)

def create_directories():
    """Create necessary directories"""
    print("\n📁 Creating directories...")
    
    directories = ['logs', 'temp']
    
    for directory in directories:
        try:
            Path(directory).mkdir(exist_ok=True)
            print(f"✅ Created directory: {directory}")
        except Exception as e:
            print(f"❌ Error creating {directory}: {e}")

def create_systemd_service():
    """Create systemd service file"""
    print("\n🔧 Creating systemd service...")
    
    current_dir = Path.cwd()
    python_path = current_dir / "venv" / "bin" / "python"
    script_path = current_dir / "torrent_bot.py"
    
    service_content = f"""[Unit]
Description=Telegram Torrent Bot
After=network.target

[Service]
Type=simple
User={os.getenv('USER')}
WorkingDirectory={current_dir}
ExecStart={python_path} {script_path}
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
"""
    
    service_file = Path("torrent-bot.service")
    
    try:
        with open(service_file, 'w') as f:
            f.write(service_content)
        
        print("✅ Service file created: torrent-bot.service")
        print("\nTo install the service, run:")
        print(f"sudo cp {service_file} /etc/systemd/system/")
        print("sudo systemctl daemon-reload")
        print("sudo systemctl enable torrent-bot")
        print("sudo systemctl start torrent-bot")
        
    except Exception as e:
        print(f"❌ Error creating service file: {e}")

def create_startup_script():
    """Create startup script"""
    print("\n🚀 Creating startup script...")
    
    startup_content = """#!/bin/bash
# Torrent Bot Startup Script

cd "$(dirname "$0")"

# Activate virtual environment
source venv/bin/activate

# Run the bot
python torrent_bot.py
"""
    
    try:
        with open("start_bot.sh", 'w') as f:
            f.write(startup_content)
        
        # Make executable
        os.chmod("start_bot.sh", 0o755)
        print("✅ Startup script created: start_bot.sh")
        
    except Exception as e:
        print(f"❌ Error creating startup script: {e}")

def print_final_instructions():
    """Print final setup instructions"""
    instructions = """
╔══════════════════════════════════════════════════════════╗
║                    INSTALLATION COMPLETE                 ║
╚══════════════════════════════════════════════════════════╝

🎉 The Telegram Torrent Bot has been installed successfully!

📋 Next Steps:

1. Test the bot:
   ./start_bot.sh

2. For production use, install as a system service:
   sudo cp torrent-bot.service /etc/systemd/system/
   sudo systemctl daemon-reload
   sudo systemctl enable torrent-bot
   sudo systemctl start torrent-bot

3. Check service status:
   sudo systemctl status torrent-bot

4. View logs:
   sudo journalctl -u torrent-bot -f

📁 Files created:
   • config.ini - Bot configuration
   • torrent_bot.py - Main bot script
   • start_bot.sh - Startup script
   • torrent-bot.service - Systemd service file

🤖 Bot Commands:
   • /download <torrent_link> - Download a torrent
   • /status - Show current downloads
   • /logs - Show recent logs
   • /history - Show download history

⚠️  Important Notes:
   • Make sure your bot is added to the Telegram group
   • The bot needs to be an admin to send messages
   • Downloads will be saved to the configured directory

🆘 Support:
   Check the README.md file for troubleshooting and advanced configuration.
"""
    print(instructions)

def main():
    """Main installation function"""
    try:
        print_banner()
        
        # Check requirements
        check_python_version()
        
        # Install system packages
        install_system_packages()
        
        # Setup Python environment
        create_virtual_environment()
        install_python_packages()
        
        # Get user configuration
        config_data = get_user_input()
        
        # Create configuration and files
        create_config_file(config_data)
        create_directories()
        create_systemd_service()
        create_startup_script()
        
        # Show final instructions
        print_final_instructions()
        
    except KeyboardInterrupt:
        print("\n❌ Installation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Installation failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
