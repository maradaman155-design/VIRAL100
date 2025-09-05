
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Google Social Masterclass Extractor - V1.0
Busca no Google "instagram masterclass [QUERY]" e extrai os melhores posts
"""

import asyncio
import logging
import json
import re
from typing import Dict, List, Any, Optional
from datetime import datetime
from pathlib import Path
from playwright.async_api import async_playwright, Browser, Page, BrowserContext
from urllib.parse import quote_plus, urlparse
import os

logger = logging.getLogger(__name__)

class GoogleSocialMasterclassExtractor:
    """
    Extrator que busca no Google e captura screenshots dos melhores posts
    """

    def __init__(self):
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.playwright = None

        # Configurações
        self.config = {
            'headless': True,
            'timeout': 60000,
            'viewport': {'width': 1920, 'height': 1080},
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            'scroll_attempts': 3,
            'scroll_delay': 2000,
            'screenshot_delay': 3000,
            'max_results_per_platform': 10
        }

        # Seletores para extrair métricas de engajamento
        self.engagement_selectors = {
            'instagram': {
                'likes': [
                    'span[class*="like"]',
                    'button[aria-label*="like"] span',
                    'span[title*="like"]',
                    'section[role="group"] span',
                    'div[class*="_aacl"] span'
                ],
                'comments': [
                    'span[class*="comment"]',
                    'button[aria-label*="comment"] span',
                    'a[href*="/comments/"] span'
                ],
                'views': [
                    'span[title*="view"]',
                    'div[class*="view"] span'
                ],
                'popup_close': [
                    'button[aria-label="Close"]',
                    'svg[aria-label="Close"]',
                    'div[role="button"][aria-label="Close"]',
                    'button:has-text("Fechar")',
                    'button:has-text("Close")',
                    'button:has-text("Cancelar")',
                    'div[class*="modal"] button[class*="close"]'
                ]
            },
            'youtube': {
                'views': [
                    '#metadata-line span:first-child',
                    'span.view-count',
                    'span[class*="view"]'
                ],
                'likes': [
                    '#segmented-like-button span',
                    'button[aria-label*="like"] span',
                    '#like-button-view-model span'
                ],
                'comments': [
                    '#count span',
                    'span[class*="comment-count"]',
                    '#comments #count span'
                ]
            },
            'facebook': {
                'likes': [
                    'span[data-testid="like-count"]',
                    'span[aria-label*="reaction"]',
                    'div[role="button"] span[class*="reaction"]'
                ],
                'comments': [
                    'span[data-testid="comment-count"]',
                    'div[aria-label*="comment"] span'
                ],
                'shares': [
                    'span[data-testid="share-count"]',
                    'div[aria-label*="share"] span'
                ],
                'popup_close': [
                    'div[aria-label="Close"]',
                    'button[aria-label="Close"]',
                    'div[role="button"][aria-label="Fechar"]'
                ]
            }
        }

        logger.info("🔍 Google Social Masterclass Extractor inicializado")

    async def __aenter__(self):
        """Context manager entry"""
        await self.start_browser()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        await self.stop_browser()

    async def start_browser(self):
        """Inicia o browser Playwright"""
        try:
            if self.playwright is None:
                self.playwright = await async_playwright().start()

            if self.browser is None:
                self.browser = await self.playwright.chromium.launch(
                    headless=self.config['headless'],
                    args=[
                        '--no-sandbox',
                        '--disable-setuid-sandbox',
                        '--disable-dev-shm-usage',
                        '--disable-blink-features=AutomationControlled',
                        '--disable-web-security',
                        '--start-maximized',
                        '--ignore-certificate-errors',
                        '--allow-running-insecure-content'
                    ]
                )

            if self.context is None:
                self.context = await self.browser.new_context(
                    viewport=self.config['viewport'],
                    user_agent=self.config['user_agent'],
                    ignore_https_errors=True,
                    java_script_enabled=True,
                    bypass_csp=True
                )

            logger.info("✅ Browser Google Masterclass iniciado")
            return True

        except Exception as e:
            logger.error(f"❌ Erro ao iniciar browser: {e}")
            return False

    async def stop_browser(self):
        """Fecha o browser"""
        try:
            if self.context:
                await self.context.close()
            if self.browser:
                await self.browser.close()
            if self.playwright:
                await self.playwright.stop()
            self.browser = None
            self.context = None
            self.playwright = None
            logger.info("✅ Browser Google Masterclass fechado")
        except Exception as e:
            logger.error(f"⚠️ Erro ao fechar browser: {e}")

    async def extract_masterclass_content(
        self, 
        query: str, 
        session_id: str,
        platforms: List[str] = None
    ) -> Dict[str, Any]:
        """
        Busca no Google "instagram masterclass [QUERY]" e extrai os melhores posts
        """
        if platforms is None:
            platforms = ['instagram', 'youtube', 'facebook']

        logger.info(f"🎯 Buscando masterclass para: {query}")
        logger.info(f"📱 Plataformas: {platforms}")

        results = {
            'query': query,
            'session_id': session_id,
            'extraction_started': datetime.now().isoformat(),
            'platforms_data': {},
            'best_posts': [],
            'total_screenshots': 0,
            'success': False
        }

        if not await self.start_browser():
            results['error'] = "Falha ao iniciar browser"
            return results

        try:
            # Extrair de cada plataforma
            for platform in platforms:
                try:
                    logger.info(f"🔍 Extraindo {platform.upper()} masterclass")
                    
                    platform_data = await self._extract_platform_masterclass(
                        platform, query, session_id
                    )
                    
                    results['platforms_data'][platform] = platform_data
                    
                    # Adiciona melhores posts ao resultado geral
                    if platform_data.get('best_posts'):
                        results['best_posts'].extend(platform_data['best_posts'])
                    
                    results['total_screenshots'] += platform_data.get('screenshots_taken', 0)
                    
                except Exception as e:
                    logger.error(f"❌ Erro ao extrair {platform}: {e}")
                    results['platforms_data'][platform] = {
                        'error': str(e),
                        'best_posts': [],
                        'screenshots_taken': 0
                    }

            # Ordena os melhores posts por engajamento total
            results['best_posts'] = sorted(
                results['best_posts'],
                key=lambda x: x.get('total_engagement', 0),
                reverse=True
            )

            results['success'] = results['total_screenshots'] > 0
            results['extraction_completed'] = datetime.now().isoformat()

            logger.info(f"✅ Extração Google Masterclass concluída: {results['total_screenshots']} screenshots")

        except Exception as e:
            logger.error(f"❌ Erro geral na extração: {e}")
            results['error'] = str(e)
        finally:
            await self.stop_browser()

        return results

    async def _extract_platform_masterclass(
        self, 
        platform: str, 
        query: str, 
        session_id: str
    ) -> Dict[str, Any]:
        """Extrai masterclass de uma plataforma específica"""
        
        # Busca no Google
        google_query = f"{platform} masterclass {query}"
        google_results = await self._search_google(google_query)
        
        # Filtra resultados relevantes da plataforma
        platform_urls = self._filter_platform_urls(google_results, platform)
        
        # Analisa cada URL e extrai métricas
        analyzed_posts = []
        for url in platform_urls[:self.config['max_results_per_platform']]:
            post_data = await self._analyze_post_url(url, platform, session_id)
            if post_data:
                analyzed_posts.append(post_data)
        
        # Identifica os melhores posts
        best_posts = self._identify_best_posts(analyzed_posts)
        
        # Captura screenshots dos melhores
        screenshots_taken = 0
        for post in best_posts:
            screenshot_path = await self._capture_post_screenshot(
                post['url'], platform, session_id, post['post_id']
            )
            if screenshot_path:
                post['screenshot_path'] = screenshot_path
                screenshots_taken += 1

        return {
            'platform': platform,
            'google_query': google_query,
            'urls_found': len(platform_urls),
            'posts_analyzed': len(analyzed_posts),
            'best_posts': best_posts,
            'screenshots_taken': screenshots_taken,
            'success': screenshots_taken > 0
        }

    async def _search_google(self, query: str) -> List[str]:
        """Busca no Google e extrai URLs dos resultados"""
        page = await self.context.new_page()
        urls = []

        try:
            search_url = f"https://www.google.com/search?q={quote_plus(query)}&num=20"
            await page.goto(search_url, wait_until='networkidle', timeout=self.config['timeout'])
            await page.wait_for_timeout(2000)

            # Fechar popup de cookies se aparecer
            try:
                cookie_buttons = await page.query_selector_all('button:has-text("Aceitar"), button:has-text("Accept"), button:has-text("I agree")')
                for btn in cookie_buttons:
                    await btn.click()
                    await page.wait_for_timeout(1000)
                    break
            except:
                pass

            # Extrair URLs dos resultados
            result_links = await page.query_selector_all('a[href*="instagram.com"], a[href*="youtube.com"], a[href*="facebook.com"]')
            
            for link in result_links:
                try:
                    href = await link.get_attribute('href')
                    if href and self._is_valid_social_url(href):
                        urls.append(href)
                except:
                    continue

            logger.info(f"🔍 Google encontrou {len(urls)} URLs para: {query}")

        except Exception as e:
            logger.error(f"❌ Erro na busca Google: {e}")
        finally:
            await page.close()

        return list(set(urls))  # Remove duplicatas

    def _filter_platform_urls(self, urls: List[str], platform: str) -> List[str]:
        """Filtra URLs da plataforma específica"""
        platform_domains = {
            'instagram': 'instagram.com',
            'youtube': 'youtube.com',
            'facebook': 'facebook.com'
        }
        
        domain = platform_domains.get(platform, '')
        return [url for url in urls if domain in url]

    async def _analyze_post_url(self, url: str, platform: str, session_id: str) -> Optional[Dict[str, Any]]:
        """Analisa uma URL específica e extrai métricas de engajamento"""
        page = await self.context.new_page()

        try:
            logger.info(f"📊 Analisando {platform}: {url}")
            
            await page.goto(url, wait_until='networkidle', timeout=self.config['timeout'])
            await page.wait_for_timeout(3000)

            # Fecha popups de login se aparecerem
            await self._close_login_popups(page, platform)

            # Extrai métricas de engajamento
            engagement_data = await self._extract_engagement_metrics(page, platform)
            
            # Gera ID único para o post
            post_id = self._generate_post_id(url)

            post_data = {
                'post_id': post_id,
                'platform': platform,
                'url': url,
                'engagement': engagement_data,
                'total_engagement': self._calculate_total_engagement(engagement_data),
                'analyzed_at': datetime.now().isoformat()
            }

            logger.info(f"✅ {platform} analisado: {engagement_data}")
            return post_data

        except Exception as e:
            logger.error(f"❌ Erro ao analisar {url}: {e}")
            return None
        finally:
            await page.close()

    async def _close_login_popups(self, page: Page, platform: str) -> None:
        """Fecha popups de login da plataforma"""
        try:
            if platform in ['instagram', 'facebook']:
                selectors = self.engagement_selectors[platform].get('popup_close', [])
                
                for selector in selectors:
                    try:
                        close_button = await page.query_selector(selector)
                        if close_button:
                            await close_button.click()
                            await page.wait_for_timeout(1000)
                            logger.info(f"✅ Popup fechado no {platform}")
                            break
                    except:
                        continue

        except Exception as e:
            logger.debug(f"⚠️ Erro ao fechar popup: {e}")

    async def _extract_engagement_metrics(self, page: Page, platform: str) -> Dict[str, int]:
        """Extrai métricas de engajamento da página"""
        metrics = {'likes': 0, 'comments': 0, 'views': 0, 'shares': 0}

        # Estratégias específicas por plataforma
        if platform == 'instagram':
            await self._extract_instagram_metrics(page, metrics)
        elif platform == 'youtube':
            await self._extract_youtube_metrics(page, metrics)
        elif platform == 'facebook':
            await self._extract_facebook_metrics(page, metrics)
        else:
            # Fallback para outras plataformas usando seletores genéricos
            await self._extract_generic_metrics(page, platform, metrics)

        return metrics

    async def _extract_instagram_metrics(self, page: Page, metrics: Dict[str, int]) -> None:
        """Extrai métricas específicas do Instagram"""
        try:
            # Aguarda carregamento do conteúdo
            await page.wait_for_timeout(2000)

            # Busca likes
            like_selectors = [
                'section[role="group"] span',
                'button[aria-label*="curtida"] span',
                'button[aria-label*="like"] span',
                'span[class*="_aacl"]',
                'div[class*="x193iq5w"] span'
            ]
            
            for selector in like_selectors:
                try:
                    element = await page.query_selector(selector)
                    if element:
                        text = await element.text_content()
                        likes = self._parse_engagement_number(text)
                        if likes > 0:
                            metrics['likes'] = likes
                            break
                except:
                    continue

            # Busca comentários
            comment_selectors = [
                'button[aria-label*="comentário"] span',
                'button[aria-label*="comment"] span', 
                'a[href*="/comments/"] span'
            ]
            
            for selector in comment_selectors:
                try:
                    element = await page.query_selector(selector)
                    if element:
                        text = await element.text_content()
                        comments = self._parse_engagement_number(text)
                        if comments > 0:
                            metrics['comments'] = comments
                            break
                except:
                    continue

        except Exception as e:
            logger.debug(f"⚠️ Erro ao extrair métricas Instagram: {e}")

    async def _extract_youtube_metrics(self, page: Page, metrics: Dict[str, int]) -> None:
        """Extrai métricas específicas do YouTube"""
        try:
            # Aguarda carregamento
            await page.wait_for_timeout(3000)

            # Views
            view_selectors = [
                '#info-contents #count span',
                'span.view-count',
                '#metadata-line span'
            ]
            
            for selector in view_selectors:
                try:
                    element = await page.query_selector(selector)
                    if element:
                        text = await element.text_content()
                        if 'visualiza' in text.lower() or 'view' in text.lower():
                            views = self._parse_engagement_number(text)
                            if views > 0:
                                metrics['views'] = views
                                break
                except:
                    continue

            # Likes
            like_selectors = [
                '#segmented-like-button span',
                'button[aria-label*="like"] span',
                '#like-button-view-model span'
            ]
            
            for selector in like_selectors:
                try:
                    element = await page.query_selector(selector)
                    if element:
                        text = await element.text_content()
                        likes = self._parse_engagement_number(text)
                        if likes > 0:
                            metrics['likes'] = likes
                            break
                except:
                    continue

            # Comentários
            comment_selectors = [
                '#comments #count span',
                'span[class*="comment-count"]'
            ]
            
            for selector in comment_selectors:
                try:
                    element = await page.query_selector(selector)
                    if element:
                        text = await element.text_content()
                        comments = self._parse_engagement_number(text)
                        if comments > 0:
                            metrics['comments'] = comments
                            break
                except:
                    continue

        except Exception as e:
            logger.debug(f"⚠️ Erro ao extrair métricas YouTube: {e}")

    async def _extract_facebook_metrics(self, page: Page, metrics: Dict[str, int]) -> None:
        """Extrai métricas específicas do Facebook"""
        try:
            # Aguarda carregamento
            await page.wait_for_timeout(2000)

            # Busca reações (likes)
            reaction_selectors = [
                'span[data-testid="like-count"]',
                'div[aria-label*="reaction"] span',
                'span[class*="reaction-count"]'
            ]
            
            for selector in reaction_selectors:
                try:
                    element = await page.query_selector(selector)
                    if element:
                        text = await element.text_content()
                        likes = self._parse_engagement_number(text)
                        if likes > 0:
                            metrics['likes'] = likes
                            break
                except:
                    continue

            # Comentários
            comment_selectors = [
                'span[data-testid="comment-count"]',
                'div[aria-label*="comentário"] span',
                'div[aria-label*="comment"] span'
            ]
            
            for selector in comment_selectors:
                try:
                    element = await page.query_selector(selector)
                    if element:
                        text = await element.text_content()
                        comments = self._parse_engagement_number(text)
                        if comments > 0:
                            metrics['comments'] = comments
                            break
                except:
                    continue

            # Compartilhamentos
            share_selectors = [
                'span[data-testid="share-count"]',
                'div[aria-label*="compartilh"] span',
                'div[aria-label*="share"] span'
            ]
            
            for selector in share_selectors:
                try:
                    element = await page.query_selector(selector)
                    if element:
                        text = await element.text_content()
                        shares = self._parse_engagement_number(text)
                        if shares > 0:
                            metrics['shares'] = shares
                            break
                except:
                    continue

        except Exception as e:
            logger.debug(f"⚠️ Erro ao extrair métricas Facebook: {e}")

    async def _extract_generic_metrics(self, page: Page, platform: str, metrics: Dict[str, int]) -> None:
        """Extrai métricas usando seletores genéricos por plataforma"""
        try:
            selectors = self.engagement_selectors.get(platform, {})

            # Extrai likes
            for selector in selectors.get('likes', []):
                try:
                    element = await page.query_selector(selector)
                    if element:
                        text = await element.text_content()
                        metrics['likes'] = self._parse_engagement_number(text)
                        if metrics['likes'] > 0:
                            break
                except:
                    continue

            # Extrai comentários
            for selector in selectors.get('comments', []):
                try:
                    element = await page.query_selector(selector)
                    if element:
                        text = await element.text_content()
                        metrics['comments'] = self._parse_engagement_number(text)
                        if metrics['comments'] > 0:
                            break
                except:
                    continue

            # Extrai views (YouTube principalmente)
            for selector in selectors.get('views', []):
                try:
                    element = await page.query_selector(selector)
                    if element:
                        text = await element.text_content()
                        metrics['views'] = self._parse_engagement_number(text)
                        if metrics['views'] > 0:
                            break
                except:
                    continue

            # Extrai shares (Facebook)
            for selector in selectors.get('shares', []):
                try:
                    element = await page.query_selector(selector)
                    if element:
                        text = await element.text_content()
                        metrics['shares'] = self._parse_engagement_number(text)
                        if metrics['shares'] > 0:
                            break
                except:
                    continue

        except Exception as e:
            logger.error(f"❌ Erro ao extrair métricas: {e}")

    def _parse_engagement_number(self, text: str) -> int:
        """Converte texto de engajamento em número"""
        if not text:
            return 0

        # Remove espaços e converte para minúsculo
        text = text.strip().lower()

        # Busca números no texto
        numbers = re.findall(r'[\d,\.]+', text)
        if not numbers:
            return 0

        # Pega o primeiro número encontrado
        number_str = numbers[0].replace(',', '').replace('.', '')
        
        try:
            number = int(number_str)
            
            # Converte abreviações (K, M, B)
            if 'k' in text:
                number *= 1000
            elif 'm' in text:
                number *= 1000000
            elif 'b' in text:
                number *= 1000000000
            
            return number
        except:
            return 0

    def _calculate_total_engagement(self, metrics: Dict[str, int]) -> int:
        """Calcula engajamento total com pesos"""
        return (
            metrics.get('likes', 0) * 1 +
            metrics.get('comments', 0) * 3 +
            metrics.get('shares', 0) * 5 +
            metrics.get('views', 0) * 0.1
        )

    def _identify_best_posts(self, posts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Identifica os melhores posts por engajamento"""
        # Ordena por engajamento total
        sorted_posts = sorted(
            posts,
            key=lambda x: x.get('total_engagement', 0),
            reverse=True
        )
        
        # Retorna top 5 ou todos se menos de 5
        return sorted_posts[:5]

    async def _capture_post_screenshot(
        self, 
        url: str, 
        platform: str, 
        session_id: str, 
        post_id: str
    ) -> Optional[str]:
        """Captura screenshot de um post específico"""
        page = await self.context.new_page()

        try:
            logger.info(f"📸 Capturando screenshot: {url}")
            
            await page.goto(url, wait_until='networkidle', timeout=self.config['timeout'])
            await page.wait_for_timeout(self.config['screenshot_delay'])

            # Fecha popups novamente
            await self._close_login_popups(page, platform)
            await page.wait_for_timeout(1000)

            # Cria diretório para screenshots
            screenshots_dir = Path(f"analyses_data/files/{session_id}/masterclass_screenshots")
            screenshots_dir.mkdir(parents=True, exist_ok=True)

            # Nome do arquivo
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{platform}_{post_id}_{timestamp}.png"
            screenshot_path = screenshots_dir / filename

            # Captura screenshot
            await page.screenshot(
                path=str(screenshot_path),
                full_page=True,
                type='png'
            )

            logger.info(f"✅ Screenshot salvo: {screenshot_path}")
            return str(screenshot_path)

        except Exception as e:
            logger.error(f"❌ Erro ao capturar screenshot de {url}: {e}")
            return None
        finally:
            await page.close()

    def _is_valid_social_url(self, url: str) -> bool:
        """Verifica se a URL é válida para redes sociais"""
        if not url:
            return False
            
        # Remove parâmetros do Google
        if 'google.com' in url or '/url?q=' in url:
            return False
            
        valid_patterns = [
            r'instagram\.com/p/',
            r'instagram\.com/reel/',
            r'youtube\.com/watch',
            r'youtube\.com/shorts',
            r'facebook\.com/.*/(posts|videos)',
            r'fb\.watch/'
        ]
        
        return any(re.search(pattern, url) for pattern in valid_patterns)

    def _generate_post_id(self, url: str) -> str:
        """Gera ID único para o post baseado na URL"""
        import hashlib
        return hashlib.md5(url.encode()).hexdigest()[:8]

    async def generate_masterclass_report(
        self, 
        extraction_results: Dict[str, Any], 
        session_id: str
    ) -> Dict[str, Any]:
        """Gera relatório dos melhores posts encontrados"""
        
        report = {
            'session_id': session_id,
            'query': extraction_results.get('query', ''),
            'generated_at': datetime.now().isoformat(),
            'summary': {
                'total_posts_analyzed': 0,
                'total_screenshots': extraction_results.get('total_screenshots', 0),
                'platforms_covered': list(extraction_results.get('platforms_data', {}).keys())
            },
            'best_posts_ranking': [],
            'platform_insights': {}
        }

        # Conta posts analisados
        for platform_data in extraction_results.get('platforms_data', {}).values():
            if isinstance(platform_data, dict):
                posts_count = len(platform_data.get('best_posts', []))
                report['summary']['total_posts_analyzed'] += posts_count

        # Ranking dos melhores posts
        best_posts = extraction_results.get('best_posts', [])
        for i, post in enumerate(best_posts[:10], 1):
            ranking_entry = {
                'rank': i,
                'platform': post.get('platform', ''),
                'url': post.get('url', ''),
                'total_engagement': post.get('total_engagement', 0),
                'engagement_breakdown': post.get('engagement', {}),
                'screenshot_available': 'screenshot_path' in post,
                'screenshot_path': post.get('screenshot_path', '')
            }
            report['best_posts_ranking'].append(ranking_entry)

        # Insights por plataforma
        for platform, data in extraction_results.get('platforms_data', {}).items():
            if isinstance(data, dict) and 'best_posts' in data:
                platform_posts = data['best_posts']
                
                if platform_posts:
                    avg_engagement = sum(p.get('total_engagement', 0) for p in platform_posts) / len(platform_posts)
                    max_engagement = max(p.get('total_engagement', 0) for p in platform_posts)
                    
                    report['platform_insights'][platform] = {
                        'posts_found': len(platform_posts),
                        'avg_engagement': round(avg_engagement, 2),
                        'max_engagement': max_engagement,
                        'screenshots_captured': data.get('screenshots_taken', 0)
                    }

        # Salva relatório
        try:
            report_dir = Path(f"analyses_data/files/{session_id}")
            report_dir.mkdir(parents=True, exist_ok=True)
            
            report_path = report_dir / "masterclass_analysis_report.json"
            with open(report_path, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            
            logger.info(f"📋 Relatório salvo: {report_path}")
            
        except Exception as e:
            logger.error(f"❌ Erro ao salvar relatório: {e}")

        return report


# Instância global
google_masterclass_extractor = GoogleSocialMasterclassExtractor()

# Funções de conveniência
async def extract_masterclass_content(query: str, session_id: str, platforms: List[str] = None) -> Dict[str, Any]:
    """Extrai conteúdo masterclass usando Google"""
    return await google_masterclass_extractor.extract_masterclass_content(query, session_id, platforms)

async def generate_masterclass_report(extraction_results: Dict[str, Any], session_id: str) -> Dict[str, Any]:
    """Gera relatório dos resultados"""
    return await google_masterclass_extractor.generate_masterclass_report(extraction_results, session_id)
