from typing import List, Dict, Any
from .templates.system import CORE_SYSTEM_PROMPT

class PromptManager:
    """
    Constructs the conversation history ensuring the System Prompt 
    is always at the top.
    """
    
    def __init__(self):
        self.system_prompt = CORE_SYSTEM_PROMPT

    def build_messages(self, chat_history: List[Dict[str, str]]) -> List[Dict[str, str]]:
        """
        Takes the raw chat history and prepends the System Prompt.
        """
        messages = []
        
        # 1. Add the System Prompt first (The "Soul")
        messages.append({
            "role": "system", 
            "content": self.system_prompt
        })
        
        # 2. Append the rest of the user's conversation
        # (We will add context limits here in Phase 1.4)
        for msg in chat_history:
            messages.append(msg)
            
        return messages