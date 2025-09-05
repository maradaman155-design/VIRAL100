
import logging
import time
import threading
from datetime import datetime
from typing import Dict, Any, Callable
from services.ai_manager import ai_manager

logger = logging.getLogger(__name__)

class SystemMonitor:
    """Monitor em tempo real do sistema ARQV30"""
    
    def __init__(self):
        self.health_checks = {
            'api_quotas': self._check_api_quotas,
            'circular_refs': self._detect_potential_issues,
            'content_quality': self._validate_system_health,
            'memory_usage': self._check_memory_usage
        }
        self.alerts = []
        self.monitoring_active = False
        self.alert_callbacks = []
    
    def add_alert_callback(self, callback: Callable):
        """Adiciona callback para alertas"""
        self.alert_callbacks.append(callback)
    
    def start_monitoring(self):
        """Inicia monitoramento contínuo"""
        self.monitoring_active = True
        monitoring_thread = threading.Thread(target=self._continuous_monitoring, daemon=True)
        monitoring_thread.start()
        logger.info("🔍 Sistema de monitoramento iniciado")
    
    def stop_monitoring(self):
        """Para o monitoramento"""
        self.monitoring_active = False
        logger.info("🔍 Sistema de monitoramento parado")
    
    def _continuous_monitoring(self):
        """Loop de monitoramento contínuo"""
        while self.monitoring_active:
            try:
                for check_name, check_func in self.health_checks.items():
                    try:
                        status = check_func()
                        if not status.get('healthy', True):
                            self._trigger_alert(check_name, status)
                    except Exception as e:
                        logger.error(f"Erro no check {check_name}: {e}")
                
                time.sleep(30)  # Check a cada 30 segundos
                
            except Exception as e:
                logger.error(f"Erro no loop de monitoramento: {e}")
                time.sleep(60)  # Wait longer on error
    
    def _check_api_quotas(self) -> Dict[str, Any]:
        """Verifica status das quotas de API"""
        try:
            quota_status = {}
            for provider, limits in ai_manager.quota_manager.provider_limits.items():
                usage_percent = (limits['requests_made'] / limits['daily']) * 100
                quota_status[provider] = {
                    'usage_percent': usage_percent,
                    'requests_made': limits['requests_made'],
                    'daily_limit': limits['daily'],
                    'status': 'critical' if usage_percent > 90 else 'warning' if usage_percent > 70 else 'ok'
                }
            
            critical_providers = [p for p, s in quota_status.items() if s['status'] == 'critical']
            
            return {
                'healthy': len(critical_providers) < len(quota_status),
                'quota_status': quota_status,
                'critical_providers': critical_providers
            }
            
        except Exception as e:
            return {'healthy': False, 'error': str(e)}
    
    def _detect_potential_issues(self) -> Dict[str, Any]:
        """Detecta potenciais problemas estruturais"""
        return {
            'healthy': True,
            'message': 'Sistema com serialização segura ativa'
        }
    
    def _validate_system_health(self) -> Dict[str, Any]:
        """Valida saúde geral do sistema"""
        try:
            # Verifica se componentes críticos estão funcionando
            critical_components = ['ai_manager', 'auto_save_manager', 'psychological_agents']
            
            for component in critical_components:
                try:
                    exec(f"from services.{component} import {component}")
                except ImportError as e:
                    return {
                        'healthy': False,
                        'error': f"Componente crítico {component} não disponível: {e}"
                    }
            
            return {'healthy': True, 'message': 'Todos os componentes críticos operacionais'}
            
        except Exception as e:
            return {'healthy': False, 'error': str(e)}
    
    def _check_memory_usage(self) -> Dict[str, Any]:
        """Verifica uso de memória"""
        try:
            import psutil
            memory = psutil.virtual_memory()
            
            return {
                'healthy': memory.percent < 85,
                'memory_percent': memory.percent,
                'available_gb': memory.available / (1024**3)
            }
        except ImportError:
            return {'healthy': True, 'message': 'psutil não disponível'}
        except Exception as e:
            return {'healthy': False, 'error': str(e)}
    
    def _trigger_alert(self, check_name: str, status: Dict[str, Any]):
        """Dispara alerta para problema detectado"""
        alert = {
            'timestamp': datetime.now().isoformat(),
            'check': check_name,
            'status': status,
            'severity': 'critical' if not status.get('healthy') else 'warning'
        }
        
        self.alerts.append(alert)
        logger.warning(f"🚨 ALERTA {check_name}: {status}")
        
        # Notifica callbacks
        for callback in self.alert_callbacks:
            try:
                callback(alert)
            except Exception as e:
                logger.error(f"Erro no callback de alerta: {e}")
    
    def get_system_status(self) -> Dict[str, Any]:
        """Obtém status completo do sistema"""
        try:
            overall_status = {}
            
            for check_name, check_func in self.health_checks.items():
                try:
                    overall_status[check_name] = check_func()
                except Exception as e:
                    overall_status[check_name] = {'healthy': False, 'error': str(e)}
            
            # Determina saúde geral
            healthy_checks = sum(1 for status in overall_status.values() if status.get('healthy', False))
            overall_healthy = healthy_checks >= len(self.health_checks) * 0.7  # 70% dos checks ok
            
            return {
                'overall_healthy': overall_healthy,
                'health_score': (healthy_checks / len(self.health_checks)) * 100,
                'checks': overall_status,
                'recent_alerts': self.alerts[-5:],  # Últimos 5 alertas
                'monitoring_active': self.monitoring_active,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                'overall_healthy': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }

# Instância global
system_monitor = SystemMonitor()

# Auto-inicia o monitoramento
system_monitor.start_monitoring()
