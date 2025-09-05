#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ARQV30 Enhanced v3.0 - Master 3-Stage Orchestrator
Orquestrador principal das 3 etapas: Coleta Massiva → Estudo IA → Relatório Final
"""

import os
import logging
import asyncio
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from pathlib import Path

# Importa os serviços das 3 etapas
from services.real_search_orchestrator import real_search_orchestrator
from services.enhanced_ai_manager import enhanced_ai_manager
from services.comprehensive_html_report_generator import ComprehensiveHTMLReportGenerator
from services.auto_save_manager import salvar_etapa, salvar_erro

logger = logging.getLogger(__name__)

class Master3StageOrchestrator:
    """
    Orquestrador principal das 3 etapas do sistema preditivo:
    
    ETAPA 1: Coleta Massiva Real (500KB+ JSON) - ZERO simulação
    ETAPA 2: Estudo Profundo IA (5 minutos) - IA se torna expert
    ETAPA 3: Relatório Final (25+ páginas HTML) - Análises únicas
    """

    def __init__(self):
        """Inicializa o orquestrador das 3 etapas"""
        self.report_generator = ComprehensiveHTMLReportGenerator()
        self.execution_stats = {
            "total_executions": 0,
            "successful_executions": 0,
            "failed_executions": 0,
            "average_execution_time": 0,
            "last_execution": None
        }
        
        logger.info("🚀 Master 3-Stage Orchestrator inicializado")
        logger.info("📋 Etapas: Coleta Massiva → Estudo IA → Relatório Final")

    async def execute_complete_3_stage_analysis(
        self,
        produto: str,
        nicho: str,
        publico: str,
        session_id: str
    ) -> Dict[str, Any]:
        """
        Executa análise completa das 3 etapas de forma sequencial
        
        Args:
            produto: Produto/serviço a ser analisado
            nicho: Nicho de mercado
            publico: Público-alvo
            session_id: ID da sessão
            
        Returns:
            Dict com resultados completos das 3 etapas
        """
        
        logger.info("🔥 INICIANDO ANÁLISE COMPLETA 3 ETAPAS")
        logger.info(f"📊 Produto: {produto}")
        logger.info(f"🎯 Nicho: {nicho}")
        logger.info(f"👥 Público: {publico}")
        logger.info(f"🆔 Sessão: {session_id}")
        
        start_time = time.time()
        execution_results = {
            "session_id": session_id,
            "execution_started": datetime.now().isoformat(),
            "input_parameters": {
                "produto": produto,
                "nicho": nicho,
                "publico": publico
            },
            "stage_1_results": {},
            "stage_2_results": {},
            "stage_3_results": {},
            "execution_stats": {},
            "success": False,
            "errors": []
        }
        
        try:
            # ==================== ETAPA 1: COLETA MASSIVA REAL ====================
            logger.info("🔍 ETAPA 1/3: Iniciando Coleta Massiva Real...")
            stage1_start = time.time()
            
            # Constrói query principal
            query_parts = [p for p in [produto, nicho, publico] if p.strip()]
            main_query = " ".join(query_parts) if query_parts else "análise de mercado"
            
            context = {
                "produto": produto,
                "nicho": nicho,
                "publico": publico,
                "session_id": session_id,
                "stage": "massive_collection"
            }
            
            # Executa coleta massiva real
            massive_data = await real_search_orchestrator.execute_massive_real_search(
                query=main_query,
                context=context,
                session_id=session_id
            )
            
            stage1_time = time.time() - stage1_start
            
            # Verifica se atingiu o tamanho alvo
            json_size_kb = len(json.dumps(massive_data, ensure_ascii=False)) / 1024
            target_achieved = json_size_kb >= 500
            
            execution_results["stage_1_results"] = {
                "success": True,
                "data_collected": massive_data,
                "execution_time_seconds": stage1_time,
                "json_size_kb": json_size_kb,
                "target_500kb_achieved": target_achieved,
                "sources_used": len(massive_data.get("providers_used", [])),
                "total_data_points": massive_data.get("statistics", {}).get("total_sources", 0)
            }
            
            logger.info(f"✅ ETAPA 1 concluída em {stage1_time:.1f}s")
            logger.info(f"📊 JSON gerado: {json_size_kb:.1f}KB (Target: 500KB)")
            logger.info(f"🎯 Target atingido: {'SIM' if target_achieved else 'NÃO'}")
            
            # Salva dados da etapa 1
            await salvar_etapa(
                session_id,
                "stage_1_massive_collection",
                execution_results["stage_1_results"],
                f"analyses_data/{session_id}/stage_1_massive_data.json"
            )
            
            # ==================== ETAPA 2: ESTUDO PROFUNDO IA ====================
            logger.info("🧠 ETAPA 2/3: Iniciando Estudo Profundo IA (5 minutos)...")
            stage2_start = time.time()
            
            # IA estuda os dados massivos por 5 minutos
            expert_knowledge = await enhanced_ai_manager.conduct_deep_study_phase(
                massive_data=massive_data,
                session_id=session_id,
                study_duration_minutes=5
            )
            
            stage2_time = time.time() - stage2_start
            
            execution_results["stage_2_results"] = {
                "success": True,
                "expert_knowledge": expert_knowledge,
                "execution_time_seconds": stage2_time,
                "study_duration_minutes": stage2_time / 60,
                "phases_completed": expert_knowledge.get("study_metadata", {}).get("phases_completed", 0),
                "efficiency_score": expert_knowledge.get("study_metadata", {}).get("efficiency_score", 0),
                "ai_provider_used": expert_knowledge.get("study_metadata", {}).get("ai_provider_used", "unknown")
            }
            
            logger.info(f"✅ ETAPA 2 concluída em {stage2_time/60:.1f} minutos")
            logger.info(f"🎓 Fases completadas: {expert_knowledge.get('study_metadata', {}).get('phases_completed', 0)}")
            logger.info(f"📈 Eficiência: {expert_knowledge.get('study_metadata', {}).get('efficiency_score', 0):.1f}%")
            
            # Salva conhecimento expert da etapa 2
            await salvar_etapa(
                session_id,
                "stage_2_ai_expertise",
                execution_results["stage_2_results"],
                f"analyses_data/{session_id}/stage_2_expert_knowledge.json"
            )
            
            # ==================== ETAPA 3: RELATÓRIO FINAL 25+ PÁGINAS ====================
            logger.info("📄 ETAPA 3/3: Gerando Relatório Final 25+ páginas...")
            stage3_start = time.time()
            
            # Gera relatório final HTML de 25+ páginas
            report_path = await self.report_generator.generate_ultimate_25_page_report(
                massive_data=massive_data,
                expert_knowledge=expert_knowledge,
                session_id=session_id
            )
            
            stage3_time = time.time() - stage3_start
            
            execution_results["stage_3_results"] = {
                "success": True,
                "report_path": report_path,
                "execution_time_seconds": stage3_time,
                "report_generated": True,
                "estimated_pages": 25  # Será atualizado pelo gerador
            }
            
            logger.info(f"✅ ETAPA 3 concluída em {stage3_time:.1f}s")
            logger.info(f"📄 Relatório salvo: {report_path}")
            
            # Salva resultados da etapa 3
            await salvar_etapa(
                session_id,
                "stage_3_final_report",
                execution_results["stage_3_results"],
                f"analyses_data/{session_id}/stage_3_report_info.json"
            )
            
            # ==================== FINALIZAÇÃO ====================
            total_time = time.time() - start_time
            
            execution_results["execution_stats"] = {
                "total_execution_time_seconds": total_time,
                "total_execution_time_minutes": total_time / 60,
                "stage_1_time_seconds": stage1_time,
                "stage_2_time_seconds": stage2_time,
                "stage_3_time_seconds": stage3_time,
                "stage_1_percentage": (stage1_time / total_time) * 100,
                "stage_2_percentage": (stage2_time / total_time) * 100,
                "stage_3_percentage": (stage3_time / total_time) * 100
            }
            
            execution_results["success"] = True
            execution_results["execution_completed"] = datetime.now().isoformat()
            
            # Atualiza estatísticas
            self.execution_stats["total_executions"] += 1
            self.execution_stats["successful_executions"] += 1
            self.execution_stats["last_execution"] = datetime.now().isoformat()
            
            # Calcula média de tempo
            if self.execution_stats["average_execution_time"] == 0:
                self.execution_stats["average_execution_time"] = total_time
            else:
                self.execution_stats["average_execution_time"] = (
                    self.execution_stats["average_execution_time"] + total_time
                ) / 2
            
            logger.info("🎉 ANÁLISE COMPLETA 3 ETAPAS FINALIZADA COM SUCESSO!")
            logger.info(f"⏱️ Tempo total: {total_time/60:.1f} minutos")
            logger.info(f"📊 Etapa 1: {stage1_time:.1f}s ({(stage1_time/total_time)*100:.1f}%)")
            logger.info(f"🧠 Etapa 2: {stage2_time:.1f}s ({(stage2_time/total_time)*100:.1f}%)")
            logger.info(f"📄 Etapa 3: {stage3_time:.1f}s ({(stage3_time/total_time)*100:.1f}%)")
            
            # Salva resultados completos
            await salvar_etapa(
                session_id,
                "complete_3_stage_analysis",
                execution_results,
                f"analyses_data/{session_id}/complete_analysis_results.json"
            )
            
            return execution_results
            
        except Exception as e:
            error_msg = f"Erro na execução das 3 etapas: {str(e)}"
            logger.error(f"❌ {error_msg}")
            
            execution_results["success"] = False
            execution_results["errors"].append(error_msg)
            execution_results["execution_completed"] = datetime.now().isoformat()
            execution_results["execution_stats"]["total_execution_time_seconds"] = time.time() - start_time
            
            # Atualiza estatísticas de erro
            self.execution_stats["total_executions"] += 1
            self.execution_stats["failed_executions"] += 1
            self.execution_stats["last_execution"] = datetime.now().isoformat()
            
            # Salva erro
            await salvar_erro(session_id, "3_stage_execution_error", error_msg)
            
            return execution_results

    async def execute_stage_1_only(
        self,
        produto: str,
        nicho: str,
        publico: str,
        session_id: str
    ) -> Dict[str, Any]:
        """Executa apenas a ETAPA 1: Coleta Massiva Real"""
        
        logger.info("🔍 Executando apenas ETAPA 1: Coleta Massiva Real")
        
        query_parts = [p for p in [produto, nicho, publico] if p.strip()]
        main_query = " ".join(query_parts) if query_parts else "análise de mercado"
        
        context = {
            "produto": produto,
            "nicho": nicho,
            "publico": publico,
            "session_id": session_id,
            "stage": "massive_collection_only"
        }
        
        try:
            massive_data = await real_search_orchestrator.execute_massive_real_search(
                query=main_query,
                context=context,
                session_id=session_id
            )
            
            json_size_kb = len(json.dumps(massive_data, ensure_ascii=False)) / 1024
            
            result = {
                "success": True,
                "stage": "stage_1_only",
                "data_collected": massive_data,
                "json_size_kb": json_size_kb,
                "target_500kb_achieved": json_size_kb >= 500,
                "execution_time": datetime.now().isoformat()
            }
            
            await salvar_etapa(
                session_id,
                "stage_1_only_execution",
                result,
                f"analyses_data/{session_id}/stage_1_only_results.json"
            )
            
            logger.info(f"✅ ETAPA 1 concluída - JSON: {json_size_kb:.1f}KB")
            return result
            
        except Exception as e:
            error_msg = f"Erro na ETAPA 1: {str(e)}"
            logger.error(f"❌ {error_msg}")
            
            result = {
                "success": False,
                "stage": "stage_1_only",
                "error": error_msg,
                "execution_time": datetime.now().isoformat()
            }
            
            await salvar_erro(session_id, "stage_1_only_error", error_msg)
            return result

    async def execute_stage_2_with_data(
        self,
        massive_data: Dict[str, Any],
        session_id: str,
        study_duration_minutes: int = 5
    ) -> Dict[str, Any]:
        """Executa apenas a ETAPA 2: Estudo Profundo IA com dados fornecidos"""
        
        logger.info(f"🧠 Executando apenas ETAPA 2: Estudo IA ({study_duration_minutes} min)")
        
        try:
            expert_knowledge = await enhanced_ai_manager.conduct_deep_study_phase(
                massive_data=massive_data,
                session_id=session_id,
                study_duration_minutes=study_duration_minutes
            )
            
            result = {
                "success": True,
                "stage": "stage_2_only",
                "expert_knowledge": expert_knowledge,
                "study_duration_minutes": study_duration_minutes,
                "execution_time": datetime.now().isoformat()
            }
            
            await salvar_etapa(
                session_id,
                "stage_2_only_execution",
                result,
                f"analyses_data/{session_id}/stage_2_only_results.json"
            )
            
            logger.info(f"✅ ETAPA 2 concluída - {study_duration_minutes} minutos de estudo")
            return result
            
        except Exception as e:
            error_msg = f"Erro na ETAPA 2: {str(e)}"
            logger.error(f"❌ {error_msg}")
            
            result = {
                "success": False,
                "stage": "stage_2_only",
                "error": error_msg,
                "execution_time": datetime.now().isoformat()
            }
            
            await salvar_erro(session_id, "stage_2_only_error", error_msg)
            return result

    async def execute_stage_3_with_data(
        self,
        massive_data: Dict[str, Any],
        expert_knowledge: Dict[str, Any],
        session_id: str
    ) -> Dict[str, Any]:
        """Executa apenas a ETAPA 3: Relatório Final com dados fornecidos"""
        
        logger.info("📄 Executando apenas ETAPA 3: Relatório Final 25+ páginas")
        
        try:
            report_path = await self.report_generator.generate_ultimate_25_page_report(
                massive_data=massive_data,
                expert_knowledge=expert_knowledge,
                session_id=session_id
            )
            
            result = {
                "success": True,
                "stage": "stage_3_only",
                "report_path": report_path,
                "execution_time": datetime.now().isoformat()
            }
            
            await salvar_etapa(
                session_id,
                "stage_3_only_execution",
                result,
                f"analyses_data/{session_id}/stage_3_only_results.json"
            )
            
            logger.info(f"✅ ETAPA 3 concluída - Relatório: {report_path}")
            return result
            
        except Exception as e:
            error_msg = f"Erro na ETAPA 3: {str(e)}"
            logger.error(f"❌ {error_msg}")
            
            result = {
                "success": False,
                "stage": "stage_3_only",
                "error": error_msg,
                "execution_time": datetime.now().isoformat()
            }
            
            await salvar_erro(session_id, "stage_3_only_error", error_msg)
            return result

    def get_execution_statistics(self) -> Dict[str, Any]:
        """Retorna estatísticas de execução do orquestrador"""
        return {
            "orchestrator_stats": self.execution_stats.copy(),
            "search_orchestrator_stats": real_search_orchestrator.get_session_statistics(),
            "ai_manager_available": enhanced_ai_manager.is_available(),
            "current_timestamp": datetime.now().isoformat()
        }

    async def health_check(self) -> Dict[str, Any]:
        """Verifica saúde de todos os componentes das 3 etapas"""
        
        health_status = {
            "overall_health": "healthy",
            "timestamp": datetime.now().isoformat(),
            "components": {
                "stage_1_search_orchestrator": {
                    "status": "healthy",
                    "available_providers": len(real_search_orchestrator.providers),
                    "api_keys_loaded": sum(len(keys) for keys in real_search_orchestrator.api_keys.values())
                },
                "stage_2_ai_manager": {
                    "status": "healthy" if enhanced_ai_manager.is_available() else "unhealthy",
                    "available_providers": len([p for p in enhanced_ai_manager.providers.values() if p.get("available", False)]),
                    "current_provider": enhanced_ai_manager.current_provider
                },
                "stage_3_report_generator": {
                    "status": "healthy",
                    "generator_ready": self.report_generator is not None
                }
            }
        }
        
        # Verifica se algum componente está unhealthy
        unhealthy_components = [
            name for name, component in health_status["components"].items()
            if component["status"] == "unhealthy"
        ]
        
        if unhealthy_components:
            health_status["overall_health"] = "degraded"
            health_status["unhealthy_components"] = unhealthy_components
        
        return health_status

# Instância global
master_3_stage_orchestrator = Master3StageOrchestrator()