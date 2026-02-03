//import React from 'react';
import { createRoot } from 'react-dom/client';

const Popup = () => {
    return (
        <div style={{ width: '300px', padding: '10px' }}>
            <h2>Luna Quick Actions</h2>
        </div>
    );
};

const container = document.createElement('div');
document.body.appendChild(container);
const root = createRoot(container);
root.render(<Popup />);