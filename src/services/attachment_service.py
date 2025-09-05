#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ARQV30 Enhanced v2.0 - Serviço de Processamento de Anexos
Análise inteligente de documentos e arquivos
"""

import os
import logging
import mimetypes
import re
from typing import Dict, List, Optional, Any, Tuple
from werkzeug.datastructures import FileStorage
import PyPDF2
import pandas as pd
from docx import Document
import json
from datetime import datetime

logger = logging.getLogger(__name__)

class AttachmentService:
    """Serviço para processamento inteligente de anexos"""

    def __init__(self):
        """Inicializa serviço de anexos"""
        self.upload_folder = os.path.join(os.path.dirname(__file__), '..', 'uploads')
        os.makedirs(self.upload_folder, exist_ok=True)

        # Tipos de arquivo suportados
        self.supported_types = {
            'application/pdf': 'pdf',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document': 'docx',
            'application/msword': 'doc',
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': 'xlsx',
            'application/vnd.ms-excel': 'xls',
            'text/csv': 'csv',
            'text/plain': 'txt',
            'application/json': 'json'
        }

        # Classificadores de conteúdo
        self.content_classifiers = {
            'drivers_mentais': [
                'urgência', 'escassez', 'autoridade', 'prova social', 'reciprocidade',
                'compromisso', 'aversão à perda', 'ancoragem', 'gatilho', 'persuasão'
            ],
            'provas_visuais': [
                'depoimento', 'testemunho', 'case', 'resultado', 'antes e depois',
                'screenshot', 'gráfico', 'estatística', 'número', 'percentual'
            ],
            'perfis_psicologicos': [
                'persona', 'perfil', 'comportamento', 'personalidade', 'psicológico',
                'motivação', 'desejo', 'dor', 'necessidade', 'aspiração'
            ],
            'dados_pesquisa': [
                'pesquisa', 'survey', 'questionário', 'dados', 'estatística',
                'amostra', 'respondente', 'análise', 'insight', 'tendência'
            ]
        }

    def process_attachment(
        self, 
        file: FileStorage, 
        session_id: str
    ) -> Dict[str, Any]:
        """Processa anexo enviado pelo usuário"""

        try:
            logger.info(f"Processando anexo: {file.filename}")

            # Valida arquivo
            if not file or not file.filename:
                return {
                    'success': False,
                    'error': 'Arquivo inválido'
                }

            # Verifica tipo de arquivo
            mime_type = file.content_type or mimetypes.guess_type(file.filename)[0]
            if mime_type not in self.supported_types:
                return {
                    'success': False,
                    'error': f'Tipo de arquivo não suportado: {mime_type}'
                }

            # Salva arquivo temporariamente
            file_path = self._save_temp_file(file, session_id)
            if not file_path:
                return {
                    'success': False,
                    'error': 'Erro ao salvar arquivo'
                }

            # Extrai conteúdo
            content = self._extract_content(file_path, mime_type)
            if not content:
                return {
                    'success': False,
                    'error': 'Erro ao extrair conteúdo'
                }

            # Classifica conteúdo
            content_type = self._classify_content(content)

            # Processa conteúdo específico
            processed_content = self._process_specific_content(content, content_type)
            
            # Analisa item por item do anexo
            detailed_analysis = self._analyze_attachment_items(content, file.filename, mime_type)

            # Remove arquivo temporário
            self._cleanup_temp_file(file_path)

            return {
                'success': True,
                'message': 'Anexo processado com sucesso',
                'session_id': session_id,
                'filename': file.filename,
                'content_type': content_type,
                'content_preview': processed_content[:500] + '...' if len(processed_content) > 500 else processed_content,
                'full_content': processed_content,
                'detailed_analysis': detailed_analysis,
                'metadata': {
                    'file_size': len(content),
                    'mime_type': mime_type,
                    'processed_at': datetime.now().isoformat()
                }
            }

        except Exception as e:
            logger.error(f"Erro ao processar anexo: {str(e)}")
            return {
                'success': False,
                'error': f'Erro interno: {str(e)}'
            }

    def _save_temp_file(self, file: FileStorage, session_id: str) -> Optional[str]:
        """Salva arquivo temporariamente"""
        try:
            # Gera nome único
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"{session_id}_{timestamp}_{file.filename}"
            file_path = os.path.join(self.upload_folder, filename)

            # Salva arquivo
            file.save(file_path)

            return file_path

        except Exception as e:
            logger.error(f"Erro ao salvar arquivo: {str(e)}")
            return None

    def _extract_content(self, file_path: str, mime_type: str) -> Optional[str]:
        """Extrai conteúdo do arquivo baseado no tipo"""
        try:
            file_type = self.supported_types.get(mime_type)

            if file_type == 'pdf':
                return self._extract_pdf_content(file_path)
            elif file_type in ['docx', 'doc']:
                return self._extract_docx_content(file_path)
            elif file_type in ['xlsx', 'xls']:
                return self._extract_excel_content(file_path)
            elif file_type == 'csv':
                return self._extract_csv_content(file_path)
            elif file_type == 'txt':
                return self._extract_text_content(file_path)
            elif file_type == 'json':
                return self._extract_json_content(file_path)
            else:
                return None

        except Exception as e:
            logger.error(f"Erro ao extrair conteúdo: {str(e)}")
            return None

    def _extract_pdf_content(self, file_path: str) -> Optional[str]:
        """Extrai texto de arquivo PDF"""
        try:
            content = ""
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)

                for page_num in range(len(pdf_reader.pages)):
                    page = pdf_reader.pages[page_num]
                    content += page.extract_text() + "\n"

            return content.strip()

        except Exception as e:
            logger.error(f"Erro ao extrair PDF: {str(e)}")
            return None

    def _extract_docx_content(self, file_path: str) -> Optional[str]:
        """Extrai texto de arquivo DOCX"""
        try:
            doc = Document(file_path)
            content = ""

            for paragraph in doc.paragraphs:
                content += paragraph.text + "\n"

            return content.strip()

        except Exception as e:
            logger.error(f"Erro ao extrair DOCX: {str(e)}")
            return None

    def _extract_excel_content(self, file_path: str) -> Optional[str]:
        """Extrai dados de arquivo Excel"""
        try:
            import pandas as pd

            # Lê todas as planilhas
            excel_file = pd.ExcelFile(file_path)
            content = ""

            for sheet_name in excel_file.sheet_names:
                df = pd.read_excel(file_path, sheet_name=sheet_name)
                content += f"PLANILHA: {sheet_name}\n"
                content += df.to_string(index=False) + "\n\n"

            # Valida qualidade do conteúdo extraído
            if len(content.strip()) < 100:
                logger.warning(f"⚠️ Conteúdo Excel muito curto: {len(content)} caracteres")
                return None

            return content.strip()

        except Exception as e:
            logger.error(f"Erro ao extrair Excel: {str(e)}")
            return None

    def _validate_content_quality(self, content: str, filename: str) -> bool:
        """Valida qualidade do conteúdo extraído"""
        if not content or len(content.strip()) < 50:
            logger.error(f"❌ Conteúdo muito curto para {filename}: {len(content) if content else 0} caracteres")
            return False

        # Verifica se não é apenas espaços ou caracteres especiais
        clean_content = re.sub(r'[\s\n\r\t]+', ' ', content.strip())
        if len(clean_content) < 30:
            logger.error(f"❌ Conteúdo inválido para {filename}")
            return False

        # Verifica se há palavras reais (não apenas números/símbolos)
        word_count = len(re.findall(r'\b[a-zA-ZÀ-ÿ]{3,}\b', content))
        if word_count < 5:
            logger.error(f"❌ Muito poucas palavras válidas em {filename}: {word_count}")
            return False

        logger.info(f"✅ Conteúdo validado para {filename}: {len(content)} caracteres, {word_count} palavras")
        return True

    def _extract_csv_content(self, file_path: str) -> Optional[str]:
        """Extrai dados de arquivo CSV"""
        try:
            df = pd.read_csv(file_path, encoding='utf-8')
            return df.to_string(index=False)

        except UnicodeDecodeError:
            # Tenta com encoding latin-1
            try:
                df = pd.read_csv(file_path, encoding='latin-1')
                return df.to_string(index=False)
            except Exception as e:
                logger.error(f"Erro ao extrair CSV: {str(e)}")
                return None
        except Exception as e:
            logger.error(f"Erro ao extrair CSV: {str(e)}")
            return None

    def _extract_text_content(self, file_path: str) -> Optional[str]:
        """Extrai conteúdo de arquivo texto"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read()

        except UnicodeDecodeError:
            # Tenta com encoding latin-1
            try:
                with open(file_path, 'r', encoding='latin-1') as file:
                    return file.read()
            except Exception as e:
                logger.error(f"Erro ao extrair texto: {str(e)}")
                return None
        except Exception as e:
            logger.error(f"Erro ao extrair texto: {str(e)}")
            return None

    def _extract_json_content(self, file_path: str) -> Optional[str]:
        """Extrai conteúdo de arquivo JSON"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                data = json.load(file)
                return json.dumps(data, indent=2, ensure_ascii=False)

        except Exception as e:
            logger.error(f"Erro ao extrair JSON: {str(e)}")
            return None

    def _classify_content(self, content: str) -> str:
        """Classifica o tipo de conteúdo baseado em palavras-chave"""
        content_lower = content.lower()
        scores = {}

        # Calcula score para cada categoria
        for category, keywords in self.content_classifiers.items():
            score = 0
            for keyword in keywords:
                score += content_lower.count(keyword.lower())
            scores[category] = score

        # Retorna categoria com maior score
        if scores:
            best_category = max(scores, key=scores.get)
            if scores[best_category] > 0:
                return best_category

        return 'geral'

    def _process_specific_content(self, content: str, content_type: str) -> str:
        """Processa conteúdo específico baseado no tipo"""

        if content_type == 'drivers_mentais':
            return self._process_mental_drivers(content)
        elif content_type == 'provas_visuais':
            return self._process_visual_proofs(content)
        elif content_type == 'perfis_psicologicos':
            return self._process_psychological_profiles(content)
        elif content_type == 'dados_pesquisa':
            return self._process_research_data(content)
        else:
            return self._process_general_content(content)

    def _process_mental_drivers(self, content: str) -> str:
        """Processa conteúdo relacionado a gatilhos mentais"""
        processed = "DRIVERS MENTAIS IDENTIFICADOS:\n\n"

        drivers_found = []
        for driver in self.content_classifiers['drivers_mentais']:
            if driver.lower() in content.lower():
                drivers_found.append(driver)

        if drivers_found:
            processed += f"Gatilhos encontrados: {', '.join(drivers_found)}\n\n"

        processed += "CONTEÚDO ORIGINAL:\n"
        processed += content

        return processed

    def _process_visual_proofs(self, content: str) -> str:
        """Processa provas visuais e depoimentos"""
        processed = "PROVAS VISUAIS E DEPOIMENTOS:\n\n"

        # Identifica números e percentuais
        import re
        numbers = re.findall(r'\d+(?:\.\d+)?%?', content)
        if numbers:
            processed += f"Números identificados: {', '.join(numbers[:10])}\n\n"

        processed += "CONTEÚDO ORIGINAL:\n"
        processed += content

        return processed

    def _process_psychological_profiles(self, content: str) -> str:
        """Processa perfis psicológicos e personas"""
        processed = "PERFIS PSICOLÓGICOS IDENTIFICADOS:\n\n"

        # Busca por características de persona
        characteristics = []
        persona_keywords = ['idade', 'gênero', 'renda', 'comportamento', 'interesse']

        for keyword in persona_keywords:
            if keyword in content.lower():
                characteristics.append(keyword)

        if characteristics:
            processed += f"Características encontradas: {', '.join(characteristics)}\n\n"

        processed += "CONTEÚDO ORIGINAL:\n"
        processed += content

        return processed

    def _process_research_data(self, content: str) -> str:
        """Processa dados de pesquisa e estatísticas"""
        processed = "DADOS DE PESQUISA ANALISADOS:\n\n"

        # Identifica dados estatísticos
        import re
        stats = re.findall(r'\d+(?:\.\d+)?%', content)
        if stats:
            processed += f"Estatísticas encontradas: {', '.join(stats[:10])}\n\n"

        processed += "CONTEÚDO ORIGINAL:\n"
        processed += content

        return processed

    def _process_general_content(self, content: str) -> str:
        """Processamento geral de conteúdo"""
        processed = "CONTEÚDO GERAL PROCESSADO:\n\n"

        # Estatísticas básicas
        word_count = len(content.split())
        char_count = len(content)

        processed += f"Estatísticas: {word_count} palavras, {char_count} caracteres\n\n"
        processed += "CONTEÚDO ORIGINAL:\n"
        processed += content

        return processed
    
    def _analyze_attachment_items(self, content: str, filename: str, mime_type: str) -> Dict[str, Any]:
        """Analisa item por item do anexo"""
        
        analysis = {
            'filename': filename,
            'mime_type': mime_type,
            'total_length': len(content),
            'items_found': [],
            'categories': {},
            'insights': []
        }
        
        try:
            # Analisa por tipo de arquivo
            if mime_type == 'application/pdf':
                analysis.update(self._analyze_pdf_items(content))
            elif 'spreadsheet' in mime_type or 'excel' in mime_type:
                analysis.update(self._analyze_spreadsheet_items(content))
            elif 'document' in mime_type or 'word' in mime_type:
                analysis.update(self._analyze_document_items(content))
            elif mime_type == 'text/csv':
                analysis.update(self._analyze_csv_items(content))
            else:
                analysis.update(self._analyze_text_items(content))
            
            # Extrai insights específicos
            analysis['insights'] = self._extract_attachment_insights(content, analysis['items_found'])
            
        except Exception as e:
            logger.error(f"Erro ao analisar itens do anexo: {e}")
            analysis['error'] = str(e)
        
        return analysis
    
    def _analyze_pdf_items(self, content: str) -> Dict[str, Any]:
        """Analisa itens específicos de PDF"""
        
        items = []
        categories = {}
        
        # Divide por seções/páginas
        sections = content.split('\n\n')
        
        for i, section in enumerate(sections[:50], 1):  # Máximo 50 seções
            if len(section.strip()) > 50:
                item_type = self._classify_pdf_section(section)
                items.append({
                    'item_number': i,
                    'type': item_type,
                    'content': section.strip()[:300],
                    'length': len(section)
                })
                
                categories[item_type] = categories.get(item_type, 0) + 1
        
        return {
            'items_found': items,
            'categories': categories,
            'total_sections': len(sections)
        }
    
    def _analyze_spreadsheet_items(self, content: str) -> Dict[str, Any]:
        """Analisa itens específicos de planilha"""
        
        items = []
        categories = {}
        
        # Divide por linhas
        lines = content.split('\n')
        
        for i, line in enumerate(lines[:200], 1):  # Máximo 200 linhas
            if len(line.strip()) > 10:
                item_type = self._classify_spreadsheet_row(line)
                items.append({
                    'item_number': i,
                    'type': item_type,
                    'content': line.strip()[:200],
                    'columns': len(line.split('\t')) if '\t' in line else len(line.split(','))
                })
                
                categories[item_type] = categories.get(item_type, 0) + 1
        
        return {
            'items_found': items,
            'categories': categories,
            'total_rows': len(lines)
        }
    
    def _analyze_document_items(self, content: str) -> Dict[str, Any]:
        """Analisa itens específicos de documento"""
        
        items = []
        categories = {}
        
        # Divide por parágrafos
        paragraphs = [p.strip() for p in content.split('\n') if len(p.strip()) > 30]
        
        for i, paragraph in enumerate(paragraphs[:100], 1):  # Máximo 100 parágrafos
            item_type = self._classify_document_paragraph(paragraph)
            items.append({
                'item_number': i,
                'type': item_type,
                'content': paragraph[:250],
                'word_count': len(paragraph.split())
            })
            
            categories[item_type] = categories.get(item_type, 0) + 1
        
        return {
            'items_found': items,
            'categories': categories,
            'total_paragraphs': len(paragraphs)
        }
    
    def _analyze_csv_items(self, content: str) -> Dict[str, Any]:
        """Analisa itens específicos de CSV"""
        
        items = []
        categories = {}
        
        lines = content.split('\n')
        headers = lines[0].split(',') if lines else []
        
        for i, line in enumerate(lines[1:101], 1):  # Máximo 100 linhas de dados
            if line.strip():
                values = line.split(',')
                item_type = self._classify_csv_row(values, headers)
                items.append({
                    'item_number': i,
                    'type': item_type,
                    'values': values[:10],  # Primeiros 10 valores
                    'complete_row': len(values) == len(headers)
                })
                
                categories[item_type] = categories.get(item_type, 0) + 1
        
        return {
            'items_found': items,
            'categories': categories,
            'headers': headers,
            'total_data_rows': len(lines) - 1
        }
    
    def _analyze_text_items(self, content: str) -> Dict[str, Any]:
        """Analisa itens específicos de texto"""
        
        items = []
        categories = {}
        
        # Divide por sentenças
        sentences = [s.strip() for s in content.split('.') if len(s.strip()) > 20]
        
        for i, sentence in enumerate(sentences[:150], 1):  # Máximo 150 sentenças
            item_type = self._classify_text_sentence(sentence)
            items.append({
                'item_number': i,
                'type': item_type,
                'content': sentence[:200],
                'has_numbers': bool(re.search(r'\d+', sentence))
            })
            
            categories[item_type] = categories.get(item_type, 0) + 1
        
        return {
            'items_found': items,
            'categories': categories,
            'total_sentences': len(sentences)
        }
    
    def _classify_pdf_section(self, section: str) -> str:
        """Classifica seção de PDF"""
        section_lower = section.lower()
        
        if any(word in section_lower for word in ['título', 'capítulo', 'seção']):
            return 'titulo_secao'
        elif any(word in section_lower for word in ['tabela', 'dados', 'estatística']):
            return 'dados_tabulares'
        elif any(word in section_lower for word in ['gráfico', 'figura', 'imagem']):
            return 'elemento_visual'
        elif len(section) > 200:
            return 'paragrafo_conteudo'
        else:
            return 'texto_geral'
    
    def _classify_spreadsheet_row(self, row: str) -> str:
        """Classifica linha de planilha"""
        if re.search(r'\d+', row):
            return 'dados_numericos'
        elif any(word in row.lower() for word in ['total', 'soma', 'média']):
            return 'calculo_resumo'
        elif row.count(',') > 5 or row.count('\t') > 5:
            return 'linha_dados'
        else:
            return 'texto_descritivo'
    
    def _classify_document_paragraph(self, paragraph: str) -> str:
        """Classifica parágrafo de documento"""
        paragraph_lower = paragraph.lower()
        
        if paragraph.isupper() or paragraph.startswith('#'):
            return 'titulo_cabecalho'
        elif any(word in paragraph_lower for word in ['objetivo', 'meta', 'propósito']):
            return 'objetivo_meta'
        elif any(word in paragraph_lower for word in ['problema', 'desafio', 'dificuldade']):
            return 'problema_desafio'
        elif any(word in paragraph_lower for word in ['solução', 'resposta', 'estratégia']):
            return 'solucao_estrategia'
        elif re.search(r'\d+%|\d+\s*(mil|milhão|bilhão)', paragraph):
            return 'dados_estatisticos'
        else:
            return 'conteudo_geral'
    
    def _classify_csv_row(self, values: List[str], headers: List[str]) -> str:
        """Classifica linha de CSV"""
        if not values:
            return 'linha_vazia'
        
        numeric_count = sum(1 for v in values if re.search(r'^\d+(\.\d+)?$', v.strip()))
        
        if numeric_count > len(values) * 0.7:
            return 'dados_numericos'
        elif any('email' in h.lower() for h in headers):
            return 'dados_contato'
        elif any('nome' in h.lower() for h in headers):
            return 'dados_pessoais'
        else:
            return 'dados_gerais'
    
    def _classify_text_sentence(self, sentence: str) -> str:
        """Classifica sentença de texto"""
        sentence_lower = sentence.lower()
        
        if sentence.endswith('?'):
            return 'pergunta'
        elif any(word in sentence_lower for word in ['problema', 'dor', 'dificuldade']):
            return 'identificacao_problema'
        elif any(word in sentence_lower for word in ['desejo', 'quero', 'sonho']):
            return 'expressao_desejo'
        elif any(word in sentence_lower for word in ['solução', 'resolver', 'melhorar']):
            return 'busca_solucao'
        elif re.search(r'\d+', sentence):
            return 'informacao_quantitativa'
        else:
            return 'informacao_geral'
    
    def _extract_attachment_insights(self, content: str, items: List[Dict[str, Any]]) -> List[str]:
        """Extrai insights específicos do anexo"""
        
        insights = []
        
        # Insights baseados na categorização
        categories = {}
        for item in items:
            item_type = item.get('type', 'unknown')
            categories[item_type] = categories.get(item_type, 0) + 1
        
        # Gera insights baseados nas categorias
        for category, count in categories.items():
            if count > 5:
                insights.append(f"Anexo contém {count} itens do tipo '{category}' - alta concentração")
        
        # Insights baseados no conteúdo
        if re.search(r'\d+%', content):
            percentages = re.findall(r'\d+%', content)
            insights.append(f"Anexo contém {len(percentages)} percentuais/estatísticas")
        
        if re.search(r'R\$\s*[\d,\.]+', content):
            money_values = re.findall(r'R\$\s*[\d,\.]+', content)
            insights.append(f"Anexo contém {len(money_values)} valores monetários")
        
        # Insights sobre estrutura
        word_count = len(content.split())
        if word_count > 1000:
            insights.append(f"Anexo extenso com {word_count:,} palavras - conteúdo substancial")
        
        return insights[:10]  # Máximo 10 insights

    def _cleanup_temp_file(self, file_path: str) -> None:
        """Remove arquivo temporário"""
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
        except Exception as e:
            logger.error(f"Erro ao remover arquivo temporário: {str(e)}")

    def get_session_attachments(self, session_id: str) -> List[Dict[str, Any]]:
        """Retorna anexos de uma sessão específica"""
        # Esta função seria implementada com um sistema de cache/banco
        # Por enquanto retorna lista vazia
        return []

    def process_text_file(self, file_path: str) -> Optional[str]:
        """Processa arquivo de texto simples"""
        return self._extract_text_content(file_path)

    def clear_session_attachments(self, session_id: str) -> bool:
        """Remove anexos de uma sessão"""
        try:
            # Remove arquivos temporários da sessão
            for filename in os.listdir(self.upload_folder):
                if filename.startswith(session_id):
                    file_path = os.path.join(self.upload_folder, filename)
                    os.remove(file_path)

            return True

        except Exception as e:
            logger.error(f"Erro ao limpar anexos da sessão: {str(e)}")
            return False

# Instância global do serviço
attachment_service = AttachmentService()