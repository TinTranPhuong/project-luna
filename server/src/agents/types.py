from pydantic import BaseModel

class AgentConfig(BaseModel):
    name: str       
    slug: str        
    model: str        
    temperature: float 
    system_prompt: str  
    description: str   
    icon: str           
    top_k: int = 40
    top_p: float = 0.95
    min_p: float = 0.05
    repeat_penalty: float = 1.1