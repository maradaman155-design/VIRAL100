"""
Orquestrador Principal do Sistema - V3.0
Integra todos os componentes para execução completa
"""

import os
import json
import asyncio
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
import logging
import uuid

# Importar todos os sistemas
from enhanced_api_rotation_manager import get_api_manager
from massive_social_search_engine import get_search_engine
from cpl_devastador_protocol import get_cpl_protocol
from deep_ai_analysis_engine import get_deep_analysis_engine
from mental_drivers_system import get_mental_drivers_system
from avatar_generation_system import get_avatar_system
from predictive_analysis_engine import get_predictive_engine
from comprehensive_html_report_generator import get_html_report_generator
from hybrid_social_extractor import extract_viral_content_hybrid
from viral_content_analyzer_insta import get_viral_content_analyzer
from google_social_masterclass_extractor import extract_masterclass_content, generate_masterclass_report

logger = logging.getLogger(__name__)

@dataclass
class SystemExecution:
    session_id: str
    start_time: datetime
    end_time: Optional[datetime]
    status: str
    tema: str
    segmento: str
    publico_alvo: str
    results: Dict[str, Any]
    errors: List[str]
    warnings: List[str]

class MasterSystemOrchestrator:
    """
    Orquestrador principal que executa todo o sistema de forma integrada:
    1. Busca massiva de redes sociais
    2. Análise profunda da IA (5 minutos)
    3. Geração de 4 avatares únicos
    4. Sistema de 19 drivers mentais
    5. Protocolo completo de CPLs devastadores
    6. Análise preditiva robusta
    7. Relatório HTML final (25+ páginas)
    """

    def __init__(self):
        self.api_manager = get_api_manager()
        self.search_engine = get_search_engine()
        self.cpl_protocol = get_cpl_protocol()
        self.deep_analysis = get_deep_analysis_engine()
        self.mental_drivers = get_mental_drivers_system()
        self.avatar_system = get_avatar_system()
        self.predictive_engine = get_predictive_engine()
        self.html_generator = get_html_report_generator()

        self.current_execution = None

    async def execute_complete_system(self, tema: str, segmento: str, 
                                    publico_alvo: str) -> SystemExecution:
        """
        Executa o sistema completo de análise e geração
        """
        session_id = f"session_{uuid.uuid4().hex[:8]}_{int(datetime.now().timestamp())}"

        execution = SystemExecution(
            session_id=session_id,
            start_time=datetime.now(),
            end_time=None,
            status="iniciando",
            tema=tema,
            segmento=segmento,
            publico_alvo=publico_alvo,
            results={},
            errors=[],
            warnings=[]
        )

        self.current_execution = execution

        try:
            logger.info("🚀 INICIANDO EXECUÇÃO COMPLETA DO SISTEMA")
            logger.info(f"📋 Sessão: {session_id}")
            logger.info(f"🎯 Tema: {tema}")
            logger.info(f"🏢 Segmento: {segmento}")
            logger.info(f"👥 Público: {publico_alvo}")

            # ETAPA 1: Busca Massiva de Redes Sociais
            execution.status = "busca_massiva"
            logger.info("🔍 ETAPA 1: Executando busca massiva de redes sociais...")

            search_results = await self.search_engine.massive_search(
                query=f"{tema} {segmento} {publico_alvo}",
                platforms=['instagram', 'youtube', 'facebook'],
                min_engagement=100,
                max_results=1000
            )

            # Salvar resultados da busca
            search_dir = self.search_engine.save_search_results(search_results, session_id)
            execution.results['search_results'] = {
                'total_posts': search_results.total_posts,
                'total_images': search_results.total_images,
                'total_videos': search_results.total_videos,
                'platforms': search_results.platforms,
                'data_directory': search_dir
            }

            logger.info(f"✅ Busca concluída: {search_results.total_posts} posts coletados")

            # Verificar se JSON tem tamanho mínimo de 500KB
            json_data = self.search_engine.generate_massive_json(search_results, min_size_kb=500)
            json_size_kb = len(json.dumps(json_data, default=str)) / 1024

            if json_size_kb < 500:
                execution.warnings.append(f"JSON gerado tem {json_size_kb:.1f}KB (mínimo: 500KB)")
            else:
                logger.info(f"✅ JSON gerado: {json_size_kb:.1f}KB")

            # Google Masterclass Search
            logger.info("🎯 Executando Google Masterclass Search")
            try:
                masterclass_results = await extract_masterclass_content(
                    f"{tema} masterclass", session_id, ['instagram', 'youtube', 'facebook']
                )
                execution.results['google_masterclass'] = masterclass_results

                # Gera relatório do masterclass
                if masterclass_results.get('success'):
                    masterclass_report = await generate_masterclass_report(masterclass_results, session_id)
                    execution.results['masterclass_report'] = masterclass_report

            except Exception as e:
                logger.error(f"❌ Erro no Google Masterclass: {e}")
                execution.errors.append(f"Google Masterclass: {str(e)}")
                execution.results['google_masterclass'] = {'error': str(e)}


            # ETAPA 2: Análise Profunda da IA (5 minutos)
            execution.status = "analise_ia"
            logger.info("🧠 ETAPA 2: Iniciando análise profunda da IA (5 minutos)...")

            data_directory = f"/workspace/project/v110/analyses_data/{session_id}"

            ai_study_session = await self.deep_analysis.initiate_deep_study(
                session_id=session_id,
                topic=f"{tema} no segmento {segmento}",
                data_directory=data_directory,
                study_minutes=5
            )

            # Salvar expertise da IA
            ai_expertise_dir = self.deep_analysis.save_expertise_session(session_id)
            execution.results['ai_expertise'] = {
                'expertise_level': ai_study_session.expertise_level,
                'confidence_score': ai_study_session.confidence_score,
                'insights_count': len(ai_study_session.key_insights),
                'conclusions_count': len(ai_study_session.expert_conclusions),
                'data_directory': ai_expertise_dir
            }

            logger.info(f"✅ IA se tornou expert: {ai_study_session.expertise_level:.1f}% de expertise")

            # ETAPA 3: Geração de 4 Avatares Únicos
            execution.status = "geracao_avatares"
            logger.info("👥 ETAPA 3: Gerando 4 avatares únicos com nomes reais...")

            avatares = await self.avatar_system.gerar_4_avatares_completos(
                contexto_nicho=f"{tema} no segmento {segmento}",
                dados_pesquisa=json_data
            )

            # Salvar avatares
            avatares_dir = self.avatar_system.salvar_avatares(session_id, avatares)
            execution.results['avatares'] = {
                'total_avatares': len(avatares),
                'nomes': [avatar.dados_demograficos.nome_completo for avatar in avatares],
                'data_directory': avatares_dir
            }

            logger.info(f"✅ {len(avatares)} avatares únicos gerados")

            # ETAPA 4: Sistema de 19 Drivers Mentais
            execution.status = "drivers_mentais"
            logger.info("🧠 ETAPA 4: Implementando sistema de 19 drivers mentais...")

            # Selecionar top 7 drivers mais efetivos
            top_drivers = self.mental_drivers.get_top_drivers_essenciais()
            driver_names = [driver.nome.lower().replace(' ', '_') for driver in top_drivers]

            # Customizar drivers para o nicho
            drivers_customizados = self.mental_drivers.customizar_drivers_para_nicho(
                drivers_selecionados=driver_names,
                contexto_nicho=f"{tema} no segmento {segmento}",
                publico_alvo=publico_alvo,
                dados_pesquisa=json_data
            )

            # Gerar sequência otimizada
            sequencia_otimizada = self.mental_drivers.gerar_sequencia_otimizada(
                drivers_customizados=drivers_customizados,
                formato_campanha="CPLs + Email Marketing"
            )

            # Salvar sistema de drivers
            drivers_dir = self.mental_drivers.salvar_sistema_drivers(
                session_id=session_id,
                drivers_customizados=drivers_customizados,
                sequencia_otimizada=sequencia_otimizada
            )

            execution.results['mental_drivers'] = {
                'total_drivers': len(drivers_customizados),
                'drivers_names': [d.driver_base.nome for d in drivers_customizados],
                'data_directory': drivers_dir
            }

            logger.info(f"✅ {len(drivers_customizados)} drivers mentais customizados")

            # ETAPA 5: Protocolo Completo de CPLs Devastadores
            execution.status = "cpls_devastadores"
            logger.info("🎬 ETAPA 5: Executando protocolo completo de CPLs devastadores...")

            cpl_results = await self.cpl_protocol.executar_protocolo_completo(
                tema=tema,
                segmento=segmento,
                publico_alvo=publico_alvo,
                session_id=session_id
            )

            execution.results['cpls'] = {
                'evento_magnetico': cpl_results['evento_magnetico']['nome'],
                'cpls_gerados': 4,
                'protocolo_completo': True,
                'data_directory': data_directory
            }

            logger.info("✅ Protocolo de CPLs devastadores concluído")

            # ETAPA 6: Análise Preditiva Robusta
            execution.status = "analise_preditiva"
            logger.info("🔮 ETAPA 6: Executando análise preditiva robusta...")

            predictive_insights = await self.predictive_engine.execute_comprehensive_prediction(
                session_id=session_id,
                data_directory=data_directory
            )

            # Salvar insights preditivos
            predictive_dir = self.predictive_engine.save_predictive_insights(session_id, predictive_insights)
            execution.results['predictive_analysis'] = {
                'confidence_score': predictive_insights.confidence_score,
                'trends_identified': len(predictive_insights.trend_predictions),
                'market_forecasts': len(predictive_insights.market_forecasts),
                'behavior_predictions': len(predictive_insights.behavior_predictions),
                'data_directory': predictive_dir
            }

            logger.info(f"✅ Análise preditiva concluída: {predictive_insights.confidence_score:.1f}% confiança")

            # ETAPA 7: Geração de Relatório HTML Final (25+ páginas)
            execution.status = "relatorio_html"
            logger.info("📄 ETAPA 7: Gerando relatório HTML final (mínimo 25 páginas)...")

            html_report_path = await self.html_generator.generate_comprehensive_report(
                session_id=session_id,
                data_directory=data_directory
            )

            execution.results['html_report'] = {
                'report_path': html_report_path,
                'min_pages': 25,
                'generated': True
            }

            logger.info(f"✅ Relatório HTML gerado: {html_report_path}")

            # FINALIZAÇÃO
            execution.status = "concluido"
            execution.end_time = datetime.now()

            # Calcular tempo total
            total_time = execution.end_time - execution.start_time

            # Salvar resumo da execução
            await self._save_execution_summary(execution)

            logger.info("🎉 SISTEMA COMPLETO EXECUTADO COM SUCESSO!")
            logger.info(f"⏱️ Tempo total: {total_time}")
            logger.info(f"📊 Resultados salvos em: {data_directory}")

            return execution

        except Exception as e:
            execution.status = "erro"
            execution.end_time = datetime.now()
            execution.errors.append(str(e))

            logger.error(f"❌ ERRO CRÍTICO na execução: {e}")

            # Salvar execução com erro
            await self._save_execution_summary(execution)

            raise

    async def _save_execution_summary(self, execution: SystemExecution):
        """Salva resumo da execução"""
        try:
            session_dir = f"/workspace/project/v110/analyses_data/{execution.session_id}"
            os.makedirs(session_dir, exist_ok=True)

            # Salvar resumo em JSON
            summary_path = os.path.join(session_dir, 'execution_summary.json')
            with open(summary_path, 'w', encoding='utf-8') as f:
                json.dump(asdict(execution), f, ensure_ascii=False, indent=2, default=str)

            # Salvar resumo em markdown
            md_path = os.path.join(session_dir, 'execution_summary.md')
            with open(md_path, 'w', encoding='utf-8') as f:
                f.write(self._generate_execution_markdown(execution))

            logger.info(f"✅ Resumo da execução salvo: {session_dir}")

        except Exception as e:
            logger.error(f"❌ Erro ao salvar resumo: {e}")

    def _generate_execution_markdown(self, execution: SystemExecution) -> str:
        """Gera resumo da execução em markdown"""

        duration = ""
        if execution.end_time:
            total_time = execution.end_time - execution.start_time
            duration = f"{total_time.total_seconds():.0f} segundos"

        return f"""# Resumo da Execução do Sistema

## Informações Gerais
- **Sessão ID**: {execution.session_id}
- **Status**: {execution.status.upper()}
- **Início**: {execution.start_time.strftime('%d/%m/%Y %H:%M:%S')}
- **Fim**: {execution.end_time.strftime('%d/%m/%Y %H:%M:%S') if execution.end_time else 'Em andamento'}
- **Duração**: {duration}

## Parâmetros de Entrada
- **Tema**: {execution.tema}
- **Segmento**: {execution.segmento}
- **Público-Alvo**: {execution.publico_alvo}

## Resultados Obtidos

### 🔍 Busca Massiva de Redes Sociais
{f"- **Posts Coletados**: {execution.results.get('search_results', {}).get('total_posts', 0):,}" if 'search_results' in execution.results else "- Não executado"}
{f"- **Imagens Extraídas**: {execution.results.get('search_results', {}).get('total_images', 0):,}" if 'search_results' in execution.results else ""}
{f"- **Vídeos Analisados**: {execution.results.get('search_results', {}).get('total_videos', 0):,}" if 'search_results' in execution.results else ""}
{f"- **Plataformas**: {', '.join(execution.results.get('search_results', {}).get('platforms', {}).keys())}" if 'search_results' in execution.results else ""}

### 🎯 Google Masterclass Search
{f"- **Sucesso**: {'✅ Sim' if execution.results.get('google_masterclass', {}).get('success') else '❌ Não'}" if 'google_masterclass' in execution.results else "- Não executado"}
{f"- **Posts Analisados**: {execution.results.get('google_masterclass', {}).get('analysis_summary', {}).get('posts_analyzed', 0):,}" if 'google_masterclass' in execution.results else ""}
{f"- **Melhores Posts (Views)**: {execution.results.get('google_masterclass', {}).get('analysis_summary', {}).get('best_posts_views', 0)}" if 'google_masterclass' in execution.results else ""}
{f"- **Melhores Posts (Likes)**: {execution.results.get('google_masterclass', {}).get('analysis_summary', {}).get('best_posts_likes', 0)}" if 'google_masterclass' in execution.results else ""}
{f"- **Melhores Posts (Comentários)**: {execution.results.get('google_masterclass', {}).get('analysis_summary', {}).get('best_posts_comments', 0)}" if 'google_masterclass' in execution.results else ""}
{f"- **Relatório Masterclass**: {execution.results.get('masterclass_report', 'N/A')}" if 'masterclass_report' in execution.results else ""}


### 🧠 Análise Profunda da IA
{f"- **Nível de Expertise**: {execution.results.get('ai_expertise', {}).get('expertise_level', 0):.1f}%" if 'ai_expertise' in execution.results else "- Não executado"}
{f"- **Confiança**: {execution.results.get('ai_expertise', {}).get('confidence_score', 0)*100:.1f}%" if 'ai_expertise' in execution.results else ""}
{f"- **Insights Gerados**: {execution.results.get('ai_expertise', {}).get('insights_count', 0)}" if 'ai_expertise' in execution.results else ""}
{f"- **Conclusões Expert**: {execution.results.get('ai_expertise', {}).get('conclusions_count', 0)}" if 'ai_expertise' in execution.results else ""}

### 👥 Avatares Únicos
{f"- **Total de Avatares**: {execution.results.get('avatares', {}).get('total_avatares', 0)}" if 'avatares' in execution.results else "- Não executado"}
{f"- **Nomes Reais**: {', '.join(execution.results.get('avatares', {}).get('nomes', []))}" if 'avatares' in execution.results else ""}

### 🧠 Drivers Mentais
{f"- **Drivers Customizados**: {execution.results.get('mental_drivers', {}).get('total_drivers', 0)}" if 'mental_drivers' in execution.results else "- Não executado"}
{f"- **Drivers Implementados**: {', '.join(execution.results.get('mental_drivers', {}).get('drivers_names', []))}" if 'mental_drivers' in execution.results else ""}

### 🎬 CPLs Devastadores
{f"- **Evento Magnético**: {execution.results.get('cpls', {}).get('evento_magnetico', 'N/A')}" if 'cpls' in execution.results else "- Não executado"}
{f"- **CPLs Gerados**: {execution.results.get('cpls', {}).get('cpls_gerados', 0)}" if 'cpls' in execution.results else ""}
{f"- **Protocolo Completo**: {'✅ Sim' if execution.results.get('cpls', {}).get('protocolo_completo') else '❌ Não'}" if 'cpls' in execution.results else ""}

### 🔮 Análise Preditiva
{f"- **Confiança Geral**: {execution.results.get('predictive_analysis', {}).get('confidence_score', 0):.1f}%" if 'predictive_analysis' in execution.results else "- Não executado"}
{f"- **Tendências Identificadas**: {execution.results.get('predictive_analysis', {}).get('trends_identified', 0)}" if 'predictive_analysis' in execution.results else ""}
{f"- **Previsões de Mercado**: {execution.results.get('predictive_analysis', {}).get('market_forecasts', 0)}" if 'predictive_analysis' in execution.results else ""}
{f"- **Mudanças Comportamentais**: {execution.results.get('predictive_analysis', {}).get('behavior_predictions', 0)}" if 'predictive_analysis' in execution.results else ""}

### 📄 Relatório HTML
{f"- **Relatório Gerado**: {'✅ Sim' if execution.results.get('html_report', {}).get('generated') else '❌ Não'}" if 'html_report' in execution.results else "- Não executado"}
{f"- **Páginas Mínimas**: {execution.results.get('html_report', {}).get('min_pages', 0)}" if 'html_report' in execution.results else ""}
{f"- **Caminho**: {execution.results.get('html_report', {}).get('report_path', 'N/A')}" if 'html_report' in execution.results else ""}

## Avisos
{chr(10).join([f"- ⚠️ {warning}" for warning in execution.warnings]) if execution.warnings else "- Nenhum aviso"}

## Erros
{chr(10).join([f"- ❌ {error}" for error in execution.errors]) if execution.errors else "- Nenhum erro"}

---

*Relatório gerado automaticamente pelo Master System Orchestrator*
"""

    def get_execution_status(self) -> Optional[SystemExecution]:
        """Retorna status da execução atual"""
        return self.current_execution

    async def validate_system_requirements(self) -> Dict[str, bool]:
        """Valida se todos os requisitos do sistema estão atendidos"""

        validation = {
            'api_manager': False,
            'search_engine': False,
            'cpl_protocol': False,
            'deep_analysis': False,
            'mental_drivers': False,
            'avatar_system': False,
            'predictive_engine': False,
            'html_generator': False,
            'pymupdf_installed': False,
            'directories_created': False
        }

        try:
            # Validar componentes
            validation['api_manager'] = self.api_manager is not None
            validation['search_engine'] = self.search_engine is not None
            validation['cpl_protocol'] = self.cpl_protocol is not None
            validation['deep_analysis'] = self.deep_analysis is not None
            validation['mental_drivers'] = self.mental_drivers is not None
            validation['avatar_system'] = self.avatar_system is not None
            validation['predictive_engine'] = self.predictive_engine is not None
            validation['html_generator'] = self.html_generator is not None

            # Validar PyMuPDF
            try:
                import fitz  # PyMuPDF
                validation['pymupdf_installed'] = True
            except ImportError:
                validation['pymupdf_installed'] = False

            # Validar diretórios
            base_dir = "/workspace/project/v110/analyses_data"
            os.makedirs(base_dir, exist_ok=True)
            validation['directories_created'] = os.path.exists(base_dir)

        except Exception as e:
            logger.error(f"❌ Erro na validação: {e}")

        return validation

    async def get_system_health(self) -> Dict[str, Any]:
        """Retorna status de saúde do sistema"""

        validation = await self.validate_system_requirements()
        api_status = self.api_manager.get_api_status_report()

        health = {
            'timestamp': datetime.now().isoformat(),
            'overall_status': 'healthy' if all(validation.values()) else 'degraded',
            'component_validation': validation,
            'api_status': api_status,
            'system_ready': all(validation.values())
        }

        return health

# Instância global
master_orchestrator = MasterSystemOrchestrator()

def get_master_orchestrator() -> MasterSystemOrchestrator:
    """Retorna instância do orquestrador principal"""
    return master_orchestrator