from rest_framework import generics
from login_app.models import Candidature
from login_app.serializers import CandidatureSerializer
from rest_framework.permissions import IsAuthenticated

class CandidatureListCreateView(generics.ListCreateAPIView):
    queryset = Candidature.objects.all()
    serializer_class = CandidatureSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        # Associer automatiquement le citoyen connecté si nécessaire
        serializer.save()


class CandidatureRetrieveUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Candidature.objects.all()
    serializer_class = CandidatureSerializer
    permission_classes = [IsAuthenticated]
