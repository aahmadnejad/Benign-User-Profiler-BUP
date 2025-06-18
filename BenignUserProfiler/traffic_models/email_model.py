#!/usr/bin/env python3

import email
import time
import imaplib
import os
import smtplib
import platform
import random
import requests
import tempfile
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from .traffic_model import TrafficModel


class SMTPModel(TrafficModel):
    def __init__(self, service_type=None):
        super().__init__()
        self.service_type = service_type  # gmail, outlook, etc.
        self.temp_dir = tempfile.mkdtemp()
        
    def __str__(self):
        return "SMTP"

    def verify(self) -> bool:
        # Check for required fields
        for key in ["sender", "password", "receivers"]:
            if key not in self.model_config:
                print(f">>> Error in SMTP model: No '{key}' specified in the config!")
                return False

        # Check email content configuration
        if not any(key in self.model_config for key in ["emails", "email_templates", "generate_content"]):
            print(">>> Error in SMTP model: No email content specified. Use 'emails', 'email_templates', or 'generate_content'.")
            return False

        # If explicit emails are provided, validate their structure
        if "emails" in self.model_config:
            for email in self.model_config["emails"]:
                for key in ["subject", "text"]:
                    if key not in email:
                        print(f">>> Error in SMTP model: No '{key}' specified in the emails config!"
                              f" email: {email}")
                        return False

        return True

    def generate(self) -> None:
        # Determine email service based on model config or email address
        service = self._determine_email_service()
        print(f">>> Using email service: {service}")
        
        # Connect to appropriate SMTP server based on service
        server = None
        port = None
        
        # Simulate mode doesn't actually connect to servers
        simulate_mode = self.model_config.get("simulate", False)
        if simulate_mode:
            print(">>> Running in simulation mode - no actual emails will be sent")
            
        try:
            if not simulate_mode:
                if service == "gmail":
                    server = smtplib.SMTP_SSL('smtp.gmail.com')
                    port = 465
                    server.connect("smtp.gmail.com", port)
                elif service == "outlook" or service == "hotmail":
                    server = smtplib.SMTP('smtp-mail.outlook.com')
                    port = 587
                    server.connect("smtp-mail.outlook.com", port)
                    server.starttls()
                elif service == "yahoo":
                    server = smtplib.SMTP_SSL('smtp.mail.yahoo.com')
                    port = 465
                    server.connect("smtp.mail.yahoo.com", port)
                else:
                    # Default to Gmail
                    server = smtplib.SMTP_SSL('smtp.gmail.com')
                    port = 465
                    server.connect("smtp.gmail.com", port)
                    
                print(f">>> Connected to {service} SMTP server on port {port}")
            
            sender = self.model_config["sender"]
            password = self.model_config["password"]
            
            # Get receivers from config
            if isinstance(self.model_config["receivers"], list):
                receivers = self.model_config["receivers"]
            else:
                # Convert single receiver to list
                receivers = [self.model_config["receivers"]]
                
            # Determine how many emails to send
            num_emails = self.model_config.get("num_emails", 1)
            
            # Generate and send emails based on the configuration
            for i in range(num_emails):
                # Handle different email content generation methods
                if "generate_content" in self.model_config and self.model_config["generate_content"]:
                    # Generate email content with Lorem Ipsum API
                    email_data = self._generate_email_content()
                    self._send_email(server, sender, password, receivers, email_data, simulate=simulate_mode)
                    
                elif "email_templates" in self.model_config:
                    # Use a random template from the provided templates
                    templates = self.model_config["email_templates"]
                    email_data = random.choice(templates)
                    self._send_email(server, sender, password, receivers, email_data, simulate=simulate_mode)
                    
                elif "emails" in self.model_config:
                    # Use explicitly configured emails
                    for email_data in self.model_config["emails"]:
                        self._send_email(server, sender, password, receivers, email_data, simulate=simulate_mode)
                        if "wait_after" in email_data:
                            time.sleep(email_data["wait_after"])
                
                # Add delay between multiple emails
                if num_emails > 1 and i < num_emails - 1:
                    delay = random.uniform(5, 15)
                    print(f">>> Waiting {delay:.1f} seconds before sending next email...")
                    time.sleep(delay)

            # Quit the server connection
            if server and not simulate_mode:
                server.quit()
                
        except Exception as e:
            print(f">>> Error in SMTP model: {e}")
            if server and not simulate_mode:
                try:
                    server.quit()
                except:
                    pass
        
    def _determine_email_service(self):
        """Determine which email service to use based on config or email address"""
        # Use explicit service_type if provided in constructor
        if self.service_type:
            return self.service_type.lower()
            
        # Use service from config if available
        if "service" in self.model_config:
            return self.model_config["service"].lower()
            
        # Try to determine from email address
        sender = self.model_config["sender"].lower()
        if "gmail" in sender:
            return "gmail"
        elif "outlook" in sender or "hotmail" in sender or "live" in sender or "office365" in sender:
            return "outlook"
        elif "yahoo" in sender:
            return "yahoo"
            
        # Default to gmail
        return "gmail"
        
    def _generate_email_content(self):
        """Generate email content using Lorem Ipsum API"""
        print(">>> Generating email content with Lorem Ipsum API")
        
        # Generate a random subject
        subject_types = [
            "Meeting Update", "Project Status", "Important Announcement", 
            "Weekly Report", "Upcoming Event", "Action Required",
            "New Opportunity", "Follow-up", "Policy Update",
            "Team Update", "Budget Review", "System Notification"
        ]
        subject = random.choice(subject_types)
        
        # Add a random identifier to make it more realistic
        if random.random() < 0.7:  # 70% chance to add identifier
            subject += f" - {random.choice(['Q1', 'Q2', 'Q3', 'Q4', '2024', 'Urgent', 'FYI', 'For Review'])}"
        
        # Generate the email body using Lorem Ipsum API
        try:
            # Try different APIs until one works
            apis = [
                "https://loripsum.net/api/3/medium/plaintext",
                "https://baconipsum.com/api/?type=all-meat&paras=3&format=text",
                "https://hipsum.co/api/?type=hipster-centric&paras=3"
            ]
            
            body_text = None
            for api_url in apis:
                try:
                    response = requests.get(api_url, timeout=5)
                    if response.status_code == 200:
                        body_text = response.text
                        break
                except:
                    continue
                    
            # If no API worked, generate fallback text
            if not body_text:
                print(">>> All Lorem Ipsum APIs failed, using fallback text")
                paragraphs = [
                    "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.",
                    "Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.",
                    "Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur."
                ]
                body_text = "\n\n".join(paragraphs)
            
            # Add a signature
            signatures = [
                "\n\nBest regards,\n[Your Name]",
                "\n\nThanks,\n[Your Name]",
                "\n\nRegards,\n[Your Name]",
                "\n\nSincerely,\n[Your Name]",
                "\n\nCheers,\n[Your Name]"
            ]
            body_text += random.choice(signatures)
            
            # Create the email data structure
            email_data = {
                "subject": subject,
                "text": body_text,
            }
            
            # Add attachments randomly
            if random.random() < 0.3:  # 30% chance to add attachments
                email_data["attachments"] = self._generate_attachments()
                
            return email_data
            
        except Exception as e:
            print(f">>> Error generating email content: {e}")
            # Fallback to a simple email
            return {
                "subject": "Automated Message",
                "text": "This is an automated email message for testing purposes."
            }
            
    def _generate_attachments(self):
        """Generate random attachments for emails"""
        attachments = []
        
        # Create a simple text file
        text_file = os.path.join(self.temp_dir, f"document_{int(time.time())}.txt")
        with open(text_file, 'w') as f:
            f.write(f"Document created on {time.ctime()}\n\n")
            f.write("This is a sample document for email attachment testing.")
        attachments.append(text_file)
        
        return attachments
        
    def _send_email(self, server, sender, password, receivers, email_data, simulate=False):
        """Send a single email using the provided server connection"""
        try:
            message = MIMEMultipart()
            message['Subject'] = email_data["subject"]
            message['From'] = sender
            
            # Choose receivers - either all or a random subset
            if "random_receivers" in email_data and email_data["random_receivers"]:
                num_receivers = min(
                    random.randint(1, len(receivers)), 
                    email_data.get("max_receivers", len(receivers))
                )
                selected_receivers = random.sample(receivers, num_receivers)
            else:
                selected_receivers = receivers
                
            message['To'] = ", ".join(selected_receivers)
            message.attach(MIMEText(email_data["text"]))

            # Add attachments if specified
            if "attachments" in email_data and email_data["attachments"]:
                for attachment in email_data["attachments"]:
                    try:
                        with open(attachment, "rb") as attached_file:
                            part = MIMEApplication(attached_file.read(), 
                                                 Name=os.path.basename(attachment))
                        part['Content-Disposition'] = f'attachment; filename="{os.path.basename(attachment)}"'
                        message.attach(part)
                        print(f">>> Attached file: {os.path.basename(attachment)}")
                    except Exception as e:
                        print(f">>> Error attaching file {attachment}: {e}")

            # Print email details
            print("\n" + "="*50)
            print(f">>> Email Details:")
            print(f">>> From: {sender}")
            print(f">>> To: {', '.join(selected_receivers)}")
            print(f">>> Subject: {email_data['subject']}")
            print(f">>> Attachments: {len(email_data.get('attachments', []))}")
            print(f">>> Body Preview: {email_data['text'][:100]}...")
            print("="*50 + "\n")
            
            # In simulation mode, don't actually send
            if simulate:
                print(f">>> [SIMULATION] Email would be sent to {len(selected_receivers)} recipients")
                return
                
            # Login and send
            print(f">>> Logging in to email server as {sender}")
            server.login(sender, password)
            
            print(f">>> Preparing to send email to {len(selected_receivers)} recipients")
            text = message.as_string()
            
            # Send the email
            print(f">>> Sending email: {email_data['subject']}")
            server.sendmail(sender, selected_receivers, text)
            print(f">>> Email successfully sent: {email_data['subject']} to {len(selected_receivers)} recipients")
        except Exception as e:
            print(f">>> Error sending email: {e}")


