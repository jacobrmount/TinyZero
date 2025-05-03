# Remedy Notification System Walkthrough

This document provides a detailed walkthrough of the Remedy Notification System, showing how notifications flow from device registration to delivery and display.

## Complete Notification Flow

### 1. Device Registration

When a user installs the Remedy app:

1. The app requests notification permissions
2. If granted, it registers with Firebase Cloud Messaging (FCM)
3. FCM returns a unique device token
4. The app sends this token to the Remedy backend
5. The backend stores the token in the user's profile

```
Mobile App                                  Firebase                                  Remedy Backend
┌───────────────┐                          ┌───────────────┐                          ┌───────────────┐
│ 1. Request    │                          │               │                          │               │
│ notification  │                          │               │                          │               │
│ permissions   │                          │               │                          │               │
├───────────────┤                          │               │                          │               │
│ 2. Register   │─────────────────────────▶│               │                          │               │
│ with FCM      │                          │               │                          │               │
│               │◀─────────────────────────┤ 3. Return     │                          │               │
│               │                          │ device token  │                          │               │
├───────────────┤                          │               │                          │               │
│ 4. Send token │─────────────────────────────────────────────────────────────────────▶│               │
│ to backend    │                          │               │                          │               │
│               │◀─────────────────────────────────────────────────────────────────────┤ 5. Store token│
│               │                          │               │                          │ in database   │
└───────────────┘                          └───────────────┘                          └───────────────┘
```

**Code Snippet: Device Registration in the React Native App**

```jsx
import messaging from '@react-native-firebase/messaging';
import { registerDeviceWithBackend } from './api';

async function registerDevice() {
  // Request permission
  const authStatus = await messaging().requestPermission();
  
  if (authStatus === messaging.AuthorizationStatus.AUTHORIZED) {
    // Get FCM token
    const token = await messaging().getToken();
    console.log('FCM Token:', token);
    
    // Register with backend
    await registerDeviceWithBackend(token);
    console.log('Device registered successfully');
  }
}
```

### 2. Creating Events and Reminders

Users interact with the Remedy chatbot to set up:
- One-time reminders ("Remind me about the meeting at 3 PM")
- Continuous monitoring ("Alert me when Bitcoin goes above $50,000")

```
User                                          Remedy Backend
┌───────────────┐                            ┌───────────────┐
│ "Alert me     │                            │               │
│ when Bitcoin  │──────────────────────────▶│ Intent        │
│ goes above    │                            │ Classification│
│ $50,000"      │                            │               │
│               │                            │               │
│               │◀──────────────────────────┤ "I'll monitor │
│               │                            │ Bitcoin and   │
│               │                            │ notify you    │
│               │                            │ when it       │
│               │                            │ exceeds       │
│               │                            │ $50,000"      │
└───────────────┘                            └───────────────┘
                                                    │
                                                    ▼
                                            ┌───────────────┐
                                            │ Store event   │
                                            │ monitoring    │
                                            │ task in DB    │
                                            └───────────────┘
```

**Sample Alert Creation**:

```python
# Server-side processing of user intent
event_monitor = {
    "user_id": "user123",
    "type": "price_alert",
    "subject": "Bitcoin",
    "conditions": [
        {
            "type": "above",
            "value": 50000,
            "is_price": True,
            "currency": "USD"
        }
    ],
    "created_at": "2023-08-15T12:00:00Z",
    "notification_channels": ["push", "email"],
    "status": "active"
}

# Store in database
db.event_monitors.insert_one(event_monitor)
```

### 3. Event Detection and Notification Triggering

The Remedy backend continuously monitors for events:

```
External API                               Remedy Backend
┌───────────────┐                         ┌───────────────┐
│ Bitcoin       │                         │ Polling       │
│ Price API     │◀───────────────────────┤ Service       │
│               │                         │               │
│               │────────────────────────▶│               │
│               │   {"price": 50100}      │               │
└───────────────┘                         └───────┬───────┘
                                                  │
                                                  ▼
                                          ┌───────────────┐
                                          │ Check         │
                                          │ condition:    │
                                          │ 50100 > 50000 │
                                          │ = TRUE        │
                                          └───────┬───────┘
                                                  │
                                                  ▼
                                          ┌───────────────┐
                                          │ Notification  │
                                          │ Service       │
                                          └───────────────┘
```

**Event Detection Code**:

