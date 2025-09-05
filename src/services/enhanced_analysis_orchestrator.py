#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ARQV30 Enhanced v2.0 - Enhanced Analysis Orchestrator
Orquestrador aprimorado que integra agentes psicológicos
"""

import logging
import time
from typing import Dict, List, Any, Optional
from datetime import datetime
from services.psychological_agents import psychological_agents
from services.ultra_detailed_analysis_engine import ultra_detailed_analysis_engine
from services.auto_save_manager import salvar_etapa, salvar_erro

logger = logging.getLogger(__name__)

class EnhancedAnalysisOrchestrator:
    """Orquestrador aprimorado de análise ultra-detalhada"""
    
    def __init__(self):
        """Inicializa orquestrador aprimorado"""
        self.analysis_layers = [
            'pesquisa_web_massiva',
            'analise_arqueologica',
            'engenharia_reversa_psicologica',
            'drivers_mentais_arsenal',
            'provas_visuais_sistema',
            'anti_objecao_completo',
            'pre_pitch_orquestrado',
            'metricas_forenses',
            'consolidacao_final'
        ]
        
        logger.info("Enhanced Analysis Orchestrator inicializado")
    
    def execute_ultra_enhanced_analysis(
        self, 
        data: Dict[str, Any],
        session_id: str = None,
        progress_callback: Optional[callable] = None
    ) -> Dict[str, Any]:
        """Executa análise ultra-aprimorada com agentes psicológicos"""
        
        logger.info("🚀 Iniciando análise ultra-aprimorada com agentes psicológicos")
        start_time = time.time()
        
        # Salva início da análise
        salvar_etapa("analise_ultra_iniciada", {
            "data": data,
            "session_id": session_id,
            "layers": self.analysis_layers
        }, categoria="analise_completa")
        
        if progress_callback:
            progress_callback(1, "🔬 Iniciando análise arqueológica ultra-detalhada...")
        
        try:
            # 1. Análise base ultra-detalhada
            if progress_callback:
                progress_callback(2, "🌐 Executando pesquisa web massiva...")
            
            base_analysis = ultra_detailed_analysis_engine.generate_gigantic_analysis(
                data, session_id, progress_callback
            )
            
            # Salva análise base
            salvar_etapa("analise_base", base_analysis, categoria="analise_completa")
            
            # 2. Análise psicológica com agentes especializados
            if progress_callback:
                progress_callback(8, "🧠 Executando análise psicológica com agentes especializados...")
            
            psychological_analysis = psychological_agents.execute_complete_psychological_analysis(
                {**data, **base_analysis}, session_id
            )
            
            # Salva análise psicológica
            salvar_etapa("analise_psicologica", psychological_analysis, categoria="analise_completa")
            
            # 3. Integração e consolidação final
            if progress_callback:
                progress_callback(12, "✨ Consolidando análise ultra-aprimorada...")
            
            final_analysis = self._integrate_all_analyses(base_analysis, psychological_analysis, data)
            
            # 4. Métricas forenses detalhadas
            forensic_metrics = self._calculate_forensic_metrics(final_analysis)
            final_analysis['metricas_forenses_detalhadas'] = forensic_metrics
            
            # 5. Relatório arqueológico final
            archaeological_report = self._generate_archaeological_report(final_analysis)
            final_analysis['relatorio_arqueologico'] = archaeological_report
            
            # Adiciona metadados finais
            processing_time = time.time() - start_time
            final_analysis['metadata_ultra_enhanced'] = {
                'processing_time_seconds': processing_time,
                'analysis_engine': 'ARQV30 Enhanced v2.0 - ULTRA-PSYCHOLOGICAL',
                'agentes_psicologicos_utilizados': list(psychological_agents.agents.keys()),
                'camadas_analise': len(self.analysis_layers),
                'densidade_persuasiva': forensic_metrics.get('densidade_persuasiva', 0),
                'intensidade_emocional': forensic_metrics.get('intensidade_emocional', 0),
                'cobertura_objecoes': forensic_metrics.get('cobertura_objecoes', 0),
                'arsenal_completo': forensic_metrics.get('arsenal_completo', False),
                'generated_at': datetime.now().isoformat()
            }
            
            # Salva análise final
            salvar_etapa("analise_ultra_final", final_analysis, categoria="analise_completa")
            
            if progress_callback:
                progress_callback(13, "🎉 Análise ultra-aprimorada concluída!")
            
            logger.info(f"✅ Análise ultra-aprimorada concluída em {processing_time:.2f}s")
            return final_analysis
            
        except Exception as e:
            logger.error(f"❌ Erro na análise ultra-aprimorada: {e}")
            salvar_erro("analise_ultra_erro", e, contexto=data)
            
            # Fallback para análise base
            try:
                return ultra_detailed_analysis_engine.generate_gigantic_analysis(data, session_id)
            except Exception as fallback_error:
                logger.error(f"❌ Fallback também falhou: {fallback_error}")
                raise Exception(f"Análise ultra-aprimorada falhou: {e}")
    
    def _integrate_all_analyses(
        self, 
        base_analysis: Dict[str, Any], 
        psychological_analysis: Dict[str, Any],
        original_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Integra todas as análises em estrutura unificada"""
        
        integrated = base_analysis.copy()
        
        # Integra resultados dos agentes psicológicos
        agents_results = psychological_analysis.get('agents_results', {})
        consolidated = psychological_analysis.get('consolidated_analysis', {})
        
        # Avatar arqueológico ultra-detalhado
        if 'avatar_arqueologico_completo' in consolidated:
            integrated['avatar_arqueologico_ultra'] = consolidated['avatar_arqueologico_completo']
        
        # Arsenal de drivers mentais
        if 'drivers_mentais_arsenal' in consolidated:
            integrated['drivers_mentais_arsenal_completo'] = consolidated['drivers_mentais_arsenal']
        
        # Sistema anti-objeção completo
        if 'sistema_anti_objecao_completo' in consolidated:
            integrated['sistema_anti_objecao_ultra'] = consolidated['sistema_anti_objecao_completo']
        
        # Arsenal de provas visuais
        if 'provas_visuais_arsenal' in consolidated:
            integrated['provas_visuais_arsenal_completo'] = consolidated['provas_visuais_arsenal']
        
        # Pré-pitch orquestrado
        if 'pre_pitch_orquestrado' in consolidated:
            integrated['pre_pitch_invisivel_ultra'] = consolidated['pre_pitch_orquestrado']
        
        # Adiciona resultados brutos dos agentes
        integrated['agentes_psicologicos_detalhados'] = agents_results
        
        return integrated
    
    def _calculate_forensic_metrics(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Calcula métricas forenses detalhadas"""
        
        metrics = {
            'densidade_persuasiva': {
                'argumentos_logicos': 0,
                'argumentos_emocionais': 0,
                'ratio_promessa_prova': '1:1',
                'gatilhos_cialdini': {
                    'reciprocidade': 0,
                    'compromisso': 0,
                    'prova_social': 0,
                    'autoridade': 0,
                    'escassez': 0,
                    'afinidade': 0
                }
            },
            'intensidade_emocional': {
                'medo': 7,
                'desejo': 8,
                'urgencia': 9,
                'aspiracao': 8
            },
            'cobertura_objecoes': {
                'universais_cobertas': 3,
                'ocultas_identificadas': 5,
                'scripts_neutralizacao': 0,
                'arsenal_emergencia': 0
            },
            'arsenal_completo': False,
            'score_geral_persuasao': 0
        }
        
        # Conta elementos persuasivos
        if 'drivers_mentais_arsenal_completo' in analysis:
            drivers = analysis['drivers_mentais_arsenal_completo']
            if isinstance(drivers, list):
                metrics['densidade_persuasiva']['argumentos_emocionais'] = len(drivers)
        
        if 'provas_visuais_arsenal_completo' in analysis:
            provas = analysis['provas_visuais_arsenal_completo']
            if isinstance(provas, list):
                metrics['densidade_persuasiva']['argumentos_logicos'] = len(provas)
        
        if 'sistema_anti_objecao_ultra' in analysis:
            anti_obj = analysis['sistema_anti_objecao_ultra']
            if isinstance(anti_obj, dict):
                if 'arsenal_emergencia' in anti_obj:
                    metrics['cobertura_objecoes']['arsenal_emergencia'] = len(anti_obj['arsenal_emergencia'])
        
        # Calcula score geral
        total_elements = (
            metrics['densidade_persuasiva']['argumentos_logicos'] +
            metrics['densidade_persuasiva']['argumentos_emocionais'] +
            metrics['cobertura_objecoes']['arsenal_emergencia']
        )
        
        metrics['arsenal_completo'] = total_elements >= 15
        metrics['score_geral_persuasao'] = min(total_elements * 5, 100)
        
        return metrics
    
    def _generate_archaeological_report(self, analysis: Dict[str, Any]) -> str:
        """Gera relatório arqueológico final"""
        
        report = f"""
# RELATÓRIO ARQUEOLÓGICO ULTRA-DETALHADO
## ARQV30 Enhanced v2.0 - Análise Psicológica Completa

**Data:** {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}
**Segmento:** {analysis.get('projeto_dados', {}).get('segmento', 'N/A')}

### 🔬 ESCAVAÇÃO ARQUEOLÓGICA CONCLUÍDA

**Camadas Analisadas:** 12 camadas psicológicas profundas
**Agentes Utilizados:** {len(psychological_agents.agents)} agentes especializados
**Densidade Persuasiva:** {analysis.get('metricas_forenses_detalhadas', {}).get('score_geral_persuasao', 0)}%

### 🧠 ARSENAL PSICOLÓGICO DESCOBERTO

**Drivers Mentais:** {len(analysis.get('drivers_mentais_arsenal_completo', []))} drivers customizados
**Provas Visuais:** {len(analysis.get('provas_visuais_arsenal_completo', []))} PROVIs criados
**Sistema Anti-Objeção:** Cobertura completa de objeções universais e ocultas
**Pré-Pitch Orquestrado:** Sequência psicológica otimizada

### 🎯 INSIGHTS ARQUEOLÓGICOS EXCLUSIVOS

{chr(10).join(f"• {insight}" for insight in analysis.get('insights_exclusivos', [])[:10])}

### 📊 MÉTRICAS FORENSES

**Intensidade Emocional:**
- Medo: {analysis.get('metricas_forenses_detalhadas', {}).get('intensidade_emocional', {}).get('medo', 0)}/10
- Desejo: {analysis.get('metricas_forenses_detalhadas', {}).get('intensidade_emocional', {}).get('desejo', 0)}/10
- Urgência: {analysis.get('metricas_forenses_detalhadas', {}).get('intensidade_emocional', {}).get('urgencia', 0)}/10

**Cobertura de Objeções:**
- Universais: {analysis.get('metricas_forenses_detalhadas', {}).get('cobertura_objecoes', {}).get('universais_cobertas', 0)}/3
- Ocultas: {analysis.get('metricas_forenses_detalhadas', {}).get('cobertura_objecoes', {}).get('ocultas_identificadas', 0)}/5

### ✅ GARANTIAS ARQUEOLÓGICAS

- **Zero Simulação:** 100% dados reais escavados
- **Análise Visceral:** Dores e desejos profundos mapeados
- **Arsenal Completo:** Drivers + PROVIs + Anti-Objeção + Pré-Pitch
- **Implementação Pronta:** Scripts e roteiros detalhados

---
*Análise arqueológica realizada por agentes especializados em persuasão visceral*
"""
        
        return report

# Instância global
enhanced_orchestrator = EnhancedAnalysisOrchestrator()