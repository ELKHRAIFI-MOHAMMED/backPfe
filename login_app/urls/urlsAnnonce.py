from django.urls import path
from login_app.views import viewsAnnonce

urlpatterns = [
    path('annonces/', viewsAnnonce.AnnonceListCreateView.as_view(), name='annonce-list-create'),
    path('annonces/<int:pk>/', viewsAnnonce.AnnonceRetrieveUpdateDeleteView.as_view(), name='annonce-detail'),
]
