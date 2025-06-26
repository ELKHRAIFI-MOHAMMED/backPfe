from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import api_view, permission_classes
from rest_framework_simplejwt.views import TokenObtainPairView
from login_app.serializers import UserSerializerSignUp,AssociationProfileSignUp,CitoyenProfileSignUp
from rest_framework_simplejwt.tokens import RefreshToken
from login_app.models import  *
from django.contrib.auth import authenticate
from rest_framework.permissions import IsAuthenticated
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.core.files.storage import default_storage
import json
import os
import uuid
from datetime import datetime








User = get_user_model()
class SignUpView(generics.CreateAPIView):
    serializer_class = UserSerializerSignUp
    
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        # 1. Create the user
        user = serializer.save()
        
        # 2. Authenticate the newly created user
        authenticated_user = authenticate(
            username=request.data.get('username'),
            password=request.data.get('password')
        )
        
        if not authenticated_user:
            return Response(
                {"error": "Authentication failed after signup"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        # 3. Generate JWT tokens
        refresh = RefreshToken.for_user(authenticated_user)
        
        # 4. Return both user data and tokens
        return Response({
            "user": UserSerializerSignUp(user, context=self.get_serializer_context()).data,
            "access": str(refresh.access_token),  # Convert to string
            "refresh": str(refresh),  # Convert to string
            "message": "User created and logged in successfully",
        }, status=status.HTTP_201_CREATED)
    


class LoginView(APIView):
    def post(self, request):
        username_email = request.data.get('username_email')
        password = request.data.get('password')

        # Vérification si c'est un email
        is_email = False
        try:
            validate_email(username_email)
            is_email = True
        except ValidationError:
            pass  

        # Authentification
        if is_email:
           
            user = authenticate(request, email=username_email, password=password)
        else:
            
            user = authenticate(request, username=username_email, password=password)
        
        if not user:
            return Response(
                {"error": "Email ou mot de passe incorrect"}, 
                status=status.HTTP_401_UNAUTHORIZED
            )

        # Génération des tokens JWT
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)

        # Réponse avec token + infos utilisateur
        return Response({
            'access': access_token,
            'refresh': str(refresh),
            'user': {
                'id': user.id,
                'email': user.email,
                'username': user.username,
                'type': user.type,  # Champ personnalisé de votre modèle
            }
        }, status=status.HTTP_200_OK)

class UserDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)


class SignUpAssociationView(generics.CreateAPIView):
    serializer_class = AssociationProfileSignUp
    permission_classes = [IsAuthenticated]
    def post(self, request, *args, **kwargs):
        userConnecte = request.user  
        
        if userConnecte.type != "ASSOCIATION":
            return Response(
                {"detail": "Seuls les utilisateurs de type 'ASSOCIATION' peuvent créer un profil association."},
                status=status.HTTP_403_FORBIDDEN
                )
            
        files = request.FILES.getlist('logo') # récupère les fichiers envoyés
        logo = []
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        for image_file in files:
            ext = os.path.splitext(image_file.name)[1]  # ex: ".jpg"
            unique_id = uuid.uuid4().hex[:8]
            new_filename = f"media/logos/{timestamp}_{unique_id}{ext}"
            path = default_storage.save(f'logos/{new_filename}', image_file)
            logo.append(path) 
        data = request.data.copy()
        data["user"] = userConnecte.id
        data['feedback'] = json.dumps([])
        if len(logo)!=0:
            data["logo"]=str(logo[0])
        
        serializer = self.get_serializer(data=data, context={'request': request})
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        # 1. Création du profil (et de l'utilisateur associé si votre serializer le gère)
        profile = serializer.save()
        
        # 2. Désactivation de l'utilisateur APRÈS la création du profil
        user = profile.user  # Supposant que votre modèle AssociationProfile a une ForeignKey vers User
        user.is_active = False
        user.save()
        
        return Response({
            "AssociationProfile":"request.user.id",
            "message": "Profil d'association créé avec succès. Compte utilisateur désactivé.",
        }, status=status.HTTP_201_CREATED)
    
