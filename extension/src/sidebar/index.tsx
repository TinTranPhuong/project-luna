import { createRoot } from 'react-dom/client';
import { useState } from 'react';
import { ChatInterface } from './components/Chat/ChatInterface';
import { ConversationHistory } from './components/History/ConversationHistory';
import { useTheme } from './hooks/useTheme';
import { api } from './api';
import { MemoryViewer } from './components/History/MemoryViewer';
import { AgentMode } from './components/Chat/ModelSelector';
import './styles/sidebar.css';

import iconMenu from '../assets/icon_menu.png';
import iconSun from '../assets/icon_sun.png';
import iconMoon from '../assets/icon_moon.png';

const Sidebar = () => {
  /* --- STATE MANAGEMENT --- */
  const [view, setView] = useState<'chat' | 'history' | 'memory'>('chat');
  const [currentSessionId, setCurrentSessionId] = useState<number | null>(null);
  const [showMenu, setShowMenu] = useState(false);
  const [mode, setMode] = useState<AgentMode>('general');
  const [ingestUrl, setIngestUrl] = useState('');
  const [statusMsg, setStatusMsg] = useState(''); 
  const [uiScale, setUiScale] = useState(1);
  const [chatKey, setChatKey] = useState(Date.now());
  
  const { theme, toggleTheme } = useTheme();

  /* --- ZOOM CONTROLS --- */
  const handleZoomIn = (e: React.MouseEvent) => {
    e.stopPropagation();
    setUiScale(prev => Math.min(prev + 0.1, 2.0)); 
  };

  const handleZoomOut = (e: React.MouseEvent) => {
    e.stopPropagation();
    setUiScale(prev => Math.max(prev - 0.1, 0.1)); 
  };

  const handleZoomReset = (e: React.MouseEvent) => {
    e.stopPropagation();
    setUiScale(1);
  };

  /* --- NAVIGATION HANDLERS --- */
  const handleSelectSession = (id: number) => {
    setCurrentSessionId(id);
    setChatKey(Date.now());
    setView('chat'); 
    setShowMenu(false);
  };

  const handleNewChat = () => {
    setCurrentSessionId(null); 
    setChatKey(Date.now());
    setView('chat');
    setShowMenu(false);
  };

  const handleSessionCreated = (id: number) => {
    setCurrentSessionId(id);
  };

  /* --- API TRANSACTIONS --- */
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

  /* --- DYNAMIC STYLING --- */
  const appStyle: any = {
    zoom: uiScale,
    height: `${100 / uiScale}vh`, 
    width: `${100 / uiScale}vw`,
  };

  return (
    <div className="app-container" style={appStyle}>
      
      {/* ==========================================
          GLOBAL HEADER 
          ========================================== */}
      <div className="header">
        {view === 'chat' ? (
          <div style={{ position: 'relative' }}>
             
             {/* --- MENU TOGGLE --- */}
             <button onClick={() => setShowMenu(!showMenu)} className="icon-btn">
               <img src={iconMenu} alt="Menu" style={{ width: '24px', height: '24px' }} />
             </button>

             {/* --- DROPDOWN SETTINGS MENU --- */}
             {showMenu && (
               <div className="settings-menu" style={{ width: '220px' }}>
                 
                 {/* ZOOM CONTROLS */}
                 <div style={{ padding: '8px 10px', borderBottom: '1px solid var(--header-border)', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                    <span style={{ fontSize: '13px', color: '#ffb3c1', fontWeight: 600 }}>ZOOM</span>
                    <div style={{ display: 'flex', gap: '4px', alignItems: 'center' }}>
                      <button onClick={handleZoomOut} className="zoom-btn">-</button>
                      <span onClick={handleZoomReset} style={{ fontSize: '10px', minWidth: '35px', textAlign: 'center', cursor: 'pointer', userSelect: 'none' }} title="Reset">
                        {Math.round(uiScale * 100)}%
                      </span>
                      <button onClick={handleZoomIn} className="zoom-btn">+</button>
                    </div>
                 </div>

                 {/* NAVIGATION LINKS */}
                 <div className="menu-item" onClick={handleNewChat}>
                   <span>New Chat</span>
                 </div>
                 <div className="menu-item" onClick={() => { setView('history'); setShowMenu(false); }}>
                   <span>History</span>
                 </div>
                 <div className="menu-item" onClick={() => { setView('memory'); setShowMenu(false); }}>
                   <span>Memory</span>
                 </div>
                 
                 {/* MAINTENANCE CONTROLS */}
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

                 {/* KNOWLEDGE INGESTION */}
                 <div style={{ padding: '8px 10px', borderTop: '1px solid var(--header-border)' }}>
                    <div style={{ fontSize: '10px', fontWeight: 'bold', color: '#94a3b8', marginBottom: '4px' }}>TEACH LUNA</div>
                    <div style={{ display: 'flex', gap: '5px' }}>
                        <input 
                            value={ingestUrl} onChange={(e) => setIngestUrl(e.target.value)}
                            placeholder="Paste URL..." 
                            style={{ flex: 1, fontSize: '11px', padding: '4px', borderRadius: '4px', border: '1px solid #cbd5e1' }}
                        />
                        <button onClick={handleIngest} style={{ background: '#48cae4', color: 'white', border: 'none', borderRadius: '4px', cursor: 'pointer', fontSize: '10px', padding: '0 8px' }}>ADD</button>
                    </div>
                    {statusMsg && <div style={{ fontSize: '10px', color: '#ff8fab', marginTop: '4px', textAlign: 'center' }}>{statusMsg}</div>}
                 </div>
               </div>
             )}
          </div>
        ) : (
          <button onClick={() => setView('chat')} className="header-btn">Back</button>
        )}
        
        {/* --- BRANDING --- */}
        <span>LUNA</span>

        {/* --- THEME TOGGLE --- */}
        <button 
          onClick={toggleTheme}
          title="Toggle Theme"
          className="icon-btn"
          style={{ width: '28px', height: '28px', padding: '4px' }}
        >
          <img 
             src={theme === 'light' ? iconSun : iconMoon} 
             alt="Theme" 
             style={{ width: '20px', height: '20px', opacity: 0.8 }} 
          />
        </button>
      </div>
      
      {/* ==========================================
          DYNAMIC VIEW ROUTING 
          ========================================== */}
      {view === 'history' ? (
        <ConversationHistory onSelectSession={handleSelectSession} onNewChat={handleNewChat} />
      ) : view === 'memory' ? (
        <MemoryViewer /> 
      ) : (
        <ChatInterface 
          key={chatKey}
          sessionId={currentSessionId} 
          onSessionCreated={handleSessionCreated} 
          currentMode={mode} 
          onSelectMode={setMode}
        />
      )}
    </div>
  );
};

const container = document.createElement('div');
document.body.appendChild(container);
const root = createRoot(container);
root.render(<Sidebar />);