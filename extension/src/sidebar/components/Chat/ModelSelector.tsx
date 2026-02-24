import { useState, useRef, useEffect } from 'react';

/* --- TYPE DEFINITIONS --- */
export type AgentMode = 'general' | 'vision' | 'image_gen' | 'creative';

interface Props {
  currentMode: AgentMode;
  onSelect: (mode: AgentMode) => void;
}

export const ModelSelector = ({ currentMode, onSelect }: Props) => {
  const [isOpen, setIsOpen] = useState(false);
  const menuRef = useRef<HTMLDivElement>(null);

  /* --- OUTSIDE CLICK LISTENER --- */
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (menuRef.current && !menuRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  /* --- MENU CONFIGURATION --- */
  const options = [
    { 
      id: 'general', 
      label: 'General', 
      desc: 'Use for general question', 
      icon: <path d="M13 2L3 14h9l-1 8 10-12h-9l1-8z" /> 
    },
    { 
      id: 'creative', 
      label: 'Creative', 
      desc: 'Use for creative writting', 
      icon: <path d="M22 11v1a10 10 0 1 1-9-10 10 10 0 0 1 9 10zM12 2a10 10 0 0 0-10 10h20a10 10 0 0 0-10-10z" /> 
    },
    { 
      id: 'image_gen', 
      label: 'Image', 
      desc: 'Use for image creation', 
      icon: <path d="M20 2H4c-1.1 0-2 .9-2 2v12c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2zM5 14l3.5-4.5 2.5 3.01L14.5 8l4.5 6H5z" /> 
    }
  ];

  const currentOpt = options.find(o => o.id === currentMode) || options[0];

  return (
    <div ref={menuRef} style={{ position: 'relative', zIndex: 200 }}>
      
      {/* --- TRIGGER BUTTON --- */}
      <button 
        onClick={() => setIsOpen(!isOpen)}
        style={{
          display: 'flex', alignItems: 'center', gap: '6px',
          background: 'transparent',
          border: '1px solid transparent',
          color: 'var(--text-secondary)', 
          padding: '6px 10px', borderRadius: '8px', cursor: 'pointer',
          fontWeight: 600, fontSize: '13px', transition: 'all 0.2s'
        }}
        onMouseEnter={(e) => {
            e.currentTarget.style.color = 'var(--text-primary)';
            e.currentTarget.style.background = 'rgba(0,0,0,0.03)';
        }}
        onMouseLeave={(e) => {
            e.currentTarget.style.color = 'var(--text-secondary)';
            e.currentTarget.style.background = 'transparent';
        }}
      >
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          {currentOpt.icon}
        </svg>
        <span>{currentOpt.label}</span>
        <span style={{ fontSize: '10px', opacity: 0.5 }}>▼</span>
      </button>

      {/* --- DROPDOWN MENU --- */}
      {isOpen && (
        <div style={{
          position: 'absolute', 
          bottom: '120%', 
          right: 0,       
          width: '200px',
          backgroundColor: 'var(--header-bg)',
          border: 'var(--header-border)',
          borderRadius: '12px',
          boxShadow: '0 -4px 20px rgba(0,0,0,0.15)', 
          padding: '6px',
          display: 'flex', flexDirection: 'column', gap: '2px',
          backdropFilter: 'blur(10px)',
          zIndex: 1000
        }}>
          {options.map((opt) => {
            const isSelected = currentMode === opt.id;
            return (
              <div 
                key={opt.id}
                onClick={() => { onSelect(opt.id as AgentMode); setIsOpen(false); }}
                style={{
                  display: 'flex', alignItems: 'center', gap: '10px',
                  padding: '10px', borderRadius: '8px', cursor: 'pointer',
                  background: isSelected ? 'rgba(56, 189, 248, 0.1)' : 'transparent',
                  transition: 'background 0.2s'
                }}
                onMouseEnter={(e) => {
                    if(!isSelected) e.currentTarget.style.background = 'rgba(0,0,0,0.04)';
                }}
                onMouseLeave={(e) => {
                    if(!isSelected) e.currentTarget.style.background = 'transparent';
                }}
              >
                
                {/* ICON RENDERER */}
                <div style={{ 
                  color: isSelected ? '#38bdf8' : 'var(--text-secondary)',
                  display: 'flex', alignItems: 'center', justifyContent: 'center'
                }}>
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                    {opt.icon}
                  </svg>
                </div>

                {/* TEXT METADATA */}
                <div style={{ display: 'flex', flexDirection: 'column', flex: 1 }}>
                  <span style={{ 
                      color: 'var(--text-primary)', 
                      fontSize: '13px', fontWeight: 600 
                  }}>
                    {opt.label}
                  </span>
                  <span style={{ 
                      color: 'var(--text-secondary)', 
                      fontSize: '11px' 
                  }}>
                    {opt.desc}
                  </span>
                </div>

                {/* SELECTION INDICATOR */}
                {isSelected && (
                  <div style={{ color: '#38bdf8', fontSize: '14px', fontWeight: 'bold' }}>✓</div>
                )}
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};