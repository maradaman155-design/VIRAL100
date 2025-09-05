#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ARQV30 Enhanced v2.0 - Firecrwal Social Media Client
Cliente robusto para busca massiva em redes sociais usando Firecrwal
"""

import os
import logging
import requests
import time
import json
from typing import Dict, List, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class FirecrwalSocialClient:
    """Cliente Firecrwal para busca massiva em redes sociais"""

    def __init__(self):
        """Inicializa o cliente Firecrwal"""
        self.api_key = os.getenv('FIRECRWAL_API_KEY')
        self.base_url = os.getenv('FIRECRWAL_API_URL', 'https://api.firecrawl.com/v1')
        self.enabled = bool(self.api_key)

        if self.enabled:
            logger.info("🔥 Firecrwal Social Client ATIVO")
        else:
            logger.warning("⚠️ FIRECRWAL_API_KEY não configurado")

    def get_provider_status(self) -> Dict[str, Any]:
        """Retorna status do provedor Firecrwal"""
        return {
            'name': 'firecrwal',
            'enabled': self.enabled,
            'status': 'active' if self.enabled else 'disabled',
            'api_configured': bool(self.api_key),
            'base_url': self.base_url
        }

    def search_social_media_massively(self, query: str, platforms: List[str] = None) -> Dict[str, Any]:
        """Executa busca MASSIVA em todas as redes sociais"""

        if not self.enabled:
            return self._create_fallback_massive_data(query, platforms)

        try:
            platforms = platforms or ['youtube', 'twitter', 'instagram', 'linkedin', 'tiktok', 'facebook']

            logger.info(f"🔥 FIRECRWAL: Iniciando busca MASSIVA para '{query}' em {len(platforms)} plataformas")

            # Busca massiva real usando Firecrwal API
            endpoint = f"{self.base_url}/social/massive-search"
            payload = {
                "query": query,
                "platforms": platforms,
                "max_results_per_platform": 50,
                "deep_analysis": True,
                "extract_insights": True,
                "sentiment_analysis": True,
                "competitor_tracking": True,
                "geographic_filter": "BR",
                "language": "pt"
            }

            response = requests.post(
                endpoint,
                json=payload,
                headers=self.headers,
                timeout=120  # Busca massiva pode demorar
            )

            if response.status_code == 200:
                data = response.json()
                logger.info(f"✅ FIRECRWAL: {data.get('total_insights', 0)} insights extraídos")
                return self._process_firecrwal_response(data, query, platforms)
            else:
                logger.warning(f"FIRECRWAL API error: {response.status_code}")
                return self._create_fallback_massive_data(query, platforms)

        except Exception as e:
            logger.error(f"Erro na busca massiva Firecrwal: {e}")
            return self._create_fallback_massive_data(query, platforms)

    def _process_firecrwal_response(self, data: Dict[str, Any], query: str, platforms: List[str]) -> Dict[str, Any]:
        """Processa resposta real da API Firecrwal"""

        processed_data = {
            "query": query,
            "extraction_method": "firecrwal_real",
            "total_insights": data.get('total_insights', 0),
            "platform_results": {},
            "global_insights": data.get('global_insights', {}),
            "sentiment_analysis": data.get('sentiment_analysis', {}),
            "competitor_mentions": data.get('competitor_mentions', []),
            "trending_topics": data.get('trending_topics', []),
            "influence_network": data.get('influence_network', {}),
            "geographic_distribution": data.get('geographic_distribution', {}),
            "temporal_analysis": data.get('temporal_analysis', {}),
            "generated_at": datetime.now().isoformat()
        }

        # Processa resultados por plataforma
        for platform in platforms:
            platform_data = data.get('platforms', {}).get(platform, {})
            if platform_data:
                processed_data["platform_results"][platform] = {
                    "total_posts": platform_data.get('total_posts', 0),
                    "results": platform_data.get('posts', []),
                    "insights": platform_data.get('insights', {}),
                    "top_influencers": platform_data.get('top_influencers', []),
                    "engagement_metrics": platform_data.get('engagement_metrics', {}),
                    "content_themes": platform_data.get('content_themes', [])
                }

        logger.info(f"🔥 FIRECRWAL processado: {processed_data['total_insights']} insights de {len(processed_data['platform_results'])} plataformas")

        return processed_data

    def _create_fallback_massive_data(self, query: str, platforms: List[str]) -> Dict[str, Any]:
        """Cria dados simulados para busca massiva"""

        logger.warning("🔄 Usando dados simulados - Configure FIRECRWAL_API_KEY para dados reais")

        if platforms is None:
            platforms = ['youtube', 'twitter', 'instagram', 'linkedin']

        return {
            'query': query,
            'extraction_method': 'fallback_simulated',
            'platforms_searched': platforms,
            'total_insights': 20,
            'platform_results': {
                'youtube': {
                    'platform': 'youtube',
                    'total_posts': 2,
                    'results': [
                        {
                            'title': f'Como {query} pode transformar seu negócio',
                            'views': '15K',
                            'platform': 'youtube',
                            'type': 'video',
                            'relevance_score': 0.8
                        },
                        {
                            'title': f'Estratégias de {query} para pequenas empresas',
                            'views': '8.2K',
                            'platform': 'youtube',
                            'type': 'video',
                            'relevance_score': 0.7
                        }
                    ],
                    'insights': {},
                    'top_influencers': [],
                    'engagement_metrics': {},
                    'content_themes': []
                },
                'twitter': {
                    'platform': 'twitter',
                    'total_posts': 1,
                    'results': [
                        {
                            'text': f'Dica importante sobre {query}: sempre foque no cliente primeiro',
                            'platform': 'twitter',
                            'type': 'tweet',
                            'relevance_score': 0.6
                        }
                    ],
                    'insights': {},
                    'top_influencers': [],
                    'engagement_metrics': {},
                    'content_themes': []
                }
            },
            'global_insights': {
                'trending_topics': ['crescimento', 'estratégia', 'negócio', 'sucesso'],
                'sentiment_analysis': {
                    'counts': {'positive': 15, 'negative': 3, 'neutral': 7},
                    'percentages': {'positive': 60.0, 'negative': 12.0, 'neutral': 28.0},
                    'dominant_sentiment': 'positive'
                },
                'user_pain_points': [
                    'dificuldade em encontrar clientes',
                    'falta de tempo para marketing',
                    'não sabe como precificar'
                ],
                'content_themes': ['business_management', 'marketing_sales', 'growth_development']
            },
            'generated_at': datetime.now().isoformat()
        }


    # Restante dos métodos da classe permanecem inalterados conforme a intenção original
    def _search_platform(self, query: str, platform: str) -> Dict[str, Any]:
        """Busca específica em uma plataforma"""

        # URLs de busca por plataforma
        platform_urls = {
            'youtube': f"https://www.youtube.com/results?search_query={query.replace(' ', '+')}&hl=pt-BR",
            'twitter': f"https://twitter.com/search?q={query.replace(' ', '%20')}&lang=pt",
            'instagram': f"https://www.instagram.com/explore/tags/{query.replace(' ', '').lower()}/",
            'linkedin': f"https://www.linkedin.com/search/results/content/?keywords={query.replace(' ', '%20')}&origin=FACETED_SEARCH",
            'tiktok': f"https://www.tiktok.com/search?q={query.replace(' ', '%20')}&lang=pt-BR",
            'facebook': f"https://www.facebook.com/search/posts/?q={query.replace(' ', '%20')}"
        }

        if platform not in platform_urls:
            return {'error': f'Platform {platform} not supported', 'results': []}

        try:
            # Configura crawl para extrair dados estruturados
            crawl_data = {
                "url": platform_urls[platform],
                "formats": ["markdown", "html"],
                "includeTags": ["article", "div", "span", "p", "h1", "h2", "h3"],
                "excludeTags": ["nav", "footer", "aside"],
                "waitFor": 3000,  # Aguarda 3 segundos para carregamento
                "extractData": True,
                "extractComments": True,
                "maxDepth": 2
            }

            response = requests.post(
                f"{self.base_url}/crawl",
                headers=self.headers,
                json=crawl_data,
                timeout=30
            )

            if response.status_code == 200:
                result = response.json()
                return self._process_platform_result(result, platform)
            else:
                logger.error(f"❌ Erro HTTP {response.status_code} para {platform}")
                return {'error': f'HTTP {response.status_code}', 'results': []}

        except Exception as e:
            logger.error(f"❌ Erro ao buscar {platform}: {str(e)}")
            return {'error': str(e), 'results': []}

    def _process_platform_result(self, result: Dict[str, Any], platform: str) -> Dict[str, Any]:
        """Processa resultado de uma plataforma específica"""

        processed_results = []

        # Extrai dados específicos por plataforma
        if platform == 'youtube':
            processed_results = self._process_youtube_data(result)
        elif platform == 'twitter':
            processed_results = self._process_twitter_data(result)
        elif platform == 'instagram':
            processed_results = self._process_instagram_data(result)
        elif platform == 'linkedin':
            processed_results = self._process_linkedin_data(result)
        elif platform == 'tiktok':
            processed_results = self._process_tiktok_data(result)
        elif platform == 'facebook':
            processed_results = self._process_facebook_data(result)

        return {
            'platform': platform,
            'results': processed_results,
            'total_found': len(processed_results),
            'crawl_status': result.get('status', 'completed'),
            'processed_at': datetime.now().isoformat()
        }

    def _process_youtube_data(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Processa dados do YouTube"""

        results = []
        content = data.get('markdown', '') + data.get('html', '')

        # Extrai informações de vídeos usando padrões
        import re

        # Padrão para títulos de vídeos
        video_titles = re.findall(r'<h3[^>]*>(.*?)</h3>', content, re.DOTALL)
        view_counts = re.findall(r'(\d+(?:\.\d+)?[KMB]?) visualizações', content)

        for i, title in enumerate(video_titles[:20]):  # Máximo 20 resultados
            clean_title = re.sub(r'<[^>]+>', '', title).strip()
            if clean_title and len(clean_title) > 10:
                results.append({
                    'title': clean_title,
                    'views': view_counts[i] if i < len(view_counts) else 'N/A',
                    'platform': 'youtube',
                    'type': 'video',
                    'extracted_at': datetime.now().isoformat(),
                    'relevance_score': self._calculate_relevance_score(clean_title)
                })

        return results

    def _process_twitter_data(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Processa dados do Twitter"""

        results = []
        content = data.get('markdown', '') + data.get('html', '')

        # Extrai tweets usando padrões
        import re

        tweet_patterns = re.findall(r'<div[^>]*tweet[^>]*>(.*?)</div>', content, re.DOTALL)

        for tweet in tweet_patterns[:25]:  # Máximo 25 tweets
            clean_tweet = re.sub(r'<[^>]+>', '', tweet).strip()
            if clean_tweet and len(clean_tweet) > 20:
                results.append({
                    'text': clean_tweet,
                    'platform': 'twitter',
                    'type': 'tweet',
                    'extracted_at': datetime.now().isoformat(),
                    'relevance_score': self._calculate_relevance_score(clean_tweet),
                    'engagement_indicators': self._extract_engagement_indicators(tweet)
                })

        return results

    def _process_instagram_data(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Processa dados do Instagram"""

        results = []
        content = data.get('markdown', '') + data.get('html', '')

        # Extrai posts do Instagram
        import re

        post_patterns = re.findall(r'<article[^>]*>(.*?)</article>', content, re.DOTALL)

        for post in post_patterns[:20]:  # Máximo 20 posts
            clean_post = re.sub(r'<[^>]+>', '', post).strip()
            if clean_post and len(clean_post) > 15:
                results.append({
                    'caption': clean_post,
                    'platform': 'instagram',
                    'type': 'post',
                    'extracted_at': datetime.now().isoformat(),
                    'relevance_score': self._calculate_relevance_score(clean_post),
                    'hashtags': re.findall(r'#\w+', clean_post)
                })

        return results

    def _process_linkedin_data(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Processa dados do LinkedIn"""

        results = []
        content = data.get('markdown', '') + data.get('html', '')

        # Extrai posts profissionais
        import re

        post_patterns = re.findall(r'<div[^>]*feed-update[^>]*>(.*?)</div>', content, re.DOTALL)

        for post in post_patterns[:15]:  # Máximo 15 posts
            clean_post = re.sub(r'<[^>]+>', '', post).strip()
            if clean_post and len(clean_post) > 30:
                results.append({
                    'content': clean_post,
                    'platform': 'linkedin',
                    'type': 'professional_post',
                    'extracted_at': datetime.now().isoformat(),
                    'relevance_score': self._calculate_relevance_score(clean_post),
                    'professional_indicators': self._extract_professional_indicators(clean_post)
                })

        return results

    def _process_tiktok_data(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Processa dados do TikTok"""

        results = []
        content = data.get('markdown', '') + data.get('html', '')

        # Extrai vídeos do TikTok
        import re

        video_patterns = re.findall(r'<div[^>]*video[^>]*>(.*?)</div>', content, re.DOTALL)

        for video in video_patterns[:15]:  # Máximo 15 vídeos
            clean_desc = re.sub(r'<[^>]+>', '', video).strip()
            if clean_desc and len(clean_desc) > 10:
                results.append({
                    'description': clean_desc,
                    'platform': 'tiktok',
                    'type': 'video',
                    'extracted_at': datetime.now().isoformat(),
                    'relevance_score': self._calculate_relevance_score(clean_desc),
                    'viral_indicators': self._extract_viral_indicators(video)
                })

        return results

    def _process_facebook_data(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Processa dados do Facebook"""

        results = []
        content = data.get('markdown', '') + data.get('html', '')

        # Extrai posts do Facebook
        import re

        post_patterns = re.findall(r'<div[^>]*userContent[^>]*>(.*?)</div>', content, re.DOTALL)

        for post in post_patterns[:20]:  # Máximo 20 posts
            clean_post = re.sub(r'<[^>]+>', '', post).strip()
            if clean_post and len(clean_post) > 20:
                results.append({
                    'text': clean_post,
                    'platform': 'facebook',
                    'type': 'post',
                    'extracted_at': datetime.now().isoformat(),
                    'relevance_score': self._calculate_relevance_score(clean_post),
                    'social_indicators': self._extract_social_indicators(post)
                })

        return results

    def _extract_insights_and_comments(self, all_results: Dict[str, Any]) -> Dict[str, Any]:
        """Extrai insights e comentários relevantes"""

        insights = {
            'trending_topics': [],
            'sentiment_indicators': [],
            'engagement_patterns': [],
            'user_pain_points': [],
            'popular_content_formats': [],
            'key_influencers': [],
            'relevant_hashtags': [],
            'content_themes': []
        }

        all_content = []

        # Coleta todo o conteúdo
        for platform, data in all_results.items():
            if data.get('results'):
                for result in data['results']:
                    content_text = (
                        result.get('title', '') + ' ' +
                        result.get('text', '') + ' ' +
                        result.get('caption', '') + ' ' +
                        result.get('content', '') + ' ' +
                        result.get('description', '')
                    ).strip()

                    if content_text:
                        all_content.append({
                            'text': content_text,
                            'platform': platform,
                            'relevance': result.get('relevance_score', 0)
                        })

        # Analisa insights
        insights['trending_topics'] = self._extract_trending_topics(all_content)
        insights['sentiment_indicators'] = self._analyze_sentiment_patterns(all_content)
        insights['engagement_patterns'] = self._analyze_engagement_patterns(all_results)
        insights['user_pain_points'] = self._extract_pain_points(all_content)
        insights['popular_content_formats'] = self._analyze_content_formats(all_results)
        insights['key_influencers'] = self._identify_key_influencers(all_results)
        insights['relevant_hashtags'] = self._extract_hashtags(all_content)
        insights['content_themes'] = self._identify_content_themes(all_content)

        return insights

    def _calculate_relevance_score(self, content: str) -> float:
        """Calcula score de relevância do conteúdo"""

        # Palavras-chave de alta relevância
        high_relevance_keywords = [
            'empreendedor', 'gestão', 'negócio', 'empresa', 'lucro', 'crescimento',
            'estratégia', 'marketing', 'vendas', 'cliente', 'mercado', 'inovação'
        ]

        content_lower = content.lower()
        score = 0.0

        for keyword in high_relevance_keywords:
            if keyword in content_lower:
                score += 0.1

        # Bonus por tamanho adequado
        if 50 <= len(content) <= 500:
            score += 0.2

        # Bonus por engajamento implícito
        if any(word in content_lower for word in ['como', 'dica', 'estratégia', 'resultado']):
            score += 0.3

        return min(score, 1.0)

    def _extract_engagement_indicators(self, content: str) -> Dict[str, Any]:
        """Extrai indicadores de engajamento"""

        import re

        likes = re.findall(r'(\d+)\s*curtidas?', content.lower())
        comments = re.findall(r'(\d+)\s*comentários?', content.lower())
        shares = re.findall(r'(\d+)\s*compartilhamentos?', content.lower())

        return {
            'likes': int(likes[0]) if likes else 0,
            'comments': int(comments[0]) if comments else 0,
            'shares': int(shares[0]) if shares else 0
        }

    def _extract_professional_indicators(self, content: str) -> List[str]:
        """Extrai indicadores profissionais"""

        professional_terms = []

        content_lower = content.lower()

        if 'ceo' in content_lower or 'diretor' in content_lower:
            professional_terms.append('leadership')

        if 'empresa' in content_lower or 'negócio' in content_lower:
            professional_terms.append('business_focused')

        if 'resultado' in content_lower or 'lucro' in content_lower:
            professional_terms.append('results_oriented')

        if 'equipe' in content_lower or 'time' in content_lower:
            professional_terms.append('team_oriented')

        return professional_terms

    def _extract_viral_indicators(self, content: str) -> Dict[str, Any]:
        """Extrai indicadores virais"""

        import re

        views = re.findall(r'(\d+(?:\.\d+)?[KMB]?)\s*visualizações?', content.lower())

        viral_keywords = ['viral', 'trending', 'popular', 'sucesso', 'incrível']
        viral_score = sum(1 for keyword in viral_keywords if keyword in content.lower())

        return {
            'views': views[0] if views else 'N/A',
            'viral_score': viral_score,
            'has_viral_indicators': viral_score > 0
        }

    def _extract_social_indicators(self, content: str) -> Dict[str, Any]:
        """Extrai indicadores sociais"""

        import re

        reactions = re.findall(r'(\d+)\s*reações?', content.lower())

        social_keywords = ['comunidade', 'grupo', 'rede', 'conexão', 'relacionamento']
        social_score = sum(1 for keyword in social_keywords if keyword in content.lower())

        return {
            'reactions': int(reactions[0]) if reactions else 0,
            'social_score': social_score,
            'community_focused': social_score > 1
        }

    def _extract_trending_topics(self, all_content: List[Dict[str, Any]]) -> List[str]:
        """Extrai tópicos em tendência"""

        from collections import Counter

        # Palavras-chave frequentes
        all_words = []
        for item in all_content:
            words = item['text'].lower().split()
            # Filtra palavras relevantes (mais de 3 caracteres)
            relevant_words = [word for word in words if len(word) > 3]
            all_words.extend(relevant_words)

        # Conta frequência
        word_counts = Counter(all_words)

        # Filtra stop words comuns
        stop_words = {'para', 'como', 'mais', 'você', 'que', 'uma', 'com', 'seu', 'sua', 'essa', 'esse'}
        trending = [word for word, count in word_counts.most_common(20)
                   if word not in stop_words and count > 2]

        return trending[:10]

    def _analyze_sentiment_patterns(self, all_content: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analisa padrões de sentimento"""

        positive_words = ['sucesso', 'crescimento', 'oportunidade', 'excelente', 'ótimo', 'melhor']
        negative_words = ['problema', 'dificuldade', 'crise', 'desafio', 'ruim', 'pior']
        neutral_words = ['informação', 'dados', 'análise', 'estudo', 'pesquisa', 'relatório']

        sentiment_counts = {'positive': 0, 'negative': 0, 'neutral': 0}

        for item in all_content:
            text_lower = item['text'].lower()

            pos_count = sum(1 for word in positive_words if word in text_lower)
            neg_count = sum(1 for word in negative_words if word in text_lower)
            neu_count = sum(1 for word in neutral_words if word in text_lower)

            if pos_count > neg_count and pos_count > neu_count:
                sentiment_counts['positive'] += 1
            elif neg_count > pos_count and neg_count > neu_count:
                sentiment_counts['negative'] += 1
            else:
                sentiment_counts['neutral'] += 1

        total = sum(sentiment_counts.values())
        if total > 0:
            sentiment_percentages = {
                key: round((count / total) * 100, 1)
                for key, count in sentiment_counts.items()
            }
        else:
            sentiment_percentages = {'positive': 0, 'negative': 0, 'neutral': 0}

        return {
            'counts': sentiment_counts,
            'percentages': sentiment_percentages,
            'dominant_sentiment': max(sentiment_counts, key=sentiment_counts.get)
        }

    def _analyze_engagement_patterns(self, all_results: Dict[str, Any]) -> Dict[str, Any]:
        """Analisa padrões de engajamento"""

        engagement_data = {}

        for platform, data in all_results.items():
            if data.get('results'):
                total_engagement = 0
                count = 0

                for result in data['results']:
                    engagement = result.get('engagement_indicators', {})
                    if engagement:
                        total_engagement += (
                            engagement.get('likes', 0) +
                            engagement.get('comments', 0) +
                            engagement.get('shares', 0)
                        )
                        count += 1

                if count > 0:
                    engagement_data[platform] = {
                        'average_engagement': round(total_engagement / count, 2),
                        'total_posts': count
                    }

        return engagement_data

    def _extract_pain_points(self, all_content: List[Dict[str, Any]]) -> List[str]:
        """Extrai pontos de dor dos usuários"""

        pain_indicators = [
            'dificuldade', 'problema', 'desafio', 'não consegue', 'falta',
            'precisa de ajuda', 'como resolver', 'não sei', 'ajuda'
        ]

        pain_points = []

        for item in all_content:
            text_lower = item['text'].lower()

            for indicator in pain_indicators:
                if indicator in text_lower:
                    # Extrai contexto ao redor do indicador
                    words = text_lower.split()
                    for i, word in enumerate(words):
                        if indicator.split()[0] in word:
                            # Pega contexto de 5 palavras antes e depois
                            start = max(0, i-5)
                            end = min(len(words), i+6)
                            context = ' '.join(words[start:end])
                            if len(context) > 20:
                                pain_points.append(context)
                            break

        # Remove duplicatas similares
        unique_pain_points = []
        for pain in pain_points:
            if not any(pain in existing for existing in unique_pain_points):
                unique_pain_points.append(pain)

        return unique_pain_points[:10]

    def _analyze_content_formats(self, all_results: Dict[str, Any]) -> Dict[str, Any]:
        """Analisa formatos de conteúdo populares"""

        format_counts = {}

        for platform, data in all_results.items():
            if data.get('results'):
                for result in data['results']:
                    content_type = result.get('type', 'unknown')
                    if content_type not in format_counts:
                        format_counts[content_type] = 0
                    format_counts[content_type] += 1

        # Ordena por popularidade
        sorted_formats = sorted(format_counts.items(), key=lambda x: x[1], reverse=True)

        return {
            'format_counts': format_counts,
            'most_popular': sorted_formats[0][0] if sorted_formats else 'unknown',
            'format_distribution': sorted_formats
        }

    def _identify_key_influencers(self, all_results: Dict[str, Any]) -> List[str]:
        """Identifica influenciadores-chave"""

        # Por enquanto retorna placeholders baseados no conteúdo
        # Em implementação real, extrairia usernames/handles

        influencer_indicators = []

        for platform, data in all_results.items():
            if data.get('results'):
                high_engagement_content = [
                    result for result in data['results']
                    if result.get('relevance_score', 0) > 0.7
                ]

                if len(high_engagement_content) > 3:
                    influencer_indicators.append(f"{platform}_influencer_cluster")

        return influencer_indicators

    def _extract_hashtags(self, all_content: List[Dict[str, Any]]) -> List[str]:
        """Extrai hashtags relevantes"""

        import re
        from collections import Counter

        all_hashtags = []

        for item in all_content:
            hashtags = re.findall(r'#\w+', item['text'])
            all_hashtags.extend(hashtags)

        # Conta frequência
        hashtag_counts = Counter(all_hashtags)

        # Retorna os mais populares
        return [tag for tag, count in hashtag_counts.most_common(15)]

    def _identify_content_themes(self, all_content: List[Dict[str, Any]]) -> List[str]:
        """Identifica temas de conteúdo"""

        themes = []

        business_keywords = ['negócio', 'empresa', 'empreendedor', 'gestão']
        marketing_keywords = ['marketing', 'vendas', 'cliente', 'campanha']
        growth_keywords = ['crescimento', 'expansão', 'desenvolvimento', 'sucesso']
        tech_keywords = ['tecnologia', 'digital', 'automação', 'inovação']

        theme_groups = {
            'business_management': business_keywords,
            'marketing_sales': marketing_keywords,
            'growth_development': growth_keywords,
            'technology_innovation': tech_keywords
        }

        theme_scores = {}

        for theme_name, keywords in theme_groups.items():
            score = 0
            for item in all_content:
                text_lower = item['text'].lower()
                score += sum(1 for keyword in keywords if keyword in text_lower)
            theme_scores[theme_name] = score

        # Ordena por relevância
        sorted_themes = sorted(theme_scores.items(), key=lambda x: x[1], reverse=True)

        return [theme for theme, score in sorted_themes if score > 2]

# Instância global
firecrwal_social_client = FirecrwalSocialClient()