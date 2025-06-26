from rest_framework import generics
from login_app.models import Annonce,AssociationProfile
from login_app.serializers import AnnonceSerializer
from login_app.permissions import OnlyAssociationCreate
from rest_framework.response import Response
class AnnonceListCreateView(generics.ListCreateAPIView):
    queryset = Annonce.objects.all()
    serializer_class = AnnonceSerializer
    permission_classes = [OnlyAssociationCreate]
    

class AnnonceRetrieveUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Annonce.objects.all()
    serializer_class = AnnonceSerializer
    permission_classes = [OnlyAssociationCreate]
