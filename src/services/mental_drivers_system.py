"""
Sistema Completo de 19 Drivers Mentais - V3.0
Implementação do sistema de ancoragem psicológica completo
"""

import os
import json
import time
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime
import logging
from enum import Enum
from enhanced_api_rotation_manager import get_api_manager

logger = logging.getLogger(__name__)

class DriverType(Enum):
    EMOCIONAL_PRIMARIO = "emocional_primario"
    RACIONAL_COMPLEMENTAR = "racional_complementar"

class FaseJornada(Enum):
    DESPERTAR = "despertar"
    DESEJO = "desejo"
    DECISAO = "decisao"
    DIRECAO = "direcao"

@dataclass
class GatilhoPsicologico:
    nome: str
    tipo: DriverType
    gatilho_central: str
    definicao_visceral: str
    mecanica_psicologica: str
    momento_instalacao: str
    pergunta_abertura: str
    historia_analogia: str
    metafora_visual: str
    comando_acao: str
    frases_ancoragem: List[str]
    prova_logica: str
    loop_reforco: str
    fase_jornada: FaseJornada
    poder_impacto: float  # 0-100

@dataclass
class DriverCustomizado:
    driver_base: GatilhoPsicologico
    contexto_nicho: str
    publico_alvo: str
    roteiro_ativacao: Dict[str, str]
    instalacao_cpls: Dict[str, str]
    ancoragem_personalizada: List[str]
    prova_especifica: Dict[str, Any]
    sequenciamento: int

