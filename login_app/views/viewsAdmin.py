from rest_framework import generics
from login_app.models import Categorie
from login_app.serializers import CategorieSerializer
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from login_app.permissions import IsAdminOrReadOnlyForCitoyenAssociation

class CategorieListCreateView(generics.ListCreateAPIView):
    queryset = Categorie.objects.all()
    serializer_class = CategorieSerializer
    permission_classes = [IsAdminOrReadOnlyForCitoyenAssociation]

class CategorieRetrieveUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Categorie.objects.all()
    serializer_class = CategorieSerializer
    permission_classes = [IsAdminOrReadOnlyForCitoyenAssociation]