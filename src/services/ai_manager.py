#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ARQV30 Enhanced v2.0 - AI Manager com Sistema de Fallback
Gerenciador inteligente de múltiplas IAs com fallback automático
"""

import os
import logging
import time
import json
from typing import Dict, List, Optional, Any
import requests
from datetime import datetime, timedelta

# Imports condicionais para os clientes de IA
try:
    import google.generativeai as genai
    HAS_GEMINI = True
except ImportError:
    HAS_GEMINI = False

try:
    import openai
    HAS_OPENAI = True
except ImportError:
    HAS_OPENAI = False

try:
    from services.groq_client import groq_client
    HAS_GROQ_CLIENT = True
except ImportError:
    HAS_GROQ_CLIENT = False

logger = logging.getLogger(__name__)

class QuotaManager:
    """Gerenciador inteligente de quotas de API"""

    def __init__(self):
        self.provider_limits = {
            'gemini': {'daily': 45, 'hourly': 10, 'requests_made': 0, 'last_reset': datetime.now()},
            'openai': {'daily': 1000, 'hourly': 100, 'requests_made': 0, 'last_reset': datetime.now()},
            'groq': {'daily': 500, 'hourly': 50, 'requests_made': 0, 'last_reset': datetime.now()},
            'huggingface': {'daily': 200, 'hourly': 20, 'requests_made': 0, 'last_reset': datetime.now()}
        }
        self.reset_counters()

    def reset_counters(self):
        """Reset contadores diários se necessário"""
        now = datetime.now()
        for provider, limits in self.provider_limits.items():
            if now - limits['last_reset'] >= timedelta(days=1):
                limits['requests_made'] = 0
                limits['last_reset'] = now

    def can_use_provider(self, provider: str) -> bool:
        """Verifica se provider ainda tem quota disponível"""
        self.reset_counters()
        if provider not in self.provider_limits:
            return False

        limits = self.provider_limits[provider]
        return limits['requests_made'] < limits['daily']

    def increment_usage(self, provider: str):
        """Incrementa uso do provider"""
        if provider in self.provider_limits:
            self.provider_limits[provider]['requests_made'] += 1

    def get_best_provider(self, component_type: str = 'general') -> Optional[str]:
        """Seleciona melhor provider baseado em quota disponível"""
        # Prioridades por tipo de componente
        priority_map = {
            'mental_drivers': ['openai', 'groq', 'gemini', 'huggingface'],
            'visual_proofs': ['gemini', 'openai', 'groq', 'huggingface'],
            'anti_objection': ['openai', 'groq', 'gemini', 'huggingface'],
            'general': ['openai', 'groq', 'gemini', 'huggingface']
        }

        priorities = priority_map.get(component_type, priority_map['general'])

        for provider in priorities:
            if self.can_use_provider(provider):
                return provider

        return None

class ContentValidator:
    """Validador robusto de conteúdo gerado"""

    GENERIC_PATTERNS = [
        'customizado para', 'adequado para', 'personalizado',
        'este produto é ideal', 'nossa solução', 'produto ou serviço',
        'sua empresa', 'seu negócio', 'mercado específico'
    ]

    MIN_CONTENT_LENGTH = {
        'mental_drivers': 500,
        'visual_proofs': 300,
        'anti_objection': 400,
        'general': 200
    }

    def validate_content(self, content: str, component: str = 'general') -> tuple[bool, str]:
        """Valida qualidade do conteúdo gerado"""
        if not content or not isinstance(content, str):
            return False, "Conteúdo vazio ou inválido"

        # Verificar tamanho mínimo (reduzido para ser menos restritivo)
        min_length = self.MIN_CONTENT_LENGTH.get(component, 150)
        if len(content.strip()) < min_length:
            return False, f"Conteúdo muito curto: {len(content)} < {min_length}"

        # Verificar padrões genéricos (mais tolerante)
        generic_count = sum(1 for pattern in self.GENERIC_PATTERNS 
                           if pattern.lower() in content.lower())
        if generic_count > 5:  # Aumentado de 3 para 5
            return False, f"Muito genérico: {generic_count} padrões encontrados"

        # Verificar repetição excessiva (mais tolerante)
        words = content.lower().split()
        unique_ratio = len(set(words)) / len(words) if words else 0
        
        # Considera contexto do componente
        min_unique_ratio = {
            'mental_drivers': 0.25,  # Drivers podem ter mais repetição
            'visual_proofs': 0.3,
            'anti_objection': 0.25,  # Anti-objeção pode repetir padrões
            'general': 0.25  # Reduzido de 0.3 para 0.25
        }.get(component, 0.25)
        
        if unique_ratio < min_unique_ratio:
            return False, f"Conteúdo repetitivo: {unique_ratio:.1%} palavras únicas (mín: {min_unique_ratio:.1%})"

        # Verificar se tem estrutura mínima (JSON, pontos, etc.)
        has_structure = any([
            '{' in content and '}' in content,  # JSON
            content.count('\n') > 2,  # Múltiplas linhas
            content.count('.') > 3,  # Múltiplas sentenças
            content.count('-') > 2,  # Lista com pontos
            content.count(':') > 1   # Estrutura com dois pontos
        ])
        
        if not has_structure and len(content) > 500:
            return False, "Conteúdo sem estrutura aparente"

        return True, "Conteúdo válido"

class AIManager:
    """Gerenciador de IA com múltiplos provedores e fallbacks robustos"""

    def __init__(self):
        """Inicializa o gerenciador de IA"""
        self.providers = {}
        self.fallback_chain = ['openai', 'groq', 'gemini', 'huggingface']
        self.provider_failures = {}
        self.disabled_providers = set()
        self.quota_manager = QuotaManager()
        self.content_validator = ContentValidator()
        self.emergency_templates = self._load_emergency_templates()
        self.initialize_providers()

    def _load_emergency_templates(self) -> Dict[str, str]:
        """Carrega templates de emergência para cada componente"""
        return {
            'mental_drivers': """
