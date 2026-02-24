import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import remarkMath from 'remark-math'; 
import rehypeKatex from 'rehype-katex'; 
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { oneDark } from 'react-syntax-highlighter/dist/esm/styles/prism';
import 'katex/dist/katex.min.css'; 
import iconIdea from '../../../assets/icon_idea.png'; 

export interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
}

interface Props {
  message: Message;
  onExecuteGen?: (prompt: string) => void;
}

export const MessageItem = ({ message, onExecuteGen }: Props) => {
  const isUser = message.role === 'user';

  /* --- EXTENSION MESSAGING --- */
  const handleGhostSearch = (query: string) => {
    chrome.runtime.sendMessage({ action: "OPEN_GHOST_TAB", query: query });
  };

  /* --- USER MESSAGE RENDERER --- */
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

  /* --- AI RESPONSE PARSER & RENDERER --- */
  const renderAssistantMessage = (content: string) => {
    let finalAnswer = content;

    /* --- 1. HARMONY FORMAT & MATH NORMALIZATION --- */
    finalAnswer = finalAnswer.replace(/(?:<\|start\|>assistant)?<\|channel\|>analysis.*?<\|message\|>/g, "<think>\n");
    finalAnswer = finalAnswer.replace(/(?:<\|start\|>assistant)?<\|channel\|>(?!analysis).*?<\|message\|>/g, "\n</think>\n");
    finalAnswer = finalAnswer.replace(/<\|im_start\|>assistant/g, "\n</think>\n");
    finalAnswer = finalAnswer.replace(/<\|end\|>/g, ""); 
    finalAnswer = finalAnswer.replace(/\\\[([\s\S]*?)\\\]/g, '$$$$$1$$$$');
    finalAnswer = finalAnswer.replace(/\\\(([\s\S]*?)\\\)/g, '$$$1$$');

    /* --- 2. TOOL EXTRACTION: BROWSER --- */
    const browserMatch = /<cmd_browser>(.*?)<\/cmd_browser>/.exec(finalAnswer);
    let searchRequest: string | null = null;

    if (browserMatch) {
      searchRequest = browserMatch[1].trim();
      finalAnswer = finalAnswer.replace(browserMatch[0], "").trim(); 
    }

    /* --- 3. TOOL EXTRACTION: IMAGE APPROVAL --- */
    const approveMatch = /<cmd_image_approve>([\s\S]*?)<\/cmd_image_approve>/.exec(finalAnswer);
    let promptToApprove: string | null = null;

    if (approveMatch) {
        promptToApprove = approveMatch[1].trim();
        finalAnswer = finalAnswer.replace(/<cmd_image_approve>([\s\S]*?)<\/cmd_image_approve>/g, "").trim();
    }

    /* --- 4. TOOL EXTRACTION: IMAGE TRACKING --- */
    const trackMatch = /<cmd_image_track>(.*?)<\/cmd_image_track>/.exec(finalAnswer);
    let trackId: string | null = null;

    if (trackMatch) {
      trackId = trackMatch[1].trim();
      finalAnswer = finalAnswer.replace(/<cmd_image_track>(.*?)<\/cmd_image_track>/g, "").trim();
    }

    /* --- 5. CHAIN-OF-THOUGHT EXTRACTION --- */
    const thinkStart = finalAnswer.indexOf("<think>");
    let thoughtContent: string | null = null;

    if (thinkStart !== -1) {
        const thinkEnd = finalAnswer.indexOf("</think>", thinkStart);
        if (thinkEnd !== -1) {
            thoughtContent = finalAnswer.substring(thinkStart + 7, thinkEnd).trim();
            finalAnswer = finalAnswer.substring(0, thinkStart) + finalAnswer.substring(thinkEnd + 8);
        } else {
            thoughtContent = finalAnswer.substring(thinkStart + 7).trim();
            finalAnswer = finalAnswer.substring(0, thinkStart);
        }
    }

    finalAnswer = finalAnswer.trim();

    return (
      <div>
        
        {/* --- CHAIN OF THOUGHT UI --- */}
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

        {/* --- GHOST BROWSER CARD --- */}
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
              "I need to search: <b>{searchRequest}</b>"
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

        {/* --- IMAGE PROMPT CARD --- */}
        {promptToApprove && (
          <div style={{ 
            marginBottom: '15px', padding: '12px', 
            borderRadius: '8px', background: 'rgba(57, 216, 240, 0.1)', 
            border: '1px solid rgba(123, 219, 235, 0.3)',
            display: 'flex', flexDirection: 'column', gap: '8px'
          }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '12px', color: '#48cae4', fontWeight: 600 }}>
              <img src={iconIdea} style={{ width: '20px' }} alt="Net" />
              <span>Luna proposed an Image Generation</span>
            </div>
            <div style={{ fontSize: '11px', color: 'var(--text-secondary)', fontStyle: 'italic', background: 'rgba(0,0,0,0.2)', padding: '8px', borderRadius:'4px' }}>
              "{promptToApprove}"
            </div>
            <button 
              onClick={() => onExecuteGen && onExecuteGen(promptToApprove!)}
              style={{
                background: '#48cae4', color: 'white', border: 'none',
                padding: '8px 16px', borderRadius: '4px', cursor: 'pointer',
                fontSize: '12px', fontWeight: 'bold', alignSelf: 'flex-start',
                display: 'flex', alignItems: 'center', gap: '6px'
              }}
            >
              <span>Approve</span>
            </button>
          </div>
        )}

        {/* --- IMAGE GENERATION TRACKER --- */}
        {trackId && (
          <div style={{ 
            marginBottom: '15px', padding: '12px', 
            borderRadius: '8px', background: 'rgba(57, 216, 240, 0.1)', 
            border: '1px solid rgba(123, 219, 235, 0.3)',
            display: 'flex', flexDirection: 'column', gap: '8px'
          }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '12px', color: '#48cae4', fontWeight: 600 }}>
              <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" style={{animation: 'spin 2s linear infinite'}}>
                <path d="M21 12a9 9 0 1 1-6.219-8.56"/>
              </svg>
              <span>Luna is processing your image</span>
            </div>
            <div style={{ fontSize: '13px', color: 'var(--text-primary)' }}>
              "Generation initiated. Track progress in the decoder terminal."
            </div>
            <button 
              onClick={() => window.open(chrome.runtime.getURL(`luna_image.html?track=${trackId}`), '_blank', 'width=820,height=600')}
              style={{
                background: '#48cae4', color: 'white', border: 'none',
                padding: '6px 12px', borderRadius: '4px', cursor: 'pointer',
                fontSize: '11px', fontWeight: 'bold', alignSelf: 'flex-start'
              }}
            >
              Open Image Generator
            </button>
          </div>
        )}

        {/* --- FINAL MARKDOWN RENDERER --- */}
        <ReactMarkdown 
          remarkPlugins={[remarkGfm, remarkMath]} 
          rehypePlugins={[rehypeKatex]} 
          components={{
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