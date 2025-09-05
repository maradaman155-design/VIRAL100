// ARQV30 Enhanced v3.0 - Sistema de Análise Moderno
// Estado global da aplicação APRIMORADO
let currentAnalysisId = null;
let analysisResults = null;
let isAnalysisRunning = false;
let savedSessions = new Map();
let autoSaveInterval = null;

// Sistema de persistência local
class AnalysisPersistence {
    constructor() {
        this.storageKey = 'arqv30_analyses';
        this.loadSavedSessions();
    }

    saveSessions() {
        try {
            const sessionsObj = Object.fromEntries(savedSessions);
            localStorage.setItem(this.storageKey, JSON.stringify(sessionsObj));
            console.log('✅ Sessões salvas localmente');
        } catch (error) {
            console.error('❌ Erro ao salvar sessões:', error);
        }
    }

    loadSavedSessions() {
        try {
            const stored = localStorage.getItem(this.storageKey);
            if (stored) {
                const sessionsObj = JSON.parse(stored);
                savedSessions = new Map(Object.entries(sessionsObj));
                console.log(`✅ ${savedSessions.size} sessões carregadas`);
                this.updateSessionsList();
            }
        } catch (error) {
            console.error('❌ Erro ao carregar sessões:', error);
            savedSessions = new Map();
        }
    }

    saveSession(sessionId, data) {
        savedSessions.set(sessionId, {
            ...data,
            lastSaved: new Date().toISOString(),
            progress: data.progress || 0
        });
        this.saveSessions();
        this.updateSessionsList();
    }

    getSession(sessionId) {
        return savedSessions.get(sessionId);
    }

    deleteSession(sessionId) {
        savedSessions.delete(sessionId);
        this.saveSessions();
        this.updateSessionsList();
    }

    updateSessionsList() {
        const container = document.getElementById('saved-sessions');
        if (!container) return;

        if (savedSessions.size === 0) {
            container.innerHTML = '<p class="text-muted">Nenhuma análise salva</p>';
            return;
        }

        const sessionsHtml = Array.from(savedSessions.entries())
            .sort((a, b) => new Date(b[1].lastSaved) - new Date(a[1].lastSaved))
            .map(([sessionId, data]) => {
                const progress = data.progress || 0;
                const status = progress === 100 ? 'Concluída' :
                              progress > 0 ? `Em andamento (${progress}%)` : 'Iniciada';

                return `
                    <div class="session-item p-3 border rounded mb-2">
                        <div class="d-flex justify-content-between align-items-start">
                            <div>
                                <h6 class="mb-1">${data.projeto || 'Análise'}</h6>
                                <small class="text-muted">
                                    Segmento: ${data.segmento || 'N/A'} •
                                    ${new Date(data.lastSaved).toLocaleString()}
                                </small>
                                <div class="mt-1">
                                    <span class="badge ${progress === 100 ? 'bg-success' : progress > 0 ? 'bg-warning' : 'bg-secondary'}">
                                        ${status}
                                    </span>
                                </div>
                            </div>
                            <div class="btn-group btn-group-sm">
                                <button class="btn btn-outline-primary" onclick="continueAnalysis('${sessionId}')">
                                    ${progress === 100 ? 'Ver' : 'Continuar'}
                                </button>
                                <button class="btn btn-outline-danger" onclick="deleteAnalysis('${sessionId}')">
                                    <i class="bi bi-trash"></i>
                                </button>
                            </div>
                        </div>
                        ${progress > 0 ? `
                            <div class="progress mt-2" style="height: 4px;">
                                <div class="progress-bar" style="width: ${progress}%"></div>
                            </div>
                        ` : ''}
                    </div>
                `;
            }).join('');

        container.innerHTML = sessionsHtml;
    }
}

const persistence = new AnalysisPersistence();

class ModernAnalysisSystem {
    constructor() {
        this.currentSessionId = null;
        this.progressInterval = null;
        this.sessions = new Map();
        this.isPaused = false;
        this.notifications = [];

        this.init();
    }

    init() {
        console.log('🔬 Sistema de Análise Moderno carregado');

        // Configura observers para animações
        this.setupAnimationObservers();

        // Carrega sessões salvas
        this.loadSavedSessions();

        // Event listeners
        this.setupEventListeners();

        // Restaura último progresso se existir
        this.restoreLastSession();

        // Configura auto-save
        this.setupAutoSave();
    }

