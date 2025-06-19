#!/usr/bin/env python3

import time
import random
import os
import tempfile
import requests
import paramiko
from pathlib import Path
from datetime import datetime
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from .base_browser import BaseBrowserModule

class CustomServiceModule(BaseBrowserModule):
    def __init__(self, headless=False):
        super().__init__(headless)
        self.temp_dir = tempfile.mkdtemp()
        self.generated_files = []
        self.downloaded_files = []

    def execute(self, config):
        try:
            # Extract configuration parameters
            base_url = config.get("custom_service_url", "http://192.168.1.55")
            username = config.get("scp_username", "capwifi")
            password = config.get("scp_password", "bccc1234")
            scp_host = config.get("scp_host", "192.68.1.55")
            upload_path = config.get("scp_upload_path", "~/file-server-uploads")
            
            # 1. Generate TXT files for later use
            self._generate_txt_files(3)
            
            print(f">>> Visiting custom service: {base_url}")
            
            # 2. Visit the main page and scroll - use additional_args to open in new tab
            additional_args = ["-new-tab"] if self.os_type == "Linux" else []
            if not self.browser_command(base_url, additional_args):
                print(">>> Failed to open the main page")
                return False
            
            print(">>> Successfully opened main page, scrolling...")
            time.sleep(random.uniform(3, 5))
            
            # Scroll the page multiple times
            scroll_count = random.randint(3, 6)
            for i in range(scroll_count):
                print(f">>> Scrolling down ({i+1}/{scroll_count})")
                self.scroll_down(1)
                time.sleep(random.uniform(2, 4))
            
            # 3. Visit the guide route using browser command
            guide_url = urljoin(base_url, "/guide")
            print(f">>> Visiting guide: {guide_url}")
            
            # Use -new-tab to open in new tab
            additional_args = ["-new-tab"] if self.os_type == "Linux" else []
            if not self.browser_command(guide_url, additional_args):
                print(">>> Failed to open guide page")
                self.close_browser()
                return False
            
            print(">>> Successfully opened guide page, scrolling...")
            time.sleep(random.uniform(3, 5))
            
            # Scroll the userguide page
            scroll_count = random.randint(4, 7)
            for i in range(scroll_count):
                print(f">>> Scrolling down guide page ({i+1}/{scroll_count})")
                self.scroll_down(1)
                time.sleep(random.uniform(2, 4))
            
            # 4. Upload a TXT file to the API
            self._upload_file_to_api(base_url)
            time.sleep(random.uniform(3, 5))
            
            # 5. Visit the main page again using browser command
            print(f">>> Visiting main page again: {base_url}")
            additional_args = ["-new-tab"] if self.os_type == "Linux" else []
            if not self.browser_command(base_url, additional_args):
                print(">>> Failed to return to main page")
                self.close_browser()
                return False
            
            print(">>> Successfully returned to main page")
            time.sleep(random.uniform(3, 5))
            
            # 6. Download the report file using browser command
            report_url = urljoin(base_url, "/report")
            print(f">>> Visiting report page to download: {report_url}")
            
            additional_args = ["-new-tab"] if self.os_type == "Linux" else []
            if not self.browser_command(report_url, additional_args):
                print(">>> Failed to access report page")
                self.close_browser()
                return False
            
            print(">>> Report download should be initiated automatically")
            download_time = random.uniform(2, 5)
            print(f">>> Waiting {download_time:.1f} seconds for download to complete...")
            time.sleep(download_time)
            
            # 7. Visit files page using browser command
            files_url = urljoin(base_url, "/files")
            print(f">>> Visiting files page: {files_url}")
            
            additional_args = ["-new-tab"] if self.os_type == "Linux" else []
            if not self.browser_command(files_url, additional_args):
                print(">>> Failed to access files page")
                self.close_browser()
                return False
            
            print(">>> Successfully opened files page")
            time.sleep(random.uniform(3, 5))
            
            # Scroll to see the file table
            scroll_count = random.randint(2, 4)
            for i in range(scroll_count):
                print(f">>> Scrolling files page ({i+1}/{scroll_count})")
                self.scroll_down(1)
                time.sleep(random.uniform(2, 4))
            
            # Actually parse the HTML to find the download links with BeautifulSoup
            print(">>> Parsing HTML to find download links")
            try:
                # Get the page content
                response = requests.get(files_url)
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Find all <a> tags with class="download-link"
                download_links = soup.find_all('a', class_='download-link')
                
                if not download_links:
                    # If no download links found with that specific class, try finding any <a> tags
                    download_links = soup.find_all('a', href=True)
                    print(f">>> No specific download-link class found, using all {len(download_links)} links")
                else:
                    print(f">>> Found {len(download_links)} download links with class='download-link'")
                
                # Extract the href attributes
                download_paths = [link['href'] for link in download_links if 'href' in link.attrs]
                
                if len(download_paths) == 0:
                    print(">>> No download links found in page HTML")
                    # Fallback to finding any href that looks like a file
                    all_links = soup.find_all('a', href=True)
                    download_paths = [link['href'] for link in all_links if '.' in link['href']]
                    print(f">>> Fallback: found {len(download_paths)} potential file links")
                
                print(f">>> Found these download paths: {download_paths[:5]}")
                
                # Use up to 3 random download paths
                download_paths_to_use = random.sample(download_paths, min(3, len(download_paths))) if download_paths else []
                
            except Exception as e:
                print(f">>> Error parsing HTML: {e}")
                # Fallback in case the HTML parsing fails
                print(">>> Using fallback download paths")
                download_paths_to_use = [
                    f"/downloads/file_{random.randint(1000, 9999)}.txt",
                    f"/downloads/file_{random.randint(1000, 9999)}.pdf"
                ]
            
            for download_path in download_paths_to_use:
                # Construct full URL by concatenating base_url with download path
                download_url = urljoin(base_url, download_path)
                file_name = os.path.basename(download_path)
                
                print(f">>> Downloading file: {file_name} from {download_url}")
                
                # Open in a new tab
                additional_args = ["-new-tab"] if self.os_type == "Linux" else []
                if not self.browser_command(download_url, additional_args):
                    print(f">>> Failed to download {file_name}")
                    continue
                
                print(f">>> Download initiated for {file_name}")
                download_time = random.uniform(2, 6)
                print(f">>> Waiting {download_time:.1f} seconds for download...")
                time.sleep(download_time)
                
                # Wait between downloads for realistic timing
                time.sleep(random.uniform(5, 10))
            
            # 8. Upload a random file to SCP server
            self._upload_to_scp_server(scp_host, username, password, upload_path)
            
            # Close browser when done
            print(">>> Closing browser")
            self.close_browser()
            return True
            
        except Exception as e:
            print(f">>> Error in CustomServiceModule: {e}")
            self.close_browser()
            return False
    
    def _generate_txt_files(self, count=3):
        """Generate random text files for upload"""
        print(f">>> Generating {count} random text files")
        
        for i in range(count):
            file_path = os.path.join(self.temp_dir, f"upload_file_{i}.txt")
            
            content_types = [
                "System monitoring log data",
                "Application configuration settings",
                "Test results from automated testing",
                "Network scan results",
                "Service status report"
            ]
            
            try:
                with open(file_path, 'w') as f:
                    f.write(f"Test file created at {datetime.now()}\n")
                    f.write(f"Purpose: {random.choice(content_types)}\n")
                    f.write(f"File ID: {random.randint(10000, 99999)}\n")
                    f.write("-" * 40 + "\n\n")
                    
                    # Add random data
                    for j in range(random.randint(30, 100)):
                        f.write(f"Line {j}: Data entry at timestamp {time.time()} with value {random.random():.6f}\n")
                
                self.generated_files.append(file_path)
                print(f">>> Created file: {file_path}")
                
            except Exception as e:
                print(f">>> Error generating file: {e}")
        
        return self.generated_files
    
    def _upload_file_to_api(self, base_url):
        """Upload a text file to the API endpoint"""
        if not self.generated_files:
            print(">>> No files available for upload")
            return False
        
        upload_url = urljoin(base_url, "/api/upload")
        file_to_upload = random.choice(self.generated_files)
        
        print(f">>> Uploading file to API: {file_to_upload} -> {upload_url}")
        
        try:
            # Use requests to upload the file
            with open(file_to_upload, 'rb') as f:
                files = {'files': (os.path.basename(file_to_upload), f, 'text/plain')}
                
                # Use the same user agent as browser for consistency
                headers = {'User-Agent': random.choice(self.user_agents)}
                
                # Perform the upload
                response = requests.post(upload_url, files=files, headers=headers)
                
                if response.status_code == 200 or response.status_code == 201:
                    print(f">>> File upload successful, status code: {response.status_code}")
                    return True
                else:
                    print(f">>> File upload failed, status code: {response.status_code}")
                    print(f">>> Response: {response.text[:100]}...")
                    return False
                
        except Exception as e:
            print(f">>> Error uploading file: {e}")
            return False
    
    def _upload_to_scp_server(self, host, username, password, remote_path):
        """Upload a random file to SCP server"""
        if not self.generated_files:
            print(">>> No files available for SCP upload")
            return False
        
        file_to_upload = random.choice(self.generated_files)
        
        print(f">>> Preparing to upload file to SCP server: {host}")
        print(f">>> Username: {username}, Remote path: {remote_path}")
        
        try:
            # Create SSH client
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            
            # Connect to the server
            print(f">>> Connecting to SCP server: {host}")
            ssh.connect(hostname=host, username=username, password=password)
            
            # Create SFTPClient
            sftp = ssh.open_sftp()
            
            # Make sure remote directory exists
            try:
                # Resolve ~ in remote path if present
                if remote_path.startswith('~'):
                    stdin, stdout, stderr = ssh.exec_command('echo $HOME')
                    home_dir = stdout.read().decode().strip()
                    remote_path = remote_path.replace('~', home_dir)
                
                # Create directory if it doesn't exist
                ssh.exec_command(f"mkdir -p {remote_path}")
            except Exception as e:
                print(f">>> Warning creating remote directory: {e}")
            
            # Determine remote file path
            remote_file = f"{remote_path}/{os.path.basename(file_to_upload)}"
            
            # Upload the file
            print(f">>> Uploading: {file_to_upload} -> {remote_file}")
            start_time = time.time()
            
            sftp.put(file_to_upload, remote_file)
            
            # Calculate statistics
            end_time = time.time()
            upload_time = end_time - start_time
            file_size_mb = os.path.getsize(file_to_upload) / (1024 * 1024)
            
            print(f">>> Upload completed in {upload_time:.2f} seconds")
            print(f">>> Uploaded {file_size_mb:.2f} MB")
            
            if upload_time > 0:
                speed = file_size_mb / upload_time
                print(f">>> Average upload speed: {speed:.2f} MB/s")
            
            # Close connections
            sftp.close()
            ssh.close()
            
            return True
            
        except Exception as e:
            print(f">>> Error during SCP upload: {e}")
            return False