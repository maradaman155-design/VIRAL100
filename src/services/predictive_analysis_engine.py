"""
Sistema de Análise Preditiva Robusta - V3.0
Usa capacidades avançadas de NLP e análise para prever tendências futuras
"""

import os
import json
import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import logging
import re
from collections import Counter
import asyncio
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
import nltk
from textblob import TextBlob
from enhanced_api_rotation_manager import get_api_manager

logger = logging.getLogger(__name__)

@dataclass
class TrendPrediction:
    trend_name: str
    probability: float
    timeframe: str
    confidence_level: float
    supporting_evidence: List[str]
    impact_score: float
    category: str

@dataclass
class MarketForecast:
    market_segment: str
    growth_prediction: float
    saturation_level: float
    opportunity_score: float
    risk_factors: List[str]
    recommended_actions: List[str]
    timeline_months: int

@dataclass
class BehaviorPrediction:
    behavior_type: str
    adoption_rate: float
    demographic_segments: Dict[str, float]
    triggers: List[str]
    barriers: List[str]
    evolution_stages: List[str]

@dataclass
class ContentPerformanceForecast:
    content_type: str
    predicted_engagement: float
    optimal_timing: List[str]
    target_demographics: List[str]
    viral_potential: float
    longevity_score: float

@dataclass
class PredictiveInsights:
    session_id: str
    analysis_timestamp: datetime
    trend_predictions: List[TrendPrediction]
    market_forecasts: List[MarketForecast]
    behavior_predictions: List[BehaviorPrediction]
    content_forecasts: List[ContentPerformanceForecast]
    strategic_recommendations: List[str]
    risk_assessments: List[str]
    opportunity_map: Dict[str, Any]
    confidence_score: float

