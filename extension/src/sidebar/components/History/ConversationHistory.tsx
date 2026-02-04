import { useHistory } from '../../hooks/useHistory';

interface Props {
  onSelectSession: (id: number) => void;
  onNewChat: () => void;
}

export const ConversationHistory = ({ onSelectSession, onNewChat }: Props) => {
  const { sessions, loading, clearAllSessions } = useHistory();

  const handleClear = async () => {
    if (confirm("Are you sure you want to delete all chat history?")) {
      await clearAllSessions();
      onNewChat();
    }
  };

  return (
    // REMOVED: style={{ backgroundColor: '#F9F9F9' }}
    // The class 'app-container' now handles the background color automatically
    <div className="app-container">
      
      {/* Header */}
      <div className="header">
        <span>Recent Chats</span>
        <button onClick={onNewChat} className="btn-primary">New Chat</button>
      </div>

      {/* Scrollable List */}
      <div className="history-content" style={{ overflowY: 'auto', flex: 1 }}>
        {loading ? (
          <div style={{ padding: '20px', textAlign: 'center', color: 'var(--text-secondary)' }}>Loading...</div>
        ) : sessions.length === 0 ? (
          <div style={{ padding: '20px', textAlign: 'center', color: 'var(--text-secondary)' }}>No history found.</div>
        ) : (
          sessions.map(session => (
            <div 
              key={session.id}
              onClick={() => onSelectSession(session.id)}
              className="history-item"
            >
              {/* Clean up the title if it accidentally saved HTML context tags */}
              {session.title.replace(/Context: <details>.*<\/summary>/, "").substring(0, 50)}
            </div>
          ))
        )}
      </div>

      {/* Footer Actions */}
      {sessions.length > 0 && (
        <div style={{ 
          padding: '16px', 
          borderTop: '1px solid var(--border-color)', 
          // REMOVED: backgroundColor: 'white'
          backgroundColor: 'var(--bg-main)' 
        }}>
          <button onClick={handleClear} className="btn-danger">Clear All History</button>
        </div>
      )}
    </div>
  );
};