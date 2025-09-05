#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ARQV30 Enhanced v2.0 - Local File Manager
Gerenciador de arquivos locais para análises ultra-detalhadas
"""

import os
import logging
import json
import time
from datetime import datetime
from typing import Dict, List, Optional, Any
import uuid

logger = logging.getLogger(__name__)

class LocalFileManager:
    """Gerenciador de arquivos locais para análises"""
    
    def __init__(self):
        """Inicializa o gerenciador de arquivos locais"""
        self.base_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'analyses_data')
        self._ensure_directory_structure()
        
        logger.info(f"Local File Manager inicializado: {self.base_dir}")
    
    def _ensure_directory_structure(self):
        """Garante que a estrutura de diretórios existe"""
        
        subdirs = [
            'avatars', 'drivers_mentais', 'provas_visuais', 'anti_objecao',
            'pre_pitch', 'predicoes_futuro', 'posicionamento', 'concorrencia',
            'palavras_chave', 'metricas', 'funil_vendas', 'plano_acao',
            'insights', 'pesquisa_web', 'completas', 'metadata'
        ]
        
        # Cria diretório base
        os.makedirs(self.base_dir, exist_ok=True)
        
        # Cria subdiretórios
        for subdir in subdirs:
            os.makedirs(os.path.join(self.base_dir, subdir), exist_ok=True)
    
    def save_analysis_locally(self, analysis_data: Dict[str, Any]) -> Dict[str, Any]:
        """Salva análise completa em arquivos locais organizados"""
        
        try:
            # Gera ID único para a análise
            analysis_id = str(uuid.uuid4())
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            
            saved_files = []
            
            # Salva cada seção em arquivo separado
            sections_to_save = {
                'avatars': analysis_data.get('avatar_ultra_detalhado'),
                'drivers_mentais': analysis_data.get('drivers_mentais_customizados'),
                'provas_visuais': analysis_data.get('provas_visuais_sugeridas'),
                'anti_objecao': analysis_data.get('sistema_anti_objecao'),
                'pre_pitch': analysis_data.get('pre_pitch_invisivel'),
                'predicoes_futuro': analysis_data.get('predicoes_futuro_completas'),
                'posicionamento': analysis_data.get('escopo_posicionamento'),
                'concorrencia': analysis_data.get('analise_concorrencia_detalhada'),
                'palavras_chave': analysis_data.get('estrategia_palavras_chave'),
                'metricas': analysis_data.get('metricas_performance_detalhadas'),
                'funil_vendas': analysis_data.get('funil_vendas_detalhado'),
                'plano_acao': analysis_data.get('plano_acao_detalhado'),
                'insights': analysis_data.get('insights_exclusivos'),
                'pesquisa_web': analysis_data.get('pesquisa_web_massiva')
            }
            
            # Salva cada seção
            for section_name, section_data in sections_to_save.items():
                if section_data:
                    file_path = self._save_section_file(
                        section_name, section_data, analysis_id, timestamp
                    )
                    if file_path:
                        saved_files.append({
                            'type': section_name,
                            'name': os.path.basename(file_path),
                            'path': file_path,
                            'size': os.path.getsize(file_path)
                        })
            
            # Salva análise completa
            complete_file_path = self._save_complete_analysis(analysis_data, analysis_id, timestamp)
            if complete_file_path:
                saved_files.append({
                    'type': 'completas',
                    'name': os.path.basename(complete_file_path),
                    'path': complete_file_path,
                    'size': os.path.getsize(complete_file_path)
                })
            
            # Salva metadados
            metadata_file_path = self._save_metadata(analysis_data, analysis_id, timestamp, saved_files)
            if metadata_file_path:
                saved_files.append({
                    'type': 'metadata',
                    'name': os.path.basename(metadata_file_path),
                    'path': metadata_file_path,
                    'size': os.path.getsize(metadata_file_path)
                })
            
            logger.info(f"✅ Análise salva localmente: {len(saved_files)} arquivos")
            
            return {
                'success': True,
                'analysis_id': analysis_id,
                'base_directory': self.base_dir,
                'files': saved_files,
                'total_files': len(saved_files),
                'timestamp': timestamp
            }
            
        except Exception as e:
            logger.error(f"❌ Erro ao salvar análise localmente: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _save_section_file(
        self, 
        section_name: str, 
        section_data: Any, 
        analysis_id: str, 
        timestamp: str
    ) -> Optional[str]:
        """Salva arquivo de uma seção específica"""
        
        try:
            filename = f"{analysis_id[:8]}_{timestamp}_{section_name}.json"
            file_path = os.path.join(self.base_dir, section_name, filename)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(section_data, f, ensure_ascii=False, indent=2)
            
            return file_path
            
        except Exception as e:
            logger.error(f"❌ Erro ao salvar seção {section_name}: {str(e)}")
            return None
    
    def _save_complete_analysis(
        self, 
        analysis_data: Dict[str, Any], 
        analysis_id: str, 
        timestamp: str
    ) -> Optional[str]:
        """Salva análise completa"""
        
        try:
            filename = f"{analysis_id[:8]}_{timestamp}_completa.json"
            file_path = os.path.join(self.base_dir, 'completas', filename)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(analysis_data, f, ensure_ascii=False, indent=2)
            
            return file_path
            
        except Exception as e:
            logger.error(f"❌ Erro ao salvar análise completa: {str(e)}")
            return None
    
    def _save_metadata(
        self, 
        analysis_data: Dict[str, Any], 
        analysis_id: str, 
        timestamp: str,
        saved_files: List[Dict[str, Any]]
    ) -> Optional[str]:
        """Salva metadados da análise"""
        
        try:
            metadata = {
                'analysis_id': analysis_id,
                'timestamp': timestamp,
                'created_at': datetime.now().isoformat(),
                'project_data': {
                    'segmento': analysis_data.get('segmento'),
                    'produto': analysis_data.get('produto'),
                    'publico': analysis_data.get('publico'),
                    'preco': analysis_data.get('preco')
                },
                'files_saved': saved_files,
                'total_files': len(saved_files),
                'analysis_metadata': analysis_data.get('metadata', {}),
                'quality_score': analysis_data.get('metadata', {}).get('quality_score', 0),
                'processing_time': analysis_data.get('metadata', {}).get('processing_time_seconds', 0)
            }
            
            filename = f"{analysis_id[:8]}_{timestamp}_metadata.json"
            file_path = os.path.join(self.base_dir, 'metadata', filename)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, ensure_ascii=False, indent=2)
            
            return file_path
            
        except Exception as e:
            logger.error(f"❌ Erro ao salvar metadados: {str(e)}")
            return None
    
    def list_local_analyses(self) -> List[Dict[str, Any]]:
        """Lista análises salvas localmente"""
        
        try:
            analyses = []
            metadata_dir = os.path.join(self.base_dir, 'metadata')
            
            if not os.path.exists(metadata_dir):
                return []
            
            for filename in os.listdir(metadata_dir):
                if filename.endswith('_metadata.json'):
                    file_path = os.path.join(metadata_dir, filename)
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            metadata = json.load(f)
                        
                        analyses.append({
                            'analysis_id': metadata.get('analysis_id'),
                            'timestamp': metadata.get('timestamp'),
                            'created_at': metadata.get('created_at'),
                            'segmento': metadata.get('project_data', {}).get('segmento'),
                            'produto': metadata.get('project_data', {}).get('produto'),
                            'total_files': metadata.get('total_files', 0),
                            'quality_score': metadata.get('quality_score', 0),
                            'processing_time': metadata.get('processing_time', 0)
                        })
                        
                    except Exception as e:
                        logger.error(f"❌ Erro ao ler metadata {filename}: {str(e)}")
                        continue
            
            # Ordena por data de criação (mais recente primeiro)
            analyses.sort(key=lambda x: x.get('created_at', ''), reverse=True)
            
            return analyses
            
        except Exception as e:
            logger.error(f"❌ Erro ao listar análises locais: {str(e)}")
            return []
    
    def get_analysis_directory(self, analysis_id: str) -> Optional[str]:
        """Obtém diretório de uma análise específica"""
        
        # Busca por arquivos que contenham o ID da análise
        for root, dirs, files in os.walk(self.base_dir):
            for file in files:
                if analysis_id[:8] in file:
                    return root
        
        return None
    
    def delete_local_analysis(self, analysis_id: str) -> bool:
        """Remove análise local por ID"""
        
        try:
            deleted_files = 0
            
            # Busca e remove todos os arquivos relacionados
            for root, dirs, files in os.walk(self.base_dir):
                for file in files:
                    if analysis_id[:8] in file:
                        file_path = os.path.join(root, file)
                        try:
                            os.remove(file_path)
                            deleted_files += 1
                            logger.info(f"🗑️ Arquivo removido: {file}")
                        except Exception as e:
                            logger.error(f"❌ Erro ao remover {file}: {str(e)}")
            
            if deleted_files > 0:
                logger.info(f"✅ Análise {analysis_id} removida: {deleted_files} arquivos")
                return True
            else:
                logger.warning(f"⚠️ Nenhum arquivo encontrado para análise {analysis_id}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Erro ao deletar análise {analysis_id}: {str(e)}")
            return False
    
    def get_analysis_files(self, analysis_id: str) -> List[Dict[str, Any]]:
        """Obtém lista de arquivos de uma análise"""
        
        try:
            files = []
            
            for root, dirs, filenames in os.walk(self.base_dir):
                for filename in filenames:
                    if analysis_id[:8] in filename:
                        file_path = os.path.join(root, filename)
                        
                        # Determina tipo baseado no diretório
                        section_type = os.path.basename(root)
                        
                        files.append({
                            'name': filename,
                            'path': file_path,
                            'type': section_type,
                            'size': os.path.getsize(file_path),
                            'modified': datetime.fromtimestamp(
                                os.path.getmtime(file_path)
                            ).isoformat()
                        })
            
            return files
            
        except Exception as e:
            logger.error(f"❌ Erro ao obter arquivos da análise {analysis_id}: {str(e)}")
            return []
    
    def load_analysis_section(self, analysis_id: str, section_name: str) -> Optional[Dict[str, Any]]:
        """Carrega uma seção específica da análise"""
        
        try:
            section_dir = os.path.join(self.base_dir, section_name)
            
            if not os.path.exists(section_dir):
                return None
            
            # Busca arquivo da seção
            for filename in os.listdir(section_dir):
                if analysis_id[:8] in filename and filename.endswith('.json'):
                    file_path = os.path.join(section_dir, filename)
                    
                    with open(file_path, 'r', encoding='utf-8') as f:
                        return json.load(f)
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Erro ao carregar seção {section_name} da análise {analysis_id}: {str(e)}")
            return None
    
    def get_storage_stats(self) -> Dict[str, Any]:
        """Obtém estatísticas de armazenamento"""
        
        try:
            stats = {
                'base_directory': self.base_dir,
                'total_files': 0,
                'total_size_bytes': 0,
                'sections': {}
            }
            
            for root, dirs, files in os.walk(self.base_dir):
                section_name = os.path.basename(root)
                
                if section_name not in stats['sections']:
                    stats['sections'][section_name] = {
                        'files': 0,
                        'size_bytes': 0
                    }
                
                for file in files:
                    file_path = os.path.join(root, file)
                    try:
                        file_size = os.path.getsize(file_path)
                        stats['total_files'] += 1
                        stats['total_size_bytes'] += file_size
                        stats['sections'][section_name]['files'] += 1
                        stats['sections'][section_name]['size_bytes'] += file_size
                    except:
                        continue
            
            # Converte bytes para MB
            stats['total_size_mb'] = round(stats['total_size_bytes'] / (1024 * 1024), 2)
            
            for section in stats['sections'].values():
                section['size_mb'] = round(section['size_bytes'] / (1024 * 1024), 2)
            
            return stats
            
        except Exception as e:
            logger.error(f"❌ Erro ao obter estatísticas: {str(e)}")
            return {}

# Instância global
local_file_manager = LocalFileManager()