import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

def send_alert_email(item_id):
    # Environment variables for email credentials and addresses
    mail_email = os.getenv('MAIL_SEND_FROM')  # Your email address
    mail_password = os.getenv('MAIL_APP_PW')  # Your email app password
    receiver_email = os.getenv('MAIL_SEND_TO')  # Where you want to receive the alert

    # SMTP server configuration
    smtp_server = "smtp.yourprovider.com"  # Change this to your email provider's SMTP server
    port = 587  # Most providers use port 587 for TLS

    # Create the email message
    message = MIMEMultipart("alternative")
    message["Subject"] = "Marketplace Item Alert"
    message["From"] = mail_email
    message["To"] = receiver_email

    # Email body - HTML version
    html = f"""\
    <html>
      <body>
        <p>Hi,<br>
           Check out this Marketplace item: <a href="https://www.facebook.com/marketplace/item/{item_id}">Item Link</a>
        </p>
      </body>
    </html>
    """

    # Turn the HTML into a MIMEText object
    part2 = MIMEText(html, "html")
    message.attach(part2)

    # Send the email
    try:
        server = smtplib.SMTP(smtp_server, port)
        server.starttls()  # Secure the connection
        server.login(mail_email, mail_password)
        server.sendmail(mail_email, receiver_email, message.as_string())
        print("Alert email sent successfully!")
    except Exception as e:
        print(f"Failed to send alert email: {e}")
    finally:
        server.quit()
