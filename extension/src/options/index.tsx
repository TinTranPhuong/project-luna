import { createRoot } from 'react-dom/client';

const Options = () => {
    return (
        <div style={{ padding: '20px' }}>
            <h1>Luna Settings</h1>
        </div>
    );
};

const container = document.createElement('div');
document.body.appendChild(container);
const root = createRoot(container);
root.render(<Options />);