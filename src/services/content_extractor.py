#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ARQV30 Enhanced v2.0 - Content Extractor
Extrator de conteúdo robusto com múltiplas estratégias
"""

import os
import logging
import time
import requests
from typing import Optional, Dict, Any
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
import re
import hashlib # Import hashlib for caching

logger = logging.getLogger(__name__)

class ContentExtractor:
    """Sistema robusto de extração de conteúdo com múltiplas estratégias"""

    def __init__(self):
        """Inicializa o extrator de conteúdo"""
        # Padrão para detectar URLs do YouTube
        self.youtube_pattern = re.compile(r'(?:youtube\.com|youtu\.be)')

        self.strategies = [
            ('direct_extraction', self._extract_direct),
            ('readability_extraction', self._extract_with_readability),
            ('beautiful_soup_extraction', self._extract_direct), # Usando _extract_direct como exemplo para BS
            ('fallback_extraction', self._extract_fallback)
        ]

        # Estratégias específicas para YouTube
        self.youtube_strategies = [
            ('youtube_api_extraction', self._youtube_api_extraction),
            ('youtube_html_extraction', self._youtube_html_extraction),
            ('youtube_fallback_extraction', self._youtube_fallback_extraction)
        ]

        self.min_content_length = 100
        self.max_retries = 3
        self.jina_api_key = os.getenv('JINA_API_KEY')
        self.jina_reader_url = "https://r.jina.ai/"

        # Parâmetros de qualidade de conteúdo
        self.content_quality_threshold = 50.0 # Limiar de qualidade mínimo (0-100)

        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'pt-BR,pt;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }

        # Cache configuration (simplistic in-memory cache for example)
        self._cache = {}
        self._cache_max_size = 100

        logger.info("Content Extractor inicializado com múltiplas estratégias")


    def extract_content(self, url: str, timeout: int = 30) -> Dict[str, Any]:
        """
        Extrai conteúdo de uma URL usando múltiplas estratégias com fallback

        Args:
            url: URL para extrair conteúdo
            timeout: Timeout em segundos

        Returns:
            dict: Conteúdo extraído com metadados
        """
        logger.info(f"🔍 Iniciando extração de conteúdo: {url}")

        if not url or not isinstance(url, str):
            logger.error(f"❌ URL inválida: {url}")
            return self._create_error_result("URL inválida ou vazia")

        start_time = time.time()

        # Sanitiza URL
        clean_url = self._sanitize_url(url)
        if not clean_url:
            logger.error(f"❌ URL não pôde ser sanitizada: {url}")
            return self._create_error_result("URL não pôde ser processada")

        # PRIORIDADE: Verifica se é rede social e usa MCP específico
        social_platform = self._identify_social_platform(clean_url)
        if social_platform:
            logger.info(f"🎯 Detectada rede social: {social_platform} - Usando MCP especializado")
            mcp_result = self._extract_social_content_mcp(clean_url, social_platform)
            if mcp_result and mcp_result.get('success'):
                return mcp_result
            logger.warning(f"⚠️ MCP {social_platform} falhou, continuando com estratégias normais")

        # Verifica cache primeiro
        cache_key = hashlib.md5(clean_url.encode()).hexdigest()
        cached_result = self._get_cached_result(cache_key)
        if cached_result:
            logger.info(f"✅ Conteúdo encontrado no cache para {clean_url}")
            return cached_result


        # Detecta se é URL do YouTube e usa estratégias específicas
        if self.youtube_pattern.search(clean_url):
            logger.info(f"▶️ URL do YouTube detectada: {clean_url}")
            content = self._extract_youtube_content(clean_url, self.max_retries)
        else:
            # Para URLs normais, usa estratégias padrão
            content = self._extract_regular_content(clean_url, self.max_retries)

        if content:
            metadata = self.extract_metadata(clean_url)
            result = {
                'url': clean_url,
                'content': content,
                'metadata': metadata,
                'success': True,
                'error': None,
                'processing_time': time.time() - start_time
            }
            self._cache_result(cache_key, result)
            return result
        else:
            return self._create_error_result("Falha ao extrair conteúdo após todas as tentativas", time.time() - start_time)


    def _extract_youtube_content(self, url: str, max_retries: int) -> Optional[str]:
        """Extração especializada para conteúdo do YouTube"""
        logger.info(f"▶️ Processando URL do YouTube com estratégias especializadas")

        for attempt in range(max_retries):
            for strategy_name, strategy_func in self.youtube_strategies:
                try:
                    logger.info(f"🎯 YouTube - Tentativa {attempt + 1}/{max_retries} - Estratégia: {strategy_name}")

                    content = strategy_func(url)

                    if content and len(content.strip()) >= self.min_content_length:
                        logger.info(f"✅ Conteúdo YouTube extraído com sucesso usando {strategy_name}")
                        logger.info(f"📊 Tamanho do conteúdo: {len(content)} caracteres")
                        return content
                    else:
                        logger.warning(f"⚠️ Estratégia YouTube {strategy_name} falhou: Conteúdo insuficiente")

                except Exception as e:
                    logger.warning(f"⚠️ Estratégia YouTube {strategy_name} falhou: {str(e)}")
                    continue

            # Pequena pausa entre tentativas
            if attempt < max_retries - 1:
                time.sleep(1)

        logger.error(f"❌ Todas as estratégias YouTube falharam para {url}")
        return None

    def _extract_regular_content(self, url: str, max_retries: int) -> Optional[str]:
        """Extração padrão para URLs normais"""

        for attempt in range(max_retries):
            for strategy_name, strategy_func in self.strategies:
                try:
                    logger.info(f"🎯 Tentativa {attempt + 1}/{max_retries} - Estratégia: {strategy_name}")

                    content = strategy_func(url)

                    if content and len(content.strip()) >= self.min_content_length:
                        logger.info(f"✅ Conteúdo extraído com sucesso usando {strategy_name}")
                        logger.info(f"📊 Tamanho do conteúdo: {len(content)} caracteres")
                        return content
                    else:
                        logger.warning(f"⚠️ Estratégia {strategy_name} falhou para {url}: Nenhum conteúdo substancial encontrado")

                except Exception as e:
                    logger.warning(f"⚠️ Estratégia {strategy_name} falhou para {url}: {str(e)}")
                    continue

            # Pequena pausa entre tentativas
            if attempt < max_retries - 1:
                time.sleep(1)

        logger.error(f"❌ Todas as estratégias falharam para {url}")
        return None

    def _extract_with_jina(self, url: str) -> Optional[str]:
        """Extrai conteúdo usando Jina Reader API"""
        try:
            if not self.jina_api_key:
                raise Exception("Jina API Key não configurada")

            headers = {
                **self.headers,
                "Authorization": f"Bearer {self.jina_api_key}"
            }

            jina_url = f"{self.jina_reader_url}{url}"

            response = requests.get(
                jina_url,
                headers=headers,
                timeout=60
            )

            if response.status_code == 200:
                content = response.text

                # Limita tamanho para otimização
                if len(content) > 15000:
                    content = content[:15000] + "... [conteúdo truncado para otimização]"

                return content
            else:
                raise Exception(f"Jina Reader retornou status {response.status_code}")

        except Exception as e:
            raise e

    def _extract_direct(self, url: str) -> Optional[str]:
        """Extração direta usando BeautifulSoup"""
        try:
            response = requests.get(
                url,
                headers=self.headers,
                timeout=20,
                allow_redirects=True
            )

            if response.status_code == 200:
                soup = BeautifulSoup(response.content, "html.parser")

                # Remove elementos desnecessários
                for element in soup(["script", "style", "nav", "footer", "header",
                                   "form", "aside", "iframe", "noscript", "advertisement",
                                   "ads", "sidebar", "menu", "breadcrumb"]):
                    element.decompose()

                # Busca conteúdo principal
                main_content = (
                    soup.find('main') or
                    soup.find('article') or
                    soup.find('div', class_=re.compile(r'content|main|article|post|entry|body')) or
                    soup.find('div', id=re.compile(r'content|main|article|post|entry|body')) or
                    soup.find('section', class_=re.compile(r'content|main|article|post|entry'))
                )

                if main_content:
                    text = main_content.get_text()
                else:
                    # Fallback para body completo
                    body = soup.find('body')
                    text = body.get_text() if body else soup.get_text()

                # Limpa o texto
                text = self._clean_text(text)

                return text
            else:
                raise Exception(f"Resposta HTTP {response.status_code}")

        except Exception as e:
            raise e

    def _extract_with_readability(self, url: str) -> Optional[str]:
        """Extração usando algoritmo de readability"""
        try:
            response = requests.get(
                url,
                headers=self.headers,
                timeout=20,
                allow_redirects=True
            )

            if response.status_code == 200:
                soup = BeautifulSoup(response.content, "html.parser")

                # Remove elementos desnecessários
                for element in soup(["script", "style", "nav", "footer", "header",
                                   "form", "aside", "iframe", "noscript"]):
                    element.decompose()

                # Algoritmo simples de readability
                # Busca por elementos com mais texto
                candidates = []

                for element in soup.find_all(['div', 'article', 'section', 'main']):
                    text = element.get_text()
                    if len(text) > 200:  # Elementos com conteúdo substancial
                        # Score baseado em tamanho e densidade de parágrafos
                        paragraphs = element.find_all('p')
                        score = len(text) + (len(paragraphs) * 50)
                        candidates.append((score, text))

                if candidates:
                    # Pega o elemento com maior score
                    candidates.sort(key=lambda x: x[0], reverse=True)
                    text = candidates[0][1]

                    # Limpa o texto
                    text = self._clean_text(text)

                    return text
                else:
                    raise Exception("Nenhum conteúdo substancial encontrado")
            else:
                raise Exception(f"Resposta HTTP {response.status_code}")

        except Exception as e:
            raise e

    def _extract_fallback(self, url: str) -> Optional[str]:
        """Extração de fallback mais agressiva"""
        try:
            response = requests.get(
                url,
                headers=self.headers,
                timeout=15,
                allow_redirects=True
            )

            if response.status_code == 200:
                soup = BeautifulSoup(response.content, "html.parser")

                # Remove apenas elementos críticos
                for element in soup(["script", "style", "noscript"]):
                    element.decompose()

                # Pega todo o texto disponível
                text = soup.get_text()

                # Limpa o texto
                text = self._clean_text(text)

                # Se ainda tem conteúdo substancial, retorna
                if len(text) > 100:
                    return text
                else:
                    raise Exception("Conteúdo insuficiente após limpeza")
            else:
                raise Exception(f"Resposta HTTP {response.status_code}")

        except Exception as e:
            raise e

    def _youtube_api_extraction(self, url: str) -> Optional[str]:
        """Extração usando API do YouTube"""
        try:
            # Verifica se a API key está disponível
            youtube_api_key = os.getenv('YOUTUBE_API_KEY')
            if not youtube_api_key:
                logger.warning("YouTube API key não configurada")
                return None

            # Extrai o ID do vídeo
            video_id = self._extract_youtube_video_id(url)
            if not video_id:
                logger.error("Não foi possível extrair ID do vídeo do YouTube")
                return None

            # Faz requisição à API
            api_url = "https://www.googleapis.com/youtube/v3/videos"
            params = {
                'part': 'snippet,contentDetails,statistics',
                'id': video_id,
                'key': youtube_api_key
            }

            response = requests.get(api_url, params=params, timeout=10)
            response.raise_for_status()

            data = response.json()
            if not data.get('items'):
                return None

            video_data = data['items'][0]
            snippet = video_data['snippet']
            stats = video_data.get('statistics', {})

            # Monta conteúdo estruturado
            content = f"""
