from rest_framework import generics
from login_app.models import Candidature , Annonce
from login_app.serializers import CandidatureSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from login_app.permissions import CandidaturePermission, CandidaturePermissionCandA

class CandidatureListCreateView(generics.ListCreateAPIView):
    queryset = Candidature.objects.all()
    serializer_class = CandidatureSerializer
    permission_classes = [CandidaturePermission]

    def perform_create(self, serializer):
        # Associer automatiquement le citoyen connecté si nécessaire
        serializer.save()


class CandidatureRetrieveUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Candidature.objects.all()
    serializer_class = CandidatureSerializer
    permission_classes = [CandidaturePermission]


class MesCandidaturesView(generics.ListAPIView):
    serializer_class = CandidatureSerializer
    permission_classes = [CandidaturePermissionCandA]

    def get_queryset(self):
        user = self.request.user
        if hasattr(user, 'citoyen_profile'):
            return Candidature.objects.filter(citoyen=user.citoyen_profile)
        
        if hasattr(user, 'association_profile'):
            
            return Candidature.objects.filter(annonce__association=user.association_profile )
        
        return Candidature.objects.none()
    



@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([CandidaturePermissionCandA])
def candidature_detail(request, pk):
    user_connecte=request.user
    candidature=None
    try:
        # Vérifier à qui appartient la candidature
        if hasattr(request.user, 'citoyen_profile'):
            candidature = get_object_or_404(Candidature, id=pk, citoyen=user_connecte.citoyen_profile)
        elif hasattr(request.user, 'association_profile'):
            candidature = get_object_or_404(
            Candidature, 
            id=pk,
            annonce__association=user_connecte.association_profile
        )
        else:
            return Response(
                {"message": "Profil non autorisé"},
                status=status.HTTP_403_FORBIDDEN
            )
    
    except Candidature.DoesNotExist:
        return Response(
            {"message": "Candidature non trouvée"},
            status=status.HTTP_404_NOT_FOUND
        )

    # Gestion des différentes méthodes
    if request.method == 'GET':
        serializer = CandidatureSerializer(candidature)
        return Response({
            "candidature": serializer.data,
            "message": "Candidature trouvée avec succès"
        }, status=status.HTTP_200_OK)

    elif request.method == 'PUT':
        data=request.data.copy()
        #interder modifer status et note de engageent
        if(user_connecte.type!="ASSOCIATION"):
            data['statut']=candidature.statut
            data['note_engagement']=candidature.note_engagement
        # interi a association de modifier msg de citoyen  
        if(user_connecte.type=="ASSOCIATION"):
            data['message']=candidature.message
            
        #interdet la modification de annonce lie a la condidature 
        data['annonce']=candidature.annonce.id
        
        serializer = CandidatureSerializer(candidature, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "candidature": serializer.data,
                "message": "Candidature mise à jour avec succès"
            })
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        if user_connecte.type=="CITOYEN":
            return  Response(
            {"message": "vous etes pas acces"},
            status=status.HTTP_403_FORBIDDEN
        )
        candidature.delete()
        return Response(
            {"message": "Candidature supprimée avec succès"},
            status=status.HTTP_204_NO_CONTENT
        )
        

# @api_view(['GET', 'PUT', 'DELETE'])
# @permission_classes([IsAuthenticated])
# def candidature_detail_user(request, pk, annonce):
#     userConnecte=request.user
#     candidature=None
#     if(userConnecte.type=="CITOYEN"):
#        candidatures = Candidature.objects.filter( citoyen=request.user.association_profile, annonce=annonce, id=pk)
#        return Response({
#         "list candidature":candidature,
#         "message":"chrche ave csucces"
#        },HTTP_200_OK)
    
    
    