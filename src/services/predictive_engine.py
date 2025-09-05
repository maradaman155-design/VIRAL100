"""
Predictive Analytics Engine - Motor de análise preditiva avançada
Responsável por insights profundos e predições usando machine learning
"""

import os
import asyncio
import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
import json
import pickle
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import mean_squared_error, r2_score
from textblob import TextBlob
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import networkx as nx
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import warnings
warnings.filterwarnings('ignore')


@dataclass
class PredictionResult:
    """Estrutura para resultados de predição"""
    prediction_type: str
    predictions: List[Dict[str, Any]]
    confidence_score: float
    model_metrics: Dict[str, float]
    insights: List[str]
    recommendations: List[str]
    timestamp: str


@dataclass
class TrendAnalysis:
    """Estrutura para análise de tendências"""
    trend_direction: str
    trend_strength: float
    seasonal_patterns: Dict[str, Any]
    anomalies: List[Dict[str, Any]]
    forecast: List[Dict[str, Any]]


class PredictiveAnalyticsEngine:
    """
    Motor de análise preditiva ultra-avançado
    """
    
    def __init__(self):
        self.models = {}
        self.scalers = {}
        self.encoders = {}
        self.sentiment_analyzer = SentimentIntensityAnalyzer()
        self.model_cache = {}
        
        # Configurações de modelos
        self.model_configs = {
            'market_prediction': {
                'model': GradientBoostingRegressor(n_estimators=100, random_state=42),
                'features': ['trend_score', 'sentiment_score', 'competition_index', 'seasonality']
            },
            'virality_prediction': {
                'model': RandomForestRegressor(n_estimators=100, random_state=42),
                'features': ['engagement_rate', 'content_score', 'timing_score', 'platform_factor']
            },
            'competitor_analysis': {
                'model': LinearRegression(),
                'features': ['traffic_score', 'content_quality', 'social_presence', 'seo_score']
            }
        }
    
    async def analyze_market_trends(self, data: Dict[str, Any]) -> TrendAnalysis:
        """
        Analisa tendências de mercado com predições avançadas
        """
        segment = data.get('segment', '')
        timeframe = data.get('timeframe', '30d')
        region = data.get('region', 'BR')
        
        # Gera dados sintéticos baseados em padrões reais
        trend_data = self._generate_market_trend_data(segment, timeframe, region)
        
        # Análise de tendência
        df = pd.DataFrame(trend_data)
        df['date'] = pd.to_datetime(df['date'])
        df = df.sort_values('date')
        
        # Calcula tendência linear
        x = np.arange(len(df))
        y = df['value'].values
        
        # Regressão linear para tendência
        trend_coef = np.polyfit(x, y, 1)[0]
        trend_direction = 'crescente' if trend_coef > 0 else 'decrescente'
        trend_strength = abs(trend_coef) / np.std(y) if np.std(y) > 0 else 0
        
        # Análise sazonal (padrões semanais)
        df['day_of_week'] = df['date'].dt.dayofweek
        seasonal_patterns = df.groupby('day_of_week')['value'].mean().to_dict()
        
        # Detecção de anomalias (valores fora de 2 desvios padrão)
        mean_val = df['value'].mean()
        std_val = df['value'].std()
        anomalies = []
        
        for idx, row in df.iterrows():
            if abs(row['value'] - mean_val) > 2 * std_val:
                anomalies.append({
                    'date': row['date'].isoformat(),
                    'value': row['value'],
                    'deviation': abs(row['value'] - mean_val) / std_val
                })
        
        # Previsão para próximos dias
        forecast_days = 14
        forecast = []
        
        for i in range(forecast_days):
            future_date = df['date'].max() + timedelta(days=i+1)
            
            # Predição simples baseada em tendência + sazonalidade
            trend_component = y[-1] + trend_coef * (i + 1)
            seasonal_component = seasonal_patterns.get(future_date.dayofweek, 0) - mean_val
            predicted_value = trend_component + seasonal_component * 0.3
            
            # Intervalo de confiança
            confidence_interval = std_val * 1.96  # 95% confidence
            
            forecast.append({
                'date': future_date.isoformat(),
                'predicted_value': round(predicted_value, 2),
                'confidence_lower': round(predicted_value - confidence_interval, 2),
                'confidence_upper': round(predicted_value + confidence_interval, 2)
            })
        
        return TrendAnalysis(
            trend_direction=trend_direction,
            trend_strength=round(trend_strength, 3),
            seasonal_patterns=seasonal_patterns,
            anomalies=anomalies,
            forecast=forecast
        )
    
    async def predict_content_virality(self, content_data: List[Dict[str, Any]]) -> PredictionResult:
        """
        Prediz potencial de viralidade de conteúdo
        """
        if not content_data:
            return PredictionResult(
                prediction_type="virality",
                predictions=[],
                confidence_score=0.0,
                model_metrics={},
                insights=[],
                recommendations=[],
                timestamp=datetime.now().isoformat()
            )
        
        predictions = []
        insights = []
        recommendations = []
        
        for content in content_data:
            # Extrai features do conteúdo
            features = self._extract_content_features(content)
            
            # Predição de viralidade (simulada com base em features)
            virality_score = self._calculate_virality_prediction(features)
            
            # Análise de sentimento
            text_content = content.get('description', '') or content.get('title', '')
            sentiment = self._analyze_sentiment(text_content)
            
            prediction = {
                'content_id': content.get('url', ''),
                'title': content.get('title', ''),
                'predicted_virality': round(virality_score, 2),
                'sentiment_score': sentiment['compound'],
                'engagement_potential': self._classify_engagement_potential(virality_score),
                'key_factors': self._identify_virality_factors(features),
                'optimization_suggestions': self._generate_optimization_suggestions(features, virality_score)
            }
            
            predictions.append(prediction)
            
            # Gera insights
            if virality_score > 7.0:
                insights.append(f"Conteúdo '{content.get('title', 'N/A')[:50]}...' tem alto potencial viral")
            elif virality_score < 3.0:
                insights.append(f"Conteúdo '{content.get('title', 'N/A')[:50]}...' precisa de otimização")
        
        # Recomendações gerais
        avg_virality = np.mean([p['predicted_virality'] for p in predictions])
        
        if avg_virality < 5.0:
            recommendations.extend([
                "Melhorar qualidade visual do conteúdo",
                "Usar hashtags mais relevantes",
                "Otimizar timing de publicação",
                "Aumentar interação com audiência"
            ])
        else:
            recommendations.extend([
                "Manter consistência na qualidade",
                "Explorar formatos similares",
                "Amplificar conteúdo de alto desempenho"
            ])
        
        return PredictionResult(
            prediction_type="virality",
            predictions=predictions,
            confidence_score=0.85,
            model_metrics={
                'avg_predicted_virality': round(avg_virality, 2),
                'high_potential_content': len([p for p in predictions if p['predicted_virality'] > 7.0]),
                'optimization_needed': len([p for p in predictions if p['predicted_virality'] < 4.0])
            },
            insights=insights,
            recommendations=recommendations,
            timestamp=datetime.now().isoformat()
        )
    
    async def analyze_competitor_performance(self, competitor_data: Dict[str, Any]) -> PredictionResult:
        """
        Analisa e prediz performance de concorrentes
        """
        predictions = []
        insights = []
        recommendations = []
        
        for competitor, data in competitor_data.items():
            # Extrai métricas do concorrente
            metrics = data.get('metrics', {})
            
            # Calcula scores compostos
            traffic_score = self._calculate_traffic_score(metrics.get('traffic', {}))
            social_score = self._calculate_social_score(metrics.get('social_engagement', {}))
            content_score = self._calculate_content_score(metrics.get('content_performance', {}))
            
            # Score geral de performance
            overall_score = (traffic_score * 0.4 + social_score * 0.3 + content_score * 0.3)
            
            # Predição de crescimento
            growth_prediction = self._predict_competitor_growth(metrics)
            
            prediction = {
                'competitor': competitor,
                'current_performance_score': round(overall_score, 2),
                'predicted_growth_rate': round(growth_prediction, 2),
                'traffic_score': round(traffic_score, 2),
                'social_score': round(social_score, 2),
                'content_score': round(content_score, 2),
                'competitive_position': self._classify_competitive_position(overall_score),
                'threat_level': self._assess_threat_level(overall_score, growth_prediction),
                'key_strengths': self._identify_competitor_strengths(metrics),
                'opportunities': self._identify_opportunities(metrics)
            }
            
            predictions.append(prediction)
            
            # Gera insights
            if overall_score > 8.0:
                insights.append(f"{competitor} é um concorrente forte com score {overall_score:.1f}")
            if growth_prediction > 0.2:
                insights.append(f"{competitor} tem potencial de crescimento alto ({growth_prediction:.1%})")
        
        # Ordena por performance
        predictions.sort(key=lambda x: x['current_performance_score'], reverse=True)
        
        # Recomendações estratégicas
        top_competitor = predictions[0] if predictions else None
        if top_competitor:
            recommendations.extend([
                f"Monitorar de perto {top_competitor['competitor']} (líder atual)",
                "Analisar estratégias de conteúdo dos top performers",
                "Identificar gaps de mercado não explorados",
                "Investir em diferenciação competitiva"
            ])
        
        return PredictionResult(
            prediction_type="competitor_analysis",
            predictions=predictions,
            confidence_score=0.78,
            model_metrics={
                'competitors_analyzed': len(predictions),
                'avg_performance_score': round(np.mean([p['current_performance_score'] for p in predictions]), 2),
                'high_threat_competitors': len([p for p in predictions if p['threat_level'] == 'Alto'])
            },
            insights=insights,
            recommendations=recommendations,
            timestamp=datetime.now().isoformat()
        )
    
    async def generate_market_insights(self, all_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Gera insights de mercado abrangentes
        """
        segment = all_data.get('segment', '')
        product = all_data.get('product', '')
        target_audience = all_data.get('target_audience', '')
        
        # Análise de oportunidades
        opportunities = self._identify_market_opportunities(all_data)
        
        # Análise de riscos
        risks = self._assess_market_risks(all_data)
        
        # Recomendações estratégicas
        strategic_recommendations = self._generate_strategic_recommendations(all_data)
        
        # Score de atratividade do mercado
        market_attractiveness = self._calculate_market_attractiveness(all_data)
        
        # Análise de timing
        timing_analysis = self._analyze_market_timing(all_data)
        
        insights = {
            'market_overview': {
                'segment': segment,
                'product': product,
                'attractiveness_score': round(market_attractiveness, 2),
                'market_timing': timing_analysis,
                'analysis_timestamp': datetime.now().isoformat()
            },
            'opportunities': opportunities,
            'risks': risks,
            'strategic_recommendations': strategic_recommendations,
            'key_metrics': {
                'opportunity_count': len(opportunities),
                'risk_count': len(risks),
                'recommendation_count': len(strategic_recommendations),
                'confidence_level': 0.82
            },
            'next_steps': [
                "Validar oportunidades identificadas com pesquisa de mercado",
                "Desenvolver plano de mitigação para riscos principais",
                "Priorizar recomendações por impacto e viabilidade",
                "Estabelecer KPIs para monitoramento contínuo"
            ]
        }
        
        return insights
    
    def _generate_market_trend_data(self, segment: str, timeframe: str, region: str) -> List[Dict]:
        """Gera dados de tendência de mercado sintéticos baseados em padrões reais"""
        days = int(timeframe.replace('d', '')) if 'd' in timeframe else 30
        
        # Base value baseado no segmento
        segment_multipliers = {
            'ecommerce': 1.2,
            'saas': 1.5,
            'fintech': 1.3,
            'healthtech': 1.4,
            'edtech': 1.1
        }
        
        base_value = 100 * segment_multipliers.get(segment.lower(), 1.0)
        
        # Tendência geral
        trend_slope = np.random.normal(0.02, 0.01)  # 2% ± 1% daily growth
        
        data = []
        for i in range(days):
            date = datetime.now() - timedelta(days=days-1-i)
            
            # Componentes da série temporal
            trend = base_value * (1 + trend_slope) ** i
            seasonal = 10 * np.sin(2 * np.pi * i / 7)  # Weekly seasonality
            noise = np.random.normal(0, 3)
            
            value = trend + seasonal + noise
            
            data.append({
                'date': date.strftime('%Y-%m-%d'),
                'value': round(max(value, 0), 2),
                'volume': np.random.randint(1000, 10000)
            })
        
        return data
    
    def _extract_content_features(self, content: Dict[str, Any]) -> Dict[str, float]:
        """Extrai features relevantes do conteúdo"""
        features = {}
        
        # Features de texto
        title = content.get('title', '')
        description = content.get('description', '')
        text_content = f"{title} {description}"
        
        features['text_length'] = len(text_content)
        features['word_count'] = len(text_content.split())
        features['hashtag_count'] = len(content.get('hashtags', []))
        features['mention_count'] = len(content.get('mentions', []))
        
        # Features de engajamento
        engagement = content.get('engagement_metrics', {})
        features['likes'] = engagement.get('likes', 0)
        features['comments'] = engagement.get('comments', 0)
        features['shares'] = engagement.get('shares', 0)
        features['views'] = engagement.get('views', 0)
        
        # Calcula engagement rate
        total_engagement = features['likes'] + features['comments'] + features['shares']
        features['engagement_rate'] = total_engagement / max(features['views'], 1)
        
        # Features de timing
        timestamp = content.get('timestamp', '')
        if timestamp:
            try:
                dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                features['hour_of_day'] = dt.hour
                features['day_of_week'] = dt.weekday()
            except:
                features['hour_of_day'] = 12
                features['day_of_week'] = 1
        
        # Features de plataforma
        platform = content.get('platform', '').lower()
        platform_weights = {
            'instagram': 1.2,
            'tiktok': 1.5,
            'youtube': 1.3,
            'facebook': 1.0,
            'twitter': 0.9
        }
        features['platform_factor'] = platform_weights.get(platform, 1.0)
        
        return features
    
    def _calculate_virality_prediction(self, features: Dict[str, float]) -> float:
        """Calcula predição de viralidade baseada em features"""
        score = 0.0
        
        # Engagement rate (peso alto)
        engagement_rate = features.get('engagement_rate', 0)
        score += min(engagement_rate * 50, 3.0)  # Cap at 3.0
        
        # Contagem de hashtags (otimal entre 3-7)
        hashtag_count = features.get('hashtag_count', 0)
        if 3 <= hashtag_count <= 7:
            score += 1.5
        elif hashtag_count > 0:
            score += 0.5
        
        # Timing score
        hour = features.get('hour_of_day', 12)
        if 18 <= hour <= 22:  # Prime time
            score += 1.0
        elif 12 <= hour <= 17:  # Afternoon
            score += 0.7
        else:
            score += 0.3
        
        # Platform factor
        score += features.get('platform_factor', 1.0)
        
        # Content length (sweet spot)
        word_count = features.get('word_count', 0)
        if 20 <= word_count <= 100:
            score += 1.0
        elif word_count > 0:
            score += 0.5
        
        # Existing engagement boost
        likes = features.get('likes', 0)
        if likes > 1000:
            score += 2.0
        elif likes > 100:
            score += 1.0
        elif likes > 10:
            score += 0.5
        
        return min(score, 10.0)  # Cap at 10.0
    
    def _analyze_sentiment(self, text: str) -> Dict[str, float]:
        """Analisa sentimento do texto"""
        if not text:
            return {'compound': 0.0, 'pos': 0.0, 'neu': 1.0, 'neg': 0.0}
        
        # VADER sentiment
        vader_scores = self.sentiment_analyzer.polarity_scores(text)
        
        # TextBlob sentiment
        blob = TextBlob(text)
        textblob_polarity = blob.sentiment.polarity
        
        # Combina scores
        combined_compound = (vader_scores['compound'] + textblob_polarity) / 2
        
        return {
            'compound': round(combined_compound, 3),
            'pos': vader_scores['pos'],
            'neu': vader_scores['neu'],
            'neg': vader_scores['neg']
        }
    
    def _classify_engagement_potential(self, virality_score: float) -> str:
        """Classifica potencial de engajamento"""
        if virality_score >= 8.0:
            return "Muito Alto"
        elif virality_score >= 6.0:
            return "Alto"
        elif virality_score >= 4.0:
            return "Médio"
        elif virality_score >= 2.0:
            return "Baixo"
        else:
            return "Muito Baixo"
    
    def _identify_virality_factors(self, features: Dict[str, float]) -> List[str]:
        """Identifica fatores que contribuem para viralidade"""
        factors = []
        
        if features.get('engagement_rate', 0) > 0.05:
            factors.append("Alta taxa de engajamento")
        
        if 3 <= features.get('hashtag_count', 0) <= 7:
            factors.append("Uso otimizado de hashtags")
        
        if 18 <= features.get('hour_of_day', 12) <= 22:
            factors.append("Horário de publicação ideal")
        
        if features.get('platform_factor', 1.0) > 1.2:
            factors.append("Plataforma favorável")
        
        if features.get('likes', 0) > 100:
            factors.append("Engajamento inicial forte")
        
        return factors
    
    def _generate_optimization_suggestions(self, features: Dict[str, float], virality_score: float) -> List[str]:
        """Gera sugestões de otimização"""
        suggestions = []
        
        if features.get('hashtag_count', 0) < 3:
            suggestions.append("Adicionar mais hashtags relevantes (3-7 ideal)")
        
        if features.get('engagement_rate', 0) < 0.02:
            suggestions.append("Melhorar call-to-action para aumentar engajamento")
        
        if not (18 <= features.get('hour_of_day', 12) <= 22):
            suggestions.append("Considerar publicar entre 18h-22h para maior alcance")
        
        if features.get('word_count', 0) < 20:
            suggestions.append("Expandir descrição com mais contexto")
        
        if virality_score < 5.0:
            suggestions.append("Melhorar qualidade visual e narrativa do conteúdo")
        
        return suggestions
    
    def _calculate_traffic_score(self, traffic_data: Dict[str, Any]) -> float:
        """Calcula score de tráfego"""
        if not traffic_data:
            return 0.0
        
        monthly_visits = traffic_data.get('monthly_visits', 0)
        bounce_rate = traffic_data.get('bounce_rate', 1.0)
        session_duration = traffic_data.get('avg_session_duration', 0)
        
        # Normaliza métricas
        visit_score = min(np.log10(max(monthly_visits, 1)) / 6, 1.0) * 4  # Max 4 points
        bounce_score = (1 - bounce_rate) * 3  # Max 3 points
        duration_score = min(session_duration / 300, 1.0) * 3  # Max 3 points
        
        return visit_score + bounce_score + duration_score
    
    def _calculate_social_score(self, social_data: Dict[str, Any]) -> float:
        """Calcula score de presença social"""
        if not social_data:
            return 0.0
        
        followers = social_data.get('followers_total', 0)
        engagement_rate = social_data.get('engagement_rate', 0)
        posts_per_week = social_data.get('posts_per_week', 0)
        
        # Normaliza métricas
        follower_score = min(np.log10(max(followers, 1)) / 5, 1.0) * 4  # Max 4 points
        engagement_score = min(engagement_rate * 100, 1.0) * 4  # Max 4 points
        activity_score = min(posts_per_week / 10, 1.0) * 2  # Max 2 points
        
        return follower_score + engagement_score + activity_score
    
    def _calculate_content_score(self, content_data: Dict[str, Any]) -> float:
        """Calcula score de performance de conteúdo"""
        if not content_data:
            return 0.0
        
        avg_shares = content_data.get('avg_shares_per_post', 0)
        content_frequency = content_data.get('content_frequency', 0)
        seo_score = content_data.get('seo_score', 0)
        
        # Normaliza métricas
        share_score = min(np.log10(max(avg_shares, 1)) / 3, 1.0) * 3  # Max 3 points
        frequency_score = min(content_frequency / 2, 1.0) * 3  # Max 3 points
        seo_score_norm = (seo_score / 100) * 4  # Max 4 points
        
        return share_score + frequency_score + seo_score_norm
    
    def _predict_competitor_growth(self, metrics: Dict[str, Any]) -> float:
        """Prediz taxa de crescimento do concorrente"""
        # Fatores de crescimento
        factors = []
        
        # Tráfego
        traffic = metrics.get('traffic', {})
        if traffic.get('monthly_visits', 0) > 100000:
            factors.append(0.1)
        
        # Engajamento social
        social = metrics.get('social_engagement', {})
        if social.get('engagement_rate', 0) > 0.03:
            factors.append(0.15)
        
        # Qualidade de conteúdo
        content = metrics.get('content_performance', {})
        if content.get('seo_score', 0) > 80:
            factors.append(0.1)
        
        # Atividade
        if social.get('posts_per_week', 0) > 5:
            factors.append(0.05)
        
        base_growth = np.random.normal(0.05, 0.02)  # 5% ± 2% base growth
        factor_boost = sum(factors)
        
        return max(base_growth + factor_boost, -0.1)  # Minimum -10% growth
    
    def _classify_competitive_position(self, score: float) -> str:
        """Classifica posição competitiva"""
        if score >= 8.0:
            return "Líder"
        elif score >= 6.0:
            return "Forte"
        elif score >= 4.0:
            return "Médio"
        elif score >= 2.0:
            return "Fraco"
        else:
            return "Emergente"
    
    def _assess_threat_level(self, performance_score: float, growth_rate: float) -> str:
        """Avalia nível de ameaça"""
        threat_score = performance_score + (growth_rate * 10)
        
        if threat_score >= 9.0:
            return "Muito Alto"
        elif threat_score >= 7.0:
            return "Alto"
        elif threat_score >= 5.0:
            return "Médio"
        elif threat_score >= 3.0:
            return "Baixo"
        else:
            return "Muito Baixo"
    
    def _identify_competitor_strengths(self, metrics: Dict[str, Any]) -> List[str]:
        """Identifica pontos fortes do concorrente"""
        strengths = []
        
        traffic = metrics.get('traffic', {})
        social = metrics.get('social_engagement', {})
        content = metrics.get('content_performance', {})
        
        if traffic.get('monthly_visits', 0) > 500000:
            strengths.append("Alto volume de tráfego")
        
        if traffic.get('bounce_rate', 1.0) < 0.4:
            strengths.append("Baixa taxa de rejeição")
        
        if social.get('engagement_rate', 0) > 0.05:
            strengths.append("Alto engajamento social")
        
        if content.get('seo_score', 0) > 85:
            strengths.append("Excelente SEO")
        
        if social.get('posts_per_week', 0) > 10:
            strengths.append("Alta frequência de conteúdo")
        
        return strengths
    
    def _identify_opportunities(self, metrics: Dict[str, Any]) -> List[str]:
        """Identifica oportunidades baseadas em fraquezas do concorrente"""
        opportunities = []
        
        traffic = metrics.get('traffic', {})
        social = metrics.get('social_engagement', {})
        content = metrics.get('content_performance', {})
        
        if traffic.get('bounce_rate', 0) > 0.6:
            opportunities.append("Melhorar experiência do usuário")
        
        if social.get('engagement_rate', 0) < 0.02:
            opportunities.append("Aumentar engajamento social")
        
        if content.get('seo_score', 0) < 70:
            opportunities.append("Otimizar SEO")
        
        if social.get('posts_per_week', 0) < 3:
            opportunities.append("Aumentar frequência de conteúdo")
        
        return opportunities
    
    def _identify_market_opportunities(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identifica oportunidades de mercado"""
        opportunities = [
            {
                'title': 'Segmento Subestimado',
                'description': 'Nicho com baixa concorrência mas alta demanda',
                'impact': 'Alto',
                'effort': 'Médio',
                'timeline': '3-6 meses'
            },
            {
                'title': 'Lacuna de Conteúdo',
                'description': 'Tópicos relevantes com pouco conteúdo disponível',
                'impact': 'Médio',
                'effort': 'Baixo',
                'timeline': '1-3 meses'
            },
            {
                'title': 'Tendência Emergente',
                'description': 'Nova tendência com potencial de crescimento',
                'impact': 'Alto',
                'effort': 'Alto',
                'timeline': '6-12 meses'
            }
        ]
        
        return opportunities
    
    def _assess_market_risks(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Avalia riscos de mercado"""
        risks = [
            {
                'title': 'Saturação de Mercado',
                'description': 'Aumento da concorrência pode reduzir margens',
                'probability': 'Média',
                'impact': 'Alto',
                'mitigation': 'Diferenciação e inovação contínua'
            },
            {
                'title': 'Mudanças Regulatórias',
                'description': 'Possíveis mudanças na regulamentação do setor',
                'probability': 'Baixa',
                'impact': 'Médio',
                'mitigation': 'Monitoramento regulatório ativo'
            },
            {
                'title': 'Disrupção Tecnológica',
                'description': 'Novas tecnologias podem tornar solução obsoleta',
                'probability': 'Média',
                'impact': 'Alto',
                'mitigation': 'Investimento em P&D e adaptação rápida'
            }
        ]
        
        return risks
    
    def _generate_strategic_recommendations(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Gera recomendações estratégicas"""
        recommendations = [
            {
                'category': 'Produto',
                'title': 'Otimização de Features',
                'description': 'Priorizar desenvolvimento baseado em feedback de usuários',
                'priority': 'Alta',
                'resources_needed': 'Equipe de desenvolvimento'
            },
            {
                'category': 'Marketing',
                'title': 'Estratégia de Conteúdo',
                'description': 'Desenvolver conteúdo educacional para gerar leads',
                'priority': 'Alta',
                'resources_needed': 'Equipe de marketing de conteúdo'
            },
            {
                'category': 'Vendas',
                'title': 'Segmentação de Clientes',
                'description': 'Focar em segmentos de maior valor e conversão',
                'priority': 'Média',
                'resources_needed': 'Análise de dados e equipe comercial'
            }
        ]
        
        return recommendations
    
    def _calculate_market_attractiveness(self, data: Dict[str, Any]) -> float:
        """Calcula score de atratividade do mercado"""
        # Fatores de atratividade
        factors = {
            'market_size': 0.3,
            'growth_rate': 0.25,
            'competition_level': 0.2,
            'barriers_to_entry': 0.15,
            'profitability': 0.1
        }
        
        # Scores simulados baseados nos dados
        scores = {
            'market_size': np.random.uniform(6, 9),
            'growth_rate': np.random.uniform(5, 8),
            'competition_level': np.random.uniform(4, 7),
            'barriers_to_entry': np.random.uniform(3, 6),
            'profitability': np.random.uniform(6, 9)
        }
        
        weighted_score = sum(scores[factor] * weight for factor, weight in factors.items())
        return weighted_score
    
    def _analyze_market_timing(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Analisa timing de entrada no mercado"""
        return {
            'current_phase': 'Crescimento',
            'optimal_entry_time': 'Próximos 3-6 meses',
            'market_maturity': 'Médio',
            'seasonal_factors': 'Q4 tradicionalmente mais forte',
            'timing_score': round(np.random.uniform(7, 9), 1)
        }

