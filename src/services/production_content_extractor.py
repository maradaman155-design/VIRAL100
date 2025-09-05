
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ARQV30 Enhanced v2.0 - Production Content Extractor (DEPRECATED)
ESTE MÓDULO FOI SUBSTITUÍDO POR robust_content_extractor.py
Mantido apenas para compatibilidade
"""
from typing import Dict, List, Optional, Any
import os
import logging
from .robust_content_extractor import robust_content_extractor

logger = logging.getLogger(__name__)


class ProductionContentExtractor:
    """Wrapper para compatibilidade - redireciona para RobustContentExtractor"""

    def __init__(self):
        """Inicializa wrapper de compatibilidade"""
        logger.warning("⚠️ ProductionContentExtractor está DEPRECATED - usando RobustContentExtractor")
        self.extractor = robust_content_extractor

    def extract_content(self, url: str) -> Optional[str]:
        """Redireciona para RobustContentExtractor"""
        return self.extractor.extract_content(url)

    def extract_metadata(self, url: str) -> Dict[str, Any]:
        """Redireciona para RobustContentExtractor"""
        # RobustContentExtractor não tem extract_metadata, então mantém funcionalidade básica
        try:
            import requests
            from bs4 import BeautifulSoup

            response = requests.get(url, timeout=15)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, "html.parser")
                title_tag = soup.find('title')
                return {
                    'title': title_tag.get_text().strip() if title_tag else '',
                    'url': url
                }
            return {'error': f'HTTP {response.status_code}'}
        except Exception as e:
            return {'error': str(e)}

    def batch_extract(self, urls: List[str], max_workers: int = 5) -> Dict[str, Optional[str]]:
        """Redireciona para RobustContentExtractor"""
        return self.extractor.batch_extract(urls, max_workers)

    def clear_cache(self):
        """Método de compatibilidade para limpar cache"""
        if hasattr(self.extractor, 'clear_cache'):
            return self.extractor.clear_cache()
        return True


# Instância global para compatibilidade
production_content_extractor = ProductionContentExtractor()
