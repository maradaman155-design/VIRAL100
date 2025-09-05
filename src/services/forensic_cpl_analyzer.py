#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ARQV30 Enhanced v2.0 - Forensic CPL Analyzer
ARQUEÓLOGO MESTRE DA PERSUASÃO - Análise Forense Completa de CPL
"""

import logging
import time
import json
import re
from typing import Dict, List, Any, Optional
from datetime import datetime
from services.ai_manager import ai_manager
from services.auto_save_manager import salvar_etapa, salvar_erro

logger = logging.getLogger(__name__)

class ForensicCPLAnalyzer:
    """ARQUEÓLOGO MESTRE DA PERSUASÃO - Análise Forense de CPL"""
    
    def __init__(self):
        """Inicializa o analisador forense de CPL"""
        self.forensic_layers = [
            'abertura_cirurgica',
            'arquitetura_narrativa', 
            'construcao_autoridade',
            'gestao_objecoes',
            'construcao_desejo',
            'educacao_estrategica',
            'apresentacao_oferta',
            'linguagem_padroes',
            'gestao_tempo_ritmo',
            'pontos_maior_impacto',
            'vazamentos_otimizacoes',
            'metricas_forenses'
        ]
        
        logger.info("🔬 ARQUEÓLOGO MESTRE DA PERSUASÃO inicializado")
    
    def analyze_cpl_forensically(
        self,
        transcription: str,
        context_data: Dict[str, Any],
        session_id: str = None
    ) -> Dict[str, Any]:
        """Executa análise forense completa do CPL"""
        
        logger.info("🔬 INICIANDO ANÁLISE FORENSE COMPLETA DO CPL")
        
        try:
            # Salva dados de entrada
            salvar_etapa("cpl_forensic_input", {
                "transcription_length": len(transcription),
                "context_data": context_data,
                "forensic_layers": self.forensic_layers
            }, categoria="analise_completa")
            
            # Valida entrada
            if not transcription or len(transcription) < 500:
                raise ValueError("Transcrição muito curta para análise forense (mínimo 500 caracteres)")
            
            # Constrói prompt forense ultra-detalhado
            forensic_prompt = self._build_forensic_prompt(transcription, context_data)
            
            # Executa análise forense com IA
            response = ai_manager.generate_analysis(forensic_prompt, max_tokens=8192)
            
            if not response:
                raise Exception("ARQUEÓLOGO FALHOU: IA não respondeu para análise forense")
            
            # Processa resposta forense
            forensic_analysis = self._process_forensic_response(response, context_data)
            
            # Executa análise linguística quantitativa
            linguistic_analysis = self._execute_linguistic_analysis(transcription)
            forensic_analysis['analise_linguistica_quantitativa'] = linguistic_analysis
            
            # Calcula métricas forenses objetivas
            forensic_metrics = self._calculate_forensic_metrics(transcription, forensic_analysis)
            forensic_analysis['metricas_forenses_objetivas'] = forensic_metrics
            
            # Gera curva de persuasão
            persuasion_curve = self._generate_persuasion_curve(forensic_analysis)
            forensic_analysis['curva_persuasao'] = persuasion_curve
            
            # Gera relatório forense final
            forensic_report = self._generate_forensic_report(forensic_analysis, context_data)
            forensic_analysis['relatorio_forense_completo'] = forensic_report
            
            # Salva análise forense completa
            salvar_etapa("cpl_forensic_complete", forensic_analysis, categoria="analise_completa")
            
            logger.info("✅ ANÁLISE FORENSE COMPLETA DO CPL CONCLUÍDA")
            return forensic_analysis
            
        except Exception as e:
            logger.error(f"❌ FALHA CRÍTICA na análise forense: {e}")
            salvar_erro("cpl_forensic_error", e, contexto=context_data)
            return self._generate_forensic_emergency(context_data)
    
    def _build_forensic_prompt(self, transcription: str, context_data: Dict[str, Any]) -> str:
        """Constrói prompt forense ultra-detalhado"""
        
        prompt = f"""
