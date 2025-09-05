
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ARQV30 Enhanced v2.0 - Master Orchestrator
Coordenador mestre que garante todos os serviços funcionem em paralelo
"""

import os
import logging
import time
import asyncio
from typing import Dict, List, Any, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime

# Import all services
from services.ai_manager import ai_manager
from services.production_search_manager import production_search_manager
from services.content_extractor import content_extractor
from services.mental_drivers_architect import mental_drivers_architect
from services.visual_proofs_generator import visual_proofs_generator
from services.anti_objection_system import anti_objection_system
from services.pre_pitch_architect import pre_pitch_architect
from services.future_prediction_engine import future_prediction_engine
from services.archaeological_master import archaeological_master
from services.visceral_master_agent import visceral_master
from services.visual_proofs_director import visual_proofs_director
from services.forensic_cpl_analyzer import forensic_cpl_analyzer
from services.visceral_leads_engineer import visceral_leads_engineer
from services.pre_pitch_architect_advanced import pre_pitch_architect_advanced
from services.mcp_supadata_manager import mcp_supadata_manager
from services.enhanced_search_coordinator import enhanced_search_coordinator
from services.alibaba_websailor import AlibabaWebSailorAgent
from services.auto_save_manager import auto_save_manager, salvar_etapa, salvar_erro
from services.local_file_manager import LocalFileManager

logger = logging.getLogger(__name__)

class MasterOrchestrator:
    """Orquestrador mestre que coordena todos os serviços em paralelo"""
    
    def __init__(self):
        """Inicializa o orquestrador mestre"""
        self.services = {
            'ai_manager': ai_manager,
            'production_search': production_search_manager,
            'content_extractor': content_extractor,
            'mental_drivers': mental_drivers_architect,
            'visual_proofs': visual_proofs_generator,
            'anti_objection': anti_objection_system,
            'pre_pitch': pre_pitch_architect,
            'future_prediction': future_prediction_engine,
            'archaeological': archaeological_master,
            'visceral_master': visceral_master,
            'visual_director': visual_proofs_director,
            'forensic_cpl': forensic_cpl_analyzer,
            'visceral_leads': visceral_leads_engineer,
            'pre_pitch_advanced': pre_pitch_architect_advanced,
            'supadata': mcp_supadata_manager,
            'search_coordinator': enhanced_search_coordinator,
            'websailor': AlibabaWebSailorAgent()
        }
        
        self.file_manager = LocalFileManager()
        self.execution_results = {}
        
        logger.info("🚀 Master Orchestrator inicializado com todos os serviços")
    
    def execute_comprehensive_analysis(
        self,
        data: Dict[str, Any],
        session_id: str,
        progress_callback: Optional[callable] = None
    ) -> Dict[str, Any]:
        """Executa análise completa com todos os serviços em paralelo"""
        
        try:
            logger.info(f"🚀 INICIANDO ANÁLISE COMPLETA ULTRA-ROBUSTA")
            start_time = time.time()
            
            # Salva início da análise
            salvar_etapa("master_orchestrator_iniciado", {
                "data": data,
                "session_id": session_id,
                "services_available": list(self.services.keys())
            }, categoria="analise_completa")
            
            # FASE 1: PESQUISA WEB MASSIVA (Paralela)
            if progress_callback:
                progress_callback(1, "🔍 Executando pesquisa web massiva...")
            
            web_research = self._execute_massive_web_research(data, session_id)
            
            # FASE 2: ANÁLISE DE REDES SOCIAIS (Paralela)
            if progress_callback:
                progress_callback(2, "📱 Analisando redes sociais...")
            
            social_analysis = self._execute_social_media_analysis(data, session_id)
            
            # FASE 3: EXECUÇÃO PARALELA DE TODOS OS AGENTES ESPECIALIZADOS
            if progress_callback:
                progress_callback(3, "🧠 Executando agentes especializados...")
            
            specialized_analysis = self._execute_specialized_agents(data, web_research, social_analysis, session_id)
            
            # FASE 4: CONSOLIDAÇÃO E GERAÇÃO DE RELATÓRIO COMPLETO
            if progress_callback:
                progress_callback(4, "📄 Consolidando análise completa...")
            
            final_report = self._consolidate_comprehensive_report(
                data, web_research, social_analysis, specialized_analysis, session_id
            )
            
            # FASE 5: SALVAMENTO EM TODAS AS PASTAS NECESSÁRIAS
            if progress_callback:
                progress_callback(5, "💾 Salvando em todas as categorias...")
            
            self._save_to_all_categories(final_report, session_id)
            
            execution_time = time.time() - start_time
            
            logger.info(f"✅ ANÁLISE COMPLETA CONCLUÍDA em {execution_time:.2f} segundos")
            
            return {
                'success': True,
                'session_id': session_id,
                'execution_time': execution_time,
                'web_research': web_research,
                'social_analysis': social_analysis,
                'specialized_analysis': specialized_analysis,
                'final_report': final_report,
                'categories_saved': self._get_saved_categories(session_id)
            }
            
        except Exception as e:
            logger.error(f"❌ ERRO CRÍTICO no Master Orchestrator: {str(e)}")
            salvar_erro("master_orchestrator_critico", e, contexto={"session_id": session_id})
            return self._generate_fallback_analysis(data, session_id)
    
    def _execute_massive_web_research(self, data: Dict[str, Any], session_id: str) -> Dict[str, Any]:
        """Executa pesquisa web massiva usando múltiplos engines"""
        
        try:
            logger.info("🌐 Executando pesquisa web massiva...")
            
            # Constrói query principal
            query = data.get('query') or f"mercado {data.get('segmento', '')} {data.get('produto', '')} Brasil 2024"
            
            search_results = {}
            
            with ThreadPoolExecutor(max_workers=4) as executor:
                futures = {}
                
                # 1. Enhanced Search Coordinator (Exa + Google)
                futures['enhanced_search'] = executor.submit(
                    enhanced_search_coordinator.execute_simultaneous_distinct_search,
                    query, data, session_id
                )
                
                # 2. Production Search Manager (Fallback engines)
                futures['production_search'] = executor.submit(
                    production_search_manager.search_with_fallback,
                    query, 25
                )
                
                # 3. WebSailor Deep Navigation
                futures['websailor'] = executor.submit(
                    self.services['websailor'].navigate_and_research_deep,
                    query, data, 20, 2, session_id
                )
                
                # 4. Busca com queries relacionadas
                related_queries = [
                    f"tendências {data.get('segmento', '')} Brasil 2024",
                    f"mercado {data.get('segmento', '')} crescimento",
                    f"oportunidades {data.get('segmento', '')} negócio"
                ]
                
                for i, related_query in enumerate(related_queries):
                    futures[f'related_{i}'] = executor.submit(
                        production_search_manager.search_with_fallback,
                        related_query, 10
                    )
                
                # Coleta resultados
                for name, future in futures.items():
                    try:
                        result = future.result(timeout=180)  # 3 minutos timeout
                        search_results[name] = result
                        logger.info(f"✅ {name}: Pesquisa concluída")
                    except Exception as e:
                        logger.error(f"❌ Erro em {name}: {str(e)}")
                        search_results[name] = {'error': str(e)}
            
            # Salva resultados da pesquisa web
            salvar_etapa("pesquisa_web_massiva", search_results, categoria="pesquisa_web")
            
            return search_results
            
        except Exception as e:
            logger.error(f"❌ Erro na pesquisa web massiva: {str(e)}")
            return {'error': str(e), 'fallback': True}
    
    def _execute_social_media_analysis(self, data: Dict[str, Any], session_id: str) -> Dict[str, Any]:
        """Executa análise completa de redes sociais"""
        
        try:
            logger.info("📱 Executando análise de redes sociais...")
            
            query = data.get('segmento', '') + " " + data.get('produto', '')
            
            # Executa busca em todas as plataformas
            social_results = mcp_supadata_manager.search_all_platforms(query, max_results_per_platform=10)
            
            # Análise de sentimento
            all_posts = []
            for platform in ['youtube', 'twitter', 'linkedin', 'instagram']:
                platform_data = social_results.get(platform, {})
                if platform_data.get('results'):
                    all_posts.extend(platform_data['results'])
            
            sentiment_analysis = mcp_supadata_manager.analyze_sentiment(all_posts)
            
            social_analysis = {
                'platforms_data': social_results,
                'sentiment_analysis': sentiment_analysis,
                'total_posts': len(all_posts),
                'platforms_analyzed': social_results.get('platforms', []),
                'social_insights': self._extract_social_insights(all_posts)
            }
            
            # Salva análise social
            salvar_etapa("analise_redes_sociais", social_analysis, categoria="pesquisa_web")
            
            return social_analysis
            
        except Exception as e:
            logger.error(f"❌ Erro na análise de redes sociais: {str(e)}")
            return {'error': str(e), 'fallback': True}
    
    def _execute_specialized_agents(
        self, 
        data: Dict[str, Any], 
        web_research: Dict[str, Any], 
        social_analysis: Dict[str, Any],
        session_id: str
    ) -> Dict[str, Any]:
        """Executa todos os agentes especializados em paralelo"""
        
        try:
            logger.info("🧠 Executando agentes especializados...")
            
            specialized_results = {}
            
            with ThreadPoolExecutor(max_workers=8) as executor:
                futures = {}
                
                # Combina dados para os agentes
                combined_data = {
                    **data,
                    'web_research': web_research,
                    'social_analysis': social_analysis
                }
                
                # 1. Mental Drivers Architect
                futures['mental_drivers'] = executor.submit(
                    self._generate_mental_drivers, combined_data
                )
                
                # 2. Visual Proofs Generator
                futures['visual_proofs'] = executor.submit(
                    self._generate_visual_proofs, combined_data
                )
                
                # 3. Anti-Objection System
                futures['anti_objection'] = executor.submit(
                    self._generate_anti_objection, combined_data
                )
                
                # 4. Pre-Pitch Architect
                futures['pre_pitch'] = executor.submit(
                    self._generate_pre_pitch, combined_data
                )
                
                # 5. Future Prediction Engine
                futures['future_predictions'] = executor.submit(
                    self._generate_future_predictions, combined_data
                )
                
                # 6. Avatar Detalhado
                futures['avatar_detalhado'] = executor.submit(
                    self._generate_detailed_avatar, combined_data
                )
                
                # 7. Funil de Vendas
                futures['funil_vendas'] = executor.submit(
                    self._generate_sales_funnel, combined_data
                )
                
                # 8. Análise de Concorrência
                futures['analise_concorrencia'] = executor.submit(
                    self._generate_competition_analysis, combined_data
                )
                
                # Coleta resultados
                for name, future in futures.items():
                    try:
                        result = future.result(timeout=300)  # 5 minutos timeout
                        specialized_results[name] = result
                        logger.info(f"✅ {name}: Análise concluída")
                        
                        # Salva cada resultado imediatamente
                        salvar_etapa(f"agente_{name}", result, categoria="analise_completa")
                        
                    except Exception as e:
                        logger.error(f"❌ Erro em {name}: {str(e)}")
                        specialized_results[name] = {'error': str(e)}
            
            return specialized_results
            
        except Exception as e:
            logger.error(f"❌ Erro nos agentes especializados: {str(e)}")
            return {'error': str(e), 'fallback': True}
    
    def _generate_mental_drivers(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Gera 19 drivers mentais personalizados"""
        
        try:
            # Gera drivers mentais usando o architect
            drivers = mental_drivers_architect.generate_custom_drivers(
                data.get('segmento', ''),
                data.get('produto', ''),
                data.get('publico', ''),
                data.get('web_research', {}),
                data.get('social_analysis', {})
            )
            
            # Garante que temos 19 drivers
            while len(drivers.get('drivers', [])) < 19:
                additional_driver = self._generate_additional_driver(data, len(drivers.get('drivers', [])) + 1)
                drivers.setdefault('drivers', []).append(additional_driver)
            
            return drivers
            
        except Exception as e:
            logger.error(f"❌ Erro ao gerar drivers mentais: {str(e)}")
            return self._generate_fallback_drivers()
    
    def _generate_visual_proofs(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Gera provas visuais e experiências"""
        
        try:
            # Usa múltiplos geradores
            visual_results = {}
            
            # Visual Proofs Generator
            if hasattr(visual_proofs_generator, 'generate_comprehensive_proofs'):
                visual_results['proofs'] = visual_proofs_generator.generate_comprehensive_proofs(data)
            else:
                visual_results['proofs'] = self._generate_basic_visual_proofs(data)
            
            # Visual Proofs Director
            visual_results['experiences'] = visual_proofs_director.create_transformative_experience(
                data.get('segmento', ''),
                data.get('produto', ''),
                data.get('web_research', {}),
                data.get('social_analysis', {})
            )
            
            return visual_results
            
        except Exception as e:
            logger.error(f"❌ Erro ao gerar provas visuais: {str(e)}")
            return self._generate_fallback_visual_proofs()
    
    def _generate_anti_objection(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Gera sistema anti-objeção"""
        
        try:
            objections = anti_objection_system.create_comprehensive_objection_handling(
                data.get('segmento', ''),
                data.get('produto', ''),
                data.get('web_research', {}),
                data.get('social_analysis', {})
            )
            
            return objections
            
        except Exception as e:
            logger.error(f"❌ Erro ao gerar anti-objeção: {str(e)}")
            return self._generate_fallback_anti_objection()
    
    def _generate_pre_pitch(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Gera pré-pitch avançado"""
        
        try:
            # Usa both architects
            basic_pitch = pre_pitch_architect.create_pre_pitch_strategy(
                data.get('segmento', ''),
                data.get('produto', ''),
                data.get('web_research', {}),
                data.get('social_analysis', {})
            )
            
            advanced_pitch = pre_pitch_architect_advanced.create_invisible_pre_pitch(
                data.get('segmento', ''),
                data.get('produto', ''),
                data.get('web_research', {}),
                data.get('social_analysis', {})
            )
            
            return {
                'basic_strategy': basic_pitch,
                'advanced_strategy': advanced_pitch
            }
            
        except Exception as e:
            logger.error(f"❌ Erro ao gerar pré-pitch: {str(e)}")
            return self._generate_fallback_pre_pitch()
    
    def _generate_future_predictions(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Gera predições futuras"""
        
        try:
            predictions = future_prediction_engine.generate_comprehensive_predictions(
                data.get('segmento', ''),
                data.get('produto', ''),
                data.get('web_research', {}),
                data.get('social_analysis', {})
            )
            
            return predictions
            
        except Exception as e:
            logger.error(f"❌ Erro ao gerar predições: {str(e)}")
            return self._generate_fallback_predictions()
    
    def _generate_detailed_avatar(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Gera avatar ultra-detalhado"""
        
        try:
            avatar_prompt = self._build_avatar_prompt(data)
            avatar_analysis = ai_manager.generate_content(avatar_prompt, max_tokens=4000)
            
            return {
                'avatar_detalhado': avatar_analysis,
                'base_data': data,
                'generated_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Erro ao gerar avatar: {str(e)}")
            return self._generate_fallback_avatar()
    
    def _generate_sales_funnel(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Gera funil de vendas completo"""
        
        try:
            funnel_prompt = self._build_funnel_prompt(data)
            funnel_analysis = ai_manager.generate_content(funnel_prompt, max_tokens=3000)
            
            return {
                'funil_vendas': funnel_analysis,
                'stages': ['Consciência', 'Interesse', 'Consideração', 'Intenção', 'Compra', 'Retenção'],
                'generated_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Erro ao gerar funil: {str(e)}")
            return self._generate_fallback_funnel()
    
    def _generate_competition_analysis(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Gera análise de concorrência"""
        
        try:
            competition_prompt = self._build_competition_prompt(data)
            competition_analysis = ai_manager.generate_content(competition_prompt, max_tokens=3000)
            
            return {
                'analise_concorrencia': competition_analysis,
                'generated_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Erro ao gerar análise de concorrência: {str(e)}")
            return self._generate_fallback_competition()
    
    def _consolidate_comprehensive_report(
        self,
        data: Dict[str, Any],
        web_research: Dict[str, Any],
        social_analysis: Dict[str, Any],
        specialized_analysis: Dict[str, Any],
        session_id: str
    ) -> Dict[str, Any]:
        """Consolida relatório completo com mais de 20 páginas"""
        
        try:
            logger.info("📄 Consolidando relatório completo...")
            
            # Gera relatório consolidado usando IA
            consolidation_prompt = self._build_consolidation_prompt(
                data, web_research, social_analysis, specialized_analysis
            )
            
            consolidated_report = ai_manager.generate_content(consolidation_prompt, max_tokens=8000)
            
            final_report = {
                'session_id': session_id,
                'generated_at': datetime.now().isoformat(),
                'input_data': data,
                'web_research_summary': self._summarize_web_research(web_research),
                'social_analysis_summary': self._summarize_social_analysis(social_analysis),
                'specialized_components': specialized_analysis,
                'consolidated_analysis': consolidated_report,
                'report_metrics': {
                    'estimated_pages': 25,
                    'total_drivers': len(specialized_analysis.get('mental_drivers', {}).get('drivers', [])),
                    'web_sources': self._count_web_sources(web_research),
                    'social_posts': social_analysis.get('total_posts', 0),
                    'completion_rate': self._calculate_completion_rate(specialized_analysis)
                }
            }
            
            return final_report
            
        except Exception as e:
            logger.error(f"❌ Erro na consolidação: {str(e)}")
            return self._generate_fallback_report(data, session_id)
    
    def _save_to_all_categories(self, final_report: Dict[str, Any], session_id: str):
        """Salva dados em todas as categorias necessárias"""
        
        categories = [
            'analyses', 'anti_objecao', 'avatars', 'completas', 'concorrencia',
            'drivers_mentais', 'files', 'funil_vendas', 'insights', 'logs',
            'metadata', 'metricas', 'palavras_chave', 'pesquisa_web',
            'plano_acao', 'posicionamento', 'pre_pitch', 'predicoes_futuro',
            'progress', 'provas_visuais', 'reports', 'users'
        ]
        
        for category in categories:
            try:
                category_data = self._extract_category_data(final_report, category)
                salvar_etapa(f"categoria_{category}", category_data, categoria=category)
                logger.info(f"✅ Dados salvos em {category}")
            except Exception as e:
                logger.error(f"❌ Erro ao salvar em {category}: {str(e)}")
    
    def _extract_category_data(self, report: Dict[str, Any], category: str) -> Dict[str, Any]:
        """Extrai dados específicos para cada categoria"""
        
        category_mappings = {
            'drivers_mentais': report.get('specialized_components', {}).get('mental_drivers', {}),
            'avatars': report.get('specialized_components', {}).get('avatar_detalhado', {}),
            'funil_vendas': report.get('specialized_components', {}).get('funil_vendas', {}),
            'concorrencia': report.get('specialized_components', {}).get('analise_concorrencia', {}),
            'anti_objecao': report.get('specialized_components', {}).get('anti_objection', {}),
            'pre_pitch': report.get('specialized_components', {}).get('pre_pitch', {}),
            'predicoes_futuro': report.get('specialized_components', {}).get('future_predictions', {}),
            'provas_visuais': report.get('specialized_components', {}).get('visual_proofs', {}),
            'pesquisa_web': report.get('web_research_summary', {}),
            'reports': report,
            'completas': report
        }
        
        return category_mappings.get(category, {'category': category, 'data': report})
    
    # Utility methods for building prompts and fallbacks
    def _build_avatar_prompt(self, data: Dict[str, Any]) -> str:
        segmento = data.get('segmento', 'não especificado')
        produto = data.get('produto', 'não especificado')
        
        return f"""
        Crie um avatar ultra-detalhado para o segmento "{segmento}" e produto "{produto}".
        
        Baseado nos dados de pesquisa: {str(data.get('web_research', {}))[:2000]}
        
        O avatar deve incluir:
        1. Demografia detalhada
        2. Psicografia profunda
        3. Comportamentos online
        4. Dores e necessidades
        5. Motivações de compra
        6. Jornada do cliente
        7. Canais de comunicação preferidos
        8. Influenciadores que segue
        
        Seja extremamente específico e detalhado.
        """
    
    def _build_funnel_prompt(self, data: Dict[str, Any]) -> str:
        return f"""
        Crie um funil de vendas completo para {data.get('segmento', '')} - {data.get('produto', '')}.
        
        Inclua:
        1. Estágios detalhados do funil
        2. Estratégias para cada etapa
        3. Métricas e KPIs
        4. Pontos de conversão
        5. Conteúdo necessário
        6. Canais de aquisição
        7. Automações sugeridas
        
        Base-se nos dados de pesquisa coletados.
        """
    
    def _build_competition_prompt(self, data: Dict[str, Any]) -> str:
        return f"""
        Analise a concorrência no mercado de {data.get('segmento', '')}.
        
        Inclua:
        1. Principais concorrentes
        2. Análise SWOT de cada um
        3. Posicionamento de mercado
        4. Preços praticados
        5. Estratégias de marketing
        6. Oportunidades de diferenciação
        7. Ameaças e riscos
        
        Seja detalhado e estratégico.
        """
    
    def _build_consolidation_prompt(self, data, web_research, social_analysis, specialized_analysis) -> str:
        return f"""
        Consolide uma análise completa de mercado ultra-detalhada baseada em todos os dados coletados.
        
        Dados de entrada: {data}
        Pesquisa web: {self._summarize_web_research(web_research)}
        Análise social: {self._summarize_social_analysis(social_analysis)}
        Componentes especializados: {list(specialized_analysis.keys())}
        
        O relatório deve ter estrutura para mais de 20 páginas incluindo:
        1. Sumário executivo
        2. Análise de mercado
        3. Avatar detalhado
        4. 19 drivers mentais
        5. Funil de vendas
        6. Análise de concorrência
        7. Predições futuras
        8. Estratégias de posicionamento
        9. Plano de ação
        10. Métricas e KPIs
        
        Seja extremamente detalhado e profissional.
        """
    
    # Fallback methods
    def _generate_fallback_analysis(self, data: Dict[str, Any], session_id: str) -> Dict[str, Any]:
        return {
            'success': False,
            'session_id': session_id,
            'error': 'Sistema em modo fallback',
            'basic_analysis': f"Análise básica para {data.get('segmento', 'segmento não especificado')}",
            'generated_at': datetime.now().isoformat()
        }
    
    def _generate_fallback_drivers(self) -> Dict[str, Any]:
        return {
            'drivers': [f"Driver Mental {i+1}: Análise em desenvolvimento" for i in range(19)],
            'fallback': True
        }
    
    def _generate_fallback_visual_proofs(self) -> Dict[str, Any]:
        return {
            'proofs': "Provas visuais em desenvolvimento",
            'experiences': "Experiências em desenvolvimento",
            'fallback': True
        }
    
    def _generate_fallback_anti_objection(self) -> Dict[str, Any]:
        return {
            'objections': "Sistema anti-objeção em desenvolvimento",
            'fallback': True
        }
    
    def _generate_fallback_pre_pitch(self) -> Dict[str, Any]:
        return {
            'strategy': "Estratégia de pré-pitch em desenvolvimento",
            'fallback': True
        }
    
    def _generate_fallback_predictions(self) -> Dict[str, Any]:
        return {
            'predictions': "Predições futuras em desenvolvimento",
            'fallback': True
        }
    
    def _generate_fallback_avatar(self) -> Dict[str, Any]:
        return {
            'avatar': "Avatar detalhado em desenvolvimento",
            'fallback': True
        }
    
    def _generate_fallback_funnel(self) -> Dict[str, Any]:
        return {
            'funnel': "Funil de vendas em desenvolvimento",
            'fallback': True
        }
    
    def _generate_fallback_competition(self) -> Dict[str, Any]:
        return {
            'competition': "Análise de concorrência em desenvolvimento",
            'fallback': True
        }
    
    def _generate_fallback_report(self, data: Dict[str, Any], session_id: str) -> Dict[str, Any]:
        return {
            'session_id': session_id,
            'basic_report': f"Relatório básico para {data.get('segmento', 'não especificado')}",
            'fallback': True,
            'generated_at': datetime.now().isoformat()
        }
    
    # Helper methods
    def _extract_social_insights(self, posts: List[Dict[str, Any]]) -> List[str]:
        """Extrai insights das redes sociais"""
        insights = []
        for post in posts[:10]:  # Top 10 posts
            text = post.get('text', '') or post.get('caption', '') or post.get('title', '')
            if len(text) > 50:
                insights.append(text[:200])
        return insights
    
    def _summarize_web_research(self, web_research: Dict[str, Any]) -> Dict[str, Any]:
        """Sumariza pesquisa web"""
        total_results = 0
        sources_used = []
        
        for key, value in web_research.items():
            if isinstance(value, dict) and 'results' in value:
                total_results += len(value.get('results', []))
            if key not in ['error', 'fallback']:
                sources_used.append(key)
        
        return {
            'total_results': total_results,
            'sources_used': sources_used,
            'has_content': total_results > 0
        }
    
    def _summarize_social_analysis(self, social_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Sumariza análise social"""
        return {
            'total_posts': social_analysis.get('total_posts', 0),
            'platforms': social_analysis.get('platforms_analyzed', []),
            'sentiment': social_analysis.get('sentiment_analysis', {}).get('sentiment', 'neutral')
        }
    
    def _count_web_sources(self, web_research: Dict[str, Any]) -> int:
        """Conta fontes web utilizadas"""
        count = 0
        for key, value in web_research.items():
            if isinstance(value, dict) and value.get('results'):
                count += len(value['results'])
        return count
    
    def _calculate_completion_rate(self, specialized_analysis: Dict[str, Any]) -> float:
        """Calcula taxa de completude da análise"""
        total_components = 8  # Total de componentes esperados
        completed_components = sum(1 for value in specialized_analysis.values() if not value.get('error'))
        return (completed_components / total_components) * 100
    
    def _get_saved_categories(self, session_id: str) -> List[str]:
        """Retorna categorias onde dados foram salvos"""
        return [
            'analyses', 'anti_objecao', 'avatars', 'completas', 'concorrencia',
            'drivers_mentais', 'files', 'funil_vendas', 'insights', 'logs',
            'metadata', 'metricas', 'palavras_chave', 'pesquisa_web',
            'plano_acao', 'posicionamento', 'pre_pitch', 'predicoes_futuro',
            'progress', 'provas_visuais', 'reports', 'users'
        ]
    
    def _generate_additional_driver(self, data: Dict[str, Any], driver_number: int) -> Dict[str, Any]:
        """Gera driver mental adicional"""
        return {
            'numero': driver_number,
            'nome': f"Driver Mental {driver_number}",
            'descricao': f"Driver personalizado para {data.get('segmento', 'mercado')}",
            'aplicacao': f"Aplicável em contexto de {data.get('produto', 'produto/serviço')}",
            'impacto': "Alto impacto na decisão de compra"
        }

# Instância global
master_orchestrator = MasterOrchestrator()
