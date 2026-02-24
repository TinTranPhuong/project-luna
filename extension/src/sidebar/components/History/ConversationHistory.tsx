import { useHistory } from '../../hooks/useHistory';
import iconTrash from '../../../assets/icon_trash.png';

interface Props {
  onSelectSession: (id: number) => void;
  onNewChat: () => void;
}

/* --- TIME HELPER --- */
const getRelativeTime = (dateString: string) => {
  const date = new Date(dateString);
  const now = new Date();
  const diffInSeconds = Math.floor((now.getTime() - date.getTime()) / 1000);

  if (diffInSeconds < 60) return 'Just now';
  
  const diffInMinutes = Math.floor(diffInSeconds / 60);
  if (diffInMinutes < 60) return `${diffInMinutes}m ago`;
  
  const diffInHours = Math.floor(diffInMinutes / 60);
  if (diffInHours < 24) return `${diffInHours}h ago`;
  
  const diffInDays = Math.floor(diffInHours / 24);
  if (diffInDays === 1) return 'Yesterday';
  if (diffInDays < 7) return `${diffInDays}d ago`;
  
  return date.toLocaleDateString(); // Fallback for older dates
};

export const ConversationHistory = ({ onSelectSession, onNewChat }: Props) => {
  /* --- HOOKS & STATE --- */
  const { sessions, loading, clearAllSessions, deleteSession } = useHistory();

  /* --- EVENT HANDLERS --- */
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
      
      {/* --- HISTORY ARCHIVE LIST --- */}
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
              
              {/* --- SESSION METADATA --- */}
              <div style={{ overflow: 'hidden', flex: 1, paddingRight: '10px' }}>
                <div style={{ fontWeight: 600, marginBottom: '4px' }}>
                  {session.title.replace(/Context: <details>.*<\/summary>/, "").substring(0, 40) || "Untitled Chat"}
                </div>
                
                {/* RELATIVE TIME */}
                <div style={{ fontSize: '11px', opacity: 0.6 }}>
                  {getRelativeTime(session.created_at)}
                </div>
              </div>

              {/* CLEANED TRASH BUTTON */}
              <button 
                className="trash-btn"
                onClick={(e) => handleDeleteOne(e, session.id)}
                title="Delete Chat"
              >
                <img src={iconTrash} alt="Delete" style={{ width: '14px', height: '14px' }} />
              </button>

            </div>
          ))
        )}
      </div>

      {/* --- FOOTER ACTIONS --- */}
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