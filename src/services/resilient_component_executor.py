#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ARQV30 Enhanced v2.0 - Resilient Component Executor
Executor resiliente que isola falhas e preserva dados
"""

import time
import logging
from typing import Dict, List, Any, Optional, Callable
from datetime import datetime
from services.auto_save_manager import auto_save_manager, salvar_etapa, salvar_erro

logger = logging.getLogger(__name__)

class ResilientComponentExecutor:
    """Executor resiliente de componentes com isolamento de falhas"""

    def __init__(self):
        """Inicializa o executor resiliente"""
        self.componentes_registrados = {}
        self.ordem_execucao = []
        self.resultados_componentes = {}
        self.estatisticas_execucao = {}

        logger.info("Resilient Component Executor inicializado")

    def registrar_componente(
        self, 
        nome: str, 
        executor: Callable,
        fallback: Optional[Callable] = None,
        obrigatorio: bool = False,
        timeout: int = 300,
        dependencias: List[str] = None
    ):
        """Registra um componente no executor"""

        self.componentes_registrados[nome] = {
            'executor': executor,
            'fallback': fallback,
            'obrigatorio': obrigatorio,
            'timeout': timeout,
            'dependencias': dependencias or [],
            'status': 'pendente'
        }

        if nome not in self.ordem_execucao:
            self.ordem_execucao.append(nome)

        logger.info(f"📝 Componente registrado: {nome}")

    def executar_pipeline_resiliente(
        self, 
        dados_entrada: Dict[str, Any],
        session_id: str = None,
        progress_callback: Optional[Callable] = None
    ) -> Dict[str, Any]:
        """Executa pipeline resiliente com isolamento de falhas"""

        logger.info(f"🚀 Iniciando pipeline resiliente com {len(self.componentes_registrados)} componentes")

        # Inicia sessão se não fornecida
        if not session_id:
            session_id = auto_save_manager.iniciar_sessao()

        # Salva início do pipeline
        salvar_etapa("pipeline_iniciado", {
            "componentes": list(self.componentes_registrados.keys()),
            "dados_entrada": dados_entrada,
            "session_id": session_id
        }, categoria="analise_completa")

        dados_acumulados = dados_entrada.copy()
        componentes_sucesso = []
        componentes_falha = []

        for i, nome_componente in enumerate(self.ordem_execucao):
            if progress_callback:
                progress_callback(i + 1, f"Executando {nome_componente}...")

            try:
                # Verifica dependências
                if not self._verificar_dependencias(nome_componente, componentes_sucesso):
                    logger.warning(f"⚠️ Dependências não atendidas para {nome_componente}")
                    componentes_falha.append(nome_componente)
                    continue

                # Executa componente com isolamento
                resultado = self._executar_componente_isolado(nome_componente, dados_acumulados)

                if resultado is not None:
                    # Sucesso - adiciona aos dados acumulados
                    dados_acumulados[nome_componente] = resultado
                    componentes_sucesso.append(nome_componente)

                    # Salva resultado imediatamente
                    salvar_etapa(f"componente_{nome_componente}", resultado, categoria="analise_completa")

                    logger.info(f"✅ Componente {nome_componente} executado com sucesso")
                else:
                    # Falha - tenta fallback
                    resultado_fallback = self._executar_fallback(nome_componente, dados_acumulados)

                    if resultado_fallback:
                        dados_acumulados[nome_componente] = resultado_fallback
                        componentes_sucesso.append(nome_componente)

                        # Salva fallback
                        salvar_etapa(f"fallback_{nome_componente}", resultado_fallback, categoria="analise_completa")

                        logger.info(f"🔄 Fallback de {nome_componente} executado com sucesso")
                    else:
                        componentes_falha.append(nome_componente)
                        logger.error(f"❌ Componente {nome_componente} falhou completamente")

            except Exception as e:
                logger.error(f"❌ Erro crítico em {nome_componente}: {str(e)}")
                salvar_erro(f"componente_{nome_componente}", e, contexto=dados_entrada)

                # Tenta fallback mesmo com erro crítico
                try:
                    resultado_fallback = self._executar_fallback(nome_componente, dados_acumulados)
                    if resultado_fallback:
                        dados_acumulados[nome_componente] = resultado_fallback
                        componentes_sucesso.append(nome_componente)
                        logger.info(f"🔄 Fallback de emergência para {nome_componente} funcionou")
                    else:
                        componentes_falha.append(nome_componente)
                except Exception as fallback_error:
                    logger.error(f"❌ Fallback de {nome_componente} também falhou: {fallback_error}")
                    componentes_falha.append(nome_componente)

        # Calcula estatísticas
        total_componentes = len(self.componentes_registrados)
        sucessos = len(componentes_sucesso)
        falhas = len(componentes_falha)
        taxa_sucesso = (sucessos / total_componentes) * 100 if total_componentes > 0 else 0

        # Resultado do pipeline
        resultado_pipeline = {
            'session_id': session_id,
            'analysis_id': auto_save_manager.analysis_id,
            'dados_gerados': {k: v for k, v in dados_acumulados.items() if k != 'dados_entrada'},
            'componentes_sucesso': componentes_sucesso,
            'componentes_falha': componentes_falha,
            'estatisticas': {
                'total_componentes': total_componentes,
                'componentes_executados': sucessos,
                'componentes_falharam': falhas,
                'taxa_sucesso': taxa_sucesso,
                'pipeline_completo': falhas == 0,
                'dados_preservados': sucessos > 0
            },
            'processamento': {
                'inicio': dados_entrada.get('start_time', time.time()),
                'fim': time.time(),
                'duracao': time.time() - dados_entrada.get('start_time', time.time())
            }
        }

        # Salva resultado final do pipeline
        salvar_etapa("pipeline_completo", resultado_pipeline, categoria="analise_completa")

        logger.info(f"📊 Pipeline concluído: {sucessos}/{total_componentes} sucessos ({taxa_sucesso:.1f}%)")

        return resultado_pipeline

    def _verificar_dependencias(self, nome_componente: str, componentes_sucesso: List[str]) -> bool:
        """Verifica se dependências do componente foram atendidas"""

        componente = self.componentes_registrados.get(nome_componente, {})
        dependencias = componente.get('dependencias', [])

        for dependencia in dependencias:
            if dependencia not in componentes_sucesso:
                return False

        return True

    def _executar_componente_isolado(self, nome_componente: str, dados: Dict[str, Any]) -> Any:
        """Executa componente com isolamento de falhas"""

        componente = self.componentes_registrados[nome_componente]
        executor = componente['executor']
        timeout = componente['timeout']

        try:
            # Em ambientes threading (como Flask), não usamos signal
            # Implementação alternativa sem signal

            result = executor(dados)

            return result

        except Exception as e:
            logger.error(f"❌ Erro isolado em {nome_componente}: {str(e)}")
            return None

    def _executar_fallback(self, nome_componente: str, dados: Dict[str, Any]) -> Any:
        """Executa fallback do componente"""

        componente = self.componentes_registrados.get(nome_componente, {})
        fallback = componente.get('fallback')

        if not fallback:
            return None

        try:
            logger.info(f"🔄 Executando fallback para {nome_componente}")
            resultado = fallback(dados)
            return resultado

        except Exception as e:
            logger.error(f"❌ Fallback de {nome_componente} falhou: {str(e)}")
            return None

    def get_execution_summary(self) -> Dict[str, Any]:
        """Retorna resumo da execução"""

        return {
            'componentes_registrados': list(self.componentes_registrados.keys()),
            'ordem_execucao': self.ordem_execucao,
            'resultados_disponiveis': list(self.resultados_componentes.keys()),
            'estatisticas': self.estatisticas_execucao
        }

    def reset(self):
        """Reseta estado do executor"""

        self.resultados_componentes = {}
        self.estatisticas_execucao = {}

        for componente in self.componentes_registrados.values():
            componente['status'] = 'pendente'

        logger.info("🔄 Executor resiliente resetado")

# Instância global
resilient_executor = ResilientComponentExecutor()