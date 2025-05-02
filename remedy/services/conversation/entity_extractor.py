from typing import Dict, List, Any, Optional, Tuple
import re
from datetime import datetime, timedelta
import dateparser

class EntityExtractor:
    """
    Extract structured entities from natural language text.
    
    This module identifies and extracts:
    - Dates and times
    - Locations
    - People and organizations
    - Numeric values and thresholds
    - Event types
    """
    
    # Date and time patterns
    DATE_PATTERNS = {
        "formal_date": r"\b(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})\b",  # MM/DD/YYYY or DD/MM/YYYY
        "iso_date": r"\b(\d{4}[/-]\d{1,2}[/-]\d{1,2})\b",    # YYYY/MM/DD
        "named_month_date": r"\b(Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)\s+\d{1,2}(?:st|nd|rd|th)?,?\s+\d{4}\b",  # Month Day, Year
        "day_month_year": r"\b\d{1,2}(?:st|nd|rd|th)?\s+(?:of\s+)?(Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?),?\s+\d{4}\b"  # Day Month Year
    }
    
    TIME_PATTERNS = {
        "formal_time": r"\b(\d{1,2}:\d{2}(?::\d{2})?\s*(?:AM|PM|am|pm)?)\b",  # HH:MM:SS AM/PM
        "hour_only": r"\b(\d{1,2}\s*(?:AM|PM|am|pm))\b",  # HH AM/PM
    }
    
    # Relative time expressions
    RELATIVE_TIME_PATTERNS = {
        "today": r"\b(today|tonight|this\s+evening)\b",
        "tomorrow": r"\b(tomorrow|next\s+day)\b",
        "next_week": r"\b(next\s+week)\b",
        "next_weekend": r"\b(next\s+weekend|this\s+weekend)\b",
        "days_later": r"\b(in\s+(\d+)\s+days?)\b",
        "weeks_later": r"\b(in\s+(\d+)\s+weeks?)\b",
        "months_later": r"\b(in\s+(\d+)\s+months?)\b",
    }
    
    # Weekday patterns
    WEEKDAY_PATTERNS = {
        "weekday": r"\b(Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday|Mon|Tue|Wed|Thu|Fri|Sat|Sun)\b",
        "next_weekday": r"\bnext\s+(Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday|Mon|Tue|Wed|Thu|Fri|Sat|Sun)\b",
    }
    
    # Numeric and threshold patterns
    NUMERIC_PATTERNS = {
        "price": r"\$\s*(\d+(?:,\d{3})*(?:\.\d{2})?)",  # $X,XXX.XX
        "percentage": r"(\d+(?:\.\d+)?)\s*%",  # X%
        "decimal": r"(\d+\.\d+)",  # X.X
        "integer": r"(?<!\w)(\d+)(?!(?:\.\d+)?%|\s*(?:AM|PM|am|pm))(?!\w)",  # X but not part of time or percentage
    }
    
    # Threshold patterns
    THRESHOLD_PATTERNS = {
        "above": r"(above|over|more than|higher than|exceeds?|greater than)\s+(\$?\d+(?:,\d{3})*(?:\.\d{2})?)",
        "below": r"(below|under|less than|lower than|falls? below|smaller than)\s+(\$?\d+(?:,\d{3})*(?:\.\d{2})?)",
        "between": r"between\s+(\$?\d+(?:,\d{3})*(?:\.\d{2})?)\s+and\s+(\$?\d+(?:,\d{3})*(?:\.\d{2})?)",
    }
    
    # Entity type specific patterns
    LOCATION_PATTERNS = {
        "address": r"\b\d{1,5}\s+[A-Za-z0-9\s,]+(?:Avenue|Ave|Street|St|Road|Rd|Drive|Dr|Boulevard|Blvd|Lane|Ln|Place|Pl|Court|Ct|Terrace|Ter|Way)\b",
        "city_state": r"\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*,\s+[A-Z]{2}\b",  # City, STATE
        "country": r"\b(?:USA|United States|Canada|UK|United Kingdom|Australia|Germany|France|Japan|China|India)\b"
    }
    
    EVENT_TYPES = {
        "sports": ["game", "match", "tournament", "olympics", "championship", "race", "playoff", "final"],
        "product": ["release", "launch", "announcement", "unveiling", "update", "new version", "product"],
        "financial": ["stock", "price", "market", "bitcoin", "crypto", "investment", "dividend", "IPO"],
        "entertainment": ["concert", "show", "movie", "release", "premiere", "album", "event", "festival"],
        "personal": ["appointment", "meeting", "call", "deadline", "birthday", "anniversary", "reminder"],
    }
    
    def __init__(self):
        pass
    
    def extract_entities(self, text: str) -> Dict[str, Any]:
        """
        Extract all entities from the given text.
        
        Args:
            text: The text to extract entities from
            
        Returns:
            Dictionary of extracted entities by type
        """
        if not text or not isinstance(text, str):
            return {}
        
        # Normalize text
        normalized_text = text.strip()
        
        # Initialize results dictionary
        entities = {}
        
        # Extract dates and times
        dates = self.extract_dates(normalized_text)
        if dates:
            entities["dates"] = dates
        
        times = self.extract_times(normalized_text)
        if times:
            entities["times"] = times
        
        # Extract numeric values and thresholds
        numeric_values = self.extract_numeric_values(normalized_text)
        if numeric_values:
            entities["numeric_values"] = numeric_values
        
        thresholds = self.extract_thresholds(normalized_text)
        if thresholds:
            entities["thresholds"] = thresholds
        
        # Extract locations
        locations = self.extract_locations(normalized_text)
        if locations:
            entities["locations"] = locations
        
        # Extract event types
        event_type = self.extract_event_type(normalized_text)
        if event_type:
            entities["event_type"] = event_type
        
        # Extract the main subject/event
        subject = self.extract_subject(normalized_text)
        if subject:
            entities["subject"] = subject
        
        return entities
    
    def extract_dates(self, text: str) -> List[Dict[str, Any]]:
        """
        Extract date entities from text.
        
        Args:
            text: Text to extract dates from
            
        Returns:
            List of dictionaries containing date information
        """
        dates = []
        
        # Check for formal date patterns
        for pattern_name, pattern in self.DATE_PATTERNS.items():
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                date_str = match.group(0)
                parsed_date = dateparser.parse(date_str)
                if parsed_date:
                    dates.append({
                        "text": date_str,
                        "parsed": parsed_date.strftime("%Y-%m-%d"),
                        "pattern": pattern_name,
                        "start": match.start(),
                        "end": match.end()
                    })
        
        # Check for relative date patterns
        for pattern_name, pattern in self.RELATIVE_TIME_PATTERNS.items():
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                relative_date_str = match.group(0)
                parsed_date = None
                
                if "today" in pattern_name:
                    parsed_date = datetime.now()
                elif "tomorrow" in pattern_name:
                    parsed_date = datetime.now() + timedelta(days=1)
                elif "next_week" in pattern_name:
                    # Next week = next Monday
                    now = datetime.now()
                    days_until_next_monday = 7 - now.weekday()
                    parsed_date = now + timedelta(days=days_until_next_monday)
                elif "next_weekend" in pattern_name:
                    # Next weekend = next Saturday
                    now = datetime.now()
                    days_until_next_saturday = 5 - now.weekday() if now.weekday() < 5 else 12 - now.weekday()
                    parsed_date = now + timedelta(days=days_until_next_saturday)
                elif "days_later" in pattern_name:
                    days = int(match.group(2))
                    parsed_date = datetime.now() + timedelta(days=days)
                elif "weeks_later" in pattern_name:
                    weeks = int(match.group(2))
                    parsed_date = datetime.now() + timedelta(weeks=weeks)
                elif "months_later" in pattern_name:
                    months = int(match.group(2))
                    # Approximate months as 30 days
                    parsed_date = datetime.now() + timedelta(days=30*months)
                
                if parsed_date:
                    dates.append({
                        "text": relative_date_str,
                        "parsed": parsed_date.strftime("%Y-%m-%d"),
                        "pattern": pattern_name,
                        "start": match.start(),
                        "end": match.end()
                    })
        
        # Check for weekday patterns
        for pattern_name, pattern in self.WEEKDAY_PATTERNS.items():
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                weekday_str = match.group(0)
                weekday_name = match.group(1).lower()
                
                # Map abbreviations to full names
                weekday_map = {
                    "mon": "monday", "tue": "tuesday", "wed": "wednesday", 
                    "thu": "thursday", "fri": "friday", "sat": "saturday", "sun": "sunday"
                }
                
                if weekday_name in weekday_map:
                    weekday_name = weekday_map[weekday_name]
                
                # Get numeric weekday (0 = Monday, 6 = Sunday)
                weekday_num = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"].index(weekday_name)
                
                now = datetime.now()
                current_weekday = now.weekday()
                
                if pattern_name == "weekday":
                    # If current day is after the target weekday, get next week's occurrence
                    days_to_add = (weekday_num - current_weekday) % 7
                    if days_to_add == 0:  # If same day, assume next week
                        days_to_add = 7
                else:  # next_weekday
                    # Always get next week's occurrence
                    days_to_add = (weekday_num - current_weekday) % 7
                    if days_to_add == 0:  # If same day, get next week
                        days_to_add = 7
                    else:
                        days_to_add += 7
                
                parsed_date = now + timedelta(days=days_to_add)
                
                dates.append({
                    "text": weekday_str,
                    "parsed": parsed_date.strftime("%Y-%m-%d"),
                    "pattern": pattern_name,
                    "start": match.start(),
                    "end": match.end()
                })
        
        # Try to use dateparser for any remaining date expressions
        if not dates:
            # Try to extract a date with dateparser if no explicit patterns matched
            parsed_date = dateparser.parse(text, settings={'PREFER_DATES_FROM': 'future'})
            if parsed_date:
                dates.append({
                    "text": text,
                    "parsed": parsed_date.strftime("%Y-%m-%d"),
                    "pattern": "dateparser",
                    "start": 0,
                    "end": len(text)
                })
        
        return dates
    
    def extract_times(self, text: str) -> List[Dict[str, Any]]:
        """
        Extract time entities from text.
        
        Args:
            text: Text to extract times from
            
        Returns:
            List of dictionaries containing time information
        """
        times = []
        
        for pattern_name, pattern in self.TIME_PATTERNS.items():
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                time_str = match.group(0)
                # Parse the time
                parsed_time = dateparser.parse(time_str)
                if parsed_time:
                    times.append({
                        "text": time_str,
                        "parsed": parsed_time.strftime("%H:%M:%S"),
                        "pattern": pattern_name,
                        "start": match.start(),
                        "end": match.end()
                    })
        
        return times
    
    def extract_numeric_values(self, text: str) -> List[Dict[str, Any]]:
        """
        Extract numeric values from text.
        
        Args:
            text: Text to extract numeric values from
            
        Returns:
            List of dictionaries containing numeric value information
        """
        numeric_values = []
        
        for pattern_name, pattern in self.NUMERIC_PATTERNS.items():
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                value_str = match.group(0)
                
                # Extract the numeric value
                numeric_value = match.group(1)
                
                # Clean and convert to appropriate type
                if pattern_name == "price":
                    # Remove $ and commas
                    clean_value = numeric_value.replace("$", "").replace(",", "")
                    try:
                        value = float(clean_value)
                    except ValueError:
                        continue
                elif pattern_name in ["percentage", "decimal"]:
                    try:
                        value = float(numeric_value)
                    except ValueError:
                        continue
                else:  # integer
                    try:
                        value = int(numeric_value)
                    except ValueError:
                        continue
                
                numeric_values.append({
                    "text": value_str,
                    "value": value,
                    "type": pattern_name,
                    "start": match.start(),
                    "end": match.end()
                })
        
        return numeric_values
    
    def extract_thresholds(self, text: str) -> List[Dict[str, Any]]:
        """
        Extract threshold conditions from text.
        
        Args:
            text: Text to extract thresholds from
            
        Returns:
            List of dictionaries containing threshold information
        """
        thresholds = []
        
        for pattern_name, pattern in self.THRESHOLD_PATTERNS.items():
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                threshold_str = match.group(0)
                
                if pattern_name in ["above", "below"]:
                    operator = match.group(1).lower()
                    value_str = match.group(2)
                    
                    # Clean value string and convert to float
                    clean_value = value_str.replace("$", "").replace(",", "")
                    try:
                        value = float(clean_value)
                    except ValueError:
                        continue
                    
                    thresholds.append({
                        "text": threshold_str,
                        "type": "above" if "above" in operator or "over" in operator or "more" in operator or "higher" in operator or "greater" in operator or "exceed" in operator else "below",
                        "value": value,
                        "is_price": "$" in value_str,
                        "start": match.start(),
                        "end": match.end()
                    })
                elif pattern_name == "between":
                    value1_str = match.group(1)
                    value2_str = match.group(2)
                    
                    # Clean value strings and convert to float
                    clean_value1 = value1_str.replace("$", "").replace(",", "")
                    clean_value2 = value2_str.replace("$", "").replace(",", "")
                    
                    try:
                        value1 = float(clean_value1)
                        value2 = float(clean_value2)
                    except ValueError:
                        continue
                    
                    thresholds.append({
                        "text": threshold_str,
                        "type": "between",
                        "min_value": min(value1, value2),
                        "max_value": max(value1, value2),
                        "is_price": "$" in value1_str or "$" in value2_str,
                        "start": match.start(),
                        "end": match.end()
                    })
        
        return thresholds
    
    def extract_locations(self, text: str) -> List[Dict[str, Any]]:
        """
        Extract location entities from text.
        
        Args:
            text: Text to extract locations from
            
        Returns:
            List of dictionaries containing location information
        """
        locations = []
        
        for pattern_name, pattern in self.LOCATION_PATTERNS.items():
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                location_str = match.group(0)
                locations.append({
                    "text": location_str,
                    "type": pattern_name,
                    "start": match.start(),
                    "end": match.end()
                })
        
        return locations
    
    def extract_event_type(self, text: str) -> Optional[str]:
        """
        Extract the type of event from text.
        
        Args:
            text: Text to extract event type from
            
        Returns:
            Event type string or None if not found
        """
        text_lower = text.lower()
        
        # Check each event type category
        for event_category, keywords in self.EVENT_TYPES.items():
            for keyword in keywords:
                if keyword.lower() in text_lower:
                    return event_category
        
        return None
    
    def extract_subject(self, text: str) -> Optional[str]:
        """
        Extract the main subject or topic from the text.
        
        Args:
            text: Text to extract subject from
            
        Returns:
            The main subject string or None if not found
        """
        # Simple heuristic approach to extract the subject
        # Look for phrases after "about", "for", "when", "if"
        subject_match = re.search(r"(?:about|for|when|if)\s+(.*?)(?:\s+on|\s+at|\s+by|\?|$)", text.lower())
        
        if subject_match:
            subject = subject_match.group(1).strip()
            # Limit length and clean up the subject
            if len(subject) > 100:  # Arbitrary limit
                subject = subject[:100] + "..."
            return subject
        
        # Alternative approach: look for the object of the sentence
        # This is a very simplified approach and not linguistically accurate
        after_verb_match = re.search(r"(?:remind|alert|notify|tell|let|inform)\s+(?:me|us)\s+(?:about|of|when|if)?\s+(.*?)(?:\s+on|\s+at|\s+by|\?|$)", text.lower())
        
        if after_verb_match:
            subject = after_verb_match.group(1).strip()
            if len(subject) > 100:
                subject = subject[:100] + "..."
            return subject
        
        return None 