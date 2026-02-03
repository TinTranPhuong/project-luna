import { extractPageContent } from './extractors/text-extractor';

console.log("Luna Content Script Ready");

// Listen for messages from the Sidebar or Background
chrome.runtime.onMessage.addListener((request, _sender, sendResponse) => {
    if (request.action === "GET_PAGE_CONTENT") {
        console.log("Luna extracting content...");
        const content = extractPageContent();
        sendResponse({ content: content });
    }
    // Return true to indicate we will respond asynchronously (standard Chrome practice)
    return true;
});