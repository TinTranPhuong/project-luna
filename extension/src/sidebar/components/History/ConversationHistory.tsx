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
    <div className="app-container">
      
      {/* Header (managed by parent index.tsx usually, but if duplicated here:) */}
      {/* Note: In your index.tsx you already have a header, so this component 
          should strictly just be the list. If this header is redundant, 
          you might see two headers. Assuming this is the content area: */}
      
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
            >
              <div style={{ fontWeight: 600, marginBottom: '4px' }}>
                {/* Clean Title */}
                {session.title.replace(/Context: <details>.*<\/summary>/, "").substring(0, 40) || "Untitled Chat"}
              </div>
              <div style={{ fontSize: '11px', opacity: 0.6 }}>
                {new Date(session.created_at).toLocaleDateString()}
              </div>
            </div>
          ))
        )}
      </div>

      {/* Footer Actions */}
      {sessions.length > 0 && (
        <div className="input-container" style={{ borderTop: 'none' }}> 
          {/* We reuse input-container class for the glass effect at the bottom */}
          <button onClick={handleClear} className="btn-danger">
            Delete All History
          </button>
        </div>
      )}
    </div>
  );
};