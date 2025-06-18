#!/bin/bash

# Set environment variables to avoid Firefox profile issues
export MOZ_HEADLESS=0  # Set to 1 for headless mode
export MOZ_DISABLE_CONTENT_SANDBOX=1
export MOZ_DBUS_REMOTE=1

# Create a temporary directory for Firefox profile
PROFILE_DIR=$(mktemp -d)
echo "Creating Firefox profile in: $PROFILE_DIR"

# Run the profiler with different options based on arguments
if [ "$1" == "--simulate" ]; then
    echo "Running in simulation mode (no real browser interactions)"
    python -m BenignUserProfiler --simulate
elif [ "$1" == "--headless" ]; then
    echo "Running with real browser in headless mode"
    export MOZ_HEADLESS=1
    python -m BenignUserProfiler --headless
else
    echo "Running with real browser in visible mode"
    python -m BenignUserProfiler
fi

# Clean up temporary files
echo "Cleaning up temporary Firefox profile"
rm -rf $PROFILE_DIR