DRIVER MENTAL CUSTOMIZADO: {segmento}

1. DRIVER DA TRANSFORMAÇÃO NECESSÁRIA
- Gatilho: Frustração com resultados atuais
- Mecânica: Contraste entre situação atual e potencial
- Ativação: "Você já tentou de tudo, mas sempre falta algo crucial..."

2. DRIVER DA OPORTUNIDADE PERDIDA
- Gatilho: Medo de ficar para trás
- Mecânica: Urgência competitiva
- Ativação: "Enquanto você hesita, seus concorrentes avançam..."

3. DRIVER DA AUTORIDADE RECONHECIDA
- Gatilho: Desejo de ser respeitado
- Mecânica: Validação social
- Ativação: "Imagine ser a referência em {segmento}..."
""",
            'visual_proofs': """
PROVA VISUAL 1: TRANSFORMAÇÃO DRAMÁTICA
- Conceito: Antes vs Depois em {segmento}
- Execução: Comparação visual clara de resultados
- Materiais: Gráficos, dados, métricas

PROVA VISUAL 2: MÉTODO REVELADO
- Conceito: Como funciona na prática
- Execução: Demonstração passo a passo
- Materiais: Diagramas, fluxogramas

PROVA VISUAL 3: PROVA SOCIAL
- Conceito: Outros já conseguiram
- Execução: Cases de sucesso documentados
- Materiais: Depoimentos, resultados
""",
            'anti_objection': """
SISTEMA ANTI-OBJEÇÃO: {segmento}

OBJEÇÃO: "Não tenho tempo"
RESPOSTA: O tempo que você 'não tem' para se capacitar é exatamente o tempo que está perdendo com ineficiência.

OBJEÇÃO: "É muito caro"
RESPOSTA: O custo de não agir é sempre maior que o investimento em crescimento.

