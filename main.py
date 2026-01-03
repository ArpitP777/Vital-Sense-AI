"""
main.py

Entry point for the Real-Time Healthcare Feedback System.
Orchestrates the live conversation flow:
    System Idle -> "start" -> Interactive Chat Loop -> "end" -> Analysis -> Storage
"""

import os
import sys
import time

# Load environment variables
try:
    from dotenv import load_dotenv  # type: ignore
    load_dotenv()
except ImportError:
    pass

from conversation import ConversationManager
from prompts import get_system_prompt, get_user_message, CONVERSATIONAL_SYSTEM_PROMPT
from llm_client import LLMClient
from feedback_analyzer import FeedbackAnalyzer
from storage import FeedbackStorage
from speech_input import SpeechInput
from speech_output import SpeechOutput


def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')


def main():
    """Main execution loop."""
    
    # 1. Initialization
    clear_screen()
    print("=" * 70)
    print("HEALTHCARE FEEDBACK ASSISTANT (REAL-TIME)")
    print("=" * 70)
    
    # Initialize components
    conversation = ConversationManager()
    storage = FeedbackStorage("feedback_data.csv")
    
    # Voice components
    speech_input = SpeechInput()
    speech_output = SpeechOutput()
    use_voice = False
    
    # Initialize LLM
    provider = os.getenv("LLM_PROVIDER", "mock").lower()
    print(f"System initializing with provider: {provider.upper()}")
    
    try:
        llm_client = LLMClient(provider=provider)
    except Exception as e:
        print(f"Error initializing LLM: {e}")
        print("Falling back to mock.")
        llm_client = LLMClient(provider="mock")

    # 2. Idle State
    print("\n[SYSTEM READY]")
    print("Type 'start' to begin the conversation.")
    print("Type 'end' during conversation to finish and analyze.")
    print("-" * 70)

    while True:
        try:
            start_cmd = input(">> ").strip().lower()
            if start_cmd == "start":
                break
            elif start_cmd == "exit" or start_cmd == "quit":
                print("Exiting system.")
                return
        except KeyboardInterrupt:
            return

    # Check for voice preference
    if speech_input.is_available() or speech_output.is_available():
        v_resp = input("\nEnable voice mode? (y/n): ").strip().lower()
        use_voice = v_resp in ['y', 'yes']

    # 3. Conversation Loop
    print("\n[SESSION STARTED]")
    print("(Assistant is typing...)")
    
    # Initial greeting from Assistant
    initial_greeting = "Hello! Thank you for speaking with us today. To start, how was your overall experience at the clinic?"
    print(f"\nAssistant: {initial_greeting}")
    if use_voice:
        speech_output.speak(initial_greeting)
        
    conversation.add_assistant_message(initial_greeting)

    while True:
        try:
            # A. Get User Input
            user_text = speech_input.get_input("\nYou: ", use_voice=use_voice)
            
            if not user_text:
                continue
                
            # Check for termination
            if user_text.strip().lower() == "end":
                print("\n[Ending session...]")
                break
            
            conversational_history = conversation.get_history()
            
            # Optimization: If history is too long, we might truncate (future feature)
            
            conversation.add_user_message(user_text)
            
            # B. Get Real-Time Assistant Response
            print("Assistant: ...", end='\r') # Simple loading indicator
            
            assistant_response = llm_client.chat(
                conversation.get_history(),
                CONVERSATIONAL_SYSTEM_PROMPT
            )
            
            print(f"Assistant: {assistant_response}")
            
            if use_voice:
                speech_output.speak(assistant_response)
                
            conversation.add_assistant_message(assistant_response)
            
        except KeyboardInterrupt:
            print("\n[Session interrupted]")
            break
        except Exception as e:
            print(f"\nError: {e}")
            break

    # 4. Analysis Phase
    transcript = conversation.get_conversation_transcript()
    if not transcript:
        print("No conversation recorded.")
        return

    print("\n" + "=" * 70)
    print("ANALYZING CONVERSATION...")
    print("=" * 70)
    
    try:
        # Prepare for analysis
        analysis_system_prompt = get_system_prompt()
        analysis_user_message = get_user_message(transcript)
        
        # Call LLM for analysis
        # Note: We treat the whole transcript as one user message for the analysis prompt
        llm_response = llm_client.analyze_feedback(analysis_user_message, analysis_system_prompt)
        
        # Process and Validate
        analyzer = FeedbackAnalyzer()
        feedback = analyzer.process_llm_output(llm_response)
        
        # Display
        print(analyzer.format_feedback_display(feedback))
        
        # Save
        print("\nSaving to database...")
        if storage.save_feedback(feedback):
            print("✓ Saved to feedback_data.csv")
        else:
            print("X Error saving data")
            
    except Exception as e:
        print(f"Analysis failed: {e}")

    print("\nSession Closed.")

if __name__ == "__main__":
    main()
