import { createRoot } from 'react-dom/client';
import { useState } from 'react';
import { ChatInterface } from './components/Chat/ChatInterface';
import { ConversationHistory } from './components/History/ConversationHistory';
import { useTheme } from './hooks/useTheme'; // <--- Import Hook
import './styles/sidebar.css';

const Sidebar = () => {
  const [view, setView] = useState<'chat' | 'history'>('chat');
  const [currentSessionId, setCurrentSessionId] = useState<number | null>(null);
  
  // Initialize Theme
  const { theme, toggleTheme } = useTheme();

  const handleSelectSession = (id: number) => {
    setCurrentSessionId(id);
    setView('chat'); 
  };

  const handleNewChat = () => {
    setCurrentSessionId(null); 
    setView('chat');
  };

  const handleSessionCreated = (id: number) => {
    setCurrentSessionId(id);
  };

  return (
    <div className="app-container">
      {/* Header */}
      <div className="header">
        {/* Left: Theme Toggle */}
        <button 
            onClick={toggleTheme} 
            className="header-btn" 
            title={`Switch to ${theme === 'light' ? 'Dark' : 'Light'} Mode`}
        >
          {theme === 'light' ? 'Dark' : 'Light'}
        </button>

        {/* Center: Title */}
        <span style={{ fontWeight: 'bold' }}>
          {view === 'history' ? 'History' : (currentSessionId ? 'Chat' : 'New Chat')}
        </span>
        
        {/* Right: Navigation */}
        {view === 'chat' ? (
          <button onClick={() => setView('history')} className="header-btn">
            History
          </button>
        ) : (
          <button onClick={() => setView('chat')} className="header-btn">
            Back
          </button>
        )}
      </div>

      <div style={{ flex: 1, overflow: 'hidden' }}>
        {view === 'history' ? (
          <ConversationHistory 
            onSelectSession={handleSelectSession} 
            onNewChat={handleNewChat} 
          />
        ) : (
          <ChatInterface 
            sessionId={currentSessionId} 
            onSessionCreated={handleSessionCreated} 
          />
        )}
      </div>
    </div>
  );
};

const container = document.createElement('div');
document.body.appendChild(container);
const root = createRoot(container);
root.render(<Sidebar />);