import { useEffect, useRef } from 'react';
import { MessageItem, Message } from './MessageItem';

interface Props {
  messages: Message[];
  loading: boolean;
}

export const MessageList = ({ messages, loading }: Props) => {
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to the bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, loading]);

  return (
    <div className="chat-content">
      {/* Empty State / Welcome Message */}
      {messages.length === 0 && !loading && (
        <div style={{ textAlign: 'center', marginTop: '40px', color: '#888' }}>
          <h3> Luna is here!   (づ￣ ³￣)づ </h3>
          <p> Ready to assist. Upload a file or start typing. </p>
        </div>
      )}

      {/* Render list of messages */}
      {messages.map((msg) => (
        <MessageItem key={msg.id} message={msg} />
      ))}

      {/* Typing Indicator */}
      {loading && (
        <div style={{ 
          alignSelf: 'flex-start', 
          backgroundColor: '#F2F2F7', 
          padding: '10px 16px', 
          borderRadius: '12px', 
          color: '#8E8E93', 
          fontSize: '12px',
          marginBottom: '10px'
        }}>
          Generating response...
        </div>
      )}
      
      {/* Invisible anchor for scrolling */}
      <div ref={messagesEndRef} />
    </div>
  );
};