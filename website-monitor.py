import requests
import time 
import os
import smtplib
import re
import logging
import signal
import threading
import yaml
from logging.handlers import TimedRotatingFileHandler
from random import randint
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from dotenv import load_dotenv


 
def main():
    monitor = MonitoringSystem()
    monitor.logger.info("starting boot up")
    load_dotenv()
    monitor.logger.info("finished boot up. Starting to check websites.")
    signal.signal(signal.SIGTERM, monitor.shutdown)
    signal.signal(signal.SIGINT, monitor.shutdown)
    try:
        monitor.run()
    except Exception as e:
        monitor.logger.error(f"Fatal error: {e}")
        raise



class MonitoringSystem:
    def __init__(self):
        self.running = True
        self.logger = self.start_logging()
        self.validate_email_credentials()
        self.websites = self.load_websites("websites.yml")
        self.monitors = {
            url: WebsiteChecker(self, url) 
            for url in self.websites
        }


    def start_logging(self):
        os.makedirs("logs", exist_ok=True) 
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.INFO)

        file_handler = TimedRotatingFileHandler(
            f"logs/website-monitor.log",
            when="midnight",
            backupCount=30
        )
        stream_handler = logging.StreamHandler()
 
        formatter = logging.Formatter(
            "%(asctime)s: %(message)s",
            datefmt="%Y.%m.%d %H:%M:%S"
        )
        file_handler.setFormatter(formatter)
        stream_handler.setFormatter(formatter)

        logger.addHandler(file_handler)
        logger.addHandler(stream_handler)

        return logger


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
        """loads all websites stored in the websites.json file"""
       
        with open(websites_file, "r") as file:
            data = yaml.safe_load(file)
            return data.get("websites", [])


    def run(self):
        """creates an infinite loop that runs the main program"""
       
        for url, monitor_instance in self.monitors.items():
            thread = threading.Thread(target=monitor_instance.check_status)
            thread.daemon = True
            thread.start()
            time.sleep(1)
        while self.running:
            time.sleep(5)


    def shutdown(self, signum, frame):
        self.logger.info(f"Received signal {signum}, shutting down gracefully...")
        self.running = False



class WebsiteChecker:
    def __init__(self, parent, url):
        self.url = url
        self.parent = parent
        self.initial_interval = 300
        self.max_interval = 3600
        self.current_interval = self.initial_interval
        self.consecutive_failures = 0
        self.is_down = False
        self.current_status_code = 0


    def check_status(self):
        """Checks website status code and any mentions of errors in the html head of the website."""
        
        while self.parent.running:
            if self.is_down:
                self.parent.logger.info(f"{self.url} was down. Next check in {self.current_interval // 60} minutes and {self.current_interval % 60} seconds.")
                time.sleep(self.current_interval)
            else:
                sleep_interval = randint(300, 600)
                self.parent.logger.info(f"{self.url} was up. Next check in: {sleep_interval // 60} minutes and {sleep_interval % 60} seconds.")
                time.sleep(sleep_interval)
            
            try:
                if self.check_status_code():
                    if self.html_no_errors():
                        if self.is_down:
                            self.handle_success()
                        else:
                            pass
                    else:
                        self.handle_failure("Email_message_html_error.html")
                else:
                    self.handle_failure("Email_message_status_code.html") 
            except Exception as e:
                self.parent.logger.error(f"Error checking {self.url}: {e}")


    def check_status_code(self):
        """checks whether the website returns a html status code between 200 and 399"""
        
        with requests.Session() as session:
            try:
                response = session.head(self.url, timeout=10, allow_redirects=True)
                self.current_status_code = response.status_code
                is_up = 200 <= self.current_status_code < 400
                return is_up
            except Exception:
                self.handle_failure("Email_message_timeout.html")
                return False

 
    def html_no_errors(self):
        """checks whether the website has any mention of 'error' in its head part of the html.
        Returns True if there are no error mentions, returns False if it finds mentions of errors"""

        try:
            head_chunks = []
            with requests.Session() as session:
                with session.get(self.url, stream=True, timeout=10, allow_redirects=True) as response:
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
        except Exception:
            self.handle_failure("Email_message_timeout.html")
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
        msg['Subject'] = f"{str(self.url)} Website Status alarm: Website nicht erreichbar"
        
        with open(email_text, "r", encoding="utf-8") as file:
            message = file.read()

        body= message.format(
            url = str(self.url),
            status_code = self.current_status_code,
            interval = self.current_interval // 60
        )

        msg.attach(MIMEText(body, "html", "utf-8"))
        
        with smtplib.SMTP(os.getenv('SMTP_SERVER'), 587) as server:
            server.starttls()
            server.login(
                os.getenv('SMTP_USERNAME'),
                os.getenv('SMTP_PASSWORD')
            )
            server.send_message(msg)



if __name__ == "__main__":
    main()