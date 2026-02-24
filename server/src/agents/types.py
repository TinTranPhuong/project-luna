from pydantic import BaseModel

class AgentConfig(BaseModel):
    """
    Configuration schema for Luna's AI agents.
    Defines the identity, underlying language model, and generation parameters for each persona.
    """
    name: str       
    slug: str        
    model: str        
    temperature: float 
    system_prompt: str  
    description: str   
    icon: str           
    
    # --- DEFAULT SAMPLERS ---
    top_k: int = 40
    top_p: float = 0.95
    min_p: float = 0.05
    repeat_penalty: float = 1.1