from django.contrib.auth.models import User
from rest_framework import serializers
from utils.email_client import send_email
from .models import Profile


class UserSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "first_name",
            "last_name",
            "email",
            "full_name",
            "is_staff",
        )

    def get_full_name(self, obj):
        return obj.get_full_name().strip()


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)

    class Meta:
        model = User
        fields = (
            "username",
            "first_name",
            "last_name",
            "email",
            "password",
        )

    def create(self, validated_data):

        user = User.objects.create_user(**validated_data)

        send_email(
            trigger="SIGNUP_WELCOME",
            email=user.email,
            name=user.get_full_name() or user.username
        )

        return user



class ProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Profile
        fields = "__all__"