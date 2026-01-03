"""
llm_client.py

Handles communication with the LLM API.
Abstracted to allow easy swapping of LLM providers.
Supports both real-time chat and structured analysis.
"""

import json
import os
import random
import time
from typing import Dict, List, Optional
from abc import ABC, abstractmethod


class LLMProvider(ABC):
    """Abstract base class for LLM providers."""
    
    @abstractmethod
    def analyze_conversation(self, conversation: str, system_prompt: str) -> str:
        """Analyze a conversation and return structured JSON response."""
        pass

    @abstractmethod
    def chat_completion(self, messages: List[Dict[str, str]], system_prompt: str) -> str:
        """
        Generate a conversational response based on history.
        
        Args:
            messages: List of message dictionaries [{'role': 'user', 'content': ...}]
            system_prompt: The system instruction for the persona
            
        Returns:
            The assistant's text response
        """
        pass


class OpenAIProvider(LLMProvider):
    """OpenAI API implementation."""
    
    def __init__(self, api_key: Optional[str] = None):
        try:
            import openai 
            self.client = openai.OpenAI(api_key=api_key or os.getenv("OPENAI_API_KEY"))
            self.model = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
        except ImportError:
            raise ImportError("openai package is required. Install with: pip install openai")
        except Exception as e:
            raise Exception(f"Failed to initialize OpenAI client: {e}")
    
    def analyze_conversation(self, conversation: str, system_prompt: str) -> str:
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": conversation}
                ],
                temperature=0.0,
                response_format={"type": "json_object"}
            )
            return response.choices[0].message.content
        except Exception as e:
            raise Exception(f"OpenAI API analysis error: {e}")

    def chat_completion(self, messages: List[Dict[str, str]], system_prompt: str) -> str:
        try:
            # Prepend system prompt to messages
            full_messages = [{"role": "system", "content": system_prompt}] + messages
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=full_messages,
                temperature=0.7,  # Higher for more natural conversation
            )
            return response.choices[0].message.content
        except Exception as e:
            raise Exception(f"OpenAI API chat error: {e}")


class AnthropicProvider(LLMProvider):
    """Anthropic Claude API implementation."""
    
    def __init__(self, api_key: Optional[str] = None):
        try:
            import anthropic 
            self.client = anthropic.Anthropic(api_key=api_key or os.getenv("ANTHROPIC_API_KEY"))
            self.model = os.getenv("ANTHROPIC_MODEL", "claude-3-haiku-20240307")
        except ImportError:
            raise ImportError("anthropic package is required. Install with: pip install anthropic")
        except Exception as e:
            raise Exception(f"Failed to initialize Anthropic client: {e}")
    
    def analyze_conversation(self, conversation: str, system_prompt: str) -> str:
        try:
            message = self.client.messages.create(
                model=self.model,
                max_tokens=1024,
                system=system_prompt,
                messages=[{"role": "user", "content": conversation}]
            )
            return message.content[0].text
        except Exception as e:
            raise Exception(f"Anthropic API analysis error: {e}")

    def chat_completion(self, messages: List[Dict[str, str]], system_prompt: str) -> str:
        try:
            # Anthropic expects specific role alternation, ensuring we start with user if needed
            # But the inputs are usually clean. System prompt is separate parameter.
            
            response = self.client.messages.create(
                model=self.model,
                max_tokens=1024,
                system=system_prompt,
                messages=messages
            )
            return response.content[0].text
        except Exception as e:
            raise Exception(f"Anthropic API chat error: {e}")


