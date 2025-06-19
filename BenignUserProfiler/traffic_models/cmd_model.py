#!/usr/bin/env python3

import os
import time
import random
import platform
import subprocess
import string
from datetime import datetime
from .traffic_model import TrafficModel


class CMDModel(TrafficModel):
    def __str__(self):
        return "CMD"

    def verify(self) -> bool:
        if ("commands" not in self.model_config and 
            "applications" not in self.model_config and
            "linux_apps" not in self.model_config and
            "windows_apps" not in self.model_config and
            "windows_commands" not in self.model_config and
            "linux_commands" not in self.model_config):
            print(">>> Error in CMD model: No commands or applications specified in the config!")
            return False
        return True

    def generate(self) -> None:
        # Execute commands if specified
        if "commands" in self.model_config:
            self._execute_commands()
            
        # Open applications if specified
        if "applications" in self.model_config:
            self._open_applications()
            
        # Open random applications if specified
        if "linux_apps" in self.model_config or "windows_apps" in self.model_config:
            self._open_random_apps()
            
        # Execute platform-specific commands if specified
        system = platform.system().lower()
        if system == "windows" and "windows_commands" in self.model_config:
            self._execute_commands(command_key="windows_commands")
            
        if system == "linux" and "linux_commands" in self.model_config:
            self._execute_commands(command_key="linux_commands")
            
        # Create and save Office documents if needed
        if self.model_config.get("create_office_docs", False):
            self._create_office_documents()

    def _execute_commands(self, command_key="commands"):
        """Execute shell commands"""
        system = platform.system().lower()
        shell = system != "windows"  # True for Linux/Mac, False for Windows
        
        # Skip if no commands for this key
        if command_key not in self.model_config:
            return
        
        for cmd_config in self.model_config[command_key]:
            # Legacy support for simple command format
            if isinstance(cmd_config, dict) and "str" in cmd_config:
                command = cmd_config["str"]
                wait_after = cmd_config.get("wait_after", 0)
            # New format with more options
            elif isinstance(cmd_config, dict) and "command" in cmd_config:
                command = cmd_config["command"]
                wait_after = cmd_config.get("wait_after", 0)
                
                # Check for use_time parameter (for office apps)
                if "use_time" in cmd_config:
                    use_time_range = cmd_config["use_time"]
                    if isinstance(use_time_range, list) and len(use_time_range) == 2:
                        wait_after = random.uniform(use_time_range[0], use_time_range[1])
            else:
                # Simple string command
                command = cmd_config
                wait_after = 0
            
            # Check if command is platform-specific
            if isinstance(cmd_config, dict) and "platform" in cmd_config:
                platforms = cmd_config["platform"] if isinstance(cmd_config["platform"], list) else [cmd_config["platform"]]
                
                # Skip if command is not for current platform
                if system not in map(str.lower, platforms) and "all" not in map(str.lower, platforms):
                    print(f">>> Skipping command '{command}': not for {system} platform")
                    continue
            
            try:
                # Print command description if available
                if isinstance(cmd_config, dict) and "description" in cmd_config:
                    print(f">>> {cmd_config['description']}")
                else:
                    print(f">>> Executing command: {command}")
                
                # Execute the command
                if isinstance(cmd_config, dict) and "show_output" in cmd_config and cmd_config["show_output"]:
                    # Run command and capture output
                    result = subprocess.run(
                        command,
                        shell=shell,
                        capture_output=True,
                        text=True
                    )
                    
                    # Print output if requested
                    if result.stdout:
                        print("Command output:")
                        print(result.stdout[:500] + ("..." if len(result.stdout) > 500 else ""))
                    
                    if result.stderr:
                        print("Command error:")
                        print(result.stderr[:500] + ("..." if len(result.stderr) > 500 else ""))
                else:
                    # Run command without capturing output
                    subprocess.run(
                        command,
                        shell=shell,
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL
                    )
                
            except Exception as e:
                print(f">>> Error executing command '{command}':")
                print(e)
                continue
                
            # Delay after command if specified
            if wait_after > 0:
                print(f">>> Waiting for {wait_after:.1f} seconds")
                time.sleep(wait_after)
            else:
                # Small random delay between commands
                time.sleep(random.uniform(0.5, 2))

    def _open_applications(self):
        """Open applications on the system"""
        system = platform.system().lower()
        
        for app_config in self.model_config["applications"]:
            # Check if app is platform-specific
            if "platform" in app_config:
                platforms = app_config["platform"] if isinstance(app_config["platform"], list) else [app_config["platform"]]
                
                # Skip if app is not for current platform
                if system not in map(str.lower, platforms) and "all" not in map(str.lower, platforms):
                    print(f">>> Skipping app '{app_config['name']}': not for {system} platform")
                    continue
            
            try:
                app_name = app_config["name"]
                print(f">>> Opening application: {app_name}")
                
                # Platform-specific app launching
                if system == "windows":
                    # Use start command on Windows
                    if "path" in app_config:
                        subprocess.Popen(f'start "" "{app_config["path"]}"', shell=True)
                    else:
                        subprocess.Popen(f'start "" "{app_name}"', shell=True)
                        
                elif system == "darwin":  # macOS
                    # Use open command on macOS
                    if "path" in app_config:
                        subprocess.Popen(["open", app_config["path"]])
                    else:
                        subprocess.Popen(["open", "-a", app_name])
                        
                elif system == "linux":
                    # Use xdg-open on Linux, or direct command
                    if "path" in app_config:
                        subprocess.Popen([app_config["path"]], 
                                        stdout=subprocess.DEVNULL, 
                                        stderr=subprocess.DEVNULL)
                    else:
                        # Try with direct command first
                        try:
                            subprocess.Popen([app_name], 
                                            stdout=subprocess.DEVNULL, 
                                            stderr=subprocess.DEVNULL)
                        except:
                            # Fallback to xdg-open if available
                            try:
                                subprocess.Popen(["xdg-open", app_name], 
                                                stdout=subprocess.DEVNULL, 
                                                stderr=subprocess.DEVNULL)
                            except Exception as e:
                                print(f">>> Failed to open {app_name}: {e}")
                
            except Exception as e:
                print(f">>> Error opening application '{app_name}':")
                print(e)
                continue
                
            # Application interaction if specified
            if "interactions" in app_config:
                # Wait for app to open
                time.sleep(app_config.get("startup_delay", 3))
                
                # Perform each interaction
                for interaction in app_config["interactions"]:
                    try:
                        if interaction["type"] == "keystrokes" and "keys" in interaction:
                            # Simulate keystrokes - this would require platform-specific implementations
                            # For a simple PoC, we just print what would happen
                            print(f">>> Would simulate keystrokes: {interaction['keys']}")
                            
                        elif interaction["type"] == "wait":
                            # Wait for specified duration
                            duration = interaction.get("duration", 2)
                            print(f">>> Waiting for {duration} seconds")
                            time.sleep(duration)
                            
                    except Exception as e:
                        print(f">>> Error during app interaction: {e}")
                        continue
            
            # Keep app open for specified duration
            app_runtime = app_config.get("runtime", 10)
            print(f">>> Keeping {app_name} open for {app_runtime} seconds")

            
            # Close app if specified
            if app_config.get("close_after", True):
                print(f">>> Closing {app_name}")
                self._close_application(app_name, system)
                
    def _close_application(self, app_name, system):
        """Close an application using platform-specific methods"""
        try:
            if system == "windows":
                # Use taskkill on Windows
                app_exe = app_name if app_name.lower().endswith(".exe") else f"{app_name}.exe"
                subprocess.run(
                    f'taskkill /F /IM "{app_exe}"',
                    shell=True,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
            elif system == "linux":
                print(f">>> Closing Linux application: {app_name}")
                # Try multiple approaches to ensure application is closed
                try:
                    # Method 1: Use killall
                    print(f">>> Attempting to close {app_name} with killall")
                    subprocess.run(
                        ["killall", "-9", app_name],
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL
                    )
                except Exception as e:
                    print(f">>> killall failed: {e}")
                
                try:
                    # Method 2: Use pkill (more flexible than killall)
                    print(f">>> Attempting to close {app_name} with pkill")
                    subprocess.run(
                        ["pkill", "-9", "-f", app_name],
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL
                    )
                except Exception as e:
                    print(f">>> pkill failed: {e}")
                    
                # Method 3: If we saved the PID earlier, we could kill by PID
                # But we'll skip that as we don't have a PID tracking system currently
                
                print(f">>> Cleanup complete for {app_name}")
            # Wait a moment for the app to close
            time.sleep(1)
        except Exception as e:
            print(f">>> Error closing application {app_name}: {e}")
    
    def _open_random_apps(self):
        """Open a random selection of applications from the configured list"""
        system = platform.system().lower()
        
        # Determine which app list to use based on platform
        if system == "windows" and "windows_apps" in self.model_config:
            app_list = self.model_config["windows_apps"]
        elif system == "linux" and "linux_apps" in self.model_config:
            app_list = self.model_config["linux_apps"]
        else:
            print(f">>> No app list found for platform: {system}")
            return
        
        # Determine how many apps to open
        min_apps = self.model_config.get("min_apps_to_open", 1)
        max_apps = self.model_config.get("max_apps_to_open", 3)
        num_apps = random.randint(min_apps, min(max_apps, len(app_list)))
        
        # Get runtime range with more randomness
        # Using a wider range for more realistic and varied behavior
        min_time = self.model_config.get("app_use_time_min", 10)
        max_time = self.model_config.get("app_use_time_max", 60)
        
        # Shuffle the entire app list first to ensure better distribution
        shuffled_apps = app_list.copy()
        random.shuffle(shuffled_apps)
        
        # Select a subset of apps from the shuffled list
        selected_apps = shuffled_apps[:num_apps]
        
        # Further randomize by occasionally swapping the order
        if random.random() < 0.5:
            random.shuffle(selected_apps)
            
        print(f">>> Opening {num_apps} random applications: {', '.join(selected_apps)}")
        
        for app_name in selected_apps:
            try:
                print(f">>> Opening application: {app_name}")
                
                # Platform-specific app launching
                if system == "windows":
                    # Use start command on Windows
                    subprocess.Popen(f'start "" "{app_name}"', shell=True)
                elif system == "linux":
                    # Use direct command on Linux with nohup to prevent hanging
                    try:
                        # Add nohup to prevent script from waiting for application to close
                        # start-stop-daemon can also be used as an alternative
                        command = f"nohup {app_name} > /dev/null 2>&1 & echo $!"
                        print(f">>> Running command: {command}")
                        
                        # Use shell=True to allow nohup and redirection
                        process = subprocess.Popen(
                            command,
                            shell=True,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE,
                            text=True
                        )
                        
                        # Get the PID (not waiting for completion)
                        output, error = process.communicate(timeout=2)
                        if output:
                            pid = output.strip()
                            print(f">>> Started {app_name} with PID {pid}")
                        if error:
                            print(f">>> Error starting {app_name}: {error}")
                            
                    except subprocess.TimeoutExpired:
                        # If communication times out, process is still running
                        print(f">>> {app_name} started (timeout on PID retrieval)")
                    except Exception as e:
                        # Fallback to xdg-open if direct launch fails
                        print(f">>> Direct launch failed: {e}, trying xdg-open")
                        try:
                            # Use xdg-open with nohup
                            subprocess.Popen(
                                f"nohup xdg-open {app_name} > /dev/null 2>&1 &", 
                                shell=True,
                                stdout=subprocess.DEVNULL, 
                                stderr=subprocess.DEVNULL
                            )
                            print(f">>> Launched {app_name} using xdg-open")
                        except Exception as e2:
                            print(f">>> Failed to open {app_name}: {e2}")
                
                # Wait a moment for app to launch
                time.sleep(random.uniform(2, 5))
                
                # Random interaction - simulate keystrokes (platform-specific)
                if random.random() < 0.7:  # 70% chance of interaction
                    self._simulate_keyboard_input(system)
                
                # Keep app open for random duration with countdown for problematic apps
                runtime = random.uniform(min_time, max_time)
                
                # For LibreOffice on Linux, show a countdown to help with dialog prompts
                if system == "linux" and "libreoffice" in app_name.lower():
                    print(f">>> LibreOffice detected - showing countdown before closing")
                    countdown_interval = 5
                    total_time = 0
                    while total_time < runtime:
                        time_left = runtime - total_time
                        if time_left <= countdown_interval:
                            print(f">>> Closing {app_name} in {time_left:.1f} seconds...")
                            time.sleep(time_left)
                            total_time += time_left
                        else:
                            print(f">>> Keeping {app_name} open - {time_left:.1f} seconds remaining")
                            time.sleep(countdown_interval)
                            total_time += countdown_interval
                # For Windows, always use a countdown approach
                elif system == "windows":
                    print(f">>> Windows app - showing countdown before closing")
                    countdown_interval = 10
                    total_time = 0
                    while total_time < runtime:
                        time_left = runtime - total_time
                        if time_left <= countdown_interval:
                            print(f">>> Closing {app_name} in {time_left:.1f} seconds...")
                            time.sleep(time_left)
                            total_time += time_left
                        else:
                            print(f">>> Keeping {app_name} open - {time_left:.1f} seconds remaining")
                            time.sleep(countdown_interval)
                            total_time += countdown_interval
                else:
                    # For other apps, just use a simple wait
                    print(f">>> Keeping {app_name} open for {runtime:.1f} seconds")
                    time.sleep(runtime)
                
                # Close the app
                self._close_application(app_name, system)
                
            except Exception as e:
                print(f">>> Error with application '{app_name}':")
                print(e)
                continue
            
            # Delay between apps
            time.sleep(random.uniform(5, 15))
    
    def _simulate_keyboard_input(self, system):
        """Simulate random keyboard input based on platform"""
        try:
            # Random number of keystrokes
            num_keystrokes = random.randint(10, 50)
            print(f">>> Simulating {num_keystrokes} random keystrokes")
            
            if system == "linux":
                # On Linux, use xdotool if available
                try:
                    # Generate random text
                    random_text = ''.join(random.choices(
                        string.ascii_letters + string.digits + ' .,-', 
                        k=num_keystrokes
                    ))
                    
                    # Use xdotool to type
                    subprocess.run(
                        ["xdotool", "type", random_text],
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL
                    )
                except:
                    print(">>> Keyboard simulation requires xdotool on Linux")
            
            elif system == "windows":
                # On Windows, we'll use PowerShell with SendKeys
                random_text = ''.join(random.choices(
                    string.ascii_letters + string.digits + ' .,-', 
                    k=num_keystrokes
                ))
                
                ps_script = f"""
                Add-Type -AssemblyName System.Windows.Forms
                [System.Windows.Forms.SendKeys]::SendWait('{random_text}')
                """
                
                subprocess.run(
                    ["powershell", "-Command", ps_script],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
            
            # Wait after typing
            time.sleep(random.uniform(1, 3))
            
        except Exception as e:
            print(f">>> Error simulating keyboard input: {e}")
    
    def _create_office_documents(self):
        """Create Office documents and save them for email attachments"""
        try:
            # Create output directory if it doesn't exist
            output_dir = os.path.expanduser("~/output-benign/email_attachments")
            os.makedirs(output_dir, exist_ok=True)
            
            # Choose which document type to create
            doc_type = random.choice(["word", "excel", "powerpoint"])
            
            # Generate a filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # Check system
            system = platform.system().lower()
            
            if system == "windows":
                # Use Microsoft Office on Windows
                if doc_type == "word":
                    self._create_word_document(output_dir, timestamp)
                elif doc_type == "excel":
                    self._create_excel_document(output_dir, timestamp)
                elif doc_type == "powerpoint":
                    self._create_powerpoint_document(output_dir, timestamp)
            elif system == "linux":
                # Use LibreOffice on Linux
                self._create_libreoffice_document(output_dir, timestamp, doc_type)
            else:
                print(f">>> Office document creation not implemented for {system}")
                
        except Exception as e:
            print(f">>> Error creating Office document: {e}")
    
    def _create_word_document(self, output_dir, timestamp):
        """Create a Microsoft Word document with PowerShell"""
        filename = f"Document_{timestamp}.docx"
        file_path = os.path.join(output_dir, filename)
        
        # Generate random content
        lorem_text = "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur."
        paragraphs = random.randint(3, 7)
        content = "\n\n".join([lorem_text for _ in range(paragraphs)])
        
        print(f">>> Creating Word document: {filename}")
        
        # PowerShell script to create Word document
        ps_script = f"""
        $word = New-Object -ComObject Word.Application
        $word.Visible = $false
        $doc = $word.Documents.Add()
        $selection = $word.Selection
        $selection.TypeText("{content}")
        $doc.SaveAs("{file_path}")
        $doc.Close()
        $word.Quit()
        [System.Runtime.Interopservices.Marshal]::ReleaseComObject($word)
        """
        
        # Run PowerShell script
        subprocess.run(
            ["powershell", "-Command", ps_script],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        
        print(f">>> Word document saved to: {file_path}")
        
    def _create_excel_document(self, output_dir, timestamp):
        """Create a Microsoft Excel document with PowerShell"""
        filename = f"Spreadsheet_{timestamp}.xlsx"
        file_path = os.path.join(output_dir, filename)
        
        print(f">>> Creating Excel document: {filename}")
        
        # PowerShell script to create Excel document
        ps_script = f"""
        $excel = New-Object -ComObject Excel.Application
        $excel.Visible = $false
        $workbook = $excel.Workbooks.Add()
        $worksheet = $workbook.Worksheets.Item(1)
        
        # Add headers
        $worksheet.Cells.Item(1, 1) = "Date"
        $worksheet.Cells.Item(1, 2) = "Description"
        $worksheet.Cells.Item(1, 3) = "Amount"
        
        # Add some random data
        for ($i = 2; $i -le 10; $i++) {{
            $worksheet.Cells.Item($i, 1) = Get-Date -Format "yyyy-MM-dd"
            $worksheet.Cells.Item($i, 2) = "Item " + ($i - 1)
            $worksheet.Cells.Item($i, 3) = [math]::Round((Get-Random -Minimum 10 -Maximum 500), 2)
        }}
        
        $workbook.SaveAs("{file_path}")
        $workbook.Close()
        $excel.Quit()
        [System.Runtime.Interopservices.Marshal]::ReleaseComObject($excel)
        """
        
        # Run PowerShell script
        subprocess.run(
            ["powershell", "-Command", ps_script],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        
        print(f">>> Excel document saved to: {file_path}")
        
    def _create_powerpoint_document(self, output_dir, timestamp):
        """Create a Microsoft PowerPoint document with PowerShell"""
        filename = f"Presentation_{timestamp}.pptx"
        file_path = os.path.join(output_dir, filename)
        
        print(f">>> Creating PowerPoint document: {filename}")
        
        # PowerShell script to create PowerPoint document
        ps_script = f"""
        $ppt = New-Object -ComObject PowerPoint.Application
        $ppt.Visible = [Microsoft.Office.Core.MsoTriState]::msoTrue
        $presentation = $ppt.Presentations.Add()
        
        # Add title slide
        $slide1 = $presentation.Slides.Add(1, 1) # 1 = position, 1 = layout (title slide)
        $slide1.Shapes.Title.TextFrame.TextRange.Text = "Presentation Title"
        $slide1.Shapes.Item(2).TextFrame.TextRange.Text = "Created on {datetime.now().strftime('%Y-%m-%d')}"
        
        # Add content slide
        $slide2 = $presentation.Slides.Add(2, 2) # 2 = position, 2 = layout (title and content)
        $slide2.Shapes.Title.TextFrame.TextRange.Text = "Content Slide"
        $textFrame = $slide2.Shapes.Item(2).TextFrame
        $textRange = $textFrame.TextRange
        $textRange.Text = "• First bullet point`n• Second bullet point`n• Third bullet point"
        
        $presentation.SaveAs("{file_path}")
        $presentation.Close()
        $ppt.Quit()
        [System.Runtime.Interopservices.Marshal]::ReleaseComObject($ppt)
        """
        
        # Run PowerShell script
        subprocess.run(
            ["powershell", "-Command", ps_script],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        
        print(f">>> PowerPoint document saved to: {file_path}")

    def _create_libreoffice_document(self, output_dir, timestamp, doc_type):
        """Create a document using LibreOffice on Linux"""
        # Determine file extension and app based on document type
        if doc_type == "word":
            extension = "odt"
            libreoffice_app = "--writer"
            file_type = "Writer document"
        elif doc_type == "excel":
            extension = "ods"
            libreoffice_app = "--calc"
            file_type = "Calc spreadsheet"
        elif doc_type == "powerpoint":
            extension = "odp"
            libreoffice_app = "--impress"
            file_type = "Impress presentation"
        else:
            extension = "odt"
            libreoffice_app = "--writer"
            file_type = "document"
            
        filename = f"Document_{timestamp}.{extension}"
        file_path = os.path.join(output_dir, filename)
        
        print(f">>> Creating LibreOffice {file_type}: {filename}")
        
        try:
            # Create a temporary content file for LibreOffice
            temp_content_file = os.path.join(output_dir, f"temp_content_{timestamp}.txt")
            
            # Generate random content - simulate using a Lorem Ipsum API
            paragraphs = random.randint(3, 7)
            lorem_text = self._get_lorem_ipsum(paragraphs)
            
            # Write content to temporary file
            with open(temp_content_file, 'w') as f:
                f.write(lorem_text)
            
            # Launch LibreOffice and create document
            if doc_type == "word":
                # For Writer document - create a simple text file first
                with open(file_path, 'w') as f:
                    f.write(lorem_text)
                    
                # Try to convert it to proper format if possible
                try:
                    # Start LibreOffice with a timeout and terminate it afterward
                    print(f">>> Starting LibreOffice {libreoffice_app} with 15 second timeout")
                    
                    # Launch process
                    process = subprocess.Popen([
                        "libreoffice", libreoffice_app,
                        "--convert-to", extension, 
                        file_path, 
                        "--outdir", output_dir
                    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    
                    # Set up a timer to kill the process after timeout
                    import threading
                    def kill_libreoffice():
                        try:
                            if process.poll() is None:  # If process is still running
                                print(f">>> LibreOffice process taking too long, terminating...")
                                process.terminate()
                                time.sleep(1)
                                # Force kill if it's still running
                                if process.poll() is None:
                                    process.kill()
                                    
                            # Also kill any other LibreOffice processes that might be hanging
                            subprocess.run(["killall", "-9", "soffice.bin", "libreoffice"], 
                                        check=False,
                                        stdout=subprocess.DEVNULL, 
                                        stderr=subprocess.DEVNULL)
                        except Exception as kill_error:
                            print(f">>> Error while killing LibreOffice: {kill_error}")
                    
                    # Start timer
                    timer = threading.Timer(15, kill_libreoffice)
                    timer.daemon = True
                    timer.start()
                    
                    # Wait for process to complete or be killed
                    try:
                        process.wait(timeout=20)  # Wait with longer timeout
                    except subprocess.TimeoutExpired:
                        print(">>> Process wait timeout, assuming LibreOffice is stuck")
                        kill_libreoffice()
                    
                    # Cancel timer if it's still active
                    timer.cancel()
                    
                except Exception as e:
                    print(f">>> Could not convert to {extension}, keeping text file: {e}")
                    # Make sure to kill any hanging LibreOffice processes
                    subprocess.run(["killall", "-9", "soffice.bin", "libreoffice"], 
                                check=False,
                                stdout=subprocess.DEVNULL, 
                                stderr=subprocess.DEVNULL)
                
            elif doc_type == "excel":
                # For Calc - create a simple CSV file with some data
                with open(file_path, 'w') as f:
                    # Write CSV header
                    f.write("Date,Description,Amount\n")
                    # Write some rows
                    for i in range(1, 11):
                        date = datetime.now().strftime("%Y-%m-%d")
                        description = f"Item {i}"
                        amount = round(random.uniform(10, 500), 2)
                        f.write(f"{date},{description},{amount}\n")
                        
                # Try to convert to spreadsheet format if possible
                try:
                    # Start LibreOffice with a timeout and terminate it afterward
                    print(f">>> Starting LibreOffice {libreoffice_app} with 15 second timeout")
                    
                    # Launch process
                    process = subprocess.Popen([
                        "libreoffice", libreoffice_app,
                        "--convert-to", extension, 
                        file_path, 
                        "--outdir", output_dir
                    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    
                    # Set up a timer to kill the process after timeout
                    import threading
                    def kill_libreoffice():
                        try:
                            if process.poll() is None:  # If process is still running
                                print(f">>> LibreOffice process taking too long, terminating...")
                                process.terminate()
                                time.sleep(1)
                                # Force kill if it's still running
                                if process.poll() is None:
                                    process.kill()
                                    
                            # Also kill any other LibreOffice processes that might be hanging
                            subprocess.run(["killall", "-9", "soffice.bin", "libreoffice"], 
                                        check=False,
                                        stdout=subprocess.DEVNULL, 
                                        stderr=subprocess.DEVNULL)
                        except Exception as kill_error:
                            print(f">>> Error while killing LibreOffice: {kill_error}")
                    
                    # Start timer
                    timer = threading.Timer(15, kill_libreoffice)
                    timer.daemon = True
                    timer.start()
                    
                    # Wait for process to complete or be killed
                    try:
                        process.wait(timeout=20)  # Wait with longer timeout
                    except subprocess.TimeoutExpired:
                        print(">>> Process wait timeout, assuming LibreOffice is stuck")
                        kill_libreoffice()
                    
                    # Cancel timer if it's still active
                    timer.cancel()
                    
                except Exception as e:
                    print(f">>> Could not convert to {extension}, keeping CSV file: {e}")
                    # Make sure to kill any hanging LibreOffice processes
                    subprocess.run(["killall", "-9", "soffice.bin", "libreoffice"], 
                                check=False,
                                stdout=subprocess.DEVNULL, 
                                stderr=subprocess.DEVNULL)
                
            elif doc_type == "powerpoint":
                # For Impress - create a simple text file with presentation structure
                with open(file_path, 'w') as f:
                    f.write("PRESENTATION TITLE\n\n")
                    f.write(f"Created on {datetime.now().strftime('%Y-%m-%d')}\n\n")
                    f.write("SLIDE 1: Introduction\n\n")
                    f.write(lorem_text[:200] + "\n\n")
                    f.write("SLIDE 2: Main Points\n\n")
                    f.write("• First bullet point\n")
                    f.write("• Second bullet point\n")
                    f.write("• Third bullet point\n\n")
                    f.write("SLIDE 3: Conclusion\n\n")
                    f.write(lorem_text[-200:])
                    
                # Try to convert to presentation format if possible
                try:
                    # Start LibreOffice with a timeout and terminate it afterward
                    print(f">>> Starting LibreOffice {libreoffice_app} with 15 second timeout")
                    
                    # Launch process
                    process = subprocess.Popen([
                        "libreoffice", libreoffice_app,
                        "--convert-to", extension, 
                        file_path, 
                        "--outdir", output_dir
                    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    
                    # Set up a timer to kill the process after timeout
                    import threading
                    def kill_libreoffice():
                        try:
                            if process.poll() is None:  # If process is still running
                                print(f">>> LibreOffice process taking too long, terminating...")
                                process.terminate()
                                time.sleep(1)
                                # Force kill if it's still running
                                if process.poll() is None:
                                    process.kill()
                                    
                            # Also kill any other LibreOffice processes that might be hanging
                            subprocess.run(["killall", "-9", "soffice.bin", "libreoffice"], 
                                        check=False,
                                        stdout=subprocess.DEVNULL, 
                                        stderr=subprocess.DEVNULL)
                        except Exception as kill_error:
                            print(f">>> Error while killing LibreOffice: {kill_error}")
                    
                    # Start timer
                    timer = threading.Timer(15, kill_libreoffice)
                    timer.daemon = True
                    timer.start()
                    
                    # Wait for process to complete or be killed
                    try:
                        process.wait(timeout=20)  # Wait with longer timeout
                    except subprocess.TimeoutExpired:
                        print(">>> Process wait timeout, assuming LibreOffice is stuck")
                        kill_libreoffice()
                    
                    # Cancel timer if it's still active
                    timer.cancel()
                    
                except Exception as e:
                    print(f">>> Could not convert to {extension}, keeping text file: {e}")
                    # Make sure to kill any hanging LibreOffice processes
                    subprocess.run(["killall", "-9", "soffice.bin", "libreoffice"], 
                                check=False,
                                stdout=subprocess.DEVNULL, 
                                stderr=subprocess.DEVNULL)
            
            # Remove temporary file
            if os.path.exists(temp_content_file):
                os.remove(temp_content_file)
                
            print(f">>> LibreOffice {file_type} saved to: {file_path}")
            
        except Exception as e:
            print(f">>> Error creating LibreOffice document: {e}")
            
    def _get_lorem_ipsum(self, paragraphs):
        """Generate Lorem Ipsum text for document content"""
        # Static Lorem Ipsum content (fallback)
        static_lorem = [
            "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.",
            "Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.",
            "Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur.",
            "Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.",
            "Sed ut perspiciatis unde omnis iste natus error sit voluptatem accusantium doloremque laudantium.",
            "Nemo enim ipsam voluptatem quia voluptas sit aspernatur aut odit aut fugit, sed quia consequuntur.",
            "Neque porro quisquam est, qui dolorem ipsum quia dolor sit amet, consectetur, adipisci velit.",
        ]
        
        # Get random paragraphs
        selected_paragraphs = random.sample(static_lorem, min(paragraphs, len(static_lorem)))
        
        # Return paragraphs with blank lines between them
        return "\n\n".join(selected_paragraphs)