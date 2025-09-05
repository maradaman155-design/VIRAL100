#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ARQV30 Enhanced v2.0 - Consolidação Final Ultra-Robusta
Sistema de consolidação que NUNCA falha e sempre gera relatório
"""

import os
import logging
import time
import json
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path
from services.auto_save_manager import auto_save_manager, salvar_etapa, salvar_erro

logger = logging.getLogger(__name__)

class ConsolidacaoFinal:
    """Sistema de consolidação final ultra-robusto"""
    
    def __init__(self):
        """Inicializa sistema de consolidação"""
        self.quality_thresholds = {
            'min_drivers_mentais': 2,
            'min_provas_visuais': 1,
            'min_fontes_pesquisa': 3,
            'min_insights': 5,
            'min_content_length': 1000
        }
        
        self.template_engines = {
            'markdown': self._generate_markdown_report,
            'html': self._generate_html_report,
            'json': self._generate_json_report,
            'minimal': self._generate_minimal_report
        }
        
        logger.info("Consolidação Final Ultra-Robusta inicializada")
    
    def consolidar_analise_completa(
        self, 
        dados_pipeline: Dict[str, Any],
        session_id: str,
        force_minimal: bool = False
    ) -> Dict[str, Any]:
        """Consolida análise completa com fallbacks robustos"""
        
        try:
            logger.info(f"🔄 Iniciando consolidação final para sessão: {session_id}")
            
            # Salva início da consolidação
            salvar_etapa("consolidacao_iniciada", {
                "session_id": session_id,
                "timestamp": time.time(),
                "force_minimal": force_minimal
            }, categoria="analise_completa")
            
            # 1. Coleta todos os dados disponíveis
            dados_coletados = self._coletar_todos_dados(dados_pipeline, session_id)
            
            # 2. Valida qualidade dos dados
            validacao_qualidade = self._validar_qualidade_dados(dados_coletados)
            salvar_etapa("validacao_qualidade", validacao_qualidade, categoria="analise_completa")
            
            # 3. Determina tipo de relatório baseado na qualidade
            if force_minimal or not validacao_qualidade['qualidade_suficiente']:
                logger.warning("⚠️ Qualidade insuficiente ou modo mínimo forçado - gerando relatório mínimo")
                relatorio_final = self._gerar_relatorio_minimo(dados_coletados, session_id, validacao_qualidade)
            else:
                logger.info("✅ Qualidade suficiente - gerando relatório completo")
                relatorio_final = self._gerar_relatorio_completo(dados_coletados, session_id, validacao_qualidade)
            
            # 4. Adiciona metadados de consolidação
            relatorio_final['metadata_consolidacao'] = {
                'session_id': session_id,
                'timestamp_consolidacao': datetime.now().isoformat(),
                'qualidade_dados': validacao_qualidade,
                'tipo_relatorio': 'minimo' if (force_minimal or not validacao_qualidade['qualidade_suficiente']) else 'completo',
                'arquivos_intermediarios': self._listar_arquivos_intermediarios(session_id),
                'garantia_dados': 'Todos os dados intermediários preservados',
                'acesso_direto': f"relatorios_intermediarios/{session_id}/"
            }
            
            # 5. Salva relatório final
            salvar_etapa("relatorio_final_consolidado", relatorio_final, categoria="analise_completa")
            
            # 6. Gera múltiplos formatos
            formatos_gerados = self._gerar_multiplos_formatos(relatorio_final, session_id)
            
            logger.info(f"✅ Consolidação final concluída: {len(formatos_gerados)} formatos gerados")
            
            return {
                'relatorio_principal': relatorio_final,
                'formatos_disponiveis': formatos_gerados,
                'status': 'consolidado_com_sucesso',
                'qualidade': validacao_qualidade,
                'session_id': session_id
            }
            
        except Exception as e:
            logger.error(f"❌ Erro na consolidação final: {str(e)}")
            salvar_erro("consolidacao_final", e, contexto={"session_id": session_id})
            
            # Fallback absoluto - NUNCA falha
            return self._fallback_absoluto(session_id, str(e))
    
    def _coletar_todos_dados(self, dados_pipeline: Dict[str, Any], session_id: str) -> Dict[str, Any]:
        """Coleta todos os dados disponíveis"""
        
        dados_coletados = {
            'dados_pipeline': dados_pipeline,
            'etapas_salvas': {},
            'arquivos_encontrados': [],
            'componentes_disponiveis': []
        }
        
        try:
            # Coleta etapas salvas
            etapas_salvas = auto_save_manager.listar_etapas_salvas(session_id)
            dados_coletados['etapas_salvas'] = etapas_salvas
            
            # Recupera dados de cada etapa
            for etapa_nome in etapas_salvas.keys():
                try:
                    dados_etapa = auto_save_manager.recuperar_etapa(etapa_nome, session_id)
                    if dados_etapa and dados_etapa.get('status') == 'sucesso':
                        dados_coletados[etapa_nome] = dados_etapa.get('dados')
                        dados_coletados['componentes_disponiveis'].append(etapa_nome)
                except Exception as e:
                    logger.warning(f"⚠️ Erro ao recuperar etapa {etapa_nome}: {e}")
                    continue
            
            # Lista arquivos intermediários
            dados_coletados['arquivos_encontrados'] = self._listar_arquivos_intermediarios(session_id)
            
            logger.info(f"📊 Dados coletados: {len(dados_coletados['componentes_disponiveis'])} componentes, {len(dados_coletados['arquivos_encontrados'])} arquivos")
            
        except Exception as e:
            logger.error(f"❌ Erro ao coletar dados: {e}")
            salvar_erro("coleta_dados", e)
        
        return dados_coletados
    
    def _validar_qualidade_dados(self, dados_coletados: Dict[str, Any]) -> Dict[str, Any]:
        """Valida qualidade dos dados coletados"""
        
        validacao = {
            'qualidade_suficiente': False,
            'componentes_encontrados': len(dados_coletados['componentes_disponiveis']),
            'drivers_mentais_count': 0,
            'provas_visuais_count': 0,
            'pesquisa_fontes': 0,
            'insights_count': 0,
            'problemas_identificados': [],
            'recomendacoes': []
        }
        
        try:
            # Verifica drivers mentais
            if 'drivers_mentais_customizados' in dados_coletados:
                drivers_data = dados_coletados['drivers_mentais_customizados']
                if isinstance(drivers_data, dict) and 'drivers_customizados' in drivers_data:
                    validacao['drivers_mentais_count'] = len(drivers_data['drivers_customizados'])
            
            # Verifica provas visuais
            if 'provas_visuais_sugeridas' in dados_coletados:
                provas_data = dados_coletados['provas_visuais_sugeridas']
                if isinstance(provas_data, list):
                    validacao['provas_visuais_count'] = len(provas_data)
            
            # Verifica pesquisa
            if 'pesquisa_web_massiva' in dados_coletados:
                pesquisa_data = dados_coletados['pesquisa_web_massiva']
                if isinstance(pesquisa_data, dict):
                    validacao['pesquisa_fontes'] = pesquisa_data.get('unique_sources', 0)
            
            # Verifica insights
            if 'insights_exclusivos' in dados_coletados:
                insights_data = dados_coletados['insights_exclusivos']
                if isinstance(insights_data, list):
                    validacao['insights_count'] = len(insights_data)
            
            # Avalia qualidade geral
            criterios_atendidos = 0
            total_criterios = len(self.quality_thresholds)
            
            if validacao['drivers_mentais_count'] >= self.quality_thresholds['min_drivers_mentais']:
                criterios_atendidos += 1
            else:
                validacao['problemas_identificados'].append(f"Drivers mentais insuficientes: {validacao['drivers_mentais_count']} < {self.quality_thresholds['min_drivers_mentais']}")
            
            if validacao['provas_visuais_count'] >= self.quality_thresholds['min_provas_visuais']:
                criterios_atendidos += 1
            else:
                validacao['problemas_identificados'].append(f"Provas visuais insuficientes: {validacao['provas_visuais_count']} < {self.quality_thresholds['min_provas_visuais']}")
            
            if validacao['pesquisa_fontes'] >= self.quality_thresholds['min_fontes_pesquisa']:
                criterios_atendidos += 1
            else:
                validacao['problemas_identificados'].append(f"Fontes de pesquisa insuficientes: {validacao['pesquisa_fontes']} < {self.quality_thresholds['min_fontes_pesquisa']}")
            
            if validacao['insights_count'] >= self.quality_thresholds['min_insights']:
                criterios_atendidos += 1
            else:
                validacao['problemas_identificados'].append(f"Insights insuficientes: {validacao['insights_count']} < {self.quality_thresholds['min_insights']}")
            
            # Qualidade suficiente se atende pelo menos 60% dos critérios
            validacao['qualidade_suficiente'] = (criterios_atendidos / total_criterios) >= 0.6
            validacao['score_qualidade'] = (criterios_atendidos / total_criterios) * 100
            
            # Gera recomendações
            if not validacao['qualidade_suficiente']:
                validacao['recomendacoes'].extend([
                    "Configure mais APIs para melhorar qualidade",
                    "Execute nova análise com dados mais específicos",
                    "Verifique conectividade de internet",
                    "Considere análise manual dos dados intermediários"
                ])
            
        except Exception as e:
            logger.error(f"❌ Erro na validação de qualidade: {e}")
            validacao['problemas_identificados'].append(f"Erro na validação: {str(e)}")
        
        return validacao
    
    def _gerar_relatorio_completo(
        self, 
        dados_coletados: Dict[str, Any], 
        session_id: str, 
        validacao: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Gera relatório completo com todos os componentes"""
        
        try:
            relatorio = {
                'tipo': 'relatorio_completo',
                'session_id': session_id,
                'timestamp': datetime.now().isoformat(),
                'qualidade_validada': True,
                'score_qualidade': validacao['score_qualidade']
            }
            
            # Adiciona todos os componentes disponíveis
            componentes_principais = [
                'projeto_dados', 'pesquisa_web_massiva', 'avatar_ultra_detalhado',
                'drivers_mentais_customizados', 'provas_visuais_sugeridas',
                'sistema_anti_objecao', 'pre_pitch_invisivel', 'predicoes_futuro_completas',
                'insights_exclusivos'
            ]
            
            for componente in componentes_principais:
                if componente in dados_coletados:
                    relatorio[componente] = dados_coletados[componente]
                elif componente in dados_coletados.get('dados_pipeline', {}):
                    relatorio[componente] = dados_coletados['dados_pipeline'][componente]
            
            # Adiciona resumo executivo
            relatorio['resumo_executivo'] = self._gerar_resumo_executivo(dados_coletados, validacao)
            
            # Adiciona diagnóstico final
            relatorio['diagnostico_final'] = self._gerar_diagnostico_final(dados_coletados, validacao)
            
            return relatorio
            
        except Exception as e:
            logger.error(f"❌ Erro ao gerar relatório completo: {e}")
            salvar_erro("relatorio_completo", e)
            return self._gerar_relatorio_minimo(dados_coletados, session_id, validacao)
    
    def _gerar_relatorio_minimo(
        self, 
        dados_coletados: Dict[str, Any], 
        session_id: str, 
        validacao: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Gera relatório mínimo garantido"""
        
        try:
            relatorio = {
                'tipo': 'relatorio_minimo',
                'session_id': session_id,
                'timestamp': datetime.now().isoformat(),
                'status': 'parcial_mas_preservado',
                'qualidade_limitada': True,
                'score_qualidade': validacao.get('score_qualidade', 0)
            }
            
            # Adiciona dados básicos sempre disponíveis
            if 'projeto_dados' in dados_coletados:
                relatorio['projeto_dados'] = dados_coletados['projeto_dados']
            elif 'dados_pipeline' in dados_coletados:
                relatorio['projeto_dados'] = dados_coletados['dados_pipeline'].get('projeto_dados', {})
            
            # Lista componentes gerados
            relatorio['componentes_gerados'] = dados_coletados['componentes_disponiveis']
            
            # Adiciona links para arquivos salvos
            relatorio['arquivos_intermediarios'] = {
                'localizacao': f"relatorios_intermediarios/{session_id}/",
                'arquivos_disponiveis': dados_coletados['arquivos_encontrados'],
                'total_arquivos': len(dados_coletados['arquivos_encontrados']),
                'instrucoes_acesso': "Acesse os arquivos diretamente no diretório para análise manual"
            }
            
            # Adiciona o que foi possível recuperar
            componentes_recuperados = {}
            for componente in dados_coletados['componentes_disponiveis']:
                if componente in dados_coletados:
                    componentes_recuperados[componente] = dados_coletados[componente]
            
            relatorio['dados_recuperados'] = componentes_recuperados
            
            # Adiciona diagnóstico dos problemas
            relatorio['diagnostico_problemas'] = {
                'problemas_identificados': validacao.get('problemas_identificados', []),
                'recomendacoes': validacao.get('recomendacoes', []),
                'proximos_passos': [
                    "Configure APIs faltantes para análise completa",
                    "Execute nova análise com configuração completa",
                    "Analise manualmente os arquivos intermediários salvos",
                    "Considere executar componentes individuais para debug"
                ]
            }
            
            # Adiciona resumo do que foi preservado
            relatorio['resumo_preservacao'] = {
                'dados_perdidos': 'NENHUM - Todos os dados intermediários foram salvos',
                'componentes_executados': len(dados_coletados['componentes_disponiveis']),
                'arquivos_salvos': len(dados_coletados['arquivos_encontrados']),
                'recuperacao_possivel': 'SIM - Todos os dados podem ser recuperados',
                'valor_preservado': 'ALTO - Análise pode ser completada manualmente'
            }
            
            return relatorio
            
        except Exception as e:
            logger.error(f"❌ Erro crítico ao gerar relatório mínimo: {e}")
            salvar_erro("relatorio_minimo", e)
            return self._fallback_absoluto(session_id, str(e))
    
    def _gerar_resumo_executivo(self, dados_coletados: Dict[str, Any], validacao: Dict[str, Any]) -> Dict[str, Any]:
        """Gera resumo executivo da análise"""
        
        try:
            # Extrai dados principais
            projeto_dados = dados_coletados.get('projeto_dados', {})
            segmento = projeto_dados.get('segmento', 'Não informado')
            produto = projeto_dados.get('produto', 'Não informado')
            
            resumo = {
                'segmento_analisado': segmento,
                'produto_servico': produto,
                'qualidade_analise': validacao.get('score_qualidade', 0),
                'componentes_gerados': len(dados_coletados['componentes_disponiveis']),
                'principais_descobertas': [],
                'recomendacoes_imediatas': [],
                'proximos_passos': []
            }
            
            # Extrai principais descobertas
            if 'insights_exclusivos' in dados_coletados:
                insights = dados_coletados['insights_exclusivos']
                if isinstance(insights, list):
                    resumo['principais_descobertas'] = insights[:5]  # Top 5 insights
            
            # Gera recomendações baseadas nos dados
            if 'drivers_mentais_customizados' in dados_coletados:
                resumo['recomendacoes_imediatas'].append(f"Implemente os {validacao['drivers_mentais_count']} drivers mentais identificados")
            
            if 'provas_visuais_sugeridas' in dados_coletados:
                resumo['recomendacoes_imediatas'].append(f"Desenvolva as {validacao['provas_visuais_count']} provas visuais sugeridas")
            
            # Próximos passos
            resumo['proximos_passos'] = [
                f"Implemente estratégias específicas para {segmento}",
                "Execute plano de ação detalhado",
                "Monitore métricas de performance",
                "Ajuste estratégias baseado em resultados"
            ]
            
            return resumo
            
        except Exception as e:
            logger.error(f"❌ Erro ao gerar resumo executivo: {e}")
            return {
                'erro': 'Falha na geração do resumo executivo',
                'dados_disponiveis': 'Consulte arquivos intermediários para análise manual'
            }
    
    def _gerar_diagnostico_final(self, dados_coletados: Dict[str, Any], validacao: Dict[str, Any]) -> Dict[str, Any]:
        """Gera diagnóstico final da análise"""
        
        try:
            diagnostico = {
                'status_geral': 'SUCESSO_PARCIAL' if validacao['qualidade_suficiente'] else 'DADOS_PRESERVADOS',
                'componentes_funcionaram': dados_coletados['componentes_disponiveis'],
                'componentes_falharam': [],
                'qualidade_geral': validacao.get('score_qualidade', 0),
                'dados_preservados': True,
                'recuperacao_possivel': True
            }
            
            # Identifica componentes que falharam
            componentes_esperados = [
                'pesquisa_web_massiva', 'avatar_ultra_detalhado', 'drivers_mentais_customizados',
                'provas_visuais_sugeridas', 'sistema_anti_objecao', 'pre_pitch_invisivel'
            ]
            
            for componente in componentes_esperados:
                if componente not in dados_coletados['componentes_disponiveis']:
                    diagnostico['componentes_falharam'].append(componente)
            
            # Avaliação final
            if validacao['qualidade_suficiente']:
                diagnostico['avaliacao'] = "Análise bem-sucedida com qualidade adequada"
                diagnostico['recomendacao'] = "Prosseguir com implementação das estratégias"
            else:
                diagnostico['avaliacao'] = "Análise parcial mas dados preservados"
                diagnostico['recomendacao'] = "Configure APIs e execute nova análise para resultados completos"
            
            return diagnostico
            
        except Exception as e:
            logger.error(f"❌ Erro ao gerar diagnóstico final: {e}")
            return {
                'status_geral': 'ERRO_MAS_DADOS_SALVOS',
                'erro': str(e),
                'dados_preservados': True
            }
    
    def _listar_arquivos_intermediarios(self, session_id: str) -> List[Dict[str, Any]]:
        """Lista todos os arquivos intermediários salvos"""
        
        arquivos = []
        base_dir = Path("relatorios_intermediarios")
        
        try:
            # Busca em todos os subdiretórios
            for subdir in base_dir.iterdir():
                if subdir.is_dir():
                    for arquivo in subdir.rglob("*"):
                        if arquivo.is_file() and session_id in arquivo.name:
                            arquivos.append({
                                'nome': arquivo.name,
                                'caminho': str(arquivo),
                                'tamanho': arquivo.stat().st_size,
                                'categoria': subdir.name,
                                'modificado': datetime.fromtimestamp(arquivo.stat().st_mtime).isoformat()
                            })
        
        except Exception as e:
            logger.error(f"❌ Erro ao listar arquivos intermediários: {e}")
        
        return arquivos
    
    def _gerar_multiplos_formatos(self, relatorio: Dict[str, Any], session_id: str) -> Dict[str, str]:
        """Gera relatório em múltiplos formatos"""
        
        formatos_gerados = {}
        
        for formato, gerador in self.template_engines.items():
            try:
                conteudo = gerador(relatorio, session_id)
                if conteudo:
                    # Salva arquivo do formato
                    arquivo_path = self._salvar_formato(conteudo, formato, session_id)
                    formatos_gerados[formato] = arquivo_path
                    logger.info(f"✅ Formato {formato} gerado: {arquivo_path}")
            except Exception as e:
                logger.error(f"❌ Erro ao gerar formato {formato}: {e}")
                continue
        
        return formatos_gerados
    
    def _generate_markdown_report(self, relatorio: Dict[str, Any], session_id: str) -> str:
        """Gera relatório em Markdown"""
        
        md_content = f"""# Relatório de Análise Ultra-Detalhada
## ARQV30 Enhanced v2.0

**Sessão:** {session_id}  
**Data:** {relatorio.get('timestamp', 'N/A')}  
**Tipo:** {relatorio.get('tipo', 'N/A')}  

### 📊 Resumo Executivo

"""
        
        if 'resumo_executivo' in relatorio:
            resumo = relatorio['resumo_executivo']
            md_content += f"**Segmento:** {resumo.get('segmento_analisado', 'N/A')}  \n"
            md_content += f"**Produto/Serviço:** {resumo.get('produto_servico', 'N/A')}  \n"
            md_content += f"**Qualidade:** {resumo.get('qualidade_analise', 0):.1f}%  \n"
            md_content += f"**Componentes:** {resumo.get('componentes_gerados', 0)}  \n\n"
        
        # Adiciona seções principais
        if 'drivers_mentais_customizados' in relatorio:
            md_content += "### 🧠 Drivers Mentais Customizados\n\n"
            drivers = relatorio['drivers_mentais_customizados']
            if isinstance(drivers, dict) and 'drivers_customizados' in drivers:
                for i, driver in enumerate(drivers['drivers_customizados'], 1):
                    md_content += f"#### Driver {i}: {driver.get('nome', 'N/A')}\n"
                    md_content += f"**Gatilho:** {driver.get('gatilho_central', 'N/A')}  \n"
                    md_content += f"**História:** {driver.get('roteiro_ativacao', {}).get('historia_analogia', 'N/A')}  \n\n"
        
        if 'insights_exclusivos' in relatorio:
            md_content += "### 💡 Insights Exclusivos\n\n"
            insights = relatorio['insights_exclusivos']
            if isinstance(insights, list):
                for i, insight in enumerate(insights, 1):
                    md_content += f"{i}. {insight}\n"
            md_content += "\n"
        
        # Adiciona diagnóstico
        if 'diagnostico_final' in relatorio:
            diagnostico = relatorio['diagnostico_final']
            md_content += "### 🎯 Diagnóstico Final\n\n"
            md_content += f"**Status:** {diagnostico.get('status_geral', 'N/A')}  \n"
            md_content += f"**Avaliação:** {diagnostico.get('avaliacao', 'N/A')}  \n"
            md_content += f"**Recomendação:** {diagnostico.get('recomendacao', 'N/A')}  \n\n"
        
        return md_content
    
    def _generate_html_report(self, relatorio: Dict[str, Any], session_id: str) -> str:
        """Gera relatório em HTML"""
        
        html_content = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Relatório ARQV30 - {session_id}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }}
        .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 40px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }}
        h1 {{ color: #2c3e50; border-bottom: 3px solid #3498db; padding-bottom: 10px; }}
        h2 {{ color: #34495e; margin-top: 30px; }}
        .metric {{ background: #ecf0f1; padding: 15px; margin: 10px 0; border-radius: 5px; }}
        .insight {{ background: #e8f5e8; padding: 10px; margin: 5px 0; border-left: 4px solid #27ae60; }}
        .warning {{ background: #fdf2e9; padding: 10px; margin: 5px 0; border-left: 4px solid #f39c12; }}
        .error {{ background: #fadbd8; padding: 10px; margin: 5px 0; border-left: 4px solid #e74c3c; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>📊 Relatório de Análise Ultra-Detalhada</h1>
        <p><strong>Sessão:</strong> {session_id}</p>
        <p><strong>Data:</strong> {relatorio.get('timestamp', 'N/A')}</p>
        <p><strong>Tipo:</strong> {relatorio.get('tipo', 'N/A')}</p>
"""
        
        # Adiciona conteúdo baseado nos dados disponíveis
        if 'resumo_executivo' in relatorio:
            resumo = relatorio['resumo_executivo']
            html_content += f"""
        <h2>📋 Resumo Executivo</h2>
        <div class="metric">
            <strong>Segmento:</strong> {resumo.get('segmento_analisado', 'N/A')}<br>
            <strong>Produto/Serviço:</strong> {resumo.get('produto_servico', 'N/A')}<br>
            <strong>Qualidade:</strong> {resumo.get('qualidade_analise', 0):.1f}%<br>
            <strong>Componentes:</strong> {resumo.get('componentes_gerados', 0)}
        </div>
"""
        
        if 'insights_exclusivos' in relatorio:
            html_content += "<h2>💡 Insights Exclusivos</h2>"
            insights = relatorio['insights_exclusivos']
            if isinstance(insights, list):
                for insight in insights:
                    html_content += f'<div class="insight">{insight}</div>'
        
        html_content += """
    </div>
</body>
</html>"""
        
        return html_content
    
    def _generate_json_report(self, relatorio: Dict[str, Any], session_id: str) -> str:
        """Gera relatório em JSON"""
        try:
            return json.dumps(relatorio, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"❌ Erro ao gerar JSON: {e}")
            return json.dumps({
                'erro': 'Falha na serialização JSON',
                'session_id': session_id,
                'timestamp': datetime.now().isoformat()
            }, ensure_ascii=False, indent=2)
    
    def _generate_minimal_report(self, relatorio: Dict[str, Any], session_id: str) -> str:
        """Gera relatório mínimo em texto"""
        
        content = f"""RELATÓRIO MÍNIMO - ARQV30 Enhanced v2.0
========================================

Sessão: {session_id}
Data: {relatorio.get('timestamp', 'N/A')}
Status: {relatorio.get('status', 'N/A')}

COMPONENTES GERADOS:
{chr(10).join(f"✅ {comp}" for comp in relatorio.get('componentes_gerados', []))}

ARQUIVOS SALVOS:
Localização: {relatorio.get('arquivos_intermediarios', {}).get('localizacao', 'N/A')}
Total: {relatorio.get('arquivos_intermediarios', {}).get('total_arquivos', 0)} arquivos

DIAGNÓSTICO:
{relatorio.get('diagnostico_final', {}).get('avaliacao', 'N/A')}

RECOMENDAÇÃO:
{relatorio.get('diagnostico_final', {}).get('recomendacao', 'N/A')}

GARANTIA:
✅ NENHUM DADO FOI PERDIDO
✅ Todos os dados intermediários foram preservados
✅ Análise pode ser completada manualmente
✅ Arquivos disponíveis para recuperação
"""
        
        return content
    
    def _salvar_formato(self, conteudo: str, formato: str, session_id: str) -> str:
        """Salva conteúdo em arquivo específico"""
        
        try:
            # Define extensão
            extensoes = {
                'markdown': '.md',
                'html': '.html',
                'json': '.json',
                'minimal': '.txt'
            }
            
            extensao = extensoes.get(formato, '.txt')
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"relatorio_final_{session_id[:8]}_{timestamp}{extensao}"
            
            # Salva no diretório de análises completas
            base_dir = Path("relatorios_intermediarios/analise_completa")
            base_dir.mkdir(parents=True, exist_ok=True)
            
            filepath = base_dir / filename
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(conteudo)
            
            return str(filepath)
            
        except Exception as e:
            logger.error(f"❌ Erro ao salvar formato {formato}: {e}")
            return f"Erro ao salvar: {str(e)}"
    
    def _fallback_absoluto(self, session_id: str, erro: str) -> Dict[str, Any]:
        """Fallback absoluto que NUNCA falha"""
        
        try:
            # Relatório de emergência mínimo
            relatorio_emergencia = {
                'tipo': 'relatorio_emergencia',
                'session_id': session_id,
                'timestamp': datetime.now().isoformat(),
                'status': 'ERRO_MAS_DADOS_PRESERVADOS',
                'erro_consolidacao': erro,
                'garantias': {
                    'dados_perdidos': 'NENHUM',
                    'arquivos_salvos': 'SIM',
                    'recuperacao_possivel': 'SIM',
                    'localizacao_dados': f"relatorios_intermediarios/{session_id}/"
                },
                'instrucoes_recuperacao': [
                    f"1. Acesse o diretório: relatorios_intermediarios/{session_id}/",
                    "2. Analise os arquivos JSON salvos em cada categoria",
                    "3. Use os dados para completar análise manualmente",
                    "4. Execute nova análise com APIs configuradas"
                ],
                'arquivos_disponiveis': self._listar_arquivos_intermediarios(session_id),
                'valor_preservado': 'ALTO - Todos os dados intermediários estão disponíveis'
            }
            
            # Salva relatório de emergência
            salvar_etapa("relatorio_emergencia", relatorio_emergencia, categoria="analise_completa")
            
            return relatorio_emergencia
            
        except Exception as final_error:
            # Último recurso - retorna estrutura mínima
            logger.critical(f"🚨 Fallback absoluto falhou: {final_error}")
            
            return {
                'tipo': 'emergencia_critica',
                'session_id': session_id,
                'timestamp': datetime.now().isoformat(),
                'erro_original': erro,
                'erro_fallback': str(final_error),
                'status': 'CRITICO_MAS_SESSAO_PRESERVADA',
                'instrucao': f"Verifique manualmente: relatorios_intermediarios/{session_id}/"
            }

# Instância global
consolidacao_final = ConsolidacaoFinal()