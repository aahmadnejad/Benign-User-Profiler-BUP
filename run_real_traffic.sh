#!/bin/bash

# Define colors for better output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${GREEN}=======================================================${NC}"
echo -e "${GREEN}=== Benign User Profiler - Real Traffic Generator ===${NC}"
echo -e "${GREEN}=======================================================${NC}"
echo -e "${YELLOW}Usage: ./run_real_traffic.sh [options]${NC}"
echo -e "${YELLOW}Options:${NC}"
echo -e "${YELLOW}  --headless     Run in headless mode (no visible browser windows)${NC}"
echo -e "${YELLOW}  --simulate     Run in simulation mode (no real browser interaction)${NC}"
echo -e "${YELLOW}  --randomize    Randomize task execution order${NC}"
echo -e "${YELLOW}  --auto-install Install required dependencies automatically${NC}"
echo -e "${YELLOW}  --debug        Show more detailed debug information${NC}"
echo -e "${YELLOW}  --verbose      Show all output including browser operations${NC}"
echo -e "${GREEN}=======================================================${NC}"
echo -e "${BLUE}Important: For scrolling and clicking to work properly, install pyautogui:${NC}"
echo -e "${BLUE}    pip install pyautogui${NC}"
echo -e "${GREEN}=======================================================${NC}"

# Detect OS
OS_TYPE="Unknown"
if [[ "$(uname)" == "Linux" ]]; then
    OS_TYPE="Linux"
    # Further detect Linux distribution
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        DISTRO=$ID
    elif [ -f /etc/lsb-release ]; then
        . /etc/lsb-release
        DISTRO=$DISTRIB_ID
    else
        DISTRO="unknown"
    fi
    echo -e "${GREEN}Detected Linux distribution: $DISTRO${NC}"
elif [[ "$(uname)" == "Darwin" ]]; then
    OS_TYPE="macOS"
    echo -e "${GREEN}Detected macOS system${NC}"
elif [[ "$(uname)" == "MINGW"* ]] || [[ "$(uname)" == "MSYS"* ]]; then
    OS_TYPE="Windows"
    echo -e "${GREEN}Detected Windows system${NC}"
else
    echo -e "${YELLOW}Unknown operating system. Some features may not work correctly.${NC}"
fi

# Parse arguments early to check for auto-install
AUTO_INSTALL=0
DEBUG=0
VERBOSE=0
HEADLESS=0
SIMULATE=0
RANDOMIZE=0

for arg in "$@"; do
    case $arg in
        --auto-install)
            AUTO_INSTALL=1
            ;;
        --debug)
            DEBUG=1
            ;;
        --verbose)
            VERBOSE=1
            ;;
    esac
done

# Function to install packages
install_package() {
    if [ $DEBUG -eq 1 ]; then
        echo -e "${YELLOW}Attempting to install package: $1${NC}"
    fi
    
    if [ "$OS_TYPE" == "Linux" ]; then
        if [ "$DISTRO" == "ubuntu" ] || [ "$DISTRO" == "debian" ]; then
            sudo apt-get update -y
            sudo apt-get install -y "$1"
        elif [ "$DISTRO" == "fedora" ]; then
            sudo dnf install -y "$1"
        elif [ "$DISTRO" == "arch" ] || [ "$DISTRO" == "manjaro" ]; then
            sudo pacman -S --noconfirm "$1"
        else
            echo -e "${RED}Unsupported Linux distribution for auto-install.${NC}"
            return 1
        fi
    elif [ "$OS_TYPE" == "Windows" ]; then
        # For Windows, we use Chocolatey if available
        if command -v choco &> /dev/null; then
            choco install -y "$1"
        else
            echo -e "${RED}Chocolatey not found. Cannot auto-install on Windows.${NC}"
            echo -e "${YELLOW}Please install Chocolatey first: https://chocolatey.org/install${NC}"
            return 1
        fi
    elif [ "$OS_TYPE" == "macOS" ]; then
        # For macOS, we use Homebrew
        if command -v brew &> /dev/null; then
            brew install "$1"
        else
            echo -e "${RED}Homebrew not found. Cannot auto-install on macOS.${NC}"
            echo -e "${YELLOW}Please install Homebrew first: https://brew.sh/${NC}"
            return 1
        fi
    else
        echo -e "${RED}Auto-install not supported on this operating system.${NC}"
        return 1
    fi
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}Successfully installed $1${NC}"
        return 0
    else
        echo -e "${RED}Failed to install $1${NC}"
        return 1
    fi
}

