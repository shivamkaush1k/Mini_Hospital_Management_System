import json

from utils import render_template, send_email


def send_email_handler(event, context):
    try:
        body = json.loads(event.get("body", "{}"))

        trigger = body.get("trigger")
        recipient = body.get("email")

        if not recipient:
            return {
                "statusCode": 400,
                "body": json.dumps({
                    "success": False,
                    "message": "Recipient email is required."
                }),
            }

        if trigger == "SIGNUP_WELCOME":

            subject = body.get(
                "subject",
                "Welcome to Mini Hospital Management System"
            )

            html = render_template(
                "signup.html",
                {
                    "name": body.get("name", "User"),
                },
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
                    "time": body.get("time", ""),
                },
            )

        else:
            return {
                "statusCode": 400,
                "body": json.dumps({
                    "success": False,
                    "message": "Unknown trigger."
                }),
            }

        send_email(
            recipient,
            subject,
            html,
        )

        return {
            "statusCode": 200,
            "body": json.dumps({
                "success": True,
                "message": "Email sent successfully."
            }),
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({
                "success": False,
                "message": str(e)
            }),
        }