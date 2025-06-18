#!/bin/bash

# Define colors for better output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}=======================================================${NC}"
echo -e "${GREEN}=== Benign User Profiler - Real Traffic Generator ===${NC}"
echo -e "${GREEN}=======================================================${NC}"
echo -e "${YELLOW}Usage: ./run_real_traffic.sh [options]${NC}"
echo -e "${YELLOW}Options:${NC}"
echo -e "${YELLOW}  --headless     Run in headless mode (no visible browser windows)${NC}"
echo -e "${YELLOW}  --simulate     Run in simulation mode (no real browser interaction)${NC}"
echo -e "${YELLOW}  --randomize    Randomize task execution order${NC}"
echo -e "${GREEN}=======================================================${NC}"

# Check for required dependencies
if ! command -v firefox &> /dev/null; then
    echo -e "${RED}Firefox is not installed. Please install Firefox first.${NC}"
    exit 1
fi

# Check for necessary tools on Linux
if [[ "$(uname)" == "Linux" ]]; then
    # Check for xdotool
    if ! command -v xdotool &> /dev/null; then
        echo -e "${YELLOW}xdotool is not installed. Some interactive features may not work.${NC}"
        echo -e "${YELLOW}Consider installing xdotool:${NC}"
        echo -e "${GREEN}    sudo apt install xdotool    # For Debian/Ubuntu${NC}"
        echo -e "${GREEN}    sudo dnf install xdotool    # For Fedora${NC}"
        echo -e "${GREEN}    sudo pacman -S xdotool      # For Arch Linux${NC}"
    fi
    
    # Check for LibreOffice (for document creation on Linux)
    if ! command -v libreoffice &> /dev/null; then
        echo -e "${YELLOW}LibreOffice is not installed. Document creation features may not work.${NC}"
        echo -e "${YELLOW}Consider installing LibreOffice:${NC}"
        echo -e "${GREEN}    sudo apt install libreoffice    # For Debian/Ubuntu${NC}"
        echo -e "${GREEN}    sudo dnf install libreoffice    # For Fedora${NC}"
        echo -e "${GREEN}    sudo pacman -S libreoffice-still    # For Arch Linux${NC}"
    fi
fi

# Check for necessary tools on Windows
if [[ "$(uname)" == "MINGW"* ]] || [[ "$(uname)" == "MSYS"* ]]; then
    echo -e "${YELLOW}Running on Windows system${NC}"
    # PowerShell is required for Windows operations
    if ! command -v powershell.exe &> /dev/null; then
        echo -e "${RED}PowerShell not found. Many features will not work properly.${NC}"
    fi
    
    # Note about Microsoft Office
    echo -e "${YELLOW}Microsoft Office is required for document creation features.${NC}"
    echo -e "${YELLOW}Make sure Word, Excel, and PowerPoint are installed for full functionality.${NC}"
fi

# Kill any existing Firefox instances to avoid conflicts
echo -e "${YELLOW}Terminating any existing Firefox instances...${NC}"
pkill -f firefox || true
sleep 2

# Create directories for downloads if they don't exist
echo -e "${GREEN}Setting up directories...${NC}"
mkdir -p ~/output-benign/{ftp_downloads,ftp_uploads,sftp_downloads,sftp_uploads,email_attachments,image_downloads}

# Check command line arguments
HEADLESS=0
SIMULATE=0
RANDOMIZE=0

while [[ $# -gt 0 ]]; do
  case $1 in
    --headless)
      HEADLESS=1
      shift
      ;;
    --simulate)
      SIMULATE=1
      shift
      ;;
    --randomize)
      RANDOMIZE=1
      shift
      ;;
    *)
      echo -e "${YELLOW}Unknown option: $1${NC}"
      shift
      ;;
  esac
done

# Build command with optional flags
CMD="python -m BenignUserProfiler"

if [[ $SIMULATE -eq 1 ]]; then
    echo -e "${GREEN}Running in SIMULATION mode (no real browser interactions)${NC}"
    CMD="$CMD --simulate"
fi

if [[ $HEADLESS -eq 1 ]]; then
    echo -e "${GREEN}Running with real browser in HEADLESS mode${NC}"
    CMD="$CMD --headless"
else
    echo -e "${GREEN}Running with real browser in VISIBLE mode${NC}"
    # Launch a Firefox instance first to make sure it's working
    echo -e "${YELLOW}Testing Firefox...${NC}"
    firefox --version
fi

if [[ $RANDOMIZE -eq 1 ]]; then
    echo -e "${GREEN}Running with RANDOMIZED task execution${NC}"
    CMD="$CMD --randomize"
fi

# Execute the command
echo -e "${GREEN}Executing: $CMD${NC}"
$CMD

echo -e "${GREEN}=======================================================${NC}"
echo -e "${GREEN}=== Traffic generation complete ===${NC}"
echo -e "${GREEN}=======================================================${NC}"