OBJEÇÃO: "Já tentei outras coisas"
RESPOSTA: As tentativas anteriores falharam porque faltava metodologia sistêmica.
"""
        }

    def initialize_providers(self):
        """Inicializa todos os provedores de IA com base nas chaves de API disponíveis."""

        # Inicializa Gemini com modelo 2.0 Flash
        if HAS_GEMINI:
            try:
                gemini_key = os.getenv('GEMINI_API_KEY')
                if gemini_key:
                    genai.configure(api_key=gemini_key)
                    # Usa o modelo 2.0 Flash para melhor performance
                    self.providers['gemini'] = {
                        'client': genai.GenerativeModel("gemini-2.0-flash-exp"),
                        'available': True,
                        'model': "gemini-2.0-flash-exp",
                        'priority': 1,
                        'error_count': 0,
                        'consecutive_failures': 0,
                        'max_errors': 5,  # Mais tolerante
                        'last_success': None,
                        'daily_requests': 0,
                        'daily_limit': 1500  # Limite diário do Gemini
                    }
                    logger.info("✅ Gemini 2.0 Flash Experimental inicializado.")
                else:
                    logger.warning("⚠️ Chave API do Gemini (GEMINI_API_KEY) não encontrada.")
            except Exception as e:
                logger.warning(f"⚠️ Falha ao inicializar Gemini: {str(e)}")
        else:
            logger.warning("⚠️ Biblioteca 'google-generativeai' não instalada.")

        # Inicializa OpenAI com sistema de rotação
        if HAS_OPENAI:
            try:
                openai_key = os.getenv('OPENAI_API_KEY')
                if openai_key:
                    self.providers["openai"] = {
                        'client': openai.OpenAI(api_key=openai_key),
                        'available': True,
                        'model': 'gpt-4o-mini',  # Usa modelo mais econômico
                        'priority': 2,
                        'error_count': 0,
                        'consecutive_failures': 0,
                        'max_errors': 5,  # Mais tolerante
                        'last_success': None,
                        'daily_requests': 0,
                        'daily_limit': 10000,  # Limite mais conservador
                        'quota_exceeded': False
                    }
                    logger.info("✅ OpenAI (gpt-4o-mini) inicializado.")
            except Exception as e:
                logger.info(f"ℹ️ OpenAI não disponível: {str(e)}")
        else:
            logger.info("ℹ️ Biblioteca 'openai' não instalada.")

        # Inicializa Groq
        try:
            if HAS_GROQ_CLIENT and groq_client and groq_client.is_enabled():
                self.providers['groq'] = {
                    'client': groq_client,
                    'available': True,
                    'model': 'llama3-70b-8192',
                    'priority': 3,
                    'error_count': 0,
                    'consecutive_failures': 0,
                    'max_errors': 3,
                    'last_success': None
                }
                logger.info("✅ Groq (llama3-70b-8192) inicializado.")
            else:
                logger.info("ℹ️ Groq client não configurado ou desabilitado.")
        except Exception as e:
            logger.info(f"ℹ️ Groq não disponível: {str(e)}")

        # Inicializa HuggingFace
        try:
            hf_key = os.getenv('HUGGINGFACE_API_KEY')
            if hf_key:
                self.providers['huggingface'] = {
                    'client': {
                        'api_key': hf_key,
                        'base_url': 'https://api-inference.huggingface.co/models/'
                    },
                    'available': True,
                    'models': ["HuggingFaceH4/zephyr-7b-beta", "google/flan-t5-base"],
                    'current_model_index': 0,
                    'priority': 4,
                    'error_count': 0,
                    'consecutive_failures': 0,
                    'max_errors': 5, # Mais tolerante a falhas temporárias
                    'last_success': None
                }
                logger.info("✅ HuggingFace inicializado.")
        except Exception as e:
            logger.info(f"ℹ️ HuggingFace não disponível: {str(e)}")

        # Atualiza a fallback_chain com base nos provedores disponíveis
        self.fallback_chain = [p for p in self.fallback_chain if p in self.providers and self.providers[p]['available']]
        
        # Configura o primary_provider inicial
        self.primary_provider = self.fallback_chain[0] if self.fallback_chain else None
        if self.primary_provider:
            logger.info(f"✅ Provedor primário definido: {self.primary_provider.upper()}")
        else:
            logger.error("❌ Nenhum provedor de IA disponível para inicialização!")

    def _register_failure(self, provider_name: str, error_msg: str):
        """Registra falha do provedor e desabilita temporariamente se necessário"""
        if provider_name not in self.providers:
            return

        # Detecta erro de quota
        if any(quota_indicator in error_msg.lower() for quota_indicator in 
               ['quota', 'rate limit', 'too many requests', 'insufficient_quota']):
            self.providers[provider_name]['quota_exceeded'] = True
            logger.warning(f"🚫 {provider_name} - QUOTA EXCEDIDA. Pausando por 1 hora.")
            self.disabled_providers.add(provider_name)
            # Agenda reativação em 1 hora
            self.providers[provider_name]['reactivate_at'] = time.time() + 3600
        else:
            self.providers[provider_name]['error_count'] += 1
            self.providers[provider_name]['consecutive_failures'] += 1

        self.provider_failures[provider_name] = self.providers[provider_name]['consecutive_failures']

        if self.providers[provider_name]['consecutive_failures'] >= self.providers[provider_name]['max_errors']:
            self.disabled_providers.add(provider_name)
            logger.warning(f"⚠️ Desabilitando {provider_name} temporariamente após {self.providers[provider_name]['consecutive_failures']} falhas consecutivas.")

        logger.error(f"❌ Falha registrada para {provider_name}: {error_msg}")

    def _register_success(self, provider_name: str):
        """Registra sucesso do provedor e reseta contadores de falha"""
        if provider_name in self.providers:
            self.providers[provider_name]['consecutive_failures'] = 0
            self.providers[provider_name]['last_success'] = time.time()
            if provider_name in self.disabled_providers:
                self.disabled_providers.remove(provider_name)
                logger.info(f"✅ {provider_name} reabilitado.")
            logger.debug(f"✅ Sucesso registrado para {provider_name}")

    def safe_serialize(self, obj: Any, visited: set = None, depth: int = 0) -> Any:
        """Serialização 100% segura contra referências circulares"""
        if visited is None:
            visited = set()

        # Limite de profundidade para evitar recursão infinita
        if depth > 15:
            return {"__max_depth__": f"Depth limit reached at {depth}"}

        # Verifica referência circular
        obj_id = id(obj)
        if obj_id in visited:
            return {"__circular_ref__": f"{type(obj).__name__}_{obj_id}"}

        # Marca objeto como visitado
        visited.add(obj_id)

        try:
            # Tipos primitivos - retorna direto
            if obj is None or isinstance(obj, (bool, int, float, str)):
                return obj

            # Dicionários
            if isinstance(obj, dict):
                result = {}
                for key, value in obj.items():
                    # Converte chaves para string segura
                    safe_key = str(key)[:100] if not isinstance(key, str) else key[:100]
                    try:
                        result[safe_key] = self.safe_serialize(value, visited.copy(), depth + 1)
                    except Exception as e:
                        result[safe_key] = f"<Error serializing: {str(e)[:50]}>"
                return result

            # Listas e tuplas
            if isinstance(obj, (list, tuple)):
                result = []
                for i, item in enumerate(obj[:50]):  # Limita a 50 itens
                    try:
                        result.append(self.safe_serialize(item, visited.copy(), depth + 1))
                    except Exception as e:
                        result.append(f"<Error at index {i}: {str(e)[:50]}>")
                return result

            # Objetos com __dict__
            if hasattr(obj, '__dict__'):
                try:
                    return self.safe_serialize(obj.__dict__, visited.copy(), depth + 1)
                except:
                    return {"__object__": f"{type(obj).__name__}"}

            # Outros tipos - converte para string segura
            try:
                str_repr = str(obj)[:500]
                return {"__string_repr__": str_repr, "__type__": type(obj).__name__}
            except:
                return {"__unserializable__": type(obj).__name__}

        except Exception as e:
            return {"__serialization_error__": str(e)[:100]}
        finally:
            visited.discard(obj_id)

    def _clean_for_serialization(self, obj, seen=None, depth=0):
        """Método legado - chama o novo sistema seguro"""
        return self.safe_serialize(obj, seen, depth)

    def generate_analysis(self, prompt: str, component_type: str = 'general', **kwargs) -> Optional[str]:
        """Gera análise com fallback inteligente, rate limiting e validação de qualidade"""

        # Verifica e reativa provedores que podem ter se recuperado
        self._check_and_reactivate_providers()

        # Aplica rate limiting inteligente
        self._apply_intelligent_rate_limiting()

        # Primeiro tenta com provider otimizado para o tipo de componente
        best_provider = self.quota_manager.get_best_provider(component_type)

        if best_provider and best_provider not in self.disabled_providers:
            # Tenta com o melhor provider disponível
            result = self._try_provider_with_exponential_backoff(best_provider, prompt, component_type, **kwargs)
            if result:
                return result

        # Fallback para todos os providers disponíveis com priorização inteligente
        fallback_order = self._get_intelligent_fallback_order(component_type)
        
        for provider_name in fallback_order:
            if provider_name == best_provider:  # Já tentou
                continue

            if provider_name in self.disabled_providers:
                continue

            if not self.quota_manager.can_use_provider(provider_name):
                logger.warning(f"⚠️ {provider_name} sem quota disponível")
                continue

            result = self._try_provider_with_exponential_backoff(provider_name, prompt, component_type, **kwargs)
            if result:
                return result

        # Fallback final: template de emergência MELHORADO
        logger.warning("🚨 Todos os providers falharam, usando template de emergência melhorado")
        return self._generate_enhanced_emergency_content(component_type, kwargs.get('data', {}))
    
    def generate_with_tools(self, prompt: str, tools: List[Dict[str, Any]] = None, **kwargs) -> Dict[str, Any]:
        """Gera análise com suporte a tool use"""
        
        if not tools:
            # Define ferramentas padrão
            tools = [
                {
                    'name': 'google_search',
                    'description': 'Busca informações específicas no Google',
                    'parameters': {
                        'query': {'type': 'string', 'description': 'Query de busca'}
                    }
                },
                {
                    'name': 'web_extract',
                    'description': 'Extrai conteúdo de uma URL específica',
                    'parameters': {
                        'url': {'type': 'string', 'description': 'URL para extrair conteúdo'}
                    }
                },
                {
                    'name': 'social_search',
                    'description': 'Busca dados específicos em redes sociais',
                    'parameters': {
                        'query': {'type': 'string', 'description': 'Query para busca social'}
                    }
                }
            ]
        
        # Adiciona instruções de tool use ao prompt
        enhanced_prompt = f"""
{prompt}

