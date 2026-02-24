from llama_cpp import Llama
from llama_cpp.llama_chat_format import Qwen3VLChatHandler
from typing import List, Dict, Any, AsyncGenerator, Optional
import os
import asyncio
import gc
import queue
import ctypes
import concurrent.futures
from server.src.config.settings import MMPROJ_PATH, MAX_CONTEXT_TOKENS

# ==============================================================================
# GLOBAL THREADING & EXECUTOR
# ==============================================================================
# Critical: CUDA contexts are bound to the OS thread that initializes them. 
# We force all Llama.cpp operations (load, infer, close) onto a single, 
# dedicated background thread to prevent catastrophic VRAM leaks.
_LLAMA_EXECUTOR = concurrent.futures.ThreadPoolExecutor(
    max_workers=1,
    thread_name_prefix="llama_cuda_worker"
)

def _run_on_llama_thread(fn, *args, **kwargs):
    """Dispatches a synchronous function to the dedicated CUDA thread."""
    return _LLAMA_EXECUTOR.submit(fn, *args, **kwargs)

async def _run_on_llama_thread_async(fn, *args, **kwargs):
    """Awaits the completion of a function dispatched to the CUDA thread."""
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(_LLAMA_EXECUTOR, lambda: fn(*args, **kwargs))

# ==============================================================================
# VRAM MANAGEMENT UTILITIES
# ==============================================================================

def _windows_force_vram_release_on_cuda_thread():
    """
    Aggressively purges residual memory allocations. 
    Synchronizes the CUDA context and forces Windows to trim the process Working Set.
    """
    try:
        nvcuda = ctypes.WinDLL("nvcuda.dll")
        result = nvcuda.cuCtxSynchronize()
        print(f"VRAM Flush: cuCtxSynchronize() {'OK' if result == 0 else f'returned {result}'}")
    except Exception as e:
        print(f"VRAM Flush: nvcuda.dll unavailable ({e})")

    try:
        handle = ctypes.windll.kernel32.GetCurrentProcess()
        ctypes.windll.psapi.EmptyWorkingSet(handle)
        print("VRAM Flush: EmptyWorkingSet OK")
    except Exception as e:
        print(f"VRAM Flush: EmptyWorkingSet failed ({e})")

    gc.collect()
    gc.collect()

# ==============================================================================
# LLAMA.CPP ADAPTER
# ==============================================================================

