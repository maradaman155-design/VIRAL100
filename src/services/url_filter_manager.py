#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ARQV30 Enhanced v2.0 - URL Filter Manager
Filtro inteligente de URLs para evitar conteúdo irrelevante
"""

import time
import random
import logging
import re
from typing import List, Set, Dict, Any, Optional
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

class URLFilterManager:
    """Gerenciador de filtros de URL para evitar conteúdo irrelevante"""
    
    def __init__(self):
        """Inicializa filtros de URL"""
        
        # Domínios completamente bloqueados
        self.dominios_bloqueados = {
            "accounts.google.com",
            "login.microsoft.com", 
            "instagram.com",
            "facebook.com",
            "zhihu.com",
            "answers.microsoft.com",
            "gmail.com",
            "outlook.com",
            "twitter.com",
            "linkedin.com",
            "youtube.com",
            "tiktok.com",
            "pinterest.com",
            "reddit.com",
            "quora.com",
            "stackoverflow.com",
            "github.com",
            "wikipedia.org",
            "amazon.com.br",
            "mercadolivre.com.br",
            "olx.com.br",
            "booking.com",
            "airbnb.com",
            "uber.com",
            "ifood.com.br"
        }
        
        # Padrões de URL bloqueados
        self.padroes_bloqueados = [
            r'/login',
            r'/signin',
            r'/register',
            r'/cadastro',
            r'/auth',
            r'/account',
            r'/profile',
            r'/settings',
            r'/admin',
            r'/dashboard',
            r'/api/',
            r'\.pdf$',
            r'\.jpg$',
            r'\.png$',
            r'\.gif$',
            r'\.mp4$',
            r'\.zip$',
            r'\.exe$',
            r'/download',
            r'/cart',
            r'/checkout',
            r'/payment',
            r'/privacy',
            r'/terms',
            r'/cookies',
            r'/sitemap'
        ]
        
        # Palavras-chave que indicam conteúdo irrelevante
        self.palavras_irrelevantes = {
            'login', 'signin', 'register', 'cadastro', 'entrar',
            'conta', 'perfil', 'configurações', 'settings',
            'carrinho', 'comprar', 'checkout', 'pagamento',
            'download', 'baixar', 'instalar', 'app store',
            'play store', 'android', 'ios', 'mobile app',
            'termos de uso', 'política de privacidade', 'cookies',
            'contato', 'fale conosco', 'suporte', 'ajuda',
            'sobre nós', 'quem somos', 'nossa história',
            'trabalhe conosco', 'vagas', 'careers', 'jobs'
        }
        
        # Domínios preferenciais (conteúdo de qualidade)
        self.dominios_preferenciais = {
            "g1.globo.com",
            "exame.com", 
            "valor.globo.com",
            "estadao.com.br",
            "folha.uol.com.br",
            "canaltech.com.br",
            "tecmundo.com.br",
            "olhardigital.com.br",
            "infomoney.com.br",
            "startse.com",
            "revistapegn.globo.com",
            "epocanegocios.globo.com",
            "istoedinheiro.com.br",
            "convergenciadigital.com.br",
            "mobiletime.com.br",
            "teletime.com.br"
        }
        
        self.urls_filtradas = set()
        self.stats = {
            'total_analisadas': 0,
            'bloqueadas_dominio': 0,
            'bloqueadas_padrao': 0,
            'bloqueadas_palavra': 0,
            'aprovadas': 0,
            'preferenciais': 0
        }
        
        logger.info(f"🔍 URL Filter Manager inicializado com {len(self.dominios_bloqueados)} domínios bloqueados")
    
    def filtrar_url(self, url: str, titulo: str = "", snippet: str = "") -> Dict[str, Any]:
        """Filtra URL e retorna resultado detalhado"""
        
        self.stats['total_analisadas'] += 1
        
        if not url or not url.startswith('http'):
            return {
                'aprovada': False,
                'motivo': 'URL inválida',
                'categoria': 'invalida',
                'prioridade': 0
            }
        
        try:
            parsed_url = urlparse(url)
            domain = parsed_url.netloc.lower()
            path = parsed_url.path.lower()
            query = parsed_url.query.lower()
            
            # Remove www. para comparação
            domain_clean = domain.replace('www.', '')
            
            # 1. Verifica domínios bloqueados
            if domain_clean in self.dominios_bloqueados:
                self.stats['bloqueadas_dominio'] += 1
                logger.debug(f"⏭️ URL bloqueada (domínio): {url}")
                return {
                    'aprovada': False,
                    'motivo': f'Domínio bloqueado: {domain_clean}',
                    'categoria': 'dominio_bloqueado',
                    'prioridade': 0
                }
            
            # 2. Verifica padrões bloqueados na URL
            url_completa = f"{path}?{query}".lower()
            for padrao in self.padroes_bloqueados:
                if re.search(padrao, url_completa):
                    self.stats['bloqueadas_padrao'] += 1
                    logger.debug(f"⏭️ URL bloqueada (padrão): {url}")
                    return {
                        'aprovada': False,
                        'motivo': f'Padrão bloqueado: {padrao}',
                        'categoria': 'padrao_bloqueado',
                        'prioridade': 0
                    }
            
            # 3. Verifica palavras irrelevantes no título/snippet
            texto_completo = f"{titulo} {snippet}".lower()
            palavras_encontradas = []
            
            for palavra in self.palavras_irrelevantes:
                if palavra in texto_completo:
                    palavras_encontradas.append(palavra)
            
            if len(palavras_encontradas) >= 2:  # 2+ palavras irrelevantes
                self.stats['bloqueadas_palavra'] += 1
                logger.debug(f"⏭️ URL bloqueada (palavras): {url}")
                return {
                    'aprovada': False,
                    'motivo': f'Palavras irrelevantes: {palavras_encontradas[:3]}',
                    'categoria': 'conteudo_irrelevante',
                    'prioridade': 0
                }
            
            # 4. Calcula prioridade
            prioridade = self._calcular_prioridade_url(domain_clean, titulo, snippet)
            
            # 5. URL aprovada
            self.stats['aprovadas'] += 1
            
            if domain_clean in self.dominios_preferenciais:
                self.stats['preferenciais'] += 1
                categoria = 'preferencial'
            else:
                categoria = 'aprovada'
            
            logger.debug(f"✅ URL aprovada: {url} (prioridade: {prioridade})")
            
            return {
                'aprovada': True,
                'motivo': 'URL válida para análise',
                'categoria': categoria,
                'prioridade': prioridade,
                'domain': domain_clean
            }
            
        except Exception as e:
            logger.error(f"❌ Erro ao filtrar URL {url}: {e}")
            return {
                'aprovada': False,
                'motivo': f'Erro no processamento: {str(e)}',
                'categoria': 'erro',
                'prioridade': 0
            }
    
    def filtrar_lista_urls(self, urls_com_metadata: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Filtra lista de URLs com metadata"""
        
        urls_aprovadas = []
        
        for item in urls_com_metadata:
            url = item.get('url', '')
            titulo = item.get('title', '')
            snippet = item.get('snippet', '')
            
            filtro_resultado = self.filtrar_url(url, titulo, snippet)
            
            if filtro_resultado['aprovada']:
                # Adiciona informações do filtro ao item
                item['filtro'] = filtro_resultado
                urls_aprovadas.append(item)
        
        # Ordena por prioridade
        urls_aprovadas.sort(key=lambda x: x['filtro']['prioridade'], reverse=True)
        
        logger.info(f"🔍 Filtro aplicado: {len(urls_aprovadas)}/{len(urls_com_metadata)} URLs aprovadas")
        
        return urls_aprovadas
    
    def _calcular_prioridade_url(self, domain: str, titulo: str, snippet: str) -> float:
        """Calcula prioridade da URL baseada em qualidade"""
        
        prioridade = 1.0  # Base
        
        # Bonus por domínio preferencial
        if domain in self.dominios_preferenciais:
            prioridade += 3.0
        
        # Bonus por palavras-chave de qualidade no título
        palavras_qualidade = [
            'análise', 'mercado', 'tendência', 'oportunidade', 'estratégia',
            'crescimento', 'inovação', 'dados', 'pesquisa', 'relatório',
            'estudo', 'insights', 'business', 'negócios', 'empresa',
            'startup', 'investimento', 'tecnologia', 'digital'
        ]
        
        titulo_lower = titulo.lower()
        snippet_lower = snippet.lower()
        
        for palavra in palavras_qualidade:
            if palavra in titulo_lower:
                prioridade += 0.5
            if palavra in snippet_lower:
                prioridade += 0.3
        
        # Bonus por ano atual
        if '2024' in titulo or '2024' in snippet:
            prioridade += 1.0
        elif '2023' in titulo or '2023' in snippet:
            prioridade += 0.5
        
        # Bonus por Brasil/brasileiro
        if any(termo in titulo_lower + snippet_lower for termo in ['brasil', 'brasileiro', 'br']):
            prioridade += 0.8
        
        # Penalty por conteúdo genérico
        if any(termo in titulo_lower for termo in ['home', 'página inicial', 'bem-vindo']):
            prioridade -= 1.0
        
        return max(prioridade, 0.1)  # Mínimo 0.1
    
    def adicionar_dominio_bloqueado(self, domain: str):
        """Adiciona domínio à lista de bloqueados"""
        self.dominios_bloqueados.add(domain.lower().replace('www.', ''))
        logger.info(f"🚫 Domínio adicionado à lista de bloqueados: {domain}")
    
    def remover_dominio_bloqueado(self, domain: str):
        """Remove domínio da lista de bloqueados"""
        domain_clean = domain.lower().replace('www.', '')
        if domain_clean in self.dominios_bloqueados:
            self.dominios_bloqueados.remove(domain_clean)
            logger.info(f"✅ Domínio removido da lista de bloqueados: {domain}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas do filtro"""
        
        total = self.stats['total_analisadas']
        
        if total > 0:
            stats_percentuais = {
                'taxa_aprovacao': (self.stats['aprovadas'] / total) * 100,
                'taxa_bloqueio_dominio': (self.stats['bloqueadas_dominio'] / total) * 100,
                'taxa_bloqueio_padrao': (self.stats['bloqueadas_padrao'] / total) * 100,
                'taxa_bloqueio_palavra': (self.stats['bloqueadas_palavra'] / total) * 100,
                'taxa_preferencial': (self.stats['preferenciais'] / total) * 100
            }
        else:
            stats_percentuais = {k: 0.0 for k in ['taxa_aprovacao', 'taxa_bloqueio_dominio', 'taxa_bloqueio_padrao', 'taxa_bloqueio_palavra', 'taxa_preferencial']}
        
        return {
            **self.stats,
            **stats_percentuais,
            'dominios_bloqueados_count': len(self.dominios_bloqueados),
            'dominios_preferenciais_count': len(self.dominios_preferenciais)
        }
    
    def reset_stats(self):
        """Reset estatísticas"""
        self.stats = {
            'total_analisadas': 0,
            'bloqueadas_dominio': 0,
            'bloqueadas_padrao': 0,
            'bloqueadas_palavra': 0,
            'aprovadas': 0,
            'preferenciais': 0
        }
        logger.info("🔄 Estatísticas do filtro resetadas")

# Instância global
url_filter_manager = URLFilterManager()

# Função de conveniência
def filtrar_urls(urls_com_metadata: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Função de conveniência para filtrar URLs"""
    return url_filter_manager.filtrar_lista_urls(urls_com_metadata)