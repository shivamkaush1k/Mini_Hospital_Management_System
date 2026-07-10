from datetime import date

from django.core.management.base import BaseCommand

from appointments.models import Appointment
from utils.email_client import send_email


class Command(BaseCommand):
    help = "Send reminder emails for today's appointments"

    def handle(self, *args, **options):

        appointments = Appointment.objects.select_related(
            "patient__user",
            "slot__doctor__user",
        ).filter(
            appointment_date=date.today(),
            status=Appointment.Status.PENDING,
        )

        count = 0

        for appointment in appointments:

            try:

                send_email(
                    trigger="APPOINTMENT_REMINDER",
                    email=appointment.patient.user.email,
                    subject="Appointment Reminder",
                    patient=appointment.patient.user.get_full_name(),
                    doctor=appointment.slot.doctor.user.get_full_name(),
                    date=appointment.appointment_date.strftime("%d %b %Y"),
                    time=appointment.appointment_time.strftime("%I:%M %p"),
                )

                count += 1

            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(
                        f"Failed for {appointment.patient.user.email}: {e}"
                    )
                )

        self.stdout.write(
            self.style.SUCCESS(f"Sent {count} reminder emails.")
        )