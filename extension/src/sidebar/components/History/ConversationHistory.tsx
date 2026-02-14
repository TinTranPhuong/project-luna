import { useHistory } from '../../hooks/useHistory';
import iconTrash from '../../../assets/icon_trash.png';

interface Props {
  onSelectSession: (id: number) => void;
  onNewChat: () => void;
}

export const ConversationHistory = ({ onSelectSession, onNewChat }: Props) => {
  // Destructure the new deleteSession function
  const { sessions, loading, clearAllSessions, deleteSession } = useHistory();

  const handleClearAll = async () => {
    if (confirm("Are you sure you want to delete all chat history?")) {
      await clearAllSessions();
      onNewChat();
    }
  };

  const handleDeleteOne = async (e: React.MouseEvent, id: number) => {
    e.stopPropagation();
    if (confirm("Delete this conversation?")) {
      await deleteSession(id);
    }
  };

  return (
    <div className="app-container">
      
      {/* The List Container */}
      <div className="history-content">
        <div style={{ marginBottom: '16px' }}>
             <h3 style={{ margin: 0, fontSize: '14px', opacity: 0.6, textTransform: 'uppercase', letterSpacing: '1px' }}>
                 Archives
             </h3>
        </div>

        {loading ? (
          <div className="history-empty">Loading archives...</div>
        ) : sessions.length === 0 ? (
          <div className="history-empty">No conversation history found.</div>
        ) : (
          sessions.map(session => (
            <div 
              key={session.id}
              onClick={() => onSelectSession(session.id)}
              className="history-item"
              style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}
            >
              {/* Left Side: Title & Date */}
              <div style={{ overflow: 'hidden', flex: 1, paddingRight: '10px' }}>
                <div style={{ fontWeight: 600, marginBottom: '4px' }}>
                  {/* Clean Title Logic Preserved */}
                  {session.title.replace(/Context: <details>.*<\/summary>/, "").substring(0, 40) || "Untitled Chat"}
                </div>
                <div style={{ fontSize: '11px', opacity: 0.6 }}>
                  {new Date(session.created_at).toLocaleDateString()}
                </div>
              </div>

              {/* Trash Button */}
              <button 
                onClick={(e) => handleDeleteOne(e, session.id)}
                title="Delete Chat"
                style={{ 
                  background: 'transparent', border: 'none', cursor: 'pointer', padding: '6px',
                  opacity: 0.4, transition: 'all 0.2s', borderRadius: '4px',
                  display: 'flex', alignItems: 'center', justifyContent: 'center'
                }}
                onMouseEnter={(e) => {
                   e.currentTarget.style.opacity = '1';
                   e.currentTarget.style.backgroundColor = 'rgba(239, 68, 68, 0.2)'; // Light Red Hover
                }}
                onMouseLeave={(e) => {
                   e.currentTarget.style.opacity = '0.4';
                   e.currentTarget.style.backgroundColor = 'transparent';
                }}
              >
                <img src={iconTrash} alt="Delete" style={{ width: '14px', height: '14px' }} />
              </button>

            </div>
          ))
        )}
      </div>

      {/* Footer Actions */}
      {sessions.length > 0 && (
        <div className="input-container" style={{ borderTop: 'none' }}> 
          <button onClick={handleClearAll} className="btn-danger">
            Delete All History
          </button>
        </div>
      )}
    </div>
  );
};