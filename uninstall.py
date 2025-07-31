#!/usr/bin/env python3
"""
Telegram Torrent Bot Uninstaller
Removes the bot installation and cleans up system files
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path

def print_banner():
    """Print uninstallation banner"""
    banner = """
╔══════════════════════════════════════════════════════════╗
║            TELEGRAM TORRENT BOT UNINSTALLER             ║
║                                                          ║
║  This script will remove the torrent bot and all        ║
║  associated files from your system.                     ║
║                                                          ║
║  ⚠️  WARNING: This action cannot be undone!             ║
╚══════════════════════════════════════════════════════════╝
    """
    print(banner)

def confirm_uninstall():
    """Ask user to confirm uninstallation"""
    print("📋 What will be removed:")
    print("   • Bot service (if installed)")
    print("   • Python virtual environment")
    print("   • Configuration files")
    print("   • Log files")
    print("   • Startup scripts")
    print("   • Service files")
    print("\n📁 What will be KEPT:")
    print("   • Downloaded torrents")
    print("   • Download history backup (if you choose)")
    
    while True:
        response = input("\n❓ Do you want to continue with uninstallation? (y/N): ").strip().lower()
        if response in ['n', 'no', '']:
            print("❌ Uninstallation cancelled")
            sys.exit(0)
        elif response in ['y', 'yes']:
            break
        else:
            print("Please enter 'y' for yes or 'n' for no")

def backup_history():
    """Ask if user wants to backup download history"""
    history_file = Path("download_history.json")
    
    if not history_file.exists():
        return
    
    while True:
        response = input("💾 Do you want to backup download history? (Y/n): ").strip().lower()
        if response in ['y', 'yes', '']:
            try:
                backup_name = f"download_history_backup_{int(os.path.getmtime(history_file))}.json"
                shutil.copy2(history_file, backup_name)
                print(f"✅ History backed up as: {backup_name}")
                break
            except Exception as e:
                print(f"❌ Failed to backup history: {e}")
                break
        elif response in ['n', 'no']:
            print("📝 Download history will be deleted")
            break
        else:
            print("Please enter 'y' for yes or 'n' for no")

def stop_and_remove_service():
    """Stop and remove systemd service"""
    print("\n🛑 Stopping and removing service...")
    
    service_name = "torrent-bot"
    service_path = f"/etc/systemd/system/{service_name}.service"
    
    try:
        # Stop the service
        result = subprocess.run(
            ["sudo", "systemctl", "stop", service_name],
            capture_output=True, text=True
        )
        if result.returncode == 0:
            print("✅ Service stopped")
        else:
            print("ℹ️  Service was not running")
        
        # Disable the service
        result = subprocess.run(
            ["sudo", "systemctl", "disable", service_name],
            capture_output=True, text=True
        )
        if result.returncode == 0:
            print("✅ Service disabled")
        else:
            print("ℹ️  Service was not enabled")
        
        # Remove service file
        if os.path.exists(service_path):
            subprocess.run(["sudo", "rm", service_path], check=True)
            print("✅ Service file removed")
        
        # Reload systemd
        subprocess.run(["sudo", "systemctl", "daemon-reload"], check=True)
        print("✅ Systemd reloaded")
        
    except subprocess.CalledProcessError as e:
        print(f"⚠️  Warning: Error managing service: {e}")
    except Exception as e:
        print(f"⚠️  Warning: Unexpected error with service: {e}")

def remove_files():
    """Remove bot files and directories"""
    print("\n🗑️  Removing files...")
    
    files_to_remove = [
        "torrent_bot.py",
        "install.py",
        "uninstall.py",
        "config.ini",
        "start_bot.sh",
        "manage_service.sh",
        "torrent-bot.service",
        "requirements.txt",
        "download_history.json",
        "README.md"
    ]
    
    directories_to_remove = [
        "venv",
        "logs",
        "temp",
        "__pycache__"
    ]
    
    # Remove files
    for file_path in files_to_remove:
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                print(f"✅ Removed: {file_path}")
        except Exception as e:
            print(f"⚠️  Warning: Could not remove {file_path}: {e}")
    
    # Remove directories
    for dir_path in directories_to_remove:
        try:
            if os.path.exists(dir_path):
                shutil.rmtree(dir_path)
                print(f"✅ Removed directory: {dir_path}")
        except Exception as e:
            print(f"⚠️  Warning: Could not remove directory {dir_path}: {e}")

def cleanup_system_packages():
    """Ask if user wants to remove system packages"""
    print("\n📦 System Package Cleanup")
    
    packages = [
        "libtorrent-rasterbar-dev",
        "pkg-config"
    ]
    
    while True:
        response = input("❓ Remove installed system packages? (y/N): ").strip().lower()
        if response in ['n', 'no', '']:
            print("📝 System packages will be kept")
            break
        elif response in ['y', 'yes']:
            print("🗑️  Removing system packages...")
            for package in packages:
                try:
                    result = subprocess.run(
                        ["sudo", "apt", "remove", "-y", package],
                        capture_output=True, text=True
                    )
                    if result.returncode == 0:
                        print(f"✅ Removed: {package}")
                    else:
                        print(f"ℹ️  {package} was not installed or couldn't be removed")
                except Exception as e:
                    print(f"⚠️  Warning: Error removing {package}: {e}")
            
            # Clean up unused packages
            try:
                subprocess.run(["sudo", "apt", "autoremove", "-y"], capture_output=True)
                print("✅ Cleaned up unused packages")
            except Exception as e:
                print(f"⚠️  Warning: Could not clean up packages: {e}")
            break
        else:
            print("Please enter 'y' for yes or 'n' for no")

def check_remaining_files():
    """Check for any remaining files"""
    print("\n🔍 Checking for remaining files...")
    
    current_dir = Path.cwd()
    remaining_files = []
    
    # Check for bot-related files
    for item in current_dir.iterdir():
        if item.name.startswith(('torrent', 'bot', 'download_history')):
            remaining_files.append(item.name)
    
    if remaining_files:
        print("📁 Remaining files found:")
        for file in remaining_files:
            print(f"   • {file}")
        
        while True:
            response = input("\n❓ Remove these files too? (y/N): ").strip().lower()
            if response in ['n', 'no', '']:
                print("📝 Remaining files kept")
                break
            elif response in ['y', 'yes']:
                for file in remaining_files:
                    try:
                        file_path = current_dir / file
                        if file_path.is_file():
                            file_path.unlink()
                        elif file_path.is_dir():
                            shutil.rmtree(file_path)
                        print(f"✅ Removed: {file}")
                    except Exception as e:
                        print(f"⚠️  Warning: Could not remove {file}: {e}")
                break
            else:
                print("Please enter 'y' for yes or 'n' for no")
    else:
        print("✅ No additional files found")

def print_final_message():
    """Print final uninstallation message"""
    message = """
