//import { createRoot } from 'react-dom/client';
import { useState, KeyboardEvent } from 'react';

interface Props {
  onSend: (text: string) => void;
  disabled?: boolean;
}

export const InputBox = ({ onSend, disabled }: Props) => {
  const [text, setText] = useState('');
  const [contextAdded, setContextAdded] = useState(false);

  const handleSend = () => {
    if (text.trim() && !disabled) {
      onSend(text);
      setText('');
    }
  };

  const handleKeyDown = (e: KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleAddContext = async () => {
    try {
      // 1. Get the active tab
      const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
      if (!tab.id) return;

      // 2. Ask the Content Script for text
      // We use chrome.tabs.sendMessage to talk to the page
      chrome.tabs.sendMessage(tab.id, { action: "GET_PAGE_CONTENT" }, (response) => {
        if (chrome.runtime.lastError) {
          console.error(chrome.runtime.lastError);
          alert("Could not read page. Try refreshing the page first.");
          return;
        }

        if (response && response.content) {
          // Prepend the context to the message buffer (hidden from user mainly, or visible)
          // For now, let's just show it in the input to prove it works
          const contextPrompt = `\n\n[Context from Website]:\n${response.content.slice(0, 500)}...\n\n`;
          setText(prev => contextPrompt + prev);
          setContextAdded(true);
        }
      });
    } catch (e) {
      console.error(e);
    }
  };

  return (
    <div style={{ padding: '16px', borderTop: '1px solid #E5E5EA', backgroundColor: '#FFFFFF' }}>
      <div style={{ display: 'flex', gap: '8px' }}>
        {/* NEW: Context Button */}
        <button
          onClick={handleAddContext}
          disabled={disabled}
          title="Read current page"
          style={{
            padding: '10px',
            borderRadius: '50%',
            backgroundColor: contextAdded ? '#34C759' : '#F2F2F7', // Green if added
            border: 'none',
            cursor: 'pointer',
            fontSize: '16px'
          }}
        >
          {contextAdded ? '👁️' : '📄'} 
        </button>

        <input
          // ... keep existing input props ...
          type="text"
          value={text}
          onChange={(e) => setText(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Ask Luna..."
          disabled={disabled}
          style={{ flex: 1, padding: '10px', borderRadius: '20px', border: '1px solid #C7C7CC', outline: 'none', fontSize: '14px' }}
        />
        {/* ... keep send button ... */}
        <button
          onClick={handleSend}
          disabled={disabled || !text.trim()}
          style={{
            padding: '8px 16px',
            borderRadius: '20px',
            backgroundColor: disabled ? '#A0A0A0' : '#007AFF',
            color: 'white',
            border: 'none',
            cursor: disabled ? 'not-allowed' : 'pointer',
            fontWeight: 600
          }}
        >
          Send
        </button>
      </div>
    </div>
  );
};