import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { oneDark } from 'react-syntax-highlighter/dist/esm/styles/prism';

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

  // --- HELPER: User Context ---
  const renderUserMessage = (content: string) => {
    if (content.includes("Context:") && content.includes("</details>")) {
      const splitIndex = content.indexOf("</details>");
      const contextBlock = content.slice(0, splitIndex); 
      const question = content.slice(splitIndex + 10).trim(); 

      let cleanContext = contextBlock
        .replace("Context:", "")
        .replace("<details>", "")
        .replace(/<summary>.*?<\/summary>/, "")
        .trim();

      return (
        <div>
          <details style={{ marginBottom: '8px' }}>
            <summary style={{ cursor: 'pointer', fontWeight: '600', fontSize: '12px', opacity: 0.8 }}>
              View Attachment
            </summary>
            <div className="details-content" style={{
              marginTop: '6px', fontSize: '11px', padding: '8px',
              borderRadius: '6px', maxHeight: '150px', overflowY: 'auto',
              whiteSpace: 'pre-wrap'
            }}>
              {cleanContext}
            </div>
          </details>
          <div style={{ fontSize: '14px' }}>{question}</div>
        </div>
      );
    }
    return content;
  };

  // --- HELPER: Assistant Thoughts ---
  const renderAssistantMessage = (content: string) => {
    const thinkMatch = /<think>([\s\S]*?)<\/think>/.exec(content);
    let thoughtContent: string | null = null;
    let finalAnswer = content;

    if (thinkMatch) {
      thoughtContent = thinkMatch[1].trim();
      finalAnswer = content.replace(thinkMatch[0], "").trim();
    }

    return (
      <div>
        {thoughtContent && (
          <details style={{ marginBottom: '12px', borderBottom: '1px solid var(--border-color)', paddingBottom: '8px' }}>
            <summary style={{ cursor: 'pointer', fontSize: '12px', opacity: 0.7, fontStyle: 'italic', userSelect: 'none' }}>
              View Thought Process
            </summary>
            <div className="details-content" style={{
              marginTop: '8px', fontSize: '12px', padding: '10px',
              borderRadius: '8px', whiteSpace: 'pre-wrap'
            }}>
              {thoughtContent}
            </div>
          </details>
        )}

        <ReactMarkdown 
          remarkPlugins={[remarkGfm]}
          components={{
            code({node, className, children, ...props}) {
              const match = /language-(\w+)/.exec(className || '');
              const isInline = !match && !String(children).includes('\n');
              
              if (!isInline && match) {
                return (
                  <div style={{ borderRadius: '8px', overflow: 'hidden', margin: '10px 0' }}>
                    <SyntaxHighlighter
                      style={oneDark}
                      language={match[1]}
                      PreTag="div"
                      customStyle={{ margin: 0, padding: '12px', fontSize: '12px' }}
                    >
                      {String(children).replace(/\n$/, '')}
                    </SyntaxHighlighter>
                  </div>
                );
              }

              // Fallback for inline code or unknown languages
              return (
                <code style={{ 
                  backgroundColor: 'var(--bg-code-inline)',
                  color: 'var(--text-main)',
                  padding: '2px 4px',
                  borderRadius: '4px', 
                  fontFamily: 'Consolas, monospace',
                  fontSize: '0.9em'
                }} {...props}>
                  {children}
                </code>
              );
            }
          }}
        >
          {finalAnswer}
        </ReactMarkdown>
      </div>
    );
  };

  return (
    <div className={`message-row ${isUser ? 'user' : 'assistant'}`}>
      <div className={`message-bubble ${isUser ? 'user' : 'assistant'}`}>
        {isUser ? renderUserMessage(message.content) : renderAssistantMessage(message.content)}
      </div>
    </div>
  );
};