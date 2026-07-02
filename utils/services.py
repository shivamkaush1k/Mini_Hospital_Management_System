from django.db import transaction


class BaseService:
    """
    Base class for reusable business logic.
    """

    @staticmethod
    @transaction.atomic
    def execute(func, *args, **kwargs):
        return func(*args, **kwargs)