class LlamaCppAdapter:
    """
    High-performance wrapper for Llama.cpp.
    Handles thread-safe model instantiation, vision-projector injection (Qwen), 
    and asynchronous generation streams.
    """
    
    def __init__(self, model_path: str, n_ctx: int = MAX_CONTEXT_TOKENS):
        self.model_path = model_path
        self.n_ctx = n_ctx
        self.llm: Optional[Llama] = None

    # --- LIFECYCLE & INITIALIZATION ---

    async def initialize(self):
        """Asynchronously loads the model weights into VRAM on the CUDA thread."""
        if self.llm is not None:
            #print("Adapter: Model already loaded, skipping.")
            return

        print(f"Adapter: Loading model -> {self.model_path}")
        if not os.path.exists(self.model_path):
            raise FileNotFoundError(f"Model file missing: {self.model_path}")

        self.llm = await _run_on_llama_thread_async(
            self._load_model_sync, self.model_path, self.n_ctx
        )
        print("Adapter: Model loaded successfully.")

    @staticmethod
    def _load_model_sync(model_path: str, n_ctx: int) -> Llama:
        """Synchronous factory method for instantiating the Llama core."""
        chat_handler = None
        is_qwen = "Qwen" in os.path.basename(model_path)

        # Vision Projector Injection
        if is_qwen and os.path.exists(MMPROJ_PATH):
            try:
                chat_handler = Qwen3VLChatHandler(clip_model_path=MMPROJ_PATH)
                #print("Adapter: Qwen VL chat handler loaded.")
            except Exception as e:
                #print(f"Adapter: Chat handler failed ({e}), text-only mode.")
                chat_handler = None

        return Llama(
            model_path=model_path,
            chat_handler=chat_handler,
            n_ctx=n_ctx,
            n_gpu_layers=-1,
            verbose=False,
            #type_k=8,
            #type_v=8,
            flash_attn=True,
        )

    def _close_sync(self):
        """
        Safely dismantles the model architecture. 
        Explicitly frees the vision encoder before destroying the main LLM object 
        to prevent dangling pointers in C++.
        """
        if self.llm is None:
            return

        chat_handler = getattr(self.llm, "chat_handler", None)
        if chat_handler is not None:
            #print("Adapter: Freeing vision encoder via ExitStack...")
            exit_stack = getattr(chat_handler, "_exit_stack", None)
            if exit_stack is not None:
                try:
                    exit_stack.close()  
                    #print("Adapter: _exit_stack.close() OK — vision encoder freed.")
                except Exception as e:
                    print(f"Adapter: _exit_stack.close() failed ({e})")
            else:
                print("Adapter: No _exit_stack found on handler.")

            try:
                self.llm.chat_handler = None
            except Exception:
                pass

        try:
            self.llm.close()
            #print("Adapter: llm.close() complete.")
        except Exception as e:
            print(f"Adapter: llm.close() warning: {e}")

        del self.llm
        self.llm = None
        
        gc.collect()
        gc.collect()

        _windows_force_vram_release_on_cuda_thread()
        print("Adapter: _close_sync complete.")

    def close(self):
        """Dispatches the VRAM purge sequence to the CUDA thread with a strict timeout."""
        #print("Adapter: Starting VRAM purge...")
        if self.llm is not None:
            future = _run_on_llama_thread(self._close_sync)
            future.result(timeout=60)
        #print("Adapter: VRAM purge complete.")

    def unload(self):
        """Alias for close()."""
        self.close()

    # --- INFERENCE EXECUTION ---

    async def generate(self, messages: List[Dict[str, Any]], settings: Dict[str, Any]) -> str:
        """Executes a standard, blocking generation task on the CUDA thread."""
        if not self.llm:
            await self.initialize()
            
        stop_tokens = ["<|im_end|>", "<|endoftext|>"]
        llm_ref = self.llm
        
        response = await _run_on_llama_thread_async(
            lambda: llm_ref.create_chat_completion(
                messages=messages,
                max_tokens=settings.get("max_tokens", MAX_CONTEXT_TOKENS),
                temperature=settings.get("temperature", 0.6),
                top_k=settings.get("top_k", 40),
                top_p=settings.get("top_p", 0.95),
                min_p=settings.get("min_p", 0.05),
                repeat_penalty=settings.get("repeat_penalty", 1.1),
                stop=stop_tokens,
                stream=False,
            )
        )
        return response["choices"][0]["message"]["content"]

    async def stream(self, messages: List[Dict[str, Any]], settings: Dict[str, Any]) -> AsyncGenerator[str, None]:
        """
        Executes a streaming generation task. 
        Uses a thread-safe Queue and sentinel pattern to bridge the gap between 
        the synchronous CUDA thread and the asynchronous FastAPI event loop.
        """
        if not self.llm:
            await self.initialize()

        stop_tokens = ["<|im_end|>", "<|endoftext|>"]
        token_queue: queue.Queue = queue.Queue()
        _DONE = object()

        llm_ref = self.llm
        max_tokens = settings.get("max_tokens", MAX_CONTEXT_TOKENS)
        temperature = settings.get("temperature", 0.6)

        def _inference():
            try:
                gen = llm_ref.create_chat_completion(
                    messages=messages,
                    max_tokens=max_tokens,
                    temperature=temperature,
                    top_k=settings.get("top_k", 40),
                    top_p=settings.get("top_p", 0.95),
                    min_p=settings.get("min_p", 0.05),
                    repeat_penalty=settings.get("repeat_penalty", 1.1),
                    stop=stop_tokens,
                    stream=True,
                )
                for chunk in gen:
                    if isinstance(chunk, dict):
                        choices = chunk.get("choices", [])
                        if choices:
                            content = choices[0].get("delta", {}).get("content", "")
                            if content:
                                token_queue.put(content)
                del gen
                gc.collect()
            except Exception as e:
                token_queue.put(RuntimeError(f"Inference error: {e}"))
            finally:
                token_queue.put(_DONE)

        # Dispatch inference to background
        _run_on_llama_thread(_inference)

        # Poll the queue asynchronously to avoid blocking the event loop
        while True:
            try:
                item = token_queue.get_nowait()
            except queue.Empty:
                await asyncio.sleep(0.005)
                continue
            
            if item is _DONE:
                break
            if isinstance(item, Exception):
                raise item
                
            yield item