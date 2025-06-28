from django.urls import path
from login_app.views import viewsCandidature

urlpatterns = [
    path('candidatures/', viewsCandidature.CandidatureListCreateView.as_view(), name='candidature-list-create'),
    path('candidatures/<int:pk>/', viewsCandidature.CandidatureRetrieveUpdateDeleteView.as_view(), name='candidature-detail'),
]
