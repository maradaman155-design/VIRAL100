
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ARQV30 Enhanced v3.0 - Visual Content Capture
Captura de screenshots e conteúdo visual usando Selenium
"""

import os
import logging
import time
import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime
from pathlib import Path

# Selenium imports
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
from webdriver_manager.chrome import ChromeDriverManager

logger = logging.getLogger(__name__)

class VisualContentCapture:
    """Capturador de conteúdo visual usando Selenium"""

    def __init__(self):
        """Inicializa o capturador visual"""
        self.driver = None
        self.wait_timeout = 10
        self.page_load_timeout = 30
        
        logger.info("📸 Visual Content Capture inicializado")

    def _setup_driver(self) -> webdriver.Chrome:
        """Configura o driver do Chrome em modo headless"""
        try:
            chrome_options = Options()
            
            # Configurações para modo headless e otimização no Replit
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--disable-web-security")
            chrome_options.add_argument("--disable-features=VizDisplayCompositor")
            chrome_options.add_argument("--remote-debugging-port=9222")
            chrome_options.add_argument("--window-size=1920,1080")
            chrome_options.add_argument("--disable-extensions")
            chrome_options.add_argument("--disable-plugins")
            chrome_options.add_argument("--disable-images")  # Para economizar banda
            chrome_options.add_argument("--user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36")
            
            # Usa selenium_checker para configuração robusta
            from .selenium_checker import selenium_checker
            
            # Executa verificação completa
            check_results = selenium_checker.full_check()
            
            if not check_results['selenium_ready']:
                raise Exception("Selenium não está configurado corretamente")
            
            # Configura o Chrome com o melhor caminho encontrado
            best_chrome_path = check_results['best_chrome_path']
            if best_chrome_path:
                chrome_options.binary_location = best_chrome_path
                logger.info(f"✅ Chrome configurado: {best_chrome_path}")
            
            # Tenta usar ChromeDriverManager primeiro
            try:
                service = Service(ChromeDriverManager().install())
                driver = webdriver.Chrome(service=service, options=chrome_options)
                logger.info("✅ ChromeDriverManager funcionou")
            except Exception as e:
                logger.warning(f"⚠️ ChromeDriverManager falhou: {e}, usando chromedriver do sistema")
                # Fallback para chromedriver do sistema
                driver = webdriver.Chrome(options=chrome_options)
            
            driver.set_page_load_timeout(self.page_load_timeout)
            
            logger.info("✅ Chrome driver configurado com sucesso")
            return driver
            
        except Exception as e:
            logger.error(f"❌ Erro ao configurar Chrome driver: {e}")
            raise

    def _create_session_directory(self, session_id: str) -> Path:
        """Cria diretório para a sessão"""
        try:
            session_dir = Path("analyses_data") / "files" / session_id
            session_dir.mkdir(parents=True, exist_ok=True)
            
            logger.info(f"📁 Diretório criado: {session_dir}")
            return session_dir
            
        except Exception as e:
            logger.error(f"❌ Erro ao criar diretório: {e}")
            raise

    def _take_screenshot(self, url: str, filename: str, session_dir: Path) -> Dict[str, Any]:
        """Captura screenshot de uma URL específica"""
        try:
            logger.info(f"📸 Capturando screenshot: {url}")
            
            # Acessa a URL
            self.driver.get(url)
            
            # Aguarda o carregamento da página
            try:
                WebDriverWait(self.driver, self.wait_timeout).until(
                    EC.presence_of_element_located((By.TAG_NAME, "body"))
                )
            except TimeoutException:
                logger.warning(f"⚠️ Timeout aguardando carregamento de {url}")
            
            # Aguarda um pouco mais para renderização completa
            time.sleep(2)
            
            # Captura informações da página
            page_title = self.driver.title or "Sem título"
            page_url = self.driver.current_url
            
            # Tenta obter meta description
            meta_description = ""
            try:
                meta_element = self.driver.find_element(By.CSS_SELECTOR, 'meta[name="description"]')
                meta_description = meta_element.get_attribute("content") or ""
            except:
                pass
            
            # Define o caminho do arquivo
            screenshot_path = session_dir / f"{filename}.png"
            
            # Captura o screenshot
            self.driver.save_screenshot(str(screenshot_path))
            
            # Verifica se o arquivo foi criado
            if screenshot_path.exists() and screenshot_path.stat().st_size > 0:
                logger.info(f"✅ Screenshot salvo: {screenshot_path}")
                
                return {
                    'success': True,
                    'url': url,
                    'final_url': page_url,
                    'title': page_title,
                    'description': meta_description,
                    'filename': f"{filename}.png",
                    'filepath': str(screenshot_path),
                    'filesize': screenshot_path.stat().st_size,
                    'timestamp': datetime.now().isoformat()
                }
            else:
                raise Exception("Screenshot não foi criado ou está vazio")
                
        except Exception as e:
            error_msg = f"Erro ao capturar screenshot de {url}: {e}"
            logger.error(f"❌ {error_msg}")
            
            return {
                'success': False,
                'url': url,
                'error': error_msg,
                'timestamp': datetime.now().isoformat()
            }

    async def capture_screenshots(self, urls: List[str], session_id: str) -> Dict[str, Any]:
        """
        Captura screenshots de uma lista de URLs
        
        Args:
            urls: Lista de URLs para capturar
            session_id: ID da sessão para organização
        """
        logger.info(f"📸 Iniciando captura de {len(urls)} screenshots para sessão {session_id}")
        
        # Resultado da operação
        capture_results = {
            'session_id': session_id,
            'total_urls': len(urls),
            'successful_captures': 0,
            'failed_captures': 0,
            'screenshots': [],
            'errors': [],
            'start_time': datetime.now().isoformat(),
            'session_directory': None
        }
        
        try:
            # Cria diretório da sessão
            session_dir = self._create_session_directory(session_id)
            capture_results['session_directory'] = str(session_dir)
            
            # Configura o driver
            self.driver = self._setup_driver()
            
            # Processa cada URL
            for i, url in enumerate(urls, 1):
                if not url or not url.startswith(('http://', 'https://')):
                    logger.warning(f"⚠️ URL inválida ignorada: {url}")
                    capture_results['failed_captures'] += 1
                    capture_results['errors'].append(f"URL inválida: {url}")
                    continue
                
                try:
                    # Gera nome do arquivo
                    filename = f"screenshot_{i:03d}"
                    
                    # Captura o screenshot
                    result = self._take_screenshot(url, filename, session_dir)
                    
                    if result['success']:
                        capture_results['successful_captures'] += 1
                        capture_results['screenshots'].append(result)
                    else:
                        capture_results['failed_captures'] += 1
                        capture_results['errors'].append(result['error'])
                    
                    # Pequena pausa entre capturas para não sobrecarregar
                    await asyncio.sleep(1)
                    
                except Exception as e:
                    error_msg = f"Erro processando URL {url}: {e}"
                    logger.error(f"❌ {error_msg}")
                    capture_results['failed_captures'] += 1
                    capture_results['errors'].append(error_msg)
            
            # Finaliza a captura
            capture_results['end_time'] = datetime.now().isoformat()
            
            logger.info(f"✅ Captura concluída: {capture_results['successful_captures']}/{capture_results['total_urls']} sucessos")
            
        except Exception as e:
            error_msg = f"Erro crítico na captura: {e}"
            logger.error(f"❌ {error_msg}")
            capture_results['critical_error'] = error_msg
            
        finally:
            # Fecha o driver se estiver aberto
            if self.driver:
                try:
                    self.driver.quit()
                    logger.info("✅ Chrome driver fechado")
                except Exception as e:
                    logger.error(f"❌ Erro ao fechar driver: {e}")
                self.driver = None
        
        return capture_results

    def select_top_urls(self, all_results: Dict[str, Any], max_urls: int = 10) -> List[str]:
        """
        Seleciona as URLs mais relevantes dos resultados de busca
        
        Args:
            all_results: Resultados consolidados de todas as buscas
            max_urls: Número máximo de URLs para retornar
        """
        logger.info(f"🎯 Selecionando top {max_urls} URLs mais relevantes")
        
        all_urls = all_results.get('consolidated_urls', [])
        
        if not all_urls:
            logger.warning("⚠️ Nenhuma URL encontrada nos resultados")
            return []
        
        # Por enquanto, retorna as primeiras URLs únicas
        # Em uma implementação mais sofisticada, poderia ranquear por relevância
        unique_urls = []
        seen_domains = set()
        
        for url in all_urls:
            try:
                # Extrai domínio para diversificar
                from urllib.parse import urlparse
                domain = urlparse(url).netloc.lower()
                
                # Adiciona URL se for de domínio novo ou se ainda não temos URLs suficientes
                if domain not in seen_domains or len(unique_urls) < max_urls // 2:
                    unique_urls.append(url)
                    seen_domains.add(domain)
                    
                    if len(unique_urls) >= max_urls:
                        break
                        
            except Exception as e:
                logger.warning(f"⚠️ Erro processando URL {url}: {e}")
                continue
        
        logger.info(f"✅ Selecionadas {len(unique_urls)} URLs de {len(seen_domains)} domínios diferentes")
        return unique_urls

    def cleanup_old_screenshots(self, days_old: int = 7):
        """Remove screenshots antigos para economizar espaço"""
        try:
            files_dir = Path("analyses_data") / "files"
            if not files_dir.exists():
                return
            
            cutoff_time = time.time() - (days_old * 24 * 60 * 60)
            removed_count = 0
            
            for session_dir in files_dir.iterdir():
                if session_dir.is_dir():
                    for screenshot in session_dir.glob("*.png"):
                        if screenshot.stat().st_mtime < cutoff_time:
                            screenshot.unlink()
                            removed_count += 1
                    
                    # Remove diretório se estiver vazio
                    try:
                        session_dir.rmdir()
                    except OSError:
                        pass  # Diretório não está vazio
            
            if removed_count > 0:
                logger.info(f"🧹 Removidos {removed_count} screenshots antigos")
                
        except Exception as e:
            logger.error(f"❌ Erro na limpeza: {e}")

# Instância global
visual_content_capture = VisualContentCapture()
