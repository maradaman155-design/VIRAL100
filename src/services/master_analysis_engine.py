#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ARQV30 Enhanced v2.0 - Master Analysis Engine
Motor unificado de análise seguindo o plano de unificação
"""

import os
import logging
import time
from typing import Dict, List, Optional, Any
from services.ai_manager import ai_manager
from services.production_search_manager import production_search_manager
from services.auto_save_manager import auto_save_manager
from datetime import datetime

logger = logging.getLogger(__name__)

class MasterAnalysisEngine:
    """Motor Mestre de Análise - Unifica todos os motores existentes"""

    def __init__(self):
        """Inicializa o motor mestre"""
        self.supported_analysis_types = [
            'ultra_detailed',
            'enhanced',
            'forensic',
            'archaeological',
            'unified'
        ]

        # Configurações dinâmicas
        self.config = {
            'max_search_results': int(os.getenv('MAX_SEARCH_RESULTS', '30')),
            'content_quality_threshold': float(os.getenv('CONTENT_QUALITY_THRESHOLD', '80.0')),
            'min_content_length': int(os.getenv('MIN_CONTENT_LENGTH', '1000')),
            'analysis_timeout': int(os.getenv('ANALYSIS_TIMEOUT', '600'))
        }

        logger.info("🎯 Master Analysis Engine inicializado com tipos: " + ', '.join(self.supported_analysis_types))

    def execute_analysis(self,
                        analysis_type: str,
                        query: str,
                        context: Dict[str, Any],
                        session_id: str = None) -> Dict[str, Any]:
        """Executa análise baseada no tipo especificado"""

        start_time = time.time()

        # Validação de entrada
        if analysis_type not in self.supported_analysis_types:
            raise ValueError(f"Tipo de análise não suportado: {analysis_type}")

        if not query or not query.strip():
            raise ValueError("Query de análise é obrigatória")

        logger.info(f"🚀 Iniciando análise {analysis_type.upper()}: {query}")

        try:
            # Seleciona estratégia baseada no tipo
            if analysis_type == 'ultra_detailed':
                return self._execute_ultra_detailed_analysis(query, context, session_id)
            elif analysis_type == 'enhanced':
                return self._execute_enhanced_analysis(query, context, session_id)
            elif analysis_type == 'forensic':
                return self._execute_forensic_analysis(query, context, session_id)
            elif analysis_type == 'archaeological':
                return self._execute_archaeological_analysis(query, context, session_id)
            elif analysis_type == 'unified':
                return self._execute_unified_analysis(query, context, session_id)
            else:
                # Fallback para ultra_detailed
                return self._execute_ultra_detailed_analysis(query, context, session_id)

        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"❌ Erro na análise {analysis_type}: {str(e)}")

            return {
                'success': False,
                'error': str(e),
                'analysis_type': analysis_type,
                'execution_time': execution_time,
                'timestamp': datetime.now().isoformat()
            }

    def _execute_ultra_detailed_analysis(self, query: str, context: Dict[str, Any], session_id: str) -> Dict[str, Any]:
        """Executa análise ultra-detalhada"""

        logger.info("🔍 Executando análise ULTRA-DETALHADA")

        # 1. Pesquisa web massiva
        search_results = self._perform_comprehensive_search(query)

        if session_id:
            auto_save_manager.salvar_etapa('pesquisa_web', search_results, session_id)

        # 2. Geração de avatar ultra-detalhado
        avatar_data = self._generate_ultra_detailed_avatar(context, search_results)

        if session_id:
            auto_save_manager.salvar_etapa('avatar_detalhado', avatar_data, session_id)

        # 3. Análise de mercado profunda
        market_analysis = self._perform_deep_market_analysis(query, search_results, context)

        # 4. Predições futuras
        future_predictions = self._generate_future_predictions(query, market_analysis)

        # 5. Estratégias de monetização
        monetization_strategies = self._generate_monetization_strategies(context, market_analysis)

        # Compila resultado final
        result = {
            'success': True,
            'analysis_type': 'ultra_detailed',
            'avatar': avatar_data,
            'market_analysis': market_analysis,
            'future_predictions': future_predictions,
            'monetization_strategies': monetization_strategies,
            'search_data': {
                'total_results': len(search_results.get('resultados', [])),
                'sources_used': search_results.get('fontes_utilizadas', [])
            },
            'metadata': {
                'query': query,
                'timestamp': datetime.now().isoformat(),
                'session_id': session_id
            }
        }

        if session_id:
            auto_save_manager.salvar_etapa('analise_completa', result, session_id)

        logger.info("✅ Análise ultra-detalhada concluída")
        return result

    def _execute_enhanced_analysis(self, query: str, context: Dict[str, Any], session_id: str) -> Dict[str, Any]:
        """Executa análise aprimorada"""

        logger.info("🔍 Executando análise APRIMORADA")

        # Versão simplificada focada em insights
        search_results = self._perform_comprehensive_search(query)
        insights = self._generate_market_insights(query, search_results, context)

        result = {
            'success': True,
            'analysis_type': 'enhanced',
            'insights': insights,
            'search_summary': search_results,
            'metadata': {
                'query': query,
                'timestamp': datetime.now().isoformat(),
                'session_id': session_id
            }
        }

        logger.info("✅ Análise aprimorada concluída")
        return result

    def _execute_forensic_analysis(self, query: str, context: Dict[str, Any], session_id: str) -> Dict[str, Any]:
        """Executa análise forense"""

        logger.info("🔍 Executando análise FORENSE")

        # Análise forense focada em dados profundos
        search_results = self._perform_comprehensive_search(query)
        forensic_data = self._perform_forensic_investigation(query, search_results, context)

        result = {
            'success': True,
            'analysis_type': 'forensic',
            'forensic_data': forensic_data,
            'evidence': search_results,
            'metadata': {
                'query': query,
                'timestamp': datetime.now().isoformat(),
                'session_id': session_id
            }
        }

        logger.info("✅ Análise forense concluída")
        return result

    def _execute_archaeological_analysis(self, query: str, context: Dict[str, Any], session_id: str) -> Dict[str, Any]:
        """Executa análise arqueológica"""

        logger.info("🔍 Executando análise ARQUEOLÓGICA")

        # Análise arqueológica com escavação profunda
        search_results = self._perform_comprehensive_search(query)
        archaeological_findings = self._perform_archaeological_excavation(query, search_results, context)

        result = {
            'success': True,
            'analysis_type': 'archaeological',
            'archaeological_findings': archaeological_findings,
            'excavation_data': search_results,
            'metadata': {
                'query': query,
                'timestamp': datetime.now().isoformat(),
                'session_id': session_id
            }
        }

        logger.info("✅ Análise arqueológica concluída")
        return result

    def _execute_unified_analysis(self, query: str, context: Dict[str, Any], session_id: str) -> Dict[str, Any]:
        """Executa análise unificada"""

        logger.info("🔍 Executando análise UNIFICADA")

        # Combina elementos de todas as análises
        search_results = self._perform_comprehensive_search(query)

        # Executa componentes unificados
        unified_insights = self._generate_unified_insights(query, search_results, context)

        result = {
            'success': True,
            'analysis_type': 'unified',
            'unified_insights': unified_insights,
            'comprehensive_data': search_results,
            'metadata': {
                'query': query,
                'timestamp': datetime.now().isoformat(),
                'session_id': session_id
            }
        }

        logger.info("✅ Análise unificada concluída")
        return result

    def _perform_comprehensive_search(self, query: str) -> Dict[str, Any]:
        """Realiza pesquisa abrangente usando o production search manager"""

        try:
            logger.info(f"🔍 Iniciando pesquisa abrangente: {query}")

            # Usa o production search manager
            search_results = production_search_manager.search_with_fallback(
                query,
                max_results=self.config['max_search_results']
            )

            if search_results:
                logger.info(f"✅ Pesquisa concluída: {len(search_results)} resultados")
                return {
                    'resultados': search_results,
                    'total_resultados': len(search_results),
                    'fontes_utilizadas': list(set([r.get('source', 'unknown') for r in search_results])),
                    'status': 'ok'
                }
            else:
                logger.warning("⚠️ Nenhum resultado encontrado")
                return {
                    'resultados': [],
                    'total_resultados': 0,
                    'fontes_utilizadas': [],
                    'status': 'no_results'
                }

        except Exception as e:
            logger.error(f"❌ Erro na pesquisa: {str(e)}")
            return {
                'resultados': [],
                'total_resultados': 0,
                'fontes_utilizadas': [],
                'status': 'error',
                'error': str(e)
            }

    def _generate_ultra_detailed_avatar(self, context: Dict[str, Any], search_results: Dict[str, Any]) -> Dict[str, Any]:
        """Gera avatar ultra-detalhado"""

        try:
            # Prepara prompt para geração de avatar
            avatar_prompt = self._build_avatar_prompt(context, search_results)

            # Usa AI Manager para gerar avatar
            avatar_analysis = ai_manager.generate_content(
                avatar_prompt,
                max_tokens=4000
            )

            return {
                'avatar_detalhado': avatar_analysis,
                'base_data': context,
                'search_influence': len(search_results.get('resultados', [])),
                'generated_at': datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"❌ Erro ao gerar avatar: {str(e)}")
            return {
                'avatar_detalhado': "Avatar não pôde ser gerado devido a erro na IA",
                'error': str(e),
                'fallback_used': True
            }

    def _perform_deep_market_analysis(self, query: str, search_results: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Realiza análise profunda de mercado"""

        try:
            # Prepara prompt para análise de mercado
            market_prompt = self._build_market_analysis_prompt(query, search_results, context)

            # Usa AI Manager
            market_analysis = ai_manager.generate_content(
                market_prompt,
                max_tokens=8000
            )

            return {
                'analise_mercado': market_analysis,
                'dados_base': search_results,
                'contexto_aplicado': context,
                'generated_at': datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"❌ Erro na análise de mercado: {str(e)}")
            return {
                'analise_mercado': "Análise de mercado não pôde ser gerada devido a erro na IA",
                'error': str(e),
                'fallback_used': True
            }

    def _generate_future_predictions(self, query: str, market_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Gera predições futuras"""

        try:
            predictions_prompt = f"""
            Baseado na análise de mercado para "{query}", gere predições detalhadas para:

            1. Tendências dos próximos 6 meses
            2. Oportunidades emergentes em 1 ano
            3. Riscos e desafios potenciais
            4. Evolução do mercado em 2-3 anos

            Análise base: {str(market_analysis)[:2000]}

            Responda em formato estruturado e detalhado.
            """

            predictions = ai_manager.generate_content(predictions_prompt, max_tokens=4000)

            return {
                'predicoes_detalhadas': predictions,
                'base_analysis': market_analysis,
                'generated_at': datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"❌ Erro ao gerar predições: {str(e)}")
            return {
                'predicoes_detalhadas': "Predições não puderam ser geradas devido a erro na IA",
                'error': str(e),
                'fallback_used': True
            }

    def _generate_monetization_strategies(self, context: Dict[str, Any], market_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Gera estratégias de monetização"""

        try:
            monetization_prompt = f"""
            Baseado no contexto {context} e análise de mercado, crie estratégias detalhadas de monetização:

            1. Modelos de receita viáveis
            2. Precificação estratégica
            3. Canais de distribuição
            4. Parcerias potenciais
            5. Escalabilidade do negócio

            Análise: {str(market_analysis)[:2000]}

            Responda com estratégias práticas e acionáveis.
            """

            strategies = ai_manager.generate_content(monetization_prompt, max_tokens=4000)

            return {
                'estrategias_monetizacao': strategies,
                'contexto_base': context,
                'generated_at': datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"❌ Erro ao gerar estratégias: {str(e)}")
            return {
                'estrategias_monetizacao': "Estratégias não puderam ser geradas devido a erro na IA",
                'error': str(e),
                'fallback_used': True
            }

    def _generate_market_insights(self, query: str, search_results: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Gera insights de mercado (versão simplificada)"""

        try:
            insights_prompt = f"""
            Analise os dados de pesquisa para "{query}" e gere insights práticos:

            Dados: {str(search_results)[:3000]}
            Contexto: {context}

            Foque em:
            1. Oportunidades imediatas
            2. Tendências chave
            3. Público-alvo
            4. Recomendações estratégicas
            """

            insights = ai_manager.generate_content(insights_prompt, max_tokens=3000)

            return {
                'insights_mercado': insights,
                'generated_at': datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"❌ Erro ao gerar insights: {str(e)}")
            return {
                'insights_mercado': "Insights não puderam ser gerados",
                'error': str(e),
                'fallback_used': True
            }

    def _perform_forensic_investigation(self, query: str, search_results: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Realiza investigação forense"""

        try:
            forensic_prompt = f"""
            INVESTIGAÇÃO FORENSE DE MERCADO para "{query}":

            Analise profundamente os dados e identifique:
            1. Padrões ocultos nos dados
            2. Correlações não óbvias
            3. Sinais de oportunidade
            4. Evidências de demanda latente
            5. Análise competitiva detalhada

            Dados: {str(search_results)[:3000]}
            Contexto: {context}

            Responda como um investigador experiente.
            """

            forensic_data = ai_manager.generate_content(forensic_prompt, max_tokens=5000)

            return {
                'investigacao_forense': forensic_data,
                'generated_at': datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"❌ Erro na investigação forense: {str(e)}")
            return {
                'investigacao_forense': "Investigação forense não pôde ser realizada",
                'error': str(e),
                'fallback_used': True
            }

    def _perform_archaeological_excavation(self, query: str, search_results: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Realiza escavação arqueológica de dados"""

        try:
            archaeological_prompt = f"""
            ESCAVAÇÃO ARQUEOLÓGICA DE MERCADO para "{query}":

            Como um arqueólogo de dados, escave profundamente e encontre:
            1. Artefatos de valor (dados únicos)
            2. Camadas históricas do mercado
            3. Evolução temporal das tendências
            4. Descobertas surpreendentes
            5. Tesouros escondidos de oportunidade

            Sítio de escavação: {str(search_results)[:3000]}
            Contexto histórico: {context}

            Relate suas descobertas como um arqueólogo experiente.
            """

            archaeological_findings = ai_manager.generate_content(archaeological_prompt, max_tokens=5000)

            return {
                'descobertas_arqueologicas': archaeological_findings,
                'generated_at': datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"❌ Erro na escavação arqueológica: {str(e)}")
            return {
                'descobertas_arqueologicas': "Escavação arqueológica não pôde ser realizada",
                'error': str(e),
                'fallback_used': True
            }

    def _generate_unified_insights(self, query: str, search_results: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Gera insights unificados combinando todas as abordagens"""

        try:
            unified_prompt = f"""
            ANÁLISE UNIFICADA COMPLETA para "{query}":

            Combine as perspectivas de:
            - Analista de mercado detalhado
            - Investigador forense
            - Arqueólogo de dados
            - Estrategista de negócios

            Dados: {str(search_results)[:3000]}
            Contexto: {context}

            Gere insights que integrem todas essas visões em uma análise coesa e acionável.
            """

            unified_insights = ai_manager.generate_content(unified_prompt, max_tokens=6000)

            return {
                'insights_unificados': unified_insights,
                'generated_at': datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"❌ Erro nos insights unificados: {str(e)}")
            return {
                'insights_unificados': "Insights unificados não puderam ser gerados",
                'error': str(e),
                'fallback_used': True
            }

    def _build_avatar_prompt(self, context: Dict[str, Any], search_results: Dict[str, Any]) -> str:
        """Constrói prompt para geração de avatar"""

        segmento = context.get('segmento', 'não especificado')
        produto = context.get('produto', 'não especificado')

        return f"""
        Crie um avatar ultra-detalhado para o segmento "{segmento}" e produto "{produto}".

        Baseado nos dados de pesquisa: {str(search_results)[:2000]}

        O avatar deve incluir:
        1. Demografia detalhada
        2. Psicografia profunda
        3. Comportamentos online
        4. Dores e necessidades
        5. Motivações de compra
        6. Jornada do cliente
        7. Canais de comunicação preferidos
        8. Influenciadores que segue

        Seja extremamente específico e detalhado.
        """

    def _build_market_analysis_prompt(self, query: str, search_results: Dict[str, Any], context: Dict[str, Any]) -> str:
        """Constrói prompt para análise de mercado"""

        return f"""
        Realize uma análise ultra-profunda de mercado para "{query}".

        Dados de pesquisa: {str(search_results)[:3000]}
        Contexto: {context}

        Analise:
        1. Tamanho e potencial do mercado
        2. Segmentação detalhada
        3. Tendências emergentes
        4. Análise competitiva
        5. Barreiras de entrada
        6. Oportunidades de nicho
        7. Riscos e desafios
        8. Projeções financeiras
        9. Estratégias de entrada
        10. Plano de ação detalhado

        Seja detalhado, específico e orientado a resultados.
        """

# Instância global
master_analysis_engine = MasterAnalysisEngine()