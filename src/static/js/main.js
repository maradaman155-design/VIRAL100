// ARQV30 Enhanced v2.0 - Main JavaScript
console.log('🚀 ARQV30 Enhanced v2.0 - Main JS carregado');

// Sistema de alertas
function showAlert(message, type = 'info') {
    const alert = document.createElement('div');
    alert.className = `alert alert-${type}`;
    alert.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 15px 20px;
        background: var(--bg-surface, #ffffff);
        border: 1px solid var(--border-color, #e0e0e0);
        border-radius: 8px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        z-index: 10000;
        max-width: 400px;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    `;

    const colors = {
        info: '#2196F3',
        success: '#4CAF50',
        warning: '#FF9800',
        error: '#F44336'
    };

    alert.style.borderLeftColor = colors[type] || colors.info;
    alert.style.borderLeftWidth = '4px';

    alert.innerHTML = `
        <div style="display: flex; align-items: center; gap: 10px;">
            <span style="color: ${colors[type] || colors.info}; font-size: 18px;">
                ${type === 'success' ? '✅' : type === 'error' ? '❌' : type === 'warning' ? '⚠️' : 'ℹ️'}
            </span>
            <span>${message}</span>
        </div>
    `;

    document.body.appendChild(alert);

    setTimeout(() => {
        if (alert.parentNode) {
            alert.remove();
        }
    }, 5000);
}

// Sistema de loading
function showLoading(message = 'Carregando...') {
    const loading = document.createElement('div');
    loading.id = 'loadingOverlay';
    loading.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(0,0,0,0.7);
        display: flex;
        align-items: center;
        justify-content: center;
        z-index: 9999;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    `;

    loading.innerHTML = `
        <div style="background: white; padding: 30px; border-radius: 12px; text-align: center; box-shadow: 0 8px 32px rgba(0,0,0,0.3);">
            <div style="width: 40px; height: 40px; border: 4px solid #f3f3f3; border-top: 4px solid #2196F3; border-radius: 50%; animation: spin 1s linear infinite; margin: 0 auto 20px;"></div>
            <div style="font-size: 16px; color: #333;">${message}</div>
        </div>
        <style>
            @keyframes spin {
                0% { transform: rotate(0deg); }
                100% { transform: rotate(360deg); }
            }
        </style>
    `;

    document.body.appendChild(loading);
    return loading;
}

function hideLoading() {
    const loading = document.getElementById('loadingOverlay');
    if (loading) {
        loading.remove();
    }
}

// Funções utilitárias
function formatCurrency(value) {
    return new Intl.NumberFormat('pt-BR', {
        style: 'currency',
        currency: 'BRL'
    }).format(value);
}

function formatDate(date) {
    return new Intl.DateTimeFormat('pt-BR').format(new Date(date));
}

// Sistema de cópia para clipboard
function copyToClipboard(text) {
    if (navigator.clipboard) {
        navigator.clipboard.writeText(text).then(() => {
            showAlert('Copiado para área de transferência!', 'success');
        }).catch(() => {
            fallbackCopyTextToClipboard(text);
        });
    } else {
        fallbackCopyTextToClipboard(text);
    }
}

function fallbackCopyTextToClipboard(text) {
    const textArea = document.createElement("textarea");
    textArea.value = text;
    textArea.style.top = "0";
    textArea.style.left = "0";
    textArea.style.position = "fixed";

    document.body.appendChild(textArea);
    textArea.focus();
    textArea.select();

    try {
        document.execCommand('copy');
        showAlert('Copiado para área de transferência!', 'success');
    } catch (err) {
        showAlert('Erro ao copiar texto', 'error');
    }

    document.body.removeChild(textArea);
}

// Sistema de validação de formulários
function validateForm(formId) {
    const form = document.getElementById(formId);
    if (!form) return false;

    const requiredFields = form.querySelectorAll('[required]');
    let isValid = true;

    requiredFields.forEach(field => {
        if (!field.value.trim()) {
            field.style.borderColor = '#F44336';
            isValid = false;
        } else {
            field.style.borderColor = '';
        }
    });

    return isValid;
}

function getSessionId() {
    let sessionId = sessionStorage.getItem('arqv30_session_id');

    if (!sessionId) {
        sessionId = `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
        sessionStorage.setItem('arqv30_session_id', sessionId);
    }

    return sessionId;
}

// Sistema de progresso corrigido
async function startProgressTracking(sessionId) {
    try {
        const response = await fetch('/api/progress/start_tracking', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ session_id: sessionId })
        });

        const result = await response.json();

        if (result.success) {
            console.log('✅ Progress tracking iniciado:', sessionId);
            return true;
        } else {
            console.error('❌ Erro ao iniciar tracking:', result.error);
            return false;
        }
    } catch (error) {
        console.error('❌ Erro no progress tracking:', error);
        return false;
    }
}

async function getProgressStatus(sessionId) {
    try {
        const response = await fetch(`/api/progress/get_progress/${sessionId}`);

        if (response.ok) {
            const result = await response.json();
            return result.progress;
        } else {
            console.error('❌ Erro ao obter progresso:', response.status);
            return null;
        }
    } catch (error) {
        console.error('❌ Erro ao obter progresso:', error);
        return null;
    }
}

async function removeFile(fileId) {
    try {
        const response = await fetch(`/api/remove_attachment/${fileId}`, {
            method: 'DELETE'
        });

        const result = await response.json();

        if (result.success) {
            const fileItem = document.querySelector(`[onclick="removeFile('${fileId}')"]`).parentNode;
            fileItem.remove();
            showAlert('Arquivo removido com sucesso!', 'success');
        } else {
            throw new Error(result.error || 'Erro ao remover arquivo');
        }

    } catch (error) {
        console.error('Erro ao remover arquivo:', error);
        showAlert(`Erro ao remover arquivo: ${error.message}`, 'error');
    }
}

// Inicialização quando DOM estiver pronto
document.addEventListener('DOMContentLoaded', function() {
    console.log('🎯 DOM carregado - Iniciando ARQV30');

    // Adiciona handlers globais
    document.addEventListener('keydown', function(e) {
        // ESC para fechar modais
        if (e.key === 'Escape') {
            const modals = document.querySelectorAll('.modal, .modal-enhanced');
            modals.forEach(modal => {
                if (modal.style.display !== 'none') {
                    modal.style.display = 'none';
                }
            });
        }
    });

    // Adiciona botões de cópia automática
    document.querySelectorAll('[data-copy]').forEach(element => {
        element.addEventListener('click', function() {
            const text = this.dataset.copy || this.textContent;
            copyToClipboard(text);
        });
    });
});

// Inicialização
document.addEventListener('DOMContentLoaded', function() {
    console.log('📁 Inicializando sistema de upload');
    // FileUploadManager será inicializado pelo upload.js

    console.log('🔬 Inicializando sistema de análise');
    // AnalysisManager será inicializado pelo analysis.js
});

// Exposição de funções globais
window.showAlert = showAlert;
window.showLoading = showLoading;
window.hideLoading = hideLoading;
window.copyToClipboard = copyToClipboard;
window.validateForm = validateForm;
window.formatCurrency = formatCurrency;
window.formatDate = formatDate;

// Exposição de funções globais
window.removeFile = removeFile;
window.handleFiles = handleFiles;
window.startProgressTracking = startProgressTracking;
window.getProgressStatus = getProgressStatus;