class MentalDriversSystem:
    """
    Sistema completo de 19 drivers mentais para ancoragem psicológica
    """
    
    def __init__(self):
        self.api_manager = get_api_manager()
        self.drivers_universais = self._initialize_universal_drivers()
        self.drivers_customizados = {}
        self.sequencias_otimizadas = {}
    
    def _initialize_universal_drivers(self) -> Dict[str, GatilhoPsicologico]:
        """
        Inicializa os 19 drivers universais
        """
        drivers = {}
        
        # DRIVERS EMOCIONAIS PRIMÁRIOS (1-11)
        
        # 1. DRIVER DA FERIDA EXPOSTA
        drivers['ferida_exposta'] = GatilhoPsicologico(
            nome="Ferida Exposta",
            tipo=DriverType.EMOCIONAL_PRIMARIO,
            gatilho_central="Dor não resolvida",
            definicao_visceral="Trazer à consciência o que foi reprimido e está causando sofrimento silencioso",
            mecanica_psicologica="Ativa o sistema límbico forçando confronto com realidade dolorosa evitada",
            momento_instalacao="Abertura do CPL1 - primeiros 2 minutos",
            pergunta_abertura="Você ainda [comportamento doloroso] mesmo sabendo que [consequência]?",
            historia_analogia="É como ter uma farpa no pé. Você pode ignorar, mas cada passo dói mais.",
            metafora_visual="Imagine olhar no espelho e ver não quem você é, mas quem você poderia ter sido",
            comando_acao="Pare de fingir que não dói. Reconheça a ferida para poder curá-la",
            frases_ancoragem=[
                "A dor que você evita é a que mais te controla",
                "Ferida não tratada vira gangrena emocional",
                "O que você não enfrenta, te enfrenta todos os dias"
            ],
            prova_logica="Estudos mostram que evitação aumenta sofrimento em 300%",
            loop_reforco="Toda vez que sentir desconforto, lembre: é sua ferida pedindo atenção",
            fase_jornada=FaseJornada.DESPERTAR,
            poder_impacto=95.0
        )
        
        # 2. DRIVER DO TROFÉU SECRETO
        drivers['trofeu_secreto'] = GatilhoPsicologico(
            nome="Troféu Secreto",
            tipo=DriverType.EMOCIONAL_PRIMARIO,
            gatilho_central="Desejo inconfessável",
            definicao_visceral="Validar ambições 'proibidas' que a pessoa não ousa admitir publicamente",
            mecanica_psicologica="Libera dopamina ao dar permissão para desejos reprimidos",
            momento_instalacao="CPL1 - após quebrar primeira objeção",
            pergunta_abertura="O que você realmente quer mas tem vergonha de admitir?",
            historia_analogia="É como guardar um tesouro no sótão. Você sabe que está lá, mas finge que não existe.",
            metafora_visual="Visualize-se recebendo o reconhecimento que sempre quis mas nunca pediu",
            comando_acao="Dê-se permissão para querer o que realmente deseja",
            frases_ancoragem=[
                "Não é sobre dinheiro, é sobre [desejo real oculto]",
                "Seu troféu secreto está esperando você ter coragem",
                "Ambição não é pecado, é combustível"
            ],
            prova_logica="Pessoas que admitem desejos reais têm 400% mais chance de alcançá-los",
            loop_reforco="Quando se sentir culpado por querer mais, lembre: você merece seu troféu",
            fase_jornada=FaseJornada.DESEJO,
            poder_impacto=88.0
        )
        
        # 3. DRIVER DA INVEJA PRODUTIVA
        drivers['inveja_produtiva'] = GatilhoPsicologico(
            nome="Inveja Produtiva",
            tipo=DriverType.EMOCIONAL_PRIMARIO,
            gatilho_central="Comparação com pares",
            definicao_visceral="Transformar inveja destrutiva em combustível para ação",
            mecanica_psicologica="Redireciona energia da inveja para motivação através de espelhamento",
            momento_instalacao="CPL2 - ao mostrar casos de sucesso",
            pergunta_abertura="Por que outros conseguem e você não?",
            historia_analogia="Inveja é como fogo: pode queimar sua casa ou cozinhar sua comida.",
            metafora_visual="Veja seus 'concorrentes' como professores mostrando o caminho",
            comando_acao="Use a inveja como GPS: ela mostra onde você quer chegar",
            frases_ancoragem=[
                "Enquanto você [situação atual], outros como você [resultado desejado]",
                "Inveja é sua bússola interna apontando seus verdadeiros desejos",
                "Se eles conseguiram, o caminho existe"
            ],
            prova_logica="Inveja produtiva aumenta performance em 250% segundo Harvard",
            loop_reforco="Quando sentir inveja, pergunte: o que isso me ensina sobre meus objetivos?",
            fase_jornada=FaseJornada.DESEJO,
            poder_impacto=82.0
        )
        
        # 4. DRIVER DO RELÓGIO PSICOLÓGICO
        drivers['relogio_psicologico'] = GatilhoPsicologico(
            nome="Relógio Psicológico",
            tipo=DriverType.EMOCIONAL_PRIMARIO,
            gatilho_central="Urgência existencial",
            definicao_visceral="Ativar consciência brutal da finitude do tempo",
            mecanica_psicologica="Ativa córtex pré-frontal criando senso de urgência através de mortalidade saliente",
            momento_instalacao="CPL3 - antes de revelar método",
            pergunta_abertura="Quantos [período] você ainda vai [desperdício]?",
            historia_analogia="Tempo é como areia na ampulheta. Cada grão que cai nunca volta.",
            metafora_visual="Imagine um cronômetro gigante sobre sua cabeça contando regressivamente",
            comando_acao="Pare de agir como se tivesse tempo infinito",
            frases_ancoragem=[
                "Tempo perdido é vida desperdiçada",
                "Seu relógio não para enquanto você procrastina",
                "Cada dia sem ação é um dia a menos para o resultado"
            ],
            prova_logica="Pessoas conscientes da finitude agem 300% mais rápido",
            loop_reforco="Toda manhã, lembre: hoje é um dia a menos na sua vida",
            fase_jornada=FaseJornada.DECISAO,
            poder_impacto=92.0
        )
        
        # 5. DRIVER DA IDENTIDADE APRISIONADA
        drivers['identidade_aprisionada'] = GatilhoPsicologico(
            nome="Identidade Aprisionada",
            tipo=DriverType.EMOCIONAL_PRIMARIO,
            gatilho_central="Conflito entre quem é e quem poderia ser",
            definicao_visceral="Expor a máscara social que impede o verdadeiro potencial",
            mecanica_psicologica="Cria dissonância cognitiva entre identidade atual e identidade possível",
            momento_instalacao="CPL1 - após diagnóstico brutal",
            pergunta_abertura="Quem você seria se ninguém estivesse olhando?",
            historia_analogia="É como usar roupas pequenas demais. Você se acostuma, mas nunca fica confortável.",
            metafora_visual="Visualize-se quebrando as correntes invisíveis que te prendem",
            comando_acao="Pare de ser quem os outros esperam e seja quem você é",
            frases_ancoragem=[
                "Você não é [rótulo limitante], você é [potencial real]",
                "Sua identidade atual é uma prisão que você mesmo construiu",
                "Liberdade começa quando você para de representar"
            ],
            prova_logica="Mudança de identidade aumenta performance em 400%",
            loop_reforco="Quando se pegar 'representando', pergunte: quem eu realmente sou?",
            fase_jornada=FaseJornada.DESPERTAR,
            poder_impacto=89.0
        )
        
        # 6. DRIVER DO CUSTO INVISÍVEL
        drivers['custo_invisivel'] = GatilhoPsicologico(
            nome="Custo Invisível",
            tipo=DriverType.EMOCIONAL_PRIMARIO,
            gatilho_central="Perda não percebida",
            definicao_visceral="Quantificar o preço oculto da inação",
            mecanica_psicologica="Ativa aversão à perda tornando custos implícitos explícitos",
            momento_instalacao="CPL2 - ao construir urgência",
            pergunta_abertura="Quanto está custando não agir?",
            historia_analogia="É como vazamento no encanamento. Você não vê, mas a conta chega.",
            metafora_visual="Imagine uma máquina contando o dinheiro que você perde por hora",
            comando_acao="Calcule o preço real da sua procrastinação",
            frases_ancoragem=[
                "Cada dia sem [solução] custa [perda específica]",
                "Inação tem preço, você só não recebe a conta na hora",
                "O que não se mede, não se gerencia - incluindo perdas"
            ],
            prova_logica="Custo de oportunidade médio da procrastinação: R$ 50.000/ano",
            loop_reforco="Antes de adiar, calcule: quanto isso vai me custar?",
            fase_jornada=FaseJornada.DECISAO,
            poder_impacto=85.0
        )
        
        # 7. DRIVER DA AMBIÇÃO EXPANDIDA
        drivers['ambicao_expandida'] = GatilhoPsicologico(
            nome="Ambição Expandida",
            tipo=DriverType.EMOCIONAL_PRIMARIO,
            gatilho_central="Sonhos pequenos demais",
            definicao_visceral="Elevar o teto mental de possibilidades",
            mecanica_psicologica="Expande zona de conforto através de ancoragem em objetivos maiores",
            momento_instalacao="CPL2 - após mostrar transformações",
            pergunta_abertura="Por que você está pedindo tão pouco da vida?",
            historia_analogia="É como pedir desconto em loja de R$ 1,99. O esforço é o mesmo, o resultado ridículo.",
            metafora_visual="Visualize-se em um elevador: você pode apertar qualquer andar",
            comando_acao="Se o esforço é o mesmo, mire mais alto",
            frases_ancoragem=[
                "Se o esforço é o mesmo, por que você está pedindo tão pouco?",
                "Sonho pequeno é insulto ao seu potencial",
                "Você foi feito para coisas maiores"
            ],
            prova_logica="Pessoas com objetivos 10x maiores alcançam 300% mais",
            loop_reforco="Quando definir meta, pergunte: posso sonhar maior?",
            fase_jornada=FaseJornada.DESEJO,
            poder_impacto=91.0
        )
        
        # 8. DRIVER DO DIAGNÓSTICO BRUTAL
        drivers['diagnostico_brutal'] = GatilhoPsicologico(
            nome="Diagnóstico Brutal",
            tipo=DriverType.EMOCIONAL_PRIMARIO,
            gatilho_central="Confronto com a realidade atual",
            definicao_visceral="Criar indignação produtiva com status quo",
            mecanica_psicologica="Gera tensão psicológica através de confronto direto com realidade",
            momento_instalacao="Abertura do CPL1 - primeiros 5 minutos",
            pergunta_abertura="Olhe seus números/situação. Até quando você vai aceitar isso?",
            historia_analogia="É como médico mostrando raio-X: dói ver, mas é necessário para curar.",
            metafora_visual="Imagine-se olhando sua vida de fora, como observador imparcial",
            comando_acao="Pare de maquiar a realidade e encare os fatos",
            frases_ancoragem=[
                "Números não mentem, pessoas se iludem",
                "Realidade é sua melhor professora, mesmo sendo cruel",
                "Diagnóstico doloroso é primeiro passo para cura"
            ],
            prova_logica="Autoconhecimento brutal aumenta mudança comportamental em 400%",
            loop_reforco="Mensalmente, faça diagnóstico brutal: onde estou realmente?",
            fase_jornada=FaseJornada.DESPERTAR,
            poder_impacto=94.0
        )
        
        # 9. DRIVER DO AMBIENTE VAMPIRO
        drivers['ambiente_vampiro'] = GatilhoPsicologico(
            nome="Ambiente Vampiro",
            tipo=DriverType.EMOCIONAL_PRIMARIO,
            gatilho_central="Consciência do entorno tóxico",
            definicao_visceral="Revelar como ambiente atual suga energia/potencial",
            mecanica_psicologica="Cria aversão ao ambiente atual através de metáfora de vampirismo energético",
            momento_instalacao="CPL2 - ao explicar por que outros falham",
            pergunta_abertura="Seu ambiente te impulsiona ou te mantém pequeno?",
            historia_analogia="Ambiente tóxico é como ar poluído: você se acostuma, mas está sempre se envenenando.",
            metafora_visual="Visualize vampiros invisíveis sugando sua energia e ambição",
            comando_acao="Identifique e elimine os vampiros do seu ambiente",
            frases_ancoragem=[
                "Você é a média das 5 pessoas com quem mais convive",
                "Ambiente vampiro suga sonhos sem você perceber",
                "Mudança de ambiente = mudança de vida"
            ],
            prova_logica="Ambiente influencia 70% dos resultados segundo Stanford",
            loop_reforco="Semanalmente avalie: meu ambiente me fortalece ou enfraquece?",
            fase_jornada=FaseJornada.DESPERTAR,
            poder_impacto=87.0
        )
        
        # 10. DRIVER DO MENTOR SALVADOR
        drivers['mentor_salvador'] = GatilhoPsicologico(
            nome="Mentor Salvador",
            tipo=DriverType.EMOCIONAL_PRIMARIO,
            gatilho_central="Necessidade de orientação externa",
            definicao_visceral="Ativar desejo por figura de autoridade que acredita neles",
            mecanica_psicologica="Ativa necessidade de aprovação e orientação parental",
            momento_instalacao="CPL3 - ao apresentar método",
            pergunta_abertura="Quando foi a última vez que alguém realmente acreditou em você?",
            historia_analogia="É como estar perdido na floresta e ver uma luz: alívio instantâneo.",
            metafora_visual="Visualize alguém estendendo a mão para te tirar do buraco",
            comando_acao="Aceite a orientação de quem já percorreu o caminho",
            frases_ancoragem=[
                "Você precisa de alguém que veja seu potencial quando você não consegue",
                "Mentor certo economiza 10 anos de tentativa e erro",
                "Sozinho você vai rápido, acompanhado vai longe"
            ],
            prova_logica="Pessoas com mentores crescem 500% mais rápido",
            loop_reforco="Quando se sentir perdido, busque quem já chegou onde quer ir",
            fase_jornada=FaseJornada.DIRECAO,
            poder_impacto=83.0
        )
        
        # 11. DRIVER DA CORAGEM NECESSÁRIA
        drivers['coragem_necessaria'] = GatilhoPsicologico(
            nome="Coragem Necessária",
            tipo=DriverType.EMOCIONAL_PRIMARIO,
            gatilho_central="Medo paralisante disfarçado",
            definicao_visceral="Transformar desculpas em decisões corajosas",
            mecanica_psicologica="Reframe medo como sinal de direção certa",
            momento_instalacao="CPL4 - momento da decisão",
            pergunta_abertura="O que você faria se soubesse que não pode falhar?",
            historia_analogia="Coragem não é ausência de medo, é ação apesar do medo.",
            metafora_visual="Visualize-se saltando de paraquedas: o medo existe, mas você salta",
            comando_acao="Não é sobre condições perfeitas, é sobre decidir apesar do medo",
            frases_ancoragem=[
                "Medo é bússola apontando para seu crescimento",
                "Coragem é músculo: quanto mais usa, mais forte fica",
                "Do outro lado do medo está sua vida extraordinária"
            ],
            prova_logica="Ação corajosa libera dopamina e constrói autoconfiança",
            loop_reforco="Quando sentir medo, pergunte: o que isso está me mostrando?",
            fase_jornada=FaseJornada.DECISAO,
            poder_impacto=90.0
        )
        
        # DRIVERS RACIONAIS COMPLEMENTARES (12-19)
        
        # 12. DRIVER DO MECANISMO REVELADO
        drivers['mecanismo_revelado'] = GatilhoPsicologico(
            nome="Mecanismo Revelado",
            tipo=DriverType.RACIONAL_COMPLEMENTAR,
            gatilho_central="Compreensão do 'como'",
            definicao_visceral="Desmistificar o complexo tornando-o simples",
            mecanica_psicologica="Reduz ansiedade através de compreensão clara do processo",
            momento_instalacao="CPL3 - revelação do método",
            pergunta_abertura="Quer saber como realmente funciona?",
            historia_analogia="É como ver truque de mágica sendo explicado: simples quando você sabe.",
            metafora_visual="Imagine abrir o capô do carro e entender cada peça",
            comando_acao="Entenda o mecanismo para dominar o resultado",
            frases_ancoragem=[
                "É simplesmente [analogia simples], não [complicação percebida]",
                "Complexo é só simples mal explicado",
                "Quando você entende como, o impossível vira inevitável"
            ],
            prova_logica="Compreensão clara aumenta execução em 300%",
            loop_reforco="Sempre pergunte: qual é o mecanismo por trás disso?",
            fase_jornada=FaseJornada.DIRECAO,
            poder_impacto=78.0
        )
        
        # 13. DRIVER DA PROVA MATEMÁTICA
        drivers['prova_matematica'] = GatilhoPsicologico(
            nome="Prova Matemática",
            tipo=DriverType.RACIONAL_COMPLEMENTAR,
            gatilho_central="Certeza numérica",
            definicao_visceral="Criar equação irrefutável de causa e efeito",
            mecanica_psicologica="Ativa córtex lógico criando sensação de certeza",
            momento_instalacao="CPL3 - validação do método",
            pergunta_abertura="Quer ver a matemática por trás do resultado?",
            historia_analogia="Matemática não mente: 2+2 sempre será 4, independente da opinião.",
            metafora_visual="Visualize uma calculadora gigante mostrando sua equação de sucesso",
            comando_acao="Confie nos números, eles não mentem",
            frases_ancoragem=[
                "Se você fizer X por Y dias = Resultado Z garantido",
                "Matemática do sucesso é simples: consistência × tempo = resultado",
                "Números não têm opinião, só mostram realidade"
            ],
            prova_logica="Decisões baseadas em dados têm 85% mais chance de sucesso",
            loop_reforco="Sempre pergunte: qual é a matemática por trás?",
            fase_jornada=FaseJornada.DIRECAO,
            poder_impacto=81.0
        )
        
        # 14. DRIVER DO PADRÃO OCULTO
        drivers['padrao_oculto'] = GatilhoPsicologico(
            nome="Padrão Oculto",
            tipo=DriverType.RACIONAL_COMPLEMENTAR,
            gatilho_central="Insight revelador",
            definicao_visceral="Mostrar o que sempre esteve lá mas ninguém viu",
            mecanica_psicologica="Gera 'aha moment' através de reconhecimento de padrões",
            momento_instalacao="CPL2 - ao mostrar casos de sucesso",
            pergunta_abertura="Quer ver o padrão que todos os bem-sucedidos seguem?",
            historia_analogia="É como ver constelação no céu: as estrelas sempre estiveram lá.",
            metafora_visual="Imagine conectar pontos e ver o desenho aparecer",
            comando_acao="Siga o padrão que já foi testado e aprovado",
            frases_ancoragem=[
                "Todos que conseguiram [resultado] fizeram [padrão específico]",
                "Sucesso deixa pistas, fracasso deixa desculpas",
                "Padrão é receita: siga e terá o mesmo resultado"
            ],
            prova_logica="Reconhecimento de padrões acelera aprendizado em 400%",
            loop_reforco="Sempre procure: qual é o padrão dos bem-sucedidos?",
            fase_jornada=FaseJornada.DIRECAO,
            poder_impacto=84.0
        )
        
        # 15. DRIVER DA EXCEÇÃO POSSÍVEL
        drivers['excecao_possivel'] = GatilhoPsicologico(
            nome="Exceção Possível",
            tipo=DriverType.RACIONAL_COMPLEMENTAR,
            gatilho_central="Quebra de limitação",
            definicao_visceral="Provar que regras podem ser quebradas",
            mecanica_psicologica="Expande modelo mental através de exemplos contrários",
            momento_instalacao="CPL1 - quebra de objeções",
            pergunta_abertura="E se tudo que te disseram fosse mentira?",
            historia_analogia="Diziam que homem não podia voar, até os irmãos Wright provarem o contrário.",
            metafora_visual="Visualize-se quebrando uma parede que parecia sólida",
            comando_acao="Questione as regras que limitam seu potencial",
            frases_ancoragem=[
                "Diziam que [limitação], mas [prova contrária]",
                "Regras são para quem não sabe quebrá-las inteligentemente",
                "Impossível é opinião, não fato"
            ],
            prova_logica="Pessoas que questionam limitações inovam 600% mais",
            loop_reforco="Quando ouvir 'impossível', pergunte: quem já provou o contrário?",
            fase_jornada=FaseJornada.DESPERTAR,
            poder_impacto=79.0
        )
        
        # 16. DRIVER DO ATALHO ÉTICO
        drivers['atalho_etico'] = GatilhoPsicologico(
            nome="Atalho Ético",
            tipo=DriverType.RACIONAL_COMPLEMENTAR,
            gatilho_central="Eficiência sem culpa",
            definicao_visceral="Validar o caminho mais rápido sem comprometer valores",
            mecanica_psicologica="Remove culpa de eficiência através de validação ética",
            momento_instalacao="CPL3 - apresentação do método",
            pergunta_abertura="Por que sofrer mais tempo se existe caminho mais rápido?",
            historia_analogia="Atalho não é trapaça quando é estrada pavimentada por quem veio antes.",
            metafora_visual="Visualize dois caminhos: um longo e pedregoso, outro curto e seguro",
            comando_acao="Escolha eficiência inteligente, não sofrimento desnecessário",
            frases_ancoragem=[
                "Por que sofrer [tempo longo] se existe [atalho comprovado]?",
                "Atalho ético é inteligência, não preguiça",
                "Tempo economizado é vida ganha"
            ],
            prova_logica="Atalhos éticos reduzem tempo de resultado em 70%",
            loop_reforco="Sempre pergunte: existe forma mais eficiente e ética?",
            fase_jornada=FaseJornada.DIRECAO,
            poder_impacto=76.0
        )
        
        # 17. DRIVER DA DECISÃO BINÁRIA
        drivers['decisao_binaria'] = GatilhoPsicologico(
            nome="Decisão Binária",
            tipo=DriverType.RACIONAL_COMPLEMENTAR,
            gatilho_central="Simplificação radical",
            definicao_visceral="Eliminar zona cinzenta forçando escolha clara",
            mecanica_psicologica="Reduz paralisia de análise através de simplificação extrema",
            momento_instalacao="CPL4 - momento da decisão final",
            pergunta_abertura="Qual vai ser: sim ou não?",
            historia_analogia="Na vida, você está sempre escolhendo: crescer ou estagnar, avançar ou recuar.",
            metafora_visual="Visualize duas portas: uma leva ao futuro desejado, outra ao passado",
            comando_acao="Pare de procurar terceira opção quando só existem duas",
            frases_ancoragem=[
                "Ou você [ação desejada] ou aceita [consequência dolorosa]",
                "Não decidir é decidir ficar onde está",
                "Zona cinzenta é zona de morte lenta"
            ],
            prova_logica="Decisões binárias aumentam ação em 200%",
            loop_reforco="Em dúvida, simplifique: quais são as duas únicas opções?",
            fase_jornada=FaseJornada.DECISAO,
            poder_impacto=88.0
        )
        
        # 18. DRIVER DA OPORTUNIDADE OCULTA
        drivers['oportunidade_oculta'] = GatilhoPsicologico(
            nome="Oportunidade Oculta",
            tipo=DriverType.RACIONAL_COMPLEMENTAR,
            gatilho_central="Vantagem não percebida",
            definicao_visceral="Revelar demanda/chance óbvia mas ignorada",
            mecanica_psicologica="Ativa FOMO através de revelação de oportunidade limitada",
            momento_instalacao="CPL1 - criação de urgência",
            pergunta_abertura="Você vê o que está bem na sua frente?",
            historia_analogia="Oportunidade é como ouro no rio: está lá, mas só quem procura encontra.",
            metafora_visual="Imagine uma porta dourada que só você pode ver",
            comando_acao="Agarre a oportunidade antes que outros a vejam",
            frases_ancoragem=[
                "O mercado está gritando por [solução] e ninguém está ouvindo",
                "Oportunidade não bate na porta, ela sussurra",
                "Quem vê primeiro, lucra primeiro"
            ],
            prova_logica="Primeiros a identificar oportunidades lucram 500% mais",
            loop_reforco="Sempre pergunte: que oportunidade todos estão ignorando?",
            fase_jornada=FaseJornada.DESPERTAR,
            poder_impacto=86.0
        )
        
        # 19. DRIVER DO MÉTODO VS SORTE
        drivers['metodo_vs_sorte'] = GatilhoPsicologico(
            nome="Método vs Sorte",
            tipo=DriverType.RACIONAL_COMPLEMENTAR,
            gatilho_central="Caos vs sistema",
            definicao_visceral="Contrastar tentativa aleatória com caminho estruturado",
            mecanica_psicologica="Cria preferência por certeza através de contraste com aleatoriedade",
            momento_instalacao="CPL3 - validação do sistema",
            pergunta_abertura="Você prefere apostar na sorte ou seguir método comprovado?",
            historia_analogia="Sem método você está cortando mata com foice. Com método, está na autoestrada.",
            metafora_visual="Visualize dois viajantes: um com GPS, outro perdido na floresta",
            comando_acao="Pare de improvisar e comece a seguir sistema",
            frases_ancoragem=[
                "Sorte é quando preparação encontra oportunidade",
                "Método transforma acaso em certeza",
                "Sistema é sorte organizada"
            ],
            prova_logica="Métodos estruturados aumentam sucesso em 400%",
            loop_reforco="Sempre pergunte: estou seguindo método ou apostando na sorte?",
            fase_jornada=FaseJornada.DIRECAO,
            poder_impacto=85.0
        )
        
        return drivers
    
    def get_drivers_por_fase(self, fase: FaseJornada) -> List[GatilhoPsicologico]:
        """
        Retorna drivers recomendados para cada fase da jornada
        """
        return [driver for driver in self.drivers_universais.values() 
                if driver.fase_jornada == fase]
    
    def get_top_drivers_essenciais(self) -> List[GatilhoPsicologico]:
        """
        Retorna os 7 drivers mais poderosos (Top essenciais)
        """
        drivers_ordenados = sorted(self.drivers_universais.values(), 
                                 key=lambda x: x.poder_impacto, reverse=True)
        return drivers_ordenados[:7]
    
    def customizar_drivers_para_nicho(self, drivers_selecionados: List[str], 
                                    contexto_nicho: str, publico_alvo: str,
                                    dados_pesquisa: Dict[str, Any]) -> List[DriverCustomizado]:
        """
        Customiza drivers universais para nicho específico
        """
        drivers_customizados = []
        
        for i, driver_nome in enumerate(drivers_selecionados):
            if driver_nome not in self.drivers_universais:
                continue
            
            driver_base = self.drivers_universais[driver_nome]
            
            # Gerar customização usando IA
            customizacao = self._gerar_customizacao_driver(
                driver_base, contexto_nicho, publico_alvo, dados_pesquisa
            )
            
            driver_customizado = DriverCustomizado(
                driver_base=driver_base,
                contexto_nicho=contexto_nicho,
                publico_alvo=publico_alvo,
                roteiro_ativacao=customizacao['roteiro_ativacao'],
                instalacao_cpls=customizacao['instalacao_cpls'],
                ancoragem_personalizada=customizacao['ancoragem_personalizada'],
                prova_especifica=customizacao['prova_especifica'],
                sequenciamento=i + 1
            )
            
            drivers_customizados.append(driver_customizado)
        
        return drivers_customizados
    
    def _gerar_customizacao_driver(self, driver: GatilhoPsicologico, 
                                  contexto_nicho: str, publico_alvo: str,
                                  dados_pesquisa: Dict[str, Any]) -> Dict[str, Any]:
        """
        Gera customização específica para um driver
        """
        prompt = f"""
        # CUSTOMIZAÇÃO DE DRIVER MENTAL PARA NICHO ESPECÍFICO
        
        ## DRIVER BASE: {driver.nome}
        - **Gatilho Central**: {driver.gatilho_central}
        - **Definição**: {driver.definicao_visceral}
        - **Mecânica**: {driver.mecanica_psicologica}
        
        ## CONTEXTO DO NICHO
        - **Nicho**: {contexto_nicho}
        - **Público**: {publico_alvo}
        - **Dados da Pesquisa**: {json.dumps(dados_pesquisa, indent=2)[:500]}
        
        ## TAREFA: CUSTOMIZAÇÃO COMPLETA
        
        Customize este driver para o nicho específico seguindo a estrutura:
        
        ### 1. ROTEIRO DE ATIVAÇÃO CUSTOMIZADO
        - **Pergunta de Abertura**: Adaptada para o nicho
        - **História/Analogia**: Usando referências do universo do público
        - **Metáfora Visual**: Específica para o contexto
        - **Comando de Ação**: Linguagem do nicho
        
        ### 2. INSTALAÇÃO NOS CPLs
        - **CPL1**: Como e quando usar
        - **CPL2**: Desenvolvimento específico
        - **CPL3**: Aprofundamento no nicho
        - **CPL4**: Fechamento personalizado
        
        ### 3. ANCORAGEM PERSONALIZADA
        - 5 frases específicas do nicho
        - Usando linguagem/gírias do público
        - Referências culturais relevantes
        
        ### 4. PROVA ESPECÍFICA
        - Dados do nicho
        - Casos reais do segmento
        - Estatísticas relevantes
        
        Formato JSON:
        {{
            "roteiro_ativacao": {{
                "pergunta_abertura": "Pergunta customizada",
                "historia_analogia": "História específica do nicho",
                "metafora_visual": "Metáfora relevante",
                "comando_acao": "Ação específica"
            }},
            "instalacao_cpls": {{
                "cpl1": "Como usar no CPL1",
                "cpl2": "Como usar no CPL2",
                "cpl3": "Como usar no CPL3",
                "cpl4": "Como usar no CPL4"
            }},
            "ancoragem_personalizada": [
                "Frase 1 específica",
                "Frase 2 específica",
                "Frase 3 específica",
                "Frase 4 específica",
                "Frase 5 específica"
            ],
            "prova_especifica": {{
                "dados_nicho": "Estatística específica",
                "caso_real": "Exemplo do segmento",
                "referencia_cultural": "Referência relevante"
            }}
        }}
        
        CRÍTICO: Use apenas linguagem e referências ESPECÍFICAS do nicho!
        """
        
        try:
            api = self.api_manager.get_active_api('qwen')
            if not api:
                _, api = self.api_manager.get_fallback_model('qwen')
            
            if api:
                response = self._generate_with_ai(prompt, api)
                return json.loads(response)
            else:
                # Fallback com customização básica
                return self._gerar_customizacao_basica(driver, contexto_nicho, publico_alvo)
                
        except Exception as e:
            logger.error(f"❌ Erro na customização: {e}")
            return self._gerar_customizacao_basica(driver, contexto_nicho, publico_alvo)
    
    def _gerar_customizacao_basica(self, driver: GatilhoPsicologico, 
                                  contexto_nicho: str, publico_alvo: str) -> Dict[str, Any]:
        """
        Gera customização básica quando IA não está disponível
        """
        return {
            "roteiro_ativacao": {
                "pergunta_abertura": f"{driver.pergunta_abertura} (adaptado para {contexto_nicho})",
                "historia_analogia": f"{driver.historia_analogia} (contexto: {contexto_nicho})",
                "metafora_visual": f"{driver.metafora_visual} (para {publico_alvo})",
                "comando_acao": f"{driver.comando_acao} (específico para {contexto_nicho})"
            },
            "instalacao_cpls": {
                "cpl1": f"Usar {driver.nome} na abertura",
                "cpl2": f"Desenvolver {driver.nome} com casos",
                "cpl3": f"Aprofundar {driver.nome} no método",
                "cpl4": f"Fechar com {driver.nome} na decisão"
            },
            "ancoragem_personalizada": [
                f"{frase} (adaptado para {contexto_nicho})" 
                for frase in driver.frases_ancoragem[:3]
            ] + [
                f"Frase específica 1 para {publico_alvo}",
                f"Frase específica 2 para {contexto_nicho}"
            ],
            "prova_especifica": {
                "dados_nicho": f"Estatística relevante para {contexto_nicho}",
                "caso_real": f"Exemplo real do segmento {contexto_nicho}",
                "referencia_cultural": f"Referência cultural de {publico_alvo}"
            }
        }
    
    def gerar_sequencia_otimizada(self, drivers_customizados: List[DriverCustomizado],
                                 formato_campanha: str) -> Dict[str, Any]:
        """
        Gera sequência otimizada de drivers para campanha
        """
        # Organizar por fase da jornada
        fases = {
            FaseJornada.DESPERTAR: [],
            FaseJornada.DESEJO: [],
            FaseJornada.DECISAO: [],
            FaseJornada.DIRECAO: []
        }
        
        for driver in drivers_customizados:
            fases[driver.driver_base.fase_jornada].append(driver)
        
        # Criar sequência otimizada
        sequencia = {
            "formato_campanha": formato_campanha,
            "sequencia_drivers": {
                "fase_1_despertar": [asdict(d) for d in fases[FaseJornada.DESPERTAR]],
                "fase_2_desejo": [asdict(d) for d in fases[FaseJornada.DESEJO]],
                "fase_3_decisao": [asdict(d) for d in fases[FaseJornada.DECISAO]],
                "fase_4_direcao": [asdict(d) for d in fases[FaseJornada.DIRECAO]]
            },
            "cronograma_instalacao": self._gerar_cronograma_instalacao(drivers_customizados),
            "scripts_ativacao": self._gerar_scripts_ativacao(drivers_customizados),
            "metricas_acompanhamento": self._gerar_metricas_acompanhamento(drivers_customizados)
        }
        
        return sequencia
    
    def _gerar_cronograma_instalacao(self, drivers: List[DriverCustomizado]) -> Dict[str, List[str]]:
        """Gera cronograma de instalação dos drivers"""
        return {
            "pre_lancamento": [d.driver_base.nome for d in drivers if d.driver_base.fase_jornada == FaseJornada.DESPERTAR],
            "cpl1": [d.driver_base.nome for d in drivers if d.driver_base.fase_jornada in [FaseJornada.DESPERTAR, FaseJornada.DESEJO]],
            "cpl2": [d.driver_base.nome for d in drivers if d.driver_base.fase_jornada == FaseJornada.DESEJO],
            "cpl3": [d.driver_base.nome for d in drivers if d.driver_base.fase_jornada == FaseJornada.DIRECAO],
            "cpl4": [d.driver_base.nome for d in drivers if d.driver_base.fase_jornada == FaseJornada.DECISAO]
        }
    
    def _gerar_scripts_ativacao(self, drivers: List[DriverCustomizado]) -> Dict[str, str]:
        """Gera scripts de ativação para cada driver"""
        scripts = {}
        
        for driver in drivers:
            script = f"""
# SCRIPT DE ATIVAÇÃO: {driver.driver_base.nome}

## ABERTURA
{driver.roteiro_ativacao.get('pergunta_abertura', '')}

## DESENVOLVIMENTO
{driver.roteiro_ativacao.get('historia_analogia', '')}

## VISUALIZAÇÃO
{driver.roteiro_ativacao.get('metafora_visual', '')}

## AÇÃO
{driver.roteiro_ativacao.get('comando_acao', '')}

## ANCORAGEM
{chr(10).join([f"- {frase}" for frase in driver.ancoragem_personalizada])}
"""
            scripts[driver.driver_base.nome] = script
        
        return scripts
    
    def _gerar_metricas_acompanhamento(self, drivers: List[DriverCustomizado]) -> Dict[str, List[str]]:
        """Gera métricas para acompanhar efetividade dos drivers"""
        return {
            "metricas_engajamento": [
                "Taxa de abertura de emails",
                "Tempo de permanência em vídeos",
                "Comentários por post",
                "Compartilhamentos"
            ],
            "metricas_conversao": [
                "Taxa de clique em CTAs",
                "Inscrições em lista",
                "Participação em webinars",
                "Conversão final"
            ],
            "metricas_psicologicas": [
                "Sentimento dos comentários",
                "Palavras-chave emocionais usadas",
                "Perguntas feitas pela audiência",
                "Objeções levantadas"
            ]
        }
    
    def _generate_with_ai(self, prompt: str, api) -> str:
        """Gera conteúdo usando IA"""
        try:
            # Implementar chamada real para API
            # Por enquanto retorna exemplo
            return '{"roteiro_ativacao": {"pergunta_abertura": "Exemplo"}, "instalacao_cpls": {}, "ancoragem_personalizada": [], "prova_especifica": {}}'
        except Exception as e:
            logger.error(f"❌ Erro na geração: {e}")
            raise
    
    def salvar_sistema_drivers(self, session_id: str, drivers_customizados: List[DriverCustomizado],
                              sequencia_otimizada: Dict[str, Any]) -> str:
        """
        Salva sistema completo de drivers mentais
        """
        try:
            session_dir = f"/workspace/project/v110/analyses_data/{session_id}"
            drivers_dir = os.path.join(session_dir, 'mental_drivers')
            os.makedirs(drivers_dir, exist_ok=True)
            
            # Salvar drivers customizados
            drivers_path = os.path.join(drivers_dir, 'drivers_customizados.json')
            with open(drivers_path, 'w', encoding='utf-8') as f:
                json.dump([asdict(d) for d in drivers_customizados], f, 
                         ensure_ascii=False, indent=2, default=str)
            
            # Salvar sequência otimizada
            sequencia_path = os.path.join(drivers_dir, 'sequencia_otimizada.json')
            with open(sequencia_path, 'w', encoding='utf-8') as f:
                json.dump(sequencia_otimizada, f, ensure_ascii=False, indent=2, default=str)
            
            # Salvar manual de uso
            manual_path = os.path.join(drivers_dir, 'manual_drivers.md')
            with open(manual_path, 'w', encoding='utf-8') as f:
                f.write(self._gerar_manual_drivers(drivers_customizados, sequencia_otimizada))
            
            logger.info(f"✅ Sistema de drivers salvo: {drivers_dir}")
            return drivers_dir
            
        except Exception as e:
            logger.error(f"❌ Erro ao salvar sistema de drivers: {e}")
            return ""
    
    def _gerar_manual_drivers(self, drivers: List[DriverCustomizado], 
                             sequencia: Dict[str, Any]) -> str:
        """Gera manual de uso dos drivers mentais"""
        return f"""# Manual do Sistema de 19 Drivers Mentais

## Visão Geral
Sistema completo de ancoragem psicológica com {len(drivers)} drivers customizados para máximo impacto.

## Drivers Implementados

{chr(10).join([f"""
### {i+1}. {driver.driver_base.nome}
- **Tipo**: {driver.driver_base.tipo.value}
- **Gatilho**: {driver.driver_base.gatilho_central}
- **Fase**: {driver.driver_base.fase_jornada.value}
- **Poder de Impacto**: {driver.driver_base.poder_impacto}%

