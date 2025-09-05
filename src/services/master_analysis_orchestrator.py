
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ARQV30 Enhanced v3.0 - Master Analysis Orchestrator
Orquestrador mestre que implementa a nova metodologia aprimorada
"""

import os
import logging
import time
from datetime import datetime
from typing import Dict, List, Any, Optional, Callable
from services.massive_data_collector import massive_data_collector
from services.enhanced_module_processor import enhanced_module_processor
from services.comprehensive_report_generator_v3 import comprehensive_report_generator_v3
from services.auto_save_manager import salvar_etapa, salvar_erro

logger = logging.getLogger(__name__)

class MasterAnalysisOrchestrator:
    """Orquestrador mestre para nova metodologia aprimorada"""

    def __init__(self):
        """Inicializa o orquestrador mestre"""
        self.execution_phases = [
            "massive_data_collection",
            "json_giant_creation", 
            "modules_processing",
            "detailed_report_generation"
        ]
        
        self.current_phase = None
        self.phase_progress = {}
        
        logger.info("🎯 Master Analysis Orchestrator v3.0 inicializado")

    def execute_complete_analysis(
        self,
        query: str,
        context: Dict[str, Any],
        session_id: str,
        progress_callback: Optional[Callable] = None
    ) -> Dict[str, Any]:
        """Executa análise completa com nova metodologia aprimorada"""
        
        logger.info("🚀 INICIANDO ANÁLISE COMPLETA COM METODOLOGIA APRIMORADA")
        start_time = time.time()
        
        # Salva início da análise
        analysis_metadata = {
            "session_id": session_id,
            "query": query,
            "context": context,
            "methodology": "ARQV30_Enhanced_v3.0_APRIMORADA",
            "phases": self.execution_phases,
            "started_at": datetime.now().isoformat()
        }
        
        salvar_etapa("master_analysis_iniciada", analysis_metadata, categoria="analise_completa")
        
        try:
            # FASE 1: Coleta Massiva de Dados
            if progress_callback:
                progress_callback(1, "🌊 FASE 1: Executando coleta massiva de dados...")
            
            self.current_phase = "massive_data_collection"
            massive_data = self._execute_phase_1_massive_collection(query, context, session_id, progress_callback)
            
            # FASE 2: Criação do JSON Gigante  
            if progress_callback:
                progress_callback(2, "📄 FASE 2: Finalizando JSON gigante...")
            
            self.current_phase = "json_giant_creation"
            json_giant_summary = self._execute_phase_2_json_creation(massive_data, session_id, progress_callback)
            
            # FASE 3: Processamento de Módulos
            if progress_callback:
                progress_callback(3, "🔧 FASE 3: Processando todos os módulos...")
            
            self.current_phase = "modules_processing"
            modules_results = self._execute_phase_3_modules_processing(massive_data, context, session_id, progress_callback)
            
            # FASE 4: Geração do Relatório Detalhado
            if progress_callback:
                progress_callback(4, "📊 FASE 4: Gerando relatório detalhado (25+ páginas)...")
            
            self.current_phase = "detailed_report_generation"
            detailed_report = self._execute_phase_4_report_generation(massive_data, modules_results, context, session_id, progress_callback)
            
            # Finalização
            execution_time = time.time() - start_time
            
            final_results = {
                "success": True,
                "session_id": session_id,
                "methodology": "ARQV30_Enhanced_v3.0_APRIMORADA",
                "execution_time": execution_time,
                "phases_completed": self.execution_phases,
                "massive_data_summary": json_giant_summary,
                "modules_summary": modules_results.get("processing_summary", {}),
                "detailed_report_summary": detailed_report.get("estatisticas_relatorio", {}),
                "analysis_metadata": analysis_metadata,
                "completed_at": datetime.now().isoformat()
            }
            
            # Salva resultado final
            salvar_etapa("master_analysis_completa", final_results, categoria="analise_completa")
            
            logger.info(f"✅ ANÁLISE COMPLETA CONCLUÍDA em {execution_time:.2f}s")
            logger.info(f"📊 Dados coletados: {json_giant_summary.get('total_sources', 0)} fontes")
            logger.info(f"🔧 Módulos processados: {modules_results.get('processing_summary', {}).get('successful_modules', 0)}")
            logger.info(f"📄 Relatório: {detailed_report.get('estatisticas_relatorio', {}).get('paginas_estimadas', 0)} páginas")
            
            return final_results
            
        except Exception as e:
            logger.error(f"❌ ERRO CRÍTICO na análise completa: {e}")
            salvar_erro("master_analysis_critico", e, contexto={"session_id": session_id, "phase": self.current_phase})
            
            return {
                "success": False,
                "error": str(e),
                "session_id": session_id,
                "failed_phase": self.current_phase,
                "methodology": "ARQV30_Enhanced_v3.0_APRIMORADA"
            }

    def _execute_phase_1_massive_collection(
        self, 
        query: str, 
        context: Dict[str, Any], 
        session_id: str,
        progress_callback: Optional[Callable] = None
    ) -> Dict[str, Any]:
        """Executa FASE 1: Coleta massiva de dados"""
        
        logger.info("🌊 EXECUTANDO FASE 1: COLETA MASSIVA DE DADOS")
        
        try:
            if progress_callback:
                progress_callback(1.1, "🔍 Iniciando buscas web simultâneas...")
            
            # Executa coleta massiva
            massive_data = massive_data_collector.execute_massive_collection(
                query, context, session_id
            )
            
            if progress_callback:
                progress_callback(1.9, "✅ Coleta massiva concluída")
            
            # Valida dados coletados
            if not massive_data or massive_data.get("statistics", {}).get("total_sources", 0) == 0:
                raise Exception("❌ Nenhum dado foi coletado na fase massiva")
            
            logger.info(f"✅ FASE 1 CONCLUÍDA: {massive_data['statistics']['total_sources']} fontes coletadas")
            return massive_data
            
        except Exception as e:
            logger.error(f"❌ FASE 1 FALHOU: {e}")
            raise e

    def _execute_phase_2_json_creation(
        self, 
        massive_data: Dict[str, Any], 
        session_id: str,
        progress_callback: Optional[Callable] = None
    ) -> Dict[str, Any]:
        """Executa FASE 2: Finalização do JSON gigante"""
        
        logger.info("📄 EXECUTANDO FASE 2: FINALIZAÇÃO DO JSON GIGANTE")
        
        try:
            if progress_callback:
                progress_callback(2.1, "📊 Calculando estatísticas finais...")
            
            # O JSON gigante já foi criado na fase 1, aqui apenas validamos e resumimos
            json_summary = {
                "total_sources": massive_data.get("statistics", {}).get("total_sources", 0),
                "total_content_length": massive_data.get("statistics", {}).get("total_content_length", 0),
                "sources_by_type": massive_data.get("statistics", {}).get("sources_by_type", {}),
                "collection_time": massive_data.get("statistics", {}).get("collection_time", 0),
                "json_file_size_mb": len(str(massive_data)) / (1024 * 1024)
            }
            
            if progress_callback:
                progress_callback(2.9, "✅ JSON gigante validado e pronto")
            
            logger.info(f"✅ FASE 2 CONCLUÍDA: JSON de {json_summary['json_file_size_mb']:.2f}MB criado")
            return json_summary
            
        except Exception as e:
            logger.error(f"❌ FASE 2 FALHOU: {e}")
            raise e

    def _execute_phase_3_modules_processing(
        self, 
        massive_data: Dict[str, Any], 
        context: Dict[str, Any],
        session_id: str,
        progress_callback: Optional[Callable] = None
    ) -> Dict[str, Any]:
        """Executa FASE 3: Processamento de todos os módulos"""
        
        logger.info("🔧 EXECUTANDO FASE 3: PROCESSAMENTO DE MÓDULOS")
        
        try:
            if progress_callback:
                progress_callback(3.1, "🔧 Iniciando processamento dos módulos...")
            
            # Executa processamento de módulos usando dados massivos
            import asyncio
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                modules_results = loop.run_until_complete(
                    enhanced_module_processor.generate_all_modules(session_id)
                )
            finally:
                loop.close()
            
            if progress_callback:
                progress_callback(3.9, "✅ Todos os módulos processados")
            
            # Valida resultados dos módulos
            success_count = modules_results.get("successful_modules", 0)
            total_count = modules_results.get("total_modules", 0)
            
            if success_count == 0:
                raise Exception("❌ Nenhum módulo foi processado com sucesso")
            
            logger.info(f"✅ FASE 3 CONCLUÍDA: {success_count}/{total_count} módulos processados")
            return modules_results
            
        except Exception as e:
            logger.error(f"❌ FASE 3 FALHOU: {e}")
            raise e

    def _execute_phase_4_report_generation(
        self, 
        massive_data: Dict[str, Any], 
        modules_results: Dict[str, Any],
        context: Dict[str, Any],
        session_id: str,
        progress_callback: Optional[Callable] = None
    ) -> Dict[str, Any]:
        """Executa FASE 4: Geração do relatório detalhado"""
        
        logger.info("📊 EXECUTANDO FASE 4: GERAÇÃO DO RELATÓRIO DETALHADO")
        
        try:
            if progress_callback:
                progress_callback(4.1, "📖 Gerando relatório detalhado...")
            
            # Gera relatório final detalhado
            detailed_report = comprehensive_report_generator_v3.compile_final_markdown_report(session_id)
            
            if progress_callback:
                progress_callback(4.9, "✅ Relatório detalhado concluído")
            
            # Valida relatório gerado
            pages_estimated = detailed_report.get("estatisticas_relatorio", {}).get("paginas_estimadas", 0)
            sections_generated = detailed_report.get("estatisticas_relatorio", {}).get("secoes_geradas", 0)
            
            if pages_estimated < 20:
                logger.warning(f"⚠️ Relatório pode estar incompleto: {pages_estimated} páginas")
            
            logger.info(f"✅ FASE 4 CONCLUÍDA: Relatório de {pages_estimated} páginas com {sections_generated} seções")
            return detailed_report
            
        except Exception as e:
            logger.error(f"❌ FASE 4 FALHOU: {e}")
            raise e

    def get_phase_progress(self, session_id: str) -> Dict[str, Any]:
        """Obtém progresso das fases de análise"""
        return {
            "current_phase": self.current_phase,
            "phases_total": len(self.execution_phases),
            "phases_list": self.execution_phases,
            "phase_progress": self.phase_progress.get(session_id, {}),
            "methodology": "ARQV30_Enhanced_v3.0_APRIMORADA"
        }

    def reset_orchestrator(self):
        """Reseta o orquestrador"""
        self.current_phase = None
        self.phase_progress.clear()
        logger.info("🔄 Master Analysis Orchestrator resetado")

# Instância global
master_analysis_orchestrator = MasterAnalysisOrchestrator()
