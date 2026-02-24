from server.src.agents.types import AgentConfig
from server.src.core.prompts.loader import load_agent_prompt

# ==============================================================================
# AGENT REGISTRY
# Centralized configuration dictionary for all AI personas available in Luna.
# ==============================================================================

AGENTS = {
    
    # --- GENERAL ASSISTANT ---
    # Default fallback agent optimized for standard chat and vision tasks.
    "general": AgentConfig(
        name="General",
        slug="general",
        model="qwen",     
        temperature=0.6,
        system_prompt=load_agent_prompt("general.md"),
        description="Chat & Vision",
        icon="zap"
    ),
    
    # --- CREATIVE WRITER ---
    # High-temperature agent designed for roleplay and unrestricted generation.
    "creative": AgentConfig(
        name="Creative",
        slug="creative",
        model="gpt-oss",     
        temperature=3.0,
        top_k=40,              
        top_p=0.95,            
        min_p=0.05,           
        repeat_penalty=1.1,
        system_prompt=load_agent_prompt("creative.md"),
        description="Creative",
        icon="mask"
    ),
    
    # --- IMAGE GENERATOR ---
    # Specialized agent configured for drafting stable diffusion art prompts.
    "image_gen": AgentConfig(
        name="Image Gen",
        slug="image_gen",
        model="qwen",    
        temperature=0.9,         
        system_prompt=load_agent_prompt("image_gen.md"),
        description="Art Prompt",
        icon="image"
    )   
}

def get_agent(slug: str) -> AgentConfig:
    """
    Retrieves an agent configuration by its UI slug.
    Safely falls back to the 'general' agent if the requested slug is not found.
    """
    return AGENTS.get(slug, AGENTS["general"])