╔══════════════════════════════════════════════════════════╗
║                 UNINSTALLATION COMPLETE                  ║
╚══════════════════════════════════════════════════════════╝

✅ The Telegram Torrent Bot has been successfully removed!

📋 What was removed:
   • Bot application files
   • Python virtual environment
   • Configuration files
   • System service
   • Log files
   • Startup scripts

📁 What remains:
   • Downloaded torrent files (in your download directory)
   • Any backup files you chose to keep
   • System packages (if you chose to keep them)

🔄 To reinstall:
   Simply run the installer script again:
   python3 install.py

🙏 Thank you for using Telegram Torrent Bot!

   If you encountered any issues during uninstallation,
   please report them on the project's GitHub page.
"""
    print(message)

def main():
    """Main uninstallation function"""
    try:
        print_banner()
        
        # Confirm uninstallation
        confirm_uninstall()
        
        # Backup history if requested
        backup_history()
        
        print("\n🚀 Starting uninstallation...")
        
        # Stop and remove service
        stop_and_remove_service()
        
        # Remove files and directories
        remove_files()
        
        # Optional system package cleanup
        cleanup_system_packages()
        
        # Check for remaining files
        check_remaining_files()
        
        # Show final message
        print_final_message()
        
    except KeyboardInterrupt:
        print("\n❌ Uninstallation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Uninstallation failed: {e}")
        print("You may need to manually remove some files.")
        sys.exit(1)

if __name__ == "__main__":
    main()
