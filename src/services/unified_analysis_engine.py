#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ARQV30 Enhanced v2.0 - Unified Analysis Engine
Motor de análise unificado que combina todas as capacidades
"""

import logging
import time
import json
from typing import Dict, List, Any, Optional
from datetime import datetime
from services.ai_manager import ai_manager
from services.unified_search_manager import unified_search_manager
from services.robust_content_extractor import robust_content_extractor
from services.pymupdf_client import pymupdf_client
from services.exa_client import exa_client
from services.mental_drivers_architect import mental_drivers_architect
from services.visual_proofs_generator import visual_proofs_generator
from services.anti_objection_system import anti_objection_system
from services.pre_pitch_architect import pre_pitch_architect
from services.archaeological_master import archaeological_master
from services.visceral_master_agent import visceral_master
from services.visual_proofs_director import visual_proofs_director
from services.forensic_cpl_analyzer import forensic_cpl_analyzer
from services.visceral_leads_engineer import visceral_leads_engineer
from services.pre_pitch_architect_advanced import pre_pitch_architect_advanced
from services.auto_save_manager import auto_save_manager, salvar_etapa, salvar_erro

logger = logging.getLogger(__name__)

class UnifiedAnalysisEngine:
    """Motor de análise unificado com todas as capacidades"""

    def __init__(self):
        """Inicializa o motor unificado"""
        self.analysis_types = {
            'standard': 'Análise Padrão Ultra-Detalhada',
            'archaeological': 'Análise Arqueológica (12 Camadas)',
            'forensic_cpl': 'Análise Forense de CPL',
            'visceral_leads': 'Engenharia Reversa de Leads',
            'pre_pitch': 'Orquestração de Pré-Pitch',
            'complete': 'Análise Completa Unificada'
        }

        self.available_agents = {
            'arqueologist': archaeological_master,
            'visceral_master': visceral_master,
            'visual_director': visual_proofs_director,
            'drivers_architect': mental_drivers_architect,
            'anti_objection': anti_objection_system,
            'pre_pitch_architect': pre_pitch_architect,
            'forensic_cpl': forensic_cpl_analyzer,
            'visceral_leads': visceral_leads_engineer,
            'pre_pitch_advanced': pre_pitch_architect_advanced
        }

        logger.info("🚀 Unified Analysis Engine inicializado")

    def _validate_required_apis(self):
        """Valida se as APIs obrigatórias estão disponíveis"""

        # Verifica se há pelo menos uma IA disponível
        ai_available = False
        for provider_name, provider in ai_manager.providers.items():
            if provider['available']:
                ai_available = True
                break

        if not ai_available:
            raise Exception(
                "❌ NENHUMA API DE IA CONFIGURADA\n\n"
                "Configure pelo menos uma:\n"
                "- GEMINI_API_KEY (Recomendado)\n"
                "- OPENAI_API_KEY\n"
                "- GROQ_API_KEY\n"
                "- HUGGINGFACE_API_KEY"
            )

        # Verifica se há pesquisa web disponível
        search_status = unified_search_manager.get_provider_status()
        search_available = any(status.get('available', False) for status in search_status.values())

        if not search_available:
            raise Exception(
                "❌ NENHUMA API DE PESQUISA CONFIGURADA\n\n"
                "Configure pelo menos uma:\n"
                "- EXA_API_KEY (Recomendado)\n"
                "- GOOGLE_API_KEY + GOOGLE_CSE_ID\n"
                "- SERPER_API_KEY"
            )

        logger.info("✅ APIs obrigatórias validadas com sucesso")

    def execute_unified_analysis(
        self,
        data: Dict[str, Any],
        analysis_type: str = 'complete',
        session_id: str = None,
        progress_callback: Optional[callable] = None
    ) -> Dict[str, Any]:
        """Executa análise unificada com tipo especificado"""

        # VALIDAÇÃO CRÍTICA: APIs obrigatórias
        self._validate_required_apis()

        logger.info(f"🚀 Iniciando análise unificada: {analysis_type}")
        start_time = time.time()

        # Inicia sessão se não fornecida
        if not session_id:
            session_id = auto_save_manager.iniciar_sessao()

        # Salva início da análise
        salvar_etapa("analise_unificada_iniciada", {
            "data": data,
            "analysis_type": analysis_type,
            "session_id": session_id,
            "available_agents": list(self.available_agents.keys())
        }, categoria="analise_completa")

        try:
            if analysis_type == 'complete':
                return self._execute_complete_unified_analysis(data, session_id, progress_callback)
            elif analysis_type == 'archaeological':
                return self._execute_archaeological_analysis(data, session_id, progress_callback)
            elif analysis_type == 'forensic_cpl':
                return self._execute_forensic_cpl_analysis(data, session_id, progress_callback)
            elif analysis_type == 'visceral_leads':
                return self._execute_visceral_leads_analysis(data, session_id, progress_callback)
            elif analysis_type == 'pre_pitch':
                return self._execute_pre_pitch_analysis(data, session_id, progress_callback)
            else:
                return self._execute_standard_analysis(data, session_id, progress_callback)

        except Exception as e:
            logger.error(f"❌ Erro na análise unificada: {e}")
            salvar_erro("analise_unificada_erro", e, contexto=data)
            raise e

    def _execute_complete_unified_analysis(
        self,
        data: Dict[str, Any],
        session_id: str,
        progress_callback: Optional[callable] = None
    ) -> Dict[str, Any]:
        """Executa análise completa unificada com todos os agentes"""

        if progress_callback:
            progress_callback(1, "🔍 Iniciando análise completa unificada...")

        # 1. Pesquisa unificada
        if progress_callback:
            progress_callback(2, "🌐 Executando pesquisa unificada (Exa + Google + Serper)...")

        search_query = data.get('query') or f"mercado {data.get('segmento', 'negócios')} Brasil 2024"
        search_results = unified_search_manager.unified_search(search_query, max_results=25, context=data, session_id=session_id)

        # 2. Extração de conteúdo avançada
        if progress_callback:
            progress_callback(3, "📄 Extraindo conteúdo com PyMuPDF Pro + extratores robustos...")

        extracted_content = self._extract_unified_content(search_results, session_id)

        # 3. Análise arqueológica
        if progress_callback:
            progress_callback(4, "🔬 Executando análise arqueológica (12 camadas)...")

        archaeological_analysis = archaeological_master.execute_archaeological_analysis(
            data, 
            research_context=json.dumps(extracted_content, ensure_ascii=False)[:15000],
            session_id=session_id
        )

        # 4. Engenharia reversa visceral
        if progress_callback:
            progress_callback(5, "🧠 Executando engenharia reversa visceral...")

        visceral_analysis = visceral_master.execute_visceral_analysis(
            data,
            research_data=extracted_content,
            session_id=session_id
        )

        # 5. Arsenal de drivers mentais
        if progress_callback:
            progress_callback(6, "⚙️ Criando arsenal de drivers mentais...")

        avatar_data = visceral_analysis.get('avatar_visceral_ultra', {})
        if not avatar_data:
            avatar_data = archaeological_analysis.get('avatar_arqueologico_ultra', {})

        drivers_system = mental_drivers_architect.generate_complete_drivers_system(avatar_data, data)

        # 6. Arsenal de PROVIs
        if progress_callback:
            progress_callback(7, "🎭 Criando arsenal de PROVIs devastadoras...")

        concepts_to_prove = self._extract_concepts_for_proofs(avatar_data, drivers_system, data)
        provis_system = visual_proofs_director.execute_provis_creation(
            concepts_to_prove,
            avatar_data,
            drivers_system,
            data,
            session_id
        )

        # 7. Sistema anti-objeção
        if progress_callback:
            progress_callback(8, "🛡️ Construindo sistema anti-objeção...")

        objections_list = avatar_data.get('muralhas_desconfianca_objecoes', [])
        if not objections_list:
            objections_list = [
                "Não tenho tempo para implementar isso agora",
                "Preciso pensar melhor sobre o investimento",
                "Meu caso é muito específico",
                "Já tentei outras coisas e não deram certo"
            ]

        anti_objection_system_result = anti_objection_system.generate_complete_anti_objection_system(
            objections_list, avatar_data, data
        )

        # 8. Pré-pitch invisível
        if progress_callback:
            progress_callback(9, "🎯 Orquestrando pré-pitch invisível...")

        drivers_list = drivers_system.get('drivers_customizados', [])
        pre_pitch_system = pre_pitch_architect_advanced.orchestrate_psychological_symphony(
            drivers_list, avatar_data, 
            data.get('event_structure', 'Webinar/Live/Evento'),
            data.get('product_offer', f"Produto: {data.get('produto', 'N/A')} - Preço: R$ {data.get('preco', 'N/A')}"),
            session_id
        )

        # 9. Consolidação final
        if progress_callback:
            progress_callback(10, "✨ Consolidando análise unificada...")

        unified_analysis = {
            'tipo_analise': 'completa_unificada',
            'projeto_dados': data,
            'pesquisa_unificada': search_results,
            'conteudo_extraido': extracted_content,
            'analise_arqueologica': archaeological_analysis,
            'engenharia_reversa_visceral': visceral_analysis,
            'arsenal_drivers_mentais': drivers_system,
            'arsenal_provas_visuais': provis_system,
            'sistema_anti_objecao': anti_objection_system_result,
            'pre_pitch_invisivel': pre_pitch_system,
            'agentes_utilizados': [
                'ARQUEÓLOGO MESTRE DA PERSUASÃO',
                'MESTRE DA PERSUASÃO VISCERAL',
                'ARQUITETO DE DRIVERS MENTAIS',
                'DIRETOR SUPREMO DE EXPERIÊNCIAS',
                'ESPECIALISTA EM PSICOLOGIA DE VENDAS',
                'MESTRE DO PRÉ-PITCH INVISÍVEL'
            ],
            'tecnologias_utilizadas': [
                'Exa Neural Search',
                'Google Custom Search',
                'PyMuPDF Pro',
                'Gemini 2.5 Pro',
                'Sistema de Extração Robusto'
            ]
        }

        # Adiciona metadados finais
        processing_time = time.time() - start_time
        unified_analysis['metadata_unificado'] = {
            'processing_time_seconds': processing_time,
            'processing_time_formatted': f"{int(processing_time // 60)}m {int(processing_time % 60)}s",
            'analysis_engine': 'ARQV30 Enhanced v2.0 - UNIFIED',
            'generated_at': datetime.now().isoformat(),
            'session_id': session_id,
            'providers_used': len(search_results.get('provider_results', {})),
            'total_sources': search_results.get('statistics', {}).get('total_results', 0),
            'brazilian_sources': search_results.get('statistics', {}).get('brazilian_sources', 0),
            'exa_enhanced': exa_client.is_available(),
            'pymupdf_pro': pymupdf_client.is_available(),
            'analysis_completeness': 'MAXIMUM'
        }

        # Salva análise unificada final
        salvar_etapa("analise_unificada_final", unified_analysis, categoria="analise_completa")

        logger.info(f"✅ Análise unificada concluída em {processing_time:.2f}s")
        return unified_analysis

    def _extract_unified_content(self, search_results: Dict[str, Any], session_id: str) -> Dict[str, Any]:
        """Extrai conteúdo usando todos os extratores disponíveis"""

        results = search_results.get('results', [])
        extracted_content = []
        pdf_content = []

        for i, result in enumerate(results[:15]):  # Top 15 resultados
            url = result.get('url', '')

            try:
                # Verifica se é PDF
                if url.lower().endswith('.pdf') or 'pdf' in url.lower():
                    # Usa PyMuPDF Pro para PDFs
                    if pymupdf_client.is_available():
                        pdf_result = pymupdf_client.extract_from_url(url)
                        if pdf_result['success']:
                            pdf_content.append({
                                'url': url,
                                'title': result.get('title', ''),
                                'content': pdf_result['text'],
                                'metadata': pdf_result['metadata'],
                                'statistics': pdf_result['statistics'],
                                'extraction_method': 'PyMuPDF_Pro'
                            })
                            continue

                # Usa extrator robusto para páginas web
                content = robust_content_extractor.extract_content(url)
                if content and len(content) > 200:
                    extracted_content.append({
                        'url': url,
                        'title': result.get('title', ''),
                        'content': content,
                        'source': result.get('source', 'unknown'),
                        'is_brazilian': result.get('is_brazilian', False),
                        'is_preferred': result.get('is_preferred', False),
                        'extraction_method': 'robust_extractor'
                    })

                # Delay para rate limiting
                time.sleep(0.3)

            except Exception as e:
                logger.error(f"❌ Erro ao extrair {url}: {e}")
                continue

        # Combina conteúdo extraído
        combined_content = {
            'web_content': extracted_content,
            'pdf_content': pdf_content,
            'statistics': {
                'total_web_pages': len(extracted_content),
                'total_pdf_pages': len(pdf_content),
                'total_content_length': sum(len(item['content']) for item in extracted_content + pdf_content),
                'extraction_success_rate': (len(extracted_content) + len(pdf_content)) / len(results) * 100 if results else 0
            }
        }

        # Salva conteúdo extraído
        salvar_etapa("conteudo_unificado_extraido", combined_content, categoria="pesquisa_web")

        return combined_content

    def _extract_concepts_for_proofs(
        self, 
        avatar_data: Dict[str, Any], 
        drivers_data: Dict[str, Any], 
        context_data: Dict[str, Any]
    ) -> List[str]:
        """Extrai conceitos que precisam de prova visual"""

        concepts = []

        # Conceitos do avatar
        if avatar_data.get('feridas_abertas_inconfessaveis'):
            concepts.extend(avatar_data['feridas_abertas_inconfessaveis'][:5])

        if avatar_data.get('sonhos_proibidos_ardentes'):
            concepts.extend(avatar_data['sonhos_proibidos_ardentes'][:5])

        # Conceitos dos drivers
        if drivers_data.get('drivers_customizados'):
            for driver in drivers_data['drivers_customizados'][:3]:
                concepts.append(driver.get('nome', 'Driver Mental'))

        # Conceitos gerais críticos
        concepts.extend([
            "Eficácia do método",
            "Transformação real possível",
            "ROI do investimento",
            "Diferencial da concorrência",
            "Tempo para resultados"
        ])

        return concepts[:12]  # Máximo 12 conceitos

    def _execute_archaeological_analysis(
        self,
        data: Dict[str, Any],
        session_id: str,
        progress_callback: Optional[callable] = None
    ) -> Dict[str, Any]:
        """Executa apenas análise arqueológica"""

        if progress_callback:
            progress_callback(1, "🔬 Iniciando análise arqueológica...")

        # Pesquisa unificada
        search_query = data.get('query') or f"mercado {data.get('segmento', 'negócios')} Brasil 2024"
        search_results = unified_search_manager.unified_search(search_query, context=data, session_id=session_id)

        # Análise arqueológica
        archaeological_result = archaeological_master.execute_archaeological_analysis(
            data,
            research_context=json.dumps(search_results, ensure_ascii=False)[:15000],
            session_id=session_id
        )

        return {
            'tipo_analise': 'arqueologica',
            'projeto_dados': data,
            'pesquisa_unificada': search_results,
            'analise_arqueologica': archaeological_result,
            'metadata': {
                'analysis_type': 'archaeological',
                'session_id': session_id,
                'generated_at': datetime.now().isoformat()
            }
        }

    def _execute_forensic_cpl_analysis(
        self,
        data: Dict[str, Any],
        session_id: str,
        progress_callback: Optional[callable] = None
    ) -> Dict[str, Any]:
        """Executa análise forense de CPL"""

        if progress_callback:
            progress_callback(1, "🔬 Iniciando análise forense de CPL...")

        transcription = data.get('transcription', '')
        context_data = {
            'contexto_estrategico': data.get('contexto_estrategico', ''),
            'objetivo_cpl': data.get('objetivo_cpl', ''),
            'formato': data.get('formato', ''),
            'temperatura_audiencia': data.get('temperatura_audiencia', '')
        }

        forensic_result = forensic_cpl_analyzer.analyze_cpl_forensically(
            transcription, context_data, session_id
        )

        return {
            'tipo_analise': 'forense_cpl',
            'projeto_dados': data,
            'analise_forense_cpl': forensic_result,
            'metadata': {
                'analysis_type': 'forensic_cpl',
                'session_id': session_id,
                'generated_at': datetime.now().isoformat()
            }
        }

    def _execute_visceral_leads_analysis(
        self,
        data: Dict[str, Any],
        session_id: str,
        progress_callback: Optional[callable] = None
    ) -> Dict[str, Any]:
        """Executa engenharia reversa de leads"""

        if progress_callback:
            progress_callback(1, "🧠 Iniciando engenharia reversa visceral...")

        leads_data = data.get('leads_data', '')
        context_data = {
            'produto_servico': data.get('produto_servico', ''),
            'principais_perguntas': data.get('principais_perguntas', ''),
            'numero_respostas': data.get('numero_respostas', 0)
        }

        visceral_result = visceral_leads_engineer.reverse_engineer_leads(
            leads_data, context_data, session_id
        )

        return {
            'tipo_analise': 'visceral_leads',
            'projeto_dados': data,
            'engenharia_reversa_leads': visceral_result,
            'metadata': {
                'analysis_type': 'visceral_leads',
                'session_id': session_id,
                'generated_at': datetime.now().isoformat()
            }
        }

    def _execute_pre_pitch_analysis(
        self,
        data: Dict[str, Any],
        session_id: str,
        progress_callback: Optional[callable] = None
    ) -> Dict[str, Any]:
        """Executa orquestração de pré-pitch"""

        if progress_callback:
            progress_callback(1, "🎯 Iniciando orquestração de pré-pitch...")

        selected_drivers = data.get('selected_drivers', [])
        avatar_data = data.get('avatar_data', {})
        event_structure = data.get('event_structure', '')
        product_offer = data.get('product_offer', '')

        pre_pitch_result = pre_pitch_architect_advanced.orchestrate_psychological_symphony(
            selected_drivers, avatar_data, event_structure, product_offer, session_id
        )

        return {
            'tipo_analise': 'pre_pitch',
            'projeto_dados': data,
            'orquestracao_pre_pitch': pre_pitch_result,
            'metadata': {
                'analysis_type': 'pre_pitch',
                'session_id': session_id,
                'generated_at': datetime.now().isoformat()
            }
        }

    def _execute_standard_analysis(
        self,
        data: Dict[str, Any],
        session_id: str,
        progress_callback: Optional[callable] = None
    ) -> Dict[str, Any]:
        """Executa análise padrão unificada"""

        if progress_callback:
            progress_callback(1, "🔍 Iniciando análise padrão unificada...")

        # Pesquisa unificada
        search_query = data.get('query') or f"mercado {data.get('segmento', 'negócios')} Brasil 2024"
        search_results = unified_search_manager.unified_search(search_query, context=data, session_id=session_id)

        # Extração de conteúdo
        extracted_content = self._extract_unified_content(search_results, session_id)

        # Análise com IA
        analysis_prompt = self._build_unified_analysis_prompt(data, extracted_content)
        ai_response = ai_manager.generate_analysis(analysis_prompt, max_tokens=8192)

        if not ai_response:
            raise Exception("IA não respondeu para análise unificada")

        # Processa resposta
        ai_analysis = self._process_ai_response(ai_response, data)

        return {
            'tipo_analise': 'padrao_unificada',
            'projeto_dados': data,
            'pesquisa_unificada': search_results,
            'conteudo_extraido': extracted_content,
            'analise_ia': ai_analysis,
            'metadata': {
                'analysis_type': 'standard_unified',
                'session_id': session_id,
                'generated_at': datetime.now().isoformat()
            }
        }

    def _build_unified_analysis_prompt(self, data: Dict[str, Any], content: Dict[str, Any]) -> str:
        """Constrói prompt unificado para análise"""

        web_content = content.get('web_content', [])
        pdf_content = content.get('pdf_content', [])

        content_summary = ""

        # Resumo do conteúdo web
        if web_content:
            content_summary += "CONTEÚDO WEB EXTRAÍDO:\n"
            for i, item in enumerate(web_content[:10], 1):
                content_summary += f"FONTE {i}: {item['title']}\n"
                content_summary += f"URL: {item['url']}\n"
                content_summary += f"Conteúdo: {item['content'][:1500]}\n\n"

        # Resumo do conteúdo PDF
        if pdf_content:
            content_summary += "CONTEÚDO PDF EXTRAÍDO:\n"
            for i, item in enumerate(pdf_content[:5], 1):
                content_summary += f"PDF {i}: {item['title']}\n"
                content_summary += f"Páginas: {item['statistics']['pages']}\n"
                content_summary += f"Conteúdo: {item['content'][:2000]}\n\n"

        prompt = f"""
