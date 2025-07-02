
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from .models import Message
from .serializers import UserSerializer, MessageSerializer
from rest_framework.views import APIView
from django.db.models import Q

User = get_user_model()

class UserListView1(APIView):
    permission_classes =[permissions.IsAuthenticated] # خاص المستخدم يكون مسجل الدخول

    def get(self, request):
        users = User.objects.all()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class UserListView(generics.ListAPIView):
    """
    Liste tous les utilisateurs avec qui l'utilisateur connecté a une conversation
    """
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Récupère tous les utilisateurs avec qui on a échangé des messages
        sent_to = User.objects.filter(messages_received__sender=self.request.user).distinct()
        received_from = User.objects.filter(messages_sent__receiver=self.request.user).distinct()
        return (sent_to | received_from).distinct().order_by('username')

class UserDetailView(generics.RetrieveAPIView):
    """
    Détails d'un utilisateur spécifique
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

class MessageHistoryView(generics.ListAPIView):
    """
    Historique des messages avec un utilisateur spécifique
    """
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
           other_user_id = self.kwargs['user_id']
           current_user = self.request.user
           other_user = User.objects.get(id=other_user_id)
    
           return Message.objects.filter(
        (Q(sender=current_user) & Q(receiver=other_user)) |
        (Q(sender=other_user) & Q(receiver=current_user))
    ).order_by('date_envoi')

class MessageCreateView(generics.CreateAPIView):
    """
    Envoyer un nouveau message
    """
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        receiver = User.objects.get(id=self.kwargs['user_id'])
        serializer.save(sender=self.request.user, receiver=receiver)






class CurrentUserView(generics.RetrieveAPIView):
    """
    Vue pour récupérer les informations de l'utilisateur connecté
    """
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user