# Install Python packages
install_python_packages() {
    echo -e "${GREEN}Installing required Python packages...${NC}"
    python -m pip install --upgrade pip
    
    if [ -f requirements.txt ]; then
        pip install -r requirements.txt
    else
        # Install core requirements including pyautogui for browser automation
        pip install requests selenium bs4 psutil pyautogui
    fi
    
    # Always try to install pyautogui (critical for browser interaction)
    echo -e "${GREEN}Installing PyAutoGUI for cross-platform browser automation...${NC}"
    pip install pyautogui
    
    # Install additional dependencies based on OS
    if [ "$OS_TYPE" == "Windows" ]; then
        echo -e "${GREEN}Installing Windows-specific dependencies...${NC}"
        pip install pywin32
    elif [ "$OS_TYPE" == "Linux" ]; then
        # Check for Linux-specific dependencies
        if ! python -c "import Xlib" &>/dev/null; then
            echo -e "${GREEN}Installing Linux X11 dependencies for PyAutoGUI...${NC}"
            pip install python-xlib
        fi
    fi
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}Python package installation successful${NC}"
    else
        echo -e "${RED}Python package installation failed${NC}"
        # Don't exit on failure, try to continue
        echo -e "${YELLOW}Will attempt to continue despite package installation issues${NC}"
    fi
}

# Check for Firefox and install if needed
if ! command -v firefox &> /dev/null; then
    echo -e "${RED}Firefox is not installed.${NC}"
    if [ $AUTO_INSTALL -eq 1 ]; then
        echo -e "${GREEN}Attempting to install Firefox...${NC}"
        if [ "$OS_TYPE" == "Linux" ]; then
            install_package firefox
        elif [ "$OS_TYPE" == "Windows" ]; then
            install_package firefox
        elif [ "$OS_TYPE" == "macOS" ]; then
            install_package firefox
        fi
        
        if ! command -v firefox &> /dev/null; then
            echo -e "${RED}Firefox installation failed. Please install Firefox manually.${NC}"
            exit 1
        fi
    else
        echo -e "${RED}Please install Firefox or run with --auto-install option.${NC}"
        exit 1
    fi
else
    echo -e "${GREEN}Firefox is installed.${NC}"
fi

# Check for necessary tools on Linux
if [ "$OS_TYPE" == "Linux" ]; then
    # Check for xdotool
    if ! command -v xdotool &> /dev/null; then
        echo -e "${YELLOW}xdotool is not installed. Some interactive features may not work.${NC}"
        if [ $AUTO_INSTALL -eq 1 ]; then
            echo -e "${GREEN}Installing xdotool...${NC}"
            install_package xdotool
        else
            echo -e "${YELLOW}Consider installing xdotool:${NC}"
            echo -e "${GREEN}    sudo apt install xdotool    # For Debian/Ubuntu${NC}"
            echo -e "${GREEN}    sudo dnf install xdotool    # For Fedora${NC}"
            echo -e "${GREEN}    sudo pacman -S xdotool      # For Arch Linux${NC}"
        fi
    fi
    
    # Check for LibreOffice (for document creation on Linux)
    if ! command -v libreoffice &> /dev/null; then
        echo -e "${YELLOW}LibreOffice is not installed. Document creation features may not work.${NC}"
        if [ $AUTO_INSTALL -eq 1 ]; then
            echo -e "${GREEN}Installing LibreOffice...${NC}"
            install_package libreoffice
        else
            echo -e "${YELLOW}Consider installing LibreOffice:${NC}"
            echo -e "${GREEN}    sudo apt install libreoffice    # For Debian/Ubuntu${NC}"
            echo -e "${GREEN}    sudo dnf install libreoffice    # For Fedora${NC}"
            echo -e "${GREEN}    sudo pacman -S libreoffice-still    # For Arch Linux${NC}"
        fi
    fi
