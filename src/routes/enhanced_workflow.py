#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ARQV30 Enhanced v3.0 - Enhanced Workflow Routes
Rotas para o workflow aprimorado em 3 etapas
"""

import logging
import time
import uuid
import asyncio
import os
import glob
import json
from datetime import datetime
from typing import Dict, Any  # Import necessário para Dict e Any
from pathlib import Path
from flask import Blueprint, request, jsonify, send_file

# --- CORRECTED IMPORTS ---
# Import the class, not a non-existent name
from services.real_search_orchestrator import real_search_orchestrator
from services.viral_content_analyzer import viral_content_analyzer
from services.enhanced_synthesis_engine import enhanced_synthesis_engine
from services.enhanced_module_processor import enhanced_module_processor
from services.comprehensive_report_generator_v3 import comprehensive_report_generator_v3
from services.auto_save_manager import salvar_etapa
# Import the ViralImageFinder CLASS
from services.viral_integration_service import ViralImageFinder

logger = logging.getLogger(__name__)

enhanced_workflow_bp = Blueprint('enhanced_workflow', __name__)

# --- CREATE AN INSTANCE OF THE SERVICE ---
# Create an instance of ViralImageFinder to use its methods.
# Using the default config loading from the class __init__.
# If you need specific config, pass it here.
viral_integration_service = ViralImageFinder()

# --- REST OF THE FILE REMAINS THE SAME ---
# (The rest of your routes code follows exactly as before,
# now using the correctly instantiated `viral_integration_service`)

@enhanced_workflow_bp.route('/workflow/step1/start', methods=['POST'])
def start_step1_collection():
    """ETAPA 1: Coleta Massiva de Dados com Screenshots"""
    try:
        data = request.get_json()

        # Gera session_id único
        session_id = f"session_{int(time.time() * 1000)}_{uuid.uuid4().hex[:8]}"

        # Extrai parâmetros
        segmento = data.get('segmento', '').strip()
        produto = data.get('produto', '').strip()
        publico = data.get('publico', '').strip()

        # Validação
        if not segmento:
            return jsonify({"error": "Segmento é obrigatório"}), 400

        # Constrói query de pesquisa
        query_parts = [segmento]
        if produto:
            query_parts.append(produto)
        query_parts.extend(["Brasil", "2025"])

        query = " ".join(query_parts)

        # Contexto da análise
        context = {
            "segmento": segmento,
            "produto": produto,
            "publico": publico,
            "query_original": query,
            "etapa": 1,
            "workflow_type": "enhanced_v3"
        }

        logger.info(f"🚀 ETAPA 1 INICIADA - Sessão: {session_id}")
        logger.info(f"🔍 Query: {query}")

        # Salva início da etapa 1
        salvar_etapa("etapa1_iniciada", {
            "session_id": session_id,
            "query": query,
            "context": context,
            "timestamp": datetime.now().isoformat()
        }, categoria="workflow")

        # Executa coleta massiva em thread separada
        def execute_collection():
            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)

                try:
                    # PRIMEIRA ETAPA: Busca viral (nova integração)
                    logger.info(f"🔥 Executando busca viral para: {query}")
                    # --- CORRECTED CALL ---
                    # Call the find_viral_images method which returns a list and filepath
                    viral_data = loop.run_until_complete(
                        viral_integration_service.find_viral_images(query=query)
                    )
                    # The method returns a tuple (List[ViralImage], str), extract list
                    viral_results_list = viral_data[0] if viral_data and len(viral_data) > 0 else []
                    # Convert ViralImage dataclass objects to dictionaries for JSON serialization
                    viral_results_dicts = [img.__dict__ for img in viral_results_list]

                    # Package results into a dictionary structure similar to the old function's expected output
                    viral_results = {
                         "search_completed_at": datetime.now().isoformat(),
                         "total_images_found": len(viral_results_list),
                         # Assuming image_path is populated if saved
                         "total_images_saved": len([img for img in viral_results_list if img.image_path]),
                         "platforms_searched": list(set(img.platform for img in viral_results_list)), # Unique platforms
                         "aggregated_metrics": {
                             "total_engagement_score": sum(img.engagement_score for img in viral_results_list),
                             "average_engagement": sum(img.engagement_score for img in viral_results_list) / len(viral_results_list) if viral_results_list else 0,
                             "total_estimated_views": sum(img.views_estimate for img in viral_results_list),
                             "total_estimated_likes": sum(img.likes_estimate for img in viral_results_list),
                             "top_performing_platform": max(set(img.platform for img in viral_results_list), key=[img.platform for img in viral_results_list].count) if viral_results_list else None
                         },
                         "viral_images": viral_results_dicts,
                         "fallback_used": False # Assuming success means no fallback for now
                     }

                    # Salva resultados do viral
                    salvar_etapa("viral_search_completed", {
                        "session_id": session_id,
                        "viral_results": viral_results,
                        "timestamp": datetime.now().isoformat()
                    }, categoria="workflow")

                    # SEGUNDA ETAPA: Busca massiva real
                    logger.info(f"🌐 Executando busca massiva para: {query}")
                    search_results = loop.run_until_complete(
                        real_search_orchestrator.execute_massive_real_search(
                            query=query,
                            context=context,
                            session_id=session_id
                        )
                    )

                    # TERCEIRA ETAPA: Analisa e captura conteúdo viral adicional
                    logger.info(f"📸 Analisando conteúdo viral adicional")
                    viral_analysis = loop.run_until_complete(
                        viral_content_analyzer.analyze_and_capture_viral_content(
                            search_results=search_results,
                            session_id=session_id,
                            max_captures=15
                        )
                    )

                finally:
                    loop.close()

                # Gera relatório de coleta incluindo dados do viral
                collection_report = _generate_collection_report(
                    search_results, viral_analysis, session_id, context, viral_results
                )

                # Salva relatório
                _save_collection_report(collection_report, session_id)

                # Salva resultado da etapa 1
                salvar_etapa("etapa1_concluida", {
                    "session_id": session_id,
                    "search_results": search_results,
                    "viral_analysis": viral_analysis,
                    "viral_results": viral_results,
                    "collection_report_generated": True,
                    "timestamp": datetime.now().isoformat()
                }, categoria="workflow")

                logger.info(f"✅ ETAPA 1 CONCLUÍDA - Sessão: {session_id}")

            except Exception as e:
                logger.error(f"❌ Erro na execução da Etapa 1: {e}")
                salvar_etapa("etapa1_erro", {
                    "session_id": session_id,
                    "error": str(e),
                    "timestamp": datetime.now().isoformat()
                }, categoria="workflow")

        # Inicia execução em background
        import threading
        thread = threading.Thread(target=execute_collection, daemon=True)
        thread.start()

        return jsonify({
            "success": True,
            "session_id": session_id,
            "message": "Etapa 1 iniciada: Coleta massiva de dados",
            "query": query,
            "estimated_duration": "3-5 minutos",
            "next_step": "/api/workflow/step2/start",
            "status_endpoint": f"/api/workflow/status/{session_id}"
        }), 200

    except Exception as e:
        logger.error(f"❌ Erro ao iniciar Etapa 1: {e}")
        return jsonify({
            "success": False,
            "error": str(e),
            "message": "Falha ao iniciar coleta de dados"
        }), 500

@enhanced_workflow_bp.route('/workflow/step2/start', methods=['POST'])
def start_step2_synthesis():
    """ETAPA 2: Síntese com IA e Busca Ativa"""
    try:
        data = request.get_json()
        session_id = data.get('session_id')

        if not session_id:
            return jsonify({"error": "session_id é obrigatório"}), 400

        logger.info(f"🧠 ETAPA 2 INICIADA - Síntese para sessão: {session_id}")

        # Salva início da etapa 2
        salvar_etapa("etapa2_iniciada", {
            "session_id": session_id,
            "timestamp": datetime.now().isoformat()
        }, categoria="workflow")

        # Executa síntese em thread separada
        def execute_synthesis():
            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)

                try:
                    # Executa síntese master com busca ativa
                    synthesis_result = loop.run_until_complete(
                        enhanced_synthesis_engine.execute_enhanced_synthesis(
                            session_id=session_id,
                            synthesis_type="master_synthesis"
                        )
                    )

                    # Executa síntese comportamental
                    behavioral_result = loop.run_until_complete(
                        enhanced_synthesis_engine.execute_behavioral_synthesis(session_id)
                    )

                    # Executa síntese de mercado
                    market_result = loop.run_until_complete(
                        enhanced_synthesis_engine.execute_market_synthesis(session_id)
                    )

                finally:
                    loop.close()

                # Salva resultado da etapa 2
                salvar_etapa("etapa2_concluida", {
                    "session_id": session_id,
                    "synthesis_result": synthesis_result,
                    "behavioral_result": behavioral_result,
                    "market_result": market_result,
                    "timestamp": datetime.now().isoformat()
                }, categoria="workflow")

                logger.info(f"✅ ETAPA 2 CONCLUÍDA - Sessão: {session_id}")

            except Exception as e:
                logger.error(f"❌ Erro na execução da Etapa 2: {e}")
                salvar_etapa("etapa2_erro", {
                    "session_id": session_id,
                    "error": str(e),
                    "timestamp": datetime.now().isoformat()
                }, categoria="workflow")

        # Inicia execução em background
        import threading
        thread = threading.Thread(target=execute_synthesis, daemon=True)
        thread.start()

        return jsonify({
            "success": True,
            "session_id": session_id,
            "message": "Etapa 2 iniciada: Síntese com IA e busca ativa",
            "estimated_duration": "2-4 minutos",
            "next_step": "/api/workflow/step3/start",
            "status_endpoint": f"/api/workflow/status/{session_id}"
        }), 200

    except Exception as e:
        logger.error(f"❌ Erro ao iniciar Etapa 2: {e}")
        return jsonify({
            "success": False,
            "error": str(e),
            "message": "Falha ao iniciar síntese"
        }), 500

@enhanced_workflow_bp.route('/workflow/step3/start', methods=['POST'])
def start_step3_generation():
    """ETAPA 3: Geração dos 16 Módulos e Relatório Final"""
    try:
        data = request.get_json()
        session_id = data.get('session_id')

        if not session_id:
            return jsonify({"error": "session_id é obrigatório"}), 400

        logger.info(f"📝 ETAPA 3 INICIADA - Geração para sessão: {session_id}")

        # Salva início da etapa 3
        salvar_etapa("etapa3_iniciada", {
            "session_id": session_id,
            "timestamp": datetime.now().isoformat()
        }, categoria="workflow")

        # Executa geração em thread separada
        def execute_generation():
            try:
                # Gera todos os 16 módulos
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

                # Salva resultado da etapa 3
                salvar_etapa("etapa3_concluida", {
                    "session_id": session_id,
                    "modules_result": modules_result,
                    "final_report": final_report,
                    "timestamp": datetime.now().isoformat()
                }, categoria="workflow")

                logger.info(f"✅ ETAPA 3 CONCLUÍDA - Sessão: {session_id}")
                logger.info(f"📊 {modules_result.get('successful_modules', 0)}/16 módulos gerados")

            except Exception as e:
                logger.error(f"❌ Erro na execução da Etapa 3: {e}")
                salvar_etapa("etapa3_erro", {
                    "session_id": session_id,
                    "error": str(e),
                    "timestamp": datetime.now().isoformat()
                }, categoria="workflow")

        # Inicia execução em background
        import threading
        thread = threading.Thread(target=execute_generation, daemon=True)
        thread.start()

        return jsonify({
            "success": True,
            "session_id": session_id,
            "message": "Etapa 3 iniciada: Geração de 16 módulos",
            "estimated_duration": "4-6 minutos",
            "modules_to_generate": 16,
            "status_endpoint": f"/api/workflow/status/{session_id}"
        }), 200

    except Exception as e:
        logger.error(f"❌ Erro ao iniciar Etapa 3: {e}")
        return jsonify({
            "success": False,
            "error": str(e),
            "message": "Falha ao iniciar geração de módulos"
        }), 500

@enhanced_workflow_bp.route('/workflow/complete', methods=['POST'])
def execute_complete_workflow():
    """Executa workflow completo em sequência"""
    try:
        data = request.get_json()

        # Gera session_id único
        session_id = f"session_{int(time.time() * 1000)}_{uuid.uuid4().hex[:8]}"

        logger.info(f"🚀 WORKFLOW COMPLETO INICIADO - Sessão: {session_id}")

        # Executa workflow completo em thread separada
        def execute_full_workflow():
            try:
                # ETAPA 1: Coleta
                logger.info("🌊 Executando Etapa 1: Coleta massiva")

                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)

                try:
                    # Constrói query
                    segmento = data.get('segmento', '').strip()
                    produto = data.get('produto', '').strip()
                    query = f"{segmento} {produto} Brasil 2024 mercado".strip()
                    context = {
                        "segmento": segmento,
                        "produto": produto,
                        "publico": data.get('publico', ''),
                        "preco": data.get('preco', ''),
                        "objetivo_receita": data.get('objetivo_receita', ''),
                        "workflow_type": "complete"
                    }

                    # PRIMEIRA ETAPA: Busca viral
                    logger.info(f"🔥 Executando busca viral para: {query}")
                    # --- CORRECTED CALL ---
                    viral_data = loop.run_until_complete(
                        viral_integration_service.find_viral_images(query=query)
                    )
                    viral_results_list = viral_data[0] if viral_data and len(viral_data) > 0 else []
                    viral_results_dicts = [img.__dict__ for img in viral_results_list]
                    viral_results = {
                         "search_completed_at": datetime.now().isoformat(),
                         "total_images_found": len(viral_results_list),
                         "total_images_saved": len([img for img in viral_results_list if img.image_path]),
                         "platforms_searched": list(set(img.platform for img in viral_results_list)),
                         "aggregated_metrics": {
                             "total_engagement_score": sum(img.engagement_score for img in viral_results_list),
                             "average_engagement": sum(img.engagement_score for img in viral_results_list) / len(viral_results_list) if viral_results_list else 0,
                             "total_estimated_views": sum(img.views_estimate for img in viral_results_list),
                             "total_estimated_likes": sum(img.likes_estimate for img in viral_results_list),
                             "top_performing_platform": max(set(img.platform for img in viral_results_list), key=[img.platform for img in viral_results_list].count) if viral_results_list else None
                         },
                         "viral_images": viral_results_dicts,
                         "fallback_used": False
                     }

                    # SEGUNDA ETAPA: Executa busca massiva
                    logger.info(f"🌐 Executando busca massiva para: {query}")
                    search_results = loop.run_until_complete(
                        real_search_orchestrator.execute_massive_real_search(
                            query=query,
                            context=context,
                            session_id=session_id
                        )
                    )

                    # TERCEIRA ETAPA: Analisa conteúdo viral adicional
                    logger.info(f"📸 Analisando conteúdo viral adicional")
                    viral_analysis = loop.run_until_complete(
                        viral_content_analyzer.analyze_and_capture_viral_content(
                            search_results=search_results,
                            session_id=session_id
                        )
                    )

                    # Gera relatório de coleta incluindo dados do viral
                    collection_report = _generate_collection_report(
                        search_results, viral_analysis, session_id, context, viral_results
                    )
                    _save_collection_report(collection_report, session_id)

                    # ETAPA 2: Síntese
                    logger.info("🧠 Executando Etapa 2: Síntese com IA")

                    synthesis_result = loop.run_until_complete(
                        enhanced_synthesis_engine.execute_enhanced_synthesis(session_id)
                    )

                    # ETAPA 3: Geração de módulos
                    logger.info("📝 Executando Etapa 3: Geração de módulos")

                    modules_result = loop.run_until_complete(
                        enhanced_module_processor.generate_all_modules(session_id)
                    )

                    # Compila relatório final
                    final_report = comprehensive_report_generator_v3.compile_final_markdown_report(session_id)

                finally:
                    loop.close()

                # Salva resultado final
                salvar_etapa("workflow_completo", {
                    "session_id": session_id,
                    "search_results": search_results,
                    "viral_analysis": viral_analysis,
                    "viral_results": viral_results,
                    "synthesis_result": synthesis_result,
                    "modules_result": modules_result,
                    "final_report": final_report,
                    "timestamp": datetime.now().isoformat()
                }, categoria="workflow")

                logger.info(f"✅ WORKFLOW COMPLETO CONCLUÍDO - Sessão: {session_id}")

            except Exception as e:
                logger.error(f"❌ Erro no workflow completo: {e}")
                salvar_etapa("workflow_erro", {
                    "session_id": session_id,
                    "error": str(e),
                    "timestamp": datetime.now().isoformat()
                }, categoria="workflow")

        # Inicia execução em background
        import threading
        thread = threading.Thread(target=execute_full_workflow, daemon=True)
        thread.start()

        return jsonify({
            "success": True,
            "session_id": session_id,
            "message": "Workflow completo iniciado",
            "estimated_total_duration": "8-15 minutos",
            "steps": [
                "Etapa 1: Coleta massiva (3-5 min)",
                "Etapa 2: Síntese com IA (2-4 min)",
                "Etapa 3: Geração de módulos (4-6 min)"
            ],
            "status_endpoint": f"/api/workflow/status/{session_id}"
        }), 200

    except Exception as e:
        logger.error(f"❌ Erro ao iniciar workflow completo: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@enhanced_workflow_bp.route('/workflow/status/<session_id>', methods=['GET'])
def get_workflow_status(session_id):
    """Obtém status do workflow"""
    try:
        # Verifica arquivos salvos para determinar status

        status = {
            "session_id": session_id,
            "current_step": 0,
            "step_status": {
                "step1": "pending",
                "step2": "pending",
                "step3": "pending"
            },
            "progress_percentage": 0,
            "estimated_remaining": "Calculando...",
            "last_update": datetime.now().isoformat()
        }

        # Verifica se etapa 1 foi concluída
        if os.path.exists(f"analyses_data/{session_id}/relatorio_coleta.md"):
            status["step_status"]["step1"] = "completed"
            status["current_step"] = 1
            status["progress_percentage"] = 33

        # Verifica se etapa 2 foi concluída
        if os.path.exists(f"analyses_data/{session_id}/resumo_sintese.json"):
            status["step_status"]["step2"] = "completed"
            status["current_step"] = 2
            status["progress_percentage"] = 66

        # Verifica se etapa 3 foi concluída
        if os.path.exists(f"analyses_data/{session_id}/relatorio_final.md"):
            status["step_status"]["step3"] = "completed"
            status["current_step"] = 3
            status["progress_percentage"] = 100
            status["estimated_remaining"] = "Concluído"

        # Verifica se há erros
        error_files = [
            f"relatorios_intermediarios/workflow/etapa1_erro*{session_id}*",
            f"relatorios_intermediarios/workflow/etapa2_erro*{session_id}*",
            f"relatorios_intermediarios/workflow/etapa3_erro*{session_id}*"
        ]

        for pattern in error_files:
            if glob.glob(pattern):
                status["error"] = "Erro detectado em uma das etapas"
                break

        return jsonify(status), 200

    except Exception as e:
        logger.error(f"❌ Erro ao obter status: {e}")
        return jsonify({
            "session_id": session_id,
            "error": str(e),
            "status": "error"
        }), 500

@enhanced_workflow_bp.route('/workflow/results/<session_id>', methods=['GET'])
def get_workflow_results(session_id):
    """Obtém resultados do workflow"""
    try:

        results = {
            "session_id": session_id,
            "available_files": [],
            "final_report_available": False,
            "modules_generated": 0,
            "screenshots_captured": 0
        }

        # Verifica relatório final
        final_report_path = f"analyses_data/{session_id}/relatorio_final.md"
        if os.path.exists(final_report_path):
            results["final_report_available"] = True
            results["final_report_path"] = final_report_path

        # Conta módulos gerados
        modules_dir = f"analyses_data/{session_id}/modules"
        if os.path.exists(modules_dir):
            modules = [f for f in os.listdir(modules_dir) if f.endswith('.md')]
            results["modules_generated"] = len(modules)
            results["modules_list"] = modules

        # Conta screenshots
        files_dir = f"analyses_data/files/{session_id}"
        if os.path.exists(files_dir):
            screenshots = [f for f in os.listdir(files_dir) if f.endswith('.png')]
            results["screenshots_captured"] = len(screenshots)
            results["screenshots_list"] = screenshots

        # Lista todos os arquivos disponíveis
        session_dir = f"analyses_data/{session_id}"
        if os.path.exists(session_dir):
            for root, dirs, files in os.walk(session_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    relative_path = os.path.relpath(file_path, session_dir)
                    results["available_files"].append({
                        "name": file,
                        "path": relative_path,
                        "size": os.path.getsize(file_path),
                        "type": file.split('.')[-1] if '.' in file else 'unknown'
                    })

        return jsonify(results), 200

    except Exception as e:
        logger.error(f"❌ Erro ao obter resultados: {e}")
        return jsonify({
            "session_id": session_id,
            "error": str(e)
        }), 500

@enhanced_workflow_bp.route('/workflow/viral_results/<session_id>', methods=['GET'])
def get_viral_results(session_id):
    """Obtém resultados específicos do módulo viral"""
    try:
        # Verifica se existem dados salvos do viral
        viral_data_files = glob.glob(f"relatorios_intermediarios/workflow/viral_search_completed*{session_id}*")

        if not viral_data_files:
            return jsonify({
                "session_id": session_id,
                "viral_available": False,
                "message": "Dados do módulo viral não encontrados"
            }), 404

        # Carrega o arquivo mais recente
        latest_file = max(viral_data_files, key=os.path.getctime)

        try:
            with open(latest_file, 'r', encoding='utf-8') as f:
                viral_data = json.load(f)

            viral_results = viral_data.get('viral_results', {})

            # Prepara resposta otimizada para o frontend
            response = {
                "session_id": session_id,
                "viral_available": True,
                "search_completed_at": viral_results.get('search_completed_at'),
                "total_images_found": viral_results.get('total_images_found', 0),
                "total_images_saved": viral_results.get('total_images_saved', 0),
                "platforms_searched": viral_results.get('platforms_searched', []),
                "aggregated_metrics": viral_results.get('aggregated_metrics', {}),
                "viral_images": viral_results.get('viral_images', []),
                "fallback_used": viral_results.get('fallback_used', False)
            }

            # Adiciona URLs relativas para as imagens locais
            for image in response["viral_images"]:
                if image.get('local_image_path'): # Adjust key if needed based on dict structure
                    # Converte caminho absoluto para relativo ao diretório de análises
                    try:
                        # Adjust path logic based on how images are actually saved by ViralImageFinder
                        # This assumes images are saved under analyses_data/viral_images_data or similar
                        # You might need to adjust the base path here.
                        # Let's assume images are saved by ViralImageFinder in its configured output_dir
                        # and we link relatively from the web root (analyses_data)
                        # If image['image_path'] contains the full local path:
                        if image.get('image_path'):
                             # Make path relative to analyses_data for web access
                             abs_path = image['image_path']
                             analyses_base = os.path.abspath("analyses_data") # Get absolute path of analyses_data
                             abs_img_path = os.path.abspath(abs_path) # Get absolute path of the image
                             if abs_img_path.startswith(analyses_base):
                                 # Calculate the relative path from analyses_data
                                 rel_img_path = os.path.relpath(abs_img_path, analyses_base)
                                 image['frontend_image_url'] = f"/files/analyses_data/{rel_img_path}"
                             else:
                                 # Image is outside analyses_data, cannot serve easily
                                 image['frontend_image_url'] = None
                        else:
                             image['frontend_image_url'] = None
                    except Exception as e:
                        logger.warning(f"Could not generate frontend URL for image: {e}")
                        image['frontend_image_url'] = None

            return jsonify(response), 200

        except json.JSONDecodeError:
            return jsonify({
                "session_id": session_id,
                "viral_available": False,
                "error": "Erro ao decodificar dados do viral"
            }), 500

    except Exception as e:
        logger.error(f"❌ Erro ao obter resultados virais: {e}")
        return jsonify({
            "session_id": session_id,
            "viral_available": False,
            "error": str(e)
        }), 500

@enhanced_workflow_bp.route('/workflow/viral_image/<session_id>/<image_name>', methods=['GET'])
def serve_viral_image(session_id, image_name):
    """Serve imagens virais salvas localmente"""
    try:
        # Adjust path based on where ViralImageFinder actually saves images
        # Assuming it saves to config['output_dir'] which defaults to 'viral_images_data'
        # And images are saved directly there or in subdirectories
        # This route might need adjustment based on actual file structure.
        # Let's try a common pattern: images saved in a session-specific folder within output_dir
        # ViralImageFinder doesn't seem to use session_id directly for saving images.
        # It saves to self.config['images_dir'] (default 'downloaded_images') or self.config['screenshots_dir']
        # We need to find the image by name potentially across these directories or use the path stored in ViralImage.image_path

        # Option 1: Search in the standard image download directory
        # images_base_dir = viral_integration_service.config.get('images_dir', 'downloaded_images')
        # image_path = Path(images_base_dir) / image_name

        # Option 2: Search in the standard screenshot directory
        # screenshots_base_dir = viral_integration_service.config.get('screenshots_dir', 'screenshots')
        # image_path = Path(screenshots_base_dir) / image_name

        # Option 3: Use the path stored in the saved data (most robust)
        # This requires accessing the saved viral data to find the image_path for the specific image_name.
        # This is complex in a simple route without state/session data access.

        # Simplified approach: Assume images are in 'downloaded_images' or 'screenshots'
        # and search for the filename.
        # This is fragile but might work if filenames are unique.
        potential_paths = [
            Path(viral_integration_service.config.get('images_dir', 'downloaded_images')) / image_name,
            Path(viral_integration_service.config.get('screenshots_dir', 'screenshots')) / image_name,
            # Add other potential directories if needed
        ]

        image_path = None
        for p in potential_paths:
            if p.exists():
                image_path = p
                break

        if not image_path or not image_path.exists():
             # Try searching recursively in the images_dir if not found directly
             images_base = Path(viral_integration_service.config.get('images_dir', 'downloaded_images'))
             if images_base.exists():
                 found_files = list(images_base.rglob(image_name))
                 if found_files:
                     image_path = found_files[0] # Take the first found

        if not image_path or not image_path.exists():
             # Try searching recursively in the screenshots_dir if not found directly
             screenshots_base = Path(viral_integration_service.config.get('screenshots_dir', 'screenshots'))
             if screenshots_base.exists():
                 found_files = list(screenshots_base.rglob(image_name))
                 if found_files:
                     image_path = found_files[0] # Take the first found

        if not image_path or not image_path.exists():
            return jsonify({"error": "Imagem não encontrada"}), 404

        return send_file(str(image_path))

    except Exception as e:
        logger.error(f"❌ Erro ao servir imagem viral: {e}")
        return jsonify({"error": str(e)}), 500

@enhanced_workflow_bp.route('/workflow/download/<session_id>/<file_type>', methods=['GET'])
def download_workflow_file(session_id, file_type):
    """Download de arquivos do workflow"""
    try:
        # Define o caminho base (sem src/)
        base_path = os.path.join("analyses_data", session_id)

        if file_type == "final_report":
            # Tenta primeiro o relatorio_final.md, depois o completo como fallback
            file_path = os.path.join(base_path, "relatorio_final.md")
            if not os.path.exists(file_path):
                file_path = os.path.join(base_path, "relatorio_final_completo.md")
            filename = f"relatorio_final_{session_id}.md"
        elif file_type == "complete_report":
            file_path = os.path.join(base_path, "relatorio_final_completo.md")
            filename = f"relatorio_completo_{session_id}.md"
        else:
            return jsonify({"error": "Tipo de relatório inválido"}), 400

        if not os.path.exists(file_path):
            return jsonify({"error": "Arquivo não encontrado"}), 404

        return send_file(
            file_path,
            as_attachment=True,
            download_name=filename
        )

    except Exception as e:
        logger.error(f"❌ Erro no download: {e}")
        return jsonify({"error": str(e)}), 500

# --- Funções auxiliares ---
def _generate_collection_report(
    search_results: Dict[str, Any],
    viral_analysis: Dict[str, Any],
    session_id: str,
    context: Dict[str, Any],
    viral_results: Dict[str, Any] = None
) -> str:
    """Gera relatório consolidado de coleta"""

    # Função auxiliar para formatar números com segurança
    def safe_format_int(value):
        try:
            # Tenta converter para int e formatar com separador de milhar
            return f"{int(value):,}"
        except (ValueError, TypeError):
            # Se falhar, retorna 'N/A' ou o valor original como string
            return str(value) if value is not None else 'N/A'

    report = f"""# RELATÓRIO DE COLETA MASSIVA - ARQV30 Enhanced v3.0

