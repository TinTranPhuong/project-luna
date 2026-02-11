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

  // UPDATE: Added 'useRag' parameter
  const sendMessage = useCallback(async (text: string, useRag: boolean, context?: string) => {
    let displayContent = text;
    let payloadMessage = text;

    if (context) {
      const contextBlock = `Context:\n<details><summary>View Attached Page Content</summary>\n\n${context}\n\n</details>`;
      displayContent = `${contextBlock}\n\n${text}`;
      payloadMessage = `${contextBlock}\n\nQuestion: ${text}`;
    }

    const userMsg: Message = { id: Date.now().toString(), role: 'user', content: displayContent };
    const aiMsgId = (Date.now() + 1).toString();
    const aiMsg: Message = { id: aiMsgId, role: 'assistant', content: "" };
    
    setMessages((prev) => [...prev, userMsg, aiMsg]);
    setLoading(true);

    abortControllerRef.current = new AbortController();

    try {
      const payload: any = { 
        message: payloadMessage,
        use_rag: useRag // <--- Sending the Toggle State to Backend
      };
      if (sessionId) payload.session_id = sessionId;

      // UPDATE: Use 127.0.0.1 for reliability
      const response = await fetch('http://127.0.0.1:8000/api/v1/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
        signal: abortControllerRef.current.signal
      });

      const newSessionId = response.headers.get("x-session-id");
      if (newSessionId) {
          console.log("Chat Locked to Session:", newSessionId);
          setSessionId(Number(newSessionId)); 
      }

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
      if (error.name === 'AbortError') {
        console.log("Generation stopped");
      } else {
        console.error(error);
        setMessages((prev) => [...prev, { id: Date.now().toString(), role: 'assistant', content: "⚠️ Error: Server connection failed." }]);
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

  return { messages, loading, sessionId, loadSession, sendMessage, clearChat, stopGeneration };
};