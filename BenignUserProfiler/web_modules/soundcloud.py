#!/usr/bin/env python3

import time
import random
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
            
            search_url = f"https://soundcloud.com/search?q={search_term.replace(' ', '%20')}"
            print(f">>> Navigating to SoundCloud search: {search_url}")
            self.browser_command(search_url)
            
            time.sleep(random.uniform(5, 10))
            
            print(">>> Selecting a track from search results")
            time.sleep(5)
            
            # Click on the first search result (typically around this position)
            self.click(900, 450)
            print(">>> Clicked on first search result")
            
            # Wait for track page to load
            time.sleep(5)
            
            # Multiple methods to ensure music plays
            print(">>> Using multiple methods to start music playback")
            
            # Method 1: Try using pyautogui to click at the exact center of the play button
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
                ]
                
                for pos in play_positions:
                    print(f">>> Clicking potential play button at {pos}")
                    pyautogui.click(pos[0], pos[1])
                    time.sleep(0.5)
                
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
            
            # Wait a bit to let music start
            print(">>> Track should be playing now")
            time.sleep(5)
            
            # Get listening time (30 minutes by default)
            listen_time = random.randint(
                config.get("soundcloud_min_listen", 1800),  # 30 min in seconds
                config.get("soundcloud_max_listen", 1800)  # 30 min in seconds
            )
            
            print(f">>> Listening to music for {listen_time} seconds")
            
            # Simulate periodic interactions while listening
            intervals = min(10, max(2, listen_time // 30))
            interval_time = listen_time / intervals
            
            for i in range(intervals):
                time.sleep(interval_time)
                
                interaction = random.choice([
                    "Still listening...",
                    "Enjoying the music...",
                    "Music playing..."
                ])
                print(f">>> {interaction}")
                
                # Occasionally interact with the player
                if random.random() < 0.6:  # Increased from 0.4
                    interaction_type = random.choice([
                        "skip_forward",
                        "play_pause",
                        "volume",
                        "scrub"
                    ])
                    
                    if self.os_type == "Windows":
                        # Use more reliable keyboard shortcuts for Windows
                        if interaction_type == "skip_forward":
                            # Press right arrow key multiple times to ensure it works
                            self.press_key("Right")
                            time.sleep(0.2)
                            self.press_key("Right")
                            print(">>> Skipped forward in track with arrow keys")
                        elif interaction_type == "play_pause":
                            # Space is universal for play/pause
                            self.press_key("space")
                            print(">>> Paused track with space key")
                            time.sleep(1.5)
                            self.press_key("space")
                            print(">>> Resumed track with space key")
                        elif interaction_type == "volume":
                            # Up/down arrows for volume
                            self.press_key("Up")
                            time.sleep(0.2)
                            self.press_key("Up")
                            time.sleep(0.5)
                            self.press_key("Down")
                            print(">>> Adjusted volume with arrow keys")
                        elif interaction_type == "scrub":
                            # Use Left/Right for scrubbing through track
                            jumps = random.randint(1, 5)
                            direction = random.choice(["Left", "Right"])
                            for _ in range(jumps):
                                self.press_key(direction)
                                time.sleep(0.1)
                            print(f">>> Jumped {direction.lower()} in track using arrow keys")
                    else:
                        # Original approach for Linux
                        if interaction_type == "skip_forward":
                            self.press_key("Right")
                            print(">>> Skipped forward in track")
                        elif interaction_type == "play_pause":
                            self.press_key("space")
                            print(">>> Paused/resumed track")
                            time.sleep(1.5)
                            self.press_key("space")
                        elif interaction_type == "volume":
                            self.click(800, 700)
                            print(">>> Adjusted volume")
                        elif interaction_type == "scrub":
                            x_pos = random.randint(300, 600)
                            self.click(x_pos, 700)
                            print(">>> Jumped to different part of track")
        
        # Close browser when done
        self.close_browser()
        return True