**Sessão:** {session_id}  
**Query:** {search_results.get('query', 'N/A')}  
**Iniciado em:** {search_results.get('search_started', 'N/A')}  
**Duração:** {search_results.get('statistics', {}).get('search_duration', 0):.2f} segundos

---

## RESUMO DA COLETA MASSIVA

### Estatísticas Gerais:
- **Total de Fontes:** {search_results.get('statistics', {}).get('total_sources', 0)}
- **URLs Únicas:** {search_results.get('statistics', {}).get('unique_urls', 0)}
- **Conteúdo Extraído:** {safe_format_int(search_results.get('statistics', {}).get('content_extracted', 0))} caracteres
- **Provedores Utilizados:** {len(search_results.get('providers_used', []))}
- **Conteúdo Viral Identificado:** {len(viral_analysis.get('viral_content_identified', []))}
- **Screenshots Capturados:** {len(viral_analysis.get('screenshots_captured', []))}

### Estatísticas do Módulo Viral:
"""

    # Adiciona estatísticas do viral se disponível
    if viral_results and not viral_results.get('fallback_used', False):
        viral_metrics = viral_results.get('aggregated_metrics', {})
        report += f"""- **Imagens Virais Encontradas:** {viral_results.get('total_images_found', 0)}
- **Imagens Salvas Localmente:** {viral_results.get('total_images_saved', 0)}
- **Plataformas Analisadas:** {', '.join(viral_results.get('platforms_searched', []))}
- **Score Total de Engajamento:** {safe_format_int(viral_metrics.get('total_engagement_score', 0))}
- **Engajamento Médio:** {viral_metrics.get('average_engagement', 0):.1f}
- **Visualizações Estimadas:** {safe_format_int(viral_metrics.get('total_estimated_views', 0))}
- **Likes Estimados:** {safe_format_int(viral_metrics.get('total_estimated_likes', 0))}
- **Plataforma Top:** {viral_metrics.get('top_performing_platform', 'N/A')}