# ANÁLISE UNIFICADA ULTRA-DETALHADA - ARQV30 ENHANCED v2.0

Você é o DIRETOR SUPREMO DE ANÁLISE UNIFICADA, especialista de elite que combina todas as metodologias.

## DADOS DO PROJETO:
- **Segmento**: {data.get('segmento', 'Não informado')}
- **Produto/Serviço**: {data.get('produto', 'Não informado')}
- **Público-Alvo**: {data.get('publico', 'Não informado')}
- **Preço**: R$ {data.get('preco', 'Não informado')}
- **Objetivo de Receita**: R$ {data.get('objetivo_receita', 'Não informado')}

## PESQUISA UNIFICADA REALIZADA:
{content_summary[:15000]}

## GERE ANÁLISE UNIFICADA COMPLETA:

```json
{{
  "avatar_unificado": {{
    "nome_ficticio": "Nome específico baseado em dados reais",
    "perfil_demografico_completo": {{
      "idade": "Faixa etária com dados reais",
      "genero": "Distribuição real",
      "renda": "Faixa de renda real",
      "escolaridade": "Nível educacional real",
      "localizacao": "Regiões geográficas reais"
    }},
    "perfil_psicografico_profundo": {{
      "personalidade": "Traços dominantes reais",
      "valores": "Valores e crenças reais",
      "comportamento_compra": "Processo real de decisão",
      "medos_profundos": "Medos reais documentados",
      "aspiracoes_secretas": "Aspirações reais"
    }},
    "dores_viscerais_unificadas": [
      "Lista de 15-20 dores específicas baseadas em dados reais"
    ],
    "desejos_secretos_unificados": [
      "Lista de 15-20 desejos profundos baseados em estudos"
    ],
    "jornada_emocional_completa": {{
      "consciencia": "Como toma consciência baseado em dados",
      "consideracao": "Processo real de avaliação",
      "decisao": "Fatores decisivos reais",
      "pos_compra": "Experiência pós-compra real"
    }}
  }},

  "posicionamento_unificado": {{
    "proposta_valor_unica": "Proposta irresistível baseada em gaps",
    "diferenciais_competitivos": [
      "Lista de diferenciais únicos e defensáveis"
    ],
    "mensagem_central": "Mensagem principal que resume tudo",
    "estrategia_oceano_azul": "Como criar mercado sem concorrência"
  }},

  "insights_unificados": [
    "Lista de 25-30 insights únicos e ultra-valiosos baseados na análise completa"
  ],

  "estrategia_implementacao": {{
    "fase_1_preparacao": {{
      "duracao": "Tempo necessário",
      "atividades": ["Lista de atividades específicas"],
      "investimento": "Investimento necessário"
    }},
    "fase_2_execucao": {{
      "duracao": "Tempo necessário", 
      "atividades": ["Lista de atividades específicas"],
      "investimento": "Investimento necessário"
    }},
    "fase_3_otimizacao": {{
      "duracao": "Tempo necessário",
      "atividades": ["Lista de atividades específicas"],
      "investimento": "Investimento necessário"
    }}
  }}
}}
```

