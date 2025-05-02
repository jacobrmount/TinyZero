"""Notification service for sending various types of notifications."""

import logging
from typing import Dict, Any, Optional

from remedy.services.notification.firebase_service import FirebaseService

logger = logging.getLogger(__name__)

class NotificationService:
    """Service for sending notifications via different channels."""
    
    def __init__(self):
        """Initialize the notification service."""
        logger.info("Initializing notification service")
        self.firebase_service = FirebaseService.get_instance()
    
    def send_notification(self, user_id: str, notification_type: str, 
                          content: Dict[str, Any], 
                          channels: Optional[list] = None) -> Dict[str, Any]:
        """
        Send a notification to a user through specified channels.
        
        Args:
            user_id: The ID of the user to notify
            notification_type: Type of notification (event, reminder, etc.)
            content: Content of the notification
            channels: List of channels to use (push, email, sms, in_app)
                     If None, will use user's default preferences
                     
        Returns:
            Dict with status of each attempted delivery
        """
        if channels is None:
            # In a real implementation, we would fetch user preferences
            channels = ["push", "email"]
            
        results = {}
        
        for channel in channels:
            if channel == "push":
                results["push"] = self.send_push_notification(user_id, content)
            elif channel == "email":
                results["email"] = self.send_email_notification(user_id, content)
            elif channel == "sms":
                results["sms"] = self.send_sms_notification(user_id, content)
            elif channel == "in_app":
                results["in_app"] = self.send_in_app_notification(user_id, content)
        
        return results
    
    def send_push_notification(self, user_id: str, content: Dict[str, Any]) -> Dict[str, Any]:
        """
        Send a push notification using Firebase Cloud Messaging.
        
        Args:
            user_id: User to notify
            content: Content of the notification
            
        Returns:
            Status of delivery attempt
        """
        try:
            # In a real implementation, we would fetch device tokens from a user database
            # This is a mock implementation for demonstration purposes
            device_token = self._get_device_token_for_user(user_id)
            
            if not device_token:
                return {
                    "success": False,
                    "error": f"No device token found for user {user_id}"
                }
            
            # Prepare notification content
            title = content.get("title", "Remedy Notification")
            body = content.get("body", "You have a new notification")
            
            # Extract additional data for FCM data payload
            data_payload = {k: str(v) for k, v in content.items() 
                           if k not in ["title", "body"] and v is not None}
            
            # Send via Firebase
            result = self.firebase_service.send_push_notification(
                token=device_token,
                title=title,
                body=body,
                data=data_payload
            )
            
            return result
        except Exception as e:
            error_msg = f"Error sending push notification: {str(e)}"
            logger.error(error_msg)
            return {
                "success": False,
                "error": error_msg
            }
    
    def send_email_notification(self, user_id: str, content: Dict[str, Any]) -> Dict[str, Any]:
        """
        Send an email notification using SendGrid or AWS SES.
        
        Args:
            user_id: User to notify
            content: Content of the notification
            
        Returns:
            Status of delivery attempt
        """
        # TODO: Implement SendGrid or AWS SES integration
        logger.info(f"Would send email notification to user {user_id}: {content}")
        return {"status": "not_implemented", "message": "Email integration pending"}
    
    def send_sms_notification(self, user_id: str, content: Dict[str, Any]) -> Dict[str, Any]:
        """
        Send an SMS notification using Twilio.
        
        Args:
            user_id: User to notify
            content: Content of the notification
            
        Returns:
            Status of delivery attempt
        """
        # TODO: Implement Twilio integration
        logger.info(f"Would send SMS notification to user {user_id}: {content}")
        return {"status": "not_implemented", "message": "Twilio integration pending"}
    
    def send_in_app_notification(self, user_id: str, content: Dict[str, Any]) -> Dict[str, Any]:
        """
        Send an in-app notification.
        
        Args:
            user_id: User to notify
            content: Content of the notification
            
        Returns:
            Status of delivery attempt
        """
        # TODO: Implement in-app notification storage
        logger.info(f"Would send in-app notification to user {user_id}: {content}")
        return {"status": "not_implemented", "message": "In-app notification pending"}
    
    def _get_device_token_for_user(self, user_id: str) -> Optional[str]:
        """
        Get a user's device token for push notifications.
        
        Args:
            user_id: ID of the user
            
        Returns:
            FCM registration token or None if not found
        """
        # In a real implementation, this would fetch from a database
        # This is a mock implementation for demonstration
        mock_tokens = {
            "user1": "fcm-token-for-user1",
            "user2": "fcm-token-for-user2",
            "test": "fcm-test-token"
        }
        
        # Default token for testing if user not found
        return mock_tokens.get(user_id, "fcm-default-test-token") 