**Roteiro de Ativação:**
- Abertura: {driver.roteiro_ativacao.get('pergunta_abertura', '')}
- Analogia: {driver.roteiro_ativacao.get('historia_analogia', '')}
- Visualização: {driver.roteiro_ativacao.get('metafora_visual', '')}
- Ação: {driver.roteiro_ativacao.get('comando_acao', '')}

**Frases de Ancoragem:**
{chr(10).join([f"- {frase}" for frase in driver.ancoragem_personalizada])}

**Instalação nos CPLs:**
{chr(10).join([f"- **{cpl.upper()}**: {instrucao}" for cpl, instrucao in driver.instalacao_cpls.items()])}

---
""" for i, driver in enumerate(drivers)])}

## Sequência de Instalação

### Fase 1: Despertar (Consciência)
{chr(10).join([f"- {driver['driver_base']['nome']}" for driver in sequencia['sequencia_drivers']['fase_1_despertar']])}

### Fase 2: Desejo (Amplificação)
{chr(10).join([f"- {driver['driver_base']['nome']}" for driver in sequencia['sequencia_drivers']['fase_2_desejo']])}

### Fase 3: Decisão (Pressão)
{chr(10).join([f"- {driver['driver_base']['nome']}" for driver in sequencia['sequencia_drivers']['fase_3_decisao']])}

### Fase 4: Direção (Caminho)
{chr(10).join([f"- {driver['driver_base']['nome']}" for driver in sequencia['sequencia_drivers']['fase_4_direcao']])}

## Cronograma de Implementação

{chr(10).join([f"**{fase.replace('_', ' ').title()}**: {', '.join(drivers_fase)}" for fase, drivers_fase in sequencia['cronograma_instalacao'].items()])}

## Métricas de Acompanhamento

### Engajamento
{chr(10).join([f"- {metrica}" for metrica in sequencia['metricas_acompanhamento']['metricas_engajamento']])}

### Conversão
{chr(10).join([f"- {metrica}" for metrica in sequencia['metricas_acompanhamento']['metricas_conversao']])}

### Psicológicas
{chr(10).join([f"- {metrica}" for metrica in sequencia['metricas_acompanhamento']['metricas_psicologicas']])}

## Instruções de Uso

1. **Preparação**: Estude cada driver antes de implementar
2. **Instalação**: Siga a sequência otimizada rigorosamente
3. **Ativação**: Use os scripts fornecidos
4. **Monitoramento**: Acompanhe as métricas definidas
5. **Otimização**: Ajuste baseado nos resultados

*Sistema de 19 Drivers Mentais - Ancoragem Psicológica Completa*
"""

# Instância global
mental_drivers_system = MentalDriversSystem()

def get_mental_drivers_system() -> MentalDriversSystem:
    """Retorna instância do sistema de drivers mentais"""
    return mental_drivers_system