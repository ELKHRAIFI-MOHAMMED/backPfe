from django.urls import path
from .views import SignUpView,UserDetailView,LoginView,SignUpAssociationView,SignUpCitoyenView,UserStatusView,AssociationProfileUpdateView,CitoyenProfileUpdateView

urlpatterns = [
    path('signup/', SignUpView.as_view(), name='signup'),
    path('signup/association/', SignUpAssociationView.as_view(), name='signupassociation'),
    path('association/edit/', AssociationProfileUpdateView.as_view(), name='association-profile-update'),
    path('citoyen/edit/', CitoyenProfileUpdateView.as_view(), name='citoyen-profile-update'),
    path('signup/citoyen/', SignUpCitoyenView.as_view(), name='signUpcitoyen'),
    path('login/', LoginView.as_view(), name='login'),
    path('me/', UserDetailView.as_view(), name='user-detail'),
    path('activate/<int:user_id>/', UserStatusView.as_view(), name='toggle_user_status')
]