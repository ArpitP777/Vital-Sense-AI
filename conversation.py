"""
conversation.py

Manages healthcare-related feedback conversation state.
Maintains a buffer of messages for context, analysis, and session tracking.
"""

from typing import List, Dict, Optional
from datetime import datetime


class ConversationManager:
    """
    Manages the conversational flow and history for collecting healthcare feedback.
    
    Features:
        - Message history management (user/assistant roles)
        - Conversation transcript generation
        - Session metadata tracking
        - Message count and statistics
        - Context window management for long conversations
    """
    
    MAX_HISTORY_LENGTH = 50  # Maximum messages before truncation
    
    def __init__(self, session_id: Optional[str] = None):
        """
        Initialize conversation manager.
        
        Args:
            session_id: Optional unique session identifier
        """
        self.messages: List[Dict[str, str]] = []
        self.session_id = session_id
        self.created_at = datetime.now()
        self.last_activity = datetime.now()
        self.is_active = True
    
    def add_user_message(self, content: str) -> None:
        """
        Add a user message to the history.
        
        Args:
            content: The message text from the user
        """
        if not content or not content.strip():
            return
            
        self.messages.append({
            "role": "user",
            "content": content.strip(),
            "timestamp": datetime.now().isoformat()
        })
        self.last_activity = datetime.now()
        self._enforce_max_length()
    
    def add_assistant_message(self, content: str) -> None:
        """
        Add an assistant message to the history.
        
        Args:
            content: The message text from the assistant
        """
        if not content or not content.strip():
            return
            
        self.messages.append({
            "role": "assistant",
            "content": content.strip(),
            "timestamp": datetime.now().isoformat()
        })
        self.last_activity = datetime.now()
        self._enforce_max_length()
    
    def add_system_message(self, content: str) -> None:
        """
        Add a system message (internal notes, not shown to user).
        
        Args:
            content: The system message content
        """
        self.messages.append({
            "role": "system",
            "content": content.strip(),
            "timestamp": datetime.now().isoformat()
        })
        
    def get_history(self) -> List[Dict[str, str]]:
        """
        Get the message history formatted for LLM context.
        Returns only role and content (excludes timestamps).
        
        Returns:
            List of message dictionaries [{'role': ..., 'content': ...}]
        """
        return [
            {"role": msg["role"], "content": msg["content"]}
            for msg in self.messages
            if msg["role"] in ("user", "assistant")
        ]
    
    def get_full_history(self) -> List[Dict[str, str]]:
        """
        Get complete message history including timestamps and system messages.
        
        Returns:
            Full list of all message dictionaries
        """
        return self.messages.copy()
    
    def get_conversation_transcript(self) -> str:
        """
        Get the complete conversation transcript as a formatted string.
        Suitable for LLM analysis.
        
        Returns:
            Full conversation transcript with labeled speakers
        """
        if not self.messages:
            return ""
            
        transcript_lines = []
        for msg in self.messages:
            if msg["role"] == "system":
                continue  # Skip system messages in transcript
            role_name = "Patient" if msg["role"] == "user" else "Assistant"
            transcript_lines.append(f"{role_name}: {msg['content']}")
            
        return "\n".join(transcript_lines)
    
    def get_last_message(self, role: Optional[str] = None) -> Optional[Dict[str, str]]:
        """
        Get the last message, optionally filtered by role.
        
        Args:
            role: Optional role filter ('user' or 'assistant')
            
        Returns:
            Last message dict or None if no messages
        """
        if not self.messages:
            return None
            
        if role:
            for msg in reversed(self.messages):
                if msg["role"] == role:
                    return msg
            return None
            
        return self.messages[-1]
    
    def get_message_count(self) -> Dict[str, int]:
        """
        Get count of messages by role.
        
        Returns:
            Dictionary with counts: {'user': n, 'assistant': m, 'total': n+m}
        """
        user_count = sum(1 for m in self.messages if m["role"] == "user")
        assistant_count = sum(1 for m in self.messages if m["role"] == "assistant")
        
        return {
            "user": user_count,
            "assistant": assistant_count,
            "total": user_count + assistant_count
        }
    
    def get_session_duration(self) -> float:
        """
        Get session duration in seconds.
        
        Returns:
            Duration in seconds since session started
        """
        return (self.last_activity - self.created_at).total_seconds()
    
    def is_empty(self) -> bool:
        """Check if conversation has no messages."""
        return len(self.messages) == 0
    
    def _enforce_max_length(self) -> None:
        """Trim old messages if history exceeds maximum length."""
        if len(self.messages) > self.MAX_HISTORY_LENGTH:
            # Keep most recent messages, remove oldest
            excess = len(self.messages) - self.MAX_HISTORY_LENGTH
            self.messages = self.messages[excess:]
    
    def end_session(self) -> None:
        """Mark the session as ended."""
        self.is_active = False
        self.last_activity = datetime.now()
    
    def reset(self) -> None:
        """Reset the conversation manager for a new session."""
        self.messages = []
        self.created_at = datetime.now()
        self.last_activity = datetime.now()
        self.is_active = True
    
    def __len__(self) -> int:
        """Return the number of messages in the conversation."""
        return len(self.messages)
    
    def __repr__(self) -> str:
        """String representation of the conversation manager."""
        counts = self.get_message_count()
        return (
            f"ConversationManager("
            f"messages={counts['total']}, "
            f"session_id={self.session_id}, "
            f"active={self.is_active})"
        )

