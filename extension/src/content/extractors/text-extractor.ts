export const extractPageContent = (): string => {
  // 1. Clone the body so we don't mess up the actual page
  const clone = document.body.cloneNode(true) as HTMLElement;

  // 2. Remove junk elements (Scripts, Styles, Ads, Navs)
  const junkSelectors = [
    'script', 'style', 'noscript', 'iframe', 
    'nav', 'footer', 'header', 
    '[role="complementary"]', '.ad', '.advertisement'
  ];

  junkSelectors.forEach(selector => {
    const elements = clone.querySelectorAll(selector);
    elements.forEach(el => el.remove());
  });

  // 3. Get clean text
  let text = clone.innerText || clone.textContent || "";
  
  // 4. Clean up whitespace (remove double spaces/newlines)
  text = text.replace(/\s+/g, ' ').trim();
  
  // 5. Limit context size (to avoid crashing the context window)
  return text.slice(0, 15000); // ~4000 tokens
};