#!/bin/bash

# =============================================================================
# HEAR! HEAR! BOT - SIMPLE DEPLOYMENT SCRIPT (NO DOCKER)
# =============================================================================
# Production deployment without Docker - uses systemd for process management

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
BOT_NAME="Hear! Hear! Bot"
VERSION="2.1.0"
SERVICE_NAME="hearhear-bot"
INSTALL_DIR="/opt/hearhear-bot"
USER="hearhear"
BACKUP_DIR="./backups"
PYTHON_VERSION="3.8"

# Functions
print_header() {
    echo -e "${BLUE}============================================${NC}"
    echo -e "${BLUE}  $BOT_NAME - Simple Deployment${NC}"
    echo -e "${BLUE}  Version: $VERSION${NC}"
    echo -e "${BLUE}============================================${NC}"
    echo
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

check_requirements() {
    print_info "Checking deployment requirements..."
    
    # Check Python version
    if command -v python3 &> /dev/null; then
        PYTHON_VER=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
        if [ "$(printf '%s\n' "$PYTHON_VERSION" "$PYTHON_VER" | sort -V | head -n1)" = "$PYTHON_VERSION" ]; then
            print_success "Python $PYTHON_VER is compatible"
        else
            print_error "Python $PYTHON_VERSION or higher is required. Found: $PYTHON_VER"
            exit 1
        fi
    else
        print_error "Python 3 is not installed"
        exit 1
    fi
    
    # Check if pip is available
    if ! command -v pip3 &> /dev/null; then
        print_error "pip3 is not installed. Please install python3-pip"
        exit 1
    fi
    
    # Check if systemd is available (for service management)
    if ! command -v systemctl &> /dev/null; then
        print_warning "systemctl not found. Service management will not be available."
    fi
    
    # Check if .env file exists
    if [ ! -f .env ]; then
        print_error ".env file not found. Please create one based on .env.example"
        exit 1
    fi
    
    print_success "All requirements satisfied"
}

setup_environment() {
    print_info "Setting up Python environment..."
    
    # Create virtual environment if it doesn't exist
    if [ ! -d ".venv" ]; then
        print_info "Creating virtual environment..."
        python3 -m venv .venv
        print_success "Virtual environment created"
    fi
    
    # Activate virtual environment
    source .venv/bin/activate
    
    # Upgrade pip
    print_info "Upgrading pip..."
    pip install --upgrade pip
    
    # Install dependencies
    print_info "Installing dependencies..."
    pip install -r requirements.txt
    
    print_success "Python environment ready"
}

create_systemd_service() {
    if command -v systemctl &> /dev/null && [ "$EUID" -eq 0 ]; then
        print_info "Creating systemd service..."
        
        # Get current directory
        CURRENT_DIR=$(pwd)
        
        # Create service file
        cat > /etc/systemd/system/${SERVICE_NAME}.service << EOF
[Unit]
Description=Hear! Hear! Discord Bot
After=network.target

[Service]
Type=simple
User=${USER}
WorkingDirectory=${CURRENT_DIR}
Environment=PATH=${CURRENT_DIR}/.venv/bin
ExecStart=${CURRENT_DIR}/.venv/bin/python main.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF
        
        # Reload systemd and enable service
        systemctl daemon-reload
        systemctl enable ${SERVICE_NAME}
        
        print_success "Systemd service created"
    else
        print_warning "Skipping systemd service creation (requires root or no systemctl available)"
    fi
}

create_startup_script() {
    print_info "Creating startup script..."
    
    cat > start_bot.sh << 'EOF'
#!/bin/bash

# Hear! Hear! Bot Startup Script
cd "$(dirname "$0")"

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}🚀 Starting Hear! Hear! Bot...${NC}"

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo -e "${RED}❌ Virtual environment not found. Please run ./deploy_simple.sh first${NC}"
    exit 1
fi

# Activate virtual environment
source .venv/bin/activate

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo -e "${RED}❌ .env file not found. Please create one based on .env.example${NC}"
    exit 1
fi

# Create logs directory
mkdir -p logs

# Start the bot
echo -e "${GREEN}🤖 Bot is starting...${NC}"
python main.py
EOF
    
    chmod +x start_bot.sh
    print_success "Startup script created"
}

create_stop_script() {
    print_info "Creating stop script..."
    
    cat > stop_bot.sh << 'EOF'
#!/bin/bash

# Hear! Hear! Bot Stop Script
SERVICE_NAME="hearhear-bot"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m'

echo -e "${GREEN}🛑 Stopping Hear! Hear! Bot...${NC}"

# Try to stop systemd service first
if command -v systemctl &> /dev/null && systemctl is-active --quiet $SERVICE_NAME; then
    echo "Stopping systemd service..."
    sudo systemctl stop $SERVICE_NAME
    echo -e "${GREEN}✅ Service stopped${NC}"
elif pgrep -f "python main.py" > /dev/null; then
    echo "Stopping bot process..."
    pkill -f "python main.py"
    echo -e "${GREEN}✅ Bot process stopped${NC}"
else
    echo -e "${RED}❌ Bot is not running${NC}"
fi
EOF
    
    chmod +x stop_bot.sh
    print_success "Stop script created"
}

create_status_script() {
    print_info "Creating status script..."
    
    cat > status_bot.sh << 'EOF'
#!/bin/bash

# Hear! Hear! Bot Status Script
SERVICE_NAME="hearhear-bot"

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}📊 Hear! Hear! Bot Status${NC}"
echo "=================================="

