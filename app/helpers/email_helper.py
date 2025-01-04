import os
import smtplib

from dotenv import load_dotenv
from email.mime.text import MIMEText

load_dotenv()


class Email:
    @staticmethod
    def send_email(to, subject, body):
        sender = os.getenv("EMAIL_SENDER")
        password = os.getenv("EMAIL_PASSWORD")
        smtp_server = os.getenv("SMTP_SERVER")
        smtp_port = os.getenv("SMTP_PORT", 587)

        try:
            msg = MIMEText(body)
            msg["Subject"] = subject
            msg["From"] = sender
            msg["To"] = to

            with smtplib.SMTP(smtp_server, smtp_port) as server:
                server.starttls()
                server.login(sender, password)  # Authentification
                server.sendmail(sender, to, msg.as_string())  # Sending
        except smtplib.SMTPAuthenticationError:
            raise Exception("SMTP Authentication Error: Check your email or password.")
        except smtplib.SMTPException as e:
            raise Exception(f"SMTP Error: {str(e)}")
        except Exception as e:
            raise Exception(f"Error sending email: {str(e)}")