class MockProvider(LLMProvider):
    """Mock provider for testing without API access."""
    
    def analyze_conversation(self, conversation: str, system_prompt: str) -> str:
        """Mock analysis returning dashboard-ready data."""
        conversation_lower = conversation.lower()
        
        # Negative experience
        if any(word in conversation_lower for word in ["bad", "terrible", "long", "wait"]):
            return json.dumps({
                "satisfaction_score": 2,
                "radar_metrics": {
                    "felt_heard": 2,
                    "concerns_addressed": 2,
                    "clear_communication": 3,
                    "respect_shown": 3,
                    "time_given": 1
                },
                "confidence_in_treatment": "partial",
                "duration_satisfaction": 2,
                "staff_behavior": 3,
                "summary_bullets": [
                    "Patient experienced significant wait times",
                    "Consultation felt rushed due to delays",
                    "Concerns were partially addressed",
                    "Recommend reviewing scheduling processes"
                ]
            })
        
        # Positive experience
        elif any(word in conversation_lower for word in ["good", "great", "excellent", "amazing"]):
            return json.dumps({
                "satisfaction_score": 5,
                "radar_metrics": {
                    "felt_heard": 5,
                    "concerns_addressed": 5,
                    "clear_communication": 5,
                    "respect_shown": 5,
                    "time_given": 5
                },
                "confidence_in_treatment": "yes",
                "duration_satisfaction": 5,
                "staff_behavior": 5,
                "summary_bullets": [
                    "Patient highly satisfied with overall care",
                    "Staff was attentive and professional",
                    "Clear communication throughout visit",
                    "Would recommend to others",
                    "No concerns or issues raised"
                ]
            })
        
        # Rude staff experience
        elif any(word in conversation_lower for word in ["rude", "mean", "dismissive", "ignored"]):
            return json.dumps({
                "satisfaction_score": 1,
                "radar_metrics": {
                    "felt_heard": 1,
                    "concerns_addressed": 2,
                    "clear_communication": 2,
                    "respect_shown": 1,
                    "time_given": 2
                },
                "confidence_in_treatment": "no",
                "duration_satisfaction": 2,
                "staff_behavior": 1,
                "summary_bullets": [
                    "Patient felt dismissed by staff",
                    "Communication was poor or unclear",
                    "Did not feel respected during visit",
                    "Urgent follow-up recommended",
                    "Consider staff training on patient interactions"
                ]
            })
        
        # Neutral experience
        else:
            return json.dumps({
                "satisfaction_score": 3,
                "radar_metrics": {
                    "felt_heard": 3,
                    "concerns_addressed": 3,
                    "clear_communication": 3,
                    "respect_shown": 4,
                    "time_given": 3
                },
                "confidence_in_treatment": "partial",
                "duration_satisfaction": 3,
                "staff_behavior": 4,
                "summary_bullets": [
                    "Patient had a routine healthcare experience",
                    "No major concerns raised",
                    "Standard care was provided",
                    "Continue monitoring for patterns"
                ]
            })

    def chat_completion(self, messages: List[Dict[str, str]], system_prompt: str) -> str:
        """Mock conversational responses with variety based on context."""
        
        last_message = messages[-1]["content"].lower() if messages else ""
        num_exchanges = len([m for m in messages if m.get("role") == "user"])
        
        # Simulate thinking time
        time.sleep(0.3)
        
        # First message / greeting
        if num_exchanges <= 1:
            greetings = [
                "Hello! I'm here to hear about your healthcare visit today. How was your overall experience?",
                "Hi there! Thank you for taking the time to share your feedback. What brings you here today?",
                "Welcome! I'd love to hear about your recent healthcare experience. What stood out to you?"
            ]
            return random.choice(greetings)
        
        # Negative sentiment responses
        if any(w in last_message for w in ["bad", "terrible", "awful", "horrible", "worst"]):
            negatives = [
                "I'm truly sorry to hear that. That sounds very difficult. Can you tell me more about what happened?",
                "That's really concerning to hear. Your experience matters. What specifically went wrong?",
                "I appreciate you sharing that, even though it was negative. What would have made it better?"
            ]
            return random.choice(negatives)
        
        if any(w in last_message for w in ["long", "slow", "wait", "waiting", "delayed"]):
            wait_responses = [
                "Wait times can be so frustrating. How long did you have to wait approximately?",
                "I understand waiting is difficult. Did anyone communicate about the delay?",
                "That's a common concern we hear. Was there anything available to make the wait more comfortable?"
            ]
            return random.choice(wait_responses)
        
        if any(w in last_message for w in ["rude", "mean", "dismissive", "ignored"]):
            rude_responses = [
                "I'm sorry you felt that way. No one should feel dismissed. Who was involved in that interaction?",
                "That's not the experience we want anyone to have. Can you describe what happened?",
                "Your feelings are valid. Would you like to share more details about that interaction?"
            ]
            return random.choice(rude_responses)
        
        # Positive sentiment responses
        if any(w in last_message for w in ["good", "great", "excellent", "amazing", "wonderful"]):
            positives = [
                "That's wonderful to hear! What made it such a positive experience?",
                "I'm so glad! Was there a particular person or aspect that stood out?",
                "That's great feedback! Would you recommend us to others? Why?"
            ]
            return random.choice(positives)
        
        if any(w in last_message for w in ["nice", "friendly", "helpful", "kind", "caring"]):
            friendly_responses = [
                "It's great that the staff made a positive impression! Anyone specific you'd like to mention?",
                "We love hearing this! Friendly interactions make such a difference, don't they?",
                "That's exactly what we aim for. Was the rest of your visit equally positive?"
            ]
            return random.choice(friendly_responses)
        
        # Topic-specific responses
        if any(w in last_message for w in ["doctor", "physician", "dr"]):
            return random.choice([
                "How was your interaction with the doctor? Did they address all your concerns?",
                "The doctor-patient relationship is so important. Did you feel heard?",
                "Was the doctor able to explain things in a way you understood?"
            ])
        
        if any(w in last_message for w in ["nurse", "nurses", "nursing"]):
            return random.choice([
                "Nurses play such a vital role. How was your experience with them?",
                "Our nursing staff works hard. Did they make you feel comfortable?",
                "Were the nurses attentive to your needs?"
            ])
        
        if any(w in last_message for w in ["appointment", "schedule", "booking"]):
            return random.choice([
                "How was the appointment scheduling process?",
                "Was it easy to get an appointment at a time that worked for you?",
                "Did the appointment start on time?"
            ])
        
        if any(w in last_message for w in ["clean", "dirty", "facility", "room", "building"]):
            return random.choice([
                "The environment matters. Was the facility up to your expectations?",
                "Cleanliness is important to us. How did you find the facilities?",
                "What did you think about the overall atmosphere of our facility?"
            ])
        
        # Off-topic redirect
        if any(w in last_message for w in ["marketing", "sales", "weather", "sports", "politics"]):
            return "I appreciate the conversation! Though I'd love to hear more about your healthcare experience specifically. Anything else you'd like to share about your visit?"
        
        # Default varied responses based on conversation progress
        if num_exchanges == 2:
            defaults = [
                "Thank you for sharing that. Is there anything specific about the staff you'd like to mention?",
                "I appreciate that feedback. What about the facilities - how did you find them?",
                "Got it. How was the communication throughout your visit?"
            ]
        elif num_exchanges == 3:
            defaults = [
                "That's helpful to know. Were there any surprises during your visit, good or bad?",
                "I see. If you could change one thing about your experience, what would it be?",
                "Thank you. Is there anything else that stands out in your memory?"
            ]
        elif num_exchanges == 4:
            defaults = [
                "You've shared some valuable insights. Any final thoughts before we wrap up?",
                "This is really helpful feedback. Anything else you'd like to add?",
                "I appreciate all you've shared. Is there anything we haven't covered?"
            ]
        else:
            defaults = [
                "Thank you for continuing to share. What else would you like to mention?",
                "I'm still listening. Feel free to share any other thoughts.",
                "Is there anything else about your experience you'd like to discuss?",
                "Your feedback is valuable. Please continue if there's more.",
                "I appreciate your openness. What else comes to mind?"
            ]
        
        return random.choice(defaults)


