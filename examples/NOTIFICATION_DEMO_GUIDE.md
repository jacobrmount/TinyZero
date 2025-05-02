# Remedy Notification System Demo Guide

This guide explains how to run and test the Remedy notification system. The demo showcases device registration, sending test notifications, and visualizing how notifications appear in a mobile app.

## 1. Prerequisites

- Python 3.9+ environment setup (see `docs/ENV_SETUP.md`)
- Firebase Cloud Messaging (FCM) credentials (optional for real notification sending)

## 2. Demo Components

The notification demo consists of three main components:

1. **Backend Notification Service**: Implementation of the `NotificationService` class with Firebase Cloud Messaging integration
2. **CLI Demo App**: A terminal-based demo script that simulates device registration and notification sending
3. **Mobile App Mockup**: A React Native app mockup showing how notifications would appear on a mobile device

## 3. Running the Backend Demo

### 3.1 Terminal-based Demo

The terminal demo allows you to simulate the complete notification flow from registration to delivery:

```bash
# Make sure you're in your Python environment
python examples/notification_demo.py
```

Follow the interactive prompts to:
1. Register a device (simulates FCM token generation)
2. Create and customize a notification
3. Preview how it would appear on a device
4. Optionally send an actual notification (requires Firebase credentials)

### 3.2 Demo Mode vs. Real Mode

The notification service supports two modes:

- **Demo Mode**: Works without real Firebase credentials, simulating the notification flow
- **Real Mode**: Requires valid Firebase credentials to actually send notifications to devices

For demo purposes, we've included a mock Firebase credentials file. The system will automatically detect this and run in demo mode.

## 4. Mobile App Integration

In a real implementation, the mobile app would:

1. Request notification permissions from the user
2. Register the device with FCM and get a token
3. Send the token to the Remedy backend
4. Receive and display notifications

### 4.1 Mobile App Mockup

We've included a React Native mockup showing how the app would handle notifications:

```bash
# If you have React Native dev environment set up:
cd examples/mobile_app
npm install
npm start
```

Alternatively, you can view the app mockup code in `examples/notification_app_mockup.js` to understand the implementation.

## 5. Notification Flow Diagram

```
┌───────────┐     ┌───────────┐     ┌───────────┐     ┌───────────┐
│  User App │     │  Remedy   │     │  Firebase │     │  Device   │
│           │     │  Backend  │     │    FCM    │     │           │
└─────┬─────┘     └─────┬─────┘     └─────┬─────┘     └─────┬─────┘
      │                 │                 │                 │
      │ Register Device │                 │                 │
      ├────────────────▶│                 │                 │
      │                 │                 │                 │
      │ Return FCM Token│                 │                 │
      │◀────────────────┤                 │                 │
      │                 │                 │                 │
      │ Store Token     │                 │                 │
      ├────────────────▶│                 │                 │
      │                 │                 │                 │
      │                 │ Event Detected  │                 │
      │                 ├────────────────▶│                 │
      │                 │ Send Notification                 │
      │                 │                 ├────────────────▶│
      │                 │                 │                 │
      │                 │                 │ Show Notification
      │                 │                 │                 │
      │                 │                 │ User Interaction│
      │                 │                 │◀────────────────┤
      │                 │                 │                 │
      │                 │ Delivery Status │                 │
      │                 │◀────────────────┤                 │
      │                 │                 │                 │
```

## 6. Testing Real Notifications

To test with real Firebase notifications:

1. Create a Firebase project at [firebase.google.com](https://firebase.google.com)
2. Enable Firebase Cloud Messaging
3. Download service account credentials JSON
4. Save it as `firebase-credentials.json` in the project root
5. Run the demo script with the "y" option when prompted to send a real notification

## 7. Next Steps

After completing this demo, you can:

1. Implement the other notification channels (email, SMS)
2. Create a real mobile app using React Native with actual FCM integration
3. Develop a notification history persistence system
4. Implement notification grouping and topics for more efficient delivery

For more details, see the `PASSDOWN.md` file in the project root. 