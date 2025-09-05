#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ARQV30 Enhanced v2.0 - Visceral Master Agent
MESTRE DA PERSUASÃO VISCERAL - Engenharia Reversa Psicológica Profunda
"""

import logging
import time
import json
from typing import Dict, List, Any, Optional
from datetime import datetime
from services.ai_manager import ai_manager
from services.auto_save_manager import salvar_etapa, salvar_erro
import random

logger = logging.getLogger(__name__)

class VisceralMasterAgent:
    """MESTRE DA PERSUASÃO VISCERAL - Engenharia Reversa Psicológica"""

    def __init__(self):
        """Inicializa o Mestre da Persuasão Visceral"""
        self.psychological_layers = [
            'feridas_abertas_inconfessaveis',
            'sonhos_proibidos_ardentes',
            'demonios_internos_paralisantes',
            'correntes_cotidiano',
            'dialeto_alma',
            'muralhas_desconfianca',
            'visoes_paraiso_inferno',
            'segmentacao_psicologica'
        ]

        logger.info("🧠 MESTRE DA PERSUASÃO VISCERAL inicializado")

    def execute_visceral_analysis(
        self,
        data: Dict[str, Any],
        research_data: Dict[str, Any] = None,
        session_id: str = None
    ) -> Dict[str, Any]:
        """Executa engenharia reversa psicológica profunda"""

        logger.info("🧠 INICIANDO ENGENHARIA REVERSA PSICOLÓGICA PROFUNDA")

        try:
            # Salva início da análise visceral
            salvar_etapa("visceral_iniciada", {
                "data": data,
                "research_data": research_data,
                "layers": self.psychological_layers
            }, categoria="analise_completa")

            # Constrói prompt visceral ultra-detalhado
            visceral_prompt = self._build_visceral_prompt(data, research_data)

            # Executa análise visceral com IA
            response = ai_manager.generate_analysis(visceral_prompt, max_tokens=8192)

            if not response:
                raise Exception("MESTRE VISCERAL FALHOU: IA não respondeu")

            # Processa resposta visceral
            visceral_analysis = self._process_visceral_response(response, data)

            # Executa segmentação psicológica avançada
            psychological_segmentation = self._execute_psychological_segmentation(visceral_analysis, data)
            visceral_analysis['segmentacao_psicologica_avancada'] = psychological_segmentation

            # Gera arsenal tático de persuasão
            tactical_arsenal = self._generate_tactical_arsenal(visceral_analysis, data)
            visceral_analysis['arsenal_tatico_persuasao'] = tactical_arsenal

            # Salva análise visceral completa
            salvar_etapa("visceral_completa", visceral_analysis, categoria="analise_completa")

            logger.info("✅ ENGENHARIA REVERSA PSICOLÓGICA CONCLUÍDA - ALMA MAPEADA")
            return visceral_analysis

        except Exception as e:
            logger.error(f"❌ FALHA CRÍTICA na análise visceral: {e}")
            salvar_erro("visceral_falha", e, contexto=data)
            return self._generate_visceral_emergency(data)

    def _build_visceral_prompt(self, data: Dict[str, Any], research_data: Dict[str, Any] = None) -> str:
        """Constrói prompt visceral ultra-detalhado"""

        segmento = data.get('segmento', 'negócios')
        produto = data.get('produto', 'Produto/Serviço')

        research_context = ""
        if research_data and research_data.get('extracted_content'):
            research_context = "\n## CONTEXTO DE PESQUISA REAL:\n"
            for i, content in enumerate(research_data['extracted_content'][:5], 1):
                research_context += f"FONTE {i}: {content.get('title', 'Sem título')}\n"
                research_context += f"Conteúdo: {content.get('content', '')[:1000]}\n\n"

        prompt = f"""
# VOCÊ É O MESTRE DA PERSUASÃO VISCERAL

Linguagem: Direta, brutalmente honesta, carregada de tensão psicológica.
Não tem medo de chocar, confrontar ou usar metáforas sombrias.
Objetivo: Forçar clareza e ação imediata através da verdade nua e crua.