class LLMClient:
    """Main LLM client that wraps provider implementations."""
    
    def __init__(self, provider: str = "mock", api_key: Optional[str] = None):
        provider_lower = provider.lower()
        
        if provider_lower == "openai":
            self.provider = OpenAIProvider(api_key)
        elif provider_lower == "anthropic":
            self.provider = AnthropicProvider(api_key)
        elif provider_lower == "mock":
            self.provider = MockProvider()
        else:
            print(f"Warning: Unknown provider '{provider}', falling back to Mock.")
            self.provider = MockProvider()
    
    def analyze_feedback(self, conversation: str, system_prompt: str) -> Dict:
        """Analyze healthcare feedback conversation and return structured data."""
        try:
            # Some providers might return code blocks, strip them
            raw_response = self.provider.analyze_conversation(conversation, system_prompt)
            clean_response = raw_response.strip()
            
            if clean_response.startswith("```json"):
                clean_response = clean_response[7:]
            if clean_response.endswith("```"):
                clean_response = clean_response[:-3]
                
            return json.loads(clean_response)
        except json.JSONDecodeError:
            # Fallback for simple errors
            print(f"Error parsing JSON from LLM: {raw_response[:100]}...")
            return {
                "satisfaction_score": 3, 
                "summary": "Analysis failed to parse.", 
                "key_issues": ["Analysis Error"]
            }
        except Exception as e:
            print(f"Analysis failed: {e}")
            return {}

    def chat(self, messages: List[Dict[str, str]], system_prompt: str) -> str:
        """Get a conversational response."""
        return self.provider.chat_completion(messages, system_prompt)