    setupAnimationObservers() {
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('animate');
                }
            });
        }, {
            threshold: 0.1,
            rootMargin: '0px 0px -50px 0px'
        });

        // Observa elementos com animação
        document.querySelectorAll('.animate-on-scroll').forEach(el => {
            observer.observe(el);
        });
    }

    setupEventListeners() {
        // Formulário principal
        const analyzeForm = document.getElementById('analysisForm');
        if (analyzeForm) {
            analyzeForm.addEventListener('submit', (e) => {
                e.preventDefault();
                this.startAnalysis();
            });
        }

        // Botões de controle
        this.setupControlButtons();

        // Upload de arquivos
        this.setupFileUpload();

        // Atalhos de teclado
        this.setupKeyboardShortcuts();

        // Auto-resize de textareas
        this.setupTextareaResize();
    }

    setupControlButtons() {
        const buttons = {
            'pauseBtn': () => this.pauseSession(),
            'resumeBtn': () => this.resumeSession(),
            'saveBtn': () => this.saveSession(),
            'refreshSessionsBtn': () => this.loadSavedSessions(),
            'clearSessionsBtn': () => this.clearAllSessions()
        };

        Object.entries(buttons).forEach(([id, handler]) => {
            const btn = document.getElementById(id);
            if (btn) {
                btn.addEventListener('click', handler);
            }
        });
    }

    setupFileUpload() {
        const fileInput = document.getElementById('fileInput');
        const dropZone = document.getElementById('dropZone');

        if (fileInput && dropZone) {
            // Drag and drop
            dropZone.addEventListener('dragover', (e) => {
                e.preventDefault();
                dropZone.classList.add('drag-over');
            });

            dropZone.addEventListener('dragleave', () => {
                dropZone.classList.remove('drag-over');
            });

            dropZone.addEventListener('drop', (e) => {
                e.preventDefault();
                dropZone.classList.remove('drag-over');
                const files = Array.from(e.dataTransfer.files);
                this.handleFiles(files);
            });

            // Click upload
            dropZone.addEventListener('click', () => fileInput.click());
            fileInput.addEventListener('change', (e) => {
                const files = Array.from(e.target.files);
                this.handleFiles(files);
            });
        }
    }

    handleFiles(files) {
        files.forEach(file => {
            if (this.validateFile(file)) {
                this.uploadFile(file);
            }
        });
    }

    validateFile(file) {
        const maxSize = 10 * 1024 * 1024; // 10MB
        const allowedTypes = [
            'application/pdf',
            'text/plain',
            'application/msword',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        ];

        if (file.size > maxSize) {
            this.showNotification('Arquivo muito grande. Máximo 10MB.', 'warning');
            return false;
        }

        if (!allowedTypes.includes(file.type)) {
            this.showNotification('Tipo de arquivo não suportado.', 'warning');
            return false;
        }

        return true;
    }

    async uploadFile(file) {
        const formData = new FormData();
        formData.append('file', file);

        try {
            const response = await fetch('/api/upload', {
                method: 'POST',
                body: formData
            });

            const result = await response.json();

            if (result.success) {
                this.showNotification(`Arquivo ${file.name} enviado com sucesso!`, 'success');
                this.addFileToList(file, result.file_id);
            } else {
                this.showNotification(`Erro no upload: ${result.error}`, 'error');
            }
        } catch (error) {
            this.showNotification(`Erro no upload: ${error.message}`, 'error');
        }
    }

    setupKeyboardShortcuts() {
        document.addEventListener('keydown', (e) => {
            // Ctrl+Enter para submeter
            if (e.ctrlKey && e.key === 'Enter') {
                e.preventDefault();
                this.startAnalysis();
            }

            // Escape para fechar notificações
            if (e.key === 'Escape') {
                this.clearNotifications();
            }

            // Alt+P para pausar/resumir
            if (e.altKey && e.key === 'p') {
                e.preventDefault();
                if (this.isPaused) {
                    this.resumeSession();
                } else {
                    this.pauseSession();
                }
            }
        });
    }

    setupTextareaResize() {
        document.querySelectorAll('textarea').forEach(textarea => {
            textarea.addEventListener('input', () => {
                textarea.style.height = 'auto';
                textarea.style.height = textarea.scrollHeight + 'px';
            });
        });
    }

    setupAutoSave() {
        const form = document.getElementById('analysisForm');
        if (form) {
            // Auto-save a cada 30 segundos
            setInterval(() => {
                this.autoSaveForm();
            }, 30000);

            // Save on form change
            form.addEventListener('change', () => {
                setTimeout(() => this.autoSaveForm(), 1000);
            });
        }
    }

    autoSaveForm() {
        const form = document.getElementById('analysisForm');
        if (!form) return;

        const formData = new FormData(form);
        const data = Object.fromEntries(formData.entries());

        localStorage.setItem('analysisFormData', JSON.stringify(data));
        this.showNotification('Formulário salvo automaticamente', 'info', 2000);
    }

    restoreFormData() {
        const savedData = localStorage.getItem('analysisFormData');
        if (savedData) {
            try {
                const data = JSON.parse(savedData);
                Object.entries(data).forEach(([key, value]) => {
                    const input = document.querySelector(`[name="${key}"]`);
                    if (input) {
                        input.value = value;
                    }
                });
            } catch (error) {
                console.error('Erro ao restaurar dados do formulário:', error);
            }
        }
    }

    async startAnalysis() {
        const form = document.getElementById('analysisForm');
        if (!form) {
            this.showNotification('Formulário não encontrado', 'error');
            return;
        }

        // Validação do formulário
        if (!this.validateForm()) {
            return;
        }

        const formData = new FormData(form);
        const data = Object.fromEntries(formData.entries());

        try {
            this.showProgress(true);
            this.updateProgress(0, 'Iniciando análise...');

            // Envia análise
            const response = await fetch('/api/execute_complete_analysis', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(data)
            });

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            const result = await response.json();

            if (result.success) {
                this.currentSessionId = result.session_id;
                this.showNotification(`Análise iniciada! Sessão: ${result.session_id}`, 'success');

                // Salva sessão no localStorage
                localStorage.setItem('currentSessionId', this.currentSessionId);

                // Inicia monitoramento
                this.startProgressMonitoring();

            } else {
                throw new Error(result.error || 'Erro desconhecido');
            }

        } catch (error) {
            console.error('Erro na análise:', error);
            this.showNotification(`Erro na análise: ${error.message}`, 'error');
            this.showProgress(false);
        }
    }

    validateForm() {
        const segmento = document.querySelector('[name="segmento"]');

        if (!segmento || !segmento.value.trim()) {
            this.showNotification('Por favor, preencha o segmento', 'warning');
            if (segmento) segmento.focus();
            return false;
        }

        if (segmento.value.trim().length < 3) {
            this.showNotification('Segmento deve ter pelo menos 3 caracteres', 'warning');
            if (segmento) segmento.focus();
            return false;
        }

        return true;
    }

    async pauseSession() {
        if (!this.currentSessionId) {
            this.showNotification('Nenhuma sessão ativa para pausar', 'warning');
            return;
        }

        try {
            const response = await fetch(`/api/sessions/${this.currentSessionId}/pause`, {
                method: 'POST'
            });

            const result = await response.json();

            if (result.success) {
                this.isPaused = true;
                this.stopProgressMonitoring();
                this.showNotification('Sessão pausada com sucesso', 'success');
                this.updateSessionControls('paused');
            } else {
                throw new Error(result.error);
            }

        } catch (error) {
            this.showNotification(`Erro ao pausar: ${error.message}`, 'error');
        }
    }

    async resumeSession() {
        if (!this.currentSessionId) {
            this.showNotification('Nenhuma sessão para resumir', 'warning');
            return;
        }

        try {
            const response = await fetch(`/api/sessions/${this.currentSessionId}/resume`, {
                method: 'POST'
            });

            const result = await response.json();

            if (result.success) {
                this.isPaused = false;
                this.startProgressMonitoring();
                this.showNotification('Sessão resumida com sucesso', 'success');
                this.updateSessionControls('running');
            } else {
                throw new Error(result.error);
            }

        } catch (error) {
            this.showNotification(`Erro ao resumir: ${error.message}`, 'error');
        }
    }

    async saveSession() {
        if (!this.currentSessionId) {
            this.showNotification('Nenhuma sessão para salvar', 'warning');
            return;
        }

        try {
            const response = await fetch(`/api/sessions/${this.currentSessionId}/save`, {
                method: 'POST'
            });

            const result = await response.json();

            if (result.success) {
                this.showNotification('Sessão salva com sucesso', 'success');
                await this.loadSavedSessions();
            } else {
                throw new Error(result.error);
            }

        } catch (error) {
            this.showNotification(`Erro ao salvar: ${error.message}`, 'error');
        }
    }

    async continueSession(sessionId) {
        try {
            this.showProgress(true);
            this.updateProgress(0, 'Continuando sessão...');

            const response = await fetch(`/api/sessions/${sessionId}/continue`, {
                method: 'POST'
            });

            const result = await response.json();

            if (result.success) {
                this.currentSessionId = sessionId;
                localStorage.setItem('currentSessionId', sessionId);

                this.showNotification('Sessão continuada com sucesso', 'success');
                this.startProgressMonitoring();

            } else {
                throw new Error(result.error);
            }

        } catch (error) {
            this.showNotification(`Erro ao continuar: ${error.message}`, 'error');
            this.showProgress(false);
        }
    }

    async loadSavedSessions() {
        try {
            // Primeiro tenta o endpoint principal
            let response = await fetch('/api/progress/sessions');

            if (!response.ok) {
                // Fallback para endpoint alternativo
                response = await fetch('/api/user/sessions');
            }

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            const result = await response.json();

            if (result.success && result.sessions) {
                this.sessions.clear();
                result.sessions.forEach(session => {
                    this.sessions.set(session.session_id, session);
                });

                this.renderSessionsList();
                logger.info(`✅ ${result.sessions.length} sessões carregadas`);
            } else {
                console.warn('Nenhuma sessão encontrada ou formato inválido');
                this.renderEmptySessionsList();
            }

        } catch (error) {
            console.error('Erro ao carregar sessões:', error);
            this.showNotification('Erro ao carregar sessões salvas', 'warning');
            this.renderEmptySessionsList();
        }
    }

    renderSessionsList() {
        const container = document.getElementById('sessionsList');
        if (!container) return;

        if (this.sessions.size === 0) {
            this.renderEmptySessionsList();
            return;
        }

        let html = '<div class="session-grid">';

        this.sessions.forEach((session, sessionId) => {
            const statusClass = this.getStatusClass(session.status);
            const statusText = this.getStatusText(session.status);

            html += `
                <div class="session-item ${session.status === 'running' ? 'active' : ''}"
                     onclick="analysisSystem.selectSession('${sessionId}')">
                    <div class="session-header">
                        <div class="session-name">
                            ${session.segmento || 'Segmento não definido'}
                        </div>
                        <span class="badge badge-${statusClass}">${statusText}</span>
                    </div>
                    <div class="session-meta">
                        <small><strong>Produto:</strong> ${session.produto || 'N/A'}</small>
                        <small><strong>Iniciado:</strong> ${this.formatDate(session.started_at)}</small>
                        ${session.etapas_salvas ? `<small><strong>Etapas:</strong> ${session.etapas_salvas}</small>` : ''}
                    </div>
                    <div class="session-actions">
                        ${this.getSessionActions(session, sessionId)}
                    </div>
                </div>
            `;
        });

        html += '</div>';
        container.innerHTML = html;
    }

    renderEmptySessionsList() {
        const container = document.getElementById('sessionsList');
        if (!container) return;

        container.innerHTML = `
            <div class="text-center" style="padding: 3rem; color: var(--text-tertiary);">
                <div style="font-size: 3rem; margin-bottom: 1rem;">📂</div>
                <h4>Nenhuma sessão encontrada</h4>
                <p>Inicie uma nova análise para criar sua primeira sessão.</p>
            </div>
        `;
    }

    getSessionActions(session, sessionId) {
        const actions = [];

        if (['paused', 'error', 'saved'].includes(session.status)) {
            actions.push(`
                <button class="btn btn-primary btn-sm"
                        onclick="event.stopPropagation(); analysisSystem.continueSession('${sessionId}')">
                    <i class="fas fa-play"></i> Continuar
                </button>
            `);
        }

        if (session.status === 'completed') {
            actions.push(`
                <button class="btn btn-secondary btn-sm"
                        onclick="event.stopPropagation(); analysisSystem.viewResults('${sessionId}')">
                    <i class="fas fa-eye"></i> Ver Resultados
                </button>
            `);
        }

        actions.push(`
            <button class="btn btn-error btn-sm"
                    onclick="event.stopPropagation(); analysisSystem.deleteSession('${sessionId}')">
                <i class="fas fa-trash"></i>
            </button>
        `);

        return actions.join(' ');
    }

    selectSession(sessionId) {
        const session = this.sessions.get(sessionId);
        if (!session) return;

        // Remove seleção anterior
        document.querySelectorAll('.session-item').forEach(item => {
            item.classList.remove('active');
        });

        // Seleciona novo item
        const selectedItem = document.querySelector(`[onclick="analysisSystem.selectSession('${sessionId}')"]`);
        if (selectedItem) {
            selectedItem.classList.add('active');
        }

        this.showSessionDetails(session);
    }

    showSessionDetails(session) {
        const detailsContainer = document.getElementById('sessionDetails');
        if (!detailsContainer) return;

        const html = `
            <div class="session-details-card">
                <div class="session-details-header">
                    <h4>Detalhes da Sessão</h4>
                    <span class="badge badge-${this.getStatusClass(session.status)}">
                        ${this.getStatusText(session.status)}
                    </span>
                </div>
                <div class="session-details-body">
                    <div class="detail-row">
                        <span class="detail-label">ID da Sessão:</span>
                        <span class="detail-value">${session.session_id}</span>
                    </div>
                    <div class="detail-row">
                        <span class="detail-label">Segmento:</span>
                        <span class="detail-value">${session.segmento || 'N/A'}</span>
                    </div>
                    <div class="detail-row">
                        <span class="detail-label">Produto:</span>
                        <span class="detail-value">${session.produto || 'N/A'}</span>
                    </div>
                    <div class="detail-row">
                        <span class="detail-label">Iniciado em:</span>
                        <span class="detail-value">${this.formatDate(session.started_at)}</span>
                    </div>
                    ${session.completed_at ? `
                        <div class="detail-row">
                            <span class="detail-label">Concluído em:</span>
                            <span class="detail-value">${this.formatDate(session.completed_at)}</span>
                        </div>
                    ` : ''}
                    <div class="detail-row">
                        <span class="detail-label">Etapas Salvas:</span>
                        <span class="detail-value">${session.etapas_salvas || 0}</span>
                    </div>
                    ${session.error ? `
                        <div class="alert alert-error">
                            <strong>Erro:</strong> ${session.error}
                        </div>
                    ` : ''}
                </div>
            </div>
        `;

        detailsContainer.innerHTML = html;
    }

    startProgressMonitoring() {
        if (!this.currentSessionId) return;

        this.progressInterval = setInterval(async () => {
            try {
                const response = await fetch(`/api/progress/${this.currentSessionId}`);
                const data = await response.json();

                if (data.success) {
                    this.updateProgress(
                        data.percentage,
                        data.current_step,
                        data.total_steps,
                        data.estimated_time
                    );

                    if (data.completed) {
                        this.stopProgressMonitoring();
                        this.showNotification('Análise concluída com sucesso!', 'success');
                        this.showProgress(false);
                        this.updateSessionControls('completed');
                        localStorage.removeItem('currentSessionId');

                        // Recarrega sessões
                        await this.loadSavedSessions();
                    }
                } else if (data.error) {
                    this.stopProgressMonitoring();
                    this.showNotification(`Erro: ${data.error}`, 'error');
                    this.showProgress(false);
                }

            } catch (error) {
                console.error('Erro no monitoramento:', error);
            }
        }, 3000); // Verifica a cada 3 segundos
    }

    stopProgressMonitoring() {
        if (this.progressInterval) {
            clearInterval(this.progressInterval);
            this.progressInterval = null;
        }
    }

    updateProgress(percentage, message, totalSteps = 13, estimatedTime = '') {
        // Atualiza barra de progresso
        const progressFill = document.querySelector('.progress-fill');
        const progressPercentage = document.querySelector('.progress-percentage');
        const progressStatus = document.querySelector('.progress-status');

        if (progressFill) {
            progressFill.style.width = `${Math.max(0, Math.min(100, percentage))}%`;
        }

        if (progressPercentage) {
            progressPercentage.textContent = `${Math.round(percentage)}%`;
        }

        if (progressStatus && message) {
            progressStatus.innerHTML = `
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <span>${message}</span>
                    ${estimatedTime ? `<small>Tempo estimado: ${estimatedTime}</small>` : ''}
                </div>
            `;
        }

        // Atualiza título da página
        document.title = `${Math.round(percentage)}% - ARQV30 Enhanced`;
    }

    showProgress(show) {
        const container = document.getElementById('progressContainer');
        if (container) {
            container.style.display = show ? 'block' : 'none';

            if (show) {
                container.scrollIntoView({ behavior: 'smooth' });
            }
        }
    }

    updateSessionControls(status) {
        const buttons = {
            pauseBtn: status === 'running',
            resumeBtn: status === 'paused',
            saveBtn: ['running', 'paused'].includes(status)
        };

        Object.entries(buttons).forEach(([id, show]) => {
            const btn = document.getElementById(id);
            if (btn) {
                btn.style.display = show ? 'inline-flex' : 'none';
            }
        });
    }

    async restoreLastSession() {
        const lastSessionId = localStorage.getItem('currentSessionId');
        if (lastSessionId) {
            this.currentSessionId = lastSessionId;
            await this.checkSessionStatus(lastSessionId);
        }

        // Restaura dados do formulário
        this.restoreFormData();
    }

    async checkSessionStatus(sessionId) {
        try {
            const response = await fetch(`/api/sessions/${sessionId}/status`);
            const result = await response.json();

            if (result.success) {
                const session = result.session;

                switch (session.status) {
                    case 'running':
                        this.showProgress(true);
                        this.startProgressMonitoring();
                        this.updateSessionControls('running');
                        this.showNotification('Sessão anterior restaurada e em execução', 'info');
                        break;

                    case 'paused':
                        this.updateSessionControls('paused');
                        this.showNotification('Sessão anterior encontrada (pausada)', 'info');
                        break;

                    case 'completed':
                        localStorage.removeItem('currentSessionId');
                        this.showNotification('Última sessão foi concluída', 'success');
                        break;

                    case 'error':
                        this.showNotification('Última sessão teve erro', 'warning');
                        break;
                }
            }

        } catch (error) {
            console.error('Erro ao verificar status da sessão:', error);
            localStorage.removeItem('currentSessionId');
        }
    }

    async viewResults(sessionId) {
        try {
            const response = await fetch(`/api/sessions/${sessionId}/results`);
            const result = await response.json();

            if (result.success) {
                // Abre resultados em nova aba ou modal
                if (result.html_report) {
                    const newWindow = window.open('', '_blank');
                    newWindow.document.write(result.html_report);
                    newWindow.document.close();
                } else if (result.report_url) {
                    window.open(result.report_url, '_blank');
                } else {
                    this.showSessionResults(result.analysis_result);
                }
            } else {
                throw new Error(result.error || 'Erro ao carregar resultados');
            }

        } catch (error) {
            this.showNotification(`Erro ao visualizar resultados: ${error.message}`, 'error');
        }
    }

    showSessionResults(analysisData) {
        // Cria modal com resultados
        const modal = document.createElement('div');
        modal.className = 'results-modal';
        modal.innerHTML = `
            <div class="modal-content">
                <div class="modal-header">
                    <h3>Resultados da Análise</h3>
                    <button class="close-btn" onclick="this.parentElement.parentElement.parentElement.remove()">×</button>
                </div>
                <div class="modal-body">
                    <pre>${JSON.stringify(analysisData, null, 2)}</pre>
                </div>
            </div>
        `;
        document.body.appendChild(modal);
    }

    async deleteSession(sessionId) {
        if (!confirm('Tem certeza que deseja excluir esta sessão?')) {
            return;
        }

        try {
            const response = await fetch(`/api/sessions/${sessionId}`, {
                method: 'DELETE'
            });

            const result = await response.json();

            if (result.success) {
                this.showNotification('Sessão excluída com sucesso', 'success');
                this.sessions.delete(sessionId);
                this.renderSessionsList();
            } else {
                throw new Error(result.error);
            }

        } catch (error) {
            this.showNotification(`Erro ao excluir: ${error.message}`, 'error');
        }
    }

    async clearAllSessions() {
        if (!confirm('Tem certeza que deseja limpar TODAS as sessões?')) {
            return;
        }

        try {
            // Tenta múltiplos endpoints para limpeza
            let response = await fetch('/api/progress/cleanup', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    force: true,
                    max_age_minutes: 0
                })
            });

            if (!response.ok) {
                // Fallback para endpoint alternativo
                response = await fetch('/api/user/clear_sessions', {
                    method: 'POST'
                });
            }

            if (!response.ok) {
                throw new Error(`Endpoint não encontrado (${response.status})`);
            }

            const result = await response.json();

            if (result.success) {
                this.showNotification('Todas as sessões foram excluídas', 'success');
                this.sessions.clear();
                this.renderEmptySessionsList();

                // Limpa também o localStorage
                localStorage.removeItem('currentSessionId');
                localStorage.removeItem('analysisFormData');
                localStorage.removeItem('arqv30_analyses');
            } else {
                throw new Error(result.error || 'Erro desconhecido');
            }

        } catch (error) {
            console.error('Erro ao limpar sessões:', error);
            this.showNotification(`Erro ao limpar sessões: ${error.message}`, 'error');
        }
    }

    // Utility Methods
    getStatusClass(status) {
        const classes = {
            'running': 'primary',
            'paused': 'warning',
            'completed': 'success',
            'error': 'error',
            'saved': 'secondary'
        };
        return classes[status] || 'secondary';
    }

    getStatusText(status) {
        const texts = {
            'running': 'Em execução',
            'paused': 'Pausada',
            'completed': 'Concluída',
            'error': 'Erro',
            'saved': 'Salva'
        };
        return texts[status] || 'Desconhecido';
    }

    formatDate(dateString) {
        if (!dateString) return 'N/A';

        try {
            const date = new Date(dateString);
            return new Intl.DateTimeFormat('pt-BR', {
                day: '2-digit',
                month: '2-digit',
                year: 'numeric',
                hour: '2-digit',
                minute: '2-digit'
            }).format(date);
        } catch {
            return dateString;
        }
    }

    showNotification(message, type = 'info', duration = 5000) {
        const notification = this.createNotification(message, type);
        this.addNotificationToContainer(notification);

        // Auto-remove
        setTimeout(() => {
            this.removeNotification(notification);
        }, duration);
    }

    createNotification(message, type) {
        const notification = document.createElement('div');
        notification.className = `notification notification-${type} fade-in`;

        const icons = {
            info: 'fas fa-info-circle',
            success: 'fas fa-check-circle',
            warning: 'fas fa-exclamation-triangle',
            error: 'fas fa-exclamation-circle'
        };

        notification.innerHTML = `
            <div class="notification-icon">
                <i class="${icons[type]}"></i>
            </div>
            <div class="notification-content">
                <div class="notification-message">${message}</div>
            </div>
            <button class="notification-close" onclick="analysisSystem.removeNotification(this.parentElement)">
                <i class="fas fa-times"></i>
            </button>
        `;

        return notification;
    }

    addNotificationToContainer(notification) {
        let container = document.getElementById('notificationContainer');
        if (!container) {
            container = document.createElement('div');
            container.id = 'notificationContainer';
            container.className = 'notification-container';
            container.style.cssText = `
                position: fixed;
                top: 1rem;
                right: 1rem;
                z-index: 9999;
                display: flex;
                flex-direction: column;
                gap: 0.5rem;
                max-width: 400px;
            `;
            document.body.appendChild(container);
        }

        container.appendChild(notification);
        this.notifications.push(notification);
    }

    removeNotification(notification) {
        if (notification && notification.parentElement) {
            notification.classList.add('fade-out');
            setTimeout(() => {
                notification.remove();
                const index = this.notifications.indexOf(notification);
                if (index > -1) {
                    this.notifications.splice(index, 1);
                }
            }, 300);
        }
    }

    clearNotifications() {
        this.notifications.forEach(notification => {
            this.removeNotification(notification);
        });
    }
}

