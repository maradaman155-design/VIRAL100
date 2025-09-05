#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ARQV30 Enhanced v2.0 - Rotas de Usuário
Endpoints para gerenciamento de usuários e sessões
"""

import logging
import uuid
from datetime import datetime
from flask import Blueprint, request, jsonify, session
from database import db_manager

logger = logging.getLogger(__name__)

# Cria blueprint
user_bp = Blueprint('user', __name__)

@user_bp.route('/session/new', methods=['POST'])
def create_session():
    """Cria nova sessão de usuário"""
    
    try:
        # Gera ID único para sessão
        session_id = str(uuid.uuid4())
        
        # Dados opcionais da sessão
        data = request.get_json() or {}
        user_info = {
            'session_id': session_id,
            'created_at': datetime.now().isoformat(),
            'user_agent': request.headers.get('User-Agent', ''),
            'ip_address': request.remote_addr,
            'metadata': data.get('metadata', {})
        }
        
        # Salva na sessão Flask
        session['session_id'] = session_id
        session['created_at'] = user_info['created_at']
        
        logger.info(f"Nova sessão criada: {session_id}")
        
        return jsonify({
            'session_id': session_id,
            'created_at': user_info['created_at'],
            'message': 'Sessão criada com sucesso'
        })
        
    except Exception as e:
        logger.error(f"Erro ao criar sessão: {str(e)}")
        return jsonify({
            'error': 'Erro ao criar sessão',
            'message': str(e)
        }), 500

@user_bp.route('/session/info', methods=['GET'])
def get_session_info():
    """Obtém informações da sessão atual"""
    
    try:
        session_id = request.args.get('session_id') or session.get('session_id')
        
        if not session_id:
            return jsonify({
                'error': 'Sessão não encontrada',
                'message': 'Nenhuma sessão ativa encontrada'
            }), 404
        
        # Informações básicas da sessão
        session_info = {
            'session_id': session_id,
            'created_at': session.get('created_at'),
            'active': True
        }
        
        # Estatísticas da sessão (se disponível no banco)
        try:
            stats = db_manager.get_stats()
            session_info['stats'] = stats
        except:
            session_info['stats'] = None
        
        return jsonify(session_info)
        
    except Exception as e:
        logger.error(f"Erro ao obter info da sessão: {str(e)}")
        return jsonify({
            'error': 'Erro ao obter informações da sessão',
            'message': str(e)
        }), 500

@user_bp.route('/session/validate', methods=['POST'])
def validate_session():
    """Valida se uma sessão é válida"""
    
    try:
        data = request.get_json()
        session_id = data.get('session_id') if data else None
        
        if not session_id:
            return jsonify({
                'valid': False,
                'message': 'Session ID não fornecido'
            }), 400
        
        # Verifica se é uma sessão válida (formato UUID)
        try:
            uuid.UUID(session_id)
            valid = True
        except ValueError:
            valid = False
        
        return jsonify({
            'session_id': session_id,
            'valid': valid,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Erro ao validar sessão: {str(e)}")
        return jsonify({
            'error': 'Erro ao validar sessão',
            'message': str(e)
        }), 500

@user_bp.route('/user/stats', methods=['GET'])
def get_user_stats():
    """Obtém estatísticas do usuário/sistema"""
    
    try:
        # Obtém estatísticas do banco
        stats = db_manager.get_stats()
        
        # Adiciona informações do sistema
        system_stats = {
            'timestamp': datetime.now().isoformat(),
            'version': '2.0.0',
            'uptime': 'N/A'  # Seria calculado em produção
        }
        
        return jsonify({
            'database_stats': stats,
            'system_stats': system_stats
        })
        
    except Exception as e:
        logger.error(f"Erro ao obter estatísticas: {str(e)}")
        return jsonify({
            'error': 'Erro ao obter estatísticas',
            'message': str(e)
        }), 500

@user_bp.route('/user/preferences', methods=['GET', 'POST'])
def user_preferences():
    """Gerencia preferências do usuário"""
    
    try:
        session_id = request.args.get('session_id') or session.get('session_id')
        
        if not session_id:
            return jsonify({
                'error': 'Sessão não encontrada',
                'message': 'Nenhuma sessão ativa encontrada'
            }), 404
        
        if request.method == 'GET':
            # Retorna preferências (por enquanto padrão)
            preferences = {
                'language': 'pt-BR',
                'theme': 'light',
                'notifications': True,
                'auto_save': True
            }
            
            return jsonify({
                'session_id': session_id,
                'preferences': preferences
            })
        
        elif request.method == 'POST':
            # Atualiza preferências
            data = request.get_json()
            preferences = data.get('preferences', {})
            
            # Salva na sessão (em produção seria no banco)
            session['preferences'] = preferences
            
            return jsonify({
                'session_id': session_id,
                'preferences': preferences,
                'message': 'Preferências atualizadas com sucesso'
            })
        
    except Exception as e:
        logger.error(f"Erro nas preferências: {str(e)}")
        return jsonify({
            'error': 'Erro ao gerenciar preferências',
            'message': str(e)
        }), 500

@user_bp.route('/user/activity', methods=['GET'])
def get_user_activity():
    """Obtém atividade recente do usuário"""
    
    try:
        session_id = request.args.get('session_id') or session.get('session_id')
        limit = min(int(request.args.get('limit', 10)), 50)
        
        if not session_id:
            return jsonify({
                'error': 'Sessão não encontrada',
                'message': 'Nenhuma sessão ativa encontrada'
            }), 404
        
        # Em produção, buscaria atividades do banco
        # Por enquanto retorna atividade simulada
        activities = [
            {
                'id': 1,
                'type': 'analysis_created',
                'description': 'Nova análise de mercado criada',
                'timestamp': datetime.now().isoformat(),
                'metadata': {'segmento': 'Produtos Digitais'}
            },
            {
                'id': 2,
                'type': 'attachment_uploaded',
                'description': 'Anexo processado com sucesso',
                'timestamp': datetime.now().isoformat(),
                'metadata': {'filename': 'documento.pdf'}
            }
        ]
        
        return jsonify({
            'session_id': session_id,
            'activities': activities[:limit],
            'count': len(activities)
        })
        
    except Exception as e:
        logger.error(f"Erro ao obter atividade: {str(e)}")
        return jsonify({
            'error': 'Erro ao obter atividade do usuário',
            'message': str(e)
        }), 500

@user_bp.route('/user/export', methods=['POST'])
def export_user_data():
    """Exporta dados do usuário"""
    
    try:
        data = request.get_json()
        session_id = data.get('session_id') if data else None
        export_format = data.get('format', 'json') if data else 'json'
        
        if not session_id:
            return jsonify({
                'error': 'Session ID obrigatório',
                'message': 'Forneça o session_id para exportação'
            }), 400
        
        # Em produção, coletaria todos os dados do usuário
        user_data = {
            'session_id': session_id,
            'export_date': datetime.now().isoformat(),
            'analyses': [],  # Seria preenchido com análises do usuário
            'attachments': [],  # Seria preenchido com anexos do usuário
            'preferences': session.get('preferences', {}),
            'metadata': {
                'version': '2.0.0',
                'format': export_format
            }
        }
        
        return jsonify({
            'message': 'Dados exportados com sucesso',
            'export_data': user_data,
            'download_url': None  # Em produção seria um link para download
        })
        
    except Exception as e:
        logger.error(f"Erro na exportação: {str(e)}")
        return jsonify({
            'error': 'Erro ao exportar dados',
            'message': str(e)
        }), 500

@user_bp.route('/user/feedback', methods=['POST'])
def submit_feedback():
    """Recebe feedback do usuário"""
    
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'error': 'Dados não fornecidos',
                'message': 'Envie o feedback no corpo da requisição'
            }), 400
        
        feedback = {
            'session_id': data.get('session_id'),
            'rating': data.get('rating'),
            'message': data.get('message', ''),
            'category': data.get('category', 'general'),
            'timestamp': datetime.now().isoformat(),
            'user_agent': request.headers.get('User-Agent', ''),
            'ip_address': request.remote_addr
        }
        
        # Em produção, salvaria no banco
        logger.info(f"Feedback recebido: {feedback}")
        
        return jsonify({
            'message': 'Feedback recebido com sucesso',
            'feedback_id': str(uuid.uuid4()),
            'timestamp': feedback['timestamp']
        })
        
    except Exception as e:
        logger.error(f"Erro ao receber feedback: {str(e)}")
        return jsonify({
            'error': 'Erro ao processar feedback',
            'message': str(e)
        }), 500

