from django.conf import settings
from django.conf.urls.static import static

from django.contrib import admin
from django.urls import include, path

handler404 = "accounts.views.custom_404"
handler500 = "accounts.views.custom_500"

urlpatterns = [
    path("admin/", admin.site.urls),

    path("", include("accounts.urls")),
    path("doctors/", include("doctors.urls")),
    path("patients/", include("patients.urls")),
    path("appointments/", include("appointments.urls")),
    path("prescriptions/", include("prescriptions.urls")),
     path("api/", include("api.urls")),
]

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT,
    )