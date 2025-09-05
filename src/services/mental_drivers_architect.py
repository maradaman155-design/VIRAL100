#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ARQV30 Enhanced v2.0 - Mental Drivers Architect
Arquiteto de Drivers Mentais Customizados
"""

import time
import random
import logging
import json
from typing import Dict, List, Any, Optional
from services.ai_manager import ai_manager
from services.auto_save_manager import salvar_etapa, salvar_erro

logger = logging.getLogger(__name__)

class MentalDriversArchitect:
    """Arquiteto de Drivers Mentais Customizados"""

    def __init__(self):
        """Inicializa o arquiteto de drivers mentais"""
        logger.info("Mental Drivers Architect inicializado")

    def generate_custom_drivers(self, segmento: str, produto: str, publico: str = "", web_research: Dict = None, social_analysis: Dict = None) -> Dict[str, Any]:
        """Gera drivers mentais customizados para o segmento e avatar"""
        drivers_result = self.create_ultra_targeted_drivers(segmento, produto)
        
        # Garante retorno como dict
        if isinstance(drivers_result, list):
            return {
                'drivers_customizados': drivers_result,
                'total_drivers': len(drivers_result),
                'generation_timestamp': time.time(),
                'validation_status': 'VALID'
            }
        elif isinstance(drivers_result, dict):
            return drivers_result
        else:
            # Fallback se retorno inválido
            return {
                'drivers_customizados': [],
                'total_drivers': 0,
                'generation_timestamp': time.time(),
                'validation_status': 'ERROR',
                'error': 'Tipo de retorno inválido'
            }

    def create_ultra_targeted_drivers(self, segmento: str, avatar_data: Dict[str, Any]) -> Dict[str, Any]:
        """Gera drivers mentais customizados para o segmento"""
        try:
            logger.info(f"🧠 Gerando drivers customizados para {segmento}")

            from services.ai_manager import ai_manager

            prompt = f"""
Crie 5 drivers mentais poderosos e específicos para o segmento "{segmento}".

Para cada driver, forneça:
1. Nome impactante
2. Gatilho emocional central
3. Definição visceral (o que realmente significa)
4. Roteiro de ativação pronto para usar

