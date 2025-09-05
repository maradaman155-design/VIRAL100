#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ARQV30 Enhanced v2.0 - Visual Proofs Generator
Gerador de Provas Visuais Instantâneas
"""

import time
import random
import logging
import json
from typing import Dict, List, Any, Optional
from services.ai_manager import ai_manager
from services.auto_save_manager import salvar_etapa, salvar_erro

logger = logging.getLogger(__name__)

class VisualProofsGenerator:
    """Gerador de Provas Visuais Instantâneas"""

    def __init__(self):
        """Inicializa o gerador de provas visuais"""
        logger.info("Visual Proofs Generator inicializado")

    def generate_comprehensive_proofs(self, data: Dict[str, Any]) -> Dict[str, Any]:
        segmento = data.get('segmento', '')
        produto = data.get('produto', '')
        """Gera provas visuais abrangentes para o segmento"""
        try:
            logger.info(f"🎭 Gerando provas visuais para {segmento} - {produto}")

            from services.ai_manager import ai_manager

            prompt = f"""
Crie 3 provas visuais (PROVIs) poderosas para o segmento "{segmento}" com produto "{produto}".

Para cada PROVI, forneça:
1. Nome impactante
2. Conceito-alvo que vai provar
3. Categoria (Destruidora de Objeção, Criadora de Urgência, Instaladora de Crença)
4. Experimento/demonstração específica
5. Analogia perfeita
6. Roteiro completo de execução
7. Materiais necessários

