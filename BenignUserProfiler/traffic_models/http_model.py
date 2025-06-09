#!/usr/bin/env python3

import time
import random
import platform
import subprocess
import os
import re
import requests
import tempfile
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin
from datetime import datetime
from .traffic_model import TrafficModel

class HTTPModel(TrafficModel):
    def __init__(self, browser_type=None, driver=None, headless=False):
        super().__init__()
        self.user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.5 Safari/605.1.15",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/114.0",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:109.0) Gecko/20100101 Firefox/113.0"
        ]
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': random.choice(self.user_agents),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Pragma': 'no-cache',
            'Cache-Control': 'no-cache'
        })
        self.download_dir = tempfile.mkdtemp()
        self.visited_urls = set()

    def __str__(self):
        return "HTTP/S"

    def generate(self) -> None:
        # Check if current time is within work hours if specified
        if not self._is_within_work_hours():
            print(">>> Current time is outside work hours. Skipping task.")
            return
            
        if "website" in self.model_config:
            if self.model_config["website"].lower() == "youtube":
                self._browse_youtube()
            elif self.model_config["website"].lower() == "download":
                self._download_media()
            elif self.model_config["website"].lower() in ["googledrive", "google_drive", "google-drive"]:
                self._use_google_drive()
            elif self.model_config["website"].lower() in ["onedrive", "one_drive", "one-drive"]:
                self._use_onedrive()
            else:
                self._browse_website(self.model_config["website"])
        elif "websites" in self.model_config:
            # Visit multiple websites
            websites = self.model_config["websites"]
            if self.model_config.get("randomize", False):
                random.shuffle(websites)
                
            for website in websites:
                if isinstance(website, dict):
                    if website.get("type") == "youtube":
                        self._browse_youtube()
                    elif website.get("type") == "download":
                        self._download_media()
                    elif website.get("type") in ["googledrive", "google_drive", "google-drive"]:
                        self._use_google_drive()
                    elif website.get("type") in ["onedrive", "one_drive", "one-drive"]:
                        self._use_onedrive()
                    else:
                        self._browse_website(website.get("url"))
                else:
                    self._browse_website(website)
                
                # Random delay between website visits
                time.sleep(random.uniform(2, 5))
        elif "link" in self.model_config:
            # Legacy support
            self._browse_website(self.model_config["link"])

    def verify(self) -> bool:
        if not (("website" in self.model_config) or 
                ("websites" in self.model_config) or 
                ("link" in self.model_config)):
            print(">>> Error in HTTP/S model: No website to visit specified in the config!")
            return False
        return True
        
    def _is_within_work_hours(self):
        """Check if current time is within specified work hours"""
        if "work_hours" not in self.model_config:
            return True  # No restriction if work hours not specified
            
        now = datetime.now().time()
        start_time_str = self.model_config["work_hours"].get("start", "09:00")
        end_time_str = self.model_config["work_hours"].get("end", "17:00")
        
        try:
            start_time = datetime.strptime(start_time_str, "%H:%M").time()
            end_time = datetime.strptime(end_time_str, "%H:%M").time()
            
            # Check if current time is within work hours
            if start_time <= now <= end_time:
                return True
            return False
        except Exception as e:
            print(f">>> Error parsing work hours: {e}")
            return True  # Default to allowing execution if parsing fails

    def _browse_website(self, url):
        """Visit a website and simulate realistic browsing"""
        try:
            # Make a request to the URL
            print(f">>> Visiting website: {url}")
            response = self.session.get(url, timeout=10)
            
            if response.status_code == 200:
                # Add to visited URLs
                self.visited_urls.add(url)
                
                # Parse the HTML
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Extract title and print
                title = soup.title.string if soup.title else "No Title"
                print(f">>> Loaded page: {title}")
                
                # Simulate initial page scan
                print(f">>> Scanning page content")
                time.sleep(random.uniform(1, 3))
                
                # Simulate scrolling behavior
                scroll_count = random.randint(3, 8)  # Random number of scrolls
                print(f">>> Scrolling through the page ({scroll_count} scrolls)")
                
                for i in range(scroll_count):
                    # Simulate a scroll action
                    scroll_action = random.choice([
                        "Scrolling down...",
                        "Reading content...",
                        "Viewing information...",
                        "Looking at page section...",
                        "Browsing page content..."
                    ])
                    print(f">>> Scroll {i+1}: {scroll_action}")
                    
                    # Simulate time spent reading content after each scroll
                    time.sleep(random.uniform(2, 6))
                
                # Random chance to scroll back up
                if random.random() < 0.3:  # 30% chance
                    print(">>> Scrolling back up to review content")
                    scroll_up_count = random.randint(1, min(3, scroll_count))
                    for i in range(scroll_up_count):
                        print(f">>> Scrolling up ({i+1}/{scroll_up_count})")
                        time.sleep(random.uniform(1, 3))
                
                # Visit sublinks if configured
                if "visit_sublinks" in self.model_config and self.model_config["visit_sublinks"].get("enabled", False):
                    depth = self.model_config["visit_sublinks"].get("depth", 1)
                    max_links = self.model_config["visit_sublinks"].get("max_links", 3)
                    self._visit_sublinks(url, soup, depth, max_links)
            else:
                print(f">>> Failed to load {url} - Status code: {response.status_code}")
                
        except Exception as e:
            print(f">>> Error in HTTP/S model when browsing {url}:")
            print(e)

    def _visit_sublinks(self, base_url, soup, depth=1, max_links=3, visited=None):
        """Visit sublinks of a website recursively"""
        if visited is None:
            visited = self.visited_urls.copy()
        
        if depth <= 0 or len(visited) >= max_links + len(self.visited_urls):
            return
            
        try:
            # Find all links on the page
            links = soup.find_all('a', href=True)
            valid_links = []
            
            # Filter for valid internal links
            base_domain = urlparse(base_url).netloc
            for link in links:
                href = link['href']
                # Convert relative URLs to absolute
                full_url = urljoin(base_url, href)
                
                if full_url.startswith(('http://', 'https://')):
                    link_domain = urlparse(full_url).netloc
                    if link_domain == base_domain and full_url not in visited:
                        valid_links.append(full_url)
            
            # Limit number of links and randomize
            if valid_links:
                links_to_visit = random.sample(
                    valid_links, 
                    min(max_links - (len(visited) - len(self.visited_urls)), len(valid_links))
                )
                
                # Visit each link
                for link in links_to_visit:
                    if len(visited) - len(self.visited_urls) >= max_links:
                        break
                        
                    print(f">>> Visiting sublink: {link}")
                    try:
                        response = self.session.get(link, timeout=10)
                        if response.status_code == 200:
                            visited.add(link)
                            self.visited_urls.add(link)
                            
                            # Parse the HTML for recursive visits
                            sub_soup = BeautifulSoup(response.text, 'html.parser')
                            
                            # Extract title and print
                            title = sub_soup.title.string if sub_soup.title else "No Title"
                            print(f">>> Loaded page: {title}")
                            
                            # Simulate initial page scan
                            print(f">>> Scanning subpage content")
                            time.sleep(random.uniform(1, 2))
                            
                            # Simulate scrolling behavior (fewer scrolls for subpages)
                            scroll_count = random.randint(2, 5)  # Random number of scrolls
                            print(f">>> Scrolling through the subpage ({scroll_count} scrolls)")
                            
                            for i in range(scroll_count):
                                # Simulate a scroll action
                                scroll_action = random.choice([
                                    "Scrolling down...",
                                    "Reading content...",
                                    "Viewing information...",
                                    "Looking at page section...",
                                    "Browsing page content..."
                                ])
                                print(f">>> Scroll {i+1}: {scroll_action}")
                                
                                # Simulate time spent reading content after each scroll
                                time.sleep(random.uniform(1, 3))
                            
                            # Recursive visit with decreased depth
                            if depth > 1:
                                self._visit_sublinks(base_url, sub_soup, depth-1, max_links, visited)
                    except Exception as e:
                        print(f">>> Error visiting sublink {link}: {e}")
                    
                    # Delay between sublinks
                    time.sleep(random.uniform(1, 3))
        
        except Exception as e:
            print(f">>> Error visiting sublinks: {e}")

    def _browse_youtube(self):
        """Simulate YouTube browsing with requests"""
        try:
            # Check if specific YouTube video URL is provided
            if "youtube_video" in self.model_config:
                video_url = self.model_config["youtube_video"]
                if not video_url.startswith("https://"):
                    # Handle video IDs or shortened URLs
                    if "youtu.be" in video_url:
                        video_id = video_url.split("/")[-1]
                    elif "v=" in video_url:
                        video_id = video_url.split("v=")[1].split("&")[0]
                    else:
                        video_id = video_url
                    
                    video_url = f"https://www.youtube.com/watch?v={video_id}"
                
                print(f">>> Visiting specific YouTube video: {video_url}")
                self._watch_youtube_video(video_url)
                return
                
            # Visit YouTube homepage
            youtube_url = "https://www.youtube.com"
            print(">>> Visiting YouTube homepage")
            response = self.session.get(youtube_url, timeout=10)
            
            if response.status_code == 200:
                self.visited_urls.add(youtube_url)
                print(">>> Browsing YouTube homepage")
                
                # Simulate scrolling through YouTube homepage
                print(">>> Scrolling through YouTube homepage")
                for i in range(random.randint(3, 6)):
                    print(f">>> Scroll {i+1}: Viewing YouTube content")
                    time.sleep(random.uniform(2, 5))
                
                # Search for videos if search terms are provided
                if "youtube_searches" in self.model_config:
                    search_term = random.choice(self.model_config["youtube_searches"])
                    search_url = f"https://www.youtube.com/results?search_query={search_term.replace(' ', '+')}"
                    print(f">>> Searching YouTube for: {search_term}")
                    
                    search_response = self.session.get(search_url, timeout=10)
                    if search_response.status_code == 200:
                        self.visited_urls.add(search_url)
                        print(f">>> Viewing search results for '{search_term}'")
                        
                        # Simulate scrolling through search results
                        print(">>> Scrolling through search results")
                        for i in range(random.randint(2, 4)):
                            print(f">>> Scroll {i+1}: Viewing more search results")
                            time.sleep(random.uniform(2, 4))
                        
                        # Parse search results page to find video links
                        soup = BeautifulSoup(search_response.text, 'html.parser')
                        
                        # Try to find video links (note: this is approximate as YouTube uses a lot of JavaScript)
                        video_links = []
                        for link in soup.find_all('a', href=True):
                            if '/watch?v=' in link['href']:
                                video_url = urljoin(youtube_url, link['href'])
                                if video_url not in video_links:
                                    video_links.append(video_url)
                        
                        # "Watch" a random video if found
                        if video_links:
                            video_url = random.choice(video_links)
                            self._watch_youtube_video(video_url)
                        else:
                            print(">>> No video links found in search results")
                
            else:
                print(f">>> Failed to load YouTube - Status code: {response.status_code}")
                
        except Exception as e:
            print(f">>> Error in YouTube browsing:")
            print(e)
            
    def _watch_youtube_video(self, video_url):
        """Watch a YouTube video with realistic simulation"""
        try:
            print(f">>> Watching YouTube video: {video_url}")
            
            # Fetch video page
            video_response = self.session.get(video_url, timeout=10)
            if video_response.status_code == 200:
                self.visited_urls.add(video_url)
                
                # Try to extract video title
                soup = BeautifulSoup(video_response.text, 'html.parser')
                title = soup.find('title')
                if title:
                    title_text = title.string.replace(' - YouTube', '')
                    print(f">>> Video title: {title_text}")
                
                # Simulate initial buffering
                print(">>> Video is buffering...")
                time.sleep(random.uniform(1, 3))
                
                # Simulate video playing
                print(">>> Video started playing")
                
                # Set video watch time
                watch_time = random.randint(30, 120) if "youtube_watch_time" not in self.model_config else \
                           random.randint(self.model_config.get("youtube_min_watch", 30),
                                        self.model_config.get("youtube_max_watch", 180))
                
                print(f">>> Watching video for {watch_time} seconds")
                
                # Simulate periodic interactions during video watching
                intervals = min(5, max(1, watch_time // 30))  # Create a few intervals during watching
                interval_time = watch_time / intervals
                
                for i in range(intervals):
                    time.sleep(interval_time)
                    
                    # Random interactions
                    interaction = random.choice([
                        "Still watching...",
                        "Scrolling down to see comments...",
                        "Scrolling back to video...",
                        "Adjusting volume...",
                        "Video playing..."
                    ])
                    print(f">>> {interaction}")
                
                # Simulate post-video interactions
                if random.random() < 0.2:  # 20% chance
                    print(">>> Liked the video")
                
                if random.random() < 0.1:  # 10% chance
                    print(">>> Subscribed to the channel")
                    
                if random.random() < 0.3:  # 30% chance
                    print(">>> Reading video comments")
                    time.sleep(random.uniform(5, 15))
                
                print(">>> Finished watching the video")
                
            else:
                print(f">>> Failed to load video - Status code: {video_response.status_code}")
                
        except Exception as e:
            print(f">>> Error watching YouTube video: {e}")

    def _download_media(self):
        """Simulate downloading media from free sources"""
        try:
            # Choose a download source from the configuration or use default
            download_sources = self.model_config.get("download_sources", [
                "https://www.pexels.com/search/free%20download/",
                "https://pixabay.com/",
                "https://unsplash.com/",
                "https://www.freepik.com/free-photos-vectors",
                "https://www.free-stock-music.com/"
            ])
            
            source = random.choice(download_sources)
            print(f">>> Visiting download source: {source}")
            
            # Visit the download source
            response = self.session.get(source, timeout=10)
            
            if response.status_code == 200:
                self.visited_urls.add(source)
                time.sleep(random.uniform(3, 5))
                
                # Parse the page to find downloadable media
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Search terms for media search
                search_terms = self.model_config.get("download_search_terms", ["nature", "city", "technology", "business"])
                search_term = random.choice(search_terms)
                
                # Try to build a search URL based on the site
                search_url = None
                
                if "pixabay.com" in source:
                    search_url = f"https://pixabay.com/images/search/{search_term.replace(' ', '%20')}/"
                elif "pexels.com" in source:
                    search_url = f"https://www.pexels.com/search/{search_term.replace(' ', '%20')}/"
                elif "unsplash.com" in source:
                    search_url = f"https://unsplash.com/s/photos/{search_term.replace(' ', '-')}"
                
                # If we created a search URL, visit it
                if search_url:
                    print(f">>> Searching for media with term: {search_term}")
                    search_response = self.session.get(search_url, timeout=10)
                    
                    if search_response.status_code == 200:
                        self.visited_urls.add(search_url)
                        time.sleep(random.uniform(2, 4))
                        
                        # Simulate downloading by finding an image URL and downloading it
                        search_soup = BeautifulSoup(search_response.text, 'html.parser')
                        
                        # Find image elements with potential download links
                        img_elements = search_soup.find_all('img', src=True)
                        
                        if img_elements:
                            # Pick a random image
                            img = random.choice(img_elements)
                            img_url = img['src']
                            
                            # Make sure it's an absolute URL
                            if not img_url.startswith(('http://', 'https://')):
                                img_url = urljoin(search_url, img_url)
                            
                            # Download the image to the temp directory
                            try:
                                img_response = self.session.get(img_url, stream=True, timeout=10)
                                if img_response.status_code == 200:
                                    img_filename = os.path.join(self.download_dir, f"downloaded_image_{int(time.time())}.jpg")
                                    
                                    with open(img_filename, 'wb') as f:
                                        for chunk in img_response.iter_content(1024):
                                            f.write(chunk)
                                    
                                    print(f">>> Downloaded image to {img_filename}")
                            except Exception as e:
                                print(f">>> Error downloading image: {e}")
                        else:
                            print(">>> No images found to download")
                else:
                    print(f">>> No search URL created for {source}")
            else:
                print(f">>> Failed to load {source} - Status code: {response.status_code}")
                
        except Exception as e:
            print(f">>> Error downloading media: {e}")

    def _use_google_drive(self):
        """Simulate Google Drive usage"""
        try:
            # Visit Google Drive
            drive_url = "https://drive.google.com"
            print(">>> Simulating Google Drive usage")
            
            # Since we can't actually login or interact with Google Drive without a browser,
            # we'll just simulate the behavior
            print(">>> Would visit Google Drive if using a browser")
            
            # Simulate creating a folder
            folder_names = ["Work Documents", "Personal Files", "Projects", "Research", "Temp Files"]
            folder_name = f"{random.choice(folder_names)} {datetime.now().strftime('%Y-%m-%d')}"
            print(f">>> Would create folder in Google Drive: {folder_name}")
            time.sleep(random.uniform(2, 4))
            
            # Simulate uploading a file
            file_content = f"Test file created at {datetime.now()}"
            temp_file = os.path.join(self.download_dir, f"test_file_{int(time.time())}.txt")
            
            with open(temp_file, 'w') as f:
                f.write(file_content)
                
            print(f">>> Would upload file to Google Drive: {temp_file}")
            time.sleep(random.uniform(2, 4))
            
            # Simulate browsing files
            print(">>> Would browse files in Google Drive")
            time.sleep(random.uniform(2, 4))
                
        except Exception as e:
            print(f">>> Error simulating Google Drive usage: {e}")

    def _use_onedrive(self):
        """Simulate OneDrive usage"""
        try:
            # Visit OneDrive
            onedrive_url = "https://onedrive.live.com"
            print(">>> Simulating OneDrive usage")
            
            # Since we can't actually login or interact with OneDrive without a browser,
            # we'll just simulate the behavior
            print(">>> Would visit OneDrive if using a browser")
            
            # Simulate creating a folder
            folder_names = ["Work Documents", "Personal Files", "Projects", "Research", "Temp Files"]
            folder_name = f"{random.choice(folder_names)} {datetime.now().strftime('%Y-%m-%d')}"
            print(f">>> Would create folder in OneDrive: {folder_name}")
            time.sleep(random.uniform(2, 4))
            
            # Simulate uploading a file
            file_content = f"Test file created at {datetime.now()}"
            temp_file = os.path.join(self.download_dir, f"test_file_{int(time.time())}.txt")
            
            with open(temp_file, 'w') as f:
                f.write(file_content)
                
            print(f">>> Would upload file to OneDrive: {temp_file}")
            time.sleep(random.uniform(2, 4))
            
            # Simulate browsing files
            print(">>> Would browse files in OneDrive")
            time.sleep(random.uniform(2, 4))
                
        except Exception as e:
            print(f">>> Error simulating OneDrive usage: {e}")