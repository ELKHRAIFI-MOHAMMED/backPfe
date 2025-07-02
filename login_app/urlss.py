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
]