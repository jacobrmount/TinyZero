"""Firebase Cloud Messaging service implementation."""

import logging
import os
import json
from typing import Dict, Any, Optional
import firebase_admin
from firebase_admin import credentials, messaging

logger = logging.getLogger(__name__)

class FirebaseService:
    """Service for sending push notifications using Firebase Cloud Messaging."""
    
    _instance = None
    
    @classmethod
    def get_instance(cls) -> 'FirebaseService':
        """Get or create a singleton instance of the Firebase service."""
        if cls._instance is None:
            cls._instance = FirebaseService()
        return cls._instance
    
    def __init__(self):
        """Initialize Firebase SDK with service account credentials."""
        self.is_initialized = False
        self.app = None
        try:
            # Look for credentials file
            cred_path = os.environ.get('FIREBASE_CREDENTIALS_PATH', './firebase-credentials.json')
            
            if os.path.exists(cred_path):
                # Initialize Firebase with credentials file
                cred = credentials.Certificate(cred_path)
                self.app = firebase_admin.initialize_app(cred)
                self.is_initialized = True
                logger.info("Firebase Cloud Messaging service initialized successfully")
            else:
                logger.warning(f"Firebase credentials file not found at {cred_path}")
        except Exception as e:
            logger.error(f"Failed to initialize Firebase: {e}")
    
    def send_push_notification(self, token: str, title: str, body: str, 
                               data: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """
        Send a push notification to a device using FCM.
        
        Args:
            token: The FCM registration token for the target device
            title: Notification title
            body: Notification body text
            data: Optional data payload to include with the notification
            
        Returns:
            Dict containing status of the send operation
        """
        if not self.is_initialized:
            error_msg = "Firebase service not properly initialized"
            logger.error(error_msg)
            return {
                "success": False,
                "error": error_msg
            }
        
        try:
            # Create the notification message
            message = messaging.Message(
                notification=messaging.Notification(
                    title=title,
                    body=body
                ),
                data=data if data else {},
                token=token
            )
            
            # Send the message
            response = messaging.send(message)
            logger.info(f"Successfully sent notification: {response}")
            
            return {
                "success": True,
                "message_id": response
            }
            
        except Exception as e:
            error_msg = f"Failed to send push notification: {str(e)}"
            logger.error(error_msg)
            return {
                "success": False,
                "error": error_msg
            }
    
    def send_multicast(self, tokens: list, title: str, body: str,
                       data: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """
        Send a push notification to multiple devices using FCM.
        
        Args:
            tokens: List of FCM registration tokens for target devices
            title: Notification title
            body: Notification body text
            data: Optional data payload to include with the notification
            
        Returns:
            Dict containing status of the multicast operation
        """
        if not self.is_initialized:
            error_msg = "Firebase service not properly initialized"
            logger.error(error_msg)
            return {
                "success": False,
                "error": error_msg
            }
        
        try:
            # Create the multicast message
            message = messaging.MulticastMessage(
                notification=messaging.Notification(
                    title=title,
                    body=body
                ),
                data=data if data else {},
                tokens=tokens
            )
            
            # Send the multicast message
            response = messaging.send_multicast(message)
            
            logger.info(f"Multicast completed: {response.success_count} successful, "
                       f"{response.failure_count} failed")
            
            return {
                "success": True,
                "success_count": response.success_count,
                "failure_count": response.failure_count,
                "responses": [r for r in response.responses]
            }
            
        except Exception as e:
            error_msg = f"Failed to send multicast notification: {str(e)}"
            logger.error(error_msg)
            return {
                "success": False,
                "error": error_msg
            } 