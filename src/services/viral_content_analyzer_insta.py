#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ARQV30 Enhanced v3.0 - Instagram Screenshot Analyzer
Analisador especializado em screenshots do Instagram
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

logger = logging.getLogger(__name__)

# Playwright imports
try:
    from playwright.async_api import async_playwright
    HAS_PLAYWRIGHT = True
except ImportError:
    HAS_PLAYWRIGHT = False
    logger.error("Playwright não disponível. Execute: pip install playwright")

class InstagramScreenshotAnalyzer:
    """Analisador especializado em screenshots do Instagram"""

    def __init__(self):
        """Inicializa o analisador Instagram"""
        self.instagram_selectors = {
            'login_popup': [
                "//button[contains(text(), 'Agora não')]",
                "//button[contains(text(), 'Not Now')]", 
                "//button[@aria-label='Close']",
                "//div[@role='button'][contains(text(), 'Close')]"
            ],
            'cookie_popup': [
                "//button[contains(text(), 'Aceitar')]",
                "//button[contains(text(), 'Accept')]",
                "//button[contains(text(), 'Allow')]"
            ],
            'post_elements': [
                "//article[@role='presentation']",
                "//div[@role='presentation']",
                "//img[contains(@srcset, 's150x150')]",
                "//video"
            ],
            'story_elements': [
                "//div[contains(@class, 'story')]",
                "//canvas",
                "//video[contains(@class, 'story')]"
            ],
            'reel_elements': [
                "//div[contains(@class, 'reel')]",
                "//video[contains(@class, 'reel')]",
                "//section[contains(@class, 'reel')]"
            ]
        }

        self.screenshot_config = {
            'width': 1920,
            'height': 1080,
            'wait_time': 5,
            'scroll_pause': 2,
            'mobile_width': 375,
            'mobile_height': 812
        }

        self.instagram_thresholds = {
            'min_likes': 1000,
            'min_comments': 50,
            'min_views': 10000,
            'engagement_rate': 0.03
        }

        logger.info("📸 Instagram Screenshot Analyzer inicializado")

    async def analyze_instagram_viral_content(
        self,
        search_results: Dict[str, Any],
        session_id: str,
        max_screenshots: int = 20
    ) -> Dict[str, Any]:
        """Analisa e captura screenshots específicos do Instagram"""

        logger.info(f"📱 Iniciando análise Instagram para sessão: {session_id}")

        analysis_results = {
            'session_id': session_id,
            'analysis_started': datetime.now().isoformat(),
            'instagram_content': [],
            'screenshots_captured': [],
            'total_instagram_posts': 0,
            'viral_instagram_posts': 0,
            'engagement_metrics': {},
            'content_types': {
                'posts': 0,
                'stories': 0,
                'reels': 0,
                'igtv': 0
            }
        }

        try:
            # FASE 1: Filtrar apenas conteúdo do Instagram
            logger.info("🔍 FASE 1: Filtrando conteúdo do Instagram")
            instagram_content = self._filter_instagram_content(search_results)
            analysis_results['instagram_content'] = instagram_content
            analysis_results['total_instagram_posts'] = len(instagram_content)

            # FASE 2: Identificar conteúdo viral do Instagram
            logger.info("🔥 FASE 2: Identificando posts virais do Instagram")
            viral_instagram = self._identify_viral_instagram(instagram_content)
            analysis_results['viral_instagram_posts'] = len(viral_instagram)

            # FASE 3: Capturar screenshots específicos do Instagram
            logger.info("📸 FASE 3: Capturando screenshots do Instagram")
            screenshots = await self._capture_instagram_screenshots(
                viral_instagram, session_id, max_screenshots
            )
            analysis_results['screenshots_captured'] = screenshots

            # FASE 4: Analisar métricas do Instagram
            logger.info("📊 FASE 4: Analisando métricas do Instagram")
            engagement_metrics = self._calculate_instagram_metrics(viral_instagram)
            analysis_results['engagement_metrics'] = engagement_metrics

            # FASE 5: Classificar tipos de conteúdo
            content_types = self._classify_instagram_content_types(viral_instagram)
            analysis_results['content_types'] = content_types

            logger.info(f"✅ Análise Instagram concluída:")
            logger.info(f"   📱 Posts Instagram: {analysis_results['total_instagram_posts']}")
            logger.info(f"   🔥 Posts virais: {analysis_results['viral_instagram_posts']}")
            logger.info(f"   📸 Screenshots: {len(analysis_results['screenshots_captured'])}")

            return analysis_results

        except Exception as e:
            logger.error(f"❌ Erro na análise Instagram: {e}")
            raise

    def _filter_instagram_content(self, search_results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Filtra apenas conteúdo do Instagram dos resultados"""
        
        instagram_content = []
        
        # Processa todos os resultados
        all_content = []
        for result_type in ['web_results', 'social_results', 'youtube_results']:
            content_list = search_results.get(result_type, [])
            if isinstance(content_list, list):
                all_content.extend(content_list)
            elif isinstance(content_list, dict):
                # Se for dict, tenta extrair listas internas
                if 'results' in content_list:
                    all_content.extend(content_list['results'])
                elif 'platforms' in content_list:
                    platforms = content_list['platforms']
                    if isinstance(platforms, dict) and 'instagram' in platforms:
                        instagram_data = platforms['instagram']
                        if isinstance(instagram_data, dict) and 'results' in instagram_data:
                            all_content.extend(instagram_data['results'])
        
        # Filtra conteúdo do Instagram
        for content in all_content:
            if self._is_instagram_content(content):
                # Enriquece com dados específicos do Instagram
                enriched_content = self._enrich_instagram_content(content)
                instagram_content.append(enriched_content)
        
        return instagram_content

    def _is_instagram_content(self, content: Dict[str, Any]) -> bool:
        """Verifica se o conteúdo é do Instagram"""
        
        url = content.get('url', '').lower()
        platform = content.get('platform', '').lower()
        source = content.get('source', '').lower()
        
        instagram_indicators = [
            'instagram.com' in url,
            'ig.com' in url,
            platform == 'instagram',
            'instagram' in source,
            'ig' == platform
        ]
        
        return any(instagram_indicators)

    def _enrich_instagram_content(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Enriquece conteúdo com dados específicos do Instagram"""
        
        enriched = content.copy()
        enriched['platform'] = 'instagram'
        
        # Detecta tipo de conteúdo Instagram
        url = content.get('url', '').lower()
        
        if '/reel/' in url or '/reels/' in url:
            enriched['instagram_type'] = 'reel'
        elif '/stories/' in url or '/story/' in url:
            enriched['instagram_type'] = 'story'
        elif '/tv/' in url or '/igtv/' in url:
            enriched['instagram_type'] = 'igtv'
        else:
            enriched['instagram_type'] = 'post'
        
        # Extrai dados de engajamento se disponíveis
        title = content.get('title', '').lower()
        description = content.get('description', '').lower()
        
        # Tenta extrair likes/comments da descrição
        likes_match = re.search(r'(\d+(?:,\d+)*)\s*likes?', title + ' ' + description)
        comments_match = re.search(r'(\d+(?:,\d+)*)\s*comments?', title + ' ' + description)
        views_match = re.search(r'(\d+(?:,\d+)*)\s*views?', title + ' ' + description)
        
        if likes_match:
            enriched['likes'] = int(likes_match.group(1).replace(',', ''))
        
        if comments_match:
            enriched['comments'] = int(comments_match.group(1).replace(',', ''))
            
        if views_match:
            enriched['views'] = int(views_match.group(1).replace(',', ''))
        
        return enriched

    def _identify_viral_instagram(self, instagram_content: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Identifica posts virais específicos do Instagram"""
        
        viral_posts = []
        
        for content in instagram_content:
            viral_score = self._calculate_instagram_viral_score(content)
            
            if viral_score >= 5.0:  # Threshold para viral
                content['viral_score'] = viral_score
                content['viral_category'] = self._categorize_instagram_viral(viral_score)
                viral_posts.append(content)
        
        # Ordena por score viral
        viral_posts.sort(key=lambda x: x.get('viral_score', 0), reverse=True)
        
        return viral_posts

    def _calculate_instagram_viral_score(self, content: Dict[str, Any]) -> float:
        """Calcula score viral específico para Instagram"""
        
        try:
            likes = int(content.get('likes', 0))
            comments = int(content.get('comments', 0))
            views = int(content.get('views', 0))
            shares = int(content.get('shares', 0))
            
            # Fórmula específica Instagram
            # Posts: likes/100 + comments/10 + shares/5
            # Reels/IGTV: views/1000 + likes/50 + comments/5
            
            instagram_type = content.get('instagram_type', 'post')
            
            if instagram_type in ['reel', 'igtv']:
                score = (views / 1000) + (likes / 50) + (comments / 5) + (shares / 2)
            else:  # post, story
                score = (likes / 100) + (comments / 10) + (shares / 5)
            
            # Bônus por tipo de conteúdo
            type_bonus = {
                'reel': 1.2,
                'story': 1.1,
                'igtv': 1.15,
                'post': 1.0
            }
            
            score *= type_bonus.get(instagram_type, 1.0)
            
            return min(10.0, score / 20)  # Normaliza para 0-10
            
        except Exception as e:
            logger.warning(f"⚠️ Erro ao calcular score viral Instagram: {e}")
            return 0.0

    def _categorize_instagram_viral(self, viral_score: float) -> str:
        """Categoriza viralidade específica do Instagram"""
        
        if viral_score >= 9.0:
            return 'INSTAGRAM_MEGA_VIRAL'
        elif viral_score >= 7.0:
            return 'INSTAGRAM_VIRAL'
        elif viral_score >= 5.0:
            return 'INSTAGRAM_TRENDING'
        else:
            return 'INSTAGRAM_POPULAR'
    async def _capture_instagram_screenshots(
        self,
        viral_instagram: List[Dict[str, Any]],
        session_id: str,
        max_screenshots: int = 20
    ) -> List[Dict[str, Any]]:
        """Captura screenshots otimizados especificamente para Instagram"""

        screenshots = []
        browser = None
        context = None
        page = None

        try:
            if not HAS_PLAYWRIGHT:
                logger.error("❌ Playwright não disponível para screenshots Instagram")
                return screenshots

            async with async_playwright() as p:
                # Configuração específica para Instagram
                browser = await p.chromium.launch(
                    headless=True,
                    args=[
                        "--no-sandbox",
                        "--disable-setuid-sandbox", 
                        "--disable-dev-shm-usage",
                        "--disable-gpu",
                        "--disable-web-security",
                        "--disable-features=VizDisplayCompositor"
                    ]
                )

                # Context otimizado para Instagram
                context = await browser.new_context(
                    viewport={
                        "width": self.screenshot_config['width'], 
                        "height": self.screenshot_config['height']
                    },
                    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                    extra_http_headers={
                        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                        "Accept-Language": "pt-BR,pt;q=0.9,en;q=0.8",
                        "Accept-Encoding": "gzip, deflate, br"
                    }
                )

                page = await context.new_page()
                logger.info("✅ Playwright Instagram context iniciado")

                # Diretório para screenshots
                screenshots_dir = Path(f"analyses_data/files/{session_id}")
                screenshots_dir.mkdir(parents=True, exist_ok=True)

                # Limita número de screenshots
                instagram_to_capture = viral_instagram[:max_screenshots]

                for i, content in enumerate(instagram_to_capture, 1):
                    try:
                        url = content.get('url', '').strip()
                        instagram_type = content.get('instagram_type', 'post')
                        
                        if not url or not url.startswith(('http://', 'https://')):
                            logger.warning(f"⚠️ URL inválida ignorada: '{url}'")
                            continue

                        logger.info(f"📸 Capturando Instagram {i}/{len(instagram_to_capture)}: {content.get('title', 'Sem título')}")

                        # Navegação com timeout otimizado
                        await page.goto(url, wait_until="networkidle", timeout=30000)

                        # Aguarda carregamento inicial
                        await asyncio.sleep(2)

                        # Tenta fechar popups específicos do Instagram
                        await self._handle_instagram_popups(page)

                        # Estratégias específicas por tipo de conteúdo
                        if instagram_type == 'reel':
                            await self._handle_instagram_reel(page)
                        elif instagram_type == 'story':
                            await self._handle_instagram_story(page)
                        elif instagram_type == 'igtv':
                            await self._handle_instagram_igtv(page)
                        else:  # post padrão
                            await self._handle_instagram_post(page)

                        # Aguarda elementos carregarem
                        await asyncio.sleep(self.screenshot_config['scroll_pause'])

                        # Scroll para garantir carregamento de conteúdo lazy
                        await page.evaluate("window.scrollTo(0, document.body.scrollHeight/3);")
                        await asyncio.sleep(1)
                        await page.evaluate("window.scrollTo(0, 0);")
                        await asyncio.sleep(1)

                        # Captura informações da página
                        page_title = await page.title() or content.get('title', 'Sem título')
                        current_url = page.url

                        # Nome do arquivo
                        filename = f"instagram_{instagram_type}_{i:03d}"
                        screenshot_path = screenshots_dir / f"{filename}.png"

                        # Captura screenshot
                        await page.screenshot(
                            path=str(screenshot_path), 
                            full_page=True,
                            quality=90
                        )

                        # Verifica se screenshot foi criado
                        if screenshot_path.exists() and screenshot_path.stat().st_size > 0:
                            logger.info(f"✅ Instagram screenshot salvo: {screenshot_path}")
                            
                            screenshots.append({
                                'success': True,
                                'url': url,
                                'final_url': current_url,
                                'title': page_title,
                                'platform': 'instagram',
                                'instagram_type': instagram_type,
                                'viral_score': content.get('viral_score', 0),
                                'viral_category': content.get('viral_category', 'N/A'),
                                'filename': f"{filename}.png",
                                'filepath': str(screenshot_path),
                                'relative_path': str(screenshot_path.relative_to(Path('analyses_data'))),
                                'filesize': screenshot_path.stat().st_size,
                                'timestamp': datetime.now().isoformat(),
                                'instagram_metrics': {
                                    'likes': content.get('likes', 0),
                                    'comments': content.get('comments', 0),
                                    'views': content.get('views', 0),
                                    'shares': content.get('shares', 0)
                                }
                            })
                        else:
                            raise Exception("Screenshot Instagram não foi criado ou está vazio")

                    except Exception as e:
                        logger.error(f"❌ Erro ao capturar screenshot Instagram de {url}: {e}")
                        screenshots.append({
                            'success': False,
                            'url': url,
                            'platform': 'instagram',
                            'instagram_type': content.get('instagram_type', 'unknown'),
                            'error': str(e),
                            'timestamp': datetime.now().isoformat()
                        })

        except Exception as e:
            logger.error(f"❌ Erro crítico na captura Instagram com Playwright: {e}")
        finally:
            if browser:
                try:
                    await browser.close()
                    logger.info("✅ Playwright Instagram browser fechado")
                except Exception as e:
                    logger.error(f"❌ Erro ao fechar browser Instagram: {e}")

        return screenshots

    async def _handle_instagram_popups(self, page) -> None: # Corrigido
        """Lida com popups específicos do Instagram"""
        
        try:
            # Popup de login/cadastro
            for selector in self.instagram_selectors['login_popup']:
                try:
                    await page.locator(selector).click(timeout=3000)
                    logger.info("✅ Fechou popup de login Instagram")
                    await asyncio.sleep(1)
                    break
                except Exception:
                    continue

            # Popup de cookies
            for selector in self.instagram_selectors['cookie_popup']:
                try:
                    await page.locator(selector).click(timeout=3000)
                    logger.info("✅ Fechou popup de cookies Instagram")
                    await asyncio.sleep(1)
                    break
                except Exception:
                    continue

            # Popup de notificações
            try:
                await page.locator("//button[contains(text(), 'Agora não')]").click(timeout=2000)
                logger.info("✅ Fechou popup de notificações Instagram")
            except Exception:
                pass

        except Exception as e:
            logger.warning(f"⚠️ Erro ao fechar popups Instagram: {e}")

    async def _handle_instagram_post(self, page) -> None:
        """Lida especificamente com posts do Instagram"""
        
        try:
            # Aguarda elementos de post carregarem
            for selector in self.instagram_selectors['post_elements']:
                try:
                    await page.locator(selector).wait_for(timeout=8000)
                    logger.info("✅ Elementos de post Instagram carregados")
                    break
                except Exception:
                    continue

            # Tenta expandir comentários se houver botão "Ver mais"
            try:
                await page.locator("//button[contains(text(), 'Ver mais')]").click(timeout=2000)
                await asyncio.sleep(1)
            except Exception:
                pass

        except Exception as e:
            logger.warning(f"⚠️ Erro ao lidar com post Instagram: {e}")

    async def _handle_instagram_reel(self, page) -> None:
        """Lida especificamente com reels do Instagram"""
        
        try:
            # Aguarda elementos de reel
            for selector in self.instagram_selectors['reel_elements']:
                try:
                    await page.locator(selector).wait_for(timeout=8000)
                    logger.info("✅ Elementos de reel Instagram carregados")
                    break
                except Exception:
                    continue

            # Pausa o vídeo se estiver reproduzindo
            try:
                await page.locator("//video").click(timeout=2000)
                await asyncio.sleep(0.5)
            except Exception:
                pass

        except Exception as e:
            logger.warning(f"⚠️ Erro ao lidar com reel Instagram: {e}")

    async def _handle_instagram_story(self, page) -> None:
        """Lida especificamente com stories do Instagram"""
        
        try:
            # Aguarda elementos de story
            for selector in self.instagram_selectors['story_elements']:
                try:
                    await page.locator(selector).wait_for(timeout=6000)
                    logger.info("✅ Elementos de story Instagram carregados")
                    break
                except Exception:
                    continue

            # Pausa story se houver controle
            try:
                await page.keyboard.press('Space')
                await asyncio.sleep(0.5)
            except Exception:
                pass

        except Exception as e:
            logger.warning(f"⚠️ Erro ao lidar com story Instagram: {e}")

    async def _handle_instagram_igtv(self, page) -> None:
        """Lida especificamente com IGTV do Instagram"""
        
        try:
            # Aguarda vídeo IGTV carregar
            try:
                await page.locator("//video").wait_for(timeout=8000)
                logger.info("✅ Vídeo IGTV Instagram carregado")
            except Exception:
                pass

            # Pausa o vídeo
            try:
                await page.locator("//video").click(timeout=2000)
                await asyncio.sleep(1)
            except Exception:
                pass

        except Exception as e:
            logger.warning(f"⚠️ Erro ao lidar com IGTV Instagram: {e}")

    def _calculate_instagram_metrics(self, viral_instagram: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calcula métricas específicas do Instagram"""
        
        total_likes = 0
        total_comments = 0
        total_views = 0
        total_shares = 0
        total_posts = len(viral_instagram)
        
        engagement_by_type = {
            'post': {'count': 0, 'total_engagement': 0},
            'reel': {'count': 0, 'total_engagement': 0},
            'story': {'count': 0, 'total_engagement': 0},
            'igtv': {'count': 0, 'total_engagement': 0}
        }

        for content in viral_instagram:
            likes = int(content.get('likes', 0))
            comments = int(content.get('comments', 0))
            views = int(content.get('views', 0))
            shares = int(content.get('shares', 0))
            instagram_type = content.get('instagram_type', 'post')
            
            total_likes += likes
            total_comments += comments
            total_views += views
            total_shares += shares
            
            # Engajamento por tipo
            if instagram_type in engagement_by_type:
                engagement_by_type[instagram_type]['count'] += 1
                engagement = likes + comments + shares
                if instagram_type in ['reel', 'igtv'] and views > 0:
                    engagement = (engagement / views) * 100  # Engagement rate
                engagement_by_type[instagram_type]['total_engagement'] += engagement

        # Calcula médias
        for content_type in engagement_by_type:
            count = engagement_by_type[content_type]['count']
            if count > 0:
                avg_engagement = engagement_by_type[content_type]['total_engagement'] / count
                engagement_by_type[content_type]['avg_engagement'] = round(avg_engagement, 2)

        return {
            'total_instagram_posts': total_posts,
            'total_likes': total_likes,
            'total_comments': total_comments,
            'total_views': total_views,
            'total_shares': total_shares,
            'avg_likes_per_post': round(total_likes / total_posts, 2) if total_posts > 0 else 0,
            'avg_comments_per_post': round(total_comments / total_posts, 2) if total_posts > 0 else 0,
            'engagement_by_type': engagement_by_type,
            'overall_engagement_rate': round((total_likes + total_comments + total_shares) / max(total_views, 1) * 100, 2)
        }

    def _classify_instagram_content_types(self, viral_instagram: List[Dict[str, Any]]) -> Dict[str, int]:
        """Classifica tipos de conteúdo Instagram"""
        
        content_types = {
            'posts': 0,
            'reels': 0,
            'stories': 0,
            'igtv': 0
        }

        for content in viral_instagram:
            instagram_type = content.get('instagram_type', 'post')
            
            if instagram_type == 'reel':
                content_types['reels'] += 1
            elif instagram_type == 'story':
                content_types['stories'] += 1
            elif instagram_type == 'igtv':
                content_types['igtv'] += 1
            else:
                content_types['posts'] += 1

        return content_types

    def generate_instagram_report(
        self,
        analysis_results: Dict[str, Any],
        session_id: str
    ) -> str:
        """Gera relatório específico do Instagram"""

        instagram_content = analysis_results.get('instagram_content', [])
        screenshots = analysis_results.get('screenshots_captured', [])
        metrics = analysis_results.get('engagement_metrics', {})
        content_types = analysis_results.get('content_types', {})

        report = f"""# RELATÓRIO INSTAGRAM VIRAL - ARQV30 v3.0

**Sessão:** {session_id}  
**Análise realizada em:** {analysis_results.get('analysis_started', 'N/A')}  
**Posts Instagram encontrados:** {analysis_results.get('total_instagram_posts', 0)}  
**Posts virais identificados:** {analysis_results.get('viral_instagram_posts', 0)}  
**Screenshots capturados:** {len(screenshots)}

---

## RESUMO EXECUTIVO INSTAGRAM

### Métricas Gerais:
- **Total de likes:** {metrics.get('total_likes', 0):,}
- **Total de comentários:** {metrics.get('total_comments', 0):,}
- **Total de visualizações:** {metrics.get('total_views', 0):,}
- **Taxa de engajamento geral:** {metrics.get('overall_engagement_rate', 0)}%

### Distribuição por Tipo de Conteúdo:
- **Posts tradicionais:** {content_types.get('posts', 0)}
- **Reels:** {content_types.get('reels', 0)}
- **Stories:** {content_types.get('stories', 0)}
- **IGTV:** {content_types.get('igtv', 0)}

---

## SCREENSHOTS INSTAGRAM CAPTURADOS

"""

        success_screenshots = [s for s in screenshots if s.get('success', False)]
        
        for i, screenshot in enumerate(success_screenshots, 1):
            report += f"""### Screenshot {i}: {screenshot.get('title', 'Sem título')}

**Tipo Instagram:** {screenshot.get('instagram_type', 'N/A').title()}  
**Score Viral:** {screenshot.get('viral_score', 0):.2f}/10  
**Categoria:** {screenshot.get('viral_category', 'N/A')}  
**URL:** {screenshot.get('url', 'N/A')}  

![Instagram Screenshot {i}]({screenshot.get('relative_path', '')})

**Métricas de Engajamento:**
"""
            
            metrics = screenshot.get('instagram_metrics', {})
            if metrics.get('likes'):
                report += f"- 👍 Likes: {metrics['likes']:,}  \n"
            if metrics.get('comments'):
                report += f"- 💬 Comentários: {metrics['comments']:,}  \n"
            if metrics.get('views'):
                report += f"- 👀 Visualizações: {metrics['views']:,}  \n"
            if metrics.get('shares'):
                report += f"- 🔄 Compartilhamentos: {metrics['shares']:,}  \n"

            report += "\n"

        report += f"""---

## INSIGHTS INSTAGRAM

### Performance por Tipo de Conteúdo:
"""

        engagement_by_type = metrics.get('engagement_by_type', {})
        for content_type, data in engagement_by_type.items():
            if data.get('count', 0) > 0:
                report += f"- **{content_type.title()}:** {data['count']} posts, engajamento médio: {data.get('avg_engagement', 0):.2f}  \n"

        report += f"""
### Recomendações Instagram:
1. **Melhor tipo de conteúdo:** {'Reels' if content_types.get('reels', 0) > 0 else 'Posts tradicionais'}
2. **Engajamento médio por post:** {metrics.get('avg_likes_per_post', 0):.0f} likes
3. **Potencial viral:** {'Alto' if metrics.get('overall_engagement_rate', 0) > 5 else 'Médio'}

---

*Relatório Instagram gerado automaticamente em {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}*
"""

        return report


# Instância global
instagram_screenshot_analyzer = InstagramScreenshotAnalyzer()

def get_viral_content_analyzer():
    """Retorna a instância global do Instagram Screenshot Analyzer"""
    return instagram_screenshot_analyzer