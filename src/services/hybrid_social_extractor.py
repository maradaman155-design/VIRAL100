#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Hybrid Social Media Extractor - V3.0
Serviço híbrido: Playwright + Chromium (principal) → Scrapy + Splash (fallback)
"""

import os
import asyncio
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)

# Importar ambos os extratores
try:
    from .playwright_social_extractor import PlaywrightSocialExtractor
    PLAYWRIGHT_AVAILABLE = True
except ImportError as e:
    logger.warning(f"⚠️ Playwright não disponível: {e}")
    PLAYWRIGHT_AVAILABLE = False

try:
    from .scrapy_social_extractor import ScrapySocialExtractor
    SCRAPY_AVAILABLE = True
except ImportError as e:
    logger.warning(f"⚠️ Scrapy não disponível: {e}")
    logger.info("💡 Para usar Scrapy, instale: pip install scrapy scrapy-splash")
    SCRAPY_AVAILABLE = False

from .enhanced_api_rotation_manager import get_api_manager

class HybridSocialExtractor:
    """Extrator híbrido com fallback automático"""

    def __init__(self):
        self.api_manager = get_api_manager()

        # Inicializar extratores disponíveis
        self.playwright_extractor = None
        self.scrapy_extractor = None

        if PLAYWRIGHT_AVAILABLE:
            try:
                self.playwright_extractor = PlaywrightSocialExtractor()
                logger.info("✅ Playwright Extractor inicializado")
            except Exception as e:
                logger.warning(f"⚠️ Erro ao inicializar Playwright: {e}")

        if SCRAPY_AVAILABLE:
            try:
                self.scrapy_extractor = ScrapySocialExtractor()
                logger.info("✅ Scrapy Extractor inicializado")
            except Exception as e:
                logger.warning(f"⚠️ Erro ao inicializar Scrapy: {e}")

        # Configurar estratégia de fallback
        self.extraction_strategies = []

        if self.playwright_extractor:
            self.extraction_strategies.append(('playwright', self.playwright_extractor))

        if self.scrapy_extractor:
            self.extraction_strategies.append(('scrapy', self.scrapy_extractor))

        if not self.extraction_strategies:
            logger.error("❌ Nenhum extrator disponível!")
            self.extraction_strategies.append(('mock', None))

        logger.info(f"🔄 Hybrid Extractor inicializado com {len(self.extraction_strategies)} estratégias")

    async def extract_viral_content(self, query: str, platforms: List[str] = None) -> Dict[str, Any]:
        """Extrai conteúdo viral usando estratégia híbrida"""

        if platforms is None:
            platforms = ['instagram', 'youtube', 'facebook']

        logger.info(f"🎯 Iniciando extração híbrida para '{query}'")

        # Tentar cada estratégia em ordem de prioridade
        for strategy_name, extractor in self.extraction_strategies:
            try:
                logger.info(f"🔄 Tentando estratégia: {strategy_name.upper()}")

                if strategy_name == 'playwright':
                    # Garante headless no ambiente sem X server
                    if hasattr(extractor, 'config'):
                        extractor.config['headless'] = True
                    results = await self._extract_with_playwright(extractor, query, platforms)
                elif strategy_name == 'scrapy':
                    results = await self._extract_with_scrapy(extractor, query, platforms)
                else:
                    results = self._extract_mock_fallback(query, platforms)

                # Verificar se obtivemos resultados válidos
                if self._validate_results(results):
                    results['extraction_method'] = strategy_name
                    results['fallback_used'] = strategy_name != 'playwright'
                    logger.info(f"✅ Extração bem-sucedida com {strategy_name.upper()}")
                    return results
                else:
                    logger.warning(f"⚠️ Resultados insuficientes com {strategy_name}")
                    continue

            except Exception as e:
                logger.error(f"❌ Erro na estratégia {strategy_name}: {e}")
                continue

        # Se todas as estratégias falharam, retornar fallback básico
        logger.warning("⚠️ Todas as estratégias falharam, usando fallback básico")
        return self._extract_mock_fallback(query, platforms)

    async def _extract_with_playwright(self, extractor, query: str, platforms: List[str]) -> Dict[str, Any]:
        """Extração usando Playwright"""

        try:
            # Tenta extrair diretamente sem health check para melhor performance
            try:
                await extractor.start_browser()
                results = await extractor.extract_viral_content(query, 'session_temp', max_items=15)
                return results
            finally:
                try:
                    await extractor.stop_browser()
                except:
                    pass

        except Exception as e:
            logger.error(f"❌ Erro no Playwright: {e}")
            raise

    async def _extract_with_scrapy(self, extractor, query: str, platforms: List[str]) -> Dict[str, Any]:
        """Extração usando Scrapy + Splash"""

        try:
            # Executar em thread separada para não bloquear
            loop = asyncio.get_event_loop()
            results = await loop.run_in_executor(
                None, 
                extractor.extract_viral_content, 
                query, 
                platforms
            )
            return results

        except Exception as e:
            logger.error(f"❌ Erro no Scrapy: {e}")
            raise

    async def _check_playwright_health(self) -> bool:
        """Verifica se Playwright está funcionando"""

        try:
            from playwright.async_api import async_playwright

            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                page = await browser.new_page()

                try:
                    await page.goto("https://httpbin.org/get", wait_until="load", timeout=30000)
                    await browser.close()
                    return True
                except Exception as e:
                    logger.warning(f"⚠️ Playwright health check falhou: {e}")
                    await browser.close()
                    return False

        except Exception as e:
            logger.warning(f"⚠️ Playwright health check falhou: {e}")
            return False

    def _validate_results(self, results: Dict[str, Any]) -> bool:
        """Valida se os resultados são suficientes"""

        if not results or not isinstance(results, dict):
            return False

        total_content = results.get('total_content', 0)
        platforms = results.get('platforms', {})

        # Verificar se temos pelo menos algum conteúdo
        if total_content == 0:
            return False

        # Verificar se pelo menos uma plataforma retornou dados
        valid_platforms = 0
        for platform, data in platforms.items():
            if isinstance(data, dict) and data.get('posts') and len(data['posts']) > 0:
                valid_platforms += 1

        return valid_platforms > 0

    def _extract_mock_fallback(self, query: str, platforms: List[str]) -> Dict[str, Any]:
        """Fallback básico com dados mock"""

        logger.info("🔄 Usando fallback mock")

        results = {
            'query': query,
            'timestamp': datetime.now().isoformat(),
            'platforms': {},
            'total_content': 0,
            'extraction_method': 'mock_fallback',
            'fallback_used': True
        }

        # Gerar dados mock para cada plataforma
        for platform in platforms:
            mock_posts = self._generate_enhanced_mock_posts(platform, query)

            results['platforms'][platform] = {
                'platform': platform,
                'posts': mock_posts,
                'total_posts': len(mock_posts),
                'extraction_method': 'mock'
            }

            results['total_content'] += len(mock_posts)

        return results

    def _generate_enhanced_mock_posts(self, platform: str, query: str) -> List[Dict[str, Any]]:
        """Gera posts mock mais realistas"""

        mock_posts = []

        # Dados mais realistas baseados na plataforma
        platform_data = {
            'instagram': {
                'count': 8,
                'engagement_base': 1500,
                'image_size': '400x400'
            },
            'youtube': {
                'count': 6,
                'engagement_base': 10000,
                'image_size': '320x180'
            },
            'facebook': {
                'count': 6,
                'engagement_base': 800,
                'image_size': '500x300'
            }
        }

        config = platform_data.get(platform, {'count': 5, 'engagement_base': 1000, 'image_size': '400x300'})

        for i in range(config['count']):
            if platform == 'instagram':
                post = {
                    'platform': 'instagram',
                    'post_id': f'ig_mock_{i}',
                    'type': 'image',
                    'images': [{
                        'url': f'https://picsum.photos/{config["image_size"]}?random={query.replace(" ", "")}{i}',
                        'alt': f'{query} - Post viral {i+1}',
                        'type': 'image'
                    }],
                    'engagement': {
                        'likes': config['engagement_base'] + i * 200,
                        'comments': 50 + i * 10,
                        'shares': 20 + i * 5
                    },
                    'conversion_score': round((config['engagement_base'] + i * 200) * 0.1, 2)
                }
            elif platform == 'youtube':
                post = {
                    'platform': 'youtube',
                    'video_id': f'yt_mock_{i}',
                    'type': 'video',
                    'thumbnails': [{
                        'url': f'https://picsum.photos/{config["image_size"]}?random=yt{query.replace(" ", "")}{i}',
                        'type': 'thumbnail'
                    }],
                    'metadata': {
                        'title': f'{query} - Estratégia Viral #{i+1}',
                        'views': f'{config["engagement_base"] + i * 2000:,} visualizações',
                        'duration': f'{3 + i}:{"30" if i % 2 else "15"}'
                    },
                    'engagement': {
                        'likes': config['engagement_base'] + i * 500,
                        'comments': 100 + i * 20
                    }
                }
            elif platform == 'facebook':
                post = {
                    'platform': 'facebook',
                    'post_id': f'fb_mock_{i}',
                    'type': 'mixed',
                    'images': [{
                        'url': f'https://picsum.photos/{config["image_size"]}?random=fb{query.replace(" ", "")}{i}',
                        'type': 'image'
                    }],
                    'engagement': {
                        'likes': config['engagement_base'] + i * 150,
                        'comments': 30 + i * 8,
                        'shares': 15 + i * 3
                    }
                }

            mock_posts.append(post)

        return mock_posts

    async def extract_high_conversion_posts(self, query: str, min_engagement: int = 1000) -> Dict[str, Any]:
        """Extrai posts com alta conversão usando estratégia híbrida"""

        logger.info(f"🎯 Buscando posts de alta conversão para '{query}'")

        # Extrair conteúdo usando estratégia híbrida
        all_content = await self.extract_viral_content(query)

        high_conversion_posts = []

        for platform, data in all_content['platforms'].items():
            if 'posts' in data:
                for post in data['posts']:
                    engagement = post.get('engagement', {})
                    likes = engagement.get('likes', 0)

                    # Filtrar por engagement mínimo
                    if likes >= min_engagement:
                        if 'conversion_score' not in post:
                            post['conversion_score'] = self._calculate_conversion_score(post)
                        high_conversion_posts.append(post)

        # Ordenar por score de conversão
        high_conversion_posts.sort(key=lambda x: x.get('conversion_score', 0), reverse=True)

        return {
            'query': query,
            'high_conversion_posts': high_conversion_posts[:20],  # Top 20
            'total_found': len(high_conversion_posts),
            'min_engagement': min_engagement,
            'extraction_method': all_content.get('extraction_method', 'hybrid'),
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

        # Bonus por múltiplas imagens/thumbnails
        images_count = len(post.get('images', [])) + len(post.get('thumbnails', []))
        if images_count > 1:
            score *= 1.2

        # Bonus por metadata rica (YouTube)
        if post.get('metadata') and len(post['metadata']) > 2:
            score *= 1.1

        return round(score, 2)

    async def get_extraction_health(self) -> Dict[str, Any]:
        """Retorna status de saúde dos extratores"""

        health = {
            'timestamp': datetime.now().isoformat(),
            'strategies_available': len(self.extraction_strategies),
            'strategies': {}
        }

        for strategy_name, extractor in self.extraction_strategies:
            if strategy_name == 'playwright':
                is_healthy = await self._check_playwright_health()
            elif strategy_name == 'scrapy':
                is_healthy = self._check_scrapy_health()
            else:
                is_healthy = True  # Mock sempre disponível

            health['strategies'][strategy_name] = {
                'available': extractor is not None,
                'healthy': is_healthy,
                'priority': self.extraction_strategies.index((strategy_name, extractor))
            }

        return health

    def _check_scrapy_health(self) -> bool:
        """Verifica se Scrapy está funcionando"""

        try:
            import scrapy
            import scrapy_splash
            return True
        except ImportError:
            return False


# Instância global
hybrid_extractor = HybridSocialExtractor()

# Funções de conveniência
async def extract_viral_content_hybrid(query: str, platforms: List[str] = None) -> Dict[str, Any]:
    """Extrai conteúdo viral usando estratégia híbrida"""
    return await hybrid_extractor.extract_viral_content(query, platforms)

async def extract_high_conversion_posts_hybrid(query: str, min_engagement: int = 1000) -> Dict[str, Any]:
    """Extrai posts de alta conversão usando estratégia híbrida"""
    return await hybrid_extractor.extract_high_conversion_posts(query, min_engagement)

async def get_extractor_health() -> Dict[str, Any]:
    """Retorna status de saúde dos extratores"""
    return await hybrid_extractor.get_extraction_health()

if __name__ == "__main__":
    # Teste do extrator híbrido
    async def test_hybrid():
        # Testar extração
        results = await extract_viral_content_hybrid("marketing digital", ["youtube"])
        print(f"Conteúdo extraído: {results['total_content']} posts")
        print(f"Método usado: {results.get('extraction_method', 'unknown')}")

        # Testar saúde
        health = await get_extractor_health()
        print(f"Estratégias disponíveis: {health['strategies_available']}")

        for strategy, status in health['strategies'].items():
            print(f"  {strategy}: {'✅' if status['healthy'] else '❌'}")

    asyncio.run(test_hybrid())