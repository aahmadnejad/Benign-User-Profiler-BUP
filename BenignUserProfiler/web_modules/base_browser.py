#!/usr/bin/env python3

import platform
import subprocess
import time
import random
import os
import sys
from abc import ABC, abstractmethod

# Add debug flag for detailed logging
DEBUG = os.environ.get("PYTHONDEVMODE", "0") == "1"
VERBOSE = os.environ.get("BUP_VERBOSE", "0") == "1"

class BaseBrowserModule(ABC):
    def __init__(self, headless=False):
        self.headless = headless
        self.os_type = platform.system()
        
        # Detect Windows environment more precisely
        if self.os_type == "Windows" or "win" in sys.platform.lower():
            self.os_type = "Windows"
        
        # Print system info for debugging
        print(f">>> OS detected: {self.os_type}")
        print(f">>> Platform: {platform.platform()}")
        print(f">>> Python: {sys.version}")
        
        # Check if selenium is available (for fallback)
        try:
            import selenium
            self.has_selenium = True
            print(">>> Selenium is available")
        except ImportError:
            self.has_selenium = False
            print(">>> Selenium is not available, using fallback methods")
    
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
            print(f">>> Attempting to click at position ({x}, {y})")
            
            # Try selenium first if available
            if hasattr(self, 'has_selenium') and self.has_selenium:
                try:
                    # Try to use selenium's direct browser interaction
                    from selenium import webdriver
                    from selenium.webdriver.common.action_chains import ActionChains
                    
                    print(">>> Using Selenium for clicking")
                    # Note: This is just a fallback check, actual implementation would need a driver instance
                    if hasattr(self, 'driver') and self.driver is not None:
                        actions = ActionChains(self.driver)
                        actions.move_to_element_with_offset(self.driver.find_element_by_tag_name('body'), x, y)
                        actions.click()
                        actions.perform()
                        print(">>> Clicked using Selenium")
                        return True
                except Exception as e:
                    print(f">>> Selenium click failed: {e}")
                    # Fall back to OS-specific methods
            
            if self.os_type == "Linux":
                print(">>> Using xdotool for clicking")
                try:
                    # First try simpler approach
                    subprocess.run(["xdotool", "mousemove", str(x), str(y), "click", "1"], 
                                check=False,
                                stdout=subprocess.DEVNULL)
                    print(">>> Linux click successful")
                    return True
                except Exception as e:
                    print(f">>> xdotool click failed: {e}")
                    # Try alternative approach
                    try:
                        # Move mouse first
                        subprocess.run(["xdotool", "mousemove", str(x), str(y)], check=False)
                        time.sleep(0.2)
                        # Then click
                        subprocess.run(["xdotool", "click", "1"], check=False)
                        return True
                    except Exception as e2:
                        print(f">>> Alternative xdotool approach failed: {e2}")
                        return False
                        
            elif self.os_type == "Windows":
                print(">>> Using Win32 API for clicking")
                
                # Create a more reliable PowerShell script for mouse clicking
                try:
                    # Try using pyautogui if available (simplest approach)
                    import pyautogui
                    pyautogui.click(x=x, y=y)
                    print(">>> Clicked using pyautogui")
                    return True
                except ImportError:
                    print(">>> pyautogui not available, falling back to PowerShell")
                
                # Method 1: Using direct Win32 API calls via PowerShell
                ps_script = f'''
                # Log what we're doing
                Write-Output "Attempting to click at position {x}, {y}"
                
                # Create a .NET method that calls the Win32 API
                Add-Type -TypeDefinition @"
                using System;
                using System.Runtime.InteropServices;
                
                public class MouseOps
                {{
                    [DllImport("user32.dll", SetLastError = true)]
                    public static extern bool SetCursorPos(int x, int y);
                    
                    [DllImport("user32.dll", SetLastError = true)]
                    public static extern void mouse_event(int dwFlags, int dx, int dy, int cButtons, int dwExtraInfo);
                    
                    [DllImport("user32.dll")]
                    [return: MarshalAs(UnmanagedType.Bool)]
                    public static extern bool GetCursorPos(out System.Drawing.Point lpPoint);
                    
                    public const int MOUSEEVENTF_LEFTDOWN = 0x0002;
                    public const int MOUSEEVENTF_LEFTUP = 0x0004;
                    public const int MOUSEEVENTF_ABSOLUTE = 0x8000;
                }}
                "@
                
                # Get current cursor position to verify
                $position = New-Object System.Drawing.Point
                [MouseOps]::GetCursorPos([ref]$position)
                Write-Output "Starting cursor position: $($position.X), $($position.Y)"
                
                # Position cursor
                $result = [MouseOps]::SetCursorPos({x}, {y})
                Write-Output "SetCursorPos result: $result"
                
                # Verify cursor position
                [MouseOps]::GetCursorPos([ref]$position)
                Write-Output "New cursor position: $($position.X), $($position.Y)"
                
                # Click down and up with delay
                Write-Output "Sending mouse down event"
                [MouseOps]::mouse_event([MouseOps]::MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
                Start-Sleep -Milliseconds 100
                
                Write-Output "Sending mouse up event"
                [MouseOps]::mouse_event([MouseOps]::MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
                
                Write-Output "Click sequence completed"
                '''
                
                # Save script to file with UTF-8 encoding
                script_path = os.path.join(os.path.expanduser("~"), "win_click.ps1")
                with open(script_path, "w", encoding="utf-8") as f:
                    f.write(ps_script)
                
                # Run PowerShell with more reliable parameters and capture output
                print(f">>> Running PowerShell script from {script_path}")
                result = subprocess.run(
                    ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", script_path],
                    capture_output=True,
                    text=True
                )
                
                # Print PowerShell output for debugging
                print(f">>> PowerShell stdout: {result.stdout}")
                if result.stderr:
                    print(f">>> PowerShell stderr: {result.stderr}")
                
                # Clean up script file
                try:
                    os.remove(script_path)
                except Exception as e:
                    print(f">>> Failed to remove script file: {e}")
                
                # Try alternative clicking method if first method may have failed
                try:
                    # Alternative click method using SendKeys
                    alt_script = f'''
                    Add-Type -AssemblyName System.Windows.Forms
                    [System.Windows.Forms.Cursor]::Position = New-Object System.Drawing.Point({x}, {y})
                    Start-Sleep -Milliseconds 100
                    [System.Windows.Forms.SendKeys]::SendWait(" ")
                    Start-Sleep -Milliseconds 100
                    '''
                    
                    subprocess.run(["powershell", "-Command", alt_script], 
                                shell=True,
                                stdout=subprocess.DEVNULL)
                except Exception as e:
                    print(f">>> Alternative click method failed: {e}")
                
                return True
                
            else:
                print(f">>> Unsupported OS for clicking: {self.os_type}")
                return False
                
        except Exception as e:
            print(f">>> Critical error clicking: {e}")
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
            print(f">>> Pressing key: {key}")
            
            # Try to use pyautogui first (most reliable cross-platform method)
            try:
                import pyautogui
                
                # Map xdotool key names to pyautogui names
                key_mapping = {
                    "Return": "enter",
                    "Escape": "esc", 
                    "Page_Down": "pagedown",
                    "Page_Up": "pageup",
                    "Right": "right",
                    "Left": "left",
                    "Up": "up",
                    "Down": "down",
                    "space": "space",
                    "alt+Left": ["alt", "left"],
                    "alt+F4": ["alt", "f4"]
                }
                
                # Convert key if it's in our mapping
                pyautogui_key = key_mapping.get(key, key)
                
                if isinstance(pyautogui_key, list):
                    # Handle key combinations
                    pyautogui.hotkey(*pyautogui_key)
                else:
                    # Press single key
                    pyautogui.press(pyautogui_key)
                
                print(f">>> Pressed key {key} using PyAutoGUI")
                return True
            except ImportError:
                print(">>> PyAutoGUI not available, using platform-specific methods")
            
            if self.os_type == "Linux":
                # Linux xdotool method
                try:
                    subprocess.run(["xdotool", "key", key], 
                                check=False,
                                stdout=subprocess.DEVNULL)
                    print(f">>> Pressed key {key} using xdotool")
                    return True
                except Exception as e:
                    print(f">>> xdotool key press failed: {e}")
                    # Fall back to other methods
            
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
                    "alt+F4": "%{F4}",
                    # Add single letter mappings
                    "a": "a", "b": "b", "c": "c", "d": "d", "e": "e", "f": "f", "g": "g",
                    "h": "h", "i": "i", "j": "j", "k": "k", "l": "l", "m": "m", "n": "n",
                    "o": "o", "p": "p", "q": "q", "r": "r", "s": "s", "t": "t", "u": "u",
                    "v": "v", "w": "w", "x": "x", "y": "y", "z": "z"
                }
                
                # Convert key to SendKeys format if it's in our mapping
                send_key = key_mapping.get(key, key)
                
                # Method 1: Windows SendKeys through PowerShell
                try:
                    ps_script = f'''
                    Add-Type -AssemblyName System.Windows.Forms
                    [System.Windows.Forms.Application]::DoEvents()
                    Write-Output "Sending key: {send_key}"
                    [System.Windows.Forms.SendKeys]::SendWait("{send_key}")
                    Start-Sleep -Milliseconds 100
                    '''
                    
                    result = subprocess.run(["powershell", "-Command", ps_script], 
                                shell=True,
                                capture_output=True,
                                text=True)
                    
                    if VERBOSE:
                        print(f">>> PowerShell key press output: {result.stdout}")
                        if result.stderr:
                            print(f">>> PowerShell key press error: {result.stderr}")
                    
                    # Method 2: Try Windows API directly for common keys
                    if key in ["space", "Return", "Escape", "Page_Down", "Page_Up", "Right", "Left", "Up", "Down"]:
                        vk_mapping = {
                            "space": 0x20,     # VK_SPACE
                            "Return": 0x0D,    # VK_RETURN
                            "Escape": 0x1B,    # VK_ESCAPE
                            "Page_Down": 0x22, # VK_NEXT
                            "Page_Up": 0x21,   # VK_PRIOR
                            "Right": 0x27,     # VK_RIGHT
                            "Left": 0x25,      # VK_LEFT
                            "Up": 0x26,        # VK_UP
                            "Down": 0x28       # VK_DOWN
                        }
                        
                        vk_code = vk_mapping.get(key)
                        if vk_code:
                            win32_script = f'''
                            Add-Type -TypeDefinition @"
                            using System;
                            using System.Runtime.InteropServices;
                            
                            public class KeyboardInput
                            {{
                                [DllImport("user32.dll")]
                                public static extern IntPtr GetForegroundWindow();
                                
                                [DllImport("user32.dll")]
                                public static extern bool PostMessage(IntPtr hWnd, uint msg, IntPtr wParam, IntPtr lParam);
                                
                                public const uint WM_KEYDOWN = 0x0100;
                                public const uint WM_KEYUP = 0x0101;
                            }}
                            "@
                            
                            $hwnd = [KeyboardInput]::GetForegroundWindow()
                            if ($hwnd -ne [IntPtr]::Zero) {{
                                Write-Output "Found foreground window: $hwnd"
                                Write-Output "Sending VK code: {vk_code}"
                                [KeyboardInput]::PostMessage($hwnd, [KeyboardInput]::WM_KEYDOWN, [IntPtr]{vk_code}, [IntPtr]::Zero)
                                Start-Sleep -Milliseconds 50
                                [KeyboardInput]::PostMessage($hwnd, [KeyboardInput]::WM_KEYUP, [IntPtr]{vk_code}, [IntPtr]::Zero)
                            }} else {{
                                Write-Output "No foreground window found"
                            }}
                            '''
                            
                            win32_result = subprocess.run(["powershell", "-Command", win32_script], 
                                        shell=True,
                                        capture_output=True,
                                        text=True)
                            
                            if VERBOSE:
                                print(f">>> Win32 API key press output: {win32_result.stdout}")
                    
                    print(f">>> Pressed key {key} using Windows methods")
                    return True
                except Exception as e:
                    print(f">>> Windows key press failed: {e}")
                    return False
            
            # Last resort if all else fails
            print(f">>> Warning: Could not press key {key} with reliable methods")
            return False
            
        except Exception as e:
            print(f">>> Error pressing key: {e}")
            return False
    
    def scroll_down(self, count=1):
        print(f">>> Attempting to scroll down {count} times")
        
        # Try to use pyautogui first if available (cross-platform solution)
        try:
            import pyautogui
            print(">>> Using PyAutoGUI for scrolling")
            for _ in range(count):
                # First try page down key
                pyautogui.press('pagedown')
                time.sleep(0.5)
                # Then also scroll with mouse wheel
                pyautogui.scroll(-100)  # Negative value scrolls down
                time.sleep(random.uniform(1, 3))
            return True
        except ImportError:
            print(">>> PyAutoGUI not available, using native methods")
        
        for i in range(count):
            print(f">>> Scroll attempt {i+1}/{count}")
            
            if self.os_type == "Linux":
                try:
                    print(">>> Using xdotool for Linux scrolling")
                    # First try Page_Down key
                    subprocess.run(["xdotool", "key", "Page_Down"], 
                                check=False,
                                stdout=subprocess.DEVNULL)
                    time.sleep(0.5)
                    
                    # Also try scrolling with mouse wheel (this often works better)
                    for _ in range(5):  # Multiple small scrolls often work better
                        subprocess.run(["xdotool", "click", "5"], 
                                    check=False,
                                    stdout=subprocess.DEVNULL)
                        time.sleep(0.1)
                except Exception as e:
                    print(f">>> Linux scroll failed: {e}")
                    # Try fallback method - send Down key multiple times
                    try:
                        for _ in range(10):
                            subprocess.run(["xdotool", "key", "Down"], check=False)
                            time.sleep(0.1)
                    except:
                        pass
            
            elif self.os_type == "Windows":
                print(">>> Using PowerShell/Win32 API for Windows scrolling")
                
                # Write a robust PowerShell script for scrolling with extensive logging
                ps_script = '''
                Write-Output "Starting scroll operation..."
                
                # Create a .NET method that calls the Win32 API for mouse wheel scrolling
                Add-Type -TypeDefinition @"
                using System;
                using System.Runtime.InteropServices;
                
                public class ScrollOps
                {
                    [DllImport("user32.dll", SetLastError = true)]
                    public static extern bool SetCursorPos(int x, int y);
                    
                    [DllImport("user32.dll", SetLastError = true)]
                    public static extern void mouse_event(int dwFlags, int dx, int dy, int cButtons, int dwExtraInfo);
                    
                    [DllImport("user32.dll")]
                    public static extern IntPtr GetForegroundWindow();
                    
                    [DllImport("user32.dll")]
                    [return: MarshalAs(UnmanagedType.Bool)]
                    public static extern bool PostMessage(IntPtr hWnd, uint msg, IntPtr wParam, IntPtr lParam);
                    
                    public const int MOUSEEVENTF_WHEEL = 0x0800;
                    public const uint WM_KEYDOWN = 0x0100;
                    public const uint WM_KEYUP = 0x0101;
                    public const uint VK_NEXT = 0x22; // Page Down key
                }
                "@
                
                # Method 1: Try to send Page Down key
                Write-Output "Sending Page Down key..."
                Add-Type -AssemblyName System.Windows.Forms
                [System.Windows.Forms.SendKeys]::SendWait("{PGDN}")
                Start-Sleep -Milliseconds 500
                
                # Method 2: Try directly posting to window
                Write-Output "Trying direct message post..."
                try {
                    $hwnd = [ScrollOps]::GetForegroundWindow()
                    if ($hwnd -ne [IntPtr]::Zero) {
                        Write-Output "Found foreground window: $hwnd"
                        [ScrollOps]::PostMessage($hwnd, [ScrollOps]::WM_KEYDOWN, [IntPtr][ScrollOps]::VK_NEXT, [IntPtr]::Zero)
                        Start-Sleep -Milliseconds 100
                        [ScrollOps]::PostMessage($hwnd, [ScrollOps]::WM_KEYUP, [IntPtr][ScrollOps]::VK_NEXT, [IntPtr]::Zero)
                    } else {
                        Write-Output "No foreground window found"
                    }
                } catch {
                    Write-Output "Error with direct message: $_"
                }
                
                # Method 3: Scroll with the mouse wheel (multiple small scrolls)
                Write-Output "Using mouse wheel..."
                
                # Get screen dimensions to scroll in the middle
                $screenWidth = [System.Windows.Forms.Screen]::PrimaryScreen.Bounds.Width
                $screenHeight = [System.Windows.Forms.Screen]::PrimaryScreen.Bounds.Height
                
                Write-Output "Screen dimensions: $screenWidth x $screenHeight"
                
                # Set cursor to middle of screen
                $centerX = $screenWidth / 2
                $centerY = $screenHeight / 2
                Write-Output "Moving cursor to center: $centerX, $centerY"
                
                $result = [ScrollOps]::SetCursorPos($centerX, $centerY)
                Write-Output "SetCursorPos result: $result"
                
                # Scroll down multiple times to ensure it works
                for ($i = 0; $i -lt 10; $i++) {
                    Write-Output "Scroll iteration $i"
                    # Negative number scrolls down
                    [ScrollOps]::mouse_event([ScrollOps]::MOUSEEVENTF_WHEEL, 0, 0, -120, 0)
                    Start-Sleep -Milliseconds 50
                }
                
                # Method 4: Alternative keyboard approach with arrow keys
                Write-Output "Using arrow keys as fallback..."
                for ($i = 0; $i -lt 10; $i++) {
                    [System.Windows.Forms.SendKeys]::SendWait("{DOWN}")
                    Start-Sleep -Milliseconds 50
                }
                
                Write-Output "Scroll operation complete"
                '''
                
                # Save script to file with UTF-8 encoding and execute
                script_path = os.path.join(os.path.expanduser("~"), "win_scroll.ps1")
                with open(script_path, "w", encoding="utf-8") as f:
                    f.write(ps_script)
                
                # Run with output capture for debugging
                result = subprocess.run(
                    ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", script_path],
                    capture_output=True,
                    text=True
                )
                
                # Print output for debugging
                print(f">>> PowerShell scroll output: {result.stdout[:200]}...")
                if result.stderr:
                    print(f">>> PowerShell scroll error: {result.stderr}")
                
                # Clean up script file
                try:
                    os.remove(script_path)
                except Exception as e:
                    print(f">>> Failed to remove scroll script: {e}")
            
            else:
                print(f">>> Unsupported OS for scrolling: {self.os_type}")
            
            # Wait between scrolls
            time.sleep(random.uniform(2, 5))
        
        return True
    
    def close_browser(self):
        try:
            if self.os_type == "Linux":
                try:
                    # First try to close gracefully with Alt+F4
                    subprocess.run(["xdotool", "key", "alt+F4"], 
                                check=False,
                                stdout=subprocess.DEVNULL, 
                                stderr=subprocess.DEVNULL)
                    time.sleep(1)
                    
                    # Then force kill any remaining Firefox processes
                    subprocess.run(["killall", "-9", "firefox"], 
                                check=False,
                                stdout=subprocess.DEVNULL, 
                                stderr=subprocess.DEVNULL)
                    
                    # Also kill firefox-bin if it exists
                    subprocess.run(["killall", "-9", "firefox-bin"], 
                                check=False,
                                stdout=subprocess.DEVNULL, 
                                stderr=subprocess.DEVNULL)
                    
                    # Also try pkill for more flexible matching
                    subprocess.run(["pkill", "-9", "-f", "firefox"], 
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