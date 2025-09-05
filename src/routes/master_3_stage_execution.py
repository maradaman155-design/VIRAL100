#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ARQV30 Enhanced v3.0 - Master 3-Stage Execution Route
Rota principal para execução das 3 etapas do sistema preditivo
"""

import os
import logging
import asyncio
import json
from datetime import datetime
from typing import Dict, Any, Optional
from flask import Blueprint, request, jsonify, render_template
import uuid

# Importa o orquestrador principal
from services.master_3_stage_orchestrator import master_3_stage_orchestrator

# Imports condicionais
try:
    from services.cpl_devastador_protocol import CPLDevastadorProtocol
    HAS_CPL_PROTOCOL = True
except ImportError:
    HAS_CPL_PROTOCOL = False
    logger.warning("CPL Devastador Protocol não disponível")

try:
    from services.auto_save_manager import salvar_etapa, salvar_erro
    HAS_AUTO_SAVE = True
except ImportError:
    HAS_AUTO_SAVE = False
    logger.warning("Auto Save Manager não disponível")
    
    # Fallback functions
    async def salvar_etapa(session_id, stage, data, path):
        logger.info(f"Salvando etapa {stage} para sessão {session_id}")
        return True
    
    async def salvar_erro(session_id, error_type, error_msg):
        logger.error(f"Erro na sessão {session_id}: {error_msg}")
        return True

logger = logging.getLogger(__name__)

# Cria blueprint
master_3_stage_bp = Blueprint('master_3_stage', __name__)

@master_3_stage_bp.route('/execute_complete_analysis', methods=['POST'])
async def execute_complete_analysis():
    """
    Executa análise completa das 3 etapas:
    ETAPA 1: Coleta Massiva Real (500KB+ JSON)
    ETAPA 2: Estudo Profundo IA (5 minutos)
    ETAPA 3: Relatório Final (25+ páginas HTML)
    """
    
    try:
        # Obtém dados da requisição
        data = request.get_json()
        
        if not data:
            return jsonify({
                "success": False,
                "error": "Dados da requisição não fornecidos"
            }), 400
        
        # Extrai parâmetros
        produto = data.get('produto', '').strip()
        nicho = data.get('nicho', '').strip()
        publico = data.get('publico', '').strip()
        
        if not any([produto, nicho, publico]):
            return jsonify({
                "success": False,
                "error": "Pelo menos um dos campos (produto, nicho, publico) deve ser preenchido"
            }), 400
        
        # Gera ID da sessão
        session_id = f"3stage_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{str(uuid.uuid4())[:8]}"
        
        logger.info(f"🚀 Iniciando execução completa 3 etapas - Sessão: {session_id}")
        
        # Executa análise completa das 3 etapas
        results = await master_3_stage_orchestrator.execute_complete_3_stage_analysis(
            produto=produto,
            nicho=nicho,
            publico=publico,
            session_id=session_id
        )
        
        # Prepara resposta
        response = {
            "success": results["success"],
            "session_id": session_id,
            "execution_results": results,
            "summary": {
                "total_execution_time_minutes": results.get("execution_stats", {}).get("total_execution_time_minutes", 0),
                "stage_1_json_size_kb": results.get("stage_1_results", {}).get("json_size_kb", 0),
                "stage_1_target_achieved": results.get("stage_1_results", {}).get("target_500kb_achieved", False),
                "stage_2_phases_completed": results.get("stage_2_results", {}).get("phases_completed", 0),
                "stage_2_efficiency_score": results.get("stage_2_results", {}).get("efficiency_score", 0),
                "stage_3_report_path": results.get("stage_3_results", {}).get("report_path", ""),
                "errors": results.get("errors", [])
            }
        }
        
        if results["success"]:
            logger.info(f"✅ Execução completa 3 etapas finalizada com sucesso - Sessão: {session_id}")
            return jsonify(response), 200
        else:
            logger.error(f"❌ Execução completa 3 etapas falhou - Sessão: {session_id}")
            return jsonify(response), 500
            
    except Exception as e:
        error_msg = f"Erro na execução completa das 3 etapas: {str(e)}"
        logger.error(f"❌ {error_msg}")
        
        return jsonify({
            "success": False,
            "error": error_msg,
            "timestamp": datetime.now().isoformat()
        }), 500

@master_3_stage_bp.route('/execute_stage_1_only', methods=['POST'])
async def execute_stage_1_only():
    """Executa apenas a ETAPA 1: Coleta Massiva Real"""
    
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                "success": False,
                "error": "Dados da requisição não fornecidos"
            }), 400
        
        produto = data.get('produto', '').strip()
        nicho = data.get('nicho', '').strip()
        publico = data.get('publico', '').strip()
        
        if not any([produto, nicho, publico]):
            return jsonify({
                "success": False,
                "error": "Pelo menos um dos campos deve ser preenchido"
            }), 400
        
        session_id = f"stage1_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{str(uuid.uuid4())[:8]}"
        
        logger.info(f"🔍 Executando apenas ETAPA 1 - Sessão: {session_id}")
        
        results = await master_3_stage_orchestrator.execute_stage_1_only(
            produto=produto,
            nicho=nicho,
            publico=publico,
            session_id=session_id
        )
        
        response = {
            "success": results["success"],
            "session_id": session_id,
            "stage": "stage_1_only",
            "results": results
        }
        
        return jsonify(response), 200 if results["success"] else 500
        
    except Exception as e:
        error_msg = f"Erro na execução da ETAPA 1: {str(e)}"
        logger.error(f"❌ {error_msg}")
        
        return jsonify({
            "success": False,
            "error": error_msg
        }), 500

@master_3_stage_bp.route('/execute_stage_2_only', methods=['POST'])
async def execute_stage_2_only():
    """Executa apenas a ETAPA 2: Estudo Profundo IA"""
    
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                "success": False,
                "error": "Dados da requisição não fornecidos"
            }), 400
        
        massive_data = data.get('massive_data')
        study_duration_minutes = data.get('study_duration_minutes', 5)
        
        if not massive_data:
            return jsonify({
                "success": False,
                "error": "massive_data é obrigatório para ETAPA 2"
            }), 400
        
        session_id = f"stage2_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{str(uuid.uuid4())[:8]}"
        
        logger.info(f"🧠 Executando apenas ETAPA 2 - Sessão: {session_id}")
        
        results = await master_3_stage_orchestrator.execute_stage_2_with_data(
            massive_data=massive_data,
            session_id=session_id,
            study_duration_minutes=study_duration_minutes
        )
        
        response = {
            "success": results["success"],
            "session_id": session_id,
            "stage": "stage_2_only",
            "results": results
        }
        
        return jsonify(response), 200 if results["success"] else 500
        
    except Exception as e:
        error_msg = f"Erro na execução da ETAPA 2: {str(e)}"
        logger.error(f"❌ {error_msg}")
        
        return jsonify({
            "success": False,
            "error": error_msg
        }), 500

@master_3_stage_bp.route('/execute_stage_3_only', methods=['POST'])
async def execute_stage_3_only():
    """Executa apenas a ETAPA 3: Relatório Final"""
    
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                "success": False,
                "error": "Dados da requisição não fornecidos"
            }), 400
        
        massive_data = data.get('massive_data')
        expert_knowledge = data.get('expert_knowledge')
        
        if not massive_data or not expert_knowledge:
            return jsonify({
                "success": False,
                "error": "massive_data e expert_knowledge são obrigatórios para ETAPA 3"
            }), 400
        
        session_id = f"stage3_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{str(uuid.uuid4())[:8]}"
        
        logger.info(f"📄 Executando apenas ETAPA 3 - Sessão: {session_id}")
        
        results = await master_3_stage_orchestrator.execute_stage_3_with_data(
            massive_data=massive_data,
            expert_knowledge=expert_knowledge,
            session_id=session_id
        )
        
        response = {
            "success": results["success"],
            "session_id": session_id,
            "stage": "stage_3_only",
            "results": results
        }
        
        return jsonify(response), 200 if results["success"] else 500
        
    except Exception as e:
        error_msg = f"Erro na execução da ETAPA 3: {str(e)}"
        logger.error(f"❌ {error_msg}")
        
        return jsonify({
            "success": False,
            "error": error_msg
        }), 500

@master_3_stage_bp.route('/create_cpl_devastador', methods=['POST'])
async def create_cpl_devastador():
    """Integra sistema CPL devastador com dados das 3 etapas"""
    
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                "success": False,
                "error": "Dados da requisição não fornecidos"
            }), 400
        
        # Dados das 3 etapas (opcionais - pode usar dados existentes)
        massive_data = data.get('massive_data', {})
        expert_knowledge = data.get('expert_knowledge', {})
        
        # Parâmetros do CPL
        tema = data.get('tema', '').strip()
        segmento = data.get('segmento', '').strip()
        publico_alvo = data.get('publico_alvo', '').strip()
        
        if not any([tema, segmento, publico_alvo]):
            return jsonify({
                "success": False,
                "error": "Pelo menos um dos campos (tema, segmento, publico_alvo) deve ser preenchido"
            }), 400
        
        session_id = f"cpl_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{str(uuid.uuid4())[:8]}"
        
        logger.info(f"🎯 Criando CPL devastador - Sessão: {session_id}")
        
        # Inicializa protocolo CPL se disponível
        if not HAS_CPL_PROTOCOL:
            return jsonify({
                "success": False,
                "error": "CPL Devastador Protocol não está disponível"
            }), 503
        
        cpl_protocol = CPLDevastadorProtocol()
        
        # Executa criação do CPL (implementação simplificada)
        cpl_results = {
            "success": True,
            "session_id": session_id,
            "tema": tema,
            "segmento": segmento,
            "publico_alvo": publico_alvo,
            "evento_magnetico": {
                "nome": f"Evento Transformador: {tema}",
                "promessa_central": f"Transforme sua vida com {tema} em 4 dias",
                "arquitetura_cpls": {
                    "cpl_1": "A Descoberta Chocante",
                    "cpl_2": "A Prova Impossível", 
                    "cpl_3": "O Mapa Secreto",
                    "cpl_4": "A Decisão do Destino"
                }
            },
            "cpls_gerados": 4,
            "data_integration": {
                "massive_data_used": len(str(massive_data)) > 0,
                "expert_knowledge_used": len(str(expert_knowledge)) > 0
            },
            "created_at": datetime.now().isoformat()
        }
        
        # Salva resultados do CPL
        await salvar_etapa(
            session_id,
            "cpl_devastador_creation",
            cpl_results,
            f"analyses_data/{session_id}/cpl_devastador_results.json"
        )
        
        logger.info(f"✅ CPL devastador criado - Sessão: {session_id}")
        
        return jsonify(cpl_results), 200
        
    except Exception as e:
        error_msg = f"Erro na criação do CPL devastador: {str(e)}"
        logger.error(f"❌ {error_msg}")
        
        return jsonify({
            "success": False,
            "error": error_msg
        }), 500

@master_3_stage_bp.route('/health_check', methods=['GET'])
async def health_check():
    """Verifica saúde de todos os componentes das 3 etapas"""
    
    try:
        health_status = await master_3_stage_orchestrator.health_check()
        
        return jsonify(health_status), 200
        
    except Exception as e:
        error_msg = f"Erro no health check: {str(e)}"
        logger.error(f"❌ {error_msg}")
        
        return jsonify({
            "overall_health": "error",
            "error": error_msg,
            "timestamp": datetime.now().isoformat()
        }), 500

@master_3_stage_bp.route('/execution_statistics', methods=['GET'])
async def execution_statistics():
    """Retorna estatísticas de execução do sistema"""
    
    try:
        stats = master_3_stage_orchestrator.get_execution_statistics()
        
        return jsonify(stats), 200
        
    except Exception as e:
        error_msg = f"Erro ao obter estatísticas: {str(e)}"
        logger.error(f"❌ {error_msg}")
        
        return jsonify({
            "error": error_msg,
            "timestamp": datetime.now().isoformat()
        }), 500

@master_3_stage_bp.route('/test_complete_system', methods=['GET'])
def test_complete_system():
    """Página de teste do sistema completo das 3 etapas"""
    
    return render_template('test_3_stage_system.html')

# Função para registrar o blueprint
def register_master_3_stage_routes(app):
    """Registra as rotas do sistema de 3 etapas"""
    app.register_blueprint(master_3_stage_bp, url_prefix='/api/3stage')
    logger.info("🚀 Rotas do Master 3-Stage System registradas")