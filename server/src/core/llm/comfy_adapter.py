import json
import random
import uuid
import urllib.request
import urllib.parse
import os
import asyncio
import websockets
from typing import Dict, Any
from server.src.config.settings import COMFY_SERVER

# ==============================================================================
# CONFIGURATION
# ==============================================================================
CLIENT_ID = str(uuid.uuid4())

# ==============================================================================
# COMFYUI INTEGRATION ADAPTER
# ==============================================================================

class ComfyAdapter:
    """
    Adapter for interfacing with a local ComfyUI Stable Diffusion instance.
    Handles payload formatting, HTTP queuing, and WebSocket telemetry tracking.
    """
    
    def __init__(self, workflow_path: str):
        self.server_address = COMFY_SERVER
        self.workflow_path = workflow_path
        self.workflow_data = self._load_workflow()

    def _load_workflow(self) -> Dict[str, Any]:
        """Loads and parses the target ComfyUI JSON workflow into memory."""
        if not os.path.exists(self.workflow_path):
            print(f"Error: Workflow file not found at {self.workflow_path}")
            return {}
        try:
            with open(self.workflow_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading workflow: {e}")
            return {}

    # --- INFERENCE EXECUTION ---
    
    def queue_prompt(self, positive_prompt: str):
        """
        Injects the generated prompt and a randomized seed into the workflow payload, 
        then dispatches it to the ComfyUI API queue.
        """
        if not self.workflow_data:
            return {"error": "Workflow not loaded"}

        workflow = self.workflow_data.copy()

        if "4" in workflow:
            workflow["4"]["inputs"]["text"] = positive_prompt

        if "7" in workflow:
            workflow["7"]["inputs"]["seed"] = random.randint(1, 1000000000)

        p = {"prompt": workflow, "client_id": CLIENT_ID}
        data = json.dumps(p).encode('utf-8')
        
        try:
            req = urllib.request.Request(f"http://{self.server_address}/prompt", data=data)
            return json.loads(urllib.request.urlopen(req).read())
        except Exception as e:
            return {"error": f"Failed to connect: {e}"}

    # --- TELEMETRY & LIFECYCLE ---

    async def wait_for_completion(self, prompt_id: str):
        """
        Establishes a WebSocket connection to monitor the execution pipeline.
        Yields control back to the event loop until the specific prompt_id finishes processing.
        """
        ws_url = f"ws://{self.server_address}/ws?clientId={CLIENT_ID}"
        print(f"Watching execution stream for Job: {prompt_id}...")
        
        try:
            async with websockets.connect(ws_url) as ws:
                while True:
                    out = await ws.recv()
                    if isinstance(out, str):
                        message = json.loads(out)
                        if message['type'] == 'executing' and message['data']['node'] is None and message['data']['prompt_id'] == prompt_id:
                            print("ComfyUI Finished Generation!")
                            break
        except Exception as e:
            print(f"WebSocket Error: {e}")

    def free_memory(self):
        """
        Aggressively forces the host Operating System to reclaim allocated RAM 
        by trimming the process Working Set. Crucial for low-VRAM environments.
        """
        import ctypes
        try:
            handle = ctypes.windll.kernel32.GetCurrentProcess()
            ctypes.windll.psapi.EmptyWorkingSet(handle)
            print("RAM Trim Complete.")
        except Exception as e:
            print(f"RAM Trim failed: {e}")