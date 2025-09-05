
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ARQV30 Enhanced v3.0 - Enhanced Analysis Route
Rota de análise aprimorada
"""

import logging
from datetime import datetime
from flask import Blueprint, request, jsonify

logger = logging.getLogger(__name__)

enhanced_analysis_bp = Blueprint('enhanced_analysis', __name__)

@enhanced_analysis_bp.route('/enhanced_execute', methods=['POST'])
def enhanced_execute():
    """Execução de análise aprimorada"""
    try:
        # Redireciona para a análise principal
        from routes.analysis import execute_complete_analysis
        return execute_complete_analysis()
        
    except Exception as e:
        logger.error(f"Erro na análise aprimorada: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@enhanced_analysis_bp.route('/status', methods=['GET'])
def enhanced_status():
    """Status do sistema aprimorado"""
    return jsonify({
        "status": "operational",
        "timestamp": datetime.now().isoformat()
    }), 200
