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
            
            # Click on the upper part of the page to play music
            print(">>> Clicking on upper part of the page to play music")
            self.click(800, 400)
            
            # Also try the space key as a fallback
            time.sleep(1)
            self.press_key("space")
            
            print(">>> Track should be playing now")
            time.sleep(5)
            
            # Get listening time
            listen_time = random.randint(
                config.get("soundcloud_min_listen", 60),
                config.get("soundcloud_max_listen", 300)
            )
            
            print(f">>> Listening to music for {listen_time} seconds")
            
            # Make sure playback starts by pressing space
            self.press_key("space")
            time.sleep(1)
            
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