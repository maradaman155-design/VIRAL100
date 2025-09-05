#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Módulo: CPL Creator
Gera o protocolo integrado de CPLs devastadores como um módulo do sistema
"""

import logging
import json
from typing import Dict, Any, Optional
from services.enhanced_ai_manager import enhanced_ai_manager
from services.auto_save_manager import salvar_etapa

logger = logging.getLogger(__name__)

async def generate_cpl_module(
    session_id: str,
    sintese_master: Dict[str, Any],
    avatar_data: Dict[str, Any],
    contexto_estrategico: Dict[str, Any],
    dados_web: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Gera o módulo de CPL como parte do fluxo principal
    
    Args:
        session_id: ID da sessão
        sintese_master: Síntese completa da análise
        avatar_data: Dados do avatar gerado
        contexto_estrategico: Contexto estratégico definido
        dados_web: Dados brutos da pesquisa web
        
    Returns:
        Dict com conteúdo do módulo CPL gerado
    """
    try:
        logger.info("🎯 Gerando módulo CPL - Protocolo Integrado de Criação de CPLs Devastadores")
        
        # Preparar contexto rico para a IA
        contexto_para_ia = {
            "sintese_analise": sintese_master,
            "avatar_cliente": avatar_data,
            "contexto_estrategico": contexto_estrategico,
            "dados_pesquisa_web": {k: v for k, v in list(dados_web.items())[:5]} if dados_web else {},
            "termos_chave": contexto_estrategico.get("termos_chave", [])[:10] if contexto_estrategico else [],
            "objecoes_identificadas": contexto_estrategico.get("objecoes", [])[:5] if contexto_estrategico else [],
            "tendencias_mercado": contexto_estrategico.get("tendencias", [])[:5] if contexto_estrategico else [],
            "casos_sucesso_reais": contexto_estrategico.get("casos_sucesso", [])[:5] if contexto_estrategico else []
        }

        prompt = f"""
# MÓDULO ESPECIALIZADO: PROTOCOLO INTEGRADO DE CRIAÇÃO DE CPLs DEVASTADORES

## CONTEXTO ESTRATÉGICO FORNECIDO:
{json.dumps(contexto_para_ia, indent=2, ensure_ascii=False)}

## INSTRUÇÕES PARA GERAÇÃO:

Com base em TODO o contexto fornecido, crie um protocolo integrado e devastador para criação de sequência de 4 CPLs (Copywriting de Alta Performance) que converta de forma excepcional.

### ESTRUTURA OBRIGATÓRIA DE SAÍDA (ENVIAR APENAS JSON VÁLIDO):

```json
{{
  "titulo": "Título impactante do protocolo gerado",
  "descricao": "Descrição do protocolo e seu impacto estratégico",
  "fases": {{
    "fase_1_arquitetura": {{
      "titulo": "Arquitetura do Evento Magnético",
      "descricao": "Visão geral da arquitetura",
      "estrategia": "Estratégia central da fase",
      "versoes_evento": [
        {{
          "tipo": "Agressiva/Polarizadora|Aspiracional/Inspiradora|Urgente/Escassa",
          "nome_evento": "Nome magnético do evento",
          "justificativa_psicologica": "Justificativa do nome",
          "promessa_central": "Promessa paralisante",
          "mapeamento_cpls": {{
            "cpl1": "Mapeamento psicológico CPL1",
            "cpl2": "Mapeamento psicológico CPL2",
            "cpl3": "Mapeamento psicológico CPL3",
            "cpl4": "Mapeamento psicológico CPL4"
          }}
        }}
      ],
      "recomendacao_final": "Recomendação de qual versão usar e por quê"
    }},
    "fase_2_cpl1": {{
      "titulo": "CPL1 - A Oportunidade Paralisante",
      "descricao": "Descrição da CPL1",
      "teasers": [
        {{
          "texto": "Texto do teaser baseado em frases EXATAS coletadas",
          "justificativa": "Por que esta frase é eficaz"
        }}
      ],
      "historia_transformacao": {{
        "antes": "Situação inicial do avatar (baseada em dados reais)",
        "durante": "Processo de transformação (baseado em casos de sucesso)",
        "depois": "Resultado final transformador (com dados reais)"
      }},
      "loops_abertos": [
        {{
          "descricao": "Descrição do loop aberto",
          "fechamento_no_cpl4": "Como será fechado no CPL4"
        }}
      ],
      "quebras_padrao": [
        {{
          "descricao": "Quebra de padrão específica",
          "base_tendencia": "Tendência que fundamenta"
        }}
      ],
      "provas_sociais": [
        {{
          "tipo": "Tipo de prova social",
          "dados_reais": "Dados concretos (se disponível)",
          "impacto_psicologico": "Impacto esperado"
        }}
      ]
    }},
    "fase_3_cpl2": {{
      "titulo": "CPL2 - A Transformação Impossível",
      "descricao": "Descrição da CPL2",
      "casos_sucesso_detalhados": [
        {{
          "caso": "Descrição do caso específico (se disponível)",
          "before_after_expandido": {{
            "antes": "Situação antes (com dados)",
            "durante": "Processo aplicado (com termos específicos do nicho)",
            "depois": "Resultados alcançados (quantificáveis)"
          }},
          "elementos_cinematograficos": [
            "Elemento 1 baseado em depoimentos reais",
            "Elemento 2 baseado em depoimentos reais"
          ],
          "resultados_quantificaveis": [
            {{
              "metrica": "Métrica medida",
              "valor_antes": "Valor inicial (se disponível)",
              "valor_depois": "Valor final (se disponível)",
              "melhoria_percentual": "Percentual de melhoria (se calculável)"
            }}
          ],
          "provas_visuais": [
            "Tipo de prova visual 1 (se mencionado)",
            "Tipo de prova visual 2 (se mencionado)"
          ]
        }}
      ],
      "metodo_revelado": {{
        "percentual_revelado": "20-30%",
        "descricao": "Descrição do que foi revelado do método",
        "elementos_principais": [
          "Elemento 1 do método (termo específico do nicho)",
          "Elemento 2 do método (termo específico do nicho)"
        ]
      }},
      "camadas_crenca": [
        {{
          "camada_numero": 1,
          "foco": "Foco da camada",
          "dados_suporte": "Dados que sustentam (se disponível)",
          "impacto_psicologico": "Impacto esperado"
        }}
      ]
    }},
    "fase_4_cpl3": {{
      "titulo": "CPL3 - O Caminho Revolucionário",
      "descricao": "Descrição da CPL3",
      "nome_metodo": "Nome do método baseado em termos-chave do nicho",
      "estrutura_passo_passo": [
        {{
          "passo": 1,
          "nome": "Nome específico do passo (termo do nicho)",
          "descricao": "Descrição detalhada",
          "tempo_execucao": "Tempo estimado de execução (se inferido)",
          "erros_comuns": [
            "Erro comum 1 identificado nas buscas",
            "Erro comum 2 identificado nas buscas"
          ],
          "dica_avancada": "Dica para otimizar resultados (se inferida)"
        }}
      ],
      "faq_estrategico": [
        {{
          "pergunta": "Pergunta real identificada nas objeções",
          "resposta": "Resposta convincente baseada em dados",
          "base_dados": "Dados que fundamentam a resposta (se disponível)"
        }}
      ],
      "justificativa_escassez": {{
        "limitacoes_reais": [
          "Limitação 1 identificada nas pesquisas",
          "Limitação 2 identificada nas pesquisas"
        ],
        "impacto_psicologico": "Impacto esperado da escassez"
      }}
    }},
    "fase_5_cpl4": {{
      "titulo": "CPL4 - A Decisão Inevitável",
      "descricao": "Descrição da CPL4",
      "stack_valor": {{
        "bonus_1_velocidade": {{
          "nome": "Nome do bônus",
          "descricao": "Descrição do valor entregue",
          "dados_tempo_economizado": "Dados concretos de tempo economizado (se disponível)",
          "impacto_avatar": "Impacto real no avatar"
        }},
        "bonus_2_facilidade": {{
          "nome": "Nome do bônus",
          "descricao": "Descrição do valor entregue",
          "friccoes_eliminadas": [
            "Fricção 1 eliminada (baseada em objeções)",
            "Fricção 2 eliminada (baseada em objeções)"
          ],
          "facilitadores_inclusos": [
            "Facilitador 1",
            "Facilitador 2"
          ]
        }},
        "bonus_3_seguranca": {{
          "nome": "Nome do bônus",
          "descricao": "Descrição do valor entregue",
          "preocupacoes_enderecadas": [
            "Preocupação 1 encontrada",
            "Preocupação 2 encontrada"
          ],
          "mecanismos_protecao": [
            "Mecanismo 1",
            "Mecanismo 2"
          ]
        }},
        "bonus_4_status": {{
          "nome": "Nome do bônus",
          "descricao": "Descrição do valor entregue",
          "aspiracoes_atendidas": [
            "Aspiração 1 identificada nas redes",
            "Aspiração 2 identificada nas redes"
          ],
          "elementos_exclusivos": [
            "Elemento 1",
            "Elemento 2"
          ]
        }},
        "bonus_5_surpresa": {{
          "nome": "Nome do bônus surpresa",
          "descricao": "Descrição do valor entregue",
          "elemento_inesperado": "Elemento que não foi mencionado nas pesquisas",
          "valor_percebido": "Alto/Médio/Baixo + justificativa"
        }}
      }},
      "precificacao_psicologica": {{
        "valor_base": "Valor definido com base em pesquisa de mercado (se inferido)",
        "comparativo_concorrentes": [
          {{
            "concorrente": "Nome do concorrente (se identificável)",
            "oferta": "Descrição da oferta (se identificável)",
            "preco": "Preço do concorrente (se identificável)",
            "diferencial_posicionamento": "Como se posicionar melhor"
          }}
        ],
        "justificativa_precificacao": "Justificativa baseada em dados reais de valor entregue"
      }},
      "garantias_agressivas": [
        {{
          "tipo_garantia": "Tipo de garantia oferecida",
          "descricao": "Descrição detalhada",
          "dados_suporte": "Dados reais que fundamentam a garantia (se disponível)",
          "periodo_cobertura": "Período de cobertura da garantia",
          "processo_resgate": "Como o cliente resgata a garantia"
        }}
      ]
    }}
  }},
  "consideracoes_finais": {{
    "impacto_previsto": "Impacto estratégico previsto da sequência CPL",
    "diferenciais": [
      "Diferencial 1 do protocolo",
      "Diferencial 2 do protocolo"
    ],
    "proximos_passos": [
      "Passo 1 para implementação",
      "Passo 2 para implementação"
    ]
  }}
}}
```

**IMPORTANTE:**
- Use APENAS dados reais fornecidos no contexto. Se um dado não estiver disponível, indique claramente (ex: "Não especificado nos dados").
- Foque em insights acionáveis e estratégias comprovadas.
- A saída DEVE ser um JSON válido, SEM markdown adicional além do bloco json de saída.
"""

        # Usar a IA com busca ativa para gerar o conteúdo do módulo
        conteudo_modulo = await enhanced_ai_manager.generate_with_active_search(
            prompt=prompt,
            context=json.dumps(contexto_para_ia, indent=2, ensure_ascii=False),
            session_id=session_id,
            max_search_iterations=2  # Menos iterações para módulo específico
        )
        
        # Tentar parsear o JSON retornado
        try:
            # Limpar possíveis marcações markdown do JSON
            conteudo_limpo = _clean_json_response(conteudo_modulo)
            modulo_cpl = json.loads(conteudo_limpo)
            
            # Validar estrutura básica
            if not _validate_cpl_structure(modulo_cpl):
                logger.warning("⚠️ Estrutura CPL incompleta, aplicando correções")
                modulo_cpl = _apply_structure_fixes(modulo_cpl)
            
            logger.info("✅ Módulo CPL gerado com sucesso")

            # Salvar o módulo gerado
            salvar_etapa("cpl_completo", modulo_cpl, categoria="modulos_principais", session_id=session_id)

            return modulo_cpl

        except json.JSONDecodeError as e:
            logger.error(f"❌ Erro ao parsear JSON do módulo CPL: {str(e)}")
            # Fallback com estrutura básica
            fallback_cpl = _create_fallback_cpl(contexto_para_ia)
            salvar_etapa("cpl_completo", fallback_cpl, categoria="modulos_principais", session_id=session_id)
            return fallback_cpl

    except Exception as e:
        logger.error(f"❌ Erro ao gerar módulo CPL: {str(e)}")
        # Retornar estrutura mínima em caso de erro
        erro_cpl = _create_error_cpl(str(e))
        salvar_etapa("cpl_erro", {"erro": str(e)}, categoria="modulos_principais", session_id=session_id)
        return erro_cpl