fi

# Check for necessary tools on Windows
if [ "$OS_TYPE" == "Windows" ]; then
    # PowerShell is required for Windows operations
    if ! command -v powershell.exe &> /dev/null; then
        echo -e "${RED}PowerShell not found. Many features will not work properly.${NC}"
    fi
    
    # Note about Microsoft Office
    echo -e "${YELLOW}Microsoft Office is recommended for document creation features.${NC}"
    echo -e "${YELLOW}Make sure Word, Excel, and PowerPoint are installed for full functionality.${NC}"
    
    # Install Python packages if auto-install
    if [ $AUTO_INSTALL -eq 1 ]; then
        install_python_packages
    fi
fi

# Check if this is the first run and install Python packages if needed
if [ ! -d "venv" ] && [ $AUTO_INSTALL -eq 1 ]; then
    echo -e "${GREEN}Setting up Python environment...${NC}"
    python -m venv venv
    source venv/bin/activate
    install_python_packages
fi

# Kill any existing Firefox instances to avoid conflicts
echo -e "${YELLOW}Terminating any existing Firefox instances...${NC}"
if [ "$OS_TYPE" == "Linux" ] || [ "$OS_TYPE" == "macOS" ]; then
    pkill -f firefox || true
elif [ "$OS_TYPE" == "Windows" ]; then
    taskkill //F //IM firefox.exe 2>/dev/null || true
fi
sleep 2

# Create directories for downloads if they don't exist
echo -e "${GREEN}Setting up directories...${NC}"
mkdir -p ~/output-benign/{ftp_downloads,ftp_uploads,sftp_downloads,sftp_uploads,email_attachments,image_downloads}

# Parse command line arguments
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
    --auto-install)
      # Already processed
      shift
      ;;
    --debug)
      # Already processed
      shift
      ;;
    *)
      echo -e "${YELLOW}Unknown option: $1${NC}"
      shift
      ;;
  esac
done

# Build command with optional flags
CMD="python -m BenignUserProfiler -p"

# Always use randomize by default
RANDOMIZE=1
echo -e "${GREEN}Running with RANDOMIZED task execution (default)${NC}"
CMD="$CMD --randomize"

if [ $SIMULATE -eq 1 ]; then
    echo -e "${GREEN}Running in SIMULATION mode (no real browser interactions)${NC}"
    CMD="$CMD --simulate"
fi

if [ $HEADLESS -eq 1 ]; then
    echo -e "${GREEN}Running with real browser in HEADLESS mode${NC}"
    CMD="$CMD --headless"
else
    echo -e "${GREEN}Running with real browser in VISIBLE mode${NC}"
    # Launch a Firefox instance first to make sure it's working
    echo -e "${YELLOW}Testing Firefox...${NC}"
    firefox --version
fi

if [ $DEBUG -eq 1 ]; then
    echo -e "${GREEN}Running in DEBUG mode${NC}"
    CMD="$CMD --debug"
    
    # Set the Python debug environment variable
    export PYTHONDEVMODE=1
    export PYTHONUTF8=1
fi

# Set verbose flag if requested
if [ $VERBOSE -eq 1 ]; then
    echo -e "${GREEN}Running in VERBOSE mode${NC}"
    export PYTHONVERBOSE=1
    # Don't redirect stdout/stderr to null for better debugging
    export BUP_VERBOSE=1
fi

# Execute the command
echo -e "${GREEN}Executing: $CMD${NC}"
$CMD

echo -e "${GREEN}=======================================================${NC}"
echo -e "${GREEN}=== Traffic generation complete ===${NC}"
echo -e "${GREEN}=======================================================${NC}"