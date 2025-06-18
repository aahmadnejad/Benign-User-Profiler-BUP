#!/usr/bin/env python3

import platform
import subprocess
import time
import random
import os
from abc import ABC, abstractmethod

class BaseBrowserModule(ABC):
    def __init__(self, headless=False):
        self.headless = headless
        self.os_type = platform.system()
    
    def browser_command(self, url, additional_args=None):
        try:
            print(f">>> Opening {url} in Firefox browser")
            if self.os_type == "Linux":
                if self.headless:
                    print(">>> Using headless mode is not supported with direct browser launch")
                
                cmd = ["firefox", "-new-window", url]
                if additional_args:
                    cmd.extend(additional_args)
                    
                subprocess.Popen(cmd, 
                               stdout=subprocess.DEVNULL, 
                               stderr=subprocess.DEVNULL)
                               
            elif self.os_type == "Darwin":  # macOS
                subprocess.Popen(["open", "-a", "Firefox", url])
                
            elif self.os_type == "Windows":
                cmd = f'start firefox -new-window "{url}"'
                if additional_args:
                    cmd += ' ' + ' '.join(additional_args)
                subprocess.Popen(cmd, shell=True)
                
            else:
                print(f">>> Unsupported platform: {self.os_type}")
                return False
                
            time.sleep(2)
            return True
        except Exception as e:
            print(f">>> Error launching browser: {e}")
            return False
    
    def keyboard_input(self, text):
        try:
            if self.os_type == "Linux":
                try:
                    subprocess.run(["which", "xdotool"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    time.sleep(1)
                    
                    subprocess.run(["xdotool", "type", text])
                    
                    subprocess.run(["xdotool", "key", "Return"])
                    return True
                except subprocess.CalledProcessError:
                    print(">>> xdotool not installed, can't simulate keyboard input")
                    return False
                    
            elif self.os_type == "Windows":
                ps_script = f'''
                Add-Type -AssemblyName System.Windows.Forms
                [System.Windows.Forms.SendKeys]::SendWait("{text}")
                [System.Windows.Forms.SendKeys]::SendWait("{{ENTER}}")
                '''
                subprocess.run(["powershell", "-Command", ps_script], shell=True)
                return True
                
            else:
                print(f">>> Keyboard input not supported on {self.os_type}")
                return False
                
        except Exception as e:
            print(f">>> Error simulating keyboard input: {e}")
            return False
    
    def click(self, x, y):
        try:
            if self.os_type == "Linux":
                subprocess.run(["xdotool", "mousemove", str(x), str(y), "click", "1"], 
                            check=False,
                            stdout=subprocess.DEVNULL, 
                            stderr=subprocess.DEVNULL)
            elif self.os_type == "Windows":
                ps_script = f'''
                Add-Type -AssemblyName System.Windows.Forms
                [System.Windows.Forms.Cursor]::Position = New-Object System.Drawing.Point({x}, {y})
                [System.Windows.Forms.MouseButtons]::Click("Left")
                '''
                subprocess.run(["powershell", "-Command", ps_script], 
                            shell=True,
                            stdout=subprocess.DEVNULL, 
                            stderr=subprocess.DEVNULL)
            return True
        except Exception as e:
            print(f">>> Error clicking: {e}")
            return False
    
    def right_click(self, x, y):
        try:
            if self.os_type == "Linux":
                subprocess.run(["xdotool", "mousemove", str(x), str(y), "click", "3"], 
                            check=False,
                            stdout=subprocess.DEVNULL, 
                            stderr=subprocess.DEVNULL)
            elif self.os_type == "Windows":
                ps_script = f'''
                Add-Type -AssemblyName System.Windows.Forms
                [System.Windows.Forms.Cursor]::Position = New-Object System.Drawing.Point({x}, {y})
                [System.Windows.Forms.MouseButtons]::Click("Right")
                '''
                subprocess.run(["powershell", "-Command", ps_script], 
                            shell=True,
                            stdout=subprocess.DEVNULL, 
                            stderr=subprocess.DEVNULL)
            return True
        except Exception as e:
            print(f">>> Error right-clicking: {e}")
            return False
    
    def press_key(self, key):
        try:
            if self.os_type == "Linux":
                subprocess.run(["xdotool", "key", key], 
                            check=False,
                            stdout=subprocess.DEVNULL, 
                            stderr=subprocess.DEVNULL)
            elif self.os_type == "Windows":
                ps_script = f'''
                Add-Type -AssemblyName System.Windows.Forms
                [System.Windows.Forms.SendKeys]::SendWait("{key}")
                '''
                subprocess.run(["powershell", "-Command", ps_script], 
                            shell=True,
                            stdout=subprocess.DEVNULL, 
                            stderr=subprocess.DEVNULL)
            return True
        except Exception as e:
            print(f">>> Error pressing key: {e}")
            return False
    
    def scroll_down(self, count=1):
        for _ in range(count):
            if self.os_type == "Linux":
                try:
                    subprocess.run(["xdotool", "key", "Page_Down"], 
                                check=False,
                                stdout=subprocess.DEVNULL, 
                                stderr=subprocess.DEVNULL)
                except:
                    pass
            elif self.os_type == "Windows":
                ps_script = '''
                Add-Type -AssemblyName System.Windows.Forms
                [System.Windows.Forms.SendKeys]::SendWait("{PGDN}")
                '''
                subprocess.run(["powershell", "-Command", ps_script], 
                            shell=True,
                            stdout=subprocess.DEVNULL, 
                            stderr=subprocess.DEVNULL)
            
            time.sleep(random.uniform(2, 5))
    
    def close_browser(self):
        try:
            if self.os_type == "Linux":
                try:
                    subprocess.run(["xdotool", "key", "alt+F4"], 
                                check=False,
                                stdout=subprocess.DEVNULL, 
                                stderr=subprocess.DEVNULL)
                    time.sleep(1)
                    
                    subprocess.run(["killall", "firefox"], 
                                check=False,
                                stdout=subprocess.DEVNULL, 
                                stderr=subprocess.DEVNULL)
                    
                    print(">>> Closed Firefox")
                except Exception as e:
                    print(f">>> Error closing Firefox: {e}")
            elif self.os_type == "Windows":
                ps_script = '''
                Add-Type -AssemblyName System.Windows.Forms
                [System.Windows.Forms.SendKeys]::SendWait("%{F4}")
                Start-Sleep -Seconds 1
                '''
                subprocess.run(["powershell", "-Command", ps_script], 
                            shell=True,
                            stdout=subprocess.DEVNULL, 
                            stderr=subprocess.DEVNULL)
                
                try:
                    subprocess.run(["taskkill", "/F", "/IM", "firefox.exe"],
                                check=False,
                                stdout=subprocess.DEVNULL, 
                                stderr=subprocess.DEVNULL)
                    print(">>> Firefox force closed with taskkill")
                except Exception as e:
                    print(f">>> Error killing Firefox: {e}")
        except:
            pass
    
    @abstractmethod
    def execute(self, config):
        pass