from pydantic import BaseModel

class AgentConfig(BaseModel):
    name: str       
    slug: str        
    model: str        
    temperature: float 
    system_prompt: str  
    description: str   
    icon: str           