
import os
import smtplib
from email.message import EmailMessage
from dotenv import load_dotenv

load_dotenv()

SMTP_EMAIL = os.getenv("SMTP_EMAIL")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")

if not SMTP_EMAIL or not SMTP_PASSWORD:
    raise ValueError("SMTP credentials not set in environment variables")


# VERIFY EMAIL


def send_verification_email(email: str, token: str):
    verify_link = f"http://127.0.0.1:8000/verify-email/{token}"

    msg = EmailMessage()
    msg["Subject"] = "Verify Your Account"
    msg["From"] = SMTP_EMAIL
    msg["To"] = email

    msg.set_content(f"""
Welcome!

Click below to verify your account:

{verify_link}
""")

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(SMTP_EMAIL, SMTP_PASSWORD)
            smtp.send_message(msg)
    except Exception as e:
        raise Exception(f"Verification email failed: {str(e)}")


# RESET PASSWORD EMAIL


def send_reset_email(email: str, token: str):
    reset_link = f"{FRONTEND_URL}/reset-password/{token}"

    msg = EmailMessage()
    msg["Subject"] = "Reset Password"
    msg["From"] = SMTP_EMAIL
    msg["To"] = email

    msg.set_content(f"""
Reset your password:

{reset_link}
""")

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(SMTP_EMAIL, SMTP_PASSWORD)
            smtp.send_message(msg)
    except Exception as e:
        raise Exception(f"Reset email failed: {str(e)}")

