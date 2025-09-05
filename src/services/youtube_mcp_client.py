
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ARQV30 Enhanced v2.0 - YouTube MCP Client
Cliente para pesquisa no YouTube usando MCP
"""

import os
import logging
import requests
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)

class YouTubeMCPClient:
    """Cliente para pesquisa no YouTube usando MCP"""

    def __init__(self):
        """Inicializa o cliente YouTube MCP"""
        self.base_url = os.getenv('YOUTUBE_MCP_URL', 'https://api.youtube-mcp.ai/v1')
        self.api_key = os.getenv('YOUTUBE_API_KEY')
        
        self.headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.api_key}' if self.api_key else '',
            'User-Agent': 'ARQV30-Enhanced/2.0'
        }

        self.is_available = bool(self.api_key)
        
        if self.is_available:
            logger.info("✅ YouTube MCP Client ATIVO")
        else:
            logger.warning("⚠️ YouTube API não configurada - sem simulação e sem fallback")

    async def search_videos(self, query: str, max_results: int = 25) -> Dict[str, Any]:
        """Busca vídeos no YouTube"""
        try:
            if not self.is_available:
                # Sem simulação quando API não está disponível
                return {"success": False, "provider": "youtube", "videos": [], "total_found": 0, "query": query, "message": "YouTube API ausente"}

            logger.info(f"🎥 Buscando no YouTube: {query}")

            payload = {
                "query": query,
                "max_results": max_results,
                "order": "relevance",
                "type": "video",
                "region_code": "BR",
                "relevance_language": "pt"
            }

            response = requests.post(
                f"{self.base_url}/search",
                json=payload,
                headers=self.headers,
                timeout=30
            )

            if response.status_code == 200:
                data = response.json()
                return self._process_youtube_results(data, query)
            else:
                logger.warning(f"⚠️ YouTube API erro {response.status_code}")
                return {"success": False, "provider": "youtube", "videos": [], "total_found": 0, "query": query, "message": f"HTTP {response.status_code}"}

        except Exception as e:
            logger.error(f"❌ Erro YouTube: {e}")
            return {"success": False, "provider": "youtube", "videos": [], "total_found": 0, "query": query, "message": str(e)}

    def _process_youtube_results(self, data: Dict[str, Any], query: str) -> Dict[str, Any]:
        """Processa resultados do YouTube"""
        processed_results = []
        
        for item in data.get('items', []):
            snippet = item.get('snippet', {})
            statistics = item.get('statistics', {})
            
            processed_results.append({
                'video_id': item.get('id', {}).get('videoId', ''),
                'title': snippet.get('title', ''),
                'description': snippet.get('description', ''),
                'channel_title': snippet.get('channelTitle', ''),
                'published_at': snippet.get('publishedAt', ''),
                'thumbnail_url': snippet.get('thumbnails', {}).get('medium', {}).get('url', ''),
                'view_count': statistics.get('viewCount', '0'),
                'like_count': statistics.get('likeCount', '0'),
                'comment_count': statistics.get('commentCount', '0'),
                'url': f"https://youtube.com/watch?v={item.get('id', {}).get('videoId', '')}",
                'platform': 'youtube',
                'query_used': query
            })

        return {
            "success": True,
            "provider": "youtube",
            "videos": processed_results,
            "total_found": len(processed_results),
            "query": query
        }

    def _create_fallback_youtube_data(self, query: str, max_results: int) -> Dict[str, Any]:
        """Cria dados de fallback para YouTube"""
        fallback_videos = []
        
        for i in range(min(max_results, 5)):
            fallback_videos.append({
                'video_id': f'fallback_{i+1}',
                'title': f'Análise Completa: {query} - Parte {i+1}',
                'description': f'Vídeo detalhado sobre {query} no mercado brasileiro, com insights e análises estratégicas.',
                'channel_title': f'Canal Análise {i+1}',
                'published_at': '2024-08-01T12:00:00Z',
                'thumbnail_url': 'https://via.placeholder.com/320x180',
                'view_count': str((i+1) * 1000),
                'like_count': str((i+1) * 50),
                'comment_count': str((i+1) * 10),
                'url': f'https://youtube.com/watch?v=example{i+1}',
                'platform': 'youtube',
                'query_used': query,
                'fallback': True
            })

        return {
            "success": True,
            "provider": "youtube_fallback",
            "videos": fallback_videos,
            "total_found": len(fallback_videos),
            "query": query,
            "message": "Usando dados simulados devido à indisponibilidade da API"
        }

# Instância global
youtube_mcp_client = YouTubeMCPClient()
