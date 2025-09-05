#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ARQV30 Enhanced v2.0 - Rotas de Arquivos
Endpoints para gerenciamento de arquivos locais das análises
"""

import os
import logging
from datetime import datetime
from flask import Blueprint, request, jsonify, send_file
from services.local_file_manager import local_file_manager
from database import db_manager

logger = logging.getLogger(__name__)

# Cria blueprint
files_bp = Blueprint('files', __name__)

@files_bp.route('/list_local_analyses', methods=['GET'])
def list_local_analyses():
    """Lista análises salvas localmente"""
    
    try:
        analyses = local_file_manager.list_local_analyses()
        
        return jsonify({
            'success': True,
            'analyses': analyses,
            'count': len(analyses),
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Erro ao listar análises locais: {str(e)}")
        return jsonify({
            'error': 'Erro ao listar análises locais',
            'message': str(e)
        }), 500

@files_bp.route('/get_analysis_files/<analysis_id>', methods=['GET'])
def get_analysis_files(analysis_id):
    """Obtém arquivos de uma análise específica"""
    
    try:
        # Busca arquivos no Supabase
        supabase_files = db_manager.get_analysis_files(analysis_id)
        
        # Busca diretório local
        local_directory = local_file_manager.get_analysis_directory(analysis_id)
        
        local_files = []
        if local_directory:
            for file in os.listdir(local_directory):
                if analysis_id[:8] in file:
                    file_path = os.path.join(local_directory, file)
                    local_files.append({
                        'name': file,
                        'path': file_path,
                        'size': os.path.getsize(file_path),
                        'type': file.split('_')[-1].split('.')[0] if '_' in file else 'unknown',
                        'modified': datetime.fromtimestamp(os.path.getmtime(file_path)).isoformat()
                    })
        
        return jsonify({
            'success': True,
            'analysis_id': analysis_id,
            'supabase_files': supabase_files,
            'local_files': local_files,
            'local_directory': local_directory,
            'total_files': len(supabase_files) + len(local_files)
        })
        
    except Exception as e:
        logger.error(f"Erro ao obter arquivos da análise {analysis_id}: {str(e)}")
        return jsonify({
            'error': 'Erro ao obter arquivos da análise',
            'message': str(e)
        }), 500

@files_bp.route('/download_file', methods=['GET'])
def download_file():
    """Download de arquivo local"""
    
    try:
        file_path = request.args.get('path')
        
        if not file_path:
            return jsonify({
                'error': 'Caminho do arquivo não fornecido'
            }), 400
        
        # Verifica se o arquivo existe e está no diretório permitido
        if not os.path.exists(file_path):
            return jsonify({
                'error': 'Arquivo não encontrado'
            }), 404
        
        # Verifica se está no diretório de análises
        if not file_path.startswith(local_file_manager.base_dir):
            return jsonify({
                'error': 'Acesso negado ao arquivo'
            }), 403
        
        return send_file(
            file_path,
            as_attachment=True,
            download_name=os.path.basename(file_path)
        )
        
    except Exception as e:
        logger.error(f"Erro no download do arquivo: {str(e)}")
        return jsonify({
            'error': 'Erro no download do arquivo',
            'message': str(e)
        }), 500

@files_bp.route('/delete_local_analysis/<analysis_id>', methods=['DELETE'])
def delete_local_analysis(analysis_id):
    """Remove análise local por ID"""
    
    try:
        # Remove do Supabase
        supabase_result = db_manager.supabase.delete_analysis(analysis_id)
        
        # Remove arquivos locais
        local_result = local_file_manager.delete_local_analysis(analysis_id)
        
        if supabase_result or local_result:
            return jsonify({
                'success': True,
                'message': 'Análise removida com sucesso',
                'supabase_deleted': supabase_result,
                'local_deleted': local_result
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Análise não encontrada'
            }), 404
            
    except Exception as e:
        logger.error(f"Erro ao deletar análise {analysis_id}: {str(e)}")
        return jsonify({
            'error': 'Erro ao deletar análise',
            'message': str(e)
        }), 500

@files_bp.route('/get_file_content', methods=['GET'])
def get_file_content():
    """Obtém conteúdo de um arquivo local"""
    
    try:
        file_path = request.args.get('path')
        max_chars = int(request.args.get('max_chars', 5000))
        
        if not file_path:
            return jsonify({
                'error': 'Caminho do arquivo não fornecido'
            }), 400
        
        # Verifica se o arquivo existe e está no diretório permitido
        if not os.path.exists(file_path):
            return jsonify({
                'error': 'Arquivo não encontrado'
            }), 404
        
        if not file_path.startswith(local_file_manager.base_dir):
            return jsonify({
                'error': 'Acesso negado ao arquivo'
            }), 403
        
        # Lê conteúdo do arquivo
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Limita tamanho se necessário
        if len(content) > max_chars:
            content = content[:max_chars] + f"\n\n... [Arquivo truncado - {len(content)} caracteres totais]"
        
        return jsonify({
            'success': True,
            'file_path': file_path,
            'file_name': os.path.basename(file_path),
            'content': content,
            'file_size': os.path.getsize(file_path),
            'truncated': len(content) > max_chars
        })
        
    except Exception as e:
        logger.error(f"Erro ao ler arquivo: {str(e)}")
        return jsonify({
            'error': 'Erro ao ler arquivo',
            'message': str(e)
        }), 500

@files_bp.route('/export_analysis/<analysis_id>', methods=['GET'])
def export_analysis(analysis_id):
    """Exporta análise completa como ZIP"""
    
    try:
        import zipfile
        import tempfile
        
        # Busca diretório da análise
        analysis_dir = local_file_manager.get_analysis_directory(analysis_id)
        
        if not analysis_dir:
            return jsonify({
                'error': 'Análise não encontrada'
            }), 404
        
        # Cria arquivo ZIP temporário
        with tempfile.NamedTemporaryFile(delete=False, suffix='.zip') as tmp_file:
            zip_path = tmp_file.name
        
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            # Adiciona todos os arquivos da análise
            for root, dirs, files in os.walk(local_file_manager.base_dir):
                for file in files:
                    if analysis_id[:8] in file:
                        file_path = os.path.join(root, file)
                        # Nome no ZIP será relativo ao diretório base
                        arcname = os.path.relpath(file_path, local_file_manager.base_dir)
                        zipf.write(file_path, arcname)
        
        return send_file(
            zip_path,
            as_attachment=True,
            download_name=f"analise_{analysis_id[:8]}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip",
            mimetype='application/zip'
        )
        
    except Exception as e:
        logger.error(f"Erro ao exportar análise {analysis_id}: {str(e)}")
        return jsonify({
            'error': 'Erro ao exportar análise',
            'message': str(e)
        }), 500

@files_bp.route('/storage_stats', methods=['GET'])
def get_storage_stats():
    """Obtém estatísticas de armazenamento"""
    
    try:
        # Estatísticas do diretório local
        total_size = 0
        total_files = 0
        
        for root, dirs, files in os.walk(local_file_manager.base_dir):
            for file in files:
                file_path = os.path.join(root, file)
                try:
                    total_size += os.path.getsize(file_path)
                    total_files += 1
                except:
                    continue
        
        # Estatísticas por tipo
        type_stats = {}
        for subdir in ['avatars', 'drivers_mentais', 'provas_visuais', 'anti_objecao', 
                      'pre_pitch', 'predicoes_futuro', 'posicionamento', 'concorrencia',
                      'palavras_chave', 'metricas', 'funil_vendas', 'plano_acao', 
                      'insights', 'pesquisa_web', 'completas', 'metadata']:
            
            subdir_path = os.path.join(local_file_manager.base_dir, subdir)
            if os.path.exists(subdir_path):
                subdir_files = len([f for f in os.listdir(subdir_path) if os.path.isfile(os.path.join(subdir_path, f))])
                subdir_size = sum(os.path.getsize(os.path.join(subdir_path, f)) 
                                for f in os.listdir(subdir_path) 
                                if os.path.isfile(os.path.join(subdir_path, f)))
                
                type_stats[subdir] = {
                    'files': subdir_files,
                    'size_bytes': subdir_size,
                    'size_mb': round(subdir_size / (1024 * 1024), 2)
                }
        
        return jsonify({
            'success': True,
            'storage_stats': {
                'base_directory': local_file_manager.base_dir,
                'total_files': total_files,
                'total_size_bytes': total_size,
                'total_size_mb': round(total_size / (1024 * 1024), 2),
                'total_size_gb': round(total_size / (1024 * 1024 * 1024), 3),
                'type_breakdown': type_stats
            },
            'supabase_connected': db_manager.supabase.is_connected(),
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Erro ao obter estatísticas de armazenamento: {str(e)}")
        return jsonify({
            'error': 'Erro ao obter estatísticas de armazenamento',
            'message': str(e)
        }), 500

@files_bp.route('/cleanup_old_files', methods=['POST'])
def cleanup_old_files():
    """Remove arquivos antigos (mais de 30 dias)"""
    
    try:
        data = request.get_json() or {}
        days_old = int(data.get('days_old', 30))
        dry_run = data.get('dry_run', True)  # Por padrão, apenas simula
        
        from datetime import timedelta
        cutoff_date = datetime.now() - timedelta(days=days_old)
        
        files_to_remove = []
        total_size_to_remove = 0
        
        # Busca arquivos antigos
        for root, dirs, files in os.walk(local_file_manager.base_dir):
            for file in files:
                file_path = os.path.join(root, file)
                try:
                    file_mtime = datetime.fromtimestamp(os.path.getmtime(file_path))
                    
                    if file_mtime < cutoff_date:
                        file_size = os.path.getsize(file_path)
                        files_to_remove.append({
                            'path': file_path,
                            'name': file,
                            'size': file_size,
                            'modified': file_mtime.isoformat()
                        })
                        total_size_to_remove += file_size
                        
                        # Remove arquivo se não for dry run
                        if not dry_run:
                            os.remove(file_path)
                            logger.info(f"🗑️ Arquivo removido: {file}")
                            
                except Exception as e:
                    logger.error(f"Erro ao processar arquivo {file}: {str(e)}")
                    continue
        
        action = "Simulação de limpeza" if dry_run else "Limpeza executada"
        
        return jsonify({
            'success': True,
            'action': action,
            'files_found': len(files_to_remove),
            'total_size_mb': round(total_size_to_remove / (1024 * 1024), 2),
            'cutoff_date': cutoff_date.isoformat(),
            'files': files_to_remove if dry_run else [],
            'dry_run': dry_run
        })
        
    except Exception as e:
        logger.error(f"Erro na limpeza de arquivos: {str(e)}")
        return jsonify({
            'error': 'Erro na limpeza de arquivos',
            'message': str(e)
        }), 500

@files_bp.route('/backup_to_supabase', methods=['POST'])
def backup_to_supabase():
    """Faz backup de análises locais para Supabase"""
    
    try:
        if not db_manager.supabase.is_connected():
            return jsonify({
                'error': 'Supabase não está conectado',
                'message': 'Configure as credenciais do Supabase'
            }), 400
        
        # Lista análises locais
        local_analyses = local_file_manager.list_local_analyses()
        
        backed_up = 0
        errors = []
        
        for analysis in local_analyses:
            try:
                analysis_id = analysis['analysis_id']
                
                # Verifica se já existe no Supabase
                existing = db_manager.supabase.get_analysis(analysis_id)
                if existing:
                    logger.info(f"⚠️ Análise {analysis_id} já existe no Supabase")
                    continue
                
                # Carrega análise completa do arquivo JSON
                json_file = None
                for root, dirs, files in os.walk(local_file_manager.base_dir):
                    for file in files:
                        if analysis_id[:8] in file and file.endswith('_completa.json'):
                            json_file = os.path.join(root, file)
                            break
                    if json_file:
                        break
                
                if json_file:
                    with open(json_file, 'r', encoding='utf-8') as f:
                        analysis_data = json.load(f)
                    
                    # Salva no Supabase
                    result = db_manager.supabase.create_analysis(analysis_data)
                    if result:
                        backed_up += 1
                        logger.info(f"✅ Backup realizado: {analysis_id}")
                    else:
                        errors.append(f"Falha ao fazer backup de {analysis_id}")
                else:
                    errors.append(f"Arquivo JSON não encontrado para {analysis_id}")
                    
            except Exception as e:
                error_msg = f"Erro no backup de {analysis.get('analysis_id', 'unknown')}: {str(e)}"
                errors.append(error_msg)
                logger.error(error_msg)
        
        return jsonify({
            'success': True,
            'message': f'Backup concluído: {backed_up} análises',
            'total_local': len(local_analyses),
            'backed_up': backed_up,
            'errors': errors,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Erro no backup para Supabase: {str(e)}")
        return jsonify({
            'error': 'Erro no backup para Supabase',
            'message': str(e)
        }), 500

@files_bp.route('/sync_with_supabase', methods=['POST'])
def sync_with_supabase():
    """Sincroniza análises entre local e Supabase"""
    
    try:
        if not db_manager.supabase.is_connected():
            return jsonify({
                'error': 'Supabase não está conectado'
            }), 400
        
        # Lista análises do Supabase
        supabase_analyses = db_manager.supabase.list_analyses(100)
        
        # Lista análises locais
        local_analyses = local_file_manager.list_local_analyses()
        
        # Identifica diferenças
        supabase_ids = set(a['id'] for a in supabase_analyses)
        local_ids = set(a['analysis_id'] for a in local_analyses)
        
        only_supabase = supabase_ids - local_ids
        only_local = local_ids - supabase_ids
        both = supabase_ids & local_ids
        
        return jsonify({
            'success': True,
            'sync_status': {
                'total_supabase': len(supabase_analyses),
                'total_local': len(local_analyses),
                'only_in_supabase': len(only_supabase),
                'only_in_local': len(only_local),
                'in_both': len(both),
                'sync_needed': len(only_supabase) + len(only_local) > 0
            },
            'details': {
                'only_supabase_ids': list(only_supabase),
                'only_local_ids': list(only_local),
                'synced_ids': list(both)
            },
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Erro na sincronização: {str(e)}")
        return jsonify({
            'error': 'Erro na sincronização',
            'message': str(e)
        }), 500