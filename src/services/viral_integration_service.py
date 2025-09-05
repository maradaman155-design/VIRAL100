# services/viral_integration_service.py

"""VIRAL IMAGE FINDER - ARQV30 Enhanced v3.0 OPTIMIZED
Módulo para buscar imagens virais no Google Imagens de Instagram/Facebook
Analisa engajamento, extrai links dos posts e salva dados estruturados
OTIMIZADO: Rotação inteligente de APIs, concorrência aprimorada, extração eficiente
"""
import os
import re
import json
import time
import asyncio
import logging
import ssl
from datetime import datetime
from typing import List, Dict, Optional, Tuple
from urllib.parse import urlparse, parse_qs, unquote, urljoin
from dataclasses import dataclass, asdict
import hashlib
import random

# Import condicional do Playwright
try:
    from playwright.async_api import async_playwright, Page, Browser, BrowserContext
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False
    logger = logging.getLogger(__name__)
    logger.warning("Playwright não encontrado. Instale com 'pip install playwright' para funcionalidades avançadas.")

# Imports assíncronos
try:
    import aiohttp
    import aiofiles
    HAS_ASYNC_DEPS = True
except ImportError:
    import requests
    HAS_ASYNC_DEPS = False
    logger = logging.getLogger(__name__)
    logger.warning("aiohttp/aiofiles não encontrados. Usando requests síncrono como fallback.")

# BeautifulSoup para parsing HTML
try:
    from bs4 import BeautifulSoup
    HAS_BS4 = True
except ImportError:
    HAS_BS4 = False
    logger = logging.getLogger(__name__)
    logger.warning("BeautifulSoup4 não encontrado.")

# Carregar variáveis de ambiente
from dotenv import load_dotenv
load_dotenv()

# Configuração de logging
logger = logging.getLogger(__name__)

@dataclass
class ViralImage:
    """Estrutura de dados para imagem viral"""
    image_url: str
    post_url: str
    platform: str
    title: str
    description: str
    engagement_score: float
    views_estimate: int
    likes_estimate: int
    comments_estimate: int
    shares_estimate: int
    author: str
    author_followers: int
    post_date: str
    hashtags: List[str]
    image_path: Optional[str] = None
    screenshot_path: Optional[str] = None
    extracted_at: str = datetime.now().isoformat()

