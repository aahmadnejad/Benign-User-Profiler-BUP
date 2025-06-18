#!/usr/bin/env python3

import time
import random
import os
import requests
import subprocess
from .base_browser import BaseBrowserModule

class ImageDownloadModule(BaseBrowserModule):
    def execute(self, config):
        download_sources = config.get("download_sources", [
            "https://www.pexels.com",
            "https://pixabay.com",
            "https://unsplash.com"
        ])
        
        source = random.choice(download_sources)
        
        search_terms = config.get("download_search_terms", 
                              ["nature", "city", "technology", "business"])
        search_term = random.choice(search_terms)
        
        # Create output directory if it doesn't exist
        output_dir = os.path.expanduser("~/output-benign/image_downloads")
        os.makedirs(output_dir, exist_ok=True)
        
        # Try direct API-based approach first (no browser needed)
        try:
            print(f">>> Attempting direct download of {search_term} image from {source}")
            
            # Different approach based on source
            if "unsplash.com" in source:
                # Use Unsplash API to search for images
                api_url = f"https://api.unsplash.com/search/photos?query={search_term}&per_page=10"
                # Using demo client ID (limited to 50 requests/hour)
                headers = {"Authorization": "Client-ID 8bJR5zKvpU6oZ5L6z5bM-qRcpDL88JvugPJ-87x3Mjg"}
                
                response = requests.get(api_url, headers=headers)
                if response.status_code == 200:
                    data = response.json()
                    if data["results"]:
                        # Get a random image from results
                        image = random.choice(data["results"])
                        image_url = image["urls"]["regular"]
                        
                        # Download the image
                        img_response = requests.get(image_url, stream=True)
                        if img_response.status_code == 200:
                            filename = f"unsplash_{int(time.time())}.jpg"
                            file_path = os.path.join(output_dir, filename)
                            
                            with open(file_path, 'wb') as f:
                                for chunk in img_response.iter_content(1024):
                                    f.write(chunk)
                            
                            print(f">>> Successfully downloaded image to {file_path}")
                            return True
            
            elif "pexels.com" in source:
                # Use Pexels API to search for images
                api_url = f"https://api.pexels.com/v1/search?query={search_term}&per_page=20"
                # Using demo API key (limited to 200 requests/hour)
                headers = {"Authorization": "563492ad6f91700001000001b76a00743e3a43918c9dbd7a12d95a71"}
                
                response = requests.get(api_url, headers=headers)
                if response.status_code == 200:
                    data = response.json()
                    if data["photos"]:
                        # Get a random image from results
                        photo = random.choice(data["photos"])
                        image_url = photo["src"]["medium"]
                        
                        # Download the image
                        img_response = requests.get(image_url, stream=True)
                        if img_response.status_code == 200:
                            filename = f"pexels_{int(time.time())}.jpg"
                            file_path = os.path.join(output_dir, filename)
                            
                            with open(file_path, 'wb') as f:
                                for chunk in img_response.iter_content(1024):
                                    f.write(chunk)
                            
                            print(f">>> Successfully downloaded image to {file_path}")
                            return True
            
            elif "pixabay.com" in source:
                # Use Pixabay API to search for images
                api_url = f"https://pixabay.com/api/?key=34249090-a56e0bf4b095a0e31ee5627ea&q={search_term}&image_type=photo&per_page=10"
                
                response = requests.get(api_url)
                if response.status_code == 200:
                    data = response.json()
                    if data["hits"]:
                        # Get a random image from results
                        image = random.choice(data["hits"])
                        image_url = image["webformatURL"]
                        
                        # Download the image
                        img_response = requests.get(image_url, stream=True)
                        if img_response.status_code == 200:
                            filename = f"pixabay_{int(time.time())}.jpg"
                            file_path = os.path.join(output_dir, filename)
                            
                            with open(file_path, 'wb') as f:
                                for chunk in img_response.iter_content(1024):
                                    f.write(chunk)
                            
                            print(f">>> Successfully downloaded image to {file_path}")
                            return True
            
            print(">>> Direct download failed, falling back to browser method")
        except Exception as e:
            print(f">>> Error with direct download: {e}")
            print(">>> Falling back to browser method")
        
        # Determine search URL for browser fallback
        search_url = None
        if "unsplash.com" in source:
            search_url = f"https://unsplash.com/s/photos/{search_term.replace(' ', '-')}"
        elif "pexels.com" in source:
            search_url = f"https://www.pexels.com/search/{search_term.replace(' ', '%20')}/"
        elif "pixabay.com" in source:
            search_url = f"https://pixabay.com/images/search/{search_term.replace(' ', '%20')}/"
        else:
            search_url = source
            
        # Use browser to download image
        if not self.browser_command(search_url):
            print(">>> Failed to launch browser for image download")
            return False
            
        print(f">>> Browsing {source} for media")
        print(f">>> Searching for: {search_term}")
        
        # Wait for page to load
        time.sleep(random.uniform(3, 6))
        
        # Scroll through results
        scroll_count = random.randint(2, 5)
        print(f">>> Scrolling through search results ({scroll_count} scrolls)")
        self.scroll_down(scroll_count)
        
        # Click on an image
        print(">>> Selecting an image to view")
        image_positions = [
            (500, 500),  # Center of screen
            (400, 450),  # Upper left
            (600, 450),  # Upper right
            (400, 650),  # Lower left
            (600, 650)   # Lower right
        ]
        pos = random.choice(image_positions)
        self.click(pos[0], pos[1])
        
        # Wait for image detail page to load
        time.sleep(random.uniform(3, 8))
        print(">>> Looking at details for a selected image")
        time.sleep(random.uniform(5, 10))
        
        # Download the image using right-click and keyboard
        print(">>> Attempting to download the image using right-click")
        # Right-click on the image (center of screen)
        self.right_click(500, 500)
        time.sleep(1)
        
        # Press down arrow twice
        print(">>> Pressing down arrow key twice")
        self.press_key("Down")
        time.sleep(0.2)
        self.press_key("Down")
        time.sleep(0.2)
        
        # Press Enter to select "Save Image As"
        self.press_key("Return")
        time.sleep(2)
        
        # Generate a unique filename
        filename = f"image_{int(time.time())}.jpg"
        file_path = os.path.join(output_dir, filename)
        
        # Type the filename in the save dialog
        time.sleep(1)
        if self.os_type == "Linux":
            # Type the path
            subprocess.run(["xdotool", "type", file_path], 
                         check=False,
                         stdout=subprocess.DEVNULL, 
                         stderr=subprocess.DEVNULL)
            time.sleep(1)
            
            # Press Enter to save
            subprocess.run(["xdotool", "key", "Return"], 
                         check=False,
                         stdout=subprocess.DEVNULL, 
                         stderr=subprocess.DEVNULL)
        elif self.os_type == "Windows":
            ps_script = f'''
            Add-Type -AssemblyName System.Windows.Forms
            [System.Windows.Forms.SendKeys]::SendWait("{file_path}")
            Start-Sleep -Seconds 1
            [System.Windows.Forms.SendKeys]::SendWait("{{ENTER}}")
            '''
            subprocess.run(["powershell", "-Command", ps_script], 
                         shell=True,
                         stdout=subprocess.DEVNULL, 
                         stderr=subprocess.DEVNULL)
        
        # Wait for download to complete
        download_time = random.uniform(2, 5)
        print(f">>> Waiting {download_time:.1f} seconds for download to complete")
        time.sleep(download_time)
        
        print(f">>> Image saved to: {file_path}")
        
        # Close browser when done
        self.close_browser()
        return True