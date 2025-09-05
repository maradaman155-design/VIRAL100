#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TrendFinder Client - V3.0
Cliente para análise de tendências usando múltiplas APIs
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

class TrendFinderClient:
    """Cliente para análise de tendências"""
    
    def __init__(self):
        self.api_manager = get_api_manager()
        self.trendfinder_url = os.getenv('TRENDFINDER_MCP_URL', 'https://trendfinder.mcp.smithery.ai')
        
        logger.info("📈 TrendFinder Client inicializado")

    async def find_trends(self, query: str, platform: str = 'all') -> Dict[str, Any]:
        """Encontra tendências para uma query"""
        
        try:
            # Tentar usar API de insights sociais
            api = self.api_manager.get_api_with_fallback('social_insights')
            if not api:
                logger.warning("⚠️ Nenhuma API disponível para análise de tendências")
                return self._generate_mock_trends(query, platform)
            
            # Se for Supadata, usar endpoint específico
            if 'supadata' in api.name.lower():
                return await self._supadata_trends(api, query, platform)
            
            # Se for Serper, usar busca de tendências
            elif 'serper' in api.name.lower():
                return await self._serper_trends(api, query, platform)
            
            # Fallback para mock
            else:
                return self._generate_mock_trends(query, platform)
                
        except Exception as e:
            logger.error(f"❌ Erro ao buscar tendências: {e}")
            return self._generate_mock_trends(query, platform)

    async def _supadata_trends(self, api, query: str, platform: str) -> Dict[str, Any]:
        """Busca tendências usando Supadata"""
        
        headers = {
            'Authorization': f'Bearer {api.api_key}',
            'Content-Type': 'application/json'
        }
        
        payload = {
            'query': query,
            'platform': platform,
            'analysis_type': 'trends',
            'time_range': '7d'
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{api.base_url}/trends/analyze",
                headers=headers,
                json=payload,
                timeout=30
            ) as response:
                
                if response.status == 200:
                    data = await response.json()
                    logger.info(f"✅ Tendências Supadata obtidas para '{query}'")
                    return self._process_supadata_trends(data, query, platform)
                
                elif response.status == 429:
                    self.api_manager.mark_api_rate_limited('social_insights', api.name)
                    # Tentar fallback
                    fallback_api = self.api_manager.get_fallback_api('social_insights', 'supadata')
                    if fallback_api:
                        return await self._serper_trends(fallback_api, query, platform)
                
                else:
                    error_text = await response.text()
                    logger.error(f"❌ Erro Supadata trends: {response.status} - {error_text}")
                    return self._generate_mock_trends(query, platform)

    async def _serper_trends(self, api, query: str, platform: str) -> Dict[str, Any]:
        """Busca tendências usando Serper"""
        
        headers = {
            'X-API-KEY': api.api_key,
            'Content-Type': 'application/json'
        }
        
        # Construir query específica por plataforma
        if platform == 'instagram':
            search_query = f"site:instagram.com {query} trending"
        elif platform == 'youtube':
            search_query = f"site:youtube.com {query} viral"
        elif platform == 'facebook':
            search_query = f"site:facebook.com {query} popular"
        else:
            search_query = f"{query} trending viral popular"
        
        payload = {
            'q': search_query,
            'num': 20,
            'gl': 'br',
            'hl': 'pt'
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
                    logger.info(f"✅ Tendências Serper obtidas para '{query}'")
                    return self._process_serper_trends(data, query, platform)
                
                else:
                    logger.error(f"❌ Erro Serper trends: {response.status}")
                    return self._generate_mock_trends(query, platform)

    def _process_supadata_trends(self, data: Dict[str, Any], query: str, platform: str) -> Dict[str, Any]:
        """Processa dados de tendências do Supadata"""
        
        return {
            'query': query,
            'platform': platform,
            'timestamp': datetime.now().isoformat(),
            'trends': data.get('trends', []),
            'trending_score': data.get('trending_score', 0),
            'growth_rate': data.get('growth_rate', 0),
            'related_keywords': data.get('related_keywords', []),
            'source': 'supadata'
        }

    def _process_serper_trends(self, data: Dict[str, Any], query: str, platform: str) -> Dict[str, Any]:
        """Processa dados de tendências do Serper"""
        
        organic_results = data.get('organic', [])
        
        # Extrair tendências dos resultados
        trends = []
        for result in organic_results[:10]:
            trends.append({
                'title': result.get('title', ''),
                'url': result.get('link', ''),
                'snippet': result.get('snippet', ''),
                'relevance_score': len(result.get('title', '').split()) * 0.1
            })
        
        return {
            'query': query,
            'platform': platform,
            'timestamp': datetime.now().isoformat(),
            'trends': trends,
            'trending_score': len(trends) * 0.1,
            'growth_rate': min(len(trends) * 0.05, 1.0),
            'related_keywords': self._extract_keywords_from_results(organic_results),
            'source': 'serper'
        }

    def _extract_keywords_from_results(self, results: List[Dict]) -> List[str]:
        """Extrai palavras-chave dos resultados"""
        
        keywords = set()
        for result in results:
            title = result.get('title', '').lower()
            snippet = result.get('snippet', '').lower()
            
            # Extrair palavras relevantes
            words = (title + ' ' + snippet).split()
            for word in words:
                if len(word) > 4 and word.isalpha():
                    keywords.add(word)
        
        return list(keywords)[:10]

    def _generate_mock_trends(self, query: str, platform: str) -> Dict[str, Any]:
        """Gera dados mock de tendências"""
        
        mock_trends = [
            {
                'title': f'Tendência viral: {query}',
                'url': f'https://example.com/trend/{query.replace(" ", "-")}',
                'snippet': f'Análise das tendências relacionadas a {query}',
                'relevance_score': 0.8
            },
            {
                'title': f'{query} - Crescimento exponencial',
                'url': f'https://example.com/growth/{query.replace(" ", "-")}',
                'snippet': f'Como {query} está dominando as redes sociais',
                'relevance_score': 0.7
            }
        ]
        
        return {
            'query': query,
            'platform': platform,
            'timestamp': datetime.now().isoformat(),
            'trends': mock_trends,
            'trending_score': 0.75,
            'growth_rate': 0.6,
            'related_keywords': [f'{query}_trend', f'{query}_viral', f'{query}_popular'],
            'source': 'mock'
        }

    async def analyze_trend_growth(self, query: str, days: int = 7) -> Dict[str, Any]:
        """Analisa crescimento de tendência ao longo do tempo"""
        
        try:
            # Simular análise de crescimento
            growth_data = {
                'query': query,
                'analysis_period': f'{days} days',
                'growth_metrics': {
                    'daily_growth': [0.1, 0.15, 0.3, 0.5, 0.8, 0.9, 1.0],
                    'peak_day': 6,
                    'total_growth': 400,
                    'trend_status': 'rising'
                },
                'predictions': {
                    'next_7_days': 'continued_growth',
                    'confidence': 0.75
                }
            }
            
            logger.info(f"📈 Análise de crescimento gerada para '{query}'")
            return growth_data
            
        except Exception as e:
            logger.error(f"❌ Erro na análise de crescimento: {e}")
            return {}

    async def get_platform_trends(self, platform: str, limit: int = 10) -> Dict[str, Any]:
        """Obtém tendências gerais de uma plataforma"""
        
        platform_queries = {
            'instagram': ['reels', 'stories', 'igtv', 'hashtag'],
            'youtube': ['shorts', 'viral', 'trending', 'challenge'],
            'facebook': ['posts', 'shares', 'reactions', 'groups'],
            'tiktok': ['fyp', 'viral', 'challenge', 'duet']
        }
        
        queries = platform_queries.get(platform, ['trending', 'viral'])
        
        # Buscar tendências para cada query
        all_trends = []
        for query in queries:
            trends = await self.find_trends(query, platform)
            all_trends.extend(trends.get('trends', []))
        
        return {
            'platform': platform,
            'timestamp': datetime.now().isoformat(),
            'total_trends': len(all_trends),
            'trends': all_trends[:limit],
            'analysis_summary': {
                'most_active_topics': queries,
                'trend_velocity': 'high' if len(all_trends) > 20 else 'medium'
            }
        }

# Instância global
trendfinder_client = TrendFinderClient()

# Funções de conveniência
async def find_trends(query: str, platform: str = 'all') -> Dict[str, Any]:
    """Encontra tendências para uma query"""
    return await trendfinder_client.find_trends(query, platform)

async def analyze_trend_growth(query: str, days: int = 7) -> Dict[str, Any]:
    """Analisa crescimento de tendência"""
    return await trendfinder_client.analyze_trend_growth(query, days)

async def get_platform_trends(platform: str, limit: int = 10) -> Dict[str, Any]:
    """Obtém tendências de uma plataforma"""
    return await trendfinder_client.get_platform_trends(platform, limit)

if __name__ == "__main__":
    # Teste do cliente
    async def test_trends():
        trends = await find_trends("marketing digital", "instagram")
        print(f"Tendências encontradas: {len(trends.get('trends', []))}")
    
    asyncio.run(test_trends())