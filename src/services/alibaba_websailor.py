#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ARQV30 Enhanced v2.0 - Alibaba WebSailor Agent
Agente de navegação web inteligente com busca profunda e análise contextual
"""

import os
import logging
import time
import requests
import json
import random
from typing import Dict, List, Optional, Any
from urllib.parse import quote_plus, urljoin, urlparse
from bs4 import BeautifulSoup
from datetime import datetime
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from services.auto_save_manager import salvar_etapa, salvar_erro

logger = logging.getLogger(__name__)

class AlibabaWebSailorAgent:
    """Agente WebSailor inteligente para navegação e análise web profunda"""

    def __init__(self):
        """Inicializa agente WebSailor"""
        self.enabled = True
        self.google_search_key = os.getenv("GOOGLE_SEARCH_KEY")
        self.jina_api_key = os.getenv("JINA_API_KEY")
        self.google_cse_id = os.getenv("GOOGLE_CSE_ID")
        self.serper_api_key = os.getenv("SERPER_API_KEY")

        # URLs das APIs
        self.google_search_url = "https://www.googleapis.com/customsearch/v1"
        self.jina_reader_url = "https://r.jina.ai/"
        self.serper_url = "https://google.serper.dev/search"

        # Headers inteligentes para navegação
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "pt-BR,pt;q=0.9,en;q=0.8",
            "Accept-Encoding": "gzip, deflate, br",
            "DNT": "1",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none"
        }

        # Domínios brasileiros preferenciais
        self.preferred_domains = {
            "g1.globo.com", "exame.com", "valor.globo.com", "estadao.com.br",
            "folha.uol.com.br", "canaltech.com.br", "tecmundo.com.br",
            "olhardigital.com.br", "infomoney.com.br", "startse.com",
            "revistapegn.globo.com", "epocanegocios.globo.com", "istoedinheiro.com.br",
            "convergenciadigital.com.br", "mobiletime.com.br", "teletime.com.br",
            "portaltelemedicina.com.br", "saudedigitalbrasil.com.br", "amb.org.br",
            "portal.cfm.org.br", "scielo.br", "ibge.gov.br", "fiocruz.br"
        }

        # Domínios bloqueados (irrelevantes)
        self.blocked_domains = {
            "instagram.com", "facebook.com", "twitter.com", "linkedin.com",
            "youtube.com", "tiktok.com", "pinterest.com", "reddit.com",
            "accounts.google.com", "login.microsoft.com", "amazon.com.br",
            "mercadolivre.com.br", "olx.com.br", "booking.com", "airbnb.com"
        }

        self.session = requests.Session()
        self.session.headers.update(self.headers)
        # Configuração SSL mais robusta
        self.session.verify = True  # Mantém verificação SSL por padrão
        
        # Configuração de timeout e retry
        from requests.adapters import HTTPAdapter
        from urllib3.util.retry import Retry
        
        try:
            # Tenta usar o parâmetro novo (urllib3 >= 1.26.0)
            retry_strategy = Retry(
                total=3,
                status_forcelist=[429, 500, 502, 503, 504],
                allowed_methods=["HEAD", "GET", "OPTIONS"],
                backoff_factor=1
            )
        except TypeError:
            # Fallback para versões antigas do urllib3
            retry_strategy = Retry(
                total=3,
                status_forcelist=[429, 500, 502, 503, 504],
                method_whitelist=["HEAD", "GET", "OPTIONS"],
                backoff_factor=1
            )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

        # Estatísticas de navegação
        self.navigation_stats = {
            'total_searches': 0,
            'successful_extractions': 0,
            'failed_extractions': 0,
            'blocked_urls': 0,
            'preferred_sources': 0,
            'total_content_chars': 0,
            'avg_quality_score': 0.0
        }

        logger.info("🌐 Alibaba WebSailor Agent inicializado - Navegação inteligente ativada")

    def navigate_and_research_deep(
        self,
        query: str,
        context: Dict[str, Any],
        max_pages: int = 25,
        depth_levels: int = 3,
        session_id: str = None
    ) -> Dict[str, Any]:
        """Navegação e pesquisa profunda com múltiplos níveis"""

        try:
            logger.info(f"🚀 INICIANDO NAVEGAÇÃO PROFUNDA para: {query}")
            start_time = time.time()

            # Salva início da navegação
            salvar_etapa("websailor_iniciado", {
                "query": query,
                "context": context,
                "max_pages": max_pages,
                "depth_levels": depth_levels
            }, categoria="pesquisa_web")

            all_content = []
            search_engines_used = []

            # NÍVEL 1: BUSCA MASSIVA MULTI-ENGINE
            logger.info("🔍 NÍVEL 1: Busca massiva com múltiplos engines")

            # Engines de busca em ordem de prioridade
            search_engines = [
                ("Google Custom Search", self._google_search_deep),
                ("Serper API", self._serper_search_deep),
                ("Bing Scraping", self._bing_search_deep),
                ("DuckDuckGo Scraping", self._duckduckgo_search_deep),
                ("Yahoo Scraping", self._yahoo_search_deep)
            ]

            for engine_name, search_func in search_engines:
                try:
                    logger.info(f"🔍 Executando {engine_name}...")
                    results = search_func(query, max_pages // len(search_engines))

                    if results:
                        search_engines_used.append(engine_name)
                        logger.info(f"✅ {engine_name}: {len(results)} resultados")

                        # Extrai conteúdo de cada resultado
                        for result in results:
                            content_data = self._extract_intelligent_content(
                                result['url'], result.get('title', ''), result.get('snippet', ''), context
                            )

                            if content_data and content_data['success']:
                                all_content.append({
                                    **content_data,
                                    'search_engine': engine_name,
                                    'search_result': result
                                })

                                # Salva cada extração bem-sucedida
                                salvar_etapa(f"websailor_extracao_{len(all_content)}", {
                                    "url": result['url'],
                                    "engine": engine_name,
                                    "content_length": len(content_data['content']),
                                    "quality_score": content_data['quality_score']
                                }, categoria="pesquisa_web")

                            time.sleep(0.5)  # Rate limiting

                    time.sleep(1)  # Delay entre engines

                except Exception as e:
                    logger.error(f"❌ Erro em {engine_name}: {str(e)}")
                    continue

            # NÍVEL 2: BUSCA EM PROFUNDIDADE (Links internos)
            if depth_levels > 1 and all_content:
                logger.info("🔍 NÍVEL 2: Busca em profundidade - Links internos")

                # Seleciona top páginas para explorar links internos
                top_pages = sorted(all_content, key=lambda x: x['quality_score'], reverse=True)[:5]

                for page in top_pages:
                    internal_links = self._extract_internal_links(page['url'], page['content'])

                    for link in internal_links[:3]:  # Top 3 links por página
                        internal_content = self._extract_intelligent_content(link, "", "", context)

                        if internal_content and internal_content['success']:
                            internal_content['search_engine'] = f"{page['search_engine']} (Internal)"
                            internal_content['parent_url'] = page['url']
                            all_content.append(internal_content)

                            time.sleep(0.3)

            # NÍVEL 3: QUERIES RELACIONADAS INTELIGENTES
            if depth_levels > 2:
                logger.info("🔍 NÍVEL 3: Queries relacionadas inteligentes")

                related_queries = self._generate_intelligent_related_queries(query, context, all_content)

                for related_query in related_queries[:3]:
                    try:
                        related_results = self._google_search_deep(related_query, 5)

                        for result in related_results:
                            related_content = self._extract_intelligent_content(
                                result['url'], result.get('title', ''), result.get('snippet', ''), context
                            )

                            if related_content and related_content['success']:
                                related_content['search_engine'] = "Google (Related Query)"
                                related_content['related_query'] = related_query
                                all_content.append(related_content)

                                time.sleep(0.4)
                    except Exception as e:
                        logger.warning(f"⚠️ Erro em query relacionada '{related_query}': {str(e)}")
                        continue

            # PROCESSAMENTO E ANÁLISE FINAL
            processed_research = self._process_and_analyze_content(all_content, query, context)

            # Atualiza estatísticas
            self._update_navigation_stats(all_content)

            end_time = time.time()

            # Salva resultado final da navegação
            salvar_etapa("websailor_resultado", processed_research, categoria="pesquisa_web")

            logger.info(f"✅ NAVEGAÇÃO PROFUNDA CONCLUÍDA em {end_time - start_time:.2f} segundos")
            logger.info(f"📊 {len(all_content)} páginas analisadas com {len(search_engines_used)} engines")

            return processed_research

        except Exception as e:
            logger.error(f"❌ ERRO CRÍTICO na navegação WebSailor: {str(e)}")
            salvar_erro("websailor_critico", e, contexto={"query": query})
            return self._generate_emergency_research(query, context)

    def _google_search_deep(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        """Busca profunda usando Google Custom Search API"""

        if not self.google_search_key or not self.google_cse_id:
            return []

        try:
            # Melhora query para pesquisa brasileira
            enhanced_query = self._enhance_query_for_brazil(query)

            params = {
                "key": self.google_search_key,
                "cx": self.google_cse_id,
                "q": enhanced_query,
                "num": min(max_results, 10),
                "lr": "lang_pt",
                "gl": "br",
                "safe": "off",
                "dateRestrict": "m12",  # Últimos 12 meses
                "sort": "date",
                "filter": "1"  # Remove duplicatas
            }

            response = requests.get(
                self.google_search_url,
                params=params,
                headers=self.headers,
                timeout=15
            )

            if response.status_code == 200:
                data = response.json()
                results = []

                for item in data.get("items", []):
                    url = item.get("link", "")

                    # Filtra URLs irrelevantes
                    if self._is_url_relevant(url, item.get("title", ""), item.get("snippet", "")):
                        results.append({
                            "title": item.get("title", ""),
                            "url": url,
                            "snippet": item.get("snippet", ""),
                            "source": "google_custom_search"
                        })

                self.navigation_stats['total_searches'] += 1
                return results
            else:
                logger.warning(f"⚠️ Google Search falhou: {response.status_code}")
                return []

        except Exception as e:
            logger.error(f"❌ Erro no Google Search: {str(e)}")
            return []

    def _serper_search_deep(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        """Busca profunda usando Serper API"""

        if not self.serper_api_key:
            return []

        try:
            headers = {
                **self.headers,
                'X-API-KEY': self.serper_api_key,
                'Content-Type': 'application/json'
            }

            payload = {
                'q': self._enhance_query_for_brazil(query),
                'gl': 'br',
                'hl': 'pt',
                'num': max_results,
                'autocorrect': True,
                'page': 1
            }

            response = requests.post(
                self.serper_url,
                json=payload,
                headers=headers,
                timeout=15
            )

            if response.status_code == 200:
                data = response.json()
                results = []

                for item in data.get("organic", []):
                    url = item.get("link", "")

                    if self._is_url_relevant(url, item.get("title", ""), item.get("snippet", "")):
                        results.append({
                            "title": item.get("title", ""),
                            "url": url,
                            "snippet": item.get("snippet", ""),
                            "source": "serper_api"
                        })

                return results
            else:
                logger.warning(f"⚠️ Serper falhou: {response.status_code}")
                return []

        except Exception as e:
            logger.error(f"❌ Erro no Serper: {str(e)}")
            return []

    def _bing_search_deep(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        """Busca profunda usando Bing (scraping inteligente)"""

        try:
            search_url = f"https://www.bing.com/search?q={quote_plus(query)}&cc=br&setlang=pt-br&count={max_results}"

            response = self.session.get(search_url, timeout=15)

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

                            # Resolve URLs do Bing
                            url = self._resolve_bing_url(url)

                            snippet_elem = item.find('p')
                            snippet = snippet_elem.get_text(strip=True) if snippet_elem else ""

                            if url and title and self._is_url_relevant(url, title, snippet):
                                results.append({
                                    "title": title,
                                    "url": url,
                                    "snippet": snippet,
                                    "source": "bing_scraping"
                                })

                return results
            else:
                logger.warning(f"⚠️ Bing falhou: {response.status_code}")
                return []

        except Exception as e:
            logger.error(f"❌ Erro no Bing: {str(e)}")
            return []

    def _duckduckgo_search_deep(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        """Busca profunda usando DuckDuckGo"""

        try:
            search_url = f"https://html.duckduckgo.com/html/?q={quote_plus(query)}"

            response = self.session.get(search_url, timeout=15)

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

                        if url and title and self._is_url_relevant(url, title, snippet):
                            results.append({
                                "title": title,
                                "url": url,
                                "snippet": snippet,
                                "source": "duckduckgo_scraping"
                            })

                return results
            else:
                return []

        except Exception as e:
            logger.error(f"❌ Erro no DuckDuckGo: {str(e)}")
            return []

    def _yahoo_search_deep(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        """Busca profunda usando Yahoo"""

        try:
            search_url = f"https://br.search.yahoo.com/search?p={quote_plus(query)}&ei=UTF-8"

            response = self.session.get(search_url, timeout=15)

            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                results = []

                result_items = soup.find_all('div', class_='Sr')

                for item in result_items[:max_results]:
                    title_elem = item.find('h3')
                    if title_elem:
                        link_elem = title_elem.find('a')
                        if link_elem:
                            title = title_elem.get_text(strip=True)
                            url = link_elem.get('href', '')

                            snippet_elem = item.find('span', class_='fz-ms')
                            snippet = snippet_elem.get_text(strip=True) if snippet_elem else ""

                            if url and title and self._is_url_relevant(url, title, snippet):
                                results.append({
                                    "title": title,
                                    "url": url,
                                    "snippet": snippet,
                                    "source": "yahoo_scraping"
                                })

                return results
            else:
                return []

        except Exception as e:
            logger.error(f"❌ Erro no Yahoo: {str(e)}")
            return []

    def _extract_intelligent_content(
        self,
        url: str,
        title: str,
        snippet: str,
        context: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Extração inteligente de conteúdo com validação"""

        if not url or not url.startswith('http'):
            return None

        try:
            # Verifica se URL é relevante
            if not self._is_url_relevant(url, title, snippet):
                self.navigation_stats['blocked_urls'] += 1
                return None

            # Prioriza domínios preferenciais
            domain = urlparse(url).netloc.lower()
            is_preferred = any(pref_domain in domain for pref_domain in self.preferred_domains)

            if is_preferred:
                self.navigation_stats['preferred_sources'] += 1

            # Extrai conteúdo usando múltiplas estratégias
            content = self._extract_with_multiple_strategies(url)

            if not content or len(content) < 300:
                self.navigation_stats['failed_extractions'] += 1
                return None

            # Valida qualidade do conteúdo
            quality_score = self._calculate_content_quality(content, url, context)

            if quality_score < 60.0:  # Threshold de qualidade
                self.navigation_stats['failed_extractions'] += 1
                return None

            # Extrai insights específicos
            insights = self._extract_content_insights(content, context)

            self.navigation_stats['successful_extractions'] += 1
            self.navigation_stats['total_content_chars'] += len(content)

            return {
                'success': True,
                'url': url,
                'title': title,
                'content': content,
                'quality_score': quality_score,
                'insights': insights,
                'is_preferred_source': is_preferred,
                'extraction_method': 'multi_strategy',
                'content_length': len(content),
                'word_count': len(content.split()),
                'extracted_at': datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"❌ Erro ao extrair conteúdo de {url}: {str(e)}")
            self.navigation_stats['failed_extractions'] += 1
            return None

    def _extract_with_multiple_strategies(self, url: str) -> Optional[str]:
        """Extrai conteúdo usando múltiplas estratégias"""

        strategies = [
            ("Jina Reader", self._extract_with_jina),
            ("Trafilatura", self._extract_with_trafilatura),
            ("Readability", self._extract_with_readability),
            ("BeautifulSoup", self._extract_with_beautifulsoup)
        ]

        for strategy_name, strategy_func in strategies:
            try:
                content = strategy_func(url)
                if content and len(content) > 300:
                    logger.info(f"✅ {strategy_name}: {len(content)} caracteres de {url}")
                    return content
            except Exception as e:
                logger.warning(f"⚠️ {strategy_name} falhou para {url}: {str(e)}")
                continue

        return None

    def _extract_with_jina(self, url: str) -> Optional[str]:
        """Extrai usando Jina Reader API"""

        if not self.jina_api_key:
            return None

        try:
            headers = {
                **self.headers,
                "Authorization": f"Bearer {self.jina_api_key}"
            }

            jina_url = f"{self.jina_reader_url}{url}"

            response = requests.get(jina_url, headers=headers, timeout=60)

            if response.status_code == 200:
                content = response.text

                if len(content) > 15000:
                    content = content[:15000] + "... [conteúdo truncado para otimização]"

                return content
            else:
                # Logar erro específico do Jina Reader
                logger.error(f"❌ Jina Reader API falhou para {url} com status {response.status_code}. Response: {response.text}")
                return None

        except Exception as e:
            logger.error(f"❌ Erro no _extract_with_jina para {url}: {str(e)}")
            raise e # Levanta a exceção para ser tratada no nível superior

    def _extract_with_trafilatura(self, url: str) -> Optional[str]:
        """Extrai usando Trafilatura"""

        try:
            import trafilatura

            downloaded = trafilatura.fetch_url(url)
            if downloaded:
                content = trafilatura.extract(
                    downloaded,
                    include_comments=False,
                    include_tables=True,
                    include_formatting=False,
                    favor_precision=False,
                    favor_recall=True,
                    url=url
                )
                return content
            return None

        except ImportError:
            logger.warning("⚠️ Trafilatura não está instalada. Ignorando.")
            return None
        except Exception as e:
            logger.error(f"❌ Erro no Trafilatura para {url}: {str(e)}")
            raise e

    def _extract_with_readability(self, url: str) -> Optional[str]:
        """Extrai usando Readability"""

        try:
            from readability import Document

            response = self.session.get(url, timeout=20)
            if response.status_code == 200:
                content_bytes = response.content # Recebe como bytes
                min_length = 300 # Define um comprimento mínimo

                # Converter bytes para string se necessário
                if isinstance(content_bytes, bytes):
                    content_str = content_bytes.decode('utf-8', errors='ignore')
                else:
                    content_str = content_bytes

                doc = Document(content_str)
                content = doc.summary()
                if content and len(content.strip()) > min_length:
                    logger.info(f"✅ Readability: {len(content)} caracteres de {url}")
                    return content
                else:
                    logger.warning(f"⚠️ Readability: conteúdo muito curto de {url}")
            else:
                logger.warning(f"⚠️ Readability falhou ao obter conteúdo de {url}: Status {response.status_code}")
            return None

        except ImportError:
            logger.warning("⚠️ Readability não está instalada. Ignorando.")
            return None
        except Exception as e:
            logger.error(f"❌ Erro no Readability para {url}: {str(e)}")
            raise e

    def _extract_with_beautifulsoup(self, url: str) -> Optional[str]:
        """Extrai usando BeautifulSoup"""

        try:
            response = self.session.get(url, timeout=20)

            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')

                # Remove elementos desnecessários
                for element in soup(['script', 'style', 'nav', 'header', 'footer', 'aside']):
                    element.decompose()

                # Busca conteúdo principal
                main_content = (
                    soup.find('main') or
                    soup.find('article') or
                    soup.find('div', class_=re.compile(r'content|main|article'))
                )

                if main_content:
                    return main_content.get_text()
                else:
                    return soup.get_text()

            else:
                logger.warning(f"⚠️ BeautifulSoup falhou ao obter conteúdo de {url}: Status {response.status_code}")
            return None

        except Exception as e:
            logger.error(f"❌ Erro no BeautifulSoup para {url}: {str(e)}")
            raise e

    def _is_url_relevant(self, url: str, title: str, snippet: str) -> bool:
        """Verifica se URL é relevante para análise"""

        if not url or not url.startswith('http'):
            return False

        domain = urlparse(url).netloc.lower()

        # Bloqueia domínios irrelevantes
        if any(blocked in domain for blocked in self.blocked_domains):
            return False

        # Bloqueia padrões irrelevantes
        blocked_patterns = [
            '/login', '/signin', '/register', '/cadastro', '/auth',
            '/account', '/profile', '/settings', '/admin', '/api/',
            '.pdf', '.jpg', '.png', '.gif', '.mp4', '.zip',
            '/download', '/cart', '/checkout', '/payment'
        ]

        url_lower = url.lower()
        if any(pattern in url_lower for pattern in blocked_patterns):
            return False

        # Verifica relevância do conteúdo
        content_text = f"{title} {snippet}".lower()

        # Palavras irrelevantes
        irrelevant_words = [
            'login', 'cadastro', 'carrinho', 'comprar', 'download',
            'termos de uso', 'política de privacidade', 'contato',
            'sobre nós', 'trabalhe conosco', 'vagas'
        ]

        irrelevant_count = sum(1 for word in irrelevant_words if word in content_text)
        if irrelevant_count >= 2:
            return False

        return True

    def _resolve_bing_url(self, url: str) -> str:
        """Resolve URLs de redirecionamento do Bing"""

        if "bing.com/ck/a" not in url or "u=a1" not in url:
            return url

        try:
            import base64

            # Extrai parâmetro u=a1...
            if "u=a1" in url:
                u_param_start = url.find("u=a1") + 4
                u_param_end = url.find("&", u_param_start)
                if u_param_end == -1:
                    u_param_end = len(url)

                encoded_part = url[u_param_start:u_param_end]

                # Decodifica Base64
                try:
                    # Limpa e adiciona padding
                    encoded_part = encoded_part.replace('%3d', '=').replace('%3D', '=')
                    missing_padding = len(encoded_part) % 4
                    if missing_padding:
                        encoded_part += '=' * (4 - missing_padding)

                    # Primeira decodificação
                    first_decode = base64.b64decode(encoded_part)
                    first_decode_str = first_decode.decode('utf-8', errors='ignore')

                    if first_decode_str.startswith('aHR0'):
                        # Segunda decodificação necessária
                        missing_padding = len(first_decode_str) % 4
                        if missing_padding:
                            first_decode_str += '=' * (4 - missing_padding)

                        second_decode = base64.b64decode(first_decode_str)
                        final_url = second_decode.decode('utf-8', errors='ignore')

                        if final_url.startswith('http'):
                            return final_url

                    elif first_decode_str.startswith('http'):
                        return first_decode_str

                except Exception:
                    pass

            return url

        except Exception:
            return url

    def _enhance_query_for_brazil(self, query: str) -> str:
        """Melhora query para pesquisa no Brasil"""

        # Termos que melhoram precisão para mercado brasileiro
        brazil_terms = [
            "Brasil", "brasileiro", "mercado nacional", "dados BR",
            "estatísticas Brasil", "empresas brasileiras", "2024", "2025"
        ]

        enhanced_query = query
        query_lower = query.lower()

        # Adiciona termos brasileiros se não estiverem presentes
        if not any(term.lower() in query_lower for term in ["brasil", "brasileiro", "br"]):
            enhanced_query += " Brasil"

        # Adiciona ano atual se não estiver presente
        if not any(year in query for year in ["2024", "2025"]):
            enhanced_query += " 2024"

        return enhanced_query.strip()

    def _calculate_content_quality(
        self,
        content: str,
        url: str,
        context: Dict[str, Any]
    ) -> float:
        """Calcula qualidade do conteúdo extraído"""

        if not content:
            return 0.0

        score = 0.0
        content_lower = content.lower()

        # Score por tamanho (máximo 20 pontos)
        if len(content) >= 2000:
            score += 20
        elif len(content) >= 1000:
            score += 15
        elif len(content) >= 500:
            score += 10
        else:
            score += 5

        # Score por relevância ao contexto (máximo 30 pontos)
        context_terms = []
        if context.get('segmento'):
            context_terms.append(context['segmento'].lower())
        if context.get('produto'):
            context_terms.append(context['produto'].lower())
        if context.get('publico'):
            context_terms.append(context['publico'].lower())

        relevance_score = 0
        for term in context_terms:
            if term and term in content_lower:
                relevance_score += 10

        score += min(relevance_score, 30)

        # Score por qualidade do domínio (máximo 20 pontos)
        domain = urlparse(url).netloc.lower()
        if any(pref in domain for pref in self.preferred_domains):
            score += 20
        elif domain.endswith('.gov.br') or domain.endswith('.edu.br'):
            score += 15
        elif domain.endswith('.org.br'):
            score += 10
        else:
            score += 5

        # Score por densidade de informação (máximo 15 pontos)
        words = content.split()
        if len(words) >= 500:
            score += 15
        elif len(words) >= 200:
            score += 10
        else:
            score += 5

        # Score por presença de dados (máximo 15 pontos)
        data_patterns = [
            r'\d+%', r'R\$\s*[\d,\.]+', r'\d+\s*(mil|milhão|bilhão)',
            r'20(23|24|25)', r'\d+\s*(empresas|profissionais|clientes)'
        ]

        data_count = sum(1 for pattern in data_patterns if re.search(pattern, content))
        score += min(data_count * 3, 15)

        return min(score, 100.0)

    def _extract_content_insights(self, content: str, context: Dict[str, Any]) -> List[str]:
        """Extrai insights específicos do conteúdo"""

        insights = []
        sentences = [s.strip() for s in content.split('.') if len(s.strip()) > 80]

        # Padrões para insights valiosos
        insight_patterns = [
            r'crescimento de (\d+(?:\.\d+)?%)',
            r'mercado de R\$ ([\d,\.]+)',
            r'(\d+(?:\.\d+)?%) dos (\w+)',
            r'investimento de R\$ ([\d,\.]+)',
            r'(\d+) empresas (\w+)',
            r'tendência (?:de|para) (\w+)',
            r'oportunidade (?:de|em) (\w+)'
        ]

        segmento = context.get('segmento', '').lower()

        for sentence in sentences[:30]:
            sentence_lower = sentence.lower()

            # Verifica se contém termos relevantes
            if segmento and segmento in sentence_lower:
                # Verifica se contém dados numéricos ou informações valiosas
                if (re.search(r'\d+', sentence) or
                    any(term in sentence_lower for term in [
                        'crescimento', 'mercado', 'oportunidade', 'tendência',
                        'futuro', 'inovação', 'desafio', 'consumidor', 'empresa',
                        'startup', 'investimento', 'receita', 'lucro', 'dados'
                    ])):
                    insights.append(sentence[:300])

        return insights[:8]

    def _extract_internal_links(self, base_url: str, content: str) -> List[str]:
        """Extrai links internos relevantes"""

        try:
            # Tenta primeiro com verificação SSL
            response = self.session.get(base_url, timeout=10)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                base_domain = urlparse(base_url).netloc

                links = []
                for a_tag in soup.find_all('a', href=True):
                    href = a_tag['href']
                    full_url = urljoin(base_url, href)

                    # Filtra apenas links do mesmo domínio
                    if (full_url.startswith('http') and
                        base_domain in full_url and
                        "#" not in full_url and
                        full_url != base_url and
                        not any(ext in full_url.lower() for ext in ['.pdf', '.jpg', '.png', '.gif'])):
                        links.append(full_url)

                return list(set(links))[:10]
        except requests.exceptions.SSLError as ssl_error:
            logger.warning(f"⚠️ Erro SSL ao extrair links de {base_url}: {str(ssl_error)}")
            # Tenta novamente sem verificação SSL como fallback
            try:
                temp_session = requests.Session()
                temp_session.headers.update(self.headers)
                temp_session.verify = False
                import urllib3
                urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
                
                response = temp_session.get(base_url, timeout=10)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'html.parser')
                    base_domain = urlparse(base_url).netloc

                    links = []
                    for a_tag in soup.find_all('a', href=True):
                        href = a_tag['href']
                        full_url = urljoin(base_url, href)

                        if (full_url.startswith('http') and
                            base_domain in full_url and
                            "#" not in full_url and
                            full_url != base_url and
                            not any(ext in full_url.lower() for ext in ['.pdf', '.jpg', '.png', '.gif'])):
                            links.append(full_url)

                    logger.info(f"✅ Links extraídos sem SSL de {base_url}: {len(links)} links")
                    return list(set(links))[:10]
            except Exception as fallback_error:
                logger.error(f"❌ Erro no fallback SSL para {base_url}: {str(fallback_error)}")
                return []
        except Exception as e:
            logger.error(f"❌ Erro ao extrair links internos de {base_url}: {str(e)}")
            return []

        return []

    def _generate_intelligent_related_queries(
        self,
        original_query: str,
        context: Dict[str, Any],
        existing_content: List[Dict[str, Any]]
    ) -> List[str]:
        """Gera queries relacionadas inteligentes baseadas no conteúdo já coletado"""

        segmento = context.get('segmento', '')
        produto = context.get('produto', '')

        # Analisa conteúdo existente para identificar gaps
        all_text = ' '.join([item['content'] for item in existing_content])

        # Identifica termos frequentes
        words = re.findall(r'\b\w{4,}\b', all_text.lower())
        word_freq = {}
        for word in words:
            word_freq[word] = word_freq.get(word, 0) + 1

        # Pega termos mais frequentes relacionados ao segmento
        relevant_terms = [word for word, freq in sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:20]
                         if freq > 3 and word not in ['para', 'mais', 'como', 'sobre', 'brasil', 'anos']]

        # Gera queries relacionadas inteligentes
        related_queries = []

        if segmento:
            related_queries.extend([
                f"futuro {segmento} Brasil tendências 2025",
                f"desafios {segmento} mercado brasileiro soluções",
                f"inovações {segmento} tecnologia Brasil",
                f"regulamentação {segmento} mudanças Brasil",
                f"investimentos {segmento} startups Brasil"
            ])

        if produto:
            related_queries.extend([
                f"demanda {produto} Brasil estatísticas",
                f"concorrência {produto} mercado brasileiro",
                f"preços {produto} benchmarks Brasil"
            ])

        # Adiciona queries baseadas em termos frequentes
        for term in relevant_terms[:3]:
            related_queries.append(f"{term} {segmento} Brasil oportunidades")

        return related_queries[:8]

    def _process_and_analyze_content(
        self,
        all_content: List[Dict[str, Any]],
        query: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Processa e analisa todo o conteúdo coletado"""

        if not all_content:
            return self._generate_emergency_research(query, context)

        # Ordena por qualidade
        all_content.sort(key=lambda x: x['quality_score'], reverse=True)

        # Combina insights únicos
        all_insights = []
        for item in all_content:
            all_insights.extend(item.get('insights', []))

        # Remove duplicatas de insights
        unique_insights = list(dict.fromkeys(all_insights))

        # Analisa tendências
        trends = self._analyze_market_trends(all_content, context)

        # Identifica oportunidades
        opportunities = self._identify_market_opportunities(all_content, context)

        # Calcula métricas de qualidade
        total_chars = sum(item['content_length'] for item in all_content)
        avg_quality = sum(item['quality_score'] for item in all_content) / len(all_content)

        # Atualiza estatísticas globais
        self.navigation_stats['avg_quality_score'] = avg_quality

        return {
            "query_original": query,
            "context": context,
            "navegacao_profunda": {
                "total_paginas_analisadas": len(all_content),
                "engines_utilizados": list(set(item['search_engine'] for item in all_content)),
                "fontes_preferenciais": sum(1 for item in all_content if item.get('is_preferred_source')),
                "qualidade_media": round(avg_quality, 2),
                "total_caracteres": total_chars,
                "insights_unicos": len(unique_insights)
            },
            "conteudo_consolidado": {
                "insights_principais": unique_insights[:20],
                "tendencias_identificadas": trends,
                "oportunidades_descobertas": opportunities,
                "fontes_detalhadas": [
                    {
                        'url': item['url'],
                        'title': item['title'],
                        'quality_score': item['quality_score'],
                        'content_length': item['content_length'],
                        'search_engine': item['search_engine'],
                        'is_preferred': item.get('is_preferred_source', False)
                    } for item in all_content[:15]
                ]
            },
            "estatisticas_navegacao": self.navigation_stats,
            "metadata": {
                "navegacao_concluida_em": datetime.now().isoformat(),
                "agente": "Alibaba_WebSailor_v2.0",
                "garantia_dados_reais": True,
                "simulacao_free": True,
                "qualidade_premium": avg_quality >= 80
            }
        }

    def _analyze_market_trends(self, content_list: List[Dict[str, Any]], context: Dict[str, Any]) -> List[str]:
        """Analisa tendências de mercado do conteúdo"""

        trends = []
        all_text = ' '.join([item['content'] for item in content_list])

        # Padrões de tendências
        trend_keywords = [
            'inteligência artificial', 'ia', 'automação', 'digital',
            'sustentabilidade', 'personalização', 'mobile', 'cloud',
            'dados', 'analytics', 'experiência', 'inovação', 'telemedicina',
            'healthtech', 'fintech', 'edtech', 'blockchain', 'metaverso'
        ]

        for keyword in trend_keywords:
            if keyword in all_text.lower():
                # Busca contexto ao redor da palavra-chave
                pattern = rf'.{{0,150}}{re.escape(keyword)}.{{0,150}}'
                matches = re.findall(pattern, all_text.lower(), re.IGNORECASE)

                if matches:
                    trend_context = matches[0].strip()
                    if len(trend_context) > 80:
                        trends.append(f"Tendência: {trend_context[:200]}...")

        return trends[:8]

    def _identify_market_opportunities(self, content_list: List[Dict[str, Any]], context: Dict[str, Any]) -> List[str]:
        """Identifica oportunidades de mercado"""

        opportunities = []
        all_text = ' '.join([item['content'] for item in content_list])

        # Padrões de oportunidades
        opportunity_keywords = [
            'oportunidade', 'potencial', 'crescimento', 'expansão',
            'nicho', 'gap', 'lacuna', 'demanda não atendida',
            'mercado emergente', 'novo mercado', 'segmento inexplorado',
            'necessidade', 'carência', 'falta de'
        ]

        for keyword in opportunity_keywords:
            if keyword in all_text.lower():
                pattern = rf'.{{0,150}}{re.escape(keyword)}.{{0,150}}'
                matches = re.findall(pattern, all_text.lower(), re.IGNORECASE)

                if matches:
                    opp_context = matches[0].strip()
                    if len(opp_context) > 80:
                        opportunities.append(f"Oportunidade: {opp_context[:200]}...")

        return opportunities[:6]

    def _update_navigation_stats(self, content_list: List[Dict[str, Any]]):
        """Atualiza estatísticas de navegação"""

        if content_list:
            avg_quality = sum(item['quality_score'] for item in content_list) / len(content_list)
            self.navigation_stats['avg_quality_score'] = avg_quality

    def _generate_emergency_research(self, query: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Gera pesquisa de emergência quando navegação falha"""

        logger.warning("⚠️ Gerando pesquisa de emergência WebSailor")

        return {
            "query_original": query,
            "context": context,
            "navegacao_profunda": {
                "total_paginas_analisadas": 0,
                "engines_utilizados": [],
                "status": "emergencia",
                "message": "Navegação em modo de emergência - configure APIs para dados completos"
            },
            "conteudo_consolidado": {
                "insights_principais": [
                    f"Pesquisa emergencial para '{query}' - sistema em recuperação",
                    "Recomenda-se nova tentativa com configuração completa das APIs",
                    "WebSailor em modo de emergência - funcionalidade limitada"
                ],
                "tendencias_identificadas": [
                    "Sistema em modo de emergência - tendências limitadas"
                ],
                "oportunidades_descobertas": [
                    "Reconfigurar APIs para navegação completa"
                ]
            },
            "metadata": {
                "navegacao_concluida_em": datetime.now().isoformat(),
                "agente": "Alibaba_WebSailor_Emergency",
                "garantia_dados_reais": False,
                "modo_emergencia": True
            }
        }

    def get_navigation_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas de navegação"""
        return self.navigation_stats.copy()

    def reset_navigation_stats(self):
        """Reset estatísticas de navegação"""
        self.navigation_stats = {
            'total_searches': 0,
            'successful_extractions': 0,
            'failed_extractions': 0,
            'blocked_urls': 0,
            'preferred_sources': 0,
            'total_content_chars': 0,
            'avg_quality_score': 0.0
        }
        logger.info("🔄 Estatísticas de navegação resetadas")

# Instância global
alibaba_websailor = AlibabaWebSailorAgent()

def get_alibaba_websailor():
    """Retorna a instância global do Alibaba WebSailor Agent"""
    return alibaba_websailor