# 🤖 Telegram Torrent Bot

A powerful Telegram bot that manages torrent downloads on Ubuntu servers. Users can send torrent links to a Telegram group and the bot will handle the downloads automatically.

## ✨ Features

- **Multi-user Support**: Multiple users can send commands simultaneously
- **Real-time Status**: Check download progress and speeds
- **Download History**: Track completed downloads
- **Log Monitoring**: View bot logs directly from Telegram
- **Auto Notifications**: Get notified when downloads complete
- **Systemd Integration**: Run as a system service with auto-restart

## 🛠️ Requirements

- Ubuntu 18.04+ (or other Debian-based Linux)
- Python 3.8+
- Telegram Bot Token
- Telegram Group ID

## 🚀 Quick Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/Sandelslover/TeleTorrent.git
   cd telegram-torrent-bot
   ```

2. **Run the installer**:
   ```bash
   python3 install.py
   ```

3. **Follow the prompts** to enter:
   - Bot token (from @BotFather)
   - Group ID (your Telegram group)
   - Download directory path

4. **Start the bot**:
   ```bash
   ./start_bot.sh
   ```

## 🗑️ Uninstallation

To completely remove the bot from your system:

```bash
python3 uninstall.py
```

The uninstaller will:
- Stop and remove the systemd service
- Remove all bot files and directories
- Optionally backup your download history
- Optionally remove installed system packages
- Keep your downloaded files safe

**Note**: Your downloaded torrent files will never be deleted during uninstallation.

## 📱 Getting Your Bot Token and Group ID

### Bot Token
1. Message [@BotFather](https://t.me/BotFather) on Telegram
2. Create a new bot with `/newbot`
3. Follow the instructions and copy your bot token
4. Make sure to disable privacy mode with `/setprivacy` → `Disable`

### Group ID
1. Add your bot to your Telegram group
2. Make the bot an admin (required to send messages)
3. Send a message in the group, then visit:
   ```
   https://api.telegram.org/bot<YourBOTToken>/getUpdates
   ```
4. Look for the `chat.id` field (it will be negative, like `-1001234567890`)

## 🎮 Bot Commands

| Command | Description | Example |
|---------|-------------|---------|
| `/download <link>` | Download a torrent | `/download magnet:?xt=urn:btih:...` |
| `/status` | Show active downloads | `/status` |
| `/logs` | Show last 20 log lines | `/logs` |
| `/history` | Show last 10 completed downloads | `/history` |
| `/help` | Show help message | `/help` |

## 🔧 Configuration

The bot uses a `config.ini` file for configuration:

```ini
[telegram]
bot_token = YOUR_BOT_TOKEN
group_id = YOUR_GROUP_ID

[paths]
download_dir = /path/to/downloads

[settings]
max_concurrent_downloads = 3
max_download_speed = 0
max_upload_speed = 0
```

### Configuration Options

- `max_concurrent_downloads`: Maximum simultaneous downloads (default: 3)
- `max_download_speed`: Max download speed in KB/s (0 = unlimited)
- `max_upload_speed`: Max upload speed in KB/s (0 = unlimited)

## 🔄 Running as a Service

### Install the service:
```bash
sudo cp torrent-bot.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable torrent-bot
sudo systemctl start torrent-bot
```

### Service management:
```bash
# Using the management script
./manage_service.sh status    # Check status
./manage_service.sh logs      # View logs  
./manage_service.sh restart   # Restart service
./manage_service.sh stop      # Stop service
./manage_service.sh start     # Start service

# Or using systemctl directly
sudo systemctl status torrent-bot
sudo journalctl -u torrent-bot -f
sudo systemctl restart torrent-bot
sudo systemctl stop torrent-bot
sudo systemctl disable torrent-bot
```

## 📁 File Structure

```
telegram-torrent-bot/
├── torrent_bot.py          # Main bot application
├── install.py              # Installation script
├── uninstall.py            # Uninstallation script
├── config.ini              # Configuration file (created during install)
├── start_bot.sh            # Startup script
├── manage_service.sh       # Service management script
├── torrent-bot.service     # Systemd service file
├── requirements.txt        # Python dependencies
├── logs/                   # Log files directory
│   └── torrent_bot.log
├── downloads/              # Default download directory
├── venv/                   # Python virtual environment
└── README.md              # This file
```

## 🐛 Troubleshooting

### Common Issues

#### Bot doesn't respond to commands
- **Check if bot is admin**: The bot must be an admin in the group
- **Verify group ID**: Make sure the group ID is correct (negative number)
- **Check privacy settings**: Disable privacy mode in @BotFather

#### Downloads don't start
- **Check permissions**: Ensure the download directory is writable
- **Verify torrent link**: Make sure the magnet link or .torrent URL is valid
- **Check logs**: Use `/logs` command or check `logs/torrent_bot.log`

#### Service won't start
```bash
# Check service logs
sudo journalctl -u torrent-bot -f

