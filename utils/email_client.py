import os
import requests

EMAIL_SERVICE_URL = os.getenv(
    "EMAIL_SERVICE_URL",
    "http://localhost:3000/dev/send-email"
)


def send_email(trigger, email, subject="", **kwargs):
    """
    Sends email request to serverless email service.
    
    Args:
        trigger (str): SIGNUP_WELCOME / BOOKING_CONFIRMATION
        email (str): recipient email
        subject (str): email subject
        kwargs: additional template data
    """

    payload = {
        "trigger": trigger,
        "email": email,
        "subject": subject,
        **kwargs
    }

    try:
        response = requests.post(
            EMAIL_SERVICE_URL,
            json=payload,
            timeout=10
        )

        if response.status_code != 200:
            print("Email service error:", response.text)

        return response.json()

    except Exception as e:
        print("Failed to send email:", str(e))
        return {
            "success": False,
            "error": str(e)
        }