import { useState, KeyboardEvent } from 'react';

interface Props {
  onSend: (text: string, context?: string) => void; // Updated signature
  disabled?: boolean;
}

export const InputBox = ({ onSend, disabled }: Props) => {
  const [text, setText] = useState('');
  const [attachedContext, setAttachedContext] = useState<string | null>(null);
  const [isReading, setIsReading] = useState(false);

  const handleSend = () => {
    if (text.trim() && !disabled) {
      // Send text AND the attached context (if any)
      onSend(text, attachedContext || undefined);
      
      // Clear inputs
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
    <div style={{ padding: '16px', borderTop: '1px solid #E5E5EA', backgroundColor: '#FFFFFF' }}>
      
      {/* IDEA 1: The Attachment Badge */}
      {attachedContext && (
        <div style={{ 
          marginBottom: '8px', 
          display: 'flex', 
          alignItems: 'center', 
          fontSize: '12px', 
          backgroundColor: '#E8F5E9', 
          color: '#2E7D32',
          padding: '6px 10px',
          borderRadius: '6px',
          border: '1px solid #C8E6C9'
        }}>
          <span>📄 Current Page Attached ({attachedContext.length} chars)</span>
          <button 
            onClick={() => setAttachedContext(null)}
            style={{ 
              marginLeft: 'auto', 
              background: 'none', 
              border: 'none', 
              cursor: 'pointer', 
              color: '#1B5E20' 
            }}
          >
            ✕
          </button>
        </div>
      )}

      <div style={{ display: 'flex', gap: '8px' }}>
        <button
          onClick={handleAttachContext}
          disabled={disabled || isReading}
          title={attachedContext ? "Page already attached" : "Read current page"}
          style={{
            padding: '10px',
            borderRadius: '50%',
            backgroundColor: attachedContext ? '#34C759' : (isReading ? '#FFF' : '#F2F2F7'),
            border: isReading ? '2px solid #007AFF' : 'none',
            cursor: disabled ? 'not-allowed' : 'pointer',
            fontSize: '16px',
            transition: 'all 0.2s'
          }}
        >
          {isReading ? '⏳' : (attachedContext ? '✅' : '👁️')}
        </button>

        <input
          type="text"
          value={text}
          onChange={(e) => setText(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Ask about this page..."
          disabled={disabled}
          style={{ flex: 1, padding: '10px', borderRadius: '20px', border: '1px solid #C7C7CC', outline: 'none', fontSize: '14px' }}
        />
        
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