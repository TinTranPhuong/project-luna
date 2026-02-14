import { extractPageContent, autoScroll } from './extractors/text-extractor';
import { SnipperHandler } from './handlers/snipper-handler';

console.log("Luna Content Script Ready");

new SnipperHandler();

chrome.runtime.onMessage.addListener((request, _sender, sendResponse) => {
    if (request.action === "GET_PAGE_CONTENT") {
        console.log("Luna processing page...");
        
        // 1. Scroll first (Idea 3)
        autoScroll().then(() => {
            // 2. Extract (Idea 2)
            return extractPageContent();
        }).then((content) => {
            sendResponse({ content: content });
        });

        // Return true to keep the channel open for async response
        return true;
    }
    return true;
});
