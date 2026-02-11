import { useEffect, useState } from 'react';
import { MessageList } from './MessageList';
import { InputBox } from './InputBox';
import { useChat } from '../../hooks/useChat'; 

interface Props {
  sessionId: number | null;
  onSessionCreated: (id: number) => void;
}

export const ChatInterface = ({ sessionId }: Props) => {
  // NEW: State for RAG Toggle
  const [useRag, setUseRag] = useState(true);

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

  const handleSendWrapper = async (text: string, context?: string) => {
    // Pass the useRag state to the hook
    await sendMessage(text, useRag, context);
  };

  return (
    <div className="app-container">
      {/* HEADER CONTROLS (Brain Toggle) */}
      <div style={{ 
        padding: '10px 20px', 
        display: 'flex', 
        justifyContent: 'flex-end',
        alignItems: 'center',
        gap: '8px',
        backgroundColor: 'var(--header-bg)',
        borderBottom: '1px solid var(--header-border)'
      }}>
        <span style={{ fontSize: '11px', color: 'var(--text-secondary)', fontWeight: 600 }}>
          BRAIN:
        </span>
        <button 
          onClick={() => setUseRag(!useRag)}
          style={{
            padding: '4px 10px',
            borderRadius: '12px',
            border: 'none',
            fontSize: '11px',
            fontWeight: 'bold',
            cursor: 'pointer',
            backgroundColor: useRag ? '#22c55e' : '#64748b',
            color: 'white',
            transition: 'all 0.2s'
          }}
        >
          {useRag ? "ON" : "OFF"}
        </button>
      </div>

      <MessageList messages={messages} loading={loading} />
      
      <InputBox 
        onSend={handleSendWrapper} 
        onStop={stopGeneration} 
        disabled={loading} 
      />
    </div>
  );
};