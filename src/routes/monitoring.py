#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ARQV30 Enhanced v2.0 - Monitoring Routes
Endpoints para monitoramento do sistema de extração
"""
from flask import Blueprint, jsonify, request
from services.robust_content_extractor import robust_content_extractor
import logging
from datetime import datetime # Import datetime

logger = logging.getLogger(__name__)

monitoring_bp = Blueprint('monitoring', __name__)


@monitoring_bp.route('/api/extractor_stats', methods=['GET'])
def get_extractor_stats():
    """Retorna estatísticas dos extratores"""
    try:
        stats = robust_content_extractor.get_extractor_stats()
        return jsonify({
            'success': True,
            'stats': stats
        })
    except Exception as e:
        logger.error(f"❌ Erro ao obter estatísticas: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@monitoring_bp.route('/api/test_extraction', methods=['GET'])
def test_extraction():
    """Testa extração para uma URL específica"""
    url = request.args.get('url')

    if not url:
        return jsonify({
            'success': False,
            'error': 'URL é obrigatória'
        }), 400

    try:
        # Testa extração com detalhes
        content = robust_content_extractor.extract_content(url)

        if content:
            # Valida qualidade do conteúdo
            from services.content_quality_validator import content_quality_validator
            validation = content_quality_validator.validate_content(content, url)

            result = {
                'success': True,
                'url': url,
                'content_length': len(content),
                'content_preview': content[:500] + '...' if len(content) > 500 else content,
                'validation': validation,
                'extractor_stats': robust_content_extractor.get_extractor_stats()
            }
        else:
            result = {
                'success': False,
                'url': url,
                'error': 'Falha na extração de conteúdo',
                'extractor_stats': robust_content_extractor.get_extractor_stats()
            }

        return jsonify({
            'success': result['success'],
            **result
        })
    except Exception as e:
        logger.error(f"❌ Erro ao testar extração: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e),
            'extractor_stats': robust_content_extractor.get_extractor_stats()
        }), 500


@monitoring_bp.route('/api/health', methods=['GET'])
def health_check():
    """Verificação de saúde do sistema"""
    try:
        # Importa o health checker
        from services.health_checker import health_checker
        from services.system_monitor import system_monitor

        # Executa verificação completa
        health_status = health_checker.check_system_health()
        monitor_status = system_monitor.get_system_status()

        return jsonify({
            'status': 'healthy' if monitor_status.get('overall_healthy', False) else 'degraded',
            'timestamp': datetime.now().isoformat(),
            'health_details': health_status,
            'monitoring': monitor_status,
            'api_quotas': monitor_status.get('checks', {}).get('api_quotas', {}),
            'serialization_safety': 'active'
        })

    except Exception as e:
        logger.error(f"Erro na verificação de saúde: {e}")
        return jsonify({
            'status': 'error',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500


@monitoring_bp.route('/quotas', methods=['GET'])
def check_quotas():
    """Verificação específica de quotas de API"""
    try:
        from services.ai_manager import ai_manager
        from services.system_monitor import system_monitor

        quota_status = system_monitor._check_api_quotas()

        return jsonify({
            'success': True,
            'quotas': quota_status,
            'recommendations': [
                f"Provider {p} em estado {s['status']}"
                for p, s in quota_status.get('quota_status', {}).items()
                if s['status'] != 'ok'
            ],
            'timestamp': datetime.now().isoformat()
        })

    except Exception as e:
        logger.error(f"Erro ao verificar quotas: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500


# Assuming 'app' is defined elsewhere and this blueprint is registered with it.
# The following route is a placeholder to demonstrate the requested change.
# In a real Flask application, this route would likely be defined within your main app file
# or another blueprint, and 'app' would be the Flask application instance.
# For the purpose of this response, we simulate its inclusion.

# Placeholder for 'app' if it's not defined in this file
# In a real scenario, you would have:
# from flask import Flask
# app = Flask(__name__)
# then register the blueprint:
# app.register_blueprint(monitoring_bp)

# The following is the corrected section based on the provided changes.
# Assuming 'app' is the Flask application instance.
# If 'app' is not defined in this file, this section would need to be adapted
# to where your Flask app instance is defined.

# @app.route('/api/app_status')
# def app_status():
#     try:
#         # Lógica existente do status
#         status_data = get_system_status() # Assuming get_system_status is defined elsewhere
#         return jsonify(status_data)
#     except Exception as e:
#         logger.error(f"Error in app_status: {e}")
#         return jsonify({"error": str(e)}), 500

# The following is the modified route as per the user's request.
# It is assumed that 'app' is available in the scope where this blueprint is registered.
# If this blueprint is being registered in a main app file, then 'app' will be available there.
# For the purpose of generating the complete file, we'll assume it's handled correctly
# when this blueprint is registered with the Flask app instance.

# If this code is in a separate file that defines a blueprint,
# the application instance 'app' would typically be passed during registration.
# Example:
# from flask import Flask
# from monitoring import monitoring_bp
# app = Flask(__name__)
# app.register_blueprint(monitoring_bp)
# Then the route would be defined within the blueprint or the app file.

# As the original code provided does not contain an '@app.route('/api/app_status')' definition.
# The change provided is to replace such a route.
# Therefore, I will add the new route definition as requested.

@monitoring_bp.route('/api/app_status')
def app_status():
    try:
        from src.services.health_checker import HealthChecker
        health_checker = HealthChecker()
        status_data = health_checker.get_system_health()

        # Garantir que status_data é um dicionário válido
        if not isinstance(status_data, dict):
            status_data = {
                "status": "unknown",
                "health_score": 0,
                "services": {},
                "timestamp": datetime.now().isoformat()
            }

        return jsonify(status_data)
    except Exception as e:
        logger.error(f"Error in app_status: {e}")
        return jsonify({
            "error": "Internal server error",
            "status": "error",
            "timestamp": datetime.now().isoformat()
        }), 500