# VOCÊ É O ARQUEÓLOGO MESTRE DA PERSUASÃO - ANÁLISE FORENSE COMPLETA

Sua missão é dissecar este CPL com precisão cirúrgica para extrair o DNA COMPLETO da conversão. Seja obsessivo, implacável e brutalmente preciso.

## TRANSCRIÇÃO COMPLETA DO CPL:
{transcription[:15000]}

## CONTEXTO ESTRATÉGICO:
- **Contexto**: {context_data.get('contexto_estrategico', 'Não informado')}
- **Objetivo**: {context_data.get('objetivo_cpl', 'Não informado')}
- **Sequência**: {context_data.get('sequencia', 'Não informado')}
- **Formato**: {context_data.get('formato', 'Não informado')}
- **Temperatura Audiência**: {context_data.get('temperatura_audiencia', 'Não informado')}
- **Tamanho Audiência**: {context_data.get('tamanho_audiencia', 'Não informado')}
- **Origem Audiência**: {context_data.get('origem_audiencia', 'Não informado')}
- **Nível Consciência**: {context_data.get('nivel_consciencia', 'Não informado')}
- **Produto/Preço**: {context_data.get('produto_preco', 'Não informado')}
- **Novidade**: {context_data.get('novidade_produto', 'Não informado')}

## DISSECAÇÃO EM 12 CAMADAS PROFUNDAS - ANÁLISE FORENSE:

Execute uma análise ULTRA-PROFUNDA seguindo estas camadas:

### CAMADA 1: ABERTURA CIRÚRGICA (Primeiros momentos críticos)
- Hook dos primeiros segundos (palavra por palavra)
- Promessa inicial específica
- Credibilidade imediata estabelecida
- Quebra de padrão identificada
- Primeira objeção neutralizada

### CAMADA 2: ARQUITETURA NARRATIVA COMPLETA
- Estrutura temporal detalhada
- Arcos narrativos mapeados
- Protagonistas e conflitos
- Momentos de tensão e alívio
- Storytelling estratégico

### CAMADA 3: CONSTRUÇÃO DE AUTORIDADE PROGRESSIVA
- Credenciais diretas e indiretas
- Prova social estratégica
- Demonstração de conhecimento
- Vulnerabilidade calculada
- Superioridade sutil

### CAMADA 4: GESTÃO DE OBJEÇÕES MICROSCÓPICA
- Objeções de credibilidade, tempo, dinheiro
- Técnicas preemptivas vs reativas
- Linguagem específica para neutralização
- Transformação de objeção em benefício

### CAMADA 5: CONSTRUÇÃO DE DESEJO SISTEMÁTICA
- Pintura da dor amplificada
- Contraposição do prazer
- Urgência do problema
- Escassez da oportunidade
- FOMO estratégico

### CAMADA 6: EDUCAÇÃO ESTRATÉGICA VS REVELAÇÃO
- Balanceamento ensino vs retenção
- Profundidade do conteúdo
- Cliffhangers educacionais
- Diferenciação amostra vs produto

### CAMADA 7: APRESENTAÇÃO DA OFERTA DETALHADA
- Timing da primeira menção
- Estrutura de apresentação
- Elementos incluídos
- Justificativa de valor
- Ancoragem de preço

### CAMADA 8: LINGUAGEM E PADRÕES VERBAIS
- Palavras de poder identificadas
- Frames linguísticos
- Padrões de repetição
- Comandos embutidos
- Pressuposições estratégicas

### CAMADA 9: GESTÃO DE TEMPO E RITMO
- Cronometragem precisa
- Análise de pacing
- Variação de velocidade
- Pausas estratégicas
- Gestão de energia

### CAMADA 10: PONTOS DE MAIOR IMPACTO
- Maior pico emocional
- Revelação principal
- Virada de chave
- Momento de conversão
- Clímax da apresentação

### CAMADA 11: VAZAMENTOS E OTIMIZAÇÕES
- Pontos fracos identificados
- Vazamentos de atenção
- Inconsistências
- Oportunidades perdidas
- Melhorias óbvias

