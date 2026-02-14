import { useEffect, useState } from 'react';
import { MessageList } from './MessageList';
import { InputBox } from './InputBox';
import { useChat } from '../../hooks/useChat'; 

interface Props {
  sessionId: number | null;
  onSessionCreated: (id: number) => void;
}

export const ChatInterface = ({ sessionId }: Props) => {
  const useRag = true; 
  
  // State for EITHER a Snippet OR an Uploaded Image
  const [capturedImage, setCapturedImage] = useState<string | null>(null);
  
  const { 
    messages, 
    loading, 
    sendMessage, 
    loadSession, 
    clearChat, 
    stopGeneration 
  } = useChat(sessionId);

  useEffect(() => {
    if (sessionId) {
      loadSession(sessionId);
    } else {
      clearChat();
    }
  }, [sessionId, loadSession, clearChat]);

  // Listen for "PROCESS_CROP" from Background Script (Snipping Tool)
  useEffect(() => {
    const handleMessage = (request: any) => {
      if (request.action === "PROCESS_CROP") {
        console.log("Received Crop Data, processing...");
        cropImage(request.imageUrl, request.cropData);
      }
    };
    chrome.runtime.onMessage.addListener(handleMessage);
    return () => chrome.runtime.onMessage.removeListener(handleMessage);
  }, []);

  // Crop Logic (for Screen Snipper)
  const cropImage = (fullImageUrl: string, crop: any) => {
    const canvas = document.createElement('canvas');
    const ctx = canvas.getContext('2d');
    const img = new Image();

    img.onload = () => {
      const scale = crop.devicePixelRatio || 1; 
      canvas.width = crop.width * scale;
      canvas.height = crop.height * scale;

      ctx?.drawImage(
        img, 
        crop.x * scale, crop.y * scale, crop.width * scale, crop.height * scale, 
        0, 0, canvas.width, canvas.height 
      );

      const croppedBase64 = canvas.toDataURL('image/jpeg', 0.8);
      setCapturedImage(croppedBase64); // Sets the image state
    };
    img.src = fullImageUrl;
  };

  // The function to trigger snipping
  const handleSnipClick = () => {
    chrome.runtime.sendMessage({ action: "START_SNIP" });
  };

  const handleSendWrapper = async (text: string) => {
    // Send text + whatever image is currently in the preview (Snippet OR Upload)
    await sendMessage(text, useRag, capturedImage || undefined);
    setCapturedImage(null); // Clear preview after sending
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
      
      {/* 1. MESSAGES AREA */}
      <div style={{ flex: 1, overflowY: 'auto', paddingTop: '60px' }}> 
        <MessageList messages={messages} loading={loading} />
      </div>

      {/* 2. IMAGE PREVIEW (Shows up above input when you snip OR upload) */}
      {capturedImage && (
        <div style={{ padding: '0 20px', marginBottom: '10px' }}>
          <div style={{ position: 'relative', display: 'inline-block' }}>
            <img 
              src={capturedImage} 
              alt="Preview"
              style={{ height: '80px', borderRadius: '8px', border: '1px solid #ff8fab', boxShadow: '0 4px 10px rgba(0,0,0,0.2)' }} 
            />
            <button 
              onClick={() => setCapturedImage(null)}
              style={{ 
                position: 'absolute', top: -8, right: -8, background: '#ef4444', color: 'white', 
                borderRadius: '50%', width: '22px', height: '22px', border: '2px solid white', 
                cursor: 'pointer', fontSize: '12px', display: 'flex', alignItems: 'center', justifyContent: 'center' 
              }}
            >✕</button>
          </div>
        </div>
      )}
      
      {/* 3. INPUT BOX (Updated to accept Uploads) */}
      <InputBox 
        onSend={handleSendWrapper} 
        onStop={stopGeneration} 
        onSnip={handleSnipClick}
        onImageUpload={setCapturedImage} 
        disabled={loading} 
      />
    </div>
  );
};