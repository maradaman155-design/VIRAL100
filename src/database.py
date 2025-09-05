
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ARQV30 Enhanced v2.0 - Database Manager Local
Manager de banco de dados usando apenas arquivos locais
"""

import os
import json
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path

logger = logging.getLogger(__name__)

class LocalDatabaseManager:
    """Manager de banco de dados local usando apenas arquivos JSON"""
    
    def __init__(self):
        """Inicializa o manager local"""
        self.base_path = Path("analyses_data")
        self.base_path.mkdir(exist_ok=True)
        self.setup_directories()
        logger.info("✅ Local Database Manager inicializado")
    
    def setup_directories(self):
        """Cria diretórios necessários"""
        directories = [
            'analyses', 'users', 'progress', 'reports', 
            'files', 'metadata', 'logs'
        ]
        
        for directory in directories:
            (self.base_path / directory).mkdir(exist_ok=True)
    
    def test_connection(self) -> bool:
        """Testa se o sistema de arquivos está funcionando"""
        try:
            test_file = self.base_path / 'test.json'
            test_file.write_text('{"test": true}')
            test_file.unlink()
            return True
        except Exception as e:
            logger.error(f"Erro no teste de conexão: {e}")
            return False
    
    def save_analysis(self, analysis_id: str, data: Dict[str, Any]) -> bool:
        """Salva análise"""
        try:
            file_path = self.base_path / 'analyses' / f"{analysis_id}.json"
            
            # Adiciona metadata
            data['metadata'] = {
                'id': analysis_id,
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat()
            }
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"✅ Análise salva: {analysis_id}")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao salvar análise {analysis_id}: {e}")
            return False
    
    def get_analysis(self, analysis_id: str) -> Optional[Dict[str, Any]]:
        """Carrega análise"""
        try:
            file_path = self.base_path / 'analyses' / f"{analysis_id}.json"
            
            if not file_path.exists():
                return None
            
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
                
        except Exception as e:
            logger.error(f"Erro ao carregar análise {analysis_id}: {e}")
            return None
    
    def save_progress(self, session_id: str, progress_data: Dict[str, Any]) -> bool:
        """Salva progresso"""
        try:
            file_path = self.base_path / 'progress' / f"{session_id}.json"
            
            progress_data['updated_at'] = datetime.now().isoformat()
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(progress_data, f, ensure_ascii=False, indent=2)
            
            return True
            
        except Exception as e:
            logger.error(f"Erro ao salvar progresso {session_id}: {e}")
            return False
    
    def get_progress(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Carrega progresso"""
        try:
            file_path = self.base_path / 'progress' / f"{session_id}.json"
            
            if not file_path.exists():
                return None
            
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
                
        except Exception as e:
            logger.error(f"Erro ao carregar progresso {session_id}: {e}")
            return None
    
    def list_analyses(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Lista análises"""
        try:
            analyses_dir = self.base_path / 'analyses'
            analyses = []
            
            for file_path in analyses_dir.glob('*.json'):
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        analyses.append({
                            'id': file_path.stem,
                            'metadata': data.get('metadata', {}),
                            'summary': data.get('summary', 'Sem resumo')
                        })
                except Exception as e:
                    logger.warning(f"Erro ao ler {file_path}: {e}")
                    continue
            
            # Ordena por data de criação (mais recente primeiro)
            analyses.sort(
                key=lambda x: x.get('metadata', {}).get('created_at', ''),
                reverse=True
            )
            
            return analyses[:limit]
            
        except Exception as e:
            logger.error(f"Erro ao listar análises: {e}")
            return []
    
    def delete_analysis(self, analysis_id: str) -> bool:
        """Deleta análise"""
        try:
            file_path = self.base_path / 'analyses' / f"{analysis_id}.json"
            
            if file_path.exists():
                file_path.unlink()
                logger.info(f"✅ Análise deletada: {analysis_id}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Erro ao deletar análise {analysis_id}: {e}")
            return False

# Instância global
db_manager = LocalDatabaseManager()
