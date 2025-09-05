#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ARQV30 Enhanced v2.0 - Component Orchestrator
Orquestrador seguro de componentes com validação rigorosa
"""

import logging
import time
import json
from typing import Dict, List, Any, Optional, Callable
from datetime import datetime

logger = logging.getLogger(__name__)

class ComponentValidationError(Exception):
    """Exceção para erros de validação de componentes"""
    pass

class ComponentOrchestrator:
    """Orquestrador seguro de componentes da análise"""

    def __init__(self):
        """Inicializa o orquestrador"""
        self.component_registry = {}
        self.execution_order = []
        self.validation_rules = {}
        self.component_results = {}
        self.execution_stats = {}

        logger.info("Component Orchestrator inicializado")

    def register_component(
        self, 
        name: str, 
        executor: Callable,
        dependencies: List[str] = None,
        validation_rules: Dict[str, Any] = None,
        required: bool = True
    ):
        """Registra um componente no orquestrador"""

        self.component_registry[name] = {
            'executor': executor,
            'dependencies': dependencies or [],
            'validation_rules': validation_rules or {},
            'required': required,
            'status': 'pending'
        }

        if name not in self.execution_order:
            self.execution_order.append(name)

        logger.info(f"📝 Componente registrado: {name}")

    def execute_components(
        self, 
        input_data: Dict[str, Any],
        progress_callback: Optional[Callable] = None
    ) -> Dict[str, Any]:
        """Executa todos os componentes registrados em ordem"""

        logger.info(f"🚀 Iniciando execução de {len(self.component_registry)} componentes")
        start_time = time.time()

        successful_components = {}
        failed_components = {}

        for i, component_name in enumerate(self.execution_order):
            if progress_callback:
                progress_callback(i + 1, f"Executando {component_name}...")

            try:
                # Verifica dependências
                if not self._check_dependencies(component_name):
                    error_msg = f"Dependências não atendidas para {component_name}"
                    logger.error(f"❌ {error_msg}")
                    failed_components[component_name] = error_msg
                    self._mark_component_failed(component_name, error_msg)
                    continue

                # Executa componente
                result = self._execute_single_component(component_name, input_data, successful_components)

                # Verifica se houve erro no resultado
                if result is not None and not isinstance(result, dict) or not result.get('error'):
                    # Valida resultado
                    if self._validate_component_result(component_name, result):
                        successful_components[component_name] = result
                        self._mark_component_successful(component_name, result)
                        logger.info(f"✅ Componente {component_name} executado com sucesso")
                    else:
                        error_msg = f"Resultado inválido para {component_name}"
                        logger.error(f"❌ {error_msg}")
                        failed_components[component_name] = error_msg
                        self._mark_component_failed(component_name, error_msg)
                elif result and isinstance(result, dict) and result.get('error'):
                    # Componente retornou com erro explícito
                    error_msg = f"Componente {component_name} falhou: {result.get('error')}"
                    logger.error(f"❌ {error_msg}")
                    failed_components[component_name] = error_msg
                    self._mark_component_failed(component_name, error_msg)
                else:
                    error_msg = f"Componente {component_name} retornou None ou resultado inválido"
                    logger.error(f"❌ {error_msg}")
                    failed_components[component_name] = error_msg
                    self._mark_component_failed(component_name, error_msg)

            except Exception as e:
                error_msg = f"Erro na execução de {component_name}: {str(e)}"
                logger.error(f"❌ {error_msg}")
                failed_components[component_name] = error_msg
                self._mark_component_failed(component_name, error_msg)

                # Se é componente obrigatório, pode interromper
                if self.component_registry[component_name]['required']:
                    logger.error(f"🚨 Componente obrigatório {component_name} falhou - análise comprometida")

        execution_time = time.time() - start_time

        # Gera relatório final
        execution_report = {
            'successful_components': successful_components,
            'failed_components': failed_components,
            'execution_stats': {
                'total_components': len(self.component_registry),
                'successful_count': len(successful_components),
                'failed_count': len(failed_components),
                'success_rate': (len(successful_components) / len(self.component_registry)) * 100,
                'execution_time': execution_time,
                'timestamp': datetime.now().isoformat()
            },
            'component_details': self.execution_stats
        }

        logger.info(f"📊 Execução concluída: {len(successful_components)}/{len(self.component_registry)} componentes bem-sucedidos")

        return execution_report

    def _check_dependencies(self, component_name: str) -> bool:
        """Verifica se as dependências de um componente foram atendidas"""

        component = self.component_registry.get(component_name, {})
        dependencies = component.get('dependencies', [])

        for dependency in dependencies:
            if dependency not in self.component_results or self.component_results[dependency]['status'] != 'success':
                logger.warning(f"⚠️ Dependência {dependency} não atendida para {component_name}")
                return False

        return True

    def _execute_single_component(
        self, 
        component_name: str, 
        input_data: Dict[str, Any],
        previous_results: Dict[str, Any]
    ) -> Any:
        """Executa um único componente"""

        component = self.component_registry[component_name]
        executor = component['executor']

        start_time = time.time()

        try:
            # Prepara dados de entrada incluindo resultados anteriores
            execution_data = {
                **input_data,
                'previous_results': previous_results
            }

            # Executa o componente
            result = executor(execution_data)

            execution_time = time.time() - start_time

            # Registra estatísticas
            self.execution_stats[component_name] = {
                'execution_time': execution_time,
                'status': 'success',
                'result_size': len(str(result)) if result else 0
            }

            return result

        except Exception as e:
            execution_time = time.time() - start_time

            self.execution_stats[component_name] = {
                'execution_time': execution_time,
                'status': 'failed',
                'error': str(e)
            }

            raise e

    def _validate_component_result(self, component_name: str, result: Any) -> bool:
        """Valida o resultado de um componente"""

        component = self.component_registry.get(component_name, {})
        validation_rules = component.get('validation_rules', {})

        if not validation_rules:
            # Se não há regras específicas, valida se não é None/vazio
            return result is not None

        try:
            # Valida tipo
            expected_type = validation_rules.get('type')
            if expected_type and not isinstance(result, expected_type):
                logger.error(f"❌ Tipo inválido para {component_name}: esperado {expected_type}, recebido {type(result)}")
                return False

            # Valida campos obrigatórios
            required_fields = validation_rules.get('required_fields', [])
            if isinstance(result, dict):
                for field in required_fields:
                    if field not in result or not result[field]:
                        logger.error(f"❌ Campo obrigatório ausente em {component_name}: {field}")
                        return False

            # Valida tamanho mínimo
            min_size = validation_rules.get('min_size')
            if min_size:
                if isinstance(result, (list, dict, str)):
                    if len(result) < min_size:
                        logger.error(f"❌ Tamanho insuficiente para {component_name}: {len(result)} < {min_size}")
                        return False

            # Valida se há erros explícitos no resultado
            if isinstance(result, dict) and result.get('error'):
                logger.error(f"❌ Erro detectado no resultado de {component_name}: {result.get('error')}")
                return False

            # Verifica se conteúdo não é fallback/genérico
            if isinstance(result, dict):
                result_str = json.dumps(result, ensure_ascii=False).lower()

                # Indicadores de conteúdo falso/genérico
                fallback_indicators = [
                    'em desenvolvimento', 'fallback', 'não disponível', 'erro na',
                    'driver 1', 'driver 2', 'customizado para', 'baseado em',
                    'específico para', 'dados não disponíveis', 'análise em desenvolvimento',
                    'erro na geração', 'unknown field'
                ]

                found_fallback = [indicator for indicator in fallback_indicators if indicator in result_str]

                if found_fallback:
                    logger.warning(f"⚠️ Conteúdo genérico/fallback detectado em {component_name}: {found_fallback}")
                    # Para avatar_detalhado, permite conteúdo com erro mas registra warning
                    if component_name == 'avatar_detalhado':
                        return True  # Permite continuar mas marca como warning
                    return False

                # Verifica se tem estrutura mínima de dados reais
                if component_name == 'mental_drivers':
                    drivers = result.get('drivers', [])
                    if not drivers or len(drivers) < 19:
                        logger.error(f"❌ {component_name}: drivers insuficientes ({len(drivers) if drivers else 0}/19)")
                        return False

                    # Verifica se drivers têm conteúdo real
                    generic_drivers = sum(1 for d in drivers if 'em desenvolvimento' in str(d).lower())
                    if generic_drivers > 5:  # Máximo 5 drivers genéricos permitidos
                        logger.error(f"❌ {component_name}: muitos drivers genéricos ({generic_drivers}/19)")
                        return False

            return True

        except Exception as e:
            logger.error(f"❌ Erro na validação de {component_name}: {str(e)}")
            return False

    def _mark_component_successful(self, component_name: str, result: Any):
        """Marca componente como bem-sucedido"""
        self.component_results[component_name] = {
            'status': 'success',
            'result': result,
            'timestamp': time.time()
        }

        self.component_registry[component_name]['status'] = 'success'

    def _mark_component_failed(self, component_name: str, error: str):
        """Marca componente como falho"""
        self.component_results[component_name] = {
            'status': 'failed',
            'error': error,
            'timestamp': time.time()
        }

        self.component_registry[component_name]['status'] = 'failed'

    def get_execution_summary(self) -> Dict[str, Any]:
        """Retorna resumo da execução"""

        successful = [name for name, result in self.component_results.items() if result['status'] == 'success']
        failed = [name for name, result in self.component_results.items() if result['status'] == 'failed']

        return {
            'total_components': len(self.component_registry),
            'successful_components': successful,
            'failed_components': failed,
            'success_rate': (len(successful) / len(self.component_registry)) * 100 if self.component_registry else 0,
            'execution_stats': self.execution_stats,
            'component_results': {name: result['result'] for name, result in self.component_results.items() if result['status'] == 'success'}
        }

    def reset(self):
        """Reseta o estado do orquestrador"""
        self.component_results = {}
        self.execution_stats = {}

        for component in self.component_registry.values():
            component['status'] = 'pending'

        logger.info("🔄 Orquestrador resetado")

# Instância global
component_orchestrator = ComponentOrchestrator()