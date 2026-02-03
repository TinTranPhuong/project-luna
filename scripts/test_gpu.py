import asyncio
import os
import sys

# Setup path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from server.core.llm.llama_cpp_adapter import LlamaCppAdapter

async def main():
    print("⚡ Initializing GPU Engine...")
    
    # Update with your actual filename
    adapter = LlamaCppAdapter("Qwen2.5-VL-7B-Instruct-Q4_K_M.gguf")
    
    try:
        await adapter.initialize()
        
        print("\n🧠 Sending Prompt...")
        messages = [{"role": "user", "content": "List 3 benefits of using CUDA for AI."}]
        
        response = await adapter.generate(messages, {"temperature": 0.7})
        print(f"\n🤖 Response:\n{response}")
        print("\n✅ If this was fast, your RTX 5060 Ti is working!")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())