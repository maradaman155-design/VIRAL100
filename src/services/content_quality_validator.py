#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ARQV30 Enhanced v2.0 - Content Quality Validator
Validador de qualidade de conteúdo extraído
"""

import logging
import re
from typing import Dict, Any, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class ContentQualityValidator:
    """Validador de qualidade de conteúdo"""
    
    def __init__(self):
        """Inicializa o validador"""
        self.min_content_length = 200  # Reduzido para ser menos rigoroso
        self.min_word_count = 50       # Reduzido para ser menos rigoroso
        self.max_navigation_ratio = 0.3
        self.min_information_density = 0.05  # Reduzido para ser menos rigoroso
        
        # Indicadores de páginas de erro
        self.error_indicators = [
            'página não encontrada', 'page not found', '404 error', '404 not found',
            'acesso negado', 'access denied', 'forbidden', '403 forbidden',
            'erro interno', 'internal server error', '500 error', '500 internal',
            'site em manutenção', 'under maintenance', 'temporarily unavailable',
            'javascript required', 'enable javascript', 'javascript disabled',
            'cookies required', 'enable cookies', 'cookies disabled',
            'browser not supported', 'navegador não suportado',
            'connection timed out', 'conexão expirou',
            'service unavailable', 'serviço indisponível',
            'bad gateway', 'gateway timeout'
        ]
        
        # Palavras de navegação/menu
        self.navigation_words = [
            'home', 'início', 'sobre', 'about', 'contato', 'contact',
            'menu', 'navegação', 'navigation', 'login', 'entrar',
            'cadastro', 'register', 'produtos', 'products', 'serviços',
            'services', 'blog', 'notícias', 'news', 'ajuda', 'help',
            'suporte', 'support', 'faq', 'termos', 'terms', 'privacidade',
            'privacy', 'política', 'policy', 'cookies', 'sitemap',
            'mapa do site', 'buscar', 'search', 'pesquisar'
        ]
        
        # Palavras que indicam conteúdo de qualidade
        self.quality_indicators = [
            'análise', 'pesquisa', 'estudo', 'relatório', 'dados',
            'estatística', 'mercado', 'tendência', 'oportunidade',
            'estratégia', 'crescimento', 'inovação', 'tecnologia',
            'business', 'marketing', 'vendas', 'cliente', 'consumidor',
            'empresa', 'negócio', 'investimento', 'receita', 'lucro'
        ]
        
        logger.info("Content Quality Validator inicializado")
    
    def validate_content(self, content: str, url: str = "", context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Valida qualidade do conteúdo extraído"""
        
        if not content:
            return {
                'valid': False,
                'score': 0.0,
                'reason': 'Conteúdo vazio',
                'details': {}
            }
        
        # Executa todas as validações
        validations = {
            'length_check': self._check_content_length(content),
            'error_page_check': self._check_error_page(content),
            'navigation_ratio_check': self._check_navigation_ratio(content),
            'information_density_check': self._check_information_density(content),
            'language_check': self._check_language(content),
            'structure_check': self._check_content_structure(content),
            'relevance_check': self._check_relevance(content, context or {})
        }
        
        # Calcula score geral
        total_score = 0.0
        max_score = 0.0
        
        for check_name, result in validations.items():
            total_score += result['score'] * result['weight']
            max_score += result['weight']
        
        final_score = (total_score / max_score) * 100 if max_score > 0 else 0
        
        # Determina se é válido
        is_valid = final_score >= 40.0  # Score mínimo reduzido para 40%
        
        # Identifica razão principal se inválido
        main_reason = "Conteúdo válido"
        if not is_valid:
            failed_checks = [name for name, result in validations.items() if not result['passed']]
            if failed_checks:
                main_reason = f"Falhou em: {', '.join(failed_checks)}"
        
        return {
            'valid': is_valid,
            'score': round(final_score, 2),
            'reason': main_reason,
            'details': validations,
            'content_stats': self._get_content_stats(content),
            'url': url,
            'validated_at': datetime.now().isoformat()
        }
    
    def _check_content_length(self, content: str) -> Dict[str, Any]:
        """Verifica comprimento do conteúdo"""
        length = len(content)
        
        if length >= self.min_content_length:
            score = min(100, (length / 2000) * 100)  # Score baseado em 2000 chars como ideal
            return {
                'passed': True,
                'score': score,
                'weight': 20,
                'message': f'Comprimento adequado: {length} caracteres',
                'value': length
            }
        else:
            score = max(20, (length / self.min_content_length) * 100)  # Score mínimo de 20
            return {
                'passed': length >= 100,  # Aceita se pelo menos 100 caracteres
                'score': score,
                'weight': 20,
                'message': f'Conteúdo muito curto: {length} < {self.min_content_length}',
                'value': length
            }
    
    def _check_error_page(self, content: str) -> Dict[str, Any]:
        """Verifica se é página de erro"""
        content_lower = content.lower()
        
        found_errors = []
        for indicator in self.error_indicators:
            if indicator in content_lower:
                found_errors.append(indicator)
        
        if found_errors:
            return {
                'passed': False,
                'score': 0,
                'weight': 30,
                'message': f'Página de erro detectada: {found_errors[0]}',
                'value': found_errors
            }
        else:
            return {
                'passed': True,
                'score': 100,
                'weight': 30,
                'message': 'Não é página de erro',
                'value': []
            }
    
    def _check_navigation_ratio(self, content: str) -> Dict[str, Any]:
        """Verifica proporção de palavras de navegação"""
        words = content.lower().split()
        
        if len(words) == 0:
            return {
                'passed': False,
                'score': 0,
                'weight': 15,
                'message': 'Nenhuma palavra encontrada',
                'value': 0
            }
        
        navigation_count = sum(1 for word in words if word in self.navigation_words)
        navigation_ratio = navigation_count / len(words)
        
        if navigation_ratio <= self.max_navigation_ratio:
            score = (1 - navigation_ratio) * 100
            return {
                'passed': True,
                'score': score,
                'weight': 15,
                'message': f'Baixa proporção de navegação: {navigation_ratio:.2%}',
                'value': navigation_ratio
            }
        else:
            score = max(0, (self.max_navigation_ratio - navigation_ratio) * 100)
            return {
                'passed': False,
                'score': score,
                'weight': 15,
                'message': f'Muitas palavras de navegação: {navigation_ratio:.2%}',
                'value': navigation_ratio
            }
    
    def _check_information_density(self, content: str) -> Dict[str, Any]:
        """Verifica densidade de informação"""
        words = content.lower().split()
        
        if len(words) == 0:
            return {
                'passed': False,
                'score': 0,
                'weight': 10,
                'message': 'Nenhuma palavra encontrada',
                'value': 0
            }
        
        # Conta palavras informativas
        info_count = sum(1 for word in words if word in self.quality_indicators)
        info_density = info_count / len(words)
        
        if info_density >= self.min_information_density:
            score = min(100, info_density * 1000)  # Amplifica score
            return {
                'passed': True,
                'score': score,
                'weight': 10,
                'message': f'Boa densidade de informação: {info_density:.2%}',
                'value': info_density
            }
        else:
            score = (info_density / self.min_information_density) * 100
            return {
                'passed': False,
                'score': score,
                'weight': 10,
                'message': f'Baixa densidade de informação: {info_density:.2%}',
                'value': info_density
            }
    
    def _check_language(self, content: str) -> Dict[str, Any]:
        """Verifica se o conteúdo está em português"""
        # Palavras comuns em português
        portuguese_words = [
            'que', 'não', 'uma', 'para', 'com', 'mais', 'como',
            'mas', 'foi', 'pelo', 'pela', 'até', 'isso', 'ela',
            'entre', 'depois', 'sem', 'mesmo', 'aos', 'seus',
            'quem', 'nas', 'me', 'esse', 'eles', 'você', 'tinha',
            'foram', 'essa', 'num', 'nem', 'suas', 'meu', 'às',
            'minha', 'numa', 'pelos', 'elas', 'qual', 'nós', 'deles'
        ]
        
        words = content.lower().split()
        
        if len(words) == 0:
            return {
                'passed': False,
                'score': 0,
                'weight': 5,
                'message': 'Nenhuma palavra encontrada',
                'value': 0
            }
        
        portuguese_count = sum(1 for word in words if word in portuguese_words)
        portuguese_ratio = portuguese_count / len(words)
        
        if portuguese_ratio >= 0.05:  # Pelo menos 5% de palavras em português
            score = min(100, portuguese_ratio * 500)
            return {
                'passed': True,
                'score': score,
                'weight': 5,
                'message': f'Conteúdo em português: {portuguese_ratio:.2%}',
                'value': portuguese_ratio
            }
        else:
            return {
                'passed': False,
                'score': portuguese_ratio * 500,
                'weight': 5,
                'message': f'Pouco conteúdo em português: {portuguese_ratio:.2%}',
                'value': portuguese_ratio
            }
    
    def _check_content_structure(self, content: str) -> Dict[str, Any]:
        """Verifica estrutura do conteúdo"""
        lines = content.split('\n')
        paragraphs = [line.strip() for line in lines if len(line.strip()) > 50]
        
        # Verifica se tem parágrafos substanciais
        if len(paragraphs) >= 3:
            score = min(100, len(paragraphs) * 10)
            return {
                'passed': True,
                'score': score,
                'weight': 10,
                'message': f'Boa estrutura: {len(paragraphs)} parágrafos',
                'value': len(paragraphs)
            }
        else:
            score = len(paragraphs) * 33
            return {
                'passed': False,
                'score': score,
                'weight': 10,
                'message': f'Estrutura pobre: {len(paragraphs)} parágrafos',
                'value': len(paragraphs)
            }
    
    def _check_relevance(self, content: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Verifica relevância do conteúdo para o contexto"""
        if not context:
            return {
                'passed': True,
                'score': 50,  # Score neutro sem contexto
                'weight': 10,
                'message': 'Sem contexto para verificar relevância',
                'value': 0
            }
        
        content_lower = content.lower()
        relevance_score = 0
        
        # Verifica termos do contexto
        context_terms = []
        
        if context.get('segmento'):
            context_terms.append(str(context['segmento']).lower())
        
        if context.get('produto'):
            context_terms.append(str(context['produto']).lower())
        
        if context.get('publico'):
            context_terms.append(str(context['publico']).lower())
        
        # Conta ocorrências dos termos
        for term in context_terms:
            if term and len(term) > 2:
                occurrences = content_lower.count(term)
                relevance_score += occurrences * 10
        
        # Normaliza score
        normalized_score = min(100, relevance_score)
        
        if normalized_score >= 20:
            return {
                'passed': True,
                'score': normalized_score,
                'weight': 10,
                'message': f'Conteúdo relevante: score {normalized_score}',
                'value': relevance_score
            }
        else:
            return {
                'passed': False,
                'score': normalized_score,
                'weight': 10,
                'message': f'Baixa relevância: score {normalized_score}',
                'value': relevance_score
            }
    
    def _get_content_stats(self, content: str) -> Dict[str, Any]:
        """Obtém estatísticas do conteúdo"""
        words = content.split()
        lines = content.split('\n')
        paragraphs = [line.strip() for line in lines if len(line.strip()) > 50]
        
        # Conta números e percentuais
        numbers = re.findall(r'\d+(?:\.\d+)?%?', content)
        
        # Conta valores monetários
        money_values = re.findall(r'R\$\s*[\d,\.]+', content)
        
        return {
            'character_count': len(content),
            'word_count': len(words),
            'line_count': len(lines),
            'paragraph_count': len(paragraphs),
            'number_count': len(numbers),
            'money_value_count': len(money_values),
            'avg_words_per_paragraph': len(words) / max(len(paragraphs), 1),
            'avg_chars_per_word': len(content) / max(len(words), 1)
        }
    
    def validate_batch(self, content_list: List[Dict[str, Any]], context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Valida múltiplos conteúdos em lote"""
        results = []
        
        for i, content_item in enumerate(content_list):
            content = content_item.get('content', '')
            url = content_item.get('url', f'item_{i}')
            
            validation = self.validate_content(content, url, context)
            validation['item_index'] = i
            results.append(validation)
        
        # Estatísticas do lote
        valid_count = sum(1 for r in results if r['valid'])
        total_count = len(results)
        avg_score = sum(r['score'] for r in results) / max(total_count, 1)
        
        return {
            'batch_results': results,
            'batch_stats': {
                'total_items': total_count,
                'valid_items': valid_count,
                'invalid_items': total_count - valid_count,
                'success_rate': (valid_count / max(total_count, 1)) * 100,
                'average_score': round(avg_score, 2)
            },
            'validated_at': datetime.now().isoformat()
        }
    
    def get_quality_report(self, validation_result: Dict[str, Any]) -> str:
        """Gera relatório de qualidade legível"""
        
        if not validation_result:
            return "❌ Nenhum resultado de validação fornecido"
        
        score = validation_result.get('score', 0)
        valid = validation_result.get('valid', False)
        details = validation_result.get('details', {})
        stats = validation_result.get('content_stats', {})
        
        report = []
        
        # Status geral
        status_icon = "✅" if valid else "❌"
        report.append(f"{status_icon} QUALIDADE: {score:.1f}% - {'VÁLIDO' if valid else 'INVÁLIDO'}")
        
        # Estatísticas básicas
        if stats:
            report.append(f"📊 ESTATÍSTICAS:")
            report.append(f"   • {stats.get('character_count', 0):,} caracteres")
            report.append(f"   • {stats.get('word_count', 0):,} palavras")
            report.append(f"   • {stats.get('paragraph_count', 0)} parágrafos")
        
        # Detalhes das verificações
        if details:
            report.append(f"🔍 VERIFICAÇÕES:")
            for check_name, result in details.items():
                icon = "✅" if result['passed'] else "❌"
                score_text = f"{result['score']:.1f}%"
                message = result['message']
                report.append(f"   {icon} {check_name}: {score_text} - {message}")
        
        return '\n'.join(report)

# Instância global
content_quality_validator = ContentQualityValidator()