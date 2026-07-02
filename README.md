# Mini Hospital Management System (HMS)

A Django-based Hospital Management System developed as part of the Backend Engineering (Python Serverless) shortlisting task.

The application enables doctors to manage their availability and patients to book appointments. It also integrates Google Calendar for appointment scheduling and uses a separate Python Serverless service for email notifications.

---

# Features

## Authentication

* Doctor Registration
* Patient Registration
* Secure Login/Logout
* Session Authentication
* Password Hashing
* Role-Based Access Control

## Doctor Features

* Doctor Dashboard
* Profile Management
* Create Availability Slots
* Update/Delete Slots
* View Upcoming Appointments
* Appointment Statistics

## Patient Features

* Patient Dashboard
* Browse Doctors
* View Available Time Slots
* Book Appointment
* View Appointment History
* Cancel Appointment

## Appointment Management

* One appointment per available slot
* Automatic slot blocking after booking
* Race-condition safe booking using database transactions
* Appointment status tracking

## Google Calendar Integration

* OAuth2 authentication
* Creates events in both doctor and patient calendars
* Automatic event generation after successful booking

## Email Notifications

A separate Serverless Python service sends:

* SIGNUP_WELCOME email
* BOOKING_CONFIRMATION email

The Django application communicates with the Serverless service over HTTP using `serverless-offline`.

---

# Technology Stack

| Component        | Technology                    |
| ---------------- | ----------------------------- |
| Backend          | Django                        |
| ORM              | Django ORM                    |
| Database         | PostgreSQL                    |
| Authentication   | Django Session Authentication |
| API              | Django REST Framework         |
| Calendar         | Google Calendar API           |
| OAuth            | OAuth2                        |
| Email Service    | Python Serverless Framework   |
| Local Serverless | serverless-offline            |

---

# Project Structure

```text
mini-hms/
│
├── README.md
├── API_DOCUMENTATION.md
├── ARCHITECTURE.md
├── requirements.txt
├── .env.example
│
├── ai-tool-usage-log/
│
├── hms/
│   ├── accounts/
│   ├── doctors/
│   ├── patients/
│   ├── appointments/
│   ├── prescriptions/
│   ├── services/
│   └── ...
│
└── email-service/
    ├── handler.py
    ├── serverless.yml
    └── ...
```

---

# Setup and Run

## 1. Clone Repository

```bash
git clone <repository-url>
cd mini-hms
```

---

## 2. Create Virtual Environment

### Windows

```bash
python -m venv venv

venv\Scripts\activate
```

### Linux / macOS

```bash
python3 -m venv venv

source venv/bin/activate
```

---

## 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

## 4. Configure Environment Variables

Copy the example environment file.

```bash
cp .env.example .env
```

Update the values for:

* Django Secret Key
* PostgreSQL Credentials
* Google OAuth Credentials
* SMTP Credentials
* Serverless Email URL

---

## 5. PostgreSQL Database

Create a PostgreSQL database.

Example:

```text
Database Name : hms_db
Username      : postgres
Password      : ********
```

---

## 6. Apply Migrations

```bash
python manage.py makemigrations

python manage.py migrate
```

---

## 7. Create Superuser

```bash
python manage.py createsuperuser
```

---

## 8. Run Django

```bash
python manage.py runserver
```

The application will be available at:

```text
http://127.0.0.1:8000/
```

---

## 9. Run the Serverless Email Service

Navigate to the email service directory.

```bash
cd email-service
```

Install dependencies.

```bash
npm install

pip install -r requirements.txt
```

Run locally.

```bash
serverless offline
```

The email service will be available at:

```text
http://localhost:3000
```

---

## 10. Google Calendar Setup

1. Create a Google Cloud Project.
2. Enable the Google Calendar API.
3. Configure the OAuth Consent Screen.
4. Create OAuth2 credentials.
5. Add the Client ID and Client Secret to `.env`.
6. Authorize doctor and patient accounts through the application.

---

# System Architecture

The application follows a modular architecture where each domain is isolated into its own Django application.

* **accounts** handles authentication and user roles.
* **doctors** manages doctor profiles and availability.
* **patients** manages patient profiles.
* **appointments** handles booking, scheduling, and concurrency control.
* **prescriptions** stores prescriptions linked to appointments.
* **services** contains integrations such as Google Calendar and the email client.

The email notification system is implemented as an independent Python Serverless application. Instead of sending emails directly, Django makes an HTTP POST request to the local Serverless endpoint. The Serverless function validates the payload and sends emails using SMTP. This separation keeps the web application focused on business logic while the email service handles notification delivery.

Google Calendar integration is isolated within the service layer. After a successful booking, the application retrieves the OAuth credentials for both users and creates calendar events using the Google Calendar API.

Role-based access is enforced using Django authentication, custom permission classes, decorators, and model ownership checks. Doctors can only manage their own availability and appointments, while patients can only book appointments and view their own records.

---

# The Design Decision

## Problem

A critical requirement was preventing two patients from booking the same appointment slot simultaneously.

If two booking requests arrive at nearly the same time, simply checking whether a slot is available is not sufficient because both requests may read the same database state before either updates it.

## Option 1

Check whether `slot.is_booked` is `False`, then create the appointment.

Although simple, this approach is vulnerable to race conditions and can result in duplicate bookings under concurrent requests.

## Option 2 (Chosen)

Wrap the booking logic inside `transaction.atomic()` and retrieve the slot using `select_for_update()`.

This acquires a database lock on the selected slot while the transaction is executing. Any concurrent transaction attempting to book the same slot must wait until the first transaction completes.

## Why This Approach Was Chosen

Using database-level locking provides strong consistency guarantees without introducing unnecessary application complexity. It is supported by Django's ORM, scales well with PostgreSQL, and ensures that only one appointment can ever be created for a given availability slot.

---

# Limitations

This project is intended as a local demonstration and is not production-ready.

Current limitations include:

* Gmail SMTP is used instead of a dedicated email provider.
* OAuth tokens are stored locally and should be encrypted in production.
* Session authentication is suitable for server-rendered applications but JWT would be preferable for public APIs.
* File uploads are stored locally instead of using cloud object storage.
* Background jobs and retry mechanisms are not implemented.
* Monitoring, logging, and rate limiting are minimal.
* Automated test coverage can be expanded further.
* Horizontal scaling considerations have not been implemented.

---

# API Documentation

Detailed endpoint documentation is available in:

```text
API_DOCUMENTATION.md
```

---

# License

This project was developed solely for the Backend Engineering Shortlisting Task and is intended for educational and evaluation purposes.
#   M i n i _ H o s p i t a l _ M a n a g m n t _ S y s t e m  
 