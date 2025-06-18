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
                $mouse = New-Object System.Windows.Forms.MouseButtons
                $mouse_event = [System.Runtime.InteropServices.RuntimeInformation]::IsOSPlatform([System.Runtime.InteropServices.OSPlatform]::Windows)
                [System.Windows.Forms.Application]::DoEvents()
                
                # Simulate mouse down and up events
                $signature = @'
                [DllImport("user32.dll",CharSet=CharSet.Auto, CallingConvention=CallingConvention.StdCall)]
                public static extern void mouse_event(uint dwFlags, uint dx, uint dy, uint cButtons, uint dwExtraInfo);
                '@
                $SendMouseClick = Add-Type -memberDefinition $signature -name "Win32MouseEventNew" -namespace Win32Functions -passThru
                
                # Left mouse button down and up
                $SendMouseClick::mouse_event(0x00000002, 0, 0, 0, 0) # MOUSEEVENTF_LEFTDOWN
                Start-Sleep -Milliseconds 10
                $SendMouseClick::mouse_event(0x00000004, 0, 0, 0, 0) # MOUSEEVENTF_LEFTUP
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
                [System.Windows.Forms.Application]::DoEvents()
                
                # Simulate mouse down and up events
                $signature = @'
                [DllImport("user32.dll",CharSet=CharSet.Auto, CallingConvention=CallingConvention.StdCall)]
                public static extern void mouse_event(uint dwFlags, uint dx, uint dy, uint cButtons, uint dwExtraInfo);
                '@
                $SendMouseClick = Add-Type -memberDefinition $signature -name "Win32MouseEventRight" -namespace Win32Functions -passThru
                
                # Right mouse button down and up
                $SendMouseClick::mouse_event(0x00000008, 0, 0, 0, 0) # MOUSEEVENTF_RIGHTDOWN
                Start-Sleep -Milliseconds 10
                $SendMouseClick::mouse_event(0x00000010, 0, 0, 0, 0) # MOUSEEVENTF_RIGHTUP
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
                # Map common key names to SendKeys format
                key_mapping = {
                    "Return": "{ENTER}",
                    "Escape": "{ESC}",
                    "Page_Down": "{PGDN}",
                    "Page_Up": "{PGUP}",
                    "Right": "{RIGHT}",
                    "Left": "{LEFT}",
                    "Up": "{UP}",
                    "Down": "{DOWN}",
                    "space": " ",
                    "alt+Left": "%{LEFT}",
                    "alt+F4": "%{F4}"
                }
                
                # Convert key to SendKeys format if it's in our mapping
                send_key = key_mapping.get(key, key)
                
                ps_script = f'''
                Add-Type -AssemblyName System.Windows.Forms
                [System.Windows.Forms.Application]::DoEvents()
                [System.Windows.Forms.SendKeys]::SendWait("{send_key}")
                Start-Sleep -Milliseconds 100
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
                # Method 1: SendKeys for Page Down
                ps_script = '''
                Add-Type -AssemblyName System.Windows.Forms
                [System.Windows.Forms.Application]::DoEvents()
                [System.Windows.Forms.SendKeys]::SendWait("{PGDN}")
                Start-Sleep -Milliseconds 100
                '''
                subprocess.run(["powershell", "-Command", ps_script], 
                            shell=True,
                            stdout=subprocess.DEVNULL, 
                            stderr=subprocess.DEVNULL)
                
                # Method 2: Alternative approach - simulate mouse wheel
                ps_script2 = '''
                Add-Type -AssemblyName System.Windows.Forms
                
                # Simulate mouse wheel scroll
                $signature = @'
                [DllImport("user32.dll",CharSet=CharSet.Auto, CallingConvention=CallingConvention.StdCall)]
                public static extern void mouse_event(uint dwFlags, uint dx, uint dy, uint cButtons, uint dwExtraInfo);
                '@
                $SendMouseEvent = Add-Type -memberDefinition $signature -name "Win32MouseEventScroll" -namespace Win32Functions -passThru
                
                # Scroll down (negative value scrolls down)
                $SendMouseEvent::mouse_event(0x00000800, 0, 0, 0xFFFFFF88, 0) # MOUSEEVENTF_WHEEL
                '''
                subprocess.run(["powershell", "-Command", ps_script2], 
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