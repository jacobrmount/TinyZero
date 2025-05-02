from typing import Tuple, List, Optional
import re

# Constants
CONFIDENCE_THRESHOLD = 0.7

# Keywords that signal continuous monitoring intent
CONTINUOUS_KEYWORDS = [
    "notify me when", "alert me when", "let me know when", "tell me when",
    "monitor", "track", "watch for", "keep an eye on", "inform me if",
    "continuous", "ongoing", "until", "as soon as", "once", 
    "when", "makes", "if they", "above", "below", "prices", "stock"
]

# Keywords that signal one-time reminder intent
ONE_TIME_KEYWORDS = [
    "remind me", "reminder", "schedule", "on the date", "at time",
    "appointment", "meeting", "deadline", "due", "calendar", "event", 
    "scheduled", "upcoming"
]

# More generic keywords that could apply to either (lower score impact)
AMBIGUOUS_KEYWORDS = [
    "on", "at", "by", "the", "for", "about", "regarding"
]

# Date and time patterns
DATE_PATTERNS = [
    r"\d{1,2}[/-]\d{1,2}[/-]\d{2,4}",  # MM/DD/YYYY or DD/MM/YYYY
    r"\d{4}[/-]\d{1,2}[/-]\d{1,2}",    # YYYY/MM/DD
    r"\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]* \d{1,2}(?:st|nd|rd|th)?,? \d{4}\b",  # Month Day, Year
    r"\b\d{1,2}(?:st|nd|rd|th)? (?:of )?(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*,? \d{4}\b"  # Day Month Year
]

TIME_PATTERNS = [
    r"\d{1,2}:\d{2}(?::\d{2})? ?(?:AM|PM|am|pm)?",  # HH:MM:SS AM/PM
    r"\d{1,2} ?(?:AM|PM|am|pm)",  # HH AM/PM
]

def classify_query(text: str) -> Tuple[str, float]:
    """
    Classify the user's query intent as either continuous monitoring or one-time reminder.
    
    Args:
        text: The user's natural language query
        
    Returns:
        Tuple containing:
        - intent: "continuous" or "one_time"
        - confidence: float between 0.0 and 1.0
    """
    if not text or not isinstance(text, str):
        return ("one_time", 0.0)  # Default with zero confidence for empty/invalid input
    
    # Normalize text
    text = text.lower().strip()
    
    # Special case handling for continuous monitoring phrases
    if any(phrase in text for phrase in ["notify me when", "alert me when", "let me know when"]):
        return ("continuous", 0.95)
    
    if any(phrase in text for phrase in ["keep an eye on", "monitor", "track", "watch for"]):
        return ("continuous", 0.9)
    
    # Special case handling for one-time reminder phrases
    if re.search(r"remind me.+(on|at|by).+(am|pm|\d{1,2}:\d{2}|\d{1,2}/\d{1,2})", text, re.IGNORECASE):
        return ("one_time", 0.95)
    
    # Calculate scores for each intent type
    continuous_score = _calculate_continuous_score(text)
    one_time_score = _calculate_one_time_score(text)
    
    # Handle case where both scores are 0 to avoid division by zero
    if continuous_score == 0 and one_time_score == 0:
        return ("one_time", 0.0)  # Default to one_time with zero confidence
    
    # For ambiguous queries, limit maximum confidence
    if _is_ambiguous_query(text):
        max_confidence = 0.65  # Below the 0.7 threshold
    else:
        max_confidence = 1.0
    
    # Determine the intent with higher score
    if continuous_score > one_time_score:
        intent = "continuous"
        # Normalize confidence to be between 0.5 and 1.0, capped by max_confidence
        total = continuous_score + one_time_score
        confidence = min(0.5 + (continuous_score / total) * 0.5, max_confidence)
    else:
        intent = "one_time"
        # Normalize confidence to be between 0.5 and 1.0, capped by max_confidence
        total = continuous_score + one_time_score
        confidence = min(0.5 + (one_time_score / total) * 0.5, max_confidence)
    
    return (intent, confidence)