class ViralImageFinder:
    """Classe principal para encontrar imagens virais - OTIMIZADA"""
    def __init__(self, config: Dict = None):
        self.config = config or self._load_config()

        # Sistema de rotação de APIs OTIMIZADO
        self.api_keys = self._load_multiple_api_keys()
        self.current_api_index = {
            'apify': 0,
            'openrouter': 0,
            'serper': 0,
            'serpapi': 0,
            'firecrawl': 0,
            'scrapingant': 0,
            'tavily': 0,
            'exa': 0,
            'jina': 0,
            'rapidapi': 0,
            'google_cse': 0,
            'phantombuster': 0
        }
        self.failed_apis = set()  # APIs que falharam recentemente
        self.api_performance = {}  # Tracking de performance das APIs

        self.instagram_session_cookie = self.config.get('instagram_session_cookie')
        self.playwright_enabled = self.config.get('playwright_enabled', True) and PLAYWRIGHT_AVAILABLE

        # Configurar diretórios necessários
        self._ensure_directories()

        # Configurar sessão HTTP síncrona para fallbacks
        if not HAS_ASYNC_DEPS:
            import requests
            self.session = requests.Session()
            self.setup_session()

    def _load_config(self) -> Dict:
        """Carrega configurações do ambiente"""
        return {
            'gemini_api_key': os.getenv('GEMINI_API_KEY'),
            'serper_api_key': os.getenv('SERPER_API_KEY'),
            'google_search_key': os.getenv('GOOGLE_SEARCH_KEY'),
            'google_cse_id': os.getenv('GOOGLE_CSE_ID'),
            'apify_api_key': os.getenv('APIFY_API_KEY'),
            'instagram_session_cookie': os.getenv('INSTAGRAM_SESSION_COOKIE'),
            'rapidapi_key': os.getenv('RAPIDAPI_KEY'),
            'max_images': int(os.getenv('MAX_IMAGES', 30)),
            'min_engagement': float(os.getenv('MIN_ENGAGEMENT', 10)),
            'timeout': int(os.getenv('TIMEOUT', 30)),
            'headless': os.getenv('PLAYWRIGHT_HEADLESS', 'True').lower() == 'true',
            'output_dir': os.getenv('OUTPUT_DIR', 'viral_images_data'),
            'images_dir': os.getenv('IMAGES_DIR', 'downloaded_images'),
            'extract_images': os.getenv('EXTRACT_IMAGES', 'True').lower() == 'true',
            'playwright_enabled': os.getenv('PLAYWRIGHT_ENABLED', 'True').lower() == 'true',
            'screenshots_dir': os.getenv('SCREENSHOTS_DIR', 'screenshots'),
            'playwright_timeout': int(os.getenv('PLAYWRIGHT_TIMEOUT', 45000)),
            'playwright_browser': os.getenv('PLAYWRIGHT_BROWSER', 'chromium'),
            'max_concurrent_requests': int(os.getenv('MAX_CONCURRENT_REQUESTS', 5)),
        }

    def _load_multiple_api_keys(self) -> Dict:
        """Carrega múltiplas chaves de API para rotação OTIMIZADA"""
        api_keys = {
            'apify': [],
            'openrouter': [],
            'serper': [],
            'serpapi': [],
            'firecrawl': [],
            'scrapingant': [],
            'tavily': [],
            'exa': [],
            'jina': [],
            'rapidapi': [],
            'google_cse': [],
            'phantombuster': []
        }

        # Apify - múltiplas chaves
        for i in range(1, 4):
            key = os.getenv(f'APIFY_API_KEY_{i}') or (os.getenv('APIFY_API_KEY') if i == 1 else None)
            if key and key.strip():
                api_keys['apify'].append(key.strip())
                logger.info(f"✅ Apify API {i} carregada")

        # OpenRouter - múltiplas chaves
        for i in range(1, 4):
            key = os.getenv(f'OPENROUTER_API_KEY_{i}') or (os.getenv('OPENROUTER_API_KEY') if i == 1 else None)
            if key and key.strip():
                api_keys['openrouter'].append(key.strip())
                logger.info(f"✅ OpenRouter API {i} carregada")

        # Serper - múltiplas chaves
        for i in range(1, 3):
            key = os.getenv(f'SERPER_API_KEY_{i}') or (os.getenv('SERPER_API_KEY') if i == 1 else None)
            if key and key.strip():
                api_keys['serper'].append(key.strip())
                logger.info(f"✅ Serper API {i} carregada")

        # SerpAPI - múltiplas chaves
        for i in range(1, 3):
            key = os.getenv(f'SERP_API_KEY_{i}') or (os.getenv('SERP_API_KEY') if i == 1 else None)
            if key and key.strip():
                api_keys['serpapi'].append(key.strip())
                logger.info(f"✅ SerpAPI API {i} carregada")

        # Firecrawl - múltiplas chaves
        for i in range(1, 3):
            key = os.getenv(f'FIRECRAWL_API_KEY_{i}') or (os.getenv('FIRECRAWL_API_KEY') if i == 1 else None)
            if key and key.strip():
                api_keys['firecrawl'].append(key.strip())
                logger.info(f"✅ Firecrawl API {i} carregada")

        # ScrapingAnt
        key = os.getenv('SCRAPINGANT_API_KEY')
        if key and key.strip():
            api_keys['scrapingant'].append(key.strip())
            logger.info("✅ ScrapingAnt API carregada")

        # Tavily
        key = os.getenv('TAVILY_API_KEY')
        if key and key.strip():
            api_keys['tavily'].append(key.strip())
            logger.info("✅ Tavily API carregada")

        # Exa
        for i in range(1, 3):
            key = os.getenv(f'EXA_API_KEY_{i}') or (os.getenv('EXA_API_KEY') if i == 1 else None)
            if key and key.strip():
                api_keys['exa'].append(key.strip())
                logger.info(f"✅ Exa API {i} carregada")

        # Jina
        for i in range(1, 3):
            key = os.getenv(f'JINA_API_KEY_{i}') or (os.getenv('JINA_API_KEY') if i == 1 else None)
            if key and key.strip():
                api_keys['jina'].append(key.strip())
                logger.info(f"✅ Jina API {i} carregada")

        # RapidAPI - múltiplas chaves
        for i in range(1, 3):
            key = os.getenv(f'RAPIDAPI_KEY_{i}') or (os.getenv('RAPIDAPI_KEY') if i == 1 else None)
            if key and key.strip():
                api_keys['rapidapi'].append(key.strip())
                logger.info(f"✅ RapidAPI {i} carregada")

        # PhantomBuster
        key = os.getenv('PHANTOMBUSTER_API_KEY')
        if key and key.strip():
            api_keys['phantombuster'].append(key.strip())
            logger.info("✅ PhantomBuster API carregada")

        # Google CSE
        google_key = os.getenv('GOOGLE_SEARCH_KEY')
        google_cse = os.getenv('GOOGLE_CSE_ID')
        if google_key and google_cse:
            api_keys['google_cse'].append({'key': google_key, 'cse_id': google_cse})
            logger.info(f"✅ Google CSE carregada")

        return api_keys

    def _get_next_api_key(self, service: str) -> Optional[str]:
        """Obtém próxima chave de API disponível com rotação inteligente OTIMIZADA"""
        if service not in self.api_keys or not self.api_keys[service]:
            return None

        keys = self.api_keys[service]
        if not keys:
            return None

        # Ordenar por performance se disponível
        if service in self.api_performance:
            sorted_indices = sorted(range(len(keys)), 
                                  key=lambda i: self.api_performance[service].get(i, 0), 
                                  reverse=True)
        else:
            sorted_indices = list(range(len(keys)))

        # Tentar todas as chaves disponíveis
        for i in sorted_indices:
            api_identifier = f"{service}_{i}"
            if api_identifier not in self.failed_apis:
                key = keys[i]
                logger.info(f"🔄 Usando {service} API #{i + 1} (performance: {self.api_performance.get(service, {}).get(i, 'N/A')})")
                
                # Atualizar índice atual
                self.current_api_index[service] = i
                return key

        logger.error(f"❌ Todas as APIs de {service} falharam recentemente")
        return None

    def _mark_api_failed(self, service: str, index: int):
        """Marca uma API como falhada temporariamente"""
        api_identifier = f"{service}_{index}"
        self.failed_apis.add(api_identifier)
        logger.warning(f"⚠️ API {service} #{index + 1} marcada como falhada")

        # Reduzir score de performance
        if service not in self.api_performance:
            self.api_performance[service] = {}
        self.api_performance[service][index] = self.api_performance[service].get(index, 0) - 1

        # Limpar falhas após 5 minutos (300 segundos)
        import threading
        def clear_failure():
            time.sleep(300)  # 5 minutos
            if api_identifier in self.failed_apis:
                self.failed_apis.remove(api_identifier)
                logger.info(f"✅ API {service} #{index + 1} reabilitada")

        threading.Thread(target=clear_failure, daemon=True).start()

    def _mark_api_success(self, service: str, index: int, response_time: float):
        """Marca uma API como bem-sucedida e atualiza performance"""
        if service not in self.api_performance:
            self.api_performance[service] = {}
        
        # Score baseado na velocidade de resposta (menor tempo = maior score)
        score = max(1, 10 - int(response_time))
        self.api_performance[service][index] = self.api_performance[service].get(index, 0) + score

    def _ensure_directories(self):
        """Garante que todos os diretórios necessários existam"""
        dirs_to_create = [
            self.config['output_dir'],
            self.config['images_dir'],
            self.config['screenshots_dir']
        ]

        for directory in dirs_to_create:
            try:
                os.makedirs(directory, exist_ok=True)
                logger.info(f"✅ Diretório criado/verificado: {directory}")
            except Exception as e:
                logger.error(f"❌ Erro ao criar diretório {directory}: {e}")

    def setup_session(self):
        """Configura sessão HTTP com headers apropriados"""
        if hasattr(self, 'session'):
            self.session.headers.update({
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'pt-BR,pt;q=0.9,en;q=0.8',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
            })

    async def search_images(self, query: str) -> List[Dict]:
        """Busca imagens usando múltiplos provedores com estratégia OTIMIZADA"""
        all_results = []

        # Funções de busca com priorização inteligente
        search_functions = [
            (self._search_serper_advanced, "serper"),
            (self._search_serpapi_advanced, "serpapi"),
            (self._search_google_cse_advanced, "google_cse"),
            (self._search_tavily_advanced, "tavily"),
            (self._search_exa_advanced, "exa"),
            (self._search_jina_advanced, "jina"),
            (self._search_firecrawl_advanced, "firecrawl"),
            (self._search_scrapingant_advanced, "scrapingant"),
            (self._search_rapidapi_instagram, "rapidapi"),
            (self._search_phantombuster_instagram, "phantombuster"),
        ]

        # Embaralhar a ordem para distribuir a carga entre as APIs
        random.shuffle(search_functions)

        # Executar buscas com concorrência limitada
        semaphore = asyncio.Semaphore(self.config['max_concurrent_requests'])
        
        async def execute_search(func, service_name):
            async with semaphore:
                if self.api_keys.get(service_name):
                    try:
                        start_time = time.time()
                        logger.info(f"🔍 Tentando buscar com {service_name} para: {query}")
                        
                        if service_name in ["rapidapi", "phantombuster"]:
                            results = await func(query)
                        else:
                            results = await func(query)
                        
                        response_time = time.time() - start_time
                        
                        if results:
                            # Marcar sucesso
                            current_index = self.current_api_index.get(service_name, 0)
                            self._mark_api_success(service_name, current_index, response_time)
                            logger.info(f"📊 {service_name} encontrou {len(results)} resultados em {response_time:.2f}s")
                        
                        return results
                    except Exception as e:
                        logger.error(f"❌ Erro na busca com {service_name} para '{query}': {e}")
                        return []
                    finally:
                        await asyncio.sleep(0.2)  # Rate limiting
                return []

        # Executar todas as buscas em paralelo
        tasks = [execute_search(func, service_name) for func, service_name in search_functions]
        search_results = await asyncio.gather(*tasks, return_exceptions=True)

        # Processar resultados
        for results in search_results:
            if isinstance(results, list):
                all_results.extend(results)
            elif isinstance(results, Exception):
                logger.error(f"❌ Erro na busca: {results}")

        # Remover duplicatas e filtrar URLs válidos
        seen_urls = set()
        unique_results = []

        for result in all_results:
            post_url = result.get('page_url', '').strip()
            if post_url and post_url not in seen_urls and self._is_valid_social_url(post_url):
                seen_urls.add(post_url)
                unique_results.append(result)

        logger.info(f"🎯 Encontrados {len(unique_results)} posts únicos e válidos")
        return unique_results[:self.config['max_images']]

    def _is_valid_social_url(self, url: str) -> bool:
        """Verifica se é uma URL válida de rede social"""
        valid_patterns = [
            r'instagram\.com/(p|reel)/',
            r'facebook\.com/.+/posts/',
            r'facebook\.com/.+/photos/',
            r'm\.facebook\.com/',
            r'youtube\.com/watch',
            r'instagram\.com/[^/]+/$'
        ]
        return any(re.search(pattern, url) for pattern in valid_patterns)

    async def _search_serper_advanced(self, query: str) -> List[Dict]:
        """Busca avançada usando Serper com rotação automática de APIs"""
        if not self.api_keys.get('serper'):
            return []

        results = []
        search_types = ['images', 'search']

        for search_type in search_types:
            url = f"https://google.serper.dev/{search_type}"
            payload = {
                "q": query,
                "num": 8,
                "safe": "off",
                "gl": "br",
                "hl": "pt-br"
            }

            if search_type == 'images':
                payload.update({
                    "imgSize": "large",
                    "imgType": "photo",
                    "imgColorType": "color"
                })

            api_key = self._get_next_api_key('serper')
            if not api_key:
                continue

            headers = {
                'X-API-KEY': api_key,
                'Content-Type': 'application/json'
            }

            try:
                if HAS_ASYNC_DEPS:
                    timeout = aiohttp.ClientTimeout(total=self.config['timeout'])
                    async with aiohttp.ClientSession(timeout=timeout) as session:
                        async with session.post(url, headers=headers, json=payload) as response:
                            response.raise_for_status()
                            data = await response.json()
                else:
                    response = self.session.post(url, headers=headers, json=payload, timeout=self.config['timeout'])
                    response.raise_for_status()
                    data = response.json()

                if search_type == 'images':
                    for item in data.get('images', []):
                        results.append({
                            'image_url': item.get('imageUrl', ''),
                            'page_url': item.get('link', ''),
                            'title': item.get('title', ''),
                            'description': item.get('snippet', ''),
                            'source': 'serper_images'
                        })
                else:
                    for item in data.get('organic', []):
                        results.append({
                            'image_url': '',
                            'page_url': item.get('link', ''),
                            'title': item.get('title', ''),
                            'description': item.get('snippet', ''),
                            'source': 'serper_search'
                        })

            except Exception as e:
                current_index = self.current_api_index.get('serper', 0)
                self._mark_api_failed('serper', current_index)
                logger.error(f"❌ Erro Serper API #{current_index + 1}: {e}")

        return results

    async def _search_serpapi_advanced(self, query: str) -> List[Dict]:
        """Busca avançada usando SerpAPI"""
        if not self.api_keys.get("serpapi"):
            return []

        results = []
        url = "https://serpapi.com/search"

        api_key = self._get_next_api_key("serpapi")
        if not api_key:
            return []

        params = {
            "api_key": api_key,
            "q": query,
            "engine": "google_images",
            "ijn": "0",
            "gl": "br",
            "hl": "pt-br"
        }

        try:
            if HAS_ASYNC_DEPS:
                timeout = aiohttp.ClientTimeout(total=self.config["timeout"])
                async with aiohttp.ClientSession(timeout=timeout) as session:
                    async with session.get(url, params=params) as response:
                        response.raise_for_status()
                        data = await response.json()
            else:
                response = self.session.get(url, params=params, timeout=self.config["timeout"])
                response.raise_for_status()
                data = response.json()

            for item in data.get("images_results", []):
                results.append({
                    "image_url": item.get("original", item.get("thumbnail", "")),
                    "page_url": item.get("link", ""),
                    "title": item.get("title", ""),
                    "description": item.get("snippet", ""),
                    "source": "serpapi"
                })

        except Exception as e:
            current_index = self.current_api_index.get("serpapi", 0)
            self._mark_api_failed("serpapi", current_index)
            logger.error(f"❌ Erro SerpAPI: {e}")

        return results

    async def _search_google_cse_advanced(self, query: str) -> List[Dict]:
        """Busca aprimorada usando Google CSE"""
        if not self.config.get('google_search_key') or not self.config.get('google_cse_id'):
            return []
        
        url = "https://www.googleapis.com/customsearch/v1"
        params = {
            'key': self.config['google_search_key'],
            'cx': self.config['google_cse_id'],
            'q': query,
            'searchType': 'image',
            'num': 6,
            'safe': 'off',
            'fileType': 'jpg,png,jpeg,webp',
            'imgSize': 'large',
            'imgType': 'photo',
            'gl': 'br',
            'hl': 'pt'
        }

        try:
            if HAS_ASYNC_DEPS:
                timeout = aiohttp.ClientTimeout(total=self.config['timeout'])
                async with aiohttp.ClientSession(timeout=timeout) as session:
                    async with session.get(url, params=params) as response:
                        response.raise_for_status()
                        data = await response.json()
            else:
                response = self.session.get(url, params=params, timeout=self.config['timeout'])
                response.raise_for_status()
                data = response.json()

            results = []
            for item in data.get('items', []):
                results.append({
                    'image_url': item.get('link', ''),
                    'page_url': item.get('image', {}).get('contextLink', ''),
                    'title': item.get('title', ''),
                    'description': item.get('snippet', ''),
                    'source': 'google_cse'
                })
            return results

        except Exception as e:
            logger.error(f"❌ Erro na busca Google CSE: {e}")
            return []

    async def _search_tavily_advanced(self, query: str) -> List[Dict]:
        """Busca avançada usando Tavily"""
        if not self.api_keys.get("tavily"):
            return []

        results = []
        url = "https://api.tavily.com/search"

        api_key = self._get_next_api_key("tavily")
        if not api_key:
            return []

        payload = {
            "api_key": api_key,
            "query": query,
            "search_depth": "advanced",
            "include_images": True,
            "include_answer": False,
            "max_results": 8
        }

        try:
            if HAS_ASYNC_DEPS:
                timeout = aiohttp.ClientTimeout(total=self.config["timeout"])
                async with aiohttp.ClientSession(timeout=timeout) as session:
                    async with session.post(url, json=payload) as response:
                        response.raise_for_status()
                        data = await response.json()
            else:
                response = self.session.post(url, json=payload, timeout=self.config["timeout"])
                response.raise_for_status()
                data = response.json()

            for item in data.get("results", []):
                if item.get("url"):
                    results.append({
                        "image_url": item.get("thumbnail", ""),
                        "page_url": item.get("url"),
                        "title": item.get("title", ""),
                        "description": item.get("content", ""),
                        "source": "tavily"
                    })

        except Exception as e:
            current_index = self.current_api_index.get("tavily", 0)
            self._mark_api_failed("tavily", current_index)
            logger.error(f"❌ Erro Tavily: {e}")

        return results

    async def _search_exa_advanced(self, query: str) -> List[Dict]:
        """Busca avançada usando Exa"""
        if not self.api_keys.get("exa"):
            return []

        results = []
        url = "https://api.exa.ai/search"

        api_key = self._get_next_api_key("exa")
        if not api_key:
            return []

        headers = {"x-api-key": api_key, "Content-Type": "application/json"}
        payload = {
            "query": query,
            "num_results": 8,
            "type": "neural",
            "start_published_date": "2023-01-01"
        }

        try:
            if HAS_ASYNC_DEPS:
                timeout = aiohttp.ClientTimeout(total=self.config["timeout"])
                async with aiohttp.ClientSession(timeout=timeout) as session:
                    async with session.post(url, headers=headers, json=payload) as response:
                        response.raise_for_status()
                        data = await response.json()
            else:
                response = self.session.post(url, headers=headers, json=payload, timeout=self.config["timeout"])
                response.raise_for_status()
                data = response.json()

            for item in data.get("results", []):
                if item.get("url"):
                    results.append({
                        "image_url": "",
                        "page_url": item.get("url"),
                        "title": item.get("title", ""),
                        "description": item.get("text", ""),
                        "source": "exa"
                    })

        except Exception as e:
            current_index = self.current_api_index.get("exa", 0)
            self._mark_api_failed("exa", current_index)
            logger.error(f"❌ Erro Exa: {e}")

        return results

    async def _search_jina_advanced(self, query: str) -> List[Dict]:
        """Busca avançada usando Jina"""
        if not self.api_keys.get("jina"):
            return []

        results = []
        url = "https://s.jina.ai/"

        api_key = self._get_next_api_key("jina")
        if not api_key:
            return []

        headers = {"Authorization": f"Bearer {api_key}"}
        search_url = f"{url}{query}"

        try:
            if HAS_ASYNC_DEPS:
                timeout = aiohttp.ClientTimeout(total=self.config["timeout"])
                async with aiohttp.ClientSession(timeout=timeout) as session:
                    async with session.get(search_url, headers=headers) as response:
                        response.raise_for_status()
                        content = await response.text()
            else:
                response = self.session.get(search_url, headers=headers, timeout=self.config["timeout"])
                response.raise_for_status()
                content = response.text

            # Parse do conteúdo retornado pelo Jina (formato específico)
            if content and len(content) > 100:
                results.append({
                    "image_url": "",
                    "page_url": search_url,
                    "title": f"Jina Search: {query}",
                    "description": content[:200],
                    "source": "jina"
                })

        except Exception as e:
            current_index = self.current_api_index.get("jina", 0)
            self._mark_api_failed("jina", current_index)
            logger.error(f"❌ Erro Jina: {e}")

        return results

    async def _search_firecrawl_advanced(self, query: str) -> List[Dict]:
        """Busca avançada usando Firecrawl"""
        if not self.api_keys.get("firecrawl"):
            return []

        results = []
        url = "https://api.firecrawl.dev/v0/search"

        api_key = self._get_next_api_key("firecrawl")
        if not api_key:
            return []

        headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
        payload = {
            "query": query,
            "pageOptions": {"includeHtml": False},
            "limit": 8
        }

        try:
            if HAS_ASYNC_DEPS:
                timeout = aiohttp.ClientTimeout(total=self.config["timeout"])
                async with aiohttp.ClientSession(timeout=timeout) as session:
                    async with session.post(url, headers=headers, json=payload) as response:
                        response.raise_for_status()
                        data = await response.json()
            else:
                response = self.session.post(url, headers=headers, json=payload, timeout=self.config["timeout"])
                response.raise_for_status()
                data = response.json()

            for item in data.get("data", []):
                if item.get("sourceURL"):
                    results.append({
                        "image_url": "",
                        "page_url": item.get("sourceURL"),
                        "title": item.get("metadata", {}).get("title", ""),
                        "description": item.get("content", "")[:200],
                        "source": "firecrawl"
                    })

        except Exception as e:
            current_index = self.current_api_index.get("firecrawl", 0)
            self._mark_api_failed("firecrawl", current_index)
            logger.error(f"❌ Erro Firecrawl: {e}")

        return results

    async def _search_scrapingant_advanced(self, query: str) -> List[Dict]:
        """Busca avançada usando ScrapingAnt"""
        if not self.api_keys.get("scrapingant"):
            return []

        results = []
        url = "https://api.scrapingant.com/v2/general"

        api_key = self._get_next_api_key("scrapingant")
        if not api_key:
            return []

        params = {
            "url": f"https://www.google.com/search?q={query}&tbm=isch",
            "x-api-key": api_key,
            "return_page_source": True
        }

        try:
            if HAS_ASYNC_DEPS:
                timeout = aiohttp.ClientTimeout(total=self.config["timeout"])
                async with aiohttp.ClientSession(timeout=timeout) as session:
                    async with session.get(url, params=params) as response:
                        response.raise_for_status()
                        data = await response.json()
            else:
                response = self.session.get(url, params=params, timeout=self.config["timeout"])
                response.raise_for_status()
                data = response.json()

            if data and data.get("content") and HAS_BS4:
                soup = BeautifulSoup(data["content"], "html.parser")
                for img in soup.find_all("img")[:8]:
                    img_url = img.get("src")
                    if img_url and img_url.startswith("http"):
                        results.append({
                            "image_url": img_url,
                            "page_url": f"https://www.google.com/search?q={query}",
                            "title": img.get("alt", ""),
                            "description": img.get("alt", ""),
                            "source": "scrapingant"
                        })

        except Exception as e:
            current_index = self.current_api_index.get("scrapingant", 0)
            self._mark_api_failed("scrapingant", current_index)
            logger.error(f"❌ Erro ScrapingAnt: {e}")

        return results

    async def _search_rapidapi_instagram(self, query: str) -> List[Dict]:
        """Busca posts do Instagram via RapidAPI"""
        if not self.api_keys.get('rapidapi'):
            return []

        url = "https://instagram-scraper-api2.p.rapidapi.com/v1/hashtag"
        params = {"hashtag": query.replace(' ', ''), "count": "12"}

        api_key = self._get_next_api_key('rapidapi')
        if not api_key:
            return []

        headers = {
            "X-RapidAPI-Key": api_key,
            "X-RapidAPI-Host": "instagram-scraper-api2.p.rapidapi.com"
        }

        try:
            if HAS_ASYNC_DEPS:
                timeout = aiohttp.ClientTimeout(total=30)
                async with aiohttp.ClientSession(timeout=timeout) as session:
                    async with session.get(url, headers=headers, params=params) as response:
                        if response.status == 200:
                            data = await response.json()
                            results = []
                            for item in data.get('data', {}).get('recent', {}).get('sections', []):
                                for media in item.get('layout_content', {}).get('medias', []):
                                    media_info = media.get('media', {})
                                    if media_info:
                                        results.append({
                                            'image_url': media_info.get('image_versions2', {}).get('candidates', [{}])[0].get('url', ''),
                                            'page_url': f"https://www.instagram.com/p/{media_info.get('code', '')}/",
                                            'title': f"Post do Instagram por @{media_info.get('user', {}).get('username', 'unknown')}",
                                            'description': media_info.get('caption', {}).get('text', '')[:200],
                                            'source': 'rapidapi_instagram'
                                        })
                            return results
            return []

        except Exception as e:
            current_index = self.current_api_index.get('rapidapi', 0)
            self._mark_api_failed('rapidapi', current_index)
            logger.error(f"❌ Erro RapidAPI: {e}")
            return []

    async def _search_phantombuster_instagram(self, query: str) -> List[Dict]:
        """Busca posts do Instagram usando PhantomBuster (simulado)"""
        # PhantomBuster requer configuração específica de Phantoms
        # Esta é uma implementação simulada
        logger.info(f"PhantomBuster search simulado para: {query}")
        return []

    async def analyze_post_engagement(self, post_url: str, platform: str) -> Dict:
        """Analisa engajamento com estratégia OTIMIZADA"""
        
        # Para Instagram, tentar Apify primeiro
        if platform == 'instagram' and ('/p/' in post_url or '/reel/' in post_url):
            try:
                apify_data = await self._analyze_with_apify_rotation(post_url)
                if apify_data:
                    logger.info(f"✅ Dados obtidos via Apify para {post_url}")
                    return apify_data
            except Exception as e:
                logger.warning(f"⚠️ Apify falhou para {post_url}: {e}")

        # Playwright como fallback robusto
        if self.playwright_enabled:
            try:
                engagement_data = await self._analyze_with_playwright_optimized(post_url, platform)
                if engagement_data:
                    logger.info(f"✅ Engajamento obtido via Playwright para {post_url}")
                    return engagement_data
            except Exception as e:
                logger.error(f"❌ Erro no Playwright para {post_url}: {e}")

        # Último fallback: estimativa inteligente
        logger.info(f"📊 Usando estimativa inteligente para: {post_url}")
        return await self._estimate_engagement_optimized(post_url, platform)

    async def _analyze_with_apify_rotation(self, post_url: str) -> Optional[Dict]:
        """Analisa post do Instagram com Apify usando rotação automática"""
        if not self.api_keys.get('apify'):
            return None

        shortcode_match = re.search(r'/(?:p|reel)/([A-Za-z0-9_-]+)/', post_url)
        if not shortcode_match:
            return None

        shortcode = shortcode_match.group(1)
        api_key = self._get_next_api_key('apify')
        if not api_key:
            return None

        apify_url = f"https://api.apify.com/v2/acts/apify~instagram-post-scraper/run-sync-get-dataset-items"
        params = {
            'token': api_key,
            'directUrls': f'["https://www.instagram.com/p/{shortcode}/"]',
            'resultsLimit': 1
        }

        try:
            if HAS_ASYNC_DEPS:
                timeout = aiohttp.ClientTimeout(total=30)
                async with aiohttp.ClientSession(timeout=timeout) as session:
                    async with session.get(apify_url, params=params) as response:
                        if response.status == 200:
                            data = await response.json()
                            if data and len(data) > 0:
                                post_data = data[0]
                                return {
                                    'engagement_score': self._calculate_engagement_score_optimized(
                                        post_data.get('likesCount', 0),
                                        post_data.get('commentsCount', 0),
                                        0,  # shares
                                        post_data.get('videoViewCount', 0) or post_data.get('likesCount', 0) * 10,
                                        post_data.get('ownerFollowersCount', 1000)
                                    ),
                                    'views_estimate': post_data.get('videoViewCount', 0) or post_data.get('likesCount', 0) * 10,
                                    'likes_estimate': post_data.get('likesCount', 0),
                                    'comments_estimate': post_data.get('commentsCount', 0),
                                    'shares_estimate': post_data.get('commentsCount', 0) // 2,
                                    'author': post_data.get('ownerUsername', ''),
                                    'author_followers': post_data.get('ownerFollowersCount', 0),
                                    'post_date': post_data.get('timestamp', ''),
                                    'hashtags': [tag.get('name', '') for tag in post_data.get('hashtags', [])]
                                }
        except Exception as e:
            current_index = self.current_api_index.get('apify', 0)
            self._mark_api_failed('apify', current_index)
            logger.error(f"❌ Erro Apify: {e}")

        return None

    async def _analyze_with_playwright_optimized(self, post_url: str, platform: str) -> Optional[Dict]:
        """Análise otimizada com Playwright"""
        if not self.playwright_enabled:
            return None

        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(
                    headless=self.config['headless'],
                    args=['--no-sandbox', '--disable-setuid-sandbox', '--disable-web-security']
                )

                context = await browser.new_context(
                    user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                    viewport={'width': 1920, 'height': 1080}
                )

                page = await context.new_page()
                page.set_default_timeout(self.config['playwright_timeout'])

                await page.goto(post_url, wait_until='domcontentloaded')
                await asyncio.sleep(2)

                # Fechar popups comuns
                await self._close_common_popups_optimized(page, platform)

                # Extrair dados baseado na plataforma
                engagement_data = await self._extract_engagement_data_optimized(page, platform)
                
                await browser.close()
                return engagement_data

        except Exception as e:
            logger.error(f"❌ Erro no Playwright otimizado: {e}")
            return None

    async def _close_common_popups_optimized(self, page: Page, platform: str):
        """Fecha popups comuns de forma otimizada"""
        popup_selectors = {
            'instagram': [
                'button:has-text("Agora não")',
                'button:has-text("Not Now")',
                '[aria-label="Fechar"]',
                '[aria-label="Close"]'
            ],
            'facebook': [
                '[aria-label="Fechar"]',
                '[aria-label="Close"]',
                'div[role="button"]:has-text("×")'
            ]
        }

        selectors = popup_selectors.get(platform, [])
        for selector in selectors:
            try:
                await page.click(selector, timeout=2000)
                await asyncio.sleep(0.5)
            except:
                continue

    async def _extract_engagement_data_optimized(self, page: Page, platform: str) -> Dict:
        """Extrai dados de engajamento de forma otimizada"""
        likes = comments = shares = views = followers = 0
        author = post_date = ''
        hashtags = []

        try:
            if platform == 'instagram':
                # Extrair métricas do Instagram
                page_text = await page.inner_text('body')
                
                # Usar regex otimizado para extrair números
                likes = self._extract_number_optimized(page_text, [r'(\d+(?:\.\d+)?[KMB]?)\s*curtidas?', r'(\d+(?:\.\d+)?[KMB]?)\s*likes?'])
                comments = self._extract_number_optimized(page_text, [r'Ver todos os (\d+(?:\.\d+)?[KMB]?)\s*comentários', r'(\d+(?:\.\d+)?[KMB]?)\s*comments?'])
                
                # Extrair hashtags
                hashtags = re.findall(r'#(\w+)', page_text)[:10]

            elif platform == 'facebook':
                page_text = await page.inner_text('body')
                
                likes = self._extract_number_optimized(page_text, [r'(\d+(?:\.\d+)?[KMB]?)\s*curtidas?', r'(\d+(?:\.\d+)?[KMB]?)\s*reações?'])
                comments = self._extract_number_optimized(page_text, [r'(\d+(?:\.\d+)?[KMB]?)\s*comentários?'])
                shares = self._extract_number_optimized(page_text, [r'(\d+(?:\.\d+)?[KMB]?)\s*compartilhamentos?'])

        except Exception as e:
            logger.debug(f"Erro na extração otimizada: {e}")

        # Calcular score de engajamento otimizado
        engagement_score = self._calculate_engagement_score_optimized(likes, comments, shares, views, followers or 1000)

        return {
            'engagement_score': engagement_score,
            'views_estimate': views or likes * 15,
            'likes_estimate': likes,
            'comments_estimate': comments,
            'shares_estimate': shares,
            'author': author,
            'author_followers': followers or 1000,
            'post_date': post_date,
            'hashtags': hashtags
        }

    def _extract_number_optimized(self, text: str, patterns: List[str]) -> int:
        """Extrai números de texto usando múltiplos padrões otimizados"""
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                number_str = matches[0]
                return self._convert_number_string_optimized(number_str)
        return 0

    def _convert_number_string_optimized(self, number_str: str) -> int:
        """Converte string de número com abreviações para inteiro"""
        if not number_str:
            return 0
        
        number_str = number_str.lower().replace(',', '.').replace(' ', '')
        
        multipliers = {'k': 1000, 'm': 1000000, 'b': 1000000000, 'mil': 1000, 'mi': 1000000}
        
        for suffix, multiplier in multipliers.items():
            if number_str.endswith(suffix):
                try:
                    return int(float(number_str[:-len(suffix)]) * multiplier)
                except ValueError:
                    continue
        
        try:
            return int(float(number_str))
        except ValueError:
            return 0

    def _calculate_engagement_score_optimized(self, likes: int, comments: int, shares: int, views: int, followers: int) -> float:
        """Calcula score de engajamento com algoritmo OTIMIZADO"""
        # Pesos otimizados baseados em importância
        weighted_interactions = likes + (comments * 8) + (shares * 15)
        
        if views > 0:
            engagement_rate = (weighted_interactions / max(views, 1)) * 100
        elif followers > 0:
            engagement_rate = (weighted_interactions / max(followers, 1)) * 100
        else:
            engagement_rate = float(weighted_interactions * 0.1)

        # Bonus para alto engajamento
        if weighted_interactions > 500:
            engagement_rate *= 1.5
        elif weighted_interactions > 100:
            engagement_rate *= 1.2

        # Bonus para conteúdo educacional (baseado em padrões)
        if comments > likes * 0.1:  # Alto ratio de comentários indica engajamento
            engagement_rate *= 1.3

        return round(max(engagement_rate, float(weighted_interactions * 0.05)), 2)

    async def _estimate_engagement_optimized(self, post_url: str, platform: str) -> Dict:
        """Estimativa inteligente e otimizada baseada na plataforma"""
        base_scores = {
            'instagram': 35.0,
            'facebook': 25.0,
            'youtube': 50.0,
            'tiktok': 45.0
        }

        base_score = base_scores.get(platform, 30.0)

        # Bonus baseado no tipo de conteúdo
        if '/reel/' in post_url:
            base_score += 15.0  # Reels têm mais engajamento
        elif '/photos/' in post_url:
            base_score += 8.0   # Fotos têm bom engajamento

        multipliers = {
            'instagram': 20,
            'facebook': 12,
            'youtube': 40,
            'tiktok': 35
        }

        multiplier = multipliers.get(platform, 15)

        return {
            'engagement_score': base_score,
            'views_estimate': int(base_score * multiplier),
            'likes_estimate': int(base_score * 1.8),
            'comments_estimate': int(base_score * 0.25),
            'shares_estimate': int(base_score * 0.4),
            'author': 'Perfil Educacional',
            'author_followers': 3000,
            'post_date': '',
            'hashtags': []
        }

    async def find_viral_images(self, query: str) -> Tuple[List[ViralImage], str]:
        """Função principal OTIMIZADA para encontrar conteúdo viral"""
        logger.info(f"🔥 BUSCA VIRAL OTIMIZADA INICIADA: {query}")

        # Buscar resultados
        search_results = await self.search_images(query)

        if not search_results:
            logger.warning("⚠️ Nenhum resultado encontrado na busca")
            return [], ""

        # Processar resultados com paralelização otimizada
        viral_images = []
        semaphore = asyncio.Semaphore(self.config['max_concurrent_requests'])

        async def process_result_optimized(i: int, result: Dict) -> Optional[ViralImage]:
            async with semaphore:
                try:
                    logger.info(f"📊 Processando {i+1}/{len(search_results[:self.config['max_images']])}: {result.get('page_url', '')}")

                    page_url = result.get('page_url', '')
                    if not page_url:
                        return None

                    platform = self._determine_platform(page_url)
                    engagement = await self.analyze_post_engagement(page_url, platform)

                    # Processar imagem de forma otimizada
                    image_path = None
                    screenshot_path = None
                    image_url = result.get('image_url', '')

                    if self.config.get('extract_images', True) and image_url:
                        try:
                            extracted_path = await self._download_image_optimized(image_url, page_url)
                            if extracted_path:
                                image_path = extracted_path
                        except Exception as e:
                            logger.debug(f"Erro no download da imagem: {e}")

                    viral_image = ViralImage(
                        image_url=image_url,
                        post_url=page_url,
                        platform=platform,
                        title=result.get('title', ''),
                        description=result.get('description', ''),
                        engagement_score=engagement.get('engagement_score', 0.0),
                        views_estimate=engagement.get('views_estimate', 0),
                        likes_estimate=engagement.get('likes_estimate', 0),
                        comments_estimate=engagement.get('comments_estimate', 0),
                        shares_estimate=engagement.get('shares_estimate', 0),
                        author=engagement.get('author', ''),
                        author_followers=engagement.get('author_followers', 0),
                        post_date=engagement.get('post_date', ''),
                        hashtags=engagement.get('hashtags', []),
                        image_path=image_path,
                        screenshot_path=screenshot_path
                    )

                    if viral_image.engagement_score >= self.config['min_engagement']:
                        logger.info(f"✅ CONTEÚDO VIRAL: {viral_image.title} - Score: {viral_image.engagement_score}")
                    
                    return viral_image

                except Exception as e:
                    logger.error(f"❌ Erro ao processar {result.get('page_url', '')}: {e}")
                    return None

        # Executar processamento otimizado
        tasks = [process_result_optimized(i, result) for i, result in enumerate(search_results[:self.config['max_images']])]
        processed_results = await asyncio.gather(*tasks, return_exceptions=True)

        # Filtrar e ordenar resultados
        for result in processed_results:
            if isinstance(result, ViralImage):
                viral_images.append(result)

        # Ordenar por score de engajamento
        viral_images.sort(key=lambda x: x.engagement_score, reverse=True)

        # Salvar resultados
        output_file = self.save_results_optimized(viral_images, query)

        logger.info(f"🎯 BUSCA OTIMIZADA CONCLUÍDA! {len(viral_images)} conteúdos encontrados")
        logger.info(f"📊 TOP 3 SCORES: {[img.engagement_score for img in viral_images[:3]]}")

        return viral_images, output_file

    async def _download_image_optimized(self, image_url: str, post_url: str) -> Optional[str]:
        """Download otimizado de imagem"""
        if not image_url:
            return None

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'image/webp,image/apng,image/*,*/*;q=0.8',
            'Referer': post_url
        }

        try:
            if HAS_ASYNC_DEPS:
                ssl_context = ssl.create_default_context()
                ssl_context.check_hostname = False
                ssl_context.verify_mode = ssl.CERT_NONE

                connector = aiohttp.TCPConnector(ssl=ssl_context)
                timeout = aiohttp.ClientTimeout(total=self.config['timeout'])

                async with aiohttp.ClientSession(connector=connector, timeout=timeout, headers=headers) as session:
                    async with session.get(image_url) as response:
                        if response.status == 200:
                            content_type = response.headers.get('content-type', '').lower()
                            if 'image' in content_type:
                                content = await response.read()
                                if len(content) > 1024:  # Mínimo 1KB
                                    filename = self._generate_filename_optimized(image_url, content_type)
                                    filepath = os.path.join(self.config['images_dir'], filename)
                                    
                                    async with aiofiles.open(filepath, 'wb') as f:
                                        await f.write(content)
                                    
                                    return filepath
        except Exception as e:
            logger.debug(f"Erro no download otimizado: {e}")

        return None

    def _generate_filename_optimized(self, url: str, content_type: str) -> str:
        """Gera nome de arquivo otimizado"""
        ext_map = {
            'image/jpeg': 'jpg',
            'image/jpg': 'jpg',
            'image/png': 'png',
            'image/webp': 'webp',
            'image/gif': 'gif'
        }
        
        ext = ext_map.get(content_type, 'jpg')
        hash_name = hashlib.md5(url.encode()).hexdigest()[:12]
        timestamp = int(time.time())
        
        return f"viral_{hash_name}_{timestamp}.{ext}"

    def _determine_platform(self, url: str) -> str:
        """Determina a plataforma baseada na URL"""
        if 'instagram.com' in url:
            return 'instagram'
        elif 'facebook.com' in url or 'm.facebook.com' in url:
            return 'facebook'
        elif 'youtube.com' in url or 'youtu.be' in url:
            return 'youtube'
        elif 'tiktok.com' in url:
            return 'tiktok'
        else:
            return 'web'

    def save_results_optimized(self, viral_images: List[ViralImage], query: str) -> str:
        """Salva resultados com dados enriquecidos OTIMIZADO"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_query = re.sub(r'[^\w\s-]', '', query).strip().replace(' ', '_')[:30]
        filename = f"viral_results_OPTIMIZED_{safe_query}_{timestamp}.json"
        filepath = os.path.join(self.config['output_dir'], filename)

        try:
            images_data = [asdict(img) for img in viral_images]
            
            # Métricas agregadas otimizadas
            total_engagement = sum(img.engagement_score for img in viral_images)
            avg_engagement = total_engagement / len(viral_images) if viral_images else 0
            
            # Estatísticas por plataforma
            platform_stats = {}
            for img in viral_images:
                platform = img.platform
                if platform not in platform_stats:
                    platform_stats[platform] = {
                        'count': 0,
                        'total_engagement': 0,
                        'avg_engagement': 0,
                        'total_views': 0,
                        'total_likes': 0
                    }
                
                platform_stats[platform]['count'] += 1
                platform_stats[platform]['total_engagement'] += img.engagement_score
                platform_stats[platform]['total_views'] += img.views_estimate
                platform_stats[platform]['total_likes'] += img.likes_estimate
            
            # Calcular médias
            for platform in platform_stats:
                count = platform_stats[platform]['count']
                if count > 0:
                    platform_stats[platform]['avg_engagement'] = round(
                        platform_stats[platform]['total_engagement'] / count, 2
                    )

            # Performance das APIs
            api_performance_summary = {}
            for service, performance in self.api_performance.items():
                if performance:
                    api_performance_summary[service] = {
                        'total_calls': sum(performance.values()),
                        'avg_performance': round(sum(performance.values()) / len(performance), 2),
                        'best_api_index': max(performance, key=performance.get)
                    }

            data = {
                'query': query,
                'extracted_at': datetime.now().isoformat(),
                'optimization_version': 'v3.0_OPTIMIZED',
                'total_content': len(viral_images),
                'viral_content': len([img for img in viral_images if img.engagement_score >= self.config['min_engagement']]),
                'images_downloaded': len([img for img in viral_images if img.image_path]),
                'screenshots_taken': len([img for img in viral_images if img.screenshot_path]),
                'metrics': {
                    'total_engagement_score': round(total_engagement, 2),
                    'average_engagement': round(avg_engagement, 2),
                    'highest_engagement': max((img.engagement_score for img in viral_images), default=0),
                    'total_estimated_views': sum(img.views_estimate for img in viral_images),
                    'total_estimated_likes': sum(img.likes_estimate for img in viral_images),
                    'engagement_distribution': {
                        'high': len([img for img in viral_images if img.engagement_score >= 50]),
                        'medium': len([img for img in viral_images if 20 <= img.engagement_score < 50]),
                        'low': len([img for img in viral_images if img.engagement_score < 20])
                    }
                },
                'platform_distribution': platform_stats,
                'api_performance': api_performance_summary,
                'top_performers': [asdict(img) for img in viral_images[:5]],
                'all_content': images_data,
                'config_used': {
                    'max_images': self.config['max_images'],
                    'min_engagement': self.config['min_engagement'],
                    'max_concurrent_requests': self.config['max_concurrent_requests'],
                    'extract_images': self.config['extract_images'],
                    'playwright_enabled': self.playwright_enabled
                },
                'api_status': {
                    'total_apis_available': sum(1 for apis in self.api_keys.values() if apis),
                    'serper_available': bool(self.api_keys.get('serper')),
                    'serpapi_available': bool(self.api_keys.get('serpapi')),
                    'google_cse_available': bool(self.api_keys.get('google_cse')),
                    'tavily_available': bool(self.api_keys.get('tavily')),
                    'exa_available': bool(self.api_keys.get('exa')),
                    'jina_available': bool(self.api_keys.get('jina')),
                    'firecrawl_available': bool(self.api_keys.get('firecrawl')),
                    'scrapingant_available': bool(self.api_keys.get('scrapingant')),
                    'rapidapi_available': bool(self.api_keys.get('rapidapi')),
                    'apify_available': bool(self.api_keys.get('apify')),
                    'phantombuster_available': bool(self.api_keys.get('phantombuster'))
                }
            }

            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

            logger.info(f"💾 Resultados OTIMIZADOS salvos: {filepath}")
            return filepath

        except Exception as e:
            logger.error(f"❌ Erro ao salvar resultados otimizados: {e}")
            return ""

# Instância global otimizada
viral_integration_service = ViralImageFinder()

# Funções wrapper para compatibilidade
async def find_viral_images(query: str) -> Tuple[List[ViralImage], str]:
    """Função wrapper assíncrona OTIMIZADA"""
    return await viral_integration_service.find_viral_images(query)

def find_viral_images_sync(query: str) -> Tuple[List[ViralImage], str]:
    """Função wrapper síncrona com tratamento de loop OTIMIZADO"""
    try:
        try:
            loop = asyncio.get_running_loop()
            import concurrent.futures
            
            def run_async_in_thread():
                new_loop = asyncio.new_event_loop()
                asyncio.set_event_loop(new_loop)
                try:
                    return new_loop.run_until_complete(
                        viral_integration_service.find_viral_images(query)
                    )
                finally:
                    new_loop.close()

            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(run_async_in_thread)
                return future.result(timeout=600)  # 10 minutos timeout

        except RuntimeError:
            return asyncio.run(viral_integration_service.find_viral_images(query))

    except Exception as e:
        logger.error(f"❌ ERRO CRÍTICO na busca viral otimizada: {e}")
        empty_result_file = viral_integration_service.save_results_optimized([], query)
        return [], empty_result_file

logger.info("🔥 Viral Integration Service OTIMIZADO v3.0 inicializado com sucesso!")

