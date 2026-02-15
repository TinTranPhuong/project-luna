import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import remarkMath from 'remark-math'; 
import rehypeKatex from 'rehype-katex'; 
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { oneDark } from 'react-syntax-highlighter/dist/esm/styles/prism';
import 'katex/dist/katex.min.css'; 

// Import Icon for the Search Card
import iconIdea from '../../../assets/icon_idea.png'; 

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

  // --- HANDLER: Open Ghost Tab ---
  const handleGhostSearch = (query: string) => {
    chrome.runtime.sendMessage({ action: "OPEN_GHOST_TAB", query: query });
  };

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

  // --- HELPER: Assistant Message (with Ghost Detection) ---
  const renderAssistantMessage = (content: string) => {
    
    // 1. Detect <cmd_browser> TAG
    const browserMatch = /<cmd_browser>(.*?)<\/cmd_browser>/.exec(content);
    let searchRequest: string | null = null;
    let finalAnswer = content;

    if (browserMatch) {
      searchRequest = browserMatch[1].trim();
      finalAnswer = content.replace(browserMatch[0], "").trim(); 
    }

    // 2. Extract <think> block
    const thinkMatch = /<think>([\s\S]*?)<\/think>/.exec(finalAnswer);
    let thoughtContent: string | null = null;

    if (thinkMatch) {
      thoughtContent = thinkMatch[1].trim();
      finalAnswer = finalAnswer.replace(thinkMatch[0], "").trim();
    }

    return (
      <div>
        {/* Thought Block */}
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

        {/* GHOST BROWSER CARD */}
        {searchRequest && (
          <div style={{ 
            marginBottom: '15px', padding: '12px', 
            borderRadius: '8px', background: 'rgba(57, 216, 240, 0.1)', 
            border: '1px solid rgba(123, 219, 235, 0.3)',
            display: 'flex', flexDirection: 'column', gap: '8px'
          }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '12px', color: '#48cae4', fontWeight: 600 }}>
              <img src={iconIdea} style={{ width: '20px' }} alt="Net" />
              <span>Luna suggests a Search</span>
            </div>
            <div style={{ fontSize: '13px', color: 'var(--text-primary)' }}>
              "We need to search: <b>{searchRequest}</b> to get more information"
            </div>
            <button 
              onClick={() => handleGhostSearch(searchRequest!)}
              style={{
                background: '#48cae4', color: 'white', border: 'none',
                padding: '6px 12px', borderRadius: '4px', cursor: 'pointer',
                fontSize: '11px', fontWeight: 'bold', alignSelf: 'flex-start'
              }}
            >
              Approve
            </button>
          </div>
        )}

        {/* Main Answer */}
        <ReactMarkdown 
          remarkPlugins={[remarkGfm, remarkMath]} 
          rehypePlugins={[rehypeKatex]} 
          components={{
            // FORCE LINKS TO OPEN IN NEW TAB
            a: ({node, ...props}) => (
              <a 
                target="_blank" 
                rel="noopener noreferrer" 
                style={{ color: '#48cae4', textDecoration: 'underline' }} 
                {...props} 
              />
            ),
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
            },
            p: ({node, ...props}) => <p style={{ marginBottom: '1em' }} {...props} />
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