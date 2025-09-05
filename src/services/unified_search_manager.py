#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ARQV30 Enhanced v2.0 - Unified Search Manager
Gerenciador unificado de busca com Exa, Google, Serper e outros provedores
"""

import os
import logging
import time
import requests
from typing import Dict, List, Optional, Any
from urllib.parse import quote_plus
from bs4 import BeautifulSoup
import json
import random
from datetime import datetime
from services.exa_client import exa_client
from services.auto_save_manager import salvar_etapa, salvar_erro

logger = logging.getLogger(__name__)

class UnifiedSearchManager:
    """Gerenciador unificado de busca com múltiplos provedores"""

    def __init__(self):
        """Inicializa o gerenciador unificado"""
        self.providers = {
            'exa': {
                'enabled': exa_client.is_available(),
                'priority': 1,  # Prioridade máxima - EXA PRIMEIRO
                'error_count': 0,
                'max_errors': 3,
                'client': exa_client
            },
            'alibaba_websailor': {
                'enabled': True,  # SEGUNDO - Alibaba WebSailor
                'priority': 2,
                'error_count': 0,
                'max_errors': 3,
                'base_url': 'https://api.alibaba-websailor.com'
            },
            'google': {
                'enabled': bool(os.getenv('GOOGLE_SEARCH_KEY') and os.getenv('GOOGLE_CSE_ID')),
                'priority': 3,  # TERCEIRO
                'error_count': 0,
                'max_errors': 3,
                'api_key': os.getenv('GOOGLE_SEARCH_KEY'),
                'cse_id': os.getenv('GOOGLE_CSE_ID'),
                'base_url': 'https://www.googleapis.com/customsearch/v1'
            },
            'serper': {
                'enabled': bool(os.getenv('SERPER_API_KEY')),
                'priority': 4,  # QUARTO
                'error_count': 0,
                'max_errors': 3,
                'api_key': os.getenv('SERPER_API_KEY'),
                'base_url': 'https://google.serper.dev/search'
            }
        }

        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'pt-BR,pt;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive'
        }

        # Domínios brasileiros preferenciais
        self.preferred_domains = [
            "g1.globo.com", "exame.com", "valor.globo.com", "estadao.com.br",
            "folha.uol.com.br", "canaltech.com.br", "tecmundo.com.br",
            "olhardigital.com.br", "infomoney.com.br", "startse.com",
            "revistapegn.globo.com", "epocanegocios.globo.com", "istoedinheiro.com.br"
        ]

        enabled_count = sum(1 for p in self.providers.values() if p['enabled'])
        logger.info(f"🔍 Unified Search Manager inicializado com {enabled_count} provedores")

    def unified_search(
        self, 
        query: str, 
        max_results: int = 25,
        context: Dict[str, Any] = None,
        session_id: str = None,
        include_social: bool = True
    ) -> Dict[str, Any]:
        """Realiza busca unificada com todos os provedores disponíveis"""
        try:
            logger.info(f"🔍 Iniciando busca unificada: {query}")

            all_results = []
            social_results = []
            search_statistics = {
                'providers_used': 0,
                'total_results': 0,
                'search_time': 0,
                'social_platforms': 0
            }

            start_time = time.time()

            # 1. Busca prioritária: Exa > Alibaba WebSailor > Google > Serper
            search_providers = ['exa', 'websailor', 'google', 'serper']

            for provider in search_providers:
                try:
                    if provider == 'exa':
                        results = self._search_with_exa(query, max_results // 4)
                    elif provider == 'websailor':
                        results = self._search_with_websailor(query, max_results // 4)
                    elif provider == 'google':
                        results = self._search_with_google(query, max_results // 4)
                    elif provider == 'serper':
                        results = self._search_with_serper(query, max_results // 4)
                    else:
                        continue

                    if results:
                        all_results.extend(results)
                        search_statistics['providers_used'] += 1
                        logger.info(f"✅ {provider}: {len(results)} resultados")

                except Exception as e:
                    logger.warning(f"⚠️ Erro no provedor {provider}: {e}")
                    continue

            # 2. Busca em redes sociais (se habilitada)
            if include_social:
                social_results = self._search_social_media(query, context)
                search_statistics['social_platforms'] = len(social_results)

            # 3. Combina resultados web e social
            combined_results = all_results + social_results

            # Remove duplicatas e prioriza por qualidade
            unique_results = self._remove_duplicates_and_rank(combined_results)
            final_results = unique_results[:max_results]

            search_statistics['total_results'] = len(final_results)
            search_statistics['search_time'] = time.time() - start_time

            # Salva resultados se session_id fornecido
            if session_id:
                salvar_etapa(
                    "busca_unificada_completa", 
                    {
                        'query': query,
                        'results': final_results,
                        'social_results': social_results,
                        'statistics': search_statistics
                    },
                    categoria="pesquisa_web",
                    session_id=session_id
                )

            logger.info(f"✅ Busca unificada concluída: {len(final_results)} resultados ({search_statistics['social_platforms']} redes sociais)")

            return {
                'success': True,
                'results': final_results,
                'social_results': social_results,
                'statistics': search_statistics,
                'query': query,
                'timestamp': datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"❌ Erro na busca unificada: {e}")
            return {
                'success': False,
                'error': str(e),
                'results': [],
                'statistics': {'providers_used': 0, 'total_results': 0, 'search_time': 0}
            }

    def _search_with_exa(self, query: str, max_results: int) -> List[Dict]:
        """Busca com Exa API (prioridade 1)"""
        try:
            from services.exa_client import exa_client
            return exa_client.search(query, max_results)
        except Exception as e:
            logger.warning(f"Exa não disponível: {e}")
            return []

    def _search_with_websailor(self, query: str, max_results: int) -> List[Dict]:
        """Busca com Alibaba WebSailor (prioridade 2)"""
        try:
            from services.alibaba_websailor import websailor_client
            return websailor_client.search(query, max_results)
        except Exception as e:
            logger.warning(f"WebSailor não disponível: {e}")
            return []

    def _search_with_google(self, query: str, max_results: int) -> List[Dict]:
        """Busca com Google API (prioridade 3)"""
        try:
            return production_search_manager.search_with_google(query, max_results)
        except Exception as e:
            logger.warning(f"Google API não disponível: {e}")
            return []

    def _search_with_serper(self, query: str, max_results: int) -> List[Dict]:
        """Busca com Serper API (prioridade 4)"""
        try:
            return production_search_manager.search_with_serper(query, max_results)
        except Exception as e:
            logger.warning(f"Serper API não disponível: {e}")
            return []

    def _search_social_media(self, query: str, context: Dict = None) -> List[Dict]:
        """Busca em redes sociais usando Supadata"""
        social_results = []

        # URLs de busca para diferentes plataformas
        social_platforms = {
            'youtube': f"https://www.youtube.com/results?search_query={query.replace(' ', '+')}",
            'twitter': f"https://twitter.com/search?q={query.replace(' ', '%20')}",
            'linkedin': f"https://www.linkedin.com/search/results/content/?keywords={query.replace(' ', '%20')}",
            'instagram': f"https://www.instagram.com/explore/tags/{query.replace(' ', '').lower()}/"
        }

        for platform, url in social_platforms.items():
            try:
                # Aqui implementaria a busca real com Supadata
                # Por enquanto, adicionamos URLs simuladas para exemplo
                social_results.append({
                    'title': f'Conteúdo {platform.title()} sobre {query}',
                    'url': url,
                    'source': platform,
                    'type': 'social_media',
                    'description': f'Resultados de {platform} para {query}'
                })
            except Exception as e:
                logger.warning(f"Erro ao buscar no {platform}: {e}")

        return social_results

    def _remove_duplicates_and_rank(self, results: List[Dict]) -> List[Dict]:
        """Remove duplicatas e ranqueia por qualidade"""
        seen_urls = set()
        unique_results = []

        # Prioridade: 1) Exa, 2) WebSailor, 3) Google, 4) Serper, 5) Social
        priority_order = ['exa', 'websailor', 'google', 'serper', 'youtube', 'twitter', 'linkedin', 'instagram']

        # Ordena por prioridade da fonte
        sorted_results = sorted(results, key=lambda x: priority_order.index(x.get('source', 'unknown')) if x.get('source') in priority_order else 999)

        for result in sorted_results:
            url = result.get('url', '')
            if url and url not in seen_urls:
                seen_urls.add(url)
                unique_results.append(result)

        return unique_results

    def _remove_duplicates(self, results: List[Dict]) -> List[Dict]:
        """Remove URLs duplicadas mantendo a primeira ocorrência (método legacy)"""
        return self._remove_duplicates_and_rank(results)

    def _search_with_exa(self, query: str, max_results: int, context: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Busca usando Exa API"""

        try:
            # Melhora query para mercado brasileiro
            enhanced_query = self._enhance_query_for_brazil(query)

            # Configura domínios preferenciais
            include_domains = self.preferred_domains if context else None

            # Busca com Exa
            exa_response = exa_client.search(
                query=enhanced_query,
                num_results=max_results,
                include_domains=include_domains,
                start_published_date="2023-01-01",  # Últimos 2 anos
                use_autoprompt=True,
                type="neural"
            )

            if not exa_response or 'results' not in exa_response:
                return []

            # Converte resultados para formato padrão
            results = []
            for item in exa_response['results']:
                results.append({
                    'title': item.get('title', ''),
                    'url': item.get('url', ''),
                    'snippet': item.get('text', '')[:300],  # Limita snippet
                    'source': 'exa',
                    'score': item.get('score', 0),
                    'published_date': item.get('publishedDate', ''),
                    'author': item.get('author', ''),
                    'exa_id': item.get('id', '')
                })

            return results

        except Exception as e:
            logger.error(f"❌ Erro na busca Exa: {e}")
            return []

    def _search_google(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        """Busca usando Google Custom Search API"""

        provider = self.providers['google']

        try:
            enhanced_query = self._enhance_query_for_brazil(query)

            params = {
                'key': provider['api_key'],
                'cx': provider['cse_id'],
                'q': enhanced_query,
                'num': min(max_results, 10),
                'lr': 'lang_pt',
                'gl': 'br',
                'safe': 'off',
                'dateRestrict': 'm12'  # Últimos 12 meses
            }

            response = requests.get(
                provider['base_url'],
                params=params,
                headers=self.headers,
                timeout=15
            )

            if response.status_code == 200:
                data = response.json()
                results = []

                for item in data.get('items', []):
                    results.append({
                        'title': item.get('title', ''),
                        'url': item.get('link', ''),
                        'snippet': item.get('snippet', ''),
                        'source': 'google'
                    })

                return results
            else:
                raise Exception(f"Google API retornou status {response.status_code}")

        except Exception as e:
            raise e

    def _search_serper(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        """Busca usando Serper API"""

        provider = self.providers['serper']

        try:
            enhanced_query = self._enhance_query_for_brazil(query)

            headers = {
                **self.headers,
                'X-API-KEY': provider['api_key'],
                'Content-Type': 'application/json'
            }

            payload = {
                'q': enhanced_query,
                'gl': 'br',
                'hl': 'pt',
                'num': max_results
            }

            response = requests.post(
                provider['base_url'],
                json=payload,
                headers=headers,
                timeout=15
            )

            if response.status_code == 200:
                data = response.json()
                results = []

                for item in data.get('organic', []):
                    results.append({
                        'title': item.get('title', ''),
                        'url': item.get('link', ''),
                        'snippet': item.get('snippet', ''),
                        'source': 'serper'
                    })

                return results
            else:
                raise Exception(f"Serper API retornou status {response.status_code}")

        except Exception as e:
            raise e

    def _search_bing(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        """Busca usando Bing (scraping)"""

        try:
            enhanced_query = self._enhance_query_for_brazil(query)
            search_url = f"{self.providers['bing']['base_url']}?q={quote_plus(enhanced_query)}&cc=br&setlang=pt-br&count={max_results}"

            response = requests.get(search_url, headers=self.headers, timeout=15)

            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                results = []

                result_items = soup.find_all('li', class_='b_algo')

                for item in result_items[:max_results]:
                    title_elem = item.find('h2')
                    if title_elem:
                        link_elem = title_elem.find('a')
                        if link_elem:
                            title = title_elem.get_text(strip=True)
                            url = link_elem.get('href', '')

                            snippet_elem = item.find('p')
                            snippet = snippet_elem.get_text(strip=True) if snippet_elem else ""

                            if url and title and url.startswith('http'):
                                results.append({
                                    'title': title,
                                    'url': url,
                                    'snippet': snippet,
                                    'source': 'bing'
                                })

                return results
            else:
                raise Exception(f"Bing retornou status {response.status_code}")

        except Exception as e:
            raise e

    def _search_alibaba_websailor(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        """Busca usando Alibaba WebSailor (SEGUNDO na prioridade)"""

        try:
            enhanced_query = self._enhance_query_for_brazil(query)

            # Integração com WebSailor existente
            from services.websailor_integration import websailor_integration

            websailor_results = websailor_integration.search_and_extract(
                query=enhanced_query,
                max_pages=max_results,
                context={"focus": "brazil_market"}
            )

            results = []
            for page in websailor_results.get('page_contents', [])[:max_results]:
                results.append({
                    'title': page.get('title', 'WebSailor Result'),
                    'url': page.get('url', ''),
                    'snippet': page.get('content', '')[:300],
                    'source': 'alibaba_websailor',
                    'relevance_score': page.get('relevance_score', 0)
                })

            return results

        except Exception as e:
            logger.warning(f"WebSailor não disponível: {e}")
            return []

    def _enhance_query_for_brazil(self, query: str) -> str:
        """Melhora query para pesquisa no Brasil"""

        enhanced_query = query
        query_lower = query.lower()

        # Adiciona termos brasileiros se não estiverem presentes
        if not any(term in query_lower for term in ["brasil", "brasileiro", "br"]):
            enhanced_query += " Brasil"

        # Adiciona ano atual se não estiver presente
        if not any(year in query for year in ["2024", "2025"]):
            enhanced_query += " 2024"

        return enhanced_query.strip()

    def _prioritize_brazilian_sources(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Prioriza fontes brasileiras"""

        for result in results:
            url = result.get('url', '')
            domain = url.split('/')[2] if len(url.split('/')) > 2 else ''

            # Marca se é fonte brasileira
            result['is_brazilian'] = (
                domain.endswith('.br') or 
                'brasil' in domain.lower() or
                any(pref in domain for pref in self.preferred_domains)
            )

            # Marca se é fonte preferencial
            result['is_preferred'] = any(pref in domain for pref in self.preferred_domains)

            # Calcula score de prioridade
            priority_score = 1.0

            if result['is_preferred']:
                priority_score += 3.0
            elif result['is_brazilian']:
                priority_score += 2.0

            # Bonus por fonte Exa
            if result.get('source') == 'exa':
                priority_score += 1.5

            result['priority_score'] = priority_score

        # Ordena por prioridade
        results.sort(key=lambda x: x.get('priority_score', 0), reverse=True)

        return results

    def _record_provider_error(self, provider_name: str):
        """Registra erro do provedor"""
        if provider_name in self.providers:
            self.providers[provider_name]['error_count'] += 1

            if self.providers[provider_name]['error_count'] >= self.providers[provider_name]['max_errors']:
                logger.warning(f"⚠️ Provedor {provider_name} desabilitado temporariamente")
                self.providers[provider_name]['enabled'] = False

    def get_provider_status(self) -> Dict[str, Any]:
        """Retorna status de todos os provedores"""
        status = {}

        for name, provider in self.providers.items():
            status[name] = {
                'enabled': provider['enabled'],
                'priority': provider['priority'],
                'error_count': provider['error_count'],
                'max_errors': provider['max_errors'],
                'available': provider['enabled'] and provider['error_count'] < provider['max_errors']
            }

        return status

    def reset_provider_errors(self, provider_name: str = None):
        """Reset contadores de erro dos provedores"""
        if provider_name:
            if provider_name in self.providers:
                self.providers[provider_name]['error_count'] = 0
                self.providers[provider_name]['enabled'] = True
                logger.info(f"🔄 Reset erros do provedor: {provider_name}")
        else:
            for provider in self.providers.values():
                provider['error_count'] = 0
                provider['enabled'] = True
            logger.info("🔄 Reset erros de todos os provedores")

# Instância global
unified_search_manager = UnifiedSearchManager()