#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Cliente para interagir com a API da Groq, servindo como um provedor de IA de alta velocidade.
"""

import os
import logging
import time
from typing import Optional

try:
    from groq import Groq
    HAS_GROQ = True
except ImportError:
    HAS_GROQ = False

logger = logging.getLogger(__name__)

class GroqClient:
    """Cliente para gerar texto usando a API da Groq."""

    def __init__(self):
        """Inicializa o cliente Groq."""
        self.api_key = os.getenv('GROQ_API_KEY')
        self.client = None
        self.available = False
        
        if not self.api_key:
            logger.info("ℹ️ GROQ_API_KEY não configurada - Groq desabilitado")
            return
        
        if not HAS_GROQ:
            logger.warning("⚠️ Biblioteca 'groq' não instalada. Execute: pip install groq")
            return
        
        if not self.api_key:
            logger.info("ℹ️ GROQ_API_KEY não configurada - Groq desabilitado")
            return
        
        if not HAS_GROQ:
            logger.warning("⚠️ Biblioteca 'groq' não instalada. Execute: pip install groq")
            return
        
        try:
            self.client = Groq(api_key=self.api_key)
            self.available = True
            logger.info("✅ Cliente Groq (llama3-70b-8192) inicializado com sucesso.")
        except Exception as e:
            logger.error(f"❌ Falha ao inicializar o cliente Groq: {e}")
            self.available = False

            try:
                self.client = Groq(api_key=self.api_key)
                self.available = True
                logger.info("✅ Cliente Groq (llama3-70b-8192) inicializado com sucesso.")
            except Exception as e:
                logger.error(f"❌ Falha ao inicializar o cliente Groq: {e}", exc_info=True)

    def is_enabled(self) -> bool:
        """Verifica se o cliente está configurado e pronto para uso."""
        return self.available and self.client is not None

    def generate(self, prompt: str, max_tokens: int = 8192) -> Optional[str]:
        """
        Gera texto usando um modelo da Groq.

        Args:
            prompt (str): O prompt para a geração de texto.
            max_tokens (int): O número máximo de tokens a serem gerados.

        Returns:
            Optional[str]: O texto gerado ou None em caso de falha.
        """
        if not self.is_enabled():
            raise Exception("Cliente Groq não está habilitado ou configurado corretamente.")

        try:
            start_time = time.time()
            # Usando o modelo Llama3 70b, conhecido por sua performance e velocidade na Groq
            chat_completion = self.client.chat.completions.create(
                messages=[
                    {
                        "role": "user",
                        "content": prompt,
                    }
                ],
                model="llama3-70b-8192",
                max_tokens=max_tokens,
                temperature=0.4, # Temperatura um pouco mais baixa para consistência
            )
            response_text = chat_completion.choices[0].message.content
            processing_time = time.time() - start_time
            logger.info(f"✅ Groq gerou {len(response_text)} caracteres em {processing_time:.2f}s")
            return response_text
        except Exception as e:
            logger.error(f"❌ Erro na chamada da API Groq: {e}", exc_info=True)
            raise

# Instância singleton
groq_client = GroqClient()
