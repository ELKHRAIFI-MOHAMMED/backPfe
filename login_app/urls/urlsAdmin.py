from django.urls import path
from login_app.views import viewsAdmin

urlpatterns = [
    path('categories/', viewsAdmin.CategorieListCreateView.as_view(), name='categorie-list-create'),
    path('categories/<int:pk>/', viewsAdmin.CategorieRetrieveUpdateDeleteView.as_view(), name='categorie-detail'),
]