def _clean_json_response(response: str) -> str:
    """
    Limpa a resposta da IA removendo marcações markdown e outros elementos não JSON
    """
    import re
    
    # Remove markdown code blocks
    response = re.sub(r'```json\s*', '', response)
    response = re.sub(r'```\s*$', '', response)
    
    # Remove qualquer texto antes do primeiro { e depois do último }
    start = response.find('{')
    end = response.rfind('}')
    
    if start != -1 and end != -1:
        response = response[start:end+1]
    
    return response.strip()


def _validate_cpl_structure(modulo: Dict[str, Any]) -> bool:
    """
    Valida se a estrutura do módulo CPL está completa
    """
    required_fields = ["titulo", "descricao", "fases", "consideracoes_finais"]
    
    for field in required_fields:
        if field not in modulo:
            return False
    
    # Verificar se as fases essenciais existem
    fases = modulo.get("fases", {})
    required_phases = ["fase_1_arquitetura", "fase_2_cpl1", "fase_3_cpl2", "fase_4_cpl3", "fase_5_cpl4"]
    
    for phase in required_phases:
        if phase not in fases:
            return False
    
    return True


def _apply_structure_fixes(modulo: Dict[str, Any]) -> Dict[str, Any]:
    """
    Aplica correções na estrutura do módulo CPL
    """
    # Garantir campos obrigatórios
    if "titulo" not in modulo:
        modulo["titulo"] = "Protocolo de CPLs Devastadores"
    
    if "descricao" not in modulo:
        modulo["descricao"] = "Protocolo integrado para criação de CPLs de alta conversão"
    
    if "fases" not in modulo:
        modulo["fases"] = {}
    
    if "consideracoes_finais" not in modulo:
        modulo["consideracoes_finais"] = {
            "impacto_previsto": "Alto potencial de conversão",
            "diferenciais": ["Baseado em dados reais", "Estrutura psicológica comprovada"],
            "proximos_passos": ["Implementar sequência", "Testar e otimizar"]
        }
    
    return modulo