// Funções globais auxiliares (devem ser chamadas a partir do escopo global)
function getFormData() {
    const form = document.getElementById('analysisForm');
    if (!form) return {};
    const formData = new FormData(form);
    return Object.fromEntries(formData.entries());
}

function showAlert(message, type = 'info') {
    // Adaptação para usar o sistema de notificações da classe
    if (window.analysisSystem && typeof window.analysisSystem.showNotification === 'function') {
        window.analysisSystem.showNotification(message, type);
    } else {
        console.warn(`Notificação simulada: [${type}] ${message}`);
    }
}

function showResults(results) {
    const resultsContainer = document.getElementById('results-container');
    const analysisContainer = document.getElementById('analysis-container');
    const progressContainer = document.getElementById('progress-container');

    if (resultsContainer && analysisContainer && progressContainer) {
        resultsContainer.style.display = 'block';
        analysisContainer.style.display = 'none';
        progressContainer.style.display = 'none';

        // Limpa resultados anteriores e exibe os novos
        const outputDiv = resultsContainer.querySelector('#analysis-output');
        if (outputDiv) {
            if (typeof results === 'string') {
                outputDiv.innerHTML = results;
            } else {
                outputDiv.textContent = JSON.stringify(results, null, 2);
            }
        }
        document.title = 'Resultados da Análise - ARQV30 Enhanced';
    }
}