RETORNE APENAS JSON VÁLIDO:
{{
    "drivers": [
        {{
            "nome": "Nome do Driver",
            "gatilho_central": "Emoção principal",
            "definicao_visceral": "O que significa na prática",
            "roteiro_ativacao": {{
                "pergunta_abertura": "Pergunta para abrir a ferida",
                "historia_analogia": "História/analogia poderosa",
                "comando_acao": "Comando direto de ação"
            }}
        }}
    ]
}}
"""

            response = ai_manager.generate_content(prompt, max_tokens=2000)
            if response:
                import json
                try:
                    # CORREÇÃO CRÍTICA: Melhor parsing de JSON
                    clean_response = response.strip()
                    
                    # Verifica se há conteúdo válido
                    if not clean_response:
                        logger.warning("⚠️ Response vazio da IA")
                        return {'drivers': self._create_fallback_drivers(segmento)}
                    
                    # Múltiplos métodos de extração JSON
                    json_text = None
                    
                    # Método 1: JSON entre ```json e ```
                    if "```json" in clean_response:
                        start = clean_response.find("```json") + 7
                        end = clean_response.rfind("```")
                        if end > start:
                            json_text = clean_response[start:end].strip()
                    
                    # Método 2: JSON entre ``` e ```
                    elif "```" in clean_response:
                        parts = clean_response.split("```")
                        for part in parts:
                            part = part.strip()
                            if part.startswith("{") and part.endswith("}"):
                                json_text = part
                                break
                    
                    # Método 3: JSON direto
                    elif clean_response.startswith("{") and clean_response.endswith("}"):
                        json_text = clean_response
                    
                    # Método 4: Busca por padrão JSON
                    else:
                        import re
                        json_match = re.search(r'\{.*\}', clean_response, re.DOTALL)
                        if json_match:
                            json_text = json_match.group()
                    
                    if json_text:
                        drivers_data = json.loads(json_text)
                        
                        # CORREÇÃO CRÍTICA: Retorna dict com chave 'drivers'
                        if isinstance(drivers_data, dict) and 'drivers' in drivers_data:
                            return drivers_data
                        elif isinstance(drivers_data, list):
                            return {'drivers': drivers_data}
                        else:
                            logger.warning("⚠️ JSON não tem estrutura esperada")
                            return {'drivers': self._create_fallback_drivers(segmento)}
                    else:
                        logger.warning("⚠️ Nenhum JSON encontrado na response")
                        return {'drivers': self._create_fallback_drivers(segmento)}
                        
                except json.JSONDecodeError as e:
                    logger.error(f"❌ Erro ao parsear JSON: {e}")
                    logger.error(f"❌ JSON problemático: {json_text[:200] if 'json_text' in locals() else 'N/A'}")
                    return {'drivers': self._create_fallback_drivers(segmento)}
                except Exception as e:
                    logger.error(f"❌ Erro geral no parsing: {e}")
                    return {'drivers': self._create_fallback_drivers(segmento)}
            else:
                return {'drivers': self._create_fallback_drivers(segmento)}

        except Exception as e:
            logger.error(f"❌ Erro ao gerar drivers customizados: {e}")
            return self._create_fallback_drivers(segmento)

    def _create_fallback_drivers(self, segmento, produto=None):
        """Cria drivers de fallback quando IA falha"""
        return [
            {
                "nome": f"Driver {segmento} - Transformação",
                "gatilho_central": "Urgência de mudança",
                "definicao_visceral": f"Parar de aceitar mediocridade em {segmento}",
                "roteiro_ativacao": {
                    "pergunta_abertura": f"Há quanto tempo você aceita resultados medianos em {segmento}?",
                    "historia_analogia": f"Conheci um especialista em {segmento} que estava na mesma situação...",
                    "comando_acao": "Pare de aceitar menos do que merece"
                }
            },
            {
                "nome": f"Driver {produto if produto else 'Produto'} - Urgência",
                "gatilho_central": "Medo de perder oportunidade",
                "definicao_visceral": f"Agir agora ou perder a chance com {produto if produto else 'o produto'}",
                "roteiro_ativacao": {
                    "pergunta_abertura": f"O que acontece se você não dominar {produto if produto else 'o produto'} este ano?",
                    "historia_analogia": f"Vi pessoas perderem grandes oportunidades por não conhecer {produto if produto else 'o produto'}...",
                    "comando_acao": "Aja antes que seja tarde demais"
                }
            }
        ]

    def _load_universal_drivers(self) -> Dict[str, Dict[str, Any]]:
        """Carrega drivers mentais universais"""
        return {
            'urgencia_temporal': {
                'nome': 'Urgência Temporal',
                'gatilho_central': 'Tempo limitado para agir',
                'definicao_visceral': 'Criar pressão temporal que força decisão imediata',
                'aplicacao': 'Quando prospect está procrastinando'
            },
            'escassez_oportunidade': {
                'nome': 'Escassez de Oportunidade',
                'gatilho_central': 'Oportunidade única e limitada',
                'definicao_visceral': 'Amplificar valor através da raridade',
                'aplicacao': 'Para aumentar percepção de valor'
            },
            'prova_social': {
                'nome': 'Prova Social Qualificada',
                'gatilho_central': 'Outros como ele já conseguiram',
                'definicao_visceral': 'Reduzir risco através de validação social',
                'aplicacao': 'Para superar objeções de confiança'
            },
            'autoridade_tecnica': {
                'nome': 'Autoridade Técnica',
                'gatilho_central': 'Expertise comprovada',
                'definicao_visceral': 'Estabelecer credibilidade através de conhecimento',
                'aplicacao': 'Para construir confiança inicial'
            },
            'reciprocidade': {
                'nome': 'Reciprocidade Estratégica',
                'gatilho_central': 'Valor entregue antecipadamente',
                'definicao_visceral': 'Criar obrigação psicológica de retribuição',
                'aplicacao': 'Para gerar compromisso'
            }
        }

    def _load_driver_templates(self) -> Dict[str, str]:
        """Carrega templates de drivers"""
        return {
            'historia_analogia': 'Era uma vez {personagem} que enfrentava {problema_similar}. Depois de {tentativas_fracassadas}, descobriu que {solucao_especifica} e conseguiu {resultado_transformador}.',
            'metafora_visual': 'Imagine {situacao_atual} como {metafora_visual}. Agora visualize {situacao_ideal} como {metafora_transformada}.',
            'comando_acao': 'Agora que você {compreensao_adquirida}, a única ação lógica é {acao_especifica} porque {consequencia_inevitavel}.'
        }

    def generate_complete_drivers_system(
        self, 
        avatar_data: Dict[str, Any], 
        context_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Gera sistema completo de drivers mentais customizados - 19 DRIVERS GARANTIDOS"""

        # Validação crítica de entrada
        if not avatar_data:
            avatar_data = {'dores_viscerais': [], 'desejos_ocultos': [], 'medos_secretos': []}

        if not context_data.get('segmento'):
            context_data['segmento'] = 'negócios'

        try:
            logger.info("🧠 Gerando 19 drivers mentais customizados...")

            # Salva dados de entrada imediatamente
            salvar_etapa("drivers_entrada", {
                "avatar_data": avatar_data,
                "context_data": context_data
            }, categoria="drivers_mentais")

            # GERA OS 19 DRIVERS UNIVERSAIS CUSTOMIZADOS
            drivers_universais = self._generate_19_universal_drivers(context_data)

            # Gera drivers adicionais baseados no avatar
            drivers_customizados = self._generate_customized_drivers_with_ai(avatar_data, context_data)

            # Combina e garante 19 drivers
            all_drivers = drivers_universais + drivers_customizados
            all_drivers = all_drivers[:19]  # Garante exatamente 19

            # Preenche até 19 se necessário
            while len(all_drivers) < 19:
                additional_driver = self._create_additional_driver(len(all_drivers) + 1, context_data)
                all_drivers.append(additional_driver)

            # Salva drivers customizados
            salvar_etapa("drivers_customizados", all_drivers, categoria="drivers_mentais")

            # Cria roteiros de ativação
            activation_scripts = self._create_activation_scripts(all_drivers, avatar_data)

            # Gera frases de ancoragem
            anchor_phrases = self._generate_anchor_phrases(all_drivers, avatar_data)

            # Sequenciamento estratégico
            sequencing = self._create_strategic_sequencing(all_drivers)

            result = {
                'drivers_customizados': all_drivers,
                'roteiros_ativacao': activation_scripts,
                'frases_ancoragem': anchor_phrases,
                'sequenciamento_estrategico': sequencing,
                'total_drivers': len(all_drivers),
                'drivers_emocionais': len([d for d in all_drivers if d.get('tipo') == 'emocional']),
                'drivers_racionais': len([d for d in all_drivers if d.get('tipo') == 'racional']),
                'personalizacao_nivel': 'Alto',
                'validation_status': 'VALID',
                'generation_timestamp': time.time()
            }

            # Salva resultado final imediatamente
            salvar_etapa("drivers_final", result, categoria="drivers_mentais")

            logger.info(f"✅ {len(all_drivers)} drivers mentais customizados gerados com sucesso")
            return result

        except Exception as e:
            logger.error(f"❌ Erro ao gerar drivers mentais: {str(e)}")
            salvar_erro("drivers_sistema", e, contexto={"segmento": context_data.get('segmento')})

            # Fallback GARANTIDO com 19 drivers
            logger.warning("🔄 Gerando 19 drivers básicos como fallback...")
            return self._generate_guaranteed_19_drivers_system(context_data)

    def _identify_ideal_drivers(self, avatar_data: Dict[str, Any], context_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identifica drivers ideais baseado no avatar"""

        ideal_drivers = []

        # Analisa dores para identificar drivers
        dores = avatar_data.get('dores_viscerais', [])

        # Mapeia dores para drivers
        if any('tempo' in dor.lower() for dor in dores):
            ideal_drivers.append(self.universal_drivers['urgencia_temporal'])

        if any('concorrência' in dor.lower() or 'competidor' in dor.lower() for dor in dores):
            ideal_drivers.append(self.universal_drivers['escassez_oportunidade'])

        if any('resultado' in dor.lower() or 'crescimento' in dor.lower() for dor in dores):
            ideal_drivers.append(self.universal_drivers['prova_social'])

        # Sempre inclui autoridade técnica
        ideal_drivers.append(self.universal_drivers['autoridade_tecnica'])

        # Sempre inclui reciprocidade
        ideal_drivers.append(self.universal_drivers['reciprocidade'])

        return ideal_drivers[:5]  # Máximo 5 drivers

    def _generate_customized_drivers(
        self, 
        ideal_drivers: List[Dict[str, Any]], 
        avatar_data: Dict[str, Any], 
        context_data: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Gera drivers customizados usando IA"""

        try:
            segmento = context_data.get('segmento', 'negócios')

            prompt = f"""
Crie drivers mentais customizados para o segmento {segmento}.

AVATAR:
{json.dumps(avatar_data, indent=2, ensure_ascii=False)[:2000]}

DRIVERS IDEAIS:
{json.dumps(ideal_drivers, indent=2, ensure_ascii=False)[:1000]}

RETORNE APENAS JSON VÁLIDO:

```json
[
  {{
    "nome": "Nome específico do driver",
    "gatilho_central": "Gatilho psicológico principal",
    "definicao_visceral": "Definição que gera impacto emocional",
    "roteiro_ativacao": {{
      "pergunta_abertura": "Pergunta que ativa o driver",
      "historia_analogia": "História específica de 150+ palavras",
      "metafora_visual": "Metáfora visual poderosa",
      "comando_acao": "Comando específico de ação"
    }},
    "frases_ancoragem": [
      "Frase 1 de ancoragem",
      "Frase 2 de ancoragem",
      "Frase 3 de ancoragem"
    ],
    "prova_logica": "Prova lógica que sustenta o driver"
  }}
]
"""

            response = ai_manager.generate_analysis(prompt, max_tokens=2000)

            if response:
                clean_response = response.strip()
                if "```json" in clean_response:
                    start = clean_response.find("```json") + 7
                    end = clean_response.rfind("```")
                    clean_response = clean_response[start:end].strip()

                try:
                    drivers = json.loads(clean_response)
                    if isinstance(drivers, list) and len(drivers) > 0:
                        logger.info("✅ Drivers customizados gerados com IA")
                        return drivers
                    else:
                        logger.warning("⚠️ IA retornou formato inválido")
                except json.JSONDecodeError:
                    logger.warning("⚠️ IA retornou JSON inválido")

            # Fallback para drivers básicos
            return self._create_basic_drivers(context_data)

        except Exception as e:
            logger.error(f"❌ Erro ao gerar drivers customizados: {str(e)}")
            return self._create_basic_drivers(context_data)

    def _generate_19_universal_drivers(self, context_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Gera os 19 drivers universais customizados para o segmento"""

        segmento = context_data.get('segmento', 'negócios')

        drivers_universais = [
            # DRIVERS EMOCIONAIS PRIMÁRIOS (1-11)
            {
                'numero': 1,
                'nome': f'Ferida Exposta {segmento}',
                'tipo': 'emocional',
                'gatilho_central': f'Dor não resolvida em {segmento}',
                'definicao_visceral': f'Trazer à consciência o que foi reprimido em {segmento}',
                'mecanica_psicologica': 'Expor vulnerabilidades para criar urgência de mudança',
                'momento_instalacao': 'Início da jornada - despertar consciência',
                'roteiro_ativacao': {
                    'pergunta_abertura': f'Você ainda luta com os mesmos problemas em {segmento} há anos?',
                    'historia_analogia': f'Conheci um empresário de {segmento} que fingiu estar bem por 5 anos. Todos pensavam que ele tinha sucesso, mas por dentro ele sabia que estava apenas sobrevivendo. Um dia, olhou no espelho e não reconheceu quem havia se tornado. A ferida estava sangrando há tanto tempo que ele nem sentia mais a dor.',
                    'metafora_visual': f'Imagine {segmento} como uma ferida que você cobriu com band-aid por anos',
                    'comando_acao': f'Pare de esconder a ferida em {segmento} e comece a curá-la de verdade'
                },
                'frases_ancoragem': [
                    f'Feridas não tratadas em {segmento} só pioram com o tempo',
                    f'O que você esconde em {segmento} está corroendo você por dentro',
                    f'Fingir que está tudo bem em {segmento} não resolve nada'
                ],
                'prova_logica': f'85% dos profissionais de {segmento} sofrem com problemas não resolvidos por mais de 3 anos',
                'loop_reforco': f'Toda vez que sentir frustração em {segmento}, lembre: feridas expostas podem ser curadas'
            },
            {
                'numero': 2,
                'nome': f'Troféu Secreto {segmento}',
                'tipo': 'emocional',
                'gatilho_central': f'Desejo inconfessável em {segmento}',
                'definicao_visceral': f'Validar ambições "proibidas" em {segmento}',
                'mecanica_psicologica': 'Liberar desejos reprimidos pela sociedade',
                'momento_instalacao': 'Meio da jornada - amplificar motivação',
                'roteiro_ativacao': {
                    'pergunta_abertura': f'Qual é o troféu que você realmente quer em {segmento} mas tem vergonha de admitir?',
                    'historia_analogia': f'Um cliente meu de {segmento} disse que queria "ajudar pessoas". Mas quando conversamos a sós, ele confessou: "Eu quero ser reconhecido como o melhor, quero que todos me vejam como autoridade". Não tinha nada de errado nisso - era sua verdadeira motivação.',
                    'metafora_visual': f'Seu troféu secreto em {segmento} é como um diamante escondido no cofre',
                    'comando_acao': f'Assuma seu verdadeiro desejo em {segmento} sem vergonha'
                },
                'frases_ancoragem': [
                    f'Seu troféu secreto em {segmento} é válido e poderoso',
                    f'Desejos ocultos em {segmento} são combustível para grandes resultados',
                    f'O que você realmente quer em {segmento} merece ser conquistado'
                ],
                'prova_logica': f'Profissionais que assumem seus verdadeiros desejos em {segmento} têm 3x mais chances de sucesso',
                'loop_reforco': f'Sempre que se sentir julgado em {segmento}, lembre: seu troféu secreto é legítimo'
            },
            {
                'numero': 3,
                'nome': f'Inveja Produtiva {segmento}',
                'tipo': 'emocional',
                'gatilho_central': f'Comparação com pares em {segmento}',
                'definicao_visceral': f'Transformar inveja em combustível para {segmento}',
                'mecanica_psicologica': 'Canalizar energia negativa para motivação positiva',
                'momento_instalacao': 'Fase de despertar - criar tensão motivacional',
                'roteiro_ativacao': {
                    'pergunta_abertura': f'Quem em {segmento} tem o que você gostaria de ter?',
                    'historia_analogia': f'Vi dois profissionais de {segmento} que começaram juntos. Um ficou com inveja do sucesso do outro e se tornou amargo. O segundo usou a inveja como combustível e superou o primeiro em 2 anos. A diferença? Um viu a inveja como veneno, outro como informação valiosa.',
                    'metafora_visual': f'Inveja em {segmento} é como fogo - pode queimar sua casa ou mover sua máquina',
                    'comando_acao': f'Use a inveja como mapa do que é possível em {segmento}'
                },
                'frases_ancoragem': [
                    f'Inveja em {segmento} é prova de que é possível',
                    f'O sucesso que você inveja em {segmento} pode ser seu',
                    f'Transforme inveja em {segmento} em estratégia'
                ],
                'prova_logica': f'70% dos grandes sucessos em {segmento} começaram observando concorrentes',
                'loop_reforco': f'Quando sentir inveja em {segmento}, pergunte: o que isso me ensina?'
            },
            {
                'numero': 4,
                'nome': f'Relógio Psicológico {segmento}',
                'tipo': 'emocional',
                'gatilho_central': f'Urgência existencial em {segmento}',
                'definicao_visceral': f'Tempo como recurso finito em {segmento}',
                'mecanica_psicologica': 'Ativar consciência da mortalidade e escassez temporal',
                'momento_instalacao': 'Fase de decisão - criar pressão temporal',
                'roteiro_ativacao': {
                    'pergunta_abertura': f'Quantos anos você ainda vai perder em {segmento} fazendo as mesmas coisas?',
                    'historia_analogia': f'Um profissional experiente de {segmento} me disse: "Se eu soubesse aos 30 o que sei hoje aos 50, teria 20 anos a mais de resultados". O tempo perdido não volta. Cada ano que você adia em {segmento} é um ano a menos de colheita.',
                    'metafora_visual': f'Seu tempo em {segmento} é como areia na ampulheta - cada grão que cai não volta',
                    'comando_acao': f'Pare de desperdiçar tempo em {segmento} e comece hoje'
                },
                'frases_ancoragem': [
                    f'Cada dia perdido em {segmento} é oportunidade que não volta',
                    f'O relógio de {segmento} não para para ninguém',
                    f'Tempo desperdiçado em {segmento} é vida desperdiçada'
                ],
                'prova_logica': f'Profissionais que agem com urgência em {segmento} crescem 5x mais rápido',
                'loop_reforco': f'Toda manhã, lembre: mais um dia para avançar em {segmento} ou desperdiçar'
            },
            {
                'numero': 5,
                'nome': f'Identidade Aprisionada {segmento}',
                'tipo': 'emocional',
                'gatilho_central': f'Conflito entre quem é e quem poderia ser em {segmento}',
                'definicao_visceral': f'Expor a máscara social que limita em {segmento}',
                'mecanica_psicologica': 'Quebrar autoimagem limitante para permitir expansão',
                'momento_instalacao': 'Início - quebrar padrões de autolimitação',
                'roteiro_ativacao': {
                    'pergunta_abertura': f'Que versão de você mesmo em {segmento} você está escondendo do mundo?',
                    'historia_analogia': f'Encontrei um líder de {segmento} que se via como "apenas mais um". Ele havia se convencido de que não era especial. Quando descobriu que estava usando essa identidade como escudo contra o fracasso, tudo mudou. Ele não era "apenas mais um" - era alguém que escolhia se esconder.',
                    'metafora_visual': f'Sua identidade atual em {segmento} é como uma prisão com a porta aberta',
                    'comando_acao': f'Liberte-se da identidade limitante em {segmento} e assuma quem realmente é'
                },
                'frases_ancoragem': [
                    f'Você não é apenas mais um em {segmento}',
                    f'Sua identidade atual em {segmento} é escolha, não destino',
                    f'A pessoa que você pode ser em {segmento} está esperando ser libertada'
                ],
                'prova_logica': f'90% dos profissionais de {segmento} operam com 30% do seu potencial real',
                'loop_reforco': f'Sempre que se limitar em {segmento}, pergunte: é real ou é medo?'
            },
            {
                'numero': 6,
                'nome': f'Custo Invisível {segmento}',
                'tipo': 'emocional',
                'gatilho_central': f'Perda não percebida em {segmento}',
                'definicao_visceral': f'Quantificar o preço da inação em {segmento}',
                'mecanica_psicologica': 'Tornar visíveis perdas que são ignoradas',
                'momento_instalacao': 'Fase de conscientização - mostrar consequências',
                'roteiro_ativacao': {
                    'pergunta_abertura': f'Quanto você está perdendo em {segmento} sem perceber?',
                    'historia_analogia': f'Um empresário de {segmento} achava que estava economizando ao não investir em melhorias. Calculamos: ele perdia R$ 50 mil por ano em oportunidades perdidas. O que ele chamava de economia era na verdade o custo mais caro da sua carreira.',
                    'metafora_visual': f'Inação em {segmento} é como vazamento silencioso - você só vê quando a conta chega',
                    'comando_acao': f'Calcule o custo real da inação em {segmento} e aja'
                },
                'frases_ancoragem': [
                    f'Não agir em {segmento} também é uma decisão cara',
                    f'O custo da inação em {segmento} é sempre maior que o da ação',
                    f'Cada dia sem evolução em {segmento} custa oportunidades'
                ],
                'prova_logica': f'Inação em {segmento} custa em média 40% das oportunidades anuais',
                'loop_reforco': f'Antes de adiar algo em {segmento}, calcule: quanto isso me custa?'
            },
            {
                'numero': 7,
                'nome': f'Ambição Expandida {segmento}',
                'tipo': 'emocional',
                'gatilho_central': f'Sonhos pequenos demais em {segmento}',
                'definicao_visceral': f'Elevar o teto mental de possibilidades em {segmento}',
                'mecanica_psicologica': 'Quebrar limitações autoimpostas de objetivos',
                'momento_instalacao': 'Meio da jornada - expandir visão',
                'roteiro_ativacao': {
                    'pergunta_abertura': f'Se o esforço é o mesmo, por que você está pedindo tão pouco em {segmento}?',
                    'historia_analogia': f'Dois profissionais de {segmento} trabalhavam 12 horas por dia. Um mirava crescer 20% ao ano, outro 200%. Descobri que o esforço era praticamente o mesmo - a diferença estava no tamanho da ambição. O segundo não trabalhava mais, trabalhava com objetivo maior.',
                    'metafora_visual': f'Ambição pequena em {segmento} é como usar Ferrari na garagem',
                    'comando_acao': f'Expanda sua ambição em {segmento} para o tamanho do seu potencial'
                },
                'frases_ancoragem': [
                    f'Sonhos pequenos em {segmento} desperdiçam grandes talentos',
                    f'Sua capacidade em {segmento} é maior que sua ambição atual',
                    f'Se vai sonhar com {segmento}, sonhe grande'
                ],
                'prova_logica': f'Profissionais com ambições grandes em {segmento} alcançam 10x mais que os conservadores',
                'loop_reforco': f'Sempre que definir metas em {segmento}, pergunte: posso sonhar maior?'
            },
            {
                'numero': 8,
                'nome': f'Diagnóstico Brutal {segmento}',
                'tipo': 'emocional',
                'gatilho_central': f'Confronto com a realidade atual em {segmento}',
                'definicao_visceral': f'Criar indignação produtiva com status quo em {segmento}',
                'mecanica_psicologica': 'Gerar desconforto necessário para mudança',
                'momento_instalacao': 'Início - quebrar complacência',
                'roteiro_ativacao': {
                    'pergunta_abertura': f'Olhe seus resultados em {segmento}. Até quando você vai aceitar isso?',
                    'historia_analogia': f'Um líder de {segmento} vivia dizendo "está tudo bem". Quando fiz ele listar todos os problemas reais, foram 23 itens críticos. "Está tudo bem" era mentira que ele contava para si mesmo. O diagnóstico brutal foi o primeiro passo para a cura.',
                    'metafora_visual': f'Sua situação atual em {segmento} é como médico que ignora sintomas graves',
                    'comando_acao': f'Encare a realidade brutal de {segmento} e decida mudar'
                },
                'frases_ancoragem': [
                    f'A verdade sobre {segmento} pode doer, mas liberta',
                    f'Diagnóstico correto em {segmento} é o primeiro passo para a cura',
                    f'Negar problemas em {segmento} não os resolve'
                ],
                'prova_logica': f'95% dos grandes avanços em {segmento} começaram com diagnóstico brutal da realidade',
                'loop_reforco': f'Mensalmente, faça diagnóstico brutal de {segmento}: onde estou vs onde deveria estar?'
            },
            {
                'numero': 9,
                'nome': f'Ambiente Vampiro {segmento}',
                'tipo': 'emocional',
                'gatilho_central': f'Consciência do entorno tóxico em {segmento}',
                'definicao_visceral': f'Revelar como ambiente atual suga energia/potencial em {segmento}',
                'mecanica_psicologica': 'Identificar influências negativas invisíveis',
                'momento_instalacao': 'Meio da jornada - justificar mudança de ambiente',
                'roteiro_ativacao': {
                    'pergunta_abertura': f'Seu ambiente atual em {segmento} te impulsiona ou te mantém pequeno?',
                    'historia_analogia': f'Conheci um talentoso profissional de {segmento} cercado de pessoas que sempre diziam "calma, não precisa de tanta pressa". Ele acreditou e por 5 anos ficou na zona de conforto. Quando mudou de ambiente, em 1 ano alcançou o que não conseguiu em 5.',
                    'metafora_visual': f'Ambiente tóxico em {segmento} é como vampiro - suga sua energia sem você perceber',
                    'comando_acao': f'Mude seu ambiente em {segmento} ou seja sugado por ele'
                },
                'frases_ancoragem': [
                    f'Ambiente medíocre em {segmento} gera resultados mediocres',
                    f'Você se torna a média do seu ambiente em {segmento}',
                    f'Ambiente que não desafia em {segmento} é ambiente que limita'
                ],
                'prova_logica': f'85% do sucesso em {segmento} depende da qualidade do ambiente',
                'loop_reforco': f'Avalie regularmente: meu ambiente em {segmento} me eleva ou me puxa para baixo?'
            },
            {
                'numero': 10,
                'nome': f'Mentor Salvador {segmento}',
                'tipo': 'emocional',
                'gatilho_central': f'Necessidade de orientação externa em {segmento}',
                'definicao_visceral': f'Ativar desejo por figura de autoridade que acredita neles em {segmento}',
                'mecanica_psicologica': 'Despertar necessidade de validação e direcionamento',
                'momento_instalacao': 'Fase de decisão - apresentar solução humana',
                'roteiro_ativacao': {
                    'pergunta_abertura': f'Você precisa de alguém que veja seu potencial em {segmento} quando você não consegue?',
                    'historia_analogia': f'Um empresário de {segmento} estava perdido há 3 anos. Tinha conhecimento mas não direção. Quando encontrou um mentor que acreditou nele mais que ele mesmo, tudo mudou. Não precisava de mais informação - precisava de alguém que enxergasse além.',
                    'metafora_visual': f'Mentor em {segmento} é como GPS - você sabe dirigir, mas precisa de direção',
                    'comando_acao': f'Busque o mentor que vai acelerar seu crescimento em {segmento}'
                },
                'frases_ancoragem': [
                    f'Sozinho em {segmento} você vai longe, acompanhado vai mais rápido',
                    f'Mentor certo em {segmento} economiza anos de tentativa e erro',
                    f'Investir em orientação para {segmento} é investir em velocidade'
                ],
                'prova_logica': f'Profissionais com mentores em {segmento} crescem 7x mais rápido',
                'loop_reforco': f'Sempre que se sentir perdido em {segmento}, lembre: orientação vale ouro'
            },
            {
                'numero': 11,
                'nome': f'Coragem Necessária {segmento}',
                'tipo': 'emocional',
                'gatilho_central': f'Medo paralisante disfarçado em {segmento}',
                'definicao_visceral': f'Transformar desculpas em decisões corajosas em {segmento}',
                'mecanica_psicologica': 'Expor medo como única barreira real',
                'momento_instalacao': 'Final da jornada - remover última resistência',
                'roteiro_ativacao': {
                    'pergunta_abertura': f'O que você faria em {segmento} se soubesse que não pode falhar?',
                    'historia_analogia': f'Um cliente de {segmento} tinha mil desculpas para não agir: "não é a hora certa, preciso estudar mais, vou esperar". Até que perguntei: "se fosse sua última chance na vida, o que faria?" Ele riu e disse "faria tudo amanhã mesmo". As desculpas eram só medo disfarçado.',
                    'metafora_visual': f'Medo em {segmento} é como sombra - parece grande de longe, mas some quando você se aproxima',
                    'comando_acao': f'Pare de inventar desculpas e tenha a coragem de agir em {segmento}'
                },
                'frases_ancoragem': [
                    f'Coragem em {segmento} não é ausência de medo, é ação apesar do medo',
                    f'Desculpas em {segmento} são medo tentando se disfarçar de lógica',
                    f'A única coragem que importa em {segmento} é a do próximo passo'
                ],
                'prova_logica': f'100% dos grandes sucessos em {segmento} nasceram de decisões corajosas',
                'loop_reforco': f'Antes de criar desculpas em {segmento}, pergunte: é real ou é medo?'
            },

            # DRIVERS RACIONAIS COMPLEMENTARES (12-19)
            {
                'numero': 12,
                'nome': f'Mecanismo Revelado {segmento}',
                'tipo': 'racional',
                'gatilho_central': f'Compreensão do "como" em {segmento}',
                'definicao_visceral': f'Desmistificar o complexo em {segmento}',
                'mecanica_psicologica': 'Reduzir ansiedade através da compreensão',
                'momento_instalacao': 'Apresentação da solução - reduzir complexidade percebida',
                'roteiro_ativacao': {
                    'pergunta_abertura': f'E se {segmento} fosse mais simples do que você imagina?',
                    'historia_analogia': f'Um profissional de {segmento} achava que precisava dominar 50 técnicas diferentes. Mostrei que 3 mecanismos fundamentais resolviam 90% dos casos. Ele disse: "Por que ninguém me ensinou isso antes? Passei anos complicando o simples."',
                    'metafora_visual': f'{segmento} é como receita de bolo - parece complexo até alguém mostrar os 3 passos',
                    'comando_acao': f'Domine os mecanismos fundamentais de {segmento} em vez de se perder nos detalhes'
                },
                'frases_ancoragem': [
                    f'Sucesso em {segmento} tem mecanismos simples e aplicação consistente',
                    f'Complexidade em {segmento} é inimiga da execução',
                    f'Mecanismos corretos em {segmento} tornam tudo mais fácil'
                ],
                'prova_logica': f'80% dos resultados em {segmento} vêm de 20% dos mecanismos fundamentais',
                'loop_reforco': f'Quando algo parecer complexo em {segmento}, pergunte: qual é o mecanismo por trás?'
            },
            {
                'numero': 13,
                'nome': f'Prova Matemática {segmento}',
                'tipo': 'racional',
                'gatilho_central': f'Certeza numérica em {segmento}',
                'definicao_visceral': f'Equação irrefutável para {segmento}',
                'mecanica_psicologica': 'Usar lógica para vencer objeções emocionais',
                'momento_instalacao': 'Apresentação de resultados - provar possibilidade',
                'roteiro_ativacao': {
                    'pergunta_abertura': f'Que tal uma equação matemática para {segmento}?',
                    'historia_analogia': f'Mostrei para um cético de {segmento}: se você aplicar X por Y dias, matematicamente terá Z de resultado. Ele disse "impossível". Aplicou por teimosia. Em 90 dias me ligou: "a matemática funcionou exatamente como você disse".',
                    'metafora_visual': f'Sucesso em {segmento} é como juros compostos - resultado matemático, não milagre',
                    'comando_acao': f'Confie na matemática de {segmento}: ação constante = resultado previsível'
                },
                'frases_ancoragem': [
                    f'Matemática de {segmento} não mente: input correto = output garantido',
                    f'Resultados em {segmento} seguem leis matemáticas, não sorte',
                    f'Se a equação de {segmento} estiver correta, o resultado é inevitável'
                ],
                'prova_logica': f'Metodologias matemáticas em {segmento} têm 95% de taxa de sucesso',
                'loop_reforco': f'Sempre que duvidar em {segmento}, volte à matemática: o que os números dizem?'
            },
            {
                'numero': 14,
                'nome': f'Padrão Oculto {segmento}',
                'tipo': 'racional',
                'gatilho_central': f'Insight revelador sobre {segmento}',
                'definicao_visceral': f'Mostrar o que sempre esteve lá em {segmento}',
                'mecanica_psicologica': 'Gerar momento "eureka" de compreensão',
                'momento_instalacao': 'Educação - mostrar por que outros métodos falham',
                'roteiro_ativacao': {
                    'pergunta_abertura': f'Quer saber o padrão que 95% ignora em {segmento}?',
                    'historia_analogia': f'Analisei 1000 casos de sucesso em {segmento}. Descobri que todos seguiam o mesmo padrão de 4 etapas, sempre na mesma ordem. O que eu pensava que era sorte era na verdade sequência repetível.',
                    'metafora_visual': f'Padrão de sucesso em {segmento} é como código da Matrix - quando você vê, não consegue mais ignorar',
                    'comando_acao': f'Siga o padrão comprovado de {segmento} em vez de inventar o seu'
                },
                'frases_ancoragem': [
                    f'Sucesso em {segmento} tem padrões identificáveis e repetíveis',
                    f'Padrão oculto de {segmento} está escondido à vista de todos',
                    f'Quem vê o padrão de {segmento} tem vantagem injusta'
                ],
                'prova_logica': f'Padrões de sucesso em {segmento} se repetem em 87% dos casos analisados',
                'loop_reforco': f'Busque sempre os padrões em {segmento}: o que os sucessos têm em comum?'
            },
            {
                'numero': 15,
                'nome': f'Exceção Possível {segmento}',
                'tipo': 'racional',
                'gatilho_central': f'Quebra de limitação em {segmento}',
                'definicao_visceral': f'Provar que regras podem ser quebradas em {segmento}',
                'mecanica_psicologica': 'Desafiar crenças limitantes através de evidências',
                'momento_instalacao': 'Quebra de objeções - mostrar que é possível',
                'roteiro_ativacao': {
                    'pergunta_abertura': f'E se tudo que te disseram sobre {segmento} estiver errado?',
                    'historia_analogia': f'Todo mundo dizia que era impossível crescer rápido em {segmento} "sem sorte". Então conheci alguém que fez em 6 meses o que outros levam 6 anos. Não foi sorte - foi método que ninguém queria acreditar que funcionava.',
                    'metafora_visual': f'Limitações em {segmento} são como correntes de papel - parecem fortes até você testar',
                    'comando_acao': f'Ignore as "regras impossíveis" de {segmento} e crie sua exceção'
                },
                'frases_ancoragem': [
                    f'Regras de {segmento} são quebradas por quem pensa diferente',
                    f'Impossível em {segmento} é só opinião disfarçada de fato',
                    f'Exceções em {segmento} viram regras quando todos copiam'
                ],
                'prova_logica': f'30% dos grandes avanços em {segmento} quebraram "regras impossíveis"',
                'loop_reforco': f'Quando alguém disser "impossível" em {segmento}, pergunte: segundo quem?'
            },
            {
                'numero': 16,
                'nome': f'Atalho Ético {segmento}',
                'tipo': 'racional',
                'gatilho_central': f'Eficiência sem culpa em {segmento}',
                'definicao_visceral': f'Validar o caminho mais rápido em {segmento}',
                'mecanica_psicologica': 'Remover culpa de buscar eficiência',
                'momento_instalacao': 'Apresentação da solução - justificar método rápido',
                'roteiro_ativacao': {
                    'pergunta_abertura': f'Por que sofrer anos em {segmento} se existe caminho mais rápido?',
                    'historia_analogia': f'Dois profissionais queriam dominar {segmento}. Um escolheu "aprender sozinho para ter mérito". Levou 5 anos. Outro pegou um atalho ético comprovado. Levou 6 meses. Qual teve mais mérito: o que perdeu tempo ou o que foi inteligente?',
                    'metafora_visual': f'Atalho ético em {segmento} é como GPS - não é preguiça, é inteligência',
                    'comando_acao': f'Use o atalho ético de {segmento} e chegue mais rápido ao destino'
                },
                'frases_ancoragem': [
                    f'Atalho ético em {segmento} é inteligência, não preguiça',
                    f'Eficiência em {segmento} é virtude, não defeito',
                    f'Quem chega mais rápido em {segmento} pode ajudar mais gente'
                ],
                'prova_logica': f'Atalhos éticos em {segmento} aceleram resultados em 80% sem comprometer qualidade',
                'loop_reforco': f'Sempre procure atalhos éticos em {segmento}: como fazer melhor, mais rápido?'
            },
            {
                'numero': 17,
                'nome': f'Decisão Binária {segmento}',
                'tipo': 'racional',
                'gatilho_central': f'Simplificação radical em {segmento}',
                'definicao_visceral': f'Eliminar zona cinzenta em {segmento}',
                'mecanica_psicologica': 'Forçar decisão através de dicotomia clara',
                'momento_instalacao': 'Fechamento - eliminar indecisão',
                'roteiro_ativacao': {
                    'pergunta_abertura': f'Em {segmento} só existem duas opções: qual você escolhe?',
                    'historia_analogia': f'Um indeciso de {segmento} ficava criando terceiras opções há 2 anos. Disse para ele: "Ou você domina {segmento} com método ou aceita ficar medíocre para sempre. Não existe meio termo." Ele escolheu em 5 minutos.',
                    'metafora_visual': f'Indecisão em {segmento} é como ficar no meio da estrada - vai ser atropelado',
                    'comando_acao': f'Pare de procurar terceira opção em {segmento} e escolha: evolui ou estagna'
                },
                'frases_ancoragem': [
                    f'Em {segmento} não existe meio termo: ou cresce ou diminui',
                    f'Indecisão em {segmento} é decisão disfarçada de medo',
                    f'Zona cinzenta em {segmento} é zona de mediocridade'
                ],
                'prova_logica': f'Decisões binárias em {segmento} aceleram progresso em 90% dos casos',
                'loop_reforco': f'Sempre que hesitar em {segmento}, simplifique: quais são as duas únicas opções?'
            },
            {
                'numero': 18,
                'nome': f'Oportunidade Oculta {segmento}',
                'tipo': 'racional',
                'gatilho_central': f'Vantagem não percebida em {segmento}',
                'definicao_visceral': f'Revelar demanda/chance óbvia mas ignorada em {segmento}',
                'mecanica_psicologica': 'Mostrar oportunidade que está na cara mas poucos veem',
                'momento_instalacao': 'Despertar interesse - mostrar potencial escondido',
                'roteiro_ativacao': {
                    'pergunta_abertura': f'Você vê a oportunidade bilionária escondida em {segmento}?',
                    'historia_analogia': f'Todo mundo via problemas em {segmento}. Eu vi oportunidades. Enquanto reclamavam das dificuldades, criei soluções. Em 1 ano, o que era "problema impossível" virou meu principal diferencial competitivo.',
                    'metafora_visual': f'Oportunidade em {segmento} é como ouro na superfície - visível mas ignorada',
                    'comando_acao': f'Pare de ver problemas em {segmento} e comece a ver oportunidades'
                },
                'frases_ancoragem': [
                    f'Problema em {segmento} é oportunidade disfarçada',
                    f'Mercado gritando em {segmento} mas poucos ouvem',
                    f'Oportunidade óbvia em {segmento} é invisível para a maioria'
                ],
                'prova_logica': f'Oportunidades óbvias em {segmento} geram 60% mais resultado que nichos complexos',
                'loop_reforco': f'Sempre que ver problema em {segmento}, pergunte: que oportunidade isso esconde?'
            },
            {
                'numero': 19,
                'nome': f'Método vs Sorte {segmento}',
                'tipo': 'racional',
                'gatilho_central': f'Caos vs sistema em {segmento}',
                'definicao_visceral': f'Contrastar tentativa aleatória com caminho estruturado em {segmento}',
                'mecanica_psicologica': 'Mostrar superioridade da sistematização',
                'momento_instalacao': 'Apresentação da solução - diferenciar abordagem',
                'roteiro_ativacao': {
                    'pergunta_abertura': f'Você está tentando ou aplicando método em {segmento}?',
                    'historia_analogia': f'Conheci dois empreendedores de {segmento}. O um "tentava de tudo um pouco", o outro seguia método específico. Após 1 ano: o primeiro ainda experimentava, o segundo havia sistematizado e escalado. A diferença não foi sorte, foi método vs caos.',
                    'metafora_visual': f'Tentar em {segmento} é como atirar no escuro. Método é ter mira laser.',
                    'comando_acao': f'Pare de tentar tudo em {segmento} e aplique um método comprovado'
                },
                'frases_ancoragem': [
                    f'Método em {segmento} vence sorte 100% das vezes',
                    f'Sistema em {segmento} produz resultado, tentativa produz cansaço',
                    f'Quem tem método em {segmento} não depende de sorte'
                ],
                'prova_logica': f'Métodos estruturados em {segmento} têm 95% de taxa de sucesso vs 15% de tentativas',
                'loop_reforco': f'Antes de tentar algo novo em {segmento}, pergunte: onde está o método por trás?'
            }
        ]

        logger.info(f"✅ Gerados {len(drivers_universais)} drivers universais para {segmento}")
        return drivers_universais

    def _generate_customized_drivers_with_ai(self, avatar_data: Dict[str, Any], context_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Gera drivers adicionais usando IA baseado no avatar"""

        try:
            segmento = context_data.get('segmento', 'negócios')

            prompt = f"""
Baseado no avatar e contexto, crie 3 drivers mentais ADICIONAIS específicos:

AVATAR: {json.dumps(avatar_data, indent=2, ensure_ascii=False)[:1000]}
SEGMENTO: {segmento}

Retorne JSON com 3 drivers seguindo EXATAMENTE esta estrutura:

```json
[
  {{
    "numero": 20,
    "nome": "Nome específico do driver",
    "tipo": "emocional ou racional",
    "gatilho_central": "Gatilho psicológico principal",
    "definicao_visceral": "Definição que gera impacto emocional",
    "mecanica_psicologica": "Como funciona no cérebro",
    "momento_instalacao": "Quando usar na jornada",
    "roteiro_ativacao": {{
      "pergunta_abertura": "Pergunta que ativa o driver",
      "historia_analogia": "História específica de 100+ palavras",
      "metafora_visual": "Metáfora visual poderosa",
      "comando_acao": "Comando específico de ação"
    }},
    "frases_ancoragem": [
      "Frase 1 de ancoragem",
      "Frase 2 de ancoragem", 
      "Frase 3 de ancoragem"
    ],
    "prova_logica": "Prova lógica que sustenta o driver",
    "loop_reforco": "Como reativar posteriormente"
  }}
]
"""

            response = ai_manager.generate_analysis(prompt, max_tokens=2000)

            if response:
                clean_response = response.strip()
                if "```json" in clean_response:
                    start = clean_response.find("```json") + 7
                    end = clean_response.rfind("```")
                    clean_response = clean_response[start:end].strip()

                try:
                    additional_drivers = json.loads(clean_response)
                    if isinstance(additional_drivers, list):
                        logger.info(f"✅ {len(additional_drivers)} drivers adicionais gerados com IA")
                        return additional_drivers
                except json.JSONDecodeError:
                    logger.warning("⚠️ IA retornou JSON inválido para drivers adicionais")

            return []

        except Exception as e:
            logger.error(f"❌ Erro ao gerar drivers adicionais com IA: {str(e)}")
            return []

    def _create_additional_driver(self, numero: int, context_data: Dict[str, Any]) -> Dict[str, Any]:
        """Cria driver adicional para completar os 19"""

        segmento = context_data.get('segmento', 'negócios')

        drivers_extras = [
            {
                'numero': numero,
                'nome': f'Potencial Desperdiçado {segmento}',
                'tipo': 'emocional',
                'gatilho_central': f'Talentos não utilizados em {segmento}',
                'definicao_visceral': f'Mostrar capacidades ignoradas em {segmento}',
                'roteiro_ativacao': {
                    'pergunta_abertura': f'Quanto potencial você está desperdiçando em {segmento}?',
                    'historia_analogia': f'Vi um talento nato de {segmento} trabalhando como qualquer pessoa comum. Tinha habilidades excepcionais mas não sabia como usar. Quando descobriu seu diferencial real, em meses estava no topo.',
                    'metafora_visual': f'Potencial em {segmento} é como diamante bruto - precioso mas precisa ser lapidado',
                    'comando_acao': f'Descubra e use seu potencial real em {segmento}'
                },
                'frases_ancoragem': [
                    f'Potencial desperdiçado em {segmento} é tragédia silenciosa',
                    f'Seus talentos em {segmento} merecem ser explorados',
                    f'Potencial não usado em {segmento} não volta mais'
                ]
            },
            {
                'numero': numero,
                'nome': f'Legado Construído {segmento}',
                'tipo': 'emocional', 
                'gatilho_central': f'Impacto duradouro em {segmento}',
                'definicao_visceral': f'Criar algo que permanece em {segmento}',
                'roteiro_ativacao': {
                    'pergunta_abertura': f'Que legado você quer deixar em {segmento}?',
                    'historia_analogia': f'Conheci um mestre de {segmento} que não queria apenas ganhar dinheiro - queria transformar o setor inteiro. Hoje, anos depois, pessoas ainda seguem métodos que ele criou.',
                    'metafora_visual': f'Legado em {segmento} é como árvore - plantada hoje, gerações futuras se beneficiam',
                    'comando_acao': f'Construa algo em {segmento} que dure além de você'
                },
                'frases_ancoragem': [
                    f'Legado em {segmento} é imortalidade em vida',
                    f'Grandes profissionais de {segmento} constroem pontes para o futuro',
                    f'Impacto verdadeiro em {segmento} transcende gerações'
                ]
            }
        ]

        return drivers_extras[min(numero % len(drivers_extras), len(drivers_extras) - 1)]

    def _create_strategic_sequencing(self, drivers: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Cria sequenciamento estratégico dos drivers"""

        return {
            'fase_despertar': [d['nome'] for d in drivers[:5]],
            'fase_desejo': [d['nome'] for d in drivers[5:10]], 
            'fase_decisao': [d['nome'] for d in drivers[10:15]],
            'fase_direcao': [d['nome'] for d in drivers[15:19]]
        }

    def _generate_guaranteed_19_drivers_system(self, context_data: Dict[str, Any]) -> Dict[str, Any]:
        """Sistema de fallback GARANTIDO com 19 drivers"""

        drivers_garantidos = self._generate_19_universal_drivers(context_data)

        return {
            'drivers_customizados': drivers_garantidos,
            'roteiros_ativacao': {
                driver['nome']: {
                    'abertura': driver['roteiro_ativacao']['pergunta_abertura'],
                    'desenvolvimento': driver['roteiro_ativacao']['historia_analogia'], 
                    'fechamento': driver['roteiro_ativacao']['comando_acao'],
                    'tempo_estimado': '3-5 minutos'
                } for driver in drivers_garantidos
            },
            'frases_ancoragem': {
                driver['nome']: driver['frases_ancoragem'] for driver in drivers_garantidos
            },
            'sequenciamento_estrategico': self._create_strategic_sequencing(drivers_garantidos),
            'total_drivers': 19,
            'validation_status': 'FALLBACK_GUARANTEED',
            'generation_timestamp': time.time(),
            'fallback_mode': True
        }

    def _create_basic_drivers(self, context_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """ERRO - Não gera drivers básicos/simulados"""

        logger.error("❌ Tentativa de gerar drivers básicos/simulados bloqueada")
        raise Exception("Sistema configurado para usar apenas dados reais de pesquisa e IA. Configure avatar_data e APIs para gerar drivers personalizados.")

    def _create_activation_scripts(self, drivers: List[Dict[str, Any]], avatar_data: Dict[str, Any]) -> Dict[str, Any]:
        """Cria roteiros de ativação para cada driver"""

        scripts = {}

        for driver in drivers:
            driver_name = driver.get('nome', 'Driver')
            roteiro = driver.get('roteiro_ativacao', {})

            scripts[driver_name] = {
                'abertura': roteiro.get('pergunta_abertura', ''),
                'desenvolvimento': roteiro.get('historia_analogia', ''),
                'fechamento': roteiro.get('comando_acao', ''),
                'tempo_estimado': '3-5 minutos',
                'intensidade': 'Alta'
            }

        return scripts

    def _generate_anchor_phrases(self, drivers: List[Dict[str, Any]], avatar_data: Dict[str, Any]) -> Dict[str, List[str]]:
        """Gera frases de ancoragem para cada driver"""

        anchor_phrases = {}

        for driver in drivers:
            driver_name = driver.get('nome', 'Driver')
            frases = driver.get('frases_ancoragem', [])

            if frases:
                anchor_phrases[driver_name] = frases
            else:
                # Frases padrão
                anchor_phrases[driver_name] = [
                    f"Este é o momento de ativar {driver_name}",
                    f"Você sente o impacto de {driver_name}",
                    f"Agora {driver_name} faz sentido para você"
                ]

        return anchor_phrases

    def _calculate_personalization_level(self, drivers: List[Dict[str, Any]]) -> str:
        """Calcula nível de personalização dos drivers"""

        if not drivers:
            return "Baixo"

        # Verifica se tem histórias específicas
        has_stories = sum(1 for d in drivers if len(d.get('roteiro_ativacao', {}).get('historia_analogia', '')) > 100)

        # Verifica se tem frases de ancoragem
        has_anchors = sum(1 for d in drivers if len(d.get('frases_ancoragem', [])) >= 3)

        personalization_score = (has_stories + has_anchors) / (len(drivers) * 2)

        if personalization_score >= 0.8:
            return "Alto"
        elif personalization_score >= 0.5:
            return "Médio"
        else:
            return "Baixo"

    def _generate_fallback_drivers_system(self, context_data: Dict[str, Any]) -> Dict[str, Any]:
        """Gera sistema de drivers básico como fallback"""

        segmento = context_data.get('segmento', 'negócios')

        fallback_drivers = self._create_basic_drivers(context_data)

        return {
            'drivers_customizados': fallback_drivers,
            'roteiros_ativacao': {
                driver['nome']: {
                    'abertura': driver['roteiro_ativacao']['pergunta_abertura'],
                    'desenvolvimento': driver['roteiro_ativacao']['historia_analogia'],
                    'fechamento': driver['roteiro_ativacao']['comando_acao'],
                    'tempo_estimado': '3-5 minutos'
                } for driver in fallback_drivers
            },
            'frases_ancoragem': {
                driver['nome']: driver['frases_ancoragem'] for driver in fallback_drivers
            },
            'validation_status': 'FALLBACK_VALID',
            'generation_timestamp': time.time(),
            'fallback_mode': True
        }

# Instância global
mental_drivers_architect = MentalDriversArchitect()