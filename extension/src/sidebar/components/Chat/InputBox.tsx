import { useState, KeyboardEvent } from 'react';

interface Props {
  onSend: (text: string, context?: string) => void;
  disabled?: boolean;
}

export const InputBox = ({ onSend, disabled }: Props) => {
  const [text, setText] = useState('');
  const [attachedContext, setAttachedContext] = useState<string | null>(null);
  const [isReading, setIsReading] = useState(false);

  // ... (Handlers same as before) ...
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
          alert("Please refresh the web page.");
          return;
        }
        if (response && response.content) setAttachedContext(response.content);
      });
    } catch (e) {
      console.error(e);
      setIsReading(false);
    }
  };
  // ...

  return (
    <div className="input-container">
      
      {attachedContext && (
        <div style={{ 
          marginBottom: '8px', display: 'flex', alignItems: 'center', fontSize: '12px', 
          backgroundColor: '#E8F5E9', color: '#2E7D32', padding: '6px 10px', 
          borderRadius: '6px', border: '1px solid #C8E6C9' 
        }}>
          <span>Page Attached ({attachedContext.length} chars)</span>
          <button 
            onClick={() => setAttachedContext(null)}
            style={{ marginLeft: 'auto', background: 'none', border: 'none', cursor: 'pointer', color: '#1B5E20', fontWeight: 'bold' }}
          >
            Remove
          </button>
        </div>
      )}

      <div style={{ display: 'flex', gap: '8px' }}>
        <button
          onClick={handleAttachContext}
          disabled={disabled || isReading}
          title={attachedContext ? "Page is attached" : "Read current page"}
          style={{
            padding: '0 12px', borderRadius: '20px',
            backgroundColor: attachedContext ? '#34C759' : 'var(--bg-secondary)', // Use variable
            color: attachedContext ? 'white' : 'var(--text-main)', // Use variable
            border: '1px solid var(--border-color)', // Add border for dark mode visibility
            cursor: disabled ? 'not-allowed' : 'pointer',
            fontSize: '12px', fontWeight: 600, whiteSpace: 'nowrap'
          }}
        >
          {isReading ? 'Reading...' : (attachedContext ? 'Attached' : 'Read Page')}
        </button>

        <input
          type="text"
          value={text}
          onChange={(e) => setText(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Type a message..."
          disabled={disabled}
          className="chat-input" 
        />
        
        <button
          onClick={handleSend}
          disabled={disabled || !text.trim()}
          className="btn-primary" // Reuse class
          style={{ borderRadius: '20px', padding: '8px 16px', opacity: disabled ? 0.5 : 1 }}
        >
          Send
        </button>
      </div>
    </div>
  );
};