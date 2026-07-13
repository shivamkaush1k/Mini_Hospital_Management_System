import os
import socket
import smtplib

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from jinja2 import Environment, FileSystemLoader


# --- Force IPv4-only DNS resolution ---
# Render containers often get an IPv6 address with no real outbound IPv6
# route, so smtplib picks the IPv6 candidate first and fails with
# "Network is unreachable". This patches socket.getaddrinfo process-wide
# so every connection (including smtplib's internal one) resolves to
# IPv4 only.
_orig_getaddrinfo = socket.getaddrinfo

def _ipv4_only_getaddrinfo(host, port, family=0, type=0, proto=0, flags=0):
    return _orig_getaddrinfo(host, port, socket.AF_INET, type, proto, flags)

socket.getaddrinfo = _ipv4_only_getaddrinfo
# --- end patch ---


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
        print("SMTP_HOST:", SMTP_HOST)
        print("SMTP_PORT:", SMTP_PORT)
        print("SMTP_USER:", SMTP_USER)
        print("Connecting to SMTP...")
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=30) as server:
            print("SMTP connection opened.")
            server.ehlo()
            print("EHLO OK")

            server.starttls()
            print("TLS started")

            server.ehlo()

            print("Logging in...")
            server.login(SMTP_USER, SMTP_PASSWORD)

            print("Login successful")
            server.sendmail(FROM_EMAIL, recipient, message.as_string())

            print("Mail sent")

    except Exception as e:
        import traceback
        traceback.print_exc()
        raise