#!/usr/bin/env python3

import os
import time
import random
import platform
import subprocess
from .traffic_model import TrafficModel


class CMDModel(TrafficModel):
    def __str__(self):
        return "CMD"

    def verify(self) -> bool:
        if "commands" not in self.model_config and "applications" not in self.model_config:
            print(">>> Error in CMD model: Neither 'commands' nor 'applications' specified in the config!")
            return False
        return True

    def generate(self) -> None:
        # Execute commands if specified
        if "commands" in self.model_config:
            self._execute_commands()
            
        # Open applications if specified
        if "applications" in self.model_config:
            self._open_applications()

    def _execute_commands(self):
        """Execute shell commands"""
        system = platform.system().lower()
        shell = system != "windows"  # True for Linux/Mac, False for Windows
        
        for cmd_config in self.model_config["commands"]:
            # Legacy support for simple command format
            if isinstance(cmd_config, dict) and "str" in cmd_config:
                command = cmd_config["str"]
                wait_after = cmd_config.get("wait_after", 0)
            # New format with more options
            elif isinstance(cmd_config, dict) and "command" in cmd_config:
                command = cmd_config["command"]
                wait_after = cmd_config.get("wait_after", 0)
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
            time.sleep(app_runtime)
            
            # Close app if specified
            if app_config.get("close_after", True):
                print(f">>> Closing {app_name}")
                # Platform-specific app closing - for demo we just mention it
                # In reality, this would require process tracking and termination