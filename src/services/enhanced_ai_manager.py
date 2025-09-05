#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ARQV30 Enhanced v3.0 - Enhanced AI Manager
Gerenciador de IA com suporte a ferramentas e busca ativa
"""

import os
import logging
import asyncio
import json
from typing import Dict, List, Optional, Any, Union
from datetime import datetime

# Imports condicionais
try:
    import google.generativeai as genai
    from google.generativeai.types import FunctionDeclaration, Tool
    HAS_GEMINI = True
except ImportError:
    HAS_GEMINI = False

try:
    import openai
    HAS_OPENAI = True
except ImportError:
    HAS_OPENAI = False

try:
    from groq import Groq
    HAS_GROQ = True
except ImportError:
    HAS_GROQ = False

# Adicionando suporte ao OpenRouter
try:
    import openai as openrouter_openai
    HAS_OPENROUTER = True
except ImportError:
    HAS_OPENROUTER = False

logger = logging.getLogger(__name__)

class EnhancedAIManager:
    """Gerenciador de IA aprimorado com ferramentas de busca ativa"""

    def __init__(self):
        """Inicializa o gerenciador aprimorado"""
        self.providers = {}
        self.current_provider = None
        self.search_orchestrator = None

        self._initialize_providers()
        self._initialize_search_tools()

        logger.info(f"🤖 Enhanced AI Manager inicializado com {len(self.providers)} provedores")

    def _initialize_providers(self):
        """Inicializa todos os provedores de IA"""

        # Qwen via OpenRouter (Prioridade 1 - mais confiável)
        if HAS_OPENROUTER:
            api_key = os.getenv("OPENROUTER_API_KEY")
            if api_key:
                try:
                    openrouter_client = openrouter_openai.OpenAI(
                        api_key=api_key,
                        base_url="https://openrouter.ai/api/v1"
                    )
                    self.providers["openrouter"] = {
                        "client": openrouter_client,
                        "model": "qwen/qwen2.5-vl-32b-instruct:free",
                        "available": True,
                        "supports_tools": False, # Ajuste se o modelo suportar tools
                        "priority": 1
                    }
                    logger.info("✅ Qwen via OpenRouter configurado")
                except Exception as e:
                    logger.error(f"❌ Erro ao configurar Qwen/OpenRouter: {e}")

        # Gemini (Prioridade 2)
        if HAS_GEMINI:
            api_key = os.getenv("GEMINI_API_KEY")
            if api_key:
                try:
                    genai.configure(api_key=api_key)
                    self.providers["gemini"] = {
                        "client": genai,
                        "model": "gemini-2.0-flash-exp",
                        "available": True,
                        "supports_tools": True,
                        "priority": 2
                    }
                    logger.info("✅ Gemini 2.0 Flash configurado")
                except Exception as e:
                    logger.error(f"❌ Erro ao configurar Gemini: {e}")

        # Groq (Prioridade 3 - fallback confiável) - ATUALIZADO PARA MODELO SUPORTADO
        if HAS_GROQ:
            api_key = os.getenv("GROQ_API_KEY")
            if api_key:
                try:
                    self.providers["groq"] = {
                        "client": Groq(api_key=api_key),
                        "model": "llama3-70b-8192", # Modelo atualizado - veja a tabela de depreciações
                        "available": True,
                        "supports_tools": False,
                        "priority": 3
                    }
                    logger.info("✅ Groq Llama configurado")
                except Exception as e:
                    logger.error(f"❌ Erro ao configurar Groq: {e}")

        # OpenAI (Prioridade 4)
        if HAS_OPENAI:
            api_key = os.getenv("OPENAI_API_KEY")
            if api_key:
                try:
                    self.providers["openai"] = {
                        "client": openai.OpenAI(api_key=api_key),
                        "model": "gpt-4o",
                        "available": True, # Habilitado
                        "supports_tools": True,
                        "priority": 4
                    }
                    logger.info("✅ OpenAI GPT-4o configurado")
                except Exception as e:
                    logger.error(f"❌ Erro ao configurar OpenAI: {e}")

    def _initialize_search_tools(self):
        """Inicializa ferramentas de busca"""
        try:
            from services.real_search_orchestrator import real_search_orchestrator
            self.search_orchestrator = real_search_orchestrator
            logger.info("✅ Ferramentas de busca ativa configuradas")
        except ImportError:
            logger.warning("⚠️ Search orchestrator não disponível")

    def _get_best_provider(self, require_tools: bool = False) -> Optional[str]:
        """Seleciona o melhor provedor disponível"""
        available = []

        for name, provider in self.providers.items():
            if not provider["available"]:
                continue

            # Se requer tools, pula provedores que não suportam
            if require_tools and not provider.get("supports_tools", False):
                 # Mas permite Qwen mesmo sem tools como fallback se necessário
                 if name != "openrouter": # Qwen pode ser usado mesmo sem tools se for o único
                    continue

            available.append((name, provider["priority"]))

        if available:
            # Ordena pela prioridade (menor número = maior prioridade)
            available.sort(key=lambda x: x[1])
            return available[0][0]

        # Se nenhum provedor com tools está disponível, mas precisamos de tools
        # Retorna o melhor provedor sem tools
        if require_tools:
            logger.warning("⚠️ Nenhum provedor com tools disponível, usando provedor simples")
            return self._get_best_provider(require_tools=False)

        return None

    async def generate_with_active_search(
        self,
        prompt: str,
        context: str = "",
        session_id: str = None,
        max_search_iterations: int = 3,
        study_time_minutes: int = 5
    ) -> str:
        """
        Gera conteúdo com busca ativa - IA pode buscar informações online
        """
        logger.info(f"🔍 Iniciando geração com busca ativa - Tempo de estudo: {study_time_minutes} min")
        
        # FASE DE ESTUDO PROFUNDO
        if context and len(context) > 10000:  # Se há muito contexto para estudar
            logger.info(f"📚 INICIANDO FASE DE ESTUDO PROFUNDO - {study_time_minutes} minutos")
            study_start = datetime.now()
            
            # Divide o contexto em chunks para análise profunda
            chunk_size = 8000
            context_chunks = [context[i:i+chunk_size] for i in range(0, len(context), chunk_size)]
            
            study_insights = []
            for i, chunk in enumerate(context_chunks[:10]):  # Máximo 10 chunks
                logger.info(f"📖 Analisando chunk {i+1}/{min(len(context_chunks), 10)}")
                
                study_prompt = f"""
                ANÁLISE PROFUNDA E APRENDIZADO:
                
                Analise profundamente este conteúdo e extraia:
                1. Insights únicos e padrões ocultos
                2. Tendências emergentes
                3. Oportunidades não óbvias
                4. Conexões entre diferentes informações
                5. Previsões baseadas nos dados
                
                CONTEÚDO PARA ANÁLISE:
                {chunk}
                
                Seja extremamente analítico e perspicaz. Vá além do óbvio.
                """
                
                try:
                    insight = await self.generate_text(study_prompt)
                    if insight and len(insight) > 100:
                        study_insights.append(insight)
                except Exception as e:
                    logger.warning(f"⚠️ Erro na análise do chunk {i+1}: {e}")
            
            # Consolida insights do estudo
            if study_insights:
                consolidated_study = "\n\n".join(study_insights)
                context = f"{context}\n\nINSIGHTS DO ESTUDO PROFUNDO:\n{consolidated_study}"
                
            study_duration = (datetime.now() - study_start).total_seconds() / 60
            logger.info(f"✅ Estudo profundo concluído em {study_duration:.1f} minutos")

        # Tenta Qwen/OpenRouter primeiro para geração com busca ativa
        if "openrouter" in self.providers and self.providers["openrouter"]["available"]:
             provider_name = "openrouter"
             logger.info(f"🤖 Usando {provider_name} com busca ativa (prioritário)")
        else:
            # Caso contrário, usa a lógica padrão
            provider_name = self._get_best_provider(require_tools=True)
            if not provider_name:
                logger.warning("⚠️ Nenhum provedor com ferramentas disponível - usando fallback")
                return await self.generate_text(prompt + "\n\n" + context)

        provider = self.providers[provider_name]
        logger.info(f"🤖 Usando {provider_name} com busca ativa")

        # Prepara prompt com instruções de busca
        enhanced_prompt = f"""
{prompt}

