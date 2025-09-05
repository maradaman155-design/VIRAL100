#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Supadata Social Insights Service - V3.0
Extração de insights, comentários e conteúdo relevante de redes sociais usando Supadata
"""

import os
import logging
import asyncio
import aiohttp
import json
from typing import Dict, List, Any, Optional
from datetime import datetime
from services.enhanced_api_rotation_manager import get_api_manager

logger = logging.getLogger(__name__)

class SupadataSocialInsights:
    """Serviço de insights sociais usando Supadata"""
    
    def __init__(self):
        self.api_manager = get_api_manager()
        self.base_url = os.getenv('SUPADATA_API_URL', 'https://api.supadata.ai/v1')
        
        logger.info("🔍 Supadata Social Insights Service inicializado")

    async def extract_instagram_insights(self, hashtag: str, limit: int = 50) -> Dict[str, Any]:
        """Extrai insights do Instagram usando Supadata"""
        
        try:
            # Obter API com fallback automático
            api = self.api_manager.get_api_with_fallback('social_insights')
            if not api:
                logger.error("❌ Nenhuma API disponível para insights sociais")
                return {}
            
            headers = {
                'Authorization': f'Bearer {api.api_key}',
                'Content-Type': 'application/json'
            }
            
            payload = {
                'platform': 'instagram',
                'query': hashtag,
                'limit': limit,
                'include_engagement': True,
                'include_comments': True,
                'include_sentiment': True
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{api.base_url}/social/instagram/insights",
                    headers=headers,
                    json=payload,
                    timeout=30
                ) as response:
                    
                    if response.status == 200:
                        data = await response.json()
                        logger.info(f"✅ Instagram insights extraídos: {len(data.get('posts', []))} posts")
                        return self._process_instagram_insights(data)
                    
                    elif response.status == 429:
                        self.api_manager.mark_api_rate_limited('social_insights', api.name)
                        # Tentar fallback
                        return await self._fallback_instagram_insights(hashtag, limit)
                    
                    else:
                        error_text = await response.text()
                        logger.error(f"❌ Erro Supadata Instagram: {response.status} - {error_text}")
                        return await self._fallback_instagram_insights(hashtag, limit)
        
        except Exception as e:
            logger.error(f"❌ Erro ao extrair insights Instagram: {e}")
            return await self._fallback_instagram_insights(hashtag, limit)

    async def extract_youtube_insights(self, query: str, limit: int = 30) -> Dict[str, Any]:
        """Extrai insights do YouTube usando Supadata"""
        
        try:
            api = self.api_manager.get_api_with_fallback('social_insights')
            if not api:
                return {}
            
            headers = {
                'Authorization': f'Bearer {api.api_key}',
                'Content-Type': 'application/json'
            }
            
            payload = {
                'platform': 'youtube',
                'query': query,
                'limit': limit,
                'include_thumbnails': True,
                'include_comments': True,
                'include_metrics': True
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{api.base_url}/social/youtube/insights",
                    headers=headers,
                    json=payload,
                    timeout=30
                ) as response:
                    
                    if response.status == 200:
                        data = await response.json()
                        logger.info(f"✅ YouTube insights extraídos: {len(data.get('videos', []))} vídeos")
                        return self._process_youtube_insights(data)
                    
                    elif response.status == 429:
                        self.api_manager.mark_api_rate_limited('social_insights', api.name)
                        return await self._fallback_youtube_insights(query, limit)
                    
                    else:
                        error_text = await response.text()
                        logger.error(f"❌ Erro Supadata YouTube: {response.status} - {error_text}")
                        return await self._fallback_youtube_insights(query, limit)
        
        except Exception as e:
            logger.error(f"❌ Erro ao extrair insights YouTube: {e}")
            return await self._fallback_youtube_insights(query, limit)

    async def extract_facebook_insights(self, query: str, limit: int = 40) -> Dict[str, Any]:
        """Extrai insights do Facebook usando Supadata"""
        
        try:
            api = self.api_manager.get_api_with_fallback('social_insights')
            if not api:
                return {}
            
            headers = {
                'Authorization': f'Bearer {api.api_key}',
                'Content-Type': 'application/json'
            }
            
            payload = {
                'platform': 'facebook',
                'query': query,
                'limit': limit,
                'include_engagement': True,
                'include_shares': True,
                'include_reactions': True
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{api.base_url}/social/facebook/insights",
                    headers=headers,
                    json=payload,
                    timeout=30
                ) as response:
                    
                    if response.status == 200:
                        data = await response.json()
                        logger.info(f"✅ Facebook insights extraídos: {len(data.get('posts', []))} posts")
                        return self._process_facebook_insights(data)
                    
                    elif response.status == 429:
                        self.api_manager.mark_api_rate_limited('social_insights', api.name)
                        return await self._fallback_facebook_insights(query, limit)
                    
                    else:
                        error_text = await response.text()
                        logger.error(f"❌ Erro Supadata Facebook: {response.status} - {error_text}")
                        return await self._fallback_facebook_insights(query, limit)
        
        except Exception as e:
            logger.error(f"❌ Erro ao extrair insights Facebook: {e}")
            return await self._fallback_facebook_insights(query, limit)

    async def get_comprehensive_social_insights(self, query: str) -> Dict[str, Any]:
        """Obtém insights abrangentes de todas as redes sociais"""
        
        logger.info(f"🔍 Extraindo insights sociais abrangentes para: '{query}'")
        
        # Executar extrações em paralelo
        tasks = [
            self.extract_instagram_insights(query, 30),
            self.extract_youtube_insights(query, 20),
            self.extract_facebook_insights(query, 25)
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        instagram_data, youtube_data, facebook_data = results
        
        # Consolidar insights
        comprehensive_insights = {
            'query': query,
            'extraction_timestamp': datetime.now().isoformat(),
            'platforms': {
                'instagram': instagram_data if isinstance(instagram_data, dict) else {},
                'youtube': youtube_data if isinstance(youtube_data, dict) else {},
                'facebook': facebook_data if isinstance(facebook_data, dict) else {}
            },
            'summary': self._generate_insights_summary(instagram_data, youtube_data, facebook_data)
        }
        
        logger.info(f"✅ Insights sociais abrangentes extraídos para '{query}'")
        return comprehensive_insights

    def _process_instagram_insights(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Processa insights do Instagram"""
        
        processed = {
            'total_posts': len(data.get('posts', [])),
            'top_posts': [],
            'engagement_metrics': {},
            'trending_hashtags': [],
            'sentiment_analysis': {}
        }
        
        posts = data.get('posts', [])
        
        # Processar top posts por engajamento
        sorted_posts = sorted(posts, key=lambda x: x.get('engagement_score', 0), reverse=True)
        processed['top_posts'] = sorted_posts[:10]
        
        # Calcular métricas de engajamento
        if posts:
            total_likes = sum(post.get('likes', 0) for post in posts)
            total_comments = sum(post.get('comments', 0) for post in posts)
            
            processed['engagement_metrics'] = {
                'avg_likes': total_likes / len(posts),
                'avg_comments': total_comments / len(posts),
                'total_engagement': total_likes + total_comments
            }
        
        return processed

    def _process_youtube_insights(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Processa insights do YouTube"""
        
        processed = {
            'total_videos': len(data.get('videos', [])),
            'top_videos': [],
            'view_metrics': {},
            'thumbnail_analysis': []
        }
        
        videos = data.get('videos', [])
        
        # Processar top vídeos por visualizações
        sorted_videos = sorted(videos, key=lambda x: x.get('views', 0), reverse=True)
        processed['top_videos'] = sorted_videos[:10]
        
        # Calcular métricas de visualização
        if videos:
            total_views = sum(video.get('views', 0) for video in videos)
            processed['view_metrics'] = {
                'avg_views': total_views / len(videos),
                'total_views': total_views
            }
        
        return processed

    def _process_facebook_insights(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Processa insights do Facebook"""
        
        processed = {
            'total_posts': len(data.get('posts', [])),
            'top_posts': [],
            'engagement_metrics': {},
            'reaction_analysis': {}
        }
        
        posts = data.get('posts', [])
        
        # Processar top posts por engajamento
        sorted_posts = sorted(posts, key=lambda x: x.get('total_reactions', 0), reverse=True)
        processed['top_posts'] = sorted_posts[:10]
        
        return processed

    def _generate_insights_summary(self, instagram_data, youtube_data, facebook_data) -> Dict[str, Any]:
        """Gera resumo dos insights"""
        
        summary = {
            'total_content_analyzed': 0,
            'platform_performance': {},
            'key_insights': [],
            'recommendations': []
        }
        
        # Contar conteúdo total
        if isinstance(instagram_data, dict):
            summary['total_content_analyzed'] += instagram_data.get('total_posts', 0)
        if isinstance(youtube_data, dict):
            summary['total_content_analyzed'] += youtube_data.get('total_videos', 0)
        if isinstance(facebook_data, dict):
            summary['total_content_analyzed'] += facebook_data.get('total_posts', 0)
        
        return summary

    # Métodos de fallback usando Serper
    async def _fallback_instagram_insights(self, hashtag: str, limit: int) -> Dict[str, Any]:
        """Fallback para Instagram usando Serper"""
        logger.info("🔄 Usando Serper como fallback para Instagram")
        
        try:
            api = self.api_manager.get_fallback_api('social_insights', 'supadata')
            if not api or 'serper' not in api.name:
                return {}
            
            # Implementar busca via Serper
            search_query = f"site:instagram.com #{hashtag}"
            return await self._serper_search(api, search_query, 'instagram')
            
        except Exception as e:
            logger.error(f"❌ Fallback Instagram falhou: {e}")
            return {}

    async def _fallback_youtube_insights(self, query: str, limit: int) -> Dict[str, Any]:
        """Fallback para YouTube usando Serper"""
        logger.info("🔄 Usando Serper como fallback para YouTube")
        
        try:
            api = self.api_manager.get_fallback_api('social_insights', 'supadata')
            if not api or 'serper' not in api.name:
                return {}
            
            search_query = f"site:youtube.com {query}"
            return await self._serper_search(api, search_query, 'youtube')
            
        except Exception as e:
            logger.error(f"❌ Fallback YouTube falhou: {e}")
            return {}

    async def _fallback_facebook_insights(self, query: str, limit: int) -> Dict[str, Any]:
        """Fallback para Facebook usando Serper"""
        logger.info("🔄 Usando Serper como fallback para Facebook")
        
        try:
            api = self.api_manager.get_fallback_api('social_insights', 'supadata')
            if not api or 'serper' not in api.name:
                return {}
            
            search_query = f"site:facebook.com {query}"
            return await self._serper_search(api, search_query, 'facebook')
            
        except Exception as e:
            logger.error(f"❌ Fallback Facebook falhou: {e}")
            return {}

    async def _serper_search(self, api, query: str, platform: str) -> Dict[str, Any]:
        """Executa busca usando Serper"""
        
        headers = {
            'X-API-KEY': api.api_key,
            'Content-Type': 'application/json'
        }
        
        payload = {
            'q': query,
            'num': 20
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{api.base_url}/search",
                headers=headers,
                json=payload,
                timeout=15
            ) as response:
                
                if response.status == 200:
                    data = await response.json()
                    return self._process_serper_results(data, platform)
                else:
                    logger.error(f"❌ Erro Serper: {response.status}")
                    return {}

    def _process_serper_results(self, data: Dict[str, Any], platform: str) -> Dict[str, Any]:
        """Processa resultados do Serper"""
        
        results = data.get('organic', [])
        
        processed = {
            'total_results': len(results),
            'platform': platform,
            'results': results[:10],
            'fallback_used': 'serper'
        }
        
        return processed

# Instância global
supadata_insights = SupadataSocialInsights()

# Funções de conveniência
async def get_instagram_insights(hashtag: str, limit: int = 50) -> Dict[str, Any]:
    """Obtém insights do Instagram"""
    return await supadata_insights.extract_instagram_insights(hashtag, limit)

async def get_youtube_insights(query: str, limit: int = 30) -> Dict[str, Any]:
    """Obtém insights do YouTube"""
    return await supadata_insights.extract_youtube_insights(query, limit)

async def get_facebook_insights(query: str, limit: int = 40) -> Dict[str, Any]:
    """Obtém insights do Facebook"""
    return await supadata_insights.extract_facebook_insights(query, limit)

async def get_comprehensive_insights(query: str) -> Dict[str, Any]:
    """Obtém insights abrangentes de todas as redes sociais"""
    return await supadata_insights.get_comprehensive_social_insights(query)

if __name__ == "__main__":
    # Teste do serviço
    async def test_insights():
        query = "marketing digital"
        insights = await get_comprehensive_insights(query)
        print(f"Insights extraídos: {insights.get('summary', {})}")
    
    asyncio.run(test_insights())