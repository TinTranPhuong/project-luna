const API_URL = 'http://127.0.0.1:8000/api/v1';

export const api = {
  // 1. Existing Teach Command
  ingestUrl: (url: string) => 
    fetch(`${API_URL}/memory/ingest`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ url, text: "" })
    }),

  // 2. Existing Clear Cache
  clearCache: () => 
    fetch(`${API_URL}/memory/cache`, { 
      method: 'DELETE' 
    }),

  // 3. Existing Get Memories
  getMemories: async () => {
    const res = await fetch(`${API_URL}/memory/all?limit=100`);
    return res.json();
  },

  // 4. Delete Command (Fixes the first red line)
  deleteMemory: (id: string) => 
    fetch(`${API_URL}/memory/${id}`, { method: 'DELETE' }),

  // 5. Update Command (Fixes the second red line)
  updateMemory: (id: string, text: string) =>
    fetch(`${API_URL}/memory/${id}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text })
    }),
    
  // 6. Add Note Command (Fixes the third red line)
  addMemory: (text: string) => 
    fetch(`${API_URL}/memory/ingest`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ url: "User Manual", text: text }) 
    }),

  // 7. Delete Folder Command
  deleteSource: (source: string) => 
    fetch(`${API_URL}/memory/source?source=${encodeURIComponent(source)}`, { 
      method: 'DELETE' 
    }),
};