from rest_framework import status
from rest_framework.exceptions import APIException


class BadRequest(APIException):

    status_code = status.HTTP_400_BAD_REQUEST

    default_detail = "Bad Request."


class Forbidden(APIException):

    status_code = status.HTTP_403_FORBIDDEN

    default_detail = "Permission Denied."


class NotFound(APIException):

    status_code = status.HTTP_404_NOT_FOUND

    default_detail = "Object not found."