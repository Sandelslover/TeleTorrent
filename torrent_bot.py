#!/usr/bin/env python3
"""
Telegram Torrent Bot
A bot that manages torrent downloads via Telegram commands
"""

import os
import sys
import json
import logging
import asyncio
import subprocess
import threading
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
import configparser

try:
    from telegram import Update
    from telegram.ext import Application, CommandHandler, ContextTypes
    import libtorrent as lt
except ImportError as e:
    print(f"Missing required dependency: {e}")
    print("Please run: pip install python-telegram-bot libtorrent")
    sys.exit(1)

class TorrentBot:
    def __init__(self, config_path: str = "config.ini"):
        self.config_path = config_path
        self.config = self.load_config()
        
        # Setup logging
        self.setup_logging()
        
        # Torrent session
        self.session = lt.session()
        self.session.listen_on(6881, 6891)
        
        # Active torrents tracking
        self.active_torrents: Dict[str, Dict] = {}
        self.download_history: List[Dict] = []
        
        # Load download history
        self.load_history()
        
        # Bot application
        self.app = None
        
    def load_config(self) -> configparser.ConfigParser:
        """Load configuration from file"""
        config = configparser.ConfigParser()
        if not os.path.exists(self.config_path):
            raise FileNotFoundError(f"Configuration file {self.config_path} not found. Run install.py first.")
        config.read(self.config_path)
        return config
    
    def setup_logging(self):
        """Setup logging configuration"""
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('logs/torrent_bot.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def load_history(self):
        """Load download history from file"""
        history_file = Path("download_history.json")
        if history_file.exists():
            try:
                with open(history_file, 'r') as f:
                    self.download_history = json.load(f)
            except Exception as e:
                self.logger.error(f"Error loading history: {e}")
                self.download_history = []
    
    def save_history(self):
        """Save download history to file"""
        try:
            with open("download_history.json", 'w') as f:
                json.dump(self.download_history[-50:], f, indent=2)  # Keep last 50 entries
        except Exception as e:
            self.logger.error(f"Error saving history: {e}")
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        welcome_msg = (
            "🤖 *Torrent Download Bot*\n\n"
            "Available commands:\n"
            "• `/download <torrent_link>` - Download a torrent\n"
            "• `/status` - Show current downloads\n"
            "• `/logs` - Show recent logs\n"
            "• `/history` - Show download history\n"
            "• `/help` - Show this help message"
        )
        await update.message.reply_text(welcome_msg, parse_mode='Markdown')
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command"""
        await self.start_command(update, context)
    
    async def download_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /download command"""
        if not context.args:
            await update.message.reply_text("❌ Please provide a torrent link or magnet URL")
            return
        
        torrent_url = ' '.join(context.args)
        user = update.effective_user
        
        try:
            # Add torrent to session
            if torrent_url.startswith('magnet:'):
                params = lt.parse_magnet_uri(torrent_url)
                params.save_path = self.config['paths']['download_dir']
                handle = self.session.add_torrent(params)
            else:
                # Assume it's a .torrent file URL
                import urllib.request
                torrent_data = urllib.request.urlopen(torrent_url).read()
                info = lt.torrent_info(torrent_data)
                handle = self.session.add_torrent({
                    'ti': info,
                    'save_path': self.config['paths']['download_dir']
                })
            
            # Track the torrent
            torrent_hash = str(handle.info_hash())
            self.active_torrents[torrent_hash] = {
                'handle': handle,
                'name': handle.name() if handle.has_metadata() else 'Unknown',
                'user': user.username or user.first_name,
                'started': datetime.now().isoformat(),
                'url': torrent_url
            }
            
            await update.message.reply_text(
                f"✅ Download started!\n"
                f"🎬 Torrent: {self.active_torrents[torrent_hash]['name']}\n"
                f"👤 Requested by: {user.username or user.first_name}"
            )
            
            self.logger.info(f"Download started by {user.username}: {torrent_url}")
            
        except Exception as e:
            error_msg = f"❌ Failed to start download: {str(e)}"
            await update.message.reply_text(error_msg)
            self.logger.error(f"Download error: {e}")
    
    async def status_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /status command"""
        if not self.active_torrents:
            await update.message.reply_text("📭 No active downloads")
            return
        
        status_msg = "📊 *Current Downloads:*\n\n"
        
        for torrent_hash, torrent_info in list(self.active_torrents.items()):
            handle = torrent_info['handle']
            status = handle.status()
            
            if status.is_seeding or status.is_finished:
                # Move to history and remove from active
                self.download_history.append({
                    'name': torrent_info['name'],
                    'user': torrent_info['user'],
                    'completed': datetime.now().isoformat(),
                    'status': 'completed'
                })
                del self.active_torrents[torrent_hash]
                self.save_history()
                continue
            
            progress = status.progress * 100
            state = self.get_torrent_state(status.state)
            download_rate = status.download_rate / 1024 / 1024  # MB/s
            
            status_msg += (
                f"🎬 *{torrent_info['name']}*\n"
                f"📊 Progress: {progress:.1f}%\n"
                f"⚡ Speed: {download_rate:.2f} MB/s\n"
                f"📥 State: {state}\n"
                f"👤 By: {torrent_info['user']}\n\n"
            )
        
        if len(status_msg) == len("📊 *Current Downloads:*\n\n"):
            status_msg = "📭 No active downloads"
        
        await update.message.reply_text(status_msg, parse_mode='Markdown')
    
    def get_torrent_state(self, state) -> str:
        """Convert torrent state to readable string"""
        states = {
            lt.torrent_status.queued_for_checking: "Queued",
            lt.torrent_status.checking_files: "Checking",
            lt.torrent_status.downloading_metadata: "Getting metadata",
            lt.torrent_status.downloading: "Downloading",
            lt.torrent_status.finished: "Finished",
            lt.torrent_status.seeding: "Seeding",
            lt.torrent_status.allocating: "Allocating",
            lt.torrent_status.checking_resume_data: "Checking resume"
        }
        return states.get(state, "Unknown")
    
    async def logs_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /logs command"""
        try:
            log_file = Path("logs/torrent_bot.log")
            if not log_file.exists():
                await update.message.reply_text("📝 No log file found")
                return
            
            # Get last 20 lines
            with open(log_file, 'r') as f:
                lines = f.readlines()
                last_lines = lines[-20:] if len(lines) >= 20 else lines
            
            log_text = ''.join(last_lines)
            if len(log_text) > 4000:  # Telegram message limit
                log_text = log_text[-4000:]
            
            await update.message.reply_text(f"```\n{log_text}\n```", parse_mode='Markdown')
            
        except Exception as e:
            await update.message.reply_text(f"❌ Error reading logs: {str(e)}")
    
    async def history_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /history command"""
        if not self.download_history:
            await update.message.reply_text("📚 No download history")
            return
        
        history_msg = "📚 *Recent Downloads:*\n\n"
        
        # Show last 10 downloads
        recent_downloads = self.download_history[-10:]
        
        for i, download in enumerate(reversed(recent_downloads), 1):
            completed_date = datetime.fromisoformat(download['completed']).strftime("%m/%d %H:%M")
            history_msg += (
                f"{i}. 🎬 {download['name']}\n"
                f"   👤 {download['user']} • ✅ {completed_date}\n\n"
            )
        
        await update.message.reply_text(history_msg, parse_mode='Markdown')
    
    async def send_startup_message(self):
        """Send startup message to the group"""
        try:
            group_id = self.config['telegram']['group_id']
            startup_msg = (
                "🚀 *Media Server is UP!*\n\n"
                "Bot is ready to accept commands:\n"
                "• `/download <link>` - Start download\n"
                "• `/status` - Check downloads\n"
                "• `/logs` - View logs\n"
                "• `/history` - Download history"
            )
            
            await self.app.bot.send_message(
                chat_id=group_id,
                text=startup_msg,
                parse_mode='Markdown'
            )
            self.logger.info("Startup message sent to group")
            
        except Exception as e:
            self.logger.error(f"Failed to send startup message: {e}")
    
    def run_torrent_monitor(self):
        """Background thread to monitor torrent progress"""
        while True:
            try:
                # Check for completed torrents
                for torrent_hash, torrent_info in list(self.active_torrents.items()):
                    handle = torrent_info['handle']
                    status = handle.status()
                    
                    if status.is_seeding or status.is_finished:
                        # Torrent completed
                        self.download_history.append({
                            'name': torrent_info['name'],
                            'user': torrent_info['user'],
                            'completed': datetime.now().isoformat(),
                            'status': 'completed'
                        })
                        
                        # Send completion message
                        asyncio.create_task(self.send_completion_message(torrent_info))
                        
                        # Remove from active torrents
                        del self.active_torrents[torrent_hash]
                        self.save_history()
                        
                        self.logger.info(f"Download completed: {torrent_info['name']}")
                
                # Sleep for 30 seconds before next check
                threading.Event().wait(30)
                
            except Exception as e:
                self.logger.error(f"Error in torrent monitor: {e}")
                threading.Event().wait(60)
    
    async def send_completion_message(self, torrent_info):
        """Send completion message to group"""
        try:
            group_id = self.config['telegram']['group_id']
            completion_msg = (
                f"✅ *Download Completed!*\n\n"
                f"🎬 {torrent_info['name']}\n"
                f"👤 Requested by: {torrent_info['user']}\n"
                f"📁 Saved to: {self.config['paths']['download_dir']}"
            )
            
            await self.app.bot.send_message(
                chat_id=group_id,
                text=completion_msg,
                parse_mode='Markdown'
            )
            
        except Exception as e:
            self.logger.error(f"Failed to send completion message: {e}")
    
    async def run(self):
        """Run the bot"""
        try:
            # Create application
            self.app = Application.builder().token(self.config['telegram']['bot_token']).build()
            
            # Add command handlers
            self.app.add_handler(CommandHandler("start", self.start_command))
            self.app.add_handler(CommandHandler("help", self.help_command))
            self.app.add_handler(CommandHandler("download", self.download_command))
            self.app.add_handler(CommandHandler("status", self.status_command))
            self.app.add_handler(CommandHandler("logs", self.logs_command))
            self.app.add_handler(CommandHandler("history", self.history_command))
            
            # Start torrent monitoring thread
            monitor_thread = threading.Thread(target=self.run_torrent_monitor, daemon=True)
            monitor_thread.start()
            
            # Initialize and start bot
            await self.app.initialize()
            await self.app.start()
            
            # Send startup message
            await self.send_startup_message()
            
            self.logger.info("Torrent bot started successfully")
            
            # Start polling
            await self.app.updater.start_polling()
            
            # Keep the bot running
            await asyncio.Event().wait()
            
        except Exception as e:
            self.logger.error(f"Error running bot: {e}")
            raise
        finally:
            if self.app:
                await self.app.stop()

def main():
    """Main entry point"""
    try:
        bot = TorrentBot()
        asyncio.run(bot.run())
    except KeyboardInterrupt:
        print("\nBot stopped by user")
    except Exception as e:
        print(f"Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
