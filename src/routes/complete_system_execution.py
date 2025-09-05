"""
Rota Principal para Execução Completa do Sistema - V3.0
Endpoint que executa todo o sistema integrado
"""

from flask import Blueprint, request, jsonify, render_template_string
import asyncio
import logging
from datetime import datetime
import os
import sys

# Adicionar path do projeto
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'services'))

from master_system_orchestrator import get_master_orchestrator

logger = logging.getLogger(__name__)

complete_system_bp = Blueprint('complete_system', __name__)

@complete_system_bp.route('/execute-complete-system', methods=['POST'])
def execute_complete_system():
    """
    Executa o sistema completo de análise
    """
    try:
        data = request.get_json()
        
        # Validar parâmetros obrigatórios
        required_fields = ['tema', 'segmento', 'publico_alvo']
        for field in required_fields:
            if not data.get(field):
                return jsonify({
                    'success': False,
                    'error': f'Campo obrigatório ausente: {field}'
                }), 400
        
        tema = data['tema']
        segmento = data['segmento']
        publico_alvo = data['publico_alvo']
        
        logger.info(f"🚀 Iniciando execução completa do sistema")
        logger.info(f"📋 Tema: {tema}")
        logger.info(f"🏢 Segmento: {segmento}")
        logger.info(f"👥 Público: {publico_alvo}")
        
        # Obter orquestrador
        orchestrator = get_master_orchestrator()
        
        # Validar sistema antes da execução
        validation = asyncio.run(orchestrator.validate_system_requirements())
        
        if not all(validation.values()):
            missing_components = [k for k, v in validation.items() if not v]
            return jsonify({
                'success': False,
                'error': 'Sistema não está pronto para execução',
                'missing_components': missing_components,
                'validation': validation
            }), 500
        
        # Executar sistema completo
        execution_result = asyncio.run(
            orchestrator.execute_complete_system(tema, segmento, publico_alvo)
        )
        
        # Preparar resposta
        response = {
            'success': True,
            'message': 'Sistema executado com sucesso!',
            'session_id': execution_result.session_id,
            'execution_time': str(execution_result.end_time - execution_result.start_time),
            'status': execution_result.status,
            'results': {
                'search_results': execution_result.results.get('search_results', {}),
                'ai_expertise': execution_result.results.get('ai_expertise', {}),
                'avatares': execution_result.results.get('avatares', {}),
                'mental_drivers': execution_result.results.get('mental_drivers', {}),
                'cpls': execution_result.results.get('cpls', {}),
                'predictive_analysis': execution_result.results.get('predictive_analysis', {}),
                'html_report': execution_result.results.get('html_report', {})
            },
            'warnings': execution_result.warnings,
            'data_directory': f"/workspace/project/v110/analyses_data/{execution_result.session_id}"
        }
        
        logger.info(f"✅ Sistema executado com sucesso: {execution_result.session_id}")
        
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"❌ Erro na execução do sistema: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'Erro interno na execução do sistema'
        }), 500

@complete_system_bp.route('/system-health', methods=['GET'])
def get_system_health():
    """
    Retorna status de saúde do sistema
    """
    try:
        orchestrator = get_master_orchestrator()
        health = asyncio.run(orchestrator.get_system_health())
        
        return jsonify(health)
        
    except Exception as e:
        logger.error(f"❌ Erro ao verificar saúde do sistema: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'overall_status': 'error'
        }), 500

