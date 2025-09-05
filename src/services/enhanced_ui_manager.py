#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ARQV30 Enhanced v2.0 - Enhanced UI Manager
Gerenciador de interface aprimorada com componentes modernos
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class EnhancedUIManager:
    """Gerenciador de interface aprimorada"""
    
    def __init__(self):
        """Inicializa gerenciador de UI"""
        self.component_templates = self._load_component_templates()
        self.ui_themes = self._load_ui_themes()
        
        logger.info("Enhanced UI Manager inicializado")
    
    def _load_component_templates(self) -> Dict[str, str]:
        """Carrega templates de componentes"""
        return {
            'archaeological_section': '''
                <div class="psychological-section">
                    <div class="section-header">
                        <div class="section-icon">
                            <i class="fas fa-microscope"></i>
                        </div>
                        <div>
                            <h3 class="section-title">🔬 Análise Arqueológica Ultra-Profunda</h3>
                            <p class="section-subtitle">DNA da Conversão Extraído em 12 Camadas Forenses</p>
                        </div>
                    </div>
                    <div class="archaeological-content">
                        {content}
                    </div>
                </div>
            ''',
            
            'visceral_avatar_section': '''
                <div class="psychological-section">
                    <div class="section-header">
                        <div class="section-icon">
                            <i class="fas fa-brain"></i>
                        </div>
                        <div>
                            <h3 class="section-title">🧠 Avatar Visceral Ultra-Detalhado</h3>
                            <p class="section-subtitle">Engenharia Reversa Psicológica Profunda</p>
                        </div>
                    </div>
                    <div class="visceral-content">
                        {content}
                    </div>
                </div>
            ''',
            
            'drivers_arsenal_section': '''
                <div class="psychological-section">
                    <div class="section-header">
                        <div class="section-icon">
                            <i class="fas fa-cogs"></i>
                        </div>
                        <div>
                            <h3 class="section-title">⚙️ Arsenal de Drivers Mentais</h3>
                            <p class="section-subtitle">19 Gatilhos Psicológicos Customizados</p>
                        </div>
                    </div>
                    <div class="drivers-content">
                        {content}
                    </div>
                </div>
            ''',
            
            'provis_arsenal_section': '''
                <div class="psychological-section">
                    <div class="section-header">
                        <div class="section-icon">
                            <i class="fas fa-theater-masks"></i>
                        </div>
                        <div>
                            <h3 class="section-title">🎭 Arsenal de PROVIs</h3>
                            <p class="section-subtitle">Provas Visuais Instantâneas Devastadoras</p>
                        </div>
                    </div>
                    <div class="provis-content">
                        {content}
                    </div>
                </div>
            ''',
            
            'anti_objection_section': '''
                <div class="psychological-section">
                    <div class="section-header">
                        <div class="section-icon">
                            <i class="fas fa-shield-alt"></i>
                        </div>
                        <div>
                            <h3 class="section-title">🛡️ Sistema Anti-Objeção</h3>
                            <p class="section-subtitle">Arsenal Psicológico Completo</p>
                        </div>
                    </div>
                    <div class="anti-objection-content">
                        {content}
                    </div>
                </div>
            ''',
            
            'forensic_metrics_section': '''
                <div class="psychological-section">
                    <div class="section-header">
                        <div class="section-icon">
                            <i class="fas fa-chart-line"></i>
                        </div>
                        <div>
                            <h3 class="section-title">📊 Métricas Forenses</h3>
                            <p class="section-subtitle">Análise Quantitativa da Persuasão</p>
                        </div>
                    </div>
                    <div class="forensic-content">
                        {content}
                    </div>
                </div>
            '''
        }
    
    def _load_ui_themes(self) -> Dict[str, Dict[str, str]]:
        """Carrega temas de UI"""
        return {
            'archaeological': {
                'primary_color': '#0ea5e9',
                'secondary_color': '#8b5cf6',
                'accent_color': '#10b981',
                'background': '#0a0a0a',
                'surface': '#1e1e1e'
            },
            'visceral': {
                'primary_color': '#ef4444',
                'secondary_color': '#f59e0b',
                'accent_color': '#8b5cf6',
                'background': '#0f0f0f',
                'surface': '#1a1a1a'
            }
        }
    
    def render_archaeological_analysis(self, archaeological_data: Dict[str, Any]) -> str:
        """Renderiza análise arqueológica"""
        
        content = f"""
        <div class="archaeological-analysis">
            <div class="dna-conversion">
                <h4>🧬 DNA da Conversão Extraído</h4>
                <div class="dna-formula">
                    <strong>Fórmula Estrutural:</strong> 
                    {archaeological_data.get('dna_conversao_completo', {}).get('formula_estrutural', 'Análise em andamento')}
                </div>
                <div class="sequence-triggers">
                    <strong>Sequência de Gatilhos:</strong>
                    <ul>
                        {self._render_list_items(archaeological_data.get('dna_conversao_completo', {}).get('sequencia_gatilhos', []))}
                    </ul>
                </div>
            </div>
            
            <div class="forensic-layers">
                <h4>🔬 Camadas Forenses Analisadas</h4>
                {self._render_forensic_layers(archaeological_data)}
            </div>
            
            <div class="timing-analysis">
                <h4>🕐 Cronometragem Detalhada</h4>
                {self._render_timing_analysis(archaeological_data)}
            </div>
        </div>
        """
        
        return self.component_templates['archaeological_section'].format(content=content)
    
    def render_visceral_avatar(self, visceral_data: Dict[str, Any]) -> str:
        """Renderiza avatar visceral ultra-detalhado"""
        
        avatar = visceral_data.get('avatar_visceral_ultra', {})
        
        content = f"""
        <div class="visceral-avatar">
            <div class="avatar-identity">
                <h4>👤 {avatar.get('nome_ficticio', 'Avatar Visceral')}</h4>
                <div class="demographic-profile">
                    {self._render_demographic_profile(avatar.get('perfil_demografico_visceral', {}))}
                </div>
            </div>
            
            <div class="psychological-wounds">
                <h4>🩸 Feridas Abertas (Inconfessáveis)</h4>
                <div class="wounds-list">
                    {self._render_wounds_list(avatar.get('feridas_abertas_inconfessaveis', []))}
                </div>
            </div>
            
            <div class="forbidden-dreams">
                <h4>🔥 Sonhos Proibidos (Ardentes)</h4>
                <div class="dreams-list">
                    {self._render_dreams_list(avatar.get('sonhos_proibidos_ardentes', []))}
                </div>
            </div>
            
            <div class="internal-demons">
                <h4>👹 Demônios Internos (Paralisantes)</h4>
                <div class="demons-list">
                    {self._render_demons_list(avatar.get('demonios_internos_paralisantes', []))}
                </div>
            </div>
            
            <div class="soul-dialect">
                <h4>🗣️ Dialeto da Alma</h4>
                {self._render_soul_dialect(avatar.get('dialeto_alma_linguagem_interna', {}))}
            </div>
        </div>
        """
        
        return self.component_templates['visceral_avatar_section'].format(content=content)
    
    def render_drivers_arsenal(self, drivers_data: Dict[str, Any]) -> str:
        """Renderiza arsenal de drivers mentais"""
        
        drivers = drivers_data.get('drivers_customizados', [])
        
        content = f"""
        <div class="drivers-arsenal">
            <div class="arsenal-overview">
                <h4>⚙️ Arsenal Completo: {len(drivers)} Drivers Customizados</h4>
                <p>Gatilhos psicológicos personalizados para máximo impacto</p>
            </div>
            
            <div class="drivers-grid">
                {self._render_drivers_grid(drivers)}
            </div>
            
            <div class="sequencing-strategy">
                <h4>🎯 Sequenciamento Estratégico</h4>
                {self._render_sequencing_strategy(drivers_data)}
            </div>
        </div>
        """
        
        return self.component_templates['drivers_arsenal_section'].format(content=content)
    
    def render_provis_arsenal(self, provis_data: Dict[str, Any]) -> str:
        """Renderiza arsenal de PROVIs"""
        
        provis = provis_data.get('arsenal_provis_completo', [])
        
        content = f"""
        <div class="provis-arsenal">
            <div class="arsenal-overview">
                <h4>🎭 Arsenal Devastador: {len(provis)} PROVIs Criadas</h4>
                <p>Experiências físicas que transformam conceitos abstratos em convicção</p>
            </div>
            
            <div class="provis-showcase">
                {self._render_provis_showcase(provis)}
            </div>
            
            <div class="orchestration-plan">
                <h4>🎼 Orquestração Estratégica</h4>
                {self._render_orchestration_plan(provis_data.get('orquestracao_estrategica', {}))}
            </div>
            
            <div class="implementation-kit">
                <h4>🛠️ Kit de Implementação</h4>
                {self._render_implementation_kit(provis_data.get('kit_implementacao', {}))}
            </div>
        </div>
        """
        
        return self.component_templates['provis_arsenal_section'].format(content=content)
    
    def render_forensic_metrics(self, forensic_data: Dict[str, Any]) -> str:
        """Renderiza métricas forenses"""
        
        content = f"""
        <div class="forensic-metrics">
            <div class="metrics-overview">
                <h4>📊 Análise Forense Quantitativa</h4>
                <p>Métricas objetivas da densidade persuasiva</p>
            </div>
            
            <div class="forensic-grid">
                {self._render_forensic_grid(forensic_data)}
            </div>
            
            <div class="cialdini-analysis">
                <h4>🎯 Gatilhos de Cialdini Identificados</h4>
                {self._render_cialdini_analysis(forensic_data)}
            </div>
            
            <div class="emotional-intensity">
                <h4>🔥 Intensidade Emocional Medida</h4>
                {self._render_emotional_intensity(forensic_data)}
            </div>
        </div>
        """
        
        return self.component_templates['forensic_metrics_section'].format(content=content)
    
    def _render_list_items(self, items: List[str]) -> str:
        """Renderiza lista de itens"""
        return ''.join(f'<li>{item}</li>' for item in items)
    
    def _render_forensic_layers(self, archaeological_data: Dict[str, Any]) -> str:
        """Renderiza camadas forenses"""
        
        layers_html = ""
        for i in range(1, 13):
            layer_key = f'camada_{i}_'
            layer_data = None
            
            # Encontra dados da camada
            for key, value in archaeological_data.items():
                if key.startswith(layer_key):
                    layer_data = value
                    break
            
            if layer_data:
                layers_html += f"""
                <div class="forensic-layer">
                    <h5>Camada {i}: {self._get_layer_name(i)}</h5>
                    <div class="layer-content">
                        {self._render_layer_content(layer_data)}
                    </div>
                </div>
                """
        
        return layers_html
    
    def _get_layer_name(self, layer_number: int) -> str:
        """Retorna nome da camada forense"""
        layer_names = {
            1: "Abertura Cirúrgica",
            2: "Arquitetura Narrativa", 
            3: "Construção de Autoridade",
            4: "Gestão de Objeções",
            5: "Construção de Desejo",
            6: "Educação Estratégica",
            7: "Apresentação da Oferta",
            8: "Linguagem e Padrões",
            9: "Gestão de Tempo",
            10: "Pontos de Impacto",
            11: "Vazamentos",
            12: "Métricas Forenses"
        }
        return layer_names.get(layer_number, f"Camada {layer_number}")
    
    def _render_layer_content(self, layer_data: Dict[str, Any]) -> str:
        """Renderiza conteúdo de uma camada"""
        
        content_html = ""
        
        for key, value in layer_data.items():
            if isinstance(value, list):
                content_html += f"""
                <div class="layer-item">
                    <strong>{key.replace('_', ' ').title()}:</strong>
                    <ul>
                        {self._render_list_items(value)}
                    </ul>
                </div>
                """
            elif isinstance(value, dict):
                content_html += f"""
                <div class="layer-item">
                    <strong>{key.replace('_', ' ').title()}:</strong>
                    <div class="nested-content">
                        {self._render_layer_content(value)}
                    </div>
                </div>
                """
            else:
                content_html += f"""
                <div class="layer-item">
                    <strong>{key.replace('_', ' ').title()}:</strong>
                    <span>{value}</span>
                </div>
                """
        
        return content_html
    
    def _render_timing_analysis(self, archaeological_data: Dict[str, Any]) -> str:
        """Renderiza análise de timing"""
        
        timing_data = archaeological_data.get('cronometragem_detalhada', {})
        
        timing_html = ""
        for key, value in timing_data.items():
            timing_html += f"""
            <div class="timing-segment">
                <h5>{key.replace('_', ' ').title()}</h5>
                <p>{value}</p>
            </div>
            """
        
        return timing_html
    
    def _render_demographic_profile(self, profile: Dict[str, Any]) -> str:
        """Renderiza perfil demográfico"""
        
        profile_html = ""
        for key, value in profile.items():
            profile_html += f"""
            <div class="profile-item">
                <span class="profile-label">{key.replace('_', ' ').title()}:</span>
                <span class="profile-value">{value}</span>
            </div>
            """
        
        return f'<div class="demographic-grid">{profile_html}</div>'
    
    def _render_wounds_list(self, wounds: List[str]) -> str:
        """Renderiza lista de feridas"""
        
        wounds_html = ""
        for i, wound in enumerate(wounds[:15], 1):
            wounds_html += f"""
            <div class="wound-item">
                <div class="wound-number">{i}</div>
                <div class="wound-text">{wound}</div>
            </div>
            """
        
        return wounds_html
    
    def _render_dreams_list(self, dreams: List[str]) -> str:
        """Renderiza lista de sonhos"""
        
        dreams_html = ""
        for i, dream in enumerate(dreams[:15], 1):
            dreams_html += f"""
            <div class="dream-item">
                <div class="dream-number">{i}</div>
                <div class="dream-text">{dream}</div>
            </div>
            """
        
        return dreams_html
    
    def _render_demons_list(self, demons: List[str]) -> str:
        """Renderiza lista de demônios internos"""
        
        demons_html = ""
        for i, demon in enumerate(demons[:10], 1):
            demons_html += f"""
            <div class="demon-item">
                <div class="demon-number">{i}</div>
                <div class="demon-text">{demon}</div>
            </div>
            """
        
        return demons_html
    
    def _render_soul_dialect(self, dialect: Dict[str, Any]) -> str:
        """Renderiza dialeto da alma"""
        
        dialect_html = ""
        
        for key, value in dialect.items():
            if isinstance(value, list):
                dialect_html += f"""
                <div class="dialect-section">
                    <h6>{key.replace('_', ' ').title()}</h6>
                    <div class="dialect-phrases">
                        {self._render_phrase_list(value)}
                    </div>
                </div>
                """
            else:
                dialect_html += f"""
                <div class="dialect-item">
                    <strong>{key.replace('_', ' ').title()}:</strong>
                    <span>{value}</span>
                </div>
                """
        
        return dialect_html
    
    def _render_phrase_list(self, phrases: List[str]) -> str:
        """Renderiza lista de frases"""
        
        phrases_html = ""
        for phrase in phrases[:5]:
            phrases_html += f'<div class="phrase-item">"{phrase}"</div>'
        
        return phrases_html
    
    def _render_drivers_grid(self, drivers: List[Dict[str, Any]]) -> str:
        """Renderiza grid de drivers"""
        
        drivers_html = ""
        
        for i, driver in enumerate(drivers, 1):
            drivers_html += f"""
            <div class="driver-card">
                <div class="driver-header">
                    <h5>Driver {i}: {driver.get('nome', 'Driver Mental')}</h5>
                    <div class="driver-priority">{driver.get('prioridade', 'ALTA')}</div>
                </div>
                
                <div class="driver-content">
                    <div class="driver-trigger">
                        <strong>Gatilho Central:</strong> {driver.get('gatilho_central', 'N/A')}
                    </div>
                    
                    <div class="driver-definition">
                        <strong>Definição Visceral:</strong> {driver.get('definicao_visceral', 'N/A')}
                    </div>
                    
                    <div class="driver-script">
                        <h6>Roteiro de Ativação:</h6>
                        {self._render_activation_script(driver.get('roteiro_ativacao', {}))}
                    </div>
                    
                    <div class="anchor-phrases">
                        <h6>Frases de Ancoragem:</h6>
                        {self._render_anchor_phrases(driver.get('frases_ancoragem', []))}
                    </div>
                </div>
            </div>
            """
        
        return drivers_html
    
    def _render_activation_script(self, script: Dict[str, Any]) -> str:
        """Renderiza roteiro de ativação"""
        
        script_html = ""
        
        for key, value in script.items():
            script_html += f"""
            <div class="script-step">
                <strong>{key.replace('_', ' ').title()}:</strong>
                <p>{value}</p>
            </div>
            """
        
        return script_html
    
    def _render_anchor_phrases(self, phrases: List[str]) -> str:
        """Renderiza frases de ancoragem"""
        
        phrases_html = ""
        for phrase in phrases:
            phrases_html += f'<div class="anchor-phrase">"{phrase}"</div>'
        
        return phrases_html
    
    def _render_sequencing_strategy(self, drivers_data: Dict[str, Any]) -> str:
        """Renderiza estratégia de sequenciamento"""
        
        sequencing = drivers_data.get('sequenciamento_estrategico', {})
        
        return f"""
        <div class="sequencing-phases">
            <div class="phase">
                <h6>Fase 1 - Despertar:</h6>
                <p>{', '.join(sequencing.get('fase_despertar', []))}</p>
            </div>
            <div class="phase">
                <h6>Fase 2 - Desejo:</h6>
                <p>{', '.join(sequencing.get('fase_desejo', []))}</p>
            </div>
            <div class="phase">
                <h6>Fase 3 - Decisão:</h6>
                <p>{', '.join(sequencing.get('fase_decisao', []))}</p>
            </div>
            <div class="phase">
                <h6>Fase 4 - Direção:</h6>
                <p>{', '.join(sequencing.get('fase_direcao', []))}</p>
            </div>
        </div>
        """
    
    def _render_provis_showcase(self, provis: List[Dict[str, Any]]) -> str:
        """Renderiza showcase de PROVIs"""
        
        provis_html = ""
        
        for provi in provis:
            provis_html += f"""
            <div class="provi-card">
                <div class="provi-header">
                    <h5>{provi.get('nome', 'PROVI')}</h5>
                    <div class="provi-category">{provi.get('categoria', 'N/A')}</div>
                </div>
                
                <div class="provi-content">
                    <div class="provi-objective">
                        <strong>Objetivo Psicológico:</strong>
                        <p>{provi.get('objetivo_psicologico', 'N/A')}</p>
                    </div>
                    
                    <div class="provi-experiment">
                        <strong>Experimento:</strong>
                        <p>{provi.get('experimento_escolhido', 'N/A')}</p>
                    </div>
                    
                    <div class="provi-analogy">
                        <strong>Analogia:</strong>
                        <p>{provi.get('analogia_perfeita', 'N/A')}</p>
                    </div>
                    
                    <div class="provi-materials">
                        <strong>Materiais:</strong>
                        {self._render_materials_list(provi.get('materiais_especificos', []))}
                    </div>
                </div>
            </div>
            """
        
        return provis_html
    
    def _render_materials_list(self, materials: List[Dict[str, Any]]) -> str:
        """Renderiza lista de materiais"""
        
        materials_html = ""
        for material in materials:
            materials_html += f"""
            <div class="material-item">
                <strong>{material.get('item', 'Material')}:</strong>
                <span>{material.get('especificacao', 'N/A')}</span>
            </div>
            """
        
        return materials_html
    
    def _render_orchestration_plan(self, orchestration: Dict[str, Any]) -> str:
        """Renderiza plano de orquestração"""
        
        return f"""
        <div class="orchestration-details">
            <div class="sequence">
                <h6>Sequência Otimizada:</h6>
                <ul>
                    {self._render_list_items(orchestration.get('sequencia_otimizada', []))}
                </ul>
            </div>
            
            <div class="emotional-escalation">
                <h6>Escalada Emocional:</h6>
                <p>{orchestration.get('escalada_emocional', 'N/A')}</p>
            </div>
            
            <div class="narrative-connector">
                <h6>Narrativa Conectora:</h6>
                <p>{orchestration.get('narrativa_conectora', 'N/A')}</p>
            </div>
        </div>
        """
    
    def _render_implementation_kit(self, kit: Dict[str, Any]) -> str:
        """Renderiza kit de implementação"""
        
        return f"""
        <div class="implementation-details">
            <div class="checklist">
                <h6>Checklist de Preparação:</h6>
                <ul>
                    {self._render_list_items(kit.get('checklist_preparacao', []))}
                </ul>
            </div>
            
            <div class="timeline">
                <h6>Timeline de Execução:</h6>
                {self._render_timeline(kit.get('timeline_execucao', {}))}
            </div>
            
            <div class="troubleshooting">
                <h6>Troubleshooting:</h6>
                {self._render_troubleshooting(kit.get('troubleshooting', {}))}
            </div>
        </div>
        """
    
    def _render_timeline(self, timeline: Dict[str, Any]) -> str:
        """Renderiza timeline"""
        
        timeline_html = ""
        for key, value in timeline.items():
            timeline_html += f"""
            <div class="timeline-item">
                <strong>{key.replace('_', ' ').title()}:</strong>
                <span>{value}</span>
            </div>
            """
        
        return timeline_html
    
    def _render_troubleshooting(self, troubleshooting: Dict[str, Any]) -> str:
        """Renderiza troubleshooting"""
        
        trouble_html = ""
        for key, value in troubleshooting.items():
            trouble_html += f"""
            <div class="trouble-item">
                <strong>{key.replace('_', ' ').title()}:</strong>
                <span>{value}</span>
            </div>
            """
        
        return trouble_html
    
    def _render_forensic_grid(self, forensic_data: Dict[str, Any]) -> str:
        """Renderiza grid de métricas forenses"""
        
        metrics = forensic_data.get('densidade_persuasiva', {})
        
        return f"""
        <div class="forensic-item">
            <div class="forensic-value">{metrics.get('argumentos_totais', 0)}</div>
            <div class="forensic-label">Argumentos Totais</div>
        </div>
        
        <div class="forensic-item">
            <div class="forensic-value">{metrics.get('argumentos_logicos', 0)}</div>
            <div class="forensic-label">Argumentos Lógicos</div>
        </div>
        
        <div class="forensic-item">
            <div class="forensic-value">{metrics.get('argumentos_emocionais', 0)}</div>
            <div class="forensic-label">Argumentos Emocionais</div>
        </div>
        
        <div class="forensic-item">
            <div class="forensic-value">{metrics.get('ratio_promessa_prova', '1:1')}</div>
            <div class="forensic-label">Ratio Promessa/Prova</div>
        </div>
        """
    
    def _render_cialdini_analysis(self, forensic_data: Dict[str, Any]) -> str:
        """Renderiza análise dos gatilhos de Cialdini"""
        
        cialdini = forensic_data.get('gatilhos_cialdini', {})
        
        cialdini_html = ""
        for gatilho, count in cialdini.items():
            cialdini_html += f"""
            <div class="cialdini-item">
                <div class="cialdini-name">{gatilho.title()}</div>
                <div class="cialdini-count">{count}</div>
                <div class="cialdini-bar">
                    <div class="cialdini-fill" style="width: {min(count * 20, 100)}%"></div>
                </div>
            </div>
            """
        
        return cialdini_html
    
    def _render_emotional_intensity(self, forensic_data: Dict[str, Any]) -> str:
        """Renderiza intensidade emocional"""
        
        emotions = forensic_data.get('intensidade_emocional', {})
        
        emotions_html = ""
        for emotion, intensity in emotions.items():
            # Extrai número da intensidade (ex: "8/10" -> 8)
            try:
                if '/' in str(intensity):
                    value = int(str(intensity).split('/')[0])
                else:
                    value = int(intensity)
            except:
                value = 5
            
            emotions_html += f"""
            <div class="emotion-item">
                <div class="emotion-name">{emotion.title()}</div>
                <div class="emotion-intensity">{intensity}</div>
                <div class="emotion-bar">
                    <div class="emotion-fill" style="width: {value * 10}%"></div>
                </div>
            </div>
            """
        
        return emotions_html

# Instância global
enhanced_ui_manager = EnhancedUIManager()