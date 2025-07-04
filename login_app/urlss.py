from django.urls import path
from . import viewss

urlpatterns = [
    # Users
    path('users/', viewss.UserListView1.as_view(), name='user-list'),
    path('users/<int:pk>/', viewss.UserDetailView.as_view(), name='user-detail'),
    path('users/current/', viewss.CurrentUserView.as_view(), name='current-user'),
    # Messages
    path('messages/<int:user_id>/', viewss.MessageHistoryView.as_view(), name='message-history'),
    path('messages/<int:user_id>/send/', viewss.MessageCreateView.as_view(), name='message-send'),
    path('association-with-users/', viewss.ListeAssociations.as_view(), name='association-with-user'),
    path('citoyens/', viewss.listcitoyen.as_view(), name='listcitoyen'),
    path('activer-ou-desactiver-Association/<idasso>', viewss.activeroudesactiverAssociation, name='activeroudesactiverAssociation'),
    path('list-user/', viewss.userActif.as_view(), name='listuser'),
    path('activer-ou-desactiver-citoyen/<idcit>', viewss.activeroudesactivercitoyen, name='activeroudesactivercitoyen'),
]