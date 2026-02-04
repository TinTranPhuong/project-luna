import { createRoot } from 'react-dom/client';
import { useState } from 'react';
import { ChatInterface } from './components/Chat/ChatInterface';
import { ConversationHistory } from './components/History/ConversationHistory';
import { useTheme } from './hooks/useTheme';
import './styles/sidebar.css';

// Import Menu Icon
import iconMenu from '../assets/icon_menu.png';

const Sidebar = () => {
  const [view, setView] = useState<'chat' | 'history'>('chat');
  const [currentSessionId, setCurrentSessionId] = useState<number | null>(null);
  const [showMenu, setShowMenu] = useState(false); // Controls the dropdown
  
  const { theme, toggleTheme } = useTheme();

  const handleSelectSession = (id: number) => {
    setCurrentSessionId(id);
    setView('chat'); 
    setShowMenu(false); // Close menu if open
  };

  const handleNewChat = () => {
    setCurrentSessionId(null); 
    setView('chat');
    setShowMenu(false);
  };

  const handleSessionCreated = (id: number) => {
    setCurrentSessionId(id);
  };

  return (
    <div className="app-container">
      
      {/* HEADER */}
      <div className="header">
        {/* LEFT: Menu Button (Only shows in Chat view) */}
        {view === 'chat' ? (
          <div style={{ position: 'relative' }}>
            <button 
                onClick={() => setShowMenu(!showMenu)} 
                className="icon-btn"
                title="Settings"
            >
              <img src={iconMenu} alt="Menu" style={{ width: '24px', height: '24px' }} />
            </button>

            {/* SETTINGS DROPDOWN */}
            {showMenu && (
              <div className="settings-menu">
                {/* Option 1: History */}
                <div 
                  className="menu-item" 
                  onClick={() => { setView('history'); setShowMenu(false); }}
                >
                  <span>History</span>
                </div>
                
                {/* Option 2: Theme Toggle */}
                <div className="menu-item" onClick={toggleTheme}>
                  <span>{theme === 'light' ? 'Dark Mode' : 'Light Mode'}</span>
                </div>
              </div>
            )}
          </div>
        ) : (
          // If in History view, show a simple "Back" text or icon
          <button onClick={() => setView('chat')} className="header-btn">
            Back
          </button>
        )}

        {/* CENTER: Title */}
        <span>LUNA</span>
        
        {/* RIGHT: Empty placeholder to balance the flex layout */}
        <div style={{ width: ' 24px' }}></div>
      </div>

      {/* CONTENT */}
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
  );
};

const container = document.createElement('div');
document.body.appendChild(container);
const root = createRoot(container);
root.render(<Sidebar />);