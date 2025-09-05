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

class AIManager:
    """Gerenciador de IAs com sistema de fallback automático"""

    def __init__(self):
        """Inicializa o gerenciador de IAs"""
        self.providers = {
            'gemini': {
                'client': None,
                'available': False,
                'priority': 1,  # GEMINI PRO CONFIRMADO COMO PRIORIDADE MÁXIMA
                'error_count': 0,
                'model': 'gemini-2.5-pro',  # Gemini 2.5 Pro
                'max_errors': 2,
                'last_success': None,
                'consecutive_failures': 0
            },
            'groq': {
                'client': None,
                'available': False,
                'priority': 2,  # FALLBACK AUTOMÁTICO
                'error_count': 0,
                'model': 'llama3-70b-8192',
                'max_errors': 2,
                'last_success': None,
                'consecutive_failures': 0
            },
            'openai': {
                'client': None,
                'available': False,
                'priority': 3,
                'error_count': 0,
                'model': 'gpt-3.5-turbo',
                'max_errors': 2,
                'last_success': None,
                'consecutive_failures': 0
            },
            'huggingface': {
                'client': None,
                'available': False,
                'priority': 4,
                'error_count': 0,
                'models': ["HuggingFaceH4/zephyr-7b-beta", "google/flan-t5-base"],
                'current_model_index': 0,
                'max_errors': 3,
                'last_success': None,
                'consecutive_failures': 0
            }
        }

        self.initialize_providers()
        available_count = len([p for p in self.providers.values() if p['available']])
        logger.info(f"🤖 AI Manager inicializado com {available_count} provedores disponíveis.")

    def initialize_providers(self):
        """Inicializa todos os provedores de IA com base nas chaves de API disponíveis."""

        # Inicializa Gemini
        if HAS_GEMINI:
            try:
                gemini_key = os.getenv('GEMINI_API_KEY')
                if gemini_key:
                    genai.configure(api_key=gemini_key)
                    self.providers['gemini']['client'] = genai.GenerativeModel("gemini-2.5-pro")
                    self.providers['gemini']['available'] = True
                    logger.info("✅ Gemini 2.5 Pro (gemini-2.5-pro) inicializado como MODELO PRIMÁRIO")
            except Exception as e:
                logger.warning(f"⚠️ Falha ao inicializar Gemini: {str(e)}")
        else:
            logger.warning("⚠️ Biblioteca 'google-generativeai' não instalada.")

        # Inicializa OpenAI
        if HAS_OPENAI:
            try:
                openai_key = os.getenv('OPENAI_API_KEY')
                if openai_key:
                    self.providers["openai"]["client"] = openai.OpenAI(api_key=openai_key)
                    self.providers["openai"]["available"] = True
                    logger.info("✅ OpenAI (gpt-3.5-turbo) inicializado com sucesso")
            except Exception as e:
                logger.info(f"ℹ️ OpenAI não disponível: {str(e)}")
        else:
            logger.info("ℹ️ Biblioteca 'openai' não instalada.")

        # Inicializa Groq
        try:
            if HAS_GROQ_CLIENT and groq_client and groq_client.is_enabled():
                self.providers['groq']['client'] = groq_client
                self.providers['groq']['available'] = True
                logger.info("✅ Groq (llama3-70b-8192) inicializado com sucesso")
            else:
                logger.info("ℹ️ Groq client não configurado")
        except Exception as e:
            logger.info(f"ℹ️ Groq não disponível: {str(e)}")

        # Inicializa HuggingFace
        try:
            hf_key = os.getenv('HUGGINGFACE_API_KEY')
            if hf_key:
                self.providers['huggingface']['client'] = {
                    'api_key': hf_key,
                    'base_url': 'https://api-inference.huggingface.co/models/'
                }
                self.providers['huggingface']['available'] = True
                logger.info("✅ HuggingFace inicializado com sucesso")
        except Exception as e:
            logger.info(f"ℹ️ HuggingFace não disponível: {str(e)}")

    def get_best_provider(self) -> Optional[str]:
        """Retorna o melhor provedor disponível com base na prioridade e contagem de erros."""
        current_time = time.time()

        # Primeiro, tenta reabilitar provedores que podem ter se recuperado
        for name, provider in self.providers.items():
            if (not provider['available'] and 
                provider.get('last_success') and 
                current_time - provider['last_success'] > 300):  # 5 minutos
                logger.info(f"🔄 Tentando reabilitar provedor {name} após cooldown")
                provider['error_count'] = 0
                provider['consecutive_failures'] = 0
                if name == 'gemini' and HAS_GEMINI:
                    provider['available'] = True
                elif name == 'groq' and HAS_GROQ_CLIENT:
                    provider['available'] = True
                elif name == 'openai' and HAS_OPENAI:
                    provider['available'] = True
                elif name == 'huggingface':
                    provider['available'] = True

        available_providers = [
            (name, provider) for name, provider in self.providers.items() 
            if provider['available'] and provider['consecutive_failures'] < provider.get('max_errors', 2)
        ]

        if not available_providers:
            logger.warning("🔄 Nenhum provedor saudável disponível. Resetando contadores.")
            for provider in self.providers.values():
                provider['error_count'] = 0
                provider['consecutive_failures'] = 0
            available_providers = [(name, p) for name, p in self.providers.items() if p['available']]

        if available_providers:
            # Ordena por prioridade e falhas consecutivas
            available_providers.sort(key=lambda x: (x[1]['priority'], x[1]['consecutive_failures']))
            return available_providers[0][0]

        return None

    def generate_analysis(self, prompt: str, max_tokens: int = 8192, provider: Optional[str] = None) -> Optional[str]:
        """Gera análise usando um provedor específico ou o melhor disponível com fallback."""

        start_time = time.time()

        # Se um provedor específico for solicitado
        if provider:
            if self.providers.get(provider) and self.providers[provider]['available']:
                logger.info(f"🤖 Usando provedor solicitado: {provider.upper()}")
                try:
                    result = self._call_provider(provider, prompt, max_tokens)
                    if result:
                        self._record_success(provider)
                        return result
                    else:
                        raise Exception("Resposta vazia")
                except Exception as e:
                    logger.error(f"❌ Provedor solicitado {provider.upper()} falhou: {e}")
                    self._record_failure(provider, str(e))
                    return None # Não tenta fallback se um provedor específico foi pedido e falhou
            else:
                logger.error(f"❌ Provedor solicitado '{provider}' não está disponível.")
                return None

        # Lógica de fallback padrão
        provider_name = self.get_best_provider()
        if not provider_name:
            raise Exception("❌ NENHUM PROVEDOR DE IA DISPONÍVEL: Configure pelo menos uma API de IA (Gemini, Groq, OpenAI ou HuggingFace)")

        try:
            result = self._call_provider(provider_name, prompt, max_tokens)
            if result:
                self._record_success(provider_name)
                return result
            else:
                raise Exception("Resposta vazia do provedor")
        except Exception as e:
            logger.error(f"❌ Erro no provedor {provider_name}: {e}")
            self._record_failure(provider_name, str(e))
            return self._try_fallback(prompt, max_tokens, exclude=[provider_name])

    def generate_parallel_analysis(self, prompts: List[Dict[str, Any]], max_tokens: int = 8192) -> Dict[str, Any]:
        """Gera múltiplas análises em paralelo usando diferentes provedores"""

        from concurrent.futures import ThreadPoolExecutor, as_completed

        results = {}

        with ThreadPoolExecutor(max_workers=len(prompts)) as executor:
            future_to_prompt = {}

            for prompt_data in prompts:
                prompt_id = prompt_data['id']
                prompt_text = prompt_data['prompt']
                preferred_provider = prompt_data.get('provider')

                future = executor.submit(
                    self.generate_analysis, 
                    prompt_text, 
                    max_tokens, 
                    preferred_provider
                )
                future_to_prompt[future] = prompt_id

            # Coleta resultados
            for future in as_completed(future_to_prompt, timeout=600):
                prompt_id = future_to_prompt[future]
                try:
                    result = future.result()
                    results[prompt_id] = {
                        'success': bool(result),
                        'content': result,
                        'error': None
                    }
                except Exception as e:
                    results[prompt_id] = {
                        'success': False,
                        'content': None,
                        'error': str(e)
                    }

        return results

    def _record_success(self, provider_name: str):
        """Registra sucesso do provedor"""
        if provider_name in self.providers:
            self.providers[provider_name]['consecutive_failures'] = 0
            self.providers[provider_name]['last_success'] = time.time()
            logger.info(f"✅ Sucesso registrado para {provider_name}")

    def _record_failure(self, provider_name: str, error_msg: str):
        """Registra falha do provedor"""
        if provider_name in self.providers:
            self.providers[provider_name]['error_count'] += 1
            self.providers[provider_name]['consecutive_failures'] += 1

            # Desabilita temporariamente se muitas falhas consecutivas
            if self.providers[provider_name]['consecutive_failures'] >= self.providers[provider_name]['max_errors']:
                logger.warning(f"⚠️ Desabilitando {provider_name} temporariamente após {self.providers[provider_name]['consecutive_failures']} falhas consecutivas")
                self.providers[provider_name]['available'] = False

            logger.error(f"❌ Falha registrada para {provider_name}: {error_msg}")

    def _call_provider(self, provider_name: str, prompt: str, max_tokens: int) -> Optional[str]:
        """Chama a função de geração do provedor especificado."""
        if provider_name == 'gemini':
            return self._generate_with_gemini(prompt, max_tokens)
        elif provider_name == 'groq':
            return self._generate_with_groq(prompt, max_tokens)
        elif provider_name == 'openai':
            return self._generate_with_openai(prompt, max_tokens)
        elif provider_name == 'huggingface':
            return self._generate_with_huggingface(prompt, max_tokens)
        return None

    def _generate_with_gemini(self, prompt: str, max_tokens: int) -> Optional[str]:
        """Gera conteúdo usando Gemini."""
        client = self.providers['gemini']['client']
        config = {
            "temperature": 0.8,  # Criatividade controlada
            "max_output_tokens": min(max_tokens, 8192),
            "top_p": 0.95,
            "top_k": 64
        }
        safety = [
            {"category": c, "threshold": "BLOCK_NONE"} 
            for c in ["HARM_CATEGORY_HARASSMENT", "HARM_CATEGORY_HATE_SPEECH", "HARM_CATEGORY_SEXUALLY_EXPLICIT", "HARM_CATEGORY_DANGEROUS_CONTENT"]
        ]
        response = client.generate_content(prompt, generation_config=config, safety_settings=safety)
        
        # CORREÇÃO CRÍTICA: Uso correto do response do Gemini
        try:
            # Primeiro tenta acesso direto
            if hasattr(response, 'text'):
                response_text = response.text
            # Se falhar, usa o accessor correto
            elif hasattr(response, 'parts') and response.parts:
                response_text = ''.join([part.text for part in response.parts if hasattr(part, 'text')])
            # Se ainda falhar, usa candidates
            elif response.candidates and len(response.candidates) > 0:
                candidate = response.candidates[0]
                if hasattr(candidate, 'content') and candidate.content.parts:
                    response_text = ''.join([part.text for part in candidate.content.parts if hasattr(part, 'text')])
                else:
                    raise Exception("Candidate sem conteúdo válido")
            else:
                raise Exception("Resposta sem conteúdo acessível")
            
            if response_text:
                logger.info(f"✅ Gemini 2.5 Pro gerou {len(response_text)} caracteres")
                return response_text
            else:
                raise Exception("Resposta vazia do Gemini 2.5 Pro")
                
        except Exception as e:
            logger.error(f"❌ Erro ao extrair texto do Gemini: {e}")
            # Fallback final
            if response.candidates and len(response.candidates) > 0:
                try:
                    candidate = response.candidates[0]
                    if hasattr(candidate, 'content') and candidate.content.parts:
                        text_parts = []
                        for part in candidate.content.parts:
                            if hasattr(part, 'text') and part.text:
                                text_parts.append(part.text)
                        if text_parts:
                            response_text = ''.join(text_parts)
                            logger.info(f"✅ Gemini 2.5 Pro (fallback) gerou {len(response_text)} caracteres")
                            return response_text
                except:
                    pass
            raise Exception(f"Falha ao extrair resposta do Gemini: {e}")

    def _generate_with_groq(self, prompt: str, max_tokens: int) -> Optional[str]:
        """Gera conteúdo usando Groq."""
        client = self.providers['groq']['client']
        content = client.generate(prompt, max_tokens=min(max_tokens, 8192))
        if content:
            logger.info(f"✅ Groq gerou {len(content)} caracteres")
            return content
        raise Exception("Resposta vazia do Groq")

    def _generate_with_openai(self, prompt: str, max_tokens: int) -> Optional[str]:
        """Gera conteúdo usando OpenAI."""
        client = self.providers['openai']['client']
        response = client.chat.completions.create(
            model=self.providers['openai']['model'],
            messages=[
                {"role": "system", "content": "Você é um especialista em análise de mercado ultra-detalhada."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=min(max_tokens, 4096),
            temperature=0.7
        )
        content = response.choices[0].message.content
        if content:
            logger.info(f"✅ OpenAI gerou {len(content)} caracteres")
            return content
        raise Exception("Resposta vazia do OpenAI")

    def _generate_with_huggingface(self, prompt: str, max_tokens: int) -> Optional[str]:
        """Gera conteúdo usando HuggingFace com rotação de modelos."""
        config = self.providers['huggingface']
        for _ in range(len(config['models'])):
            model_index = config['current_model_index']
            model = config['models'][model_index]
            config['current_model_index'] = (model_index + 1) % len(config['models']) # Rotaciona para a próxima vez

            try:
                url = f"{config['client']['base_url']}{model}"
                headers = {"Authorization": f"Bearer {config['client']['api_key']}"}
                payload = {"inputs": prompt, "parameters": {"max_new_tokens": min(max_tokens, 1024)}}
                response = requests.post(url, headers=headers, json=payload, timeout=60)

                if response.status_code == 200:
                    res_json = response.json()
                    content = res_json[0].get("generated_text", "")
                    if content:
                        logger.info(f"✅ HuggingFace ({model}) gerou {len(content)} caracteres")
                        return content
                elif response.status_code == 503:
                    logger.warning(f"⚠️ Modelo HuggingFace {model} está carregando (503), tentando próximo...")
                    continue
                else:
                    logger.warning(f"⚠️ Erro {response.status_code} no modelo {model}")
                    continue
            except Exception as e:
                logger.warning(f"⚠️ Erro no modelo {model}: {e}")
                continue
        raise Exception("Todos os modelos HuggingFace falharam")

    def reset_provider_errors(self, provider_name: str = None):
        """Reset contadores de erro dos provedores"""
        if provider_name:
            if provider_name in self.providers:
                self.providers[provider_name]['error_count'] = 0
                self.providers[provider_name]['consecutive_failures'] = 0
                self.providers[provider_name]['available'] = True
                logger.info(f"🔄 Reset erros do provedor: {provider_name}")
        else:
            for provider in self.providers.values():
                provider['error_count'] = 0
                provider['consecutive_failures'] = 0
                if provider.get('client'):  # Só reabilita se tem cliente configurado
                    provider['available'] = True
            logger.info("🔄 Reset erros de todos os provedores")

    def _try_fallback(self, prompt: str, max_tokens: int, exclude: List[str]) -> Optional[str]:
        """Tenta usar o próximo provedor disponível como fallback."""
        logger.info(f"🔄 Acionando fallback, excluindo: {', '.join(exclude)}")

        # Ordena provedores por prioridade, excluindo os que já falharam
        available_providers = [
            (name, provider) for name, provider in self.providers.items()
            if (provider['available'] and 
                name not in exclude and 
                provider['consecutive_failures'] < provider.get('max_errors', 2))
        ]

        if not available_providers:
            logger.critical("❌ Todos os provedores de fallback falharam.")
            return None

        # Ordena por prioridade
        available_providers.sort(key=lambda x: (x[1]['priority'], x[1]['consecutive_failures']))
        next_provider = available_providers[0][0]

        logger.info(f"🔄 Tentando fallback para: {next_provider.upper()}")

        try:
            result = self._call_provider(next_provider, prompt, max_tokens)
            if result:
                self._record_success(next_provider)
                return result
            else:
                raise Exception("Resposta vazia do fallback")
        except Exception as e:
            logger.error(f"❌ Fallback para {next_provider} também falhou: {e}")
            self._record_failure(next_provider, str(e))
            return self._try_fallback(prompt, max_tokens, exclude + [next_provider])

    def get_provider_status(self) -> Dict[str, Any]:
        """Retorna status detalhado dos provedores"""
        status = {}

        for name, provider in self.providers.items():
            status[name] = {
                'available': provider['available'],
                'priority': provider['priority'],
                'error_count': provider['error_count'],
                'consecutive_failures': provider['consecutive_failures'],
                'last_success': provider.get('last_success'),
                'max_errors': provider['max_errors'],
                'model': provider.get('model', 'N/A')
            }

        return status

    def generate_content(self, prompt: str, max_tokens: int = 1000, **kwargs) -> Optional[str]:
        """Método alias para compatibilidade"""
        provider = kwargs.get('provider')
        return self.generate_analysis(prompt, max_tokens, provider)

    def generate_response(self, prompt: str, max_tokens: int = 1000, **kwargs) -> Optional[str]:
        """Gera uma resposta de IA, utilizando o melhor provedor disponível com fallback."""
        return self.generate_analysis(prompt, max_tokens, **kwargs.get('provider'))

# Instância global
ai_manager = AIManager()