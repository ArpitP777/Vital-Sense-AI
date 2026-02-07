from typing import List, Dict, Optional
from datetime import datetime


class ConversationManager:
    
    MAX_HISTORY_LENGTH = 50
    
    def __init__(self, session_id: Optional[str] = None):
        self.messages: List[Dict[str, str]] = []
        self.session_id = session_id
        self.created_at = datetime.now()
        self.last_activity = datetime.now()
        self.is_active = True
    
    def add_user_message(self, content: str) -> None:
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
        self.messages.append({
            "role": "system",
            "content": content.strip(),
            "timestamp": datetime.now().isoformat()
        })
        
    def get_history(self) -> List[Dict[str, str]]:
        return [
            {"role": msg["role"], "content": msg["content"]}
            for msg in self.messages
            if msg["role"] in ("user", "assistant")
        ]
    
    def get_full_history(self) -> List[Dict[str, str]]:
        return self.messages.copy()
    
    def get_conversation_transcript(self) -> str:
        if not self.messages:
            return ""
            
        transcript_lines = []
        for msg in self.messages:
            if msg["role"] == "system":
                continue
            role_name = "Patient" if msg["role"] == "user" else "Assistant"
            transcript_lines.append(f"{role_name}: {msg['content']}")
            
        return "\n".join(transcript_lines)
    
    def get_last_message(self, role: Optional[str] = None) -> Optional[Dict[str, str]]:
        if not self.messages:
            return None
            
        if role:
            for msg in reversed(self.messages):
                if msg["role"] == role:
                    return msg
            return None
            
        return self.messages[-1]
    
    def get_message_count(self) -> Dict[str, int]:
        user_count = sum(1 for m in self.messages if m["role"] == "user")
        assistant_count = sum(1 for m in self.messages if m["role"] == "assistant")
        
        return {
            "user": user_count,
            "assistant": assistant_count,
            "total": user_count + assistant_count
        }
    
    def get_session_duration(self) -> float:
        return (self.last_activity - self.created_at).total_seconds()
    
    def is_empty(self) -> bool:
        return len(self.messages) == 0
    
    def _enforce_max_length(self) -> None:
        if len(self.messages) > self.MAX_HISTORY_LENGTH:
            excess = len(self.messages) - self.MAX_HISTORY_LENGTH
            self.messages = self.messages[excess:]
    
    def end_session(self) -> None:
        self.is_active = False
        self.last_activity = datetime.now()
    
    def reset(self) -> None:
        self.messages = []
        self.created_at = datetime.now()
        self.last_activity = datetime.now()
        self.is_active = True
    
    def __len__(self) -> int:
        return len(self.messages)
    
    def __repr__(self) -> str:
        counts = self.get_message_count()
        return (
            f"ConversationManager("
            f"messages={counts['total']}, "
            f"session_id={self.session_id}, "
            f"active={self.is_active})"
        )
