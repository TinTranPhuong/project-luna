//import React from 'react';
import { createRoot } from 'react-dom/client';

const Sidebar = () => {
    return (
        <div style={{ padding: '20px', fontFamily: 'sans-serif' }}>
            <h1>Luna AI</h1>
            <p>System Online</p>
        </div>
    );
};

const container = document.createElement('div');
document.body.appendChild(container);
const root = createRoot(container);
root.render(<Sidebar />);