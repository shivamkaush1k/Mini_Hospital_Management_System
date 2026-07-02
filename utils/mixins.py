from .helpers import (
    is_admin,
    is_doctor,
    is_patient,
)


class RoleMixin:

    def is_admin(self):
        return is_admin(
            self.request.user
        )

    def is_doctor(self):
        return is_doctor(
            self.request.user
        )

    def is_patient(self):
        return is_patient(
            self.request.user
        )