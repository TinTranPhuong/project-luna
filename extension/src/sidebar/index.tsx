import { createRoot } from 'react-dom/client';
import { useState, useEffect, useRef } from 'react';
import { MessageItem, Message } from './components/Chat/MessageItem';
import { InputBox } from './components/Chat/InputBox';

const Sidebar = () => {
  const [messages, setMessages] = useState<Message[]>([
    { id: '1', role: 'assistant', content: 'Hello! I am Luna. How can I help you?' }
  ]);
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSend = async (text: string) => {
    // 1. Add User Message immediately
    const userMsg: Message = { id: Date.now().toString(), role: 'user', content: text };
    setMessages(prev => [...prev, userMsg]);
    setLoading(true);

    try {
      // 2. Call the Local Python Server
      const response = await fetch('http://localhost:8000/api/v1/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: text }) // We handle session_id later
      });

      const data = await response.json();

      // 3. Add AI Response
      const aiMsg: Message = { 
        id: (Date.now() + 1).toString(), 
        role: 'assistant', 
        content: data.response 
      };
      setMessages(prev => [...prev, aiMsg]);

    } catch (error) {
      console.error(error);
      const errorMsg: Message = { 
        id: Date.now().toString(), 
        role: 'assistant', 
        content: "Error: I couldn't reach the local server. Is it running?" 
      };
      setMessages(prev => [...prev, errorMsg]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ 
      display: 'flex', 
      flexDirection: 'column', 
      height: '100vh', 
      fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif' 
    }}>
      {/* Header */}
      <div style={{ padding: '16px', borderBottom: '1px solid #E5E5EA', fontWeight: 'bold' }}>
        Luna AI
      </div>

      {/* Message List (Scrollable) */}
      <div style={{ flex: 1, overflowY: 'auto', padding: '16px' }}>
        {messages.map(msg => (
          <MessageItem key={msg.id} message={msg} />
        ))}
        {loading && <div style={{ color: '#8E8E93', fontSize: '12px', marginLeft: '10px' }}>Luna is thinking...</div>}
        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <InputBox onSend={handleSend} disabled={loading} />
    </div>
  );
};

const container = document.createElement('div');
document.body.appendChild(container);
const root = createRoot(container);
root.render(<Sidebar />);