class AssociationProfileUpdateView(generics.RetrieveUpdateAPIView):
    queryset = AssociationProfile.objects.all()
    serializer_class = AssociationProfileSignUp
    permission_classes = [IsAuthenticated]

    def get_object(self):
        # Récupère le profil de l'association de l'utilisateur connecté
        return get_object_or_404(AssociationProfile, user=self.request.user)

    def update(self, request, *args, **kwargs):
        profile = AssociationProfile.objects.get(user=request.user)
        data = request.data.copy()

        # Vérifie s'il y a un nouveau fichier "logo" envoyé
        new_logo_files = request.FILES.getlist('logo')
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        if new_logo_files:
            # Supprimer l'ancien logo du dossier si présent
            if profile.logo and default_storage.exists(profile.logo):
                default_storage.delete(profile.logo)

            # Enregistrer le nouveau logo
            new_logo_file = new_logo_files[0]
            ext = os.path.splitext(new_logo_file.name)[1]  # ex: ".jpg"
            unique_id = uuid.uuid4().hex[:8]
            new_filename = f"media/logos/{timestamp}_{unique_id}{ext}"
            path = default_storage.save(f'logos/{new_filename}', new_logo_file)
            data['logo'] = str(path)
            

        serializer = self.get_serializer(profile, data=data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        return Response({
            "message": "Profil mis à jour avec succès.",
            "logo": serializer.data.get("logo")
        })


class SignUpCitoyenView(generics.CreateAPIView):
    serializer_class = CitoyenProfileSignUp
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        user_connecte = request.user
        
        
        if user_connecte.type != "CITOYEN":
            return Response(
                {"detail": "Seuls les utilisateurs de type 'CITOYEN' peuvent créer un profil citoyen."},
                status=status.HTTP_403_FORBIDDEN
                )
        
        # 1. Traiter les fichiers reçus dans album_photos[]

        files = request.FILES.getlist('album_photos') # récupère les fichiers envoyés
        
        album_photo_paths = []
        for image_file in files:
            filename = default_storage.save(f'album_photos/{image_file.name}', image_file)
            album_photo_paths.append(filename)
            
            
       
        
        
        # 2. Ajouter user et album_photos au data
        data = request.data.copy()
        data['user'] = user_connecte.id
        data['album_photos'] =json.dumps(album_photo_paths) # très important si plusieurs fichiers
        data['feedback'] =json.dumps([])
        serializer = self.get_serializer(data=data, context={'request': request})
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # 3. Créer le profil
        profile = serializer.save()

        # 4. Désactiver le compte utilisateur
        user = profile.user
        user.is_active = False
        user.save()

        return Response({
            "CitoyenProfile": profile.id,
            "message": "Profil citoyen créé avec succès. Compte utilisateur désactivé.",
        }, status=status.HTTP_201_CREATED)
    
class CitoyenProfileUpdateView(generics.RetrieveUpdateAPIView):
    queryset = CitoyenProfile.objects.all()
    serializer_class = CitoyenProfileSignUp
    permission_classes = [IsAuthenticated]

    def get_object(self, request):
        # Récupère le profil de l'association de l'utilisateur connecté
        return get_object_or_404(CitoyenProfile, user=self.request.user)



class UserStatusView(APIView):
    permission_classes = [IsAuthenticated]  # Seul un utilisateur authentifié peut accéder

    def post(self, request, user_id):
        try:
            user = User.objects.get(pk=user_id)
            
            # Empêcher un admin de se désactiver lui-même
            if user == request.user and request.user.type != "ADMIN":
                return Response(
                    {"error": "You cannot deactivate yourself and not Admin"},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            # Basculer le statut is_active
            user.is_active = not user.is_active
            user.save()
            
            return Response({
                "id": user.id,
                "username": user.username,
                "new_status": "active" if user.is_active else "inactive",
                "message": "User status updated successfully"
            }, status=status.HTTP_200_OK)
            
        except User.DoesNotExist:
            return Response(
                {"error": "User not found"},
                status=status.HTTP_404_NOT_FOUND
            )