CONTEXTO DISPONÍVEL:
{context}

INSTRUÇÕES ESPECIAIS:
- Analise o contexto fornecido detalhadamente
- Busque dados atualizados sobre o mercado brasileiro
- Procure por estatísticas, tendências e casos reais
- Forneça insights profundos baseados nos dados disponíveis

IMPORTANTE: Gere uma análise completa mesmo sem ferramentas de busca, baseando-se no contexto fornecido.
"""

        try:
            # Executa geração com ferramentas
            if provider_name == "gemini":
                return await self._generate_gemini_with_tools(enhanced_prompt, max_search_iterations, session_id)
            elif provider_name == "openai":
                return await self._generate_openai_with_tools(enhanced_prompt, max_search_iterations, session_id)
            else:
                # Para Qwen/OpenRouter e outros, usa geração simples
                return await self.generate_text(enhanced_prompt)
        except Exception as e:
            logger.error(f"❌ Erro com {provider_name}: {e}")
            # Fallback para geração simples com Qwen/OpenRouter
            logger.info("🔄 Usando fallback para Qwen/OpenRouter")
            return await self.generate_text(enhanced_prompt)

    async def _generate_gemini_with_tools(
        self,
        prompt: str,
        max_iterations: int,
        session_id: str = None
    ) -> str:
        """Gera com Gemini usando ferramentas"""

        try:
            model = genai.GenerativeModel("gemini-2.0-flash-exp")

            # Define função de busca
            search_function = FunctionDeclaration(
                name="google_search",
                description="Busca informações atualizadas na internet",
                parameters={
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Termo de busca"
                        }
                    },
                    "required": ["query"]
                }
            )

            tool = Tool(function_declarations=[search_function])

            # Inicia chat com ferramentas
            chat = model.start_chat(tools=[tool])

            iteration = 0
            conversation_history = []

            while iteration < max_iterations:
                iteration += 1
                logger.info(f"🔄 Iteração {iteration}/{max_iterations}")

                try:
                    # Envia mensagem
                    if iteration == 1:
                        response = chat.send_message(prompt)
                    else:
                        # Continua conversa com resultados de busca
                        response = chat.send_message("Continue a análise com os dados obtidos.")

                    # Verifica se há function calls
                    if response.candidates[0].content.parts:
                        for part in response.candidates[0].content.parts:
                            if part.function_call:
                                function_call = part.function_call

                                if function_call.name == "google_search":
                                    search_query = function_call.args.get("query", "")
                                    logger.info(f"🔍 IA solicitou busca: {search_query}")

                                    # Executa busca real
                                    search_results = await self._execute_real_search(search_query, session_id)

                                    # Envia resultados de volta para a IA
                                    search_response = chat.send_message(
                                        f"Resultados da busca para \'{search_query}\':\n{search_results}"
                                    )

                                    conversation_history.append({
                                        "search_query": search_query,
                                        "search_results": search_results[:1000] # Limita para log
                                    })

                                    continue

                    # Se chegou aqui, é resposta final
                    final_response = response.text

                    logger.info(f"✅ Geração com busca ativa concluída em {iteration} iterações")
                    logger.info(f"🔍 {len(conversation_history)} buscas realizadas")

                    return final_response

                except Exception as e:
                    logger.error(f"❌ Erro na iteração {iteration}: {e}")
                    break

            # Se chegou ao limite de iterações
            logger.warning(f"⚠️ Limite de iterações atingido ({max_iterations})")
            return "Análise realizada com busca ativa, mas processo limitado por iterações."

        except Exception as e:
            logger.error(f"❌ Erro no Gemini com ferramentas: {e}")
            raise

    async def _generate_openai_with_tools(
        self,
        prompt: str,
        max_iterations: int,
        session_id: str = None
    ) -> str:
        """Gera com OpenAI usando ferramentas"""

        try:
            client = self.providers["openai"]["client"]

            # Define função de busca
            tools = [{
                "type": "function",
                "function": {
                    "name": "google_search",
                    "description": "Busca informações atualizadas na internet",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "Termo de busca"
                            }
                        },
                        "required": ["query"]
                    }
                }
            }]

            messages = [{"role": "user", "content": prompt}]
            iteration = 0

            while iteration < max_iterations:
                iteration += 1
                logger.info(f"🔄 Iteração OpenAI {iteration}/{max_iterations}")

                try:
                    response = client.chat.completions.create(
                        model=self.providers["openai"]["model"],
                        messages=messages,
                        tools=tools,
                        tool_choice="auto",
                        max_tokens=4000
                    )

                    message = response.choices[0].message

                    # Verifica tool calls
                    if hasattr(message, "tool_calls") and message.tool_calls:
                        tool_call = message.tool_calls[0]

                        if tool_call.function.name == "google_search":
                            args = json.loads(tool_call.function.arguments)
                            search_query = args.get("query", "")

                            logger.info(f"🔍 IA OpenAI solicitou busca: {search_query}")

                            # Executa busca real
                            search_results = await self._execute_real_search(search_query, session_id)

                            # Adiciona à conversa
                            messages.append({
                                "role": "assistant",
                                "tool_calls": [{
                                    "id": tool_call.id,
                                    "type": "function",
                                    "function": {
                                        "name": "google_search",
                                        "arguments": tool_call.function.arguments
                                    }
                                }]
                            })

                            messages.append({
                                "role": "tool",
                                "tool_call_id": tool_call.id,
                                "content": search_results
                            })

                            continue

                    # Resposta final
                    final_response = message.content
                    logger.info(f"✅ OpenAI geração concluída em {iteration} iterações")
                    return final_response

                except Exception as e:
                    error_msg = str(e)
                    if "429" in error_msg or "quota" in error_msg.lower() or "insufficient_quota" in error_msg.lower():
                        logger.error(f"❌ OpenAI quota excedida: {e}")
                        # Marca OpenAI como indisponível temporariamente
                        self.providers["openai"]["available"] = False
                        logger.info("🔄 Marcando OpenAI como indisponível e tentando outro provedor")

                        # Tenta usar outro provedor como fallback
                        fallback_provider = self._get_best_provider(require_tools=False)
                        if fallback_provider and fallback_provider != "openai":
                            logger.info(f"🔄 Usando {fallback_provider} como fallback para OpenAI")
                            return await self.generate_text(prompt)
                        else:
                            return "OpenAI quota excedida e nenhum provedor alternativo disponível. Por favor, configure uma chave API válida."
                    else:
                        logger.error(f"❌ Erro na iteração OpenAI {iteration}: {e}")
                    break

            return "Análise realizada com OpenAI e busca ativa."

        except Exception as e:
            logger.error(f"❌ Erro no OpenAI com ferramentas: {e}")
            raise

    async def _execute_real_search(self, search_query: str, session_id: str = None) -> str:
        """Executa busca real usando o orquestrador"""

        if not self.search_orchestrator:
            return f"Busca não disponível para: {search_query}"

        try:
            # Executa busca massiva real
            search_results = await self.search_orchestrator.execute_massive_real_search(
                query=search_query,
                context={"ai_requested": True},
                session_id=session_id or "ai_search"
            )

            # Formata resultados para a IA
            formatted_results = self._format_search_results_for_ai(search_results)

            return formatted_results

        except Exception as e:
            logger.error(f"❌ Erro na busca real: {e}")
            return f"Erro na busca para \'{search_query}\': {str(e)}"

    def _format_search_results_for_ai(self, search_results: Dict[str, Any]) -> str:
        """Formata resultados de busca para consumo da IA"""

        formatted = """
