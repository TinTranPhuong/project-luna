from llama_cpp import Llama

try:
    print("⏳ Attempting to load Text Model only...")
    llm = Llama(
        model_path="server/src/models/Qwen3VL-8B-Instruct-Q8_0.gguf",
        n_ctx=2048,
        verbose=True
    )
    print("✅ SUCCESS! The model file is healthy.")
except Exception as e:
    print(f"❌ FAILURE! The model file is bad or library is old.\nError: {e}")