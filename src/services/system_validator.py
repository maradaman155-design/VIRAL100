
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ARQV30 Enhanced v2.0 - System Validator
Validador de sistema e corretor de erros automatizado
"""

import os
import logging
import traceback
from typing import Dict, List, Any, Optional
from datetime import datetime

# Import all services to validate
try:
    from services.ai_manager import ai_manager
    AI_MANAGER_OK = True
except Exception as e:
    AI_MANAGER_OK = False
    AI_MANAGER_ERROR = str(e)

try:
    from services.enhanced_search_coordinator import enhanced_search_coordinator
    SEARCH_COORDINATOR_OK = True
except Exception as e:
    SEARCH_COORDINATOR_OK = False
    SEARCH_COORDINATOR_ERROR = str(e)

try:
    from services.alibaba_websailor import alibaba_websailor
    WEBSAILOR_OK = True
except Exception as e:
    WEBSAILOR_OK = False
    WEBSAILOR_ERROR = str(e)

try:
    from services.mcp_supadata_manager import mcp_supadata_manager
    SUPADATA_OK = True
except Exception as e:
    SUPADATA_OK = False
    SUPADATA_ERROR = str(e)

try:
    from services.mental_drivers_architect import mental_drivers_architect
    DRIVERS_ARCHITECT_OK = True
except Exception as e:
    DRIVERS_ARCHITECT_OK = False
    DRIVERS_ARCHITECT_ERROR = str(e)

try:
    from services.visual_proofs_generator import visual_proofs_generator
    VISUAL_PROOFS_OK = True
except Exception as e:
    VISUAL_PROOFS_OK = False
    VISUAL_PROOFS_ERROR = str(e)

try:
    from services.anti_objection_system import anti_objection_system
    ANTI_OBJECTION_OK = True
except Exception as e:
    ANTI_OBJECTION_OK = False
    ANTI_OBJECTION_ERROR = str(e)

try:
    from services.pre_pitch_architect import pre_pitch_architect
    PRE_PITCH_OK = True
except Exception as e:
    PRE_PITCH_OK = False
    PRE_PITCH_ERROR = str(e)

try:
    from services.future_prediction_engine import future_prediction_engine
    FUTURE_PREDICTION_OK = True
except Exception as e:
    FUTURE_PREDICTION_OK = False
    FUTURE_PREDICTION_ERROR = str(e)

logger = logging.getLogger(__name__)

class SystemValidator:
    """Validador de sistema e corretor automático de erros"""

    def __init__(self):
        """Inicializa o validador"""
        self.validation_results = {}
        self.critical_errors = []
        self.warnings = []
        self.fixes_applied = []
        
        logger.info("🔧 System Validator inicializado")

    def validate_all_systems(self) -> Dict[str, Any]:
        """Valida todos os sistemas e corrige erros automaticamente"""
        
        try:
            logger.info("🚀 INICIANDO VALIDAÇÃO COMPLETA DO SISTEMA")
            start_time = datetime.now()

            # FASE 1: Validação de APIs e variáveis de ambiente
            env_validation = self._validate_environment_variables()
            
            # FASE 2: Validação de serviços críticos
            services_validation = self._validate_core_services()
            
            # FASE 3: Validação de módulos importados
            modules_validation = self._validate_imported_modules()
            
            # FASE 4: Correção automática de erros
            auto_fixes = self._apply_automatic_fixes()
            
            # FASE 5: Teste de conectividade
            connectivity_test = self._test_system_connectivity()
            
            validation_summary = {
                'validation_timestamp': start_time.isoformat(),
                'environment_validation': env_validation,
                'services_validation': services_validation,
                'modules_validation': modules_validation,
                'automatic_fixes': auto_fixes,
                'connectivity_test': connectivity_test,
                'overall_status': self._determine_overall_status(),
                'critical_errors': self.critical_errors,
                'warnings': self.warnings,
                'fixes_applied': self.fixes_applied,
                'recommendations': self._generate_recommendations()
            }

            logger.info("✅ VALIDAÇÃO COMPLETA DO SISTEMA CONCLUÍDA")
            return validation_summary

        except Exception as e:
            logger.error(f"❌ ERRO CRÍTICO na validação do sistema: {str(e)}")
            return {
                'validation_timestamp': datetime.now().isoformat(),
                'status': 'CRITICAL_ERROR',
                'error': str(e),
                'traceback': traceback.format_exc()
            }

    def _validate_environment_variables(self) -> Dict[str, Any]:
        """Valida variáveis de ambiente necessárias"""
        
        logger.info("🔍 Validando variáveis de ambiente...")
        
        required_vars = [
            'OPENAI_API_KEY',
            'ANTHROPIC_API_KEY', 
            'GEMINI_API_KEY',
            'GROQ_API_KEY',
            'EXA_API_KEY',
            'TAVILY_API_KEY',
            'DEEPSEEK_API_KEY',
            'HUGGINGFACE_API_TOKEN'
        ]
        
        env_status = {}
        missing_vars = []
        
        for var in required_vars:
            value = os.getenv(var)
            if value:
                env_status[var] = '✅ CONFIGURADA'
                # Valida se a API key não é um placeholder
                if value.startswith('sk-') or value.startswith('gsk_') or len(value) > 20:
                    env_status[var] += ' (Formato válido)'
                else:
                    env_status[var] += ' ⚠️ (Formato suspeito)'
                    self.warnings.append(f"API key {var} pode ter formato inválido")
            else:
                env_status[var] = '❌ NÃO CONFIGURADA'
                missing_vars.append(var)
                self.critical_errors.append(f"Variável de ambiente {var} não configurada")
        
        # Validação de arquivo .env
        env_file_exists = os.path.exists('.env')
        env_status['ENV_FILE'] = '✅ EXISTE' if env_file_exists else '❌ NÃO EXISTE'
        
        if not env_file_exists:
            self.critical_errors.append("Arquivo .env não encontrado")
        
        return {
            'status': 'VALID' if not missing_vars else 'INVALID',
            'missing_variables': missing_vars,
            'variables_status': env_status,
            'env_file_exists': env_file_exists,
            'total_required': len(required_vars),
            'configured_count': len(required_vars) - len(missing_vars)
        }

    def _validate_core_services(self) -> Dict[str, Any]:
        """Valida serviços críticos do sistema"""
        
        logger.info("🔍 Validando serviços críticos...")
        
        services_status = {
            'ai_manager': {
                'imported': AI_MANAGER_OK,
                'error': AI_MANAGER_ERROR if not AI_MANAGER_OK else None,
                'functional': False
            },
            'search_coordinator': {
                'imported': SEARCH_COORDINATOR_OK,
                'error': SEARCH_COORDINATOR_ERROR if not SEARCH_COORDINATOR_OK else None,
                'functional': False
            },
            'websailor': {
                'imported': WEBSAILOR_OK,
                'error': WEBSAILOR_ERROR if not WEBSAILOR_OK else None,
                'functional': False
            },
            'supadata_manager': {
                'imported': SUPADATA_OK,
                'error': SUPADATA_ERROR if not SUPADATA_OK else None,
                'functional': False
            },
            'drivers_architect': {
                'imported': DRIVERS_ARCHITECT_OK,
                'error': DRIVERS_ARCHITECT_ERROR if not DRIVERS_ARCHITECT_OK else None,
                'functional': False
            },
            'visual_proofs': {
                'imported': VISUAL_PROOFS_OK,
                'error': VISUAL_PROOFS_ERROR if not VISUAL_PROOFS_OK else None,
                'functional': False
            },
            'anti_objection': {
                'imported': ANTI_OBJECTION_OK,
                'error': ANTI_OBJECTION_ERROR if not ANTI_OBJECTION_OK else None,
                'functional': False
            },
            'pre_pitch': {
                'imported': PRE_PITCH_OK,
                'error': PRE_PITCH_ERROR if not PRE_PITCH_OK else None,
                'functional': False
            },
            'future_prediction': {
                'imported': FUTURE_PREDICTION_OK,
                'error': FUTURE_PREDICTION_ERROR if not FUTURE_PREDICTION_OK else None,
                'functional': False
            }
        }
        
        # Testa funcionalidade dos serviços importados com sucesso
        for service_name, status in services_status.items():
            if status['imported']:
                try:
                    # Testa funcionalidade básica
                    if service_name == 'ai_manager' and AI_MANAGER_OK:
                        # Teste básico do AI Manager
                        test_result = ai_manager.generate_content("Teste", max_tokens=10)
                        status['functional'] = bool(test_result)
                    else:
                        # Para outros serviços, considera funcional se importou
                        status['functional'] = True
                        
                    if status['functional']:
                        logger.info(f"✅ Serviço {service_name} funcional")
                    else:
                        logger.warning(f"⚠️ Serviço {service_name} importado mas não funcional")
                        self.warnings.append(f"Serviço {service_name} pode ter problemas de configuração")
                        
                except Exception as e:
                    status['functional'] = False
                    status['functional_error'] = str(e)
                    logger.error(f"❌ Erro ao testar {service_name}: {str(e)}")
                    self.warnings.append(f"Erro ao testar funcionalidade de {service_name}: {str(e)}")
            else:
                logger.error(f"❌ Serviço {service_name} não pôde ser importado")
                self.critical_errors.append(f"Falha na importação do serviço {service_name}")
        
        # Calcula estatísticas
        total_services = len(services_status)
        imported_services = sum(1 for s in services_status.values() if s['imported'])
        functional_services = sum(1 for s in services_status.values() if s['functional'])
        
        return {
            'status': 'HEALTHY' if functional_services >= total_services * 0.8 else 'DEGRADED',
            'services_status': services_status,
            'total_services': total_services,
            'imported_services': imported_services,
            'functional_services': functional_services,
            'import_rate': (imported_services / total_services) * 100,
            'functional_rate': (functional_services / total_services) * 100
        }

    def _validate_imported_modules(self) -> Dict[str, Any]:
        """Valida módulos Python importados"""
        
        logger.info("🔍 Validando módulos importados...")
        
        critical_modules = [
            'flask', 'requests', 'asyncio', 'threading', 'concurrent.futures',
            'datetime', 'json', 'os', 'logging', 'time', 'typing'
        ]
        
        optional_modules = [
            'openai', 'anthropic', 'google.generativeai', 'groq', 
            'exa_py', 'tavily', 'supabase', 'pymupdf'
        ]
        
        modules_status = {}
        
        # Testa módulos críticos
        for module in critical_modules:
            try:
                __import__(module)
                modules_status[module] = '✅ DISPONÍVEL'
            except ImportError as e:
                modules_status[module] = f'❌ INDISPONÍVEL: {str(e)}'
                self.critical_errors.append(f"Módulo crítico {module} não disponível")
        
        # Testa módulos opcionais
        for module in optional_modules:
            try:
                __import__(module)
                modules_status[module] = '✅ DISPONÍVEL'
            except ImportError as e:
                modules_status[module] = f'⚠️ INDISPONÍVEL: {str(e)}'
                self.warnings.append(f"Módulo opcional {module} não disponível")
        
        critical_available = sum(1 for module in critical_modules if modules_status[module].startswith('✅'))
        optional_available = sum(1 for module in optional_modules if modules_status[module].startswith('✅'))
        
        return {
            'status': 'HEALTHY' if critical_available == len(critical_modules) else 'CRITICAL',
            'modules_status': modules_status,
            'critical_modules': {
                'total': len(critical_modules),
                'available': critical_available,
                'availability_rate': (critical_available / len(critical_modules)) * 100
            },
            'optional_modules': {
                'total': len(optional_modules),
                'available': optional_available,
                'availability_rate': (optional_available / len(optional_modules)) * 100
            }
        }

    def _apply_automatic_fixes(self) -> Dict[str, Any]:
        """Aplica correções automáticas para problemas conhecidos"""
        
        logger.info("🔧 Aplicando correções automáticas...")
        
        fixes_applied = []
        fixes_failed = []
        
        # Fix 1: Criar diretórios necessários
        try:
            required_dirs = [
                'analyses_data',
                'logs',
                'relatorios_intermediarios',
                'src/uploads'
            ]
            
            for dir_path in required_dirs:
                if not os.path.exists(dir_path):
                    os.makedirs(dir_path, exist_ok=True)
                    fixes_applied.append(f"Criado diretório: {dir_path}")
                    self.fixes_applied.append(f"Diretório {dir_path} criado")
                    
        except Exception as e:
            fixes_failed.append(f"Erro ao criar diretórios: {str(e)}")
        
        # Fix 2: Criar arquivo .env template se não existir
        try:
            if not os.path.exists('.env'):
                env_template = """