# Check systemd service status
if command -v systemctl &> /dev/null && systemctl list-unit-files | grep -q $SERVICE_NAME; then
    echo -e "${BLUE}Systemd Service:${NC}"
    systemctl status $SERVICE_NAME --no-pager -l
    echo
fi

# Check if process is running
if pgrep -f "python main.py" > /dev/null; then
    PID=$(pgrep -f "python main.py")
    echo -e "${GREEN}✅ Bot is running (PID: $PID)${NC}"
    
    # Show process info
    echo -e "${BLUE}Process Info:${NC}"
    ps -p $PID -o pid,ppid,user,%cpu,%mem,etime,cmd --no-headers
    echo
else
    echo -e "${RED}❌ Bot is not running${NC}"
fi

# Check web server
echo -e "${BLUE}Web Server Check:${NC}"
if curl -s -f http://localhost:8080/ > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Web server is responding${NC}"
else
    echo -e "${RED}❌ Web server is not responding${NC}"
fi

# Show recent logs
echo -e "${BLUE}Recent Logs (last 10 lines):${NC}"
if [ -f "logs/bot.log" ]; then
    tail -n 10 logs/bot.log
else
    echo "No log file found"
fi
EOF
    
    chmod +x status_bot.sh
    print_success "Status script created"
}

backup_data() {
    print_info "Creating backup..."
    
    # Create backup directory
    mkdir -p "$BACKUP_DIR"
    
    # Backup current logs
    if [ -d "logs" ]; then
        cp -r logs "$BACKUP_DIR/logs_$(date +%Y%m%d_%H%M%S)" 2>/dev/null || true
        print_success "Logs backed up"
    fi
    
    # Backup configuration
    if [ -f ".env" ]; then
        cp .env "$BACKUP_DIR/.env_$(date +%Y%m%d_%H%M%S)" 2>/dev/null || true
        print_success "Configuration backed up"
    fi
}

deploy() {
    print_info "Starting deployment..."
    
    # Pull latest code (if this is a git repository)
    if [ -d ".git" ]; then
        print_info "Pulling latest code..."
        git pull origin main || print_warning "Could not pull latest code"
    fi
    
    # Setup environment
    setup_environment
    
    # Create scripts
    create_startup_script
    create_stop_script
    create_status_script
    
    # Create systemd service (if running as root)
    create_systemd_service
    
    # Create logs directory
    mkdir -p logs
    
    print_success "Deployment completed"
}

start_bot() {
    print_info "Starting bot..."
    
    if command -v systemctl &> /dev/null && systemctl list-unit-files | grep -q ${SERVICE_NAME}; then
        print_info "Starting via systemd..."
        sudo systemctl start ${SERVICE_NAME}
        sleep 2
        if systemctl is-active --quiet ${SERVICE_NAME}; then
            print_success "Bot started successfully via systemd"
        else
            print_error "Failed to start bot via systemd"
            systemctl status ${SERVICE_NAME} --no-pager
        fi
    else
        print_info "Starting via script..."
        nohup ./start_bot.sh > logs/nohup.log 2>&1 &
        sleep 3
        if pgrep -f "python main.py" > /dev/null; then
            print_success "Bot started successfully"
        else
            print_error "Failed to start bot"
            cat logs/nohup.log
        fi
    fi
}

stop_bot() {
    print_info "Stopping bot..."
    ./stop_bot.sh
}

show_status() {
    ./status_bot.sh
}

show_logs() {
    print_info "Showing live logs..."
    if [ -f "logs/bot.log" ]; then
        tail -f logs/bot.log
    else
        echo "No log file found. Starting from nohup log:"
        tail -f logs/nohup.log 2>/dev/null || echo "No logs available"
    fi
}

# Main deployment process
main() {
    print_header
    
    # Parse command line arguments
    case "${1:-deploy}" in
        "deploy")
            check_requirements
            backup_data
            deploy
            print_success "Deployment completed successfully!"
            echo
            print_info "Next steps:"
            echo "  1. Review your .env configuration"
            echo "  2. Start the bot: ./deploy_simple.sh start"
            echo "  3. Check status: ./deploy_simple.sh status"
            echo "  4. View logs: ./deploy_simple.sh logs"
            ;;
        "start")
            start_bot
            ;;
        "stop")
            stop_bot
            ;;
        "restart")
            stop_bot
            sleep 2
            start_bot
            ;;
        "status")
            show_status
            ;;
        "logs")
            show_logs
            ;;
        "backup")
            backup_data
            print_success "Backup completed!"
            ;;
        "update")
            print_info "Updating bot..."
            stop_bot
            backup_data
            deploy
            start_bot
            print_success "Update completed!"
            ;;
        "help"|"-h"|"--help")
            echo "Usage: $0 [command]"
            echo
            echo "Commands:"
            echo "  deploy    - Full deployment setup (default)"
            echo "  start     - Start the bot"
            echo "  stop      - Stop the bot"
            echo "  restart   - Restart the bot"
            echo "  status    - Show bot status"
            echo "  logs      - View live logs"
            echo "  backup    - Create backup"
            echo "  update    - Update and restart bot"
            echo "  help      - Show this help message"
            echo
            echo "Examples:"
            echo "  $0 deploy    # Initial setup"
            echo "  $0 start     # Start bot"
            echo "  $0 status    # Check if running"
            echo "  $0 logs      # View live logs"
            ;;
        *)
            print_error "Unknown command: $1"
            echo "Use '$0 help' for usage information."
            exit 1
            ;;
    esac
}

# Run main function with all arguments
main "$@"