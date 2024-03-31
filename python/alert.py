import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

def send_alert_email(item_id):
    # Environment variables for email credentials and addresses
    mail_email = os.getenv('MAIL_SEND_FROM')  # Your email address
    mail_password = os.getenv('MAIL_APP_PW')  # Your email app password

    # SMTP server configuration
    smtp_server = "smtp.fastmail.com"
    port = 587  # TLS port; use 465 for SSL

    # Create the email message
    message = MIMEMultipart("alternative")
    message["Subject"] = "Marketplace Item Alert"
    message["From"] = mail_email
    message["To"] = mail_email  # Sending to self for testing; replace with actual recipient if needed

    # Email body - HTML version
    html = f"""\
    <html>
      <body>
        <p>Hi,<br>
           Check out this Grange Marketplace item: <a href="https://www.facebook.com/marketplace/item/{item_id}">Item Link</a>
        </p>
      </body>
    </html>
    """

    # Turn the HTML into a MIMEText object
    part = MIMEText(html, "html")
    message.attach(part)

    # Send the email
    try:
        server = smtplib.SMTP(smtp_server, port)
        server.starttls()  # Secure the connection
        server.login(mail_email, mail_password)
        server.sendmail(mail_email, mail_email, message.as_string())  # For alert, you may want to send it to a different email
        print("Alert email sent successfully!")
    except Exception as e:
        print(f"Failed to send alert email: {e}")
    finally:
        server.quit()

# To send an alert, call send_alert_email with a specific item_id, for example:
# send_alert_email('123456789012345')
