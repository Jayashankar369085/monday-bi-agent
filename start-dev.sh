#!/bin/bash

# Skylark Drones BI Agent - Local Development Startup Script
# Usage: ./start-dev.sh

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║     Skylark Drones BI Agent - Local Development Setup      ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════════╝${NC}"

# Check for required commands
check_command() {
    if ! command -v $1 &> /dev/null; then
        echo -e "${RED}✗ $1 is not installed${NC}"
        return 1
    fi
    echo -e "${GREEN}✓ $1 is installed${NC}"
}

echo ""
echo -e "${YELLOW}Checking dependencies...${NC}"
check_command docker || exit 1
check_command docker-compose || exit 1

# Check for .env file
echo ""
echo -e "${YELLOW}Checking environment configuration...${NC}"
if [ ! -f "backend/.env" ]; then
    echo -e "${YELLOW}Creating .env file from template...${NC}"
    cp backend/.env.example backend/.env
    echo -e "${RED}⚠ Please update backend/.env with your API keys:${NC}"
    echo "   - MONDAY_API_TOKEN=your_monday_api_token"
    echo "   - OPENAI_API_KEY=your_openai_api_key"
    echo ""
    read -p "Continue after updating .env? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Build and start services
echo ""
echo -e "${YELLOW}Building Docker images...${NC}"
docker-compose build

echo ""
echo -e "${YELLOW}Starting services...${NC}"
docker-compose up -d

# Wait for services to be ready
echo ""
echo -e "${YELLOW}Waiting for services to start...${NC}"
sleep 5

# Check service health
echo ""
echo -e "${YELLOW}Checking service health...${NC}"

# Backend health check
if curl -f http://localhost:8000/api/health > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Backend is running${NC}"
else
    echo -e "${RED}✗ Backend is not responding${NC}"
    echo "  Check logs with: docker-compose logs backend"
fi

# Frontend check
if curl -f http://localhost > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Frontend is running${NC}"
else
    echo -e "${RED}✗ Frontend is not responding${NC}"
    echo "  Check logs with: docker-compose logs frontend"
fi

echo ""
echo -e "${GREEN}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║                   Services Started!                        ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${GREEN}🌐 Frontend:        http://localhost${NC}"
echo -e "${GREEN}📡 Backend API:     http://localhost:8000${NC}"
echo -e "${GREEN}📖 API Docs:        http://localhost:8000/docs${NC}"
echo -e "${GREEN}🏥 Health Check:    http://localhost:8000/api/health${NC}"
echo ""
echo -e "${YELLOW}Useful commands:${NC}"
echo "  View logs:          docker-compose logs -f"
echo "  View backend logs:  docker-compose logs -f backend"
echo "  View frontend logs: docker-compose logs -f frontend"
echo "  Stop services:      docker-compose down"
echo "  Rebuild:            docker-compose build --no-cache"
echo ""
echo -e "${YELLOW}Next steps:${NC}"
echo "  1. Open http://localhost in your browser"
echo "  2. Try example queries or generate leadership update"
echo "  3. Check backend logs for any errors"
echo ""
echo -e "${GREEN}✓ Ready to go!${NC}"