RESULTADOS DA BUSCA REAL:
Query: {query}
Fontes encontradas: {total_sources}

""".format(
            query=search_results.get("query", ""),
            total_sources=search_results.get("statistics", {}).get("total_sources", 0)
        )

        # Web results
        web_results = search_results.get("web_results", [])
        if web_results:
            formatted += "=== RESULTADOS WEB ===\n"
            for i, result in enumerate(web_results[:10], 1):
                formatted += f"{i}. {result.get('title', 'Sem título')}\n"
                formatted += f"   URL: {result.get('url', '')}\n"
                formatted += f"   Resumo: {result.get('snippet', '')[:200]}...\n\n"

        # YouTube results
        youtube_results = search_results.get("youtube_results", [])
        if youtube_results:
            formatted += "=== RESULTADOS YOUTUBE ===\n"
            for i, result in enumerate(youtube_results[:5], 1):
                formatted += f"{i}. {result.get('title', 'Sem título')}\n"
                formatted += f"   Canal: {result.get('channel', '')}\n"
                formatted += f"   Views: {result.get('view_count', 0):,}\n"
                formatted += f"   Likes: {result.get('like_count', 0):,}\n\n"

        # Social results
        social_results = search_results.get("social_results", [])
        if social_results:
            formatted += "=== RESULTADOS REDES SOCIAIS ===\n"
            for i, result in enumerate(social_results[:5], 1):
                formatted += f"{i}. {result.get('title', 'Sem título')}\n"
                formatted += f"   Plataforma: {result.get('platform', '')}\n"
                formatted += f"   Engajamento: {result.get('viral_score', 0):.1f}/10\n\n"

        # Conteúdo viral
        viral_content = search_results.get("viral_content", [])
        if viral_content:
            formatted += "=== CONTEÚDO VIRAL ===\n"
            for i, content in enumerate(viral_content[:5], 1):
                formatted += f"{i}. {content.get('title', 'Sem título')}\n"
                formatted += f"   URL: {content.get('url', '')}\n"
                formatted += f"   Plataforma: {content.get('platform', '')}\n"
                formatted += f"   Viral Score: {content.get('viral_score', 0):.1f}/10\n\n"

        # Screenshots
        screenshots = search_results.get("screenshots_captured", [])
        if screenshots:
            formatted += "=== SCREENSHOTS CAPTURADOS ===\n"
            for i, screenshot_path in enumerate(screenshots[:5], 1):
                formatted += f"{i}. {screenshot_path}\n"
            formatted += "\n"

        return formatted

    # Método dummy para 'generate_text' caso seja chamado sem provedor com tools
    async def generate_text(self, prompt: str, max_tokens: int = 4000, temperature: float = 0.7) -> str:
        """Gera texto usando o melhor provedor disponível"""
        provider_name = self._get_best_provider(require_tools=False)

        if not provider_name:
            logger.warning("⚠️ Nenhum provedor disponível")
            return "Erro: Nenhum provedor de IA disponível para gerar texto."

        provider = self.providers[provider_name]
        logger.info(f"🤖 Usando {provider_name} para geração de texto")

        try:
            if provider_name == "openrouter":
                client = provider["client"]
                response = client.chat.completions.create(
                    model=provider["model"],
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=max_tokens,
                    temperature=temperature
                )
                return response.choices[0].message.content

            elif provider_name == "gemini":
                model = genai.GenerativeModel("gemini-2.0-flash-exp")
                response = model.generate_content(
                    prompt,
                    generation_config=genai.types.GenerationConfig(
                        max_output_tokens=max_tokens,
                        temperature=temperature,
                    )
                )
                return response.text

            elif provider_name == "groq":
                client = provider["client"]
                response = client.chat.completions.create(
                    model=provider["model"],
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=max_tokens,
                    temperature=temperature
                )
                return response.choices[0].message.content

            elif provider_name == "openai":
                client = provider["client"]
                response = client.chat.completions.create(
                    model=provider["model"],
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=max_tokens,
                    temperature=temperature
                )
                return response.choices[0].message.content

        except Exception as e:
            logger.error(f"❌ Erro na geração de texto com {provider_name}: {e}")
            return f"Erro na geração: {str(e)}"

        return "Erro: Método de geração não implementado para este provedor"

    async def conduct_deep_study_phase(
        self,
        massive_data: Dict[str, Any],
        session_id: str,
        study_duration_minutes: int = 5
    ) -> Dict[str, Any]:
        """
        ETAPA 2: Conduz estudo profundo de 5 minutos nos dados massivos
        A IA se torna expert no assunto analisando o JSON gigante
        """
        
        logger.info(f"🧠 ETAPA 2 - ESTUDO PROFUNDO IA iniciado - Duração: {study_duration_minutes} minutos")
        logger.info(f"📊 Analisando {len(json.dumps(massive_data, ensure_ascii=False))/1024:.1f}KB de dados")
        
        import time
        start_time = time.time()
        study_end_time = start_time + (study_duration_minutes * 60)
        
        # Estrutura de conhecimento expert
        expert_knowledge = {
            "study_metadata": {
                "session_id": session_id,
                "study_start": datetime.now().isoformat(),
                "target_duration_minutes": study_duration_minutes,
                "data_size_analyzed_kb": len(json.dumps(massive_data, ensure_ascii=False)) / 1024,
                "ai_provider_used": self.current_provider
            },
            "domain_expertise": {},
            "market_intelligence": {},
            "competitive_analysis": {},
            "behavioral_insights": {},
            "trend_analysis": {},
            "predictive_insights": {},
            "strategic_recommendations": {},
            "study_phases_completed": []
        }
        
        # Fases de estudo progressivo
        study_phases = [
            ("Análise Estrutural dos Dados", self._analyze_data_structure),
            ("Extração de Insights de Mercado", self._extract_market_insights),
            ("Análise Competitiva Profunda", self._analyze_competitive_landscape),
            ("Padrões Comportamentais", self._identify_behavioral_patterns),
            ("Análise de Tendências", self._analyze_trends),
            ("Geração de Insights Preditivos", self._generate_predictive_insights),
            ("Síntese Estratégica", self._synthesize_strategic_recommendations)
        ]
        
        phase_duration = (study_duration_minutes * 60) / len(study_phases)
        
        for i, (phase_name, phase_function) in enumerate(study_phases):
            if time.time() >= study_end_time:
                logger.warning(f"⏰ Tempo limite atingido na fase {i+1}")
                break
                
            logger.info(f"📚 Fase {i+1}/{len(study_phases)}: {phase_name}")
            phase_start = time.time()
            
            try:
                # Executa fase com timeout
                phase_result = await asyncio.wait_for(
                    phase_function(massive_data, expert_knowledge),
                    timeout=phase_duration + 30  # Buffer de 30s
                )
                
                expert_knowledge["study_phases_completed"].append({
                    "phase": phase_name,
                    "completed": True,
                    "duration_seconds": time.time() - phase_start,
                    "insights_generated": len(str(phase_result))
                })
                
                logger.info(f"✅ {phase_name} concluída em {time.time() - phase_start:.1f}s")
                
            except asyncio.TimeoutError:
                logger.warning(f"⏰ Timeout na fase {phase_name}")
                expert_knowledge["study_phases_completed"].append({
                    "phase": phase_name,
                    "completed": False,
                    "timeout": True
                })
            except Exception as e:
                logger.error(f"❌ Erro na fase {phase_name}: {e}")
                expert_knowledge["study_phases_completed"].append({
                    "phase": phase_name,
                    "completed": False,
                    "error": str(e)
                })
        
        # Finaliza estudo
        total_study_time = time.time() - start_time
        expert_knowledge["study_metadata"]["actual_duration_seconds"] = total_study_time
        expert_knowledge["study_metadata"]["study_end"] = datetime.now().isoformat()
        expert_knowledge["study_metadata"]["phases_completed"] = len([p for p in expert_knowledge["study_phases_completed"] if p.get("completed")])
        expert_knowledge["study_metadata"]["efficiency_score"] = (expert_knowledge["study_metadata"]["phases_completed"] / len(study_phases)) * 100
        
        logger.info(f"🎓 ETAPA 2 concluída em {total_study_time/60:.1f} minutos")
        logger.info(f"📊 Fases completadas: {expert_knowledge['study_metadata']['phases_completed']}/{len(study_phases)}")
        
        return expert_knowledge

    async def _analyze_data_structure(self, massive_data: Dict[str, Any], expert_knowledge: Dict[str, Any]) -> Dict[str, Any]:
        """Analisa estrutura dos dados coletados"""
        
        prompt = f"""
        Analise a estrutura dos seguintes dados massivos coletados e extraia insights sobre:
        1. Qualidade e densidade das informações
        2. Principais fontes de dados identificadas
        3. Gaps ou lacunas nos dados
        4. Oportunidades de análise mais profunda
        
        Dados para análise (primeiros 3000 caracteres):
        {str(massive_data)[:3000]}...
        
        Forneça uma análise estrutural concisa e insights acionáveis.
        """
        
        analysis = await self.generate_text(prompt, max_tokens=1000)
        expert_knowledge["domain_expertise"]["data_structure_analysis"] = analysis
        return {"analysis": analysis}

    async def _extract_market_insights(self, massive_data: Dict[str, Any], expert_knowledge: Dict[str, Any]) -> Dict[str, Any]:
        """Extrai insights de mercado dos dados"""
        
        market_data = massive_data.get("market_intelligence", {})
        web_data = massive_data.get("web_intelligence", {})
        
        prompt = f"""
        Com base nos dados de mercado coletados, extraia insights profundos sobre:
        1. Tamanho e potencial do mercado
        2. Principais tendências identificadas
        3. Oportunidades de negócio
        4. Ameaças e desafios
        5. Segmentação de mercado
        
        Dados de mercado:
        {str(market_data)[:2000]}
        
        Dados web relevantes:
        {str(web_data)[:2000]}
        
        Forneça insights estratégicos acionáveis.
        """
        
        insights = await self.generate_text(prompt, max_tokens=1200)
        expert_knowledge["market_intelligence"] = insights
        return {"insights": insights}

    async def _analyze_competitive_landscape(self, massive_data: Dict[str, Any], expert_knowledge: Dict[str, Any]) -> Dict[str, Any]:
        """Analisa paisagem competitiva"""
        
        competitive_data = massive_data.get("competitive_intelligence", {})
        
        prompt = f"""
        Analise a paisagem competitiva com base nos dados coletados:
        1. Principais competidores identificados
        2. Forças e fraquezas de cada competidor
        3. Gaps competitivos e oportunidades
        4. Estratégias de diferenciação recomendadas
        5. Posicionamento ideal no mercado
        
        Dados competitivos:
        {str(competitive_data)[:2500]}
        
        Forneça análise competitiva estratégica.
        """
        
        analysis = await self.generate_text(prompt, max_tokens=1200)
        expert_knowledge["competitive_analysis"] = analysis
        return {"analysis": analysis}

    async def _identify_behavioral_patterns(self, massive_data: Dict[str, Any], expert_knowledge: Dict[str, Any]) -> Dict[str, Any]:
        """Identifica padrões comportamentais"""
        
        behavioral_data = massive_data.get("behavioral_intelligence", {})
        social_data = massive_data.get("social_intelligence", {})
        
        prompt = f"""
        Identifique padrões comportamentais dos consumidores:
        1. Principais motivações e necessidades
        2. Pontos de dor identificados
        3. Jornada do cliente típica
        4. Gatilhos de decisão de compra
        5. Canais de comunicação preferidos
        
        Dados comportamentais:
        {str(behavioral_data)[:2000]}
        
        Dados sociais:
        {str(social_data)[:2000]}
        
        Forneça insights comportamentais profundos.
        """
        
        patterns = await self.generate_text(prompt, max_tokens=1200)
        expert_knowledge["behavioral_insights"] = patterns
        return {"patterns": patterns}

    async def _analyze_trends(self, massive_data: Dict[str, Any], expert_knowledge: Dict[str, Any]) -> Dict[str, Any]:
        """Analisa tendências identificadas"""
        
        trend_data = massive_data.get("trend_intelligence", {})
        
        prompt = f"""
        Analise as tendências identificadas nos dados:
        1. Tendências emergentes mais relevantes
        2. Velocidade de adoção das tendências
        3. Impacto potencial no mercado
        4. Oportunidades de capitalização
        5. Riscos de não acompanhar as tendências
        
        Dados de tendências:
        {str(trend_data)[:2500]}
        
        Forneça análise de tendências estratégica.
        """
        
        analysis = await self.generate_text(prompt, max_tokens=1200)
        expert_knowledge["trend_analysis"] = analysis
        return {"analysis": analysis}

    async def _generate_predictive_insights(self, massive_data: Dict[str, Any], expert_knowledge: Dict[str, Any]) -> Dict[str, Any]:
        """Gera insights preditivos"""
        
        all_insights = {
            "market": expert_knowledge.get("market_intelligence", ""),
            "competitive": expert_knowledge.get("competitive_analysis", ""),
            "behavioral": expert_knowledge.get("behavioral_insights", ""),
            "trends": expert_knowledge.get("trend_analysis", "")
        }
        
        prompt = f"""
        Com base em toda a análise realizada, gere insights preditivos:
        1. Cenários futuros mais prováveis (6-24 meses)
        2. Oportunidades emergentes a serem exploradas
        3. Riscos futuros a serem mitigados
        4. Recomendações de timing para ações
        5. Indicadores-chave para monitoramento
        
        Síntese das análises realizadas:
        {str(all_insights)[:3000]}
        
        Forneça previsões estratégicas acionáveis.
        """
        
        predictions = await self.generate_text(prompt, max_tokens=1500)
        expert_knowledge["predictive_insights"] = predictions
        return {"predictions": predictions}

    async def _synthesize_strategic_recommendations(self, massive_data: Dict[str, Any], expert_knowledge: Dict[str, Any]) -> Dict[str, Any]:
        """Sintetiza recomendações estratégicas finais"""
        
        all_knowledge = {
            "market": expert_knowledge.get("market_intelligence", ""),
            "competitive": expert_knowledge.get("competitive_analysis", ""),
            "behavioral": expert_knowledge.get("behavioral_insights", ""),
            "trends": expert_knowledge.get("trend_analysis", ""),
            "predictions": expert_knowledge.get("predictive_insights", "")
        }
        
        prompt = f"""
        Sintetize todas as análises em recomendações estratégicas finais:
        1. Top 5 prioridades estratégicas imediatas
        2. Plano de ação para próximos 90 dias
        3. Investimentos recomendados
        4. Métricas de sucesso a acompanhar
        5. Próximos passos específicos
        
        Todo o conhecimento adquirido:
        {str(all_knowledge)[:4000]}
        
        Forneça recomendações estratégicas definitivas e acionáveis.
        """
        
        recommendations = await self.generate_text(prompt, max_tokens=1500)
        expert_knowledge["strategic_recommendations"] = recommendations
        return {"recommendations": recommendations}


# Instância global
enhanced_ai_manager = EnhancedAIManager()
