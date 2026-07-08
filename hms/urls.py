from django.conf import settings
from django.conf.urls.static import static
import uuid
from django.contrib import admin
from django.urls import include, path
from patients import views
handler404 = "accounts.views.custom_404"
handler500 = "accounts.views.custom_500"
urlpatterns = [
    path("admin/", admin.site.urls),

    path("", include("accounts.urls")),
    path("<uuid:pk>/", views.patient_detail, name="patient_detail"),
    path("doctors/", include("doctors.urls")),
    path("patients/", include("patients.urls")),
    path("appointments/", include("appointments.urls")),
    path("prescriptions/", include("prescriptions.urls")),
     path("api/", include("api.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])