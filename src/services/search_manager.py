#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ARQV30 Enhanced v2.0 - Search Manager com Sistema de Fallback
Gerenciador inteligente de múltiplos serviços de busca com fallback automático
"""

import os
import logging
import time
import requests
from typing import Dict, List, Optional, Any
from urllib.parse import quote_plus
from bs4 import BeautifulSoup
import json

logger = logging.getLogger(__name__)

class SearchManager:
    """Gerenciador de buscas com sistema de fallback automático"""
    
    def __init__(self):
        """Inicializa o gerenciador de buscas"""
        self.providers = {
            'google': {
                'available': False,
                'priority': 1,
                'rate_limit_reset': None,
                'error_count': 0,
                'api_key': os.getenv('GOOGLE_SEARCH_KEY'),
                'cse_id': os.getenv('GOOGLE_CSE_ID')
            },
            'serper': {
                'available': False,
                'priority': 2,
                'rate_limit_reset': None,
                'error_count': 0,
                'api_key': os.getenv('SERPER_API_KEY')
            },
            'bing': {
                'available': True,  # Sempre disponível (scraping)
                'priority': 3,
                'rate_limit_reset': None,
                'error_count': 0
            },
            'duckduckgo': {
                'available': True,  # Sempre disponível (scraping)
                'priority': 4,
                'rate_limit_reset': None,
                'error_count': 0
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
        
        self.initialize_providers()
        logger.info(f"Search Manager inicializado com {len([p for p in self.providers.values() if p['available']])} provedores disponíveis")
    
    def initialize_providers(self):
        """Inicializa provedores de busca"""
        
        # Verifica Google Custom Search
        if self.providers['google']['api_key'] and self.providers['google']['cse_id']:
            self.providers['google']['available'] = True
            logger.info("✅ Google Custom Search disponível")
        
        # Verifica Serper
        if self.providers['serper']['api_key']:
            self.providers['serper']['available'] = True
            logger.info("✅ Serper API disponível")
        
        logger.info("✅ Bing e DuckDuckGo sempre disponíveis (scraping)")
    
    def get_best_provider(self) -> Optional[str]:
        """Retorna o melhor provedor disponível"""
        available_providers = [
            (name, provider) for name, provider in self.providers.items() 
            if provider['available'] and provider['error_count'] < 3
        ]
        
        if not available_providers:
            # Reset error counts se todos falharam
            for provider in self.providers.values():
                if provider['available']:
                    provider['error_count'] = 0
            available_providers = [
                (name, provider) for name, provider in self.providers.items() 
                if provider['available']
            ]
        
        if available_providers:
            # Ordena por prioridade e menor número de erros
            available_providers.sort(key=lambda x: (x[1]['priority'], x[1]['error_count']))
            return available_providers[0][0]
        
        return None
    
    def search(self, query: str, max_results: int = 10) -> List[Dict[str, Any]]:
        """Realiza busca usando o melhor provedor disponível"""
        
        provider_name = self.get_best_provider()
        if not provider_name:
            logger.error("❌ Nenhum provedor de busca disponível")
            return []
        
        logger.info(f"🔍 Usando provedor de busca: {provider_name}")
        
        try:
            if provider_name == 'google':
                return self._search_google(query, max_results)
            elif provider_name == 'serper':
                return self._search_serper(query, max_results)
            elif provider_name == 'bing':
                return self._search_bing(query, max_results)
            elif provider_name == 'duckduckgo':
                return self._search_duckduckgo(query, max_results)
        except Exception as e:
            logger.error(f"❌ Erro no provedor {provider_name}: {str(e)}")
            self.providers[provider_name]['error_count'] += 1
            
            # Tenta próximo provedor
            return self._try_fallback_search(query, max_results, exclude=[provider_name])
        
        return []
    
    def _search_google(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        """Busca usando Google Custom Search API"""
        try:
            url = "https://www.googleapis.com/customsearch/v1"
            params = {
                'key': self.providers['google']['api_key'],
                'cx': self.providers['google']['cse_id'],
                'q': query,
                'num': min(max_results, 10),
                'lr': 'lang_pt',
                'gl': 'br',
                'safe': 'off',
                'dateRestrict': 'm6'
            }
            
            response = requests.get(url, params=params, headers=self.headers, timeout=15)
            
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
                
                logger.info(f"✅ Google Search: {len(results)} resultados")
                return results
            else:
                raise Exception(f"Google API retornou status {response.status_code}")
                
        except Exception as e:
            if "quota" in str(e).lower() or "limit" in str(e).lower():
                logger.warning(f"⚠️ Google Search atingiu limite: {str(e)}")
                self.providers['google']['rate_limit_reset'] = time.time() + 3600
            raise e
    
    def _search_serper(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        """Busca usando Serper API"""
        try:
            url = "https://google.serper.dev/search"
            headers = {
                **self.headers,
                'X-API-KEY': self.providers['serper']['api_key'],
                'Content-Type': 'application/json'
            }
            
            payload = {
                'q': query,
                'gl': 'br',
                'hl': 'pt',
                'num': max_results
            }
            
            response = requests.post(url, json=payload, headers=headers, timeout=15)
            
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
                
                logger.info(f"✅ Serper Search: {len(results)} resultados")
                return results
            else:
                raise Exception(f"Serper API retornou status {response.status_code}")
                
        except Exception as e:
            if "quota" in str(e).lower() or "limit" in str(e).lower():
                logger.warning(f"⚠️ Serper atingiu limite: {str(e)}")
                self.providers['serper']['rate_limit_reset'] = time.time() + 3600
            raise e
    
    def _search_bing(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        """Busca usando Bing (scraping)"""
        try:
            search_url = f"https://www.bing.com/search?q={quote_plus(query)}&cc=br&setlang=pt-br&count={max_results}"
            
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
                
                logger.info(f"✅ Bing Search: {len(results)} resultados")
                return results
            else:
                raise Exception(f"Bing retornou status {response.status_code}")
                
        except Exception as e:
            raise e
    
    def _search_duckduckgo(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        """Busca usando DuckDuckGo (scraping)"""
        try:
            search_url = f"https://html.duckduckgo.com/html/?q={quote_plus(query)}"
            
            response = requests.get(search_url, headers=self.headers, timeout=15)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                results = []
                
                result_divs = soup.find_all('div', class_='result')
                
                for div in result_divs[:max_results]:
                    title_elem = div.find('a', class_='result__a')
                    snippet_elem = div.find('a', class_='result__snippet')
                    
                    if title_elem:
                        title = title_elem.get_text(strip=True)
                        url = title_elem.get('href', '')
                        snippet = snippet_elem.get_text(strip=True) if snippet_elem else ""
                        
                        if url and title and url.startswith('http'):
                            results.append({
                                'title': title,
                                'url': url,
                                'snippet': snippet,
                                'source': 'duckduckgo'
                            })
                
                logger.info(f"✅ DuckDuckGo Search: {len(results)} resultados")
                return results
            else:
                if response.status_code == 202:
                    logger.warning(f"⚠️ DuckDuckGo retornou status 202")
                    return [] # Retorna lista vazia para 202, indicando que a busca não foi concluída
                else:
                    raise Exception(f"DuckDuckGo retornou status {response.status_code}")
                
        except Exception as e:
            raise e
    
    def _try_fallback_search(self, query: str, max_results: int, exclude: List[str] = None) -> List[Dict[str, Any]]:
        """Tenta usar provedor de fallback para busca"""
        exclude = exclude or []
        
        for provider_name in ['google', 'serper', 'bing', 'duckduckgo']:
            if provider_name in exclude:
                continue
                
            if not self.providers[provider_name]['available']:
                continue
                
            if self.providers[provider_name]['error_count'] >= 3:
                continue
            
            logger.info(f"🔄 Tentando fallback de busca para: {provider_name}")
            
            try:
                if provider_name == 'google':
                    return self._search_google(query, max_results)
                elif provider_name == 'serper':
                    return self._search_serper(query, max_results)
                elif provider_name == 'bing':
                    return self._search_bing(query, max_results)
                elif provider_name == 'duckduckgo':
                    return self._search_duckduckgo(query, max_results)
            except Exception as e:
                logger.warning(f"⚠️ Fallback de busca {provider_name} falhou: {str(e)}")
                self.providers[provider_name]['error_count'] += 1
                continue
        
        logger.error("❌ Todos os provedores de busca de fallback falharam")
        return []
    
    def multi_search(self, query: str, max_results_per_provider: int = 5) -> List[Dict[str, Any]]:
        """Realiza busca em múltiplos provedores simultaneamente"""
        all_results = []
        
        for provider_name in ['google', 'serper', 'bing', 'duckduckgo']:
            if not self.providers[provider_name]['available']:
                continue
                
            if self.providers[provider_name]['error_count'] >= 3:
                continue
            
            try:
                logger.info(f"🔍 Buscando em {provider_name}...")
                
                if provider_name == 'google':
                    results = self._search_google(query, max_results_per_provider)
                elif provider_name == 'serper':
                    results = self._search_serper(query, max_results_per_provider)
                elif provider_name == 'bing':
                    results = self._search_bing(query, max_results_per_provider)
                elif provider_name == 'duckduckgo':
                    results = self._search_duckduckgo(query, max_results_per_provider)
                else:
                    continue
                
                all_results.extend(results)
                time.sleep(1)  # Rate limiting
                
            except Exception as e:
                logger.warning(f"⚠️ Erro em {provider_name}: {str(e)}")
                self.providers[provider_name]['error_count'] += 1
                continue
        
        # Remove duplicatas baseado na URL
        seen_urls = set()
        unique_results = []
        
        for result in all_results:
            if result['url'] not in seen_urls:
                seen_urls.add(result['url'])
                unique_results.append(result)
        
        logger.info(f"✅ Multi-search: {len(unique_results)} resultados únicos de {len(all_results)} totais")
        return unique_results
    
    def get_provider_status(self) -> Dict[str, Any]:
        """Retorna status de todos os provedores"""
        status = {}
        
        for name, provider in self.providers.items():
            status[name] = {
                'available': provider['available'],
                'priority': provider['priority'],
                'error_count': provider['error_count'],
                'rate_limited': (provider.get('rate_limit_reset') or 0) > time.time()
            }
        
        return status
    
    def reset_provider_errors(self, provider_name: str = None):
        """Reset contadores de erro"""
        if provider_name:
            if provider_name in self.providers:
                self.providers[provider_name]['error_count'] = 0
                logger.info(f"🔄 Reset erros do provedor de busca: {provider_name}")
        else:
            for provider in self.providers.values():
                provider['error_count'] = 0
            logger.info("🔄 Reset erros de todos os provedores de busca")

# Instância global
search_manager = SearchManager()
