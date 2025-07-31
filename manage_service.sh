#!/bin/bash
# Torrent Bot Service Management Script

SERVICE_NAME="torrent-bot"
SERVICE_FILE="torrent-bot.service"

function show_usage() {
    echo "Usage: $0 {install|start|stop|restart|status|logs|uninstall}"
    echo ""
    echo "Commands:"
    echo "  install   - Install the service"
    echo "  start     - Start the service"
    echo "  stop      - Stop the service"
    echo "  restart   - Restart the service"
    echo "  status    - Show service status"
    echo "  logs      - Show service logs"
    echo "  uninstall - Remove the service"
}

function install_service() {
    echo "Installing $SERVICE_NAME service..."
    
    if [[ ! -f "$SERVICE_FILE" ]]; then
        echo "Error: $SERVICE_FILE not found. Run install.py first."
        exit 1
    fi
    
    sudo cp "$SERVICE_FILE" "/etc/systemd/system/"
    sudo systemctl daemon-reload
    sudo systemctl enable "$SERVICE_NAME"
    
    echo "✅ Service installed successfully"
    echo "Run '$0 start' to start the service"
}

function start_service() {
    echo "Starting $SERVICE_NAME service..."
    sudo systemctl start "$SERVICE_NAME"
    echo "✅ Service started"
    show_status
}

function stop_service() {
    echo "Stopping $SERVICE_NAME service..."
    sudo systemctl stop "$SERVICE_NAME"
    echo "✅ Service stopped"
}

function restart_service() {
    echo "Restarting $SERVICE_NAME service..."
    sudo systemctl restart "$SERVICE_NAME"
    echo "✅ Service restarted"
    show_status
}

function show_status() {
    echo "Service status:"
    sudo systemctl status "$SERVICE_NAME" --no-pager
}

function show_logs() {
    echo "Following service logs (Press Ctrl+C to exit):"
    sudo journalctl -u "$SERVICE_NAME" -f
}

function uninstall_service() {
    echo "Uninstalling $SERVICE_NAME service..."
    
    sudo systemctl stop "$SERVICE_NAME" 2>/dev/null
    sudo systemctl disable "$SERVICE_NAME" 2>/dev/null
    sudo rm -f "/etc/systemd/system/$SERVICE_FILE"
    sudo systemctl daemon-reload
    
    echo "✅ Service uninstalled"
}

# Main script logic
case "$1" in
    install)
        install_service
        ;;
    start)
        start_service
        ;;
    stop)
        stop_service
        ;;
    restart)
        restart_service
        ;;
    status)
        show_status
        ;;
    logs)
        show_logs
        ;;
    uninstall)
        uninstall_service
        ;;
    *)
        show_usage
        exit 1
        ;;
esac

exit 0