function updateProgressUI(percentage, message) {
    const progressBar = document.querySelector('.progress-bar');
    const progressText = document.querySelector('.progress-text');

    if (progressBar) {
        progressBar.style.width = `${percentage}%`;
    }
    if (progressText) {
        progressText.textContent = `${message} (${percentage.toFixed(1)}%)`;
    }
}


async function checkAnalysisStatus(sessionId) {
    try {
        const response = await fetch(`/api/analysis_status/${sessionId}`);
        const data = await response.json();

        if (data.success) {
            currentAnalysisId = sessionId;
            isAnalysisRunning = data.status === 'running';

            if (data.status === 'running') {
                updateProgressUI(data.progress || 0, data.current_step || 'Continuando...');
                startAutoSave();
                pollProgress();
            } else if (data.status === 'completed') {
                showResults(data.results);
                stopAutoSave();
            } else {
                // Se estiver pausada, salva localmente e atualiza UI
                persistence.saveSession(sessionId, {
                    ...getFormData(),
                    progress: data.progress || 0,
                    status: data.status,
                    results: data.results
                });
            }
        } else {
            throw new Error(data.error || 'Não foi possível verificar o status');
        }
    } catch (error) {
        console.error('Erro ao verificar status:', error);
        showAlert('Erro ao verificar status da análise: ' + error.message, 'error');
    }
}