# Check if config file exists
ls -la config.ini

# Test manual start
./start_bot.sh
```

#### Python dependencies issues
```bash
# Reinstall dependencies
source venv/bin/activate
pip install --upgrade python-telegram-bot libtorrent
```

### Debug Mode

To run the bot in debug mode with verbose logging:

1. Edit `torrent_bot.py` and change logging level:
   ```python
   logging.basicConfig(level=logging.DEBUG, ...)
   ```

2. Run manually:
   ```bash
   source venv/bin/activate
   python torrent_bot.py
   ```

## 🎛️ Advanced Configuration

### Custom Download Settings

Edit `config.ini` to customize torrent behavior:

```ini
[settings]
max_concurrent_downloads = 5
max_download_speed = 10240  # 10 MB/s in KB/s
max_upload_speed = 1024     # 1 MB/s in KB/s
listen_port_min = 6881
listen_port_max = 6891
```

### Environment Variables

You can also use environment variables for sensitive data:

```bash
export BOT_TOKEN="your_bot_token_here"
export GROUP_ID="-1001234567890"
./start_bot.sh
```

### Custom Download Categories

Modify the bot to organize downloads by category:

```python
# In torrent_bot.py, modify the download path based on content
def get_download_path(self, torrent_name):
    if any(ext in torrent_name.lower() for ext in ['.mkv', '.mp4', '.avi']):
        return os.path.join(self.config['paths']['download_dir'], 'movies')
    elif any(ext in torrent_name.lower() for ext in ['.mp3', '.flac', '.wav']):
        return os.path.join(self.config['paths']['download_dir'], 'music')
    else:
        return self.config['paths']['download_dir']
```

## 📊 Monitoring and Analytics

### Log Analysis

View detailed statistics from logs:

```bash
# Count downloads today
grep "$(date +%Y-%m-%d)" logs/torrent_bot.log | grep "Download started" | wc -l

# Show most active users
grep "Download started by" logs/torrent_bot.log | awk '{print $6}' | sort | uniq -c | sort -nr

# Monitor real-time activity
tail -f logs/torrent_bot.log
```

### System Resource Monitoring

Monitor bot resource usage:

```bash
# Check CPU and memory usage
ps aux | grep torrent_bot.py

# Monitor disk space
df -h /path/to/downloads

# Network activity
netstat -i
```



### Complete Reinstallation

If you need to completely reinstall:

1. **Uninstall current version**:
   ```bash
   python3 uninstall.py
   ```

2. **Reinstall**:
   ```bash
   python3 install.py
   ```

### Database Backup

Backup download history regularly:

```bash
# Create backup script
cat > backup_history.sh << 'EOF'
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
cp download_history.json backups/history_$DATE.json
find backups/ -name "history_*.json" -mtime +30 -delete
EOF

chmod +x backup_history.sh

# Add to crontab for daily backups
echo "0 2 * * * /path/to/telegram-torrent-bot/backup_history.sh" | crontab -
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

### Development Setup

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

### Code Style

- Follow PEP 8 guidelines
- Use meaningful variable names
- Add comments for complex logic
- Include docstrings for functions

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

If you encounter any issues:

1. Check this README for troubleshooting steps
2. Look at the [Issues](https://github.com/Sandelslover/TeleTorrent/issues) page
3. Create a new issue with:
   - Your Ubuntu version
   - Python version
   - Error messages
   - Steps to reproduce

## 📝 Changelog

### v1.0.0
- Initial release
- Basic download functionality
- Status monitoring
- History tracking
- Systemd service integration
- Installation and uninstallation scripts
- Service management utilities

## 🔧 Available Scripts

| Script | Purpose | Usage |
|--------|---------|-------|
| `install.py` | Install the bot | `python3 install.py` |
| `uninstall.py` | Remove the bot | `python3 uninstall.py` |
| `start_bot.sh` | Start bot manually | `./start_bot.sh` |
| `manage_service.sh` | Manage systemd service | `./manage_service.sh {start\|stop\|status\|logs}` |

## 🙏 Acknowledgments

- [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot) - Telegram Bot API wrapper
- [libtorrent](https://www.libtorrent.org/) - BitTorrent library
- The open-source community for inspiration and support

---

**⚠️ Disclaimer**: This bot is for educational purposes. Please ensure you comply with your local laws and only download content you have the right to access. The authors are not responsible for any misuse of this software.
