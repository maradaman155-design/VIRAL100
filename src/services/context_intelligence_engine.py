
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ARQV30 Enhanced v2.0 - Context Intelligence Engine
Sistema pioneiro que REALMENTE entende o segmento e produto
"""

import logging
import json
import re
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from services.ai_manager import ai_manager

logger = logging.getLogger(__name__)

@dataclass
class SegmentIntelligence:
    """Inteligência extraída do segmento"""
    segment_type: str
    industry: str
    target_audience: str
    pain_points: List[str]
    desires: List[str]
    competition_level: str
    avg_price_range: str
    market_maturity: str
    psychological_triggers: List[str]
    common_objections: List[str]
    proof_concepts: List[str]

@dataclass
class ProductIntelligence:
    """Inteligência extraída do produto"""
    product_category: str
    delivery_method: str
    value_proposition: str
    transformation_promise: str
    implementation_complexity: str
    success_metrics: List[str]
    required_materials: List[str]
    time_to_results: str
    credibility_factors: List[str]

class ContextIntelligenceEngine:
    """Engine que entende REALMENTE o contexto do negócio"""
    
    def __init__(self):
        """Inicializa o engine"""
        self.segment_database = self._load_segment_knowledge()
        self.product_patterns = self._load_product_patterns()
        logger.info("🧠 Context Intelligence Engine inicializado")
    
    def analyze_context(self, segmento: str, produto: str = None) -> Dict[str, Any]:
        """Analisa profundamente o contexto do segmento e produto"""
        
        logger.info(f"🔍 Analisando contexto: {segmento} | {produto}")
        
        # 1. Extrai inteligência do segmento
        segment_intel = self._extract_segment_intelligence(segmento)
        
        # 2. Extrai inteligência do produto (se fornecido)
        product_intel = None
        if produto:
            product_intel = self._extract_product_intelligence(produto, segment_intel)
        
        # 3. Gera contexto unificado
        unified_context = self._generate_unified_context(segment_intel, product_intel)
        
        # 4. Valida e enriquece com IA
        enriched_context = self._enrich_with_ai(unified_context, segmento, produto)
        
        logger.info(f"✅ Contexto analisado: {len(enriched_context)} insights extraídos")
        
        return enriched_context
    
    def _extract_segment_intelligence(self, segmento: str) -> SegmentIntelligence:
        """Extrai inteligência profunda do segmento"""
        
        segmento_lower = segmento.lower()
        
        # Detecta tipo de segmento
        segment_type = self._detect_segment_type(segmento_lower)
        
        # Mapeia características conhecidas
        characteristics = self._map_segment_characteristics(segment_type, segmento_lower)
        
        return SegmentIntelligence(
            segment_type=segment_type,
            industry=characteristics.get('industry', 'Serviços'),
            target_audience=characteristics.get('target_audience', 'Empreendedores'),
            pain_points=characteristics.get('pain_points', []),
            desires=characteristics.get('desires', []),
            competition_level=characteristics.get('competition_level', 'Alta'),
            avg_price_range=characteristics.get('avg_price_range', 'R$ 100 - R$ 2.000'),
            market_maturity=characteristics.get('market_maturity', 'Maduro'),
            psychological_triggers=characteristics.get('psychological_triggers', []),
            common_objections=characteristics.get('common_objections', []),
            proof_concepts=characteristics.get('proof_concepts', [])
        )
    
    def _extract_product_intelligence(self, produto: str, segment_intel: SegmentIntelligence) -> ProductIntelligence:
        """Extrai inteligência específica do produto"""
        
        produto_lower = produto.lower()
        
        # Detecta categoria do produto
        product_category = self._detect_product_category(produto_lower)
        
        # Mapeia características do produto
        characteristics = self._map_product_characteristics(product_category, produto_lower, segment_intel)
        
        return ProductIntelligence(
            product_category=product_category,
            delivery_method=characteristics.get('delivery_method', 'Digital'),
            value_proposition=characteristics.get('value_proposition', ''),
            transformation_promise=characteristics.get('transformation_promise', ''),
            implementation_complexity=characteristics.get('implementation_complexity', 'Média'),
            success_metrics=characteristics.get('success_metrics', []),
            required_materials=characteristics.get('required_materials', []),
            time_to_results=characteristics.get('time_to_results', '30-90 dias'),
            credibility_factors=characteristics.get('credibility_factors', [])
        )
    
    def _detect_segment_type(self, segmento: str) -> str:
        """Detecta o tipo específico do segmento"""
        
        segment_patterns = {
            'infoprodutos': ['curso', 'ebook', 'treinamento', 'infoproduto', 'masterclass'],
            'coaching': ['coach', 'mentoria', 'consultoria', 'desenvolvimento pessoal'],
            'ecommerce': ['loja virtual', 'dropshipping', 'marketplace', 'vendas online'],
            'saas': ['software', 'app', 'plataforma', 'sistema', 'ferramenta digital'],
            'servicos_locais': ['clínica', 'escritório', 'prestação de serviços', 'atendimento local'],
            'afiliados': ['afiliado', 'marketing de afiliados', 'comissão', 'divulgação'],
            'financeiro': ['investimento', 'finanças', 'mercado financeiro', 'trader'],
            'saude_bem_estar': ['emagrecimento', 'fitness', 'saúde', 'bem-estar', 'beleza'],
            'relacionamentos': ['conquista', 'relacionamento', 'sedução', 'namoro'],
            'profissional': ['carreira', 'profissional', 'concurso', 'emprego', 'cv'],
            'tecnologia': ['programação', 'desenvolvimento', 'ti', 'tecnologia', 'software'],
            'marketing_vendas': ['marketing', 'vendas', 'digital', 'tráfego', 'conversão']
        }
        
        for segment_type, patterns in segment_patterns.items():
            if any(pattern in segmento for pattern in patterns):
                return segment_type
        
        return 'generico'
    
    def _detect_product_category(self, produto: str) -> str:
        """Detecta a categoria específica do produto"""
        
        product_patterns = {
            'curso_online': ['curso', 'treinamento', 'masterclass', 'formação'],
            'ebook': ['ebook', 'guia', 'manual', 'livro digital'],
            'consultoria': ['consultoria', 'mentoria', 'coaching', 'acompanhamento'],
            'software': ['software', 'app', 'aplicativo', 'sistema', 'ferramenta'],
            'produto_fisico': ['produto', 'item', 'equipamento', 'material'],
            'servico_recorrente': ['assinatura', 'mensal', 'recorrente', 'plano'],
            'evento': ['evento', 'workshop', 'palestra', 'encontro', 'congresso'],
            'certificacao': ['certificação', 'diploma', 'certificado', 'credencial']
        }
        
        for category, patterns in product_patterns.items():
            if any(pattern in produto for pattern in patterns):
                return category
        
        return 'generico'
    
    def _generate_unified_context(self, segment_intel: SegmentIntelligence, product_intel: ProductIntelligence = None) -> Dict[str, Any]:
        """Gera contexto unificado e inteligente"""
        
        context = {
            'segment_analysis': {
                'type': segment_intel.segment_type,
                'industry': segment_intel.industry,
                'target_audience': segment_intel.target_audience,
                'competition_level': segment_intel.competition_level,
                'market_maturity': segment_intel.market_maturity,
                'avg_price_range': segment_intel.avg_price_range
            },
            'psychological_profile': {
                'pain_points': segment_intel.pain_points,
                'desires': segment_intel.desires,
                'triggers': segment_intel.psychological_triggers,
                'common_objections': segment_intel.common_objections
            },
            'proof_strategy': {
                'concepts_to_prove': segment_intel.proof_concepts,
                'credibility_factors': product_intel.credibility_factors if product_intel else [],
                'success_metrics': product_intel.success_metrics if product_intel else []
            }
        }
        
        if product_intel:
            context['product_analysis'] = {
                'category': product_intel.product_category,
                'delivery_method': product_intel.delivery_method,
                'value_proposition': product_intel.value_proposition,
                'transformation_promise': product_intel.transformation_promise,
                'implementation_complexity': product_intel.implementation_complexity,
                'time_to_results': product_intel.time_to_results,
                'required_materials': product_intel.required_materials
            }
        
        return context
    
    def _enrich_with_ai(self, context: Dict[str, Any], segmento: str, produto: str = None) -> Dict[str, Any]:
        """Enriquece o contexto com inteligência artificial"""
        
        prompt = f"""
        Você é um especialista em análise de mercado. Analise profundamente este contexto de negócios e enriqueça com insights específicos e práticos:

        SEGMENTO: {segmento}
        PRODUTO: {produto or "Não especificado"}
        
        CONTEXTO ATUAL: {json.dumps(context, indent=2, ensure_ascii=False)}
        
        ENRIQUEÇA COM:
        1. Dores específicas REAIS deste segmento (não genéricas)
        2. Desejos profundos específicos 
        3. Objeções típicas REAIS deste mercado
        4. Conceitos que precisam ser PROVADOS visualmente
        5. Gatilhos psicológicos específicos
        6. Linguagem e vocabulário típicos do público
        7. Métricas de sucesso específicas
        8. Transformações prometidas típicas
        9. Timeline realista de resultados
        10. Fatores de credibilidade importantes

        Responda APENAS com um JSON válido com as chaves:
        - specific_pain_points
        - deep_desires
        - real_objections
        - proof_concepts
        - psychological_triggers
        - typical_language
        - success_metrics
        - transformation_promises
        - realistic_timeline
        - credibility_factors
        """
        
        try:
            ai_response = ai_manager.generate_text(prompt)
            
            # Extrai JSON da resposta
            json_match = re.search(r'\{.*\}', ai_response, re.DOTALL)
            if json_match:
                ai_insights = json.loads(json_match.group())
                
                # Merge com contexto existente
                context['ai_enriched'] = ai_insights
                context['enrichment_applied'] = True
                
                logger.info("✅ Contexto enriquecido com IA")
            else:
                logger.warning("⚠️ IA não retornou JSON válido")
                
        except Exception as e:
            logger.error(f"❌ Erro ao enriquecer com IA: {e}")
        
        return context
    
    def _load_segment_knowledge(self) -> Dict[str, Any]:
        """Carrega base de conhecimento sobre segmentos"""
        return {
            'infoprodutos': {
                'pain_points': [
                    'Não sabe como criar conteúdo de qualidade',
                    'Dificuldade para precificar produtos digitais',
                    'Não consegue gerar tráfego qualificado',
                    'Baixa taxa de conversão nas vendas',
                    'Não sabe como estruturar um lançamento'
                ],
                'desires': [
                    'Liberdade financeira vendendo conhecimento',
                    'Trabalhar de qualquer lugar',
                    'Ser reconhecido como autoridade',
                    'Ter renda passiva e recorrente',
                    'Impactar positivamente outras pessoas'
                ],
                'psychological_triggers': [
                    'Prova social com cases de sucesso',
                    'Escassez temporal em lançamentos',
                    'Autoridade através de expertise',
                    'Reciprocidade com conteúdo gratuito'
                ],
                'common_objections': [
                    'Não tenho conhecimento suficiente',
                    'Mercado está saturado',
                    'Não sei como divulgar',
                    'É muito caro investir',
                    'Pode não dar certo'
                ]
            },
            'coaching': {
                'pain_points': [
                    'Dificuldade para atrair clientes ideais',
                    'Não consegue cobrar o que vale',
                    'Falta de metodologia estruturada',
                    'Não sabe como demonstrar resultados',
                    'Insegurança sobre credibilidade'
                ],
                'desires': [
                    'Ter agenda sempre cheia',
                    'Ser reconhecido como especialista',
                    'Transformar vidas através do trabalho',
                    'Ter alta lucratividade por cliente',
                    'Construir legado profissional'
                ]
            }
            # Adicionar mais segmentos conforme necessário
        }
    
    def _load_product_patterns(self) -> Dict[str, Any]:
        """Carrega padrões conhecidos de produtos"""
        return {
            'curso_online': {
                'proof_concepts': [
                    'Metodologia comprovada',
                    'Resultados dos alunos',
                    'Qualidade do conteúdo',
                    'Suporte oferecido',
                    'Atualização constante'
                ]
            },
            'consultoria': {
                'proof_concepts': [
                    'Expertise do consultor',
                    'Cases de clientes',
                    'Metodologia proprietária',
                    'ROI demonstrável',
                    'Acompanhamento próximo'
                ]
            }
        }
    
    def _map_segment_characteristics(self, segment_type: str, segmento: str) -> Dict[str, Any]:
        """Mapeia características específicas do segmento"""
        
        base_characteristics = self.segment_database.get(segment_type, {})
        
        # Personaliza baseado no texto específico do segmento
        if 'avançado' in segmento or 'expert' in segmento:
            base_characteristics['avg_price_range'] = 'R$ 500 - R$ 5.000'
            base_characteristics['target_audience'] = 'Profissionais experientes'
        elif 'iniciante' in segmento or 'básico' in segmento:
            base_characteristics['avg_price_range'] = 'R$ 50 - R$ 500'
            base_characteristics['target_audience'] = 'Iniciantes'
        
        return base_characteristics
    
    def _map_product_characteristics(self, product_category: str, produto: str, segment_intel: SegmentIntelligence) -> Dict[str, Any]:
        """Mapeia características específicas do produto"""
        
        base_characteristics = self.product_patterns.get(product_category, {})
        
        # Personaliza baseado no contexto do segmento
        if segment_intel.segment_type == 'infoprodutos':
            if 'curso' in produto:
                base_characteristics['delivery_method'] = 'Plataforma de ensino'
                base_characteristics['time_to_results'] = '30-60 dias'
            elif 'ebook' in produto:
                base_characteristics['delivery_method'] = 'Download digital'
                base_characteristics['time_to_results'] = '7-14 dias'
        
        return base_characteristics

# Instância global
context_intelligence = ContextIntelligenceEngine()
