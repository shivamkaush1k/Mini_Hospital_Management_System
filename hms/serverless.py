import requests
from django.conf import settings


class ServerlessEmailClient:
    """
    Client to communicate with Serverless Email Service
    """

    def __init__(self):
        # URL of your serverless-offline endpoint
        # Example: http://localhost:3000/send-email
        self.base_url = getattr(
            settings,
            "SERVERLESS_EMAIL_URL",
            "http://localhost:3000"
        )

    def send_email(self, trigger, email, subject, **kwargs):
        """
        Sends request to serverless email function
        """

        payload = {
            "trigger": trigger,
            "email": email,
            "subject": subject,
            "data": kwargs
        }

        try:
            response = requests.post(
                f"{self.base_url}/send-email",
                json=payload,
                timeout=5
            )

            if response.status_code not in [200, 201]:
                print("Serverless email error:", response.text)
                return False

            return True

        except Exception as e:
            print("Email service unreachable:", str(e))
            return False


# Singleton instance (used everywhere in Django)
email_client = ServerlessEmailClient()