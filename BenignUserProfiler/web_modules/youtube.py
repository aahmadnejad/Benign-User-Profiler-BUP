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
            
            # Two approaches for search: direct URL or interactive search
            search_method = random.choice(["direct_url", "interactive"])
            
            if search_method == "direct_url":
                # Navigate directly to search results URL
                search_url = f"https://www.youtube.com/results?search_query={search_term.replace(' ', '+')}"
                print(f">>> Using direct URL search: {search_url}")
                self.browser_command(search_url)
            else:
                # Interactive search using search box
                print(">>> Using interactive search method")
                
                # Click on search box - try several possible positions
                search_box_positions = [
                    (500, 40),   # Center top
                    (600, 40),   # Right top
                    (400, 40)    # Left top
                ]
                
                # Try clicking on search box
                for pos in search_box_positions:
                    print(f">>> Clicking search box at position {pos}")
                    try:
                        import pyautogui
                        screen_width, screen_height = pyautogui.size()
                        # Scale based on screen size
                        scaled_x = int(pos[0] * screen_width / 1000)
                        scaled_y = int(pos[1] * screen_height / 800)
                        pyautogui.click(scaled_x, scaled_y)
                    except ImportError:
                        self.click(pos[0], pos[1])
                    time.sleep(0.5)
                
                # Type the search term
                print(f">>> Typing search term: {search_term}")
                for char in search_term:
                    try:
                        import pyautogui
                        pyautogui.write(char, interval=0.1)
                    except ImportError:
                        self.keyboard_input(char)
                    time.sleep(0.05)
                
                # Press Enter to search
                time.sleep(0.5)
                print(">>> Pressing Enter to search")
                try:
                    import pyautogui
                    pyautogui.press('enter')
                except ImportError:
                    self.press_key("Return")
                
                # Wait for search results to load
                time.sleep(5)
            
            # Wait for search results to load
            time.sleep(random.uniform(5, 10))
            
            # Click on a video from search results
            print(">>> Selecting a video from search results")
            
            try:
                # Try to use PyAutoGUI for more precise control
                import pyautogui
                screen_width, screen_height = pyautogui.size()
                
                # Dynamically calculate video positions based on screen size
                video_positions = [
                    (screen_width // 2, int(screen_height * 0.3)),    # First video (top result)
                    (screen_width // 2, int(screen_height * 0.4)),    # Second video
                    (screen_width // 2, int(screen_height * 0.5)),    # Third video
                    (screen_width // 2, int(screen_height * 0.6)),    # Fourth video
                    (screen_width // 2, int(screen_height * 0.7))     # Fifth video
                ]
                
                # Randomly choose which video to click
                video_weights = [0.4, 0.3, 0.15, 0.1, 0.05]  # Higher weights for top results
                selected_index = random.choices(range(len(video_positions)), weights=video_weights, k=1)[0]
                selected_pos = video_positions[selected_index]
                
                print(f">>> Clicking on video at position {selected_pos} (result #{selected_index+1})")
                pyautogui.click(selected_pos[0], selected_pos[1])
                
            except ImportError:
                # Fallback to standard positions
                video_positions = [
                    (500, 300),  # First video
                    (500, 400),  # Second video
                    (500, 500),  # Third video
                    (500, 600),  # Fourth video
                    (500, 700)   # Fifth video
                ]
                
                # Randomly choose which video to click
                video_weights = [0.4, 0.3, 0.15, 0.1, 0.05]  # Higher weights for top results
                selected_index = random.choices(range(len(video_positions)), weights=video_weights, k=1)[0]
                selected_pos = video_positions[selected_index]
                
                print(f">>> Clicking on video at position {selected_pos} (result #{selected_index+1})")
                self.click(selected_pos[0], selected_pos[1])
                
            # Try multiple clicks to ensure we hit the video
            for i in range(2):
                time.sleep(0.5)
                try:
                    import pyautogui
                    # Random offset for second click
                    offset_x = random.randint(-20, 20)
                    offset_y = random.randint(-10, 10)
                    pyautogui.click(selected_pos[0] + offset_x, selected_pos[1] + offset_y)
                except ImportError:
                    self.click(selected_pos[0], selected_pos[1])
            
            # Wait for video to load and start playing
            time.sleep(random.uniform(5, 10))
            
            # Determine how long to watch (30 minutes by default)
            watch_time = random.randint(
                config.get("youtube_min_watch", 1800),  # 30 min in seconds
                config.get("youtube_max_watch", 1800)   # 30 min in seconds
            )
            
            print(f">>> Watching video for {watch_time} seconds")
            
            # Forcefully ensure video playback using multiple methods
            print(">>> Trying all methods to ensure video playback")
            
            # If YouTube direct video URL is provided, use it directly
            if "youtube_video" in config:
                direct_url = config["youtube_video"]
                print(f">>> Using direct YouTube URL: {direct_url}")
                self.browser_command(direct_url)
                time.sleep(5)  # Wait for page to load
            
            # Create a function to try multiple play methods in succession
            def try_play_methods():
                # Method 1: Directly click on multiple potential player positions
                click_positions = [
                    (500, 350),   # Center of typical video player
                    (400, 300),   # Upper part of player
                    (600, 350),   # Right side of player
                    (500, 400),   # Lower part of player
                    (350, 350)    # Left side of player
                ]
                
                for pos in click_positions:
                    print(f">>> Clicking at position {pos}")
                    try:
                        # Try PyAutoGUI first (more reliable)
                        import pyautogui
                        screen_width, screen_height = pyautogui.size()
                        # Scale position based on screen size
                        x_scale = screen_width / 1000
                        y_scale = screen_height / 700
                        scaled_x = int(pos[0] * x_scale)
                        scaled_y = int(pos[1] * y_scale)
                        print(f">>> Using PyAutoGUI to click at {scaled_x}, {scaled_y}")
                        pyautogui.click(scaled_x, scaled_y)
                    except ImportError:
                        # Fallback to base click method
                        self.click(pos[0], pos[1])
                    time.sleep(0.5)
                
                # Method 2: Press multiple different keys that might trigger play
                play_keys = ["space", "k", "p", "Return"]
                for key in play_keys:
                    print(f">>> Pressing '{key}' key to play video")
                    self.press_key(key)
                    time.sleep(0.5)
                
                # Method 3: Try F to enter/exit fullscreen (sometimes helps)
                print(">>> Pressing 'f' key to toggle fullscreen")
                self.press_key("f")
                time.sleep(1)
                self.press_key("f")  # Press again to exit fullscreen
                time.sleep(1)
                
                # Method 4: Click large play button if it appears
                big_play_positions = [
                    (screen_width // 2, screen_height // 2),  # Center of screen
                    (screen_width // 2, screen_height // 2 - 50)  # Slightly above center
                ]
                for pos in big_play_positions:
                    try:
                        import pyautogui
                        print(f">>> Clicking large play button at {pos}")
                        pyautogui.click(pos[0], pos[1])
                    except ImportError:
                        pass
                    time.sleep(0.5)
            
            # Try playback methods at the beginning
            try_play_methods()
            time.sleep(3)  # Wait to see if video starts
            
            # Simulate periodic interactions while watching
            intervals = min(10, max(2, watch_time // 30))
            interval_time = watch_time / intervals
            
            # Every 5 minutes, try the play methods again to ensure video keeps playing
            last_play_check = time.time()
            play_check_interval = 300  # 5 minutes
            
            for i in range(intervals):
                # Sleep for the current interval
                current_sleep = min(interval_time, play_check_interval)
                time.sleep(current_sleep)
                
                # Check if we need to try play methods again
                current_time = time.time()
                if current_time - last_play_check >= play_check_interval:
                    print(">>> Periodic playback check - ensuring video is still playing")
                    try_play_methods()
                    last_play_check = current_time
                
                # Print status updates
                interaction = random.choice([
                    "Still watching...",
                    "Watching video...",
                    "Video playing..."
                ])
                print(f">>> {interaction}")
                
                # Get the approximate completion percentage
                elapsed = (i + 1) * interval_time
                percent_complete = min(100, (elapsed / watch_time) * 100)
                print(f">>> Video progress: approximately {percent_complete:.1f}% complete")
                
                # Occasionally interact with the video (use keyboard shortcuts - more reliable)
                if random.random() < 0.7:  # 70% chance to interact
                    # Always use keyboard shortcuts since they're more reliable across platforms
                    interaction_type = random.choice([
                        "play_pause",
                        "like",
                        "volume",
                        "skip",
                        "fullscreen",
                        "quality",
                        "mute"
                    ])
                    
                    if interaction_type == "play_pause":
                        # Space or K key for play/pause
                        key = random.choice(["space", "k"])
                        self.press_key(key)
                        print(f">>> Pressed {key} key to pause video")
                        time.sleep(1.5)  # Brief pause
                        self.press_key(key)  # Resume
                        print(f">>> Pressed {key} key to resume video")
                        
                    elif interaction_type == "like":
                        # L key for like
                        self.press_key("l")
                        print(">>> Pressed L key to like/unlike video")
                        
                    elif interaction_type == "volume":
                        # Up/down arrows for volume
                        for _ in range(random.randint(1, 3)):
                            self.press_key("Up")
                            time.sleep(0.2)
                        time.sleep(0.5)
                        for _ in range(random.randint(1, 2)):
                            self.press_key("Down")
                            time.sleep(0.2)
                        print(">>> Adjusted volume with arrow keys")
                        
                    elif interaction_type == "skip":
                        # Left/right arrows for skipping
                        direction = random.choice(["forward", "backward"])
                        if direction == "forward":
                            for _ in range(random.randint(1, 5)):
                                self.press_key("Right")
                                time.sleep(0.2)
                            print(">>> Skipped forward in video")
                        else:
                            for _ in range(random.randint(1, 3)):
                                self.press_key("Left")
                                time.sleep(0.2)
                            print(">>> Skipped backward in video")
                            
                    elif interaction_type == "fullscreen":
                        # F key for fullscreen
                        self.press_key("f")
                        print(">>> Toggled fullscreen mode")
                        time.sleep(3)
                        self.press_key("f")  # Toggle back
                        print(">>> Exited fullscreen mode")
                        
                    elif interaction_type == "quality":
                        # First press settings key (.)
                        self.press_key(".")
                        time.sleep(1)
                        # Press up/down to navigate menu
                        for _ in range(random.randint(1, 4)):
                            self.press_key("Down")
                            time.sleep(0.3)
                        # Press escape to exit settings
                        self.press_key("Escape")
                        print(">>> Adjusted video quality settings")
                        
                    elif interaction_type == "mute":
                        # M key to mute/unmute
                        self.press_key("m")
                        print(">>> Muted video")
                        time.sleep(2)
                        self.press_key("m")
                        print(">>> Unmuted video")
                
                # Every third interval, try scrolling to see comments
                if i % 3 == 0 and random.random() < 0.5:
                    self.scroll_down(random.randint(1, 3))
                    print(">>> Scrolled down to view comments")
                    time.sleep(2)
                    # Scroll back up
                    for _ in range(random.randint(1, 3)):
                        self.press_key("Home")
                        time.sleep(0.5)
                    print(">>> Scrolled back to video")
            
        # Close browser when done
        self.close_browser()
        return True