Formato JSON:
{{
    "provis": [
        {{
            "nome": "PROVI 1: Nome Impactante",
            "conceito_alvo": "O que vai provar",
            "categoria": "Tipo de prova",
            "prioridade": "Crítica/Alta/Média",
            "objetivo_psicologico": "Efeito na mente",
            "experimento": "Demonstração específica",
            "analogia_perfeita": "Assim como...",
            "roteiro_completo": {{
                "setup": "Como preparar",
                "execucao": "Como executar",
                "climax": "Momento de maior impacto",
                "bridge": "Como conectar ao produto"
            }},
            "materiais": ["item1", "item2"],
            "variacoes": {{
                "online": "Versão online",
                "grande_publico": "Para muitas pessoas",
                "intimista": "Para grupos pequenos"
            }},
            "plano_b": "O que fazer se der errado"
        }}
    ]
}}
"""

            response = ai_manager.generate_content(prompt, max_tokens=3000)
            if response:
                import json
                try:
                    provis_data = json.loads(response)
                    return provis_data.get('provis', [])
                except:
                    return self._create_fallback_provis(segmento, produto)
            else:
                return self._create_fallback_provis(segmento, produto)

        except Exception as e:
            logger.error(f"❌ Erro ao gerar provas visuais: {e}")
            return self._create_fallback_provis(segmento, produto)

    def _create_fallback_provis(self, segmento, produto):
        """Cria PROVIs de fallback quando IA falha"""
        return [
            {
                "nome": f"PROVI 1: Demonstração {produto}",
                "conceito_alvo": f"Provar que {produto} realmente funciona",
                "categoria": "Destruidora de Objeção",
                "prioridade": "Crítica",
                "objetivo_psicologico": f"Quebrar ceticismo sobre {produto}",
                "experimento": f"Demonstração prática de {produto}",
                "analogia_perfeita": f"Assim como você pode ver {produto} funcionando, você pode ter os mesmos resultados",
                "roteiro_completo": {
                    "setup": f"Prepare exemplo de {produto}",
                    "execucao": f"Mostre {produto} em ação",
                    "climax": "Revele o resultado final",
                    "bridge": f"Conecte ao potencial da audiência com {produto}"
                },
                "materiais": [f"Exemplo de {produto}", "Material de demonstração"],
                "variacoes": {
                    "online": "Versão digital da demonstração",
                    "grande_publico": "Demonstração ampliada",
                    "intimista": "Demonstração personalizada"
                },
                "plano_b": "Ter exemplo backup preparado"
            }
        ]


    def _load_proof_types(self) -> Dict[str, Dict[str, Any]]:
        """Carrega tipos de provas visuais"""
        return {
            'antes_depois': {
                'nome': 'Transformação Antes/Depois',
                'objetivo': 'Mostrar transformação clara e mensurável',
                'impacto': 'Alto',
                'facilidade': 'Média'
            },
            'comparacao_competitiva': {
                'nome': 'Comparação vs Concorrência',
                'objetivo': 'Demonstrar superioridade clara',
                'impacto': 'Alto',
                'facilidade': 'Alta'
            },
            'timeline_resultados': {
                'nome': 'Timeline de Resultados',
                'objetivo': 'Mostrar progressão temporal',
                'impacto': 'Médio',
                'facilidade': 'Alta'
            },
            'social_proof_visual': {
                'nome': 'Prova Social Visual',
                'objetivo': 'Validação através de terceiros',
                'impacto': 'Alto',
                'facilidade': 'Média'
            },
            'demonstracao_processo': {
                'nome': 'Demonstração do Processo',
                'objetivo': 'Mostrar como funciona na prática',
                'impacto': 'Médio',
                'facilidade': 'Baixa'
            }
        }

    def _load_visual_elements(self) -> Dict[str, List[str]]:
        """Carrega elementos visuais disponíveis"""
        return {
            'graficos': ['Barras', 'Linhas', 'Pizza', 'Área', 'Dispersão'],
            'comparacoes': ['Lado a lado', 'Sobreposição', 'Timeline', 'Tabela'],
            'depoimentos': ['Vídeo', 'Texto', 'Áudio', 'Screenshot'],
            'demonstracoes': ['Screencast', 'Fotos', 'Infográfico', 'Animação'],
            'dados': ['Números', 'Percentuais', 'Valores', 'Métricas']
        }

    def generate_complete_proofs_system(
        self, 
        concepts_to_prove: List[str], 
        avatar_data: Dict[str, Any], 
        context_data: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Gera sistema completo de provas visuais"""

        # Validação crítica de entrada
        if not concepts_to_prove:
            logger.error("❌ Nenhum conceito para provar")
            raise ValueError("PROVAS VISUAIS FALHARAM: Nenhum conceito fornecido")

        if not context_data.get('segmento'):
            logger.error("❌ Segmento não informado")
            raise ValueError("PROVAS VISUAIS FALHARAM: Segmento obrigatório")

        try:
            logger.info(f"🎭 Gerando provas visuais para {len(concepts_to_prove)} conceitos")

            # Salva dados de entrada imediatamente
            salvar_etapa("provas_entrada", {
                "concepts_to_prove": concepts_to_prove,
                "avatar_data": avatar_data,
                "context_data": context_data
            }, categoria="provas_visuais")

            # Seleciona conceitos mais importantes
            priority_concepts = self._prioritize_concepts(concepts_to_prove, avatar_data)

            # Gera provas visuais para cada conceito
            visual_proofs = []

            for i, concept in enumerate(priority_concepts[:8]):  # Máximo 8 provas
                try:
                    proof = self._generate_visual_proof_for_concept(concept, avatar_data, context_data, i+1)
                    if proof:
                        visual_proofs.append(proof)
                        # Salva cada prova gerada
                        salvar_etapa(f"prova_{i+1}", proof, categoria="provas_visuais")
                except Exception as e:
                    logger.error(f"❌ Erro ao gerar prova para conceito '{concept}': {e}")
                    continue

            if not visual_proofs:
                logger.error("❌ Nenhuma prova visual gerada")
                # Usa provas padrão em vez de falhar
                logger.warning("🔄 Usando provas visuais padrão")
                visual_proofs = self._get_default_visual_proofs(context_data)

            # Salva provas visuais finais
            salvar_etapa("provas_finais", visual_proofs, categoria="provas_visuais")

            logger.info(f"✅ {len(visual_proofs)} provas visuais geradas com sucesso")
            return visual_proofs

        except Exception as e:
            logger.error(f"❌ Erro ao gerar provas visuais: {str(e)}")
            salvar_erro("provas_sistema", e, contexto={"segmento": context_data.get('segmento')})

            # Fallback para provas básicas
            logger.warning("🔄 Gerando provas visuais básicas como fallback...")
            return self._get_default_visual_proofs(context_data)

    def _prioritize_concepts(self, concepts: List[str], avatar_data: Dict[str, Any]) -> List[str]:
        """Prioriza conceitos baseado no avatar"""

        # Dores têm prioridade alta
        dores = avatar_data.get('dores_viscerais', [])
        desejos = avatar_data.get('desejos_secretos', [])

        prioritized = []

        # Adiciona dores primeiro
        for concept in concepts:
            if any(concept.lower() in dor.lower() for dor in dores):
                prioritized.append(concept)

        # Adiciona desejos
        for concept in concepts:
            if concept not in prioritized and any(concept.lower() in desejo.lower() for desejo in desejos):
                prioritized.append(concept)

        # Adiciona conceitos restantes
        for concept in concepts:
            if concept not in prioritized:
                prioritized.append(concept)

        return prioritized

    def _generate_visual_proof_for_concept(
        self, 
        concept: str, 
        avatar_data: Dict[str, Any], 
        context_data: Dict[str, Any],
        proof_number: int
    ) -> Optional[Dict[str, Any]]:
        """Gera prova visual para um conceito específico"""

        try:
            segmento = context_data.get('segmento', 'negócios')

            # Seleciona tipo de prova mais adequado
            proof_type = self._select_best_proof_type(concept, avatar_data)

            # Gera prova usando IA
            prompt = f"""
Crie uma prova visual específica para o conceito: "{concept}"

SEGMENTO: {segmento}
TIPO DE PROVA: {proof_type['nome']}
OBJETIVO: {proof_type['objetivo']}

RETORNE APENAS JSON VÁLIDO:

```json
{{
  "nome": "PROVI {proof_number}: Nome específico da prova",
  "conceito_alvo": "{concept}",
  "tipo_prova": "{proof_type['nome']}",
  "experimento": "Descrição detalhada do experimento visual",
  "materiais": [
    "Material 1 específico",
    "Material 2 específico",
    "Material 3 específico"
  ],
  "roteiro_completo": {{
    "preparacao": "Como preparar a prova",
    "execucao": "Como executar a demonstração",
    "impacto_esperado": "Qual reação esperar"
  }},
  "metricas_sucesso": [
    "Métrica 1 de sucesso",
    "Métrica 2 de sucesso"
  ]
}}
"""

            response = ai_manager.generate_analysis(prompt, max_tokens=800)

            if response:
                clean_response = response.strip()
                if "```json" in clean_response:
                    start = clean_response.find("```json") + 7
                    end = clean_response.rfind("```")
                    clean_response = clean_response[start:end].strip()

                try:
                    proof = json.loads(clean_response)
                    logger.info(f"✅ Prova visual {proof_number} gerada com IA")
                    return proof
                except json.JSONDecodeError:
                    logger.warning(f"⚠️ IA retornou JSON inválido para prova {proof_number}")

            # Fallback para prova básica
            return self._create_basic_proof(concept, proof_type, proof_number, context_data)

        except Exception as e:
            logger.error(f"❌ Erro ao gerar prova visual: {str(e)}")
            return self._create_basic_proof(concept, proof_type, proof_number, context_data)

    def _select_best_proof_type(self, concept: str, avatar_data: Dict[str, Any]) -> Dict[str, Any]:
        """Seleciona melhor tipo de prova para o conceito"""

        concept_lower = concept.lower()

        # Mapeia conceitos para tipos de prova
        if any(word in concept_lower for word in ['resultado', 'crescimento', 'melhoria']):
            return self.proof_types['antes_depois']
        elif any(word in concept_lower for word in ['concorrente', 'melhor', 'superior']):
            return self.proof_types['comparacao_competitiva']
        elif any(word in concept_lower for word in ['tempo', 'rapidez', 'velocidade']):
            return self.proof_types['timeline_resultados']
        elif any(word in concept_lower for word in ['outros', 'clientes', 'pessoas']):
            return self.proof_types['social_proof_visual']
        else:
            return self.proof_types['demonstracao_processo']

    def _create_basic_proof(
        self, 
        concept: str, 
        proof_type: Dict[str, Any], 
        proof_number: int, 
        context_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Cria prova visual básica"""

        segmento = context_data.get('segmento', 'negócios')

        return {
            'nome': f'PROVI {proof_number}: {proof_type["nome"]} para {segmento}',
            'conceito_alvo': concept,
            'tipo_prova': proof_type['nome'],
            'experimento': f'Demonstração visual do conceito "{concept}" através de {proof_type["nome"].lower()} específica para {segmento}',
            'materiais': [
                'Gráficos comparativos',
                'Dados numéricos',
                'Screenshots de resultados',
                'Depoimentos visuais'
            ],
            'roteiro_completo': {
                'preparacao': f'Prepare materiais visuais que demonstrem {concept} no contexto de {segmento}',
                'execucao': f'Apresente a prova visual de forma clara e impactante',
                'impacto_esperado': 'Redução de ceticismo e aumento de confiança'
            },
            'metricas_sucesso': [
                'Redução de objeções relacionadas ao conceito',
                'Aumento de interesse e engajamento',
                'Aceleração do processo de decisão'
            ],
            'fallback_mode': True
        }

    def _get_default_visual_proofs(self, context_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Retorna provas visuais padrão como fallback"""

        segmento = context_data.get('segmento', 'negócios')

        return [
            {
                'nome': f'PROVI 1: Resultados Comprovados em {segmento}',
                'conceito_alvo': f'Eficácia da metodologia em {segmento}',
                'tipo_prova': 'Antes/Depois',
                'experimento': f'Comparação visual de resultados antes e depois da aplicação da metodologia em {segmento}',
                'materiais': ['Gráficos de crescimento', 'Dados de performance', 'Screenshots de métricas'],
                'roteiro_completo': {
                    'preparacao': 'Organize dados de clientes que aplicaram a metodologia',
                    'execucao': 'Mostre transformação clara com números específicos',
                    'impacto_esperado': 'Convencimento através de evidência visual'
                },
                'metricas_sucesso': ['Redução de ceticismo', 'Aumento de interesse']
            },
            {
                'nome': f'PROVI 2: Comparação com Mercado em {segmento}',
                'conceito_alvo': f'Superioridade da abordagem em {segmento}',
                'tipo_prova': 'Comparação Competitiva',
                'experimento': f'Comparação visual entre abordagem tradicional e metodologia específica para {segmento}',
                'materiais': ['Tabelas comparativas', 'Gráficos de performance', 'Benchmarks do setor'],
                'roteiro_completo': {
                    'preparacao': 'Colete dados de mercado e benchmarks',
                    'execucao': 'Apresente comparação lado a lado',
                    'impacto_esperado': 'Demonstração clara de vantagem competitiva'
                },
                'metricas_sucesso': ['Compreensão do diferencial', 'Justificativa de preço premium']
            },
            {
                'nome': f'PROVI 3: Depoimentos Visuais {segmento}',
                'conceito_alvo': f'Validação social no {segmento}',
                'tipo_prova': 'Prova Social Visual',
                'experimento': f'Compilação visual de depoimentos de profissionais de {segmento}',
                'materiais': ['Vídeos de depoimento', 'Screenshots de resultados', 'Fotos de clientes'],
                'roteiro_completo': {
                    'preparacao': 'Selecione melhores depoimentos com resultados',
                    'execucao': 'Apresente sequência de validações sociais',
                    'impacto_esperado': 'Redução de risco percebido'
                },
                'metricas_sucesso': ['Aumento de confiança', 'Redução de objeções']
            }
        ]

# Instância global
visual_proofs_generator = VisualProofsGenerator()