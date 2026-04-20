class Toast {
    static show(message, type = 'info', duration = 3000) {
        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;
        toast.innerHTML = `
            <div class="toast-content">
                <span class="toast-icon">${this.getIcon(type)}</span>
                <span class="toast-message">${message}</span>
            </div>
        `;
        
        document.body.appendChild(toast);
        
        setTimeout(() => {
            toast.classList.add('toast-hide');
            setTimeout(() => toast.remove(), 300);
        }, duration);
    }
    
    static getIcon(type) {
        const icons = {
            success: '✅',
            error: '❌',
            warning: '⚠️',
            info: 'ℹ️'
        };
        return icons[type] || icons.info;
    }
}

// Modal dialog
class Modal {
    static show(title, content, buttons = []) {
        const modal = document.createElement('div');
        modal.className = 'modal-overlay';
        modal.innerHTML = `
            <div class="modal-container">
                <div class="modal-header">
                    <h3>${title}</h3>
                    <button class="modal-close">&times;</button>
                </div>
                <div class="modal-content">${content}</div>
                <div class="modal-footer">
                    ${buttons.map(btn => `
                        <button class="modal-btn ${btn.class || ''}" data-action="${btn.action}">
                            ${btn.text}
                        </button>
                    `).join('')}
                </div>
            </div>
        `;
        
        document.body.appendChild(modal);
        
        // Add styles
        const style = document.createElement('style');
        style.textContent = `
            .modal-overlay {
                position: fixed;
                top: 0;
                left: 0;
                right: 0;
                bottom: 0;
                background: rgba(0, 0, 0, 0.8);
                display: flex;
                align-items: center;
                justify-content: center;
                z-index: 2000;
                animation: fadeIn 0.3s ease;
            }
            
            .modal-container {
                background: var(--bg-card);
                border-radius: 15px;
                width: 90%;
                max-width: 500px;
                border: 1px solid var(--border-color);
                box-shadow: 0 10px 40px rgba(0, 0, 0, 0.5);
                animation: slideUp 0.3s ease;
            }
            
            .modal-header {
                padding: 20px;
                border-bottom: 1px solid var(--border-color);
                display: flex;
                justify-content: space-between;
                align-items: center;
            }
            
            .modal-header h3 {
                color: var(--text-primary);
                margin: 0;
            }
            
            .modal-close {
                background: transparent;
                border: none;
                color: var(--text-muted);
                font-size: 24px;
                cursor: pointer;
                padding: 0 5px;
            }
            
            .modal-close:hover {
                color: var(--error);
            }
            
            .modal-content {
                padding: 20px;
                color: var(--text-secondary);
            }
            
            .modal-footer {
                padding: 20px;
                border-top: 1px solid var(--border-color);
                display: flex;
                gap: 10px;
                justify-content: flex-end;
            }
            
            .modal-btn {
                padding: 8px 20px;
                border-radius: 8px;
                border: none;
                cursor: pointer;
                transition: all 0.3s ease;
            }
            
            .modal-btn.primary {
                background: var(--accent-gradient);
                color: white;
            }
            
            .modal-btn.secondary {
                background: transparent;
                border: 1px solid var(--border-color);
                color: var(--text-primary);
            }
            
            @keyframes slideUp {
                from {
                    opacity: 0;
                    transform: translateY(20px);
                }
                to {
                    opacity: 1;
                    transform: translateY(0);
                }
            }
        `;
        
        document.head.appendChild(style);
        
        // Handle close
        modal.querySelector('.modal-close').onclick = () => modal.remove();
        modal.onclick = (e) => {
            if (e.target === modal) modal.remove();
        };
        
        return modal;
    }
}

// Export to global
window.Toast = Toast;
window.Modal = Modal;