from typing import Dict, List, Optional, Any, Tuple
import json

from remedy.services.classifier.intent_classifier import classify_query, get_fallback_options, CONFIDENCE_THRESHOLD
from remedy.services.conversation.entity_extractor import EntityExtractor
from remedy.services.conversation.conversation_context import ConversationContext

class DialogueManager:
    """
    Manages multi-turn conversations with users, including:
    - Intent classification
    - Entity extraction
    - Context tracking
    - Generating appropriate responses
    - Confirming understood intents and entities
    
    This class coordinates the various NLP components to provide a coherent
    conversational experience.
    """
    
    def __init__(self, user_id: str = None, conversation_id: str = None):
        """
        Initialize a new dialogue manager.
        
        Args:
            user_id: Unique identifier for the user
            conversation_id: Unique identifier for the conversation
        """
        self.context = ConversationContext(user_id, conversation_id)
        self.entity_extractor = EntityExtractor()
        self.confidence_threshold = CONFIDENCE_THRESHOLD
    
    def process_message(self, message: str) -> Dict[str, Any]:
        """
        Process a user message and generate a response.
        
        Args:
            message: The user's message text
            
        Returns:
            Dictionary with the response and action information
        """
        if not message or not isinstance(message, str):
            return {
                "response": "I'm sorry, I didn't receive a valid message. Could you please try again?",
                "action": None,
                "requires_confirmation": False
            }
        
        # Add the user message to the conversation history
        self.context.add_user_message(message)
        
        # Determine the current state of the conversation
        if self.context.current_state == "initial":
            # Initial state: Classify intent and extract entities
            return self._handle_initial_state(message)
        elif self.context.current_state == "clarifying":
            # Clarifying state: Handle clarification of intent
            return self._handle_clarifying_state(message)
        elif self.context.current_state == "confirming":
            # Confirming state: Handle confirmation of action
            return self._handle_confirming_state(message)
        else:  # complete or any other state
            # Reset to initial state and handle as new query
            self.context.current_state = "initial"
            return self._handle_initial_state(message)
    
    def _handle_initial_state(self, message: str) -> Dict[str, Any]:
        """
        Handle messages in the initial state.
        
        Args:
            message: The user's message
            
        Returns:
            Response dictionary
        """
        # Classify the intent
        intent, confidence = classify_query(message)
        self.context.set_intent(intent, confidence)
        
        # Extract entities
        entities = self.entity_extractor.extract_entities(message)
        
        # Store extracted entities in the context
        for entity_type, entity_values in entities.items():
            if entity_type in ["dates", "times", "numeric_values", "thresholds", "locations"]:
                # These are lists of entities
                for entity in entity_values:
                    # Store each entity with a more specific key
                    entity_key = f"{entity_type}_{entity['text'].replace(' ', '_')}"
                    self.context.add_entity(entity_key, entity)
            else:
                # Direct entity values
                self.context.add_entity(entity_type, entity_values)
        
        # If confidence is below threshold, ask for clarification
        if confidence < self.confidence_threshold:
            fallback_options = get_fallback_options(message)
            response = (
                "I'm not sure I understand what you want to do. Would you like to:\n" +
                "\n".join(f"- {option}" for option in fallback_options)
            )
            self.context.add_system_message(response)
            return {
                "response": response,
                "action": None,
                "requires_confirmation": False,
                "options": fallback_options
            }
        
        # Create action based on intent and entities
        action = self._create_action_from_intent(intent, entities, message)
        
        # Add the pending action to the context
        if action:
            action_type = "monitor_event" if intent == "continuous" else "set_reminder"
            self.context.add_pending_action(action_type, action)
            
            # Generate confirmation message
            confirmation_message = self._generate_confirmation_message(action_type, action)
            self.context.add_system_message(confirmation_message)
            
            return {
                "response": confirmation_message,
                "action": action,
                "requires_confirmation": True
            }
        else:
            # If we couldn't create an action, ask for more information
            response = (
                "I understood you want " + 
                ("continuous monitoring" if intent == "continuous" else "a one-time reminder") +
                ", but I need more details. Could you provide more information?"
            )
            self.context.add_system_message(response)
            self.context.current_state = "clarifying"
            return {
                "response": response,
                "action": None,
                "requires_confirmation": False
            }
    
    def _handle_clarifying_state(self, message: str) -> Dict[str, Any]:
        """
        Handle messages in the clarifying state.
        
        Args:
            message: The user's message
            
        Returns:
            Response dictionary
        """
        # Check if the message is selecting one of the fallback options
        affirmative = any(word in message.lower() for word in ["yes", "yeah", "sure", "okay", "yep", "yup", "correct"])
        
        if affirmative and "continuous" in message.lower():
            # User selected continuous monitoring
            self.context.set_intent("continuous", 0.9)
        elif affirmative and ("one-time" in message.lower() or "reminder" in message.lower()):
            # User selected one-time reminder
            self.context.set_intent("one_time", 0.9)
        else:
            # Extract new entities from the clarification message
            new_entities = self.entity_extractor.extract_entities(message)
            
            # Add new entities to the existing context
            for entity_type, entity_values in new_entities.items():
                if entity_type in ["dates", "times", "numeric_values", "thresholds", "locations"]:
                    for entity in entity_values:
                        entity_key = f"{entity_type}_{entity['text'].replace(' ', '_')}"
                        self.context.add_entity(entity_key, entity)
                else:
                    self.context.add_entity(entity_type, entity_values)
        
        # Combine the original message with the clarification to get better context
        combined_message = ""
        for history_item in self.context.history:
            if history_item["speaker"] == "user":
                combined_message += " " + history_item["text"]
        
        # Re-extract all entities with the combined message
        all_entities = self.entity_extractor.extract_entities(combined_message)
        
        # Create action based on intent and entities
        intent = self.context.current_intent or "one_time"  # Default to one_time if no intent set
        action = self._create_action_from_intent(intent, all_entities, combined_message)
        
        # Add the pending action to the context
        if action:
            action_type = "monitor_event" if intent == "continuous" else "set_reminder"
            self.context.add_pending_action(action_type, action)
            
            # Generate confirmation message
            confirmation_message = self._generate_confirmation_message(action_type, action)
            self.context.add_system_message(confirmation_message)
            
            return {
                "response": confirmation_message,
                "action": action,
                "requires_confirmation": True
            }
        else:
            # If we still couldn't create an action, ask for specific information
            missing_info = self._identify_missing_information(intent, all_entities)
            response = f"I still need more information. Could you please tell me {missing_info}?"
            self.context.add_system_message(response)
            return {
                "response": response,
                "action": None,
                "requires_confirmation": False
            }
    
    def _handle_confirming_state(self, message: str) -> Dict[str, Any]:
        """
        Handle messages in the confirming state.
        
        Args:
            message: The user's message
            
        Returns:
            Response dictionary
        """
        # Check if the message is a confirmation or rejection
        confirmation_words = ["yes", "yeah", "sure", "okay", "confirm", "correct", "right", "yep", "yup"]
        rejection_words = ["no", "nope", "cancel", "wrong", "incorrect", "not right", "not correct"]
        
        message_lower = message.lower()
        
        # Check for confirmation
        if any(word in message_lower for word in confirmation_words):
            # Confirm the pending action
            confirmed_action = self.context.confirm_action()
            
            if confirmed_action:
                response = "Great! I've confirmed your request. "
                
                if confirmed_action["action_type"] == "monitor_event":
                    response += "I'll monitor this event and let you know when it happens."
                else:  # set_reminder
                    response += "I'll remind you at the scheduled time."
                
                self.context.add_system_message(response)
                return {
                    "response": response,
                    "action": confirmed_action,
                    "requires_confirmation": False,
                    "confirmed": True
                }
            else:
                # No pending action to confirm
                response = "I don't have any pending requests to confirm. What would you like me to do?"
                self.context.add_system_message(response)
                self.context.current_state = "initial"
                return {
                    "response": response,
                    "action": None,
                    "requires_confirmation": False
                }
        
        # Check for rejection
        elif any(word in message_lower for word in rejection_words):
            # Reject the pending action
            rejected_action = self.context.reject_action()
            
            if rejected_action:
                response = "I've canceled that request. Is there something else you'd like me to help with?"
                self.context.add_system_message(response)
                self.context.current_state = "initial"
                return {
                    "response": response,
                    "action": None,
                    "requires_confirmation": False,
                    "canceled": True
                }
            else:
                # No pending action to reject
                response = "I don't have any pending requests to cancel. What would you like me to do?"
                self.context.add_system_message(response)
                self.context.current_state = "initial"
                return {
                    "response": response,
                    "action": None,
                    "requires_confirmation": False
                }
        
        # If it's neither confirmation nor rejection, treat as modification
        else:
            # Extract entities from the modification message
            modification_entities = self.entity_extractor.extract_entities(message)
            
            # Get the last pending action
            if self.context.pending_actions:
                pending_action = self.context.pending_actions[-1]
                
                # Update the action with new entities
                updated_action = self._update_action_with_entities(pending_action, modification_entities)
                
                # Remove the old pending action and add the updated one
                self.context.reject_action()
                action_type = pending_action["action_type"]
                self.context.add_pending_action(action_type, updated_action)
                
                # Generate confirmation message
                confirmation_message = self._generate_confirmation_message(action_type, updated_action)
                confirmation_message = "I've updated your request. " + confirmation_message
                self.context.add_system_message(confirmation_message)
                
                return {
                    "response": confirmation_message,
                    "action": updated_action,
                    "requires_confirmation": True,
                    "modified": True
                }
            else:
                # No pending action to modify
                response = "I don't have any pending requests to modify. What would you like me to do?"
                self.context.add_system_message(response)
                self.context.current_state = "initial"
                return {
                    "response": response,
                    "action": None,
                    "requires_confirmation": False
                }
    
    def _create_action_from_intent(self, intent: str, entities: Dict[str, Any], original_message: str) -> Dict[str, Any]:
        """
        Create an action based on the intent and extracted entities.
        
        Args:
            intent: The classified intent ("continuous" or "one_time")
            entities: Dictionary of extracted entities
            original_message: The original user message
            
        Returns:
            Action dictionary or None if insufficient information
        """
        action = {
            "original_query": original_message,
        }
        
        # Add the subject if available
        if "subject" in entities:
            action["subject"] = entities["subject"]
        
        # Handle continuous monitoring intent
        if intent == "continuous":
            # Need a subject and ideally a threshold
            if "subject" not in entities:
                return None
            
            action["type"] = "continuous"
            
            # Add thresholds if available
            if "thresholds" in entities:
                action["conditions"] = entities["thresholds"]
            
            # Add event type if available
            if "event_type" in entities:
                action["event_type"] = entities["event_type"]
            
        # Handle one-time reminder intent
        else:  # one_time
            # Need a subject and ideally a date/time
            if "subject" not in entities:
                return None
            
            action["type"] = "one_time"
            
            # Add date if available
            if "dates" in entities and entities["dates"]:
                action["date"] = entities["dates"][0]["parsed"]  # Use the first date found
            
            # Add time if available
            if "times" in entities and entities["times"]:
                action["time"] = entities["times"][0]["parsed"]  # Use the first time found
            
            # If no explicit date/time, check if there are relative time references
            if "date" not in action and "time" not in action:
                # We need at least some time reference for a reminder
                return None
        
        # If we get here, we have enough information for an action
        return action
    
    def _update_action_with_entities(self, action: Dict[str, Any], entities: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update an existing action with new entities.
        
        Args:
            action: The existing action dictionary
            entities: New entities to incorporate
            
        Returns:
            Updated action dictionary
        """
        updated_action = action.copy()
        
        # Update the parameters with new entities
        if "parameters" in updated_action:
            params = updated_action["parameters"].copy()
        else:
            params = {}
        
        # Update subject if provided
        if "subject" in entities:
            params["subject"] = entities["subject"]
        
        # Update date if provided
        if "dates" in entities and entities["dates"]:
            params["date"] = entities["dates"][0]["parsed"]
        
        # Update time if provided
        if "times" in entities and entities["times"]:
            params["time"] = entities["times"][0]["parsed"]
        
        # Update thresholds if provided
        if "thresholds" in entities:
            params["conditions"] = entities["thresholds"]
        
        # Update event type if provided
        if "event_type" in entities:
            params["event_type"] = entities["event_type"]
        
        updated_action["parameters"] = params
        return updated_action
    
    def _generate_confirmation_message(self, action_type: str, action: Dict[str, Any]) -> str:
        """
        Generate a confirmation message for the user.
        
        Args:
            action_type: Type of the action ("monitor_event" or "set_reminder")
            action: Action dictionary with details
            
        Returns:
            Confirmation message string
        """
        if action_type == "monitor_event":
            message = "I'll monitor "
            
            if "subject" in action:
                message += f"{action['subject']}"
            else:
                message += "this event"
            
            if "conditions" in action and isinstance(action["conditions"], list) and action["conditions"]:
                condition = action["conditions"][0]
                if condition["type"] == "above":
                    message += f" and notify you when it goes above {condition['value']}"
                    if condition.get("is_price", False):
                        message += "$"
                elif condition["type"] == "below":
                    message += f" and notify you when it goes below {condition['value']}"
                    if condition.get("is_price", False):
                        message += "$"
                elif condition["type"] == "between":
                    message += f" and notify you when it's between {condition['min_value']} and {condition['max_value']}"
                    if condition.get("is_price", False):
                        message += "$"
            
            message += ". Is this correct?"
            
        else:  # set_reminder
            message = "I'll remind you about "
            
            if "subject" in action:
                message += f"{action['subject']}"
            else:
                message += "this"
            
            if "date" in action and "time" in action:
                message += f" on {action['date']} at {action['time']}"
            elif "date" in action:
                message += f" on {action['date']}"
            elif "time" in action:
                message += f" at {action['time']}"
            
            message += ". Is this correct?"
        
        return message
    
    def _identify_missing_information(self, intent: str, entities: Dict[str, Any]) -> str:
        """
        Identify what information is missing for a complete action.
        
        Args:
            intent: The current intent
            entities: The extracted entities
            
        Returns:
            String describing the missing information
        """
        missing = []
        
        # Always need a subject
        if "subject" not in entities:
            missing.append("what you want me to track or remind you about")
        
        # For continuous monitoring, we ideally need conditions
        if intent == "continuous" and "thresholds" not in entities:
            missing.append("what conditions should trigger the notification")
        
        # For one-time reminders, we need date/time
        if intent == "one_time":
            if "dates" not in entities or not entities["dates"]:
                missing.append("the date for the reminder")
            
            if "times" not in entities or not entities["times"]:
                missing.append("the time for the reminder")
        
        if not missing:
            return "more details about your request"
        
        if len(missing) == 1:
            return missing[0]
        
        return ", ".join(missing[:-1]) + " and " + missing[-1]
    
    def get_conversation_summary(self) -> Dict[str, Any]:
        """
        Get a summary of the current conversation.
        
        Returns:
            Dictionary with conversation summary
        """
        return self.context.get_conversation_summary()
    
    def save_conversation(self, directory: str = "./conversations") -> str:
        """
        Save the conversation context to disk.
        
        Args:
            directory: Directory where to save the conversation
            
        Returns:
            Path to the saved file
        """
        return self.context.save(directory)
    
    @classmethod
    def load_conversation(cls, filename: str) -> 'DialogueManager':
        """
        Load a conversation from disk.
        
        Args:
            filename: Path to the saved conversation file
            
        Returns:
            DialogueManager with the loaded conversation
        """
        context = ConversationContext.load(filename)
        manager = cls(context.user_id, context.conversation_id)
        manager.context = context
        return manager 