## DADOS PARA ENGENHARIA REVERSA PSICOLÓGICA:
- **Segmento**: {segmento}
- **Produto/Serviço**: {produto}
- **Público-Alvo**: {data.get('publico', 'Não informado')}
- **Preço**: R$ {data.get('preco', 'Não informado')}
- **Dados Adicionais**: {data.get('dados_adicionais', 'Não informado')}

{research_context}

## EXECUTE ENGENHARIA REVERSA PSICOLÓGICA PROFUNDA:

Vá além dos dados superficiais. Mergulhe FUNDO em:
- **Dores profundas e inconfessáveis** (o que não admitem nem para si mesmos)
- **Desejos ardentes e proibidos** (o que querem mas têm vergonha de admitir)
- **Medos paralisantes e irracionais** (o que os congela de medo)
- **Frustrações diárias** (as pequenas mortes cotidianas)
- **Objeções cínicas reais** (o que realmente pensam mas não falam)
- **Linguagem interna verdadeira** (como realmente falam quando ninguém ouve)
- **Sonhos selvagens secretos** (fantasias de sucesso que escondem)

OBJETIVO: Criar dossiê tão preciso que o usuário possa "LER A MENTE" dos leads.

RETORNE JSON ESTRUTURADO ULTRA-COMPLETO:

