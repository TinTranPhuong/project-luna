export class ContentMessageHandler {
  
  constructor() {
    chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
      this.handleMessage(request, sender, sendResponse);
      return true; // Keep channel open for async response
    });
  }

  private handleMessage(request: any, _sender: chrome.runtime.MessageSender, sendResponse: (response?: any) => any) {
    
    // 1. Sidebar asks to START (Forward to Content Script)
    if (request.action === "START_SNIP") {
      chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
        if (tabs[0]?.id) {
          chrome.tabs.sendMessage(tabs[0].id, { action: "ACTIVATE_SNIP" });
          sendResponse({ status: "Snip Started" }); 
          } else {
          sendResponse({ status: "No Active Tab" }); 
          }
      });
    }

    // 1.5. Sidebar asks to OPEN GHOST TAB (New Logic)
    if (request.action === "OPEN_GHOST_TAB") {
      const query = request.query;
      chrome.tabs.create({
        url: chrome.runtime.getURL(`ghost.html?q=${encodeURIComponent(query)}`)
      });
      sendResponse({ status: "Ghost Tab Opened" });
    }

    // 2. Content Script says DONE (Capture & Return)
    if (request.action === "SNIP_COMPLETED") {
      const { cropData } = request;
      
      chrome.tabs.captureVisibleTab(chrome.windows.WINDOW_ID_CURRENT, { format: "png" }, (dataUrl) => {
        // Send back to Sidebar (Runtime Message)
        chrome.runtime.sendMessage({ 
          action: "PROCESS_CROP", 
          imageUrl: dataUrl, 
          cropData: cropData 
        });
      });
    }

    // 3. Fallback for unknown messages 
    else {
      sendResponse({ status: "Unknown Action" });
    }
  }
}