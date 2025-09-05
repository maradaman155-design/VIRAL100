#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ARQV30 Enhanced v3.0 - Analysis Route
Rota de análise atualizada para nova metodologia
"""

import logging
import time
import uuid
import random
from datetime import datetime
from flask import Blueprint, request, jsonify
from services.master_analysis_orchestrator import master_analysis_orchestrator
from services.auto_save_manager import salvar_etapa
from services.progress_tracker_enhanced import progress_tracker
from services.real_search_orchestrator import real_search_orchestrator
from services.viral_content_analyzer import viral_content_analyzer
from services.enhanced_synthesis_engine import enhanced_synthesis_engine

logger = logging.getLogger(__name__)

analysis_bp = Blueprint('analysis', __name__)

@analysis_bp.route('/execute_complete_analysis', methods=['POST'])
def execute_complete_analysis():
    """Executa análise completa com nova metodologia aprimorada"""
    try:
        # Recebe dados da requisição
        data = request.get_json()

        if not data:
            return jsonify({"error": "Dados da requisição são obrigatórios"}), 400

        # Gera session_id único
        session_id = f"session_{int(time.time() * 1000)}_{uuid.uuid4().hex[:8]}"

        # Extrai parâmetros
        segmento = data.get('segmento', '').strip()
        produto = data.get('produto', '').strip()
        publico = data.get('publico', '').strip()
        objetivos = data.get('objetivos', '').strip()
        contexto_adicional = data.get('contexto_adicional', '').strip()

        # Validação básica
        if not segmento and not produto:
            return jsonify({"error": "Segmento ou produto são obrigatórios"}), 400

        # Constrói query de pesquisa
        query_parts = []
        if segmento:
            query_parts.append(segmento)
        if produto:
            query_parts.append(produto)
        query_parts.append("Brasil 2024")

        query = " ".join(query_parts)

        # Contexto da análise
        context = {
            "segmento": segmento,
            "produto": produto,
            "publico": publico,
            "objetivos": objetivos,
            "contexto_adicional": contexto_adicional,
            "methodology": "ARQV30_Enhanced_v3.0_REAL_DATA_ONLY"
        }

        # Salva dados da requisição
        requisicao_data = {
            "session_id": session_id,
            "timestamp": datetime.now().isoformat(),
            "query": query,
            "context": context,
            "methodology": "REAL_DATA_v3.0"
        }

        salvar_etapa("requisicao_analise_aprimorada", requisicao_data, categoria="analise_completa")

        # Inicializa progress tracker
        progress_tracker.start_session(session_id, 4)  # 4 fases principais

        def progress_callback(step, message: str):
            """Callback para atualizações de progresso"""
            try:
                # Converte step para int se necessário
                step_int = int(float(step)) if not isinstance(step, int) else step
                progress_tracker.update_progress(session_id, step_int, message)
                logger.info(f"Progress {session_id}: Step {step_int} - {message}")
            except Exception as e:
                logger.error(f"Erro no progress callback: {e}")

        # Executa análise completa com nova metodologia
        logger.info(f"🚀 Iniciando análise aprimorada para session {session_id}")
        logger.info(f"📋 Query: {query}")
        logger.info(f"🎯 Segmento: {segmento} | Produto: {produto}")

        # Executa análise com novo sistema aprimorado
        def execute_enhanced_analysis():
            try:
                import asyncio
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                
                try:
                    # ETAPA 1: Busca massiva real
                    progress_callback(1, "🌊 Executando busca massiva real...")
                    search_results = loop.run_until_complete(
                        real_search_orchestrator.execute_massive_real_search(
                            query=query,
                            context=context,
                            session_id=session_id
                        )
                    )
                    
                    # ETAPA 2: Análise de conteúdo viral
                    progress_callback(2, "🔥 Analisando conteúdo viral...")
                    viral_analysis = loop.run_until_complete(
                        viral_content_analyzer.analyze_and_capture_viral_content(
                            search_results=search_results,
                            session_id=session_id
                        )
                    )
                    
                    # ETAPA 3: Síntese com IA ativa
                    progress_callback(3, "🧠 Executando síntese com IA...")
                    synthesis_result = loop.run_until_complete(
                        enhanced_synthesis_engine.execute_enhanced_synthesis(session_id)
                    )
                    
                    # ETAPA 4: Geração de módulos
                    progress_callback(4, "📝 Gerando 16 módulos...")
                    from services.enhanced_module_processor import enhanced_module_processor
                    modules_result = loop.run_until_complete(
                        enhanced_module_processor.generate_all_modules(session_id)
                    )
                    
                finally:
                    loop.close()
                
                return {
                    "success": True,
                    "search_results": search_results,
                    "viral_analysis": viral_analysis,
                    "synthesis_result": synthesis_result,
                    "modules_result": modules_result,
                    "phases_completed": ["busca_massiva", "analise_viral", "sintese_ia", "geracao_modulos"]
                }
                
            except Exception as e:
                logger.error(f"❌ Erro na análise aprimorada: {e}")
                return {
                    "success": False,
                    "error": str(e)
                }
        
        # Executa análise
        analysis_results = execute_enhanced_analysis()

        # Finaliza progress tracker
        progress_tracker.complete_session(session_id)

        # Resposta da API
        if analysis_results.get("success"):
            response = {
                "success": True,
                "session_id": session_id,
                "methodology": "ARQV30_Enhanced_v3.0_REAL_DATA_ONLY",
                "message": "Análise completa concluída com sucesso",
                "execution_summary": {
                    "execution_time": 0,  # Será calculado
                    "phases_completed": analysis_results.get("phases_completed", []),
                    "total_sources": analysis_results.get("search_results", {}).get("statistics", {}).get("total_sources", 0),
                    "viral_content": len(analysis_results.get("viral_analysis", {}).get("viral_content_identified", [])),
                    "screenshots_captured": len(analysis_results.get("viral_analysis", {}).get("screenshots_captured", [])),
                    "modules_generated": analysis_results.get("modules_result", {}).get("successful_modules", 0)
                },
                "data_quality": {
                    "sources_quality": "PREMIUM - 100% dados reais",
                    "processing_quality": "ULTRA_HIGH",
                    "viral_content_captured": True,
                    "ai_active_search": True,
                    "api_rotation_used": True
                },
                "access_info": {
                    "session_directory": f"analyses_data/{session_id}",
                    "screenshots_directory": f"analyses_data/files/{session_id}",
                    "modules_directory": f"analyses_data/{session_id}/modules",
                    "final_report_available": True
                }
            }

            logger.info(f"✅ Análise aprimorada concluída com sucesso: {session_id}")
            return jsonify(response), 200

        else:
            error_response = {
                "success": False,
                "session_id": session_id,
                "methodology": "ARQV30_Enhanced_v3.0_REAL_DATA_ONLY",
                "error": analysis_results.get("error", "Erro desconhecido"),
                "message": "Análise falhou durante execução"
            }

            logger.error(f"❌ Análise falhou: {session_id} - {analysis_results.get('error')}")
            return jsonify(error_response), 500

    except Exception as e:
        logger.error(f"❌ Erro crítico na rota de análise: {e}")
        return jsonify({
            "success": False,
            "error": str(e),
            "message": "Erro interno do servidor"
        }), 500

@analysis_bp.route('/analysis_status/<session_id>', methods=['GET'])
def get_analysis_status(session_id):
    """Obtém status da análise em andamento"""
    try:
        # Obtém progresso do tracker
        progress_info = progress_tracker.get_session_progress(session_id)

        # Obtém progresso das fases do orquestrador
        phase_progress = master_analysis_orchestrator.get_phase_progress(session_id)

        status_response = {
            "session_id": session_id,
            "methodology": "ARQV30_Enhanced_v3.0_APRIMORADA",
            "progress_info": progress_info,
            "phase_progress": phase_progress,
            "timestamp": datetime.now().isoformat()
        }

        return jsonify(status_response), 200

    except Exception as e:
        logger.error(f"❌ Erro ao obter status: {e}")
        return jsonify({
            "session_id": session_id,
            "error": str(e),
            "status": "error"
        }), 500

@analysis_bp.route('/reset_orchestrator', methods=['POST'])
def reset_orchestrator():
    """Reseta o orquestrador mestre"""
    try:
        master_analysis_orchestrator.reset_orchestrator()
        progress_tracker.reset()

        return jsonify({
            "success": True,
            "message": "Orquestrador resetado com sucesso",
            "timestamp": datetime.now().isoformat()
        }), 200

    except Exception as e:
        logger.error(f"❌ Erro ao resetar orquestrador: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

# Rota para compatibilidade com interface atual
@analysis_bp.route('/execute_analysis', methods=['POST'])
def execute_analysis_compatibility():
    """Rota de compatibilidade que redireciona para nova metodologia"""
    logger.info("🔄 Redirecionando para nova metodologia aprimorada")
    return execute_complete_analysis()

@analysis_bp.route('/analyze', methods=['POST'])
def analyze_compatibility():
    """Rota de compatibilidade /api/analyze que redireciona para nova metodologia"""
    logger.info("🔄 Redirecionando /api/analyze para nova metodologia aprimorada")
    return execute_complete_analysis()

@analysis_bp.route('/start_data_collection', methods=['POST'])
def start_data_collection():
    """Inicia coleta de dados - nova rota compatível"""
    try:
        data = request.get_json()
        session_id = f"session_{int(time.time() * 1000)}_{random.randint(100000, 999999)}"

        # Importa o coletor massivo
        from services.massive_data_collector import massive_data_collector

        # Executa coleta de dados
        result = massive_data_collector.collect_comprehensive_data(
            produto=data.get('produto', ''),
            nicho=data.get('nicho', ''),
            publico=data.get('publico', ''),
            session_id=session_id
        )

        return jsonify({
            "success": True,
            "session_id": session_id,
            "message": "Coleta de dados concluída",
            "data": result
        })

    except Exception as e:
        logger.error(f"Erro na coleta de dados: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

# Novos endpoints para as 3 etapas
@analysis_bp.route('/collection/start', methods=['POST'])
def start_collection():
    """Etapa 1: Inicia coleta massiva de dados"""
    try:
        data = request.get_json()
        
        # Gera session_id se não fornecido
        session_id = data.get('session_id')
        if not session_id:
            import time
            import uuid
            session_id = f"session_{int(time.time() * 1000)}_{uuid.uuid4().hex[:8]}"
        
        # Importa o coletor massivo
        from services.massive_data_collector import massive_data_collector
        
        # Executa coleta de forma assíncrona
        import asyncio
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(
                massive_data_collector.execute_massive_collection(
                    query=data.get('query', data.get('segmento', 'análise de mercado')),
                    context=data,
                    session_id=session_id
                )
            )
        finally:
            loop.close()
        
        return jsonify({
            "success": True,
            "session_id": session_id,
            "message": "Coleta de dados concluída",
            "data": result,
            "step": 1,
            "next_step": "/api/analysis/start"
        })
        
    except Exception as e:
        logger.error(f"Erro na coleta: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@analysis_bp.route('/analysis/start', methods=['POST'])
def start_analysis():
    """Etapa 2: Inicia análise e síntese com IA"""
    try:
        data = request.get_json()
        session_id = data.get('session_id')
        
        if not session_id:
            return jsonify({"success": False, "error": "session_id obrigatório"}), 400
        
        # Importa o motor de síntese
        from services.ai_synthesis_engine import ai_synthesis_engine
        
        # Executa síntese
        import asyncio
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(
                ai_synthesis_engine.analyze_and_synthesize(session_id)
            )
        finally:
            loop.close()
        
        return jsonify({
            "success": True,
            "session_id": session_id,
            "message": "Análise e síntese concluídas",
            "data": result,
            "step": 2,
            "next_step": "/api/generation/start"
        })
        
    except Exception as e:
        logger.error(f"Erro na análise: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@analysis_bp.route('/generation/start', methods=['POST'])
def start_generation():
    """Etapa 3: Inicia geração de módulos e relatório final"""
    try:
        data = request.get_json()
        session_id = data.get('session_id')
        
        if not session_id:
            return jsonify({"success": False, "error": "session_id obrigatório"}), 400
        
        # Importa processador de módulos e gerador de relatório
        from services.enhanced_module_processor import enhanced_module_processor
        from services.comprehensive_report_generator_v3 import comprehensive_report_generator_v3
        
        # Executa geração de módulos
        import asyncio
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            modules_result = loop.run_until_complete(
                enhanced_module_processor.generate_all_modules(session_id)
            )
        finally:
            loop.close()
        
        # Compila relatório final
        final_report = comprehensive_report_generator_v3.compile_final_markdown_report(session_id)
        
        return jsonify({
            "success": True,
            "session_id": session_id,
            "message": "Geração concluída com sucesso",
            "modules": modules_result,
            "final_report": final_report,
            "step": 3,
            "workflow_completed": True
        })
        
    except Exception as e:
        logger.error(f"Erro na geração: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@analysis_bp.route('/workflow/step1', methods=['POST'])
def workflow_step1():
    """Etapa 1: Coleta de dados"""
    try:
        data = request.get_json()
        session_id = f"session_{int(time.time() * 1000)}_{random.randint(100000, 999999)}"

        # Importa o coletor massivo
        from services.massive_data_collector import massive_data_collector

        # Executa coleta de dados
        result = massive_data_collector.collect_comprehensive_data(
            produto=data.get('produto', ''),
            nicho=data.get('nicho', ''),
            publico=data.get('publico', ''),
            session_id=session_id
        )

        return jsonify({
            "success": True,
            "session_id": session_id,
            "message": "Coleta de dados concluída",
            "data": result
        })

    except Exception as e:
        logger.error(f"Erro na etapa 1: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@analysis_bp.route('/analyze_data', methods=['POST'])
def analyze_data_endpoint():
    """Endpoint compatível para análise de dados"""
    try:
        data = request.get_json()
        session_id = data.get('session_id')

        if not session_id:
            return jsonify({"success": False, "error": "session_id obrigatório"}), 400

        # Importa o motor de síntese
        from services.ai_synthesis_engine import ai_synthesis_engine
        
        # Executa síntese com IA
        import asyncio
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(
                ai_synthesis_engine.analyze_and_synthesize(session_id)
            )
        finally:
            loop.close()

        return jsonify({
            "success": True,
            "session_id": session_id,
            "message": "Análise e síntese concluídas",
            "sintese": result.get("synthesis_data", {}),
            "synthesis_path": result.get("synthesis_path", "")
        })

    except Exception as e:
        logger.error(f"Erro na análise de dados: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@analysis_bp.route('/workflow/step2', methods=['POST'])
def workflow_step2():
    """Etapa 2: Análise e síntese com IA"""
    try:
        data = request.get_json()
        session_id = data.get('session_id')

        if not session_id:
            return jsonify({"success": False, "error": "session_id obrigatório"}), 400

        # Importa o AI manager
        from services.ai_manager import ai_manager

        # Carrega dados coletados
        import os
        session_dir = f"analyses_data/{session_id}"
        if not os.path.exists(session_dir):
            return jsonify({"success": False, "error": "Sessão não encontrada"}), 404

        # Lê relatório de coleta
        relatorio_path = f"{session_dir}/relatorio_coleta.md"
        if os.path.exists(relatorio_path):
            with open(relatorio_path, 'r', encoding='utf-8') as f:
                relatorio_content = f.read()
        else:
            relatorio_content = "Dados não encontrados"

        # Prompt para síntese
        prompt = f"""
        Analise os dados coletados e crie uma síntese estratégica completa.
        Utilize ferramentas de busca quando necessário para enriquecer a análise.

        Dados coletados:
        {relatorio_content}

        Crie um resumo estruturado em JSON com:
        - insights_principais
        - oportunidades_identificadas  
        - publico_alvo_refinado
        - estrategias_recomendadas
        - pontos_atencao
        """

        # Executa análise com ferramentas
        result = ai_manager.generate_with_tools(
            prompt=prompt,
            tools=['google_search']
        )

        # Salva síntese
        import json
        sintese_path = f"{session_dir}/resumo_sintese.json"
        with open(sintese_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)

        return jsonify({
            "success": True,
            "session_id": session_id,
            "message": "Análise e síntese concluídas",
            "sintese": result
        })

    except Exception as e:
        logger.error(f"Erro na etapa 2: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@analysis_bp.route('/generate_report', methods=['POST'])
def generate_report_endpoint():
    """Endpoint compatível para geração de relatório"""
    try:
        data = request.get_json()
        session_id = data.get('session_id')

        if not session_id:
            return jsonify({"success": False, "error": "session_id obrigatório"}), 400

        # Importa processador de módulos e gerador de relatório
        from services.enhanced_module_processor import enhanced_module_processor
        from services.comprehensive_report_generator_v3 import comprehensive_report_generator_v3

        # Executa geração de módulos de forma assíncrona
        import asyncio
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            modules_result = loop.run_until_complete(
                enhanced_module_processor.generate_all_modules(session_id)
            )
        finally:
            loop.close()
        
        # Compila relatório final
        final_report = comprehensive_report_generator_v3.compile_final_markdown_report(session_id)

        return jsonify({
            "success": True,
            "session_id": session_id,
            "message": "Relatório final gerado com sucesso",
            "modules": modules_result,
            "final_report": final_report
        })

    except Exception as e:
        logger.error(f"Erro na geração de relatório: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@analysis_bp.route('/workflow/step3', methods=['POST'])
def workflow_step3():
    """Etapa 3: Geração de módulos e relatório final"""
    try:
        data = request.get_json()
        session_id = data.get('session_id')

        if not session_id:
            return jsonify({"success": False, "error": "session_id obrigatório"}), 400

        # Importa processador de módulos
        from services.enhanced_module_processor import enhanced_module_processor

        # Gera todos os módulos
        modules_result = enhanced_module_processor.generate_all_modules(session_id)

        # Gera relatório final
        from services.comprehensive_report_generator_v3 import comprehensive_report_generator_v3

        final_report = comprehensive_report_generator_v3.generate_final_report(session_id)

        return jsonify({
            "success": True,
            "session_id": session_id,
            "message": "Relatório final gerado com sucesso",
            "modules": modules_result,
            "final_report": final_report
        })

    except Exception as e:
        logger.error(f"Erro na etapa 3: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@analysis_bp.route('/workflow/complete', methods=['POST'])
def workflow_complete():
    """Executa workflow completo em 3 etapas"""
    try:
        data = request.get_json()

        # Etapa 1: Coleta
        step1_response = workflow_step1()
        step1_data = step1_response.get_json()

        if not step1_data.get('success'):
            return step1_response

        session_id = step1_data['session_id']

        # Etapa 2: Análise
        step2_response = workflow_step2()
        step2_data = step2_response.get_json()

        if not step2_data.get('success'):
            return step2_response

        # Etapa 3: Relatório
        step3_response = workflow_step3()

        return step3_response

    except Exception as e:
        logger.error(f"Erro no workflow completo: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@analysis_bp.route('/progress/<session_id>')
def get_progress(session_id):
    """Obtém progresso da análise"""
    try:
        progress_data = progress_tracker.get_progress(session_id)

        if not progress_data:
            return jsonify({
                'status': 'not_found',
                'message': f'Sessão {session_id} não encontrada'
            }), 404

        return jsonify(progress_data)

    except Exception as e:
        logger.error(f"Erro ao obter progresso {session_id}: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@analysis_bp.route('/status/<session_id>')
def check_analysis_status(session_id):
    """Verifica status detalhado de uma análise"""
    try:
        # Verifica se a análise está em andamento
        progress_data = progress_tracker.get_progress(session_id)

        if progress_data:
            return jsonify({
                'status': 'running',
                'progress': progress_data.get('progress_percentage', 0),
                'current_step': progress_data.get('current_step', ''),
                'message': progress_data.get('message', ''),
                'can_continue': True
            })

        # Verifica se existe resultado salvo
        try:
            from pathlib import Path
            reports_dir = Path('analyses_data/reports')
            reports_dir.mkdir(exist_ok=True)

            # Procura por arquivos de relatório da sessão
            report_files = list(reports_dir.glob(f'*{session_id}*'))

            if report_files:
                return jsonify({
                    'status': 'completed',
                    'progress': 100,
                    'message': 'Análise concluída',
                    'can_continue': False,
                    'report_available': True
                })
        except Exception:
            pass

        return jsonify({
            'status': 'not_found',
            'progress': 0,
            'message': 'Análise não encontrada',
            'can_continue': False
        }), 404

    except Exception as e:
        logger.error(f"Erro ao verificar status {session_id}: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e),
            'can_continue': False
        }), 500