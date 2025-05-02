"""Tests for the notification service."""

import unittest
from unittest.mock import patch, MagicMock

from remedy.services.notification.notification_service import NotificationService
from remedy.services.notification.firebase_service import FirebaseService


class TestNotificationService(unittest.TestCase):
    """Test cases for the notification service."""
    
    @patch('remedy.services.notification.firebase_service.FirebaseService.get_instance')
    def setUp(self, mock_firebase_get_instance):
        """Set up test fixtures before each test method."""
        # Mock the Firebase service
        self.mock_firebase = MagicMock()
        mock_firebase_get_instance.return_value = self.mock_firebase
        
        # Create notification service
        self.notification_service = NotificationService()
    
    def test_send_push_notification(self):
        """Test the push notification functionality."""
        # Mock successful Firebase response
        self.mock_firebase.send_push_notification.return_value = {
            "success": True,
            "message_id": "mock-message-id-123"
        }
        
        # Test data
        user_id = "test_user"
        content = {
            "title": "Test Notification",
            "body": "This is a test notification",
            "event_id": "123",
            "type": "reminder"
        }
        
        # Call method under test
        result = self.notification_service.send_push_notification(user_id, content)
        
        # Verify results
        self.assertTrue(result["success"])
        self.assertEqual(result["message_id"], "mock-message-id-123")
        
        # Verify Firebase service was called with correct parameters
        self.mock_firebase.send_push_notification.assert_called_once()
        call_args = self.mock_firebase.send_push_notification.call_args[1]
        self.assertIsNotNone(call_args.get("token"))
        self.assertEqual(call_args.get("title"), "Test Notification")
        self.assertEqual(call_args.get("body"), "This is a test notification")
        self.assertIn("event_id", call_args.get("data", {}))
        self.assertIn("type", call_args.get("data", {}))
    
    def test_send_notification_multiple_channels(self):
        """Test sending notifications through multiple channels."""
        # Mock responses for different channels
        self.mock_firebase.send_push_notification.return_value = {
            "success": True,
            "message_id": "mock-message-id-123"
        }
        
        # Create service method mocks
        self.notification_service.send_email_notification = MagicMock(
            return_value={"status": "sent", "message": "Email sent successfully"}
        )
        self.notification_service.send_sms_notification = MagicMock(
            return_value={"status": "sent", "message": "SMS sent successfully"}
        )
        
        # Test data
        user_id = "test_user"
        notification_type = "event_alert"
        content = {
            "title": "Price Alert",
            "body": "Bitcoin has reached your target price of $50,000",
            "event_id": "btc-price-50k",
            "price": 50000
        }
        channels = ["push", "email", "sms"]
        
        # Call method under test
        results = self.notification_service.send_notification(
            user_id, notification_type, content, channels
        )
        
        # Verify results for each channel
        self.assertTrue(results["push"]["success"])
        self.assertEqual(results["email"]["status"], "sent")
        self.assertEqual(results["sms"]["status"], "sent")
        
        # Verify each channel method was called
        self.mock_firebase.send_push_notification.assert_called_once()
        self.notification_service.send_email_notification.assert_called_once_with(user_id, content)
        self.notification_service.send_sms_notification.assert_called_once_with(user_id, content)
    
    def test_get_device_token(self):
        """Test the device token lookup functionality."""
        # Test with known user
        token = self.notification_service._get_device_token_for_user("user1")
        self.assertEqual(token, "fcm-token-for-user1")
        
        # Test with unknown user (should return default test token)
        token = self.notification_service._get_device_token_for_user("unknown_user")
        self.assertEqual(token, "fcm-default-test-token")


if __name__ == '__main__':
    unittest.main() 