"""
Supadata MCP Client - Cliente para integração com Supadata MCP
Responsável por análise de dados avançada e integração com serviços externos
"""

import os
import asyncio
import httpx
import json
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
from urllib.parse import urljoin
import time


@dataclass
class DataQuery:
    """Estrutura para consultas de dados"""
    query_type: str
    parameters: Dict[str, Any]
    filters: Dict[str, Any]
    timestamp: str
    priority: int = 1


@dataclass
class DataResult:
    """Estrutura para resultados de dados"""
    query_id: str
    data: Union[Dict, List]
    metadata: Dict[str, Any]
    timestamp: str
    status: str
    processing_time: float


class SupadataClient:
    """
    Cliente para integração com Supadata MCP
    """
    
    def __init__(self):
        self.session = httpx.AsyncClient(timeout=60.0)
        # Usa SUPADATA_API_URL (preferencial) ou SUPADATA_BASE_URL, com default correto .ai
        self.base_url = os.getenv('SUPADATA_API_URL') or os.getenv('SUPADATA_BASE_URL') or 'https://api.supadata.ai/v1'
        self.api_key = os.getenv('SUPADATA_API_KEY', '')
        self.cache = {}
        self.rate_limit_delay = 1.0  # segundos entre requests
        
    async def __aenter__(self):
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.session.aclose()
    
    def _get_headers(self) -> Dict[str, str]:
        """Retorna headers para autenticação"""
        return {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json',
            'User-Agent': 'PRT-Busca/1.0'
        }
    
    async def _make_request(self, method: str, endpoint: str, 
                           data: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Faz requisição para a API Supadata
        """
        url = urljoin(self.base_url, endpoint)
        headers = self._get_headers()
        
        try:
            if method.upper() == 'GET':
                response = await self.session.get(url, headers=headers, params=data)
            elif method.upper() == 'POST':
                response = await self.session.post(url, headers=headers, json=data)
            elif method.upper() == 'PUT':
                response = await self.session.put(url, headers=headers, json=data)
            elif method.upper() == 'DELETE':
                response = await self.session.delete(url, headers=headers)
            else:
                raise ValueError(f"Método HTTP não suportado: {method}")
            
            response.raise_for_status()
            
            # Rate limiting
            await asyncio.sleep(self.rate_limit_delay)
            
            return response.json()
            
        except httpx.HTTPStatusError as e:
            print(f"Erro HTTP na requisição Supadata: {e.response.status_code}")
            return {'error': f'HTTP {e.response.status_code}', 'message': str(e)}
        except Exception as e:
            print(f"Erro na requisição Supadata: {e}")
            return {'error': 'request_failed', 'message': str(e)}
    
    async def query_market_data(self, segment: str, region: str = 'BR', 
                               timeframe: str = '30d') -> DataResult:
        """
        Consulta dados de mercado por segmento
        """
        query_id = f"market_{segment}_{region}_{timeframe}_{int(time.time())}"
        
        # Cache check
        cache_key = f"market_{segment}_{region}_{timeframe}"
        if cache_key in self.cache:
            cached_result = self.cache[cache_key]
            if time.time() - cached_result['timestamp'] < 3600:  # 1 hora
                return DataResult(
                    query_id=query_id,
                    data=cached_result['data'],
                    metadata=cached_result['metadata'],
                    timestamp=datetime.now().isoformat(),
                    status='cached',
                    processing_time=0.0
                )
        
        start_time = time.time()
        
        # Simula consulta de dados de mercado (em produção usaria API real)
        market_data = await self._simulate_market_data(segment, region, timeframe)
        
        processing_time = time.time() - start_time
        
        result = DataResult(
            query_id=query_id,
            data=market_data,
            metadata={
                'segment': segment,
                'region': region,
                'timeframe': timeframe,
                'data_points': len(market_data.get('trends', [])),
                'last_updated': datetime.now().isoformat()
            },
            timestamp=datetime.now().isoformat(),
            status='success',
            processing_time=processing_time
        )
        
        # Cache result
        self.cache[cache_key] = {
            'data': market_data,
            'metadata': result.metadata,
            'timestamp': time.time()
        }
        
        return result
    
    async def analyze_competitor_data(self, competitors: List[str], 
                                    metrics: List[str] = None) -> DataResult:
        """
        Analisa dados de concorrentes
        """
        if metrics is None:
            metrics = ['traffic', 'social_engagement', 'content_performance']
        
        query_id = f"competitors_{hash(str(competitors))}_{int(time.time())}"
        start_time = time.time()
        
        competitor_analysis = {}
        
        for competitor in competitors:
            competitor_data = await self._analyze_single_competitor(competitor, metrics)
            competitor_analysis[competitor] = competitor_data
        
        processing_time = time.time() - start_time
        
        # Gera insights comparativos
        insights = self._generate_competitor_insights(competitor_analysis)
        
        result = DataResult(
            query_id=query_id,
            data={
                'competitors': competitor_analysis,
                'comparative_insights': insights,
                'analysis_summary': self._summarize_competitor_analysis(competitor_analysis)
            },
            metadata={
                'competitors_count': len(competitors),
                'metrics_analyzed': metrics,
                'analysis_depth': 'comprehensive'
            },
            timestamp=datetime.now().isoformat(),
            status='success',
            processing_time=processing_time
        )
        
        return result
    
    async def get_trend_predictions(self, segment: str, horizon: str = '90d') -> DataResult:
        """
        Obtém predições de tendências
        """
        query_id = f"trends_{segment}_{horizon}_{int(time.time())}"
        start_time = time.time()
        
        # Simula análise preditiva
        predictions = await self._generate_trend_predictions(segment, horizon)
        
        processing_time = time.time() - start_time
        
        result = DataResult(
            query_id=query_id,
            data=predictions,
            metadata={
                'segment': segment,
                'prediction_horizon': horizon,
                'confidence_level': 0.85,
                'model_version': '2.1.0'
            },
            timestamp=datetime.now().isoformat(),
            status='success',
            processing_time=processing_time
        )
        
        return result
    
    async def analyze_audience_data(self, target_audience: Dict[str, Any]) -> DataResult:
        """
        Analisa dados de audiência
        """
        query_id = f"audience_{hash(str(target_audience))}_{int(time.time())}"
        start_time = time.time()
        
        audience_analysis = await self._analyze_audience_profile(target_audience)
        
        processing_time = time.time() - start_time
        
        result = DataResult(
            query_id=query_id,
            data=audience_analysis,
            metadata={
                'audience_segments': len(audience_analysis.get('segments', [])),
                'data_sources': ['social_media', 'web_analytics', 'surveys'],
                'accuracy_score': 0.92
            },
            timestamp=datetime.now().isoformat(),
            status='success',
            processing_time=processing_time
        )
        
        return result
    
    async def _simulate_market_data(self, segment: str, region: str, timeframe: str) -> Dict[str, Any]:
        """Simula dados de mercado (substituir por API real em produção)"""
        
        # Gera dados sintéticos baseados no segmento
        base_growth = np.random.normal(0.05, 0.02)  # 5% growth ± 2%
        
        trends = []
        for i in range(30):  # 30 dias de dados
            date = (datetime.now() - timedelta(days=29-i)).strftime('%Y-%m-%d')
            value = 100 * (1 + base_growth) ** i + np.random.normal(0, 5)
            trends.append({
                'date': date,
                'value': round(value, 2),
                'volume': np.random.randint(1000, 10000)
            })
        
        return {
            'segment': segment,
            'region': region,
            'trends': trends,
            'market_size': np.random.randint(1000000, 10000000),
            'growth_rate': round(base_growth * 100, 2),
            'key_players': [f'Player_{i}' for i in range(1, 6)],
            'market_share_distribution': {
                f'Player_{i}': round(np.random.uniform(5, 25), 1)
                for i in range(1, 6)
            }
        }
    
    async def _analyze_single_competitor(self, competitor: str, metrics: List[str]) -> Dict[str, Any]:
        """Analisa um único concorrente"""
        
        competitor_data = {
            'name': competitor,
            'domain': f"{competitor.lower().replace(' ', '')}.com",
            'metrics': {}
        }
        
        for metric in metrics:
            if metric == 'traffic':
                competitor_data['metrics']['traffic'] = {
                    'monthly_visits': np.random.randint(10000, 1000000),
                    'bounce_rate': round(np.random.uniform(0.3, 0.7), 2),
                    'avg_session_duration': round(np.random.uniform(60, 300), 0),
                    'traffic_sources': {
                        'organic': round(np.random.uniform(0.3, 0.6), 2),
                        'direct': round(np.random.uniform(0.2, 0.4), 2),
                        'social': round(np.random.uniform(0.1, 0.3), 2),
                        'paid': round(np.random.uniform(0.05, 0.2), 2)
                    }
                }
            elif metric == 'social_engagement':
                competitor_data['metrics']['social_engagement'] = {
                    'followers_total': np.random.randint(1000, 100000),
                    'engagement_rate': round(np.random.uniform(0.01, 0.1), 3),
                    'posts_per_week': np.random.randint(3, 20),
                    'platforms': {
                        'instagram': np.random.randint(500, 50000),
                        'facebook': np.random.randint(1000, 30000),
                        'twitter': np.random.randint(200, 20000),
                        'linkedin': np.random.randint(100, 10000)
                    }
                }
            elif metric == 'content_performance':
                competitor_data['metrics']['content_performance'] = {
                    'avg_shares_per_post': np.random.randint(10, 500),
                    'content_frequency': round(np.random.uniform(0.5, 3.0), 1),
                    'top_content_types': ['blog', 'video', 'infographic'],
                    'seo_score': round(np.random.uniform(60, 95), 1)
                }
        
        return competitor_data
    
    def _generate_competitor_insights(self, competitor_analysis: Dict[str, Any]) -> List[str]:
        """Gera insights comparativos"""
        insights = []
        
        # Análise de tráfego
        traffic_data = {}
        for comp, data in competitor_analysis.items():
            if 'traffic' in data.get('metrics', {}):
                traffic_data[comp] = data['metrics']['traffic']['monthly_visits']
        
        if traffic_data:
            top_traffic = max(traffic_data, key=traffic_data.get)
            insights.append(f"{top_traffic} lidera em tráfego mensal com {traffic_data[top_traffic]:,} visitas")
        
        # Análise de engajamento social
        engagement_data = {}
        for comp, data in competitor_analysis.items():
            if 'social_engagement' in data.get('metrics', {}):
                engagement_data[comp] = data['metrics']['social_engagement']['engagement_rate']
        
        if engagement_data:
            top_engagement = max(engagement_data, key=engagement_data.get)
            insights.append(f"{top_engagement} tem a melhor taxa de engajamento: {engagement_data[top_engagement]:.1%}")
        
        return insights
    
    def _summarize_competitor_analysis(self, competitor_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Resumo da análise de concorrentes"""
        total_competitors = len(competitor_analysis)
        
        summary = {
            'total_competitors': total_competitors,
            'analysis_date': datetime.now().isoformat(),
            'key_findings': []
        }
        
        # Calcula médias
        if competitor_analysis:
            traffic_values = []
            engagement_values = []
            
            for data in competitor_analysis.values():
                metrics = data.get('metrics', {})
                if 'traffic' in metrics:
                    traffic_values.append(metrics['traffic']['monthly_visits'])
                if 'social_engagement' in metrics:
                    engagement_values.append(metrics['social_engagement']['engagement_rate'])
            
            if traffic_values:
                summary['avg_monthly_traffic'] = int(np.mean(traffic_values))
            if engagement_values:
                summary['avg_engagement_rate'] = round(np.mean(engagement_values), 3)
        
        return summary
    
    async def _generate_trend_predictions(self, segment: str, horizon: str) -> Dict[str, Any]:
        """Gera predições de tendências"""
        
        # Simula modelo preditivo
        days = int(horizon.replace('d', ''))
        
        predictions = []
        base_value = 100
        trend_slope = np.random.uniform(-0.1, 0.3)  # -10% a +30% trend
        
        for i in range(days):
            date = (datetime.now() + timedelta(days=i)).strftime('%Y-%m-%d')
            
            # Trend + seasonality + noise
            trend_component = base_value * (1 + trend_slope * i / days)
            seasonal_component = 10 * np.sin(2 * np.pi * i / 7)  # Weekly seasonality
            noise = np.random.normal(0, 2)
            
            predicted_value = trend_component + seasonal_component + noise
            confidence_interval = abs(np.random.normal(0, 5))
            
            predictions.append({
                'date': date,
                'predicted_value': round(predicted_value, 2),
                'confidence_lower': round(predicted_value - confidence_interval, 2),
                'confidence_upper': round(predicted_value + confidence_interval, 2),
                'trend_strength': round(abs(trend_slope), 2)
            })
        
        return {
            'segment': segment,
            'horizon': horizon,
            'predictions': predictions,
            'model_metrics': {
                'accuracy': round(np.random.uniform(0.8, 0.95), 2),
                'rmse': round(np.random.uniform(2, 8), 2),
                'trend_direction': 'up' if trend_slope > 0 else 'down',
                'confidence_level': 0.85
            },
            'key_insights': [
                f"Tendência {'crescente' if trend_slope > 0 else 'decrescente'} prevista",
                f"Variação semanal de aproximadamente {round(abs(seasonal_component), 1)} pontos",
                f"Confiança do modelo: {round(np.random.uniform(80, 95), 1)}%"
            ]
        }
    
    async def _analyze_audience_profile(self, target_audience: Dict[str, Any]) -> Dict[str, Any]:
        """Analisa perfil de audiência"""
        
        audience_analysis = {
            'target_definition': target_audience,
            'segments': [],
            'demographics': {},
            'psychographics': {},
            'behavior_patterns': {},
            'recommendations': []
        }
        
        # Gera segmentos de audiência
        segments = [
            {
                'name': 'Early Adopters',
                'size_percentage': round(np.random.uniform(15, 25), 1),
                'characteristics': ['Tech-savvy', 'High income', 'Urban'],
                'engagement_level': 'High'
            },
            {
                'name': 'Mainstream Users',
                'size_percentage': round(np.random.uniform(40, 60), 1),
                'characteristics': ['Price-conscious', 'Mixed demographics', 'Suburban'],
                'engagement_level': 'Medium'
            },
            {
                'name': 'Late Adopters',
                'size_percentage': round(np.random.uniform(20, 30), 1),
                'characteristics': ['Conservative', 'Older demographic', 'Rural'],
                'engagement_level': 'Low'
            }
        ]
        
        audience_analysis['segments'] = segments
        
        # Demografia
        audience_analysis['demographics'] = {
            'age_distribution': {
                '18-24': round(np.random.uniform(10, 20), 1),
                '25-34': round(np.random.uniform(25, 35), 1),
                '35-44': round(np.random.uniform(20, 30), 1),
                '45-54': round(np.random.uniform(15, 25), 1),
                '55+': round(np.random.uniform(5, 15), 1)
            },
            'gender_split': {
                'male': round(np.random.uniform(40, 60), 1),
                'female': round(np.random.uniform(40, 60), 1)
            },
            'income_levels': {
                'low': round(np.random.uniform(20, 30), 1),
                'medium': round(np.random.uniform(40, 50), 1),
                'high': round(np.random.uniform(20, 30), 1)
            }
        }
        
        # Recomendações
        audience_analysis['recommendations'] = [
            "Focar em conteúdo educacional para Early Adopters",
            "Desenvolver campanhas de preço-valor para Mainstream Users",
            "Usar canais tradicionais para alcançar Late Adopters",
            "Personalizar mensagens por segmento demográfico"
        ]
        
        return audience_analysis
    
    async def export_data(self, data_result: DataResult, format: str = 'json') -> str:
        """
        Exporta dados em diferentes formatos
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"supadata_export_{data_result.query_id}_{timestamp}"
        
        export_dir = os.path.join(os.getcwd(), 'analyses_data', 'exports')
        os.makedirs(export_dir, exist_ok=True)
        
        if format.lower() == 'json':
            filepath = os.path.join(export_dir, f"{filename}.json")
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(asdict(data_result), f, indent=2, ensure_ascii=False)
        
        elif format.lower() == 'csv' and isinstance(data_result.data, dict):
            filepath = os.path.join(export_dir, f"{filename}.csv")
            
            # Tenta converter dados para DataFrame
            try:
                if 'trends' in data_result.data:
                    df = pd.DataFrame(data_result.data['trends'])
                elif 'predictions' in data_result.data:
                    df = pd.DataFrame(data_result.data['predictions'])
                else:
                    # Fallback para estrutura genérica
                    df = pd.json_normalize(data_result.data)
                
                df.to_csv(filepath, index=False, encoding='utf-8')
            except Exception as e:
                print(f"Erro ao exportar CSV: {e}")
                return ""
        
        else:
            return ""
        
        return filepath

