from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
import uuid
import json
import os

class ConversationContext:
    """
    Manages conversation context across multiple turns of dialogue.
    
    This class handles:
    - Tracking conversation history
    - Storing extracted intents and entities
    - Maintaining state across conversation turns
    - Managing confirmation status of intents
    """
    
    def __init__(self, user_id: str = None, conversation_id: str = None):
        """
        Initialize a new conversation context.
        
        Args:
            user_id: Unique identifier for the user
            conversation_id: Unique identifier for the conversation
        """
        self.user_id = user_id or "anonymous"
        self.conversation_id = conversation_id or str(uuid.uuid4())
        self.created_at = datetime.now()
        self.last_updated = self.created_at
        
        # Conversation history as a list of tuples (speaker, text, timestamp)
        self.history: List[Dict[str, Any]] = []
        
        # Current conversation state
        self.current_state = "initial"  # Options: initial, clarifying, confirming, complete
        
        # Extracted intent and confidence
        self.current_intent: Optional[str] = None
        self.intent_confidence: float = 0.0
        
        # Extracted entities from the conversation
        self.entities: Dict[str, Any] = {}
        
        # Pending actions requiring confirmation
        self.pending_actions: List[Dict[str, Any]] = []
        
        # Confirmed actions
        self.confirmed_actions: List[Dict[str, Any]] = []
    
    def add_user_message(self, text: str) -> None:
        """
        Add a user message to the conversation history.
        
        Args:
            text: The text of the user's message
        """
        message = {
            "speaker": "user",
            "text": text,
            "timestamp": datetime.now()
        }
        self.history.append(message)
        self.last_updated = message["timestamp"]
    
    def add_system_message(self, text: str) -> None:
        """
        Add a system message to the conversation history.
        
        Args:
            text: The text of the system's message
        """
        message = {
            "speaker": "system",
            "text": text,
            "timestamp": datetime.now()
        }
        self.history.append(message)
        self.last_updated = message["timestamp"]
    
    def set_intent(self, intent: str, confidence: float) -> None:
        """
        Set the current intent and confidence score.
        
        Args:
            intent: The identified intent (e.g., "continuous" or "one_time")
            confidence: Confidence score for the intent (0.0 to 1.0)
        """
        self.current_intent = intent
        self.intent_confidence = confidence
        
        if confidence >= 0.7:  # Using the standard threshold
            self.current_state = "confirming"
        else:
            self.current_state = "clarifying"
    
    def add_entity(self, entity_type: str, entity_value: Any) -> None:
        """
        Add an extracted entity to the context.
        
        Args:
            entity_type: The type of entity (e.g., "date", "time", "location")
            entity_value: The value of the entity
        """
        self.entities[entity_type] = entity_value
    
    def add_pending_action(self, action_type: str, parameters: Dict[str, Any]) -> None:
        """
        Add a pending action that requires user confirmation.
        
        Args:
            action_type: The type of action to perform (e.g., "set_reminder", "monitor_event")
            parameters: Parameters needed for the action
        """
        action = {
            "action_type": action_type,
            "parameters": parameters,
            "created_at": datetime.now()
        }
        self.pending_actions.append(action)
        self.current_state = "confirming"
    
    def confirm_action(self, action_index: int = -1) -> Optional[Dict[str, Any]]:
        """
        Confirm a pending action and move it to confirmed actions.
        
        Args:
            action_index: Index of the action to confirm, defaults to the most recent
            
        Returns:
            The confirmed action or None if no action was found
        """
        if not self.pending_actions:
            return None
        
        if action_index == -1:
            # Confirm the most recent action
            action = self.pending_actions.pop()
        else:
            # Confirm a specific action
            if 0 <= action_index < len(self.pending_actions):
                action = self.pending_actions.pop(action_index)
            else:
                return None
        
        action["confirmed_at"] = datetime.now()
        self.confirmed_actions.append(action)
        
        if not self.pending_actions:
            self.current_state = "complete"
            
        return action
    
    def reject_action(self, action_index: int = -1) -> Optional[Dict[str, Any]]:
        """
        Reject a pending action.
        
        Args:
            action_index: Index of the action to reject, defaults to the most recent
            
        Returns:
            The rejected action or None if no action was found
        """
        if not self.pending_actions:
            return None
        
        if action_index == -1:
            # Reject the most recent action
            action = self.pending_actions.pop()
        else:
            # Reject a specific action
            if 0 <= action_index < len(self.pending_actions):
                action = self.pending_actions.pop(action_index)
            else:
                return None
        
        if not self.pending_actions:
            self.current_state = "initial"
            
        return action
    
    def get_conversation_summary(self) -> Dict[str, Any]:
        """
        Get a summary of the conversation context.
        
        Returns:
            Dictionary with conversation summary
        """
        return {
            "conversation_id": self.conversation_id,
            "user_id": self.user_id,
            "created_at": self.created_at.isoformat(),
            "last_updated": self.last_updated.isoformat(),
            "current_state": self.current_state,
            "current_intent": self.current_intent,
            "intent_confidence": self.intent_confidence,
            "entities": self.entities,
            "pending_actions_count": len(self.pending_actions),
            "confirmed_actions_count": len(self.confirmed_actions),
            "turns": len(self.history)
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the conversation context to a dictionary for serialization.
        
        Returns:
            Dictionary representation of the conversation context
        """
        return {
            "conversation_id": self.conversation_id,
            "user_id": self.user_id,
            "created_at": self.created_at.isoformat(),
            "last_updated": self.last_updated.isoformat(),
            "history": self.history,
            "current_state": self.current_state,
            "current_intent": self.current_intent,
            "intent_confidence": self.intent_confidence,
            "entities": self.entities,
            "pending_actions": self.pending_actions,
            "confirmed_actions": self.confirmed_actions
        }
    
    def save(self, directory: str = "./conversations") -> str:
        """
        Save the conversation context to a JSON file.
        
        Args:
            directory: Directory where to save the conversation
            
        Returns:
            Path to the saved file
        """
        os.makedirs(directory, exist_ok=True)
        filename = f"{directory}/{self.conversation_id}.json"
        
        with open(filename, 'w') as f:
            # Convert datetime objects to strings for JSON serialization
            context_dict = self.to_dict()
            json.dump(context_dict, f, indent=2, default=lambda o: o.isoformat() if isinstance(o, datetime) else o)
        
        return filename
    
    @classmethod
    def load(cls, filename: str) -> 'ConversationContext':
        """
        Load a conversation context from a JSON file.
        
        Args:
            filename: Path to the JSON file
            
        Returns:
            Loaded ConversationContext object
        """
        with open(filename, 'r') as f:
            data = json.load(f)
        
        # Create a new instance
        context = cls(user_id=data["user_id"], conversation_id=data["conversation_id"])
        
        # Convert string timestamps back to datetime objects
        context.created_at = datetime.fromisoformat(data["created_at"])
        context.last_updated = datetime.fromisoformat(data["last_updated"])
        
        # Load history with datetime objects
        context.history = []
        for msg in data["history"]:
            msg_copy = msg.copy()
            msg_copy["timestamp"] = datetime.fromisoformat(msg["timestamp"])
            context.history.append(msg_copy)
        
        # Load other attributes
        context.current_state = data["current_state"]
        context.current_intent = data["current_intent"]
        context.intent_confidence = data["intent_confidence"]
        context.entities = data["entities"]
        
        # Load actions with datetime objects
        context.pending_actions = data["pending_actions"]
        context.confirmed_actions = []
        for action in data["confirmed_actions"]:
            action_copy = action.copy()
            action_copy["created_at"] = datetime.fromisoformat(action["created_at"])
            if "confirmed_at" in action:
                action_copy["confirmed_at"] = datetime.fromisoformat(action["confirmed_at"])
            context.confirmed_actions.append(action_copy)
        
        return context 