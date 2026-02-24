import os

# ==============================================================================
# PROMPT LOADER
# ==============================================================================

def load_agent_prompt(filename: str) -> str:
    """
    Resolves the absolute path to the designated agent markdown file 
    and loads its contents as the system prompt string.
    """
    current_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(current_dir, "agents", filename)
    
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        print(f"Error: Could not find prompt file: {filename}")
        return "System Error: Prompt file not found."