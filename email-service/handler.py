import json

from utils import render_template, send_email


def send_email_handler(event, context):
    try:
        body = json.loads(event.get("body", "{}"))

        trigger = body.get("trigger")
        recipient = body.get("email")
        subject = body.get("subject", "")

        if trigger == "SIGNUP_WELCOME":
            html = render_template(
                "signup.html",
                {
                    "name": body.get("name", "User")
                },
            )

        elif trigger == "BOOKING_CONFIRMATION":
            html = render_template(
                "booking.html",
                {
                    "patient": body.get("patient"),
                    "doctor": body.get("doctor"),
                    "date": body.get("date"),
                    "time": body.get("time"),
                },
            )

        else:
            return {
                "statusCode": 400,
                "body": json.dumps(
                    {
                        "success": False,
                        "message": "Unknown trigger"
                    }
                ),
            }

        send_email(
            recipient,
            subject,
            html,
        )

        return {
            "statusCode": 200,
            "body": json.dumps(
                {
                    "success": True,
                    "message": "Email sent successfully",
                }
            ),
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps(
                {
                    "success": False,
                    "message": str(e),
                }
            ),
        }