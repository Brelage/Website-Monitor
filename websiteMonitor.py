import requests
import time 
import os
import json
import smtplib
import re
from random import randint, uniform
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from dotenv import load_dotenv


class WebsiteChecker:
    def __init__(self, url):
        self.url = url
        self.initial_interval = 300
        self.max_interval = 3600
        self.current_interval = self.initial_interval
        self.consecutive_failures = 0
        self.is_down = False
        self.current_status_code = 0

    def check_status(self):
        """Checks website status code and any mentions of errors in the html head of the website."""
        
        if self.is_down:
            time.sleep(self.current_interval)
        else:
            time.sleep(randint(300, 600))
        
        try:
            if self.check_status_code():
                if self.html_no_errors():
                    if self.is_down:
                        self.handle_success()
                    else:
                        pass
                else:
                    self.handle_failure("Email_message_html_error.txt")
            else:
                self.handle_failure("Email_message_status_code.txt") 
        except:
            raise


    def check_status_code(self):
        """checks whether the website returns a html status code between 200 and 399"""
        
        with requests.Session() as session:
            try:
                response = session.head(self.url, timeout=10, allow_redirects=True)
                self.current_status_code = response.status_code
                is_up = 200 <= self.current_status_code < 400
                return is_up
            except:
                self.handle_failure("Email_message_timeout.txt")
                return False

 
    def html_no_errors(self):
        """checks whether the website has any mention of 'error' in its head part of the html.
        Returns True if there are no error mentions, returns False if it finds mentions of errors"""
        
        try:
            head_chunks = []
            response = requests.get(self.url, stream=True, timeout=10, allow_redirects=True)
            for chunk in response.iter_content(chunk_size=512, decode_unicode=True):
                if chunk:
                    head_chunks.append(chunk)
                    if "</head>" in chunk:
                        break
            head_content = "".join(head_chunks)

            error_patterns = [r"error", r"not found", r"unavailable", r"nicht erreichbar", r"nicht gefunden"]
            for pattern in error_patterns:
                if re.search(pattern, head_content, re.IGNORECASE):
                    return False
            return True
        except:
            self.handle_failure("Email_message_timeout.txt")
            return True


    def handle_success(self):
        """reset monitoring parameters after successful check."""
        
        self.is_down = False
        self.consecutive_failures = 0
        self.current_interval = self.initial_interval


    def handle_failure(self, email_text):
        """Adjust monitoring parameters after failed check."""
       
        self.is_down = True
        self.current_interval = min(self.initial_interval * (3 ** self.consecutive_failures), self.max_interval)
        if self.current_interval < self.max_interval and self.consecutive_failures < 4:
            self.send_email(email_text)
        self.consecutive_failures += 1


    def send_email(self, email_text):
        """Sends an email notification using environment variables for credentials and instance variables for distinct messages."""
        
        msg = MIMEMultipart()
        msg['From'] = os.getenv('SENDER_EMAIL')
        msg['To'] = ", ".join(os.getenv("RECIPIENT_EMAIL", "").split(","))
        msg['Subject'] = f"{str(self.url)} website status alarm: could not reach website"
        
        with open(email_text, "r") as file:
            message = file.read()

        body= message.format(
            url = str(self.url),
            status_code = self.current_status_code,
            interval = self.current_interval // 60
        )

        msg.attach(MIMEText(body, "plain"))
        
        with smtplib.SMTP(os.getenv('SMTP_SERVER'), 587) as server:
            server.starttls()
            server.login(
                os.getenv('SMTP_USERNAME'),
                os.getenv('SMTP_PASSWORD')
            )
            server.send_message(msg)



class MonitoringSystem:
    def __init__(self, websites_file: str):
        self.running = True
        self.websites = self.load_websites(websites_file)
        self.monitors = {
            url: WebsiteChecker(url) 
            for url in self.websites
        }
        self.validate_email_credentials()


    def validate_email_credentials(self):
        """Validates that all required environment variables are set."""
       
        required_vars = [
            'SMTP_SERVER',
            'SMTP_USERNAME',
            'SMTP_PASSWORD',
            'SENDER_EMAIL',
            'RECIPIENT_EMAIL'
        ]
        missing_vars = [var for var in required_vars if not os.getenv(var)]
        if missing_vars:
            raise EnvironmentError(
                f"Missing required environment variables: {', '.join(missing_vars)}"
            )
    

    def load_websites(self, websites_file):
        """loads all websites stored in the websites_file.json file"""
       
        with open(websites_file, "r") as file:
            data = json.load(file)
            return data.get("websites", [])


    def run(self):
        """creates an infinite loop that runs the main program"""
       
        while self.running:
            for _, monitor_instance in self.monitors.items():
                monitor_instance.check_status()



if __name__ == "__main__":
    try:
        load_dotenv()
        monitor_system = MonitoringSystem("website_list.json")
        monitor_system.run()
    except Exception as e:
        raise