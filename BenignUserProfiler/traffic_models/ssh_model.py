#!/usr/bin/env python3

from datetime import datetime
import time
import random
import os
import paramiko
from .traffic_model import TrafficModel


class SSHModel(TrafficModel):
    def __init__(self):
        super().__init__()
        self.scp_files = []  # Track files created with SCP
        
    def __str__(self):
        return "SSH"

    def verify(self) -> bool:
        # Check for required connection parameters
        for key in ["username", "address"]:
            if key not in self.model_config:
                print(f">>> Error in SSH model: No '{key}' specified in the config!")
                return False
                
        # Either password or private key must be provided
        if "password" not in self.model_config and "private_key" not in self.model_config:
            print(f">>> Error in SSH model: No 'private_key' or 'password' specified in the config!")
            return False
            
        # Commands must be specified unless in simulation mode
        if "commands" not in self.model_config and not self.model_config.get("simulate", False):
            print(f">>> Error in SSH model: No 'commands' specified in the config!")
            return False
            
        return True

    def generate(self) -> None:
        # Extract configuration parameters
        host = self.model_config["address"]
        port = self.model_config.get("port", 22)  # Default SSH port
        username = self.model_config["username"]
        password = self.model_config.get("password")
        private_key = self.model_config.get("private_key")
        commands = self.model_config.get("commands", [])
        timeout = self.model_config.get("timeout", 30)
        
        # Check if we're in simulation mode
        if self.model_config.get("simulate", False):
            self._simulate_ssh_operations()
            return
            
        # Connect to SSH server
        ssh = None
        try:
            print(f">>> Connecting to SSH server: {host}:{port}")
            print(f">>> Username: {username}")
            
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            
            # Connect using either private key or password
            if password is None and private_key is not None:
                print(f">>> Using private key authentication: {private_key}")
                private_key_file = paramiko.RSAKey.from_private_key_file(private_key)
                ssh.connect(
                    hostname=host, 
                    port=port, 
                    username=username, 
                    pkey=private_key_file,
                    timeout=timeout
                )
            else:
                print(f">>> Using password authentication")
                ssh.connect(
                    hostname=host, 
                    port=port, 
                    username=username, 
                    password=password,
                    timeout=timeout
                )
                
            print(f">>> Successfully connected to {host}")
            
            # Try to get system information
            try:
                print(">>> Getting system information...")
                stdin, stdout, stderr = ssh.exec_command("uname -a")
                system_info = stdout.read().decode().strip()
                print(f">>> System: {system_info}")
            except:
                print(">>> Could not retrieve system information")
            
            # Execute SCP operations first to upload test files
            if self.model_config.get("scp_operations", True):
                print("\n>>> Performing SCP file transfers")
                self._perform_scp_operations(ssh, host, port, username, password)
            
            # Execute each command
            for i, command in enumerate(commands):
                cmd_str = command.get("str") or command.get("command")
                show_output = command.get("show_output", True)
                
                if not cmd_str:
                    print(">>> Error: Missing command string")
                    continue
                
                print(f"\n>>> Executing command [{i+1}/{len(commands)}]: {cmd_str}")
                
                try:
                    # Record start time for performance measurement
                    start_time = time.time()
                    
                    # Execute the command
                    stdin, stdout, stderr = ssh.exec_command(cmd_str)
                    
                    # Wait for command to complete
                    exit_status = stdout.channel.recv_exit_status()
                    
                    # Calculate execution time
                    end_time = time.time()
                    execution_time = end_time - start_time
                    
                    # Get command output
                    output = stdout.read().decode()
                    error = stderr.read().decode()
                    
                    # Print status and execution time
                    if exit_status == 0:
                        print(f">>> Command completed successfully in {execution_time:.2f} seconds")
                    else:
                        print(f">>> Command failed with exit status {exit_status} in {execution_time:.2f} seconds")
                    
                    # Show command output if requested
                    if show_output:
                        if output:
                            print(">>> Command output:")
                            # Limit output to avoid excessive console spam
                            output_lines = output.split("\n")
                            if len(output_lines) > 20:
                                print("\n".join(output_lines[:10]))
                                print(f"... ({len(output_lines) - 20} lines hidden) ...")
                                print("\n".join(output_lines[-10:]))
                            else:
                                print(output)
                        else:
                            print(">>> No output from command")
                            
                        # Show errors if any
                        if error:
                            print(">>> Command errors:")
                            print(error)
                    else:
                        print(">>> Output hidden (show_output=False)")
                    
                    # Wait after command if specified
                    if "wait_after" in command:
                        wait_time = command["wait_after"]
                        print(f">>> Waiting {wait_time} seconds before next command...")
                        time.sleep(wait_time)
                    else:
                        # Small default delay
                        time.sleep(random.uniform(0.5, 2))
                        
                except Exception as e:
                    print(f">>> Error executing command: {cmd_str}")
                    print(f">>> {type(e).__name__}: {str(e)}")
                    continue
            
            # Clean up SCP files if any were created
            if self.scp_files and self.model_config.get("cleanup_scp_files", True):
                print("\n>>> Cleaning up SCP test files")
                self._cleanup_scp_files(ssh)
            
            # Close connection
            print("\n>>> Closing SSH connection...")
            ssh.close()
            print(">>> SSH session completed successfully")
            
        except Exception as e:
            print(f">>> Error in SSH connection/operations:")
            print(f">>> {type(e).__name__}: {str(e)}")
            # If this was a connection error, try with different port or settings
            if "connect" in str(e).lower() and self.model_config.get("retry_on_failure", True):
                print(">>> Connection failed, will retry with alternative settings...")
                time.sleep(2)
                self._retry_with_alternative_settings()
        finally:
            # Ensure SSH connection is closed
            if ssh:
                try:
                    ssh.close()
                except:
                    pass
    
    def _simulate_ssh_operations(self):
        """Simulate SSH operations without actually connecting to a server"""
        host = self.model_config["address"]
        port = self.model_config.get("port", 22)
        username = self.model_config["username"]
        commands = self.model_config.get("commands", [])
        
        # If no commands are provided, create some realistic commands
        if not commands:
            commands = [
                {"str": "ls -la", "show_output": True},
                {"str": "ps aux | grep python", "show_output": True},
                {"str": "free -m", "show_output": True},
                {"str": "df -h", "show_output": True},
                {"str": "uptime", "show_output": True}
            ]
        
        print(f">>> [SIMULATION] Connecting to SSH server: {host}:{port}")
        print(f">>> [SIMULATION] Username: {username}")
        print(f">>> [SIMULATION] Successfully connected")
        
        # Simulate system information
        system_types = [
            "Linux hostname 5.15.0-58-generic #64-Ubuntu SMP x86_64 GNU/Linux",
            "Linux hostname 5.4.0-150-generic #167-Ubuntu SMP x86_64 GNU/Linux",
            "Linux hostname 5.10.0-23-amd64 #1 SMP Debian 5.10.179-1 x86_64 GNU/Linux",
            "Linux hostname 6.1.21-v8+ #1642 SMP aarch64 GNU/Linux"
        ]
        print(f">>> [SIMULATION] System: {random.choice(system_types)}")
        
        # Simulate executing each command
        for i, command in enumerate(commands):
            cmd_str = command.get("str") or command.get("command")
            show_output = command.get("show_output", True)
            
            print(f"\n>>> [SIMULATION] Executing command [{i+1}/{len(commands)}]: {cmd_str}")
            
            # Simulate execution time
            execution_time = random.uniform(0.1, 2.0)
            time.sleep(min(execution_time, 1.0))  # Don't wait too long in simulation
            
            print(f">>> [SIMULATION] Command completed in {execution_time:.2f} seconds")
            
            # Generate fake output based on the command
            if show_output:
                if "ls" in cmd_str:
                    self._simulate_ls_output()
                elif "ps" in cmd_str:
                    self._simulate_ps_output()
                elif "free" in cmd_str:
                    self._simulate_free_output()
                elif "df" in cmd_str:
                    self._simulate_df_output()
                elif "uptime" in cmd_str:
                    self._simulate_uptime_output()
                else:
                    print(f">>> [SIMULATION] Command executed successfully")
            else:
                print(">>> [SIMULATION] Output hidden (show_output=False)")
            
            # Wait if specified
            if "wait_after" in command:
                wait_time = min(command["wait_after"], 2)  # Cap wait time for simulation
                print(f">>> [SIMULATION] Waiting {wait_time} seconds...")
                time.sleep(wait_time)
            else:
                time.sleep(random.uniform(0.2, 0.5))
        
        print("\n>>> [SIMULATION] Closing SSH connection")
        print(">>> [SIMULATION] SSH session completed successfully")
    
    def _simulate_ls_output(self):
        """Simulate output of ls command"""
        file_types = ["d", "-", "l"]
        file_permissions = ["rw-r--r--", "rwxr-xr-x", "rw-rw-r--", "r--r--r--"]
        file_names = ["file.txt", "image.jpg", "script.py", "data.csv", "README.md", 
                     "config.json", "Dockerfile", "requirements.txt", ".gitignore"]
        dir_names = ["src", "docs", "test", "build", "dist", "node_modules", ".git", "venv"]
        
        print(">>> [SIMULATION] Directory listing:")
        # Add some directories
        for i in range(random.randint(2, 5)):
            name = random.choice(dir_names)
            print(f">>> [SIMULATION] d{random.choice(file_permissions)}  {random.randint(1, 5)} user group {random.randint(1024, 8192):8d} Jan {random.randint(1, 31)} {random.randint(10, 23)}:{random.randint(10, 59)} {name}")
        
        # Add some files
        for i in range(random.randint(3, 10)):
            name = random.choice(file_names)
            print(f">>> [SIMULATION] -{random.choice(file_permissions)}  {random.randint(1, 2)} user group {random.randint(1024, 1024*1024):8d} Jan {random.randint(1, 31)} {random.randint(10, 23)}:{random.randint(10, 59)} {name}")
    
    def _simulate_ps_output(self):
        """Simulate output of ps command"""
        processes = [
            "root         1  0.0  0.1 170864 11812 ?        Ss   Jun15   0:23 /sbin/init",
            "root         2  0.0  0.0      0     0 ?        S    Jun15   0:00 [kthreadd]",
            f"user      {random.randint(1000, 9999)}  0.0  0.2 718992 22536 ?        Sl   10:23   0:02 /usr/bin/python3 app.py",
            f"user      {random.randint(1000, 9999)}  0.1  1.2 1218992 125536 ?      Sl   09:15   1:23 /usr/bin/python3 -m flask run",
            f"user      {random.randint(1000, 9999)}  0.0  0.5 892544 42768 ?        Sl   11:30   0:14 /usr/bin/nodejs server.js",
            f"user      {random.randint(1000, 9999)}  1.2  2.1 1562788 218672 ?      Sl   08:45   3:12 docker-compose up"
        ]
        
        print(">>> [SIMULATION] Process list:")
        print(">>> [SIMULATION] USER       PID  %CPU %MEM   VSZ  RSS TTY      STAT START   TIME COMMAND")
        for process in random.sample(processes, min(4, len(processes))):
            print(f">>> [SIMULATION] {process}")
    
    def _simulate_free_output(self):
        """Simulate output of free command"""
        total_mem = random.randint(8000, 32000)
        used_mem = random.randint(int(total_mem * 0.3), int(total_mem * 0.8))
        free_mem = total_mem - used_mem
        shared_mem = random.randint(100, 500)
        buff_cache = random.randint(1000, 4000)
        available = free_mem + buff_cache - random.randint(100, 500)
        
        total_swap = random.randint(4000, 16000)
        used_swap = random.randint(0, int(total_swap * 0.2))
        free_swap = total_swap - used_swap
        
        print(">>> [SIMULATION] Memory usage:")
        print(">>> [SIMULATION]               total        used        free      shared  buff/cache   available")
        print(f">>> [SIMULATION] Mem:       {total_mem:10d} {used_mem:10d} {free_mem:10d} {shared_mem:10d} {buff_cache:10d} {available:10d}")
        print(f">>> [SIMULATION] Swap:      {total_swap:10d} {used_swap:10d} {free_swap:10d}")
    
    def _simulate_df_output(self):
        """Simulate output of df command"""
        filesystems = [
            ["/dev/sda1", random.randint(20, 200), random.randint(30, 90), "/"],
            ["/dev/sda2", random.randint(50, 500), random.randint(10, 40), "/home"],
            ["/dev/sdb1", random.randint(500, 2000), random.randint(5, 60), "/data"],
            ["tmpfs", random.randint(1, 16), random.randint(1, 10), "/run"]
        ]
        
        print(">>> [SIMULATION] Disk usage:")
        print(">>> [SIMULATION] Filesystem     Size  Used Avail Use% Mounted on")
        for fs in filesystems:
            name, size, use_percent, mount = fs
            used = int(size * use_percent / 100)
            avail = size - used
            print(f">>> [SIMULATION] {name:12s} {size:4d}G  {used:3d}G  {avail:3d}G  {use_percent:2d}% {mount}")
    
    def _simulate_uptime_output(self):
        """Simulate output of uptime command"""
        hours = random.randint(1, 1000)
        minutes = random.randint(0, 59)
        users = random.randint(1, 10)
        load1 = random.uniform(0.01, 4.0)
        load5 = random.uniform(0.01, 3.0)
        load15 = random.uniform(0.01, 2.0)
        
        current_time = datetime.now().strftime("%H:%M:%S")
        print(f">>> [SIMULATION] {current_time} up {hours}:{minutes:02d}, {users} users, load average: {load1:.2f}, {load5:.2f}, {load15:.2f}")
        
    def _perform_scp_operations(self, ssh, host, port, username, password):
        """Perform SCP file transfers to the remote server"""
        try:
            # Create a temporary directory for SCP transfers
            temp_dir = "/tmp/scp_test_files"
            ssh.exec_command(f"mkdir -p {temp_dir}")
            
            # Number of files to transfer
            num_transfers = random.randint(3, 7)
            print(f">>> Will perform {num_transfers} SCP file transfers")
            
            # Create and transfer files
            for i in range(num_transfers):
                # Create a local temporary file with random content
                local_file = f"/tmp/scp_test_{int(time.time())}_{i}.txt"
                
                # Generate random content
                content_types = [
                    "Sample log data for system monitoring",
                    "Configuration data for application deployment",
                    "Test results from automated testing pipeline",
                    "JSON data for API integration testing",
                    "CSV data for reporting and analysis"
                ]
                
                # Create the local file
                with open(local_file, 'w') as f:
                    f.write(f"Test file created at {datetime.now()}\n")
                    f.write(f"Purpose: {random.choice(content_types)}\n")
                    f.write(f"File size: {random.randint(1, 10)} KB\n")
                    f.write("-" * 40 + "\n")
                    
                    # Add some random data
                    for j in range(random.randint(10, 50)):
                        f.write(f"Line {j}: {os.urandom(8).hex()}\n")
                
                # Remote file path
                remote_file = f"{temp_dir}/file_{i}.txt"
                self.scp_files.append(remote_file)
                
                # Upload using SCP
                print(f">>> Uploading file {i+1}/{num_transfers}: {local_file} -> {remote_file}")
                
                try:
                    # Try to use paramiko's SCP functionality
                    from scp import SCPClient
                    
                    # Create SCP client
                    with SCPClient(ssh.get_transport()) as scp:
                        scp.put(local_file, remote_file)
                    
                    print(f">>> Successfully uploaded file using SCP")
                    
                except ImportError:
                    # Fallback to using sftp subsystem
                    try:
                        sftp = ssh.open_sftp()
                        sftp.put(local_file, remote_file)
                        sftp.close()
                        print(f">>> Successfully uploaded file using SFTP subsystem")
                    except Exception as e:
                        print(f">>> Error uploading file: {e}")
                        continue
                
                # Clean up local file
                try:
                    os.remove(local_file)
                except:
                    pass
                
                # Small delay between transfers
                time.sleep(random.uniform(1, 3))
            
            # Verify the transfers
            stdin, stdout, stderr = ssh.exec_command(f"ls -la {temp_dir}")
            output = stdout.read().decode()
            print(f">>> Remote directory contents:\n{output}")
            
            return True
            
        except Exception as e:
            print(f">>> Error during SCP operations: {e}")
            return False
    
    def _cleanup_scp_files(self, ssh):
        """Clean up files created during SCP operations"""
        if not self.scp_files:
            return
            
        print(f">>> Cleaning up {len(self.scp_files)} SCP files")
        
        for file_path in self.scp_files:
            try:
                print(f">>> Removing {file_path}")
                ssh.exec_command(f"rm -f {file_path}")
                time.sleep(0.5)
            except Exception as e:
                print(f">>> Error removing file {file_path}: {e}")
        
        # Try to remove the temp directory
        try:
            temp_dir = "/tmp/scp_test_files"
            print(f">>> Removing directory {temp_dir}")
            ssh.exec_command(f"rmdir {temp_dir}")
        except:
            pass
            
        # Clear the list
        self.scp_files = []
    
    def _retry_with_alternative_settings(self):
        """Try alternative settings if initial connection fails"""
        # This is a stub - in a real implementation you might try:
        # - Different ports
        # - Different authentication methods
        # - Proxy or tunnel connections
        print(">>> Not implementing retry logic in this version")
