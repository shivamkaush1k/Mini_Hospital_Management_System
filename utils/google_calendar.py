import datetime
import requests
from django.conf import settings


GOOGLE_CALENDAR_API = "https://www.googleapis.com/calendar/v3/calendars/primary/events"


def create_calendar_event(access_token, title, start_time, end_time, description=""):
    """
    Creates an event in Google Calendar
    """

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    event = {
        "summary": title,
        "description": description,
        "start": {
            "dateTime": start_time.isoformat(),
            "timeZone": "Asia/Kolkata"
        },
        "end": {
            "dateTime": end_time.isoformat(),
            "timeZone": "Asia/Kolkata"
        }
    }

    response = requests.post(
        GOOGLE_CALENDAR_API,
        headers=headers,
        json=event
    )

    if response.status_code not in [200, 201]:
        print("Google Calendar Error:", response.text)
        return None

    return response.json()


def create_appointment_events(appointment):
    """
    Creates calendar events for both doctor and patient
    """

    try:
        doctor = appointment.doctor
        patient = appointment.patient

        start_time = appointment.start_time
        end_time = appointment.end_time

        title_for_patient = f"Appointment with Dr. {doctor.user.username}"
        title_for_doctor = f"Appointment with {patient.user.username}"

        # Doctor event
        if hasattr(doctor, "google_access_token") and doctor.google_access_token:
            create_calendar_event(
                doctor.google_access_token,
                title_for_doctor,
                start_time,
                end_time,
                description="Patient consultation"
            )

        # Patient event
        if hasattr(patient, "google_access_token") and patient.google_access_token:
            create_calendar_event(
                patient.google_access_token,
                title_for_patient,
                start_time,
                end_time,
                description="Doctor consultation"
            )

        return True

    except Exception as e:
        print("Calendar integration error:", str(e))
        return False