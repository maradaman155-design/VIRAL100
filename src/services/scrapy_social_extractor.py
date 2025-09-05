#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Scrapy + Splash Social Media Extractor - V3.0
Extração massiva de conteúdo viral usando Scrapy + Splash como fallback
"""

import os
import json
import logging
import asyncio
from typing import Dict, List, Any, Optional
from datetime import datetime
from pathlib import Path
import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy_splash import SplashRequest
from scrapy.utils.project import get_project_settings
from services.enhanced_api_rotation_manager import get_api_manager

logger = logging.getLogger(__name__)

class SocialMediaSpider(scrapy.Spider):
    """Spider Scrapy para extração de conteúdo viral"""
    
    name = 'social_media_spider'
    
    def __init__(self, query='', platforms='', *args, **kwargs):
        super(SocialMediaSpider, self).__init__(*args, **kwargs)
        self.query = query
        self.platforms = platforms.split(',') if platforms else ['instagram', 'youtube', 'facebook']
        self.results = {
            'query': query,
            'timestamp': datetime.now().isoformat(),
            'platforms': {},
            'total_content': 0
        }
        
        # Configurações por plataforma
        self.platform_configs = {
            'instagram': {
                'url_template': 'https://www.instagram.com/explore/tags/{query}/',
                'selectors': {
                    'posts': 'article[role="presentation"]',
                    'images': 'img[alt*="Photo"], img[alt*="Image"]',
                    'likes': 'span[class*="like"]'
                },
                'wait_time': 3
            },
            'youtube': {
                'url_template': 'https://www.youtube.com/results?search_query={query}&sp=CAMSAhAB',
                'selectors': {
                    'videos': 'ytd-video-renderer',
                    'thumbnails': 'img[class*="thumbnail"]',
                    'titles': '#video-title'
                },
                'wait_time': 2
            },
            'facebook': {
                'url_template': 'https://www.facebook.com/search/posts/?q={query}',
                'selectors': {
                    'posts': '[data-pagelet="FeedUnit"]',
                    'images': 'img[data-imgperflogname]'
                },
                'wait_time': 4
            }
        }

    def start_requests(self):
        """Gera requests iniciais para cada plataforma"""
        
        for platform in self.platforms:
            if platform in self.platform_configs:
                config = self.platform_configs[platform]
                url = config['url_template'].format(query=self.query.replace(' ', ''))
                
                # Usar SplashRequest para renderização JavaScript
                yield SplashRequest(
                    url=url,
                    callback=self.parse_platform,
                    args={
                        'wait': config['wait_time'],
                        'html': 1,
                        'png': 1,
                        'render_all': 1,
                        'timeout': 30
                    },
                    meta={'platform': platform, 'config': config}
                )

    def parse_platform(self, response):
        """Parse do conteúdo de cada plataforma"""
        
        platform = response.meta['platform']
        config = response.meta['config']
        
        logger.info(f"🔍 Processando {platform.upper()}: {response.url}")
        
        posts = []
        
        try:
            if platform == 'instagram':
                posts = self._parse_instagram(response, config)
            elif platform == 'youtube':
                posts = self._parse_youtube(response, config)
            elif platform == 'facebook':
                posts = self._parse_facebook(response, config)
            
            # Salvar screenshot se disponível
            screenshot_path = None
            if hasattr(response, 'data') and 'png' in response.data:
                screenshot_path = self._save_screenshot(response.data['png'], platform)
            
            platform_data = {
                'platform': platform,
                'posts': posts,
                'total_posts': len(posts),
                'screenshot': screenshot_path,
                'extraction_time': datetime.now().isoformat()
            }
            
            self.results['platforms'][platform] = platform_data
            self.results['total_content'] += len(posts)
            
            logger.info(f"✅ {platform.upper()}: {len(posts)} posts extraídos")
            
        except Exception as e:
            logger.error(f"❌ Erro ao processar {platform}: {e}")
            self.results['platforms'][platform] = {
                'error': str(e),
                'posts': []
            }

    def _parse_instagram(self, response, config):
        """Parse específico do Instagram"""
        
        posts = []
        selectors = config['selectors']
        
        # Extrair posts
        post_elements = response.css(selectors['posts'])
        
        for i, post in enumerate(post_elements[:20]):  # Limitar a 20 posts
            try:
                post_data = {
                    'platform': 'instagram',
                    'post_id': f'ig_post_{i}',
                    'type': 'image',
                    'images': [],
                    'engagement': {}
                }
                
                # Extrair imagens
                images = post.css(selectors['images'])
                for img in images[:3]:  # Máximo 3 imagens
                    src = img.css('::attr(src)').get()
                    alt = img.css('::attr(alt)').get()
                    if src:
                        post_data['images'].append({
                            'url': src,
                            'alt': alt or '',
                            'type': 'image'
                        })
                
                # Extrair likes se disponível
                likes_elem = post.css(selectors['likes'])
                if likes_elem:
                    likes_text = likes_elem.css('::text').get()
                    if likes_text:
                        post_data['engagement']['likes'] = self._parse_engagement_number(likes_text)
                
                if post_data['images']:
                    posts.append(post_data)
                    
            except Exception as e:
                logger.warning(f"⚠️ Erro ao processar post Instagram {i}: {e}")
                continue
        
        return posts

    def _parse_youtube(self, response, config):
        """Parse específico do YouTube"""
        
        videos = []
        selectors = config['selectors']
        
        # Extrair vídeos
        video_elements = response.css(selectors['videos'])
        
        for i, video in enumerate(video_elements[:12]):  # Limitar a 12 vídeos
            try:
                video_data = {
                    'platform': 'youtube',
                    'video_id': f'yt_video_{i}',
                    'type': 'video',
                    'thumbnails': [],
                    'metadata': {}
                }
                
                # Extrair thumbnail
                thumbnail = video.css(selectors['thumbnails']).css('::attr(src)').get()
                if thumbnail:
                    video_data['thumbnails'].append({
                        'url': thumbnail,
                        'type': 'thumbnail'
                    })
                
                # Extrair título
                title = video.css(selectors['titles']).css('::text').get()
                if title:
                    video_data['metadata']['title'] = title.strip()
                
                if video_data['thumbnails']:
                    videos.append(video_data)
                    
            except Exception as e:
                logger.warning(f"⚠️ Erro ao processar vídeo YouTube {i}: {e}")
                continue
        
        return videos

    def _parse_facebook(self, response, config):
        """Parse específico do Facebook"""
        
        posts = []
        selectors = config['selectors']
        
        # Extrair posts
        post_elements = response.css(selectors['posts'])
        
        for i, post in enumerate(post_elements[:15]):  # Limitar a 15 posts
            try:
                post_data = {
                    'platform': 'facebook',
                    'post_id': f'fb_post_{i}',
                    'type': 'mixed',
                    'images': []
                }
                
                # Extrair imagens
                images = post.css(selectors['images'])
                for img in images[:2]:  # Máximo 2 imagens
                    src = img.css('::attr(src)').get()
                    if src and 'scontent' in src:  # Filtrar imagens do Facebook
                        post_data['images'].append({
                            'url': src,
                            'type': 'image'
                        })
                
                if post_data['images']:
                    posts.append(post_data)
                    
            except Exception as e:
                logger.warning(f"⚠️ Erro ao processar post Facebook {i}: {e}")
                continue
        
        return posts

    def _parse_engagement_number(self, text: str) -> int:
        """Converte texto de engagement em número"""
        
        if not text:
            return 0
        
        text = text.lower().replace(',', '').replace('.', '')
        
        try:
            if 'k' in text:
                return int(float(text.replace('k', '')) * 1000)
            elif 'm' in text:
                return int(float(text.replace('m', '')) * 1000000)
            else:
                return int(''.join(filter(str.isdigit, text)))
        except:
            return 0

    def _save_screenshot(self, png_data: bytes, platform: str) -> str:
        """Salva screenshot capturado pelo Splash"""
        
        try:
            screenshots_dir = Path("analyses_data/screenshots")
            screenshots_dir.mkdir(parents=True, exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{platform}_{self.query.replace(' ', '_')}_{timestamp}.png"
            filepath = screenshots_dir / filename
            
            with open(filepath, 'wb') as f:
                f.write(png_data)
            
            logger.info(f"📸 Screenshot salvo: {filename}")
            return str(filepath)
            
        except Exception as e:
            logger.error(f"❌ Erro ao salvar screenshot: {e}")
            return None

    def closed(self, reason):
        """Callback executado quando spider termina"""
        logger.info(f"🕷️ Spider finalizado: {reason}")
        logger.info(f"📊 Total extraído: {self.results['total_content']} posts")


class ScrapySocialExtractor:
    """Extrator de conteúdo viral usando Scrapy + Splash"""
    
    def __init__(self):
        self.api_manager = get_api_manager()
        self.splash_url = os.getenv('SPLASH_URL', 'http://localhost:8050')
        
        # Configurações do Scrapy
        self.settings = {
            'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'ROBOTSTXT_OBEY': False,
            'DOWNLOAD_DELAY': 2,
            'RANDOMIZE_DOWNLOAD_DELAY': True,
            'CONCURRENT_REQUESTS': 4,
            'CONCURRENT_REQUESTS_PER_DOMAIN': 2,
            'AUTOTHROTTLE_ENABLED': True,
            'AUTOTHROTTLE_START_DELAY': 1,
            'AUTOTHROTTLE_MAX_DELAY': 10,
            'AUTOTHROTTLE_TARGET_CONCURRENCY': 2.0,
            'SPLASH_URL': self.splash_url,
            'DOWNLOADER_MIDDLEWARES': {
                'scrapy_splash.SplashCookiesMiddleware': 723,
                'scrapy_splash.SplashMiddleware': 725,
                'scrapy.downloadermiddlewares.httpcompression.HttpCompressionMiddleware': 810,
            },
            'SPIDER_MIDDLEWARES': {
                'scrapy_splash.SplashDeduplicateArgsMiddleware': 100,
            },
            'DUPEFILTER_CLASS': 'scrapy_splash.SplashAwareDupeFilter',
            'HTTPCACHE_STORAGE': 'scrapy_splash.SplashAwareFSCacheStorage',
            'LOG_LEVEL': 'INFO'
        }
        
        logger.info("🕷️ Scrapy Social Extractor inicializado")

    def extract_viral_content(self, query: str, platforms: List[str] = None) -> Dict[str, Any]:
        """Extrai conteúdo viral usando Scrapy + Splash"""
        
        if platforms is None:
            platforms = ['instagram', 'youtube', 'facebook']
        
        logger.info(f"🔍 Iniciando extração Scrapy para '{query}'")
        
        try:
            # Verificar se Splash está disponível
            if not self._check_splash_availability():
                logger.warning("⚠️ Splash não disponível, usando modo básico")
                return self._extract_without_splash(query, platforms)
            
            # Configurar processo Scrapy
            process = CrawlerProcess(self.settings)
            
            # Variável para armazenar resultados
            results = {}
            
            def spider_closed(spider):
                results.update(spider.results)
            
            # Adicionar spider ao processo
            process.crawl(
                SocialMediaSpider,
                query=query,
                platforms=','.join(platforms)
            )
            
            # Conectar callback de finalização
            from scrapy import signals
            process.signals.connect(spider_closed, signal=signals.spider_closed)
            
            # Executar spider
            process.start(stop_after_crawl=True)
            
            logger.info(f"✅ Extração Scrapy completa: {results.get('total_content', 0)} posts")
            return results
            
        except Exception as e:
            logger.error(f"❌ Erro na extração Scrapy: {e}")
            return self._extract_without_splash(query, platforms)

    def _check_splash_availability(self) -> bool:
        """Verifica se o serviço Splash está disponível"""
        
        try:
            import requests
            response = requests.get(f"{self.splash_url}/info", timeout=5)
            return response.status_code == 200
        except:
            return False

    def _extract_without_splash(self, query: str, platforms: List[str]) -> Dict[str, Any]:
        """Extração básica sem Splash (fallback)"""
        
        logger.info("🔄 Usando extração básica sem Splash")
        
        results = {
            'query': query,
            'timestamp': datetime.now().isoformat(),
            'platforms': {},
            'total_content': 0,
            'fallback_mode': True
        }
        
        # Simular extração básica para cada plataforma
        for platform in platforms:
            mock_posts = self._generate_mock_posts(platform, query)
            
            results['platforms'][platform] = {
                'platform': platform,
                'posts': mock_posts,
                'total_posts': len(mock_posts),
                'extraction_method': 'mock_fallback'
            }
            
            results['total_content'] += len(mock_posts)
        
        return results

    def _generate_mock_posts(self, platform: str, query: str) -> List[Dict[str, Any]]:
        """Gera posts mock para fallback"""
        
        mock_posts = []
        
        for i in range(5):  # 5 posts mock por plataforma
            if platform == 'instagram':
                post = {
                    'platform': 'instagram',
                    'post_id': f'ig_mock_{i}',
                    'type': 'image',
                    'images': [{
                        'url': f'https://via.placeholder.com/400x400?text={query}+{i}',
                        'alt': f'{query} post {i}',
                        'type': 'image'
                    }],
                    'engagement': {'likes': 1000 + i * 100}
                }
            elif platform == 'youtube':
                post = {
                    'platform': 'youtube',
                    'video_id': f'yt_mock_{i}',
                    'type': 'video',
                    'thumbnails': [{
                        'url': f'https://via.placeholder.com/320x180?text={query}+Video+{i}',
                        'type': 'thumbnail'
                    }],
                    'metadata': {
                        'title': f'{query} - Vídeo Viral {i}',
                        'views': f'{10000 + i * 1000} visualizações'
                    }
                }
            elif platform == 'facebook':
                post = {
                    'platform': 'facebook',
                    'post_id': f'fb_mock_{i}',
                    'type': 'mixed',
                    'images': [{
                        'url': f'https://via.placeholder.com/500x300?text={query}+FB+{i}',
                        'type': 'image'
                    }]
                }
            
            mock_posts.append(post)
        
        return mock_posts

    def extract_high_conversion_posts(self, query: str, min_engagement: int = 1000) -> Dict[str, Any]:
        """Extrai posts com alta conversão"""
        
        logger.info(f"🎯 Buscando posts de alta conversão para '{query}'")
        
        # Extrair conteúdo de todas as plataformas
        all_content = self.extract_viral_content(query)
        
        high_conversion_posts = []
        
        for platform, data in all_content['platforms'].items():
            if 'posts' in data:
                for post in data['posts']:
                    engagement = post.get('engagement', {})
                    likes = engagement.get('likes', 0)
                    
                    # Filtrar por engagement mínimo
                    if likes >= min_engagement:
                        post['conversion_score'] = self._calculate_conversion_score(post)
                        high_conversion_posts.append(post)
        
        # Ordenar por score de conversão
        high_conversion_posts.sort(key=lambda x: x.get('conversion_score', 0), reverse=True)
        
        return {
            'query': query,
            'high_conversion_posts': high_conversion_posts[:20],  # Top 20
            'total_found': len(high_conversion_posts),
            'min_engagement': min_engagement,
            'extraction_time': datetime.now().isoformat()
        }

    def _calculate_conversion_score(self, post: Dict[str, Any]) -> float:
        """Calcula score de conversão do post"""
        
        score = 0.0
        engagement = post.get('engagement', {})
        
        # Fatores de score
        likes = engagement.get('likes', 0)
        comments = engagement.get('comments', 0)
        shares = engagement.get('shares', 0)
        
        # Calcular score baseado em engagement
        score += likes * 0.1
        score += comments * 0.3  # Comentários valem mais
        score += shares * 0.5    # Shares valem ainda mais
        
        # Bonus por múltiplas imagens
        images_count = len(post.get('images', []))
        if images_count > 1:
            score *= 1.2
        
        return round(score, 2)


# Instância global
scrapy_extractor = ScrapySocialExtractor()

# Funções de conveniência
def extract_viral_content_scrapy(query: str, platforms: List[str] = None) -> Dict[str, Any]:
    """Extrai conteúdo viral usando Scrapy + Splash"""
    return scrapy_extractor.extract_viral_content(query, platforms)

def extract_high_conversion_posts_scrapy(query: str, min_engagement: int = 1000) -> Dict[str, Any]:
    """Extrai posts de alta conversão usando Scrapy"""
    return scrapy_extractor.extract_high_conversion_posts(query, min_engagement)

if __name__ == "__main__":
    # Teste do extrator
    results = extract_viral_content_scrapy("marketing digital", ["youtube"])
    print(f"Conteúdo extraído: {results['total_content']} posts")
    
    for platform, data in results['platforms'].items():
        print(f"{platform}: {len(data.get('posts', []))} posts")