#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ARQV30 Enhanced v2.0 - URL Resolver CORRIGIDO
Resolve URLs de redirecionamento e encurtadores com decodificação robusta
"""

import os
import logging
import base64
import requests
import json
from urllib.parse import parse_qs, urlparse, unquote
from typing import Optional

logger = logging.getLogger(__name__)

class URLResolver:
    """Resolvedor robusto de URLs de redirecionamento"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })
        self.timeout = 10
        
    def resolve_redirect_url(self, url: str) -> str:
        """
        Resolve URLs de redirecionamento do Bing, Google e encurtadores.
        """
        try:
            original_url = url
            
            # Bing: URLs com u=a1aHR0c...
            if "bing.com/ck/a" in url and "u=a1" in url:
                logger.info(f"🔄 Resolvendo URL do Bing: {url[:100]}...")
                resolved = self._resolve_bing_url(url)
                if resolved and resolved != url and resolved.startswith('http'):
                    logger.info(f"✅ URL Bing resolvida: {resolved}")
                    return resolved
            
            # Google: URLs com /url?q=
            elif "/url?q=" in url or "google." in url and "url?q=" in url:
                logger.info(f"🔄 Resolvendo URL do Google: {url[:100]}...")
                resolved = self._resolve_google_url(url)
                if resolved and resolved != url and resolved.startswith('http'):
                    logger.info(f"✅ URL Google resolvida: {resolved}")
                    return resolved
            
            # Encurtadores conhecidos
            elif self._is_short_url(url):
                logger.info(f"🔄 Resolvendo URL encurtada: {url}")
                resolved = self._resolve_short_url(url)
                if resolved and resolved != url and resolved.startswith('http'):
                    logger.info(f"✅ URL encurtada resolvida: {resolved}")
                    return resolved
            
            # URL já está limpa
            return url
            
        except Exception as e:
            logger.error(f"❌ Erro ao resolver URL {url}: {str(e)}")
            return url  # Retorna a original se falhar
    
    def _resolve_bing_url(self, url: str) -> str:
        """Resolve URLs específicas do Bing com decodificação Base64 dupla"""
        try:
            logger.debug(f"🔍 Resolvendo URL do Bing: {url}")
            
            # Extrai parâmetro u=a1...
            if "u=a1" in url:
                # Formato: u=a1aHR0c...
                u_param_start = url.find("u=a1") + 4  # Pula "u=a1"
                u_param_end = url.find("&", u_param_start)
                if u_param_end == -1:
                    u_param_end = len(url)
                
                encoded_part = url[u_param_start:u_param_end]
                
                logger.debug(f"🔍 Parte codificada extraída: {encoded_part[:50]}...")
                
                # Decodifica Base64 duplo
                try:
                    # Limpa caracteres especiais que podem interferir
                    encoded_part = encoded_part.replace('%3d', '=').replace('%3D', '=')
                    
                    # Adiciona padding se necessário
                    missing_padding = len(encoded_part) % 4
                    if missing_padding:
                        encoded_part += '=' * (4 - missing_padding)
                    
                    # Primeira decodificação
                    first_decode = base64.b64decode(encoded_part)
                    logger.debug(f"🔍 Primeira decodificação: {first_decode[:50]}...")
                    
                    # Verifica se precisa de segunda decodificação
                    first_decode_str = first_decode.decode('utf-8', errors='ignore')
                    
                    if first_decode_str.startswith('aHR0'):
                        # Precisa de segunda decodificação
                        missing_padding = len(first_decode_str) % 4
                        if missing_padding:
                            first_decode_str += '=' * (4 - missing_padding)
                        
                        second_decode = base64.b64decode(first_decode_str)
                        final_url = second_decode.decode('utf-8', errors='ignore')
                        
                        if final_url.startswith('http'):
                            logger.info(f"✅ URL Bing decodificada (dupla): {final_url}")
                            return final_url
                    
                    elif first_decode_str.startswith('http'):
                        # Primeira decodificação já é suficiente
                        logger.info(f"✅ URL Bing decodificada (simples): {first_decode_str}")
                        return first_decode_str
                    
                except Exception as decode_error:
                    logger.warning(f"⚠️ Falha na decodificação Base64: {str(decode_error)}")
                    # Tenta decodificação alternativa
                    try:
                        # Remove caracteres problemáticos e tenta novamente
                        clean_encoded = ''.join(c for c in encoded_part if c.isalnum() or c in '+/=')
                        decoded = base64.b64decode(clean_encoded + '==')
                        decoded_str = decoded.decode('utf-8', errors='ignore')
                        if decoded_str.startswith('http'):
                            logger.info(f"✅ URL Bing decodificada (alternativa): {decoded_str}")
                            return decoded_str
                    except:
                        pass
            
            # Método alternativo: follow redirects
            return self._follow_redirects(url)
            
        except Exception as e:
            logger.error(f"❌ Erro ao resolver Bing URL: {e}")
            return url
    
    def _resolve_google_url(self, url: str) -> str:
        """Resolve URLs do Google"""
        try:
            parsed = urlparse(url)
            
            if "url?q=" in url:
                # Extrai parâmetro q
                query_params = parse_qs(parsed.query)
                q_param = query_params.get('q')
                if q_param:
                    decoded_url = unquote(q_param[0])
                    if decoded_url.startswith('http'):
                        logger.info(f"✅ URL Google decodificada: {decoded_url}")
                        return decoded_url
            
            # Follow redirects se não conseguir extrair
            return self._follow_redirects(url)
            
        except Exception as e:
            logger.error(f"❌ Erro ao resolver Google URL: {e}")
            return url
    
    def _is_short_url(self, url: str) -> bool:
        """Verifica se é URL encurtada"""
        short_domains = [
            'bit.ly', 'tinyurl.com', 'goo.gl', 't.co', 'short.link',
            'ow.ly', 'buff.ly', 'tiny.cc', 'is.gd', 'v.gd'
        ]
        return any(domain in url for domain in short_domains)
    
    def _resolve_short_url(self, url: str) -> str:
        """Resolve URLs encurtadas seguindo redirects"""
        return self._follow_redirects(url)
    
    def _follow_redirects(self, url: str, max_redirects: int = 5) -> str:
        """Segue redirects até a URL final"""
        try:
            response = self.session.head(
                url, 
                allow_redirects=True, 
                timeout=self.timeout,
                verify=False  # Para evitar problemas de SSL
            )
            
            final_url = response.url
            if final_url and final_url != url and final_url.startswith('http'):
                logger.info(f"🔄 Redirect seguido: {url[:50]}... -> {final_url[:50]}...")
                return final_url
            
            return url
            
        except Exception as e:
            logger.warning(f"⚠️ Erro ao seguir redirects para {url}: {e}")
            return url

# Instância global
url_resolver = URLResolver()

# Função de conveniência
def resolve_url(url: str) -> str:
    """Função de conveniência para resolver URLs"""
    return url_resolver.resolve_redirect_url(url)