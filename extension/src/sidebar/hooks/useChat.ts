import { useState, useCallback, useRef } from 'react';
import { Message } from '../components/Chat/MessageItem';

export const useChat = (initialSessionId: number | null) => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [loading, setLoading] = useState(false);
  const [sessionId, setSessionId] = useState<number | null>(initialSessionId);
  
  // Ref to control the "Stop" button
  const abortControllerRef = useRef<AbortController | null>(null);

  // --- STOP FUNCTION ---
  const stopGeneration = useCallback(() => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort(); 
      abortControllerRef.current = null;
      setLoading(false);
    }
  }, []);

  // --- SEND FUNCTION (Streaming) ---
  const sendMessage = useCallback(async (text: string, context?: string) => {
    let displayContent = text;
    let payloadMessage = text;

    if (context) {
      const contextBlock = `Context:\n<details><summary>View Attached Page Content</summary>\n\n${context}\n\n</details>`;
      displayContent = `${contextBlock}\n\n${text}`;
      payloadMessage = `${contextBlock}\n\nQuestion: ${text}`;
    }

    // 1. Add User Message
    const userMsg: Message = { id: Date.now().toString(), role: 'user', content: displayContent };
    
    // 2. Add Empty AI Message (Placeholder for streaming)
    const aiMsgId = (Date.now() + 1).toString();
    const aiMsg: Message = { id: aiMsgId, role: 'assistant', content: "" };
    
    setMessages((prev) => [...prev, userMsg, aiMsg]);
    setLoading(true);

    // 3. Prepare Abort Controller (For Stop Button)
    abortControllerRef.current = new AbortController();

    try {
      const payload: any = { message: payloadMessage };
      if (sessionId) payload.session_id = sessionId;

      const response = await fetch('http://localhost:8000/api/v1/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
        signal: abortControllerRef.current.signal // Connect the stop button
      });

      if (!response.body) throw new Error("No response body");

      // 4. READ THE STREAM
      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let aiText = "";

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        // Decode chunk and append to text
        const chunk = decoder.decode(value, { stream: true });
        aiText += chunk;

        // Update UI instantly
        setMessages((prev) => 
          prev.map(msg => msg.id === aiMsgId ? { ...msg, content: aiText } : msg)
        );
      }

    } catch (error: any) {
      if (error.name === 'AbortError') {
        console.log("Generation stopped by user");
        // Optional: Add a " [Stopped]" marker
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
      const res = await fetch(`http://localhost:8000/api/v1/chat/history/${id}`);
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

  