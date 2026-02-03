import { createRoot } from 'react-dom/client';
import { useState, useEffect, useRef } from 'react';
import { MessageItem, Message } from './components/Chat/MessageItem';
import { InputBox } from './components/Chat/InputBox';

// FIX: Import from the existing file structure
import { ConversationHistory } from './components/History/ConversationHistory';

const Sidebar = () => {
  // View State: 'chat' or 'history'
  const [view, setView] = useState<'chat' | 'history'>('chat');
  
  const [messages, setMessages] = useState<Message[]>([]);
  const [currentSessionId, setCurrentSessionId] = useState<number | null>(null);
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Auto-scroll
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };
  useEffect(() => { scrollToBottom(); }, [messages, view]);

  // Load initial state (New Chat)
  useEffect(() => {
    if (!currentSessionId && messages.length === 0) {
      setMessages([{ id: 'init', role: 'assistant', content: 'Hello! I am Luna. How can I help you?' }]);
    }
  }, []);

  // --- Actions ---

  const handleLoadSession = async (sessionId: number) => {
    setLoading(true);
    setCurrentSessionId(sessionId);
    setView('chat'); // Switch back to chat view
    
    try {
      const res = await fetch(`http://localhost:8000/api/v1/chat/history/${sessionId}`);
      const history = await res.json();
      
      // Map DB format to UI format
      const uiMessages: Message[] = history.map((msg: any) => ({
        id: msg.id.toString(),
        role: msg.role,
        content: msg.content
      }));
      setMessages(uiMessages);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  const handleNewChat = () => {
    setCurrentSessionId(null);
    setMessages([{ id: Date.now().toString(), role: 'assistant', content: 'Hello! I am Luna. How can I help you?' }]);
    setView('chat');
  };

  const handleSend = async (text: string, context?: string) => {
    // 1. Prepare the content
    let displayContent = text;
    let payloadMessage = text;

    if (context) {
      // Create the hidden block
      const contextBlock = `Context:\n<details><summary>📄 View Attached Page Content</summary>\n\n${context}\n\n</details>`;
      
      // Update what YOU see (Context + Question)
      displayContent = `${contextBlock}\n\n${text}`;
      
      // Update what the AI sees
      payloadMessage = `${contextBlock}\n\nQuestion: ${text}`;
    }

    // 2. Add to UI immediately
    const userMsg: Message = { 
      id: Date.now().toString(), 
      role: 'user', 
      content: displayContent // <--- CHANGE: Show the full content (collapsed)
    };
    
    setMessages(prev => [...prev, userMsg]);
    setLoading(true);

    try {
      const payload: any = { message: payloadMessage }; // <--- CHANGE: Use the formatted payload
      if (currentSessionId) payload.session_id = currentSessionId;

      const response = await fetch('http://localhost:8000/api/v1/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });

      const data = await response.json();
      
      if (!currentSessionId) setCurrentSessionId(data.session_id);

      const aiMsg: Message = { 
        id: (Date.now() + 1).toString(), 
        role: 'assistant', 
        content: data.response 
      };
      setMessages(prev => [...prev, aiMsg]);

    } catch (error) {
      console.error(error);
      setMessages(prev => [...prev, { id: Date.now().toString(), role: 'assistant', content: "⚠️ Error: Server offline." }]);
    } finally {
      setLoading(false);
    }
  };

  // --- Render ---

  if (view === 'history') {
    return <ConversationHistory onSelectSession={handleLoadSession} onNewChat={handleNewChat} />;
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100vh', fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif' }}>
      
      {/* Header with History Button */}
      <div style={{ padding: '12px 16px', borderBottom: '1px solid #E5E5EA', display: 'flex', justifyContent: 'space-between', alignItems: 'center', backgroundColor: '#F9F9F9' }}>
        <span style={{ fontWeight: 'bold' }}>🌙 Luna AI</span>
        <button 
          onClick={() => setView('history')}
          style={{ background: 'none', border: 'none', cursor: 'pointer', fontSize: '18px' }}
          title="View History"
        >
          History
        </button>
      </div>

      {/* Message List */}
      <div style={{ flex: 1, overflowY: 'auto', padding: '16px' }}>
        {messages.map(msg => (
          <MessageItem key={msg.id} message={msg} />
        ))}
        {loading && <div style={{ color: '#8E8E93', fontSize: '12px', marginLeft: '10px' }}>Thinking...</div>}
        <div ref={messagesEndRef} />
      </div>

      <InputBox onSend={handleSend} disabled={loading} />
    </div>
  );
};

const container = document.createElement('div');
document.body.appendChild(container);
const root = createRoot(container);
root.render(<Sidebar />);