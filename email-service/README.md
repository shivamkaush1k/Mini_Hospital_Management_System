# Mini HMS Email Service

A standalone Email Microservice for the **Mini Hospital Management System**.

This service is built using **Flask**, **Jinja2**, and **SMTP (Gmail App Password)** to send transactional emails such as:

- Welcome Emails
- Appointment Confirmation Emails

It exposes a simple REST API that can be consumed by the main Django Hospital Management System or any other application.

---

## Features

- REST API using Flask
- HTML email templates with Jinja2
- Gmail SMTP support
- Environment variable configuration
- Ready for deployment on Render
- Easily extensible for additional email templates

---

## Tech Stack

- Python 3
- Flask
- Jinja2
- python-dotenv
- Gunicorn
- SMTP (Gmail)

---

## Project Structure

```
email-service/
│
├── app.py
├── utils.py
├── requirements.txt
├── .env
├── .gitignore
├── README.md
│
├── templates/
│   ├── signup.html
│   └── booking.html
│
└── __init__.py
```

---

## Installation

Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/mini-hms-email-service.git
```

Go into the project

```bash
cd mini-hms-email-service
```

Create a virtual environment

```bash
python -m venv venv
```

Activate it

### Windows

```bash
venv\Scripts\activate
```

### Linux / macOS

```bash
source venv/bin/activate
```

Install dependencies

```bash
pip install -r requirements.txt
```

---

## Environment Variables

Create a `.env` file in the project root.

```env
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your_email@gmail.com
SMTP_PASSWORD=YOUR_GMAIL_APP_PASSWORD
FROM_EMAIL=your_email@gmail.com
```

---

## Run Locally

```bash
python app.py
```

The service starts on

```
http://127.0.0.1:10000
```

---

## API Endpoints

### Health Check

```
GET /
```

Response

```json
{
  "status": "Email Service Running"
}
```

---

### Send Email

```
POST /send-email
```

---

## Signup Welcome Email

Request

```json
{
    "trigger":"SIGNUP_WELCOME",
    "email":"user@example.com",
    "name":"John Doe"
}
```

---

## Appointment Confirmation Email

Request

```json
{
    "trigger":"BOOKING_CONFIRMATION",
    "email":"patient@example.com",
    "patient":"John Doe",
    "doctor":"Dr. Smith",
    "date":"10 July 2026",
    "time":"10:30 AM"
}
```

---

## Successful Response

```json
{
    "success": true,
    "message": "Email sent successfully."
}
```

---

## Supported Email Templates

Currently supported triggers

| Trigger | Description |
|----------|-------------|
| SIGNUP_WELCOME | Sends a welcome email after user registration |
| BOOKING_CONFIRMATION | Sends appointment confirmation email |

---

## Deployment

This service is designed to be deployed independently on **Render**.

### Build Command

```bash
pip install -r requirements.txt
```

### Start Command

```bash
gunicorn app:app
```

Configure the SMTP environment variables in the Render dashboard before deployment.

---

## Integration

The Django Mini HMS project communicates with this service via HTTP requests.

Example:

```python
requests.post(
    "https://your-email-service.onrender.com/send-email",
    json={
        "trigger": "SIGNUP_WELCOME",
        "email": user.email,
        "name": user.first_name,
    },
)
```

---

## Future Enhancements

- Password Reset Emails
- Appointment Cancellation Emails
- Prescription Ready Notifications
- Invoice Emails
- OTP Verification
- Email Logging
- Queue Support (Celery/RabbitMQ)
- AWS SES Integration

---

## License

This project is developed for educational and portfolio purposes.
