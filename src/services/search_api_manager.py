#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ARQV30 Enhanced v3.0 - Search API Manager
Gerenciador de rotação de chaves de API para múltiplos provedores
"""

import os
import logging
from typing import Dict, List, Optional, Any
import asyncio
import aiohttp
from datetime import datetime

logger = logging.getLogger(__name__)

class SearchAPIManager:
    """Gerenciador de rotação de chaves de API para busca intercalada"""

    def __init__(self):
        """Inicializa o gerenciador com rotação de chaves"""
        self.api_keys: Dict[str, List[str]] = {}
        self.key_indices: Dict[str, int] = {}
        self.providers = ['FIRECRAWL', 'JINA', 'GOOGLE', 'EXA']

        self._load_api_keys()
        logger.info(f"🔑 Search API Manager inicializado com {sum(len(keys) for keys in self.api_keys.values())} chaves totais")

    def _load_api_keys(self):
        """Carrega todas as chaves de API do ambiente"""
        for provider in self.providers:
            keys = []

            # Carrega chave principal
            main_key = os.getenv(f"{provider}_API_KEY")
            if main_key:
                keys.append(main_key)

            # Carrega chaves numeradas (1, 2, 3, etc.)
            counter = 1
            while True:
                numbered_key = os.getenv(f"{provider}_API_KEY_{counter}")
                if numbered_key:
                    keys.append(numbered_key)
                    counter += 1
                else:
                    break

            if keys:
                self.api_keys[provider] = keys
                self.key_indices[provider] = 0
                logger.info(f"✅ {provider}: {len(keys)} chaves carregadas")
            else:
                if provider == 'GOOGLE':
                    logger.info(f"ℹ️ {provider}: Chave opcional não configurada")
                else:
                    logger.warning(f"⚠️ {provider}: Nenhuma chave encontrada")

    def get_next_key(self, provider: str) -> Optional[str]:
        """Retorna a próxima chave de API disponível para um provedor"""
        if provider not in self.api_keys or not self.api_keys[provider]:
            logger.error(f"❌ Nenhuma chave disponível para {provider}")
            return None

        keys = self.api_keys[provider]
        current_index = self.key_indices[provider]

        # Obtém a chave atual
        key = keys[current_index]

        # Rotaciona para a próxima chave
        self.key_indices[provider] = (current_index + 1) % len(keys)

        logger.debug(f"🔄 {provider}: Usando chave {current_index + 1}/{len(keys)}")
        return key

    async def _search_firecrawl(self, query: str, api_key: str) -> Dict[str, Any]:
        """Busca usando Firecrawl"""
        try:
            async with aiohttp.ClientSession() as session:
                headers = {
                    'Authorization': f'Bearer {api_key}',
                    'Content-Type': 'application/json'
                }

                payload = {
                    'url': f'https://www.google.com/search?q={query}',
                    'formats': ['markdown'],
                    'onlyMainContent': True,
                    'includeTags': ['p', 'h1', 'h2', 'h3']
                }

                async with session.post(
                    'https://api.firecrawl.dev/v0/scrape',
                    json=payload,
                    headers=headers,
                    timeout=30
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        # Simula resultados baseados no conteúdo
                        content = data.get('data', {}).get('markdown', '')
                        results = [{'content': content[:1000], 'url': payload['url'], 'title': f'Resultado Firecrawl para {query}'}]
                        return {
                            'provider': 'FIRECRAWL',
                            'results': results,
                            'success': True
                        }
                    else:
                        logger.error(f"❌ Firecrawl erro {response.status}")
                        return {'provider': 'FIRECRAWL', 'success': False, 'error': f'Status {response.status}'}

        except Exception as e:
            logger.error(f"❌ Erro Firecrawl: {e}")
            return {'provider': 'FIRECRAWL', 'success': False, 'error': str(e)}

    async def _search_jina(self, query: str, api_key: str) -> Dict[str, Any]:
        """Busca usando Jina AI"""
        try:
            async with aiohttp.ClientSession() as session:
                headers = {
                    'Authorization': f'Bearer {api_key}',
                    'Accept': 'application/json'
                }

                # Usa Jina Reader para buscar conteúdo
                search_url = f"https://r.jina.ai/https://www.google.com/search?q={query}"

                async with session.get(
                    search_url,
                    headers=headers,
                    timeout=30
                ) as response:
                    if response.status == 200:
                        content = await response.text()
                        # Simula resultados baseados no conteúdo
                        results = [{'content': content[:1000], 'url': search_url, 'title': f'Resultado Jina para {query}'}]
                        return {
                            'provider': 'JINA',
                            'results': results,
                            'success': True
                        }
                    else:
                        logger.error(f"❌ Jina erro {response.status}")
                        return {'provider': 'JINA', 'success': False, 'error': f'Status {response.status}'}

        except Exception as e:
            if "401" in str(e):
                logger.warning(f"⚠️ Jina chave inválida, rotacionando...")
                # Rotaciona para próxima chave se disponível
                if hasattr(self, '_jina_key_index'):
                    self._jina_key_index = (self._jina_key_index + 1) % len(self.jina_keys)
                    logger.info(f"🔄 Tentando com próxima chave Jina")
                    # Tenta novamente com nova chave (máximo 1 tentativa extra)
                    if not hasattr(self, '_jina_retry_count'):
                        self._jina_retry_count = 0
                    if self._jina_retry_count < 1:
                        self._jina_retry_count += 1
                        return self._search_jina(query)

            logger.error(f"❌ Jina erro {e}")
            return []


    async def _search_google(self, query: str, api_key: str) -> Dict[str, Any]:
        """Busca usando Google Custom Search"""
        try:
            cx_id = os.getenv('GOOGLE_CSE_ID')
            if not cx_id:
                return {'provider': 'GOOGLE', 'success': False, 'error': 'CSE_ID não configurado'}

            async with aiohttp.ClientSession() as session:
                params = {
                    'key': api_key,
                    'cx': cx_id,
                    'q': query,
                    'num': 10,
                    'lr': 'lang_pt',
                    'gl': 'br'
                }

                async with session.get(
                    'https://www.googleapis.com/customsearch/v1',
                    params=params,
                    timeout=30
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        return {
                            'provider': 'GOOGLE',
                            'results': data.get('items', []),
                            'success': True
                        }
                    else:
                        logger.error(f"❌ Google erro {response.status}")
                        return {'provider': 'GOOGLE', 'success': False, 'error': f'Status {response.status}'}

        except Exception as e:
            logger.error(f"❌ Erro Google: {e}")
            return {'provider': 'GOOGLE', 'success': False, 'error': str(e)}

    async def _search_exa(self, query: str, api_key: str) -> Dict[str, Any]:
        """Busca usando Exa"""
        try:
            async with aiohttp.ClientSession() as session:
                headers = {
                    'x-api-key': api_key,
                    'Content-Type': 'application/json'
                }

                payload = {
                    'query': query,
                    'numResults': 10,
                    'useAutoprompt': True,
                    'type': 'neural'
                }

                async with session.post(
                    'https://api.exa.ai/search',
                    json=payload,
                    headers=headers,
                    timeout=30
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        return {
                            'provider': 'EXA',
                            'results': data.get('results', []),
                            'success': True
                        }
                    else:
                        logger.error(f"❌ Exa erro {response.status}")
                        return {'provider': 'EXA', 'success': False, 'error': f'Status {response.status}'}

        except Exception as e:
            logger.error(f"❌ Erro Exa: {e}")
            return {'provider': 'EXA', 'success': False, 'error': str(e)}

    async def interleaved_search(self, query: str) -> Dict[str, Any]:
        """Orquestra buscas intercaladas entre provedores"""
        logger.info(f"🔍 Iniciando busca intercalada para: {query}")

        search_tasks = []
        results = {
            'query': query,
            'timestamp': datetime.now().isoformat(),
            'providers_used': [],
            'successful_searches': 0,
            'failed_searches': 0,
            'all_results': [],
            'consolidated_urls': []
        }

        # Cria tarefas para cada provedor disponível
        search_methods = {
            'FIRECRAWL': self._search_firecrawl,
            'JINA': self._search_jina,
            'GOOGLE': self._search_google,
            'EXA': self._search_exa
        }

        for provider in self.providers:
            if provider in self.api_keys:
                api_key = self.get_next_key(provider)
                if api_key and provider in search_methods:
                    # Inicializa índices e contagens de retentativa para Jina se necessário
                    if provider == 'JINA':
                        if not hasattr(self, '_jina_key_index'):
                            self._jina_key_index = 0
                        if not hasattr(self, '_jina_retry_count'):
                            self._jina_retry_count = 0

                    task = search_methods[provider](query, api_key)
                    search_tasks.append(task)
                    results['providers_used'].append(provider)

        # Executa todas as buscas em paralelo
        if search_tasks:
            try:
                search_results = await asyncio.gather(*search_tasks, return_exceptions=True)

                for result in search_results:
                    if isinstance(result, Exception):
                        logger.error(f"❌ Erro na busca: {result}")
                        results['failed_searches'] += 1
                    elif isinstance(result, dict):
                        results['all_results'].append(result)
                        if result.get('success'):
                            results['successful_searches'] += 1

                            # Extrai URLs dos resultados
                            provider_results = result.get('results', [])
                            if isinstance(provider_results, list):
                                for item in provider_results:
                                    if isinstance(item, dict):
                                        url = item.get('url') or item.get('link')
                                        if url and url not in results['consolidated_urls']:
                                            results['consolidated_urls'].append(url)
                        else:
                            results['failed_searches'] += 1

                logger.info(f"✅ Busca concluída: {results['successful_searches']}/{len(search_tasks)} sucessos")
                logger.info(f"📊 URLs coletadas: {len(results['consolidated_urls'])}")

            except Exception as e:
                logger.error(f"❌ Erro na execução das buscas: {e}")
                results['error'] = str(e)
        else:
            logger.error("❌ Nenhum provedor disponível para busca")
            results['error'] = 'Nenhum provedor disponível'

        return results

    def get_available_providers(self) -> List[str]:
        """Retorna lista de provedores disponíveis"""
        return list(self.api_keys.keys())

    def get_provider_stats(self) -> Dict[str, Dict[str, Any]]:
        """Retorna estatísticas dos provedores"""
        stats = {}
        for provider in self.providers:
            if provider in self.api_keys:
                stats[provider] = {
                    'total_keys': len(self.api_keys[provider]),
                    'current_index': self.key_indices[provider],
                    'available': True
                }
            else:
                stats[provider] = {
                    'total_keys': 0,
                    'current_index': 0,
                    'available': False
                }
        return stats

# Instância global
search_api_manager = SearchAPIManager()