async function pollProgress() {
    if (!currentAnalysisId) return;

    try {
        const response = await fetch(`/api/progress/${currentAnalysisId}`);
        const data = await response.json();

        if (data.success) {
            updateProgressUI(data.percentage, data.current_step);
            persistence.saveSession(currentAnalysisId, {
                ...getFormData(),
                progress: data.percentage,
                status: data.completed ? 'completed' : 'running',
                current_step: data.current_step,
                results: data.results
            });

            if (data.completed) {
                showResults(data.results);
                stopAutoSave();
                isAnalysisRunning = false;
                currentAnalysisId = null;
            } else if (isAnalysisRunning) {
                setTimeout(pollProgress, 3000); // Verifica a cada 3 segundos
            }
        } else {
            throw new Error(data.error || 'Erro ao obter progresso');
        }
    } catch (error) {
        console.error('Erro no polling de progresso:', error);
        showAlert('Erro ao monitorar progresso: ' + error.message, 'error');
        stopAutoSave();
        isAnalysisRunning = false;
    }
}


// --- Funções Globais Auxiliares ---

// Inicialização global
let analysisSystem;

function executeAnalysis() {
    console.log('🚀 Iniciando análise...');

    const formData = getFormData();

    if (!formData.segmento || !formData.produto) {
        showAlert('Por favor, preencha pelo menos o segmento e produto.', 'warning');
        return;
    }

    // Reset UI
    document.getElementById('analysis-container').style.display = 'block';
    document.getElementById('progress-container').style.display = 'block';
    document.getElementById('results-container').style.display = 'none';

    // Salva dados do formulário para continuação futura
    const sessionData = {
        ...formData,
        startedAt: new Date().toISOString(),
        status: 'initiated'
    };

    // Inicia análise
    startAnalysis(formData);
}

