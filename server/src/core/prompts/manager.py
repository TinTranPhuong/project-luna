from typing import List, Dict, Any
from .templates.system import CORE_SYSTEM_PROMPT
from datetime import datetime
from server.src.config.settings import MAX_HISTORY_MESSAGES

class PromptManager:
    """
    Constructs the conversation history with a Sliding Window.
    """
    
    def __init__(self):
        current_time = datetime.now().strftime("%A, %B %d, %Y at %I:%M %p")
        
        self.system_prompt = f"Current Date & Time: {current_time}\n\n{CORE_SYSTEM_PROMPT}"

    def build_messages(self, chat_history: List[Dict[str, str]]) -> List[Dict[str, str]]:
        """
        Takes raw chat history, trims it to the limit, and prepends the System Prompt.
        """
        final_messages = []
        
        # 1. ALWAYS Add the System Prompt first (The "Soul")
        final_messages.append({
            "role": "system", 
            "content": self.system_prompt
        })
        
        # 2. Apply the Sliding Window (The "Focus")
        # Take only the last N messages
        if len(chat_history) > MAX_HISTORY_MESSAGES:
            # Slice the list: get the last MAX_HISTORY_MESSAGES items
            recent_history = chat_history[-MAX_HISTORY_MESSAGES:]
            
            # (Optional) Debug print to see it working in console
            print(f"Trimming context: Keeping last {len(recent_history)}/{len(chat_history)} messages")
        else:
            recent_history = chat_history

        # 3. Add the user's conversation
        final_messages.extend(recent_history)
            
        return final_messages