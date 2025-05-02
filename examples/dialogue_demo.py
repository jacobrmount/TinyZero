#!/usr/bin/env python3
"""
Dialogue Manager Demo Script

This script demonstrates the Remedy dialogue management capability with an
interactive conversation interface. It supports both continuous monitoring
and one-time reminder intents with multi-turn dialogue.

Usage:
    python dialogue_demo.py
"""

import os
import sys
import json
from datetime import datetime

# Add the project root to the path to ensure imports work
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from remedy.services.conversation import DialogueManager
from colorama import init, Fore, Style

# Initialize colorama for colored console output
init()

def print_system_message(message):
    """Print a system message in blue."""
    print(f"\n{Fore.BLUE}Remedy: {message}{Style.RESET_ALL}")

def print_user_message(message):
    """Print a user message in green."""
    print(f"\n{Fore.GREEN}You: {message}{Style.RESET_ALL}")

def print_json(data):
    """Print JSON data in a nicely formatted way."""
    print(f"\n{Fore.YELLOW}DEBUG: {json.dumps(data, indent=2)}{Style.RESET_ALL}")

def print_divider():
    """Print a divider line."""
    print(f"\n{Fore.WHITE}{'-' * 60}{Style.RESET_ALL}")

def main():
    """Run the dialogue manager demo."""
    print_divider()
    print_system_message("Welcome to the Remedy Dialogue Manager Demo!")
    print_system_message("I can help you set up reminders or monitor events.")
    print_system_message("Type 'exit' to quit, 'debug' to see internal state, or 'reset' to start over.")
    print_divider()
    
    # Create a new dialogue manager
    manager = DialogueManager()
    
    while True:
        # Get user input
        user_input = input(f"{Fore.GREEN}You: {Style.RESET_ALL}")
        
        # Check for special commands
        if user_input.lower() == 'exit':
            print_system_message("Goodbye! Thanks for trying the Remedy Dialogue Manager.")
            break
        elif user_input.lower() == 'debug':
            # Print the current conversation state
            print_json(manager.get_conversation_summary())
            print_divider()
            continue
        elif user_input.lower() == 'reset':
            # Create a new dialogue manager
            manager = DialogueManager()
            print_system_message("Conversation has been reset.")
            print_divider()
            continue
        
        # Process the user message
        response = manager.process_message(user_input)
        
        # Print the system response
        print_system_message(response["response"])
        
        # If the action was confirmed, save the conversation for future reference
        if response.get("confirmed", False):
            save_path = manager.save_conversation("./conversation_history")
            print_system_message(f"Conversation saved to {save_path}")
            
            # Optional: Print debug info about the confirmed action
            if "action" in response:
                print_divider()
                print_system_message("Action details:")
                print_json(response["action"])
                print_divider()
        
        print_divider()

if __name__ == "__main__":
    main() 