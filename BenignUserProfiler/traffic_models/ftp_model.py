#!/usr/bin/env python3

import time
import os
import random
import tempfile
from ftplib import FTP_TLS, FTP, all_errors
from pathlib import Path
from datetime import datetime
from .traffic_model import TrafficModel

class FTPModel(TrafficModel):
    def __init__(self, ssl=False):
        super().__init__()
        self.__ssl = ssl
        self.temp_dir = tempfile.mkdtemp()
        self.protocol = "FTPS" if ssl else "FTP"

    def __str__(self):
        return self.protocol

    def verify(self) -> bool:
        # Check for required connection parameters
        for key in ["address", "username", "password"]:
            if key not in self.model_config:
                print(f">>> Error in {self.protocol} model: No '{key}' specified in the config!")
                return False

        # Either downloads, uploads, browse, or simulate must be specified
        if not any(key in self.model_config for key in ["downloads", "uploads", "browse", "simulate"]):
            print(f">>> Error in {self.protocol} model: No operations specified. Use 'downloads', 'uploads', 'browse', or 'simulate'.")
            return False

        # Validate download configurations if present
        if "downloads" in self.model_config:
            for download in self.model_config["downloads"]:
                for key in ["path", "output_dir", "file_name"]:
                    if key not in download:
                        print(f">>> Error in {self.protocol} model: No '{key}' specified in the downloads"
                              f" config! download: {download}")
                        return False

        # Validate upload configurations if present
        if "uploads" in self.model_config:
            for upload in self.model_config["uploads"]:
                for key in ["path", "input_dir", "file_name"]:
                    if key not in upload:
                        print(f">>> Error in {self.protocol} model: No '{key}' specified in the uploads"
                              f" config! upload: {upload}")
                        return False

        return True

    def generate(self) -> None:
        # Extract configuration parameters
        host = self.model_config["address"]
        port = self.model_config.get("port", 21)  # Default FTP port
        username = self.model_config["username"]
        password = self.model_config["password"]
        
        # Check if we're in simulation mode
        if self.model_config.get("simulate", False):
            self._simulate_ftp_operations()
            return
        
        # Prepare data structures for operations
        downloads = self.model_config.get("downloads", [])
        uploads = self.model_config.get("uploads", [])
        browse_dirs = self.model_config.get("browse", [])
        
        # Connect to FTP server
        ftp = None
        try:
            print(f">>> Connecting to {self.protocol} server: {host}:{port}")
            
            # Choose connection type based on SSL setting
            if self.__ssl:
                ftp = FTP_TLS(host=host, timeout=30)
                ftp.connect(host, port)
            else:
                ftp = FTP(host=host, timeout=30)
                ftp.connect(host, port)
                
            print(f">>> Connected to {host}. Logging in as {username}...")
            ftp.login(username, password)
            
            # Enable secure data connection for FTPS
            if self.__ssl:
                print(">>> Enabling secure data connection...")
                ftp.prot_p()
                
            print(f">>> Successfully logged in as {username}")
            
            # Display welcome message
            welcome = ftp.getwelcome()
            print(f">>> Server welcome: {welcome}")
            
            # Get system info if available
            try:
                system_info = ftp.sendcmd("SYST")
                print(f">>> Server system: {system_info}")
            except:
                pass
                
            # Perform browsing operations
            if browse_dirs:
                self._browse_directories(ftp, browse_dirs)
                
            # Perform download operations
            if downloads:
                self._download_files(ftp, downloads)
                
            # Perform upload operations
            if uploads:
                self._upload_files(ftp, uploads)
                
            # Close connection
            print(f">>> Closing {self.protocol} connection...")
            ftp.quit()
            print(f">>> {self.protocol} session completed successfully")
            
        except all_errors as e:
            print(f">>> Error in {self.protocol} connection/operations:")
            print(f">>> {type(e).__name__}: {str(e)}")
        except Exception as e:
            print(f">>> Unexpected error in {self.protocol} model:")
            print(f">>> {type(e).__name__}: {str(e)}")
        finally:
            # Ensure FTP connection is closed
            if ftp:
                try:
                    ftp.quit()
                except:
                    try:
                        ftp.close()
                    except:
                        pass
    
    def _browse_directories(self, ftp, browse_dirs):
        """Browse directories on FTP server"""
        print(f"\n>>> Browsing {self.protocol} directories...")
        
        # If no specific directories provided, browse the current directory
        if not browse_dirs:
            browse_dirs = ["."]
            
        for dir_path in browse_dirs:
            try:
                print(f"\n>>> Changing to directory: {dir_path}")
                ftp.cwd(dir_path)
                
                # List directory contents
                print(f">>> Listing contents of: {dir_path}")
                file_list = []
                ftp.dir(file_list.append)
                
                # Print directory contents
                if file_list:
                    print(">>> Directory contents:")
                    for item in file_list[:10]:  # Show first 10 items only to avoid too much output
                        print(f">>>   {item}")
                    if len(file_list) > 10:
                        print(f">>>   ... and {len(file_list) - 10} more items")
                else:
                    print(">>> Directory is empty")
                    
                # Get current working directory
                try:
                    cwd = ftp.pwd()
                    print(f">>> Current directory: {cwd}")
                except:
                    pass
                    
                # Random delay to simulate browsing
                time.sleep(random.uniform(1, 3))
                
            except all_errors as e:
                print(f">>> Error browsing directory {dir_path}: {e}")
                continue
                
    def _download_files(self, ftp, downloads):
        """Download files from FTP server"""
        print(f"\n>>> Starting {self.protocol} downloads...")
        
        for download in downloads:
            try:
                # Extract parameters
                remote_path = download["path"]
                output_dir = Path(download.get("output_dir", self.temp_dir))
                file_name = download["file_name"]
                
                # Create output directory if it doesn't exist
                os.makedirs(output_dir, exist_ok=True)
                
                # Navigate to the specified directory
                print(f">>> Changing to directory: {remote_path}")
                ftp.cwd(remote_path)
                
                # Prepare local file path
                output_file = output_dir / file_name
                
                # Get file size if possible
                try:
                    file_size = ftp.size(file_name)
                    print(f">>> File size: {file_size} bytes")
                except:
                    print(">>> Could not determine file size")
                    
                # Download the file
                print(f">>> Downloading: {file_name} to {output_file}")
                start_time = time.time()
                
                with open(output_file, 'wb') as f:
                    ftp.retrbinary(f"RETR {file_name}", f.write)
                
                # Calculate download statistics
                end_time = time.time()
                download_time = end_time - start_time
                file_size_mb = os.path.getsize(output_file) / (1024 * 1024)
                
                print(f">>> Download completed in {download_time:.2f} seconds")
                print(f">>> Downloaded {file_size_mb:.2f} MB")
                
                if download_time > 0:
                    speed = file_size_mb / download_time
                    print(f">>> Average download speed: {speed:.2f} MB/s")
                    
                # Wait if specified
                if "wait_after" in download:
                    wait_time = download["wait_after"]
                    print(f">>> Waiting {wait_time} seconds before next operation...")
                    time.sleep(wait_time)
                else:
                    # Small default delay
                    time.sleep(random.uniform(1, 3))
                    
            except all_errors as e:
                print(f">>> Error downloading {download.get('file_name')}: {e}")
                continue
            except Exception as e:
                print(f">>> Unexpected error during download: {e}")
                continue
                
    def _upload_files(self, ftp, uploads):
        """Upload files to FTP server"""
        print(f"\n>>> Starting {self.protocol} uploads...")
        
        for upload in uploads:
            try:
                # Extract parameters
                remote_path = upload["path"]
                input_dir = Path(upload.get("input_dir", self.temp_dir))
                file_name = upload["file_name"]
                
                # If the file doesn't exist, create a temporary one for testing
                input_file = input_dir / file_name
                if not os.path.exists(input_file):
                    print(f">>> File {input_file} not found, creating a test file")
                    os.makedirs(input_dir, exist_ok=True)
                    
                    # Create a test file with timestamp and random content
                    with open(input_file, 'w') as f:
                        f.write(f"Test file created on {datetime.now()}\n")
                        f.write(f"This is a test file for FTP upload testing.\n")
                        # Add some random data to make the file bigger
                        for i in range(100):
                            f.write(f"Line {i}: {random.randint(1000, 9999)}\n")
                
                # Navigate to the upload directory
                print(f">>> Changing to directory: {remote_path}")
                ftp.cwd(remote_path)
                
                # Upload the file
                print(f">>> Uploading: {input_file} to {remote_path}/{file_name}")
                start_time = time.time()
                
                with open(input_file, 'rb') as f:
                    ftp.storbinary(f"STOR {file_name}", f)
                
                # Calculate upload statistics
                end_time = time.time()
                upload_time = end_time - start_time
                file_size_mb = os.path.getsize(input_file) / (1024 * 1024)
                
                print(f">>> Upload completed in {upload_time:.2f} seconds")
                print(f">>> Uploaded {file_size_mb:.2f} MB")
                
                if upload_time > 0:
                    speed = file_size_mb / upload_time
                    print(f">>> Average upload speed: {speed:.2f} MB/s")
                
                # Wait if specified
                if "wait_after" in upload:
                    wait_time = upload["wait_after"]
                    print(f">>> Waiting {wait_time} seconds before next operation...")
                    time.sleep(wait_time)
                else:
                    # Small default delay
                    time.sleep(random.uniform(1, 3))
                    
            except all_errors as e:
                print(f">>> Error uploading {upload.get('file_name')}: {e}")
                continue
            except Exception as e:
                print(f">>> Unexpected error during upload: {e}")
                continue
    
    def _simulate_ftp_operations(self):
        """Simulate FTP operations without actually connecting to a server"""
        host = self.model_config["address"]
        port = self.model_config.get("port", 21)
        username = self.model_config["username"]
        
        print(f">>> [SIMULATION] Connecting to {self.protocol} server: {host}:{port}")
        print(f">>> [SIMULATION] Logging in as {username}...")
        print(f">>> [SIMULATION] Successfully logged in")
        print(f">>> [SIMULATION] Server welcome: Welcome to FTP service")
        
        # Simulate browsing if configured
        if "browse" in self.model_config:
            browse_dirs = self.model_config["browse"]
            print(f"\n>>> [SIMULATION] Browsing directories: {browse_dirs}")
            
            for dir_path in browse_dirs:
                print(f">>> [SIMULATION] Changing to directory: {dir_path}")
                print(f">>> [SIMULATION] Listing contents of: {dir_path}")
                
                # Generate random directory listing
                listing_count = random.randint(5, 15)
                print(f">>> [SIMULATION] Directory contains {listing_count} items")
                
                # Show some fake directory items
                for i in range(min(listing_count, 5)):
                    item_type = random.choice(["d", "-"])
                    item_name = random.choice([
                        "documents", "images", "reports", "backup", "data", 
                        "file.txt", "image.jpg", "report.pdf", "data.csv", "config.xml"
                    ])
                    item_size = random.randint(1024, 1024*1024*10)
                    print(f">>> [SIMULATION] {item_type}rw-r--r--  1 user group {item_size:10d} Jan 01 2024 {item_name}")
                
                # Simulate browsing delay
                browse_time = random.uniform(1, 3)
                print(f">>> [SIMULATION] Browsing for {browse_time:.1f} seconds...")
                time.sleep(browse_time)
        
        # Simulate downloads if configured
        if "downloads" in self.model_config:
            downloads = self.model_config["downloads"]
            print(f"\n>>> [SIMULATION] Starting downloads: {len(downloads)} files")
            
            for download in downloads:
                file_name = download["file_name"]
                output_dir = download.get("output_dir", self.temp_dir)
                remote_path = download["path"]
                
                print(f">>> [SIMULATION] Changing to directory: {remote_path}")
                print(f">>> [SIMULATION] Downloading: {file_name} to {output_dir}")
                
                # Simulate file size and download speed
                file_size_mb = random.uniform(0.1, 50)
                download_speed = random.uniform(0.5, 10)  # MB/s
                download_time = file_size_mb / download_speed
                
                print(f">>> [SIMULATION] File size: {file_size_mb:.2f} MB")
                print(f">>> [SIMULATION] Downloading at {download_speed:.2f} MB/s")
                print(f">>> [SIMULATION] Estimated time: {download_time:.2f} seconds")
                
                # Simulate the download time
                time.sleep(min(download_time, 5))  # Cap at 5 seconds for simulation
                
                print(f">>> [SIMULATION] Download completed")
                
                # Wait if specified
                if "wait_after" in download:
                    wait_time = min(download["wait_after"], 3)  # Cap at 3 seconds for simulation
                    print(f">>> [SIMULATION] Waiting {wait_time} seconds...")
                    time.sleep(wait_time)
        
        # Simulate uploads if configured
        if "uploads" in self.model_config:
            uploads = self.model_config["uploads"]
            print(f"\n>>> [SIMULATION] Starting uploads: {len(uploads)} files")
            
            for upload in uploads:
                file_name = upload["file_name"]
                input_dir = upload.get("input_dir", self.temp_dir)
                remote_path = upload["path"]
                
                print(f">>> [SIMULATION] Changing to directory: {remote_path}")
                print(f">>> [SIMULATION] Uploading: {input_dir}/{file_name} to {remote_path}")
                
                # Simulate file size and upload speed
                file_size_mb = random.uniform(0.1, 20)
                upload_speed = random.uniform(0.2, 5)  # MB/s
                upload_time = file_size_mb / upload_speed
                
                print(f">>> [SIMULATION] File size: {file_size_mb:.2f} MB")
                print(f">>> [SIMULATION] Uploading at {upload_speed:.2f} MB/s")
                print(f">>> [SIMULATION] Estimated time: {upload_time:.2f} seconds")
                
                # Simulate the upload time
                time.sleep(min(upload_time, 5))  # Cap at 5 seconds for simulation
                
                print(f">>> [SIMULATION] Upload completed")
                
                # Wait if specified
                if "wait_after" in upload:
                    wait_time = min(upload["wait_after"], 3)  # Cap at 3 seconds for simulation
                    print(f">>> [SIMULATION] Waiting {wait_time} seconds...")
                    time.sleep(wait_time)
        
        print(f"\n>>> [SIMULATION] Closing {self.protocol} connection")
        print(f">>> [SIMULATION] {self.protocol} session completed successfully")
