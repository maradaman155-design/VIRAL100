"""
Viral Content Analyzer - Analisador de conteúdo viral
Responsável por captura de screenshots e análise de mídias sociais
"""

import os
import asyncio
import httpx
import json
import base64
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
import re
from urllib.parse import urlparse, parse_qs
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from PIL import Image
import io
import time


@dataclass
class ViralContent:
    """Estrutura para conteúdo viral"""
    platform: str
    url: str
    title: str
    description: str
    author: str
    engagement_metrics: Dict[str, int]
    screenshot_path: str
    content_type: str
    hashtags: List[str]
    mentions: List[str]
    timestamp: str
    virality_score: float


@dataclass
class SocialMetrics:
    """Métricas de engajamento social"""
    likes: int = 0
    shares: int = 0
    comments: int = 0
    views: int = 0
    reactions: int = 0
    saves: int = 0


class ViralContentAnalyzer:
    """
    Analisador de conteúdo viral com captura de screenshots
    """
    
    def __init__(self):
        self.session = httpx.AsyncClient(timeout=30.0)
        self.instagram_token = os.getenv('INSTAGRAM_ACCESS_TOKEN')
        self.facebook_token = os.getenv('FACEBOOK_ACCESS_TOKEN')
        self.youtube_api_key = os.getenv('YOUTUBE_API_KEY')
        self.screenshot_dir = os.path.join(os.getcwd(), 'analyses_data', 'screenshots')
        os.makedirs(self.screenshot_dir, exist_ok=True)
        
    async def __aenter__(self):
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.session.aclose()
    
    def _setup_selenium_driver(self, mobile: bool = False) -> webdriver.Chrome:
        """Configura driver Selenium para captura de screenshots"""
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        
        if mobile:
            chrome_options.add_argument('--window-size=375,812')  # iPhone X size
            chrome_options.add_argument('--user-agent=Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X)')
        else:
            chrome_options.add_argument('--window-size=1920,1080')
            chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
        
        return webdriver.Chrome(options=chrome_options)
    
    async def capture_screenshot(self, url: str, filename: str, 
                                mobile: bool = False, full_page: bool = True) -> str:
        """
        Captura screenshot de uma URL
        """
        try:
            driver = self._setup_selenium_driver(mobile)
            driver.get(url)
            
            # Aguarda carregamento
            WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # Scroll para carregar conteúdo dinâmico
            if full_page:
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(3)
                driver.execute_script("window.scrollTo(0, 0);")
                time.sleep(2)
            
            # Remove elementos que podem atrapalhar
            driver.execute_script("""
                // Remove cookie banners, popups, etc.
                var elements = document.querySelectorAll('[class*="cookie"], [class*="popup"], [class*="modal"], [id*="cookie"], [id*="popup"]');
                elements.forEach(function(element) {
                    element.style.display = 'none';
                });
            """)
            
            screenshot_path = os.path.join(self.screenshot_dir, filename)
            
            if full_page:
                # Screenshot da página inteira
                total_height = driver.execute_script("return document.body.scrollHeight")
                driver.set_window_size(1920, total_height)
                time.sleep(2)
            
            driver.save_screenshot(screenshot_path)
            driver.quit()
            
            return screenshot_path
            
        except Exception as e:
            print(f"Erro ao capturar screenshot de {url}: {e}")
            return ""
    
    async def analyze_instagram_content(self, hashtag: str, limit: int = 20) -> List[ViralContent]:
        """
        Analisa conteúdo do Instagram por hashtag
        """
        if not self.instagram_token:
            return []
        
        # Instagram Basic Display API é limitada, simulamos análise
        viral_contents = []
        
        try:
            # Busca posts por hashtag (simulado - API real requer aprovação)
            posts_data = await self._simulate_instagram_search(hashtag, limit)
            
            for post in posts_data:
                screenshot_filename = f"instagram_{post['id']}_{int(time.time())}.png"
                screenshot_path = await self.capture_screenshot(
                    post['url'], screenshot_filename, mobile=True
                )
                
                viral_content = ViralContent(
                    platform="Instagram",
                    url=post['url'],
                    title=post.get('caption', '')[:100],
                    description=post.get('caption', ''),
                    author=post.get('username', ''),
                    engagement_metrics={
                        'likes': post.get('likes', 0),
                        'comments': post.get('comments', 0),
                        'shares': post.get('shares', 0)
                    },
                    screenshot_path=screenshot_path,
                    content_type=post.get('media_type', 'image'),
                    hashtags=self._extract_hashtags(post.get('caption', '')),
                    mentions=self._extract_mentions(post.get('caption', '')),
                    timestamp=post.get('timestamp', ''),
                    virality_score=self._calculate_virality_score(post, 'instagram')
                )
                
                viral_contents.append(viral_content)
                
        except Exception as e:
            print(f"Erro ao analisar Instagram: {e}")
        
        return viral_contents
    
    async def analyze_youtube_content(self, query: str, limit: int = 20) -> List[ViralContent]:
        """
        Analisa conteúdo do YouTube
        """
        if not self.youtube_api_key:
            return []
        
        viral_contents = []
        
        try:
            # Busca vídeos
            search_url = "https://www.googleapis.com/youtube/v3/search"
            search_params = {
                'part': 'snippet',
                'q': query,
                'type': 'video',
                'maxResults': limit,
                'order': 'relevance',
                'key': self.youtube_api_key
            }
            
            response = await self.session.get(search_url, params=search_params)
            response.raise_for_status()
            search_data = response.json()
            
            # Busca estatísticas dos vídeos
            video_ids = [item['id']['videoId'] for item in search_data.get('items', [])]
            
            if video_ids:
                stats_url = "https://www.googleapis.com/youtube/v3/videos"
                stats_params = {
                    'part': 'statistics,snippet',
                    'id': ','.join(video_ids),
                    'key': self.youtube_api_key
                }
                
                stats_response = await self.session.get(stats_url, params=stats_params)
                stats_response.raise_for_status()
                stats_data = stats_response.json()
                
                for video in stats_data.get('items', []):
                    video_id = video['id']
                    video_url = f"https://www.youtube.com/watch?v={video_id}"
                    
                    screenshot_filename = f"youtube_{video_id}_{int(time.time())}.png"
                    screenshot_path = await self.capture_screenshot(
                        video_url, screenshot_filename
                    )
                    
                    stats = video.get('statistics', {})
                    snippet = video.get('snippet', {})
                    
                    viral_content = ViralContent(
                        platform="YouTube",
                        url=video_url,
                        title=snippet.get('title', ''),
                        description=snippet.get('description', ''),
                        author=snippet.get('channelTitle', ''),
                        engagement_metrics={
                            'views': int(stats.get('viewCount', 0)),
                            'likes': int(stats.get('likeCount', 0)),
                            'comments': int(stats.get('commentCount', 0)),
                            'shares': 0  # YouTube não fornece shares via API
                        },
                        screenshot_path=screenshot_path,
                        content_type='video',
                        hashtags=self._extract_hashtags(snippet.get('description', '')),
                        mentions=[],
                        timestamp=snippet.get('publishedAt', ''),
                        virality_score=self._calculate_virality_score(
                            {'stats': stats, 'snippet': snippet}, 'youtube'
                        )
                    )
                    
                    viral_contents.append(viral_content)
                    
        except Exception as e:
            print(f"Erro ao analisar YouTube: {e}")
        
        return viral_contents
    
    async def analyze_facebook_content(self, query: str, limit: int = 20) -> List[ViralContent]:
        """
        Analisa conteúdo do Facebook (simulado devido a limitações da API)
        """
        viral_contents = []
        
        try:
            # Simula busca no Facebook
            facebook_data = await self._simulate_facebook_search(query, limit)
            
            for post in facebook_data:
                screenshot_filename = f"facebook_{post['id']}_{int(time.time())}.png"
                screenshot_path = await self.capture_screenshot(
                    post['url'], screenshot_filename
                )
                
                viral_content = ViralContent(
                    platform="Facebook",
                    url=post['url'],
                    title=post.get('message', '')[:100],
                    description=post.get('message', ''),
                    author=post.get('from', {}).get('name', ''),
                    engagement_metrics={
                        'likes': post.get('reactions', 0),
                        'comments': post.get('comments', 0),
                        'shares': post.get('shares', 0)
                    },
                    screenshot_path=screenshot_path,
                    content_type=post.get('type', 'status'),
                    hashtags=self._extract_hashtags(post.get('message', '')),
                    mentions=self._extract_mentions(post.get('message', '')),
                    timestamp=post.get('created_time', ''),
                    virality_score=self._calculate_virality_score(post, 'facebook')
                )
                
                viral_contents.append(viral_content)
                
        except Exception as e:
            print(f"Erro ao analisar Facebook: {e}")
        
        return viral_contents
    
    def _extract_hashtags(self, text: str) -> List[str]:
        """Extrai hashtags do texto"""
        hashtag_pattern = r'#\w+'
        hashtags = re.findall(hashtag_pattern, text)
        return [tag.lower() for tag in hashtags]
    
    def _extract_mentions(self, text: str) -> List[str]:
        """Extrai menções do texto"""
        mention_pattern = r'@\w+'
        mentions = re.findall(mention_pattern, text)
        return [mention.lower() for mention in mentions]
    
    def _calculate_virality_score(self, content_data: Dict, platform: str) -> float:
        """
        Calcula score de viralidade baseado na plataforma
        """
        score = 0.0
        
        if platform == 'youtube':
            stats = content_data.get('stats', {})
            views = int(stats.get('viewCount', 0))
            likes = int(stats.get('likeCount', 0))
            comments = int(stats.get('commentCount', 0))
            
            # Score baseado em views (normalizado)
            if views > 1000000:  # 1M+ views
                score += 10.0
            elif views > 100000:  # 100K+ views
                score += 7.0
            elif views > 10000:  # 10K+ views
                score += 5.0
            elif views > 1000:  # 1K+ views
                score += 3.0
            
            # Score baseado em engagement rate
            if views > 0:
                engagement_rate = (likes + comments) / views
                score += min(engagement_rate * 100, 5.0)
                
        elif platform == 'instagram':
            likes = content_data.get('likes', 0)
            comments = content_data.get('comments', 0)
            
            total_engagement = likes + comments
            if total_engagement > 10000:
                score += 10.0
            elif total_engagement > 1000:
                score += 7.0
            elif total_engagement > 100:
                score += 5.0
            elif total_engagement > 10:
                score += 3.0
                
        elif platform == 'facebook':
            reactions = content_data.get('reactions', 0)
            comments = content_data.get('comments', 0)
            shares = content_data.get('shares', 0)
            
            total_engagement = reactions + comments + (shares * 2)  # Shares valem mais
            if total_engagement > 5000:
                score += 10.0
            elif total_engagement > 500:
                score += 7.0
            elif total_engagement > 50:
                score += 5.0
            elif total_engagement > 5:
                score += 3.0
        
        return min(score, 10.0)  # Cap at 10.0
    
    async def _simulate_instagram_search(self, hashtag: str, limit: int) -> List[Dict]:
        """Simula busca no Instagram (para demonstração)"""
        # Em produção, usaria Instagram Basic Display API ou Graph API
        return [
            {
                'id': f'ig_{i}',
                'url': f'https://instagram.com/p/example{i}',
                'caption': f'Post sobre {hashtag} #{hashtag} #viral',
                'username': f'user_{i}',
                'likes': 1000 + i * 100,
                'comments': 50 + i * 10,
                'shares': 20 + i * 5,
                'media_type': 'image',
                'timestamp': datetime.now().isoformat()
            }
            for i in range(limit)
        ]
    
    async def _simulate_facebook_search(self, query: str, limit: int) -> List[Dict]:
        """Simula busca no Facebook (para demonstração)"""
        return [
            {
                'id': f'fb_{i}',
                'url': f'https://facebook.com/posts/example{i}',
                'message': f'Post sobre {query} muito viral!',
                'from': {'name': f'Page {i}'},
                'reactions': 500 + i * 50,
                'comments': 25 + i * 5,
                'shares': 10 + i * 2,
                'type': 'status',
                'created_time': datetime.now().isoformat()
            }
            for i in range(limit)
        ]
    
    async def analyze_trending_content(self, segment: str, platforms: List[str] = None) -> Dict[str, List[ViralContent]]:
        """
        Analisa conteúdo em tendência por segmento
        """
        if platforms is None:
            platforms = ['youtube', 'instagram', 'facebook']
        
        trending_content = {}
        
        for platform in platforms:
            if platform == 'youtube':
                content = await self.analyze_youtube_content(segment, 10)
            elif platform == 'instagram':
                content = await self.analyze_instagram_content(segment, 10)
            elif platform == 'facebook':
                content = await self.analyze_facebook_content(segment, 10)
            else:
                content = []
            
            trending_content[platform] = content
        
        return trending_content
    
    async def generate_virality_report(self, content_list: List[ViralContent]) -> Dict[str, Any]:
        """
        Gera relatório de viralidade
        """
        if not content_list:
            return {}
        
        # Estatísticas gerais
        total_content = len(content_list)
        platforms = list(set(content.platform for content in content_list))
        avg_virality = sum(content.virality_score for content in content_list) / total_content
        
        # Top hashtags
        all_hashtags = []
        for content in content_list:
            all_hashtags.extend(content.hashtags)
        
        hashtag_counts = {}
        for hashtag in all_hashtags:
            hashtag_counts[hashtag] = hashtag_counts.get(hashtag, 0) + 1
        
        top_hashtags = sorted(hashtag_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        
        # Conteúdo mais viral por plataforma
        platform_top = {}
        for platform in platforms:
            platform_content = [c for c in content_list if c.platform == platform]
            if platform_content:
                platform_top[platform] = max(platform_content, key=lambda x: x.virality_score)
        
        report = {
            'summary': {
                'total_content': total_content,
                'platforms_analyzed': platforms,
                'average_virality_score': round(avg_virality, 2),
                'analysis_timestamp': datetime.now().isoformat()
            },
            'top_hashtags': top_hashtags,
            'platform_leaders': {
                platform: {
                    'title': content.title,
                    'url': content.url,
                    'virality_score': content.virality_score,
                    'engagement_metrics': content.engagement_metrics
                }
                for platform, content in platform_top.items()
            },
            'content_distribution': {
                platform: len([c for c in content_list if c.platform == platform])
                for platform in platforms
            }
        }
        
        return report

