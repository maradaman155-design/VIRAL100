#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ARQV30 Enhanced v2.0 - DeepSeek Client
Cliente para integração com DeepSeek API para análise complementar
"""

import os
import logging
import requests
import json
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

class DeepSeekClient:
    """Cliente para integração com DeepSeek API"""
    
    def __init__(self):
        """Inicializa cliente DeepSeek"""
        self.api_key = os.getenv("DEEPSEEK_API_KEY")
        self.base_url = "https://api.deepseek.com/v1"
        self.model = "deepseek-chat"
        
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        self.available = bool(self.api_key)
        
        if self.available:
            logger.info("DeepSeek client inicializado com sucesso")
        else:
            logger.warning("DeepSeek API key não encontrada")
    
    def is_available(self) -> bool:
        """Verifica se o cliente está disponível"""
        return self.available
    
    def generate_text(
        self, 
        prompt: str, 
        max_tokens: int = 1000,
        temperature: float = 0.7,
        timeout: int = 60
    ) -> Optional[str]:
        """Gera texto usando DeepSeek"""
        
        if not self.available:
            logger.warning("DeepSeek não está disponível")
            return None
        
        try:
            payload = {
                "model": self.model,
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "max_tokens": max_tokens,
                "temperature": temperature,
                "stream": False
            }
            
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=self.headers,
                json=payload,
                timeout=timeout
            )
            
            if response.status_code == 200:
                data = response.json()
                content = data["choices"][0]["message"]["content"]
                logger.info(f"DeepSeek gerou {len(content)} caracteres")
                return content
            else:
                logger.error(f"Erro DeepSeek: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Erro na requisição DeepSeek: {str(e)}", exc_info=True)
            return None
    
    def analyze_market_strategy(self, context: Dict[str, Any]) -> Optional[str]:
        """Análise estratégica específica de mercado"""
        
        prompt = f"""
        Como especialista em estratégia de mercado, analise o seguinte contexto e forneça 5 insights estratégicos únicos:
        
        Segmento: {context.get('segmento', 'Não especificado')}
        Produto: {context.get('produto', 'Não especificado')}
        Público: {context.get('publico', 'Não especificado')}
        Preço: {context.get('preco', 'Não especificado')}
        
        Foque em:
        1. Oportunidades ocultas no mercado
        2. Riscos não percebidos pela maioria
        3. Estratégias de diferenciação inovadoras
        4. Tendências emergentes relevantes
        5. Recomendações táticas específicas
        
        Seja específico e evite generalidades. Cada insight deve ser acionável.
        """
        
        return self.generate_text(prompt, max_tokens=1500, temperature=0.8)

# Instância global (opcional)
try:
    deepseek_client = DeepSeekClient()
except Exception as e:
    logger.error(f"Erro ao inicializar DeepSeek client: {str(e)}")
    deepseek_client = None

