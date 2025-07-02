from django.urls import path
from . import views

urlpatterns = [
    # Users
    path('users/', views.UserListView.as_view(), name='user-list'),
    path('users/<int:pk>/', views.UserDetailView.as_view(), name='user-detail'),
    path('users/current/', views.CurrentUserView.as_view(), name='current-user'),
    # Messages
    path('messages/<int:user_id>/', views.MessageHistoryView.as_view(), name='message-history'),
    path('messages/<int:user_id>/send/', views.MessageCreateView.as_view(), name='message-send'),
]