FERRAMENTAS DISPONÍVEIS:
Você pode usar as seguintes ferramentas para obter informações adicionais:

1. google_search("sua query aqui") - Para buscar informações específicas
2. web_extract("url aqui") - Para extrair conteúdo de URLs
3. social_search("sua query aqui") - Para buscar em redes sociais

Para usar uma ferramenta, inclua na sua resposta exatamente como mostrado acima.
Exemplo: google_search("tendências telemedicina Brasil 2024")

Continue sua análise normalmente. Use ferramentas apenas se precisar de informações específicas adicionais.
"""
        
        try:
            # Gera resposta com prompt aprimorado
            response = self.generate_analysis(enhanced_prompt, **kwargs)
            
            return {
                'response': response,
                'tools_available': tools,
                'tool_use_enabled': True
            }
            
        except Exception as e:
            logger.error(f"❌ Erro na geração com tools: {e}")
            return {
                'response': None,
                'error': str(e),
                'tool_use_enabled': False
            }

    def _try_provider_with_validation(self, provider_name: str, prompt: str, component_type: str, **kwargs) -> Optional[str]:
        """Tenta um provider específico com validação de qualidade"""
        provider_info = self.providers.get(provider_name)
        if not provider_info or not provider_info.get('client'):
            return None

        client = provider_info['client']
        model = provider_info['model']

        try:
            logger.info(f"🤖 Tentando geração com {provider_name} ({model}) para {component_type}")

            # Incrementa contador de quota
            self.quota_manager.increment_usage(provider_name)

            # Tenta gerar com o provedor
            result = None
            if provider_name == 'gemini':
                config = genai.types.GenerationConfig(
                    temperature=kwargs.get('temperature', 0.8),  # Aumenta temperatura para reduzir repetição
                    top_p=kwargs.get('top_p', 0.95),
                    top_k=kwargs.get('top_k', 64),
                    max_output_tokens=kwargs.get('max_tokens', 4096)
                )
                safety = [
                    {"category": c, "threshold": "BLOCK_NONE"}
                    for c in ["HARM_CATEGORY_HARASSMENT", "HARM_CATEGORY_HATE_SPEECH", "HARM_CATEGORY_SEXUALLY_EXPLICIT", "HARM_CATEGORY_DANGEROUS_CONTENT"]
                ]
                response = client.generate_content(prompt, generation_config=config, safety_settings=safety)
                if response.text:
                    result = response.text
                    
                    # VALIDAÇÃO ESPECÍFICA PARA GEMINI: Detecta conteúdo repetitivo
                    is_repetitive, repetition_msg = self._validate_gemini_response(result)
                    if is_repetitive:
                        logger.warning(f"⚠️ Conteúdo repetitivo detectado na Gemini: {repetition_msg}")
                        # Tenta novamente com temperatura mais alta
                        config.temperature = min(1.0, config.temperature + 0.2)
                        response = client.generate_content(prompt, generation_config=config, safety_settings=safety)
                        if response.text:
                            result = response.text
                            # Verifica novamente
                            is_repetitive_retry, _ = self._validate_gemini_response(result)
                            if is_repetitive_retry:
                                logger.error(f"❌ Gemini continua gerando conteúdo repetitivo após retry")
                                self._register_failure(provider_name, "Conteúdo persistentemente repetitivo")
                                return None
            elif provider_name == 'openai':
                response = client.chat.completions.create(
                    model=model,
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=kwargs.get('max_tokens', 4096),
                    temperature=kwargs.get('temperature', 0.7)
                )
                result = response.choices[0].message.content
            elif provider_name == 'groq':
                result = client.generate(prompt, max_tokens=kwargs.get('max_tokens', 4096))
            elif provider_name == 'huggingface':
                url = f"{provider_info['client']['base_url']}{model}"
                headers = {"Authorization": f"Bearer {provider_info['client']['api_key']}"}
                payload = {"inputs": prompt, "parameters": {"max_new_tokens": kwargs.get('max_tokens', 1024)}}
                response = requests.post(url, headers=headers, json=payload, timeout=60)
                if response.status_code == 200:
                    res_json = response.json()
                    result = res_json[0].get("generated_text", "")
                elif response.status_code == 503:
                    raise Exception("Modelo HuggingFace está carregando (503)")
                else:
                    raise Exception(f"Erro {response.status_code}: {response.text}")
            
            if not result or len(result.strip()) < 50:
                logger.warning(f"⚠️ Resultado vazio ou muito curto de {provider_name}")
                return None

            # Valida qualidade do conteúdo
            is_valid, validation_msg = self.content_validator.validate_content(result, component_type)

            if not is_valid:
                logger.warning(f"⚠️ Conteúdo de {provider_name} rejeitado: {validation_msg}")
                # Se o conteúdo for rejeitado, considera como falha para o provedor
                self._register_failure(provider_name, f"Conteúdo rejeitado: {validation_msg}")
                return None

            self._register_success(provider_name)
            logger.info(f"✅ Geração bem-sucedida e validada com {provider_name}")
            return result

        except Exception as e:
            logger.error(f"❌ Erro em {provider_name}: {e}")
            self._register_failure(provider_name, str(e))
            return None

    def _generate_emergency_content(self, component_type: str, data: Dict[str, Any]) -> str:
        """Gera conteúdo de emergência usando templates"""
        template = self.emergency_templates.get(component_type, self.emergency_templates.get('general', ''))

        # Substitui variáveis do template
        try:
            segmento = data.get('segmento', 'negócios')
            produto = data.get('produto', 'produto/serviço')

            content = template.format(
                segmento=segmento,
                produto=produto
            )

            logger.info(f"🚨 Template de emergência gerado para {component_type}")
            return content

        except Exception as e:
            logger.error(f"❌ Erro ao gerar template de emergência: {e}")
            return f"""
