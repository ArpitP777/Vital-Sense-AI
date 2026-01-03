"""
llm_assistant.py

Uses LLM to generate natural conversational responses from the assistant.
"""

import os
from typing import Optional
from llm_client import LLMClient
from conversational_assistant import ConversationalAssistant


class LLMAssistant:
    """Generates natural conversational responses using LLM."""
    
    def __init__(self, provider: str = "openai"):
        """Initialize the LLM assistant."""
        self.llm_client = LLMClient(provider=provider)
        self.conversation = ConversationalAssistant()
    
    def generate_response(self, user_message: str) -> str:
        """
        Generate a natural response to the user's message.
        
        Args:
            user_message: The user's message
            
        Returns:
            Assistant's response
        """
        # Add user message to conversation
        self.conversation.add_user_message(user_message)
        
        # Build conversation context
        context = self.conversation.get_conversation_context()
        
        # Generate response using LLM
        try:
            # Use a simple prompt for conversational response
            user_prompt = f"""Previous conversation:
{context}

Continue the conversation naturally. Respond to the patient's last message as an empathetic healthcare feedback assistant. Keep your response brief (1-3 sentences), warm, and conversational. Do NOT summarize or score anything."""

            # Get response from LLM
            # For conversational mode, we just want text, not JSON
            # We'll use the provider's chat completion directly
            try:
                if hasattr(self.llm_client.provider, 'client'):
                    client = self.llm_client.provider.client
                    if hasattr(client, 'chat') and hasattr(client.chat, 'completions'):
                        # OpenAI style
                        response = client.chat.completions.create(
                            model="gpt-3.5-turbo",
                            messages=[
                                {"role": "system", "content": self.conversation.ASSISTANT_SYSTEM_PROMPT},
                                {"role": "user", "content": user_prompt}
                            ],
                            temperature=0.7,
                            max_tokens=150
                        )
                        assistant_response = response.choices[0].message.content.strip()
                    elif hasattr(client, 'messages') and hasattr(client.messages, 'create'):
                        # Anthropic style
                        message = client.messages.create(
                            model="claude-3-haiku-20240307",
                            max_tokens=150,
                            system=self.conversation.ASSISTANT_SYSTEM_PROMPT,
                            messages=[{"role": "user", "content": user_prompt}]
                        )
                        assistant_response = message.content[0].text.strip()
                    else:
                        # Fallback to mock response
                        assistant_response = self._generate_mock_response(user_message)
                else:
                    # Mock provider fallback
                    assistant_response = self._generate_mock_response(user_message)
            except Exception as e:
                print(f"Error in LLM response generation: {e}")
                assistant_response = self._generate_mock_response(user_message)
            
            # Add assistant response to conversation
            self.conversation.add_assistant_message(assistant_response)
            
            return assistant_response
            
        except Exception as e:
            print(f"Error generating response: {e}")
            # Fallback response
            fallback = "I understand. Could you tell me a bit more about that?"
            self.conversation.add_assistant_message(fallback)
            return fallback
    
    def _generate_mock_response(self, user_message: str) -> str:
        """Generate a simple mock response for testing."""
        message_lower = user_message.lower()
        
        if any(word in message_lower for word in ["good", "great", "excellent", "satisfied"]):
            return "That's wonderful to hear! Can you tell me more about what made it a positive experience?"
        elif any(word in message_lower for word in ["bad", "poor", "terrible", "unhappy"]):
            return "I'm sorry to hear that. Would you like to share more details about what happened?"
        elif any(word in message_lower for word in ["wait", "long", "slow"]):
            return "I understand that waiting can be frustrating. How long did you wait, and how did that affect your experience?"
        elif any(word in message_lower for word in ["staff", "doctor", "nurse"]):
            return "Thank you for sharing that. How did the staff make you feel during your visit?"
        else:
            return "Thank you for sharing. Is there anything else about your experience you'd like to tell me?"
    
    def start_conversation(self) -> str:
        """Start a new conversation."""
        return self.conversation.start_conversation()
    
    def end_conversation(self) -> str:
        """End the conversation."""
        return self.conversation.end_conversation()
    
    def get_conversation_transcript(self) -> str:
        """Get the full conversation transcript for analysis."""
        return self.conversation.get_conversation_context()
    
    def is_active(self) -> bool:
        """Check if conversation is active."""
        return self.conversation.is_conversation_active()
    
    def reset(self):
        """Reset the assistant."""
        self.conversation.reset()

