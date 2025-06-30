from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import authenticate
from django.utils.translation import gettext_lazy as _
from django.core.validators import ValidationError
from .models import *





User = get_user_model()

class UserSerializerSignUp(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'password', 'type', "is_active")
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email'),  # Corregido: usar get() en lugar de get[]
            password=validated_data['password'],
            type=validated_data['type']
        )
        return user
    
    




class AssociationProfileSignUp(serializers.ModelSerializer):
    reseaux_sociaux = serializers.JSONField(binary=True, required=False)
    
   
    
    class Meta:
        model = AssociationProfile
        fields = ("id","user", 'nom', 'description', 'contact', 'logo', 'reseaux_sociaux', 'feedback')
        extra_kwargs = {
            'logo': {'required': False, 'allow_null': True},
            'reseaux_sociaux': {'required': False},
            'feedback': {'required': False, 'allow_null': True},
            'user': {'required': False},
            'contact': {'required': False},
            'id': {'required': False}
        }
    
    
    def create(self, validated_data):
        request = self.context.get('request')
        if not request or not hasattr(request, 'user'):
            raise serializers.ValidationError("Authentification requise")
            
        # Convertit explicitement le feedback en liste
        feedback_data = validated_data.get('feedback', [])
        if feedback_data is None:
            feedback_data = []
            
            
        associationProfile = AssociationProfile.objects.create(
            id=self.context['request'].user.id,
            user=validated_data['user'],
            nom=validated_data['nom'],
            description=validated_data.get('description', ''),
            contact=validated_data.get('contact', ''),
            logo=validated_data.get('logo'),
            reseaux_sociaux=validated_data.get('reseaux_sociaux', {}),
            feedback=feedback_data  # Stocke directement la liste
        )
        return associationProfile
    
    def update(self, instance, validated_data):
          # Logo
        logo = validated_data.pop('logo', None)
        if logo is not None:
            instance.logo = logo

        # Feedback
        if 'feedback' in validated_data:
            instance.feedback = validated_data['feedback'] or []

        # Autres champs
        for attr, value in validated_data.items():
            if attr not in ['feedback', 'user']:  # Déjà traités séparément
                setattr(instance, attr, value)
        
        instance.save()
        return instance

    
class CitoyenProfileSignUp(serializers.ModelSerializer):
    class Meta:
        model = CitoyenProfile
        fields = ('user', 'nom', 'prenom', 'bio', 'experiences', 'album_photos', 'feedback')
        extra_kwargs = {
            'user': {'required': False, 'allow_null': True},
            'feedback': {'required': False, 'allow_null': True},
            'album_photos': {'required': False, 'allow_null': True},
            'bio': {'required': False, 'allow_null': True},
            'experiences': {'required': False, 'allow_null': True},
        }

    def validate(self, data):
        user = data.get('user')
        if AssociationProfile.objects.filter(user=user).exists():
            raise serializers.ValidationError({
                "user": "Un profil association existe déjà avec cet ID utilisateur."
            })
        return data

    def create(self, validated_data):
        feedback = validated_data.get('feedback', []) or []
        album_photos = validated_data.get('album_photos', []) or []
        bio = validated_data.get('bio', "") or ""
        experiences = validated_data.get('experiences', "") or ""

        citoyen = CitoyenProfile.objects.create(
            id=self.context['request'].user.id,
            user=validated_data['user'],
            nom=validated_data['nom'],
            prenom=validated_data['prenom'],
            bio=bio,
            experiences=experiences,
            album_photos=album_photos,
            feedback=feedback
        )
        return citoyen

    def update(self, instance, validated_data):
        
        for attr, value in validated_data.items():
            if attr not in ['feedback', 'album_photos', 'user']:
                setattr(instance, attr, value)

        instance.save()
        return instance
    
class CategorieSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categorie
        fields = '__all__'



class AnnonceSerializer(serializers.ModelSerializer):
    date_debut = serializers.DateTimeField(
        format="%Y-%m-%dT%H:%M",
        input_formats=["%Y-%m-%dT%H:%M", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M"]
    )
    date_fin = serializers.DateTimeField(
        format="%Y-%m-%dT%H:%M",
        input_formats=["%Y-%m-%dT%H:%M", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M"]
    )
    
    association = serializers.SerializerMethodField()
    class Meta:
        model = Annonce
        fields = '__all__'
        
    def get_association(self, obj):
      try:
        # On récupère directement l'association liée à cette annonce
        profile = obj.association
        return AssociationProfileSignUp(profile).data if profile else None
      except AssociationProfile.DoesNotExist:
        return None

    def create(self, validated_data):
        association = self.context['request'].user.association_profile  # 🔁 Corrigé ici
        annonce = Annonce.objects.create(
            association=association,
            **validated_data
        )
        return annonce
    
class CandidatureSerializer(serializers.ModelSerializer):
    class Meta:
        model = Candidature
        fields = '__all__'
        read_only_fields = ['date_candidature']  # champ auto
        extra_kwargs = {
            'note_engagement': {'required': False, 'allow_null': True}
        }

    def create(self, validated_data):
        citoyen = self.context['request'].user.citoyen_profile
        return Candidature.objects.create(citoyen=citoyen,**validated_data)
    

    
    