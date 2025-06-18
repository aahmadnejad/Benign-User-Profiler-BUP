#!/usr/bin/env python3

import time
import random
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin
from .base_browser import BaseBrowserModule

class WebBrowseModule(BaseBrowserModule):
    def __init__(self, headless=False):
        super().__init__(headless)
        self.visited_urls = set()
        self.user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.5 Safari/605.1.15",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/114.0",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:109.0) Gecko/20100101 Firefox/113.0"
        ]
    
    def execute(self, config):
        url = config.get("website") or config.get("link")
        if not url:
            print(">>> No website URL provided in config")
            return False
        
        # Handle Google search specifically
        if url.lower() == "https://www.google.com" and "search_terms" in config:
            return self._execute_google_search(config)
            
        # Handle regular website browsing
        if not self.browser_command(url):
            return self._fallback_browse(url)
            
        print(f">>> Browsing website: {url}")
        
        # Initial page load
        time.sleep(random.uniform(2, 5))
        
        # Determine how long to browse (30 minutes by default)
        browse_time = random.randint(
            config.get("min_browse_time", 1800),  # 30 min in seconds
            config.get("max_browse_time", 1800)  # 30 min in seconds
        )
        
        start_time = time.time()
        elapsed_time = 0
        
        print(f">>> Will browse for approximately {browse_time} seconds")
        
        # Initialize a list to track visited URLs within this session
        visited_urls_in_session = []
        if isinstance(url, str):
            visited_urls_in_session.append(url)
        
        # Click around the page periodically with more random interactions
        while elapsed_time < browse_time:
            # Randomly decide what to do next
            action = random.choices(
                ["scroll", "click", "open_new_link", "go_back", "refresh"], 
                weights=[0.4, 0.3, 0.2, 0.05, 0.05], 
                k=1
            )[0]
            
            if action == "scroll":
                # More scrolling with varied amounts
                scroll_amount = random.randint(1, 5)
                print(f">>> Scrolling down {scroll_amount} times")
                self.scroll_down(scroll_amount)
                
            elif action == "click" and config.get("click_elements", True):
                # Try clicking at positions where links or buttons might be
                click_positions = [
                    (random.randint(300, 700), random.randint(200, 600)),  # Random position
                    (random.randint(400, 600), random.randint(300, 500)),  # Another random position
                    (400, 400),  # Center
                    (300, 200),  # Upper navigation
                    (500, 300),  # Content area
                    (300, 700),  # Bottom navigation
                    (400, 600),  # Lower content
                    (100, 200)   # Sidebar/menu
                ]
                
                pos = random.choice(click_positions)
                print(f">>> Clicking at position {pos}")
                self.click(pos[0], pos[1])
                
                # Wait for page to respond to click
                click_wait = random.uniform(3, 8)
                elapsed_time += click_wait
                time.sleep(click_wait)
                
                # Check if the page changed (simulate by random chance)
                if random.random() < 0.6:  # 60% chance we clicked a link
                    print(">>> Page appears to have changed, waiting for load")
                    load_wait = random.uniform(2, 5)
                    elapsed_time += load_wait
                    time.sleep(load_wait)
                    
                    # Simulate adding a new URL to our history
                    current_url = f"{url}/page_{random.randint(1, 100)}"
                    visited_urls_in_session.append(current_url)
                    print(f">>> Now viewing: {current_url}")
            
            elif action == "open_new_link" and config.get("visit_sublinks", {}).get("enabled", True):
                # Simulate opening a new URL on the same site
                base_url = url
                if isinstance(base_url, dict) and "url" in base_url:
                    base_url = base_url["url"]
                
                # Generate a plausible sublink
                subpaths = ["about", "products", "services", "contact", "blog", "news", 
                           "faq", "support", "login", "register", "article", "category"]
                new_url = f"{base_url}/{random.choice(subpaths)}"
                
                print(f">>> Opening new URL: {new_url}")
                if self.browser_command(new_url):
                    visited_urls_in_session.append(new_url)
                    # Wait for page to load
                    load_wait = random.uniform(5, 10)
                    elapsed_time += load_wait
                    time.sleep(load_wait)
            
            elif action == "go_back" and len(visited_urls_in_session) > 1:
                print(">>> Going back to previous page")
                self.press_key("alt+Left")
                back_wait = random.uniform(2, 5)
                elapsed_time += back_wait
                time.sleep(back_wait)
                
                # Update our simulated history
                if len(visited_urls_in_session) > 1:
                    visited_urls_in_session.pop()
                    print(f">>> Returned to: {visited_urls_in_session[-1]}")
            
            elif action == "refresh":
                print(">>> Refreshing page")
                # Press F5 to refresh
                self.press_key("F5")
                refresh_wait = random.uniform(3, 7)
                elapsed_time += refresh_wait
                time.sleep(refresh_wait)
            
            # Random wait between actions
            wait_time = random.uniform(5, 15)
            elapsed_time += wait_time
            time.sleep(wait_time)
            
            # Show browsing statistics periodically
            if random.random() < 0.2:  # 20% chance
                print(f">>> Browsing stats: {len(visited_urls_in_session)} pages visited, {elapsed_time:.1f} seconds elapsed")
                remaining = browse_time - elapsed_time
                if remaining > 0:
                    print(f">>> Approximately {remaining:.1f} seconds remaining in browsing session")
            
            elapsed_time = time.time() - start_time
        
        print(f">>> Finished browsing after {elapsed_time:.1f} seconds")
        
        # Close browser when done
        self.close_browser()
        return True
    
    def _execute_google_search(self, config):
        # First access Google
        if not self.browser_command("https://www.google.com"):
            return self._fallback_browse("https://www.google.com")
            
        print(">>> Accessing Google search")
        time.sleep(random.uniform(2, 4))
        
        # Get a random search term from config
        search_term = random.choice(config["search_terms"])
        print(f">>> Will search for: {search_term}")
        
        # Type the search term into the search box
        self.keyboard_input(search_term)
        
        # Wait for search results
        time.sleep(random.uniform(3, 6))
        
        # Scroll through results
        scroll_count = random.randint(1, 4)
        for i in range(scroll_count):
            print(f">>> Scrolling through search results ({i+1}/{scroll_count})")
            self.scroll_down(1)
            time.sleep(random.uniform(2, 5))
        
        # Click on a result if configured
        if config.get("click_results", True):
            # Determine how many results to visit
            results_to_visit = random.randint(
                config.get("min_results_to_visit", 1),
                config.get("max_results_to_visit", 3)
            )
            
            print(f">>> Will visit {results_to_visit} search results")
            
            # Visit results
            for i in range(results_to_visit):
                # Calculate position for result click (different results down the page)
                y_pos = 250 + (i * 80)  # First result at ~250px, then every ~80px down
                self.click(400, y_pos)
                print(f">>> Clicked on result {i+1}")
                
                # Wait for page to load
                time.sleep(random.uniform(3, 6))
                
                # Browse the result page briefly
                result_browse_time = random.uniform(10, 30)
                print(f">>> Browsing result for {result_browse_time:.0f} seconds")
                
                # Scroll on the result page
                result_scrolls = random.randint(1, 3)
                for j in range(result_scrolls):
                    self.scroll_down(1)
                    time.sleep(random.uniform(2, 5))
                
                # Go back to search results
                self.press_key("alt+Left")
                print(">>> Returning to search results")
                time.sleep(random.uniform(2, 4))
        
        # Close browser when done
        self.close_browser()
        return True
    
    def _fallback_browse(self, url):
        print(f">>> Failed to launch browser for {url}")
        return False