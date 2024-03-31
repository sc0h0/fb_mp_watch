import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

def send_test_email():
    mail_email = os.getenv('MAIL_SEND_FROM')  # Using the sender's email for both sending and receiving
    smtp_server = "smtp.fastmail.com"
    port = 587  # TLS port; use 465 for SSL
    mail_app_pw = os.getenv('MAIL_APP_PW')

    message = MIMEMultipart()
    message["From"] = mail_email
    message["To"] = mail_email
    message["Subject"] = "Self Test Email from GitHub Actions"
    
    body = "This is a self-test email sent from a Python script using GitHub Actions secrets."
    message.attach(MIMEText(body, "plain"))

    try:
        server = smtplib.SMTP(smtp_server, port)
        server.starttls()
        server.login(mail_email, mail_app_pw)
        server.sendmail(mail_email, mail_email, message.as_string())
        print("Self-test email sent successfully!")
    except Exception as e:
        print(f"Failed to send self-test email: {e}")
    finally:
        server.quit()