function continueAnalysis(sessionId) {
    console.log(`🔄 Continuando análise: ${sessionId}`);

    const sessionData = persistence.getSession(sessionId);
    if (!sessionData) {
        showAlert('Sessão não encontrada', 'error');
        return;
    }

    // Restaura dados do formulário
    document.getElementById('segmento').value = sessionData.segmento || '';
    document.getElementById('produto').value = sessionData.produto || '';
    document.getElementById('publico').value = sessionData.publico || '';
    document.getElementById('preco').value = sessionData.preco || '';
    document.getElementById('objetivo_receita').value = sessionData.objetivo_receita || '';

    // Define a sessão atual
    currentAnalysisId = sessionId;

    // Se a análise está completa, mostra resultados
    if (sessionData.progress === 100 && sessionData.results) {
        showResults(sessionData.results);
        return;
    }

    // Se está incompleta, verifica status no servidor
    checkAnalysisStatus(sessionId);
}

function deleteAnalysis(sessionId) {
    if (confirm('Tem certeza que deseja excluir esta análise?')) {
        persistence.deleteSession(sessionId);
        showAlert('Análise excluída com sucesso', 'success');
    }
}

function startAutoSave() {
    if (autoSaveInterval) {
        clearInterval(autoSaveInterval);
    }

    autoSaveInterval = setInterval(() => {
        if (currentAnalysisId && isAnalysisRunning) {
            // Auto-save dos dados de progresso
            const currentProgress = getCurrentProgress();
            persistence.saveSession(currentAnalysisId, {
                ...getFormData(),
                progress: currentProgress,
                status: 'in_progress',
                lastAutoSave: new Date().toISOString()
            });
        }
    }, 30000); // Auto-save a cada 30 segundos
}

