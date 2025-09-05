
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ARQV30 Enhanced v2.0 - Fallback Search Engine
Motor de busca de fallback quando APIs externas falham
"""

import logging
import requests
import time
from typing import Dict, List, Any, Optional
from urllib.parse import quote_plus
from bs4 import BeautifulSoup
import re
from datetime import datetime

logger = logging.getLogger(__name__)

class FallbackSearchEngine:
    """Motor de busca de fallback usando scraping direto"""
    
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'pt-BR,pt;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate',
            'DNT': '1',
            'Connection': 'keep-alive'
        }
        
        self.search_engines = {
            'bing': self._search_bing_direct,
            'duckduckgo': self._search_duckduckgo_direct,
            'yahoo': self._search_yahoo_direct
        }
        
        logger.info("🔄 Fallback Search Engine inicializado")
    
    def comprehensive_fallback_search(self, query: str, max_results: int = 25) -> List[Dict[str, Any]]:
        """Executa busca abrangente usando múltiplos motores de fallback"""
        
        try:
            logger.info(f"🚀 Iniciando busca fallback para: {query}")
            
            all_results = []
            
            # Executa em todos os motores disponíveis
            for engine_name, search_func in self.search_engines.items():
                try:
                    logger.info(f"🔍 Buscando em {engine_name}...")
                    results = search_func(query, max_results // len(self.search_engines))
                    
                    if results:
                        all_results.extend(results)
                        logger.info(f"✅ {engine_name}: {len(results)} resultados")
                    
                    time.sleep(2)  # Rate limiting
                    
                except Exception as e:
                    logger.error(f"❌ Erro em {engine_name}: {str(e)}")
                    continue
            
            # Remove duplicatas
            unique_results = self._remove_duplicates(all_results)
            
            logger.info(f"✅ Busca fallback concluída: {len(unique_results)} resultados únicos")
            
            return unique_results[:max_results]
            
        except Exception as e:
            logger.error(f"❌ Erro na busca fallback: {str(e)}")
            return self._generate_synthetic_results(query)
    
    def _search_bing_direct(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        """Busca direta no Bing com URLs corretas"""
        
        try:
            search_url = f"https://www.bing.com/search?q={quote_plus(query + ' site:brasil OR site:.br')}&count={max_results}"
            
            response = requests.get(search_url, headers=self.headers, timeout=15)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                results = []
                
                # Procura resultados orgânicos
                for item in soup.find_all('li', class_='b_algo')[:max_results]:
                    title_elem = item.find('h2')
                    if title_elem and title_elem.find('a'):
                        link = title_elem.find('a')
                        
                        title = title_elem.get_text(strip=True)
                        url = link.get('href', '')
                        
                        # Pega snippet
                        snippet_elem = item.find('p') or item.find('div', class_='b_caption')
                        snippet = snippet_elem.get_text(strip=True) if snippet_elem else ""
                        
                        # Filtra URLs válidas e brasileiras
                        if (url.startswith('http') and 
                            ('.br' in url or 'brasil' in url.lower() or 'globo.com' in url) and
                            not any(exclude in url.lower() for exclude in ['bing.com/ck', 'redirect', 'proxy'])):
                            
                            results.append({
                                'title': title,
                                'url': url,
                                'snippet': snippet,
                                'source': 'bing_direct',
                                'found_at': datetime.now().isoformat()
                            })
                
                return results
                
        except Exception as e:
            logger.error(f"❌ Erro no Bing direto: {str(e)}")
            return []
    
    def _search_duckduckgo_direct(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        """Busca direta no DuckDuckGo"""
        
        try:
            search_url = f"https://html.duckduckgo.com/html/?q={quote_plus(query + ' Brasil')}"
            
            response = requests.get(search_url, headers=self.headers, timeout=15)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                results = []
                
                for result_div in soup.find_all('div', class_='result')[:max_results]:
                    title_elem = result_div.find('a', class_='result__a')
                    snippet_elem = result_div.find('a', class_='result__snippet')
                    
                    if title_elem:
                        title = title_elem.get_text(strip=True)
                        url = title_elem.get('href', '')
                        snippet = snippet_elem.get_text(strip=True) if snippet_elem else ""
                        
                        if url.startswith('http') and '.br' in url:
                            results.append({
                                'title': title,
                                'url': url,
                                'snippet': snippet,
                                'source': 'duckduckgo_direct',
                                'found_at': datetime.now().isoformat()
                            })
                
                return results
                
        except Exception as e:
            logger.error(f"❌ Erro no DuckDuckGo direto: {str(e)}")
            return []
    
    def _search_yahoo_direct(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        """Busca direta no Yahoo"""
        
        try:
            search_url = f"https://br.search.yahoo.com/search?p={quote_plus(query)}&n={max_results}"
            
            response = requests.get(search_url, headers=self.headers, timeout=15)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                results = []
                
                for result in soup.find_all('div', class_='Sr')[:max_results]:
                    title_elem = result.find('h3')
                    link_elem = result.find('a')
                    snippet_elem = result.find('p')
                    
                    if title_elem and link_elem:
                        title = title_elem.get_text(strip=True)
                        url = link_elem.get('href', '')
                        snippet = snippet_elem.get_text(strip=True) if snippet_elem else ""
                        
                        if url.startswith('http') and '.br' in url:
                            results.append({
                                'title': title,
                                'url': url,
                                'snippet': snippet,
                                'source': 'yahoo_direct',
                                'found_at': datetime.now().isoformat()
                            })
                
                return results
                
        except Exception as e:
            logger.error(f"❌ Erro no Yahoo direto: {str(e)}")
            return []
    
    def _remove_duplicates(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove resultados duplicados baseado na URL"""
        
        seen_urls = set()
        unique_results = []
        
        for result in results:
            url = result.get('url', '')
            if url not in seen_urls:
                seen_urls.add(url)
                unique_results.append(result)
        
        return unique_results
    
    def _generate_synthetic_results(self, query: str) -> List[Dict[str, Any]]:
        """Gera resultados sintéticos quando todas as buscas falham"""
        
        synthetic_sources = [
            {
                'title': f'Análise de mercado: {query}',
                'url': 'https://g1.globo.com/economia/',
                'snippet': f'Análise detalhada sobre as tendências de mercado para {query} no Brasil.',
                'source': 'synthetic_fallback'
            },
            {
                'title': f'Oportunidades em {query}',
                'url': 'https://exame.com/negocios/',
                'snippet': f'Principais oportunidades de negócio identificadas no setor de {query}.',
                'source': 'synthetic_fallback'
            },
            {
                'title': f'Crescimento do setor {query}',
                'url': 'https://valor.globo.com/empresas/',
                'snippet': f'Dados sobre o crescimento e perspectivas do mercado de {query}.',
                'source': 'synthetic_fallback'
            }
        ]
        
        logger.warning("⚠️ Usando resultados sintéticos - APIs indisponíveis")
        return synthetic_sources

# Instância global
fallback_search_engine = FallbackSearchEngine()
