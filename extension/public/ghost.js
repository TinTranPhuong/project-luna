document.addEventListener("DOMContentLoaded", async () => {
    const params = new URLSearchParams(window.location.search);
    // 1. TRIM whitespace to prevent errors
    const query = (params.get("q") || "google.com").trim();
    
    const outputElement = document.getElementById("output");
    const progressLine = document.getElementById("progress");
    
    // SMART DETECTION
    const isUrl = (string) => {
        // If it starts with http/https or www, it IS a URL.
        if (string.startsWith("http://") || string.startsWith("https://") || string.startsWith("www.")) return true;
        // Fallback: Has a dot, no spaces (e.g. "openai.com")
        return string.includes(".") && !string.includes(" ");
    };

    let targetUrl = "";
    let displayMsg = "";

    // 2. DECIDE DESTINATION
    if (isUrl(query)) {
        // It's a website! Ensure it has https://
        if (!query.startsWith("http")) {
            targetUrl = `https://${query}`;
        } else {
            targetUrl = query;
        }
        displayMsg = `> Navigating to: "${targetUrl}"`;
    } else {
        // It's a search!
        targetUrl = `https://www.google.com/search?q=${encodeURIComponent(query)}`;
        displayMsg = `> Searching: "${query}"`;
    }

    // Messages to display
    const lines = [
        { text: "> Initializing search protocols...", delay: 20 },
        { text: "> Connecting to neural network...", delay: 10 },
        { text: displayMsg, delay: 30, color: "#ff8fab" }, // Show correct message
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

    // Run Animation
    let progress = 0;
    for (const line of lines) {
        progress += 25;
        if(progressLine) progressLine.style.width = `${progress}%`;
        
        await typeText(line.text, line.delay, line.color);
    }

    if(progressLine) progressLine.style.width = "100%";

    setTimeout(() => {
        window.location.href = targetUrl; 
    }, 400); 
});