def _create_fallback_cpl(contexto: Dict[str, Any]) -> Dict[str, Any]:
    """
    Cria uma estrutura CPL de fallback baseada no contexto disponível
    """
    avatar = contexto.get("avatar_cliente", {})
    estrategico = contexto.get("contexto_estrategico", {})
    
    return {
        "titulo": "Protocolo de CPLs Devastadores - Versão Fallback",
        "descricao": f"Protocolo adaptado para {avatar.get('perfil', 'avatar identificado')}",
        "fases": {
            "fase_1_arquitetura": {
                "titulo": "Arquitetura do Evento Magnético",
                "descricao": "Estrutura base para evento de conversão",
                "estrategia": "Maximizar interesse e engajamento inicial",
                "versoes_evento": [
                    {
                        "tipo": "Aspiracional/Inspiradora",
                        "nome_evento": f"Transformação {estrategico.get('nicho', 'Profissional')}",
                        "justificativa_psicologica": "Apela para aspirações de crescimento",
                        "promessa_central": "Resultados extraordinários em tempo reduzido",
                        "mapeamento_cpls": {
                            "cpl1": "Despertar interesse com oportunidade única",
                            "cpl2": "Demonstrar transformações reais",
                            "cpl3": "Revelar método revolucionário",
                            "cpl4": "Converter com oferta irresistível"
                        }
                    }
                ],
                "recomendacao_final": "Versão aspiracional recomendada para máximo engajamento"
            },
            "fase_2_cpl1": {
                "titulo": "CPL1 - A Oportunidade Paralisante",
                "descricao": "Primeiro contato que desperta curiosidade máxima",
                "teasers": [
                    {
                        "texto": "Descoberta revolucionária está mudando tudo no seu nicho",
                        "justificativa": "Cria curiosidade e urgência"
                    }
                ],
                "historia_transformacao": {
                    "antes": "Situação de frustração comum no nicho",
                    "durante": "Descoberta do método transformador",
                    "depois": "Resultados extraordinários alcançados"
                },
                "loops_abertos": [
                    {
                        "descricao": "Qual é exatamente esse método revolucionário?",
                        "fechamento_no_cpl4": "Revelação completa na oferta final"
                    }
                ],
                "quebras_padrao": [
                    {
                        "descricao": "Contradiz crenças estabelecidas no mercado",
                        "base_tendencia": "Novos dados científicos/mercadológicos"
                    }
                ],
                "provas_sociais": [
                    {
                        "tipo": "Casos de sucesso inicial",
                        "dados_reais": "Não especificado nos dados",
                        "impacto_psicologico": "Credibilidade e possibilidade"
                    }
                ]
            },
            "fase_3_cpl2": {
                "titulo": "CPL2 - A Transformação Impossível",
                "descricao": "Demonstra resultados que parecem impossíveis",
                "casos_sucesso_detalhados": [
                    {
                        "caso": "Transformação dramática em tempo recorde",
                        "before_after_expandido": {
                            "antes": "Situação de dificuldade extrema",
                            "durante": "Aplicação do método revelado",
                            "depois": "Resultados excepcionais documentados"
                        },
                        "elementos_cinematograficos": [
                            "Narrativa emocional envolvente",
                            "Detalhes visuais impactantes"
                        ],
                        "resultados_quantificaveis": [
                            {
                                "metrica": "Melhoria principal do nicho",
                                "valor_antes": "Não especificado nos dados",
                                "valor_depois": "Não especificado nos dados",
                                "melhoria_percentual": "Não especificado nos dados"
                            }
                        ],
                        "provas_visuais": [
                            "Screenshots/fotos dos resultados",
                            "Depoimentos em vídeo"
                        ]
                    }
                ],
                "metodo_revelado": {
                    "percentual_revelado": "25%",
                    "descricao": "Elementos-chave do método sem revelar tudo",
                    "elementos_principais": [
                        "Princípio fundamental único",
                        "Abordagem contraintuitiva"
                    ]
                },
                "camadas_crenca": [
                    {
                        "camada_numero": 1,
                        "foco": "É possível ter esses resultados",
                        "dados_suporte": "Casos documentados",
                        "impacto_psicologico": "Quebra limitações mentais"
                    }
                ]
            },
            "fase_4_cpl3": {
                "titulo": "CPL3 - O Caminho Revolucionário",
                "descricao": "Revela o método e cria escassez",
                "nome_metodo": f"Método {estrategico.get('termos_chave', ['Inovador'])[0] if estrategico.get('termos_chave') else 'Revolucionário'}",
                "estrutura_passo_passo": [
                    {
                        "passo": 1,
                        "nome": "Fundação Estratégica",
                        "descricao": "Estabelece a base do método",
                        "tempo_execucao": "Não especificado nos dados",
                        "erros_comuns": [
                            "Pular etapas fundamentais",
                            "Não seguir sequência correta"
                        ],
                        "dica_avancada": "Personalizar para situação específica"
                    }
                ],
                "faq_estrategico": [
                    {
                        "pergunta": "Quanto tempo leva para ver resultados?",
                        "resposta": "Resultados iniciais em prazo surpreendentemente rápido",
                        "base_dados": "Não especificado nos dados"
                    }
                ],
                "justificativa_escassez": {
                    "limitacoes_reais": [
                        "Capacidade limitada de atendimento",
                        "Método ainda não amplamente conhecido"
                    ],
                    "impacto_psicologico": "Urgência para não perder oportunidade"
                }
            },
            "fase_5_cpl4": {
                "titulo": "CPL4 - A Decisão Inevitável",
                "descricao": "Oferta irresistível que converte",
                "stack_valor": {
                    "bonus_1_velocidade": {
                        "nome": "Acelerador de Resultados",
                        "descricao": "Ferramentas para acelerar implementação",
                        "dados_tempo_economizado": "Não especificado nos dados",
                        "impacto_avatar": "Economia significativa de tempo"
                    },
                    "bonus_2_facilidade": {
                        "nome": "Kit Implementação Simples",
                        "descricao": "Torna o processo mais fácil",
                        "friccoes_eliminadas": [
                            "Complexidade desnecessária",
                            "Dúvidas sobre como começar"
                        ],
                        "facilitadores_inclusos": [
                            "Guia passo a passo",
                            "Templates prontos"
                        ]
                    },
                    "bonus_3_seguranca": {
                        "nome": "Garantia Blindada",
                        "descricao": "Remove todo o risco do investimento",
                        "preocupacoes_enderecadas": [
                            "Medo de não funcionar",
                            "Receio do investimento"
                        ],
                        "mecanismos_protecao": [
                            "Garantia incondicional",
                            "Suporte dedicado"
                        ]
                    },
                    "bonus_4_status": {
                        "nome": "Acesso VIP Exclusivo",
                        "descricao": "Status diferenciado no mercado",
                        "aspiracoes_atendidas": [
                            "Ser reconhecido como autoridade",
                            "Ter acesso privilegiado"
                        ],
                        "elementos_exclusivos": [
                            "Comunidade privada",
                            "Conteúdo exclusivo"
                        ]
                    },
                    "bonus_5_surpresa": {
                        "nome": "Bônus Surpresa Revelado",
                        "descricao": "Valor adicional inesperado",
                        "elemento_inesperado": "Ferramenta premium não anunciada",
                        "valor_percebido": "Alto - adiciona valor significativo"
                    }
                },
                "precificacao_psicologica": {
                    "valor_base": "Não especificado nos dados",
                    "comparativo_concorrentes": [
                        {
                            "concorrente": "Não identificado nos dados",
                            "oferta": "Não especificado nos dados",
                            "preco": "Não especificado nos dados",
                            "diferencial_posicionamento": "Valor superior com garantias"
                        }
                    ],
                    "justificativa_precificacao": "Baseada no valor entregue vs resultados obtidos"
                },
                "garantias_agressivas": [
                    {
                        "tipo_garantia": "Satisfação Incondicional",
                        "descricao": "Garantia total de satisfação ou reembolso",
                        "dados_suporte": "Não especificado nos dados",
                        "periodo_cobertura": "30-60 dias",
                        "processo_resgate": "Solicitação simples por email"
                    }
                ]
            }
        },
        "consideracoes_finais": {
            "impacto_previsto": "Alta conversão baseada em estrutura psicológica comprovada",
            "diferenciais": [
                "Sequência estruturada cientificamente",
                "Adaptação ao avatar específico",
                "Múltiplas camadas de persuasão"
            ],
            "proximos_passos": [
                "Personalizar conteúdo para dados específicos",
                "Testar e otimizar cada CPL",
                "Monitorar métricas de conversão"
            ]
        }
    }


def _create_error_cpl(error_message: str) -> Dict[str, Any]:
    """
    Cria uma estrutura CPL de erro
    """
    return {
        "titulo": "Protocolo de CPLs - Erro na Geração",
        "descricao": f"Não foi possível gerar o protocolo completo devido a: {error_message}",
        "fases": {},
        "consideracoes_finais": {
            "impacto_previsto": "Não aplicável devido a erro",
            "diferenciais": [],
            "proximos_passos": [
                "Verificar logs de erro",
                "Validar dados de entrada",
                "Tentar regenerar o módulo"
            ]
        }
    }
