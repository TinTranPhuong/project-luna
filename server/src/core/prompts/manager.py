from typing import List, Dict
from datetime import datetime
from server.src.config.settings import MAX_HISTORY_MESSAGES

# ==============================================================================
# PROMPT MANAGEMENT
# ==============================================================================

class PromptManager:
    """
    Orchestrates the final assembly of the conversation payload before inference.
    Injects dynamic context (e.g., temporal awareness) and enforces context 
    window limits via sliding window truncation.
    """

    def build_messages(self, chat_history: List[Dict[str, str]]) -> List[Dict[str, str]]:
        """
        Parses the raw chat history, injects the current timestamp into the system 
        prompt, and truncates older messages to prevent VRAM overflow.
        """
        final_messages = []
        messages_to_process = list(chat_history)

        # --- 1. DYNAMIC CONTEXT INJECTION (TIME) ---
        current_time = datetime.now().strftime("%A, %B %d, %Y at %I:%M %p")
        time_block = f"Current Date: {current_time}"
        system_message = None
        
        if messages_to_process and messages_to_process[0].get("role") == "system":
            system_message = messages_to_process.pop(0)
            
            original_content = system_message["content"]
            system_message["content"] = f"{time_block}\n\n{original_content}"
            
        else:
            system_message = {"role": "system", "content": time_block}

        # --- 2. SLIDING WINDOW (TOKEN LIMIT ENFORCEMENT) ---
        if len(messages_to_process) > MAX_HISTORY_MESSAGES:
            recent_history = messages_to_process[-MAX_HISTORY_MESSAGES:]
        else:
            recent_history = messages_to_process

        # --- 3. PAYLOAD REASSEMBLY ---
        if system_message:
            final_messages.append(system_message)
        
        final_messages.extend(recent_history)
            
        return final_messages