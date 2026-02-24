import { useEffect, useState } from 'react';
import { MessageList } from './MessageList';
import { InputBox } from './InputBox';
import { useChat } from '../../hooks/useChat'; 
import { AgentMode } from './ModelSelector';
import { processCropImage } from '../../utils/imageProcessor'; 

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

  /* --- SESSION MANAGEMENT --- */
  useEffect(() => {
    if (sessionId) loadSession(sessionId);
    else clearChat();
  }, [sessionId, loadSession, clearChat]);

  /* --- EXTENSION MESSAGE LISTENERS --- */
  useEffect(() => {
    const handleMessage = (request: any) => {
      if (request.action === "PROCESS_CROP") {
        processCropImage(request.imageUrl, request.cropData, setCapturedImage);
      }
    };
    
    chrome.runtime.onMessage.addListener(handleMessage);
    return () => chrome.runtime.onMessage.removeListener(handleMessage);
  }, []);

  /* --- EVENT HANDLERS --- */
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
      
      {/* MAIN CHAT AREA */}
      <div style={{ flex: 1, overflowY: 'auto', paddingTop: '60px' }}> 
        <MessageList 
          messages={messages} 
          loading={loading} 
          onExecuteGen={executeGen} 
        />
      </div>

      {/* IMAGE PREVIEW OVERLAY */}
      {capturedImage && (
        <div style={{ padding: '0 20px', marginBottom: '10px' }}>
          <div style={{ position: 'relative', display: 'inline-block' }}>
            <img 
              src={capturedImage} 
              alt="Preview" 
              style={{ 
                height: '80px', borderRadius: '8px', border: '1px solid #ff8fab', 
                boxShadow: '0 4px 10px rgba(0,0,0,0.2)' 
              }} 
            />
            <button 
              onClick={() => setCapturedImage(null)} 
              style={{ 
                position: 'absolute', top: -8, right: -8, background: '#ef4444', 
                color: 'white', borderRadius: '50%', width: '22px', height: '22px', 
                border: '2px solid white', cursor: 'pointer' 
              }}
            >
              ✕
            </button>
          </div>
        </div>
      )}
      
      {/* INPUT COMPONENT */}
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