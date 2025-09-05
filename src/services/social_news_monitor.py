import os
import logging
import requests
from typing import List, Dict, Any
from datetime import datetime, timedelta
from services.mcp_supadata_manager import MCPSupadataManager
from services.production_search_manager import production_search_manager
from services.ai_manager import ai_manager # Para análise de sentimento ou sumarização

logger = logging.getLogger(__name__)

class SocialNewsMonitor:
    def __init__(self):
        self.mcp_supadata_manager = MCPSupadataManager()
        # Mock de um banco de dados para armazenar menções
        self.mentions_db = [] # Em um ambiente real, seria um banco de dados como Supabase

    def _perform_sentiment_analysis(self, text: str) -> Dict[str, Any]:
        """Realiza análise de sentimento em um texto usando AI Manager (mock)."""
        # Em um cenário real, você chamaria um modelo de ML ou API de sentimento aqui.
        # Por simplicidade, este é um mock.
        if "ótimo" in text.lower() or "excelente" in text.lower() or "sucesso" in text.lower():
            return {"sentiment": "positive", "score": 0.9}
        elif "ruim" in text.lower() or "problema" in text.lower() or "falha" in text.lower():
            return {"sentiment": "negative", "score": 0.8}
        else:
            return {"sentiment": "neutral", "score": 0.5}

    def monitor_keywords(self, keywords: List[str], search_sources: List[str] = None, time_range_days: int = 1) -> List[Dict[str, Any]]:
        """Monitora palavras-chave em fontes de notícias e mídias sociais (simulado)."""
        if not search_sources: # Default para simulação
            search_sources = ["web", "news"]

        all_mentions = []
        for keyword in keywords:
            logger.info(f"Monitorando palavra-chave: {keyword}")
            
            # Simula busca por notícias/web usando production_search_manager
            query = f'"{keyword}"'
            search_results = production_search_manager.perform_search(query)

            for result_type in ["web_results", "news_results"]:
                for item in search_results.get(result_type, [])[:5]: # Limita para simulação
                    url = item.get("url")
                    title = item.get("title")
                    
                    if url and title:
                        logger.info(f"Extraindo conteúdo de: {url}")
                        extracted_data = self.mcp_supadata_manager.extract_from_url(url)
                        
                        if "error" not in extracted_data:
                            content = extracted_data.get("extracted_text", "")
                            sentiment_analysis = self._perform_sentiment_analysis(content)
                            
                            mention = {
                                "keyword": keyword,
                                "title": title,
                                "url": url,
                                "source_type": result_type.replace("_results", ""),
                                "content_preview": content[:200] + "..." if len(content) > 200 else content,
                                "sentiment": sentiment_analysis.get("sentiment"),
                                "sentiment_score": sentiment_analysis.get("score"),
                                "timestamp": datetime.now().isoformat()
                            }
                            self.mentions_db.append(mention)
                            all_mentions.append(mention)
                        else:
                            logger.warning(f"Falha ao extrair conteúdo de {url} com Supadata: {extracted_data["error"]}")
        
        logger.info(f"Total de menções encontradas e processadas: {len(all_mentions)}")
        return all_mentions

    def get_mentions_summary(self, keywords: List[str] = None) -> Dict[str, Any]:
        """Retorna um resumo das menções coletadas."""
        filtered_mentions = self.mentions_db
        if keywords:
            filtered_mentions = [m for m in self.mentions_db if m["keyword"] in keywords]

        total_mentions = len(filtered_mentions)
        positive_mentions = len([m for m in filtered_mentions if m["sentiment"] == "positive"])
        negative_mentions = len([m for m in filtered_mentions if m["sentiment"] == "negative"])
        neutral_mentions = len([m for m in filtered_mentions if m["sentiment"] == "neutral"])

        return {
            "total_mentions": total_mentions,
            "positive_mentions": positive_mentions,
            "negative_mentions": negative_mentions,
            "neutral_mentions": neutral_mentions,
            "mentions_list": filtered_mentions
        }

# Exemplo de uso (apenas para demonstração)
if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '..', '.env.example'))

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler()
        ]
    )

    # Mock Production Search Manager e AI Manager para teste
    class MockProductionSearchManager:
        def perform_search(self, query):
            logger.info(f"Mock Search Manager: Realizando busca para query: {query}")
            if "produto X" in query:
                return {"web_results": [
                    {"url": "https://example.com/noticia_produto_x_sucesso", "title": "Produto X é um sucesso!"},
                    {"url": "https://example.com/blog_produto_x_problema", "title": "Problemas com o Produto X"}
                ]}
            elif "empresa Y" in query:
                return {"web_results": [
                    {"url": "https://example.com/noticia_empresa_y_otima", "title": "Empresa Y com resultados ótimos"}
                ]}
            return {"web_results": []}

    class MockAIManager:
        def generate_text(self, prompt):
            return ""

    import services.production_search_manager
    import services.ai_manager
    services.production_search_manager.production_search_manager = MockProductionSearchManager()
    services.ai_manager.ai_manager = MockAIManager()

    monitor = SocialNewsMonitor()

    print("Iniciando monitoramento de palavras-chave...")
    mentions = monitor.monitor_keywords(["produto X", "empresa Y"])
    print("Menções coletadas:")
    for m in mentions:
        print(f"- Keyword: {m["keyword"]}, Sentimento: {m["sentiment"]}, URL: {m["url"]}")

    summary = monitor.get_mentions_summary()
    print("\nResumo das menções:")
    print(summary)


