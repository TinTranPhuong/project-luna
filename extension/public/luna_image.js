document.addEventListener("DOMContentLoaded", async () => {
    // --- INITIALIZATION & DOM SELECTION ---
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

    // --- UTILITIES ---
    const typeLine = async (text, color = null) => {
        const div = document.createElement("div");
        if (color) div.style.color = color;
        
        const time = new Date().toLocaleTimeString('en-US', {
            hour12: false, 
            hour: '2-digit', 
            minute: '2-digit', 
            second: '2-digit'
        });
        
        div.innerHTML = `[${time}] ${text}`;
        outputElement.appendChild(div);
        outputElement.scrollTop = outputElement.scrollHeight; 
    };

    if (!trackId) {
        typeLine("> ERROR: Missing tracking ID.", "#ef4444");
        return;
    }

    // --- CONNECTION SETUP ---
    typeLine(`> LINK ESTABLISHED. Tracking Job ID: ${trackId.substring(0, 8)}...`);
    typeLine("> Connecting to neural engine websocket...");
    typeLine("> Websocket connected. Awaiting image generation...");
    progressUi.style.display = "block";

    const COMFY_URL = "127.0.0.1:8188";
    let socket = new WebSocket(`ws://${COMFY_URL}/ws`); 
    let currentNode = ""; 
    let isFinished = false;

    // --- WEBSOCKET EVENT LISTENERS ---
    socket.addEventListener('open', () => {
        typeLine("> Websocket connected. Awaiting data stream.", "#ff8fab");
    });

    socket.addEventListener('message', (event) => {
        if (isFinished) return;
        const msg = JSON.parse(event.data);
        
        if (msg.type === 'executing' && msg.data.prompt_id === trackId && msg.data.node !== null) {
            currentNode = `Node ${msg.data.node}`;
            progressStatus.innerText = `EXECUTING: ${currentNode}`;
            typeLine(`> Processing block: ${currentNode}`);
        }

        if (msg.type === 'progress' && msg.data.prompt_id === trackId) {
            const { value, max } = msg.data;
            const percent = Math.round((value / max) * 100);
            progressFill.style.width = `${percent}%`;
            progressPercent.innerText = `${percent}%`;
            progressStatus.innerText = `SAMPLING: Step ${value}/${max}`;
        }
    });

    // --- HISTORY POLLING FALLBACK ---
    const checkHistory = setInterval(async () => {
        if (isFinished) return;
        
        try {
            const res = await fetch(`http://${COMFY_URL}/history/${trackId}`);
            const historyData = await res.json();

            if (historyData[trackId]) {
                isFinished = true;
                clearInterval(checkHistory); 
                if (socket.readyState === WebSocket.OPEN) socket.close(); 

                progressFill.style.width = "100%";
                progressPercent.innerText = "100%";
                progressStatus.innerText = "DECODING FINAL TENSORS...";
                typeLine("> Generation successful. Loading image...", "#ff8fab");

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
                    
                    setTimeout(() => {
                        progressUi.style.display = 'none';
                        cursor.style.display = 'none';
                        imageElement.src = imgUrl;
                        imageElement.style.display = "block";
                        downloadBtn.style.display = "block";
                        typeLine("> Image rendered successfully.", "#ff8fab");
                    }, 800);

                    // --- DOWNLOAD HANDLER ---
                    downloadBtn.onclick = async () => {
                        downloadBtn.innerText = "DOWNLOADING...";
                        try {
                            const imgRes = await fetch(imgUrl);
                            const blob = await imgRes.blob();
                            const url = window.URL.createObjectURL(blob);
                            const a = document.createElement("a");
                            
                            a.href = url; 
                            a.download = filename; 
                            a.click();
                            
                            window.URL.revokeObjectURL(url);
                            downloadBtn.innerText = "DOWNLOAD COMPLETE";
                        } catch (e) { 
                            downloadBtn.innerText = "ERROR"; 
                        }
                    };
                } else {
                     typeLine("> ERROR: Could not locate output filename in history.", "#ef4444");
                }
            }
        } catch (err) {
            // Silently ignore fetch errors during heavy ComfyUI processing
        }
    }, 2000); 
});