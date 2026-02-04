import { useState, KeyboardEvent } from 'react';
// Import your assets (Ensure these match your filenames exactly)
import iconScan from '../../../assets/icon_scan.png';
import iconSend from '../../../assets/icon_send.png';

interface Props {
  onSend: (text: string, context?: string) => void;
  disabled?: boolean;
}

export const InputBox = ({ onSend, disabled }: Props) => {
  const [text, setText] = useState('');
  const [attachedContext, setAttachedContext] = useState<string | null>(null);
  const [isReading, setIsReading] = useState(false);

  const handleSend = () => {
    if (text.trim() && !disabled) {
      onSend(text, attachedContext || undefined);
      setText('');
      setAttachedContext(null);
    }
  };

  const handleKeyDown = (e: KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleAttachContext = async () => {
    setIsReading(true);
    try {
      const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
      if (!tab.id) return;

      chrome.tabs.sendMessage(tab.id, { action: "GET_PAGE_CONTENT" }, (response) => {
        setIsReading(false);
        if (chrome.runtime.lastError) {
          alert("Refresh the page first!");
          return;
        }
        if (response && response.content) {
          setAttachedContext(response.content);
        }
      });
    } catch (e) {
      console.error(e);
      setIsReading(false);
    }
  };

  return (
    <div className="input-container">
      
      {/* Attachment Indicator (Remains text for clarity) */}
      {attachedContext && (
        <div className="attachment-badge">
          <span>Page Attached</span>
          <button onClick={() => setAttachedContext(null)}>✕</button>
        </div>
      )}

      <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
        
        {/* SCAN BUTTON (Icon) */}
        <button
          onClick={handleAttachContext}
          disabled={disabled || isReading}
          title="Scan this page"
          className="icon-btn"
          style={{ opacity: attachedContext ? 1 : 0.6 }} // Dim if not attached
        >
          <img 
            src={iconScan} 
            alt="Scan" 
            style={{ 
              width: '24px', 
              height: '24px',
              // Add a subtle spin animation if reading
              animation: isReading ? 'spin 1s linear infinite' : 'none'
            }} 
          />
        </button>

        {/* INPUT FIELD */}
        <input
          type="text"
          value={text}
          onChange={(e) => setText(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Ask Luna..."
          disabled={disabled}
          className="chat-input" 
        />
        
        {/* SEND BUTTON (Icon) */}
        <button
          onClick={handleSend}
          disabled={disabled || !text.trim()}
          className="icon-btn send-btn"
          title="Send"
        >
          <img src={iconSend} alt="Send" style={{ width: '24px', height: '24px' }} />
        </button>
      </div>
    </div>
  );
};