CRÍTICO: Use APENAS dados REAIS da pesquisa unificada. Combine insights de todas as fontes.
"""

        return prompt

    def _process_ai_response(self, response: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Processa resposta da IA"""

        try:
            # Extrai JSON da resposta
            clean_text = response.strip()

            if "```json" in clean_text:
                start = clean_text.find("```json") + 7
                end = clean_text.rfind("```")
                clean_text = clean_text[start:end].strip()

            # Parseia JSON
            analysis = json.loads(clean_text)

            # Adiciona metadados
            analysis['metadata_ai'] = {
                'generated_at': datetime.now().isoformat(),
                'provider_used': 'unified_ai_manager',
                'analysis_type': 'unified_complete'
            }

            return analysis

        except json.JSONDecodeError as e:
            logger.error(f"❌ Erro ao parsear JSON: {e}")
            return self._create_fallback_analysis(data)

    def _create_fallback_analysis(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """FALLBACK REMOVIDO - Sistema exige análise com dados reais"""

        raise Exception(
            "❌ ANÁLISE COM DADOS REAIS OBRIGATÓRIA\n\n"
            "O sistema não aceita mais fallbacks ou simulações.\n"
            "Configure pelo menos uma API de IA (Gemini, OpenAI, Groq) e uma de pesquisa (Exa, Google).\n\n"
            "APIs necessárias:\n"
            "- GEMINI_API_KEY ou OPENAI_API_KEY ou GROQ_API_KEY\n"
            "- EXA_API_KEY ou GOOGLE_CSE_ID + GOOGLE_API_KEY\n\n"
            "Todas as análises devem ser baseadas em dados reais coletados da web."
        )

    def get_analysis_capabilities(self) -> Dict[str, Any]:
        """Retorna capacidades de análise disponíveis"""

        return {
            'analysis_types': self.analysis_types,
            'available_agents': {
                name: {
                    'available': True,
                    'description': f'Agente {name} disponível'
                } for name in self.available_agents.keys()
            },
            'search_providers': unified_search_manager.get_provider_status(),
            'extraction_capabilities': {
                'web_extraction': robust_content_extractor is not None,
                'pdf_extraction': pymupdf_client.is_available(),
                'exa_neural_search': exa_client.is_available()
            },
            'ai_providers': ai_manager.get_provider_status() if ai_manager else {}
        }

    def _extrair_secao(self, resultados: Dict[str, Any], chave: str, default: Any) -> Any:
        """Extrai uma seção específica dos resultados"""
        try:
            return resultados.get(chave, default)
        except Exception as e:
            logger.error(f"❌ Erro ao extrair seção {chave}: {e}")
            return default

    def _extrair_metricas(self, resultados: Dict[str, Any]) -> Dict[str, Any]:
        """Extrai métricas dos resultados"""
        metricas = {
            'total_fontes': 0,
            'qualidade_dados': 'média',
            'cobertura_analise': 0.0,
            'tempo_analise': 0,
            'componentes_executados': []
        }

        try:
            if 'web_search' in resultados:
                web_data = resultados['web_search']
                if isinstance(web_data, dict):
                    metricas['total_fontes'] = len(web_data.get('resultados', []))

            # Calcula cobertura da análise
            componentes_esperados = ['web_search', 'social_analysis', 'mental_drivers', 'future_predictions', 'avatar_detalhado']
            componentes_presentes = [comp for comp in componentes_esperados if comp in resultados]
            metricas['componentes_executados'] = componentes_presentes
            metricas['cobertura_analise'] = (len(componentes_presentes) / len(componentes_esperados)) * 100

            # Determina qualidade dos dados
            if metricas['cobertura_analise'] >= 80:
                metricas['qualidade_dados'] = 'alta'
            elif metricas['cobertura_analise'] >= 60:
                metricas['qualidade_dados'] = 'média'
            else:
                metricas['qualidade_dados'] = 'baixa'

        except Exception as e:
            logger.error(f"❌ Erro ao extrair métricas: {e}")

        return metricas

# Instância global
unified_analysis_engine = UnifiedAnalysisEngine()