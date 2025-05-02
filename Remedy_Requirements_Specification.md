# Remedy Requirements Specification

## 1. Project Overview

* **Repository:** `https://github.com/Jiayi-Pan/TinyZero`
* **Goal:** Develop an enhanced version of Remedy that expands its capabilities beyond countdown and multiplication tasks to include a conversational interface with event monitoring and notifications.
* **Vision:** Create a system that leverages Remedy's reinforcement learning capabilities to develop self-verification and search abilities while adding practical user-facing functionality.

## 2. Technical Stack

* **Core Framework:** Remedy/veRL (existing)
* **Language Models:**
  * Base: QWen2.5 series (3B model recommended for reasoning capabilities)
  * Fine-tuning: Reinforcement Learning using veRL framework
* **Development Environment:**
  * Python 3.9
  * PyTorch 2.4.0 with CUDA 12.1
  * vLLM 0.6.3 for inference
  * Ray for distributed computing
* **Dependencies:**
  * Flash Attention 2
  * Wandb for experiment tracking
  * Matplotlib for visualization
* **Mobile Integration:**
  * React Native for cross-platform mobile UI
  * Firebase Cloud Messaging for push notifications
  * Local SQLite database for persistent storage
* **API Services:**
  * RESTful API for communication between mobile client and Remedy backend
  * Webhook support for event monitoring
  * Transactional email service (SendGrid or AWS SES)
  * Twilio for SMS notifications

## 3. Functional Requirements

### 3.1 Core Language Model Capabilities

1. **Expanded Reasoning Tasks:**
   * Maintain existing countdown and multiplication capabilities
   * Add natural language understanding for event monitoring queries
   * Implement time-based reasoning for scheduling and reminders

2. **Self-Verification Mechanism:**
   * Utilize the existing self-verification capabilities for event detection
   * Implement confidence scoring for event detection accuracy
   * Add fallback mechanisms when confidence is below threshold

3. **Search and Information Retrieval:**
   * Leverage and expand existing search abilities
   * Implement targeted data source polling for continuous event monitoring
   * Add structured data parsing for various information sources

### 3.2 Conversational Interface

1. **Query Understanding:**
   * Parse natural language questions related to future events
   * Classify queries as continuous monitoring or one-time reminders
   * Extract relevant entities, dates, times, and conditions

2. **Dialogue Management:**
   * Support multi-turn conversations for clarification
   * Implement context tracking across conversation turns
   * Provide confirmation of understood intent and parameters

3. **Response Generation:**
   * Generate natural language confirmations of scheduled alerts
   * Provide clear explanations of monitoring strategy
   * Support streaming responses with incremental display

### 3.3 Event Monitoring System

1. **Event Classification:**
   * Categorize events by type (sports, product releases, deadlines, etc.)
   * Identify required data sources for monitoring each event type
   * Support custom user-defined event types

2. **Monitoring Strategies:**
   * **Continuous Monitoring:**
     * Poll relevant data sources at configurable intervals
     * Parse responses to detect trigger conditions
     * Support complex conditional logic for event detection
   * **Time-Based Alerts:**
     * Schedule one-time or recurring reminders based on specific dates/times
     * Support timezone awareness and conversions
     * Handle relative time expressions ("tomorrow", "next week")

3. **Information Sources:**
   * Support integration with public APIs (sports, weather, news, etc.)
   * Implement RSS/Atom feed parsing
   * Support webhook endpoints for custom data sources
   * Include web scraping capabilities for public information

### 3.4 Notification System

1. **Delivery Channels:**
   * **In-App Notifications:**
     * Display within the mobile application
     * Support rich formatting and action buttons
   * **Push Notifications:**
     * Integrate with Firebase Cloud Messaging
     * Support both iOS and Android platforms
   * **Email Notifications:**
     * Send formatted emails via transactional email service
     * Include original query and detected event details
   * **SMS Notifications:**
     * Send text messages via Twilio
     * Format for readability on mobile devices

2. **Notification Management:**
   * Allow users to customize notification preferences per event
   * Implement priority levels for notifications
   * Support snooze and dismiss functionality
   * Track delivery status and user interaction

### 3.5 Mobile Application

1. **User Interface:**
   * Chat interface for natural language interaction
   * Event management dashboard
   * Notification history and settings
   * Account management

2. **Features:**
   * **Chat Screen:**
     * Text input with send button
     * Message history display
     * Streaming response visualization
     * Quick action suggestions
   * **Events Dashboard:**
     * List of active monitoring tasks
     * Status indicators (pending, triggered, expired)
     * Edit and delete functionality
   * **Settings:**
     * Notification preferences
     * Default monitoring parameters
     * Data source connections

3. **Offline Functionality:**
   * Store scheduled events locally
   * Queue notifications when offline
   * Sync with server when connection restored

## 4. Non-Functional Requirements

### 4.1 Performance

1. **Inference Latency:**
   * LLM response initiation < 2 seconds
   * Complete response generation < 10 seconds for complex queries
   * Event detection latency < 5 minutes from occurrence

2. **Scalability:**
   * Support for at least 100 concurrent users
   * Handle 1000+ active monitoring tasks
   * Process 10,000+ notifications per day

3. **Resource Utilization:**
   * Optimize for mobile battery consumption
   * Efficient background task scheduling
   * Minimal data transfer for monitoring tasks

