// src/content/handlers/snipper-handler.ts

export class SnipperHandler {
  private startX = 0;
  private startY = 0;
  private overlay: HTMLDivElement | null = null;
  private selectionBox: HTMLDivElement | null = null;

  constructor() {
    // Listen for the activation command
    chrome.runtime.onMessage.addListener((request) => {
      if (request.action === "ACTIVATE_SNIP") {
        this.createOverlay();
      }
    });
  }

  private createOverlay() {
    if (this.overlay) return;

    this.overlay = document.createElement('div');
    Object.assign(this.overlay.style, {
      position: 'fixed', top: '0', left: '0',
      width: '100vw', height: '100vh',
      backgroundColor: 'rgba(0, 0, 0, 0.3)',
      zIndex: '2147483647', cursor: 'crosshair'
    });

    this.selectionBox = document.createElement('div');
    Object.assign(this.selectionBox.style, {
      position: 'fixed', border: '2px solid #ff8fab',
      backgroundColor: 'rgba(255, 255, 255, 0.1)', display: 'none'
    });
    this.overlay.appendChild(this.selectionBox);

    this.overlay.addEventListener('mousedown', (e) => this.onMouseDown(e));
    document.body.appendChild(this.overlay);
  }

  private onMouseDown(e: MouseEvent) {
    this.startX = e.clientX;
    this.startY = e.clientY;

    if (this.selectionBox) {
      Object.assign(this.selectionBox.style, {
        left: `${this.startX}px`, top: `${this.startY}px`,
        width: '0px', height: '0px', display: 'block'
      });
    }

    const mouseMove = (ev: MouseEvent) => this.onMouseMove(ev);
    const mouseUp = (ev: MouseEvent) => {
      window.removeEventListener('mousemove', mouseMove);
      window.removeEventListener('mouseup', mouseUp);
      this.onMouseUp(ev);
    };

    window.addEventListener('mousemove', mouseMove);
    window.addEventListener('mouseup', mouseUp);
  }

  private onMouseMove(e: MouseEvent) {
    if (!this.selectionBox) return;
    const currentX = e.clientX;
    const currentY = e.clientY;

    const width = Math.abs(currentX - this.startX);
    const height = Math.abs(currentY - this.startY);
    const left = Math.min(currentX, this.startX);
    const top = Math.min(currentY, this.startY);

    Object.assign(this.selectionBox.style, {
      width: `${width}px`, height: `${height}px`,
      left: `${left}px`, top: `${top}px`
    });
  }

  private onMouseUp(_e: MouseEvent) {
    if (!this.selectionBox || !this.overlay) return;

    const rect = this.selectionBox.getBoundingClientRect();
    const cropData = {
      x: rect.left, y: rect.top,
      width: rect.width, height: rect.height,
      devicePixelRatio: window.devicePixelRatio
    };

    document.body.removeChild(this.overlay);
    this.overlay = null;
    this.selectionBox = null;

    if (rect.width > 5 && rect.height > 5) {
      chrome.runtime.sendMessage({ action: "SNIP_COMPLETED", cropData });
    }
  }
}