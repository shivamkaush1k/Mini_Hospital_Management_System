from rest_framework import viewsets
from .models import Patient, MedicalHistory
from .serializers import PatientSerializer, MedicalHistorySerializer

class PatientViewSet(viewsets.ModelViewSet):
    queryset = Patient.objects.select_related("user")
    serializer_class = PatientSerializer


class MedicalHistoryViewSet(viewsets.ModelViewSet):
    serializer_class = MedicalHistorySerializer

    def get_queryset(self):
        return MedicalHistory.objects.filter(patient_id=self.kwargs["patient_pk"])