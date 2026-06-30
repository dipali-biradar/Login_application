
import os
import smtplib
from email.message import EmailMessage
# pyrefly: ignore [missing-import]
from dotenv import load_dotenv

load_dotenv()

from utils.logger import logger

SMTP_EMAIL = os.getenv("SMTP_EMAIL")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")

if not SMTP_EMAIL or not SMTP_PASSWORD:
    logger.error("SMTP credentials not set in environment variables")
    raise ValueError("SMTP credentials not set in environment variables")

logger.info(f"Email service initialized with SMTP email: {SMTP_EMAIL}")


# VERIFY EMAIL


def send_verification_email(email: str, token: str):
    logger.info("Entering send_verification_email()")
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
        logger.debug(f"Attempting to send verification email to {email}")
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(SMTP_EMAIL, SMTP_PASSWORD)
            smtp.send_message(msg)
        logger.info(f"Verification email sent successfully to {email}")
    except Exception as e:
        logger.error(f"Failed to send verification email to {email}: {str(e)}")
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
        logger.debug(f"Attempting to send password reset email to {email}")
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(SMTP_EMAIL, SMTP_PASSWORD)
            smtp.send_message(msg)
        logger.info(f"Password reset email sent successfully to {email}")
    except Exception as e:
        logger.error(f"Failed to send password reset email to {email}: {str(e)}")
        raise Exception(f"Reset email failed: {str(e)}")

