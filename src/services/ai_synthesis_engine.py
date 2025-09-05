#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ARQV30 Enhanced v3.0 - AI Synthesis Engine
Motor de síntese da IA com ferramentas de busca ativa
"""

import os
import logging
import json
import asyncio
from typing import Dict, Any, Optional
from datetime import datetime
from pathlib import Path
from services.ai_manager import ai_manager
from services.search_api_manager import search_api_manager

logger = logging.getLogger(__name__)

class AISynthesisEngine:
    """Motor de síntese da IA com busca ativa"""

    def __init__(self):
        """Inicializa o motor de síntese"""
        self.synthesis_prompts = self._load_synthesis_prompts()
        logger.info("🧠 AI Synthesis Engine inicializado")

    def _load_synthesis_prompts(self) -> Dict[str, str]:
        """Carrega prompts de síntese"""
        return {
            'master_synthesis': """
            Você é um analista estratégico especializado em síntese de dados de mercado.

            Sua missão é estudar profundamente o relatório de coleta fornecido e criar uma síntese estruturada e acionável.

            IMPORTANTE: Você tem acesso à ferramenta google_search. Use-a sempre que:
            - Encontrar um tópico que precisa de aprofundamento
            - Precisar verificar dados ou estatísticas
            - Quiser buscar informações mais recentes
            - Identificar tendências que precisam de validação

            INSTRUÇÕES:
            1. Analise todo o conteúdo do relatório de coleta
            2. Use a ferramenta de busca para enriquecer sua análise
            3. Sintetize todos os achados em um JSON estruturado

            ESTRUTURA DO JSON DE RESPOSTA:
            {
                "insights_principais": [
                    "Lista de 10-15 insights principais extraídos"
                ],
                "oportunidades_identificadas": [
                    "Lista de 8-12 oportunidades de mercado"
                ],
                "publico_alvo_refinado": {
                    "demografia": "Perfil demográfico refinado",
                    "psicografia": "Perfil psicográfico detalhado",
                    "comportamentos": "Padrões comportamentais identificados",
                    "dores_principais": ["Lista das principais dores"],
                    "desejos_principais": ["Lista dos principais desejos"]
                },
                "estrategias_recomendadas": [
                    "Lista de 6-10 estratégias específicas"
                ],
                "pontos_atencao": [
                    "Lista de 5-8 pontos que requerem atenção"
                ],
                "dados_mercado": {
                    "tamanho_estimado": "Estimativa do tamanho do mercado",
                    "crescimento_projetado": "Projeção de crescimento",
                    "principais_players": ["Lista dos principais players"],
                    "barreiras_entrada": ["Principais barreiras"]
                },
                "tendencias_futuras": [
                    "Lista de tendências identificadas para o futuro"
                ],
                "metricas_chave": {
                    "kpis_sugeridos": ["Lista de KPIs recomendados"],
                    "benchmarks": "Benchmarks de mercado identificados"
                }
            }

            RELATÓRIO DE COLETA:
            """
        }

    async def analyze_and_synthesize(
        self, 
        session_id: str, 
        model: str = "gemini", 
        api_key: str = None, 
        analysis_time: int = 300
    ) -> Dict[str, Any]:
        """
        Analisa e sintetiza dados coletados usando IA com ferramentas
        
        Args:
            session_id: ID da sessão
            model: Modelo de IA a usar
            api_key: Chave da API (opcional)
            analysis_time: Tempo máximo de análise em segundos
        """
        logger.info(f"🧠 Iniciando síntese com IA para sessão: {session_id}")
        
        try:
            # 1. Carrega relatório de coleta
            relatorio_coleta = self._load_collection_report(session_id)
            if not relatorio_coleta:
                raise Exception("Relatório de coleta não encontrado")
            
            # 2. Constrói prompt mestre
            master_prompt = self._build_master_prompt(relatorio_coleta)
            
            # 3. Executa síntese com ferramentas
            logger.info("🔍 Executando síntese com ferramentas de busca ativa...")
            synthesis_result = await ai_manager.generate_with_tools(
                prompt=master_prompt,
                context=relatorio_coleta[:10000],  # Primeiros 10k caracteres como contexto
                tools=['google_search'],
                max_iterations=5
            )
            
            # 4. Processa e valida resultado
            processed_synthesis = self._process_synthesis_result(synthesis_result)
            
            # 5. Salva síntese
            synthesis_path = self._save_synthesis_result(session_id, processed_synthesis)
            
            logger.info(f"✅ Síntese concluída e salva em: {synthesis_path}")
            
            return {
                "success": True,
                "session_id": session_id,
                "synthesis_path": synthesis_path,
                "synthesis_data": processed_synthesis,
                "analysis_time": analysis_time,
                "model_used": model,
                "tools_used": ["google_search"],
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Erro na síntese: {e}")
            return {
                "success": False,
                "error": str(e),
                "session_id": session_id,
                "timestamp": datetime.now().isoformat()
            }

    def _load_collection_report(self, session_id: str) -> Optional[str]:
        """Carrega relatório de coleta da sessão"""
        try:
            report_path = Path(f"analyses_data/{session_id}/relatorio_coleta.md")
            if report_path.exists():
                with open(report_path, 'r', encoding='utf-8') as f:
                    return f.read()
            
            logger.warning(f"⚠️ Relatório de coleta não encontrado: {report_path}")
            return None
            
        except Exception as e:
            logger.error(f"❌ Erro ao carregar relatório: {e}")
            return None

    def _build_master_prompt(self, relatorio_coleta: str) -> str:
        """Constrói prompt mestre para síntese"""
        base_prompt = self.synthesis_prompts['master_synthesis']
        return f"{base_prompt}\n\n{relatorio_coleta}"

    def _process_synthesis_result(self, synthesis_result: str) -> Dict[str, Any]:
        """Processa resultado da síntese"""
        try:
            # Tenta extrair JSON da resposta
            if "```json" in synthesis_result:
                start = synthesis_result.find("```json") + 7
                end = synthesis_result.rfind("```")
                json_text = synthesis_result[start:end].strip()
                return json.loads(json_text)
            
            # Se não encontrar JSON, tenta parsear a resposta inteira
            try:
                return json.loads(synthesis_result)
            except json.JSONDecodeError:
                # Fallback: cria estrutura básica
                return self._create_fallback_synthesis(synthesis_result)
                
        except Exception as e:
            logger.error(f"❌ Erro ao processar síntese: {e}")
            return self._create_fallback_synthesis(synthesis_result)

    def _create_fallback_synthesis(self, raw_text: str) -> Dict[str, Any]:
        """Cria síntese de fallback"""
        return {
            "insights_principais": [
                "Síntese gerada em modo de fallback",
                "Análise baseada no conteúdo coletado",
                "Recomenda-se revisão manual dos dados"
            ],
            "oportunidades_identificadas": [
                "Oportunidades identificadas no conteúdo coletado",
                "Análise de mercado baseada em dados reais"
            ],
            "publico_alvo_refinado": {
                "demografia": "Perfil baseado na análise dos dados",
                "psicografia": "Características psicológicas identificadas",
                "comportamentos": "Padrões comportamentais observados",
                "dores_principais": ["Dores identificadas na análise"],
                "desejos_principais": ["Desejos identificados na análise"]
            },
            "estrategias_recomendadas": [
                "Estratégias baseadas na análise dos dados coletados"
            ],
            "pontos_atencao": [
                "Pontos que requerem atenção especial"
            ],
            "raw_synthesis": raw_text[:2000],
            "fallback_mode": True,
            "timestamp": datetime.now().isoformat()
        }

    def _save_synthesis_result(self, session_id: str, synthesis_data: Dict[str, Any]) -> str:
        """Salva resultado da síntese"""
        try:
            session_dir = Path(f"analyses_data/{session_id}")
            session_dir.mkdir(parents=True, exist_ok=True)
            
            synthesis_path = session_dir / "resumo_sintese.json"
            
            with open(synthesis_path, 'w', encoding='utf-8') as f:
                json.dump(synthesis_data, f, ensure_ascii=False, indent=2)
            
            return str(synthesis_path)
            
        except Exception as e:
            logger.error(f"❌ Erro ao salvar síntese: {e}")
            raise

# Instância global
ai_synthesis_engine = AISynthesisEngine()