document.addEventListener("DOMContentLoaded", async () => {
    const params = new URLSearchParams(window.location.search);
    const trackId = params.get("track");
    
    const outputElement = document.getElementById("output");
    const cursor = document.getElementById("cursor");
    const progressUi = document.getElementById("progress-ui");
    const progressFill = document.getElementById("progress-fill");
    const progressStatus = document.getElementById("progress-status");
    const progressPercent = document.getElementById("progress-percent");
    const imageElement = document.getElementById("generated-image");
    const downloadBtn = document.getElementById("download-btn");

    // --- Helper: Hacker Typing Animation ---
    const typeLine = async (text, color = null) => {
        const div = document.createElement("div");
        if (color) div.style.color = color;
        // Adds a live timestamp for that cyberpunk terminal feel
        const time = new Date().toLocaleTimeString('en-US', {hour12:false, hour:'2-digit', minute:'2-digit', second:'2-digit'});
        div.innerHTML = `[${time}] ${text}`;
        outputElement.appendChild(div);
        outputElement.scrollTop = outputElement.scrollHeight; // Auto-scrolls to bottom
    };

    if (!trackId) {
        typeLine("> ERROR: Missing tracking ID.", "#ef4444");
        return;
    }

    // --- 1. Start Tracking ---
    typeLine(`> LINK ESTABLISHED. Tracking Job ID: ${trackId.substring(0, 8)}...`);
    typeLine("> Connecting to neural engine websocket...");
    progressUi.style.display = "block";

    const COMFY_URL = "127.0.0.1:8188";
    
    // Connect as a global observer (no clientId)
    let socket = new WebSocket(`ws://${COMFY_URL}/ws`); 
    let currentNode = ""; 
    let isFinished = false;

    // --- 2. WebSocket Stream (Catches whatever ComfyUI allows us to see) ---
    socket.addEventListener('open', () => {
        typeLine("> Websocket connected. Awaiting data stream.", "#ff8fab");
    });

    socket.addEventListener('message', (event) => {
        if (isFinished) return;
        const msg = JSON.parse(event.data);
        
        // Broadcasted Execution updates
        if (msg.type === 'executing' && msg.data.prompt_id === trackId && msg.data.node !== null) {
            currentNode = `Node ${msg.data.node}`;
            progressStatus.innerText = `EXECUTING: ${currentNode}`;
            typeLine(`> Processing block: ${currentNode}`);
        }

        // Progress updates (If the adapter allows them to broadcast)
        if (msg.type === 'progress' && msg.data.prompt_id === trackId) {
            const { value, max } = msg.data;
            const percent = Math.round((value / max) * 100);
            progressFill.style.width = `${percent}%`;
            progressPercent.innerText = `${percent}%`;
            progressStatus.innerText = `SAMPLING: Step ${value}/${max}`;
        }
    });

    // --- 3. THE BULLETPROOF SAFETY NET (API Polling) ---
    // Because ComfyUI hides the 'executed' event from us, we poll the history endpoint.
    // The millisecond the image finishes, it appears here, guaranteeing we catch it!
    const checkHistory = setInterval(async () => {
        if (isFinished) return;
        
        try {
            const res = await fetch(`http://${COMFY_URL}/history/${trackId}`);
            const historyData = await res.json();

            // If our Job ID exists in the history, the image is officially done!
            if (historyData[trackId]) {
                isFinished = true;
                clearInterval(checkHistory); // Stop polling
                if (socket.readyState === WebSocket.OPEN) socket.close(); // Close connection

                progressFill.style.width = "100%";
                progressPercent.innerText = "100%";
                progressStatus.innerText = "DECODING FINAL TENSORS...";
                typeLine("> Generation successful. Loading image...", "#ff8fab");

                // Safely dig through the JSON to find the exact image filename
                let filename = null;
                const outputs = historyData[trackId].outputs;
                for (const key in outputs) {
                    const nodeOutput = outputs[key];
                    if (nodeOutput.images && nodeOutput.images.length > 0) {
                        filename = nodeOutput.images[0].filename;
                        break;
                    }
                }

                if (filename) {
                    const imgUrl = `http://${COMFY_URL}/view?filename=${filename}&type=output`;
                    
                    // Trigger the final UI reveal
                    setTimeout(() => {
                        progressUi.style.display = 'none';
                        cursor.style.display = 'none';
                        imageElement.src = imgUrl;
                        imageElement.style.display = "block";
                        downloadBtn.style.display = "block";
                        typeLine("> Image rendered successfully.", "#ff8fab");
                    }, 800);

                    // Setup Clean Download logic
                    downloadBtn.onclick = async () => {
                        downloadBtn.innerText = "DOWNLOADING...";
                        try {
                            const imgRes = await fetch(imgUrl);
                            const blob = await imgRes.blob();
                            const url = window.URL.createObjectURL(blob);
                            const a = document.createElement("a");
                            a.href = url; a.download = filename; a.click();
                            window.URL.revokeObjectURL(url);
                            downloadBtn.innerText = "DOWNLOAD COMPLETE";
                        } catch (e) { downloadBtn.innerText = "ERROR"; }
                    };
                } else {
                     typeLine("> ERROR: Could not locate output filename in history.", "#ef4444");
                }
            }
        } catch (err) {
            // Ignore fetch errors (ComfyUI might block requests while heavily processing)
        }
    }, 2000); // Poll every 2 seconds
});