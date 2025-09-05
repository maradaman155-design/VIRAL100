"""VIRAL IMAGE FINDER - ARQV30 Enhanced v3.0
Módulo para buscar imagens virais no Google Imagens de Instagram/Facebook
Analisa engajamento, extrai links dos posts e salva dados estruturados
Corrigido e aprimorado para usar Apify + Playwright (fallback) e tirar screenshots.
"""

import os
import re
import json
import time
import asyncio
import logging
from datetime import datetime
from typing import List, Dict, Optional, Tuple
from urllib.parse import urlparse, parse_qs, unquote, urljoin
from dataclasses import dataclass, asdict
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import hashlib

# Carregar variáveis de ambiente
load_dotenv()

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import condicional do Playwright
try:
    from playwright.async_api import async_playwright, Page, Browser, BrowserContext
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False
    logger.warning("Playwright não encontrado. Instale com 'pip install playwright' para funcionalidades avançadas.")

@dataclass
class ViralImage:
    """Estrutura de dados para imagem viral"""
    image_url: str
    post_url: str
    platform: str # 'instagram' ou 'facebook'
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
    image_path: Optional[str] = None # Caminho do arquivo da imagem
    screenshot_path: Optional[str] = None # Caminho da screenshot
    extracted_at: str = datetime.now().isoformat()

