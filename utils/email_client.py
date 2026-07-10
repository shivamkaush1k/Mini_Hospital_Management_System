import os
import requests

EMAIL_SERVICE_URL = os.getenv(
    "EMAIL_SERVICE_URL",
    "https://mini-hms-email-service.onrender.com/send-email"
)

def send_email(trigger, email, subject="", **kwargs):
    payload = {
        "trigger": trigger,
        "email": email,
        "subject": subject,
        **kwargs,
    }

    print("=" * 50)
    print("EMAIL PAYLOAD")
    print(payload)
    print("=" * 50)

    try:
        response = requests.post(
            EMAIL_SERVICE_URL,
            json=payload,
            timeout=30,
        )

        print("STATUS:", response.status_code)
        print("BODY:", response.text)

        try:
            return response.json()
        except ValueError:
            return {
                "success": False,
                "error": response.text,
            }

    except requests.RequestException as e:
        print("EMAIL ERROR:", e)
        return {
            "success": False,
            "error": str(e),
        }