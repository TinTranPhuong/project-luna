import React, { useEffect, useState } from 'react';
import { api } from '../../api';

import iconFolder from '../../../assets/icon_folder.png';
import iconTrash from '../../../assets/icon_trash.png';

/* --- INTERFACES & UTILITIES --- */
interface MemoryItem {
  id: string;
  text: string;
  metadata: any;
}

const groupBySource = (items: MemoryItem[]) => {
  const groups: Record<string, MemoryItem[]> = {};
  items.forEach(item => {
    const source = item.metadata?.source || "Unknown Source";
    if (!groups[source]) groups[source] = [];
    groups[source].push(item);
  });
  return groups;
};

export const MemoryViewer = () => {
  /* --- STATE MANAGEMENT --- */
  const [memories, setMemories] = useState<MemoryItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [expandedSources, setExpandedSources] = useState<Record<string, boolean>>({});

  const [editingId, setEditingId] = useState<string | null>(null);
  const [editText, setEditText] = useState("");
  const [isAdding, setIsAdding] = useState(false);
  const [newNote, setNewNote] = useState("");

  /* --- API TRANSACTIONS --- */
  const fetchBrain = async () => {
    setLoading(true);
    try {
      const data = await api.getMemories();
      setMemories(data);
    } catch (e) { 
      console.error(e); 
    } finally { 
      setLoading(false); 
    }
  };

  useEffect(() => { fetchBrain(); }, []);

  /* --- EVENT HANDLERS --- */
  const handleDelete = async (id: string) => {
    if(!confirm("Forget this memory forever?")) return;
    await api.deleteMemory(id);
    fetchBrain(); 
  };

  const handleDeleteFolder = async (e: React.MouseEvent, source: string, count: number) => {
    e.stopPropagation(); 
    if(!confirm(`WARNING: This will delete ALL ${count} memories from:\n\n${source}\n\nAre you sure?`)) return;
    
    await api.deleteSource(source);
    fetchBrain();
  };

  const startEdit = (mem: MemoryItem) => {
    setEditingId(mem.id);
    setEditText(mem.text);
  };

  const saveEdit = async (id: string) => {
    await api.updateMemory(id, editText);
    setEditingId(null);
    fetchBrain(); 
  };

  const saveNewNote = async () => {
    if(!newNote.trim()) return;
    await api.addMemory(newNote);
    setIsAdding(false);
    setNewNote("");
    fetchBrain(); 
  };

  const toggleFolder = (source: string) => {
    setExpandedSources(prev => ({ ...prev, [source]: !prev[source] }));
  };

  /* --- RENDER PREPARATION --- */
  const groupedMemories = groupBySource(memories);
  const sources = Object.keys(groupedMemories);

  return (
    <div className="memory-container">
      
      {/* --- COMPONENT HEADER --- */}
      <div className="memory-header">
        <h3>Memory Bank ({memories.length})</h3>
        <button 
          onClick={() => setIsAdding(!isAdding)}
          className="btn-primary"
          style={{ padding: '4px 10px', fontSize: '11px' }}
        >
          {isAdding ? 'Cancel' : '+ Add Note'}
        </button>
      </div>

      {/* --- ADD NEW MEMORY FORM --- */}
      {isAdding && (
        <div className="memory-add-form">
          <textarea 
            className="memory-input"
            value={newNote}
            onChange={(e) => setNewNote(e.target.value)}
            placeholder="Write a fact for Kyuna to remember..."
            rows={3}
          />
          <div style={{ marginTop: '8px', display: 'flex', justifyContent: 'flex-end' }}>
            <button onClick={saveNewNote} className="btn-primary" style={{ fontSize: '12px' }}>
              Save Memory
            </button>
          </div>
        </div>
      )}

      {/* --- MEMORY DIRECTORY --- */}
      {loading ? (
        <div className="history-empty">Scanning Neural Network...</div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
          {sources.map((source) => {
            const items = groupedMemories[source];
            const isExpanded = expandedSources[source];

            return (
              <div key={source} className="memory-folder">
                
                {/* --- FOLDER HEADER --- */}
                <div className="folder-header" onClick={() => toggleFolder(source)}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px', overflow: 'hidden', flex: 1 }}>
                    <img src={iconFolder} alt="Folder" style={{ width: '18px', height: '18px', opacity: 0.8 }} />
                    <span style={{ whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis', maxWidth: '160px' }}>
                      {source}
                    </span>
                    <span className="folder-count">{items.length}</span>
                  </div>

                  {/* CLEANED FOLDER TRASH BUTTON */}
                  <button 
                    className="trash-btn" 
                    onClick={(e) => handleDeleteFolder(e, source, items.length)}
                    title="Delete entire folder"
                  >
                    <img src={iconTrash} alt="Delete" style={{ width: '14px', height: '14px' }} />
                  </button>
                </div>

                {/* --- FOLDER CONTENT (MEMORIES) --- */}
                {isExpanded && (
                  <div className="folder-content">
                    {items.map((mem) => (
                      <div key={mem.id} className="memory-card">
                        
                        {editingId === mem.id ? (
                          
                          /* --- EDIT MODE --- */
                          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                            <textarea 
                              className="memory-input"
                              value={editText} 
                              onChange={(e) => setEditText(e.target.value)}
                              rows={4}
                            />
                            <div style={{ display: 'flex', gap: '6px' }}>
                              <button onClick={() => saveEdit(mem.id)} className="btn-small-primary" style={{ flex: 1 }}>Save</button>
                              <button onClick={() => setEditingId(null)} className="btn-small-cancel" style={{ flex: 1 }}>Cancel</button>
                            </div>
                          </div>
                        ) : (
                          
                          /* --- VIEW MODE --- */
                          <div>
                             <div className="memory-text">{mem.text}</div>                           
                             <div className="memory-meta">
                               <span>ID: {mem.id.slice(0, 6)}</span>
                               <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
                                 <button onClick={() => startEdit(mem)} className="action-btn btn-edit">Edit</button>
                                 
                                 {/* CLEANED SINGLE MEMORY TRASH BUTTON */}
                                 <button 
                                   className="trash-btn"
                                   onClick={() => handleDelete(mem.id)} 
                                   title="Delete Memory"
                                 >
                                   <img 
                                     src={iconTrash} 
                                     alt="Delete" 
                                     style={{ width: '12px', height: '12px'}} 
                                   />
                                 </button>
                               </div>
                             </div>
                          </div>
                        )}

                      </div>
                    ))}
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};