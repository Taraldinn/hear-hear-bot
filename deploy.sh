#!/bin/bash

# =============================================================================
# HEAR! HEAR! BOT - PRODUCTION DEPLOYMENT SCRIPT
# =============================================================================
# Automated deployment script for production environments

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
DOCKER_IMAGE_NAME="hearhear-bot"
BACKUP_DIR="./backups"

# Functions
print_header() {
    echo -e "${BLUE}============================================${NC}"
    echo -e "${BLUE}  $BOT_NAME - Production Deployment${NC}"
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
    
    # Check if Docker is installed
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    # Check if Docker Compose is installed
    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi
    
    # Check if .env file exists
    if [ ! -f .env ]; then
        print_error ".env file not found. Please create one based on .env.example"
        exit 1
    fi
    
    print_success "All requirements satisfied"
}

backup_data() {
    print_info "Creating backup of current deployment..."
    
    # Create backup directory
    mkdir -p "$BACKUP_DIR"
    
    # Backup current logs
    if [ -d "logs" ]; then
        cp -r logs "$BACKUP_DIR/logs_$(date +%Y%m%d_%H%M%S)" 2>/dev/null || true
        print_success "Logs backed up"
    fi
    
    # Backup current database (if using Docker volumes)
    if docker volume ls | grep -q hearhear; then
        print_info "Backing up Docker volumes..."
        docker run --rm -v hearhear-bot_mongodb-data:/data -v "$PWD/$BACKUP_DIR":/backup alpine tar czf /backup/mongodb_$(date +%Y%m%d_%H%M%S).tar.gz -C /data . 2>/dev/null || true
        print_success "Database backup created"
    fi
}

deploy() {
    print_info "Starting deployment..."
    
    # Pull latest code (if this is a git repository)
    if [ -d ".git" ]; then
        print_info "Pulling latest code..."
        git pull origin main || print_warning "Could not pull latest code"
    fi
    
    # Build and start services
    print_info "Building and starting services..."
    docker-compose down --remove-orphans 2>/dev/null || true
    docker-compose build --no-cache
    docker-compose up -d
    
    # Wait for services to be ready
    print_info "Waiting for services to start..."
    sleep 10
    
    # Check if services are running
    if docker-compose ps | grep -q "Up"; then
        print_success "Services are running"
    else
        print_error "Some services failed to start"
        docker-compose logs
        exit 1
    fi
}

health_check() {
    print_info "Performing health checks..."
    
    # Check bot container
    if docker-compose exec -T bot python -c "print('Bot container is healthy')" &>/dev/null; then
        print_success "Bot container is healthy"
    else
        print_error "Bot container health check failed"
        return 1
    fi
    
    # Check web server
    if curl -f http://localhost:8080/ &>/dev/null; then
        print_success "Web server is responding"
    else
        print_warning "Web server health check failed (may still be starting)"
    fi
    
    # Check database
    if docker-compose exec -T mongodb mongosh --eval "db.adminCommand('ping')" &>/dev/null; then
        print_success "Database is healthy"
    else
        print_warning "Database health check failed"
    fi
}

show_status() {
    echo
    print_info "Deployment Status:"
    docker-compose ps
    
    echo
    print_info "Service Logs (last 10 lines):"
    docker-compose logs --tail=10
    
    echo
    print_info "Available Endpoints:"
    echo "  - Bot Status: http://localhost:8080/"
    echo "  - Documentation: http://localhost:8080/docs"
    echo "  - Statistics: http://localhost:8080/stats"
    
    echo
    print_info "Useful Commands:"
    echo "  - View logs: docker-compose logs -f"
    echo "  - Restart bot: docker-compose restart bot"
    echo "  - Stop services: docker-compose down"
    echo "  - Update deployment: ./deploy.sh"
}

cleanup() {
    print_info "Cleaning up old Docker images..."
    docker image prune -f --filter "label=org.label-schema.name=$BOT_NAME" || true
    print_success "Cleanup completed"
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
            health_check
            cleanup
            show_status
            print_success "Deployment completed successfully!"
            ;;
        "restart")
            print_info "Restarting services..."
            docker-compose restart
            health_check
            print_success "Services restarted successfully!"
            ;;
        "stop")
            print_info "Stopping services..."
            docker-compose down
            print_success "Services stopped successfully!"
            ;;
        "logs")
            docker-compose logs -f
            ;;
        "status")
            show_status
            ;;
        "backup")
            backup_data
            print_success "Backup completed!"
            ;;
        "cleanup")
            print_info "Performing full cleanup..."
            docker-compose down -v --remove-orphans
            docker system prune -f
            print_success "Cleanup completed!"
            ;;
        "help"|"-h"|"--help")
            echo "Usage: $0 [command]"
            echo
            echo "Commands:"
            echo "  deploy    - Full deployment (default)"
            echo "  restart   - Restart services"
            echo "  stop      - Stop all services"
            echo "  logs      - View live logs"
            echo "  status    - Show deployment status"
            echo "  backup    - Create backup"
            echo "  cleanup   - Clean up Docker resources"
            echo "  help      - Show this help message"
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