function stopAutoSave() {
    if (autoSaveInterval) {
        clearInterval(autoSaveInterval);
        autoSaveInterval = null;
    }
}

function getCurrentProgress() {
    const progressBar = document.querySelector('.progress-bar');
    if (progressBar) {
        const style = progressBar.getAttribute('style');
        const match = style.match(/width:\s*(\d+)%/);
        return match ? parseInt(match[1]) : 0;
    }
    return 0;
}

async function startAnalysis(formData) {
    try {
        isAnalysisRunning = true;

        const response = await fetch('/api/execute_complete_analysis', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(formData)
        });

        const data = await response.json();

        if (data.session_id) {
            currentAnalysisId = data.session_id;

            // Salva dados iniciais da sessão
            persistence.saveSession(currentAnalysisId, {
                ...formData,
                startedAt: new Date().toISOString(),
                status: 'running',
                progress: 0
            });

            // Inicia auto-save
            startAutoSave();

            pollProgress();
        } else {
            throw new Error('Session ID não retornado');
        }

    } catch (error) {
        console.error('Erro na análise:', error);
        showAlert('Erro ao iniciar análise: ' + error.message, 'error');
        isAnalysisRunning = false;
        stopAutoSave();
    }
}


// CSS para notificações (adicionado dinamicamente)
const notificationStyles = `
    .notification {
        display: flex;
        align-items: flex-start;
        gap: 0.75rem;
        padding: 1rem;
        background: white;
        border-radius: 0.75rem;
        box-shadow: 0 10px 15px -3px rgb(0 0 0 / 0.1);
        border: 1px solid #e5e7eb;
        min-width: 300px;
        max-width: 400px;
        animation: slideInRight 0.3s ease-out;
        position: relative;
        overflow: hidden;
    }

    .notification::before {
        content: '';
        position: absolute;
        left: 0;
        top: 0;
        bottom: 0;
        width: 4px;
    }

    .notification-info::before { background: #3b82f6; }
    .notification-success::before { background: #10b981; }
    .notification-warning::before { background: #f59e0b; }
    .notification-error::before { background: #ef4444; }

    .notification-icon {
        flex-shrink: 0;
        width: 20px;
        height: 20px;
        display: flex;
        align-items: center;
        justify-content: center;
    }

    .notification-info .notification-icon { color: #3b82f6; }
    .notification-success .notification-icon { color: #10b981; }
    .notification-warning .notification-icon { color: #f59e0b; }
    .notification-error .notification-icon { color: #ef4444; }

    .notification-content {
        flex: 1;
    }

    .notification-message {
        font-size: 0.875rem;
        color: #374151;
        font-weight: 500;
        line-height: 1.4;
    }

    .notification-close {
        flex-shrink: 0;
        width: 20px;
        height: 20px;
        border: none;
        background: none;
        color: #9ca3af;
        cursor: pointer;
        border-radius: 0.25rem;
        display: flex;
        align-items: center;
        justify-content: center;
        transition: all 0.15s;
    }

    .notification-close:hover {
        background: #f3f4f6;
        color: #374151;
    }

    .fade-out {
        animation: slideOutRight 0.3s ease-in forwards;
    }

    @keyframes slideInRight {
        from {
            opacity: 0;
            transform: translateX(100px);
        }
        to {
            opacity: 1;
            transform: translateX(0);
        }
    }

    @keyframes slideOutRight {
        to {
            opacity: 0;
            transform: translateX(100px);
        }
    }
`;

// Adiciona estilos das notificações
if (!document.getElementById('notificationStyles')) {
    const style = document.createElement('style');
    style.id = 'notificationStyles';
    style.textContent = notificationStyles;
    document.head.appendChild(style);
}

document.addEventListener('DOMContentLoaded', () => {
    analysisSystem = new ModernAnalysisSystem();
    console.log('🚀 ARQV30 Enhanced v3.0 - Sistema Moderno Inicializado');
    console.log('🎯 Interface Moderna Carregada');
});