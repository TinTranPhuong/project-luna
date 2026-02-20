from server.src.agents.types import AgentConfig
from server.src.core.prompts.loader import load_agent_prompt

AGENTS = {
    # AGENT 1: GENERAL 
    "general": AgentConfig(
        name="General",
        slug="general",
        model="qwen",     
        temperature=0.6,
        system_prompt=load_agent_prompt("general.md"),
        description="Chat & Vision",
        icon="zap"
    ),
    
    # AGENT 2: IMAGE GEN 
    "image_gen": AgentConfig(
        name="Image Gen",
        slug="image_gen",
        model="qwen",    
        temperature=0.9,         
        system_prompt=load_agent_prompt("image_gen.md"),
        description="Art Prompt Architect",
        icon="image"
    )
}

def get_agent(slug: str) -> AgentConfig:
    """Returns the requested agent or defaults to General."""
    return AGENTS.get(slug, AGENTS["general"])