/* ==========================================================================
   GLOBAL CONFIGURATION
   ========================================================================== */
export const API_BASE_URL = 'http://127.0.0.1:8000/api/v1';

export const api = {
  /* --- KNOWLEDGE BASE (RAG) --- */
  ingestUrl: (url: string) => 
    fetch(`${API_BASE_URL}/memory/ingest`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ url, text: "" })
    }),

  clearCache: () => 
    fetch(`${API_BASE_URL}/memory/cache`, { 
      method: 'DELETE' 
    }),

  /* --- MEMORY MANAGEMENT --- */
  getMemories: async () => {
    const res = await fetch(`${API_BASE_URL}/memory/all?limit=100`);
    return res.json();
  },

  addMemory: (text: string) => 
    fetch(`${API_BASE_URL}/memory/ingest`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ url: "User Manual", text: text }) 
    }),

  updateMemory: (id: string, text: string) =>
    fetch(`${API_BASE_URL}/memory/${id}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text })
    }),

  deleteMemory: (id: string) => 
    fetch(`${API_BASE_URL}/memory/${id}`, { method: 'DELETE' }),

  deleteSource: (source: string) => 
    fetch(`${API_BASE_URL}/memory/source?source=${encodeURIComponent(source)}`, { 
      method: 'DELETE' 
    }),

  /* --- CHAT ENGINE --- */
  chat: async (message: string, sessionId: number | null, useRag: boolean, image?: string | null) => {
    const response = await fetch(`${API_BASE_URL}/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ 
        message, 
        session_id: sessionId, 
        use_rag: useRag,
        image: image 
      })
    });
    
    if (!response.body) throw new Error("No response body");
    return response.body.getReader();
  },
};