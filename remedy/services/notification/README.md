# Remedy Notification Service

This service provides a flexible framework for sending notifications through various channels, with an initial implementation of Firebase Cloud Messaging (FCM) for push notifications.

## Overview

The notification service is designed to:

1. Support multiple notification channels (push, email, SMS, in-app)
2. Provide a consistent API for all notification types
3. Handle delivery status tracking and error reporting
4. Support customization of notification content by channel

## Implementation Details

### Core Components

- **NotificationService**: Main entry point for sending notifications via different channels
- **FirebaseService**: Firebase Cloud Messaging implementation for push notifications

### Push Notifications (Implemented)

The push notification channel uses Firebase Cloud Messaging to deliver notifications to mobile devices. Key features include:

- Device token management
- Support for notification title, body, and data payload
- Multicast capabilities for sending to multiple devices
- Proper error handling and status reporting

### Other Channels (Planned)

- **Email Notifications**: Will integrate with SendGrid or AWS SES
- **SMS Notifications**: Will integrate with Twilio
- **In-App Notifications**: Will store notifications in a persistent database

## Usage Example

```python
from remedy.services.notification.notification_service import NotificationService

# Initialize the service
notification_service = NotificationService()

# Send a notification through multiple channels
result = notification_service.send_notification(
    user_id="user123",
    notification_type="event_alert",
    content={
        "title": "Price Alert",
        "body": "Bitcoin has reached your target price of $50,000",
        "event_id": "btc-price-50k",
        "price": 50000
    },
    channels=["push", "email"]
)

# Check the result
if result["push"]["success"]:
    print(f"Push notification sent successfully: {result['push']['message_id']}")
else:
    print(f"Push notification failed: {result['push']['error']}")
```

## Configuration

### Firebase Cloud Messaging

To use the Firebase Cloud Messaging integration:

1. Create a Firebase project and enable FCM
2. Download the service account credentials
3. Save the credentials as `firebase-credentials.json` or set the path using the `FIREBASE_CREDENTIALS_PATH` environment variable

## Testing

Unit tests are available in the `tests/services/notification` directory. Run them with:

```bash
python -m unittest discover -v tests/services/notification
```

## Demo

A demonstration script is available to showcase the notification flow:

```bash
python examples/notification_demo.py
```

For more details, see the [Notification Demo Guide](../../examples/NOTIFICATION_DEMO_GUIDE.md). 