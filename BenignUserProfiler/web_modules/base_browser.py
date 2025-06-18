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
                
                # Wait for window to open
                time.sleep(2)
                
                # Try to maximize the window using xdotool if available
                try:
                    subprocess.run(["xdotool", "search", "--onlyvisible", "--class", "Firefox", "windowactivate", "key", "alt+F10"], 
                                check=False,
                                stdout=subprocess.DEVNULL, 
                                stderr=subprocess.DEVNULL)
                except:
                    pass
                               
            elif self.os_type == "Darwin":  # macOS
                subprocess.Popen(["open", "-a", "Firefox", url])
                
            elif self.os_type == "Windows":
                # Launch Firefox with new window
                cmd = f'start firefox -new-window "{url}"'
                if additional_args:
                    cmd += ' ' + ' '.join(additional_args)
                subprocess.Popen(cmd, shell=True)
                
                # Wait for window to open
                time.sleep(3)
                
                # Maximize window using PowerShell
                ps_script = '''
                Add-Type -AssemblyName System.Windows.Forms
                
                # Focus Firefox window
                $firefox = Get-Process firefox -ErrorAction SilentlyContinue
                if ($firefox) {
                    # Try to find and activate the Firefox window
                    Add-Type @"
                    using System;
                    using System.Runtime.InteropServices;
                    public class WindowHelper {
                        [DllImport("user32.dll")]
                        [return: MarshalAs(UnmanagedType.Bool)]
                        public static extern bool SetForegroundWindow(IntPtr hWnd);
                        
                        [DllImport("user32.dll")]
                        [return: MarshalAs(UnmanagedType.Bool)]
                        public static extern bool ShowWindow(IntPtr hWnd, int nCmdShow);
                    }
                "@
                    
                    # Focus the window
                    [WindowHelper]::SetForegroundWindow($firefox.MainWindowHandle)
                    
                    # Maximize (SW_MAXIMIZE = 3)
                    [WindowHelper]::ShowWindow($firefox.MainWindowHandle, 3)
                    
                    # Alternative method - send maximize shortcut
                    [System.Windows.Forms.SendKeys]::SendWait("%{SPACE}")
                    Start-Sleep -Milliseconds 100
                    [System.Windows.Forms.SendKeys]::SendWait("x")
                }
                '''
                
                # Save script to file and execute
                script_path = os.path.join(os.path.expanduser("~"), "maximize_script.ps1")
                with open(script_path, "w") as f:
                    f.write(ps_script)
                
                subprocess.run(["powershell", "-ExecutionPolicy", "Bypass", "-File", script_path], 
                            shell=True,
                            stdout=subprocess.DEVNULL, 
                            stderr=subprocess.DEVNULL)
                
                # Clean up script file
                try:
                    os.remove(script_path)
                except:
                    pass
                
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
                # For Windows, using a more direct approach and escaping special characters
                # Replace special characters that need escaping in SendKeys
                for char, replacement in [
                    ('+', '{+}'), ('^', '{^}'), ('%', '{%}'), ('~', '{~}'),
                    ('(', '{(}'), (')', '{)}'), ('{', '{{}'), ('}', '{}}'),
                    ('[', '{[}'), (']', '{]}')
                ]:
                    text = text.replace(char, replacement)
                
                ps_script = f'''
                Add-Type -AssemblyName System.Windows.Forms
                [System.Windows.Forms.Form]::ActiveForm | Out-Null
                [System.Windows.Forms.Application]::DoEvents()
                
                # Type the text character by character with small delays
                $text = @"{text}"
                foreach ($char in $text.ToCharArray()) {{
                    [System.Windows.Forms.SendKeys]::SendWait($char.ToString())
                    Start-Sleep -Milliseconds 10
                }}
                
                # Press Enter
                Start-Sleep -Milliseconds 100
                [System.Windows.Forms.SendKeys]::SendWait("{{ENTER}}")
                '''
                
                # Save script to file and execute (more reliable than passing directly)
                script_path = os.path.join(os.path.expanduser("~"), "keyboard_script.ps1")
                with open(script_path, "w") as f:
                    f.write(ps_script)
                
                subprocess.run(["powershell", "-ExecutionPolicy", "Bypass", "-File", script_path], 
                            shell=True,
                            stdout=subprocess.DEVNULL, 
                            stderr=subprocess.DEVNULL)
                
                # Clean up script file
                try:
                    os.remove(script_path)
                except:
                    pass
                
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
                # Method 1: Using direct Win32 API calls
                ps_script = f'''
                # Create a .NET method that calls the Win32 API
                Add-Type -TypeDefinition @"
                using System;
                using System.Runtime.InteropServices;
                
                public class MouseOperations
                {{
                    [DllImport("user32.dll")]
                    public static extern bool SetCursorPos(int x, int y);
                    
                    [DllImport("user32.dll")]
                    public static extern void mouse_event(int dwFlags, int dx, int dy, int cButtons, int dwExtraInfo);
                    
                    public const int MOUSEEVENTF_LEFTDOWN = 0x0002;
                    public const int MOUSEEVENTF_LEFTUP = 0x0004;
                }}
                "@
                
                # Position cursor and click
                [MouseOperations]::SetCursorPos({x}, {y})
                Start-Sleep -Milliseconds 100
                [MouseOperations]::mouse_event([MouseOperations]::MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
                Start-Sleep -Milliseconds 100
                [MouseOperations]::mouse_event([MouseOperations]::MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
                '''
                
                # Save script to file and execute (more reliable than passing directly)
                script_path = os.path.join(os.path.expanduser("~"), "click_script.ps1")
                with open(script_path, "w") as f:
                    f.write(ps_script)
                
                subprocess.run(["powershell", "-ExecutionPolicy", "Bypass", "-File", script_path], 
                            shell=True,
                            stdout=subprocess.DEVNULL, 
                            stderr=subprocess.DEVNULL)
                
                # Clean up script file
                try:
                    os.remove(script_path)
                except:
                    pass
                
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
                # Write a robust PowerShell script for scrolling
                ps_script = '''
                # Create a .NET method that calls the Win32 API for mouse wheel scrolling
                Add-Type -TypeDefinition @"
                using System;
                using System.Runtime.InteropServices;
                
                public class ScrollOperations
                {
                    [DllImport("user32.dll")]
                    public static extern bool SetCursorPos(int x, int y);
                    
                    [DllImport("user32.dll")]
                    public static extern void mouse_event(int dwFlags, int dx, int dy, int cButtons, int dwExtraInfo);
                    
                    public const int MOUSEEVENTF_WHEEL = 0x0800;
                }
                "@
                
                # First, try to send Page Down key
                Add-Type -AssemblyName System.Windows.Forms
                [System.Windows.Forms.SendKeys]::SendWait("{PGDN}")
                Start-Sleep -Milliseconds 200
                
                # Then also try to scroll with the mouse wheel
                # Get screen dimensions to scroll in the middle
                $screenWidth = [System.Windows.Forms.Screen]::PrimaryScreen.Bounds.Width
                $screenHeight = [System.Windows.Forms.Screen]::PrimaryScreen.Bounds.Height
                
                # Set cursor to middle of screen
                [ScrollOperations]::SetCursorPos($screenWidth / 2, $screenHeight / 2)
                Start-Sleep -Milliseconds 100
                
                # Scroll down multiple times to ensure it works
                for ($i = 0; $i -lt 5; $i++) {
                    # Negative number scrolls down
                    [ScrollOperations]::mouse_event([ScrollOperations]::MOUSEEVENTF_WHEEL, 0, 0, -120, 0)
                    Start-Sleep -Milliseconds 50
                }
                '''
                
                # Save script to file and execute (more reliable than passing directly)
                script_path = os.path.join(os.path.expanduser("~"), "scroll_script.ps1")
                with open(script_path, "w") as f:
                    f.write(ps_script)
                
                subprocess.run(["powershell", "-ExecutionPolicy", "Bypass", "-File", script_path], 
                            shell=True,
                            stdout=subprocess.DEVNULL, 
                            stderr=subprocess.DEVNULL)
                
                # Clean up script file
                try:
                    os.remove(script_path)
                except:
                    pass
            
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