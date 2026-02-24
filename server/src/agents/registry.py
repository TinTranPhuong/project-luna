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
    
    # AGENT 2: CREATIVE
    "creative": AgentConfig(
        name="Creative",
        slug="creative",
        model="gpt-oss",     
        temperature=3,
        top_k=40,              
        top_p=0.95,            
        min_p=0.05,           
        repeat_penalty=1.1,
        system_prompt=load_agent_prompt("creative.md"),
        description="Creative",
        icon="mask"
    ),
    
    # AGENT 3: IMAGE GEN 
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
    return AGENTS.get(slug, AGENTS["general"])