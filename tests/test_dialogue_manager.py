import unittest
from remedy.services.conversation.dialogue_manager import DialogueManager
from remedy.services.classifier.intent_classifier import CONFIDENCE_THRESHOLD

class TestDialogueManager(unittest.TestCase):
    def setUp(self):
        # Create a fresh dialogue manager for each test
        self.dialogue_manager = DialogueManager()
    
    def test_initial_state_high_confidence_continuous(self):
        """Test that a high-confidence continuous monitoring query is handled correctly in the initial state."""
        response = self.dialogue_manager.process_message("Notify me when the new iPhone is released")
        
        self.assertEqual(self.dialogue_manager.context.current_state, "confirming")
        self.assertEqual(self.dialogue_manager.context.current_intent, "continuous")
        self.assertGreaterEqual(self.dialogue_manager.context.intent_confidence, CONFIDENCE_THRESHOLD)
        self.assertTrue(response["requires_confirmation"])
        self.assertIsNotNone(response["action"])
        self.assertIn("monitor", response["response"])
        self.assertIn("iPhone", response["response"])
    
    def test_initial_state_high_confidence_one_time(self):
        """Test that a high-confidence one-time reminder query is handled correctly in the initial state."""
        response = self.dialogue_manager.process_message("Remind me about my doctor's appointment on March 15th at 2:30 PM")
        
        self.assertEqual(self.dialogue_manager.context.current_state, "confirming")
        self.assertEqual(self.dialogue_manager.context.current_intent, "one_time")
        self.assertGreaterEqual(self.dialogue_manager.context.intent_confidence, CONFIDENCE_THRESHOLD)
        self.assertTrue(response["requires_confirmation"])
        self.assertIsNotNone(response["action"])
        self.assertIn("remind", response["response"])
        self.assertIn("doctor", response["response"])
    
    def test_initial_state_low_confidence(self):
        """Test that a low-confidence query requests clarification."""
        response = self.dialogue_manager.process_message("Tell me about the meeting")
        
        self.assertEqual(self.dialogue_manager.context.current_state, "clarifying")
        self.assertLess(self.dialogue_manager.context.intent_confidence, CONFIDENCE_THRESHOLD)
        self.assertFalse(response["requires_confirmation"])
        self.assertIsNone(response["action"])
        self.assertIn("not sure", response["response"])
        self.assertTrue("options" in response)
        self.assertGreaterEqual(len(response["options"]), 2)
    
    def test_incomplete_info_one_time(self):
        """Test that a one-time reminder query with incomplete information asks for more details."""
        response = self.dialogue_manager.process_message("Remind me about the meeting")
        
        # Should still be high confidence for one_time intent, but missing date/time
        self.assertEqual(self.dialogue_manager.context.current_intent, "one_time")
        self.assertGreaterEqual(self.dialogue_manager.context.intent_confidence, CONFIDENCE_THRESHOLD)
        
        # Should ask for more information
        self.assertEqual(self.dialogue_manager.context.current_state, "clarifying")
        self.assertFalse(response["requires_confirmation"])
        self.assertIsNone(response["action"])
        self.assertIn("more details", response["response"])
    
    def test_incomplete_info_continuous(self):
        """Test that a continuous monitoring query with incomplete information asks for more details."""
        response = self.dialogue_manager.process_message("Track the price")
        
        # Should still be high confidence for continuous intent, but missing specific details
        self.assertEqual(self.dialogue_manager.context.current_intent, "continuous")
        
        # Should ask for more information
        self.assertEqual(self.dialogue_manager.context.current_state, "clarifying")
        self.assertFalse(response["requires_confirmation"])
        self.assertIsNone(response["action"])
        self.assertIn("more details", response["response"])
    
    def test_clarifying_state_adds_info(self):
        """Test that providing additional information in the clarifying state leads to action creation."""
        # Start with incomplete information
        self.dialogue_manager.process_message("Remind me about the meeting")
        
        # Provide more information
        response = self.dialogue_manager.process_message("on next Monday at 3 PM")
        
        # Should now have enough information for an action
        self.assertEqual(self.dialogue_manager.context.current_state, "confirming")
        self.assertTrue(response["requires_confirmation"])
        self.assertIsNotNone(response["action"])
        self.assertIn("remind", response["response"])
        self.assertIn("meeting", response["response"])
    
    def test_confirmation_state_confirm(self):
        """Test that confirming an action in the confirming state leads to action confirmation."""
        # Create an action that requires confirmation
        self.dialogue_manager.process_message("Remind me about my doctor's appointment on March 15th at 2:30 PM")
        
        # Confirm the action
        response = self.dialogue_manager.process_message("Yes, that's correct")
        
        self.assertEqual(self.dialogue_manager.context.current_state, "complete")
        self.assertFalse(response["requires_confirmation"])
        self.assertTrue(response.get("confirmed", False))
        self.assertIn("confirmed", response["response"])
    
    def test_confirmation_state_reject(self):
        """Test that rejecting an action in the confirming state resets the state."""
        # Create an action that requires confirmation
        self.dialogue_manager.process_message("Remind me about my doctor's appointment on March 15th at 2:30 PM")
        
        # Reject the action
        response = self.dialogue_manager.process_message("No, that's not right")
        
        self.assertEqual(self.dialogue_manager.context.current_state, "initial")
        self.assertFalse(response["requires_confirmation"])
        self.assertTrue(response.get("canceled", False))
        self.assertIn("canceled", response["response"])
    
    def test_confirmation_state_modify(self):
        """Test that modifying an action in the confirming state updates the action."""
        # Create an action that requires confirmation
        self.dialogue_manager.process_message("Remind me about my doctor's appointment on March 15th at 2:30 PM")
        
        # Modify the action
        response = self.dialogue_manager.process_message("Change it to March 16th at 3:00 PM")
        
        self.assertEqual(self.dialogue_manager.context.current_state, "confirming")
        self.assertTrue(response["requires_confirmation"])
        self.assertTrue(response.get("modified", False))
        self.assertIn("updated", response["response"])
    
    def test_multi_turn_conversation(self):
        """Test a complete multi-turn conversation with clarification and confirmation."""
        # Start with vague request
        response1 = self.dialogue_manager.process_message("I need a reminder")
        
        # Should be clarifying
        self.assertEqual(self.dialogue_manager.context.current_state, "clarifying")
        
        # Add details
        response2 = self.dialogue_manager.process_message("for my dentist appointment next Friday at 10 AM")
        
        # Should now be confirming
        self.assertEqual(self.dialogue_manager.context.current_state, "confirming")
        self.assertTrue(response2["requires_confirmation"])
        
        # Modify some details
        response3 = self.dialogue_manager.process_message("actually make it 11 AM")
        
        # Should still be confirming, but with updated time
        self.assertEqual(self.dialogue_manager.context.current_state, "confirming")
        self.assertTrue(response3["requires_confirmation"])
        self.assertIn("11", response3["response"])
        
        # Confirm
        response4 = self.dialogue_manager.process_message("Yes, that's perfect")
        
        # Should be complete
        self.assertEqual(self.dialogue_manager.context.current_state, "complete")
        self.assertTrue(response4.get("confirmed", False))
    
    def test_conversation_context_management(self):
        """Test that conversation history and context are properly maintained."""
        # Have a multi-turn conversation
        self.dialogue_manager.process_message("Remind me about the meeting")
        self.dialogue_manager.process_message("on Monday at 2 PM")
        self.dialogue_manager.process_message("Yes, that's correct")
        
        # Check conversation summary
        summary = self.dialogue_manager.get_conversation_summary()
        
        # Should have 3 user messages and corresponding system messages
        self.assertEqual(summary["turns"], 6)  # 3 user + 3 system messages
        self.assertEqual(summary["current_state"], "complete")
        self.assertEqual(summary["confirmed_actions_count"], 1)

if __name__ == "__main__":
    unittest.main() 