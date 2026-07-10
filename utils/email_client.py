import os
import requests

EMAIL_SERVICE_URL = os.getenv(
    "EMAIL_SERVICE_URL",
    "http://localhost:10000/send-email"
)


def send_email(trigger, email, subject="", **kwargs):
    

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
    

def send_email(trigger, email, subject="", **kwargs):

    payload = {
        "trigger": trigger,
        "email": email,
        "subject": subject,
        **kwargs
    }

    print("=" * 50)
    print("EMAIL PAYLOAD")
    print(payload)
    print("=" * 50)

    try:
        response = requests.post(
            EMAIL_SERVICE_URL,
            json=payload,
            timeout=10
        )

        print("STATUS:", response.status_code)
        print("BODY:", response.text)

        return response.json()

    except Exception as e:
        print("EMAIL ERROR:", e)
        raise