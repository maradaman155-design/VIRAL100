#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ARQV30 Enhanced v2.0 - Exa Client
Cliente para integração com Exa API para pesquisa avançada
"""

import os
import logging
import requests
import json
from typing import Dict, List, Optional, Any
from datetime import datetime

logger = logging.getLogger(__name__)

class ExaClient:
    """Cliente para integração com Exa API"""
    
    def __init__(self):
        """Inicializa cliente Exa"""
        self.api_key = os.getenv("EXA_API_KEY", "a0dd63a6-0bd1-488f-a63e-2c4f4cfe969f")
        self.base_url = "https://api.exa.ai"
        
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        self.available = bool(self.api_key)
        
        if self.available:
            logger.info("✅ Exa client inicializado com sucesso")
        else:
            logger.warning("⚠️ Exa API key não encontrada")
    
    def is_available(self) -> bool:
        """Verifica se o cliente está disponível"""
        return self.available
    
    def search(
        self, 
        query: str, 
        num_results: int = 10,
        include_domains: List[str] = None,
        exclude_domains: List[str] = None,
        start_crawl_date: str = None,
        end_crawl_date: str = None,
        start_published_date: str = None,
        end_published_date: str = None,
        use_autoprompt: bool = True,
        type: str = "neural"
    ) -> Optional[Dict[str, Any]]:
        """Realiza busca usando Exa API"""
        
        if not self.available:
            logger.warning("Exa não está disponível")
            return None
        
        try:
            payload = {
                "query": query,
                "numResults": num_results,
                "useAutoprompt": use_autoprompt,
                "type": type
            }
            
            if include_domains:
                payload["includeDomains"] = include_domains
            
            if exclude_domains:
                payload["excludeDomains"] = exclude_domains
            
            if start_crawl_date:
                payload["startCrawlDate"] = start_crawl_date
            
            if end_crawl_date:
                payload["endCrawlDate"] = end_crawl_date
            
            if start_published_date:
                payload["startPublishedDate"] = start_published_date
            
            if end_published_date:
                payload["endPublishedDate"] = end_published_date
            
            response = requests.post(
                f"{self.base_url}/search",
                headers=self.headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                logger.info(f"✅ Exa search: {len(data.get('results', []))} resultados")
                return data
            else:
                logger.error(f"❌ Erro Exa: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"❌ Erro na requisição Exa: {str(e)}")
            return None
    
    def get_contents(
        self, 
        ids: List[str],
        text: bool = True,
        highlights: bool = False,
        summary: bool = False
    ) -> Optional[Dict[str, Any]]:
        """Obtém conteúdo detalhado dos resultados"""
        
        if not self.available:
            return None
        
        try:
            payload = {
                "ids": ids,
                "text": text,
                "highlights": highlights,
                "summary": summary
            }
            
            response = requests.post(
                f"{self.base_url}/contents",
                headers=self.headers,
                json=payload,
                timeout=60
            )
            
            if response.status_code == 200:
                data = response.json()
                logger.info(f"✅ Exa contents: {len(data.get('results', []))} conteúdos")
                return data
            else:
                logger.error(f"❌ Erro Exa contents: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"❌ Erro ao obter conteúdos Exa: {str(e)}")
            return None
    
    def find_similar(
        self, 
        url: str, 
        num_results: int = 10,
        exclude_source_domain: bool = True
    ) -> Optional[Dict[str, Any]]:
        """Encontra páginas similares"""
        
        if not self.available:
            return None
        
        try:
            payload = {
                "url": url,
                "numResults": num_results,
                "excludeSourceDomain": exclude_source_domain
            }
            
            response = requests.post(
                f"{self.base_url}/findSimilar",
                headers=self.headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                logger.info(f"✅ Exa similar: {len(data.get('results', []))} similares")
                return data
            else:
                logger.error(f"❌ Erro Exa similar: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"❌ Erro ao buscar similares: {str(e)}")
            return None

# Instância global
exa_client = ExaClient()