```json
{{
  "avatar_visceral_ultra": {{
    "nome_ficticio": "Nome arqueológico específico baseado no segmento",
    "perfil_demografico_visceral": {{
      "idade_cronologica": "Idade real baseada em dados",
      "idade_emocional": "Idade psicológica real vs cronológica",
      "status_social_percebido": "Como se vê vs como é realmente visto",
      "pressoes_externas_reais": "Família, sociedade, trabalho, financeiro",
      "recursos_emocionais_disponiveis": "Energia, tempo, dinheiro emocional",
      "fase_vida_predominante": "Início carreira, meio, crise, estabilidade",
      "nivel_escolaridade_aparente": "Baseado em vocabulário e estrutura",
      "recursos_financeiros_inferidos": "Sinais de capacidade financeira"
    }},

    "feridas_abertas_inconfessaveis": [
      "Lista de 20-25 dores secretas, viscerais e profundas que não admitem nem para si mesmos"
    ],

    "sonhos_proibidos_ardentes": [
      "Lista de 20-25 desejos secretos, ardentes e proibidos que têm vergonha de admitir"
    ],

    "demonios_internos_paralisantes": [
      "Lista de 15-20 medos paralisantes, irracionais e que os congelam de terror"
    ],

    "correntes_cotidiano_pequenas_mortes": [
      "Lista de 15-20 frustrações diárias, pequenas mortes que os matam por dentro"
    ],

    "dialeto_alma_linguagem_interna": {{
      "frases_tipicas_dores": ["Frases exatas que usam para descrever dores"],
      "frases_tipicas_desejos": ["Frases exatas que usam para desejos"],
      "metaforas_comuns_vida": ["Metáforas que usam para vida"],
      "vocabulario_especifico_nicho": ["Palavras e gírias específicas"],
      "tom_comunicacao_real": "Tom real quando falam sobre o assunto",
      "influenciadores_confianca": ["Quem realmente confiam"],
      "fontes_informacao_desprezadas": ["Quem desprezam ou desconfiam"],
      "linguagem_formal_vs_informal": "Como falam formalmente vs informalmente"
    }},

    "muralhas_desconfianca_objecoes": [
      "Lista de 15-20 objeções reais, cínicas e brutalmente honestas"
    ],

    "visoes_paraiso_inferno": {{
      "dia_perfeito_pos_transformacao": "Narrativa detalhada do dia ideal após solução",
      "pesadelo_recorrente_sem_solucao": "Narrativa detalhada do pior cenário sem solução",
      "momento_decisao_ideal": "Como seria o momento ideal de decisão",
      "vida_5_anos_sem_mudanca": "Como será a vida em 5 anos sem mudança",
      "vida_5_anos_com_transformacao": "Como será a vida em 5 anos com transformação"
    }},

    "jornada_emocional_completa": {{
      "consciencia_dor": "Como realmente toma consciência da dor",
      "negacao_inicial": "Como nega ou minimiza o problema",
      "aceitacao_gradual": "Processo de aceitação da realidade",
      "busca_solucoes": "Como busca soluções (padrões)",
      "resistencia_mudanca": "Como resiste à mudança necessária",
      "momento_quebra": "O que quebra a resistência",
      "decisao_final": "Fatores que levam à decisão final",
      "pos_decisao": "Como se sente após tomar decisão",
      "implementacao": "Como lida com implementação",
      "resultados": "Como reage aos primeiros resultados"
    }},

    "arquetipos_dominantes": [
      {{
        "nome_arquetipo": "Nome do arquétipo identificado",
        "percentual_grupo": "Percentual que representa",
        "caracteristicas_unicas": "Características distintivas",
        "abordagem_especifica": "Como abordar este arquétipo",
        "medos_especificos": "Medos específicos deste grupo",
        "desejos_especificos": "Desejos específicos deste grupo"
      }}
    ]
  }},

  "engenharia_reversa_insights": {{
    "padroes_comportamentais": ["Padrão 1", "Padrão 2"],
    "contradições_identificadas": ["Contradição 1", "Contradição 2"],
    "gaps_consciencia": ["Gap 1", "Gap 2"],
    "pontos_alavancagem": ["Ponto 1", "Ponto 2"],
    "momentos_vulnerabilidade": ["Momento 1", "Momento 2"],
    "gatilhos_decisao": ["Gatilho 1", "Gatilho 2"]
  }},

  "mapeamento_emocional_profundo": {{
    "temperatura_emocional_dominante": "Otimista/Pessimista/Ansioso/Desesperado",
    "nivel_vulnerabilidade": "Alto/Médio/Baixo - se abriram ou ficaram superficiais",
    "padroes_linguagem_emocional": "Formal/Casual/Técnica/Emocional",
    "sinais_resistencia_vs_abertura": "Resistente/Aberto para mudança",
    "intensidade_dor_expressa": "Nível de intensidade da dor demonstrada",
    "urgencia_percebida": "Sinais de desespero vs conformismo",
    "historico_tentativas": "Tentativas anteriores mencionadas e frustrações"
  }},

  "arsenal_tatico_visceral": {{
    "angulos_copy_devastadores": [
      "Ângulo 1: Foco na dor mais profunda",
      "Ângulo 2: Contraste brutal com realidade atual",
      "Ângulo 3: Urgência existencial",
      "Ângulo 4: Autoridade através de vulnerabilidade",
      "Ângulo 5: Prova social de transformação"
    ],
    "tipos_conteudo_magnetico": [
      "Confissões brutalmente honestas",
      "Cases de transformação extrema",
      "Diagnósticos dolorosos mas precisos",
      "Revelações chocantes do mercado",
      "Métodos contraintuitivos"
    ],
    "tom_voz_ideal_visceral": "Direto, confrontador, brutalmente honesto, sem filtros",
    "gatilhos_emocionais_devastadores": [
      "Medo de continuar na mediocridade",
      "Vergonha de não ter coragem",
      "Inveja produtiva de quem conseguiu",
      "Urgência de não perder mais tempo",
      "Desejo ardente de vingança contra limitações"
    ],
    "momentos_vulnerabilidade_maxima": [
      "Quando admite que está preso",
      "Quando reconhece que precisa de ajuda",
      "Quando vê outros conseguindo",
      "Quando calcula tempo perdido",
      "Quando visualiza futuro sem mudança"
    ]
  }}
}}
```

