
"""
DEEP RESEARCH MCP CLIENT
Cliente para integração com DeepResearchMCP do GitHub
Conforme especificado no Plano de Aprimoramento 85v350
"""

import asyncio
import aiohttp
import json
import os
from typing import Dict, Any, Optional, List
from dataclasses import dataclass


@dataclass 
class ResearchRequest:
    """Estrutura de requisição de pesquisa"""
    query: str
    depth_level: int = 3
    max_sources: int = 10
    domains_filter: Optional[List[str]] = None
    language: str = "pt-BR"


class DeepResearchMCPClient:
    """
    CLIENTE PARA DEEPRESEARCHMCP
    
    Funcionalidades:
    - Pesquisa aprofundada via MCP
    - Análise de múltiplas fontes
    - Extração de insights relevantes
    - Integração com workflow de análise
    """
    
    def __init__(self):
        """Inicializa cliente DeepResearchMCP"""
        
        self.base_url = os.getenv(
            'DEEP_RESEARCH_MCP_URL', 
            'https://api.deepresearch.mcp.smithery.ai'
        )
        self.api_key = os.getenv('DEEP_RESEARCH_MCP_KEY', '')
        self.timeout = 120  # 2 minutos para pesquisas profundas
        
        # Headers padrão
        self.headers = {
            'Content-Type': 'application/json',
            'User-Agent': 'ManusAI-DeepResearch/1.0'
        }
        
        if self.api_key:
            self.headers['Authorization'] = f'Bearer {self.api_key}'
    
    async def execute_deep_research(
        self, 
        request: ResearchRequest
    ) -> Dict[str, Any]:
        """
        EXECUTA PESQUISA APROFUNDADA
        
        Args:
            request: Requisição de pesquisa estruturada
            
        Returns:
            Resultados da pesquisa aprofundada
        """
        
        try:
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=self.timeout)) as session:
                
                # Preparar payload
                payload = {
                    'query': request.query,
                    'options': {
                        'depth_level': request.depth_level,
                        'max_sources': request.max_sources,
                        'language': request.language,
                        'include_analysis': True,
                        'extract_insights': True
                    }
                }
                
                if request.domains_filter:
                    payload['options']['domains_filter'] = request.domains_filter
                
                # Executar requisição
                async with session.post(
                    f"{self.base_url}/research/deep",
                    headers=self.headers,
                    json=payload
                ) as response:
                    
                    if response.status == 200:
                        result = await response.json()
                        return await self._process_research_result(result)
                    
                    elif response.status == 202:
                        # Pesquisa assíncrona - aguardar conclusão
                        task_id = (await response.json()).get('task_id')
                        return await self._wait_for_async_result(session, task_id)
                    
                    else:
                        error_text = await response.text()
                        return {
                            'success': False,
                            'error': f'HTTP {response.status}: {error_text}',
                            'fallback_used': True
                        }
        
        except asyncio.TimeoutError:
            return await self._fallback_research(request)
        
        except Exception as e:
            return {
                'success': False,
                'error': f'Erro no DeepResearchMCP: {str(e)}',
                'fallback_used': True,
                'fallback_result': await self._fallback_research(request)
            }
    
    async def _wait_for_async_result(
        self, 
        session: aiohttp.ClientSession, 
        task_id: str
    ) -> Dict[str, Any]:
        """Aguarda resultado de pesquisa assíncrona"""
        
        max_attempts = 60  # 5 minutos máximo
        attempt = 0
        
        while attempt < max_attempts:
            try:
                async with session.get(
                    f"{self.base_url}/research/status/{task_id}",
                    headers=self.headers
                ) as response:
                    
                    if response.status == 200:
                        status_data = await response.json()
                        
                        if status_data.get('status') == 'completed':
                            return await self._process_research_result(
                                status_data.get('result', {})
                            )
                        
                        elif status_data.get('status') == 'failed':
                            return {
                                'success': False,
                                'error': status_data.get('error', 'Pesquisa falhou'),
                                'fallback_used': True
                            }
                        
                        # Ainda processando
                        await asyncio.sleep(5)
                        attempt += 1
                    
                    else:
                        break
            
            except Exception:
                await asyncio.sleep(5)
                attempt += 1
        
        # Timeout na verificação
        return {
            'success': False,
            'error': 'Timeout aguardando resultado da pesquisa assíncrona',
            'fallback_used': True
        }
    
    async def _process_research_result(self, raw_result: Dict[str, Any]) -> Dict[str, Any]:
        """Processa resultado bruto da pesquisa"""
        
        processed = {
            'success': True,
            'sources_analyzed': raw_result.get('sources_count', 0),
            'research_depth': raw_result.get('depth_achieved', 0),
            'execution_time': raw_result.get('execution_time', 0)
        }
        
        # Extrair conteúdo principal
        content = raw_result.get('content', {})
        processed.update({
            'key_findings': content.get('key_findings', []),
            'insights': content.get('insights', []),
            'data_points': content.get('data_points', []),
            'trends_identified': content.get('trends', []),
            'sources': content.get('sources', [])
        })
        
        # Análise qualitativa
        analysis = raw_result.get('analysis', {})
        processed.update({
            'credibility_score': analysis.get('credibility_score', 0),
            'relevance_score': analysis.get('relevance_score', 0),
            'completeness_score': analysis.get('completeness_score', 0),
            'recommendations': analysis.get('recommendations', [])
        })
        
        # Metadados
        processed['metadata'] = {
            'research_timestamp': raw_result.get('timestamp'),
            'model_version': raw_result.get('model_version'),
            'language_detected': raw_result.get('language_detected'),
            'domains_covered': raw_result.get('domains_covered', [])
        }
        
        return processed
    
    async def _fallback_research(self, request: ResearchRequest) -> Dict[str, Any]:
        """Pesquisa de fallback quando DeepResearchMCP falha"""
        
        # Implementar pesquisa básica como fallback
        return {
            'success': False,
            'fallback_used': True,
            'basic_research': {
                'query': request.query,
                'message': 'DeepResearchMCP indisponível - usando pesquisa básica',
                'suggestions': [
                    f'Pesquisar "{request.query}" manualmente',
                    'Verificar configuração do DeepResearchMCP',
                    'Usar outros provedores de pesquisa'
                ]
            }
        }
    
    async def research_market_segment(self, segment: str) -> Dict[str, Any]:
        """Pesquisa específica para segmento de mercado"""
        
        request = ResearchRequest(
            query=f"análise mercado {segment} tendências 2024 oportunidades",
            depth_level=4,
            max_sources=15,
            domains_filter=[
                'ibge.gov.br', 'sebrae.com.br', 'statista.com',
                'mckinsey.com', 'pwc.com', 'deloitte.com'
            ]
        )
        
        return await self.execute_deep_research(request)
    
    async def research_competition(self, segment: str, competitors: List[str]) -> Dict[str, Any]:
        """Pesquisa específica de concorrência"""
        
        competitor_query = f"análise concorrentes {segment} " + " ".join(competitors)
        
        request = ResearchRequest(
            query=competitor_query,
            depth_level=3,
            max_sources=20,
            language="pt-BR"
        )
        
        return await self.execute_deep_research(request)
    
    def get_client_status(self) -> Dict[str, Any]:
        """Verifica status do cliente"""
        
        return {
            'service_name': 'DeepResearchMCP',
            'base_url': self.base_url,
            'api_key_configured': bool(self.api_key),
            'available': bool(self.base_url and self.api_key),
            'timeout': self.timeout,
            'version': '1.0'
        }
