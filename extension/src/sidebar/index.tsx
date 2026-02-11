import { createRoot } from 'react-dom/client';
import { useState } from 'react';
import { ChatInterface } from './components/Chat/ChatInterface';
import { ConversationHistory } from './components/History/ConversationHistory';
import { useTheme } from './hooks/useTheme';
import { api } from './api';
import { MemoryViewer } from './components/History/MemoryViewer';
import './styles/sidebar.css';
import iconMenu from '../assets/icon_menu.png';

const Sidebar = () => {
  const [view, setView] = useState<'chat' | 'history' | 'memory'>('chat');
  const [currentSessionId, setCurrentSessionId] = useState<number | null>(null);
  const [showMenu, setShowMenu] = useState(false);
  const [ingestUrl, setIngestUrl] = useState('');
  const [statusMsg, setStatusMsg] = useState(''); 

  const { theme, toggleTheme } = useTheme();

  // --- Handlers ---
  const handleSelectSession = (id: number) => {
    setCurrentSessionId(id);
    setView('chat'); 
    setShowMenu(false);
  };

  const handleNewChat = () => {
    setCurrentSessionId(null); 
    setView('chat');
    setShowMenu(false);
  };

  const handleSessionCreated = (id: number) => {
    setCurrentSessionId(id);
  };

  // 1. Handle Ingest (Teach Luna)
  const handleIngest = async () => {
    if(!ingestUrl) return;
    setStatusMsg('Reading...');
    try {
       await api.ingestUrl(ingestUrl);
       setStatusMsg('Learned!');
       setIngestUrl('');
       setTimeout(() => setStatusMsg(''), 2000);
    } catch (e) {
       setStatusMsg('Failed');
    }
  };

  // 2. Handle Cache Clear (Flush Memory)
  const handleClearCache = async () => {
    setStatusMsg('Cleaning...');
    try {
        await api.clearCache();
        setStatusMsg('Cache Wiped!');
        setTimeout(() => setStatusMsg(''), 2000);
    } catch (e) {
        setStatusMsg('Error');
    }
  };

  return (
    <div className="app-container">
      {/* HEADER */}
      <div className="header">
        {view === 'chat' ? (
          <div style={{ position: 'relative' }}>
             {/* Menu Button */}
             <button onClick={() => setShowMenu(!showMenu)} className="icon-btn">
               <img src={iconMenu} alt="Menu" style={{ width: '24px', height: '24px' }} />
             </button>

             {/* SETTINGS MENU */}
             {showMenu && (
               <div className="settings-menu" style={{ width: '220px' }}>
                 
                 <div className="menu-item" onClick={() => { setView('history'); setShowMenu(false); }}>
                   <span>History</span>
                 </div>
                 <div className="menu-item" onClick={() => { setView('memory'); setShowMenu(false); }}>
                   <span>Memory</span>
                 </div>
                 <div className="menu-item" onClick={toggleTheme}>
                   <span>{theme === 'light' ? 'Dark Mode' : 'Light Mode'}</span>
                 </div>

                 {/* MAINTENANCE (Cache) */}
                 <div style={{ padding: '8px 10px', borderTop: '1px solid var(--header-border)', marginTop: '5px' }}>
                    <div style={{ fontSize: '10px', fontWeight: 'bold', color: '#94a3b8', marginBottom: '4px' }}>MAINTENANCE</div>
                    <button 
                        onClick={handleClearCache}
                        style={{
                            width: '100%', padding: '6px', borderRadius: '6px',
                            border: '1px solid var(--bubble-border-ai)', background: 'var(--bg-app)',
                            color: 'var(--text-primary)', fontSize: '11px', cursor: 'pointer',
                            display: 'flex', justifyContent: 'space-between'
                        }}
                    >
                        <span>Clear Cache</span>
                    </button>
                 </div>

                 {/* TEACH LUNA (Ingest) */}
                 <div style={{ padding: '8px 10px', borderTop: '1px solid var(--header-border)' }}>
                    <div style={{ fontSize: '10px', fontWeight: 'bold', color: '#94a3b8', marginBottom: '4px' }}>TEACH LUNA</div>
                    <div style={{ display: 'flex', gap: '5px' }}>
                        <input 
                            value={ingestUrl} onChange={(e) => setIngestUrl(e.target.value)}
                            placeholder="Paste URL..." 
                            style={{ flex: 1, fontSize: '11px', padding: '4px', borderRadius: '4px', border: '1px solid #cbd5e1' }}
                        />
                        <button onClick={handleIngest} style={{ background: '#60a5fa', color: 'white', border: 'none', borderRadius: '4px', cursor: 'pointer', fontSize: '10px', padding: '0 8px' }}>ADD</button>
                    </div>
                    {statusMsg && <div style={{ fontSize: '10px', color: '#22c55e', marginTop: '4px', textAlign: 'center' }}>{statusMsg}</div>}
                 </div>

               </div>
             )}
          </div>
        ) : (
          <button onClick={() => setView('chat')} className="header-btn">Back</button>
        )}
        <span>LUNA</span>
        <div style={{ width: '24px' }}></div>
      </div>
      
      {/* CONTENT */}
      {view === 'history' ? (
        <ConversationHistory onSelectSession={handleSelectSession} onNewChat={handleNewChat} />
      ) : view === 'memory' ? (
        <MemoryViewer /> 
      ) : (
        <ChatInterface sessionId={currentSessionId} onSessionCreated={handleSessionCreated} />
      )}
    </div>
  );
};

const container = document.createElement('div');
document.body.appendChild(container);
const root = createRoot(container);
root.render(<Sidebar />);