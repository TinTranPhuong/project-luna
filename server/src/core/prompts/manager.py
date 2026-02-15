from typing import List, Dict, Any
from datetime import datetime
from server.src.config.settings import MAX_HISTORY_MESSAGES

class PromptManager:
    """
    Manages conversation history and injects dynamic context (like Time).
    """
    
    def __init__(self):
        pass

    def build_messages(self, chat_history: List[Dict[str, str]]) -> List[Dict[str, str]]:
        final_messages = []
        messages_to_process = list(chat_history)

        current_time = datetime.now().strftime("%A, %B %d, %Y at %I:%M %p")
        time_block = f"Current Date: {current_time}"
        system_message = None
        
        if messages_to_process and messages_to_process[0].get("role") == "system":
            system_message = messages_to_process.pop(0)
            
            # INJECT THE TIME into the existing prompt
            original_content = system_message["content"]
            system_message["content"] = f"{time_block}\n\n{original_content}"
            
        else:
            # If for some reason there is no system prompt, create one with just the time
            system_message = {"role": "system", "content": time_block}

        # 3. Apply Sliding Window (Trim old messages)
        if len(messages_to_process) > MAX_HISTORY_MESSAGES:
            recent_history = messages_to_process[-MAX_HISTORY_MESSAGES:]
        else:
            recent_history = messages_to_process

        # 4. Rebuild the list
        if system_message:
            final_messages.append(system_message)
        
        final_messages.extend(recent_history)
            
        return final_messages