"""
    else:
        report += """- **Status do Módulo Viral:** Não disponível ou falhou
- **Imagens Virais:** 0
- **Plataformas:** Nenhuma analisada

"""

    report += """### Provedores Utilizados:
"""
    providers = search_results.get('providers_used', [])
    if providers:
        report += "\n".join(f"- {provider}" for provider in providers) + "\n\n"
    else:
        report += "- Nenhum provedor listado\n\n"

    report += "---\n\n## RESULTADOS DE BUSCA WEB\n\n"

    # Adiciona resultados web
    web_results = search_results.get('web_results', [])
    if web_results:
        for i, result in enumerate(web_results[:15], 1):
            report += f"### {i}. {result.get('title', 'Sem título')}\n\n"
            report += f"**URL:** {result.get('url', 'N/A')}  \n"
            report += f"**Fonte:** {result.get('source', 'N/A')}  \n"
            report += f"**Relevância:** {result.get('relevance_score', 0):.2f}/1.0  \n"
            snippet = result.get('snippet', 'N/A')
            report += f"**Resumo:** {snippet[:200]}{'...' if len(snippet) > 200 else ''}  \n\n"
    else:
        report += "Nenhum resultado web encontrado.\n\n"

    # Adiciona resultados do YouTube
    youtube_results = search_results.get('youtube_results', [])
    if youtube_results:
        report += "---\n\n## RESULTADOS DO YOUTUBE\n\n"
        for i, result in enumerate(youtube_results[:10], 1):
            report += f"### {i}. {result.get('title', 'Sem título')}\n\n"
            report += f"**Canal:** {result.get('channel', 'N/A')}  \n"
            report += f"**Views:** {safe_format_int(result.get('view_count', 'N/A'))}  \n"
            report += f"**Likes:** {safe_format_int(result.get('like_count', 'N/A'))}  \n"
            report += f"**Comentários:** {safe_format_int(result.get('comment_count', 'N/A'))}  \n"
            report += f"**Score Viral:** {result.get('viral_score', 0):.2f}/10  \n"
            report += f"**URL:** {result.get('url', 'N/A')}  \n\n"
    else:
        report += "---\n\n## RESULTADOS DO YOUTUBE\n\nNenhum resultado do YouTube encontrado.\n\n"

    # Adiciona resultados de redes sociais
    social_results = search_results.get('social_results', [])
    if social_results:
        report += "---\n\n## RESULTADOS DE REDES SOCIAIS\n\n"
        for i, result in enumerate(social_results[:10], 1):
            report += f"### {i}. {result.get('title', 'Sem título')}\n\n"
            report += f"**Plataforma:** {result.get('platform', 'N/A').title() if result.get('platform') else 'N/A'}  \n"
            report += f"**Autor:** {result.get('author', 'N/A')}  \n"
            report += f"**Engajamento:** {result.get('viral_score', 0):.2f}/10  \n"
            report += f"**URL:** {result.get('url', 'N/A')}  \n"
            content = result.get('content', 'N/A')
            report += f"**Conteúdo:** {content[:150]}{'...' if len(content) > 150 else ''}  \n\n"
    else:
        report += "---\n\n## RESULTADOS DE REDES SOCIAIS\n\nNenhum resultado de rede social encontrado.\n\n"

    # Adiciona seção específica para resultados virais
    if viral_results and not viral_results.get('fallback_used', False):
        viral_images = viral_results.get('viral_images', [])
        if viral_images:
            report += "---\n\n## CONTEÚDO VIRAL COLETADO\n\n"

            # Top 10 imagens virais por engajamento
            top_viral = sorted(viral_images, key=lambda x: x.get('engagement_score', 0), reverse=True)[:10]

            for i, viral_img in enumerate(top_viral, 1):
                report += f"### {i}. {viral_img.get('title', 'Conteúdo Viral')}\n\n"
                report += f"**Plataforma:** {viral_img.get('platform', 'N/A').title()}  \n"
                report += f"**Score de Engajamento:** {viral_img.get('engagement_score', 0):.1f}  \n"
                report += f"**Autor:** {viral_img.get('author', 'Desconhecido')}  \n"
                report += f"**Seguidores do Autor:** {safe_format_int(viral_img.get('author_followers', 0))}  \n"
                report += f"**Visualizações Estimadas:** {safe_format_int(viral_img.get('views_estimate', 0))}  \n"
                report += f"**Likes Estimados:** {safe_format_int(viral_img.get('likes_estimate', 0))}  \n"
                report += f"**Comentários Estimados:** {safe_format_int(viral_img.get('comments_estimate', 0))}  \n"
                report += f"**Compartilhamentos Estimados:** {safe_format_int(viral_img.get('shares_estimate', 0))}  \n"
                report += f"**Data do Post:** {viral_img.get('post_date', 'N/A')[:10]}  \n"

                # Hashtags
                hashtags = viral_img.get('hashtags', [])
                if hashtags:
                    report += f"**Hashtags:** {', '.join(f'#{tag}' for tag in hashtags[:5])}  \n"

                # URL original
                if viral_img.get('post_url'): # Use post_url for original post link
                    report += f"**URL Original:** {viral_img.get('post_url')}  \n"

                # Imagem local se disponível
                # Use the image_path from the ViralImage object
                local_path = viral_img.get('image_path') # This is the path returned by ViralImageFinder
                if local_path and os.path.exists(local_path):
                    try:
                        # Make path relative to analyses_data for markdown linking
                        analyses_base = os.path.abspath("analyses_data")
                        abs_img_path = os.path.abspath(local_path)
                        if abs_img_path.startswith(analyses_base):
                            rel_img_path = os.path.relpath(abs_img_path, analyses_base)
                            # Ensure forward slashes for markdown
                            rel_img_path_md = rel_img_path.replace(os.sep, '/')
                            report += f"**Imagem Local:** ![Viral {i}](/files/{rel_img_path_md})  \n"
                        else:
                            # If image is outside analyses_data, link might not work or needs adjustment
                            report += f"**Imagem Local:** *Path outside analyses_data: {local_path}*  \n"
                    except Exception as e:
                        logger.warning(f"Error generating relative path for image {local_path}: {e}")
                        report += f"**Imagem Local:** *Erro ao gerar link: {local_path}*  \n"
                elif local_path:
                    # Path exists in data but file not found on disk
                    report += f"**Imagem Local:** *Arquivo não encontrado: {local_path}*  \n"
                else:
                   # No local path stored
                   report += f"**Imagem Local:** *Não disponível*  \n"

                # Descrição
                description = viral_img.get('description', '')
                if description:
                    report += f"**Descrição:** {description[:200]}{'...' if len(description) > 200 else ''}  \n"

                report += "\n"
        else:
            report += "---\n\n## CONTEÚDO VIRAL COLETADO\n\nNenhum conteúdo viral foi encontrado.\n\n"
    else:
        report += "---\n\n## CONTEÚDO VIRAL COLETADO\n\nMódulo viral não disponível ou falhou.\n\n"

    # Adiciona screenshots capturados
    screenshots = viral_analysis.get('screenshots_captured', [])
    if screenshots:
        report += "---\n\n## EVIDÊNCIAS VISUAIS CAPTURADAS\n\n"
        for i, screenshot in enumerate(screenshots, 1):
            report += f"### Screenshot {i}: {screenshot.get('title', 'Sem título')}\n\n"
            report += f"**Plataforma:** {screenshot.get('platform', 'N/A').title() if screenshot.get('platform') else 'N/A'}  \n"
            report += f"**Score Viral:** {screenshot.get('viral_score', 0):.2f}/10  \n"
            report += f"**URL Original:** {screenshot.get('url', 'N/A')}  \n"

            # Métricas de engajamento - CORRIGIDO AQUI
            metrics = screenshot.get('content_metrics', {})
            if metrics:
                # Usa a função auxiliar para formatar com segurança
                if 'views' in metrics:
                    report += f"**Views:** {safe_format_int(metrics['views'])}  \n"
                if 'likes' in metrics:
                    report += f"**Likes:** {safe_format_int(metrics['likes'])}  \n"
                if 'comments' in metrics:
                    report += f"**Comentários:** {safe_format_int(metrics['comments'])}  \n"

            # Verifica se o caminho da imagem existe antes de adicioná-lo
            img_path = screenshot.get('relative_path', '') # Use relative_path if stored by viral_content_analyzer
            # Ajuste o caminho base conforme a estrutura do seu projeto
            # full_img_path = os.path.join("analyses_data", "files", session_id, os.path.basename(img_path))
            # if img_path and os.path.exists(full_img_path):
            #      report += f"![Screenshot {i}]({img_path})  \n\n"
            # elif img_path: # Se o caminho existir, mas o arquivo não, mostra o caminho
            #      report += f"![Screenshot {i}]({img_path}) *(Imagem não encontrada localmente)*  \n\n"
            # else:
            #      report += "*Imagem não disponível.*  \n\n"

            # Assuming relative_path is relative to analyses_data/files/session_id
            if img_path:
                 # Ensure forward slashes for markdown
                 img_path_md = img_path.replace(os.sep, '/')
                 report += f"![Screenshot {i}](/files/{img_path_md})  \n\n"
            else:
                 report += "*Imagem não disponível.*  \n\n"
    else:
        report += "---\n\n## EVIDÊNCIAS VISUAIS CAPTURADAS\n\nNenhum screenshot foi capturado.\n\n"

    # Adiciona contexto da análise
    report += "---\n\n## CONTEXTO DA ANÁLISE\n\n"
    context_items_added = False
    for key, value in context.items():
        if value: # Só adiciona se o valor não for vazio/falso
            report += f"**{key.replace('_', ' ').title()}:** {value}  \n"
            context_items_added = True
    if not context_items_added:
         report += "Nenhum contexto adicional fornecido.\n"
    report += f"\n---\n\n*Relatório gerado automaticamente em {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}*"

    return report

def _save_collection_report(report_content: str, session_id: str):
    """Salva relatório de coleta"""
    try:
        session_dir = f"analyses_data/{session_id}"
        os.makedirs(session_dir, exist_ok=True)

        report_path = f"{session_dir}/relatorio_coleta.md"
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report_content)

        logger.info(f"✅ Relatório de coleta salvo: {report_path}")

    except Exception as e:
        logger.error(f"❌ Erro ao salvar relatório de coleta: {e}")
        # Opcional: Re-raise a exception se quiser que o erro pare a execução da etapa
        # raise

# --- O resto do seu código (outras funções, se houver) permanece inalterado ---
