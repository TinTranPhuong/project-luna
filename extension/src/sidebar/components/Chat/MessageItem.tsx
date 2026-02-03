//import { createRoot } from 'react-dom/client';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

export interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
}

interface Props {
  message: Message;
}

export const MessageItem = ({ message }: Props) => {
  const isUser = message.role === 'user';

  // HELPER: Custom renderer for User messages to handle the "Context" dropdown
  const renderUserMessage = (content: string) => {
    // Check if this message has our special "Context" hidden tag
    if (content.includes("Context:") && content.includes("</details>")) {
      const splitIndex = content.indexOf("</details>");
      const contextBlock = content.slice(0, splitIndex); 
      const question = content.slice(splitIndex + 10).trim(); // +10 is the length of "</details>"

      // Clean up the tags to get the raw text content
      let cleanContext = contextBlock
        .replace("Context:", "")
        .replace("<details>", "")
        .replace("<summary>📄 View Attached Page Content</summary>", "")
        .trim();

      return (
        <div>
          {/* The Interactive Dropdown */}
          <details style={{ marginBottom: '8px' }}>
            <summary style={{ cursor: 'pointer', fontWeight: 'bold', fontSize: '12px', opacity: 0.9 }}>
              📄 Attached Content (Click to View)
            </summary>
            <div style={{
              marginTop: '6px',
              fontSize: '11px',
              padding: '8px',
              backgroundColor: 'rgba(0,0,0,0.2)', // Darker background for contrast
              borderRadius: '6px',
              maxHeight: '150px',
              overflowY: 'auto',
              whiteSpace: 'pre-wrap', // Preserve line breaks
              textAlign: 'left'
            }}>
              {cleanContext}
            </div>
          </details>

          {/* The Actual Question */}
          <div style={{ fontSize: '14px' }}>{question}</div>
        </div>
      );
    }
    // Normal message (no context)
    return content;
  };

  return (
    <div style={{
      display: 'flex',
      justifyContent: isUser ? 'flex-end' : 'flex-start',
      marginBottom: '12px',
    }}>
      <div style={{
        maxWidth: '85%',
        padding: '10px 14px',
        borderRadius: '12px',
        fontSize: '14px',
        lineHeight: '1.5',
        backgroundColor: isUser ? '#007AFF' : '#F2F2F7',
        color: isUser ? '#FFFFFF' : '#000000',
        borderBottomRightRadius: isUser ? '2px' : '12px',
        borderBottomLeftRadius: isUser ? '12px' : '2px',
        overflowWrap: 'break-word'
      }}>
        {isUser ? (
          // Use our new helper here
          renderUserMessage(message.content)
        ) : (
          <ReactMarkdown 
            remarkPlugins={[remarkGfm]}
            components={{
              code({node, className, children, ...props}) {
                const match = /language-(\w+)/.exec(className || '');
                const isInline = !match && !String(children).includes('\n');
                
                return (
                  <code style={{ 
                    backgroundColor: isInline ? 'rgba(0,0,0,0.05)' : '#1E1E1E',
                    color: isInline ? 'inherit' : '#D4D4D4',
                    padding: isInline ? '2px 4px' : '12px',
                    borderRadius: '6px', 
                    fontFamily: 'Consolas, Monaco, monospace',
                    display: isInline ? 'inline' : 'block',
                    whiteSpace: 'pre-wrap',
                    margin: isInline ? 0 : '8px 0',
                    border: isInline ? 'none' : '1px solid #333'
                  }} {...props}>
                    {children}
                  </code>
                )
              }
            }}
          >
            {message.content}
          </ReactMarkdown>
        )}
      </div>
    </div>
  );
};