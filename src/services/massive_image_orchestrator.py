#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ARQV30 Enhanced v3.0 - Orquestrador Massivo de Extração de Imagens
Sistema ultra-robusto com rotatividade de APIs e extração massiva de redes sociais
"""

import os
import logging
import asyncio
import time
import json
from typing import Dict, List, Any, Optional
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

# Importar todos os extratores
from services.firecrawl_image_extractor import firecrawl_image_extractor
from services.tavily_image_extractor import tavily_image_extractor
from services.supadata_image_extractor import supadata_image_extractor
from services.playwright_image_extractor import playwright_image_extractor
from services.real_viral_image_extractor import real_viral_image_extractor
from services.viral_image_extractor import viral_image_extractor

from services.enhanced_api_rotation_manager import api_rotation_manager
from services.auto_save_manager import salvar_etapa, salvar_erro

logger = logging.getLogger(__name__)

class MassiveImageOrchestrator:
    """Orquestrador massivo para extração de imagens com rotatividade de APIs"""
    
    def __init__(self):
        self.extractors = {
            'firecrawl': firecrawl_image_extractor,
            'tavily': tavily_image_extractor,
            'supadata': supadata_image_extractor,
            'playwright': playwright_image_extractor,
            'real_viral': real_viral_image_extractor,
            'viral_basic': viral_image_extractor
        }
        
        self.session_dir = "extracted_images"
        self.max_concurrent_extractors = 3
        self.images_per_extractor = 20
        self.total_target_images = 100
        
        os.makedirs(self.session_dir, exist_ok=True)
        logger.info("🚀 Massive Image Orchestrator inicializado com 6 extratores")

    async def extract_massive_social_images(self, query: str, session_id: str) -> Dict[str, Any]:
        """Extração massiva de imagens com rotatividade de APIs"""
        logger.info(f"🚀 INICIANDO EXTRAÇÃO MASSIVA DE IMAGENS para: {query}")
        
        start_time = time.time()
        
        # Estrutura do resultado gigante
        massive_results = {
            'session_id': session_id,
            'query': query,
            'extraction_started_at': datetime.now().isoformat(),
            'extraction_completed_at': None,
            'total_execution_time': 0,
            'extractors_used': [],
            'api_rotation_stats': {},
            'platforms': {
                'instagram': {'images': [], 'count': 0, 'extractors': []},
                'youtube': {'images': [], 'count': 0, 'extractors': []},
                'facebook': {'images': [], 'count': 0, 'extractors': []},
                'tiktok': {'images': [], 'count': 0, 'extractors': []},
                'twitter': {'images': [], 'count': 0, 'extractors': []},
                'linkedin': {'images': [], 'count': 0, 'extractors': []}
            },
            'extraction_results': {},
            'total_images_extracted': 0,
            'success_rate': 0.0,
            'errors': [],
            'performance_metrics': {
                'fastest_extractor': None,
                'slowest_extractor': None,
                'most_productive_extractor': None,
                'api_failures': 0,
                'successful_extractions': 0
            }
        }
        
        # Salvar início da extração
        await self._save_extraction_progress(massive_results, session_id, "iniciado")
        
        try:
            # FASE 1: Extração simultânea com todos os extratores
            logger.info("🔥 FASE 1: Extração simultânea com rotatividade de APIs")
            
            extraction_tasks = []
            
            # Criar tasks para cada extrator
            for extractor_name, extractor in self.extractors.items():
                if hasattr(extractor, 'extract_social_images'):
                    task = asyncio.create_task(
                        self._extract_with_timeout(extractor, query, session_id, extractor_name)
                    )
                    extraction_tasks.append(task)
                    massive_results['extractors_used'].append(extractor_name)
            
            # Executar extrações em paralelo
            logger.info(f"🚀 Executando {len(extraction_tasks)} extratores simultaneamente")
            
            completed_extractions = await asyncio.gather(*extraction_tasks, return_exceptions=True)
            
            # FASE 2: Processar resultados de cada extrator
            logger.info("📊 FASE 2: Processando resultados dos extratores")
            
            for i, result in enumerate(completed_extractions):
                extractor_name = massive_results['extractors_used'][i]
                
                if isinstance(result, Exception):
                    logger.error(f"❌ Erro no extrator {extractor_name}: {result}")
                    massive_results['errors'].append({
                        'extractor': extractor_name,
                        'error': str(result),
                        'timestamp': datetime.now().isoformat()
                    })
                    massive_results['extraction_results'][extractor_name] = {
                        'status': 'error',
                        'error': str(result),
                        'images_extracted': 0
                    }
                else:
                    # Processar resultado bem-sucedido
                    await self._process_extractor_result(result, extractor_name, massive_results)
            
            # FASE 3: Consolidação e métricas finais
            logger.info("🎯 FASE 3: Consolidação e cálculo de métricas")
            
            await self._calculate_final_metrics(massive_results, start_time)
            
            # FASE 4: Salvar JSON gigante final
            logger.info("💾 FASE 4: Salvando JSON gigante final")
            
            await self._save_massive_json(massive_results, session_id)
            
            logger.info(f"✅ EXTRAÇÃO MASSIVA CONCLUÍDA: {massive_results['total_images_extracted']} imagens em {massive_results['total_execution_time']:.2f}s")
            
        except Exception as e:
            logger.error(f"❌ Erro crítico na extração massiva: {e}")
            massive_results['errors'].append({
                'type': 'critical_error',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            })
            
            # Salvar erro
            await salvar_erro(f"massive_extraction_error_{session_id}", {
                'error': str(e),
                'session_id': session_id,
                'query': query
            })
        
        return massive_results

    async def _extract_with_timeout(self, extractor, query: str, session_id: str, extractor_name: str, timeout: int = 120) -> Dict[str, Any]:
        """Executa extração com timeout"""
        logger.info(f"🔄 Iniciando extração com {extractor_name}")
        
        start_time = time.time()
        
        try:
            # Executar extração com timeout
            result = await asyncio.wait_for(
                extractor.extract_social_images(query, session_id),
                timeout=timeout
            )
            
            execution_time = time.time() - start_time
            
            # Adicionar métricas de performance
            result['extractor_name'] = extractor_name
            result['execution_time'] = execution_time
            result['timeout_used'] = timeout
            result['status'] = 'completed'
            
            logger.info(f"✅ {extractor_name} concluído em {execution_time:.2f}s")
            
            return result
            
        except asyncio.TimeoutError:
            logger.warning(f"⏰ {extractor_name} timeout após {timeout}s")
            return {
                'extractor_name': extractor_name,
                'status': 'timeout',
                'execution_time': timeout,
                'error': f'Timeout após {timeout}s',
                'total_images': 0
            }
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"❌ {extractor_name} erro: {e}")
            return {
                'extractor_name': extractor_name,
                'status': 'error',
                'execution_time': execution_time,
                'error': str(e),
                'total_images': 0
            }

    async def _process_extractor_result(self, result: Dict[str, Any], extractor_name: str, massive_results: Dict[str, Any]):
        """Processa resultado de um extrator"""
        logger.info(f"📊 Processando resultado do {extractor_name}")
        
        try:
            # Adicionar resultado do extrator
            massive_results['extraction_results'][extractor_name] = result
            
            # Processar imagens por plataforma
            if 'platforms' in result:
                for platform_name, platform_data in result['platforms'].items():
                    if platform_name in massive_results['platforms']:
                        # Adicionar imagens da plataforma
                        if 'images' in platform_data:
                            for image in platform_data['images']:
                                # Adicionar metadados do extrator
                                image['extracted_by'] = extractor_name
                                image['extraction_timestamp'] = datetime.now().isoformat()
                                
                                massive_results['platforms'][platform_name]['images'].append(image)
                        
                        # Atualizar contadores
                        massive_results['platforms'][platform_name]['count'] = len(
                            massive_results['platforms'][platform_name]['images']
                        )
                        
                        # Adicionar extrator à lista
                        if extractor_name not in massive_results['platforms'][platform_name]['extractors']:
                            massive_results['platforms'][platform_name]['extractors'].append(extractor_name)
            
            # Atualizar contador total
            total_images = sum(
                platform['count'] for platform in massive_results['platforms'].values()
            )
            massive_results['total_images_extracted'] = total_images
            
            logger.info(f"✅ {extractor_name}: {result.get('total_images', 0)} imagens processadas")
            
        except Exception as e:
            logger.error(f"❌ Erro ao processar resultado do {extractor_name}: {e}")
            massive_results['errors'].append({
                'extractor': extractor_name,
                'error': f'Erro no processamento: {str(e)}',
                'timestamp': datetime.now().isoformat()
            })

    async def _calculate_final_metrics(self, massive_results: Dict[str, Any], start_time: float):
        """Calcula métricas finais da extração"""
        logger.info("📈 Calculando métricas finais")
        
        try:
            # Tempo total
            total_time = time.time() - start_time
            massive_results['total_execution_time'] = total_time
            massive_results['extraction_completed_at'] = datetime.now().isoformat()
            
            # Métricas de performance por extrator
            extractor_performances = []
            successful_extractions = 0
            
            for extractor_name, result in massive_results['extraction_results'].items():
                if result.get('status') == 'completed':
                    successful_extractions += 1
                    
                    performance = {
                        'extractor': extractor_name,
                        'execution_time': result.get('execution_time', 0),
                        'images_extracted': result.get('total_images', 0),
                        'images_per_second': result.get('total_images', 0) / max(result.get('execution_time', 1), 1)
                    }
                    extractor_performances.append(performance)
            
            # Encontrar melhor e pior performance
            if extractor_performances:
                fastest = min(extractor_performances, key=lambda x: x['execution_time'])
                slowest = max(extractor_performances, key=lambda x: x['execution_time'])
                most_productive = max(extractor_performances, key=lambda x: x['images_extracted'])
                
                massive_results['performance_metrics'].update({
                    'fastest_extractor': fastest,
                    'slowest_extractor': slowest,
                    'most_productive_extractor': most_productive,
                    'successful_extractions': successful_extractions,
                    'api_failures': len(massive_results['extractors_used']) - successful_extractions
                })
            
            # Taxa de sucesso
            if massive_results['extractors_used']:
                massive_results['success_rate'] = successful_extractions / len(massive_results['extractors_used'])
            
            # Estatísticas de APIs
            try:
                massive_results['api_rotation_stats'] = api_rotation_manager.get_usage_stats()
            except AttributeError:
                massive_results['api_rotation_stats'] = {'note': 'Stats não disponíveis'}
            
            logger.info(f"📊 Métricas calculadas: {massive_results['total_images_extracted']} imagens, {successful_extractions}/{len(massive_results['extractors_used'])} extratores bem-sucedidos")
            
        except Exception as e:
            logger.error(f"❌ Erro ao calcular métricas: {e}")

    async def _save_massive_json(self, massive_results: Dict[str, Any], session_id: str):
        """Salva o JSON gigante final"""
        try:
            # Diretório da sessão
            session_dir = os.path.join("analyses_data", session_id)
            os.makedirs(session_dir, exist_ok=True)
            
            # Nome do arquivo com timestamp
            timestamp = int(time.time())
            filename = f"massive_image_extraction_{session_id}_{timestamp}.json"
            filepath = os.path.join(session_dir, filename)
            
            # Salvar JSON gigante
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(massive_results, f, indent=2, ensure_ascii=False)
            
            # Calcular tamanho do arquivo
            file_size = os.path.getsize(filepath)
            file_size_mb = file_size / (1024 * 1024)
            
            logger.info(f"💾 JSON GIGANTE salvo: {filepath} ({file_size_mb:.2f} MB)")
            
            # Salvar também uma versão compacta
            compact_filename = f"massive_image_extraction_compact_{session_id}_{timestamp}.json"
            compact_filepath = os.path.join(session_dir, compact_filename)
            
            with open(compact_filepath, 'w', encoding='utf-8') as f:
                json.dump(massive_results, f, separators=(',', ':'), ensure_ascii=False)
            
            # Salvar etapa
            await salvar_etapa(f"massive_extraction_completed_{session_id}", {
                'json_file': filepath,
                'compact_file': compact_filepath,
                'file_size_mb': file_size_mb,
                'total_images': massive_results['total_images_extracted'],
                'execution_time': massive_results['total_execution_time']
            })
            
        except Exception as e:
            logger.error(f"❌ Erro ao salvar JSON gigante: {e}")

    async def _save_extraction_progress(self, results: Dict[str, Any], session_id: str, stage: str):
        """Salva progresso da extração"""
        try:
            await salvar_etapa(f"massive_extraction_{stage}_{session_id}", {
                'stage': stage,
                'session_id': session_id,
                'query': results.get('query', ''),
                'extractors_used': results.get('extractors_used', []),
                'timestamp': datetime.now().isoformat()
            })
        except Exception as e:
            logger.error(f"❌ Erro ao salvar progresso: {e}")

    def get_extraction_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas dos extratores"""
        try:
            api_stats = api_rotation_manager.get_usage_stats()
        except AttributeError:
            api_stats = {'note': 'Stats não disponíveis'}
        
        return {
            'available_extractors': list(self.extractors.keys()),
            'max_concurrent': self.max_concurrent_extractors,
            'images_per_extractor': self.images_per_extractor,
            'total_target': self.total_target_images,
            'api_stats': api_stats
        }

# Instância global
massive_image_orchestrator = MassiveImageOrchestrator()