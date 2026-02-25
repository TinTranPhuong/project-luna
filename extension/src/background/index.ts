import { ContentMessageHandler } from './handlers/content-message-handler';
console.log("Luna Background Service Starting...");

new ContentMessageHandler();

chrome.sidePanel.setPanelBehavior({ openPanelOnActionClick: true })
  .catch((error) => console.error(error));