from rest_framework.permissions import BasePermission, SAFE_METHODS
from datetime import datetime, timezone

class IsAdminOrReadOnlyForCitoyenAssociation(BasePermission):
    def has_permission(self, request, view):
        user = request.user

        # Si l'utilisateur n'est pas authentifié 
        if not user or not user.is_authenticated:
            return False

        # Si c'est un admin, autoriser tout
        if user.type == "ADMIN":
            return True

        # Si c'est un CITOYEN ou ASSOCIATION, lecture seule uniquement
        if user.type in ['CITOYEN', 'ASSOCIATION']:
            return request.method in SAFE_METHODS

        # Par défaut, accès refusé
        return False


class OnlyAssociationCreate(BasePermission):
    def has_permission(self, request, view):
        user = request.user

        if not user or not user.is_authenticated:
            return False

        if user.type == "ADMIN":
            return request.method in ['DELETE', 'PUT', 'GET','POST']

        if user.type == "CITOYEN":
            return request.method in SAFE_METHODS

        if user.type == "ASSOCIATION":
            return request.method in ['POST', 'GET']

        return False

    def has_object_permission(self, request, view, obj):
        user = request.user
        
        if not user or not user.is_authenticated:
            return False
        
        if not (user.id==obj.id_user) and request.method in ['PUT']:
            return False
        
        if user.type == "ADMIN":
            return request.method in ['DELETE', 'PUT', 'GET']

        if user.type == "CITOYEN":
            return request.method in SAFE_METHODS

        if user.type == "ASSOCIATION":
            if obj.date_debut < datetime.now(timezone.utc):
                return request.method in ['DELETE', 'POST', 'GET']
            return True

        return False