TÍTULO: {snippet.get('title', 'N/A')}

CANAL: {snippet.get('channelTitle', 'N/A')}

DESCRIÇÃO:
{snippet.get('description', 'Nenhuma descrição disponível')}

DATA DE PUBLICAÇÃO: {snippet.get('publishedAt', 'N/A')[:10]}

ESTATÍSTICAS:
- Visualizações: {stats.get('viewCount', 'N/A')}
- Likes: {stats.get('likeCount', 'N/A')}
- Comentários: {stats.get('commentCount', 'N/A')}

TAGS: {', '.join(snippet.get('tags', [])) if snippet.get('tags') else 'Nenhuma tag'}

CATEGORIA: {snippet.get('categoryId', 'N/A')}

URL: {url}
""".strip()

            return content

        except Exception as e:
            logger.error(f"Erro na extração YouTube API: {str(e)}")
            return None

    def _youtube_html_extraction(self, url: str) -> Optional[str]:
        """Extração de conteúdo básico do HTML do YouTube"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }

            response = requests.get(url, headers=headers, timeout=15)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')

            # Extrai título
            title_element = soup.find('title')
            title = title_element.text if title_element else "Título não encontrado"

            # Extrai descrição da meta tag
            description = ""
            meta_desc = soup.find('meta', {'name': 'description'})
            if meta_desc and meta_desc.get('content'):
                description = meta_desc['content']

            # Tenta extrair informações do script JSON
            script_content = ""
            for script in soup.find_all('script'):
                if script.string and 'videoDetails' in script.string:
                    script_content = script.string[:1000]  # Primeiros 1000 chars
                    break

            content = f"""
TÍTULO: {title}

DESCRIÇÃO: {description}

URL: {url}

INFORMAÇÕES ADICIONAIS:
Este vídeo do YouTube foi processado com extração básica de HTML.
Para análise completa do conteúdo, seria necessário processamento de vídeo especializado.

CONTEXTO: {script_content[:500] if script_content else 'Contexto adicional não disponível'}
""".strip()

            return content

        except Exception as e:
            logger.error(f"Erro na extração YouTube HTML: {str(e)}")
            return None

    def _youtube_fallback_extraction(self, url: str) -> Optional[str]:
        """Extração de fallback para YouTube - informações mínimas"""
        try:
            video_id = self._extract_youtube_video_id(url)

            content = f"""
VÍDEO DO YOUTUBE IDENTIFICADO

URL: {url}
ID do Vídeo: {video_id or 'Não identificado'}

NOTA: Este é um conteúdo do YouTube que não pôde ser extraído completamente.
Para análise detalhada, seriam necessárias:
1. API key do YouTube configurada
2. Processamento de conteúdo audiovisual
3. Análise de comentários e engajamento

RECOMENDAÇÃO: Configure a API do YouTube ou utilize ferramentas especializadas
para análise completa de conteúdo de vídeo.

STATUS: Fallback de emergência ativado
""".strip()

            return content

        except Exception as e:
            logger.error(f"Erro no fallback YouTube: {str(e)}")
            return "Conteúdo do YouTube - Extração não disponível"

    def _extract_youtube_video_id(self, url: str) -> Optional[str]:
        """Extrai o ID do vídeo de uma URL do YouTube"""
        patterns = [
            r'(?:youtube\.com\/(?:[^\/\n\s]+\/\S+\/|(?:v|e(?:mbed)?)\/|\S*?[?&]v=)|youtu\.be\/)([a-zA-Z0-9_-]{11})',
            r'^([a-zA-Z0-9_-]{11})$'
        ]

        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        return None

    def _clean_text(self, text: str) -> str:
        """Limpa e normaliza o texto extraído"""
        if not text:
            return ""

        # Remove quebras de linha excessivas
        text = re.sub(r'\n\s*\n', '\n\n', text)

        # Remove espaços excessivos
        text = re.sub(r' +', ' ', text)

        # Remove caracteres especiais problemáticos
        text = re.sub(r'[^\w\s\.,;:!?\-\(\)%$€£¥\n]', '', text)

        # Quebra em linhas
        lines = (line.strip() for line in text.splitlines())

        # Remove linhas muito curtas (provavelmente menu/navegação)
        meaningful_lines = []
        for line in lines:
            if len(line) > 10:  # Linhas com pelo menos 10 caracteres
                meaningful_lines.append(line)

        # Junta linhas significativas
        cleaned_text = '\n'.join(meaningful_lines)

        # Limita tamanho final
        if len(cleaned_text) > 12000:
            cleaned_text = cleaned_text[:12000] + "... [conteúdo truncado para otimização]"

        return cleaned_text.strip()

    def extract_metadata(self, url: str) -> Dict[str, Any]:
        """Extrai metadatos da página"""
        try:
            response = requests.get(
                url,
                headers=self.headers,
                timeout=15,
                allow_redirects=True
            )

            if response.status_code == 200:
                soup = BeautifulSoup(response.content, "html.parser")

                metadata = {
                    'title': '',
                    'description': '',
                    'keywords': '',
                    'author': '',
                    'published_date': '',
                    'language': '',
                    'canonical_url': url
                }

                # Título
                title_tag = soup.find('title')
                if title_tag:
                    metadata['title'] = title_tag.get_text().strip()

                # Meta tags
                meta_tags = soup.find_all('meta')
                for tag in meta_tags:
                    name = tag.get('name', '').lower()
                    property_attr = tag.get('property', '').lower()
                    content = tag.get('content', '')

                    if name == 'description' or property_attr == 'og:description':
                        metadata['description'] = content
                    elif name == 'keywords':
                        metadata['keywords'] = content
                    elif name == 'author':
                        metadata['author'] = content
                    elif name == 'language' or name == 'lang':
                        metadata['language'] = content
                    elif property_attr == 'article:published_time':
                        metadata['published_date'] = content

                # URL canônica
                canonical = soup.find('link', rel='canonical')
                if canonical:
                    metadata['canonical_url'] = canonical.get('href', url)

                return metadata
            else:
                return {'error': f'HTTP {response.status_code}'}

        except Exception as e:
            return {'error': str(e)}

    def is_content_relevant(self, content: str, keywords: list) -> bool:
        """Verifica se o conteúdo é relevante baseado em palavras-chave"""
        if not content or not keywords:
            return False

        content_lower = content.lower()

        # Conta quantas palavras-chave aparecem
        matches = 0
        for keyword in keywords:
            if keyword.lower() in content_lower:
                matches += 1

        # Considera relevante se pelo menos 30% das palavras-chave aparecem
        relevance_threshold = len(keywords) * 0.3
        return matches >= relevance_threshold

    def extract_links(self, url: str, internal_only: bool = True) -> list:
        """Extrai links da página"""
        try:
            response = requests.get(
                url,
                headers=self.headers,
                timeout=15,
                allow_redirects=True
            )

            if response.status_code == 200:
                soup = BeautifulSoup(response.content, "html.parser")
                base_domain = urlparse(url).netloc

                links = []
                for a_tag in soup.find_all('a', href=True):
                    href = a_tag['href']
                    full_url = urljoin(url, href)

                    # Filtra apenas links internos se solicitado
                    if internal_only:
                        link_domain = urlparse(full_url).netloc
                        if link_domain != base_domain:
                            continue

                    # Filtra links válidos
                    if (full_url.startswith('http') and
                        '#' not in full_url and
                        not any(ext in full_url.lower() for ext in ['.pdf', '.jpg', '.png', '.gif', '.zip'])):
                        links.append({
                            'url': full_url,
                            'text': a_tag.get_text().strip()[:100],
                            'title': a_tag.get('title', '')
                        })

                return links[:20]  # Máximo 20 links
            else:
                return []

        except Exception as e:
            logger.error(f"Erro ao extrair links de {url}: {str(e)}")
            return []

    # --- Helper methods for new social media MCPs ---

    def _sanitize_url(self, url: str) -> str:
        """Sanitiza e normaliza a URL."""
        try:
            parsed_url = urlparse(url)
            # Remove fragment and query parameters that might not be relevant for caching/identification
            clean_url = parsed_url._replace(fragment="", query="").geturl()
            return clean_url
        except Exception:
            return url # Return original if parsing fails

    def _identify_social_platform(self, url: str) -> Optional[str]:
        """Identifica a plataforma de rede social a partir da URL."""
        if 'twitter.com' in url or 'x.com' in url:
            return 'twitter'
        elif 'facebook.com' in url:
            return 'facebook'
        elif 'instagram.com' in url:
            return 'instagram'
        elif 'linkedin.com' in url:
            return 'linkedin'
        elif 'youtube.com' in url or 'youtu.be' in url:
            return 'youtube' # Already handled, but good for consistency
        return None

    def _extract_social_content_mcp(self, url: str, platform: str) -> Dict[str, Any]:
        """
        Extrai conteúdo de redes sociais usando estratégias específicas (MCPs).
        Esta é uma implementação de placeholder. Em um cenário real,
        aqui iriam chamadas para APIs específicas ou web scraping mais detalhado.
        """
        logger.info(f"Attempting to extract content from {platform} using MCP for URL: {url}")

        # Placeholder implementation:
        # In a real application, you would integrate with specific APIs or
        # use more advanced scraping techniques tailored to each platform.

        if platform == 'twitter':
            # Example: Try to fetch tweet details
            # You'd need a library like Tweepy or custom scraping here
            return {'success': False, 'message': 'Twitter MCP not fully implemented'}
        elif platform == 'facebook':
            # Similar to Twitter, requires specific handling
            return {'success': False, 'message': 'Facebook MCP not fully implemented'}
        elif platform == 'instagram':
            # Instagram is notoriously difficult to scrape reliably
            return {'success': False, 'message': 'Instagram MCP not fully implemented'}
        elif platform == 'linkedin':
            # LinkedIn also requires careful handling and API access
            return {'success': False, 'message': 'LinkedIn MCP not fully implemented'}
        elif platform == 'youtube':
            # Reuse existing YouTube logic if needed, or specific MCP
            content = self._youtube_api_extraction(url) # Or another YouTube specific method
            if content:
                return {'success': True, 'content': content, 'platform': platform}
            else:
                return {'success': False, 'message': 'YouTube MCP failed'}

        return {'success': False, 'message': f'No specific MCP implemented for {platform}'}


    def _get_cached_result(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """Busca resultado do cache."""
        return self._cache.get(cache_key)

    def _cache_result(self, cache_key: str, result: Dict[str, Any]):
        """Armazena resultado no cache."""
        if len(self._cache) >= self._cache_max_size:
            # Simple eviction: remove the oldest item (not truly LRU but a basic approach)
            oldest_key = next(iter(self._cache))
            del self._cache[oldest_key]
        self._cache[cache_key] = result

    def _create_error_result(self, message: str, processing_time: Optional[float] = None) -> Dict[str, Any]:
        """Cria um dicionário de erro padrão."""
        error_message = f"Erro: {message}"
        logger.error(error_message)
        return {
            'url': None, # Or the problematic URL if available
            'content': None,
            'metadata': None,
            'success': False,
            'error': error_message,
            'processing_time': processing_time if processing_time is not None else 0.0
        }

    def extract_content_from_url(self, url: str, use_readability: bool = True) -> tuple[Optional[str], Optional[str]]:
        """Extrai conteúdo de uma URL usando múltiplas estratégias de fallback com validação rigorosa"""

        if not self._is_valid_url(url):
            logger.warning(f"⚠️ URL inválida: {url}")
            return None, None

        logger.info(f"🔍 Extraindo conteúdo de: {url}")

        # Estratégias ordenadas por prioridade
        strategies = [
            ("requests_readability", self._extract_with_requests_readability),
            ("requests_html", self._extract_with_requests_html),
            ("selenium", self._extract_with_selenium),
            ("beautifulsoup", self._extract_with_beautifulsoup)
        ]

        for strategy_name, strategy_func in strategies:
            try:
                content = strategy_func(url)

                # VALIDAÇÃO RIGOROSA DO CONTEÚDO
                if not self._is_content_valid(content, url):
                    logger.warning(f"⚠️ {strategy_name} - conteúdo inválido ou insuficiente")
                    continue

                # AVALIAÇÃO DE QUALIDADE
                quality_score = self._assess_content_quality(content)
                if quality_score < self.content_quality_threshold:
                    logger.warning(f"⚠️ {strategy_name} - qualidade muito baixa ({quality_score:.1f}%)")
                    continue

                logger.info(f"✅ Sucesso com {strategy_name}: {len(content)} caracteres (qualidade: {quality_score:.1f}%)")
                return content, strategy_name

            except Exception as e:
                logger.error(f"❌ Erro em {strategy_name}: {e}")
                continue

        logger.error(f"❌ Falha em TODAS as estratégias para: {url}")
        return None, None

    def _is_content_valid(self, content: Optional[str], url: str) -> bool:
        """Valida se o conteúdo extraído é suficiente e relevante"""
        if not content:
            logger.warning(f"⚠️ Conteúdo vazio para {url}")
            return False

        # Verificar comprimento mínimo
        if len(content.strip()) < self.min_content_length:
            logger.warning(f"⚠️ Conteúdo insuficiente ({len(content)} caracteres) para {url}")
            return False

        # Verificar se não é apenas HTML/JavaScript sem conteúdo útil
        text_ratio = self._calculate_text_ratio(content)
        if text_ratio < 0.1:  # Menos de 10% de texto útil
            logger.warning(f"⚠️ Muito pouco texto útil ({text_ratio:.1%}) para {url}")
            return False

        # Verificar se não é erro 404, 403, etc
        error_indicators = ['404', '403', 'forbidden', 'not found', 'access denied', 'error']
        content_lower = content.lower()
        if any(indicator in content_lower for indicator in error_indicators) and len(content) < 1000:
            logger.warning(f"⚠️ Possível página de erro para {url}")
            return False

        return True

    def _assess_content_quality(self, content: str) -> float:
        """Avalia a qualidade do texto extraído (0-100)"""
        if not content:
            return 0.0

        quality_score = 0.0

        # 1. Proporção de texto útil vs HTML/código (40 pontos)
        text_ratio = self._calculate_text_ratio(content)
        quality_score += min(text_ratio * 40, 40)

        # 2. Diversidade de palavras (30 pontos)
        words = content.lower().split()
        if words:
            unique_ratio = len(set(words)) / len(words)
            quality_score += min(unique_ratio * 30, 30)

        # 3. Comprimento adequado (20 pontos)
        length_score = min(len(content) / 5000, 1.0) * 20  # Até 5000 chars = 100%
        quality_score += length_score

        # 4. Estrutura de texto (10 pontos)
        sentences = content.count('.') + content.count('!') + content.count('?')
        if sentences > 5:  # Pelo menos 5 sentenças
            quality_score += 10

        return min(quality_score, 100.0)

    def _calculate_text_ratio(self, content: str) -> float:
        """Calcula a proporção de texto útil vs código/HTML"""
        import re

        # Remove HTML tags
        text_without_html = re.sub(r'<[^>]+>', '', content)

        # Remove JavaScript e CSS
        text_without_scripts = re.sub(r'<(script|style)[^>]*>.*?</\1>', '', text_without_html, flags=re.DOTALL | re.IGNORECASE)

        # Remove caracteres especiais excessivos
        clean_text = re.sub(r'[^\w\s\.\,\!\?\-\:\;]', '', text_without_scripts)

        # Calcula proporção
        if len(content) == 0:
            return 0.0

        return len(clean_text.strip()) / len(content)

    # Placeholder methods for strategies used in extract_content_from_url
    def _extract_with_requests_readability(self, url: str) -> Optional[str]:
        """Placeholder for requests_readability strategy."""
        logger.debug("Using placeholder for _extract_with_requests_readability")
        # This would typically use a library like 'readability-lxml'
        # For now, we'll just return a dummy value or call another method if appropriate
        return self._extract_with_readability(url) # Reusing existing for example

    def _extract_with_requests_html(self, url: str) -> Optional[str]:
        """Placeholder for requests_html strategy."""
        logger.debug("Using placeholder for _extract_with_requests_html")
        # This would typically use 'requests-html' library
        return self._extract_direct(url) # Reusing existing for example

    def _extract_with_selenium(self, url: str) -> Optional[str]:
        """Placeholder for selenium strategy."""
        logger.debug("Using placeholder for _extract_with_selenium")
        # This would require Selenium WebDriver setup
        # For now, returning a dummy value
        return None # Replace with actual Selenium logic if implemented

    def _extract_with_beautifulsoup(self, url: str) -> Optional[str]:
        """Placeholder for beautifulsoup strategy."""
        logger.debug("Using placeholder for _extract_with_beautifulsoup")
        # This is already covered by _extract_direct, but keeping for clarity
        return self._extract_direct(url)

    def _is_valid_url(self, url: str) -> bool:
        """Valida o formato básico da URL."""
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc]) and result.scheme in ['http', 'https']
        except ValueError:
            return False


# Instância global
content_extractor = ContentExtractor()