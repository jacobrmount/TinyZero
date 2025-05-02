# Remedy Project Passdown

## Project Overview

Remedy is a mobile chatbot that enables users to set reminders or continuously monitor events. It leverages Reinforcement Learning capabilities to develop self-verification and search abilities while providing practical user-facing functionality.

## Project Structure

The project is organized into the following key modules:

- `remedy/core/`: Core language model capabilities, including the base model and reinforcement learning components.
- `remedy/services/`: Service modules for different functionality.
  - `remedy/services/classifier/`: Intent classification for user queries.
  - `remedy/services/conversation/`: Dialogue management and context tracking.
  - `remedy/services/notification/`: Notification delivery through various channels.
- `tests/`: Unit and integration tests.
- `docs/`: Documentation, including setup guides.

## Current Progress

### What's Built So Far

1. **Core Framework**
   - TinyZero base model implementation for countdown and multiplication tasks
   - veRL integration for reinforcement learning

2. **Conversation System**
   - Basic intent classification for continuous monitoring and one-time reminders
   - Dialogue context management for multi-turn conversations
   - Action creation and confirmation flow

3. **Notification System (Recently Added)**
   - Notification service infrastructure with support for multiple channels
   - Firebase Cloud Messaging integration for push notifications (complete)
   - Stubs for email, SMS, and in-app notifications

## Branching Conventions

- `main`: Stable, production-ready code
- `develop`: Integration branch for features
- `feature/{feature-name}`: Feature branches
- `feature/{feature-name}-foundation`: Initial implementation of a feature

## Testing

To run tests:

```bash
python -m unittest discover -v
```

## Environment Setup

Follow `docs/ENV_SETUP.md` for complete setup instructions:

1. **Using Conda**:
   ```bash
   conda env create -f environment.yml
   conda activate remedy
   pip install -e .
   ```

2. **Using Docker**:
   ```bash
   docker build -t remedy:latest .
   docker run --gpus all -it --rm remedy:latest
   ```

## Next Steps

### Current Focus: Notification Service Integration

We have implemented Firebase Cloud Messaging (FCM) for push notifications. The following tasks are prioritized next:

1. **Email Notifications**
   - Integrate SendGrid for transactional emails
   - Implement email templates for different notification types
   - Add email delivery status tracking

2. **SMS Notifications**
   - Integrate Twilio for SMS messaging
   - Implement message formatting for mobile displays
   - Add retry logic for failed deliveries

3. **In-App Notifications**
   - Develop persistent storage for in-app notifications
   - Create APIs for retrieving user notification history
   - Implement read/unread status tracking

### Other Priorities

1. **User Management**
   - Add OAuth login functionality
   - Move from JSON to database storage for user data
   - Implement user preference management

2. **Event Monitoring**
   - Develop integrations with external APIs for event data
   - Implement continuous polling mechanism
   - Create event detection logic

## Reference Documentation

- `Remedy_Requirements_Specification.md`: Comprehensive requirements specification
- `docs/ENV_SETUP.md`: Environment setup guide
- `README.md`: General project information 