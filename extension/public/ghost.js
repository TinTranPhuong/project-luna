document.addEventListener("DOMContentLoaded", async () => {
    // --- INITIALIZATION & SANITIZATION ---
    const params = new URLSearchParams(window.location.search);
    const query = (params.get("q") || "google.com").trim();
    
    const outputElement = document.getElementById("output");
    const progressLine = document.getElementById("progress");
    
    // --- QUERY ROUTING LOGIC ---
    const isUrl = (string) => {
        if (string.startsWith("http://") || string.startsWith("https://") || string.startsWith("www.")) {
            return true;
        }
        return string.includes(".") && !string.includes(" ");
    };

    let targetUrl = "";
    let displayMsg = "";

    if (isUrl(query)) {
        if (!query.startsWith("http")) {
            targetUrl = `https://${query}`;
        } else {
            targetUrl = query;
        }
        displayMsg = `> Navigating to: "${targetUrl}"`;
    } else {
        targetUrl = `https://www.google.com/search?q=${encodeURIComponent(query)}`;
        displayMsg = `> Searching: "${query}"`;
    }

    // --- ANIMATION CONFIGURATION ---
    const lines = [
        { text: "> Initializing search protocols...", delay: 20 },
        { text: "> Connecting to neural network...", delay: 10 },
        { text: displayMsg, delay: 30, color: "#ff8fab" },
        { text: "> Launching...", delay: 50 }
    ];

    const typeText = async (text, speed, color = null) => {
        const div = document.createElement("div");
        if (color) div.style.color = color;
        outputElement.appendChild(div);
        
        for (let i = 0; i < text.length; i++) {
            div.innerHTML += text[i];
            await new Promise(r => setTimeout(r, speed));
        }
        await new Promise(r => setTimeout(r, 100));
    };

    // --- EXECUTION SEQUENCE ---
    let progress = 0;
    
    for (const line of lines) {
        progress += 25;
        if (progressLine) progressLine.style.width = `${progress}%`;
        
        await typeText(line.text, line.delay, line.color);
    }

    if (progressLine) progressLine.style.width = "100%";

    setTimeout(() => {
        window.location.href = targetUrl; 
    }, 400); 
});