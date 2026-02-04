import { useEffect } from 'react';
import { MessageList } from './MessageList';
import { InputBox } from './InputBox';
import { useChat } from '../../hooks/useChat'; 

interface Props {
  sessionId: number | null;
  onSessionCreated: (id: number) => void;
}

export const ChatInterface = ({ sessionId, onSessionCreated }: Props) => {
  // Use the custom hook instead of local state
  const { messages, loading, sendMessage, loadSession, clearChat } = useChat(sessionId);

  // Sync session ID changes
  useEffect(() => {
    if (sessionId) {
      loadSession(sessionId);
    } else {
      clearChat();
    }
  }, [sessionId, loadSession, clearChat]);

  const handleSendWrapper = async (text: string, context?: string) => {
    const newSessionId = await sendMessage(text, context);
    if (newSessionId && !sessionId) {
      onSessionCreated(newSessionId);
    }
  };

  return (
    <div className="app-container">
      <MessageList messages={messages} loading={loading} />
      <InputBox onSend={handleSendWrapper} disabled={loading} />
    </div>
  );
};