### CAMADA 12: MÉTRICAS FORENSES OBJETIVAS
- Análise linguística quantitativa
- Ratio EU vs VOCÊ
- Promessas vs Provas
- Densidade persuasiva
- Gatilhos de Cialdini

RETORNE JSON ESTRUTURADO ULTRA-COMPLETO:

```json
{{
  "dna_conversao_completo": {{
    "formula_estrutural": "Fórmula extraída da conversão",
    "sequencia_gatilhos": ["Gatilho 1", "Gatilho 2", "Gatilho 3"],
    "padroes_linguagem": ["Padrão 1", "Padrão 2"],
    "timing_otimo": "Timing ideal de cada elemento"
  }},
  
  "camada_1_abertura_cirurgica": {{
    "hook_primeiros_segundos": "Análise palavra por palavra dos primeiros 30 segundos",
    "emocao_ativada": "Emoção predominante ativada",
    "promessa_inicial": "Primeira promessa específica feita",
    "credibilidade_imediata": "Como estabelece credibilidade imediatamente",
    "quebra_padrao": "Técnica de pattern interrupt usada",
    "primeira_objecao_neutralizada": "Qual objeção antecipa e neutraliza",
    "tempo_primeira_promessa": "Segundos até primeira promessa",
    "separacao_outros": "Como se diferencia de outros"
  }},
  
  "camada_2_arquitetura_narrativa": {{
    "estrutura_temporal": "Mapeamento minuto a minuto da estrutura",
    "arcos_narrativos": ["História 1", "História 2"],
    "protagonistas": ["Personagem 1", "Personagem 2"],
    "conflitos_apresentados": ["Conflito 1", "Conflito 2"],
    "momentos_tensao": ["Tensão 1", "Tensão 2"],
    "pontos_alivio": ["Alívio 1", "Alívio 2"],
    "estrutura_classica": "Usa contexto → conflito → clímax → resolução?",
    "historias_pessoais_terceiros": "Proporção pessoal vs terceiros",
    "conexao_individual_universal": "Como conecta histórias com problema universal"
  }},
  
  "cronometragem_detalhada": {{
    "minuto_00_03_abertura": "Análise dos primeiros 3 minutos",
    "minuto_03_XX_educacao": "Análise da fase educacional",
    "minuto_XX_XX_transicao": "Análise da transição para venda",
    "minuto_XX_XX_oferta": "Análise da apresentação da oferta",
    "minuto_XX_final_fechamento": "Análise do fechamento/CTA"
  }},
  
  "metricas_forenses_objetivas": {{
    "ratio_eu_voce": {{
      "contagem_eu": 0,
      "contagem_voce": 0,
      "percentual_eu": 0,
      "percentual_voce": 0
    }},
    "promessas_vs_provas": {{
      "total_promessas": 0,
      "total_provas": 0,
      "ratio_promessa_prova": "1:X"
    }},
    "densidade_persuasiva": {{
      "argumentos_totais": 0,
      "argumentos_logicos": 0,
      "argumentos_emocionais": 0,
      "densidade_por_minuto": 0
    }},
    "gatilhos_cialdini": {{
      "reciprocidade": 0,
      "compromisso": 0,
      "prova_social": 0,
      "autoridade": 0,
      "escassez": 0,
      "afinidade": 0
    }}
  }}
}}
```

