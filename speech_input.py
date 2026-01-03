"""
speech_input.py (Optional)

Handles voice input for accessibility and modern UX.
Converts speech to text using speech recognition.
Gracefully falls back to text input if voice fails.
"""

import sys
from typing import Optional


class SpeechInput:
    """Handles speech-to-text conversion for user input."""
    
    def __init__(self):
        """Initialize speech recognition (if available)."""
        self.speech_available = False
        self.recognizer = None
        self.microphone = None
        
        try:
            import speech_recognition as sr  # type: ignore
            self.recognizer = sr.Recognizer()
            self.microphone = sr.Microphone()
            
            # Adjust for ambient noise
            with self.microphone as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
            
            self.speech_available = True
        except ImportError:
            # speech_recognition not installed - that's okay, we'll use text
            self.speech_available = False
        except Exception as e:
            # Microphone or other issues - fall back to text
            print(f"Speech recognition not available: {e}")
            self.speech_available = False
    
    def get_input(self, prompt: str, use_voice: bool = False) -> str:
        """
        Get user input either via voice or text.
        
        Args:
            prompt: Prompt to display to the user
            use_voice: Whether to attempt voice input first
            
        Returns:
            User input as string
        """
        # Try voice input if requested and available
        if use_voice and self.speech_available:
            try:
                print(f"\n🎤 Listening... (speak your response)")
                with self.microphone as source:
                    audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=30)
                
                print("Processing audio...")
                text = self.recognizer.recognize_google(audio)
                print(f"You said: {text}\n")
                return text
                
            except Exception as e:
                print(f"Voice recognition failed: {e}")
                print("Falling back to text input...\n")
                # Fall through to text input
        
        # Text input fallback (or default)
        try:
            return input(prompt)
        except KeyboardInterrupt:
            print("\n\nInterrupted by user.")
            sys.exit(0)
        except EOFError:
            return ""
    
    def is_available(self) -> bool:
        """
        Check if speech input is available.
        
        Returns:
            True if speech recognition is available, False otherwise
        """
        return self.speech_available

