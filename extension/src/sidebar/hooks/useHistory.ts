import { useState, useEffect, useCallback } from 'react';
import { API_BASE_URL } from '../api'; 

/* --- INTERFACES --- */
export interface Session {
  id: number;
  title: string;
  created_at: string;
}

export const useHistory = () => {
  /* --- STATE --- */
  const [sessions, setSessions] = useState<Session[]>([]);
  const [loading, setLoading] = useState(true);

  /* --- API TRANSACTIONS --- */
  const fetchSessions = useCallback(async () => {
    setLoading(true);
    try {
      // USE DYNAMIC TEMPLATE STRINGS
      const res = await fetch(`${API_BASE_URL}/chat/sessions`);
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
      await fetch(`${API_BASE_URL}/chat/sessions`, { method: 'DELETE' });
      setSessions([]);
    } catch (e) {
      console.error("Failed to wipe memory", e);
    }
  }, []);

  const deleteSession = useCallback(async (id: number) => {
    try {
      await fetch(`${API_BASE_URL}/chat/sessions/${id}`, { method: 'DELETE' });
      setSessions(prev => prev.filter(s => s.id !== id));
    } catch (e) {
      console.error("Failed to delete session", e);
    }
  }, []);

  /* --- LIFECYCLE --- */
  useEffect(() => {
    fetchSessions();
  }, [fetchSessions]);

  return { sessions, loading, fetchSessions, clearAllSessions, deleteSession };
};