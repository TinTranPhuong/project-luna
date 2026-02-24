import { useState, useEffect } from 'react';

export const useTheme = () => {
  /* --- INITIALIZATION UTILITIES --- */
  const getInitialTheme = () => {
    const saved = localStorage.getItem('theme');
    if (saved) return saved;
    return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
  };

  /* --- STATE --- */
  const [theme, setTheme] = useState(getInitialTheme);

  /* --- LIFECYCLE EFFECTS --- */
  useEffect(() => {
    document.body.setAttribute('data-theme', theme);
    localStorage.setItem('theme', theme);
  }, [theme]);

  /* --- ACTIONS --- */
  const toggleTheme = () => {
    setTheme((prev) => (prev === 'light' ? 'dark' : 'light'));
  };

  return { theme, toggleTheme };
};