import { useEffect } from 'react';
import { MessageList } from './MessageList';
import { InputBox } from './InputBox';
import { useChat } from '../../hooks/useChat'; 

interface Props {
  sessionId: number | null;
  onSessionCreated: (id: number) => void;
}

// FIX: Remove 'onSessionCreated' from here 👇
export const ChatInterface = ({ sessionId }: Props) => {
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
    // FIX: Just await. Do not expect a return value.
    await sendMessage(text, context);
  };

  return (
    <div className="app-container">
      <MessageList messages={messages} loading={loading} />
      
      <InputBox 
        onSend={handleSendWrapper} 
        onStop={stopGeneration} 
        disabled={loading} 
      />
    </div>
  );
};