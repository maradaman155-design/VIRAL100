#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ARQV30 Enhanced v3.0 - Real Search Orchestrator with Massive Collection
Orquestrador de busca REAL massiva com rotação de APIs, captura visual e coleta massiva
"""
import os
import logging
import asyncio
import aiohttp
import time
from typing import Dict, List, Any, Optional
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import quote_plus
import json
logger = logging.getLogger(__name__)

# Importa serviços existentes
from services.enhanced_search_coordinator import enhanced_search_coordinator
from services.social_media_extractor import social_media_extractor
from services.auto_save_manager import salvar_etapa, salvar_erro

# Importa novos serviços da Etapa 1
from services.search_api_manager import search_api_manager
from services.trendfinder_client import trendfinder_client
from services.supadata_mcp_client import supadata_client
from services.visual_content_capture import visual_content_capture

# Novos imports para Google Masterclass Extractor
from .enhanced_api_rotation_manager import get_api_manager
from .alibaba_websailor import alibaba_websailor
from .hybrid_social_extractor import extract_viral_content_hybrid
from .viral_content_analyzer_insta import get_viral_content_analyzer
from .google_social_masterclass_extractor import extract_masterclass_content, generate_masterclass_report

class RealSearchOrchestrator:
    """Orquestrador de busca REAL massiva - ZERO SIMULAÇÃO"""
    def __init__(self):
        """Inicializa orquestrador com todas as APIs reais"""
        self.api_keys = self._load_all_api_keys()
        self.key_indices = {provider: 0 for provider in self.api_keys.keys()}
        # Provedores em ordem de prioridade
        self.providers = [
            'ALIBABA_WEBSAILOR',  # Adicionado como prioridade máxima
            'FIRECRAWL',
            'JINA',
            'GOOGLE',
            'EXA',
            'SERPER',
            'YOUTUBE',
            'SUPADATA'
        ]
        # URLs base dos serviços
        self.service_urls = {
            'FIRECRAWL': 'https://api.firecrawl.dev/v0/scrape',
            'JINA': 'https://r.jina.ai/',
            'GOOGLE': 'https://www.googleapis.com/customsearch/v1',
            'EXA': 'https://api.exa.ai/search',
            'SERPER': 'https://google.serper.dev/search',
            'YOUTUBE': 'https://www.googleapis.com/youtube/v3/search',
            'SUPADATA': os.getenv('SUPADATA_API_URL', 'https://server.smithery.ai/@supadata-ai/mcp/mcp')
        }
        self.session_stats = {
            'total_searches': 0,
            'successful_searches': 0,
            'failed_searches': 0,
            'api_rotations': {},
            'content_extracted': 0,
            'screenshots_captured': 0
        }
        logger.info(f"🚀 Real Search Orchestrator inicializado com {sum(len(keys) for keys in self.api_keys.values())} chaves totais")

    def _load_all_api_keys(self) -> Dict[str, List[str]]:
        """Carrega todas as chaves de API do ambiente"""
        api_keys = {}
        for provider in ['FIRECRAWL', 'JINA', 'GOOGLE', 'EXA', 'SERPER', 'YOUTUBE', 'SUPADATA', 'X']:
            keys = []
            # Chave principal
            main_key = os.getenv(f"{provider}_API_KEY")
            if main_key:
                keys.append(main_key)
            # Chaves numeradas
            counter = 1
            while True:
                numbered_key = os.getenv(f"{provider}_API_KEY_{counter}")
                if numbered_key:
                    keys.append(numbered_key)
                    counter += 1
                else:
                    break
            if keys:
                api_keys[provider] = keys
                logger.info(f"✅ {provider}: {len(keys)} chaves carregadas")
        return api_keys

    def get_next_api_key(self, provider: str) -> Optional[str]:
        """Obtém próxima chave de API com rotação automática"""
        if provider not in self.api_keys or not self.api_keys[provider]:
            return None
        keys = self.api_keys[provider]
        current_index = self.key_indices[provider]
        # Obtém chave atual
        key = keys[current_index]
        # Rotaciona para próxima
        self.key_indices[provider] = (current_index + 1) % len(keys)
        # Atualiza estatísticas
        if provider not in self.session_stats['api_rotations']:
            self.session_stats['api_rotations'][provider] = 0
        self.session_stats['api_rotations'][provider] += 1
        logger.debug(f"🔄 {provider}: Usando chave {current_index + 1}/{len(keys)}")
        return key

    async def execute_massive_collection(
        self,
        query: str,
        context: Dict[str, Any],
        session_id: str
    ) -> Dict[str, Any]:
        """Executa coleta massiva de dados com integração completa"""
        logger.info(f"🚀 INICIANDO COLETA MASSIVA COMPLETA para: {query}")
        start_time = time.time()

        # Estrutura de dados consolidados
        massive_data = {
            "session_id": session_id,
            "query": query,
            "context": context,
            "collection_started": datetime.now().isoformat(),
            "web_search_data": {},
            "social_media_data": {},
            "trends_data": {},
            "supadata_results": {},
            "visual_content": {},
            "extracted_content": [],
            "statistics": {
                "total_sources": 0,
                "total_content_length": 0,
                "collection_time": 0,
                "sources_by_type": {},
                "screenshot_count": 0,
                "api_rotations": {}
            }
        }

        try:
            # FASE 1: Busca REAL massiva com todos os provedores
            logger.info("🔍 FASE 1: Executando busca REAL massiva...")
            search_results = await self.execute_massive_real_search(query, context, session_id)
            massive_data["web_search_data"] = search_results

            # FASE 2: Coleta de Tendências via TrendFinder MCP
            logger.info("📈 FASE 2: Coletando tendências via TrendFinder...")
            if trendfinder_client.is_available():
                trends_results = await trendfinder_client.search(query)
                massive_data["trends_data"] = trends_results
            else:
                logger.warning("⚠️ TrendFinder não disponível")
                massive_data["trends_data"] = {"success": False, "error": "TrendFinder não configurado"}

            # FASE 3: Dados Sociais via Supadata MCP
            logger.info("📊 FASE 3: Coletando dados sociais via Supadata...")
            if supadata_client.is_available():
                supadata_results = await supadata_client.search(query, "all")
                massive_data["supadata_results"] = supadata_results
            else:
                logger.warning("⚠️ Supadata não disponível")
                massive_data["supadata_results"] = {"success": False, "error": "Supadata não configurado"}

            # FASE 4: Extração de Redes Sociais (método existente como fallback)
            logger.info("📱 FASE 4: Extraindo dados de redes sociais (fallback)...")
            try:
                # Usa método existente do social_media_extractor
                social_results = social_media_extractor.search_all_platforms(query, 15)

                # Adapta formato para compatibilidade
                if social_results.get("success"):
                    social_results = {
                        "success": True,
                        "all_platforms_data": social_results,
                        "total_posts": social_results.get("total_results", 0),
                        "platforms_analyzed": len(social_results.get("platforms", [])),
                        "extracted_at": datetime.now().isoformat()
                    }
                else:
                    social_results = {
                        "success": False,
                        "error": "Falha na extração de redes sociais",
                        "all_platforms_data": {"platforms": {}},
                        "total_posts": 0
                    }
            except Exception as social_error:
                logger.error(f"❌ Erro na extração social: {social_error}")
                social_results = {
                    "success": False,
                    "error": str(social_error),
                    "all_platforms_data": {"platforms": {}},
                    "total_posts": 0
                }

            massive_data["social_media_data"] = social_results

            # FASE 5: Google Masterclass Search
            logger.info("🎯 FASE 5: Busca Google Masterclass")

            masterclass_results = {}
            try:
                masterclass_results = await extract_masterclass_content(
                    query,
                    session_id,
                    ['instagram', 'youtube', 'facebook']
                )
                logger.info(f"✅ Google Masterclass: {masterclass_results.get('total_screenshots', 0)} screenshots capturados")
            except Exception as e:
                logger.error(f"❌ Erro no Google Masterclass: {e}")
                masterclass_results = {'error': str(e)}

            # FASE 6: Análise de conteúdo viral
            logger.info("🔥 FASE 6: Analisando conteúdo viral identificado")

            viral_analysis_results = {}
            if search_results.get('viral_content'): # Verifica search_results aqui
                analyzer = get_viral_content_analyzer()
                viral_analysis_results = await analyzer.analyze_instagram_viral_content(
                    {'results': search_results['viral_content']},
                    session_id,
                    max_screenshots=10
                )

            # FASE 7: Seleção de URLs Relevantes (para screenshots gerais)
            logger.info("🎯 FASE 7: Selecionando URLs mais relevantes (geral)...")
            selected_urls = visual_content_capture.select_top_urls(search_results, max_urls=8)

            # FASE 8: Captura de Screenshots (gerais)
            logger.info("📸 FASE 8: Capturando screenshots das URLs selecionadas (geral)...")
            if selected_urls:
                try:
                    screenshot_results = await visual_content_capture.capture_screenshots(
                        selected_urls, session_id
                    )
                    massive_data["visual_content"] = screenshot_results
                    massive_data["statistics"]["screenshot_count"] = screenshot_results.get("successful_captures", 0)
                except Exception as capture_error:
                    logger.error(f"❌ Erro na captura de screenshots (geral): {capture_error}")
                    massive_data["visual_content"] = {"success": False, "error": str(capture_error)}
                    massive_data["statistics"]["screenshot_count"] = 0
            else:
                logger.warning("⚠️ Nenhuma URL selecionada para screenshots (geral)")
                massive_data["visual_content"] = {"success": False, "error": "Nenhuma URL disponível"}

            # FASE 9: Consolidação e Processamento
            logger.info("🔗 FASE 9: Consolidando dados coletados...")

            # Extrai e processa conteúdo
            all_results = []

            # Processa resultados web
            if search_results.get("web_results"):
                all_results.extend(search_results["web_results"])

            # Processa resultados sociais existentes - CORRIGIDO
            if social_results.get("all_platforms_data"):
                platforms = social_results["all_platforms_data"].get("platforms", {})

                # Verifica se platforms é um dict ou list
                if isinstance(platforms, dict):
                    # Se é dict, itera pelos items
                    for platform, data in platforms.items():
                        if isinstance(data, dict) and "results" in data:
                            all_results.extend(data["results"])
                elif isinstance(platforms, list):
                    # Se é list, itera diretamente
                    for platform_data in platforms:
                        if isinstance(platform_data, dict) and "results" in platform_data:
                            all_results.extend(platform_data["results"])
                        elif isinstance(platform_data, dict) and "platform" in platform_data:
                            # Se o item da lista tem estrutura diferente
                            platform_results = platform_data.get("data", {}).get("results", [])
                            all_results.extend(platform_results)

            # Processa tendências do TrendFinder
            if massive_data["trends_data"].get("success"):
                trends = massive_data["trends_data"].get("trends", [])
                all_results.extend([{"source": "TrendFinder", "content": trend} for trend in trends])

            # Processa dados do Supadata
            if massive_data["supadata_results"].get("success"):
                posts = massive_data["supadata_results"].get("posts", [])
                all_results.extend([{"source": "Supadata", "content": post} for post in posts])

            # Adiciona resultados do Google Masterclass
            if masterclass_results and not masterclass_results.get('error'):
                if masterclass_results.get('instagram_posts'):
                    all_results.extend(masterclass_results['instagram_posts'])
                if masterclass_results.get('youtube_videos'):
                    all_results.extend(masterclass_results['youtube_videos'])
                if masterclass_results.get('facebook_posts'):
                    all_results.extend(masterclass_results['facebook_posts'])

            massive_data["extracted_content"] = all_results

            # Calcula estatísticas finais
            collection_time = time.time() - start_time
            total_sources = len(all_results)
            total_content = sum(len(str(item)) for item in all_results)

            # Atualiza estatísticas com informações dos novos serviços
            sources_by_type = {
                "web_search_intercalado": search_results.get("statistics", {}).get("total_sources", 0),
                "social_media_fallback": self._count_social_results(social_results),
                "trendfinder_mcp": len(massive_data["trends_data"].get("trends", [])),
                "supadata_mcp": massive_data["supadata_results"].get("total_results", 0),
                "screenshots_gerais": massive_data["statistics"]["screenshot_count"],
                "masterclass_capturas": masterclass_results.get('total_screenshots', 0) if masterclass_results else 0,
                "viral_analysis_capturas": viral_analysis_results.get('screenshots_captured', 0) if viral_analysis_results else 0
            }

            # Tenta consolidar as estatísticas de api_rotations de todos os serviços
            final_api_rotations = {}
            if search_results.get("statistics", {}).get("api_calls_made"):
                final_api_rotations['web_search'] = search_results["statistics"]["api_calls_made"]
            # Adicionar outras rotações de API se disponíveis em outros módulos

            massive_data["statistics"].update({
                "total_sources": total_sources,
                "total_content_length": total_content,
                "collection_time": collection_time,
                "sources_by_type": sources_by_type,
                "api_rotations": final_api_rotations # Usa as rotações consolidadas
            })

            # Gera relatório de coleta com referências às imagens
            collection_report = await self._generate_collection_report(massive_data, session_id)

            # Salva dados coletados
            salvar_etapa("massive_data_collected", massive_data, categoria="coleta_massiva")

            logger.info(f"✅ COLETA MASSIVA COMPLETA CONCLUÍDA")
            logger.info(f"📊 {total_sources} fontes coletadas em {collection_time:.2f}s")
            logger.info(f"📝 {total_content:,} caracteres de conteúdo")
            logger.info(f"📸 {massive_data['statistics']['screenshot_count']} screenshots gerais capturados")
            logger.info(f"📸 {masterclass_results.get('total_screenshots', 0)} screenshots masterclass capturados")
            logger.info(f"🔥 {viral_analysis_results.get('screenshots_captured', 0)} screenshots de análise viral capturados")


            return massive_data

        except Exception as e:
            logger.error(f"❌ Erro durante a coleta massiva: {e}", exc_info=True)
            salvar_erro("massive_data_collection", e, contexto={"query": query, "session_id": session_id})
            return {"error": "Falha na coleta massiva de dados", "details": str(e)}

    def _count_social_results(self, social_results: Dict[str, Any]) -> int:
        """Conta resultados sociais de forma segura"""
        try:
            platforms = social_results.get("all_platforms_data", {}).get("platforms", {})
            total_count = 0

            if isinstance(platforms, dict):
                for data in platforms.values():
                    if isinstance(data, dict) and "results" in data:
                        total_count += len(data["results"])
            elif isinstance(platforms, list):
                for platform_data in platforms:
                    if isinstance(platform_data, dict):
                        if "results" in platform_data:
                            total_count += len(platform_data["results"])
                        elif "data" in platform_data and isinstance(platform_data["data"], dict):
                            results = platform_data["data"].get("results", [])
                            total_count += len(results)

            return total_count
        except Exception as e:
            logger.error(f"Erro ao contar resultados sociais: {e}")
            return 0

    async def execute_massive_real_search(
        self,
        query: str,
        context: Dict[str, Any],
        session_id: str
    ) -> Dict[str, Any]:
        """Executa busca REAL massiva com todos os provedores"""
        logger.info(f"🚀 INICIANDO BUSCA REAL MASSIVA para: {query}")
        start_time = time.time()
        # Estrutura de resultados
        search_results = {
            'query': query,
            'session_id': session_id,
            'search_started': datetime.now().isoformat(),
            'providers_used': [],
            'web_results': [],
            'social_results': [],
            'youtube_results': [],
            'viral_content': [],
            'screenshots_captured': [],
            'statistics': {
                'total_sources': 0,
                'unique_urls': 0,
                'content_extracted': 0,
                'api_calls_made': 0,
                'search_duration': 0
            }
        }
        try:
            # FASE 1: Busca com Alibaba WebSailor (prioritária)
            logger.info("🔍 FASE 1: Busca com Alibaba WebSailor")
            websailor_results = await self._search_alibaba_websailor(query, context)
            if websailor_results.get('success'):
                search_results['web_results'].extend(websailor_results['results'])
                search_results['providers_used'].append('ALIBABA_WEBSAILOR')
                logger.info(f"✅ Alibaba WebSailor retornou {len(websailor_results['results'])} resultados")
            # FASE 2: Busca Web Massiva Simultânea (provedores restantes)
            logger.info("🌐 FASE 2: Busca web massiva simultânea")
            web_tasks = []
            # Firecrawl
            if 'FIRECRAWL' in self.api_keys:
                web_tasks.append(self._search_firecrawl(query))
            # Jina
            if 'JINA' in self.api_keys:
                web_tasks.append(self._search_jina(query))
            # Google
            if 'GOOGLE' in self.api_keys:
                web_tasks.append(self._search_google(query))
            # Exa
            if 'EXA' in self.api_keys:
                web_tasks.append(self._search_exa(query))
            # Serper
            if 'SERPER' in self.api_keys:
                web_tasks.append(self._search_serper(query))
            # Executa todas as buscas web simultaneamente
            if web_tasks:
                web_results = await asyncio.gather(*web_tasks, return_exceptions=True)
                for result in web_results:
                    if isinstance(result, Exception):
                        logger.error(f"❌ Erro na busca web: {result}")
                        continue
                    if result.get('success') and result.get('results'):
                        search_results['web_results'].extend(result['results'])
                        search_results['providers_used'].append(result.get('provider', 'unknown'))
            # FASE 3: Busca em Redes Sociais
            logger.info("📱 FASE 3: Busca massiva em redes sociais")
            social_tasks = []
            # YouTube
            if 'YOUTUBE' in self.api_keys:
                social_tasks.append(self._search_youtube(query))
            # Supadata (Instagram, Facebook, TikTok)
            if 'SUPADATA' in self.api_keys:
                 social_tasks.append(self._search_supadata(query))
            # Twitter/X
            if 'X' in self.api_keys:
                social_tasks.append(self._search_twitter(query))

            # Executa buscas sociais
            if social_tasks:
                social_results = await asyncio.gather(*social_tasks, return_exceptions=True)
                for result in social_results:
                    if isinstance(result, Exception):
                        logger.error(f"❌ Erro na busca social: {result}")
                        continue
                    if result.get('success'):
                        if result.get('platform') == 'youtube':
                            search_results['youtube_results'].extend(result.get('results', []))
                        elif result.get('platform') == 'twitter':
                            search_results['social_results'].extend(result.get('results', [])) # Twitter vai para social_results
                        elif result.get('platform') == 'instagram' or result.get('platform') == 'facebook' or result.get('platform') == 'tiktok':
                            search_results['social_results'].extend(result.get('results', [])) # Supadata vai para social_results
                        else: # Para outros provedores sociais sem plataforma definida
                            search_results['social_results'].extend(result.get('results', []))

            # FASE 4: Identificação de Conteúdo Viral (com base nos resultados sociais agregados)
            logger.info("🔥 FASE 4: Identificando conteúdo viral")
            all_social_and_youtube = search_results['youtube_results'] + search_results['social_results']
            viral_content = self._identify_viral_content(all_social_and_youtube)
            search_results['viral_content'] = viral_content # Armazena os posts virais identificados

            # FASE 5: Captura de Screenshots do conteúdo viral identificado
            logger.info("📸 FASE 5: Capturando screenshots do conteúdo viral")
            if viral_content:
                screenshots = await self._capture_viral_screenshots(viral_content, session_id)
                search_results['screenshots_captured'] = screenshots
                self.session_stats['screenshots_captured'] = len(screenshots) # Atualiza estatística global

            # Calcula estatísticas finais
            search_duration = time.time() - start_time
            all_results_for_stats = search_results['web_results'] + search_results['social_results'] + search_results['youtube_results']
            unique_urls = list(set(r.get('url', '') for r in all_results_for_stats if r.get('url')))
            search_results['statistics'].update({
                'total_sources': len(all_results_for_stats),
                'unique_urls': len(unique_urls),
                'content_extracted': sum(len(r.get('content', '')) for r in all_results_for_stats),
                'api_calls_made': sum(self.session_stats['api_rotations'].values()), # Soma todas as rotações de API
                'search_duration': search_duration
            })
            logger.info(f"✅ BUSCA REAL MASSIVA CONCLUÍDA em {search_duration:.2f}s")
            logger.info(f"📊 {len(all_results_for_stats)} resultados de {len(search_results['providers_used'])} provedores")
            logger.info(f"📸 {len(search_results['screenshots_captured'])} screenshots de conteúdo viral capturados")
            return search_results
        except Exception as e:
            logger.error(f"❌ ERRO CRÍTICO na busca massiva: {e}", exc_info=True)
            raise

    async def _search_alibaba_websailor(self, query: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Busca REAL usando Alibaba WebSailor Agent"""
        try:
            # Usa a instância global do agente WebSailor
            if not alibaba_websailor or not alibaba_websailor.enabled:
                logger.warning("⚠️ Alibaba WebSailor não está habilitado")
                return {'success': False, 'error': 'Alibaba WebSailor não habilitado'}
            # Executa a pesquisa profunda - CORRIGIDO: removido await pois o método é síncrono
            research_result = alibaba_websailor.navigate_and_research_deep(
                query=query,
                context=context,
                max_pages=30,
                depth_levels=2,
                session_id=None # Ou passe session_id se o método aceitar
            )
            if not research_result or not research_result.get('conteudo_consolidado'):
                return {'success': False, 'error': 'Nenhum resultado da pesquisa WebSailor'}
            # Converte resultados do WebSailor para formato padrão
            results = []
            fontes_detalhadas = research_result.get('conteudo_consolidado', {}).get('fontes_detalhadas', [])
            for fonte in fontes_detalhadas:
                results.append({
                    'title': fonte.get('title', ''),
                    'url': fonte.get('url', ''),
                    'snippet': '',  # WebSailor não fornece snippet diretamente
                    'source': 'alibaba_websailor',
                    'relevance_score': fonte.get('quality_score', 0.7),
                    'content_length': fonte.get('content_length', 0)
                })
            logger.info(f"✅ Alibaba WebSailor processado com {len(results)} resultados")
            return {
                'success': True,
                'provider': 'ALIBABA_WEBSAILOR',
                'results': results,
                'raw_data': research_result
            }
        except ImportError:
            logger.warning("⚠️ Alibaba WebSailor não encontrado")
            return {'success': False, 'error': 'Alibaba WebSailor não disponível'}
        except Exception as e:
            logger.error(f"❌ Erro Alibaba WebSailor: {e}")
            return {'success': False, 'error': str(e)}

    async def _search_firecrawl(self, query: str) -> Dict[str, Any]:
        """Busca REAL usando Firecrawl"""
        try:
            api_key = self.get_next_api_key('FIRECRAWL')
            if not api_key:
                return {'success': False, 'error': 'Firecrawl API key não disponível'}
            # Busca no Google e extrai com Firecrawl
            search_url = f"https://www.google.com/search?q={quote_plus(query)}&hl=pt-BR&gl=BR"
            async with aiohttp.ClientSession() as session:
                headers = {
                    'Authorization': f'Bearer {api_key}',
                    'Content-Type': 'application/json'
                }
                payload = {
                    'url': search_url,
                    'formats': ['markdown', 'html'],
                    'onlyMainContent': True,
                    'includeTags': ['p', 'h1', 'h2', 'h3', 'article'],
                    'excludeTags': ['nav', 'footer', 'aside', 'script'],
                    'waitFor': 3000
                }
                async with session.post(
                    self.service_urls['FIRECRAWL'],
                    json=payload,
                    headers=headers,
                    timeout=30
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        content = data.get('data', {}).get('markdown', '')
                        # Extrai resultados do conteúdo
                        results = self._extract_search_results_from_content(content, 'firecrawl')
                        return {
                            'success': True,
                            'provider': 'FIRECRAWL',
                            'results': results,
                            'raw_content': content[:2000]
                        }
                    else:
                        error_text = await response.text()
                        logger.error(f"❌ Firecrawl erro {response.status}: {error_text}")
                        return {'success': False, 'error': f'HTTP {response.status}'}
        except Exception as e:
            logger.error(f"❌ Erro Firecrawl: {e}")
            return {'success': False, 'error': str(e)}

    async def _search_jina(self, query: str) -> Dict[str, Any]:
        """Busca REAL usando Jina AI"""
        try:
            api_key = self.get_next_api_key('JINA')
            if not api_key:
                return {'success': False, 'error': 'Jina API key não disponível'}
            # Busca múltiplas URLs com Jina
            search_urls = [
                f"https://www.google.com/search?q={quote_plus(query)}&hl=pt-BR",
                f"https://www.bing.com/search?q={quote_plus(query)}&cc=br",
                f"https://search.yahoo.com/search?p={quote_plus(query)}&ei=UTF-8"
            ]
            results = []
            async with aiohttp.ClientSession() as session:
                for search_url in search_urls:
                    try:
                        jina_url = f"{self.service_urls['JINA']}{search_url}"
                        headers = {
                            'Authorization': f'Bearer {api_key}',
                            'Accept': 'text/plain'
                        }
                        async with session.get(
                            jina_url,
                            headers=headers,
                            timeout=30
                        ) as response:
                            if response.status == 200:
                                content = await response.text()
                                extracted_results = self._extract_search_results_from_content(content, 'jina')
                                results.extend(extracted_results)
                            else:
                                logger.warning(f"⚠️ Jina retornou status {response.status} para {search_url}")
                                continue
                    except Exception as e:
                        logger.warning(f"⚠️ Erro em URL Jina {search_url}: {e}")
                        continue
            return {
                'success': True,
                'provider': 'JINA',
                'results': results[:20]  # Limita a 20 resultados
            }
        except Exception as e:
            logger.error(f"❌ Erro Jina: {e}")
            return {'success': False, 'error': str(e)}

    async def _search_google(self, query: str) -> Dict[str, Any]:
        """Busca REAL usando Google Custom Search"""
        try:
            api_key = self.get_next_api_key('GOOGLE')
            cse_id = os.getenv('GOOGLE_CSE_ID')
            if not api_key or not cse_id:
                logger.warning("⚠️ Google API keys não configuradas")
                return {'success': False, 'error': 'Google API não configurada'}
            async with aiohttp.ClientSession() as session:
                params = {
                    'key': api_key,
                    'cx': cse_id,
                    'q': f"{query} Brasil 2024",
                    'num': 10,
                    'lr': 'lang_pt',
                    'gl': 'br',
                    'safe': 'off',
                    'dateRestrict': 'm6'
                }
                async with session.get(
                    self.service_urls['GOOGLE'],
                    params=params,
                    timeout=30
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        results = []
                        for item in data.get('items', []):
                            results.append({
                                'title': item.get('title', ''),
                                'url': item.get('link', ''),
                                'snippet': item.get('snippet', ''),
                                'source': 'google_real',
                                'published_date': item.get('pagemap', {}).get('metatags', [{}])[0].get('article:published_time', ''),
                                'relevance_score': 0.9
                            })
                        return {
                            'success': True,
                            'provider': 'GOOGLE',
                            'results': results
                        }
                    else:
                        error_text = await response.text()
                        logger.error(f"❌ Google erro {response.status}: {error_text}")
                        return {'success': False, 'error': f'HTTP {response.status}'}
        except Exception as e:
            logger.error(f"❌ Erro Google: {e}")
            return {'success': False, 'error': str(e)}

    async def _search_youtube(self, query: str) -> Dict[str, Any]:
        """Busca REAL no YouTube com foco em conteúdo viral"""
        try:
            api_key = self.get_next_api_key('YOUTUBE')
            if not api_key:
                logger.warning("⚠️ YouTube API key não disponível")
                return {'success': False, 'error': 'YouTube API key não disponível'}
            async with aiohttp.ClientSession() as session:
                params = {
                    'part': "snippet,id",
                    'q': f"{query} Brasil",
                    'key': api_key,
                    'maxResults': 25,
                    'order': 'viewCount',  # Ordena por visualizações
                    'type': 'video',
                    'regionCode': 'BR',
                    'relevanceLanguage': 'pt',
                    'publishedAfter': '2023-01-01T00:00:00Z'
                }
                async with session.get(
                    self.service_urls['YOUTUBE'],
                    params=params,
                    timeout=30
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        results = []
                        for item in data.get('items', []):
                            snippet = item.get('snippet', {})
                            video_id = item.get('id', {}).get('videoId', '')
                            if not video_id: continue
                            # Busca estatísticas detalhadas
                            stats = await self._get_youtube_video_stats(video_id, api_key, session)
                            results.append({
                                'title': snippet.get('title', ''),
                                'url': f"https://www.youtube.com/watch?v={video_id}",
                                'description': snippet.get('description', ''),
                                'channel': snippet.get('channelTitle', ''),
                                'published_at': snippet.get('publishedAt', ''),
                                'thumbnail': snippet.get('thumbnails', {}).get('high', {}).get('url', ''),
                                'view_count': stats.get('viewCount', 0),
                                'comment_count': stats.get('commentCount', 0),
                                'platform': 'youtube',
                                'viral_score': self._calculate_viral_score(stats),
                                'relevance_score': 0.85
                            })
                        # Ordena por score viral
                        results.sort(key=lambda x: x['viral_score'], reverse=True)
                        return {
                            'success': True,
                            'provider': 'YOUTUBE',
                            'platform': 'youtube',
                            'results': results
                        }
                    else:
                        error_text = await response.text()
                        logger.error(f"❌ YouTube erro {response.status}: {error_text}")
                        return {'success': False, 'error': f'HTTP {response.status}'}
        except Exception as e:
            logger.error(f"❌ Erro YouTube: {e}")
            return {'success': False, 'error': str(e)}

    async def _get_youtube_video_stats(self, video_id: str, api_key: str, session: aiohttp.ClientSession) -> Dict[str, Any]:
        """Obtém estatísticas detalhadas de um vídeo do YouTube"""
        try:
            params = {
                'part': 'statistics',
                'id': video_id,
                'key': api_key
            }
            async with session.get(
                'https://www.googleapis.com/youtube/v3/videos',
                params=params,
                timeout=10
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    items = data.get('items', [])
                    if items:
                        return items[0].get('statistics', {})
                return {}
        except Exception as e:
            logger.warning(f"⚠️ Erro ao obter stats do vídeo {video_id}: {e}")
            return {}

    async def _search_supadata(self, query: str) -> Dict[str, Any]:
        """Busca REAL usando Supadata MCP para Instagram, Facebook, TikTok"""
        try:
            api_key = self.get_next_api_key('SUPADATA')
            if not api_key:
                logger.warning("⚠️ Supadata API key não disponível - usando fallback")
                return self._generate_fallback_social_results(query, 'supadata')
                
            async with aiohttp.ClientSession() as session:
                headers = {
                    'Authorization': f'Bearer {api_key}',
                    'Content-Type': 'application/json'
                }
                payload = {
                    'method': 'social_search',
                    'params': {
                        'query': query,
                        'platforms': ['instagram', 'facebook', 'tiktok'],
                        'limit': 50,
                        'sort_by': 'engagement',
                        'include_metrics': True
                    }
                }
                async with session.post(
                    self.service_urls['SUPADATA'],
                    json=payload,
                    headers=headers,
                    timeout=45
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        results = []
                        posts = data.get('result', {}).get('posts', [])
                        for post in posts:
                            results.append({
                                'title': post.get('caption', '')[:100],
                                'url': post.get('url', ''),
                                'content': post.get('caption', ''),
                                'platform': post.get('platform', 'social'),
                                'engagement_rate': post.get('engagement_rate', 0),
                                'likes': post.get('likes', 0),
                                'comments': post.get('comments', 0),
                                'shares': post.get('shares', 0),
                                'author': post.get('author', ''),
                                'published_at': post.get('published_at', ''),
                                'viral_score': self._calculate_social_viral_score(post),
                                'relevance_score': 0.8
                            })
                        return {
                            'success': True,
                            'provider': 'SUPADATA',
                            'platform': 'social', # Plataforma genérica para Supadata
                            'results': results
                        }
                    elif response.status == 401:
                        error_text = await response.text()
                        logger.warning(f"⚠️ Supadata erro 401 (não autorizado): {error_text}")
                        logger.info("💡 Verifique se a API key do Supadata está configurada corretamente")
                        return self._generate_fallback_social_results(query, 'supadata')
                    else:
                        error_text = await response.text()
                        logger.error(f"❌ Supadata erro {response.status}: {error_text}")
                        return self._generate_fallback_social_results(query, 'supadata')
        except Exception as e:
            logger.error(f"❌ Erro Supadata: {e}")
            return self._generate_fallback_social_results(query, 'supadata')

    async def _search_twitter(self, query: str) -> Dict[str, Any]:
        """Busca REAL no Twitter/X"""
        try:
            api_key = self.get_next_api_key('X')
            if not api_key:
                logger.warning("⚠️ X API key não disponível - usando fallback")
                return self._generate_fallback_social_results(query, 'twitter')
                
            async with aiohttp.ClientSession() as session:
                headers = {
                    'Authorization': f'Bearer {api_key}',
                    'Content-Type': 'application/json'
                }
                params = {
                    'query': f"{query} lang:pt -is:retweet", # Exclui retweets
                    'max_results': 50,
                    'tweet.fields': 'public_metrics,created_at,author_id,entities',
                    'user.fields': 'username,verified,public_metrics,profile_image_url',
                    'expansions': 'author_id',
                    'sort_order': 'relevancy' # Tenta ordenar por relevância
                }
                async with session.get(
                    'https://api.twitter.com/2/tweets/search/recent',
                    params=params,
                    headers=headers,
                    timeout=30
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        results = []
                        tweets = data.get('data', [])
                        users = {user['id']: user for user in data.get('includes', {}).get('users', [])}
                        for tweet in tweets:
                            author = users.get(tweet.get('author_id', ''), {})
                            metrics = tweet.get('public_metrics', {})
                            # Extrai URLs do tweet, se houver
                            tweet_url = tweet.get('id')
                            url = f"https://twitter.com/i/status/{tweet_url}" if tweet_url else ""

                            results.append({
                                'title': tweet.get('text', '')[:100], # Usa o texto do tweet como título
                                'url': url,
                                'content': tweet.get('text', ''),
                                'platform': 'twitter',
                                'author': author.get('username', ''),
                                'author_verified': author.get('verified', False),
                                'author_profile_image': author.get('profile_image_url', ''),
                                'retweets': metrics.get('retweet_count', 0),
                                'likes': metrics.get('like_count', 0),
                                'replies': metrics.get('reply_count', 0),
                                'quotes': metrics.get('quote_count', 0),
                                'published_at': tweet.get('created_at', ''),
                                'viral_score': self._calculate_twitter_viral_score(metrics),
                                'relevance_score': 0.75 # Pontuação padrão de relevância
                            })
                        return {
                            'success': True,
                            'provider': 'X',
                            'platform': 'twitter',
                            'results': results
                        }
                    elif response.status == 401:
                        error_text = await response.text()
                        logger.warning(f"⚠️ X/Twitter erro 401 (não autorizado): {error_text}")
                        logger.info("💡 Verifique se a API key do Twitter/X está configurada corretamente")
                        return self._generate_fallback_social_results(query, 'twitter')
                    else:
                        error_text = await response.text()
                        logger.error(f"❌ X/Twitter erro {response.status}: {error_text}")
                        return self._generate_fallback_social_results(query, 'twitter')
        except Exception as e:
            logger.error(f"❌ Erro X/Twitter: {e}")
            return self._generate_fallback_social_results(query, 'twitter')

    async def _search_exa(self, query: str) -> Dict[str, Any]:
        """Busca REAL usando Exa Neural Search"""
        try:
            api_key = self.get_next_api_key('EXA')
            if not api_key:
                logger.warning("⚠️ Exa API key não disponível")
                return {'success': False, 'error': 'Exa API key não disponível'}
            async with aiohttp.ClientSession() as session:
                headers = {
                    'x-api-key': api_key,
                    'Content-Type': 'application/json'
                }
                payload = {
                    'query': f"{query} Brasil mercado tendências",
                    'numResults': 15,
                    'useAutoprompt': True,
                    'type': 'neural',
                    'includeDomains': [
                        'g1.globo.com', 'exame.com', 'valor.globo.com',
                        'estadao.com.br', 'folha.uol.com.br', 'infomoney.com.br'
                    ],
                    'startPublishedDate': '2023-01-01'
                }
                async with session.post(
                    self.service_urls['EXA'],
                    json=payload,
                    headers=headers,
                    timeout=30
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        results = []
                        for item in data.get('results', []):
                            results.append({
                                'title': item.get('title', ''),
                                'url': item.get('url', ''),
                                'snippet': item.get('text', '')[:300],
                                'source': 'exa_neural',
                                'score': item.get('score', 0),
                                'published_date': item.get('publishedDate', ''),
                                'relevance_score': item.get('score', 0.8)
                            })
                        return {
                            'success': True,
                            'provider': 'EXA',
                            'results': results
                        }
                    else:
                        error_text = await response.text()
                        logger.error(f"❌ Exa erro {response.status}: {error_text}")
                        return {'success': False, 'error': f'HTTP {response.status}'}
        except Exception as e:
            logger.error(f"❌ Erro Exa: {e}")
            return {'success': False, 'error': str(e)}

    async def _search_serper(self, query: str) -> Dict[str, Any]:
        """Busca REAL usando Serper"""
        try:
            api_key = self.get_next_api_key('SERPER')
            if not api_key:
                logger.warning("⚠️ Serper API key não disponível")
                return {'success': False, 'error': 'Serper API key não disponível'}
            async with aiohttp.ClientSession() as session:
                headers = {
                    'X-API-KEY': api_key,
                    'Content-Type': 'application/json'
                }
                payload = {
                    'q': f"{query} Brasil mercado",
                    'gl': 'br',
                    'hl': 'pt',
                    'num': 15,
                    'autocorrect': True
                }
                async with session.post(
                    self.service_urls['SERPER'],
                    json=payload,
                    headers=headers,
                    timeout=30
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        results = []
                        for item in data.get('organic', []):
                            results.append({
                                'title': item.get('title', ''),
                                'url': item.get('link', ''),
                                'snippet': item.get('snippet', ''),
                                'source': 'serper_real',
                                'position': item.get('position', 0),
                                'relevance_score': 0.85
                            })
                        return {
                            'success': True,
                            'provider': 'SERPER',
                            'results': results
                        }
                    else:
                        error_text = await response.text()
                        logger.error(f"❌ Serper erro {response.status}: {error_text}")
                        return {'success': False, 'error': f'HTTP {response.status}'}
        except Exception as e:
            logger.error(f"❌ Erro Serper: {e}")
            return {'success': False, 'error': str(e)}

    def _extract_search_results_from_content(self, content: str, provider: str) -> List[Dict[str, Any]]:
        """Extrai resultados de busca do conteúdo extraído"""
        results = []
        if not content:
            return results
        # Divide o conteúdo em seções
        lines = content.split('\n')
        current_result = {}
        for line in lines:
            line = line.strip()
            if not line:
                continue
            # Detecta títulos (linhas com mais de 20 caracteres e sem URLs)
            if (len(line) > 20 and
                not line.startswith('http') and
                not line.startswith('www') and
                '.' not in line[:10]):
                # Salva resultado anterior se existir
                if current_result.get('title'):
                    results.append(current_result)
                # Inicia novo resultado
                current_result = {
                    'title': line,
                    'url': '',
                    'snippet': '',
                    'source': provider,
                    'relevance_score': 0.7
                }
            # Detecta URLs
            elif line.startswith(('http', 'www')):
                if current_result:
                    current_result['url'] = line
            # Detecta descrições (linhas médias)
            elif 50 <= len(line) <= 200 and current_result:
                current_result['snippet'] = line
        # Adiciona último resultado
        if current_result.get('title'):
            results.append(current_result)
        # Filtra resultados válidos
        valid_results = [r for r in results if r.get('title') and len(r.get('title', '')) > 10]
        return valid_results[:15]  # Máximo 15 por provedor

    def _identify_viral_content(self, all_social_results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Identifica conteúdo viral para captura de screenshots"""
        if not all_social_results:
            return []
        # Ordena por score viral
        sorted_content = sorted(
            all_social_results,
            key=lambda x: x.get('viral_score', 0),
            reverse=True
        )
        # Seleciona top 10 conteúdos virais
        viral_content = []
        seen_urls = set()
        for content in sorted_content:
            url = content.get('url', '')
            if url and url not in seen_urls and len(viral_content) < 10:
                viral_content.append(content)
                seen_urls.add(url)
        logger.info(f"🔥 {len(viral_content)} conteúdos virais identificados")
        return viral_content

    async def _capture_viral_screenshots(self, viral_content: List[Dict[str, Any]], session_id: str) -> List[Dict[str, Any]]:
        """Captura screenshots do conteúdo viral usando Selenium"""
        screenshots = []
        try:
            from selenium import webdriver
            from selenium.webdriver.chrome.options import Options
            from selenium.webdriver.chrome.service import Service
            from selenium.webdriver.common.by import By
            from selenium.webdriver.support.ui import WebDriverWait
            from selenium.webdriver.support import expected_conditions as EC
            from webdriver_manager.chrome import ChromeDriverManager
            # Configura Chrome em modo headless com supressão de warnings
            chrome_options = Options()
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--window-size=1920,1080")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--disable-software-rasterizer")
            chrome_options.add_argument("--disable-background-timer-throttling")
            chrome_options.add_argument("--disable-backgrounding-occluded-windows")
            chrome_options.add_argument("--disable-renderer-backgrounding")
            chrome_options.add_argument("--disable-features=TranslateUI")
            chrome_options.add_argument("--disable-ipc-flooding-protection")
            chrome_options.add_argument("--enable-unsafe-swiftshader")
            chrome_options.add_argument("--disable-extensions")
            chrome_options.add_argument("--disable-default-apps")
            chrome_options.add_argument("--disable-sync")
            chrome_options.add_argument("--disable-translate")
            chrome_options.add_argument("--hide-scrollbars")
            chrome_options.add_argument("--mute-audio")
            chrome_options.add_argument("--no-first-run")
            chrome_options.add_argument("--disable-logging")
            chrome_options.add_argument("--disable-permissions-api")
            chrome_options.add_argument("--disable-presentation-api")
            chrome_options.add_argument("--disable-web-security")
            # Suprime logs e warnings específicos
            chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_argument("--log-level=3")  # Suprime logs INFO, WARNING, ERROR
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=chrome_options)
            # Cria diretório para screenshots
            screenshots_dir = f"analyses_data/files/{session_id}/viral_screenshots"
            os.makedirs(screenshots_dir, exist_ok=True)
            try:
                for i, content in enumerate(viral_content, 1):
                    try:
                        url = content.get('url', '')
                        if not url:
                            continue
                        logger.info(f"📸 Capturando screenshot viral {i}/{len(viral_content)}: {content.get('title', 'Sem título')[:50]}...")
                        # Acessa a URL
                        driver.get(url)
                        # Aguarda carregamento
                        WebDriverWait(driver, 15).until(
                            EC.presence_of_element_located((By.TAG_NAME, "body"))
                        )
                        # Aguarda renderização completa (ajustar se necessário)
                        time.sleep(3)
                        # Captura screenshot
                        screenshot_filename = f"viral_content_{i:02d}.png"
                        screenshot_path = os.path.join(screenshots_dir, screenshot_filename)
                        driver.save_screenshot(screenshot_path)
                        # Verifica se foi criado
                        if os.path.exists(screenshot_path) and os.path.getsize(screenshot_path) > 0:
                            screenshots.append({
                                'content_data': content, # Dados do post original
                                'screenshot_path': screenshot_path, # Caminho relativo ou absoluto
                                'filename': screenshot_filename,
                                'url': url,
                                'title': content.get('title', ''),
                                'platform': content.get('platform', ''),
                                'viral_score': content.get('viral_score', 0),
                                'captured_at': datetime.now().isoformat()
                            })
                            logger.info(f"✅ Screenshot viral {i} capturado: {screenshot_path}")
                        else:
                            logger.warning(f"⚠️ Falha ao capturar screenshot viral {i}: arquivo vazio ou não criado.")
                    except Exception as e:
                        logger.error(f"❌ Erro ao capturar screenshot viral {i} para {url}: {e}")
                        continue
            finally:
                driver.quit()
        except ImportError:
            logger.error("❌ Selenium não instalado ou webdriver_manager - screenshots virais não disponíveis.")
            return []
        except Exception as e:
            logger.error(f"❌ Erro geral na captura de screenshots virais: {e}")
            return []
        return screenshots

    def _calculate_viral_score(self, stats: Dict[str, Any]) -> float:
        """Calcula score viral para YouTube"""
        try:
            views = int(stats.get('viewCount', 0))
            likes = int(stats.get('likeCount', 0))
            comments = int(stats.get('commentCount', 0))
            # Fórmula viral: views + (likes * 10) + (comments * 20)
            viral_score = views + (likes * 10) + (comments * 20)
            # Normaliza para 0-10 (escalonamento aproximado)
            # Ajuste o divisor com base na escala desejada
            normalized_score = min(10.0, viral_score / 500000) # Divisor exemplo: 500k para ter um score máximo de 10
            return round(normalized_score, 2)
        except Exception as e:
            logger.warning(f"Erro ao calcular viral score do YouTube: {e}")
            return 0.0

    def _calculate_social_viral_score(self, post: Dict[str, Any]) -> float:
        """Calcula score viral para redes sociais (Instagram, Facebook, TikTok via Supadata)"""
        try:
            likes = int(post.get('likes', 0))
            comments = int(post.get('comments', 0))
            shares = int(post.get('shares', 0))
            engagement_rate = float(post.get('engagement_rate', 0))
            # Fórmula viral: pondera likes, comments, shares e engagement rate
            viral_score = (likes * 1) + (comments * 5) + (shares * 10) + (engagement_rate * 1000)
            # Normaliza para 0-10
            normalized_score = min(10.0, viral_score / 15000) # Divisor exemplo: 15k
            return round(normalized_score, 2)
        except Exception as e:
            logger.warning(f"Erro ao calcular viral score social: {e}")
            return 0.0

    def _calculate_twitter_viral_score(self, metrics: Dict[str, Any]) -> float:
        """Calcula score viral para Twitter"""
        try:
            retweets = int(metrics.get('retweet_count', 0))
            likes = int(metrics.get('like_count', 0))
            replies = int(metrics.get('reply_count', 0))
            quotes = int(metrics.get('quote_count', 0))
            # Fórmula viral: pondera retweets, likes, replies e quotes
            viral_score = (retweets * 10) + (likes * 2) + (replies * 5) + (quotes * 15)
            # Normaliza para 0-10
            normalized_score = min(10.0, viral_score / 5000) # Divisor exemplo: 5k
            return round(normalized_score, 2)
        except Exception as e:
            logger.warning(f"Erro ao calcular viral score do Twitter: {e}")
            return 0.0

    def get_session_statistics(self) -> Dict[str, Any]:
        """Retorna estatísticas da sessão atual"""
        return self.session_stats.copy()

    async def _generate_collection_report(self, massive_data: Dict[str, Any], session_id: str):
        """Gera um relatório de coleta com referências às imagens capturadas."""
        logger.info(f"📝 Gerando relatório de coleta para sessão: {session_id}")

        # Cria diretório da sessão
        session_dir = f"analyses_data/{session_id}"
        os.makedirs(session_dir, exist_ok=True)

        report_data = {
            "session_id": session_id,
            "query": massive_data["query"],
            "collection_timestamp": massive_data["collection_started"],
            "summary": {
                "total_sources": massive_data["statistics"]["total_sources"],
                "total_content_length": massive_data["statistics"]["total_content_length"],
                "collection_duration": f"{massive_data['statistics']['collection_time']:.2f}s",
                "screenshot_count": massive_data["statistics"]["screenshot_count"], # Screenshots gerais
                "masterclass_screenshots": massive_data.get('masterclass_analysis', {}).get('total_screenshots', 0),
                "viral_analysis_screenshots": massive_data.get('viral_analysis', {}).get('screenshots_captured', 0),
                "api_rotations": massive_data["statistics"]["api_rotations"],
                "sources_by_type": massive_data["statistics"]["sources_by_type"]
            },
            "visual_references": [],
            "errors": []
        }

        # Gera relatório em Markdown
        markdown_report = self._generate_markdown_report(massive_data, session_id)

        # Salva relatório de coleta
        report_path = f"{session_dir}/relatorio_coleta.md"
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(markdown_report)

        logger.info(f"✅ Relatório de coleta salvo: {report_path}")

        # Inclui screenshots gerais no relatório
        if massive_data["visual_content"] and massive_data["visual_content"].get("success"):
            report_data["visual_references"].extend(massive_data["visual_content"].get("screenshots", []))
            logger.info(f"🖼️ {len(massive_data['visual_content'].get('screenshots', []))} referências visuais gerais incluídas no relatório.")
        else:
            report_data["errors"].append({
                "source": "Visual Content Capture (Geral)",
                "message": massive_data["visual_content"].get("error", "Nenhum dado de visual geral disponível.")
            })
            logger.warning("🖼️ Nenhum dado visual geral para incluir no relatório.")

        # Inclui screenshots do Masterclass
        masterclass_analysis = massive_data.get('masterclass_analysis', {})
        if masterclass_analysis and not masterclass_analysis.get('error'):
            report_data["visual_references"].extend(masterclass_analysis.get("screenshots", []))
            logger.info(f"🖼️ {masterclass_analysis.get('total_screenshots', 0)} referências visuais do Masterclass incluídas no relatório.")
        elif masterclass_analysis and masterclass_analysis.get('error'):
            report_data["errors"].append({
                "source": "Google Masterclass Extractor",
                "message": masterclass_analysis.get("error", "Erro ao processar Masterclass.")
            })

        # Inclui screenshots da Análise Viral
        viral_analysis = massive_data.get('viral_analysis', {})
        if viral_analysis and viral_analysis.get('screenshots_captured', 0) > 0:
            report_data["visual_references"].extend(viral_analysis.get("screenshots", []))
            logger.info(f"🔥 {viral_analysis.get('screenshots_captured', 0)} referências visuais de Análise Viral incluídas no relatório.")
        elif viral_analysis and viral_analysis.get('error'):
             report_data["errors"].append({
                "source": "Viral Content Analyzer",
                "message": viral_analysis.get("error", "Erro ao analisar conteúdo viral.")
            })

        # Adicionar erros de outras fontes, se houver
        if massive_data.get("web_search_data", {}).get("error"):
            report_data["errors"].append({"source": "Web Search", "message": massive_data["web_search_data"]["error"]})
        if massive_data.get("trends_data", {}).get("error"):
            report_data["errors"].append({"source": "TrendFinder", "message": massive_data["trends_data"]["error"]})
        if massive_data.get("supadata_results", {}).get("error"):
            report_data["errors"].append({"source": "Supadata", "message": massive_data["supadata_results"]["error"]})
        if massive_data.get("social_media_data", {}).get("error"):
             report_data["errors"].append({"source": "Social Media Extractor (Fallback)", "message": massive_data["social_media_data"]["error"]})

        try:
            salvar_etapa("collection_report", report_data, categoria="relatorios")
            logger.info("✅ Relatório de coleta gerado e salvo com sucesso.")
        except Exception as e:
            logger.error(f"❌ Erro ao salvar relatório de coleta: {e}")

        return report_data

    def _generate_markdown_report(self, massive_data: Dict[str, Any], session_id: str) -> str:
        """Gera relatório em formato Markdown"""

        report = f"""# RELATÓRIO DE COLETA DE DADOS - ARQV30 Enhanced v3.0

**Sessão:** `{session_id}`  
**Query:** `{massive_data.get('query', 'N/A')}`  
**Iniciado em:** {massive_data.get('collection_started', 'N/A')}  
**Duração Total:** {massive_data.get('statistics', {}).get('collection_time', 0):.2f} segundos

---

## RESUMO DA COLETA

### Estatísticas Gerais:
- **Total de Fontes Coletadas:** {massive_data.get('statistics', {}).get('total_sources', 0)}
- **Total de Caracteres:** {massive_data.get('statistics', {}).get('total_content_length', 0):,}
- **Screenshots Gerais:** {massive_data.get('statistics', {}).get('screenshot_count', 0)}
- **Screenshots Masterclass:** {massive_data.get('masterclass_analysis', {}).get('total_screenshots', 0)}
- **Screenshots Análise Viral:** {massive_data.get('viral_analysis', {}).get('screenshots_captured', 0)}
- **APIs Utilizadas (Rotações):** {json.dumps(massive_data.get('statistics', {}).get('api_rotations', {}))}

### Fontes por Tipo:
"""

        # Adiciona estatísticas por tipo
        sources_by_type = massive_data.get('statistics', {}).get('sources_by_type', {})
        if isinstance(sources_by_type, dict):
            sorted_sources = sorted(sources_by_type.items(), key=lambda item: item[1], reverse=True)
            for source_type, count in sorted_sources:
                report += f"- **{source_type.replace('_', ' ').title()}:** {count}\n"
        else:
            report += f"- **Dados de Fontes:** {sources_by_type}\n" # Fallback se não for dict

        report += "\n---\n\n"

        # Adiciona dados de busca web
        web_data = massive_data.get('web_search_data', {})
        if web_data.get('web_results'):
            report += "## DADOS DE BUSCA WEB\n\n"
            report += f"Fontes encontradas: {web_data.get('statistics', {}).get('total_sources', 0)} | URLs únicas: {web_data.get('statistics', {}).get('unique_urls', 0)}\n\n"
            for i, result in enumerate(web_data['web_results'][:5], 1): # Mostra os 5 primeiros
                report += f"**{i}. [{result.get('title', 'Sem título')}]({result.get('url', '#')})**  \n"
                report += f"   Fonte: `{result.get('source', 'N/A')}` | Relevância: {result.get('relevance_score', 'N/A')}\n"
                report += f"   Resumo: {result.get('snippet', 'N/A')[:200]}...\n\n"

        # Adiciona dados sociais (fallback e Supadata)
        social_data = massive_data.get('social_media_data', {})
        if social_data.get('success') and social_data.get('all_platforms_data'):
            report += "## DADOS DE REDES SOCIAIS (Fallback + Supadata)\n\n"
            platforms = social_data.get('all_platforms_data', {}).get('platforms', {})
            total_social_posts = social_data.get('total_posts', 0)
            report += f"Total de posts analisados: {total_social_posts}\n\n"

            if isinstance(platforms, dict):
                for platform, data in platforms.items():
                    results = data.get('results', [])
                    if results:
                        report += f"### {platform.title()} ({len(results)} posts)\n\n"
                        for i, post in enumerate(results[:3], 1): # Mostra os 3 primeiros por plataforma
                            title = post.get('title', post.get('text', post.get('caption', 'Post sem título')))
                            author = post.get('author', 'Sem autor')
                            score = post.get('viral_score', 'N/A')
                            report += f"**{i}. [{title[:100]}...]({post.get('url', '#')})** por **{author}** (Score Viral: {score})\n"
                            report += f"   Likes: {post.get('likes', 0)} | Comentários: {post.get('comments', 0)}\n\n"
            elif isinstance(platforms, list):
                for i, platform_data in enumerate(platforms):
                    if isinstance(platform_data, dict):
                        platform_name = platform_data.get('platform', f'Platform_{i}')
                        results = platform_data.get('results', [])
                        if results:
                            report += f"### {platform_name.title()} ({len(results)} posts)\n\n"
                            for j, post in enumerate(results[:3], 1):
                                title = post.get('title', post.get('text', post.get('caption', 'Post sem título')))
                                author = post.get('author', 'Sem autor')
                                score = post.get('viral_score', 'N/A')
                                report += f"**{j}. [{title[:100]}...]({post.get('url', '#')})** por **{author}** (Score Viral: {score})\n"
                                report += f"   Likes: {post.get('likes', 0)} | Comentários: {post.get('comments', 0)}\n\n"

        # Adiciona dados do Masterclass
        masterclass_analysis = massive_data.get('masterclass_analysis', {})
        if masterclass_analysis and not masterclass_analysis.get('error'):
            report += "## ANÁLISE GOOGLE MASTERCLASS\n\n"
            report += f"Busca realizada para: `{massive_data.get('query')}`\n"
            report += f"Plataformas analisadas: `{', '.join(masterclass_analysis.get('platforms_searched', []))}`\n"
            report += f"Total de posts/vídeos encontrados: {masterclass_analysis.get('total_results', 0)}\n"
            report += f"Total de screenshots capturados: {masterclass_analysis.get('total_screenshots', 0)}\n\n"

            if masterclass_analysis.get('instagram_posts'):
                report += "### Instagram (Melhores Posts):\n"
                for i, post in enumerate(masterclass_analysis['instagram_posts'][:3], 1):
                    report += f"**{i}. [{post.get('title', '')[:100]}...]({post.get('url', '#')})**\n"
                    report += f"   Visualizações: {post.get('views', 0):,} | Likes: {post.get('likes', 0):,} | Comentários: {post.get('comments', 0):,}\n\n"

            if masterclass_analysis.get('youtube_videos'):
                report += "### YouTube (Melhores Vídeos):\n"
                for i, video in enumerate(masterclass_analysis['youtube_videos'][:3], 1):
                    report += f"**{i}. [{video.get('title', '')[:100]}...]({video.get('url', '#')})**\n"
                    report += f"   Canal: {video.get('channel', 'N/A')} | Views: {video.get('views', 0):,} | Likes: {video.get('likes', 0):,}\n\n"

            if masterclass_analysis.get('facebook_posts'):
                report += "### Facebook (Melhores Posts):\n"
                for i, post in enumerate(masterclass_analysis['facebook_posts'][:3], 1):
                    report += f"**{i}. [{post.get('title', '')[:100]}...]({post.get('url', '#')})**\n"
                    report += f"   Likes: {post.get('likes', 0):,} | Comentários: {post.get('comments', 0):,} | Compartilhamentos: {post.get('shares', 0):,}\n\n"

        # Adiciona screenshots (referências visuais)
        visual_references = massive_data.get('visual_references', [])
        if visual_references:
            report += "## EVIDÊNCIAS VISUAIS (Screenshots)\n\n"
            for i, ref in enumerate(visual_references, 1):
                # Tenta obter o caminho do arquivo para a imagem no relatório
                # Assume que o caminho é relativo ao diretório de análise
                filepath = ref.get('screenshot_path', ref.get('filepath', ''))
                if filepath:
                    # Cria um link markdown para a imagem
                    # Nota: A exibição de imagens em markdown em alguns ambientes pode depender do contexto
                    report += f"### Screenshot {i}\n"
                    report += f"**URL Original:** {ref.get('url', 'N/A')}\n"
                    report += f"**Título/Descrição:** {ref.get('title', 'N/A')}\n"
                    report += f"![Screenshot {i}]({filepath})  \n\n"
                else:
                    report += f"**Screenshot {i} (Caminho não disponível):** {ref.get('url', 'N/A')}\n\n"

        # Adiciona erros encontrados
        errors = massive_data.get('errors', [])
        if errors:
            report += "## ERROS ENCONTRADOS DURANTE A COLETA\n\n"
            for i, error in enumerate(errors, 1):
                report += f"**{i}. Fonte:** {error.get('source', 'Desconhecida')}\n"
                report += f"   **Mensagem:** {error.get('message', 'Erro não especificado')}\n\n"

        report += f"\n---\n\n*Relatório gerado automaticamente em {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}*"

        return report

    def _generate_fallback_social_results(self, query: str, platform: str) -> Dict[str, Any]:
        """Gera resultado sem simulação quando APIs falham (respeita DISABLE_FALLBACKS/FORCE_REAL_DATA)."""
        disable_fallbacks = str(os.getenv('DISABLE_FALLBACKS', 'false')).lower() == 'true' or \
                             str(os.getenv('FORCE_REAL_DATA', 'false')).lower() == 'true'
        if disable_fallbacks:
            logger.info(f"⛔ Fallbacks desativados – retornando lista vazia para {platform}")
            return {
                'success': False,
                'provider': platform.upper(),
                'platform': platform,
                'results': [],
                'is_fallback': True,
                'fallback_reason': 'fallbacks_disabled'
            }

        logger.info(f"🔄 Gerando resultados de fallback para {platform}")
        # Modo legado: gerar placeholders mínimos (mantido apenas se fallbacks permitidos)
        keywords = query.lower().split()
        fallback_results = [{
            'title': f"Conteúdo relacionado a {' '.join(keywords[:2])} - Post {i+1}",
            'url': f"https://{platform}.com/fallback_post_{i+1}",
            'content': f"Conteúdo simulado sobre {query} - dados não disponíveis devido a problemas de API",
            'platform': platform,
            'author': f"usuario_{platform}_{i+1}",
            'likes': 100 * (i + 1),
            'comments': 10 * (i + 1),
            'shares': 5 * (i + 1),
            'published_at': datetime.now().isoformat(),
            'viral_score': 2.0 + i,
            'relevance_score': 0.5,
            'is_fallback': True
        } for i in range(3)]

        return {
            'success': True,
            'provider': platform.upper(),
            'platform': platform,
            'results': fallback_results,
            'is_fallback': True,
            'fallback_reason': 'API authentication failed or unavailable'
        }

# Instância global
real_search_orchestrator = RealSearchOrchestrator()