CONTEÚDO DE EMERGÊNCIA: {component_type.upper()}

Este é um conteúdo gerado em modo de emergência devido a falhas nos sistemas de IA.
O sistema detectou problemas técnicos e ativou o protocolo de continuidade.

Componente: {component_type}
Data: {data.get('segmento', 'Não informado')}
Status: Sistema em modo de recuperação

Recomenda-se verificar logs e configurações de API.
"""

    def _validate_gemini_response(self, response: str) -> tuple[bool, str]:
        """Valida resposta da Gemini para detectar conteúdo repetitivo"""
        import re
        
        if not response or len(response.strip()) < 100:
            return True, "Conteúdo muito curto para validar repetição"
        
        # Divide em sentenças
        sentences = re.split(r'[.!?]+', response)
        sentences = [s.strip().lower() for s in sentences if len(s.strip()) > 10]
        
        if len(sentences) < 5:
            return False, "Poucas sentenças para análise"
        
        # Conta repetições de sentenças
        sentence_counts = {}
        for sentence in sentences:
            # Normaliza a sentença (remove espaços extras, pontuação)
            normalized = re.sub(r'[^\w\s]', '', sentence)
            normalized = ' '.join(normalized.split())
            
            if len(normalized) > 15:  # Ignora sentenças muito curtas
                sentence_counts[normalized] = sentence_counts.get(normalized, 0) + 1
        
        # Verifica se alguma sentença se repete muito
        max_repetitions = max(sentence_counts.values()) if sentence_counts else 0
        repetition_rate = max_repetitions / len(sentences) if sentences else 0
        
        # Considera repetitivo se:
        # 1. Alguma sentença aparece mais de 3 vezes
        # 2. Mais de 30% das sentenças são repetições
        if max_repetitions > 3:
            return True, f"Sentença repetida {max_repetitions} vezes"
        
        if repetition_rate > 0.3:
            return True, f"Taxa de repetição alta: {repetition_rate:.1%}"
        
        # Verifica repetição de frases/padrões
        words = response.lower().split()
        if len(words) < 50:
            return False, "Texto muito curto"
        
        # Conta palavras únicas vs total
        unique_words = len(set(words))
        word_diversity = unique_words / len(words)
        
        if word_diversity < 0.3:  # Menos de 30% de palavras únicas
            return True, f"Baixa diversidade de palavras: {word_diversity:.1%}"
        
        return False, "Conteúdo válido sem repetição excessiva"

    def generate_content(self, prompt: str, max_tokens: int = 4096, component_type: str = 'general', **kwargs) -> str:
        """Gera conteúdo usando o melhor provedor disponível com fallback e validação"""
        
        # Verifica disponibilidade geral
        if not any(p['available'] for p in self.providers.values()):
            logger.error("❌ Nenhum provedor de IA está disponível.")
            return "Erro: Nenhum provedor de IA disponível."

        # Tenta gerar análise
        content = self.generate_analysis(prompt, component_type=component_type, max_tokens=max_tokens, **kwargs)

        if content and not content.startswith("Erro:") and not content.startswith("CONTEÚDO DE EMERGÊNCIA:"):
            # Validação final após geração
            is_valid, msg = self.content_validator.validate_content(content, component_type)
            if is_valid:
                return content
            else:
                logger.warning(f"Conteúdo final rejeitado pela validação: {msg}")
                # Se a validação final falhar, tenta gerar um template de emergência
                return self._generate_emergency_content(component_type, {'segmento': component_type})
        
        # Retorna o conteúdo de emergência se a geração falhar completamente
        if not content:
            return self._generate_emergency_content(component_type, {'segmento': component_type})
            
        return content

    def _check_and_reactivate_providers(self):
        """Verifica e reativa provedores que podem ter se recuperado"""
        current_time = time.time()
        
        for provider_name in list(self.disabled_providers):
            provider_info = self.providers.get(provider_name, {})
            
            # Verifica se é hora de reativar por quota
            reactivate_at = provider_info.get('reactivate_at', 0)
            if reactivate_at > 0 and current_time >= reactivate_at:
                self.disabled_providers.discard(provider_name)
                self.providers[provider_name]['quota_exceeded'] = False
                self.providers[provider_name]['consecutive_failures'] = 0
                self.providers[provider_name]['reactivate_at'] = 0
                logger.info(f"✅ {provider_name} reativado após cooldown de quota")

    def _apply_intelligent_rate_limiting(self):
        """Aplica rate limiting inteligente baseado no histórico de uso"""
        current_time = time.time()
        
        for provider_name, provider_info in self.providers.items():
            # Verifica se precisa de delay baseado no histórico
            last_request = provider_info.get('last_request_time', 0)
            requests_in_minute = provider_info.get('requests_in_minute', 0)
            
            # Se fez muitas requisições no último minuto, adiciona delay
            if current_time - last_request < 60 and requests_in_minute >= 10:
                delay = min(5, requests_in_minute * 0.5)  # Máximo 5 segundos
                logger.info(f"⏱️ Rate limiting {provider_name}: aguardando {delay:.1f}s")
                time.sleep(delay)
                
            # Reset contador se passou mais de 1 minuto
            if current_time - last_request > 60:
                provider_info['requests_in_minute'] = 0

    def _try_provider_with_exponential_backoff(self, provider_name: str, prompt: str, component_type: str, **kwargs) -> Optional[str]:
        """Tenta provider com exponential backoff em caso de rate limiting"""
        max_retries = 3
        base_delay = 2
        
        for attempt in range(max_retries):
            try:
                result = self._try_provider_with_validation(provider_name, prompt, component_type, **kwargs)
                if result:
                    return result
                    
            except Exception as e:
                error_msg = str(e).lower()
                
                # Se é erro de rate limiting (429), aplica exponential backoff
                if '429' in error_msg or 'rate limit' in error_msg or 'too many requests' in error_msg:
                    if attempt < max_retries - 1:  # Não espera na última tentativa
                        delay = base_delay * (2 ** attempt)  # 2, 4, 8 segundos
                        logger.warning(f"⏱️ Rate limit em {provider_name}, tentativa {attempt + 1}/{max_retries}. Aguardando {delay}s...")
                        time.sleep(delay)
                        continue
                else:
                    # Para outros erros, falha imediatamente
                    self._register_failure(provider_name, str(e))
                    break
                    
        return None

    def _get_intelligent_fallback_order(self, component_type: str) -> List[str]:
        """Determina ordem inteligente de fallback baseada no histórico de sucesso"""
        # Ordena providers por taxa de sucesso e disponibilidade
        available_providers = [
            name for name in self.fallback_chain 
            if name in self.providers and 
            self.providers[name]['available'] and 
            name not in self.disabled_providers
        ]
        
        # Ordena por sucesso recente (menos falhas consecutivas primeiro)
        return sorted(available_providers, 
                     key=lambda x: self.providers[x].get('consecutive_failures', 0))

    def _generate_enhanced_emergency_content(self, component_type: str, data: Dict[str, Any]) -> str:
        """Gera conteúdo de emergência MELHORADO com dados mais ricos"""
        
        # Templates melhorados baseados no contexto
        enhanced_templates = {
            'mental_drivers': self._generate_emergency_drivers(data),
            'visual_proofs': self._generate_emergency_proofs(data),
            'anti_objection': self._generate_emergency_anti_objection(data),
            'general': self._generate_emergency_general(data)
        }
        
        template = enhanced_templates.get(component_type, enhanced_templates['general'])
        
        logger.info(f"🚨 Template de emergência MELHORADO gerado para {component_type}")
        return template

    def _generate_emergency_drivers(self, data: Dict[str, Any]) -> str:
        """Gera drivers de emergência baseados no contexto"""
        segmento = data.get('segmento', 'negócios')
        
        return f"""
{{
  "drivers_mentais_arsenal": [
    {{
      "numero": 1,
      "nome": "DRIVER DA TRANSFORMAÇÃO URGENTE",
      "gatilho_central": "Necessidade imediata de mudança no {segmento}",
      "definicao_visceral": "Reconhecer que o status quo não é mais sustentável",
      "mecanica_psicologica": "Ativa urgência pela mudança necessária",
      "roteiro_ativacao": {{
        "pergunta_abertura": "Quando foi a última vez que você sentiu que estava realmente progredindo em {segmento}?",
        "historia_analogia": "Um profissional de {segmento} descobriu que trabalhar mais não era a solução...",
        "metafora_visual": "É como correr numa esteira - muito esforço, nenhum avanço real",
        "comando_acao": "Identifique agora o que realmente precisa mudar"
      }},
      "frases_ancoragem": [
        "Mais do mesmo gera mais do mesmo",
        "A definição de insanidade é repetir e esperar resultados diferentes",
        "Mudança é a única constante do sucesso"
      ]
    }}
  ],
  "emergency_mode": true,
  "context_adapted": true
}}
"""

    def _generate_emergency_proofs(self, data: Dict[str, Any]) -> str:
        """Gera provas visuais de emergência"""
        segmento = data.get('segmento', 'negócios')
        
        return f"""
{{
  "arsenal_provas_visuais": [
    {{
      "nome": "PROVA VISUAL 1: Transformação Comprovada",
      "categoria": "Instaladora de Crença",
      "objetivo_psicologico": "Demonstrar possibilidade real de mudança",
      "conceito_alvo": "Resultados tangíveis em {segmento}",
      "experimento_detalhado": "Comparação antes/depois de implementação",
      "roteiro_execucao": {{
        "setup": "Apresentar caso real de transformação",
        "execucao": "Mostrar métricas específicas de melhoria",
        "climax": "Revelar o resultado final surpreendente",
        "bridge": "Conectar com a situação atual do prospect"
      }}
    }}
  ],
  "emergency_mode": true,
  "context_adapted": true
}}
"""

    def _generate_emergency_anti_objection(self, data: Dict[str, Any]) -> str:
        """Gera sistema anti-objeção de emergência"""
        return """
{
  "sistema_anti_objecao": {
    "objecoes_universais": {
      "tempo": {
        "objecao_principal": "Não tenho tempo para implementar isso",
        "contra_ataque_principal": "Técnica do Cálculo da Sangria Temporal",
        "scripts_neutralizacao": [
          "Quanto tempo você está perdendo por não ter isso implementado?",
          "O tempo que você 'não tem' é exatamente o que está sendo desperdiçado",
          "Vamos calcular: quantas horas você perde por semana com ineficiência?"
        ]
      },
      "dinheiro": {
        "objecao_principal": "Está muito caro para mim agora",
        "contra_ataque_principal": "Comparação Cruel do Custo de Oportunidade",
        "scripts_neutralizacao": [
          "Qual o custo de não tomar esta decisão?",
          "Quanto você já perdeu mantendo as coisas como estão?",
          "O que é mais caro: investir na solução ou continuar com o problema?"
        ]
      }
    },
    "emergency_mode": true
  }
}
"""

    def _generate_emergency_general(self, data: Dict[str, Any]) -> str:
        """Gera conteúdo geral de emergência"""
        segmento = data.get('segmento', 'negócios')
        
        return f"""
