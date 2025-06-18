#!/usr/bin/env python3

import time
import random
from .base_browser import BaseBrowserModule

class YoutubeModule(BaseBrowserModule):
    def execute(self, config):
        youtube_url = "https://www.youtube.com"
        
        if not self.browser_command(youtube_url):
            print(">>> Failed to launch browser for YouTube")
            return False
            
        print(f">>> Browsing YouTube: {youtube_url}")
        
        # Wait for page to load
        time.sleep(random.uniform(5, 10))
        
        # Check if we have search terms
        if "youtube_searches" in config:
            search_term = random.choice(config["youtube_searches"])
            print(f">>> Searching for: {search_term}")
            
            # Navigate directly to search results
            search_url = f"https://www.youtube.com/results?search_query={search_term.replace(' ', '+')}"
            self.browser_command(search_url)
            
            # Wait for search results to load
            time.sleep(random.uniform(5, 10))
            
            # Click on the first video (approximately where videos appear)
            video_positions = [
                (500, 600),  # First video
                (500, 850),  # Second video
                (500, 950)   # Third video
            ]
            
            # Choose which video to click (usually first one)
            pos = video_positions[0]
            if random.random() < 0.3:  # 30% chance to click on a different video
                pos = random.choice(video_positions[1:])
                
            print(f">>> Clicking on video at position {pos}")
            self.click(pos[0], pos[1])
            
            # Wait for video to load and start playing
            time.sleep(random.uniform(5, 10))
            
            # Determine how long to watch
            watch_time = random.randint(
                config.get("youtube_min_watch", 60),
                config.get("youtube_max_watch", 300)
            )
            
            print(f">>> Watching video for {watch_time} seconds")
            
            # Force video to play using multiple methods
            print(">>> Trying to start video playback")
            
            # Method 1: Click in the center of the video player
            print(">>> Clicking center of video")
            try:
                import pyautogui
                # Get screen size
                screen_width, screen_height = pyautogui.size()
                # Click center of screen
                pyautogui.click(screen_width // 2, screen_height // 2)
                time.sleep(1)
            except ImportError:
                self.click(500, 400)  # Fallback to approximate center
                time.sleep(1)
            
            # Method 2: Press space bar
            print(">>> Pressing space bar to play/pause")
            self.press_key("space")
            time.sleep(1)
            
            # Method 3: Press 'k' key (YouTube keyboard shortcut for play/pause)
            print(">>> Pressing 'k' key (YouTube shortcut)")
            self.press_key("k")
            time.sleep(1)
            
            # Simulate periodic interactions while watching
            intervals = min(10, max(2, watch_time // 30))
            interval_time = watch_time / intervals
            
            for i in range(intervals):
                time.sleep(interval_time)
                
                # Print status updates
                interaction = random.choice([
                    "Still watching...",
                    "Watching video...",
                    "Video playing..."
                ])
                print(f">>> {interaction}")
                
                # Occasionally interact with the video
                if random.random() < 0.7:  # 70% chance to interact (increased from 50%)
                    interaction_type = random.choice([
                        "scroll",
                        "like",
                        "volume",
                        "skip",
                        "fullscreen"
                    ])
                    
                    # Get screen dimensions for more accurate positioning
                    if self.os_type == "Windows":
                        # Use more reliable key presses instead of clicks when possible
                        if interaction_type == "scroll":
                            self.scroll_down()
                            print(">>> Scrolled down in comments")
                        elif interaction_type == "like":
                            # Use L key to like on YouTube
                            self.press_key("l")
                            print(">>> Pressed L key to like video")
                        elif interaction_type == "volume":
                            # Use up/down arrow for volume
                            self.press_key("Up")
                            time.sleep(0.5)
                            self.press_key("Down")
                            print(">>> Adjusted volume with arrow keys")
                        elif interaction_type == "skip":
                            # Skip forward with right arrow key
                            self.press_key("Right")
                            self.press_key("Right")
                            print(">>> Skipped forward in video")
                        elif interaction_type == "fullscreen":
                            # F key for fullscreen
                            self.press_key("f")
                            print(">>> Pressed F key for fullscreen")
                            time.sleep(3)
                            # Exit fullscreen
                            self.press_key("Escape")
                    else:
                        # Original click-based approach for Linux
                        if interaction_type == "scroll":
                            self.scroll_down()
                            print(">>> Scrolled down in comments")
                        elif interaction_type == "like":
                            # Like button position
                            self.click(600, 700)
                            print(">>> Clicked like button")
                        elif interaction_type == "volume":
                            # Volume control area
                            self.click(200, 700)
                            print(">>> Adjusted volume")
                        elif interaction_type == "fullscreen":
                            # Fullscreen button area
                            self.click(900, 700)
                            print(">>> Toggled fullscreen")
                            time.sleep(5)
                            # Press Escape to exit fullscreen
                            self.press_key("Escape")
                        elif interaction_type == "skip":
                            # Skip forward
                            self.press_key("Right")
                            print(">>> Skipped forward in video")
            
        # Close browser when done
        self.close_browser()
        return True