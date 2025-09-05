
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Extrator de Redes Sociais com Playwright
Substitui Selenium para captura de screenshots e extração de dados sociais
"""

import os
import logging
import asyncio
import time
from typing import Dict, List, Any, Optional
from datetime import datetime
from pathlib import Path
import json
import re

try:
    from playwright.async_api import async_playwright, Browser, Page
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False
    logging.warning("⚠️ Playwright não instalado")

logger = logging.getLogger(__name__)

class PlaywrightSocialExtractor:
    """Extrator de redes sociais usando Playwright"""
    
    def __init__(self):
        self.browser: Optional[Browser] = None
        self.enabled = PLAYWRIGHT_AVAILABLE
        self.session_stats = {
            'pages_extracted': 0,
            'screenshots_captured': 0,
            'images_downloaded': 0,
            'errors': 0
        }
        
        if self.enabled:
            logger.info("🎭 Playwright Social Extractor inicializado")
        else:
            logger.error("❌ Playwright não disponível")

    async def start_browser(self) -> bool:
        """Inicia o navegador Playwright"""
        if not self.enabled:
            return False
            
        try:
            self.playwright = await async_playwright().start()
            self.browser = await self.playwright.chromium.launch(
                headless=True,
                args=[
                    '--no-sandbox',
                    '--disable-dev-shm-usage',
                    '--disable-gpu',
                    '--disable-extensions',
                    '--disable-background-timer-throttling',
                    '--disable-backgrounding-occluded-windows',
                    '--disable-renderer-backgrounding'
                ]
            )
            logger.info("🎭 Navegador Playwright iniciado")
            return True
        except Exception as e:
            logger.error(f"❌ Erro ao iniciar Playwright: {e}")
            return False

    async def stop_browser(self):
        """Para o navegador Playwright"""
        try:
            if self.browser:
                await self.browser.close()
            if hasattr(self, 'playwright'):
                await self.playwright.stop()
            logger.info("🎭 Navegador Playwright parado")
        except Exception as e:
            logger.error(f"❌ Erro ao parar Playwright: {e}")

    async def extract_social_content_with_images(
        self, 
        search_results: Dict[str, Any], 
        session_id: str,
        max_pages: int = 10
    ) -> Dict[str, Any]:
        """Extrai conteúdo social e IMAGENS das URLs"""
        
        if not await self.start_browser():
            return {"success": False, "error": "Navegador não iniciado"}

        extraction_results = {
            "success": True,
            "session_id": session_id,
            "extracted_at": datetime.now().isoformat(),
            "social_content": [],
            "screenshots": [],
            "images_extracted": [],
            "statistics": {
                "pages_processed": 0,
                "screenshots_captured": 0,
                "images_downloaded": 0,
                "extraction_time": 0
            }
        }

        start_time = time.time()
        
        # Cria diretórios
        session_dir = Path(f"analyses_data/files/{session_id}")
        screenshots_dir = session_dir / "screenshots" 
        images_dir = session_dir / "social_images"
        
        for dir_path in [session_dir, screenshots_dir, images_dir]:
            dir_path.mkdir(parents=True, exist_ok=True)

        try:
            # Extrai URLs dos resultados de busca
            urls_to_process = []
            
            # Processa diferentes formatos de resultados
            if isinstance(search_results, dict):
                # Verifica se tem web_results
                if 'web_results' in search_results:
                    for result in search_results['web_results'][:max_pages]:
                        if result.get('url'):
                            urls_to_process.append({
                                'url': result['url'],
                                'title': result.get('title', 'Sem título'),
                                'source': 'web_search'
                            })
                
                # Verifica se tem social_results
                if 'social_results' in search_results:
                    for result in search_results['social_results'][:max_pages]:
                        if result.get('url'):
                            urls_to_process.append({
                                'url': result['url'],
                                'title': result.get('title', 'Sem título'),
                                'source': 'social_media'
                            })
                
                # Se é uma lista de resultados
                if 'all_results' in search_results:
                    for result in search_results['all_results'][:max_pages]:
                        if result.get('url'):
                            urls_to_process.append({
                                'url': result['url'],
                                'title': result.get('title', 'Sem título'),
                                'source': 'mixed'
                            })

            # Processa cada URL
            for i, url_data in enumerate(urls_to_process[:max_pages], 1):
                try:
                    logger.info(f"🎭 Processando {i}/{len(urls_to_process)}: {url_data['title']}")
                    
                    page_result = await self._process_page_with_images(
                        url_data['url'], 
                        url_data['title'],
                        screenshots_dir,
                        images_dir,
                        i
                    )
                    
                    if page_result['success']:
                        extraction_results['social_content'].append(page_result['content'])
                        
                        if page_result['screenshot_path']:
                            extraction_results['screenshots'].append(page_result['screenshot_info'])
                            extraction_results['statistics']['screenshots_captured'] += 1
                        
                        if page_result['images']:
                            extraction_results['images_extracted'].extend(page_result['images'])
                            extraction_results['statistics']['images_downloaded'] += len(page_result['images'])
                        
                        extraction_results['statistics']['pages_processed'] += 1
                    
                    # Rate limiting
                    await asyncio.sleep(2)
                    
                except Exception as e:
                    logger.error(f"❌ Erro ao processar URL {url_data['url']}: {e}")
                    self.session_stats['errors'] += 1

            extraction_results['statistics']['extraction_time'] = time.time() - start_time
            
            logger.info(f"✅ Extração concluída: {extraction_results['statistics']['pages_processed']} páginas, "
                       f"{extraction_results['statistics']['screenshots_captured']} screenshots, "
                       f"{extraction_results['statistics']['images_downloaded']} imagens")

        except Exception as e:
            logger.error(f"❌ Erro durante extração: {e}")
            extraction_results['success'] = False
            extraction_results['error'] = str(e)
        
        finally:
            await self.stop_browser()

        return extraction_results

    async def _process_page_with_images(
        self, 
        url: str, 
        title: str,
        screenshots_dir: Path,
        images_dir: Path,
        page_num: int
    ) -> Dict[str, Any]:
        """Processa uma página extraindo conteúdo, screenshot e imagens"""
        
        result = {
            'success': False,
            'content': {},
            'screenshot_path': None,
            'screenshot_info': {},
            'images': []
        }

        try:
            page = await self.browser.new_page()
            
            # Configura viewport
            await page.set_viewport_size({"width": 1920, "height": 1080})
            
            # Navega para a página
            await page.goto(url, wait_until='domcontentloaded', timeout=30000)
            
            # Aguarda carregamento
            await page.wait_for_timeout(3000)
            
            # 1. EXTRAI CONTEÚDO
            content = await self._extract_page_content(page, url, title)
            
            # 2. CAPTURA SCREENSHOT
            screenshot_path = screenshots_dir / f"page_{page_num:03d}_{self._sanitize_filename(title)}.png"
            await page.screenshot(path=str(screenshot_path), full_page=True)
            
            # 3. EXTRAI IMAGENS
            images = await self._extract_page_images(page, images_dir, page_num)
            
            result.update({
                'success': True,
                'content': content,
                'screenshot_path': str(screenshot_path),
                'screenshot_info': {
                    'path': str(screenshot_path),
                    'filename': screenshot_path.name,
                    'url': url,
                    'title': title,
                    'captured_at': datetime.now().isoformat()
                },
                'images': images
            })
            
            await page.close()
            
        except Exception as e:
            logger.error(f"❌ Erro ao processar página {url}: {e}")
            result['error'] = str(e)
            if 'page' in locals():
                await page.close()

        return result

    async def _extract_page_content(self, page: Page, url: str, title: str) -> Dict[str, Any]:
        """Extrai conteúdo da página"""
        try:
            # Extrai texto principal
            text_content = await page.evaluate("""
                () => {
                    // Remove scripts e styles
                    const scripts = document.querySelectorAll('script, style, nav, footer, aside');
                    scripts.forEach(el => el.remove());
                    
                    // Pega o texto do body
                    return document.body.innerText.trim();
                }
            """)
            
            # Extrai meta tags
            meta_info = await page.evaluate("""
                () => {
                    const metas = {};
                    document.querySelectorAll('meta').forEach(meta => {
                        const name = meta.getAttribute('name') || meta.getAttribute('property');
                        const content = meta.getAttribute('content');
                        if (name && content) {
                            metas[name] = content;
                        }
                    });
                    return metas;
                }
            """)
            
            # Extrai links de redes sociais
            social_links = await page.evaluate("""
                () => {
                    const links = [];
                    document.querySelectorAll('a[href*="instagram.com"], a[href*="facebook.com"], a[href*="twitter.com"], a[href*="linkedin.com"], a[href*="youtube.com"], a[href*="tiktok.com"]').forEach(link => {
                        links.push({
                            text: link.innerText.trim(),
                            href: link.href,
                            platform: link.href.includes('instagram') ? 'instagram' : 
                                     link.href.includes('facebook') ? 'facebook' :
                                     link.href.includes('twitter') ? 'twitter' :
                                     link.href.includes('linkedin') ? 'linkedin' :
                                     link.href.includes('youtube') ? 'youtube' :
                                     link.href.includes('tiktok') ? 'tiktok' : 'unknown'
                        });
                    });
                    return links;
                }
            """)

            return {
                'url': url,
                'title': title,
                'text_content': text_content[:5000],  # Limita texto
                'meta_info': meta_info,
                'social_links': social_links,
                'content_length': len(text_content),
                'extracted_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Erro ao extrair conteúdo: {e}")
            return {'url': url, 'title': title, 'error': str(e)}

    async def _extract_page_images(self, page: Page, images_dir: Path, page_num: int) -> List[Dict[str, Any]]:
        """Extrai e baixa imagens da página"""
        images_extracted = []
        
        try:
            # Encontra todas as imagens
            images_data = await page.evaluate("""
                () => {
                    const images = [];
                    document.querySelectorAll('img').forEach((img, index) => {
                        if (img.src && img.src.startsWith('http')) {
                            images.push({
                                src: img.src,
                                alt: img.alt || '',
                                width: img.naturalWidth || img.width,
                                height: img.naturalHeight || img.height,
                                index: index
                            });
                        }
                    });
                    return images;
                }
            """)
            
            # Filtra imagens relevantes (não muito pequenas)
            relevant_images = [
                img for img in images_data 
                if img['width'] >= 200 and img['height'] >= 200
            ][:5]  # Máximo 5 imagens por página
            
            # Baixa as imagens
            for i, img_data in enumerate(relevant_images, 1):
                try:
                    # Navega para a imagem para baixá-la
                    img_response = await page.request.get(img_data['src'])
                    
                    if img_response.status == 200:
                        # Determina extensão
                        content_type = img_response.headers.get('content-type', '')
                        if 'jpeg' in content_type or 'jpg' in content_type:
                            ext = '.jpg'
                        elif 'png' in content_type:
                            ext = '.png'
                        elif 'webp' in content_type:
                            ext = '.webp'
                        else:
                            ext = '.jpg'  # padrão
                        
                        # Salva imagem
                        img_filename = f"page_{page_num:03d}_img_{i:02d}{ext}"
                        img_path = images_dir / img_filename
                        
                        with open(img_path, 'wb') as f:
                            f.write(await img_response.body())
                        
                        images_extracted.append({
                            'filename': img_filename,
                            'path': str(img_path),
                            'original_url': img_data['src'],
                            'alt_text': img_data['alt'],
                            'width': img_data['width'],
                            'height': img_data['height'],
                            'file_size': img_path.stat().st_size,
                            'downloaded_at': datetime.now().isoformat()
                        })
                        
                        logger.info(f"📸 Imagem salva: {img_filename}")
                        
                except Exception as e:
                    logger.warning(f"⚠️ Erro ao baixar imagem {img_data['src']}: {e}")
                    continue
                    
        except Exception as e:
            logger.error(f"❌ Erro na extração de imagens: {e}")
        
        return images_extracted

    def _sanitize_filename(self, filename: str) -> str:
        """Sanitiza nome do arquivo"""
        # Remove caracteres especiais
        sanitized = re.sub(r'[<>:"/\\|?*]', '_', filename)
        # Limita tamanho
        return sanitized[:50]

    def get_statistics(self) -> Dict[str, Any]:
        """Retorna estatísticas da sessão"""
        return self.session_stats.copy()

# Instância global
playwright_social_extractor = PlaywrightSocialExtractor()
