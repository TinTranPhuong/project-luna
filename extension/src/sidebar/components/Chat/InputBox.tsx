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
  
  // Ref for the hidden file input
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleSend = () => {
    if (text.trim()) {
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

  // Handle File Selection
  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      const reader = new FileReader();
      reader.onloadend = () => {
        // Send the image data up to ChatInterface
        onImageUpload(reader.result as string);
      };
      reader.readAsDataURL(file);
    }
    // Reset value so you can upload the same file again if you deleted it
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

      <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
        
        {/* LEFT TOOLS GROUP */}
        <div style={{ display: 'flex', gap: '4px' }}>
          
          {/* UPLOAD BUTTON  */}
          <button
            onClick={() => fileInputRef.current?.click()} // Triggers the hidden input
            disabled={disabled}
            className="icon-btn"
            title="Upload Image"
          >
            <img src={iconUpload} alt="Upload" style={{ width: '20px', height: '20px', opacity: 0.8 }} />
          </button>

          {/* SNIP BUTTON  */}
          <button
            onClick={onSnip}
            disabled={disabled}
            className="icon-btn"
            title="Snip Screen"
          >
            <img src={iconScissors} alt="Snip" style={{ width: '20px', height: '20px', opacity: 0.8 }} />
          </button>
        </div>

        {/* INPUT FIELD */}
        <input
          type="text"
          value={text}
          onChange={(e) => setText(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder={disabled ? "Luna is thinking..." : "Ask Luna..."}
          disabled={disabled}
          className="chat-input" 
          style={{ flex: 1 }} 
        />
        
        {/* MODEL SELECTOR */}
        <ModelSelector currentMode={currentMode} onSelect={onSelectMode} />

        {/* RIGHT ACTION BUTTON */}
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
  );
};