class ViralImageFinder:
    """Classe principal para encontrar imagens virais"""
    def __init__(self, config: Dict = None):
        self.config = config or self._load_config()
        self.session = requests.Session()
        self.setup_session()
        self.apify_api_key = self.config.get('apify_api_key')
        self.instagram_session_cookie = self.config.get('instagram_session_cookie')
        self.playwright_enabled = self.config.get('playwright_enabled', True) and PLAYWRIGHT_AVAILABLE

    def _load_config(self) -> Dict:
        """Carrega configurações do ambiente"""
        return {
            'gemini_api_key': os.getenv('GEMINI_API_KEY'),
            'serper_api_key': os.getenv('SERPER_API_KEY'),
            'google_search_key': os.getenv('GOOGLE_SEARCH_KEY'),
            'google_cse_id': os.getenv('GOOGLE_CSE_ID'),
            'apify_api_key': os.getenv('APIFY_API_KEY'),
            'instagram_session_cookie': os.getenv('INSTAGRAM_SESSION_COOKIE'),
            'max_images': int(os.getenv('MAX_IMAGES', 30)),
            'min_engagement': float(os.getenv('MIN_ENGAGEMENT', 0)),
            'timeout': int(os.getenv('TIMEOUT', 30)),
            'headless': os.getenv('PLAYWRIGHT_HEADLESS', 'True').lower() == 'true',
            'output_dir': os.getenv('OUTPUT_DIR', 'viral_images_data'),
            'images_dir': os.getenv('IMAGES_DIR', 'downloaded_images'),
            'extract_images': os.getenv('EXTRACT_IMAGES', 'True').lower() == 'true',
            'playwright_enabled': os.getenv('PLAYWRIGHT_ENABLED', 'True').lower() == 'true',
            'screenshots_dir': os.getenv('SCREENSHOTS_DIR', 'screenshots'),
            'playwright_timeout': int(os.getenv('PLAYWRIGHT_TIMEOUT', 30000)),
            'playwright_browser': os.getenv('PLAYWRIGHT_BROWSER', 'chromium'),
        }

    def setup_session(self):
        """Configura sessão HTTP com headers apropriados"""
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'pt-BR,pt;q=0.9,en;q=0.8',
        })

    async def search_images(self, query: str) -> List[Dict]:
        """Busca imagens usando Serper (prioritário)"""
        all_results = []
        queries = [
            f'site:instagram.com "{query}" masterclass curso gratis',
            f'site:facebook.com "{query}" aula gratuita curso online',
            f'instagram facebook "{query}" curso gratis',
            f'"{query}" masterclass instagram stories highlights',
            f'"{query}" facebook grupo curso gratuito',
            f'site:instagram.com/p "{query}" curso online',
            f'site:facebook.com/watch "{query}" aula gratis'
        ]

        for q in queries:
            logger.info(f"Buscando: {q}")
            results = []

            # Tentar Serper primeiro
            if self.config.get('serper_api_key'):
                try:
                    serper_results = await self._search_serper(q)
                    results.extend(serper_results)
                    logger.info(f"Serper encontrou {len(serper_results)} imagens para: {q}")
                except Exception as e:
                    logger.error(f"Erro na busca Serper para '{q}': {e}")

            # Tentar Google CSE (com verificação de erro 429)
            if self.config.get('google_search_key') and self.config.get('google_cse_id'):
                try:
                    google_results = await self._search_google_cse(q)
                    results.extend(google_results)
                    logger.info(f"Google CSE encontrou {len(google_results)} imagens para: {q}")
                except requests.exceptions.HTTPError as e:
                    if e.response.status_code == 429:
                        logger.error(f"Erro 429 na busca Google CSE para '{q}': Quota excedida. Pulando Google CSE.")
                    else:
                        logger.error(f"Erro na busca Google CSE para '{q}': {e}")
                except Exception as e:
                    logger.error(f"Erro inesperado na busca Google CSE para '{q}': {e}")

            all_results.extend(results)

        # Remover duplicatas baseadas em post_url
        seen_urls = set()
        unique_results = []
        for result in all_results:
            post_url = result.get('page_url', '').strip()
            if post_url and post_url not in seen_urls:
                seen_urls.add(post_url)
                unique_results.append(result)

        logger.info(f"Encontrados {len(unique_results)} posts relevantes")
        return unique_results

    async def _search_serper(self, query: str) -> List[Dict]:
        """Busca imagens usando Serper.dev"""
        if not self.config.get('serper_api_key'):
            return []
        url = "https://google.serper.dev/images"
        payload = json.dumps({
            "q": query,
            "num": 2,
            "safe": "off",
            "imgSize": "large",
            "imgType": "photo"
        })
        headers = {
            'X-API-KEY': self.config['serper_api_key'],
            'Content-Type': 'application/json'
        }
        response = requests.post(url, headers=headers, data=payload, timeout=self.config['timeout'])
        response.raise_for_status()
        data = response.json()
        results = []
        for item in data.get('images', []):
            results.append({
                'image_url': item.get('imageUrl', ''),
                'page_url': item.get('link', ''),
                'title': item.get('title', ''),
                'description': item.get('snippet', '')
            })
        return results

    async def _search_google_cse(self, query: str) -> List[Dict]:
        """Busca imagens usando Google Custom Search Engine"""
        if not self.config.get('google_search_key') or not self.config.get('google_cse_id'):
            return []
        url = "https://www.googleapis.com/customsearch/v1"
        params = {
            'key': self.config['google_search_key'],
            'cx': self.config['google_cse_id'],
            'q': query,
            'searchType': 'image',
            'num': 2,
            'safe': 'off',
            'fileType': 'jpg,png,jpeg',
            'imgSize': 'large',
            'imgType': 'photo'
        }
        response = self.session.get(url, params=params, timeout=self.config['timeout'])
        response.raise_for_status()
        data = response.json()
        results = []
        for item in data.get('items', []):
            results.append({
                'image_url': item.get('link', ''),
                'page_url': item.get('image', {}).get('contextLink', ''),
                'title': item.get('title', ''),
                'description': item.get('snippet', '')
            })
        return results

    async def analyze_post_engagement(self, post_url: str, platform: str) -> Dict:
        """Analisa engajamento do post, usando Apify primeiro, depois Playwright como fallback"""
        # Primeira tentativa: Apify (para Instagram)
        if platform == 'instagram' and self.apify_api_key and self.instagram_session_cookie:
            logger.info(f"Tentando análise com Apify para: {post_url}")
            try:
                engagement_data = await self._analyze_instagram_with_apify(post_url)
                if engagement_data:
                    logger.info(f"Engajamento obtido via Apify para {post_url}: {engagement_data}")
                    return engagement_data
                else:
                    logger.warning(f"Apify não retornou dados para {post_url}. Usando fallback Playwright.")
            except Exception as e:
                logger.error(f"Erro ao usar Apify para {post_url}: {e}. Usando fallback Playwright.")

        # Segunda tentativa: Playwright (para Instagram e Facebook)
        if self.playwright_enabled:
            logger.info(f"Tentando análise com Playwright para: {post_url}")
            try:
                engagement_data = await self._analyze_with_playwright(post_url, platform)
                if engagement_data:
                    logger.info(f"Engajamento obtido via Playwright para {post_url}: {engagement_data}")
                    return engagement_data
                else:
                    logger.warning(f"Playwright não retornou dados para {post_url}. Usando análise simples.")
            except Exception as e:
                logger.error(f"Erro ao usar Playwright para {post_url}: {e}. Usando análise simples.")

        # Último fallback: análise simples
        logger.info(f"Usando análise simples para: {post_url}")
        if platform == 'instagram':
            return await self._analyze_instagram_post_simple(post_url)
        elif platform == 'facebook':
            return await self._analyze_facebook_post_simple(post_url)
        else:
            return self._get_default_engagement(platform)

    async def _analyze_instagram_with_apify(self, post_url: str) -> Optional[Dict]:
        """Analisa engajamento de post do Instagram usando Apify"""
        if not self.apify_api_key or not self.instagram_session_cookie:
            return None

        # Extrair shortcode do URL
        match = re.search(r'/p/([A-Za-z0-9_-]+)/|/reel/([A-Za-z0-9_-]+)/', post_url)
        if not match:
            logger.warning(f"Não foi possível extrair shortcode do Instagram URL: {post_url}")
            return None
        shortcode = match.group(1) or match.group(2)

        apify_url = "https://api.apify.com/v2/acts/apify~instagram-post-scraper/run-sync-get-dataset-items"
        params = {
            'token': self.apify_api_key
        }
        payload = {
            "instagramPostUrls": [f"https://www.instagram.com/p/{shortcode}/"],
            "resultsLimit": 1,
            "sessionCookies": [self.instagram_session_cookie]
        }

        try:
            response = requests.post(apify_url, params=params, json=payload, timeout=60)
            response.raise_for_status()
            data = response.json()

            if data and isinstance(data, list) and len(data) > 0:
                post_data = data[0]
                likes = post_data.get('likesCount', 0)
                comments = post_data.get('commentsCount', 0)
                views = post_data.get('videoViewCount', 0) # Para reels
                author = post_data.get('ownerUsername', '')
                followers = post_data.get('ownerFollowersCount', 0)
                post_date = post_data.get('date', '')
                caption = post_data.get('caption', '')
                hashtags = re.findall(r"#(\w+)", caption)

                score = self._calculate_engagement_score(
                    likes=likes, comments=comments, shares=0, views=views, followers=followers
                )

                return {
                    'engagement_score': score,
                    'views_estimate': views,
                    'likes_estimate': likes,
                    'comments_estimate': comments,
                    'shares_estimate': 0,
                    'author': author,
                    'author_followers': followers,
                    'post_date': post_date,
                    'hashtags': hashtags
                }
            else:
                logger.warning(f"Apify não retornou dados válidos para {post_url}")
                return None
        except requests.exceptions.RequestException as e:
            logger.error(f"Erro de requisição Apify para {post_url}: {e}")
            return None
        except Exception as e:
            logger.error(f"Erro inesperado Apify para {post_url}: {e}")
            return None

    async def _analyze_with_playwright(self, post_url: str, platform: str) -> Optional[Dict]:
        """Analisa engajamento usando Playwright"""
        if not self.playwright_enabled:
            return None

        logger.info(f"Iniciando análise Playwright para {post_url}")
        browser: Optional[Browser] = None
        context: Optional[BrowserContext] = None
        page: Optional[Page] = None
        try:
            async with async_playwright() as p:
                # Escolher navegador
                if self.config['playwright_browser'] == 'firefox':
                    browser_type = p.firefox
                elif self.config['playwright_browser'] == 'webkit':
                    browser_type = p.webkit
                else: # default to chromium
                    browser_type = p.chromium

                # Lançar navegador
                browser = await browser_type.launch(headless=self.config['headless'])
                # Criar contexto (permite definir cookies, viewport etc.)
                context = await browser.new_context()
                # Criar página
                page = await context.new_page()
                # Definir timeout
                page.set_default_timeout(self.config['playwright_timeout'])

                # Navegar até a página
                await page.goto(post_url)
                await page.wait_for_load_state('networkidle') # Esperar carregar

                likes, comments, shares, views, followers = 0, 0, 0, 0, 0
                author = ""
                post_date = ""
                hashtags = []

                if platform == 'instagram':
                    # Extrair dados do Instagram
                    # Autor
                    try:
                        author_elem = await page.query_selector('header section h2 a')
                        if not author_elem:
                            author_elem = await page.query_selector('header section div a')
                        if author_elem:
                            author = await author_elem.inner_text()
                    except:
                        pass

                    # Data (simplificada)
                    try:
                        date_elem = await page.query_selector('time')
                        if date_elem:
                            post_date = await date_elem.get_attribute('datetime') or await date_elem.inner_text()
                    except:
                        pass

                    # Engajamento (likes, comments)
                    try:
                        # Likes (pode estar em um span dentro de section)
                        likes_elem = await page.query_selector('section span')
                        if likes_elem:
                            likes_text = await likes_elem.inner_text()
                            # Extrair número de texto (ex: "1.234 curtidas")
                            likes_match = re.search(r'([\d.,KM]+)', likes_text)
                            if likes_match:
                                likes_str = likes_match.group(1).replace('.', '').replace(',', '')
                                if 'K' in likes_str:
                                    likes = int(float(likes_str.replace('K', '')) * 1000)
                                elif 'M' in likes_str:
                                    likes = int(float(likes_str.replace('M', '')) * 1000000)
                                else:
                                    likes = int(likes_str)
                    except Exception as e:
                        logger.debug(f"Erro ao extrair likes do Instagram: {e}")

                    try:
                        # Comentários (pode estar em um botão ou texto)
                        comments_elem = await page.query_selector('ul li button span')
                        if comments_elem:
                            comments_text = await comments_elem.inner_text()
                            comments_match = re.search(r'([\d.,KM]+)', comments_text)
                            if comments_match:
                                comments_str = comments_match.group(1).replace('.', '').replace(',', '')
                                if 'K' in comments_str:
                                    comments = int(float(comments_str.replace('K', '')) * 1000)
                                elif 'M' in comments_str:
                                    comments = int(float(comments_str.replace('M', '')) * 1000000)
                                else:
                                    comments = int(comments_str)
                    except Exception as e:
                        logger.debug(f"Erro ao extrair comments do Instagram: {e}")

                    # Hashtags (da legenda)
                    try:
                        caption_elem = await page.query_selector('article div[role="button"] + div h1')
                        if caption_elem:
                            caption_text = await caption_elem.inner_text()
                            hashtags = re.findall(r"#(\w+)", caption_text)
                    except Exception as e:
                        logger.debug(f"Erro ao extrair hashtags do Instagram: {e}")

                elif platform == 'facebook':
                    # Extrair dados do Facebook (mais complexo)
                    # Autor
                    try:
                        author_elem = await page.query_selector('strong a')
                        if not author_elem:
                             author_elem = await page.query_selector('[data-sigil="mfeed_pivots_message feed-story-highlight-candidate"] strong a')
                        if author_elem:
                            author = await author_elem.inner_text()
                    except:
                        pass

                    # Engajamento (likes, comments, shares)
                    try:
                        # Procurar por elementos que contenham reações
                        reaction_elems = await page.query_selector_all('[data-sigil="mfeed_pivots_message feed-story-highlight-candidate"] span')
                        for elem in reaction_elems:
                            text = await elem.inner_text()
                            if 'curtida' in text.lower() or 'like' in text.lower():
                                likes_match = re.search(r'([\d.,KM]+)', text)
                                if likes_match:
                                    likes_str = likes_match.group(1).replace('.', '').replace(',', '')
                                    if 'K' in likes_str:
                                        likes = int(float(likes_str.replace('K', '')) * 1000)
                                    elif 'M' in likes_str:
                                        likes = int(float(likes_str.replace('M', '')) * 1000000)
                                    else:
                                        likes = int(likes_str)
                            elif 'comentário' in text.lower() or 'comment' in text.lower():
                                comments_match = re.search(r'([\d.,KM]+)', text)
                                if comments_match:
                                    comments_str = comments_match.group(1).replace('.', '').replace(',', '')
                                    if 'K' in comments_str:
                                        comments = int(float(comments_str.replace('K', '')) * 1000)
                                    elif 'M' in comments_str:
                                        comments = int(float(comments_str.replace('M', '')) * 1000000)
                                    else:
                                        comments = int(comments_str)
                            elif 'compartilhamento' in text.lower() or 'share' in text.lower():
                                shares_match = re.search(r'([\d.,KM]+)', text)
                                if shares_match:
                                    shares_str = shares_match.group(1).replace('.', '').replace(',', '')
                                    if 'K' in shares_str:
                                        shares = int(float(shares_str.replace('K', '')) * 1000)
                                    elif 'M' in shares_str:
                                        shares = int(float(shares_str.replace('M', '')) * 1000000)
                                    else:
                                        shares = int(shares_str)
                    except Exception as e:
                        logger.debug(f"Erro ao extrair engajamento do Facebook: {e}")

                # Calcular score
                score = self._calculate_engagement_score(likes, comments, shares, views, followers)
                return {
                    'engagement_score': score,
                    'views_estimate': views,
                    'likes_estimate': likes,
                    'comments_estimate': comments,
                    'shares_estimate': shares,
                    'author': author,
                    'author_followers': followers,
                    'post_date': post_date,
                    'hashtags': hashtags
                }

        except Exception as e:
            logger.error(f"Erro ao analisar com Playwright {post_url}: {e}")
            return None
        finally:
            # Fechar recursos
            if page:
                await page.close()
            if context:
                await context.close()
            if browser:
                await browser.close()

    async def _analyze_instagram_post_simple(self, post_url: str) -> Dict:
        """Análise simplificada do Instagram"""
        try:
            response = self.session.get(post_url, timeout=self.config['timeout'])
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                return self._estimate_engagement_from_html(soup, 'instagram')
        except Exception as e:
            logger.error(f"Erro ao analisar post Instagram: {e}")
        return self._get_default_engagement('instagram')

    async def _analyze_facebook_post_simple(self, post_url: str) -> Dict:
        """Análise simplificada do Facebook"""
        try:
            response = self.session.get(post_url, timeout=self.config['timeout'])
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                return self._estimate_engagement_from_html(soup, 'facebook')
        except Exception as e:
            logger.error(f"Erro ao analisar post Facebook: {e}")
        return self._get_default_engagement('facebook')

    def _estimate_engagement_from_html(self, soup: BeautifulSoup, platform: str) -> Dict:
        """Estima engajamento baseado em padrões de HTML"""
        likes, comments, shares, views, followers = 0, 0, 0, 0, 0
        author = ""
        post_date = ""
        hashtags = []

        if platform == 'instagram':
            # Simulação genérica
            pass
        elif platform == 'facebook':
            # Simulação genérica
            pass

        score = self._calculate_engagement_score(likes, comments, shares, views, followers)
        return {
            'engagement_score': score,
            'views_estimate': views,
            'likes_estimate': likes,
            'comments_estimate': comments,
            'shares_estimate': shares,
            'author': author,
            'author_followers': followers,
            'post_date': post_date,
            'hashtags': hashtags
        }

    def _calculate_engagement_score(self, likes: int, comments: int, shares: int, views: int, followers: int) -> float:
        """Calcula score de engajamento"""
        total_interactions = likes + comments + shares
        if views > 0:
            return round((total_interactions / (views + 1)) * 100, 2)
        else:
            return float(total_interactions)

    def _get_default_engagement(self, platform: str) -> Dict:
        """Retorna valores padrão para engajamento"""
        return {
            'engagement_score': 0.0,
            'views_estimate': 0,
            'likes_estimate': 0,
            'comments_estimate': 0,
            'shares_estimate': 0,
            'author': '',
            'author_followers': 0,
            'post_date': '',
            'hashtags': []
        }

    def _generate_unique_filename(self, base_name: str, content_type: str, url: str) -> str:
        """Gera um nome de arquivo único para evitar sobrescrita"""
        ext = 'jpg'
        if 'png' in content_type:
            ext = 'png'
        elif 'jpeg' in content_type:
            ext = 'jpeg'
        elif 'webp' in content_type:
            ext = 'webp'

        # Se o nome base for vazio ou não tiver extensão válida, usar hash da URL
        if not base_name or '.' not in base_name or not any(e in base_name for e in ['jpg', 'jpeg', 'png', 'webp']):
            hash_name = hashlib.md5(url.encode()).hexdigest()[:12]
            return f"{hash_name}.{ext}"
        else:
            # Garantir unicidade adicionando hash ao final se necessário
            name_without_ext, current_ext = os.path.splitext(base_name)
            if not current_ext or current_ext[1:] not in ['jpg', 'jpeg', 'png', 'webp']:
                # Se a extensão não for válida, usar a detectada
                return f"{name_without_ext}.{ext}"
            else:
                # Extensão válida, mas verificar unicidade
                full_path = os.path.join(self.config['images_dir'], base_name)
                if os.path.exists(full_path):
                    hash_suffix = hashlib.md5(url.encode()).hexdigest()[:6]
                    return f"{name_without_ext}_{hash_suffix}{current_ext}"
                else:
                    return base_name

    def extract_image_data(self, image_url: str, post_url: str, platform: str) -> Optional[str]:
        """Extrai e salva a imagem ou tira uma screenshot se falhar"""
        if not self.config.get('extract_images', True):
            return None

        try:
            # Etapa 1: Tentar com a URL fornecida diretamente
            logger.info(f"Tentando download direto da image_url: {image_url}")
            response = self.session.get(image_url, timeout=self.config['timeout'], stream=True)
            response.raise_for_status()
            content_type = response.headers.get('content-type', '').lower()
            content_length = int(response.headers.get('content-length', 0))

            if 'image' not in content_type:
                logger.warning(f"URL não aponta para uma imagem válida (Content-Type: {content_type}): {image_url}")
                # Etapa 2: Tentar resolver a URL real a partir do post_url
                logger.info(f"Tentando resolver imagem real a partir do post: {post_url}")
                resolved_url = self._resolve_image_from_post(post_url, platform)
                if resolved_url and resolved_url != image_url:
                    logger.info(f"Nova URL resolvida: {resolved_url}")
                    # Recursão segura para uma vez
                    return self.extract_image_data(resolved_url, post_url, platform)
                else:
                    logger.error(f"Não foi possível resolver uma URL de imagem válida para {post_url}")
                    # Tentar tirar uma screenshot da página do post
                    screenshot_path = self.take_screenshot(post_url, platform)
                    return screenshot_path
            else:
                if content_length > 10 * 1024 * 1024: # 10MB
                    logger.warning(f"Imagem muito grande: {image_url}")
                    # Tentar tirar uma screenshot
                    screenshot_path = self.take_screenshot(post_url, platform)
                    return screenshot_path

                os.makedirs(self.config['images_dir'], exist_ok=True)

                # Gerar nome de arquivo único
                parsed_url = urlparse(image_url)
                filename = os.path.basename(parsed_url.path)
                filename = self._generate_unique_filename(filename, content_type, image_url)

                filepath = os.path.join(self.config['images_dir'], filename)

                # Salvar imagem
                with open(filepath, 'wb') as f:
                    for chunk in response.iter_content(1024):
                        f.write(chunk)

                logger.info(f"Imagem salva: {filepath}")
                return filepath

        except requests.exceptions.RequestException as e:
            logger.error(f"Erro de requisição ao baixar imagem {image_url}: {e}")
            # Tentar tirar uma screenshot
            screenshot_path = self.take_screenshot(post_url, platform)
            return screenshot_path
        except Exception as e:
            logger.error(f"Erro ao salvar imagem {image_url}: {e}")
            # Tentar tirar uma screenshot
            screenshot_path = self.take_screenshot(post_url, platform)
            return screenshot_path

    def _resolve_image_from_post(self, post_url: str, platform: str) -> Optional[str]:
        """Tenta encontrar a URL real da imagem dentro da página do post."""
        try:
            response = self.session.get(post_url, timeout=self.config['timeout'])
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')

            if platform == 'instagram':
                og_image = soup.find('meta', property='og:image')
                if og_image and og_image.get('content'):
                    return og_image['content']
            elif platform == 'facebook':
                og_image = soup.find('meta', property='og:image')
                if og_image and og_image.get('content'):
                    return og_image['content']

        except Exception as e:
            logger.error(f"Erro ao resolver imagem do post {post_url}: {e}")
        return None

    def take_screenshot(self, post_url: str, platform: str) -> Optional[str]:
        """Tenta tirar uma screenshot da página do post se o download falhar."""
        if not self.playwright_enabled:
            logger.warning("Playwright não está habilitado ou disponível. Screenshot não tirada.")
            return None

        logger.info(f"Tentando tirar screenshot da página: {post_url}")
        os.makedirs(self.config['screenshots_dir'], exist_ok=True)
        
        # Gerar nome de arquivo para a screenshot
        safe_title = re.sub(r'[^\w\s-]', '', post_url).strip().replace(' ', '_')
        hash_suffix = hashlib.md5(post_url.encode()).hexdigest()[:8]
        screenshot_filename = f"screenshot_{safe_title}_{hash_suffix}.png"
        screenshot_path = os.path.join(self.config['screenshots_dir'], screenshot_filename)

        async def _take_screenshot_async():
            async with async_playwright() as p:
                # Escolher navegador
                if self.config['playwright_browser'] == 'firefox':
                    browser_type = p.firefox
                elif self.config['playwright_browser'] == 'webkit':
                    browser_type = p.webkit
                else: # default to chromium
                    browser_type = p.chromium

                # Lançar navegador
                browser = await browser_type.launch(headless=self.config['headless'])
                # Criar contexto
                context = await browser.new_context()
                # Criar página
                page = await context.new_page()
                # Definir timeout
                page.set_default_timeout(self.config['playwright_timeout'])

                try:
                    # Navegar até a página
                    await page.goto(post_url)
                    await page.wait_for_load_state('networkidle') # Esperar carregar

                    # Tirar screenshot
                    await page.screenshot(path=screenshot_path, full_page=False)
                    logger.info(f"Screenshot salva: {screenshot_path}")
                    return screenshot_path
                except Exception as e:
                    logger.error(f"Erro ao tirar screenshot de {post_url}: {e}")
                    return None
                finally:
                    # Fechar recursos
                    await page.close()
                    await context.close()
                    await browser.close()

        try:
            # Executar a função assíncrona de forma síncrona
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(_take_screenshot_async())
            loop.close()
            return result
        except Exception as e:
            logger.error(f"Erro ao executar screenshot: {e}")
            return None

    async def find_viral_images(self, query: str) -> Tuple[List[ViralImage], str]:
        """Função principal para encontrar imagens virais"""
        logger.info(f"Iniciando busca por imagens virais: {query}")

        # Buscar resultados
        search_results = await self.search_images(query)

        # Analisar engajamento e processar
        viral_images = []
        for i, result in enumerate(search_results[:self.config['max_images']]):
            try:
                logger.info(f"Processando {i+1}/{len(search_results[:self.config['max_images']])}: {result.get('page_url', '')}")

                # Determinar plataforma
                page_url = result.get('page_url', '')
                platform = 'instagram' if 'instagram.com' in page_url else 'facebook'

                # Analisar engajamento
                engagement = await self.analyze_post_engagement(page_url, platform)

                # Extrair imagem (opcional, pode ser lento)
                image_path = None
                if self.config.get('extract_images', True):
                    image_url_from_result = result.get('image_url', '')
                    image_path = self.extract_image_data(image_url_from_result, page_url, platform)

                # Criar objeto ViralImage
                viral_image = ViralImage(
                    image_url=result.get('image_url', ''),
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
                    screenshot_path=None # Será preenchido se necessário
                )

                # Verificar critério de viralidade
                if viral_image.engagement_score >= self.config['min_engagement']:
                    viral_images.append(viral_image)
                    logger.info(f"Adicionada imagem viral: {viral_image.title} - Score: {viral_image.engagement_score}")
                else:
                    logger.debug(f"Imagem não atende ao critério de engajamento ({viral_image.engagement_score} < {self.config['min_engagement']}): {page_url}")

            except Exception as e:
                logger.error(f"Erro ao processar {result.get('page_url', '')}: {e}")

        # Salvar resultados
        output_file = self.save_results(viral_images, query)

        logger.info(f"Busca concluída! Encontradas {len(viral_images)} imagens virais")
        return viral_images, output_file

    def save_results(self, viral_images: List[ViralImage], query: str, ai_analysis: Dict = None):
        """Salva resultados em arquivo JSON"""
        os.makedirs(self.config['output_dir'], exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_query = re.sub(r'[^\w\s-]', '', query).strip().replace(' ', '_')
        filename = f"viral_images_{safe_query}_{timestamp}.json"
        filepath = os.path.join(self.config['output_dir'], filename)

        try:
            # Converter objetos ViralImage para dicionários
            images_data = [asdict(img) for img in viral_images]

            data = {
                'query': query,
                'extracted_at': datetime.now().isoformat(),
                'total_images': len(viral_images),
                'images': images_data,
                'ai_analysis': ai_analysis or {}
            }

            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

            logger.info(f"Resultados salvos em: {filepath}")
            return filepath
        except Exception as e:
            logger.error(f"Erro ao salvar arquivo: {e}")
            return None

    def _get_platform_distribution(self, images: List[ViralImage]) -> Dict:
        """Calcula distribuição por plataforma"""
        platforms = {}
        for img in images:
            platforms[img.platform] = platforms.get(img.platform, 0) + 1
        return platforms

    def _calculate_avg_engagement(self, images: List[ViralImage]) -> float:
        """Calcula engajamento médio"""
        if not images:
            return 0
        return sum(img.engagement_score for img in images) / len(images)


# Função principal para uso do módulo
async def main():
    """Função principal de exemplo"""
    config = {
        'gemini_api_key': os.getenv('GEMINI_API_KEY'),
        'serper_api_key': os.getenv('SERPER_API_KEY'),
        'google_search_key': os.getenv('GOOGLE_SEARCH_KEY'),
        'google_cse_id': os.getenv('GOOGLE_CSE_ID'),
        'apify_api_key': os.getenv('APIFY_API_KEY'),
        'instagram_session_cookie': os.getenv('INSTAGRAM_SESSION_COOKIE'),
        'playwright_enabled': os.getenv('PLAYWRIGHT_ENABLED', 'True').lower() == 'true',
        'screenshots_dir': os.getenv('SCREENSHOTS_DIR', 'screenshots'),
        'max_images': int(os.getenv('MAX_IMAGES', 30)),
        'min_engagement': float(os.getenv('MIN_ENGAGEMENT', 0)),
        'timeout': int(os.getenv('TIMEOUT', 30)),
        'headless': os.getenv('PLAYWRIGHT_HEADLESS', 'True').lower() == 'true',
        'output_dir': os.getenv('OUTPUT_DIR', 'viral_images_data'),
        'images_dir': os.getenv('IMAGES_DIR', 'downloaded_images'),
        'extract_images': os.getenv('EXTRACT_IMAGES', 'True').lower() == 'true',
        'playwright_timeout': int(os.getenv('PLAYWRIGHT_TIMEOUT', 30000)),
        'playwright_browser': os.getenv('PLAYWRIGHT_BROWSER', 'chromium'),
    }

    # Inicializar finder
    finder = ViralImageFinder(config)

    # Executar busca
    try:
        query = input("Digite o termo de busca: ").strip()
        if not query:
            logger.error("Termo de busca inválido.")
            return

        viral_images, output_file = await finder.find_viral_images(query)

        # Relatório final
        print("\n" + "=" * 20 + " RELATÓRIO DE IMAGENS VIRAIS " + "=" * 20)
        print(f"Query: {query}")
        print(f"Total encontradas: {len(viral_images)}")
        print(f"Arquivo salvo: {output_file}")

        if viral_images:
            print("\n=== TOP 10 IMAGENS VIRAIS ===")
            sorted_images = sorted(viral_images, key=lambda x: x.engagement_score, reverse=True)
            for i, img in enumerate(sorted_images[:10]):
                print(f"{i+1}. {img.platform.upper()} - @{img.author}")
                print(f"   Score: {img.engagement_score}")
                print(f"   Likes: {img.likes_estimate} | Comments: {img.comments_estimate}")
                print(f"   URL: {img.post_url}")
                if img.image_path:
                    print(f"   Imagem salva: {img.image_path}")
                elif img.screenshot_path:
                    print(f"   Screenshot salva: {img.screenshot_path}")
                else:
                    print(f"   Imagem não salva.")
                print("-" * 20)
        else:
            print("\nNenhuma imagem viral encontrada com os critérios especificados.")
            print("Dicas:")
            print("- Configure pelo menos uma API (Serper ou Google CSE)")
            print("- Reduza o min_engagement se necessário")
            print("- Verifique sua conexão com a internet")

    except Exception as e:
        logger.exception(f"Erro durante a execução principal: {e}")


if __name__ == "__main__":
    print("VIRAL IMAGE FINDER v3.0")
    print("=====================")
    asyncio.run(main())
