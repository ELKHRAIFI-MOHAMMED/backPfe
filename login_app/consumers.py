# # consumers.py
# import json
# from channels.generic.websocket import AsyncWebsocketConsumer
# from channels.db import database_sync_to_async
# from django.contrib.auth import get_user_model
# from django.core.exceptions import ObjectDoesNotExist
# from login_app.models import Message
# from rest_framework_simplejwt.tokens import AccessToken

# User = get_user_model()

# class ChatConsumer(AsyncWebsocketConsumer):
#     async def connect(self):
#         self.sender_id = self.scope['url_route']['kwargs']['sender_id']
#         self.receiver_id = self.scope['url_route']['kwargs']['receiver_id']
        
#         # Normalisation du nom du groupe
#         user_ids = sorted([int(self.sender_id), int(self.receiver_id)])
#         self.room_group_name = f'chat_{user_ids[0]}_{user_ids[1]}'
        
#         await self.accept()
        
#         # Vérification de l'utilisateur via le token dans le premier message
#         # On ne fait pas l'authentification ici pour permettre au client d'envoyer le token

#     async def disconnect(self, close_code):
#         # Quitter le groupe
#         await self.channel_layer.group_discard(
#             self.room_group_name,
#             self.channel_name
#         )

#     async def receive(self, text_data):
#         try:
#             text_data_json = json.loads(text_data)
            
#             # Authentification
#             if text_data_json.get('type') == 'authentication':
#                 token = text_data_json.get('token')
#                 if await self.authenticate_user(token):
#                     await self.send(text_data=json.dumps({
#                         'type': 'authentication',
#                         'status': 'success'
#                     }))
#                 else:
#                     await self.send(text_data=json.dumps({
#                         'type': 'authentication',
#                         'status': 'failed',
#                         'message': 'Invalid token'
#                     }))
#                     await self.close()
#                 return
            
#             # Messages normaux
#             message = text_data_json.get('message')
#             sender_id = text_data_json.get('sender_id')
#             receiver_id = text_data_json.get('receiver_id')
            
#             # Validation de l'expéditeur
#             if str(sender_id) != self.sender_id:
#                 await self.send(text_data=json.dumps({
#                     'type': 'error',
#                     'message': 'Sender ID mismatch'
#                 }))
#                 return
                
#             # Sauvegarde du message
#             saved_message = await self.save_message(sender_id, receiver_id, message)
            
#             # Envoi au groupe
#             await self.channel_layer.group_send(
#                 self.room_group_name,
#                 {
#                     'type': 'chat_message',
#                     'message': message,
#                     'sender_id': sender_id,
#                     'receiver_id': receiver_id,
#                     'timestamp': saved_message.date_envoi.isoformat(),
#                     'message_id': saved_message.id  # Ajout de l'ID du message
#                 }
#             )
            
#         except json.JSONDecodeError:
#             await self.send(text_data=json.dumps({
#                 'type': 'error',
#                 'message': 'Invalid JSON format'
#             }))
#         except Exception as e:
#             print(f"Error in receive: {e}")
#             await self.send(text_data=json.dumps({
#                 'type': 'error',
#                 'message': 'Internal server error'
#             }))

#     async def chat_message(self, event):
#         # Envoi du message via WebSocket
#         await self.send(text_data=json.dumps({
#             'type': 'chat_message',
#             'message': event['message'],
#             'sender_id': event['sender_id'],
#             'receiver_id': event['receiver_id'],
#             'timestamp': event['timestamp'],
#             'message_id': event.get('message_id')  # Inclure l'ID du message
#         }))

#     @database_sync_to_async
#     def authenticate_user(self, token):
#         try:
#             access_token = AccessToken(token)
#             user_id = access_token['user_id']
#             user = User.objects.get(id=user_id)
#             return user.id == int(self.sender_id)
#         except Exception as e:
#             print(f"Authentication error: {e}")
#             return False

#     @database_sync_to_async
#     def save_message(self, sender_id, receiver_id, content):
#         try:
#             sender = User.objects.get(id=sender_id)
#             receiver = User.objects.get(id=receiver_id)
#             message = Message.objects.create(
#                 sender=sender,
#                 receiver=receiver,
#                 contenu=content
#             )
#             return message
#         except ObjectDoesNotExist as e:
#             print(f"User not found: {e}")
#             raise
#         except Exception as e:
#             print(f"Error saving message: {e}")
#             raise


import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from login_app.models import Message
from rest_framework_simplejwt.tokens import AccessToken

User = get_user_model()

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.sender_id = self.scope['url_route']['kwargs']['sender_id']
        self.receiver_id = self.scope['url_route']['kwargs']['receiver_id']

        # Générer un nom de groupe stable peu importe l’ordre des IDs
        user_ids = sorted([int(self.sender_id), int(self.receiver_id)])
        self.room_group_name = f'chat_{user_ids[0]}_{user_ids[1]}'

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)

            if data.get('type') == 'authentication':
                token = data.get('token')
                if await self.authenticate_user(token):
                    await self.send(text_data=json.dumps({
                        'type': 'authentication',
                        'status': 'success'
                    }))
                else:
                    await self.send(text_data=json.dumps({
                        'type': 'authentication',
                        'status': 'failed',
                        'message': 'Invalid token'
                    }))
                    await self.close()
                return

            # Message standard
            message = data.get('message')
            sender_id = data.get('sender_id')
            receiver_id = data.get('receiver_id')

            if str(sender_id) != self.sender_id:
                await self.send(text_data=json.dumps({
                    'type': 'error',
                    'message': 'Sender ID mismatch'
                }))
                return

            saved_message = await self.save_message(sender_id, receiver_id, message)

            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message': message,
                    'sender_id': sender_id,
                    'receiver_id': receiver_id,
                    'timestamp': saved_message.date_envoi.isoformat(),
                    'message_id': saved_message.id,
                }
            )

        except Exception as e:
            print(f"Receive error: {e}")
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Internal server error'
            }))

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            'type': 'chat_message',
            'message': event['message'],
            'sender_id': event['sender_id'],
            'receiver_id': event['receiver_id'],
            'timestamp': event['timestamp'],
            'message_id': event['message_id'],
        }))

    @database_sync_to_async
    def authenticate_user(self, token):
        try:
            access_token = AccessToken(token)
            user_id = access_token['user_id']
            return str(user_id) == self.sender_id
        except Exception as e:
            print(f"Auth error: {e}")
            return False

    @database_sync_to_async
    def save_message(self, sender_id, receiver_id, content):
        sender = User.objects.get(id=sender_id)
        receiver = User.objects.get(id=receiver_id)
        return Message.objects.create(sender=sender, receiver=receiver, contenu=content)
