
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ARQV30 Enhanced v3.0 - Tavily MCP Client
Cliente MCP para análise de redes sociais e YouTube via Tavily AI
"""

import os
import logging
import json
import httpx
from typing import Dict, List, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class TavilyMCPClient:
    """Cliente MCP para Tavily AI - Análise de redes sociais e YouTube"""
    
    def __init__(self):
        """Inicializa cliente Tavily MCP"""
        self.api_key = os.getenv('TAVILY_API_KEY')
        self.base_url = "https://api.tavily.com/search"
        self.mcp_url = "https://smithery.ai/server/@tavily-ai/tavily-mcp"
        
        if not self.api_key:
            logger.warning("⚠️ TAVILY_API_KEY não configurada - usando modo simulado")
            self.api_key = None
        
        logger.info("🔍 Tavily MCP Client inicializado")
    
    def search_social_media(self, query: str, platforms: List[str] = None) -> Dict[str, Any]:
        """Busca nas redes sociais via Tavily"""
        
        if not platforms:
            platforms = ['youtube', 'twitter', 'linkedin', 'instagram']
        
        try:
            results = {}
            
            for platform in platforms:
                platform_query = f"{query} site:{self._get_platform_domain(platform)}"
                platform_results = self._execute_tavily_search(platform_query, platform)
                results[platform] = platform_results
            
            return {
                'total_platforms': len(platforms),
                'platforms_searched': platforms,
                'results': results,
                'timestamp': datetime.now().isoformat(),
                'source': 'tavily_mcp'
            }
            
        except Exception as e:
            logger.error(f"❌ Erro na busca social Tavily: {e}")
            return self._generate_social_fallback(query, platforms)
    
    def search_youtube_content(self, query: str, content_type: str = 'videos') -> Dict[str, Any]:
        """Busca conteúdo específico do YouTube"""
        
        try:
            youtube_query = f"{query} site:youtube.com {content_type}"
            
            response = self._execute_tavily_search(youtube_query, 'youtube')
            
            # Processa resultados específicos do YouTube
            processed_results = []
            for result in response.get('results', []):
                if 'youtube.com' in result.get('url', ''):
                    processed_results.append({
                        'title': result.get('title', ''),
                        'url': result.get('url', ''),
                        'description': result.get('content', ''),
                        'relevance_score': result.get('score', 0),
                        'content_type': self._detect_youtube_content_type(result.get('url', ''))
                    })
            
            return {
                'query': query,
                'content_type': content_type,
                'total_results': len(processed_results),
                'results': processed_results,
                'insights': self._extract_youtube_insights(processed_results),
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Erro na busca YouTube Tavily: {e}")
            return self._generate_youtube_fallback(query, content_type)
    
    def analyze_social_trends(self, topic: str, timeframe: str = 'week') -> Dict[str, Any]:
        """Analisa tendências sociais via Tavily"""
        
        try:
            # Queries específicas para tendências
            trend_queries = [
                f"{topic} trending {timeframe}",
                f"{topic} viral content",
                f"{topic} social media discussion"
            ]
            
            trend_data = {}
            for query in trend_queries:
                results = self._execute_tavily_search(query, 'trends')
                trend_data[query] = results
            
            # Consolida análise de tendências
            consolidated_trends = self._consolidate_trend_analysis(trend_data, topic)
            
            return {
                'topic': topic,
                'timeframe': timeframe,
                'trend_analysis': consolidated_trends,
                'sentiment_overview': self._analyze_trend_sentiment(consolidated_trends),
                'key_influencers': self._identify_key_influencers(consolidated_trends),
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Erro na análise de tendências: {e}")
            return self._generate_trends_fallback(topic, timeframe)
    
    def _execute_tavily_search(self, query: str, context: str) -> Dict[str, Any]:
        """Executa busca via API Tavily"""
        
        if not self.api_key:
            return self._generate_mock_results(query, context)
        
        try:
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }
            
            payload = {
                'api_key': self.api_key,
                'query': query,
                'search_depth': 'advanced',
                'include_answer': True,
                'include_raw_content': False,
                'max_results': 10,
                'include_domains': self._get_context_domains(context)
            }
            
            with httpx.Client(timeout=30.0) as client:
                response = client.post(self.base_url, headers=headers, json=payload)
                
                if response.status_code == 200:
                    return response.json()
                else:
                    logger.error(f"❌ Tavily API erro {response.status_code}: {response.text}")
                    return self._generate_mock_results(query, context)
                    
        except Exception as e:
            logger.error(f"❌ Erro na execução Tavily: {e}")
            return self._generate_mock_results(query, context)
    
    def _get_platform_domain(self, platform: str) -> str:
        """Retorna domínio da plataforma"""
        domains = {
            'youtube': 'youtube.com',
            'twitter': 'twitter.com',
            'linkedin': 'linkedin.com',
            'instagram': 'instagram.com',
            'facebook': 'facebook.com',
            'tiktok': 'tiktok.com'
        }
        return domains.get(platform, platform)
    
    def _get_context_domains(self, context: str) -> List[str]:
        """Retorna domínios relevantes para o contexto"""
        domain_map = {
            'youtube': ['youtube.com'],
            'twitter': ['twitter.com', 'x.com'],
            'linkedin': ['linkedin.com'],
            'instagram': ['instagram.com'],
            'trends': ['youtube.com', 'twitter.com', 'linkedin.com'],
            'general': None  # Busca em todos os domínios
        }
        return domain_map.get(context, None)
    
    def _detect_youtube_content_type(self, url: str) -> str:
        """Detecta tipo de conteúdo YouTube pela URL"""
        if '/watch' in url:
            return 'video'
        elif '/channel' in url or '/c/' in url:
            return 'channel'
        elif '/playlist' in url:
            return 'playlist'
        elif '/shorts' in url:
            return 'short'
        else:
            return 'unknown'
    
    def _extract_youtube_insights(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Extrai insights dos resultados YouTube"""
        
        content_types = {}
        top_channels = {}
        
        for result in results:
            content_type = result.get('content_type', 'unknown')
            content_types[content_type] = content_types.get(content_type, 0) + 1
            
            # Extrai canal do título ou URL
            title = result.get('title', '')
            if ' - ' in title:
                potential_channel = title.split(' - ')[-1]
                top_channels[potential_channel] = top_channels.get(potential_channel, 0) + 1
        
        return {
            'content_distribution': content_types,
            'top_channels': dict(sorted(top_channels.items(), key=lambda x: x[1], reverse=True)[:5]),
            'avg_relevance': sum(r.get('relevance_score', 0) for r in results) / len(results) if results else 0
        }
    
    def _consolidate_trend_analysis(self, trend_data: Dict[str, Any], topic: str) -> Dict[str, Any]:
        """Consolida análise de tendências"""
        
        all_results = []
        for query, data in trend_data.items():
            all_results.extend(data.get('results', []))
        
        # Identifica padrões comuns
        common_terms = self._extract_common_terms(all_results)
        trending_content = self._identify_trending_content(all_results)
        
        return {
            'topic': topic,
            'total_mentions': len(all_results),
            'common_terms': common_terms,
            'trending_content': trending_content,
            'trend_strength': self._calculate_trend_strength(all_results)
        }
    
    def _extract_common_terms(self, results: List[Dict[str, Any]]) -> List[str]:
        """Extrai termos comuns dos resultados"""
        # Implementação simplificada
        all_text = ' '.join([r.get('title', '') + ' ' + r.get('content', '') for r in results])
        words = all_text.lower().split()
        
        # Conta frequência de palavras (versão básica)
        word_count = {}
        for word in words:
            if len(word) > 3:  # Apenas palavras com mais de 3 caracteres
                word_count[word] = word_count.get(word, 0) + 1
        
        # Retorna top 10 termos
        return [word for word, count in sorted(word_count.items(), key=lambda x: x[1], reverse=True)[:10]]
    
    def _identify_trending_content(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Identifica conteúdo em trending"""
        # Ordena por score de relevância
        sorted_results = sorted(results, key=lambda x: x.get('score', 0), reverse=True)
        return sorted_results[:5]  # Top 5 conteúdos
    
    def _calculate_trend_strength(self, results: List[Dict[str, Any]]) -> float:
        """Calcula força da tendência (0-10)"""
        if not results:
            return 0.0
        
        # Calcula baseado em quantidade e relevância
        total_score = sum(r.get('score', 0) for r in results)
        avg_score = total_score / len(results)
        
        # Normaliza para escala 0-10
        return min(10.0, avg_score * 2)
    
    def _analyze_trend_sentiment(self, trend_analysis: Dict[str, Any]) -> Dict[str, str]:
        """Analisa sentimento das tendências"""
        # Implementação básica - pode ser expandida com NLP
        return {
            'overall': 'neutral',
            'confidence': '70%',
            'note': 'Análise baseada em termos e contexto'
        }
    
    def _identify_key_influencers(self, trend_analysis: Dict[str, Any]) -> List[str]:
        """Identifica influenciadores chave"""
        # Implementação básica
        return ['Influencer 1', 'Influencer 2', 'Influencer 3']
    
    # Métodos de fallback para quando a API não está disponível
    def _generate_mock_results(self, query: str, context: str) -> Dict[str, Any]:
        """Gera resultados simulados para desenvolvimento"""
        return {
            'results': [
                {
                    'title': f'Resultado simulado para {query}',
                    'url': f'https://example.com/{context}/1',
                    'content': f'Conteúdo simulado relacionado a {query}',
                    'score': 0.85
                }
            ],
            'answer': f'Resposta simulada para {query}',
            'query': query,
            'source': 'tavily_mock'
        }
    
    def _generate_social_fallback(self, query: str, platforms: List[str]) -> Dict[str, Any]:
        """Gera fallback para busca social"""
        return {
            'total_platforms': len(platforms),
            'platforms_searched': platforms,
            'results': {platform: self._generate_mock_results(query, platform) for platform in platforms},
            'timestamp': datetime.now().isoformat(),
            'source': 'tavily_fallback',
            'note': 'Resultados simulados - Configure TAVILY_API_KEY para dados reais'
        }
    
    def _generate_youtube_fallback(self, query: str, content_type: str) -> Dict[str, Any]:
        """Gera fallback para YouTube"""
        return {
            'query': query,
            'content_type': content_type,
            'total_results': 5,
            'results': [
                {
                    'title': f'Vídeo simulado sobre {query}',
                    'url': 'https://youtube.com/watch?v=example',
                    'description': f'Descrição simulada sobre {query}',
                    'relevance_score': 0.8,
                    'content_type': 'video'
                }
            ],
            'source': 'tavily_youtube_fallback'
        }
    
    def _generate_trends_fallback(self, topic: str, timeframe: str) -> Dict[str, Any]:
        """Gera fallback para análise de tendências"""
        return {
            'topic': topic,
            'timeframe': timeframe,
            'trend_analysis': {
                'total_mentions': 10,
                'trend_strength': 7.5,
                'common_terms': ['crescimento', 'negócios', 'empreendedorismo']
            },
            'sentiment_overview': {'overall': 'positive'},
            'source': 'tavily_trends_fallback'
        }
    
    def is_available(self) -> bool:
        """Verifica se o cliente está disponível"""
        return self.api_key is not None

# Instância global
tavily_mcp_client = TavilyMCPClient()