```python
def check_price_alerts():
    """Poll for price changes and trigger notifications for matching conditions"""
    # Get current prices from API
    prices = price_api.get_current_prices()
    
    # Find active price alerts
    alerts = db.event_monitors.find({
        "type": "price_alert",
        "status": "active"
    })
    
    for alert in alerts:
        current_price = prices.get(alert["subject"].lower())
        if not current_price:
            continue
            
        for condition in alert["conditions"]:
            if condition["type"] == "above" and current_price > condition["value"]:
                # Condition met, trigger notification
                trigger_notification(alert)
                
                # Update alert status if it's a one-time alert
                if alert.get("repeat", False) == False:
                    db.event_monitors.update_one(
                        {"_id": alert["_id"]},
                        {"$set": {"status": "triggered"}}
                    )
```

### 4. Sending Notifications

When an event is detected, the NotificationService sends alerts through configured channels:

```
Remedy Backend                             Firebase                               User Devices
┌───────────────┐                         ┌───────────────┐                       ┌───────────────┐
│ Notification  │                         │               │                       │               │
│ Service       │                         │               │                       │               │
│               │                         │               │                       │               │
│ 1. Format     │                         │               │                       │               │
│ notification  │                         │               │                       │               │
│               │                         │               │                       │               │
│ 2. Get user's │                         │               │                       │               │
│ device tokens │                         │               │                       │               │
│               │                         │               │                       │               │
│ 3. Send via   │─────────────────────────▶│ 4. Process &  │                       │               │
│ Firebase      │                         │ route         │                       │               │
│               │                         │ notification  │                       │               │
│               │                         │               │─────────────────────▶│ 5. Display    │
│               │                         │               │                       │ notification  │
│               │                         │               │                       │               │
└───────────────┘                         └───────────────┘                       └───────────────┘
```

**Notification Service Code**:

```python
# From our implementation in remedy/services/notification/notification_service.py
def send_notification(self, user_id, notification_type, content, channels=None):
    """Send a notification through multiple channels"""
    if channels is None:
        channels = ["push", "email"]  # Default channels
        
    results = {}
    
    for channel in channels:
        if channel == "push":
            results["push"] = self.send_push_notification(user_id, content)
        elif channel == "email":
            results["email"] = self.send_email_notification(user_id, content)
        # ... other channels
    
    return results
```

### 5. Notification Appearance on Device

When the notification arrives on the device:

1. The system displays the notification with title and body
2. The user can tap to open the app
3. The app can perform additional actions based on the notification data

**Mobile App Screen: Notification History**

```
┌─────────────────────────────────────────────────┐
│                                           9:41  │
│  ┌─────────────────────────────────────────┐    │
│  │              Remedy       Notifications │    │
│  │                                 ┌─┐     │    │
│  │                                 │▓│     │    │
│  │                                 └─┘     │    │
│  ├─────────────────────────────────────────┤    │
│  │                                         │    │
│  │  ┌─────────────────────────────────┐    │    │
│  │  │ Device registered with FCM      │    │    │
│  │  │ Token: fcm-token...789          │    │    │
│  │  └─────────────────────────────────┘    │    │
│  │                                         │    │
│  │  Notification History                   │    │
│  │                                         │    │
│  │  ┌─────────────────────────────────┐    │    │
│  │  │ 🔔 Bitcoin Price Alert          │    │    │
│  │  │ Bitcoin has reached $50,000!    │    │    │
│  │  │ 8/15/2023, 2:30:00 PM           │    │    │
│  │  └─────────────────────────────────┘    │    │
│  │                                         │    │
│  └─────────────────────────────────────────┘    │
└─────────────────────────────────────────────────┘
```

**Push Notification Appearance**:

```
┌─────────────────────────────────────────────────┐
│  ╔═══════════════════════════════════════════╗  │
│  ║                                           ║  │
│  ║  🔔 Remedy                                ║  │
│  ║  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ ║  │
│  ║  Bitcoin Price Alert                      ║  │
│  ║  Bitcoin has reached $50,000!             ║  │
│  ║                                           ║  │
│  ╚═══════════════════════════════════════════╝  │
└─────────────────────────────────────────────────┘
```

## Running the Demo

To see this notification flow in action:

1. Run the interactive CLI demo:
   ```bash
   python examples/notification_demo.py
   ```

2. To record a demonstration:
   ```bash
   ./examples/record_notification_demo.sh
   ```

For a full React Native app mockup, see `examples/notification_app_mockup.js`. 