CONTEÚDO DE EMERGÊNCIA CONTEXTUALIZADO: {segmento.upper()}

SITUAÇÃO: O sistema está operando em modo de emergência devido a limitações temporárias de API.

ANÁLISE BASEADA EM PADRÕES CONHECIDOS:

1. OPORTUNIDADE IDENTIFICADA
   - Mercado de {segmento} em constante evolução
   - Necessidade de diferenciação competitiva
   - Demanda por soluções personalizadas

2. ESTRATÉGIA RECOMENDADA
   - Foco na personalização extrema
   - Implementação gradual e mensurável
   - Acompanhamento de resultados

3. PRÓXIMOS PASSOS
   - Validar estratégia com dados específicos
   - Implementar fase piloto
   - Escalar conforme resultados

STATUS: Conteúdo gerado em modo de emergência - recomenda-se nova análise com APIs disponíveis.
"""

    def get_provider_status(self) -> Dict[str, Dict[str, Any]]:
        """Retorna status detalhado de todos os provedores"""
        status = {}
        for name, provider_info in self.providers.items():
            status[name] = {
                'available': provider_info.get('available', False),
                'model': provider_info.get('model', 'N/A'),
                'priority': provider_info.get('priority', 99),
                'error_count': provider_info.get('error_count', 0),
                'consecutive_failures': provider_info.get('consecutive_failures', 0),
                'disabled': name in self.disabled_providers,
                'quota_exceeded': provider_info.get('quota_exceeded', False),
                'daily_requests': provider_info.get('daily_requests', 0),
                'daily_limit': provider_info.get('daily_limit', 0),
                'quota_daily_remaining': self.quota_manager.provider_limits.get(name, {}).get('daily', 0) - self.quota_manager.provider_limits.get(name, {}).get('requests_made', 0),
                'requests_in_minute': provider_info.get('requests_in_minute', 0),
                'last_request_time': provider_info.get('last_request_time', 0)
            }
        return status

# Instância global
ai_manager = AIManager()