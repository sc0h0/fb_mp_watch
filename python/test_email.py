import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

# Environment variable for the email
mail_email = os.getenv('MAIL_SEND_FROM')  # Using the sender's email for both sending and receiving

# SMTP server configuration (adjust as needed for your email service)
smtp_server = "smtp.fastmail.com"  # Example: FastMail SMTP server
port = 587  # TLS port; use 465 for SSL

# App password for SMTP authentication
mail_app_pw = os.getenv('MAIL_APP_PW')

# Create a multipart message and set headers
message = MIMEMultipart()
message["From"] = mail_email
message["To"] = mail_email  # Sender and recipient are the same
message["Subject"] = "Self Test Email from GitHub Actions"

# Email body
body = "This is a self-test email sent from a Python script using GitHub Actions secrets."
message.attach(MIMEText(body, "plain"))

# Send the email
try:
    server = smtplib.SMTP(smtp_server, port)
    server.starttls()  # Secure the connection
    server.login(mail_email, mail_app_pw)  # Log in to the SMTP server

    # Send the email
    server.sendmail(mail_email, mail_email, message.as_string())  # From and To are the same
    print("Self-test email sent successfully!")
except Exception as e:
    print(f"Failed to send self-test email: {e}")
finally:
    server.quit()
