import { useState, useCallback } from 'react';
import { Message } from '../components/Chat/MessageItem';

export const useChat = (initialSessionId: number | null) => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [loading, setLoading] = useState(false);
  const [sessionId, setSessionId] = useState<number | null>(initialSessionId);

  // Load a specific session
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

  // Send a message
  const sendMessage = useCallback(async (text: string, context?: string) => {
    let displayContent = text;
    let payloadMessage = text;

    // Handle Context Attachment
    if (context) {
      const contextBlock = `Context:\n<details><summary>📄 View Attached Page Content</summary>\n\n${context}\n\n</details>`;
      displayContent = `${contextBlock}\n\n${text}`;
      payloadMessage = `${contextBlock}\n\nQuestion: ${text}`;
    }

    // Optimistic Update
    const userMsg: Message = { id: Date.now().toString(), role: 'user', content: displayContent };
    setMessages((prev) => [...prev, userMsg]);
    setLoading(true);

    try {
      const payload: any = { message: payloadMessage };
      if (sessionId) payload.session_id = sessionId;

      const response = await fetch('http://localhost:8000/api/v1/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });

      const data = await response.json();

      // If new session, update state
      if (!sessionId && data.session_id) {
        setSessionId(data.session_id);
      }

      const aiMsg: Message = { id: (Date.now() + 1).toString(), role: 'assistant', content: data.response };
      setMessages((prev) => [...prev, aiMsg]);
      
      return data.session_id; // Return ID so UI knows if a new chat started
    } catch (error) {
      console.error(error);
      setMessages((prev) => [...prev, { id: Date.now().toString(), role: 'assistant', content: "⚠️ Error: Server offline." }]);
    } finally {
      setLoading(false);
    }
  }, [sessionId]);

  const clearChat = useCallback(() => {
    setSessionId(null);
    setMessages([]);
  }, []);

  return { messages, loading, sessionId, loadSession, sendMessage, clearChat };
};