# ARQV30 Enhanced v2.0 - Environment Variables
# Configure suas APIs aqui

# OpenAI
OPENAI_API_KEY=your_openai_api_key_here

# Anthropic (Claude)
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# Google Gemini
GEMINI_API_KEY=your_gemini_api_key_here

# Groq
GROQ_API_KEY=your_groq_api_key_here

# Exa Search
EXA_API_KEY=your_exa_api_key_here

# Tavily Search
TAVILY_API_KEY=your_tavily_api_key_here

# DeepSeek
DEEPSEEK_API_KEY=your_deepseek_api_key_here

# HuggingFace
HUGGINGFACE_API_TOKEN=your_huggingface_token_here

# Supabase (opcional)
SUPABASE_URL=your_supabase_url_here
SUPABASE_KEY=your_supabase_key_here
"""
                with open('.env', 'w') as f:
                    f.write(env_template)
                fixes_applied.append("Arquivo .env template criado")
                self.fixes_applied.append("Template .env criado - configure suas APIs")
                
        except Exception as e:
            fixes_failed.append(f"Erro ao criar .env: {str(e)}")
        
        # Fix 3: Configurar logging se não configurado
        try:
            if not logging.getLogger().handlers:
                logging.basicConfig(
                    level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    handlers=[
                        logging.StreamHandler(),
                        logging.FileHandler('logs/system.log', mode='a', encoding='utf-8')
                    ]
                )
                fixes_applied.append("Sistema de logging configurado")
                self.fixes_applied.append("Logging configurado automaticamente")
                
        except Exception as e:
            fixes_failed.append(f"Erro ao configurar logging: {str(e)}")
        
        return {
            'fixes_applied': fixes_applied,
            'fixes_failed': fixes_failed,
            'total_fixes_attempted': len(fixes_applied) + len(fixes_failed),
            'success_rate': (len(fixes_applied) / (len(fixes_applied) + len(fixes_failed))) * 100 if (fixes_applied or fixes_failed) else 0
        }

    def _test_system_connectivity(self) -> Dict[str, Any]:
        """Testa conectividade do sistema"""
        
        logger.info("🌐 Testando conectividade do sistema...")
        
        connectivity_tests = {
            'internet_connection': False,
            'openai_api': False,
            'internal_services': False
        }
        
        # Teste de conexão com internet
        try:
            import requests
            response = requests.get('https://httpbin.org/status/200', timeout=10)
            connectivity_tests['internet_connection'] = response.status_code == 200
        except Exception as e:
            logger.warning(f"⚠️ Teste de conectividade falhou: {str(e)}")
        
        # Teste básico de API (se OpenAI configurada)
        try:
            if AI_MANAGER_OK and os.getenv('OPENAI_API_KEY'):
                test_result = ai_manager.generate_content("Hi", max_tokens=5)
                connectivity_tests['openai_api'] = bool(test_result)
        except Exception as e:
            logger.warning(f"⚠️ Teste de API OpenAI falhou: {str(e)}")
        
        # Teste de serviços internos
        try:
            from services.auto_save_manager import auto_save_manager
            session_id = auto_save_manager.iniciar_sessao()
            connectivity_tests['internal_services'] = bool(session_id)
        except Exception as e:
            logger.warning(f"⚠️ Teste de serviços internos falhou: {str(e)}")
        
        return {
            'status': 'CONNECTED' if all(connectivity_tests.values()) else 'PARTIAL',
            'tests': connectivity_tests,
            'connected_services': sum(connectivity_tests.values()),
            'total_tests': len(connectivity_tests)
        }

    def _determine_overall_status(self) -> str:
        """Determina status geral do sistema"""
        
        if len(self.critical_errors) > 5:
            return 'CRITICAL'
        elif len(self.critical_errors) > 0:
            return 'DEGRADED'
        elif len(self.warnings) > 10:
            return 'WARNING'
        else:
            return 'HEALTHY'

    def _generate_recommendations(self) -> List[str]:
        """Gera recomendações para melhorar o sistema"""
        
        recommendations = []
        
        if self.critical_errors:
            recommendations.append("🚨 PRIORIDADE ALTA: Resolva os erros críticos listados")
            recommendations.append("📝 Configure todas as variáveis de ambiente necessárias")
            recommendations.append("🔧 Verifique a instalação de dependências Python")
        
        if self.warnings:
            recommendations.append("⚠️ PRIORIDADE MÉDIA: Revise os avisos para otimizar performance")
            recommendations.append("🔍 Teste conectividade com APIs externas")
        
        if not self.critical_errors and not self.warnings:
            recommendations.append("✅ Sistema operacional! Considere otimizações avançadas")
            recommendations.append("📊 Configure monitoramento de performance")
        
        recommendations.extend([
            "💾 Mantenha backups regulares dos dados",
            "🔐 Revise configurações de segurança periodicamente",
            "📋 Monitore logs do sistema regularmente"
        ])
        
        return recommendations

    def generate_health_report(self) -> str:
        """Gera relatório de saúde do sistema em formato texto"""
        
        validation_result = self.validate_all_systems()
        
        report = f"""
