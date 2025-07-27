#!/bin/bash

# Script để setup và chạy browserless service

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default values
BROWSERLESS_PORT=3000
BROWSERLESS_IMAGE="ghcr.io/browserless/chromium"
CONTAINER_NAME="nhatot-browserless"

print_banner() {
    echo -e "${BLUE}"
    echo "╔══════════════════════════════════════════════════════════════╗"
    echo "║                🚀 BROWSERLESS SETUP 🚀                     ║"
    echo "║            Setup Browserless cho Nhatot Crawler             ║"
    echo "╚══════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

check_docker() {
    if ! command -v docker &> /dev/null; then
        echo -e "${RED}❌ Docker không được cài đặt!${NC}"
        echo -e "${YELLOW}Vui lòng cài đặt Docker trước: https://docs.docker.com/get-docker/${NC}"
        exit 1
    fi
    
    if ! docker info &> /dev/null; then
        echo -e "${RED}❌ Docker daemon không chạy!${NC}"
        echo -e "${YELLOW}Vui lòng khởi động Docker Desktop hoặc Docker daemon${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}✅ Docker đã sẵn sàng${NC}"
}

stop_existing_container() {
    if docker ps -a --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
        echo -e "${YELLOW}🛑 Đang dừng container browserless hiện tại...${NC}"
        docker stop "$CONTAINER_NAME" &> /dev/null || true
        docker rm "$CONTAINER_NAME" &> /dev/null || true
        echo -e "${GREEN}✅ Đã dừng container cũ${NC}"
    fi
}

pull_browserless_image() {
    echo -e "${BLUE}📥 Đang tải browserless image...${NC}"
    if docker pull "$BROWSERLESS_IMAGE"; then
        echo -e "${GREEN}✅ Đã tải browserless image thành công${NC}"
    else
        echo -e "${RED}❌ Lỗi tải browserless image${NC}"
        exit 1
    fi
}

start_browserless() {
    echo -e "${BLUE}🚀 Đang khởi động browserless service...${NC}"
    
    # Check if port is in use
    if lsof -Pi :$BROWSERLESS_PORT -sTCP:LISTEN -t >/dev/null 2>&1; then
        echo -e "${YELLOW}⚠️  Port $BROWSERLESS_PORT đang được sử dụng${NC}"
        echo -e "${YELLOW}Đang dừng process sử dụng port này...${NC}"
        lsof -ti:$BROWSERLESS_PORT | xargs kill -9 2>/dev/null || true
        sleep 2
    fi
    
    # Start browserless container
    docker run -d \
        --name "$CONTAINER_NAME" \
        -p $BROWSERLESS_PORT:3000 \
        --restart unless-stopped \
        -e "CONCURRENT=10" \
        -e "TIMEOUT=30000" \
        "$BROWSERLESS_IMAGE"
    
    # Wait for service to be ready
    echo -e "${YELLOW}⏳ Chờ browserless service khởi động...${NC}"
    for i in {1..30}; do
        if curl -s http://localhost:$BROWSERLESS_PORT/json/version &> /dev/null; then
            echo -e "${GREEN}✅ Browserless service đã sẵn sàng!${NC}"
            break
        fi
        if [ $i -eq 30 ]; then
            echo -e "${RED}❌ Timeout: Browserless service không khởi động được${NC}"
            docker logs "$CONTAINER_NAME"
            exit 1
        fi
        sleep 1
    done
}

show_status() {
    echo -e "${BLUE}📊 Trạng thái Browserless Service:${NC}"
    echo -e "${GREEN}   🌐 URL: http://localhost:$BROWSERLESS_PORT${NC}"
    echo -e "${GREEN}   📚 Docs: http://localhost:$BROWSERLESS_PORT/docs${NC}"
    echo -e "${GREEN}   🔍 Debug: http://localhost:$BROWSERLESS_PORT/debugger${NC}"
    echo -e "${GREEN}   📦 Container: $CONTAINER_NAME${NC}"
    
    echo -e "\n${BLUE}🔗 WebSocket endpoint cho crawler:${NC}"
    echo -e "${YELLOW}   ws://localhost:$BROWSERLESS_PORT${NC}"
    
    echo -e "\n${BLUE}📝 Commands hữu ích:${NC}"
    echo -e "${YELLOW}   # Xem logs${NC}"
    echo -e "   docker logs $CONTAINER_NAME"
    echo -e "${YELLOW}   # Dừng service${NC}"
    echo -e "   docker stop $CONTAINER_NAME"
    echo -e "${YELLOW}   # Restart service${NC}"
    echo -e "   docker restart $CONTAINER_NAME"
}

show_help() {
    echo "Sử dụng: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  -p, --port PORT       Port cho browserless service (mặc định: 3000)"
    echo "  -h, --help           Hiển thị help"
    echo "  --stop               Dừng browserless service"
    echo "  --restart            Restart browserless service"
    echo "  --status             Kiểm tra trạng thái service"
    echo "  --logs               Xem logs của service"
    echo ""
    echo "Ví dụ:"
    echo "  $0                   # Khởi động với cấu hình mặc định"
    echo "  $0 -p 3001           # Khởi động trên port 3001"
    echo "  $0 --stop            # Dừng service"
    echo "  $0 --restart         # Restart service"
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -p|--port)
            BROWSERLESS_PORT="$2"
            shift 2
            ;;
        --stop)
            stop_existing_container
            echo -e "${GREEN}✅ Đã dừng browserless service${NC}"
            exit 0
            ;;
        --restart)
            stop_existing_container
            start_browserless
            show_status
            exit 0
            ;;
        --status)
            if docker ps --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
                echo -e "${GREEN}✅ Browserless service đang chạy${NC}"
                show_status
            else
                echo -e "${RED}❌ Browserless service không chạy${NC}"
            fi
            exit 0
            ;;
        --logs)
            if docker ps -a --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
                docker logs -f "$CONTAINER_NAME"
            else
                echo -e "${RED}❌ Container $CONTAINER_NAME không tồn tại${NC}"
            fi
            exit 0
            ;;
        -h|--help)
            show_help
            exit 0
            ;;
        *)
            echo -e "${RED}❌ Option không hợp lệ: $1${NC}"
            show_help
            exit 1
            ;;
    esac
done

# Main execution
main() {
    print_banner
    
    echo -e "${BLUE}🔍 Kiểm tra requirements...${NC}"
    check_docker
    
    stop_existing_container
    pull_browserless_image
    start_browserless
    
    echo -e "\n${GREEN}🎉 Setup hoàn thành!${NC}"
    show_status
    
    echo -e "\n${BLUE}💡 Bạn có thể chạy crawler ngay bây giờ:${NC}"
    echo -e "${YELLOW}   cd $(dirname "$0")${NC}"
    echo -e "${YELLOW}   python index.py${NC}"
    echo -e "${YELLOW}   # hoặc${NC}"
    echo -e "${YELLOW}   python run_crawler.py${NC}"
}

# Run main function
main "$@" 