import { useState, useCallback, useRef } from 'react';
import { Message } from '../components/Chat/MessageItem';
import { API_BASE_URL } from '../api'; 

export const useChat = (initialSessionId: number | null) => {
  /* --- STATE & REFS --- */
  const [messages, setMessages] = useState<Message[]>([]);
  const [loading, setLoading] = useState(false);
  const [sessionId, setSessionId] = useState<number | null>(initialSessionId);
  
  const abortControllerRef = useRef<AbortController | null>(null);

  /* --- ABORT HANDLERS --- */
  const stopGeneration = useCallback(() => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort(); 
      abortControllerRef.current = null;
      setLoading(false);
    }
  }, []);

  /* --- SILENT COMMAND EXECUTION (TOOLS/IMAGE GEN) --- */
  const executeGen = useCallback(async (prompt: string, mode: string = 'image_gen') => {
    setLoading(true);
    
    const aiMsgId = (Date.now() + 1).toString();
    const aiMsg: Message = { id: aiMsgId, role: 'assistant', content: "" }; 
    setMessages((prev) => [...prev, aiMsg]);
    
    abortControllerRef.current = new AbortController();

    try {
      const payload: any = { 
        message: `/execute_image ${prompt}`,
        use_rag: false,
        mode: mode 
      };
      
      if (sessionId) payload.session_id = sessionId;

      // USE CENTRALIZED URL
      const response = await fetch(`${API_BASE_URL}/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
        signal: abortControllerRef.current.signal
      });

      const newSessionId = response.headers.get("x-session-id");
      if (newSessionId) setSessionId(Number(newSessionId));

      if (!response.body) throw new Error("No response body");

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let aiText = "";

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        const chunk = decoder.decode(value, { stream: true });
        aiText += chunk;
        
        setMessages((prev) => 
          prev.map(msg => msg.id === aiMsgId ? { ...msg, content: aiText } : msg)
        );
      }
    } catch (error: unknown) { 
      //  SAFE ERROR NARROWING
      const isAbortError = error instanceof Error && error.name === 'AbortError';
      if (!isAbortError) {
        setMessages((prev) => 
            prev.map(msg => msg.id === aiMsgId ? { ...msg, content: "Error: Generation failed." } : msg)
        );
      }
    } finally {
      setLoading(false);
      abortControllerRef.current = null;
    }
  }, [sessionId]);

  /* --- STANDARD CHAT TRANSACTION --- */
  const sendMessage = useCallback(async (
    text: string, 
    useRag: boolean, 
    image?: string | null, 
    context?: string,
    mode: string = 'general' 
  ) => {
    
    /* --- CONTEXT & VISUAL PREPARATION --- */
    let displayContent = text;
    let payloadMessage = text;

    if (context) {
      const contextBlock = `Context:\n<details><summary>View Attached Page Content</summary>\n\n${context}\n\n</details>`;
      displayContent = `${contextBlock}\n\n${text}`;
      payloadMessage = `${contextBlock}\n\nQuestion: ${text}`;
    }

    if (image) {
      displayContent += "\n\n`[ Image Attached ]`";
    }

    /* --- OPTIMISTIC UI UPDATE --- */
    const userMsg: Message = { 
        id: Date.now().toString(), 
        role: 'user', 
        content: displayContent 
    };
    
    const aiMsgId = (Date.now() + 1).toString();
    const aiMsg: Message = { id: aiMsgId, role: 'assistant', content: "" }; 
    
    setMessages((prev) => [...prev, userMsg, aiMsg]);
    setLoading(true);

    abortControllerRef.current = new AbortController();

    try {
      /* --- API PAYLOAD CONSTRUCTION --- */
      const payload: any = { 
        message: payloadMessage,
        use_rag: useRag,
        image: image || null,
        mode: mode 
      };
      
      if (sessionId) payload.session_id = sessionId;

      // USE CENTRALIZED URL
      const response = await fetch(`${API_BASE_URL}/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
        signal: abortControllerRef.current.signal
      });

      const newSessionId = response.headers.get("x-session-id");
      if (newSessionId) {
          setSessionId(Number(newSessionId)); 
      }

      if (!response.body) throw new Error("No response body");

      /* --- STREAM EXTRACTION & RENDERING --- */
      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let aiText = "";

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        const chunk = decoder.decode(value, { stream: true });
        aiText += chunk;
        
        setMessages((prev) => 
          prev.map(msg => msg.id === aiMsgId ? { ...msg, content: aiText } : msg)
        );
      }

    } catch (error: unknown) { 
      // SAFE ERROR NARROWING
      const isAbortError = error instanceof Error && error.name === 'AbortError';
      if (isAbortError) {
        console.log("Generation stopped");
      } else {
        console.error(error);
        setMessages((prev) => 
            prev.map(msg => msg.id === aiMsgId ? { ...msg, content: "Error: Connection failed." } : msg)
        );
      }
    } finally {
      setLoading(false);
      abortControllerRef.current = null;
    }
  }, [sessionId]);

  /* --- SESSION DATA MANAGEMENT --- */
  const loadSession = useCallback(async (id: number) => {
    setLoading(true);
    setSessionId(id);
    try {
      // USE CENTRALIZED URL
      const res = await fetch(`${API_BASE_URL}/chat/history/${id}`);
      const data = await res.json();
      const uiMessages = data.map((msg: any) => ({
        id: msg.id.toString(),
        role: msg.role,
        content: msg.content
      }));
      setMessages(uiMessages);
    } catch (e) {
      console.error("Failed to load history", e);
    } finally {
      setLoading(false);
    }
  }, []);

  const clearChat = useCallback(() => {
    setSessionId(null);
    setMessages([]);
  }, []);

  return { messages, loading, sessionId, loadSession, sendMessage, clearChat, executeGen, stopGeneration };
};