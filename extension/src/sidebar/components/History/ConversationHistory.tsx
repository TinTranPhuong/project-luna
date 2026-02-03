//import { createRoot } from 'react-dom/client';
import { useState, useEffect } from 'react';

interface Session {
  id: number;
  title: string;
  created_at: string;
}

interface Props {
  onSelectSession: (id: number) => void;
  onNewChat: () => void;
}

export const ConversationHistory = ({ onSelectSession, onNewChat }: Props) => {
  const [sessions, setSessions] = useState<Session[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadSessions();
  }, []);

  const loadSessions = () => {
    fetch('http://localhost:8000/api/v1/chat/sessions')
      .then(res => res.json())
      .then(data => {
        setSessions(data);
        setLoading(false);
      })
      .catch(err => {
        console.error("Failed to load history:", err);
        setLoading(false);
      });
  };

  const handleClearMemory = async () => {
    if (!confirm("⚠️ Are you sure? This will delete ALL chat history permanently.")) {
      return;
    }

    try {
      await fetch('http://localhost:8000/api/v1/chat/sessions', {
        method: 'DELETE'
      });
      // Clear the list locally
      setSessions([]);
      // Start a fresh chat
      onNewChat();
    } catch (e) {
      alert("Failed to wipe memory. Is the server running?");
    }
  };

  return (
    <div style={{ flex: 1, display: 'flex', flexDirection: 'column', backgroundColor: '#F9F9F9' }}>
      {/* Header */}
      <div style={{ padding: '16px', borderBottom: '1px solid #E5E5EA', fontWeight: 'bold', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <span>🕒 Recent Chats</span>
        <button 
          onClick={onNewChat}
          style={{
            padding: '6px 12px',
            backgroundColor: '#007AFF',
            color: 'white',
            border: 'none',
            borderRadius: '16px',
            fontSize: '12px',
            cursor: 'pointer'
          }}
        >
          + New
        </button>
      </div>

      {/* List */}
      <div style={{ overflowY: 'auto', flex: 1 }}>
        {loading ? (
          <div style={{ padding: '20px', textAlign: 'center', color: '#888' }}>Loading...</div>
        ) : sessions.length === 0 ? (
          <div style={{ padding: '20px', textAlign: 'center', color: '#888' }}>No history yet.</div>
        ) : (
          sessions.map(session => (
            <div 
              key={session.id}
              onClick={() => onSelectSession(session.id)}
              style={{
                padding: '12px 16px',
                borderBottom: '1px solid #EFEFEF',
                cursor: 'pointer',
                backgroundColor: 'white',
                fontSize: '14px',
                whiteSpace: 'nowrap',
                overflow: 'hidden',
                textOverflow: 'ellipsis'
              }}
              onMouseEnter={(e) => e.currentTarget.style.backgroundColor = '#F2F2F7'}
              onMouseLeave={(e) => e.currentTarget.style.backgroundColor = 'white'}
            >
              {session.title}
            </div>
          ))
        )}
      </div>

      {/* Footer: Clear Button */}
      {sessions.length > 0 && (
        <div style={{ padding: '16px', borderTop: '1px solid #E5E5EA', backgroundColor: 'white' }}>
          <button
            onClick={handleClearMemory}
            style={{
              width: '100%',
              padding: '10px',
              backgroundColor: '#FF3B30', // Danger Red
              color: 'white',
              border: 'none',
              borderRadius: '8px',
              fontWeight: 600,
              cursor: 'pointer'
            }}
          >
            🗑️ Clear Memory
          </button>
        </div>
      )}
    </div>
  );
};