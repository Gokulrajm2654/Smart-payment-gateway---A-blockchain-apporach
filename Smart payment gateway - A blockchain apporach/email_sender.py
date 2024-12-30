# email_sender.py
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import db_conns

def send_confirmation_email(receiver_email, username):
    sender_email = "gokulrajm2021@gmail.com"  # Replace with your email
    sender_password = "xzec gcgt omdu mnyr"  # Replace with your email password

    subject = "Account Creation Confirmation"
    body = f"""
    Dear {username},

    You have successfully created an account on the Smart Payment Gateway.

    If you have any questions or need further assistance, please do not hesitate to contact us.

    Best regards,
    Smart Payment Gateway Team
    """

    # Create the email
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    try:
        # Connect to the SMTP server
        server = smtplib.SMTP('smtp.gmail.com', 587)  # Example for Gmail
        server.starttls()
        server.login(sender_email, sender_password)
        server.send_message(msg)
        print("Email sent successfully.")
    except Exception as e:
        print(f"Error occurred: {e}")
    finally:
        server.quit()

def send_reset_email(receiver_email, reset_link):
    sender_email = "gokulrajm2021@gmail.com"  # Replace with your email
    sender_password = "xzec gcgt omdu mnyr"  # Replace with your email password

    subject = "Password Reset Request"
    body = f"""
    Hi there,

    You requested a password reset for your account on the Smart Payment Gateway. 
    Please click the link below to reset your password:

    {reset_link}

    If you did not request a password reset, please ignore this email.

    Best regards,
    Smart Payment Gateway Team
    """

    # Create the email
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    try:
        # Connect to the SMTP server
        server = smtplib.SMTP('smtp.gmail.com', 587)  # Example for Gmail
        server.starttls()
        server.login(sender_email, sender_password)
        server.send_message(msg)
        print("Reset email sent successfully.")
    except Exception as e:
        print(f"Error occurred: {e}")
    finally:
        server.quit()

def send_alert_email(username):
    # You need to fetch the user's email address from the database
    receiver_email = db_conns.get_user_email(username)  # Implement this function to fetch email
    sender_email = "gokulrajm2021@gmail.com"
    sender_password = "xzec gcgt omdu mnyr"

    subject = "Security Alert: Multiple Failed Login Attempts"
    body = f"""
    Dear {username},

    We noticed multiple failed login attempts (3 or more) to your account on the Smart Payment Gateway.
    
    If this wasn't you, we recommend that you reset your password immediately to ensure the security of your account.

    Best regards,
    Smart Payment Gateway Team
    """

    # Create the email
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, sender_password)
        server.send_message(msg)
        print("Alert email sent successfully.")
    except Exception as e:
        print(f"Error occurred: {e}")
    finally:
        server.quit()
