import { useEffect, useRef } from 'react';
import { MessageItem, Message } from './MessageItem';

interface Props {
  messages: Message[];
  loading: boolean;
  onExecuteGen?: (prompt: string) => void;
}

export const MessageList = ({ messages, loading, onExecuteGen }: Props) => {
  const messagesEndRef = useRef<HTMLDivElement>(null);

  /* --- AUTO-SCROLL LOGIC --- */
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, loading]);

  return (
    <div className="chat-content">
      
      {/* EMPTY STATE */}
      {messages.length === 0 && !loading && (
        <div style={{ textAlign: 'center', marginTop: '40px', color: '#888' }}>
          <h3> Luna is here!   (づ￣ ³￣)づ </h3>
          <p> Ready to assist. Upload a file/image or start typing. </p>
        </div>
      )}

      {/* MESSAGE HISTORY */}
      {messages.map((msg) => (
        <MessageItem 
          key={msg.id} 
          message={msg} 
          onExecuteGen={onExecuteGen}
        />
      ))}

      {/* LOADING INDICATOR */}
      {loading && (
        <div style={{ 
          alignSelf: 'flex-start', 
          backgroundColor: '#48cae4', 
          padding: '10px 16px', 
          borderRadius: '12px', 
          color: '#ffffff', 
          fontSize: '12px',
          marginBottom: '10px'
        }}>
          Luna is thinking...
        </div>
      )}
      
      {/* SCROLL ANCHOR */}
      <div ref={messagesEndRef} />
    </div>
  );
};