"""
speech_output.py (Optional)

Converts text questions to speech for accessibility.
Uses text-to-speech to read questions aloud.
Improves demo impact and accessibility.
"""

from typing import Optional


class SpeechOutput:
    """Handles text-to-speech conversion for questions."""
    
    def __init__(self):
        """Initialize text-to-speech (if available)."""
        self.tts_available = False
        self.engine = None
        
        try:
            import pyttsx3  # type: ignore
            self.engine = pyttsx3.init()
            
            # Set speech rate and volume (optional customization)
            self.engine.setProperty('rate', 150)  # Speed of speech
            self.engine.setProperty('volume', 0.9)  # Volume level (0.0 to 1.0)
            
            self.tts_available = True
        except ImportError:
            # pyttsx3 not installed - that's okay, we'll just print text
            self.tts_available = False
        except Exception as e:
            # TTS initialization failed - fall back to text only
            print(f"Text-to-speech not available: {e}")
            self.tts_available = False
    
    def speak(self, text: str, async_mode: bool = False):
        """
        Convert text to speech and speak it aloud.
        
        Args:
            text: Text to speak
            async_mode: If True, speak asynchronously (non-blocking)
        """
        if not self.tts_available:
            return
        
        try:
            if async_mode:
                # Run in background (requires threading)
                import threading
                thread = threading.Thread(target=self.engine.say, args=(text,))
                thread.daemon = True
                thread.start()
            else:
                self.engine.say(text)
                self.engine.runAndWait()
        except Exception as e:
            # Silently fail - text display is still available
            pass
    
    def ask_question(self, question: str, use_voice: bool = True):
        """
        Ask a question both in text and voice.
        
        Args:
            question: Question to ask
            use_voice: Whether to also speak the question aloud
        """
        # Always print the question
        print(f"\n{question}")
        
        # Optionally speak it
        if use_voice and self.tts_available:
            self.speak(question)
    
    def is_available(self) -> bool:
        """
        Check if text-to-speech is available.
        
        Returns:
            True if TTS is available, False otherwise
        """
        return self.tts_available

