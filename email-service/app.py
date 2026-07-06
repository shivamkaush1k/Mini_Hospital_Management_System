from dotenv import load_dotenv
import os

load_dotenv()

print("SMTP_HOST =", os.getenv("SMTP_HOST"))
print("SMTP_USER =", os.getenv("SMTP_USER"))

from flask import Flask, request, jsonify
from utils import render_template, send_email


from dotenv import load_dotenv

load_dotenv()

from flask import Flask, request, jsonify
from utils import render_template, send_email

app = Flask(__name__)


@app.get("/")
def home():
    return jsonify({
        "status": "Email Service Running"
    })


@app.post("/send-email")
def send_email_api():

    body = request.get_json(force=True)

    trigger = body.get("trigger")
    recipient = body.get("email")

    if not recipient:
        return jsonify({
            "success": False,
            "message": "Recipient email is required."
        }), 400

    if trigger == "SIGNUP_WELCOME":

        subject = body.get(
            "subject",
            "Welcome to Mini Hospital Management System"
        )

        html = render_template(
            "signup.html",
            {
                "name": body.get("name", "User")
            }
        )

    elif trigger == "BOOKING_CONFIRMATION":

        subject = body.get(
            "subject",
            "Appointment Confirmation"
        )

        html = render_template(
            "booking.html",
            {
                "patient": body.get("patient", "Patient"),
                "doctor": body.get("doctor", "Doctor"),
                "date": body.get("date", ""),
                "time": body.get("time", "")
            }
        )

    else:
        return jsonify({
            "success": False,
            "message": "Unknown trigger."
        }), 400

    send_email(
        recipient,
        subject,
        html
    )

    return jsonify({
        "success": True,
        "message": "Email sent successfully."
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)