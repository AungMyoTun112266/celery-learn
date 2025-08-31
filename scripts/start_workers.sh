#!/usr/bin/env bash
# Start Celery Workers Script
# Usage: ./scripts/start_workers.sh [worker_type]

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}Starting Celery Workers for Customer Processor${NC}"
echo "================================================="

# Default to starting all workers
WORKER_TYPE=${1:-"all"}

# Helper: detect CPU cores
get_concurrency() {
    if command -v nproc >/dev/null 2>&1; then
        nproc
    else
        sysctl -n hw.ncpu
    fi
}

# Function to start a specific worker
start_worker() {
    local worker_name=$1
    local queue=$2
    local concurrency=$3
    local prefetch=$4

    # cleanup stale pid
    rm -f ./logs/${worker_name}.pid

    echo -e "${YELLOW}Starting ${worker_name} worker...${NC}"

    celery -A shinsa.celery_app.app worker \
        --queues=$queue \
        --concurrency=$concurrency \
        --prefetch-multiplier=$prefetch \
        --loglevel=info \
        --hostname=${worker_name}@%h \
        --detach \
        --pidfile=./logs/${worker_name}.pid \
        --logfile=./logs/${worker_name}.log

    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ ${worker_name} worker started successfully${NC}"
    else
        echo -e "${RED}✗ Failed to start ${worker_name} worker${NC}"
    fi
}

# Create logs directory if it doesn't exist
mkdir -p logs

case $WORKER_TYPE in
    "coordination"|"coord")
        start_worker "coordination" "coordination" 4 10
        ;;
    
    "io"|"io_intensive")
        start_worker "io_intensive" "io_intensive" 20 4
        ;;
    
    "cpu"|"cpu_intensive")
        start_worker "cpu_intensive" "cpu_intensive" $(get_concurrency) 1
        ;;
    
    # "general"|"default")
    #     start_worker "general" "coordination,default" 2 4
    #     ;;
    
    "all")
        echo -e "${YELLOW}Starting all worker types...${NC}"
        start_worker "coordination" "coordination" 4 10
        sleep 2
        start_worker "io_intensive" "io_intensive" 20 4
        sleep 2
        start_worker "cpu_intensive" "cpu_intensive" $(get_concurrency) 1
        sleep 2
        # start_worker "general" "coordination,default" 2 4
        ;;
    
    *)
        echo -e "${RED}Unknown worker type: $WORKER_TYPE${NC}"
        echo "Available types: coordination, io, cpu, general, all"
        exit 1
        ;;
esac

echo ""
echo -e "${GREEN}Worker startup complete!${NC}"
echo ""
echo "To check worker status:"
echo "  celery -A app.celery_app status"
echo ""
echo "To stop all workers:"
echo "  celery -A app.celery_app control shutdown"
echo ""
echo "To monitor with Flower:"
echo "  celery -A app.celery_app flower"
