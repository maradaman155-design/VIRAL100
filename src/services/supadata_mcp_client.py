
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ARQV30 Enhanced v3.0 - Supadata MCP Client
Cliente para integração com Supadata MCP
"""

import os
import logging
import httpx
import asyncio
from typing import Dict, Any, Optional, List
from datetime import datetime

logger = logging.getLogger(__name__)

class SupadataClient:
    """Cliente para Supadata MCP"""

    def __init__(self):
        """Inicializa o cliente Supadata"""
        self.mcp_url = os.getenv('SUPADATA_MCP_URL')
        self.timeout = 60
        
        if not self.mcp_url:
            logger.warning("⚠️ SUPADATA_MCP_URL não configurado")
        else:
            logger.info(f"📊 Supadata Client inicializado: {self.mcp_url}")

    async def search(self, query: str, platform: str = "all") -> Dict[str, Any]:
        """
        Busca dados de redes sociais usando Supadata MCP
        
        Args:
            query: Termo de busca
            platform: Plataforma específica ou "all" para todas
        """
        if not self.mcp_url:
            return {
                'success': False,
                'error': 'SUPADATA_MCP_URL não configurado',
                'source': 'Supadata'
            }

        try:
            logger.info(f"📊 Buscando dados sociais para: {query} (plataforma: {platform})")
            
            # Payload para o MCP
            payload = {
                'method': 'social_search',
                'params': {
                    'query': query,
                    'platform': platform,
                    'limit': 100,
                    'include_metrics': True,
                    'include_sentiment': True,
                    'date_range': '30d'  # últimos 30 dias
                }
            }
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    self.mcp_url,
                    json=payload,
                    headers={
                        'Content-Type': 'application/json',
                        'User-Agent': 'ARQV30-Supadata/1.0'
                    }
                )
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Processa os resultados
                    social_data = {
                        'success': True,
                        'source': 'Supadata',
                        'query': query,
                        'platform': platform,
                        'timestamp': datetime.now().isoformat(),
                        'posts': data.get('result', {}).get('posts', []),
                        'profiles': data.get('result', {}).get('profiles', []),
                        'hashtags': data.get('result', {}).get('hashtags', []),
                        'mentions': data.get('result', {}).get('mentions', []),
                        'engagement_metrics': data.get('result', {}).get('engagement_metrics', {}),
                        'sentiment_analysis': data.get('result', {}).get('sentiment_analysis', {}),
                        'demographic_data': data.get('result', {}).get('demographic_data', {}),
                        'trending_topics': data.get('result', {}).get('trending_topics', []),
                        'influencer_data': data.get('result', {}).get('influencer_data', []),
                        'total_results': data.get('result', {}).get('total_results', 0)
                    }
                    
                    logger.info(f"✅ Supadata: {social_data['total_results']} resultados encontrados")
                    return social_data
                    
                else:
                    error_msg = f"Erro HTTP {response.status_code}: {response.text}"
                    logger.error(f"❌ Supadata erro: {error_msg}")
                    return {
                        'success': False,
                        'error': error_msg,
                        'source': 'Supadata'
                    }
                    
        except httpx.TimeoutException:
            error_msg = f"Timeout após {self.timeout}s"
            logger.error(f"❌ Supadata timeout: {error_msg}")
            return {
                'success': False,
                'error': error_msg,
                'source': 'Supadata'
            }
            
        except Exception as e:
            error_msg = f"Erro inesperado: {str(e)}"
            logger.error(f"❌ Supadata erro: {error_msg}")
            return {
                'success': False,
                'error': error_msg,
                'source': 'Supadata'
            }

    async def get_profile_analytics(self, profile_handle: str, platform: str) -> Dict[str, Any]:
        """
        Obtém análise detalhada de um perfil específico
        
        Args:
            profile_handle: Handle/username do perfil
            platform: Plataforma do perfil
        """
        if not self.mcp_url:
            return {
                'success': False,
                'error': 'SUPADATA_MCP_URL não configurado',
                'source': 'Supadata'
            }

        try:
            payload = {
                'method': 'profile_analytics',
                'params': {
                    'profile_handle': profile_handle,
                    'platform': platform,
                    'metrics_depth': 'detailed',
                    'include_content': True,
                    'include_audience': True
                }
            }
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    self.mcp_url,
                    json=payload,
                    headers={'Content-Type': 'application/json'}
                )
                
                if response.status_code == 200:
                    data = response.json()
                    return {
                        'success': True,
                        'source': 'Supadata',
                        'profile_data': data.get('result', {}),
                        'timestamp': datetime.now().isoformat()
                    }
                else:
                    return {
                        'success': False,
                        'error': f"HTTP {response.status_code}",
                        'source': 'Supadata'
                    }
                    
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'source': 'Supadata'
            }

    async def get_hashtag_analytics(self, hashtag: str, platforms: List[str] = None) -> Dict[str, Any]:
        """
        Obtém análise de performance de hashtag
        
        Args:
            hashtag: Hashtag para analisar (sem #)
            platforms: Lista de plataformas para analisar
        """
        if not self.mcp_url:
            return {
                'success': False,
                'error': 'SUPADATA_MCP_URL não configurado',
                'source': 'Supadata'
            }

        try:
            payload = {
                'method': 'hashtag_analytics',
                'params': {
                    'hashtag': hashtag,
                    'platforms': platforms or ['instagram', 'twitter', 'tiktok'],
                    'time_range': '30d',
                    'include_related': True
                }
            }
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    self.mcp_url,
                    json=payload,
                    headers={'Content-Type': 'application/json'}
                )
                
                if response.status_code == 200:
                    data = response.json()
                    return {
                        'success': True,
                        'source': 'Supadata',
                        'hashtag_analytics': data.get('result', {}),
                        'timestamp': datetime.now().isoformat()
                    }
                else:
                    return {
                        'success': False,
                        'error': f"HTTP {response.status_code}",
                        'source': 'Supadata'
                    }
                    
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'source': 'Supadata'
            }

    async def search_competitors(self, brand_keywords: List[str], industry: str) -> Dict[str, Any]:
        """
        Busca concorrentes baseado em palavras-chave da marca
        
        Args:
            brand_keywords: Lista de palavras-chave da marca
            industry: Setor/indústria
        """
        if not self.mcp_url:
            return {
                'success': False,
                'error': 'SUPADATA_MCP_URL não configurado',
                'source': 'Supadata'
            }

        try:
            payload = {
                'method': 'competitor_search',
                'params': {
                    'brand_keywords': brand_keywords,
                    'industry': industry,
                    'limit': 50,
                    'include_metrics': True,
                    'analysis_depth': 'comprehensive'
                }
            }
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    self.mcp_url,
                    json=payload,
                    headers={'Content-Type': 'application/json'}
                )
                
                if response.status_code == 200:
                    data = response.json()
                    return {
                        'success': True,
                        'source': 'Supadata',
                        'competitors': data.get('result', {}).get('competitors', []),
                        'market_analysis': data.get('result', {}).get('market_analysis', {}),
                        'timestamp': datetime.now().isoformat()
                    }
                else:
                    return {
                        'success': False,
                        'error': f"HTTP {response.status_code}",
                        'source': 'Supadata'
                    }
                    
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'source': 'Supadata'
            }

    def is_available(self) -> bool:
        """Verifica se o serviço está disponível"""
        return bool(self.mcp_url)

# Instância global
supadata_client = SupadataClient()
