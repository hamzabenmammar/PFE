from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
import json
from django.contrib.contenttypes.models import ContentType
from .models import Notification

class NotificationService:
    @staticmethod
    def create_notification(recipient, notification_type, title, message, related_object=None):
        """
        Crée une notification et l'envoie via WebSocket si possible
        
        Args:
            recipient: Utilisateur qui recevra la notification
            notification_type: Type de notification (utiliser NotificationType)
            title: Titre de la notification
            message: Message détaillé
            related_object: Objet associé à la notification (optionnel)
        """
        # Créer l'objet notification
        notification = Notification(
            recipient=recipient,
            type=notification_type,
            title=title,
            message=message
        )
        
        # Ajouter l'objet associé si fourni
        if related_object:
            content_type = ContentType.objects.get_for_model(related_object)
            notification.content_type = content_type
            notification.object_id = related_object.id
        
        notification.save()
        
        # Envoyer la notification par WebSocket
        channel_layer = get_channel_layer()
        user_group_name = f"user_{recipient.id}_notifications"
        
        notification_data = {
            'id': notification.id,
            'type': notification.get_type_display(),
            'title': notification.title,
            'message': notification.message,
            'created_at': notification.created_at.isoformat(),
        }
        
        try:
            async_to_sync(channel_layer.group_send)(
                user_group_name,
                {
                    'type': 'notification_message',
                    'notification': notification_data
                }
            )
        except:
            # Gérer le cas où le WebSocket n'est pas disponible
            # La notification est déjà sauvegardée en base de données
            pass
        
        return notification
    
    @staticmethod
    def notify_group(users, notification_type, title, message, related_object=None):
        """Envoie une notification à un groupe d'utilisateurs"""
        notifications = []
        for user in users:
            notification = NotificationService.create_notification(
                user, notification_type, title, message, related_object
            )
            notifications.append(notification)
        return notifications
    
    @staticmethod
    def get_user_notifications(user, read=None, limit=None):
        """
        Récupère les notifications d'un utilisateur
        
        Args:
            user: Utilisateur dont on veut les notifications
            read: Si True, renvoie les notifications lues, si False les non lues, si None toutes
            limit: Nombre maximum de notifications à renvoyer
        """
        notifications = Notification.objects.filter(recipient=user)
        
        if read is not None:
            notifications = notifications.filter(read=read)
        
        notifications = notifications.order_by('-created_at')
        
        if limit:
            notifications = notifications[:limit]
        
        return notifications