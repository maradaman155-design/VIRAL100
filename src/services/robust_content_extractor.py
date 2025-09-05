#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ARQV30 Enhanced v2.0 - Robust Content Extractor
Extrator multicamadas aprimorado com suporte a PDF e fallback robusto
"""

import time
import random
import os
import logging
import requests
import json
from typing import Dict, List, Optional, Any, Tuple
from urllib.parse import urljoin, urlparse
import re
import tempfile
from concurrent.futures import ThreadPoolExecutor, as_completed
from services.auto_save_manager import salvar_etapa, salvar_erro

# Imports condicionais para não quebrar se não estiver instalado
try:
    import trafilatura
    HAS_TRAFILATURA = True
except ImportError:
    HAS_TRAFILATURA = False

try:
    from readability import Document
    HAS_READABILITY = True
except ImportError:
    HAS_READABILITY = False

try:
    import newspaper
    from newspaper import Article
    HAS_NEWSPAPER = True
except ImportError:
    HAS_NEWSPAPER = False

try:
    from bs4 import BeautifulSoup
    HAS_BEAUTIFULSOUP = True
except ImportError:
    HAS_BEAUTIFULSOUP = False

try:
    import PyPDF2
    HAS_PYPDF2 = True
except ImportError:
    HAS_PYPDF2 = False

try:
    import pdfplumber
    HAS_PDFPLUMBER = True
except ImportError:
    HAS_PDFPLUMBER = False

try:
    import fitz  # PyMuPDF
    HAS_PYMUPDF = True
except ImportError:
    HAS_PYMUPDF = False

from services.url_resolver import url_resolver

logger = logging.getLogger(__name__)

class RobustContentExtractor:
    """Extrator de conteúdo multicamadas e robusto com suporte aprimorado a PDF"""

    def __init__(self):
        """Inicializa o extrator robusto"""
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'pt-BR,pt;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        })

        self.timeout = 30
        self.min_content_length = 200  # Reduzido de 500 para 200
        self.max_content_length = 50000  # 50K chars max

        # Estatísticas dos extratores
        self.stats = {
            'trafilatura': {'success': 0, 'failed': 0, 'total_time': 0, 'usage_count': 0, 'available': HAS_TRAFILATURA},
            'readability': {'success': 0, 'failed': 0, 'total_time': 0, 'usage_count': 0, 'available': HAS_READABILITY},
            'newspaper': {'success': 0, 'failed': 0, 'total_time': 0, 'usage_count': 0, 'available': HAS_NEWSPAPER},
            'beautifulsoup': {'success': 0, 'failed': 0, 'total_time': 0, 'usage_count': 0, 'available': HAS_BEAUTIFULSOUP},
            'pdf_pypdf2': {'success': 0, 'failed': 0, 'total_time': 0, 'usage_count': 0, 'available': HAS_PYPDF2},
            'pdf_pdfplumber': {'success': 0, 'failed': 0, 'total_time': 0, 'usage_count': 0, 'available': HAS_PDFPLUMBER},
            'pdf_pymupdf': {'success': 0, 'failed': 0, 'total_time': 0, 'usage_count': 0, 'available': HAS_PYMUPDF},
            'global': {
                'total_extractions': 0,
                'total_successes': 0,
                'total_failures': 0,
                'success_rate': 0.0
            }
        }

        logger.info("🔧 Robust Content Extractor inicializado")
        logger.info(f"📚 Extratores disponíveis: {self._get_available_extractors()}")

    def extract_content(self, url: str) -> Optional[str]:
        """
        Extrai conteúdo usando múltiplos extratores em ordem de prioridade
        Agora com suporte aprimorado a PDF e melhor fallback
        """
        if not url or not url.startswith('http'):
            logger.error(f"❌ URL inválida: {url}")
            return None

        try:
            start_time = time.time()
            self.stats['global']['total_extractions'] += 1

            logger.info(f"🔍 Iniciando extração de: {url}")

            # 1. Resolve URL de redirecionamento
            resolved_url = url_resolver.resolve_redirect_url(url)
            if resolved_url != url:
                logger.info(f"🔄 URL resolvida: {url} -> {resolved_url}")
                # Salva resolução de URL
                salvar_etapa("url_resolvida", {
                    "original": url,
                    "resolved": resolved_url
                }, categoria="pesquisa_web")
                url = resolved_url

            # Valida URL resolvida
            if not url.startswith('http'):
                logger.error(f"❌ URL resolvida inválida: {url}")
                salvar_erro("url_invalida", ValueError(f"URL inválida: {url}"))
                self.stats['global']['total_failures'] += 1
                self._update_global_stats()
                return None

            # 2. Verifica se é PDF
            if self._is_pdf_url(url):
                logger.info("📄 Detectado PDF - usando extratores especializados")
                # PRIORIDADE MÁXIMA: PyMuPDF primeiro
                from services.pymupdf_client import pymupdf_client
                if pymupdf_client.is_available():
                    logger.info("🚀 Usando PyMuPDF Pro com PRIORIDADE MÁXIMA")
                    pdf_result = pymupdf_client.extract_from_url(url)
                    if pdf_result.get('success') and pdf_result.get('text'):
                        content = pdf_result['text']
                        if self._validate_content(content, url):
                            salvar_etapa("extracao_pymupdf_pro", {
                                "url": url,
                                "content_length": len(content),
                                "pages": pdf_result.get('metadata', {}).get('pages', 0),
                                "extractor": "PyMuPDF_Pro_Priority"
                            }, categoria="pesquisa_web")
                            self.stats['global']['total_successes'] += 1
                            self._update_global_stats()
                            logger.info(f"✅ PyMuPDF Pro SUCESSO: {len(content)} caracteres")
                            return content

                # Fallback para outros extratores de PDF
                content = self._extract_pdf_content(url) # Utiliza a nova função para extração de PDF
                if content and self._validate_content(content, url):
                    # Salva extração de PDF bem-sucedida
                    salvar_etapa("extracao_pdf", {
                        "url": url,
                        "content_length": len(content),
                        "extractor": "pdf_specialized"
                    }, categoria="pesquisa_web")
                    self.stats['global']['total_successes'] += 1
                    self._update_global_stats()
                    return content

            # 3. Baixa conteúdo HTML
            html_content = self._fetch_html(url)
            if not html_content:
                logger.error(f"❌ Falha ao baixar HTML para {url}")
                salvar_erro("download_html", Exception(f"Falha no download: {url}"))
                self.stats['global']['total_failures'] += 1
                self._update_global_stats()
                return None

            # Valida HTML mínimo
            if len(html_content) < 500:
                logger.warning(f"⚠️ HTML muito pequeno: {len(html_content)} caracteres")
                # Continua tentando extrair, mas com expectativas baixas

            logger.info(f"📥 HTML baixado: {len(html_content)} caracteres")

            # 4. Verifica se é página dinâmica (JavaScript-heavy)
            if self._is_dynamic_page(html_content):
                logger.warning(f"⚠️ Página dinâmica detectada: {url}")
                # Tenta extração mais agressiva
                content = self._extract_dynamic_content(html_content, url)
                if content and self._validate_content(content, url):
                    # Salva extração dinâmica bem-sucedida
                    salvar_etapa("extracao_dinamica", {
                        "url": url,
                        "content_length": len(content),
                        "extractor": "dynamic_specialized"
                    }, categoria="pesquisa_web")
                    self.stats['global']['total_successes'] += 1
                    self._update_global_stats()
                    return content

            # 5. Tenta extratores em ordem de prioridade
            extractors = [
                ('trafilatura', self._extract_with_trafilatura),
                ('readability', self._extract_with_readability),
                ('newspaper', self._extract_with_newspaper),
                ('beautifulsoup', self._extract_with_beautifulsoup)
            ]

            for extractor_name, extractor_func in extractors:
                if not self._is_extractor_available(extractor_name):
                    continue

                try:
                    logger.info(f"🔍 Tentando extração com {extractor_name}...")
                    extractor_start = time.time()
                    self.stats[extractor_name]['usage_count'] += 1

                    content = extractor_func(html_content, url)
                    extractor_time = time.time() - extractor_start

                    if self._validate_content(content, url):
                        self.stats[extractor_name]['success'] += 1
                        self.stats[extractor_name]['total_time'] += extractor_time
                        self.stats['global']['total_successes'] += 1
                        self._update_global_stats()

                        # Salva extração bem-sucedida
                        salvar_etapa("extracao_sucesso", {
                            "url": url,
                            "extractor": extractor_name,
                            "content_length": len(content),
                            "extraction_time": extractor_time
                        }, categoria="pesquisa_web")

                        logger.info(f"✅ Extração bem-sucedida com {extractor_name}: {len(content)} caracteres em {extractor_time:.2f}s")
                        return content
                    else:
                        self.stats[extractor_name]['failed'] += 1
                        logger.warning(f"⚠️ Conteúdo insuficiente com {extractor_name}: {len(content) if content else 0} caracteres")

                except Exception as e:
                    self.stats[extractor_name]['failed'] += 1
                    logger.error(f"❌ Erro com {extractor_name}: {str(e)}")
                    salvar_erro(f"extrator_{extractor_name}", e, contexto={"url": url})
                    continue

            # 6. Fallback final - extração agressiva
            logger.warning(f"⚠️ Todos os extratores padrão falharam, tentando extração agressiva...")
            content = self._aggressive_fallback_extraction(html_content, url)
            if content and len(content) >= 100:  # Critério mais flexível para fallback
                logger.info(f"✅ Extração agressiva bem-sucedida: {len(content)} caracteres")
                # Salva fallback bem-sucedido
                salvar_etapa("extracao_fallback", {
                    "url": url,
                    "content_length": len(content),
                    "extractor": "aggressive_fallback"
                }, categoria="pesquisa_web")
                self.stats['global']['total_successes'] += 1
                self._update_global_stats()
                return content

            # Todos os extratores falharam
            logger.error(f"❌ FALHA CRÍTICA: Todos os extratores falharam para {url}")
            salvar_erro("extracao_total_falha", Exception(f"Todos extratores falharam: {url}"))
            self.stats['global']['total_failures'] += 1
            self._update_global_stats()
            return None

        except Exception as e:
            logger.error(f"❌ Erro crítico na extração de {url}: {str(e)}")
            salvar_erro("extracao_critica", e, contexto={"url": url})
            self.stats['global']['total_failures'] += 1
            self._update_global_stats()
            return None

    def _is_pdf_url(self, url: str) -> bool:
        """Verifica se a URL aponta para um PDF"""
        return (url.lower().endswith('.pdf') or 
                'pdf' in url.lower() or 
                'application/pdf' in url.lower())

    def _extract_pdf_content(self, url: str) -> Optional[str]:
        """Extrai conteúdo de PDF usando múltiplas estratégias"""

        try:
            # Baixa o PDF
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()

            # Salva temporariamente
            with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as temp_file:
                temp_file.write(response.content)
                temp_path = temp_file.name

            try:
                # Tenta PDFPlumber primeiro (melhor para PDFs complexos)
                if HAS_PDFPLUMBER:
                    content = self._extract_pdf_with_pdfplumber(temp_path)
                    if content and len(content) > 100:
                        self.stats['pdf_pdfplumber']['success'] += 1
                        logger.info(f"✅ PDF extraído com PDFPlumber: {len(content)} caracteres")
                        return content
                    else:
                        self.stats['pdf_pdfplumber']['failed'] += 1

                # Tenta PyMuPDF se disponível
                if HAS_PYMUPDF:
                    content = self._extract_pdf_with_pymupdf(temp_path)
                    if content and len(content) > 100:
                        self.stats['pdf_pymupdf']['success'] += 1
                        logger.info(f"✅ PDF extraído com PyMuPDF: {len(content)} caracteres")
                        return content
                    else:
                        self.stats['pdf_pymupdf']['failed'] += 1

                # Fallback para PyPDF2
                if HAS_PYPDF2:
                    content = self._extract_pdf_with_pypdf2(temp_path)
                    if content and len(content) > 100:
                        self.stats['pdf_pypdf2']['success'] += 1
                        logger.info(f"✅ PDF extraído com PyPDF2: {len(content)} caracteres")
                        return content
                    else:
                        self.stats['pdf_pypdf2']['failed'] += 1

                logger.error(f"❌ Falha na extração de PDF: {url}")
                return None

            finally:
                # Remove arquivo temporário
                try:
                    os.unlink(temp_path)
                except:
                    pass

        except Exception as e:
            logger.error(f"❌ Erro ao processar PDF {url}: {str(e)}")
            return None

    def _extract_pdf_with_pdfplumber(self, pdf_path: str) -> Optional[str]:
        """Extrai texto usando PDFPlumber"""
        try:
            import pdfplumber

            text = ""
            with pdfplumber.open(pdf_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"

            return self._clean_content(text) if text else None

        except Exception as e:
            logger.error(f"Erro PDFPlumber: {e}")
            return None

    def _extract_pdf_with_pypdf2(self, pdf_path: str) -> Optional[str]:
        """Extrai texto usando PyPDF2"""
        try:
            import PyPDF2

            text = ""
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page in pdf_reader.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"

            return self._clean_content(text) if text else None

        except Exception as e:
            logger.error(f"Erro PyPDF2: {e}")
            return None

    def _extract_pdf_with_pymupdf(self, pdf_path: str) -> Optional[str]:
        """Extrai texto usando PyMuPDF"""
        try:
            import fitz

            doc = fitz.open(pdf_path)
            text = ""

            for page_num in range(len(doc)):
                page = doc[page_num]
                page_text = page.get_text()
                if page_text:
                    text += page_text + "\n"

            doc.close()
            return self._clean_content(text) if text else None

        except Exception as e:
            logger.error(f"Erro PyMuPDF: {e}")
            return None
            
    def extract_pdf_content(self, file_path: str) -> str:
        """Extrai conteúdo de PDF com PyMuPDF como principal"""
        try:
            # 1. PYMUPDF COMO PRINCIPAL
            if HAS_PYMUPDF:
                try:
                    import fitz  # PyMuPDF
                    doc = fitz.open(file_path)
                    content = ""
                    for page_num in range(doc.page_count):
                        page = doc[page_num]
                        content += page.get_text()
                    doc.close()

                    if len(content.strip()) > 100:
                        logger.info(f"✅ PyMuPDF extraiu {len(content)} caracteres")
                        return content
                except Exception as e:
                    logger.warning(f"⚠️ PyMuPDF falhou: {e}")

            # 2. FALLBACK: PyPDF2
            if HAS_PYPDF2:
                try:
                    import PyPDF2
                    with open(file_path, 'rb') as file:
                        reader = PyPDF2.PdfReader(file)
                        content = ""
                        for page in reader.pages:
                            content += page.extract_text()

                    if len(content.strip()) > 100:
                        logger.info(f"✅ PyPDF2 extraiu {len(content)} caracteres")
                        return content
                except Exception as e:
                    logger.warning(f"⚠️ PyPDF2 falhou: {e}")

            # 3. FALLBACK: pdfplumber
            if HAS_PDFPLUMBER:
                try:
                    import pdfplumber
                    content = ""
                    with pdfplumber.open(file_path) as pdf:
                        for page in pdf.pages:
                            page_text = page.extract_text()
                            if page_text:
                                content += page_text

                    if len(content.strip()) > 100:
                        logger.info(f"✅ pdfplumber extraiu {len(content)} caracteres")
                        return content
                except Exception as e:
                    logger.warning(f"⚠️ pdfplumber falhou: {e}")

            logger.error("❌ Todos os extratores de PDF falharam")
            return ""

        except Exception as e:
            logger.error(f"❌ Erro crítico na extração de PDF: {e}")
            return ""

    def _is_dynamic_page(self, html: str) -> bool:
        """Verifica se é página dinâmica (JavaScript-heavy)"""
        if not html:
            return False

        # Indicadores de página dinâmica
        dynamic_indicators = [
            'react', 'angular', 'vue.js', 'spa-',
            'document.write', 'innerHTML', 'createElement',
            'loading...', 'carregando...', 'please enable javascript',
            'javascript required', 'js-', 'ng-', 'v-'
        ]

        html_lower = html.lower()
        js_indicators = sum(1 for indicator in dynamic_indicators if indicator in html_lower)

        # Se tem muitos indicadores JS e pouco conteúdo de texto
        text_content = BeautifulSoup(html, 'html.parser').get_text() if HAS_BEAUTIFULSOUP else html
        text_ratio = len(text_content.strip()) / len(html) if html else 0

        return js_indicators > 3 and text_ratio < 0.1

    def _extract_dynamic_content(self, html: str, url: str) -> Optional[str]:
        """Extração especializada para conteúdo dinâmico"""

        if not HAS_BEAUTIFULSOUP:
            return None

        try:
            soup = BeautifulSoup(html, 'html.parser')

            # Remove scripts e elementos dinâmicos
            for element in soup(['script', 'style', 'noscript', 'iframe']):
                element.decompose()

            # Busca por elementos com conteúdo pré-renderizado
            content_selectors = [
                '[data-content]', '[data-text]', '.content-loaded',
                '.server-rendered', '.static-content', '.preloaded',
                'main', 'article', '.post-content', '.article-content',
                '.entry-content', '.page-content', '.text-content'
            ]

            extracted_content = []

            for selector in content_selectors:
                try:
                    elements = soup.select(selector)
                    for element in elements:
                        text = element.get_text(strip=True)
                        if len(text) > 50:  # Conteúdo substancial
                            extracted_content.append(text)
                except:
                    continue

            if extracted_content:
                combined = '\n\n'.join(extracted_content)
                return self._clean_content(combined)

            # Fallback: extrai todo texto disponível
            all_text = soup.get_text()
            return self._clean_content(all_text) if len(all_text) > 100 else None

        except Exception as e:
            logger.error(f"Erro na extração dinâmica: {e}")
            return None

    def _aggressive_fallback_extraction(self, html: str, url: str) -> Optional[str]:
        """Extração agressiva como último recurso"""

        if not HAS_BEAUTIFULSOUP:
            return None

        try:
            soup = BeautifulSoup(html, 'html.parser')

            # Remove apenas elementos críticos
            for element in soup(['script', 'style']):
                element.decompose()

            # Coleta todo texto disponível
            all_text = soup.get_text()

            # Filtra linhas com conteúdo significativo
            lines = all_text.split('\n')
            meaningful_lines = []

            for line in lines:
                line = line.strip()
                if (len(line) > 20 and  # Linha substancial
                    not re.match(r'^[\s\W]*$', line) and  # Não só espaços/símbolos
                    not line.lower().startswith(('menu', 'nav', 'footer', 'header'))):  # Não navegação
                    meaningful_lines.append(line)

            if meaningful_lines:
                content = '\n'.join(meaningful_lines)
                return self._clean_content(content)

            return None

        except Exception as e:
            logger.error(f"Erro na extração agressiva: {e}")
            return None

    def _fetch_html(self, url: str) -> Optional[str]:
        """Baixa conteúdo HTML da URL com retry"""
        max_retries = 3

        for attempt in range(max_retries):
            try:
                response = self.session.get(
                    url,
                    timeout=self.timeout,
                    verify=False,  # Para evitar problemas de SSL
                    allow_redirects=True
                )

                response.raise_for_status()

                # Detecta encoding
                if response.encoding is None:
                    response.encoding = 'utf-8'

                html = response.text

                if len(html) < 500:
                    logger.warning(f"⚠️ HTML muito pequeno (tentativa {attempt + 1}): {len(html)} caracteres")
                    if attempt < max_retries - 1:
                        time.sleep(2)  # Aguarda antes de tentar novamente
                        continue

                return html

            except requests.exceptions.Timeout:
                logger.warning(f"⏰ Timeout na tentativa {attempt + 1} para {url}")
                if attempt < max_retries - 1:
                    time.sleep(2 + random.uniform(0, 2))  # Delay aleatório
                    continue
            except Exception as e:
                logger.error(f"❌ Erro ao baixar {url} (tentativa {attempt + 1}): {str(e)}")
                if attempt < max_retries - 1:
                    time.sleep(2 + random.uniform(0, 2))  # Delay aleatório
                    continue

        return None

    def _extract_with_trafilatura(self, html: str, url: str) -> Optional[str]:
        """Extrai com Trafilatura (prioridade 1) com configurações aprimoradas"""
        if not HAS_TRAFILATURA:
            return None

        try:
            # Configurações mais agressivas para trafilatura
            content = trafilatura.extract(
                html,
                include_comments=False,
                include_tables=True,
                include_formatting=False,
                favor_precision=False,  # Mudado para False para ser mais inclusivo
                favor_recall=True,      # Prioriza recuperar mais conteúdo
                url=url,
                config=trafilatura.settings.use_config()
            )

            if content:
                content = self._clean_content(content)
                return content

            return None

        except Exception as e:
            logger.error(f"Erro Trafilatura: {e}")
            return None

    def _extract_with_readability(self, html: str, url: str) -> Optional[str]:
        """Extrai com Readability (prioridade 2) com configurações aprimoradas"""
        if not HAS_READABILITY:
            return None

        try:
            # Configurações mais inclusivas
            doc = Document(html, positive_keywords=['content', 'article', 'post', 'text', 'main'])
            content = doc.summary()

            if content:
                # Remove tags HTML
                if HAS_BEAUTIFULSOUP:
                    soup = BeautifulSoup(content, 'html.parser')
                    content = soup.get_text()
                else:
                    # Remove tags manualmente
                    content = re.sub(r'<[^>]+>', '', content)

                content = self._clean_content(content)
                return content

            return None

        except Exception as e:
            logger.error(f"Erro Readability: {e}")
            return None

    def _extract_with_newspaper(self, html: str, url: str) -> Optional[str]:
        """Extrai com Newspaper3k (prioridade 3) com configurações aprimoradas"""
        if not HAS_NEWSPAPER:
            return None

        try:
            article = Article(url)
            article.set_html(html)
            article.parse()

            content = article.text
            if content:
                content = self._clean_content(content)
                return content

            return None

        except Exception as e:
            logger.error(f"Erro Newspaper: {e}")
            return None

    def _extract_with_beautifulsoup(self, html: str, url: str) -> Optional[str]:
        """Extrai com BeautifulSoup (fallback final) com estratégia aprimorada"""
        if not HAS_BEAUTIFULSOUP:
            return None

        try:
            soup = BeautifulSoup(html, 'html.parser')

            # Remove scripts e styles
            for script in soup(['script', 'style', 'nav', 'header', 'footer', 'aside', 'form']):
                script.decompose()

            # Estratégia em camadas para encontrar conteúdo
            content_strategies = [
                # Estratégia 1: Elementos semânticos
                lambda: self._extract_semantic_content(soup),
                # Estratégia 2: Elementos por classe/ID
                lambda: self._extract_by_selectors(soup),
                # Estratégia 3: Maior bloco de texto
                lambda: self._extract_largest_text_block(soup),
                # Estratégia 4: Todo o body
                lambda: self._extract_full_body(soup)
            ]

            for strategy in content_strategies:
                try:
                    content = strategy()
                    if content and len(content) > 100:
                        return self._clean_content(content)
                except:
                    continue

            return None

        except Exception as e:
            logger.error(f"Erro BeautifulSoup: {e}")
            return None

    def _extract_semantic_content(self, soup) -> Optional[str]:
        """Extrai usando elementos semânticos HTML5"""
        semantic_elements = soup.find_all(['article', 'main', 'section'])

        if semantic_elements:
            content_parts = []
            for element in semantic_elements:
                text = element.get_text()
                if len(text) > 50:
                    content_parts.append(text)

            if content_parts:
                return '\n\n'.join(content_parts)

        return None

    def _extract_by_selectors(self, soup) -> Optional[str]:
        """Extrai usando seletores CSS comuns"""
        content_selectors = [
            '.content', '#content', '.post', '.article',
            '.entry', '.text', '.body', '.main-content',
            '.post-content', '.article-content', '.entry-content',
            '.page-content', '.text-content', '.story-content'
        ]

        for selector in content_selectors:
            try:
                elements = soup.select(selector)
                if elements:
                    content_parts = []
                    for element in elements:
                        text = element.get_text()
                        if len(text) > 50:
                            content_parts.append(text)

                    if content_parts:
                        return '\n\n'.join(content_parts)
            except:
                continue

        return None

    def _extract_largest_text_block(self, soup) -> Optional[str]:
        """Encontra e extrai o maior bloco de texto"""
        all_divs = soup.find_all(['div', 'section', 'article'])

        largest_text = ""
        largest_size = 0

        for div in all_divs:
            text = div.get_text()
            if len(text) > largest_size:
                largest_size = len(text)
                largest_text = text

        return largest_text if largest_size > 100 else None

    def _extract_full_body(self, soup) -> Optional[str]:
        """Extrai todo o conteúdo do body como último recurso"""
        body = soup.find('body')
        if body:
            return body.get_text()
        else:
            return soup.get_text()

    def _clean_content(self, content: str) -> str:
        """Limpa e normaliza o conteúdo extraído com melhorias"""
        if not content:
            return ""

        # Remove quebras de linha excessivas
        content = re.sub(r'\n\s*\n\s*\n+', '\n\n', content)

        # Remove espaços excessivos
        content = re.sub(r'[ \t]+', ' ', content)

        # Remove caracteres de controle
        content = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', content)

        # Remove linhas muito curtas (provavelmente navegação)
        lines = content.split('\n')
        meaningful_lines = []

        for line in lines:
            line = line.strip()
            if (len(line) > 10 and  # Linha substancial
                not re.match(r'^[\s\W]*$', line) and  # Não só símbolos
                not line.lower() in ['menu', 'home', 'contato', 'sobre', 'login']):  # Não navegação
                meaningful_lines.append(line)

        content = '\n'.join(meaningful_lines)

        # Normaliza
        content = content.strip()

        # Limita tamanho
        if len(content) > self.max_content_length:
            content = content[:self.max_content_length] + "..."

        return content

    def _validate_content(self, content: str, url: str) -> bool:
        """Valida se o conteúdo extraído é válido com critérios aprimorados"""
        if not content:
            logger.warning(f"⚠️ Conteúdo vazio para {url}")
            return False

        # Verifica tamanho mínimo mais rigoroso
        min_length = 500 if not self._is_pdf_url(url) else 200
        if len(content) < min_length:
            logger.warning(f"⚠️ Conteúdo pequeno para {url}: {len(content)} < {self.min_content_length}")
            return False

        # Verifica densidade de palavras
        words = content.split()
        min_words = 100 if not self._is_pdf_url(url) else 50
        if len(words) < min_words:
            logger.warning(f"⚠️ Poucas palavras para {url}: {len(words)}")
            return False

        # Verifica se não é página de erro
        error_indicators = ['404', 'not found', 'página não encontrada', 'erro', 'error',
                           'forbidden', 'access denied', 'unauthorized', 'service unavailable']
        content_lower = content.lower()

        error_count = sum(1 for indicator in error_indicators if indicator in content_lower)
        if error_count > 2 and len(content) < 2000:
            logger.warning(f"⚠️ Possível página de erro para {url}: {error_count} indicadores")
            return False

        # Verifica densidade de conteúdo português
        common_words = ['o', 'a', 'de', 'da', 'do', 'e', 'em', 'um', 'uma', 'com', 'não', 'para', 'que', 'se', 'é', 'ou']
        real_words = sum(1 for word in words if any(common in word.lower() for common in common_words))

        portuguese_ratio = real_words / len(words)
        if portuguese_ratio < 0.08:  # Pelo menos 8% de palavras em português
            logger.warning(f"⚠️ Conteúdo suspeito para {url}: poucos conectivos ({real_words}/{len(words)})")
            return False

        # Verifica se não é só navegação/menu
        navigation_words = ['menu', 'home', 'contato', 'sobre', 'login', 'cadastro', 'produtos', 'serviços']
        nav_count = sum(1 for word in words if word.lower() in navigation_words)
        nav_ratio = nav_count / len(words)

        if nav_ratio > 0.3:  # Mais de 30% são palavras de navegação
            logger.warning(f"⚠️ Muito conteúdo de navegação para {url}: {nav_ratio:.2%}")
            return False

        logger.info(f"✅ Conteúdo válido para {url}: {len(content)} caracteres, {len(words)} palavras")
        return True

    def _is_extractor_available(self, extractor_name: str) -> bool:
        """Verifica se o extrator está disponível"""
        return self.stats.get(extractor_name, {}).get('available', False)

    def _get_available_extractors(self) -> List[str]:
        """Retorna lista de extratores disponíveis"""
        available = []
        for name, stats in self.stats.items():
            if name != 'global' and stats.get('available', False):
                available.append(name)
        return available

    def _update_global_stats(self):
        """Atualiza estatísticas globais"""
        total = self.stats['global']['total_extractions']
        successes = self.stats['global']['total_successes']

        if total > 0:
            self.stats['global']['success_rate'] = (successes / total) * 100

        # Atualiza estatísticas individuais dos extratores
        for extractor_name, stats in self.stats.items():
            if extractor_name == 'global':
                continue

            total_attempts = stats['success'] + stats['failed']
            if total_attempts > 0:
                stats['success_rate'] = (stats['success'] / total_attempts) * 100
                if stats['success'] > 0:
                    stats['avg_response_time'] = stats['total_time'] / stats['success']
                else:
                    stats['avg_response_time'] = 0
            else:
                stats['success_rate'] = 0
                stats['avg_response_time'] = 0

            # Adiciona razão se não disponível
            if not stats['available']:
                if extractor_name == 'trafilatura' and not HAS_TRAFILATURA:
                    stats['reason'] = 'Biblioteca trafilatura não instalada'
                elif extractor_name == 'readability' and not HAS_READABILITY:
                    stats['reason'] = 'Biblioteca readability-lxml não instalada'
                elif extractor_name == 'newspaper' and not HAS_NEWSPAPER:
                    stats['reason'] = 'Biblioteca newspaper3k não instalada'
                elif extractor_name == 'beautifulsoup' and not HAS_BEAUTIFULSOUP:
                    stats['reason'] = 'Biblioteca beautifulsoup4 não instalada'
                elif extractor_name == 'pdf_pypdf2' and not HAS_PYPDF2:
                    stats['reason'] = 'Biblioteca PyPDF2 não instalada'
                elif extractor_name == 'pdf_pdfplumber' and not HAS_PDFPLUMBER:
                    stats['reason'] = 'Biblioteca pdfplumber não instalada'

    def get_extractor_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas dos extratores"""
        self._update_global_stats()
        return self.stats.copy()

    def reset_extractor_stats(self, extractor_name: Optional[str] = None):
        """Reset estatísticas dos extratores"""
        if extractor_name and extractor_name in self.stats:
            if extractor_name != 'global':
                self.stats[extractor_name].update({
                    'success': 0, 'failed': 0, 'total_time': 0, 'usage_count': 0,
                    'success_rate': 0, 'avg_response_time': 0
                })
            logger.info(f"🔄 Reset estatísticas do extrator: {extractor_name}")
        else:
            # Reset todas
            for extractor in self.stats:
                if extractor != 'global':
                    self.stats[extractor].update({
                        'success': 0, 'failed': 0, 'total_time': 0, 'usage_count': 0,
                        'success_rate': 0, 'avg_response_time': 0
                    })

            self.stats['global'] = {
                'total_extractions': 0,
                'total_successes': 0,
                'total_failures': 0,
                'success_rate': 0.0
            }
            logger.info("🔄 Reset estatísticas de todos os extratores")

    def batch_extract(self, urls: List[str], max_workers: int = 5) -> Dict[str, Optional[str]]:
        """Extrai conteúdo de múltiplas URLs em paralelo"""
        results = {}

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_url = {executor.submit(self.extract_content, url): url for url in urls}

            for future in as_completed(future_to_url):
                url = future_to_url[future]
                try:
                    content = future.result()
                    results[url] = content
                except Exception as e:
                    logger.error(f"Erro na extração paralela de {url}: {e}")
                    results[url] = None

        return results

    def test_extraction(self, url: str) -> Dict[str, Any]:
        """Testa extração para uma URL específica com detalhes"""
        start_time = time.time()

        result = {
            'url': url,
            'success': False,
            'content_length': 0,
            'extraction_time': 0,
            'extractor_used': None,
            'error': None,
            'content_preview': None
        }

        try:
            content = self.extract_content(url)
            extraction_time = time.time() - start_time

            if content:
                result.update({
                    'success': True,
                    'content_length': len(content),
                    'extraction_time': extraction_time,
                    'content_preview': content[:500] + '...' if len(content) > 500 else content
                })
            else:
                result.update({
                    'extraction_time': extraction_time,
                    'error': 'Nenhum conteúdo extraído'
                })

        except Exception as e:
            result.update({
                'extraction_time': time.time() - start_time,
                'error': str(e)
            })

        return result

    def clear_cache(self):
        """Limpa cache de sessão"""
        self.session.close()
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })
        logger.info("🧹 Cache de extração limpo")

# Instância global
robust_content_extractor = RobustContentExtractor()