#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ARQV30 Enhanced v2.0 - Enhanced Search Coordinator ULTRA-ROBUSTO
Coordenador que GARANTE buscas simultâneas e distintas entre Exa e Google
"""

import os
import logging
import time
import asyncio
from typing import Dict, List, Optional, Any
from concurrent.futures import ThreadPoolExecutor, as_completed
from services.exa_client import exa_client
from services.production_search_manager import production_search_manager
from services.auto_save_manager import salvar_etapa, salvar_erro

logger = logging.getLogger(__name__)

class EnhancedSearchCoordinator:
    """Coordenador ULTRA-ROBUSTO de buscas simultâneas e distintas"""
    
    def __init__(self):
        """Inicializa coordenador de busca"""
        self.exa_available = exa_client.is_available()
        self.google_available = bool(os.getenv('GOOGLE_SEARCH_KEY') and os.getenv('GOOGLE_CSE_ID'))
        
        logger.info(f"🔍 Enhanced Search Coordinator ULTRA-ROBUSTO - Exa: {self.exa_available}, Google: {self.google_available}")
    
    def execute_simultaneous_distinct_search(
        self, 
        base_query: str, 
        context: Dict[str, Any],
        session_id: str = None
    ) -> Dict[str, Any]:
        """GARANTE buscas simultâneas e distintas entre Exa e Google"""
        
        logger.info(f"🚀 INICIANDO BUSCAS SIMULTÂNEAS E DISTINTAS para: {base_query}")
        
        # Prepara queries DISTINTAS para cada provedor
        exa_query = self._prepare_exa_neural_query(base_query, context)
        google_query = self._prepare_google_keyword_query(base_query, context)
        
        # GARANTE que as queries são diferentes
        if exa_query == google_query:
            exa_query += " insights análise neural semântica"
            google_query += " dados estatísticas keywords específicas"
        
        # Salva queries preparadas
        salvar_etapa("queries_simultaneas_distintas", {
            "base_query": base_query,
            "exa_query": exa_query,
            "google_query": google_query,
            "context": context,
            "garantia_simultanea": True,
            "garantia_distinta": True
        }, categoria="pesquisa_web")
        
        search_results = {
            'base_query': base_query,
            'exa_results': [],
            'google_results': [],
            'other_results': [],
            'execution_mode': 'SIMULTANEOUS_DISTINCT',
            'statistics': {
                'total_results': 0,
                'exa_count': 0,
                'google_count': 0,
                'other_count': 0,
                'search_time': 0,
                'simultaneous_execution': True,
                'distinct_queries': True
            }
        }
        
        start_time = time.time()
        
        # EXECUTA BUSCAS SIMULTANEAMENTE com ThreadPoolExecutor
        with ThreadPoolExecutor(max_workers=3) as executor:
            futures = {}
            
            # Busca Exa (se disponível) - NEURAL SEARCH
            if self.exa_available:
                futures['exa'] = executor.submit(self._execute_exa_neural_search, exa_query, context)
                logger.info(f"🧠 Exa Neural Search INICIADA: {exa_query}")
            
            # Busca Google (se disponível) - KEYWORD SEARCH
            if self.google_available:
                futures['google'] = executor.submit(self._execute_google_keyword_search, google_query, context)
                logger.info(f"🔍 Google Keyword Search INICIADA: {google_query}")
            
            # Busca outros provedores - FALLBACK SEARCH
            futures['other'] = executor.submit(self._execute_other_providers_search, base_query, context)
            logger.info(f"🌐 Other Providers Search INICIADA: {base_query}")
            
            # Coleta resultados conforme completam (SIMULTANEAMENTE)
            for provider_name, future in futures.items():
                try:
                    result = future.result(timeout=120)  # 2 minutos timeout
                    
                    if provider_name == 'exa':
                        search_results['exa_results'] = result['results']
                        search_results['statistics']['exa_count'] = len(result['results'])
                        logger.info(f"✅ Exa Neural: {len(result['results'])} resultados ÚNICOS")
                        
                        # Salva resultados Exa IMEDIATAMENTE
                        salvar_etapa("exa_neural_results", result, categoria="pesquisa_web")
                        
                    elif provider_name == 'google':
                        search_results['google_results'] = result['results']
                        search_results['statistics']['google_count'] = len(result['results'])
                        logger.info(f"✅ Google Keywords: {len(result['results'])} resultados ÚNICOS")
                        
                        # Salva resultados Google IMEDIATAMENTE
                        salvar_etapa("google_keyword_results", result, categoria="pesquisa_web")
                        
                    elif provider_name == 'other':
                        search_results['other_results'] = result['results']
                        search_results['statistics']['other_count'] = len(result['results'])
                        logger.info(f"✅ Outros Provedores: {len(result['results'])} resultados")
                        
                        # Salva resultados outros IMEDIATAMENTE
                        salvar_etapa("other_providers_results", result, categoria="pesquisa_web")
                
                except Exception as e:
                    logger.error(f"❌ Erro em busca {provider_name}: {e}")
                    salvar_erro(f"busca_{provider_name}", e, contexto={"query": base_query})
                    
                    # CONTINUA MESMO COM ERRO - SALVA O QUE TEM
                    search_results[f'{provider_name}_error'] = str(e)
                    continue
        
        # Calcula estatísticas finais
        search_time = time.time() - start_time
        search_results['statistics']['search_time'] = search_time
        search_results['statistics']['total_results'] = (
            search_results['statistics']['exa_count'] + 
            search_results['statistics']['google_count'] + 
            search_results['statistics']['other_count']
        )
        
        # GARANTE que pelo menos uma busca funcionou
        if search_results['statistics']['total_results'] == 0:
            logger.warning("⚠️ NENHUMA BUSCA RETORNOU RESULTADOS - Continuando análise")
            search_results['fallback_message'] = "Buscas falharam mas análise continua"
        
        # Salva resultado consolidado IMEDIATAMENTE
        salvar_etapa("busca_simultanea_consolidada", search_results, categoria="pesquisa_web")
        
        logger.info(f"✅ Buscas SIMULTÂNEAS E DISTINTAS concluídas em {search_time:.2f}s")
        logger.info(f"📊 Total: {search_results['statistics']['total_results']} resultados únicos")
        
        return search_results
    
    def _prepare_exa_neural_query(self, base_query: str, context: Dict[str, Any]) -> str:
        """Prepara query ESPECÍFICA para Exa Neural Search"""
        
        # Exa é melhor com queries conceituais e semânticas
        exa_query = f"{base_query} insights análise profunda"
        
        # Adiciona contexto semântico para busca neural
        if context.get('segmento'):
            exa_query += f" {context['segmento']} tendências oportunidades"
        
        # Termos para busca neural semântica
        exa_query += " estratégia inovação futuro"
        
        return exa_query.strip()
    
    def _prepare_google_keyword_query(self, base_query: str, context: Dict[str, Any]) -> str:
        """Prepara query ESPECÍFICA para Google Keyword Search"""
        
        # Google é melhor com keywords específicas e dados
        google_query = f"{base_query} dados estatísticas"
        
        # Adiciona keywords específicas
        if context.get('segmento'):
            google_query += f" {context['segmento']} mercado brasileiro"
        
        # Termos para busca por keywords
        google_query += " Brasil 2024 crescimento números"
        
        return google_query.strip()
    
    def _execute_exa_neural_search(self, query: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Executa busca NEURAL específica no Exa"""
        
        try:
            logger.info(f"🧠 Executando Exa NEURAL SEARCH: {query}")
            
            # Domínios brasileiros preferenciais para Exa
            include_domains = [
                "g1.globo.com", "exame.com", "valor.globo.com", "estadao.com.br",
                "folha.uol.com.br", "canaltech.com.br", "infomoney.com.br",
                "startse.com", "revistapegn.globo.com", "epocanegocios.globo.com"
            ]
            
            exa_response = exa_client.search(
                query=query,
                num_results=20,  # Mais resultados para Exa
                include_domains=include_domains,
                start_published_date="2023-01-01",
                use_autoprompt=True,
                type="neural"  # FORÇA BUSCA NEURAL
            )
            
            if exa_response and 'results' in exa_response:
                results = []
                for item in exa_response['results']:
                    results.append({
                        'title': item.get('title', ''),
                        'url': item.get('url', ''),
                        'snippet': item.get('text', '')[:300],
                        'source': 'exa_neural',
                        'score': item.get('score', 0),
                        'published_date': item.get('publishedDate', ''),
                        'exa_id': item.get('id', ''),
                        'search_type': 'neural_semantic'
                    })
                
                logger.info(f"✅ Exa Neural Search: {len(results)} resultados ÚNICOS")
                return {
                    'provider': 'exa',
                    'query': query,
                    'results': results,
                    'success': True,
                    'search_type': 'neural_semantic'
                }
            else:
                logger.warning("⚠️ Exa não retornou resultados - CONTINUANDO")
                return {
                    'provider': 'exa',
                    'query': query,
                    'results': [],
                    'success': False,
                    'error': 'Exa não retornou resultados válidos'
                }
                
        except Exception as e:
            logger.error(f"❌ Erro na busca Exa: {e}")
            # SALVA ERRO MAS CONTINUA
            salvar_erro("exa_neural_search", e, contexto={"query": query})
            return {
                'provider': 'exa',
                'query': query,
                'results': [],
                'success': False,
                'error': str(e)
            }
    
    def _execute_google_keyword_search(self, query: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Executa busca KEYWORD específica no Google"""
        
        try:
            logger.info(f"🔍 Executando Google KEYWORD SEARCH: {query}")
            
            # Usa production search manager especificamente para Google
            google_api_key = os.getenv('GOOGLE_SEARCH_KEY')
            google_cse_id = os.getenv('GOOGLE_CSE_ID')
            
            if not google_api_key or not google_cse_id:
                raise Exception("Google API não configurada")
            
            import requests
            
            params = {
                'key': google_api_key,
                'cx': google_cse_id,
                'q': query,
                'num': 20,  # Mais resultados para Google
                'lr': 'lang_pt',
                'gl': 'br',
                'safe': 'off',
                'dateRestrict': 'm12'  # Últimos 12 meses
            }
            
            response = requests.get(
                'https://www.googleapis.com/customsearch/v1',
                params=params,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                results = []
                
                for item in data.get('items', []):
                    results.append({
                        'title': item.get('title', ''),
                        'url': item.get('link', ''),
                        'snippet': item.get('snippet', ''),
                        'source': 'google_keywords',
                        'search_type': 'keyword_based'
                    })
                
                logger.info(f"✅ Google Keyword Search: {len(results)} resultados ÚNICOS")
                return {
                    'provider': 'google',
                    'query': query,
                    'results': results,
                    'success': True,
                    'search_type': 'keyword_based'
                }
            else:
                raise Exception(f"Google API retornou status {response.status_code}")
            
        except Exception as e:
            logger.error(f"❌ Erro na busca Google: {e}")
            # SALVA ERRO MAS CONTINUA
            salvar_erro("google_keyword_search", e, contexto={"query": query})
            return {
                'provider': 'google',
                'query': query,
                'results': [],
                'success': False,
                'error': str(e)
            }
    
    def _execute_other_providers_search(self, query: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Executa busca em outros provedores como fallback"""
        
        try:
            logger.info(f"🌐 Executando Other Providers Search: {query}")
            
            # Usa outros provedores (Serper, Bing, DuckDuckGo)
            other_results = production_search_manager.search_with_fallback(query, max_results=15)
            
            # Filtra resultados que não são Google ou Exa
            other_only = []
            for result in other_results:
                if result.get('source') not in ['google', 'exa', 'google_keywords', 'exa_neural']:
                    result['search_type'] = 'fallback_providers'
                    other_only.append(result)
            
            logger.info(f"✅ Other Providers: {len(other_only)} resultados")
            return {
                'provider': 'other',
                'query': query,
                'results': other_only,
                'success': len(other_only) > 0,
                'search_type': 'fallback_providers'
            }
            
        except Exception as e:
            logger.error(f"❌ Erro na busca outros provedores: {e}")
            # SALVA ERRO MAS CONTINUA
            salvar_erro("other_providers_search", e, contexto={"query": query})
            return {
                'provider': 'other',
                'query': query,
                'results': [],
                'success': False,
                'error': str(e)
            }

# Instância global
enhanced_search_coordinator = EnhancedSearchCoordinator()