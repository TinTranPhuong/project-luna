import { useEffect, useState } from 'react';
import { MessageList } from './MessageList';
import { InputBox } from './InputBox';
import { useChat } from '../../hooks/useChat'; 
import { AgentMode } from './ModelSelector';

interface Props {
  sessionId: number | null;
  onSessionCreated: (id: number) => void;
  currentMode: AgentMode;
  onSelectMode: (mode: AgentMode) => void; 
}

export const ChatInterface = ({ sessionId, currentMode, onSelectMode }: Props) => {
  const useRag = true; 
  const [capturedImage, setCapturedImage] = useState<string | null>(null);
  
  const { messages, loading, sendMessage, loadSession, clearChat, stopGeneration, executeGen } = useChat(sessionId);

  useEffect(() => {
    if (sessionId) loadSession(sessionId);
    else clearChat();
  }, [sessionId, loadSession, clearChat]);

  // Snipping Tool Logic
  useEffect(() => {
    const handleMessage = (request: any) => {
      if (request.action === "PROCESS_CROP") {
        cropImage(request.imageUrl, request.cropData);
      }
    };
    chrome.runtime.onMessage.addListener(handleMessage);
    return () => chrome.runtime.onMessage.removeListener(handleMessage);
  }, []);

  const cropImage = (fullImageUrl: string, crop: any) => {
    const canvas = document.createElement('canvas');
    const ctx = canvas.getContext('2d');
    const img = new Image();
    img.onload = () => {
      const scale = crop.devicePixelRatio || 1; 
      canvas.width = crop.width * scale;
      canvas.height = crop.height * scale;
      ctx?.drawImage(img, crop.x * scale, crop.y * scale, crop.width * scale, crop.height * scale, 0, 0, canvas.width, canvas.height);
      setCapturedImage(canvas.toDataURL('image/jpeg', 0.8));
    };
    img.src = fullImageUrl;
  };

  const handleSnipClick = () => {
    chrome.runtime.sendMessage({ action: "START_SNIP" });
  };

  const handleSendWrapper = async (text: string, context?: string) => {
    await sendMessage(
      text, 
      useRag, 
      capturedImage || undefined, 
      context, 
      currentMode 
    );
    setCapturedImage(null);
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
      <div style={{ flex: 1, overflowY: 'auto', paddingTop: '60px' }}> 
        {/* FIXED: Passed the executeGen prop down */}
        <MessageList messages={messages} loading={loading} onExecuteGen={executeGen} />
      </div>

      {capturedImage && (
        <div style={{ padding: '0 20px', marginBottom: '10px' }}>
          <div style={{ position: 'relative', display: 'inline-block' }}>
            <img src={capturedImage} alt="Preview" style={{ height: '80px', borderRadius: '8px', border: '1px solid #ff8fab', boxShadow: '0 4px 10px rgba(0,0,0,0.2)' }} />
            <button onClick={() => setCapturedImage(null)} style={{ position: 'absolute', top: -8, right: -8, background: '#ef4444', color: 'white', borderRadius: '50%', width: '22px', height: '22px', border: '2px solid white', cursor: 'pointer' }}>✕</button>
          </div>
        </div>
      )}
      
      <InputBox 
        onSend={handleSendWrapper} 
        onStop={stopGeneration} 
        onSnip={handleSnipClick}
        onImageUpload={setCapturedImage} 
        disabled={loading}
        currentMode={currentMode}
        onSelectMode={onSelectMode}
      />
    </div>
  );
};