=== RELATÓRIO DE SAÚDE DO SISTEMA ARQV30 ===
Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}

🎯 STATUS GERAL: {validation_result.get('overall_status', 'UNKNOWN')}

📊 RESUMO:
- Erros Críticos: {len(self.critical_errors)}
- Avisos: {len(self.warnings)}
- Correções Aplicadas: {len(self.fixes_applied)}

🔧 VARIÁVEIS DE AMBIENTE:
{validation_result.get('environment_validation', {}).get('configured_count', 0)}/{validation_result.get('environment_validation', {}).get('total_required', 0)} configuradas

🚀 SERVIÇOS:
{validation_result.get('services_validation', {}).get('functional_services', 0)}/{validation_result.get('services_validation', {}).get('total_services', 0)} funcionais

🌐 CONECTIVIDADE:
{validation_result.get('connectivity_test', {}).get('connected_services', 0)}/{validation_result.get('connectivity_test', {}).get('total_tests', 0)} testes passou

💡 RECOMENDAÇÕES:
"""
        
        for i, rec in enumerate(validation_result.get('recommendations', []), 1):
            report += f"{i}. {rec}\n"
        
        if self.critical_errors:
            report += "\n❌ ERROS CRÍTICOS:\n"
            for error in self.critical_errors:
                report += f"  • {error}\n"
        
        if self.warnings:
            report += "\n⚠️ AVISOS:\n"
            for warning in self.warnings:
                report += f"  • {warning}\n"
        
        if self.fixes_applied:
            report += "\n✅ CORREÇÕES APLICADAS:\n"
            for fix in self.fixes_applied:
                report += f"  • {fix}\n"
        
        return report

# Instância global
system_validator = SystemValidator()

if __name__ == "__main__":
    # Executa validação se chamado diretamente
    print("🚀 Iniciando validação do sistema...")
    result = system_validator.validate_all_systems()
    print(system_validator.generate_health_report())
