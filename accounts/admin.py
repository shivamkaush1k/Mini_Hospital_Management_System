from django.contrib import admin
from .models import Profile


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):

    list_display = (
        "user",
        "role",
        "phone",
        "city",
        "country",
    )

    list_filter = (
        "role",
        "gender",
        "country",
    )

    search_fields = (
        "user__username",
        "user__first_name",
        "user__last_name",
        "user__email",
        "phone",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
    )

    ordering = (
        "user__username",
    )