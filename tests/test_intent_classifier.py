import unittest
from remedy.services.classifier.intent_classifier import (
    classify_query, get_fallback_options, CONFIDENCE_THRESHOLD
)

class TestIntentClassifier(unittest.TestCase):
    def test_high_confidence_continuous_queries(self):
        """Test that continuous monitoring queries are correctly classified with high confidence."""
        continuous_queries = [
            "Notify me when Coby Mayo makes an MLB roster",
            "Alert me when the new iPhone is released",
            "Let me know when tickets for the Taylor Swift concert go on sale",
            "Keep an eye on Bitcoin prices and tell me if they go above $100,000",
            "Track the weather and tell me if it's going to rain this weekend",
            "Monitor the stock price of AAPL and alert me if it drops below $150",
        ]
        
        for query in continuous_queries:
            intent, confidence = classify_query(query)
            self.assertEqual(intent, "continuous", f"Failed to classify as continuous: {query}")
            self.assertGreaterEqual(confidence, CONFIDENCE_THRESHOLD, 
                                  f"Confidence too low for continuous query: {query}, got {confidence}")
    
    def test_high_confidence_one_time_queries(self):
        """Test that one-time reminder queries are correctly classified with high confidence."""
        one_time_queries = [
            "Remind me when the next Jordan 4s release on 05/05/2025 09:00",
            "Set a reminder for my doctor's appointment on March 15th at 2:30 PM",
            "Remind me about the team meeting tomorrow at 10 AM",
            "Schedule a reminder for my tax deadline on April 15th, 2025",
            "Remind me to call mom on her birthday June 12th",
        ]
        
        for query in one_time_queries:
            intent, confidence = classify_query(query)
            self.assertEqual(intent, "one_time", f"Failed to classify as one_time: {query}")
            self.assertGreaterEqual(confidence, CONFIDENCE_THRESHOLD, 
                                  f"Confidence too low for one_time query: {query}, got {confidence}")
    
    def test_low_confidence_queries(self):
        """Test that ambiguous queries result in low confidence and appropriate fallback options."""
        ambiguous_queries = [
            "I need to know about the game",
            "Something about the weather",
            "Tell me about the meeting",
            "Is there any update?",
            "What about that thing we discussed?",
        ]
        
        for query in ambiguous_queries:
            intent, confidence = classify_query(query)
            self.assertLess(confidence, CONFIDENCE_THRESHOLD, 
                          f"Confidence too high for ambiguous query: {query}, got {confidence}")
            
            options = get_fallback_options(query)
            self.assertGreaterEqual(len(options), 2, f"Not enough fallback options for: {query}")
            
            # Check that options present meaningful alternatives
            self.assertTrue(any("one-time" in option.lower() for option in options), 
                          f"No one-time option in fallback for: {query}")
            self.assertTrue(any("monitor" in option.lower() or "alert" in option.lower() 
                              for option in options), 
                          f"No continuous monitoring option in fallback for: {query}")
    
    def test_edge_cases(self):
        """Test edge cases like empty strings and gibberish."""
        edge_cases = [
            "",
            "   ",
            None,
            "asdfghjklqwertyuiop",
            "!@#$%^&*()",
            123,  # Non-string input should be handled gracefully
        ]
        
        for case in edge_cases:
            try:
                if case is None or not isinstance(case, str):
                    # For non-string inputs, test that they don't cause exceptions
                    intent, confidence = classify_query(case)
                    self.assertIn(intent, ["continuous", "one_time"], f"Invalid intent for edge case: {case}")
                    self.assertGreaterEqual(confidence, 0.0, f"Negative confidence for edge case: {case}")
                    self.assertLessEqual(confidence, 1.0, f"Confidence > 1.0 for edge case: {case}")
                    
                    options = get_fallback_options(case)
                    self.assertGreaterEqual(len(options), 2, f"Not enough fallback options for edge case: {case}")
                else:
                    # For valid but meaningless strings
                    intent, confidence = classify_query(case)
                    self.assertLess(confidence, CONFIDENCE_THRESHOLD, 
                                  f"Confidence too high for edge case: {case}")
                    
                    options = get_fallback_options(case)
                    self.assertGreaterEqual(len(options), 2, f"Not enough fallback options for edge case: {case}")
            except Exception as e:
                self.fail(f"Exception raised for edge case {case}: {str(e)}")
    
    def test_threshold_boundary(self):
        """Test behavior right at the confidence threshold boundary."""
        # This test would ideally mock the classification logic to force confidence values
        # right at the threshold boundary, but we'll use examples that are likely
        # to be near the boundary
        
        boundary_queries = [
            "Tell me about the event tomorrow",  # Ambiguous but has time indicator
            "Update me on the project",  # Could be one-time or continuous
            "Information about the conference",  # Unclear intent
        ]
        
        for query in boundary_queries:
            intent, confidence = classify_query(query)
            
            # If confidence is below threshold, check fallback options
            if confidence < CONFIDENCE_THRESHOLD:
                options = get_fallback_options(query)
                self.assertGreaterEqual(len(options), 2, 
                                      f"Not enough fallback options near threshold: {query}, confidence: {confidence}")
            # If confidence is above threshold, validate the intent makes sense
            else:
                self.assertIn(intent, ["continuous", "one_time"], 
                            f"Invalid intent near threshold: {query}, confidence: {confidence}")

if __name__ == "__main__":
    unittest.main()
