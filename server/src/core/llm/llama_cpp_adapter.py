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

_LLAMA_EXECUTOR = concurrent.futures.ThreadPoolExecutor(
    max_workers=1,
    thread_name_prefix="llama_cuda_worker"
)

def _run_on_llama_thread(fn, *args, **kwargs):
    return _LLAMA_EXECUTOR.submit(fn, *args, **kwargs)

async def _run_on_llama_thread_async(fn, *args, **kwargs):
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(_LLAMA_EXECUTOR, lambda: fn(*args, **kwargs))

def _windows_force_vram_release_on_cuda_thread():
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

class LlamaCppAdapter:
    def __init__(self, model_path: str, n_ctx: int = MAX_CONTEXT_TOKENS):
        self.model_path = model_path
        self.n_ctx = n_ctx
        self.llm: Optional[Llama] = None

    async def initialize(self):
        if self.llm is not None:
            print("Adapter: Model already loaded, skipping.")
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
        chat_handler = None
        is_qwen = "Qwen" in os.path.basename(model_path)

        if is_qwen and os.path.exists(MMPROJ_PATH):
            try:
                chat_handler = Qwen3VLChatHandler(clip_model_path=MMPROJ_PATH)
                print("Adapter: Qwen VL chat handler loaded.")
            except Exception as e:
                print(f"Adapter: Chat handler failed ({e}), text-only mode.")
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
        if self.llm is None:
            return

        chat_handler = getattr(self.llm, "chat_handler", None)
        if chat_handler is not None:
            print("Adapter: Freeing vision encoder via ExitStack...")
            exit_stack = getattr(chat_handler, "_exit_stack", None)
            if exit_stack is not None:
                try:
                    exit_stack.close()  
                    print("Adapter: _exit_stack.close() OK — vision encoder freed.")
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
            print("Adapter: llm.close() complete.")
        except Exception as e:
            print(f"Adapter: llm.close() warning: {e}")

        del self.llm
        self.llm = None
        gc.collect()
        gc.collect()

        _windows_force_vram_release_on_cuda_thread()
        print("Adapter: _close_sync complete.")

    def close(self):
        print("Adapter: Starting VRAM purge...")
        if self.llm is not None:
            future = _run_on_llama_thread(self._close_sync)
            future.result(timeout=60)
        print("Adapter: VRAM purge complete.")

    def unload(self):
        self.close()

    async def generate(self, messages: List[Dict[str, Any]], settings: Dict[str, Any]) -> str:
        if not self.llm:
            await self.initialize()
            
        stop_tokens = ["<|im_end|>", "<|endoftext|>"]
        llm_ref = self.llm
        response = await _run_on_llama_thread_async(
            lambda: llm_ref.create_chat_completion(
                messages=messages,
                max_tokens=settings.get("max_tokens", MAX_CONTEXT_TOKENS),
                temperature=settings.get("temperature", 0.6),
                # 🟢 DYNAMIC SAMPLERS
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

        _run_on_llama_thread(_inference)

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