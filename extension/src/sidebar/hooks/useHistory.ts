import { useState, useEffect, useCallback } from 'react';

export interface Session {
  id: number;
  title: string;
  created_at: string;
}

export const useHistory = () => {
  const [sessions, setSessions] = useState<Session[]>([]);
  const [loading, setLoading] = useState(true);

  const fetchSessions = useCallback(async () => {
    setLoading(true);
    try {
      const res = await fetch('http://localhost:8000/api/v1/chat/sessions');
      const data = await res.json();
      setSessions(data);
    } catch (err) {
      console.error("Failed to load history:", err);
    } finally {
      setLoading(false);
    }
  }, []);

  const clearAllSessions = useCallback(async () => {
    try {
      await fetch('http://localhost:8000/api/v1/chat/sessions', { method: 'DELETE' });
      setSessions([]);
    } catch (e) {
      console.error("Failed to wipe memory", e);
    }
  }, []);

  // Initial load
  useEffect(() => {
    fetchSessions();
  }, [fetchSessions]);

  return { sessions, loading, fetchSessions, clearAllSessions };
};