class IMAPModel(TrafficModel):
    def __init__(self, service_type=None):
        super().__init__()
        self.service_type = service_type  # gmail, outlook, etc.
        self.temp_dir = tempfile.mkdtemp()
        
    def __str__(self):
        return "IMAP"

    def verify(self) -> bool:
        for key in ["username", "password"]:
            if key not in self.model_config:
                print(f">>> Error in IMAP model: No '{key}' specified in the config!")
                return False
                
        # Check for attachments_dir only if download_attachments is True
        if self.model_config.get("download_attachments", False) and "attachments_dir" not in self.model_config:
            print(">>> Error in IMAP model: No 'attachments_dir' specified but download_attachments is True!")
            return False
            
        return True

    def generate(self) -> None:
        username = self.model_config["username"]
        password = self.model_config["password"]
        
        # Determine service type
        service = self._determine_email_service()
        print(f">>> Using email service: {service}")
        
        # Simulate mode doesn't actually connect to servers
        simulate_mode = self.model_config.get("simulate", False)
        if simulate_mode:
            print(">>> Running in simulation mode - no actual email server connections will be made")
            self._simulate_email_checking()
            return
        
        # Get proper IMAP server based on service
        imap_server = None
        try:
            if service == "gmail":
                imap_server = "imap.gmail.com"
            elif service == "outlook" or service == "hotmail":
                imap_server = "outlook.office365.com"
            elif service == "yahoo":
                imap_server = "imap.mail.yahoo.com"
            else:
                # Default to Gmail
                imap_server = "imap.gmail.com"
                
            print(f">>> Connecting to {service} IMAP server: {imap_server}")
            mail = imaplib.IMAP4_SSL(imap_server)
            
            print(f">>> Logging in as {username}")
            mail.login(username, password)
            
            # Select mailbox (inbox by default)
            mailbox = self.model_config.get("mailbox", "INBOX")
            status, messages = mail.select(mailbox)
            print(f">>> Selected mailbox: {mailbox}")
            
            # Get mailbox statistics
            status, response = mail.status(mailbox, "(MESSAGES UNSEEN)")
            if status == "OK":
                print(f">>> Mailbox stats: {response[0].decode()}")
            
            # Determine email search criteria
            if "search_criteria" in self.model_config:
                search_criteria = self.model_config["search_criteria"]
                print(f">>> Using search criteria: {search_criteria}")
            else:
                # Default to unread messages
                search_criteria = "UNSEEN"
                print(f">>> Using default search criteria: {search_criteria}")
                
            # Fetch emails based on criteria
            print(f">>> Searching for emails...")
            _, selected_mails = mail.search(None, search_criteria)
            
            # Check if any emails were found
            if not selected_mails[0]:
                print(">>> No emails found matching criteria")
                mail.close()
                mail.logout()
                return
            else:
                print(f">>> Found {len(selected_mails[0].split())} matching emails")
            
            # Process found emails
            max_emails = self.model_config.get("max_emails", 5)  # Limit number of emails processed
            print(f">>> Will process up to {max_emails} emails")
            email_count = 0
            
            for num in selected_mails[0].split():
                if email_count >= max_emails:
                    break
                    
                print(f"\n>>> Fetching email {email_count+1}/{max_emails}...")
                _, data = mail.fetch(num, '(RFC822)')
                _, bytes_data = data[0]

                email_message = email.message_from_bytes(bytes_data)
                print("\n" + "="*50)
                print(f">>> Email {email_count+1} Details:")
                print(f">>> Subject: {email_message['subject']}")
                print(f">>> To: {email_message['to']}")
                print(f">>> From: {email_message['from']}")
                print(f">>> Date: {email_message['date']}")
                
                # Track if email has attachments
                has_attachments = False
                
                # Process email body
                for part in email_message.walk():
                    if part.get_content_type() == "text/plain" or part.get_content_type() == "text/html":
                        message = part.get_payload(decode=True)
                        if message:
                            print(f">>> Message preview: {message.decode()[:100]}...")  # Show first 100 chars
                            
                            # Simulate reading time
                            read_time = random.uniform(3, 10)
                            print(f">>> Reading email for {read_time:.1f} seconds...")
                            time.sleep(read_time)
                        
                    # Check for attachments
                    if (part.get_content_maintype() != 'multipart' and 
                        part.get('Content-Disposition') is not None):
                        
                        filename = part.get_filename()
                        if filename:
                            has_attachments = True
                            print(f">>> Found attachment: {filename}")
                            
                            # Download attachments if enabled
                            if self.model_config.get("download_attachments", False):
                                # Use specified dir or temp dir
                                attachments_dir = self.model_config.get("attachments_dir", self.temp_dir)
                                attachment_path = os.path.join(attachments_dir, filename)
                                
                                print(f">>> Downloading attachment: {filename}...")
                                download_time = random.uniform(1, 5)
                                time.sleep(download_time)  # Simulate download time
                                
                                if not os.path.isfile(attachment_path):
                                    with open(attachment_path, 'wb') as attached_file:
                                        attached_file.write(part.get_payload(decode=True))
                                    print(f">>> Downloaded attachment to: {attachment_path}")
                
                if not has_attachments:
                    print(">>> No attachments found")
                
                # Mark as read if specified
                if self.model_config.get("mark_as_read", False):
                    print(">>> Marking email as read")
                    mail.store(num, '+FLAGS', '\\Seen')
                
                email_count += 1
                print("="*50)
                
                # Random delay between reading emails
                if email_count < max_emails and email_count < len(selected_mails[0].split()):
                    delay = random.uniform(2, 5)
                    print(f"\n>>> Waiting {delay:.1f} seconds before checking next email...")
                    time.sleep(delay)
            
            print(f"\n>>> Email checking completed. Processed {email_count} emails.")
            
            # Check for other folders if specified
            if "check_folders" in self.model_config and self.model_config["check_folders"]:
                folders_to_check = self.model_config["check_folders"]
                print(f"\n>>> Checking additional folders: {folders_to_check}")
                
                for folder in folders_to_check:
                    print(f"\n>>> Checking folder: {folder}")
                    try:
                        status, messages = mail.select(folder)
                        if status == "OK":
                            # Just get stats for these folders
                            status, response = mail.status(folder, "(MESSAGES UNSEEN)")
                            if status == "OK":
                                print(f">>> Folder stats: {response[0].decode()}")
                                
                            # Random delay between folder checks
                            time.sleep(random.uniform(1, 3))
                        else:
                            print(f">>> Folder {folder} not found or cannot be selected")
                    except Exception as e:
                        print(f">>> Error checking folder {folder}: {e}")
            
            print("\n>>> Logging out from email server")
            mail.close()
            mail.logout()
            
        except Exception as e:
            print(f">>> Error in IMAP model: {e}")
        finally:
            if 'mail' in locals():
                try:
                    mail.close()
                    mail.logout()
                except:
                    pass
    
    def _simulate_email_checking(self):
        """Simulate checking emails without actually connecting to a server"""
        username = self.model_config["username"]
        service = self._determine_email_service()
        
        print(f">>> [SIMULATION] Connecting to {service} IMAP server")
        print(f">>> [SIMULATION] Logging in as {username}")
        print(f">>> [SIMULATION] Selected mailbox: INBOX")
        
        # Simulate finding emails
        num_emails = random.randint(3, 10)
        print(f">>> [SIMULATION] Found {num_emails} emails")
        
        # Simulate processing emails
        max_emails = min(self.model_config.get("max_emails", 5), num_emails)
        print(f">>> [SIMULATION] Will process {max_emails} emails")
        
        for i in range(max_emails):
            print(f"\n>>> [SIMULATION] Reading email {i+1}/{max_emails}")
            
            # Generate random email details
            subject_prefixes = ["Re:", "Fwd:", "", "", ""]  # More chance of direct emails
            subject_types = [
                "Meeting Update", "Project Status", "Important Announcement", 
                "Weekly Report", "Upcoming Event", "Action Required"
            ]
            subject = f"{random.choice(subject_prefixes)} {random.choice(subject_types)}"
            
            # Random sender
            sender_domains = ["gmail.com", "outlook.com", "company.com", "example.org"]
            sender_names = ["john.doe", "jane.smith", "alex.wilson", "sam.johnson", "chris.davis"]
            sender = f"{random.choice(sender_names)}@{random.choice(sender_domains)}"
            
            # Random date within last week
            days_ago = random.randint(0, 7)
            hours_ago = random.randint(0, 23)
            minutes_ago = random.randint(0, 59)
            date_str = f"{days_ago}d {hours_ago}h {minutes_ago}m ago"
            
            print("\n" + "="*50)
            print(f">>> [SIMULATION] Email {i+1} Details:")
            print(f">>> Subject: {subject}")
            print(f">>> From: {sender}")
            print(f">>> Date: {date_str}")
            
            # Simulate reading time
            read_time = random.uniform(3, 8)
            print(f">>> [SIMULATION] Reading email for {read_time:.1f} seconds...")
            time.sleep(read_time)
            
            # Random chance of attachment
            if random.random() < 0.3:  # 30% chance
                attachment_types = ["document.pdf", "report.xlsx", "image.jpg", "presentation.pptx"]
                attachment = random.choice(attachment_types)
                print(f">>> [SIMULATION] Found attachment: {attachment}")
                
                if self.model_config.get("download_attachments", False):
                    print(f">>> [SIMULATION] Downloading attachment: {attachment}")
                    time.sleep(random.uniform(1, 3))  # Simulate download time
            else:
                print(">>> [SIMULATION] No attachments found")
                
            print("="*50)
            
            # Delay between emails
            if i < max_emails - 1:
                delay = random.uniform(1, 4)
                print(f"\n>>> [SIMULATION] Waiting {delay:.1f} seconds before next email...")
                time.sleep(delay)
                
        print("\n>>> [SIMULATION] Email checking completed")
        
        # Check additional folders
        if "check_folders" in self.model_config and self.model_config["check_folders"]:
            folders = self.model_config["check_folders"]
            print(f"\n>>> [SIMULATION] Checking additional folders: {folders}")
            
            for folder in folders:
                print(f">>> [SIMULATION] Checking folder: {folder}")
                unread = random.randint(0, 5)
                total = random.randint(unread, unread + 20)
                print(f">>> [SIMULATION] Folder stats: {total} total, {unread} unread")
                time.sleep(random.uniform(1, 2))
                
        print("\n>>> [SIMULATION] Logging out from email server")
                    
    def _determine_email_service(self):
        """Determine which email service to use based on config or email address"""
        # Use explicit service_type if provided in constructor
        if self.service_type:
            return self.service_type.lower()
            
        # Use service from config if available
        if "service" in self.model_config:
            return self.model_config["service"].lower()
            
        # Try to determine from username
        username = self.model_config["username"].lower()
        if "gmail" in username:
            return "gmail"
        elif "outlook" in username or "hotmail" in username or "live" in username or "office365" in username:
            return "outlook"
        elif "yahoo" in username:
            return "yahoo"
            
        # Default to gmail
        return "gmail"