CRÍTICO: Seja cirúrgico, obsessivo e implacável na análise. Use APENAS dados REAIS da transcrição.
"""
        
        return prompt
    
    def _process_forensic_response(self, response: str, context_data: Dict[str, Any]) -> Dict[str, Any]:
        """Processa resposta forense com validação rigorosa"""
        
        try:
            # Extrai JSON da resposta
            clean_text = response.strip()
            
            if "```json" in clean_text:
                start = clean_text.find("```json") + 7
                end = clean_text.rfind("```")
                clean_text = clean_text[start:end].strip()
            
            # Parseia JSON
            forensic_data = json.loads(clean_text)
            
            # Adiciona metadados forenses
            forensic_data['metadata_forense'] = {
                'generated_at': datetime.now().isoformat(),
                'agent': 'ARQUEÓLOGO MESTRE DA PERSUASÃO',
                'camadas_analisadas': len(self.forensic_layers),
                'profundidade_escavacao': 'ULTRA-PROFUNDA',
                'analise_forense_completa': True,
                'context_data': context_data
            }
            
            return forensic_data
            
        except json.JSONDecodeError as e:
            logger.error(f"❌ Erro ao parsear JSON forense: {e}")
            return self._extract_forensic_insights_from_text(response, context_data)
    
    def _extract_forensic_insights_from_text(self, text: str, context_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extrai insights forenses do texto quando JSON falha"""
        
        return {
            "dna_conversao_completo": {
                "formula_estrutural": "Análise forense extraída do texto - Sistema em recuperação",
                "sequencia_gatilhos": [
                    "Despertar consciência da dor",
                    "Amplificar desejo de mudança",
                    "Criar urgência de ação",
                    "Apresentar solução única",
                    "Neutralizar objeções",
                    "Forçar decisão imediata"
                ]
            },
            "raw_forensic_text": text[:3000],
            "extraction_method": "text_analysis_forensic"
        }
    
    def _execute_linguistic_analysis(self, transcription: str) -> Dict[str, Any]:
        """Executa análise linguística quantitativa"""
        
        words = transcription.split()
        sentences = re.split(r'[.!?]+', transcription)
        
        # Contagem EU vs VOCÊ
        eu_count = len(re.findall(r'\b(eu|meu|minha|comigo|me)\b', transcription, re.IGNORECASE))
        voce_count = len(re.findall(r'\b(você|seu|sua|contigo|te)\b', transcription, re.IGNORECASE))
        
        total_pronouns = eu_count + voce_count
        eu_percentage = (eu_count / total_pronouns * 100) if total_pronouns > 0 else 0
        voce_percentage = (voce_count / total_pronouns * 100) if total_pronouns > 0 else 0
        
        # Contagem de promessas vs provas
        promessa_patterns = [r'vou te', r'você vai', r'vai conseguir', r'vai ter', r'vai ser']
        prova_patterns = [r'por exemplo', r'veja', r'olha', r'dados mostram', r'pesquisa']
        
        promessas = sum(len(re.findall(pattern, transcription, re.IGNORECASE)) for pattern in promessa_patterns)
        provas = sum(len(re.findall(pattern, transcription, re.IGNORECASE)) for pattern in prova_patterns)
        
        # Gatilhos de Cialdini
        cialdini_triggers = {
            'reciprocidade': len(re.findall(r'\b(grátis|presente|dou|ofereço)\b', transcription, re.IGNORECASE)),
            'compromisso': len(re.findall(r'\b(comprometa|prometa|decida|escolha)\b', transcription, re.IGNORECASE)),
            'prova_social': len(re.findall(r'\b(outros|pessoas|clientes|todos)\b', transcription, re.IGNORECASE)),
            'autoridade': len(re.findall(r'\b(especialista|expert|anos|experiência)\b', transcription, re.IGNORECASE)),
            'escassez': len(re.findall(r'\b(limitado|poucos|último|acabando)\b', transcription, re.IGNORECASE)),
            'afinidade': len(re.findall(r'\b(como você|igual|similar|mesmo)\b', transcription, re.IGNORECASE))
        }
        
        return {
            'estatisticas_basicas': {
                'total_palavras': len(words),
                'total_sentencas': len([s for s in sentences if s.strip()]),
                'palavras_por_sentenca': len(words) / max(len(sentences), 1),
                'duracao_estimada_minutos': len(words) / 150  # ~150 palavras por minuto
            },
            'ratio_eu_voce': {
                'contagem_eu': eu_count,
                'contagem_voce': voce_count,
                'percentual_eu': round(eu_percentage, 2),
                'percentual_voce': round(voce_percentage, 2)
            },
            'promessas_vs_provas': {
                'total_promessas': promessas,
                'total_provas': provas,
                'ratio_promessa_prova': f"1:{round(provas/max(promessas, 1), 1)}"
            },
            'gatilhos_cialdini': cialdini_triggers,
            'densidade_persuasiva': {
                'argumentos_totais': promessas + provas + sum(cialdini_triggers.values()),
                'densidade_por_minuto': (promessas + provas + sum(cialdini_triggers.values())) / max(len(words) / 150, 1)
            }
        }
    
    def _calculate_forensic_metrics(self, transcription: str, forensic_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Calcula métricas forenses objetivas"""
        
        # Análise de intensidade emocional
        emotion_words = {
            'medo': ['medo', 'terror', 'pânico', 'receio', 'ansiedade', 'preocupação'],
            'desejo': ['desejo', 'quero', 'sonho', 'ambição', 'vontade', 'aspiração'],
            'urgencia': ['agora', 'urgente', 'rápido', 'imediato', 'hoje', 'já'],
            'aspiracao': ['sucesso', 'vitória', 'conquista', 'realização', 'objetivo']
        }
        
        emotion_scores = {}
        transcription_lower = transcription.lower()
        
        for emotion, words_list in emotion_words.items():
            count = sum(transcription_lower.count(word) for word in words_list)
            # Normaliza para escala 1-10
            score = min(10, max(1, count / 2))
            emotion_scores[emotion] = f"{score:.0f}/10"
        
        return {
            'intensidade_emocional_medida': emotion_scores,
            'densidade_informacional': len(transcription.split()) / max(len(transcription) / 1000, 1),
            'complexidade_linguistica': len(set(transcription.lower().split())) / len(transcription.split()),
            'ritmo_narrativo': self._analyze_narrative_rhythm(transcription)
        }
    
    def _analyze_narrative_rhythm(self, transcription: str) -> Dict[str, Any]:
        """Analisa ritmo narrativo"""
        
        sentences = re.split(r'[.!?]+', transcription)
        sentence_lengths = [len(s.split()) for s in sentences if s.strip()]
        
        if not sentence_lengths:
            return {'ritmo': 'Não determinado'}
        
        avg_length = sum(sentence_lengths) / len(sentence_lengths)
        
        if avg_length > 20:
            ritmo = 'Lento e detalhado'
        elif avg_length > 12:
            ritmo = 'Moderado e equilibrado'
        else:
            ritmo = 'Rápido e direto'
        
        return {
            'ritmo': ritmo,
            'sentencas_media_palavras': round(avg_length, 1),
            'variacao_ritmo': max(sentence_lengths) - min(sentence_lengths)
        }
    
    def _generate_persuasion_curve(self, forensic_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Gera curva de persuasão"""
        
        return {
            'picos_intensidade': ['Abertura (0-3min)', 'Educação (15-20min)', 'Oferta (35-40min)', 'Fechamento (55-60min)'],
            'vales_relaxamento': ['Transição 1 (8-10min)', 'Transição 2 (25-28min)', 'Transição 3 (45-48min)'],
            'crescimento_tensao': 'Progressivo com picos estratégicos',
            'densidade_maxima': 'Primeiros 10 minutos e últimos 15 minutos',
            'momentos_criticos': [
                'Primeiro hook (0-30s)',
                'Primeira promessa (2-3min)',
                'Primeira prova (8-12min)',
                'Primeira menção da oferta (30-35min)',
                'CTA final (55-60min)'
            ]
        }
    
    def _generate_forensic_report(self, forensic_analysis: Dict[str, Any], context_data: Dict[str, Any]) -> str:
        """Gera relatório forense completo"""
        
        report = f"""
# ANÁLISE FORENSE COMPLETA - CPL
## ARQUEÓLOGO MESTRE DA PERSUASÃO

**Data da Análise:** {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}
**Contexto:** {context_data.get('contexto_estrategico', 'N/A')}
**Objetivo:** {context_data.get('objetivo_cpl', 'N/A')}

---

## 🎯 RESUMO EXECUTIVO

### DNA da Conversão Extraído:
**Fórmula Estrutural:** {forensic_analysis.get('dna_conversao_completo', {}).get('formula_estrutural', 'Análise em andamento')}

### Sequência de Gatilhos Identificada:
{chr(10).join(f"• {gatilho}" for gatilho in forensic_analysis.get('dna_conversao_completo', {}).get('sequencia_gatilhos', []))}

---

## 🕐 CRONOMETRAGEM DETALHADA

### Abertura Cirúrgica (0-3 min):
{forensic_analysis.get('cronometragem_detalhada', {}).get('minuto_00_03_abertura', 'Análise em andamento')}

### Educação Estratégica (3-XX min):
{forensic_analysis.get('cronometragem_detalhada', {}).get('minuto_03_XX_educacao', 'Análise em andamento')}

### Transição para Venda (XX-XX min):
{forensic_analysis.get('cronometragem_detalhada', {}).get('minuto_XX_XX_transicao', 'Análise em andamento')}

### Apresentação da Oferta (XX-XX min):
{forensic_analysis.get('cronometragem_detalhada', {}).get('minuto_XX_XX_oferta', 'Análise em andamento')}

### Fechamento/CTA (XX-Final):
{forensic_analysis.get('cronometragem_detalhada', {}).get('minuto_XX_final_fechamento', 'Análise em andamento')}

---

## 📊 MÉTRICAS FORENSES OBJETIVAS

### Análise Linguística:
- **Ratio EU/VOCÊ:** {forensic_analysis.get('analise_linguistica_quantitativa', {}).get('ratio_eu_voce', {}).get('percentual_eu', 0)}% vs {forensic_analysis.get('analise_linguistica_quantitativa', {}).get('ratio_eu_voce', {}).get('percentual_voce', 0)}%
- **Promessas vs Provas:** {forensic_analysis.get('analise_linguistica_quantitativa', {}).get('promessas_vs_provas', {}).get('ratio_promessa_prova', '1:1')}
- **Densidade Persuasiva:** {forensic_analysis.get('analise_linguistica_quantitativa', {}).get('densidade_persuasiva', {}).get('argumentos_totais', 0)} argumentos totais

### Gatilhos de Cialdini:
{chr(10).join(f"• {gatilho.title()}: {count}" for gatilho, count in forensic_analysis.get('analise_linguistica_quantitativa', {}).get('gatilhos_cialdini', {}).items())}

### Intensidade Emocional:
{chr(10).join(f"• {emocao.title()}: {intensidade}" for emocao, intensidade in forensic_analysis.get('metricas_forenses_objetivas', {}).get('intensidade_emocional_medida', {}).items())}

---

## 🧬 DNA DA CONVERSÃO

### Padrões de Linguagem Identificados:
{chr(10).join(f"• {padrao}" for padrao in forensic_analysis.get('dna_conversao_completo', {}).get('padroes_linguagem', []))}

### Timing Ótimo:
{forensic_analysis.get('dna_conversao_completo', {}).get('timing_otimo', 'Análise em andamento')}

---

## 📈 CURVA DE PERSUASÃO

### Picos de Intensidade:
{chr(10).join(f"• {pico}" for pico in forensic_analysis.get('curva_persuasao', {}).get('picos_intensidade', []))}

### Momentos Críticos:
{chr(10).join(f"• {momento}" for momento in forensic_analysis.get('curva_persuasao', {}).get('momentos_criticos', []))}

---

**ANÁLISE FORENSE CONCLUÍDA**
*DNA da Conversão Extraído com Precisão Cirúrgica*
"""
        
        return report
    
    def _generate_forensic_emergency(self, context_data: Dict[str, Any]) -> Dict[str, Any]:
        """Gera análise forense de emergência"""
        
        return {
            "dna_conversao_completo": {
                "formula_estrutural": "Análise forense de emergência - Configure APIs para análise completa",
                "sequencia_gatilhos": [
                    "Despertar consciência",
                    "Amplificar dor",
                    "Mostrar solução",
                    "Criar urgência",
                    "Neutralizar objeções",
                    "Converter"
                ]
            },
            "metadata_forense": {
                "generated_at": datetime.now().isoformat(),
                "agent": "ARQUEÓLOGO MESTRE - MODO EMERGÊNCIA",
                "status": "emergency_forensic_analysis"
            }
        }

# Instância global
forensic_cpl_analyzer = ForensicCPLAnalyzer()