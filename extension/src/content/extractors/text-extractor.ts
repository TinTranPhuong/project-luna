import { Readability } from '@mozilla/readability';
import DOMPurify from 'dompurify';
import TurndownService from 'turndown';

// Helper: Auto-scroll to bottom to trigger lazy loading
export const autoScroll = async (): Promise<void> => {
    return new Promise((resolve) => {
        let totalHeight = 0;
        const distance = 100;
        const timer = setInterval(() => {
            const scrollHeight = document.body.scrollHeight;
            window.scrollBy(0, distance);
            totalHeight += distance;

            // Stop scrolling if we reached the bottom or it's taking too long (3s max)
            if (totalHeight >= scrollHeight || totalHeight > 15000) {
                clearInterval(timer);
                window.scrollTo(0, 0); 
                resolve();
            }
        }, 20); 
    });
};

export const extractPageContent = async (): Promise<string> => {
    // 1. Clone document to avoid modifying the visible page
    const clone = document.cloneNode(true) as Document;
    
    // 2. Use Readability to find the "Main Content"
    const reader = new Readability(clone);
    const article = reader.parse();

    if (!article) {
        // Fallback: If Readability fails, just grab body text
        return document.body.innerText.slice(0, 5000);
    }

    // 3. Clean the HTML 
    const cleanHtml = DOMPurify.sanitize(article.content || "");

    // 4. Convert to Markdown 
    const turndownService = new TurndownService({
        headingStyle: 'atx',
        codeBlockStyle: 'fenced'
    });
    
    // Remove images/links to save even more space 
    turndownService.remove(['img', 'script', 'style', 'iframe']);

    const markdown = turndownService.turndown(cleanHtml);

    // 5. Add Metadata
    const finalContent = `Title: ${article.title}\nURL: ${window.location.href}\n\n${markdown}`;
    return finalContent.slice(0, 30000);
};