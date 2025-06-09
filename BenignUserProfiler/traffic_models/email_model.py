#!/usr/bin/env python3

import email
import time
import imaplib
import os
import smtplib
import platform
import random
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from .traffic_model import TrafficModel


class SMTPModel(TrafficModel):
    def __init__(self, service_type=None):
        self.service_type = service_type  # gmail, outlook, etc.
        
    def __str__(self):
        return "SMTP"

    def verify(self) -> bool:
        for key in ["sender", "password", "receivers"]:
            if key not in self.model_config:
                print(f">>> Error in SMTP model: No '{key}' specified in the config!")
                return False

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
        
        # Connect to appropriate SMTP server based on service
        server, port = None, None
        try:
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
        except Exception as e:
            print(f">>> Error connecting to {service} SMTP server.")
            print(e)
            return

        sender = self.model_config["sender"]
        password = self.model_config["password"]
        
        # Get receivers from config
        if isinstance(self.model_config["receivers"], list):
            receivers = self.model_config["receivers"]
        else:
            # Convert single receiver to list
            receivers = [self.model_config["receivers"]]
            
        # Handle email templates or configured emails
        if "email_templates" in self.model_config:
            templates = self.model_config["email_templates"]
            email_data = random.choice(templates)
            self._send_email(server, sender, password, receivers, email_data)
        elif "emails" in self.model_config:
            for email_data in self.model_config["emails"]:
                self._send_email(server, sender, password, receivers, email_data)
                if "wait_after" in email_data:
                    time.sleep(email_data["wait_after"])

        server.quit()
        
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
        elif "outlook" in sender or "hotmail" in sender or "live" in sender:
            return "outlook"
        elif "yahoo" in sender:
            return "yahoo"
            
        # Default to gmail
        return "gmail"
        
    def _send_email(self, server, sender, password, receivers, email_data):
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
                    except Exception as e:
                        print(f">>> Error attaching file {attachment}: {e}")

            # Login and send
            server.login(sender, password)
            text = message.as_string()
            server.sendmail(sender, selected_receivers, text)
            print(f">>> Email sent: {email_data['subject']} to {len(selected_receivers)} recipients")
        except Exception as e:
            print(f">>> Error sending email: {e}")


class IMAPModel(TrafficModel):
    def __init__(self, service_type=None):
        self.service_type = service_type  # gmail, outlook, etc.
        
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
            mail.login(username, password)
            
            # Select mailbox (inbox by default)
            mailbox = self.model_config.get("mailbox", "INBOX")
            status, messages = mail.select(mailbox)
            print(f">>> Selected mailbox: {mailbox}")
            
            # Determine email search criteria
            if "search_criteria" in self.model_config:
                search_criteria = self.model_config["search_criteria"]
            else:
                # Default to unread messages
                search_criteria = "UNSEEN"
                
            # Fetch emails based on criteria
            _, selected_mails = mail.search(None, search_criteria)
            
            # Process found emails
            max_emails = self.model_config.get("max_emails", 5)  # Limit number of emails processed
            email_count = 0
            
            for num in selected_mails[0].split():
                if email_count >= max_emails:
                    break
                    
                _, data = mail.fetch(num, '(RFC822)')
                _, bytes_data = data[0]

                email_message = email.message_from_bytes(bytes_data)
                print("\n")
                print(40 * "=")
                print("Subject: ", email_message["subject"])
                print("To:", email_message["to"])
                print("From: ", email_message["from"])
                print("Date: ", email_message["date"])
                
                # Process email body
                for part in email_message.walk():
                    if part.get_content_type() == "text/plain" or part.get_content_type() == "text/html":
                        message = part.get_payload(decode=True)
                        print("Message: \n", message.decode()[:100] + "...")  # Show first 100 chars
                        
                    # Download attachments if enabled
                    if (self.model_config.get("download_attachments", False) and 
                        part.get_content_maintype() != 'multipart' and 
                        part.get('Content-Disposition') is not None):

                        filename = part.get_filename()
                        if filename:
                            attachment_path = os.path.join(
                                self.model_config["attachments_dir"], filename)
                            if not os.path.isfile(attachment_path):
                                with open(attachment_path, 'wb') as attached_file:
                                    attached_file.write(part.get_payload(decode=True))
                                print(f">>> Downloaded attachment: {filename}")
                
                # Mark as read if specified
                if self.model_config.get("mark_as_read", False):
                    mail.store(num, '+FLAGS', '\\Seen')
                
                email_count += 1
                print(40 * "=", "\n")
                
                # Random delay between reading emails
                time.sleep(random.uniform(1, 3))
            
            print(f">>> Processed {email_count} emails")
            
        except Exception as e:
            print(f">>> Error in IMAP model: {e}")
        finally:
            if 'mail' in locals():
                try:
                    mail.close()
                    mail.logout()
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
            
        # Try to determine from username
        username = self.model_config["username"].lower()
        if "gmail" in username:
            return "gmail"
        elif "outlook" in username or "hotmail" in username or "live" in username:
            return "outlook"
        elif "yahoo" in username:
            return "yahoo"
            
        # Default to gmail
        return "gmail"