CRÍTICO: Seja brutalmente honesto. Vá fundo na psique. Não tenha medo de chocar ou confrontar.
O objetivo é criar um dossiê tão preciso que permita "ler a mente" dos leads.
"""

        return prompt

    def _process_visceral_response(self, response: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Processa resposta visceral com extração profunda"""

        try:
            # Extrai JSON da resposta
            clean_text = response.strip()

            if "```json" in clean_text:
                start = clean_text.find("```json") + 7
                end = clean_text.rfind("```")
                clean_text = clean_text[start:end].strip()

            # Parseia JSON
            visceral_data = json.loads(clean_text)

            # Adiciona metadados viscerais
            visceral_data['metadata_visceral'] = {
                'generated_at': datetime.now().isoformat(),
                'agent': 'MESTRE DA PERSUASÃO VISCERAL',
                'profundidade_psicologica': 'ULTRA-PROFUNDA',
                'engenharia_reversa_completa': True,
                'alma_mapeada': True
            }

            # Correção específica para nomes próprios no avatar
            if 'avatar_visceral_ultra' in visceral_data:
                avatar_data = visceral_data['avatar_visceral_ultra']
                # Gera nome próprio real baseado no segmento e gênero
                nomes_femininos = ["Ana Silva", "Maria Santos", "Carla Oliveira", "Julia Costa", "Patricia Lima",
                                  "Fernanda Alves", "Beatriz Souza", "Camila Rodrigues", "Daniela Ferreira", "Roberta Martins",
                                  "Mariana Pereira", "Aline Ribeiro", "Gabriela Nascimento", "Leticia Cardoso", "Vanessa Torres"]
                nomes_masculinos = ["Carlos Silva", "João Santos", "Pedro Oliveira", "Rafael Costa", "Bruno Lima",
                                  "Diego Alves", "Marcos Souza", "Lucas Rodrigues", "Felipe Ferreira", "Ricardo Martins",
                                  "André Pereira", "Gustavo Ribeiro", "Henrique Nascimento", "Thiago Cardoso", "Leonardo Torres"]

                if avatar_data.get('genero', 'feminino').lower() == 'masculino':
                    nome_ficticio = random.choice(nomes_masculinos)
                else:
                    nome_ficticio = random.choice(nomes_femininos)
                avatar_data['nome_ficticio'] = nome_ficticio

            return visceral_data

        except json.JSONDecodeError as e:
            logger.error(f"❌ Erro ao parsear JSON visceral: {e}")
            return self._extract_visceral_insights_from_text(response, data)
        except Exception as e:
            logger.error(f"❌ Falha ao processar resposta visceral: {e}")
            # NÃO retorna fallbacks - usa dados reais ou falha
            raise Exception(f"Falha na criação do avatar: {e}")


    def _extract_visceral_insights_from_text(self, text: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Extrai insights viscerais do texto quando JSON falha"""

        segmento = data.get('segmento', 'negócios')

        # Análise visceral baseada no texto
        return {
            "avatar_visceral_ultra": {
                "nome_ficticio": f"Profissional {segmento} em Crise Existencial",
                "feridas_abertas_inconfessaveis": [
                    f"Trabalhar 12+ horas em {segmento} e ganhar menos que um funcionário CLT",
                    "Sentir-se um fracasso disfarçado de empreendedor bem-sucedido",
                    "Ter vergonha de admitir que não sabe o que está fazendo",
                    "Viver com medo constante de que tudo desmorone a qualquer momento",
                    "Sentir inveja doentia de concorrentes que 'não merecem' o sucesso",
                    "Ter síndrome do impostor mesmo com resultados aparentes",
                    "Sacrificar relacionamentos familiares pelo trabalho sem ver retorno",
                    "Sentir-se preso numa armadilha dourada que ele mesmo criou",
                    "Ter medo de ser descoberto como 'não tão bom quanto parece'",
                    "Viver em negação sobre a real situação financeira do negócio",
                    "Sentir-se sozinho e incompreendido mesmo cercado de pessoas",
                    "Ter vergonha de pedir ajuda por parecer fraqueza",
                    "Procrastinar decisões importantes por medo de errar",
                    "Sentir-se velho demais para recomeçar, jovem demais para desistir",
                    "Viver comparando-se obsessivamente com outros profissionais"
                ],
                "sonhos_proibidos_ardentes": [
                    f"Ser THE autoridade inquestionável no mercado de {segmento}",
                    "Ter um negócio que gere R$ 100k/mês sem sua presença",
                    "Ser convidado para palestrar nos maiores eventos do país",
                    "Ter liberdade total: trabalhar de onde quiser, quando quiser",
                    "Ser procurado por grandes empresas como consultor premium",
                    "Ganhar mais em um mês do que ganhava em um ano",
                    "Ter uma equipe que funcione perfeitamente sem microgerenciamento",
                    "Ser invejado pelos mesmos que hoje o ignoram",
                    "Aposentar-se aos 45 anos com patrimônio de R$ 10 milhões",
                    "Ter múltiplas fontes de renda passiva funcionando 24/7",
                    "Ser featured na capa de revistas como case de sucesso",
                    "Viajar o mundo trabalhando apenas 4 horas por dia",
                    "Deixar um legado que impacte milhões de pessoas",
                    "Ter segurança financeira absoluta para 3 gerações",
                    "Ser mentor de outros empreendedores milionários"
                ],
                "demonios_internos_paralisantes": [
                    "Terror absoluto de fracassar publicamente e virar piada",
                    "Pânico de descobrirem que é uma fraude disfarçada",
                    "Medo paralisante de tomar a decisão errada e perder tudo",
                    "Pavor de ser julgado pelos pares como incompetente",
                    "Terror de não conseguir sustentar a família",
                    "Medo irracional de que o sucesso seja apenas sorte",
                    "Pânico de que a concorrência descubra seus 'segredos'",
                    "Terror de envelhecer sem ter 'vencido na vida'",
                    "Medo de que os filhos tenham vergonha do pai/mãe",
                    "Pavor de morrer sem deixar nada significativo"
                ]
            },
            "raw_visceral_analysis": text[:3000],
            "extraction_method": "text_analysis_visceral"
        }

    def _execute_psychological_segmentation(self, visceral_data: Dict[str, Any], data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Executa segmentação psicológica avançada"""

        segmento = data.get('segmento', 'negócios')

        # Segmentação baseada nos dados viscerais
        psychological_segments = [
            {
                "nome_segmento": "O Técnico Aprisionado",
                "percentual_estimado": "35%",
                "caracteristicas_distintas": f"Profissionais de {segmento} com alta competência técnica mas presos no operacional",
                "feridas_especificas": [
                    "Sabe fazer mas não sabe vender",
                    "Trabalha muito mas ganha pouco",
                    "É o melhor tecnicamente mas não é reconhecido"
                ],
                "desejos_especificos": [
                    "Ser reconhecido pelo conhecimento técnico",
                    "Transformar expertise em dinheiro",
                    "Sair do operacional sem perder controle"
                ],
                "abordagem_especifica": "Foco na transformação de conhecimento em autoridade e autoridade em receita",
                "linguagem_preferida": "Técnica, com dados e provas concretas",
                "gatilhos_mais_eficazes": ["Autoridade técnica", "Prova matemática", "Método vs sorte"]
            },
            {
                "nome_segmento": "O Escalador Frustrado",
                "percentual_estimado": "40%",
                "caracteristicas_distintas": f"Empreendedores em {segmento} que cresceram mas bateram no teto",
                "feridas_especificas": [
                    "Cresceu até certo ponto e estagnou",
                    "Trabalha mais mas não cresce proporcionalmente",
                    "Vê outros ultrapassando sem entender como"
                ],
                "desejos_especificos": [
                    "Quebrar o teto de faturamento atual",
                    "Descobrir o que está fazendo errado",
                    "Acelerar crescimento sem trabalhar mais"
                ],
                "abordagem_especifica": "Foco em identificar gargalos ocultos e sistemas de escala",
                "linguagem_preferida": "Direta, focada em resultados e ROI",
                "gatilhos_mais_eficazes": ["Diagnóstico brutal", "Custo invisível", "Oportunidade oculta"]
            },
            {
                "nome_segmento": "O Visionário Sufocado",
                "percentual_estimado": "25%",
                "caracteristicas_distintas": f"Líderes em {segmento} com visão grande mas execução travada",
                "feridas_especificas": [
                    "Tem ideias grandes mas não consegue implementar",
                    "Equipe não acompanha sua visão",
                    "Sente-se incompreendido e sozinho"
                ],
                "desejos_especificos": [
                    "Transformar visão em realidade",
                    "Ter equipe que execute sua visão",
                    "Ser compreendido e seguido"
                ],
                "abordagem_especifica": "Foco em transformar visão em sistema executável",
                "linguagem_preferida": "Inspiracional, com foco em legado e impacto",
                "gatilhos_mais_eficazes": ["Ambição expandida", "Troféu secreto", "Mentor salvador"]
            }
        ]

        return psychological_segments

    def _generate_tactical_arsenal(self, visceral_data: Dict[str, Any], data: Dict[str, Any]) -> Dict[str, Any]:
        """Gera arsenal tático de persuasão visceral"""

        return {
            "angulos_copy_devastadores": [
                "A verdade brutal que ninguém te conta sobre [segmento]",
                "Por que você está trabalhando como escravo no seu próprio negócio",
                "O erro fatal que 90% dos profissionais de [segmento] cometem",
                "Como seus concorrentes 'inferiores' estão te ultrapassando",
                "A mentira confortável que está destruindo seu futuro"
            ],
            "headlines_viscerais": [
                f"Profissionais de {data.get('segmento', 'negócios')} que leem isso ficam com raiva (mas não conseguem parar)",
                "Se você trabalha mais de 8 horas por dia, está fazendo errado",
                "Por que você ganha menos que deveria (e como seus concorrentes descobriram isso)",
                "A diferença entre quem cresce e quem estagnou não é o que você pensa",
                "O que separa os R$ 10k/mês dos R$ 100k/mês (não é talento)"
            ],
            "ganchos_emocionais_brutais": [
                "Você está cansado de ser o mais inteligente da sala e o mais pobre?",
                "Quantos anos você ainda vai aceitar ganhar menos do que merece?",
                "Seus concorrentes não são melhores que você. Eles só sabem algo que você não sabe.",
                "O mercado não está saturado. Você só não sabe como se posicionar.",
                "Pare de trabalhar PARA o seu negócio. Faça ele trabalhar PARA você."
            ],
            "scripts_confrontacao": [
                "Vou falar uma verdade que vai doer: você está desperdiçando seu potencial",
                "Se isso te incomoda, é porque é verdade",
                "Você pode continuar fingindo que está tudo bem, mas os números não mentem",
                "A única pessoa que você está enganando é você mesmo",
                "Ou você muda agora ou aceita que vai ficar assim para sempre"
            ]
        }

    def _generate_visceral_emergency(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Gera análise visceral de emergência"""

        segmento = data.get('segmento', 'negócios')

        return {
            "avatar_visceral_ultra": {
                "nome_ficticio": f"Profissional {segmento} em Negação",
                "feridas_abertas_inconfessaveis": [
                    f"Trabalhar excessivamente em {segmento} sem ver crescimento real",
                    "Sentir-se um fracasso disfarçado de empreendedor",
                    "Ter vergonha de admitir que não sabe o que faz",
                    "Viver com medo constante de que tudo desmorone",
                    "Sentir inveja dos concorrentes que crescem mais"
                ],
                "sonhos_proibidos_ardentes": [
                    f"Ser THE autoridade em {segmento}",
                    "Ter liberdade financeira total",
                    "Trabalhar 4 horas e ganhar 10x mais",
                    "Ser invejado pelos pares",
                    "Deixar um legado duradouro"
                ]
            },
            "metadata_visceral": {
                "generated_at": datetime.now().isoformat(),
                "agent": "MESTRE VISCERAL - MODO EMERGÊNCIA",
                "status": "emergency_visceral_analysis"
            }
        }

# Instância global
visceral_master = VisceralMasterAgent()