@complete_system_bp.route('/execution-status', methods=['GET'])
def get_execution_status():
    """
    Retorna status da execução atual
    """
    try:
        orchestrator = get_master_orchestrator()
        current_execution = orchestrator.get_execution_status()
        
        if not current_execution:
            return jsonify({
                'success': True,
                'message': 'Nenhuma execução em andamento',
                'status': 'idle'
            })
        
        return jsonify({
            'success': True,
            'execution': {
                'session_id': current_execution.session_id,
                'status': current_execution.status,
                'start_time': current_execution.start_time.isoformat(),
                'tema': current_execution.tema,
                'segmento': current_execution.segmento,
                'publico_alvo': current_execution.publico_alvo,
                'results': current_execution.results,
                'warnings': current_execution.warnings,
                'errors': current_execution.errors
            }
        })
        
    except Exception as e:
        logger.error(f"❌ Erro ao verificar status: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@complete_system_bp.route('/interface', methods=['GET'])
def show_interface():
    """
    Mostra interface web para execução do sistema
    """
    interface_html = """
    <!DOCTYPE html>
    <html lang="pt-BR">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Sistema Completo de Análise - V3.0</title>
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }
            
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                padding: 2rem;
            }
            
            .container {
                max-width: 800px;
                margin: 0 auto;
                background: white;
                border-radius: 12px;
                box-shadow: 0 10px 30px rgba(0,0,0,0.2);
                overflow: hidden;
            }
            
            .header {
                background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%);
                color: white;
                padding: 2rem;
                text-align: center;
            }
            
            .header h1 {
                font-size: 2rem;
                margin-bottom: 0.5rem;
            }
            
            .header p {
                opacity: 0.9;
                font-size: 1.1rem;
            }
            
            .content {
                padding: 2rem;
            }
            
            .form-group {
                margin-bottom: 1.5rem;
            }
            
            .form-group label {
                display: block;
                margin-bottom: 0.5rem;
                font-weight: 600;
                color: #374151;
            }
            
            .form-group input,
            .form-group textarea {
                width: 100%;
                padding: 0.75rem;
                border: 2px solid #e5e7eb;
                border-radius: 8px;
                font-size: 1rem;
                transition: border-color 0.3s ease;
            }
            
            .form-group input:focus,
            .form-group textarea:focus {
                outline: none;
                border-color: #2563eb;
            }
            
            .btn {
                background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%);
                color: white;
                padding: 1rem 2rem;
                border: none;
                border-radius: 8px;
                font-size: 1.1rem;
                font-weight: 600;
                cursor: pointer;
                transition: transform 0.2s ease;
                width: 100%;
            }
            
            .btn:hover {
                transform: translateY(-2px);
            }
            
            .btn:disabled {
                opacity: 0.6;
                cursor: not-allowed;
                transform: none;
            }
            
            .status {
                margin-top: 2rem;
                padding: 1rem;
                border-radius: 8px;
                display: none;
            }
            
            .status.success {
                background: #d1fae5;
                border: 1px solid #10b981;
                color: #065f46;
            }
            
            .status.error {
                background: #fee2e2;
                border: 1px solid #ef4444;
                color: #991b1b;
            }
            
            .status.loading {
                background: #dbeafe;
                border: 1px solid #3b82f6;
                color: #1e40af;
            }
            
            .features {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 1rem;
                margin-bottom: 2rem;
            }
            
            .feature {
                background: #f8fafc;
                padding: 1rem;
                border-radius: 8px;
                text-align: center;
                border: 1px solid #e2e8f0;
            }
            
            .feature-icon {
                font-size: 2rem;
                margin-bottom: 0.5rem;
            }
            
            .feature h3 {
                font-size: 0.9rem;
                color: #374151;
                margin-bottom: 0.25rem;
            }
            
            .feature p {
                font-size: 0.8rem;
                color: #6b7280;
            }
            
            .progress {
                display: none;
                margin-top: 1rem;
            }
            
            .progress-bar {
                background: #e5e7eb;
                border-radius: 10px;
                height: 8px;
                overflow: hidden;
            }
            
            .progress-fill {
                background: linear-gradient(90deg, #2563eb 0%, #1d4ed8 100%);
                height: 100%;
                width: 0%;
                transition: width 0.3s ease;
                animation: pulse 2s infinite;
            }
            
            @keyframes pulse {
                0%, 100% { opacity: 1; }
                50% { opacity: 0.7; }
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🚀 Sistema Completo de Análise</h1>
                <p>Busca massiva • IA Expert • Avatares únicos • Drivers mentais • CPLs devastadores</p>
            </div>
            
            <div class="content">
                <div class="features">
                    <div class="feature">
                        <div class="feature-icon">🔍</div>
                        <h3>Busca Massiva</h3>
                        <p>Instagram, Facebook, YouTube</p>
                    </div>
                    <div class="feature">
                        <div class="feature-icon">🧠</div>
                        <h3>IA Expert</h3>
                        <p>5 min de estudo profundo</p>
                    </div>
                    <div class="feature">
                        <div class="feature-icon">👥</div>
                        <h3>4 Avatares</h3>
                        <p>Nomes reais e únicos</p>
                    </div>
                    <div class="feature">
                        <div class="feature-icon">⚡</div>
                        <h3>19 Drivers</h3>
                        <p>Ancoragem psicológica</p>
                    </div>
                    <div class="feature">
                        <div class="feature-icon">🎬</div>
                        <h3>CPLs Devastadores</h3>
                        <p>Protocolo de 5 fases</p>
                    </div>
                    <div class="feature">
                        <div class="feature-icon">📄</div>
                        <h3>Relatório 25+ pág</h3>
                        <p>HTML moderno</p>
                    </div>
                </div>
                
                <form id="systemForm">
                    <div class="form-group">
                        <label for="tema">Tema Principal *</label>
                        <input type="text" id="tema" name="tema" required 
                               placeholder="Ex: Marketing Digital, Vendas Online, Empreendedorismo">
                    </div>
                    
                    <div class="form-group">
                        <label for="segmento">Segmento de Mercado *</label>
                        <input type="text" id="segmento" name="segmento" required 
                               placeholder="Ex: E-commerce, Consultoria, Infoprodutos">
                    </div>
                    
                    <div class="form-group">
                        <label for="publico_alvo">Público-Alvo *</label>
                        <textarea id="publico_alvo" name="publico_alvo" rows="3" required 
                                  placeholder="Ex: Empreendedores iniciantes de 25-40 anos que querem aumentar vendas online"></textarea>
                    </div>
                    
                    <button type="submit" class="btn" id="executeBtn">
                        🚀 Executar Sistema Completo
                    </button>
                </form>
                
                <div class="progress" id="progress">
                    <div class="progress-bar">
                        <div class="progress-fill" id="progressFill"></div>
                    </div>
                    <p id="progressText" style="text-align: center; margin-top: 0.5rem; color: #6b7280;"></p>
                </div>
                
                <div class="status" id="status"></div>
            </div>
        </div>
        
        <script>
            const form = document.getElementById('systemForm');
            const executeBtn = document.getElementById('executeBtn');
            const status = document.getElementById('status');
            const progress = document.getElementById('progress');
            const progressFill = document.getElementById('progressFill');
            const progressText = document.getElementById('progressText');
            
            const steps = [
                'Iniciando sistema...',
                'Executando busca massiva...',
                'IA estudando dados (5 min)...',
                'Gerando 4 avatares únicos...',
                'Implementando drivers mentais...',
                'Criando CPLs devastadores...',
                'Análise preditiva...',
                'Gerando relatório HTML...',
                'Finalizando...'
            ];
            
            let currentStep = 0;
            let progressInterval;
            
            form.addEventListener('submit', async (e) => {
                e.preventDefault();
                
                const formData = new FormData(form);
                const data = {
                    tema: formData.get('tema'),
                    segmento: formData.get('segmento'),
                    publico_alvo: formData.get('publico_alvo')
                };
                
                // Validar campos
                if (!data.tema || !data.segmento || !data.publico_alvo) {
                    showStatus('error', 'Todos os campos são obrigatórios!');
                    return;
                }
                
                // Iniciar execução
                executeBtn.disabled = true;
                executeBtn.textContent = '⏳ Executando...';
                showStatus('loading', 'Iniciando execução do sistema completo...');
                showProgress();
                
                try {
                    const response = await fetch('/execute-complete-system', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify(data)
                    });
                    
                    const result = await response.json();
                    
                    if (result.success) {
                        hideProgress();
                        showStatus('success', `
                            <h3>✅ Sistema executado com sucesso!</h3>
                            <p><strong>Sessão:</strong> ${result.session_id}</p>
                            <p><strong>Tempo:</strong> ${result.execution_time}</p>
                            <p><strong>Posts coletados:</strong> ${result.results.search_results.total_posts || 0}</p>
                            <p><strong>Avatares gerados:</strong> ${result.results.avatares.total_avatares || 0}</p>
                            <p><strong>Drivers implementados:</strong> ${result.results.mental_drivers.total_drivers || 0}</p>
                            <p><strong>Relatório:</strong> ${result.results.html_report.generated ? '✅ Gerado' : '❌ Erro'}</p>
                            ${result.warnings.length > 0 ? `<p><strong>Avisos:</strong> ${result.warnings.join(', ')}</p>` : ''}
                        `);
                    } else {
                        hideProgress();
                        showStatus('error', `Erro: ${result.error}`);
                    }
                    
                } catch (error) {
                    hideProgress();
                    showStatus('error', `Erro de conexão: ${error.message}`);
                }
                
                executeBtn.disabled = false;
                executeBtn.textContent = '🚀 Executar Sistema Completo';
            });
            
            function showStatus(type, message) {
                status.className = `status ${type}`;
                status.innerHTML = message;
                status.style.display = 'block';
            }
            
            function showProgress() {
                progress.style.display = 'block';
                currentStep = 0;
                
                progressInterval = setInterval(() => {
                    if (currentStep < steps.length) {
                        progressText.textContent = steps[currentStep];
                        progressFill.style.width = `${((currentStep + 1) / steps.length) * 100}%`;
                        currentStep++;
                    }
                }, 30000); // 30 segundos por etapa
            }
            
            function hideProgress() {
                progress.style.display = 'none';
                if (progressInterval) {
                    clearInterval(progressInterval);
                }
            }
            
            // Verificar saúde do sistema ao carregar
            window.addEventListener('load', async () => {
                try {
                    const response = await fetch('/system-health');
                    const health = await response.json();
                    
                    if (!health.system_ready) {
                        showStatus('error', 'Sistema não está pronto. Verifique as configurações.');
                        executeBtn.disabled = true;
                    }
                } catch (error) {
                    console.warn('Não foi possível verificar saúde do sistema:', error);
                }
            });
        </script>
    </body>
    </html>
    """
    
    return render_template_string(interface_html)

@complete_system_bp.route('/view-report/<session_id>', methods=['GET'])
def view_report(session_id):
    """
    Visualiza relatório HTML gerado
    """
    try:
        report_path = f"/workspace/project/v110/analyses_data/{session_id}/relatorio_completo.html"
        
        if not os.path.exists(report_path):
            return jsonify({
                'success': False,
                'error': 'Relatório não encontrado'
            }), 404
        
        with open(report_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        return html_content
        
    except Exception as e:
        logger.error(f"❌ Erro ao visualizar relatório: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500