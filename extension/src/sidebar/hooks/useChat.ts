import { useState, useCallback, useRef } from 'react';
import { Message } from '../components/Chat/MessageItem';

export const useChat = (initialSessionId: number | null) => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [loading, setLoading] = useState(false);
  const [sessionId, setSessionId] = useState<number | null>(initialSessionId);
  
  const abortControllerRef = useRef<AbortController | null>(null);

  const stopGeneration = useCallback(() => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort(); 
      abortControllerRef.current = null;
      setLoading(false);
    }
  }, []);

  // Triggers the backend execution command quietly without adding a user bubble
  const executeGen = useCallback(async (prompt: string, mode: string = 'image_gen') => {
    setLoading(true);
    
    // Create an empty AI message bubble to stream the response into
    const aiMsgId = (Date.now() + 1).toString();
    const aiMsg: Message = { id: aiMsgId, role: 'assistant', content: "" }; 
    setMessages((prev) => [...prev, aiMsg]);
    
    abortControllerRef.current = new AbortController();

    try {
      const payload: any = { 
        message: `/execute_image ${prompt}`, // Special command
        use_rag: false,
        mode: mode 
      };
      if (sessionId) payload.session_id = sessionId;

      const response = await fetch('http://127.0.0.1:8000/api/v1/chat', {
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
    } catch (error: any) {
      if (error.name !== 'AbortError') {
        setMessages((prev) => 
            prev.map(msg => msg.id === aiMsgId ? { ...msg, content: "Error: Generation failed." } : msg)
        );
      }
    } finally {
      setLoading(false);
      abortControllerRef.current = null;
    }
  }, [sessionId]);

  // Added 'mode' as the last argument
  const sendMessage = useCallback(async (
    text: string, 
    useRag: boolean, 
    image?: string | null, 
    context?: string,
    mode: string = 'general' 
  ) => {
    
    // 1. Prepare Visuals
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

    // 2. Optimistic Update
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
      // 3. Construct Payload
      const payload: any = { 
        message: payloadMessage,
        use_rag: useRag,
        image: image || null,
        mode: mode 
      };
      
      if (sessionId) payload.session_id = sessionId;

      const response = await fetch('http://127.0.0.1:8000/api/v1/chat', {
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

      // 4. Handle Streaming
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

    } catch (error: any) {
      if (error.name === 'AbortError') {
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

  const loadSession = useCallback(async (id: number) => {
    setLoading(true);
    setSessionId(id);
    try {
      const res = await fetch(`http://127.0.0.1:8000/api/v1/chat/history/${id}`);
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