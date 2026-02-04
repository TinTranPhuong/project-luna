import { useState, KeyboardEvent } from 'react';
import iconScan from '../../../assets/icon_scan.png';
import iconSend from '../../../assets/icon_send.png';
import iconStop from '../../../assets/icon_stop.png'; // <--- Import your new icon

interface Props {
  onSend: (text: string, context?: string) => void;
  onStop: () => void;      // <--- New Prop
  disabled?: boolean;      // This now means "Is Loading"
}

export const InputBox = ({ onSend, onStop, disabled }: Props) => {
  const [text, setText] = useState('');
  const [attachedContext, setAttachedContext] = useState<string | null>(null);
  const [isReading, setIsReading] = useState(false);

  const handleSend = () => {
    if (text.trim()) {
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
      
      {attachedContext && (
        <div className="attachment-badge">
          <span>Page Attached</span>
          <button onClick={() => setAttachedContext(null)}>✕</button>
        </div>
      )}

      <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
        
        {/* SCAN BUTTON */}
        <button
          onClick={handleAttachContext}
          disabled={disabled || isReading}
          className="icon-btn"
          title="Scan Page"
        >
          <img src={iconScan} alt="Scan" style={{ width: '24px', height: '24px' }} />
        </button>

        {/* INPUT */}
        <input
          type="text"
          value={text}
          onChange={(e) => setText(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder={disabled ? "Luna is typing..." : "Ask Luna..."}
          disabled={disabled} // Disable typing while generating? Optional.
          className="chat-input" 
        />
        
        {/* SEND / STOP TOGGLE */}
        {disabled ? (
          //  STOP BUTTON
          <button
            onClick={onStop}
            className="icon-btn send-btn"
            title="Stop Generation"
            style={{ backgroundColor: 'rgba(239, 68, 68, 0.1)' }} // Light Red background
          >
            <img src={iconStop} alt="Stop" style={{ width: '24px', height: '24px' }} />
          </button>
        ) : (
          // SEND BUTTON
          <button
            onClick={handleSend}
            disabled={!text.trim()}
            className="icon-btn send-btn"
            title="Send"
          >
            <img src={iconSend} alt="Send" style={{ width: '24px', height: '24px' }} />
          </button>
        )}
      </div>
    </div>
  );
};

