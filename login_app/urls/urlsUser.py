from django.urls import path
from login_app.views import viewsUser

urlpatterns = [
    path('signup/', viewsUser.SignUpView.as_view(), name='signup'),
    path('signup/association/', viewsUser.SignUpAssociationView.as_view(), name='signupassociation'),
    path('association/edit/', viewsUser.AssociationProfileUpdateView.as_view(), name='association-profile-update'),
    path('citoyen/edit/', viewsUser.CitoyenProfileUpdateView.as_view(), name='citoyen-profile-update'),
    path('signup/citoyen/', viewsUser.SignUpCitoyenView.as_view(), name='signUpcitoyen'),
    path('login/', viewsUser.LoginView.as_view(), name='login'),
    path('me/', viewsUser.UserDetailView.as_view(), name='user-detail'),
    path('activate/<int:user_id>/', viewsUser.UserStatusView.as_view(), name='toggle_user_status')
]