def get_fallback_options(text: str) -> List[str]:
    """
    Generate fallback options when confidence is below the threshold.
    
    Args:
        text: The user's natural language query
        
    Returns:
        List of suggested intent clarification options
    """
    if not text or not isinstance(text, str):
        return [
            "Should I set a one-time reminder?", 
            "Would you like me to continuously monitor for an event?"
        ]
    
    # Extract potential event or action from the query
    event_match = re.search(r"(?:about|for|when|if)\s+(.*?)(?:\s+on|\s+at|\s+by|\?|$)", text.lower())
    event = event_match.group(1) if event_match else "this"
    
    # Extract potential date/time if present
    date_time = _extract_date_time(text)
    
    # Generate context-aware options
    options = []
    
    if date_time:
        options.append(f"Set a one-time reminder for {event} on {date_time}")
    else:
        options.append(f"Set a one-time reminder for {event}")
    
    options.append(f"Continuously monitor and alert me when {event} happens")
    
    return options

def _calculate_continuous_score(text: str) -> float:
    """Calculate a score for continuous monitoring intent based on keywords."""
    score = 0.0
    
    # Check for continuous monitoring keywords
    for keyword in CONTINUOUS_KEYWORDS:
        if keyword in text:
            score += 1.0
    
    # Specific pattern matches for common continuous monitoring phrases
    if re.search(r"(notify|alert|tell|let).+?when", text):
        score += 2.0
    
    if "notify me when" in text or "alert me when" in text or "let me know when" in text:
        score += 3.0
    
    # Check for conditional patterns that suggest continuous monitoring
    if re.search(r"if.+(above|below|exceeds|drops|falls|rises|changes)", text):
        score += 2.0
    
    # Key phrases for market monitoring
    if re.search(r"(bitcoin|stock|price|market|crypto|eth|btc).+(above|below|drops|rises)", text):
        score += 2.5
    
    # Reduce score if there are specific dates/times mentioned
    date_time_present = False
    for pattern in DATE_PATTERNS + TIME_PATTERNS:
        if re.search(pattern, text):
            date_time_present = True
            break
    
    if date_time_present:
        score -= 0.5
    
    return max(0.0, score)  # Ensure score is non-negative

def _calculate_one_time_score(text: str) -> float:
    """Calculate a score for one-time reminder intent based on keywords and date/time patterns."""
    score = 0.0
    
    # Check for one-time reminder keywords
    for keyword in ONE_TIME_KEYWORDS:
        if keyword in text:
            score += 1.0
    
    # Check for ambiguous keywords (lower weight)
    for keyword in AMBIGUOUS_KEYWORDS:
        if keyword in text:
            score += 0.2
    
    # Specific pattern matches for common reminder phrases
    if re.search(r"remind me (to|about|of)", text):
        score += 2.0
    
    if "set a reminder" in text or "schedule a reminder" in text:
        score += 2.0
    
    # Increase score if there are specific dates/times mentioned
    for pattern in DATE_PATTERNS + TIME_PATTERNS:
        if re.search(pattern, text):
            score += 1.5
            break
    
    return max(0.0, score)  # Ensure score is non-negative

def _extract_date_time(text: str) -> Optional[str]:
    """Extract date and time information from text if present."""
    # Check for date patterns
    for pattern in DATE_PATTERNS:
        date_match = re.search(pattern, text)
        if date_match:
            return date_match.group(0)
    
    # Check for time patterns
    for pattern in TIME_PATTERNS:
        time_match = re.search(pattern, text)
        if time_match:
            return time_match.group(0)
    
    return None

def _is_ambiguous_query(text: str) -> bool:
    """Determine if a query is ambiguous (lacking clear intent signals)."""
    # Check if the text is too short
    if len(text.split()) < 4:
        return True
    
    # Check if it's a question without clear intent markers
    if text.endswith("?") and not any(kw in text for kw in CONTINUOUS_KEYWORDS + ONE_TIME_KEYWORDS):
        return True
    
    # Check if it starts with ambiguous phrases
    ambiguous_starts = ["tell me about", "what about", "i need", "information", "something about"]
    if any(text.startswith(start) for start in ambiguous_starts):
        return True
    
    # Check if it contains common ambiguous phrases
    ambiguous_phrases = ["the meeting", "the game", "the weather", "the project", "that thing", "any update"]
    if any(phrase in text for phrase in ambiguous_phrases):
        return True
    
    return False
