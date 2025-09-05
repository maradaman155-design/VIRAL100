#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ARQV30 Enhanced v2.0 - PyMuPDF Pro Client
Cliente para processamento avançado de PDFs com PyMuPDF Pro
"""

import os
import logging
import tempfile
import requests
from typing import Dict, List, Optional, Any, Union
from datetime import datetime

# Import condicional do PyMuPDF
try:
    import fitz  # PyMuPDF
    HAS_PYMUPDF = True
except ImportError:
    HAS_PYMUPDF = False

logger = logging.getLogger(__name__)

class PyMuPDFProClient:
    """Cliente para processamento avançado de PDFs"""
    
    def __init__(self):
        """Inicializa cliente PyMuPDF Pro"""
        self.pro_key = os.getenv("PYMUPDF_PRO_KEY", "jcUW5jc605Oa1LY1qU07ZDn6")
        self.available = HAS_PYMUPDF
        self.priority = 1  # Prioridade máxima para PDFs
        
        if self.available and self.pro_key:
            try:
                # Configura chave Pro se disponível
                if hasattr(fitz, 'set_license_key'):
                    fitz.set_license_key(self.pro_key)
                    logger.info("✅ PyMuPDF Pro configurado com chave de licença")
                else:
                    logger.info("✅ PyMuPDF disponível (versão padrão)")
            except Exception as e:
                logger.warning(f"⚠️ Erro ao configurar PyMuPDF Pro: {e}")
        
        if self.available:
            logger.info("✅ PyMuPDF client inicializado com PRIORIDADE MÁXIMA para PDFs")
        else:
            logger.warning("⚠️ PyMuPDF não instalado - execute: pip install PyMuPDF")
    
    def is_available(self) -> bool:
        """Verifica se está disponível"""
        return self.available
    
    def extract_text_advanced(
        self, 
        pdf_path: str,
        include_images: bool = False,
        include_tables: bool = True,
        include_annotations: bool = True
    ) -> Dict[str, Any]:
        """Extrai texto avançado de PDF"""
        
        if not self.available:
            return {'success': False, 'error': 'PyMuPDF não disponível'}
        
        try:
            doc = fitz.open(pdf_path)
            
            result = {
                'success': True,
                'text': '',
                'metadata': {
                    'pages': len(doc),
                    'title': doc.metadata.get('title', ''),
                    'author': doc.metadata.get('author', ''),
                    'subject': doc.metadata.get('subject', ''),
                    'creator': doc.metadata.get('creator', ''),
                    'producer': doc.metadata.get('producer', ''),
                    'creation_date': doc.metadata.get('creationDate', ''),
                    'modification_date': doc.metadata.get('modDate', '')
                },
                'pages_content': [],
                'tables': [],
                'images': [],
                'annotations': []
            }
            
            # Extrai texto de cada página
            for page_num in range(len(doc)):
                page = doc[page_num]
                
                # Texto da página
                page_text = page.get_text()
                result['text'] += page_text + '\n'
                
                page_data = {
                    'page_number': page_num + 1,
                    'text': page_text,
                    'word_count': len(page_text.split())
                }
                
                # Tabelas se solicitado
                if include_tables:
                    try:
                        tables = page.find_tables()
                        for table in tables:
                            table_data = table.extract()
                            result['tables'].append({
                                'page': page_num + 1,
                                'data': table_data,
                                'bbox': table.bbox
                            })
                    except Exception as e:
                        logger.warning(f"Erro ao extrair tabelas da página {page_num + 1}: {e}")
                
                # Imagens se solicitado
                if include_images:
                    try:
                        image_list = page.get_images()
                        for img_index, img in enumerate(image_list):
                            result['images'].append({
                                'page': page_num + 1,
                                'index': img_index,
                                'xref': img[0],
                                'bbox': page.get_image_bbox(img)
                            })
                    except Exception as e:
                        logger.warning(f"Erro ao extrair imagens da página {page_num + 1}: {e}")
                
                # Anotações se solicitado
                if include_annotations:
                    try:
                        annotations = page.annots()
                        for annot in annotations:
                            result['annotations'].append({
                                'page': page_num + 1,
                                'type': annot.type[1],
                                'content': annot.content,
                                'bbox': annot.rect
                            })
                    except Exception as e:
                        logger.warning(f"Erro ao extrair anotações da página {page_num + 1}: {e}")
                
                result['pages_content'].append(page_data)
            
            doc.close()
            
            # Estatísticas finais
            result['statistics'] = {
                'total_characters': len(result['text']),
                'total_words': len(result['text'].split()),
                'total_tables': len(result['tables']),
                'total_images': len(result['images']),
                'total_annotations': len(result['annotations']),
                'extraction_method': 'PyMuPDF_Pro' if self.pro_key else 'PyMuPDF'
            }
            
            logger.info(f"✅ PDF extraído: {result['statistics']['total_characters']} chars, {result['statistics']['total_words']} palavras")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Erro ao extrair PDF: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def extract_from_url(self, url: str, **kwargs) -> Dict[str, Any]:
        """Extrai PDF diretamente de URL"""
        
        if not self.available:
            return {'success': False, 'error': 'PyMuPDF não disponível'}
        
        try:
            # Baixa PDF temporariamente
            response = requests.get(url, timeout=60)
            response.raise_for_status()
            
            with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as temp_file:
                temp_file.write(response.content)
                temp_path = temp_file.name
            
            try:
                # Extrai usando arquivo temporário
                result = self.extract_text_advanced(temp_path, **kwargs)
                result['source_url'] = url
                return result
            finally:
                # Remove arquivo temporário
                try:
                    os.unlink(temp_path)
                except:
                    pass
                    
        except Exception as e:
            logger.error(f"❌ Erro ao extrair PDF de URL {url}: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def convert_to_text(self, pdf_path: str) -> str:
        """Converte PDF para texto simples"""
        
        result = self.extract_text_advanced(pdf_path)
        
        if result['success']:
            return result['text']
        else:
            return ""
    
    def get_pdf_info(self, pdf_path: str) -> Dict[str, Any]:
        """Obtém informações detalhadas do PDF"""
        
        if not self.available:
            return {'success': False, 'error': 'PyMuPDF não disponível'}
        
        try:
            doc = fitz.open(pdf_path)
            
            info = {
                'success': True,
                'metadata': doc.metadata,
                'page_count': len(doc),
                'is_encrypted': doc.is_encrypted,
                'is_pdf': doc.is_pdf,
                'page_sizes': []
            }
            
            # Informações de cada página
            for page_num in range(len(doc)):
                page = doc[page_num]
                rect = page.rect
                info['page_sizes'].append({
                    'page': page_num + 1,
                    'width': rect.width,
                    'height': rect.height,
                    'rotation': page.rotation
                })
            
            doc.close()
            return info
            
        except Exception as e:
            logger.error(f"❌ Erro ao obter info do PDF: {str(e)}")
            return {'success': False, 'error': str(e)}

# Instância global
pymupdf_client = PyMuPDFProClient()