### 4.2 Reliability

1. **System Uptime:**
   * 99.9% backend service availability
   * Graceful degradation during partial outages
   * Automatic recovery from temporary failures

2. **Data Persistence:**
   * No data loss during application updates
   * Backup/restore capability for user settings
   * Transaction safety for critical operations

3. **Notification Reliability:**
   * 99% successful delivery rate
   * Retry mechanism for failed notifications
   * Fallback to alternative channels when primary fails

### 4.3 Security

1. **Data Protection:**
   * End-to-end encryption for sensitive user data
   * Secure storage of authentication credentials
   * No plaintext storage of personal information

2. **Authentication:**
   * Multi-factor authentication option
   * Secure token-based API access
   * Session timeout and automatic logouts

3. **Privacy Controls:**
   * User consent for data collection
   * Configurable data retention policies
   * Opt-out options for analytics

### 4.4 Usability

1. **Accessibility:**
   * Support for screen readers
   * High contrast mode
   * Configurable text size
   * Voice input support

2. **Internationalization:**
   * Support for multiple languages
   * Time/date format localization
   * Cultural sensitivity in notifications

3. **User Experience:**
   * Intuitive navigation with minimal learning curve
   * Consistent design language
   * Responsive layouts for different screen sizes

### 4.5 Maintainability

1. **Code Structure:**
   * Modular architecture with clear separation of concerns
   * Comprehensive documentation
   * Consistent coding standards

2. **Testing:**
   * Automated test suite with 80%+ coverage
   * Integration tests for all key workflows
   * Performance benchmarks

3. **Deployment:**
   * CI/CD pipeline for automated testing and deployment
   * Version control with clear release management
   * Feature flags for gradual rollout

## 5. Constraints

1. **Technical Constraints:**
   * Must build upon existing Remedy/veRL codebase
   * Model size limited to 3B parameters for reasonable inference speed
   * Mobile app must function on devices with iOS 14+ and Android 10+

2. **Business Constraints:**
   * Initial release deadline: 12 weeks from project start
   * Development resources: 3 ML engineers, 2 mobile developers, 1 designer
   * Budget constraints for third-party API usage

3. **Legal and Compliance:**
   * Data privacy compliance (GDPR, CCPA)
   * Terms of service for third-party APIs
   * Open source license compatibility

## 6. Deliverables

1. **Software Components:**
   * Enhanced Remedy core with event monitoring capabilities
   * RESTful API service for mobile integration
   * Cross-platform mobile application (iOS and Android)
   * Admin dashboard for monitoring and analytics

2. **Documentation:**
   * Architecture diagrams
   * API documentation
   * User guides
   * Development setup instructions
   * Deployment guides

3. **Testing Assets:**
   * Test suite covering all major functionality
   * Performance benchmarking tools
   * Sample datasets for event monitoring

## 7. Milestones and Timeline

| Milestone | Description | Timeline | Criteria |
|-----------|-------------|----------|----------|
| **1. Project Setup** | Environment setup, requirements refinement | Week 1-2 | Development environment configured, detailed requirements approved |
| **2. Core ML Enhancement** | Extend Remedy for event monitoring | Week 3-5 | Model fine-tuning complete, event classification functional |
| **3. API Development** | Create RESTful services for mobile integration | Week 4-6 | API endpoints implemented and documented |
| **4. Mobile UI Development** | Develop React Native mobile interface | Week 5-8 | UI components implemented, navigation functional |
| **5. Notification System** | Implement multi-channel notification delivery | Week 7-9 | Push, email, and SMS notifications functional |
| **6. Integration & Testing** | End-to-end integration and QA | Week 9-11 | All components integrated, major bugs resolved |
| **7. Final Release** | Production deployment and launch | Week 12 | System deployed to production environment |

## 8. Quality Assurance

1. **Testing Approach:**
   * Unit testing for individual components
   * Integration testing for component interactions
   * End-to-end testing for complete workflows
   * Performance testing under load

2. **Quality Metrics:**
   * Code coverage: 80%+ for critical paths
   * Response time benchmarks met
   * Error rate < 1% for notification delivery
   * Crash-free sessions > 99.5%

3. **User Acceptance Testing:**
   * Beta testing with selected users
   * Feedback collection and issue prioritization
   * Usability testing with defined scenarios

## 9. Risks and Mitigation

| Risk | Impact | Probability | Mitigation Strategy |
|------|--------|------------|---------------------|
| LLM inference too slow for mobile | High | Medium | Optimize model, consider server-side inference |
| Battery drain from background monitoring | High | High | Implement efficient polling, server-side monitoring |
| Data source reliability issues | Medium | High | Multiple redundant sources, graceful error handling |
| Notification delivery failures | Medium | Medium | Retry logic, delivery confirmations, alternative channels |
| Scope creep | High | High | Strict change management, MVP focus, prioritized backlog |

## 10. Glossary

* **Remedy:** The core reinforcement learning framework for language models.
* **veRL:** The underlying Volcano Engine Reinforcement Learning framework.
* **LLM:** Large Language Model, the AI system at the core of the application.
* **Event Monitoring:** The process of continuously checking for specific conditions or occurrences.
* **Notification Channels:** Methods of delivering alerts to users (push, email, SMS).
* **Inference:** The process of running the language model to generate responses. 