#!/usr/bin/env python
"""
Notification Demo Script

This script demonstrates the Remedy notification flow:
1. Device registration
2. Sending a test notification
3. Visualizing how it would appear in the app
"""

import os
import sys
import logging
import uuid
import json
import time
from typing import Dict, Any, Optional

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Simulated device registration database
device_db = {}

# Mock Firebase service
class MockFirebaseService:
    """Mock implementation of Firebase service for demonstration purposes."""
    
    def __init__(self):
        """Initialize the mock Firebase service."""
        self.is_initialized = True
        self.demo_mode = True
        logger.info("Initialized mock Firebase service")
    
    def send_push_notification(self, token: str, title: str, body: str, 
                               data: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """Mock method to simulate sending a push notification."""
        logger.info(f"DEMO: Would send notification to token {token[:8]}...{token[-8:]} with title: '{title}'")
        logger.info(f"DEMO: Notification body: '{body}'")
        if data:
            logger.info(f"DEMO: Data payload: {data}")
        
        # Simulate network delay
        time.sleep(0.5)
        
        return {
            "success": True,
            "message_id": f"demo-msg-id-{os.urandom(4).hex()}",
            "demo_mode": True
        }

# Mock notification service
class MockNotificationService:
    """Mock implementation of the notification service for demonstration."""
    
    def __init__(self):
        """Initialize the mock notification service."""
        self.firebase_service = MockFirebaseService()
        logger.info("Initialized mock notification service")
    
    def send_notification(self, user_id: str, notification_type: str, 
                          content: Dict[str, Any], 
                          channels: Optional[list] = None) -> Dict[str, Any]:
        """Mock method to send notifications through multiple channels."""
        if channels is None:
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
        """Send a push notification using the mock Firebase service."""
        try:
            # In a real implementation, we would fetch device tokens from a user database
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
        """Mock method to simulate sending an email notification."""
        logger.info(f"DEMO: Would send email notification to user {user_id}: {content}")
        return {"status": "simulated", "message": "Email notification simulated"}
    
    def send_sms_notification(self, user_id: str, content: Dict[str, Any]) -> Dict[str, Any]:
        """Mock method to simulate sending an SMS notification."""
        logger.info(f"DEMO: Would send SMS notification to user {user_id}: {content}")
        return {"status": "simulated", "message": "SMS notification simulated"}
    
    def send_in_app_notification(self, user_id: str, content: Dict[str, Any]) -> Dict[str, Any]:
        """Mock method to simulate sending an in-app notification."""
        logger.info(f"DEMO: Would send in-app notification to user {user_id}: {content}")
        return {"status": "simulated", "message": "In-app notification simulated"}
    
    def _get_device_token_for_user(self, user_id: str) -> Optional[str]:
        """Get a mock device token for a user."""
        if user_id in device_db and device_db[user_id]:
            # Return the first device token for this user
            return device_db[user_id][0]["token"]
        
        # Default token for testing if user not found
        return f"fcm-default-test-token-{user_id}"

def register_device(user_id, device_name="iPhone", platform="iOS"):
    """
    Simulate device registration for FCM
    
    In a real implementation, this would:
    1. Register with Firebase on the device
    2. Get a real FCM token
    3. Store the token in a database
    
    Here we just simulate generating a token
    """
    # Generate a random FCM token (in reality, this comes from Firebase SDK on the device)
    device_token = f"fcm-{uuid.uuid4()}"
    
    if user_id not in device_db:
        device_db[user_id] = []
        
    device_db[user_id].append({
        "token": device_token,
        "device_name": device_name,
        "platform": platform,
        "active": True
    })
    
    logger.info(f"Registered device for user {user_id}: {device_name} ({platform})")
    logger.info(f"Generated token: {device_token}")
    
    return device_token

def visualize_notification(title, body, data=None):
    """
    Visualize how a notification would appear on a device
    """
    print("\n" + "="*60)
    print(" "*20 + "NOTIFICATION PREVIEW")
    print("="*60)
    
    if data and data.get("type") == "event_alert":
        icon = "🔔"
    elif data and data.get("type") == "reminder_alert":
        icon = "⏰"
    else:
        icon = "📱"
        
    print(f"\n  {icon} Remedy")
    print(f"  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print(f"  {title}")
    print(f"  {body}")
    
    # Show additional data that would be available to the app
    if data:
        print(f"  ⚙️  Additional data for the app:")
        for key, value in data.items():
            print(f"     - {key}: {value}")
            
    print("\n" + "="*60)
    print(" "*15 + "SWIPE LEFT TO OPEN THE APP")
    print("="*60 + "\n")

def main():
    """Main demo function for notification flow"""
    print("🚀 Starting Remedy Notification Demo")
    print("="*60)
    
    # 1. Simulate device registration
    print("\n📱 STEP 1: Device Registration\n")
    user_id = input("Enter a user ID (or press Enter for 'demo_user'): ").strip() or "demo_user"
    
    device_name = input("Enter device name (or press Enter for 'iPhone 14'): ").strip() or "iPhone 14"
    
    platform = input("Enter platform (ios/android, default: ios): ").strip().lower() or "ios"
    platform = "iOS" if platform == "ios" else "Android"
    
    token = register_device(user_id, device_name, platform)
    print(f"\n✅ Device registered successfully with token: {token[:8]}...{token[-8:]}")
    
    # 2. Simulate creating a notification
    print("\n📝 STEP 2: Create Notification\n")
    
    notification_type = input("Notification type (event/reminder, default: event): ").strip().lower() or "event"
    
    title = input("Enter notification title (or press Enter for default): ").strip()
    if not title:
        title = "Bitcoin Price Alert" if notification_type == "event" else "Meeting Reminder"
        
    body = input("Enter notification body (or press Enter for default): ").strip()
    if not body:
        body = "Bitcoin has reached $50,000!" if notification_type == "event" else "Team meeting in 15 minutes"
    
    # Create notification content
    content = {
        "title": title,
        "body": body,
        "type": f"{notification_type}_alert",
        "id": str(uuid.uuid4())[:8],
        "timestamp": "2023-08-15T14:30:00Z"
    }
    
    if notification_type == "event":
        content["event_type"] = "price_alert"
        content["threshold"] = "50000"
        content["currency"] = "USD"
    else:
        content["reminder_time"] = "2023-08-15T15:00:00Z"
        content["location"] = "Conference Room A"
    
    # 3. Preview how notification would appear
    print("\n👁️  STEP 3: Notification Preview\n")
    visualize_notification(content["title"], content["body"], content)
    
    # 4. Send the notification (in simulation mode)
    print("\n📤 STEP 4: Sending Notification\n")
    print("Would you like to send a simulated notification?")
    choice = input("(Y/n): ").strip().lower()
    
    if choice != 'n':
        # Send a simulated notification
        notification_service = MockNotificationService()
        try:
            print("\nSending notification...")
            result = notification_service.send_notification(
                user_id=user_id,
                notification_type=notification_type,
                content=content,
                channels=["push"]
            )
            if result.get("push", {}).get("success", False):
                print("\n✅ Notification sent successfully!")
                print(f"Message ID: {result['push'].get('message_id', 'N/A')}")
            else:
                print("\n❌ Failed to send notification:")
                print(f"Error: {result.get('push', {}).get('error', 'Unknown error')}")
        except Exception as e:
            print(f"\n❌ Error sending notification: {str(e)}")
    else:
        print("\n🔔 Simulation skipped.")
    
    # 5. Next steps
    print("\n🔮 STEP 5: Next Steps\n")
    print("In a complete implementation, you would also:")
    print("1. Store notification history in a database")
    print("2. Implement delivery tracking and retry mechanisms")
    print("3. Add support for notification actions (e.g., buttons)")
    print("4. Implement notification grouping and topics")
    print("5. Add support for rich media (images, actions)")
    
    print("\n🎉 Demo completed! Thank you for using Remedy Notifications.")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nDemo interrupted by user.")
    except Exception as e:
        print(f"\n\nError during demo: {str(e)}") 