import json
import random
import uuid
import urllib.request
import urllib.parse
import os
import asyncio
import websockets
from typing import Dict, Any

COMFY_SERVER = "127.0.0.1:8188"
CLIENT_ID = str(uuid.uuid4())

class ComfyAdapter:
    def __init__(self, workflow_path: str):
        self.server_address = COMFY_SERVER
        self.workflow_path = workflow_path
        self.workflow_data = self._load_workflow()

    def _load_workflow(self) -> Dict[str, Any]:
        if not os.path.exists(self.workflow_path):
            print(f"Error: Workflow file not found at {self.workflow_path}")
            return {}
        try:
            with open(self.workflow_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading workflow: {e}")
            return {}

    def queue_prompt(self, positive_prompt: str):
        if not self.workflow_data:
            return {"error": "Workflow not loaded"}

        workflow = self.workflow_data.copy()

        # Node 4 = Prompt
        if "4" in workflow:
            workflow["4"]["inputs"]["text"] = positive_prompt

        # Node 7 = Seed
        if "7" in workflow:
            workflow["7"]["inputs"]["seed"] = random.randint(1, 1000000000)

        # Send to API
        p = {"prompt": workflow, "client_id": CLIENT_ID}
        data = json.dumps(p).encode('utf-8')
        
        try:
            req = urllib.request.Request(f"http://{self.server_address}/prompt", data=data)
            return json.loads(urllib.request.urlopen(req).read())
        except Exception as e:
            return {"error": f"Failed to connect: {e}"}

    async def wait_for_completion(self, prompt_id: str):
        ws_url = f"ws://{self.server_address}/ws?clientId={CLIENT_ID}"
        print(f"Watching Paint Job {prompt_id}...")
        
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
        """Forces the OS to reclaim RAM immediately."""
        import ctypes
        # This tells Windows to trim the 'Working Set' of the process
        # It's the most aggressive way to force a RAM release.
        try:
            handle = ctypes.windll.kernel32.GetCurrentProcess()
            ctypes.windll.psapi.EmptyWorkingSet(handle)
            print("RAM Trim Complete.")
        except Exception as e:
            print(f"RAM Trim failed: {e}")