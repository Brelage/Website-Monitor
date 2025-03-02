import requests
import time 
import os
import json
from random import randint, uniform
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from dotenv import load_dotenv


class WebsiteChecker:
    # creates an object per website and checks itself
    def __init__(self, url, initial_interval: int = 300):
        self.url = url
        self.initial_interval = initial_interval
        self.current_interval = initial_interval
        self.max_interval = 3600
        self.consecutive_failures = 0
        self.is_down = False
        self.current_status_code = 0

    def check_status(self) -> bool:
        """Check website status with improved error handling."""
        
        if self.is_down:
            time.sleep(min(60 * (2 ** self.consecutive_failures), self.max_interval))
        else:
            time.sleep(randint(300, 600))
        
        try:
            with requests.Session() as session:
                session.headers.update({
                    'User-Agent': 'Website-Monitor/1.0'
                    }) 
                response = session.head(
                    self.url,
                    timeout=10,
                    allow_redirects=True
                )
                self.current_status_code = response.status_code
                
                is_up = 200 <= self.current_status_code < 400
                if is_up:
                    if self.is_down:
                        self.handle_success()
                    else:
                        pass
                else:
                    self.handle_failure() 
                return is_up
                
        except:
            self.handle_failure()
            return False


    def handle_success(self):
        """reset monitoring parameters after successful check."""
        self.is_down = False
        self.consecutive_failures = 0
        self.current_interval = self.initial_interval


    def handle_failure(self):
        """Adjust monitoring parameters after failed check."""
        self.is_down = True
        self.consecutive_failures += 1
        jitter = uniform(0.8, 1.2)
        self.current_interval = min(
            self.initial_interval * (2 ** self.consecutive_failures) * jitter,
            self.max_interval
        )
        if self.current_interval < self.max_interval:
            self.send_email()


    def send_email(self):
        """Sends an email notification using environment variables for credentials and instance variables for distinct messages."""
        
        msg = MIMEMultipart()
        msg['From'] = os.getenv('SENDER_EMAIL')
        msg['To'] = ", ".join(os.getenv("RECIPIENT_EMAIL", "").split(","))
        msg['Subject'] = f"{str(self.url)} website status alarm: could not reach website"
        
        with open("Email_message.txt", "r") as file:
            message = file.read()

        body= message.format(
            url = str(self.url),
            status_code = self.current_status_code,
            interval = int(self.current_interval) // 60
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