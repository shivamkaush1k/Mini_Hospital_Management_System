import os
import smtplib

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from jinja2 import Environment, FileSystemLoader


SMTP_HOST = os.environ["SMTP_HOST"]
SMTP_PORT = int(os.environ["SMTP_PORT"])
SMTP_USER = os.environ["SMTP_USER"]
SMTP_PASSWORD = os.environ["SMTP_PASSWORD"]
FROM_EMAIL = os.environ["FROM_EMAIL"]


env = Environment(
    loader=FileSystemLoader("templates")
)


def render_template(template_name, context):

    template = env.get_template(template_name)

    return template.render(**context)


def send_email(recipient, subject, html):
    message = MIMEMultipart("alternative")

    message["Subject"] = subject
    message["From"] = FROM_EMAIL
    message["To"] = recipient

    message.attach(MIMEText(html, "html"))

    try:
        print("Connecting to SMTP...")

        with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=30) as server:
            server.ehlo()
            server.starttls()
            server.ehlo()

            print("Logging in...")
            server.login(SMTP_USER, SMTP_PASSWORD)

            print("Sending email...")
            server.sendmail(
                FROM_EMAIL,
                recipient,
                message.as_string()
            )

            print("Email sent successfully.")

    except Exception as e:
        import traceback
        traceback.print_exc()
        raise