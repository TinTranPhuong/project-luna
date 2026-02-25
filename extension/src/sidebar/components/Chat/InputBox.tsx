import { useState, KeyboardEvent, useRef } from 'react';
import iconUpload from '../../../assets/icon_upload.png'; 
import iconSend from '../../../assets/icon_send.png';
import iconStop from '../../../assets/icon_stop.png';
import iconScissors from '../../../assets/icon_scissors.png'; 
import { ModelSelector, AgentMode } from './ModelSelector';

interface Props {
  onSend: (text: string) => void;
  onStop: () => void;
  onSnip: () => void;
  onImageUpload: (base64Image: string) => void; 
  disabled?: boolean;
  currentMode: AgentMode;            
  onSelectMode: (mode: AgentMode) => void; 
}

export const InputBox = ({ onSend, onStop, onSnip, onImageUpload, onSelectMode, currentMode, disabled }: Props) => {
  const [text, setText] = useState('');
  const fileInputRef = useRef<HTMLInputElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  /* --- EVENT HANDLERS --- */
  const handleSend = () => {
    if (text.trim()) {
      onSend(text);
      setText('');
      if (textareaRef.current) {
        textareaRef.current.style.height = 'auto';
      }
    }
  };

  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleInput = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setText(e.target.value);
    e.target.style.height = 'auto'; 
    e.target.style.height = `${Math.min(e.target.scrollHeight, 120)}px`; 
  };

  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    
    if (file) {
      const reader = new FileReader();
      reader.onloadend = () => {
        onImageUpload(reader.result as string);
      };
      reader.readAsDataURL(file);
    }
    
    e.target.value = "";
  };

  return (
    <div className="input-container">
      
      {/* HIDDEN FILE INPUT */}
      <input 
        type="file" 
        ref={fileInputRef} 
        style={{ display: 'none' }} 
        accept="image/*"
        onChange={handleFileUpload}
      />

      <div style={{ display: 'flex', alignItems: 'flex-end', gap: '8px' }}>
        
        {/* TOOLBAR: LEFT */}
        <div style={{ display: 'flex', gap: '4px', paddingBottom: '8px' }}>
          <button
            onClick={() => fileInputRef.current?.click()}
            disabled={disabled}
            className="icon-btn"
            title="Upload Image"
          >
            <img src={iconUpload} alt="Upload" style={{ width: '20px', height: '20px', opacity: 0.8 }} />
          </button>

          <button
            onClick={onSnip}
            disabled={disabled}
            className="icon-btn"
            title="Snip Screen"
          >
            <img src={iconScissors} alt="Snip" style={{ width: '20px', height: '20px', opacity: 0.8 }} />
          </button>
        </div>

        {/* MULTI-LINE TEXTAREA */}
        <textarea
          ref={textareaRef}
          value={text}
          onChange={handleInput}
          onKeyDown={handleKeyDown}
          placeholder={disabled ? "Luna is thinking..." : "Ask Luna"}
          disabled={disabled}
          className="chat-input" 
          rows={1}
          style={{ 
            flex: 1, 
            resize: 'none', 
            overflowY: 'auto', 
            minHeight: '20px',
            fontFamily: 'inherit',
            lineHeight: '1.4',
            paddingTop: '12px'
          }} 
        />
        
        {/* RIGHT CONTROLS WRAPPER (To keep them aligned to the bottom) */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', paddingBottom: '4px' }}>
          {/* MODEL SELECTOR */}
          <ModelSelector currentMode={currentMode} onSelect={onSelectMode} />

          {/* TOOLBAR: RIGHT */}
          {disabled ? (
            <button
              onClick={onStop}
              className="icon-btn send-btn"
              title="Stop"
              style={{ backgroundColor: 'rgba(239, 68, 68, 0.1)' }}
            >
              <img src={iconStop} alt="Stop" style={{ width: '20px', height: '20px' }} />
            </button>
          ) : (
            <button
              onClick={handleSend}
              disabled={!text.trim()}
              className="icon-btn send-btn"
              title="Send"
            >
              <img src={iconSend} alt="Send" style={{ width: '20px', height: '20px' }} />
            </button>
          )}
        </div>
      </div>
    </div>
  );
};