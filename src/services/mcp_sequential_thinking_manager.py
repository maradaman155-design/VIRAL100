import os
import requests
import logging
from typing import Dict, Any, List
from datetime import datetime

logger = logging.getLogger(__name__)

class MCPSequentialThinkingManager:
    def __init__(self):
        # CONFIGURAÇÃO SMITHERY AI CONFORME PLANO
        self.base_url = os.getenv(
            'MCP_SEQUENTIAL_THINKING_URL', 
            'https://smithery.ai/server/@smithery-ai/server-sequential-thinking'
        )
        self.enabled = os.getenv('MCP_SEQUENTIAL_THINKING_ENABLED', 'true').lower() == 'true'
        self.active_processes: Dict[str, Dict[str, Any]] = {}

        if not self.base_url and self.enabled:
            logger.error("MCP_SEQUENTIAL_THINKING_URL não configurado nas variáveis de ambiente e MCP está habilitado.")
            raise ValueError("MCP_SEQUENTIAL_THINKING_URL não configurado.")
        
        if not self.enabled:
            logger.warning("MCP Sequential Thinking está desabilitado.")

    def _make_request(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Faz uma requisição para o MCP Sequential Thinking."""
        if not self.enabled:
            return {"error": "MCP Sequential Thinking desabilitado"}
            
        try:
            headers = {"Content-Type": "application/json"}
            response = requests.post(self.base_url, json=payload, headers=headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Erro na requisição MCP: {e}")
            return {"error": str(e)}

    def start_thinking_process(self, initial_prompt: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Inicia um novo processo de pensamento sequencial"""
        try:
            if not self.enabled:
                return {"error": "MCP Sequential Thinking desabilitado", "process_id": None}

            process_id = f"st_{int(datetime.now().timestamp())}_{hash(initial_prompt) % 10000}"

            # Estrutura o processo de pensamento em etapas
            thinking_steps = self._create_thinking_framework(initial_prompt, context)

            payload = {
                "action": "start_process",
                "prompt": initial_prompt,
                "context": context or {},
                "process_id": process_id,
                "thinking_framework": thinking_steps,
                "config": {
                    "max_steps": 15,
                    "depth_analysis": True,
                    "creative_mode": True,
                    "self_reflection": True,
                    "critical_thinking": True
                }
            }

            response = self._make_request(payload)

            if response.get("success"):
                self.active_processes[process_id] = {
                    "initial_prompt": initial_prompt,
                    "context": context,
                    "started_at": datetime.now(),
                    "current_step": 0,
                    "total_steps": len(thinking_steps),
                    "thinking_framework": thinking_steps,
                    "status": "active",
                    "insights": [],
                    "reasoning_chain": []
                }

                logger.info(f"✅ Processo de pensamento iniciado: {process_id} ({len(thinking_steps)} etapas)")
                return {
                    "success": True,
                    "process_id": process_id,
                    "framework": thinking_steps,
                    "initial_analysis": response.get("analysis", ""),
                    "next_steps": response.get("next_steps", []),
                    "estimated_duration": len(thinking_steps) * 30  # segundos
                }
            else:
                logger.error(f"❌ Erro ao iniciar processo: {response.get('error', 'Erro desconhecido')}")
                return {"error": response.get("error", "Erro ao iniciar processo"), "process_id": None}

        except Exception as e:
            logger.error(f"❌ Erro no processo de pensamento: {e}")
            return {"error": str(e), "process_id": None}

    def advance_thinking_step(self, process_id: str, user_input: str = None) -> dict:
        """Avança para o próximo passo no processo de pensamento sequencial."""
        if process_id not in self.active_processes:
            return {"error": "Processo não encontrado ou já finalizado."}
            
        process_data = self.active_processes[process_id]
        current_step_index = process_data["current_step"]

        if current_step_index >= len(process_data["thinking_framework"]):
            return {"error": "Processo já atingiu o número máximo de etapas."}

        current_step_config = process_data["thinking_framework"][current_step_index]
        
        payload = {
            "action": "advance_process",
            "process_id": process_id,
            "current_step": current_step_index + 1,
            "step_details": {
                "name": current_step_config["name"],
                "description": current_step_config["description"],
                "questions": current_step_config.get("questions", []),
                "user_input": user_input if user_input else ""
            },
            "context": {
                **process_data["context"],
                "current_insights": process_data["insights"],
                "reasoning_chain": process_data["reasoning_chain"]
            }
        }

        response = self._make_request(payload)

        if response.get("success"):
            process_data["current_step"] += 1
            process_data["insights"].append({
                "step": process_data["current_step"],
                "analysis": response.get("analysis", ""),
                "recommendations": response.get("recommendations", [])
            })
            process_data["reasoning_chain"].append({
                "step": process_data["current_step"],
                "reasoning": response.get("reasoning", "")
            })

            if process_data["current_step"] >= process_data["total_steps"]:
                process_data["status"] = "completed"
                logger.info(f"✅ Processo {process_id} concluído.")
                # Aqui podemos remover o processo da memória se desejado
                # del self.active_processes[process_id] 

            return {
                "success": True,
                "process_id": process_id,
                "next_step": process_data["current_step"] + 1,
                "analysis": response.get("analysis", ""),
                "recommendations": response.get("recommendations", []),
                "new_insights": response.get("insights", []),
                "reasoning": response.get("reasoning", "")
            }
        else:
            logger.error(f"❌ Erro ao avançar passo do processo {process_id}: {response.get('error', 'Erro desconhecido')}")
            # Considerar um fallback ou tentativa de recuperação aqui
            process_data["status"] = "failed"
            return {"error": response.get("error", "Erro ao avançar passo"), "process_id": process_id}


    def get_process_status(self, process_id: str) -> dict:
        """Obtém o status atual de um processo de pensamento sequencial."""
        if process_id not in self.active_processes:
            return {"error": "Processo não encontrado."}
            
        process_data = self.active_processes[process_id]
        
        return {
            "success": True,
            "process_id": process_id,
            "status": process_data["status"],
            "current_step": process_data["current_step"],
            "total_steps": process_data["total_steps"],
            "started_at": process_data["started_at"].isoformat(),
            "insights_count": len(process_data["insights"]),
            "last_analysis": process_data["insights"][-1]["analysis"] if process_data["insights"] else None
        }

    def _create_thinking_framework(self, prompt: str, context: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Cria framework estruturado de pensamento"""

        # Identifica o tipo de problema
        problem_type = self._identify_problem_type(prompt)

        if problem_type == "market_analysis":
            return self._market_analysis_framework(prompt, context)
        elif problem_type == "competitor_analysis":
            return self._competitor_analysis_framework(prompt, context)
        elif problem_type == "content_strategy":
            return self._content_strategy_framework(prompt, context)
        else:
            return self._general_thinking_framework(prompt, context)

    def _identify_problem_type(self, prompt: str) -> str:
        """Identifica o tipo de problema baseado no prompt"""
        prompt_lower = prompt.lower()

        if any(word in prompt_lower for word in ['mercado', 'market', 'tendencia', 'trend']):
            return "market_analysis"
        elif any(word in prompt_lower for word in ['concorrente', 'competitor', 'competição']):
            return "competitor_analysis"
        elif any(word in prompt_lower for word in ['conteúdo', 'content', 'marketing', 'estratégia']):
            return "content_strategy"
        else:
            return "general_analysis"

    def _market_analysis_framework(self, prompt: str, context: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Framework para análise de mercado"""
        return [
            {
                "step": 1,
                "name": "Definição do Escopo",
                "description": "Definir claramente o mercado e segmento a ser analisado",
                "questions": [
                    "Qual é o mercado específico?",
                    "Qual é o público-alvo?",
                    "Qual é o segmento geográfico?"
                ],
                "expected_output": "Escopo bem definido do mercado"
            },
            {
                "step": 2,
                "name": "Análise de Tamanho",
                "description": "Determinar o tamanho e potencial do mercado",
                "questions": [
                    "Qual é o TAM (Total Addressable Market)?",
                    "Qual é o SAM (Serviceable Addressable Market)?",
                    "Qual é o SOM (Serviceable Obtainable Market)?"
                ],
                "expected_output": "Métricas de tamanho do mercado"
            },
            {
                "step": 3,
                "name": "Análise de Tendências",
                "description": "Identificar tendências atuais e futuras",
                "questions": [
                    "Quais são as principais tendências?",
                    "O que está crescendo/declinando?",
                    "Quais fatores impulsionam mudanças?"
                ],
                "expected_output": "Mapa de tendências relevantes"
            },
            {
                "step": 4,
                "name": "Análise Competitiva",
                "description": "Mapear o cenário competitivo",
                "questions": [
                    "Quem são os principais players?",
                    "Qual é a participação de mercado?",
                    "Quais são as barreiras de entrada?"
                ],
                "expected_output": "Landscape competitivo"
            },
            {
                "step": 5,
                "name": "Oportunidades e Ameaças",
                "description": "Identificar oportunidades e riscos",
                "questions": [
                    "Onde estão as oportunidades não exploradas?",
                    "Quais são os principais riscos?",
                    "Como mitigar ameaças?"
                ],
                "expected_output": "Matriz de oportunidades e ameaças"
            },
            {
                "step": 6,
                "name": "Síntese e Recomendações",
                "description": "Consolidar insights e criar plano de ação",
                "questions": [
                    "Quais são os principais insights?",
                    "Qual é a estratégia recomendada?",
                    "Quais são os próximos passos?"
                ],
                "expected_output": "Estratégia e plano de ação"
            }
        ]

    def _competitor_analysis_framework(self, prompt: str, context: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Framework para análise de concorrentes"""
        return [
            {
                "step": 1,
                "name": "Identificação de Concorrentes",
                "description": "Mapear concorrentes diretos e indiretos",
                "questions": [
                    "Quem são os concorrentes diretos?",
                    "Quem são os concorrentes indiretos?",
                    "Quem são os novos entrantes?"
                ],
                "expected_output": "Lista completa de concorrentes"
            },
            {
                "step": 2,
                "name": "Análise de Produtos/Serviços",
                "description": "Comparar ofertas dos concorrentes",
                "questions": [
                    "Quais produtos/serviços oferecem?",
                    "Qual é a proposta de valor?",
                    "Quais são os diferenciais?"
                ],
                "expected_output": "Matriz comparativa de ofertas"
            },
            {
                "step": 3,
                "name": "Análise de Preços",
                "description": "Comparar estratégias de precificação",
                "questions": [
                    "Qual é a estratégia de preços?",
                    "Como se posicionam no mercado?",
                    "Qual é a relação custo-benefício?"
                ],
                "expected_output": "Análise competitiva de preços"
            },
            {
                "step": 4,
                "name": "Análise de Marketing",
                "description": "Avaliar estratégias de marketing e comunicação",
                "questions": [
                    "Quais canais de marketing usam?",
                    "Qual é a mensagem principal?",
                    "Como é a presença digital?"
                ],
                "expected_output": "Benchmark de estratégias de marketing"
            },
            {
                "step": 5,
                "name": "Pontos Fortes e Fracos",
                "description": "Identificar vantagens e vulnerabilidades",
                "questions": [
                    "Quais são os pontos fortes de cada um?",
                    "Onde estão as vulnerabilidades?",
                    "Que gaps existem no mercado?"
                ],
                "expected_output": "Matriz SWOT dos concorrentes"
            },
            {
                "step": 6,
                "name": "Oportunidades de Diferenciação",
                "description": "Identificar como se diferenciar",
                "questions": [
                    "Onde podemos nos diferenciar?",
                    "Quais necessidades não atendidas?",
                    "Como superar os concorrentes?"
                ],
                "expected_output": "Estratégia de diferenciação"
            }
        ]

    def _content_strategy_framework(self, prompt: str, context: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Framework para estratégia de conteúdo"""
        return [
            {
                "step": 1,
                "name": "Definição de Objetivos",
                "description": "Estabelecer objetivos claros para o conteúdo",
                "questions": [
                    "Qual é o objetivo principal?",
                    "Quais KPIs vamos medir?",
                    "Qual é o prazo esperado?"
                ],
                "expected_output": "Objetivos SMART definidos"
            },
            {
                "step": 2,
                "name": "Análise de Audiência",
                "description": "Entender profundamente o público-alvo",
                "questions": [
                    "Quem é o público-alvo?",
                    "Quais são suas dores e desejos?",
                    "Onde consomem conteúdo?"
                ],
                "expected_output": "Personas detalhadas"
            },
            {
                "step": 3,
                "name": "Auditoria de Conteúdo",
                "description": "Avaliar conteúdo existente",
                "questions": [
                    "Que conteúdo já existe?",
                    "O que está funcionando?",
                    "Que gaps precisam ser preenchidos?"
                ],
                "expected_output": "Inventário e análise de gaps"
            },
            {
                "step": 4,
                "name": "Planejamento de Formatos",
                "description": "Definir tipos e formatos de conteúdo",
                "questions": [
                    "Quais formatos são mais eficazes?",
                    "Qual é a capacidade de produção?",
                    "Como distribuir entre os canais?"
                ],
                "expected_output": "Mix de formatos otimizado"
            },
            {
                "step": 5,
                "name": "Calendário Editorial",
                "description": "Criar cronograma de publicações",
                "questions": [
                    "Qual é a frequência ideal?",
                    "Quando publicar cada tipo?",
                    "Como sincronizar com campanhas?"
                ],
                "expected_output": "Calendário editorial estruturado"
            },
            {
                "step": 6,
                "name": "Métricas e Otimização",
                "description": "Definir sistema de monitoramento",
                "questions": [
                    "Como medir o sucesso?",
                    "Qual é o processo de otimização?",
                    "Como escalar o que funciona?"
                ],
                "expected_output": "Framework de medição e otimização"
            }
        ]

    def _general_thinking_framework(self, prompt: str, context: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Framework geral de pensamento"""
        return [
            {
                "step": 1,
                "name": "Compreensão do Problema",
                "description": "Entender completamente o desafio",
                "questions": [
                    "Qual é exatamente o problema?",
                    "Por que isso é importante?",
                    "Quais são as limitações?"
                ],
                "expected_output": "Definição clara do problema"
            },
            {
                "step": 2,
                "name": "Coleta de Informações",
                "description": "Reunir dados e insights relevantes",
                "questions": [
                    "Que informações precisamos?",
                    "Onde encontrar dados confiáveis?",
                    "Quais são as fontes primárias?"
                ],
                "expected_output": "Base de dados estruturada"
            },
            {
                "step": 3,
                "name": "Análise e Síntese",
                "description": "Processar e conectar informações",
                "questions": [
                    "Quais padrões emergem?",
                    "Como os dados se relacionam?",
                    "Quais são as correlações?"
                ],
                "expected_output": "Insights e conexões identificadas"
            },
            {
                "step": 4,
                "name": "Geração de Alternativas",
                "description": "Criar múltiplas soluções possíveis",
                "questions": [
                    "Quais são as opções disponíveis?",
                    "Como podemos abordar diferentemente?",
                    "Que soluções criativas existem?"
                ],
                "expected_output": "Leque de alternativas viáveis"
            },
            {
                "step": 5,
                "name": "Avaliação de Opções",
                "description": "Comparar e avaliar alternativas",
                "questions": [
                    "Quais são os prós e contras?",
                    "Qual é o custo-benefício?",
                    "Quais são os riscos?"
                ],
                "expected_output": "Matriz de avaliação"
            },
            {
                "step": 6,
                "name": "Recomendação Final",
                "description": "Escolher a melhor abordagem",
                "questions": [
                    "Qual é a melhor opção?",
                    "Como implementar?",
                    "Como medir o sucesso?"
                ],
                "expected_output": "Plano de ação recomendado"
            }
        ]

# Exemplo de uso (apenas para demonstração, remover em produção)
if __name__ == "__main__":
    # Para testar, defina a variável de ambiente antes de executar este script
    # Ex: export MCP_SEQUENTIAL_THINKING_URL="https://smithery.ai/server/@xinzhongyouhai/mcp-sequentialthinking-tools"
    # Ou adicione ao seu .env e carregue com python-dotenv
    from dotenv import load_dotenv
    load_dotenv()

    # Configurar logging básico para visualização
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    manager = MCPSequentialThinkingManager()

    # Exemplo de início de um processo
    print("Iniciando processo de pensamento...")
    result = manager.start_thinking_process("Como otimizar a busca de dados em uma aplicação Flask, considerando o SEO e a experiência do usuário?")
    print(result)

    if result.get("success") and result.get("process_id"):
        process_id = result["process_id"]
        print(f"Processo iniciado com ID: {process_id}")

        # Exemplo de avanço de um passo
        print("Avançando para o próximo passo...")
        step_result = manager.advance_thinking_step(process_id, "Considerar que a aplicação usa PostgreSQL e busca é feita via ORM.")
        print(step_result)

        # Exemplo de obtenção de status
        print("Obtendo status do processo...")
        status = manager.get_process_status(process_id)
        print(status)
        
        # Avançando mais alguns passos para demonstrar o fluxo
        if step_result.get("success"):
            print("Avançando para outro passo...")
            step_result_2 = manager.advance_thinking_step(process_id, "Focar em índices e otimização de queries.")
            print(step_result_2)

            print("Obtendo status do processo novamente...")
            status_2 = manager.get_process_status(process_id)
            print(status_2)

    elif result.get("error"):
        print(f"Falha ao iniciar o processo: {result['error']}")