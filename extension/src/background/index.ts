import { ContentMessageHandler } from './handlers/content-message-handler';
// Import your other handlers here if you have them (e.g. PopupMessageHandler)

console.log("Luna Background Service Starting...");

// 1. Initialize the Message Handler
// This starts listening for "START_SNIP" from the Sidebar
new ContentMessageHandler();

// 2. (Optional) Keep your other existing init code below
// ...