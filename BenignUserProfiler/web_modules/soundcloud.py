#!/usr/bin/env python3

import time
import random
import subprocess
import os
from .base_browser import BaseBrowserModule

class SoundcloudModule(BaseBrowserModule):
    def execute(self, config):
        soundcloud_url = "https://soundcloud.com"
        
        if not self.browser_command(soundcloud_url):
            print(">>> Failed to launch browser for SoundCloud")
            return False
            
        print(f">>> Browsing SoundCloud: {soundcloud_url}")
        time.sleep(random.uniform(5, 10))
        
        if "soundcloud_searches" in config:
            search_term = random.choice(config["soundcloud_searches"])
            print(f">>> Searching for music: {search_term}")
            
            # Choose between different search methods (direct URL or interactive)
            search_method = random.choice(["direct_url", "interactive"])
            
            if search_method == "direct_url":
                # Navigate directly to search results URL
                search_url = f"https://soundcloud.com/search?q={search_term.replace(' ', '%20')}"
                print(f">>> Using direct URL search: {search_url}")
                self.browser_command(search_url)
            else:
                # Interactive search using search box
                print(">>> Using interactive search method")
                # Navigate to main page
                self.browser_command(soundcloud_url)
                time.sleep(random.uniform(3, 5))
                
                # Try to find and click on the search box
                # Wait for page to fully load
                time.sleep(random.uniform(3, 5))
                
                try:
                    import pyautogui
                    screen_width, screen_height = pyautogui.size()
                    
                    # Try locations for SoundCloud's search box (not browser search bar)
                    # These positions target lower in the page to avoid browser's search bar
                    search_positions = [
                        (screen_width // 2, 150),          # Middle of SoundCloud search
                        (screen_width * 0.7, 150),         # Right side of SoundCloud search
                        (screen_width * 0.8, 150),         # Far right of SoundCloud search
                        (screen_width * 0.3, 150),         # Left side of SoundCloud search
                        (screen_width * 0.5, 200)          # Lower position as fallback
                    ]
                    
                    print(">>> Clicking on SoundCloud's search box (avoiding browser search bar)")
                    
                    # Try clicking on each possible search position
                    for pos in search_positions:
                        print(f">>> Clicking SoundCloud search box at {pos}")
                        pyautogui.click(pos[0], pos[1])
                        time.sleep(1.0)  # Longer wait to ensure focus
                        
                        # Type the search term
                        pyautogui.write(search_term)
                        time.sleep(0.5)
                        pyautogui.press('enter')
                        time.sleep(1.0)
                except ImportError:
                    # Fallback to multiple clicks
                    # Using positions further down in the page to target SoundCloud's search
                    search_positions = [(500, 150), (600, 150), (400, 150), (500, 200)]
                    
                    print(">>> Clicking on SoundCloud's search box (avoiding browser search bar)")
                    for pos in search_positions:
                        print(f">>> Clicking SoundCloud search box at {pos}")
                        self.click(pos[0], pos[1])
                        time.sleep(1.0)  # Longer wait to ensure focus
                        
                        # Type the search term using base_browser methods
                        for char in search_term:
                            self.press_key(char)
                            time.sleep(0.05)
                        self.press_key("Return")
                        time.sleep(1.0)
            
            # Wait for search results to load
            time.sleep(random.uniform(5, 10))
            
            print(">>> Selecting a track from search results")
            
            # Select a track with weighted random selection (prefer top results)
            # Define different selection areas with weights
            selection_areas = [
                # Area, weight (higher means more likely)
                {"area": {"x_min": 400, "x_max": 800, "y_min": 250, "y_max": 350}, "weight": 0.5},  # Top result
                {"area": {"x_min": 400, "x_max": 800, "y_min": 350, "y_max": 450}, "weight": 0.3},  # Second result
                {"area": {"x_min": 400, "x_max": 800, "y_min": 450, "y_max": 550}, "weight": 0.1},  # Third result
                {"area": {"x_min": 400, "x_max": 800, "y_min": 550, "y_max": 650}, "weight": 0.1}   # Fourth result
            ]
            
            # Choose an area based on weights
            weights = [area["weight"] for area in selection_areas]
            chosen_area = random.choices(selection_areas, weights=weights, k=1)[0]["area"]
            
            # Pick a random point within that area
            try:
                import pyautogui
                screen_width, screen_height = pyautogui.size()
                
                # Scale the coordinates based on screen size
                x_min = int(chosen_area["x_min"] * screen_width / 1920)
                x_max = int(chosen_area["x_max"] * screen_width / 1920)
                y_min = chosen_area["y_min"]
                y_max = chosen_area["y_max"]
                
                # Select random point within the area
                x = random.randint(x_min, x_max)
                y = random.randint(y_min, y_max)
                
                print(f">>> Clicking on track at position ({x}, {y})")
                
                # Click multiple times with slight offsets to ensure we hit the track
                for offset in [(0, 0), (10, 0), (-10, 0), (0, 10), (0, -10)]:
                    click_x = max(0, min(screen_width, x + offset[0]))
                    click_y = max(0, min(screen_height, y + offset[1]))
                    pyautogui.click(click_x, click_y)
                    time.sleep(0.3)
            except ImportError:
                # Fallback to simple click at fixed positions
                self.click(random.randint(400, 800), random.randint(300, 600))
                time.sleep(0.5)
                self.click(random.randint(400, 800), random.randint(300, 600))
            
            # Wait for track page to load
            time.sleep(5)
            
            # Multiple methods to ensure music plays
            print(">>> Using multiple methods to start music playback")
            
            # Method 1: Try using pyautogui to click at likely play button positions
            try:
                import pyautogui
                # Get screen size
                screen_width, screen_height = pyautogui.size()
                
                # First click on center of screen
                center_x, center_y = screen_width // 2, screen_height // 2
                print(f">>> Clicking center of screen ({center_x}, {center_y})")
                pyautogui.click(center_x, center_y)
                time.sleep(1)
                
                # Then try clicking on likely play button positions
                play_positions = [
                    (center_x, center_y - 100),  # Above center
                    (center_x - 200, center_y),  # Left of center
                    (center_x, center_y - 50),   # Slightly above center
                    (center_x - 100, center_y),  # Slightly left of center
                    (center_x - 250, center_y),  # Far left (SoundCloud play button)
                    (center_x - 250, center_y - 50), # Far left, slightly above
                    (center_x - 250, center_y + 50)  # Far left, slightly below
                ]
                
                for pos in play_positions:
                    print(f">>> Clicking potential play button at {pos}")
                    # Click multiple times with slight offsets
                    for offset in [(0, 0), (5, 0), (-5, 0), (0, 5), (0, -5)]:
                        click_x = max(0, min(screen_width, pos[0] + offset[0]))
                        click_y = max(0, min(screen_height, pos[1] + offset[1]))
                        pyautogui.click(click_x, click_y)
                        time.sleep(0.2)
                
            except ImportError:
                # Fallback to multiple clicks at different positions
                for pos in [(800, 400), (500, 300), (300, 400), (700, 300)]:
                    print(f">>> Clicking position {pos}")
                    self.click(pos[0], pos[1])
                    time.sleep(1)
            
            # Method 2: Press space key multiple times
            for _ in range(3):
                print(">>> Pressing space key to play/pause")
                self.press_key("space")
                time.sleep(0.5)
            
            # Method 3: Press J and K keys (common media player shortcuts)
            print(">>> Trying media player shortcuts")
            for key in ["j", "k", "l"]:
                self.press_key(key)
                time.sleep(0.5)
                
            # Method 4: Try to click on the waveform
            try:
                import pyautogui
                screen_width, screen_height = pyautogui.size()
                
                # SoundCloud's waveform is usually in the middle of the page
                waveform_y = screen_height // 2
                
                # Click at several positions along the waveform
                for x_ratio in [0.25, 0.5, 0.75]:
                    x = int(screen_width * x_ratio)
                    print(f">>> Clicking on waveform at ({x}, {waveform_y})")
                    pyautogui.click(x, waveform_y)
                    time.sleep(0.5)
            except ImportError:
                pass
            
            # Wait a bit to let music start
            print(">>> Track should be playing now")
            time.sleep(5)
            
            # Get listening time (30 minutes by default)
            listen_time = random.randint(
                config.get("soundcloud_min_listen", 1800),  # 30 min in seconds
                config.get("soundcloud_max_listen", 1800)  # 30 min in seconds
            )
            
            print(f">>> Listening to music for {listen_time} seconds")
            
            # Create a function to retry playback periodically
            def ensure_playback():
                print(">>> Ensuring music is playing...")
                
                # Try to click play button at various locations
                try:
                    import pyautogui
                    screen_width, screen_height = pyautogui.size()
                    
                    # For SoundCloud, the play button is often in these areas
                    play_positions = [
                        (screen_width // 2, screen_height // 2 - 100),  # Center-top
                        (screen_width // 3, screen_height // 2),        # Left-center
                        (screen_width // 2, screen_height // 2),        # Center
                        (screen_width // 2 - 200, screen_height // 2),  # Far left-center
                        (50, screen_height // 2),                      # Very far left (play button)
                        (screen_width // 2 - 250, screen_height // 2)   # Another far left position
                    ]
                    
                    # Click each position with multiple attempts and offsets
                    for pos in play_positions:
                        print(f">>> Clicking potential play button at {pos}")
                        for offset in [(0, 0), (5, 5), (-5, -5), (5, -5), (-5, 5)]:
                            click_x = max(0, min(screen_width, pos[0] + offset[0]))
                            click_y = max(0, min(screen_height, pos[1] + offset[1]))
                            pyautogui.click(click_x, click_y)
                            time.sleep(0.2)
                except ImportError:
                    # Use legacy approach
                    for pos in [(400, 300), (300, 350), (500, 300)]:
                        self.click(pos[0], pos[1])
                        time.sleep(0.5)
                
                # Press space key (universal play/pause)
                print(">>> Pressing space to play/pause")
                self.press_key("space")
                time.sleep(0.5)
                
                # Sometimes pressing 'L' restarts playback
                self.press_key("l")
                time.sleep(0.5)
                
                # Try using platform-specific methods as a last resort
                try:
                    platform = self.get_platform()
                    
                    if platform == "linux":
                        # On Linux, try xdotool key space
                        try:
                            subprocess.run(["xdotool", "key", "space"], timeout=1)
                            print(">>> Used xdotool to press space")
                        except (subprocess.SubprocessError, FileNotFoundError):
                            pass
                    elif platform == "windows":
                        # On Windows, pyautogui is already being used above
                        pass
                except Exception as e:
                    print(f">>> Error trying platform-specific playback: {e}")
            
            # Set up periodic checks
            intervals = min(15, max(3, listen_time // 120))  # More intervals
            interval_time = listen_time / intervals
            last_playback_check = time.time()
            playback_check_interval = 180  # Check every 3 minutes
            
            # Initial playback check to ensure it's playing from the start
            ensure_playback()
            
            # Simulate periodic interactions while listening
            for i in range(intervals):
                # Sleep for shorter intervals
                current_sleep = min(interval_time, playback_check_interval)
                time.sleep(current_sleep)
                
                # Check if we need to retry playback
                current_time = time.time()
                if current_time - last_playback_check >= playback_check_interval:
                    ensure_playback()
                    last_playback_check = current_time
                
                # Print status update
                interaction = random.choice([
                    "Still listening...",
                    "Enjoying the music...",
                    "Music playing...",
                    "Track continues...",
                    "Audio streaming..."
                ])
                print(f">>> {interaction}")
                
                # Show progress
                elapsed = (i + 1) * interval_time
                percent_complete = min(100, (elapsed / listen_time) * 100)
                print(f">>> Track progress: approximately {percent_complete:.1f}% complete")
                
                # Interact with the player using universal keyboard shortcuts
                if random.random() < 0.7:  # Increased chance to interact
                    interaction_type = random.choice([
                        "skip_forward",
                        "skip_backward",
                        "play_pause",
                        "volume_up",
                        "volume_down",
                        "mute"
                    ])
                    
                    # Use keyboard controls (works better cross-platform)
                    if interaction_type == "skip_forward":
                        # Press right arrow key multiple times
                        for _ in range(random.randint(1, 3)):
                            self.press_key("Right")
                            time.sleep(0.2)
                        print(">>> Skipped forward in track")
                    
                    elif interaction_type == "skip_backward":
                        # Press left arrow key multiple times
                        for _ in range(random.randint(1, 3)):
                            self.press_key("Left")
                            time.sleep(0.2)
                        print(">>> Skipped backward in track")
                    
                    elif interaction_type == "play_pause":
                        # Space is universal for play/pause
                        self.press_key("space")
                        print(">>> Paused track")
                        time.sleep(random.uniform(1.0, 2.0))
                        self.press_key("space")
                        print(">>> Resumed track")
                    
                    elif interaction_type == "volume_up":
                        # Up arrow for volume up
                        for _ in range(random.randint(1, 3)):
                            self.press_key("Up")
                            time.sleep(0.2)
                        print(">>> Increased volume")
                    
                    elif interaction_type == "volume_down":
                        # Down arrow for volume down
                        for _ in range(random.randint(1, 3)):
                            self.press_key("Down")
                            time.sleep(0.2)
                        print(">>> Decreased volume")
                    
                    elif interaction_type == "mute":
                        # M key often mutes
                        self.press_key("m")
                        print(">>> Muted track")
                        time.sleep(random.uniform(1.0, 2.0))
                        self.press_key("m")
                        print(">>> Unmuted track")
                
                # Occasionally scroll to see more tracks
                if i % 3 == 0 and random.random() < 0.5:
                    scroll_amount = random.randint(1, 3)
                    self.scroll_down(scroll_amount)
                    print(f">>> Scrolled down {scroll_amount} times to see more tracks")
                    time.sleep(random.uniform(1.0, 3.0))
                    
                    # Maybe click on another track
                    if random.random() < 0.3:  # 30% chance to click another track
                        try:
                            import pyautogui
                            screen_width = pyautogui.size()[0]
                            # Click in the area where tracks are usually listed
                            x_pos = random.randint(screen_width // 4, screen_width // 4 * 3)
                            y_pos = random.randint(400, 600)
                            print(f">>> Clicking on another track at ({x_pos}, {y_pos})")
                            
                            # Try clicking multiple times with slight offsets
                            for offset in [(0, 0), (10, 0), (-10, 0), (0, 10), (0, -10)]:
                                click_x = max(0, min(screen_width, x_pos + offset[0]))
                                click_y = max(0, min(screen_height, y_pos + offset[1]))
                                pyautogui.click(click_x, click_y)
                                time.sleep(0.2)
                            
                            # Ensure playback of the new track
                            time.sleep(2)
                            ensure_playback()
                        except ImportError:
                            # Fallback to standard click
                            self.click(random.randint(300, 700), random.randint(400, 600))
                            time.sleep(2)
        
        # Close browser when done
        self.close_browser()
        return True
        
    def get_platform(self):
        """Helper method to determine the platform"""
        import platform
        system = platform.system().lower()
        if system == "linux":
            return "linux"
        elif system == "windows":
            return "windows"
        elif system == "darwin":
            return "macos"
        else:
            return "unknown"