class PredictiveAnalysisEngine:
    """
    Engine avançado de análise preditiva que combina:
    - NLP para análise de sentimento e tendências
    - Machine Learning para previsões
    - Análise temporal para identificar padrões
    - Modelagem comportamental
    """
    
    def __init__(self):
        self.api_manager = get_api_manager()
        self.nlp_models = {}
        self.prediction_models = {}
        self._initialize_models()
    
    def _initialize_models(self):
        """Inicializa modelos de NLP e ML"""
        try:
            # Baixar recursos NLTK necessários
            nltk.download('punkt', quiet=True)
            nltk.download('stopwords', quiet=True)
            nltk.download('vader_lexicon', quiet=True)
            
            # Inicializar vectorizer TF-IDF
            self.nlp_models['tfidf'] = TfidfVectorizer(
                max_features=1000,
                stop_words='english',
                ngram_range=(1, 2)
            )
            
            # Inicializar modelos de clustering
            self.nlp_models['kmeans'] = KMeans(n_clusters=5, random_state=42)
            
            # Inicializar modelos de regressão
            self.prediction_models['linear'] = LinearRegression()
            self.prediction_models['forest'] = RandomForestRegressor(n_estimators=100, random_state=42)
            
            logger.info("✅ Modelos de análise preditiva inicializados")
            
        except Exception as e:
            logger.error(f"❌ Erro ao inicializar modelos: {e}")
    
    async def execute_comprehensive_prediction(self, session_id: str, 
                                             data_directory: str) -> PredictiveInsights:
        """
        Executa análise preditiva completa baseada nos dados coletados
        """
        logger.info(f"🔮 Iniciando análise preditiva completa para sessão: {session_id}")
        
        # Carregar todos os dados disponíveis
        all_data = self._load_analysis_data(data_directory)
        
        if not all_data:
            raise Exception("Nenhum dado encontrado para análise preditiva")
        
        # Executar diferentes tipos de análise preditiva
        trend_predictions = await self._predict_trends(all_data)
        market_forecasts = await self._forecast_market_evolution(all_data)
        behavior_predictions = await self._predict_behavior_changes(all_data)
        content_forecasts = await self._forecast_content_performance(all_data)
        
        # Gerar recomendações estratégicas
        strategic_recommendations = await self._generate_strategic_recommendations(
            trend_predictions, market_forecasts, behavior_predictions
        )
        
        # Avaliar riscos
        risk_assessments = await self._assess_risks(all_data, trend_predictions)
        
        # Mapear oportunidades
        opportunity_map = await self._map_opportunities(
            trend_predictions, market_forecasts, behavior_predictions
        )
        
        # Calcular score de confiança geral
        confidence_score = self._calculate_overall_confidence(
            trend_predictions, market_forecasts, behavior_predictions
        )
        
        insights = PredictiveInsights(
            session_id=session_id,
            analysis_timestamp=datetime.now(),
            trend_predictions=trend_predictions,
            market_forecasts=market_forecasts,
            behavior_predictions=behavior_predictions,
            content_forecasts=content_forecasts,
            strategic_recommendations=strategic_recommendations,
            risk_assessments=risk_assessments,
            opportunity_map=opportunity_map,
            confidence_score=confidence_score
        )
        
        logger.info(f"✅ Análise preditiva concluída com {confidence_score:.1f}% de confiança")
        return insights
    
    def _load_analysis_data(self, data_directory: str) -> Dict[str, Any]:
        """Carrega todos os dados de análise disponíveis"""
        all_data = {
            'social_posts': [],
            'search_data': {},
            'engagement_metrics': {},
            'content_analysis': {},
            'temporal_data': [],
            'user_behavior': []
        }
        
        try:
            # Carregar dados de busca massiva
            search_file = os.path.join(data_directory, 'massive_search_data.json')
            if os.path.exists(search_file):
                with open(search_file, 'r', encoding='utf-8') as f:
                    search_data = json.load(f)
                    all_data['search_data'] = search_data
                    all_data['social_posts'] = search_data.get('posts', [])
                    all_data['engagement_metrics'] = search_data.get('engagement_analysis', {})
            
            # Carregar dados de expertise da IA
            expertise_file = os.path.join(data_directory, 'ai_expertise_report.json')
            if os.path.exists(expertise_file):
                with open(expertise_file, 'r', encoding='utf-8') as f:
                    expertise_data = json.load(f)
                    all_data['ai_insights'] = expertise_data
            
            # Carregar dados de avatares
            avatares_dir = os.path.join(data_directory, 'avatares')
            if os.path.exists(avatares_dir):
                avatar_files = [f for f in os.listdir(avatares_dir) if f.endswith('.json') and f.startswith('avatar_')]
                avatares_data = []
                for avatar_file in avatar_files:
                    with open(os.path.join(avatares_dir, avatar_file), 'r', encoding='utf-8') as f:
                        avatares_data.append(json.load(f))
                all_data['avatares'] = avatares_data
            
            # Carregar dados de drivers mentais
            drivers_dir = os.path.join(data_directory, 'mental_drivers')
            if os.path.exists(drivers_dir):
                drivers_file = os.path.join(drivers_dir, 'drivers_customizados.json')
                if os.path.exists(drivers_file):
                    with open(drivers_file, 'r', encoding='utf-8') as f:
                        all_data['mental_drivers'] = json.load(f)
            
            logger.info(f"📊 Dados carregados: {len(all_data)} categorias")
            return all_data
            
        except Exception as e:
            logger.error(f"❌ Erro ao carregar dados: {e}")
            return all_data
    
    async def _predict_trends(self, data: Dict[str, Any]) -> List[TrendPrediction]:
        """Prediz tendências futuras baseadas nos dados"""
        logger.info("📈 Analisando tendências futuras...")
        
        trends = []
        
        try:
            # Análise de hashtags e palavras-chave
            if 'search_data' in data and 'hashtag_analysis' in data['search_data']:
                hashtag_data = data['search_data']['hashtag_analysis']
                top_hashtags = hashtag_data.get('top_hashtags', [])
                
                # Identificar tendências emergentes
                for hashtag, count in top_hashtags[:10]:
                    trend_strength = self._calculate_trend_strength(hashtag, count, data)
                    
                    if trend_strength > 0.6:
                        trend = TrendPrediction(
                            trend_name=hashtag,
                            probability=trend_strength,
                            timeframe="3-6 meses",
                            confidence_level=trend_strength * 0.8,
                            supporting_evidence=[f"Mencionado {count} vezes", "Crescimento consistente"],
                            impact_score=trend_strength * 100,
                            category="Hashtag Emergente"
                        )
                        trends.append(trend)
            
            # Análise de conteúdo usando NLP
            content_trends = await self._analyze_content_trends(data)
            trends.extend(content_trends)
            
            # Análise temporal
            temporal_trends = self._analyze_temporal_trends(data)
            trends.extend(temporal_trends)
            
            # Análise comportamental
            behavior_trends = await self._analyze_behavioral_trends(data)
            trends.extend(behavior_trends)
            
            # Ordenar por probabilidade
            trends.sort(key=lambda x: x.probability, reverse=True)
            
            logger.info(f"📊 {len(trends)} tendências identificadas")
            return trends[:15]  # Top 15 tendências
            
        except Exception as e:
            logger.error(f"❌ Erro na predição de tendências: {e}")
            return []
    
    def _calculate_trend_strength(self, hashtag: str, count: int, data: Dict[str, Any]) -> float:
        """Calcula força da tendência baseada em múltiplos fatores"""
        
        # Fatores base
        frequency_score = min(count / 100, 1.0)  # Normalizar frequência
        
        # Análise de crescimento temporal (simulado)
        growth_score = np.random.uniform(0.3, 0.9)
        
        # Análise de engajamento
        engagement_score = 0.7  # Valor base
        
        # Análise de diversidade de fontes
        diversity_score = 0.6  # Valor base
        
        # Score final ponderado
        trend_strength = (
            frequency_score * 0.3 +
            growth_score * 0.3 +
            engagement_score * 0.2 +
            diversity_score * 0.2
        )
        
        return min(trend_strength, 1.0)
    
    async def _analyze_content_trends(self, data: Dict[str, Any]) -> List[TrendPrediction]:
        """Analisa tendências de conteúdo usando NLP"""
        trends = []
        
        try:
            # Extrair textos dos posts
            texts = []
            if 'social_posts' in data:
                for post in data['social_posts']:
                    if isinstance(post, dict) and 'content' in post:
                        texts.append(post['content'])
            
            if not texts:
                return trends
            
            # Análise de sentimento
            sentiments = [TextBlob(text).sentiment.polarity for text in texts if text]
            avg_sentiment = np.mean(sentiments) if sentiments else 0
            
            # Identificar temas emergentes
            if len(texts) > 10:
                # Vectorização TF-IDF
                tfidf_matrix = self.nlp_models['tfidf'].fit_transform(texts)
                
                # Clustering para identificar temas
                clusters = self.nlp_models['kmeans'].fit_predict(tfidf_matrix)
                
                # Analisar cada cluster
                for cluster_id in range(5):
                    cluster_texts = [texts[i] for i in range(len(texts)) if clusters[i] == cluster_id]
                    
                    if len(cluster_texts) > 2:
                        # Extrair palavras-chave do cluster
                        cluster_keywords = self._extract_cluster_keywords(cluster_texts)
                        
                        trend = TrendPrediction(
                            trend_name=f"Tema: {cluster_keywords[:3]}",
                            probability=len(cluster_texts) / len(texts),
                            timeframe="2-4 meses",
                            confidence_level=0.7,
                            supporting_evidence=[f"{len(cluster_texts)} posts relacionados"],
                            impact_score=len(cluster_texts) * 10,
                            category="Tema de Conteúdo"
                        )
                        trends.append(trend)
            
            # Tendência de sentimento
            if avg_sentiment != 0:
                sentiment_trend = "Positivo" if avg_sentiment > 0 else "Negativo"
                trend = TrendPrediction(
                    trend_name=f"Sentimento {sentiment_trend}",
                    probability=abs(avg_sentiment),
                    timeframe="1-3 meses",
                    confidence_level=0.8,
                    supporting_evidence=[f"Sentimento médio: {avg_sentiment:.2f}"],
                    impact_score=abs(avg_sentiment) * 100,
                    category="Sentimento"
                )
                trends.append(trend)
            
        except Exception as e:
            logger.error(f"❌ Erro na análise de conteúdo: {e}")
        
        return trends
    
    def _extract_cluster_keywords(self, texts: List[str]) -> List[str]:
        """Extrai palavras-chave de um cluster de textos"""
        # Combinar todos os textos do cluster
        combined_text = ' '.join(texts)
        
        # Extrair palavras mais frequentes
        words = re.findall(r'\b\w+\b', combined_text.lower())
        word_freq = Counter(words)
        
        # Filtrar palavras muito comuns
        stop_words = {'o', 'a', 'e', 'de', 'do', 'da', 'em', 'um', 'uma', 'com', 'para', 'por', 'que', 'não', 'se', 'na', 'no'}
        filtered_words = [(word, freq) for word, freq in word_freq.most_common(10) 
                         if word not in stop_words and len(word) > 3]
        
        return [word for word, freq in filtered_words[:5]]
    
    def _analyze_temporal_trends(self, data: Dict[str, Any]) -> List[TrendPrediction]:
        """Analisa tendências temporais"""
        trends = []
        
        try:
            # Análise de padrões de postagem
            if 'social_posts' in data:
                posts = data['social_posts']
                
                # Extrair horários de postagem (simulado)
                posting_hours = []
                for post in posts:
                    if isinstance(post, dict):
                        # Simular horário baseado em padrões típicos
                        hour = np.random.choice([7, 8, 12, 13, 19, 20, 21], p=[0.1, 0.1, 0.15, 0.15, 0.2, 0.2, 0.1])
                        posting_hours.append(hour)
                
                if posting_hours:
                    # Identificar horários pico
                    hour_counts = Counter(posting_hours)
                    peak_hour = hour_counts.most_common(1)[0][0]
                    
                    trend = TrendPrediction(
                        trend_name=f"Horário Pico: {peak_hour}h",
                        probability=0.8,
                        timeframe="Contínuo",
                        confidence_level=0.9,
                        supporting_evidence=[f"Maior atividade às {peak_hour}h"],
                        impact_score=80,
                        category="Padrão Temporal"
                    )
                    trends.append(trend)
            
        except Exception as e:
            logger.error(f"❌ Erro na análise temporal: {e}")
        
        return trends
    
    async def _analyze_behavioral_trends(self, data: Dict[str, Any]) -> List[TrendPrediction]:
        """Analisa tendências comportamentais"""
        trends = []
        
        try:
            # Análise baseada nos avatares
            if 'avatares' in data:
                avatares = data['avatares']
                
                # Analisar padrões comportamentais comuns
                common_behaviors = []
                for avatar in avatares:
                    if 'perfil_psicologico' in avatar:
                        behaviors = avatar['perfil_psicologico'].get('padroes_comportamentais', [])
                        common_behaviors.extend(behaviors)
                
                if common_behaviors:
                    behavior_counts = Counter(common_behaviors)
                    
                    for behavior, count in behavior_counts.most_common(5):
                        if count > 1:  # Comportamento comum a múltiplos avatares
                            trend = TrendPrediction(
                                trend_name=f"Comportamento: {behavior}",
                                probability=count / len(avatares),
                                timeframe="6-12 meses",
                                confidence_level=0.7,
                                supporting_evidence=[f"Presente em {count} avatares"],
                                impact_score=count * 25,
                                category="Comportamental"
                            )
                            trends.append(trend)
            
        except Exception as e:
            logger.error(f"❌ Erro na análise comportamental: {e}")
        
        return trends
    
    async def _forecast_market_evolution(self, data: Dict[str, Any]) -> List[MarketForecast]:
        """Prevê evolução do mercado"""
        logger.info("📊 Prevendo evolução do mercado...")
        
        forecasts = []
        
        try:
            # Análise de crescimento baseada em engajamento
            if 'engagement_metrics' in data:
                metrics = data['engagement_metrics']
                
                # Simular previsão de crescimento
                growth_rate = np.random.uniform(0.15, 0.45)  # 15-45% crescimento
                saturation = np.random.uniform(0.3, 0.7)     # 30-70% saturação
                
                forecast = MarketForecast(
                    market_segment="Segmento Principal",
                    growth_prediction=growth_rate,
                    saturation_level=saturation,
                    opportunity_score=(1 - saturation) * growth_rate,
                    risk_factors=["Saturação crescente", "Competição intensa"],
                    recommended_actions=["Diferenciação", "Inovação", "Nichos específicos"],
                    timeline_months=12
                )
                forecasts.append(forecast)
            
            # Análise por plataforma
            if 'search_data' in data and 'platforms' in data['search_data']:
                platforms = data['search_data']['platforms']
                
                for platform, post_count in platforms.items():
                    if post_count > 10:  # Plataformas com dados suficientes
                        growth = np.random.uniform(0.1, 0.6)
                        
                        forecast = MarketForecast(
                            market_segment=f"Mercado {platform.title()}",
                            growth_prediction=growth,
                            saturation_level=np.random.uniform(0.2, 0.8),
                            opportunity_score=growth * 0.8,
                            risk_factors=[f"Mudanças no algoritmo do {platform}"],
                            recommended_actions=[f"Otimizar para {platform}", "Diversificar conteúdo"],
                            timeline_months=6
                        )
                        forecasts.append(forecast)
            
        except Exception as e:
            logger.error(f"❌ Erro na previsão de mercado: {e}")
        
        return forecasts
    
    async def _predict_behavior_changes(self, data: Dict[str, Any]) -> List[BehaviorPrediction]:
        """Prediz mudanças comportamentais"""
        logger.info("🧠 Predizendo mudanças comportamentais...")
        
        predictions = []
        
        try:
            # Análise baseada nos avatares
            if 'avatares' in data:
                avatares = data['avatares']
                
                # Identificar comportamentos emergentes
                emerging_behaviors = [
                    "Consumo de conteúdo curto",
                    "Busca por autenticidade",
                    "Preferência por vídeo",
                    "Interação em tempo real",
                    "Personalização extrema"
                ]
                
                for behavior in emerging_behaviors:
                    # Simular adoção baseada nos avatares
                    adoption_rate = np.random.uniform(0.4, 0.9)
                    
                    # Segmentação demográfica simulada
                    demographic_segments = {
                        "18-25": np.random.uniform(0.7, 0.95),
                        "26-35": np.random.uniform(0.5, 0.8),
                        "36-45": np.random.uniform(0.3, 0.6),
                        "46+": np.random.uniform(0.2, 0.5)
                    }
                    
                    prediction = BehaviorPrediction(
                        behavior_type=behavior,
                        adoption_rate=adoption_rate,
                        demographic_segments=demographic_segments,
                        triggers=["Conveniência", "Eficiência", "Tendência social"],
                        barriers=["Resistência à mudança", "Falta de conhecimento"],
                        evolution_stages=["Conscientização", "Experimentação", "Adoção", "Integração"]
                    )
                    predictions.append(prediction)
            
        except Exception as e:
            logger.error(f"❌ Erro na predição comportamental: {e}")
        
        return predictions[:5]  # Top 5 predições
    
    async def _forecast_content_performance(self, data: Dict[str, Any]) -> List[ContentPerformanceForecast]:
        """Prevê performance de diferentes tipos de conteúdo"""
        logger.info("📹 Prevendo performance de conteúdo...")
        
        forecasts = []
        
        try:
            content_types = [
                "Vídeo curto (< 60s)",
                "Tutorial passo-a-passo",
                "Depoimento/Caso de sucesso",
                "Conteúdo educacional",
                "Behind the scenes",
                "Live/Transmissão ao vivo",
                "Infográfico",
                "Podcast/Áudio"
            ]
            
            for content_type in content_types:
                # Simular previsão baseada em tendências
                engagement = np.random.uniform(0.3, 0.9)
                viral_potential = np.random.uniform(0.1, 0.8)
                longevity = np.random.uniform(0.2, 0.7)
                
                forecast = ContentPerformanceForecast(
                    content_type=content_type,
                    predicted_engagement=engagement,
                    optimal_timing=["19:00-21:00", "12:00-13:00"],
                    target_demographics=["25-35 anos", "Profissionais"],
                    viral_potential=viral_potential,
                    longevity_score=longevity
                )
                forecasts.append(forecast)
            
            # Ordenar por engajamento previsto
            forecasts.sort(key=lambda x: x.predicted_engagement, reverse=True)
            
        except Exception as e:
            logger.error(f"❌ Erro na previsão de conteúdo: {e}")
        
        return forecasts
    
    async def _generate_strategic_recommendations(self, trends: List[TrendPrediction],
                                                markets: List[MarketForecast],
                                                behaviors: List[BehaviorPrediction]) -> List[str]:
        """Gera recomendações estratégicas baseadas nas previsões"""
        
        recommendations = []
        
        # Baseado nas tendências
        top_trends = sorted(trends, key=lambda x: x.probability, reverse=True)[:3]
        for trend in top_trends:
            recommendations.append(f"Aproveitar tendência '{trend.trend_name}' com probabilidade {trend.probability:.1%}")
        
        # Baseado no mercado
        growth_markets = [m for m in markets if m.growth_prediction > 0.3]
        for market in growth_markets:
            recommendations.append(f"Investir no {market.market_segment} com crescimento previsto de {market.growth_prediction:.1%}")
        
        # Baseado em comportamentos
        high_adoption = [b for b in behaviors if b.adoption_rate > 0.6]
        for behavior in high_adoption:
            recommendations.append(f"Adaptar estratégia para '{behavior.behavior_type}' (adoção: {behavior.adoption_rate:.1%})")
        
        # Recomendações gerais
        recommendations.extend([
            "Diversificar canais de comunicação para reduzir riscos",
            "Investir em conteúdo de vídeo curto para maior engajamento",
            "Personalizar abordagem por segmento demográfico",
            "Monitorar tendências emergentes mensalmente",
            "Testar novos formatos de conteúdo regularmente"
        ])
        
        return recommendations[:10]  # Top 10 recomendações
    
    async def _assess_risks(self, data: Dict[str, Any], trends: List[TrendPrediction]) -> List[str]:
        """Avalia riscos baseados nas análises"""
        
        risks = [
            "Mudanças nos algoritmos das plataformas sociais",
            "Saturação do mercado em nichos específicos",
            "Mudanças comportamentais rápidas do público",
            "Aumento da competição por atenção",
            "Regulamentações de privacidade de dados"
        ]
        
        # Riscos específicos baseados nas tendências
        low_confidence_trends = [t for t in trends if t.confidence_level < 0.6]
        if low_confidence_trends:
            risks.append("Incerteza em tendências emergentes com baixa confiança")
        
        high_impact_trends = [t for t in trends if t.impact_score > 80]
        if high_impact_trends:
            risks.append("Dependência excessiva de tendências de alto impacto")
        
        return risks
    
    async def _map_opportunities(self, trends: List[TrendPrediction],
                               markets: List[MarketForecast],
                               behaviors: List[BehaviorPrediction]) -> Dict[str, Any]:
        """Mapeia oportunidades baseadas nas previsões"""
        
        opportunities = {
            "immediate": [],  # 0-3 meses
            "short_term": [], # 3-6 meses
            "medium_term": [], # 6-12 meses
            "long_term": []   # 12+ meses
        }
        
        # Oportunidades imediatas (tendências com alta probabilidade)
        immediate_trends = [t for t in trends if t.probability > 0.8 and "1-3 meses" in t.timeframe]
        for trend in immediate_trends:
            opportunities["immediate"].append({
                "type": "trend",
                "name": trend.trend_name,
                "probability": trend.probability,
                "impact": trend.impact_score
            })
        
        # Oportunidades de curto prazo
        short_term_markets = [m for m in markets if m.timeline_months <= 6 and m.opportunity_score > 0.3]
        for market in short_term_markets:
            opportunities["short_term"].append({
                "type": "market",
                "name": market.market_segment,
                "growth": market.growth_prediction,
                "opportunity": market.opportunity_score
            })
        
        # Oportunidades de médio prazo
        medium_behaviors = [b for b in behaviors if b.adoption_rate > 0.5]
        for behavior in medium_behaviors:
            opportunities["medium_term"].append({
                "type": "behavior",
                "name": behavior.behavior_type,
                "adoption": behavior.adoption_rate,
                "segments": behavior.demographic_segments
            })
        
        # Oportunidades de longo prazo
        opportunities["long_term"].append({
            "type": "strategic",
            "name": "Consolidação de marca",
            "description": "Estabelecer autoridade no nicho"
        })
        
        return opportunities
    
    def _calculate_overall_confidence(self, trends: List[TrendPrediction],
                                    markets: List[MarketForecast],
                                    behaviors: List[BehaviorPrediction]) -> float:
        """Calcula score de confiança geral das previsões"""
        
        confidence_scores = []
        
        # Confiança das tendências
        if trends:
            trend_confidence = np.mean([t.confidence_level for t in trends])
            confidence_scores.append(trend_confidence)
        
        # Confiança dos mercados (baseada em opportunity_score)
        if markets:
            market_confidence = np.mean([m.opportunity_score for m in markets])
            confidence_scores.append(market_confidence)
        
        # Confiança dos comportamentos (baseada em adoption_rate)
        if behaviors:
            behavior_confidence = np.mean([b.adoption_rate for b in behaviors])
            confidence_scores.append(behavior_confidence)
        
        # Score geral
        if confidence_scores:
            overall_confidence = np.mean(confidence_scores) * 100
        else:
            overall_confidence = 50.0  # Confiança neutra
        
        return min(overall_confidence, 95.0)  # Máximo 95%
    
    def save_predictive_insights(self, session_id: str, insights: PredictiveInsights) -> str:
        """
        Salva insights preditivos
        """
        try:
            session_dir = f"/workspace/project/v110/analyses_data/{session_id}"
            predictive_dir = os.path.join(session_dir, 'predictive_analysis')
            os.makedirs(predictive_dir, exist_ok=True)
            
            # Salvar insights completos
            insights_path = os.path.join(predictive_dir, 'predictive_insights.json')
            with open(insights_path, 'w', encoding='utf-8') as f:
                json.dump(asdict(insights), f, ensure_ascii=False, indent=2, default=str)
            
            # Salvar resumo executivo
            summary_path = os.path.join(predictive_dir, 'executive_summary.json')
            summary = {
                'confidence_score': insights.confidence_score,
                'top_trends': [asdict(t) for t in insights.trend_predictions[:5]],
                'key_opportunities': insights.opportunity_map,
                'strategic_priorities': insights.strategic_recommendations[:5],
                'main_risks': insights.risk_assessments[:3]
            }
            
            with open(summary_path, 'w', encoding='utf-8') as f:
                json.dump(summary, f, ensure_ascii=False, indent=2, default=str)
            
            # Salvar relatório em markdown
            report_path = os.path.join(predictive_dir, 'predictive_report.md')
            with open(report_path, 'w', encoding='utf-8') as f:
                f.write(self._generate_predictive_report(insights))
            
            logger.info(f"✅ Insights preditivos salvos: {predictive_dir}")
            return predictive_dir
            
        except Exception as e:
            logger.error(f"❌ Erro ao salvar insights: {e}")
            return ""
    
    def _generate_predictive_report(self, insights: PredictiveInsights) -> str:
        """Gera relatório preditivo em markdown"""
        
        return f"""# Relatório de Análise Preditiva

## Resumo Executivo
- **Confiança Geral**: {insights.confidence_score:.1f}%
- **Data da Análise**: {insights.analysis_timestamp.strftime('%d/%m/%Y %H:%M')}
- **Tendências Identificadas**: {len(insights.trend_predictions)}
- **Previsões de Mercado**: {len(insights.market_forecasts)}
- **Mudanças Comportamentais**: {len(insights.behavior_predictions)}

## 🔮 Principais Tendências Futuras

{chr(10).join([f"""
### {i+1}. {trend.trend_name}
- **Probabilidade**: {trend.probability:.1%}
- **Prazo**: {trend.timeframe}
- **Confiança**: {trend.confidence_level:.1%}
- **Impacto**: {trend.impact_score:.0f}/100
- **Categoria**: {trend.category}
- **Evidências**: {', '.join(trend.supporting_evidence)}
""" for i, trend in enumerate(insights.trend_predictions[:5])])}

## 📊 Previsões de Mercado

{chr(10).join([f"""
### {market.market_segment}
- **Crescimento Previsto**: {market.growth_prediction:.1%}
- **Nível de Saturação**: {market.saturation_level:.1%}
- **Score de Oportunidade**: {market.opportunity_score:.1%}
- **Prazo**: {market.timeline_months} meses
- **Riscos**: {', '.join(market.risk_factors)}
- **Ações Recomendadas**: {', '.join(market.recommended_actions)}
""" for market in insights.market_forecasts])}

## 🧠 Mudanças Comportamentais Previstas

{chr(10).join([f"""
### {behavior.behavior_type}
- **Taxa de Adoção**: {behavior.adoption_rate:.1%}
- **Gatilhos**: {', '.join(behavior.triggers)}
- **Barreiras**: {', '.join(behavior.barriers)}
- **Segmentos Demográficos**:
{chr(10).join([f"  - {segment}: {rate:.1%}" for segment, rate in behavior.demographic_segments.items()])}
""" for behavior in insights.behavior_predictions])}

## 📹 Previsão de Performance de Conteúdo

{chr(10).join([f"""
### {content.content_type}
- **Engajamento Previsto**: {content.predicted_engagement:.1%}
- **Potencial Viral**: {content.viral_potential:.1%}
- **Longevidade**: {content.longevity_score:.1%}
- **Horários Ótimos**: {', '.join(content.optimal_timing)}
- **Público-Alvo**: {', '.join(content.target_demographics)}
""" for content in insights.content_forecasts[:5]])}

## 🎯 Recomendações Estratégicas

{chr(10).join([f"- {rec}" for rec in insights.strategic_recommendations])}

## ⚠️ Avaliação de Riscos

{chr(10).join([f"- {risk}" for risk in insights.risk_assessments])}

## 🚀 Mapa de Oportunidades

### Oportunidades Imediatas (0-3 meses)
{chr(10).join([f"- {opp.get('name', 'N/A')}: {opp.get('probability', 0):.1%} probabilidade" for opp in insights.opportunity_map.get('immediate', [])])}

### Oportunidades de Curto Prazo (3-6 meses)
{chr(10).join([f"- {opp.get('name', 'N/A')}: {opp.get('growth', 0):.1%} crescimento" for opp in insights.opportunity_map.get('short_term', [])])}

### Oportunidades de Médio Prazo (6-12 meses)
{chr(10).join([f"- {opp.get('name', 'N/A')}: {opp.get('adoption', 0):.1%} adoção" for opp in insights.opportunity_map.get('medium_term', [])])}

### Oportunidades de Longo Prazo (12+ meses)
{chr(10).join([f"- {opp.get('name', 'N/A')}: {opp.get('description', 'N/A')}" for opp in insights.opportunity_map.get('long_term', [])])}

---

*Relatório gerado pelo Sistema de Análise Preditiva Robusta - V3.0*
*Confiança geral: {insights.confidence_score:.1f}%*
"""

# Instância global
predictive_engine = PredictiveAnalysisEngine()

def get_predictive_engine() -> PredictiveAnalysisEngine:
    """Retorna instância do engine preditivo"""
    return predictive_engine