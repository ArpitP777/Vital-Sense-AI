"""
conversational_assistant.py

Manages natural, two-way conversational interactions with patients.
Handles the assistant's persona, conversation flow, and state management.
"""

from typing import List, Dict, Optional, Tuple
from enum import Enum
from datetime import datetime


class ConversationState(Enum):
    """Enum representing the current state of the conversation."""
    IDLE = "idle"
    ACTIVE = "active"
    ENDING = "ending"
    COMPLETED = "completed"


class ConversationalAssistant:
    """
    Manages natural conversation flow for healthcare feedback collection.
    
    This assistant maintains empathetic, patient-centered dialogue
    while gathering meaningful feedback about healthcare experiences.
    
    Attributes:
        state: Current conversation state
        conversation_history: List of all messages exchanged
        topics_discussed: Set of topics mentioned during conversation
    """
    
    # System prompt defining the assistant's persona and behavior
    ASSISTANT_SYSTEM_PROMPT = """You are a calm, empathetic healthcare feedback assistant engaged in a real-time, two-way conversation with a patient.

This is NOT a survey and NOT a one-way interview. You are having a genuine conversation.

CONVERSATION CONTROL RULES:
- The conversation starts ONLY after the user explicitly begins it.
- The conversation remains active until the user explicitly ends it.
- Behave like a present, attentive human listener at all times.
- Do NOT rush to conclusions or endings.
- Do NOT assume the conversation is finished unless the user ends it.

INTERACTION BEHAVIOR:
- Respond to every user message naturally and thoughtfully.
- Allow the user to speak freely without forcing questions.
- If the user pauses or gives short responses, gently encourage elaboration.
- Ask follow-up questions only when helpful and relevant.
- If the user changes topics, adapt smoothly without breaking flow.

TONE & STYLE:
- Warm, supportive, and genuinely conversational
- Never robotic, scripted, or repetitive
- Acknowledge emotions before responding to content
- Keep responses concise and human-like (1-3 sentences typically)
- Use natural language, avoid clinical or formal phrasing

CONTEXT AWARENESS:
- Maintain full memory of the conversation.
- Refer back to earlier points naturally (e.g., "You mentioned earlier...").
- Track topics but do not force them - let the conversation flow.
- Notice patterns and themes in what the patient shares.

IMPORTANT RESTRICTIONS:
- Do NOT generate scores or ratings during the conversation.
- Do NOT summarize unless the user explicitly ends the conversation.
- Do NOT control the conversation length - the user controls it.
- Do NOT ask multiple questions at once.

GOAL:
- Listen actively and empathetically.
- Understand the patient's complete experience.
- Let the conversation flow naturally until the user chooses to end it.
- Gather insights about: satisfaction, positives, negatives, and suggestions.

Keep responses brief, empathetic, and natural. Respond as a caring listener would."""

    # Pre-defined responses for common scenarios
    GREETINGS = [
        "Hello! I'm here to listen about your healthcare experience today. What would you like to share?",
        "Hi there! I'd love to hear about your recent healthcare visit. How did it go?",
        "Welcome! I'm here to understand your healthcare experience. Feel free to share anything on your mind."
    ]
    
    CLOSING_MESSAGES = [
        "Thank you so much for sharing your experience with me. Your feedback is really valuable.",
        "I appreciate you taking the time to share this. Your input helps us improve.",
        "Thank you for this conversation. Your feedback will make a real difference."
    ]
    
    ENCOURAGEMENT_PROMPTS = [
        "I see. Would you like to tell me more about that?",
        "Thank you for sharing. Is there anything else you'd like to add?",
        "I understand. Feel free to share any other thoughts you have."
    ]

    def __init__(self):
        """Initialize the conversational assistant."""
        self.conversation_history: List[Dict[str, str]] = []
        self.state = ConversationState.IDLE
        self.topics_discussed: set = set()
        self.created_at: Optional[datetime] = None
        self.ended_at: Optional[datetime] = None
        self._greeting_index = 0
    
    def start_conversation(self) -> str:
        """
        Start a new conversation session.
        
        Returns:
            The greeting message to display to the user
        """
        self.conversation_history = []
        self.state = ConversationState.ACTIVE
        self.topics_discussed = set()
        self.created_at = datetime.now()
        self.ended_at = None
        
        # Rotate through greetings for variety
        greeting = self.GREETINGS[self._greeting_index % len(self.GREETINGS)]
        self._greeting_index += 1
        
        self.conversation_history.append({
            "role": "assistant",
            "content": greeting,
            "timestamp": datetime.now().isoformat()
        })
        
        return greeting
    
    def end_conversation(self) -> str:
        """
        End the conversation gracefully.
        
        Returns:
            The closing message to display
        """
        if self.state == ConversationState.IDLE:
            return "There's no active conversation to end."
        
        if self.state == ConversationState.COMPLETED:
            return "This conversation has already ended."
        
        self.state = ConversationState.COMPLETED
        self.ended_at = datetime.now()
        
        # Select closing message based on conversation length
        msg_count = len([m for m in self.conversation_history if m["role"] == "user"])
        if msg_count >= 5:
            closing = self.CLOSING_MESSAGES[0]  # Longer conversation - full thanks
        elif msg_count >= 2:
            closing = self.CLOSING_MESSAGES[1]  # Medium conversation
        else:
            closing = self.CLOSING_MESSAGES[2]  # Short conversation
        
        self.conversation_history.append({
            "role": "assistant",
            "content": closing,
            "timestamp": datetime.now().isoformat()
        })
        
        return closing
    
    def add_user_message(self, message: str) -> bool:
        """
        Add a user message to the conversation history.
        
        Args:
            message: The user's message text
            
        Returns:
            True if message was added, False if conversation not active
        """
        if self.state != ConversationState.ACTIVE:
            return False
            
        if not message or not message.strip():
            return False
        
        cleaned_message = message.strip()
        
        self.conversation_history.append({
            "role": "user",
            "content": cleaned_message,
            "timestamp": datetime.now().isoformat()
        })
        
        # Track topics mentioned (simple keyword detection)
        self._detect_topics(cleaned_message)
        
        return True
    
    def add_assistant_message(self, message: str) -> bool:
        """
        Add an assistant response to the conversation history.
        
        Args:
            message: The assistant's response text
            
        Returns:
            True if message was added, False if conversation not active
        """
        if self.state not in (ConversationState.ACTIVE, ConversationState.ENDING):
            return False
            
        if not message or not message.strip():
            return False
        
        self.conversation_history.append({
            "role": "assistant",
            "content": message.strip(),
            "timestamp": datetime.now().isoformat()
        })
        
        return True
    
    def _detect_topics(self, message: str) -> None:
        """
        Detect and track topics mentioned in a message.
        
        Args:
            message: The message to analyze
        """
        message_lower = message.lower()
        
        topic_keywords = {
            "wait_time": ["wait", "waiting", "long time", "hours", "delay"],
            "staff": ["staff", "nurse", "doctor", "receptionist", "employee"],
            "facility": ["room", "building", "facility", "parking", "clean"],
            "communication": ["explain", "told", "said", "understand", "confused"],
            "treatment": ["treatment", "procedure", "medicine", "prescription"],
            "billing": ["cost", "bill", "insurance", "payment", "expensive"],
            "appointment": ["appointment", "schedule", "booking", "available"],
            "overall_positive": ["good", "great", "excellent", "happy", "satisfied"],
            "overall_negative": ["bad", "poor", "terrible", "unhappy", "disappointed"]
        }
        
        for topic, keywords in topic_keywords.items():
            if any(kw in message_lower for kw in keywords):
                self.topics_discussed.add(topic)
    
    def get_conversation_context(self) -> str:
        """
        Get the conversation history formatted for LLM context.
        
        Returns:
            Formatted conversation string with role labels
        """
        formatted = []
        for msg in self.conversation_history:
            role_label = "Assistant" if msg["role"] == "assistant" else "Patient"
            formatted.append(f"{role_label}: {msg['content']}")
        return "\n\n".join(formatted)
    
    def get_history_for_llm(self) -> List[Dict[str, str]]:
        """
        Get conversation history in LLM-compatible format.
        
        Returns:
            List of message dicts with 'role' and 'content' keys only
        """
        return [
            {"role": msg["role"], "content": msg["content"]}
            for msg in self.conversation_history
        ]
    
    def get_conversation_summary(self) -> Dict:
        """
        Get a summary of the conversation for analysis.
        
        Returns:
            Dictionary containing conversation metadata and statistics
        """
        user_messages = [m for m in self.conversation_history if m["role"] == "user"]
        assistant_messages = [m for m in self.conversation_history if m["role"] == "assistant"]
        
        duration = None
        if self.created_at:
            end_time = self.ended_at or datetime.now()
            duration = (end_time - self.created_at).total_seconds()
        
        return {
            "state": self.state.value,
            "message_count": len(self.conversation_history),
            "user_message_count": len(user_messages),
            "assistant_message_count": len(assistant_messages),
            "topics_discussed": list(self.topics_discussed),
            "duration_seconds": duration,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "ended_at": self.ended_at.isoformat() if self.ended_at else None
        }
    
    def is_conversation_active(self) -> bool:
        """
        Check if conversation is currently active.
        
        Returns:
            True if conversation is in ACTIVE state
        """
        return self.state == ConversationState.ACTIVE
    
    def get_suggested_followup(self) -> Optional[str]:
        """
        Get a suggested follow-up question based on topics not yet discussed.
        
        Returns:
            A follow-up question string, or None if nothing to suggest
        """
        unexplored_prompts = {
            "wait_time": "I haven't heard about wait times - was there any waiting involved?",
            "staff": "How was your interaction with the staff?",
            "facility": "What did you think of the facilities?",
            "treatment": "Can you tell me about the care or treatment you received?"
        }
        
        for topic, prompt in unexplored_prompts.items():
            if topic not in self.topics_discussed:
                return prompt
        
        return None
    
    def should_end_naturally(self) -> Tuple[bool, str]:
        """
        Determine if the conversation should naturally conclude.
        
        Returns:
            Tuple of (should_end, reason)
        """
        user_msgs = [m for m in self.conversation_history if m["role"] == "user"]
        
        # Check if last message indicates ending
        if user_msgs:
            last_msg = user_msgs[-1]["content"].lower()
            end_phrases = ["that's all", "nothing else", "i'm done", "that's it", "no more"]
            if any(phrase in last_msg for phrase in end_phrases):
                return True, "User indicated completion"
        
        # Check if conversation is very long
        if len(user_msgs) > 15:
            return True, "Conversation length limit reached"
        
        return False, ""
    
    def reset(self) -> None:
        """Reset the conversation assistant for a new session."""
        self.conversation_history = []
        self.state = ConversationState.IDLE
        self.topics_discussed = set()
        self.created_at = None
        self.ended_at = None
    
    def __len__(self) -> int:
        """Return the number of messages in the conversation."""
        return len(self.conversation_history)
    
    def __repr__(self) -> str:
        """String representation of the assistant."""
        return (
            f"ConversationalAssistant("
            f"state={self.state.value}, "
            f"messages={len(self.conversation_history)}, "
            f"topics={len(self.topics_discussed)})"
        )

