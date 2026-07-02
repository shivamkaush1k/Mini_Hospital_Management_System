from rest_framework import serializers
from django.contrib.auth.models import User

from accounts.serializers import UserSerializer
from .models import Doctor


class DoctorSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = Doctor
        fields = "__all__"

    def get_full_name(self, obj):
        return obj.user.get_full_name().strip()