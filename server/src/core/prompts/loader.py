import os

def load_agent_prompt(filename: str) -> str:
    """
    Reads a markdown file from the 'agents' directory 
    and returns it as a string.
    """
    # Get the directory where this script (loader.py) lives
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Build path to the agents folder
    file_path = os.path.join(current_dir, "agents", filename)
    
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        print(f"Error: Could not find prompt file: {filename}")
        return "System Error: Prompt file not found."