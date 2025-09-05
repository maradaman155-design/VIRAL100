#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ARQV30 Enhanced v2.0 - Social Media Extractor
Extrator robusto para redes sociais
"""

import logging
import re
import numpy as np
from typing import Dict, List, Any, Optional
from datetime import datetime
from collections import Counter, defaultdict

logger = logging.getLogger(__name__)

class SocialMediaExtractor:
    """Extrator para análise de redes sociais"""

    def __init__(self):
        """Inicializa o extrator de redes sociais"""
        self.enabled = True
        logger.info("✅ Social Media Extractor inicializado")

    def extract_comprehensive_data(self, query: str, context: Dict[str, Any], session_id: str) -> Dict[str, Any]:
        """Extrai dados abrangentes de redes sociais com foco em engajamento"""
        logger.info(f"🔍 Extraindo dados abrangentes para: {query}")
        
        try:
            # Busca em todas as plataformas com dados de engajamento
            all_platforms_data = self.search_all_platforms_enhanced(query, max_results_per_platform=15)
            
            # Analisa sentimento
            sentiment_analysis = self.analyze_sentiment_trends(all_platforms_data)
            
            # Identifica conteúdo de alto engajamento
            high_engagement_content = self.identify_high_engagement_content(all_platforms_data)
            
            # Extrai insights de hashtags e tendências
            hashtag_insights = self.extract_hashtag_insights(all_platforms_data)
            
            # Analisa padrões de timing
            timing_patterns = self.analyze_posting_patterns(all_platforms_data)
            
            return {
                "success": True,
                "query": query,
                "session_id": session_id,
                "all_platforms_data": all_platforms_data,
                "sentiment_analysis": sentiment_analysis,
                "high_engagement_content": high_engagement_content,
                "hashtag_insights": hashtag_insights,
                "timing_patterns": timing_patterns,
                "total_posts": all_platforms_data.get("total_results", 0),
                "platforms_analyzed": len(all_platforms_data.get("platforms", [])),
                "extracted_at": datetime.now().isoformat(),
                "engagement_metrics": {
                    "avg_likes": high_engagement_content.get("avg_likes", 0),
                    "avg_comments": high_engagement_content.get("avg_comments", 0),
                    "avg_shares": high_engagement_content.get("avg_shares", 0),
                    "top_performing_threshold": high_engagement_content.get("threshold", 0)
                }
            }
            
        except Exception as e:
            logger.error(f"❌ Erro na extração abrangente: {e}")
            return {
                "success": False,
                "error": str(e),
                "query": query,
                "session_id": session_id
            }

    def search_all_platforms(self, query: str, max_results_per_platform: int = 10) -> Dict[str, Any]:
        """Busca em todas as plataformas de redes sociais"""

        logger.info(f"🔍 Iniciando busca em redes sociais para: {query}")

        results = {
            "query": query,
            "platforms": ["youtube", "twitter", "instagram", "linkedin"],
            "total_results": 0,
            # Em modo real/data-only, não geramos simulações.
            # Mantemos as chaves vazias para compatibilidade com consumidores.
            "youtube": {"success": False, "results": []},
            "twitter": {"success": False, "results": []},
            "instagram": {"success": False, "results": []},
            "linkedin": {"success": False, "results": []},
            "search_quality": "none",
            "generated_at": datetime.now().isoformat()
        }

        # Conta total de resultados
        for platform in results["platforms"]:
            platform_data = results.get(platform, {})
            if platform_data.get("results"):
                results["total_results"] += len(platform_data["results"])

        results["success"] = results["total_results"] > 0

        logger.info(f"✅ Busca concluída: {results['total_results']} posts encontrados")

        return results

    def _simulate_youtube_data(self, query: str, max_results: int) -> Dict[str, Any]:
        """Simula dados do YouTube"""

        results = []
        for i in range(min(max_results, 8)):
            results.append({
                'title': f'Vídeo sobre {query} - Tutorial Completo {i+1}',
                'description': f'Aprenda tudo sobre {query} neste vídeo completo e prático',
                'channel': f'Canal Expert {i+1}',
                'published_at': '2024-08-01T00:00:00Z',
                'view_count': str((i+1) * 1500),
                'like_count': (i+1) * 120,
                'comment_count': (i+1) * 45,
                'url': f'https://youtube.com/watch?v=example{i+1}',
                'platform': 'youtube',
                'engagement_rate': round(((i+1) * 120) / ((i+1) * 1500) * 100, 2),
                'sentiment': 'positive' if i % 3 == 0 else 'neutral',
                'relevance_score': round(0.8 + (i * 0.02), 2)
            })

        return {
            "success": True,
            "platform": "youtube",
            "results": results,
            "total_found": len(results),
            "query": query
        }

    def _simulate_twitter_data(self, query: str, max_results: int) -> Dict[str, Any]:
        """Simula dados do Twitter"""

        results = []
        sentiments = ['positive', 'negative', 'neutral']

        for i in range(min(max_results, 12)):
            results.append({
                'text': f'Interessante discussão sobre {query}! Vejo muito potencial no mercado brasileiro. #{query} #negócios #empreendedorismo',
                'author': f'@especialista{i+1}',
                'created_at': '2024-08-01T00:00:00Z',
                'retweet_count': (i+1) * 15,
                'like_count': (i+1) * 35,
                'reply_count': (i+1) * 8,
                'quote_count': (i+1) * 5,
                'url': f'https://twitter.com/i/status/example{i+1}',
                'platform': 'twitter',
                'sentiment': sentiments[i % 3],
                'influence_score': round(0.6 + (i * 0.03), 2),
                'hashtags': [f'#{query}', '#negócios', '#brasil']
            })

        return {
            "success": True,
            "platform": "twitter",
            "results": results,
            "total_found": len(results),
            "query": query
        }

    def _simulate_instagram_data(self, query: str, max_results: int) -> Dict[str, Any]:
        """Simula dados do Instagram"""

        results = []
        for i in range(min(max_results, 10)):
            results.append({
                'caption': f'Transformando o mercado de {query}! 🚀 Veja como esta inovação está mudando tudo! #{query} #inovação #brasil',
                'media_type': 'IMAGE',
                'like_count': (i+1) * 250,
                'comment_count': (i+1) * 18,
                'timestamp': '2024-08-01T00:00:00Z',
                'url': f'https://instagram.com/p/example{i+1}',
                'username': f'influencer{i+1}',
                'platform': 'instagram',
                'engagement_rate': round(((i+1) * 268) / ((i+1) * 5000) * 100, 2),
                'hashtags': [f'#{query}', '#inovação', '#brasil', '#negócios'],
                'follower_count': (i+1) * 5000
            })

        return {
            "success": True,
            "platform": "instagram",
            "results": results,
            "total_found": len(results),
            "query": query
        }

    def _simulate_linkedin_data(self, query: str, max_results: int) -> Dict[str, Any]:
        """Simula dados do LinkedIn"""

        results = []
        for i in range(min(max_results, 8)):
            results.append({
                'title': f'O Futuro do {query}: Tendências e Oportunidades',
                'content': f'Análise profissional sobre o crescimento exponencial no setor de {query}. Dados mostram aumento de 200% na demanda.',
                'author': f'Dr. Especialista {i+1}',
                'company': f'Consultoria Innovation {i+1}',
                'published_date': '2024-08-01',
                'likes': (i+1) * 85,
                'comments': (i+1) * 25,
                'shares': (i+1) * 12,
                'url': f'https://linkedin.com/posts/example{i+1}',
                'platform': 'linkedin',
                'author_title': f'CEO & Founder - Expert em {query}',
                'company_size': f'{(i+1) * 500}-{(i+1) * 1000} funcionários',
                'engagement_quality': 'high' if i % 2 == 0 else 'medium'
            })

        return {
            "success": True,
            "platform": "linkedin",
            "results": results,
            "total_found": len(results),
            "query": query
        }

    def analyze_sentiment_trends(self, platforms_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analisa tendências de sentimento across platforms"""

        total_positive = 0
        total_negative = 0
        total_neutral = 0
        total_posts = 0

        platform_sentiments = {}

        for platform_name, platform_data in platforms_data.items():
            if platform_name in ['youtube', 'twitter', 'instagram', 'linkedin']:
                results = platform_data.get('results', [])

                platform_positive = 0
                platform_negative = 0
                platform_neutral = 0

                for post in results:
                    sentiment = post.get('sentiment', 'neutral')
                    if sentiment == 'positive':
                        platform_positive += 1
                        total_positive += 1
                    elif sentiment == 'negative':
                        platform_negative += 1
                        total_negative += 1
                    else:
                        platform_neutral += 1
                        total_neutral += 1

                total_posts += len(results)

                if len(results) > 0:
                    platform_sentiments[platform_name] = {
                        'positive_percentage': round((platform_positive / len(results)) * 100, 1),
                        'negative_percentage': round((platform_negative / len(results)) * 100, 1),
                        'neutral_percentage': round((platform_neutral / len(results)) * 100, 1),
                        'total_posts': len(results),
                        'dominant_sentiment': 'positive' if platform_positive > platform_negative and platform_positive > platform_neutral else 'negative' if platform_negative > platform_positive else 'neutral'
                    }

        overall_sentiment = 'neutral'
        if total_positive > total_negative and total_positive > total_neutral:
            overall_sentiment = 'positive'
        elif total_negative > total_positive and total_negative > total_neutral:
            overall_sentiment = 'negative'

        return {
            'overall_sentiment': overall_sentiment,
            'overall_positive_percentage': round((total_positive / total_posts) * 100, 1) if total_posts > 0 else 0,
            'overall_negative_percentage': round((total_negative / total_posts) * 100, 1) if total_posts > 0 else 0,
            'overall_neutral_percentage': round((total_neutral / total_posts) * 100, 1) if total_posts > 0 else 0,
            'total_posts_analyzed': total_posts,
            'platform_breakdown': platform_sentiments,
            'confidence_score': round(abs(total_positive - total_negative) / total_posts * 100, 1) if total_posts > 0 else 0,
            'analysis_timestamp': datetime.now().isoformat()
        }

    def search_all_platforms_enhanced(self, query: str, max_results_per_platform: int = 15) -> Dict[str, Any]:
        """Busca aprimorada em todas as plataformas com dados de engajamento"""
        logger.info(f"🔍 Busca aprimorada em plataformas para: {query}")
        
        # Usa o método existente como base e aprimora os dados
        base_data = self.search_all_platforms(query, max_results_per_platform)
        
        # Adiciona métricas de engajamento específicas
        enhanced_data = base_data.copy()
        
        if "platforms" in enhanced_data:
            for platform_name, platform_data in enhanced_data["platforms"].items():
                if "results" in platform_data:
                    for result in platform_data["results"]:
                        # Adiciona métricas de engajamento calculadas
                        result["engagement_score"] = self._calculate_engagement_score(result)
                        result["viral_potential"] = self._calculate_viral_potential(result)
                        result["content_quality"] = self._assess_content_quality(result)
        
        return enhanced_data

    def identify_high_engagement_content(self, platforms_data: Dict[str, Any]) -> Dict[str, Any]:
        """Identifica conteúdo de alto engajamento (top 10% por plataforma)"""
        logger.info("📊 Identificando conteúdo de alto engajamento...")
        
        high_engagement = {
            "instagram": [],
            "youtube": [],
            "twitter": [],
            "linkedin": [],
            "avg_likes": 0,
            "avg_comments": 0,
            "avg_shares": 0,
            "threshold": 0
        }
        
        all_engagement_scores = []
        
        if "platforms" in platforms_data:
            for platform_name, platform_data in platforms_data["platforms"].items():
                if "results" in platform_data:
                    results = platform_data["results"]
                    
                    # Calcula scores de engajamento
                    engagement_scores = []
                    for result in results:
                        score = result.get("engagement_score", 0)
                        engagement_scores.append((result, score))
                        all_engagement_scores.append(score)
                    
                    # Ordena por engajamento
                    engagement_scores.sort(key=lambda x: x[1], reverse=True)
                    
                    # Pega top 10%
                    top_count = max(1, len(engagement_scores) // 10)
                    top_content = [item[0] for item in engagement_scores[:top_count]]
                    
                    high_engagement[platform_name] = top_content
        
        # Calcula métricas médias
        if all_engagement_scores:
            high_engagement["threshold"] = np.percentile(all_engagement_scores, 90) if len(all_engagement_scores) > 0 else 0
            
            # Calcula médias de likes, comentários, shares
            all_likes = []
            all_comments = []
            all_shares = []
            
            for platform_content in high_engagement.values():
                if isinstance(platform_content, list):
                    for content in platform_content:
                        if isinstance(content, dict):
                            all_likes.append(content.get("like_count", 0))
                            all_comments.append(content.get("comment_count", 0))
                            all_shares.append(content.get("shares", content.get("retweet_count", 0)))
            
            high_engagement["avg_likes"] = np.mean(all_likes) if all_likes else 0
            high_engagement["avg_comments"] = np.mean(all_comments) if all_comments else 0
            high_engagement["avg_shares"] = np.mean(all_shares) if all_shares else 0
        
        return high_engagement

    def extract_hashtag_insights(self, platforms_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extrai insights de hashtags e tendências"""
        logger.info("🏷️ Extraindo insights de hashtags...")
        
        hashtag_insights = {
            "trending_hashtags": [],
            "hashtag_performance": {},
            "recommended_hashtags": [],
            "hashtag_networks": {}
        }
        
        all_hashtags = []
        hashtag_engagement = defaultdict(list)
        
        if "platforms" in platforms_data:
            for platform_name, platform_data in platforms_data["platforms"].items():
                if "results" in platform_data:
                    for result in platform_data["results"]:
                        # Extrai hashtags do conteúdo
                        hashtags = result.get("hashtags", [])
                        if not hashtags:
                            # Tenta extrair do texto/caption
                            text = result.get("text", result.get("caption", ""))
                            hashtags = re.findall(r'#\w+', text)
                        
                        engagement_score = result.get("engagement_score", 0)
                        
                        for hashtag in hashtags:
                            all_hashtags.append(hashtag.lower())
                            hashtag_engagement[hashtag.lower()].append(engagement_score)
        
        # Analisa performance das hashtags
        if all_hashtags:
            hashtag_counter = Counter(all_hashtags)
            hashtag_insights["trending_hashtags"] = hashtag_counter.most_common(20)
            
            # Calcula performance média por hashtag
            for hashtag, scores in hashtag_engagement.items():
                if scores:
                    hashtag_insights["hashtag_performance"][hashtag] = {
                        "avg_engagement": np.mean(scores),
                        "usage_count": len(scores),
                        "max_engagement": max(scores),
                        "consistency": np.std(scores) if len(scores) > 1 else 0
                    }
            
            # Recomenda hashtags baseado em performance
            sorted_hashtags = sorted(
                hashtag_insights["hashtag_performance"].items(),
                key=lambda x: x[1]["avg_engagement"],
                reverse=True
            )
            hashtag_insights["recommended_hashtags"] = [
                {"hashtag": hashtag, "score": data["avg_engagement"]}
                for hashtag, data in sorted_hashtags[:10]
            ]
        
        return hashtag_insights

    def analyze_posting_patterns(self, platforms_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analisa padrões de timing de postagens"""
        logger.info("⏰ Analisando padrões de timing...")
        
        timing_patterns = {
            "best_posting_times": {},
            "day_of_week_analysis": {},
            "hourly_distribution": {},
            "seasonal_trends": {}
        }
        
        timestamps = []
        
        if "platforms" in platforms_data:
            for platform_name, platform_data in platforms_data["platforms"].items():
                if "results" in platform_data:
                    for result in platform_data["results"]:
                        timestamp_str = result.get("timestamp", result.get("created_at", result.get("published_at", "")))
                        if timestamp_str:
                            try:
                                # Tenta parsear diferentes formatos de timestamp
                                if "T" in timestamp_str:
                                    timestamp = datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
                                else:
                                    timestamp = datetime.strptime(timestamp_str, "%Y-%m-%d")
                                
                                timestamps.append({
                                    "datetime": timestamp,
                                    "platform": platform_name,
                                    "engagement": result.get("engagement_score", 0)
                                })
                            except Exception as e:
                                logger.debug(f"Erro ao parsear timestamp {timestamp_str}: {e}")
        
        # Analisa padrões se há dados suficientes
        if timestamps:
            # Análise por hora do dia
            hourly_engagement = defaultdict(list)
            daily_engagement = defaultdict(list)
            
            for item in timestamps:
                hour = item["datetime"].hour
                day = item["datetime"].strftime("%A")
                engagement = item["engagement"]
                
                hourly_engagement[hour].append(engagement)
                daily_engagement[day].append(engagement)
            
            # Melhores horários
            timing_patterns["hourly_distribution"] = {
                hour: {
                    "avg_engagement": np.mean(scores),
                    "post_count": len(scores)
                }
                for hour, scores in hourly_engagement.items()
            }
            
            # Melhores dias da semana
            timing_patterns["day_of_week_analysis"] = {
                day: {
                    "avg_engagement": np.mean(scores),
                    "post_count": len(scores)
                }
                for day, scores in daily_engagement.items()
            }
            
            # Identifica melhores horários
            best_hours = sorted(
                timing_patterns["hourly_distribution"].items(),
                key=lambda x: x[1]["avg_engagement"],
                reverse=True
            )[:3]
            
            timing_patterns["best_posting_times"] = [
                {"hour": hour, "engagement": data["avg_engagement"]}
                for hour, data in best_hours
            ]
        
        return timing_patterns

    def _calculate_engagement_score(self, result: Dict[str, Any]) -> float:
        """Calcula score de engajamento para um post"""
        try:
            likes = result.get("like_count", 0)
            comments = result.get("comment_count", 0)
            shares = result.get("shares", result.get("retweet_count", 0))
            views = result.get("view_count", result.get("follower_count", 1000))
            
            # Converte strings para números se necessário
            if isinstance(likes, str):
                likes = int(likes.replace(",", "").replace(".", ""))
            if isinstance(comments, str):
                comments = int(comments.replace(",", "").replace(".", ""))
            if isinstance(shares, str):
                shares = int(shares.replace(",", "").replace(".", ""))
            if isinstance(views, str):
                views = int(views.replace(",", "").replace(".", ""))
            
            # Fórmula de engajamento ponderada
            engagement_score = (likes * 1.0 + comments * 2.0 + shares * 3.0) / max(views, 1) * 100
            
            return min(engagement_score, 100.0)  # Limita a 100
            
        except Exception as e:
            logger.debug(f"Erro ao calcular engagement score: {e}")
            return 0.0

    def _calculate_viral_potential(self, result: Dict[str, Any]) -> float:
        """Calcula potencial viral de um conteúdo"""
        try:
            engagement_score = result.get("engagement_score", 0)
            shares = result.get("shares", result.get("retweet_count", 0))
            comments = result.get("comment_count", 0)
            
            # Fatores que indicam potencial viral
            viral_indicators = 0
            
            # Alto número de shares
            if shares > 50:
                viral_indicators += 30
            elif shares > 20:
                viral_indicators += 20
            elif shares > 5:
                viral_indicators += 10
            
            # Alto engajamento
            if engagement_score > 5.0:
                viral_indicators += 25
            elif engagement_score > 2.0:
                viral_indicators += 15
            
            # Muitos comentários (indica discussão)
            if comments > 100:
                viral_indicators += 25
            elif comments > 50:
                viral_indicators += 15
            elif comments > 20:
                viral_indicators += 10
            
            # Presença de hashtags trending
            text = result.get("text", result.get("caption", ""))
            trending_keywords = ["viral", "trending", "breaking", "urgente", "exclusivo"]
            if any(keyword in text.lower() for keyword in trending_keywords):
                viral_indicators += 20
            
            return min(viral_indicators, 100.0)
            
        except Exception as e:
            logger.debug(f"Erro ao calcular potencial viral: {e}")
            return 0.0

    def _assess_content_quality(self, result: Dict[str, Any]) -> float:
        """Avalia qualidade do conteúdo"""
        try:
            quality_score = 0
            
            # Análise do texto/caption
            text = result.get("text", result.get("caption", result.get("title", "")))
            
            if text:
                # Comprimento adequado
                if 50 <= len(text) <= 500:
                    quality_score += 25
                elif len(text) > 500:
                    quality_score += 20
                elif len(text) > 20:
                    quality_score += 15
                
                # Presença de call-to-action
                cta_keywords = ["clique", "acesse", "saiba mais", "confira", "veja", "descubra"]
                if any(keyword in text.lower() for keyword in cta_keywords):
                    quality_score += 20
                
                # Uso de emojis (moderado)
                emoji_count = len(re.findall(r'[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF\U0001F1E0-\U0001F1FF]', text))
                if 1 <= emoji_count <= 5:
                    quality_score += 15
                elif emoji_count > 5:
                    quality_score += 5
                
                # Presença de hashtags relevantes
                hashtags = re.findall(r'#\w+', text)
                if 1 <= len(hashtags) <= 10:
                    quality_score += 20
                elif len(hashtags) > 10:
                    quality_score += 10
                
                # Ausência de spam
                spam_indicators = ["compre agora", "oferta limitada", "clique aqui", "ganhe dinheiro"]
                if not any(spam in text.lower() for spam in spam_indicators):
                    quality_score += 20
            
            return min(quality_score, 100.0)
            
        except Exception as e:
            logger.debug(f"Erro ao avaliar qualidade do conteúdo: {e}")
            return 0.0

# Instância global
social_media_extractor = SocialMediaExtractor()

# Função para compatibilidade
def get_social_media_extractor():
    """Retorna a instância global do social media extractor"""
    return social_media_extractor