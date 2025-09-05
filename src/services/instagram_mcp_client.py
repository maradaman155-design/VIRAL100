#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ARQV30 Enhanced v2.0 - Instagram MCP Client
Cliente para pesquisa no Instagram usando MCP
"""

import os
import logging
import requests
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)

class InstagramMCPClient:
    """Cliente para pesquisa no Instagram usando MCP"""

    def __init__(self):
        """Inicializa o cliente Instagram MCP"""
        self.base_url = os.getenv('INSTAGRAM_MCP_URL', 'https://api.instagram-mcp.ai/v1')
        self.api_key = os.getenv('INSTAGRAM_API_KEY')

        self.headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.api_key}' if self.api_key else '',
            'User-Agent': 'ARQV30-Enhanced/2.0'
        }

        self.is_available = bool(self.api_key)

        if self.is_available:
            logger.info("✅ Instagram MCP Client ATIVO")
        else:
            logger.warning("⚠️ Instagram API não configurada - sem simulação")

    async def search_instagram_content(self, query: str, hashtags: List[str] = None) -> Dict[str, Any]:
        """Busca conteúdo no Instagram"""
        try:
            if not self.is_available:
                return {"success": False, "provider": "instagram", "data": [], "total_found": 0, "query": query, "message": "Instagram API ausente"}

            logger.info(f"📸 Buscando no Instagram: {query}")

            payload = {
                "query": query,
                "hashtags": hashtags or [],
                "count": 20,
                "type": "recent"
            }

            response = requests.post(
                f"{self.base_url}/search",
                json=payload,
                headers=self.headers,
                timeout=30
            )

            if response.status_code == 200:
                data = response.json()
                return self._process_instagram_results(data, query)
            else:
                logger.warning(f"⚠️ Instagram API erro {response.status_code}")
                return {"success": False, "provider": "instagram", "data": [], "total_found": 0, "query": query, "message": f"HTTP {response.status_code}"}

        except Exception as e:
            logger.error(f"❌ Erro Instagram: {e}")
            return {"success": False, "provider": "instagram", "data": [], "total_found": 0, "query": query, "message": str(e)}

    def _process_instagram_results(self, data: Dict[str, Any], query: str) -> Dict[str, Any]:
        """Processa resultados do Instagram"""
        processed_results = []

        for item in data.get('data', []):
            processed_results.append({
                'id': item.get('id', ''),
                'caption': item.get('caption', {}).get('text', ''),
                'media_type': item.get('media_type', ''),
                'like_count': item.get('like_count', 0),
                'comment_count': item.get('comments_count', 0),
                'timestamp': item.get('timestamp', ''),
                'permalink': item.get('permalink', ''),
                'username': item.get('username', ''),
                'hashtags': self._extract_hashtags_from_caption(item.get('caption', {}).get('text', '')),
                'platform': 'instagram',
                'query_used': query
            })

        return {
            "success": True,
            "provider": "instagram",
            "data": processed_results,
            "total_found": len(processed_results),
            "query": query
        }

    def _create_fallback_instagram_data(self, query: str, hashtags: List[str] = None) -> Dict[str, Any]:
        """Mantido por compatibilidade – sem simulação."""
        return {"success": False, "provider": "instagram", "data": [], "total_found": 0, "query": query}

    def _extract_hashtags_from_caption(self, caption: str) -> List[str]:
        """Extrai hashtags do caption"""
        import re
        hashtags = re.findall(r'#\w+', caption)
        return hashtags

# Instância global
instagram_mcp_client = InstagramMCPClient()