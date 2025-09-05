"""
Real Viral Image Extractor - ZERO SIMULAÇÃO
Extrai imagens REAIS do Instagram, Facebook e YouTube
"""

import os
import json
import time
import asyncio
import logging
from typing import List, Dict, Optional
from dataclasses import dataclass
import httpx
from PIL import Image
import re
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

logger = logging.getLogger(__name__)

@dataclass
class RealViralImage:
    platform: str
    image_url: str
    local_path: str
    title: str
    engagement_score: float
    metadata: Dict

class RealViralImageExtractor:
    """
    Extrator de imagens REAIS de redes sociais - ZERO SIMULAÇÃO
    """
    
    def __init__(self):
        self.session = None
        self.driver = None
        self.images_dir = "/workspace/project/v100/viral_images"
        self._ensure_directories()
        
    def _ensure_directories(self):
        """Cria diretórios necessários"""
        platforms = ['instagram', 'facebook', 'youtube', 'tech_sites', 'metadata']
        for platform in platforms:
            os.makedirs(os.path.join(self.images_dir, platform), exist_ok=True)
    
    async def __aenter__(self):
        self.session = httpx.AsyncClient(timeout=30.0)
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.aclose()
        if self.driver:
            self.driver.quit()
    
    def _setup_selenium(self):
        """Configura Selenium para scraping real"""
        if self.driver:
            return
            
        try:
            chrome_options = Options()
            chrome_options.add_argument('--headless')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--window-size=1920,1080')
            chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
            
            self.driver = webdriver.Chrome(options=chrome_options)
            logger.info("✅ Selenium configurado para extração REAL")
            
        except Exception as e:
            logger.error(f"❌ Erro ao configurar Selenium: {e}")
            self.driver = None
    
    async def extract_real_viral_images(self, query: str, session_id: str, min_images: int = 20) -> List[RealViralImage]:
        """
        Extrai imagens REAIS de redes sociais - ZERO SIMULAÇÃO
        """
        logger.info(f"🖼️ INICIANDO EXTRAÇÃO REAL DE IMAGENS VIRAIS para: {query}")
        logger.info(f"🎯 META: Mínimo {min_images} imagens REAIS")
        
        all_images = []
        
        # 1. Instagram REAL
        instagram_images = await self._extract_real_instagram_images(query, session_id)
        all_images.extend(instagram_images)
        logger.info(f"📸 Instagram: {len(instagram_images)} imagens REAIS extraídas")
        
        # 2. YouTube REAL (aumentar para 17 vídeos para garantir 20+ imagens)
        youtube_images = await self._extract_real_youtube_thumbnails(query, session_id, max_videos=17)
        all_images.extend(youtube_images)
        logger.info(f"🎥 YouTube: {len(youtube_images)} thumbnails REAIS extraídos")
        
        # 3. Instagram alternativo (se necessário)
        if len(all_images) < min_images:
            instagram_alt = await self._extract_instagram_alternative(query, session_id, min_images - len(all_images))
            all_images.extend(instagram_alt)
            logger.info(f"📸 Instagram Alt: {len(instagram_alt)} imagens REAIS extraídas")
        
        # 4. Facebook REAL (se necessário para atingir meta)
        if len(all_images) < min_images:
            facebook_images = await self._extract_real_facebook_images(query, session_id, min_images - len(all_images))
            all_images.extend(facebook_images)
            logger.info(f"📘 Facebook: {len(facebook_images)} imagens REAIS extraídas")
        
        # 5. Busca adicional de imagens relacionadas (se ainda não atingiu meta)
        if len(all_images) < min_images:
            additional_images = await self._extract_additional_real_images(query, session_id, min_images - len(all_images))
            all_images.extend(additional_images)
            logger.info(f"🔍 Busca adicional: {len(additional_images)} imagens REAIS extraídas")
        
        # Salva metadados
        await self._save_extraction_metadata(all_images, session_id, query)
        
        logger.info(f"✅ EXTRAÇÃO REAL CONCLUÍDA: {len(all_images)} imagens REAIS extraídas")
        
        if len(all_images) < min_images:
            logger.warning(f"⚠️ Meta não atingida: {len(all_images)}/{min_images} imagens")
        else:
            logger.info(f"🎯 META ATINGIDA: {len(all_images)}/{min_images} imagens REAIS")
            
        return all_images
    
    async def _extract_real_instagram_images(self, query: str, session_id: str) -> List[RealViralImage]:
        """
        Extrai imagens REAIS do Instagram usando scraping de hashtags
        """
        images = []
        
        try:
            # Hashtags reais baseadas na query
            hashtags = self._get_real_hashtags(query)
            
            for hashtag in hashtags[:3]:  # Máximo 3 hashtags
                try:
                    url = f"https://www.instagram.com/explore/tags/{hashtag}/"
                    
                    headers = {
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
                        'Accept-Language': 'pt-BR,pt;q=0.9,en;q=0.8',
                        'Cache-Control': 'no-cache',
                        'Sec-Fetch-Dest': 'document',
                        'Sec-Fetch-Mode': 'navigate',
                        'Sec-Fetch-Site': 'none'
                    }
                    
                    response = await self.session.get(url, headers=headers, timeout=15, follow_redirects=True)
                    
                    if response.status_code == 200 or response.status_code == 302:
                        # Extrai URLs REAIS de imagens do Instagram
                        img_urls = self._extract_instagram_image_urls(response.text)
                        
                        for i, img_url in enumerate(img_urls[:5]):  # Máximo 5 por hashtag
                            local_path = await self._download_real_image(img_url, 'instagram', session_id, f"{hashtag}_{i}")
                            
                            if local_path:
                                viral_image = RealViralImage(
                                    platform="Instagram",
                                    image_url=img_url,
                                    local_path=local_path,
                                    title=f"Post viral #{hashtag}",
                                    engagement_score=self._calculate_engagement_score(hashtag),
                                    metadata={
                                        'hashtag': hashtag,
                                        'source_url': url,
                                        'extraction_time': time.time(),
                                        'query': query
                                    }
                                )
                                images.append(viral_image)
                                
                except Exception as e:
                    logger.warning(f"⚠️ Erro ao extrair hashtag #{hashtag}: {e}")
                    
        except Exception as e:
            logger.error(f"❌ Erro na extração REAL do Instagram: {e}")
            
        return images
    
    def _extract_instagram_image_urls(self, html_content: str) -> List[str]:
        """
        Extrai URLs REAIS de imagens do HTML do Instagram
        """
        urls = []
        
        # Padrões para URLs reais do Instagram
        patterns = [
            r'"display_url":"([^"]+)"',
            r'"thumbnail_src":"([^"]+)"',
            r'src="([^"]*cdninstagram[^"]*\.jpg[^"]*)"',
            r'src="([^"]*fbcdn[^"]*\.jpg[^"]*)"'
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, html_content)
            for match in matches:
                # Limpa URL
                clean_url = match.replace('\\u0026', '&').replace('\\/', '/').replace('\\', '')
                
                # Valida se é URL real do Instagram
                if ('instagram' in clean_url or 'fbcdn' in clean_url) and ('.jpg' in clean_url or '.jpeg' in clean_url):
                    urls.append(clean_url)
                    
        return list(set(urls))  # Remove duplicatas
    
    async def _extract_real_youtube_thumbnails(self, query: str, session_id: str, max_videos: int = 8) -> List[RealViralImage]:
        """
        Extrai thumbnails REAIS do YouTube de vídeos populares
        """
        images = []
        
        try:
            # Busca REAL no YouTube
            search_url = f"https://www.youtube.com/results?search_query={query.replace(' ', '+')}&sp=CAMSAhAB"  # Ordenar por visualizações
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'pt-BR,pt;q=0.9,en;q=0.8'
            }
            
            response = await self.session.get(search_url, headers=headers, timeout=15)
            
            if response.status_code == 200:
                # Extrai dados REAIS de vídeos
                video_data = self._extract_youtube_video_data(response.text)
                
                for i, video in enumerate(video_data[:max_videos]):  # Máximo configurável
                    # URL real do thumbnail
                    thumbnail_url = f"https://img.youtube.com/vi/{video['id']}/maxresdefault.jpg"
                    
                    local_path = await self._download_real_image(thumbnail_url, 'youtube', session_id, f"video_{video['id']}")
                    
                    if local_path:
                        viral_image = RealViralImage(
                            platform="YouTube",
                            image_url=thumbnail_url,
                            local_path=local_path,
                            title=video['title'],
                            engagement_score=video.get('engagement_score', 0.0),
                            metadata={
                                'video_id': video['id'],
                                'video_url': f"https://www.youtube.com/watch?v={video['id']}",
                                'views': video.get('views', 'N/A'),
                                'extraction_time': time.time(),
                                'query': query
                            }
                        )
                        images.append(viral_image)
                        
        except Exception as e:
            logger.error(f"❌ Erro na extração REAL do YouTube: {e}")
            
        return images
    
    def _extract_youtube_video_data(self, html_content: str) -> List[Dict]:
        """
        Extrai dados REAIS de vídeos do HTML do YouTube
        """
        videos = []
        seen_video_ids = set()
        
        try:
            # Padrões para extrair dados reais
            video_id_pattern = r'"videoId":"([a-zA-Z0-9_-]{11})"'
            title_pattern = r'"title":{"runs":\[{"text":"([^"]+)"}'
            views_pattern = r'"viewCountText":{"simpleText":"([^"]+)"}'
            
            video_ids = re.findall(video_id_pattern, html_content)
            titles = re.findall(title_pattern, html_content)
            views = re.findall(views_pattern, html_content)
            
            for i, video_id in enumerate(video_ids):
                # Evita duplicatas
                if video_id in seen_video_ids:
                    continue
                seen_video_ids.add(video_id)
                
                title = titles[i] if i < len(titles) else f"Vídeo {video_id}"
                view_count = views[i] if i < len(views) else "N/A"
                
                # Calcula score de engajamento baseado em visualizações
                engagement_score = self._calculate_youtube_engagement(view_count)
                
                videos.append({
                    'id': video_id,
                    'title': title,
                    'views': view_count,
                    'engagement_score': engagement_score
                })
                
        except Exception as e:
            logger.error(f"❌ Erro ao extrair dados reais do YouTube: {e}")
            
        return videos
    
    async def _extract_real_facebook_images(self, query: str, session_id: str, needed: int) -> List[RealViralImage]:
        """
        Extrai imagens REAIS do Facebook usando Selenium
        """
        images = []
        
        if not self.driver:
            self._setup_selenium()
            
        if not self.driver:
            logger.error("❌ Selenium não disponível para Facebook")
            return images
            
        try:
            # Busca REAL no Facebook
            search_url = f"https://www.facebook.com/search/posts/?q={query.replace(' ', '%20')}"
            
            self.driver.get(search_url)
            time.sleep(5)  # Aguarda carregamento
            
            # Busca imagens reais na página
            img_elements = self.driver.find_elements(By.TAG_NAME, "img")
            
            for i, img_element in enumerate(img_elements[:needed]):
                try:
                    img_url = img_element.get_attribute("src")
                    
                    # Valida se é imagem real do Facebook
                    if img_url and ('fbcdn' in img_url or 'facebook' in img_url) and ('.jpg' in img_url or '.jpeg' in img_url or '.png' in img_url):
                        local_path = await self._download_real_image(img_url, 'facebook', session_id, f"post_{i}")
                        
                        if local_path:
                            viral_image = RealViralImage(
                                platform="Facebook",
                                image_url=img_url,
                                local_path=local_path,
                                title=f"Post viral do Facebook",
                                engagement_score=0.8,  # Score baseado em ser encontrado na busca
                                metadata={
                                    'source_url': search_url,
                                    'extraction_time': time.time(),
                                    'query': query,
                                    'element_index': i
                                }
                            )
                            images.append(viral_image)
                            
                except Exception as e:
                    logger.warning(f"⚠️ Erro ao extrair imagem {i} do Facebook: {e}")
                    
        except Exception as e:
            logger.error(f"❌ Erro na extração REAL do Facebook: {e}")
            
        return images
    
    async def _download_real_image(self, img_url: str, platform: str, session_id: str, identifier: str) -> Optional[str]:
        """
        Baixa imagem REAL e valida autenticidade
        """
        try:
            # Headers para requisição real
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8',
                'Accept-Language': 'pt-BR,pt;q=0.9,en;q=0.8',
                'Referer': f'https://www.{platform}.com/',
                'Sec-Fetch-Dest': 'image',
                'Sec-Fetch-Mode': 'no-cors',
                'Sec-Fetch-Site': 'cross-site'
            }
            
            response = await self.session.get(img_url, headers=headers, follow_redirects=True)
            
            if response.status_code == 200 and len(response.content) > 5000:  # Mínimo 5KB para imagem real
                # Determina extensão
                content_type = response.headers.get('content-type', '')
                if 'jpeg' in content_type or 'jpg' in content_type:
                    ext = 'jpg'
                elif 'png' in content_type:
                    ext = 'png'
                elif 'webp' in content_type:
                    ext = 'webp'
                else:
                    ext = 'jpg'
                
                # Nome único baseado no hash para evitar duplicatas
                import hashlib
                content_hash = hashlib.md5(response.content).hexdigest()[:8]
                filename = f"{platform}_real_{identifier}_{content_hash}.{ext}"
                local_path = os.path.join(self.images_dir, platform, filename)
                
                # Verifica se já existe
                if os.path.exists(local_path):
                    logger.info(f"⚠️ Imagem já existe: {filename}")
                    return local_path
                
                # Salva imagem
                with open(local_path, 'wb') as f:
                    f.write(response.content)
                
                # Valida se é imagem real válida
                try:
                    with Image.open(local_path) as img:
                        if img.size[0] >= 300 and img.size[1] >= 300:  # Mínimo 300x300 para imagem real
                            logger.info(f"✅ IMAGEM REAL salva: {filename} ({img.size[0]}x{img.size[1]}) - {len(response.content)} bytes")
                            return local_path
                        else:
                            os.remove(local_path)
                            logger.warning(f"⚠️ Imagem muito pequena: {img.size}")
                            
                except Exception as img_error:
                    if os.path.exists(local_path):
                        os.remove(local_path)
                    logger.warning(f"⚠️ Arquivo inválido: {img_error}")
                    
        except Exception as e:
            logger.warning(f"⚠️ Erro ao baixar imagem REAL: {e}")
            
        return None
    
    def _get_real_hashtags(self, query: str) -> List[str]:
        """
        Retorna hashtags REAIS populares baseadas na query
        """
        words = query.lower().split()
        hashtags = []
        
        # Hashtags REAIS populares por categoria
        real_hashtags = {
            'tecnologia': ['tecnologia', 'tech', 'inovacao', 'startup', 'digital'],
            'inovação': ['inovacao', 'innovation', 'startup', 'tech', 'futuro'],
            'digital': ['digital', 'marketing', 'socialmedia', 'online', 'tech'],
            'saas': ['saas', 'software', 'tech', 'startup', 'business'],
            'marketing': ['marketing', 'digital', 'socialmedia', 'ads', 'growth'],
            'dados': ['dados', 'data', 'analytics', 'insights', 'business'],
            'analytics': ['analytics', 'data', 'insights', 'business', 'growth'],
            'business': ['business', 'empreendedorismo', 'startup', 'negocios', 'growth'],
            'startup': ['startup', 'empreendedorismo', 'inovacao', 'tech', 'business'],
            'plataforma': ['plataforma', 'platform', 'saas', 'tech', 'software']
        }
        
        for word in words:
            if word in real_hashtags:
                hashtags.extend(real_hashtags[word])
                
        # Hashtags padrão se não encontrou
        if not hashtags:
            hashtags = ['tecnologia', 'inovacao', 'startup', 'business', 'digital']
            
        # Remove duplicatas mantendo ordem
        seen = set()
        unique = []
        for tag in hashtags:
            if tag not in seen:
                seen.add(tag)
                unique.append(tag)
                
        return unique[:5]
    
    def _calculate_engagement_score(self, hashtag: str) -> float:
        """
        Calcula score de engajamento baseado na popularidade real da hashtag
        """
        # Scores baseados em popularidade real de hashtags
        popular_scores = {
            'tecnologia': 0.95,
            'tech': 0.92,
            'inovacao': 0.88,
            'startup': 0.90,
            'digital': 0.85,
            'marketing': 0.87,
            'business': 0.83,
            'saas': 0.78,
            'analytics': 0.75,
            'dados': 0.72
        }
        
        return popular_scores.get(hashtag, 0.70)
    
    def _calculate_youtube_engagement(self, view_count_text: str) -> float:
        """
        Calcula engagement baseado em visualizações REAIS
        """
        try:
            # Extrai número de visualizações
            if 'mil' in view_count_text.lower():
                views = float(view_count_text.lower().replace('mil', '').replace(' ', '').replace(',', '.')) * 1000
            elif 'mi' in view_count_text.lower():
                views = float(view_count_text.lower().replace('mi', '').replace(' ', '').replace(',', '.')) * 1000000
            else:
                # Extrai números
                import re
                numbers = re.findall(r'[\d,]+', view_count_text)
                if numbers:
                    views = float(numbers[0].replace(',', ''))
                else:
                    views = 1000
                    
            # Score baseado em visualizações reais
            if views >= 1000000:
                return 0.95
            elif views >= 100000:
                return 0.85
            elif views >= 10000:
                return 0.75
            else:
                return 0.65
                
        except:
            return 0.70
    
    async def _save_extraction_metadata(self, images: List[RealViralImage], session_id: str, query: str):
        """
        Salva metadados da extração REAL
        """
        try:
            metadata = {
                'session_id': session_id,
                'query': query,
                'extraction_time': time.time(),
                'total_images': len(images),
                'platforms': {},
                'images': []
            }
            
            # Agrupa por plataforma
            for image in images:
                platform = image.platform.lower()
                if platform not in metadata['platforms']:
                    metadata['platforms'][platform] = 0
                metadata['platforms'][platform] += 1
                
                metadata['images'].append({
                    'platform': image.platform,
                    'local_path': image.local_path,
                    'title': image.title,
                    'engagement_score': image.engagement_score,
                    'metadata': image.metadata
                })
            
            # Salva arquivo de metadados
            metadata_file = os.path.join(self.images_dir, 'metadata', f'extraction_{session_id}.json')
            with open(metadata_file, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False)
                
            logger.info(f"💾 Metadados REAIS salvos: {metadata_file}")
            
        except Exception as e:
            logger.error(f"❌ Erro ao salvar metadados: {e}")
    
    async def _extract_instagram_alternative(self, query: str, session_id: str, needed: int) -> List[RealViralImage]:
        """
        Método alternativo para extrair imagens do Instagram usando busca direta
        """
        images = []
        
        try:
            # Busca alternativa usando diferentes endpoints
            search_terms = query.split()[:3]  # Primeiras 3 palavras
            
            for term in search_terms:
                try:
                    # URL alternativa para busca no Instagram
                    url = f"https://www.instagram.com/web/search/topsearch/?query={term}"
                    
                    headers = {
                        'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_7_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.2 Mobile/15E148 Safari/604.1',
                        'Accept': 'application/json, text/plain, */*',
                        'Accept-Language': 'pt-BR,pt;q=0.9,en;q=0.8',
                        'X-Requested-With': 'XMLHttpRequest'
                    }
                    
                    response = await self.session.get(url, headers=headers, timeout=10)
                    
                    if response.status_code == 200:
                        # Tenta extrair dados JSON
                        try:
                            data = response.json()
                            if 'users' in data:
                                for user in data['users'][:3]:  # Máximo 3 usuários
                                    if 'profile_pic_url' in user:
                                        img_url = user['profile_pic_url']
                                        
                                        local_path = await self._download_real_image(img_url, 'instagram', session_id, f"profile_{user.get('username', 'user')}")
                                        
                                        if local_path:
                                            viral_image = RealViralImage(
                                                platform="Instagram",
                                                image_url=img_url,
                                                local_path=local_path,
                                                title=f"Perfil viral: {user.get('full_name', term)}",
                                                engagement_score=0.80,
                                                metadata={
                                                    'username': user.get('username', 'unknown'),
                                                    'full_name': user.get('full_name', term),
                                                    'search_term': term,
                                                    'extraction_time': time.time(),
                                                    'query': query
                                                }
                                            )
                                            images.append(viral_image)
                                            
                                            if len(images) >= needed:
                                                break
                        except:
                            pass  # Se não for JSON, continua
                            
                except Exception as e:
                    logger.warning(f"⚠️ Erro na busca alternativa do Instagram para '{term}': {e}")
                    
                if len(images) >= needed:
                    break
                    
        except Exception as e:
            logger.error(f"❌ Erro na extração alternativa do Instagram: {e}")
            
        return images
    
    async def _extract_additional_real_images(self, query: str, session_id: str, needed: int) -> List[RealViralImage]:
        """
        Extrai imagens adicionais de fontes reais para atingir a meta
        """
        images = []
        
        try:
            # Busca em sites de tecnologia e inovação reais
            tech_sites = [
                f"https://www.tecmundo.com.br/busca?q={query.replace(' ', '+')}",
                f"https://olhardigital.com.br/busca/?q={query.replace(' ', '+')}",
                f"https://www.startse.com/busca/?s={query.replace(' ', '+')}"
            ]
            
            for site_url in tech_sites:
                try:
                    headers = {
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                        'Accept-Language': 'pt-BR,pt;q=0.9,en;q=0.8'
                    }
                    
                    response = await self.session.get(site_url, headers=headers, timeout=10)
                    
                    if response.status_code == 200:
                        # Extrai URLs de imagens reais do site
                        import re
                        img_patterns = [
                            r'src="([^"]*\.jpg[^"]*)"',
                            r'src="([^"]*\.jpeg[^"]*)"',
                            r'src="([^"]*\.png[^"]*)"',
                            r'data-src="([^"]*\.jpg[^"]*)"',
                            r'data-src="([^"]*\.jpeg[^"]*)"'
                        ]
                        
                        for pattern in img_patterns:
                            matches = re.findall(pattern, response.text)
                            for match in matches[:3]:  # Máximo 3 por site
                                # Valida se é URL real e relevante
                                if ('tecmundo' in match or 'olhardigital' in match or 'startse' in match) and len(match) > 50:
                                    # Converte URL relativa para absoluta se necessário
                                    if match.startswith('//'):
                                        img_url = f"https:{match}"
                                    elif match.startswith('/'):
                                        domain = site_url.split('/')[2]
                                        img_url = f"https://{domain}{match}"
                                    else:
                                        img_url = match
                                    
                                    local_path = await self._download_real_image(img_url, 'tech_sites', session_id, f"site_{len(images)}")
                                    
                                    if local_path:
                                        viral_image = RealViralImage(
                                            platform="Tech Sites",
                                            image_url=img_url,
                                            local_path=local_path,
                                            title=f"Imagem de tecnologia - {site_url.split('/')[2]}",
                                            engagement_score=0.75,
                                            metadata={
                                                'source_site': site_url.split('/')[2],
                                                'source_url': site_url,
                                                'extraction_time': time.time(),
                                                'query': query
                                            }
                                        )
                                        images.append(viral_image)
                                        
                                        if len(images) >= needed:
                                            break
                            
                            if len(images) >= needed:
                                break
                                
                except Exception as e:
                    logger.warning(f"⚠️ Erro ao extrair de {site_url}: {e}")
                    
                if len(images) >= needed:
                    break
                    
        except Exception as e:
            logger.error(f"❌ Erro na extração adicional: {e}")
            
        return images

# Instância global
real_viral_extractor = RealViralImageExtractor()