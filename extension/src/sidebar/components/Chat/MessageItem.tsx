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
          message.content
        ) : (
          <ReactMarkdown 
            remarkPlugins={[remarkGfm]}
            components={{
              // THE UPGRADE: Dark Mode for Code Blocks
              code({node, className, children, ...props}) {
                const match = /language-(\w+)/.exec(className || '');
                const isInline = !match && !String(children).includes('\n');
                
                return (
                  <code style={{ 
                    // Dark Grey Background (#1E1E1E) for blocks, Light for inline
                    backgroundColor: isInline ? 'rgba(0,0,0,0.05)' : '#1E1E1E',
                    color: isInline ? 'inherit' : '#D4D4D4', // Light Grey Text
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