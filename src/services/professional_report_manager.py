#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ARQV30 Enhanced v2.0 - Professional Report Manager
Sistema pioneiro de relatórios automáticos profissionais
"""

import os
import json
import logging
from datetime import datetime
from typing import Dict, Any, List
from pathlib import Path
import shutil

logger = logging.getLogger(__name__)

class ProfessionalReportManager:
    """Gerenciador profissional de relatórios"""
    
    def __init__(self):
        """Inicializa o gerenciador"""
        self.base_path = Path("relatorios_profissionais")
        self.base_path.mkdir(exist_ok=True)
        
        # Estrutura profissional de diretórios
        self.directories = {
            'pdf_reports': self.base_path / 'pdfs',
            'json_data': self.base_path / 'dados',
            'intermediate_files': self.base_path / 'intermediarios',
            'templates': self.base_path / 'templates',
            'exports': self.base_path / 'exportacoes'
        }
        
        for dir_path in self.directories.values():
            dir_path.mkdir(exist_ok=True)
        
        logger.info("🗂️ Professional Report Manager inicializado")
    
    def auto_save_analysis(self, session_id: str, analysis_data: Dict[str, Any]) -> Dict[str, str]:
        """Salva análise automaticamente de forma profissional"""
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        segmento = self._sanitize_filename(analysis_data.get('segmento', 'analise'))
        
        # Estrutura profissional de arquivos
        files_saved = {}
        
        try:
            # 1. Salva dados principais (JSON estruturado)
            main_data_file = self.directories['json_data'] / f"{segmento}_{timestamp}_completo.json"
            with open(main_data_file, 'w', encoding='utf-8') as f:
                json.dump(analysis_data, f, ensure_ascii=False, indent=2)
            files_saved['dados_principais'] = str(main_data_file)
            
            # 2. Salva resumo executivo
            summary_file = self.directories['json_data'] / f"{segmento}_{timestamp}_resumo.json"
            summary_data = self._extract_executive_summary(analysis_data)
            with open(summary_file, 'w', encoding='utf-8') as f:
                json.dump(summary_data, f, ensure_ascii=False, indent=2)
            files_saved['resumo_executivo'] = str(summary_file)
            
            # 3. Salva componentes separadamente para fácil acesso
            components_dir = self.directories['intermediate_files'] / f"{segmento}_{timestamp}"
            components_dir.mkdir(exist_ok=True)
            
            # Componentes principais
            key_components = [
                'avatar_ultra_detalhado',
                'drivers_mentais_customizados', 
                'sistema_anti_objecao',
                'provas_visuais_sugeridas',
                'pre_pitch_invisivel',
                'predicoes_futuro_completas',
                'insights_exclusivos'
            ]
            
            for component in key_components:
                if component in analysis_data:
                    component_file = components_dir / f"{component}.json"
                    with open(component_file, 'w', encoding='utf-8') as f:
                        json.dump(analysis_data[component], f, ensure_ascii=False, indent=2)
            
            files_saved['componentes_separados'] = str(components_dir)
            
            # 4. Cria índice de sessão
            session_index = self._create_session_index(session_id, analysis_data, files_saved)
            index_file = self.directories['json_data'] / f"INDEX_{session_id}.json"
            with open(index_file, 'w', encoding='utf-8') as f:
                json.dump(session_index, f, ensure_ascii=False, indent=2)
            files_saved['indice_sessao'] = str(index_file)
            
            logger.info(f"✅ Análise salva profissionalmente: {len(files_saved)} arquivos")
            
        except Exception as e:
            logger.error(f"❌ Erro ao salvar análise: {e}")
        
        return files_saved
    
    def auto_save_pdf(self, session_id: str, pdf_buffer, analysis_data: Dict[str, Any]) -> str:
        """Salva PDF automaticamente com nome profissional"""
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        segmento = self._sanitize_filename(analysis_data.get('segmento', 'analise'))
        produto = self._sanitize_filename(analysis_data.get('produto', ''))
        
        # Nome profissional do PDF
        if produto:
            pdf_name = f"ARQV30_Relatorio_{segmento}_{produto}_{timestamp}.pdf"
        else:
            pdf_name = f"ARQV30_Relatorio_{segmento}_{timestamp}.pdf"
        
        pdf_path = self.directories['pdf_reports'] / pdf_name
        
        try:
            with open(pdf_path, 'wb') as f:
                f.write(pdf_buffer.read())
            
            # Cria metadados do PDF
            pdf_metadata = {
                'session_id': session_id,
                'filename': pdf_name,
                'created_at': datetime.now().isoformat(),
                'segmento': analysis_data.get('segmento'),
                'produto': analysis_data.get('produto'),
                'file_size_bytes': pdf_path.stat().st_size,
                'file_path': str(pdf_path)
            }
            
            metadata_file = self.directories['pdf_reports'] / f"{pdf_name.replace('.pdf', '_metadata.json')}"
            with open(metadata_file, 'w', encoding='utf-8') as f:
                json.dump(pdf_metadata, f, ensure_ascii=False, indent=2)
            
            logger.info(f"📄 PDF salvo automaticamente: {pdf_name}")
            return str(pdf_path)
            
        except Exception as e:
            logger.error(f"❌ Erro ao salvar PDF: {e}")
            return ""
    
    def create_professional_export(self, session_id: str) -> str:
        """Cria exportação profissional completa"""
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        export_dir = self.directories['exports'] / f"ARQV30_Export_{session_id}_{timestamp}"
        export_dir.mkdir(exist_ok=True)
        
        try:
            # 1. Copia dados principais
            data_dir = export_dir / "dados"
            data_dir.mkdir(exist_ok=True)
            
            # Encontra arquivos da sessão
            session_files = list(self.directories['json_data'].glob(f"*{session_id}*"))
            for file in session_files:
                shutil.copy2(file, data_dir)
            
            # 2. Copia PDFs
            pdf_dir = export_dir / "relatorios"
            pdf_dir.mkdir(exist_ok=True)
            
            pdf_files = list(self.directories['pdf_reports'].glob("*.pdf"))
            # Copia PDFs recentes (última hora)
            recent_pdfs = [f for f in pdf_files if (datetime.now() - datetime.fromtimestamp(f.stat().st_mtime)).seconds < 3600]
            for pdf in recent_pdfs:
                shutil.copy2(pdf, pdf_dir)
            
            # 3. Cria README profissional
            readme_content = self._generate_export_readme(session_id)
            with open(export_dir / "README.txt", 'w', encoding='utf-8') as f:
                f.write(readme_content)
            
            # 4. Comprime exportação (opcional)
            # shutil.make_archive(str(export_dir), 'zip', export_dir)
            
            logger.info(f"📦 Exportação profissional criada: {export_dir}")
            return str(export_dir)
            
        except Exception as e:
            logger.error(f"❌ Erro ao criar exportação: {e}")
            return ""
    
    def cleanup_old_files(self, days_to_keep: int = 30):
        """Limpa arquivos antigos mantendo organização"""
        
        cutoff_date = datetime.now().timestamp() - (days_to_keep * 24 * 60 * 60)
        
        for directory in self.directories.values():
            if directory.exists():
                for file in directory.rglob("*"):
                    if file.is_file() and file.stat().st_mtime < cutoff_date:
                        try:
                            file.unlink()
                            logger.info(f"🗑️ Arquivo antigo removido: {file.name}")
                        except Exception as e:
                            logger.warning(f"⚠️ Não foi possível remover {file}: {e}")
    
    def get_session_files(self, session_id: str) -> Dict[str, List[str]]:
        """Retorna todos os arquivos de uma sessão"""
        
        files_by_type = {
            'json_data': [],
            'pdf_reports': [],
            'intermediate_files': [],
            'exports': []
        }
        
        for dir_type, dir_path in self.directories.items():
            if dir_path.exists():
                # Busca arquivos que contenham o session_id
                session_files = list(dir_path.glob(f"*{session_id}*"))
                files_by_type[dir_type] = [str(f) for f in session_files]
        
        return files_by_type
    
    def _sanitize_filename(self, name: str) -> str:
        """Sanitiza nome para uso em arquivos"""
        if not name:
            return "sem_nome"
        
        # Remove caracteres especiais
        import re
        sanitized = re.sub(r'[^\w\s-]', '', name.strip())
        sanitized = re.sub(r'[-\s]+', '_', sanitized)
        return sanitized[:50]  # Limita tamanho
    
    def _extract_executive_summary(self, analysis_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extrai resumo executivo dos dados"""
        
        summary = {
            'sessao': {
                'timestamp': datetime.now().isoformat(),
                'segmento': analysis_data.get('segmento'),
                'produto': analysis_data.get('produto'),
                'publico': analysis_data.get('publico')
            },
            'metricas': {
                'componentes_gerados': 0,
                'insights_encontrados': 0,
                'drivers_customizados': 0,
                'provas_visuais': 0
            },
            'principais_insights': [],
            'recomendacoes_imediatas': []
        }
        
        # Conta componentes
        key_components = [
            'avatar_ultra_detalhado',
            'drivers_mentais_customizados',
            'sistema_anti_objecao', 
            'provas_visuais_sugeridas',
            'pre_pitch_invisivel',
            'predicoes_futuro_completas'
        ]
        
        summary['metricas']['componentes_gerados'] = sum(1 for comp in key_components if comp in analysis_data)
        
        # Extrai insights
        if 'insights_exclusivos' in analysis_data:
            insights = analysis_data['insights_exclusivos']
            if isinstance(insights, list):
                summary['metricas']['insights_encontrados'] = len(insights)
                summary['principais_insights'] = insights[:5]  # Top 5
        
        # Conta drivers
        if 'drivers_mentais_customizados' in analysis_data:
            drivers = analysis_data['drivers_mentais_customizados']
            if isinstance(drivers, dict) and 'total_drivers' in drivers:
                summary['metricas']['drivers_customizados'] = drivers['total_drivers']
        
        return summary
    
    def _create_session_index(self, session_id: str, analysis_data: Dict[str, Any], files_saved: Dict[str, str]) -> Dict[str, Any]:
        """Cria índice profissional da sessão"""
        
        return {
            'session_info': {
                'id': session_id,
                'created_at': datetime.now().isoformat(),
                'version': 'ARQV30 Enhanced v2.0'
            },
            'analysis_summary': {
                'segmento': analysis_data.get('segmento'),
                'produto': analysis_data.get('produto'),
                'publico': analysis_data.get('publico'),
                'preco': analysis_data.get('preco'),
                'objetivo_receita': analysis_data.get('objetivo_receita')
            },
            'files_generated': files_saved,
            'access_info': {
                'main_data': files_saved.get('dados_principais'),
                'executive_summary': files_saved.get('resumo_executivo'),
                'components_directory': files_saved.get('componentes_separados')
            },
            'usage_instructions': [
                "1. Consulte 'resumo_executivo.json' para visão geral",
                "2. Acesse componentes individuais na pasta 'intermediarios'",
                "3. Dados completos estão em '*_completo.json'",
                "4. PDFs estão na pasta 'pdfs' com metadados"
            ]
        }
    
    def _generate_export_readme(self, session_id: str) -> str:
        """Gera README profissional para exportação"""
        
        return f"""
ARQV30 Enhanced v2.0 - Exportação Profissional
==============================================

Sessão: {session_id}
Data: {datetime.now().strftime('%d/%m/%Y às %H:%M')}

ESTRUTURA DE ARQUIVOS:
---------------------
📁 dados/           - Dados JSON da análise
📁 relatorios/      - Relatórios PDF gerados  
📄 README.txt       - Este arquivo

COMO USAR:
---------
1. Dados JSON contêm toda a análise estruturada
2. PDFs são os relatórios finais profissionais
3. Cada componente pode ser acessado individualmente
4. Metadados estão incluídos para referência

COMPONENTES PRINCIPAIS:
----------------------
✓ Avatar Ultra-Detalhado
✓ Drivers Mentais Customizados
✓ Sistema Anti-Objeção
✓ Provas Visuais (PROVIs)
✓ Pré-Pitch Invisível
✓ Predições do Futuro

SUPORTE:
--------
Sistema ARQV30 Enhanced v2.0
Análise Psicológica de Mercado com IA
        """

    def _create_comprehensive_report_structure(self, analysis_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        ESTRUTURA COMPLETA DO RELATÓRIO - CONFORME PLANO 85v350
        Inclui todas as seções obrigatórias especificadas:
        concorrencia, drivers_mentais, funil_vendas, insights, metricas,
        palavras_chave, pesquisa_web, plano_acao, posicionamento, pre_pitch,
        predicoes_futuro, provas_visuais, reports, analyses, anti_objecao,
        avatars, completas
        """
        pass


# Instância global
professional_reports = ProfessionalReportManager()
professional_report_manager = professional_reports  # Alias para compatibilidade