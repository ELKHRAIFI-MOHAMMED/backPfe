from django.db import models

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _

class User(AbstractUser):
    class UserType(models.TextChoices):
        ADMIN = "ADMIN", _("Admin")
        ASSOCIATION = "ASSOCIATION", _("Association")
        CITOYEN = "CITOYEN", _("Citoyen")
    
    type = models.CharField(max_length=20, choices=UserType.choices)
    # is_active et date_joined sont déjà inclus dans AbstractUser

    def __str__(self):
        return self.username


class AssociationProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='association_profile')
    nom = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    contact = models.CharField(max_length=255)
    logo = models.ImageField(upload_to='logos/', blank=True, null=True)
    reseaux_sociaux = models.JSONField(blank=True, null=True)  # ou TextField selon ta préférence
    feedback =models.TextField(blank=True, null=True)

    def __str__(self):
        return self.nom


class CitoyenProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='citoyen_profile')
    prenom = models.CharField(max_length=100)
    nom = models.CharField(max_length=100)
    bio = models.TextField(blank=True)
    experiences = models.TextField(blank=True)
    album_photos = models.TextField(blank=True, null=True)
    feedback =models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.prénom} {self.nom}"


class Categorie(models.Model):
    nom = models.CharField(max_length=100)

    def __str__(self):
        return self.nom


class Annonce(models.Model):
    class AnnonceType(models.TextChoices):
        EVENEMENT = "EVENEMENT", _("Évènement")
        DON = "DON", _("Don")
        APPEL_BENEVOLAT = "APPEL_BENEVOLAT", _("Appel Bénévolat")

    titre = models.CharField(max_length=255)
    description = models.TextField()
    lieu = models.CharField(max_length=255)
    type = models.CharField(max_length=20, choices=AnnonceType.choices)
    date_debut = models.DateTimeField()
    date_fin = models.DateTimeField()
    association = models.ForeignKey(AssociationProfile, on_delete=models.CASCADE, related_name='annonces')
    categorie = models.ForeignKey(Categorie, on_delete=models.SET_NULL, null=True, related_name='annonces')
    date_creation = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.titre


class Candidature(models.Model):
    class Statut(models.TextChoices):
        EN_ATTENTE = "EN_ATTENTE", _("En attente")
        ACCEPTEE = "ACCEPTEE", _("Acceptée")
        REFUSEE = "REFUSEE", _("Refusée")

    citoyen = models.ForeignKey(CitoyenProfile, on_delete=models.CASCADE, related_name='candidatures')
    annonce = models.ForeignKey(Annonce, on_delete=models.CASCADE, related_name='candidatures')
    statut = models.CharField(max_length=20, choices=Statut.choices, default=Statut.EN_ATTENTE)
    message = models.TextField()
    date_candidature = models.DateTimeField(auto_now_add=True)
    note_engagement = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return f"Candidature de {self.citoyen} pour {self.annonce}"


class Message(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='messages_sent')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='messages_received')
    contenu = models.TextField()
    date_envoi = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message de {self.sender} à {self.receiver} le {self.date_envoi}"
