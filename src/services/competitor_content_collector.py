import os
import logging
import requests
from typing import List, Dict, Any
from services.mcp_supadata_manager import MCPSupadataManager
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

class CompetitorContentCollector:
    def __init__(self):
        self.mcp_supadata_manager = MCPSupadataManager()
        # Mock de um banco de dados para armazenar configurações de concorrentes e conteúdo
        self.competitors_config = {}
        self.competitor_content_db = []

    def add_competitor(self, name: str, base_urls: List[str]):
        """Adiciona ou atualiza a configuração de um concorrente."""
        self.competitors_config[name] = {"base_urls": base_urls, "last_crawled": None}
        logger.info(f"Concorrente {name} adicionado/atualizado com URLs: {base_urls}")

    def _crawl_for_new_urls(self, base_url: str) -> List[str]:
        """Simula o rastreamento de uma URL base para encontrar novas URLs de conteúdo."""
        # Em um cenário real, isso seria um crawler mais sofisticado.
        # Por simplicidade, vamos mockar algumas URLs.
        logger.info(f"Simulando rastreamento para novas URLs em: {base_url}")
        if "example.com" in base_url:
            return [
                f"{base_url}/blog/novo-post-1",
                f"{base_url}/produtos/lancamento-x",
                f"{base_url}/noticias/ultimas-novidades"
            ]
        return []

    def collect_and_analyze_content(self, competitor_name: str) -> List[Dict[str, Any]]:
        """Coleta e analisa o conteúdo de um concorrente específico."""
        config = self.competitors_config.get(competitor_name)
        if not config:
            logger.warning(f"Concorrente {competitor_name} não configurado.")
            return []

        new_content_items = []
        for base_url in config["base_urls"]:
            new_urls = self._crawl_for_new_urls(base_url)
            for url in new_urls:
                logger.info(f"Extraindo conteúdo de concorrente: {url}")
                extracted_data = self.mcp_supadata_manager.extract_from_url(url)
                
                if "error" not in extracted_data:
                    content = extracted_data.get("extracted_text", "")
                    title = extracted_data.get("title", "Sem Título")
                    
                    # Simula análise de palavras-chave e tópicos
                    keywords = [word for word in content.lower().split() if len(word) > 5 and content.lower().count(word) > 2][:5]

                    content_item = {
                        "competitor": competitor_name,
                        "url": url,
                        "title": title,
                        "content_preview": content[:200] + "..." if len(content) > 200 else content,
                        "keywords": keywords,
                        "timestamp": datetime.now().isoformat()
                    }
                    self.competitor_content_db.append(content_item)
                    new_content_items.append(content_item)
                else:
                    logger.warning(f"Falha ao extrair conteúdo de {url} com Supadata: {extracted_data["error"]}")
        
        config["last_crawled"] = datetime.now().isoformat()
        logger.info(f"Coleta e análise para {competitor_name} concluída. Novos itens: {len(new_content_items)}")
        return new_content_items

    def get_competitor_content_summary(self, competitor_name: str = None) -> Dict[str, Any]:
        """Retorna um resumo do conteúdo coletado para um concorrente ou todos."""
        filtered_content = self.competitor_content_db
        if competitor_name:
            filtered_content = [c for c in self.competitor_content_db if c["competitor"] == competitor_name]

        total_items = len(filtered_content)
        unique_keywords = set()
        for item in filtered_content:
            unique_keywords.update(item["keywords"])

        return {
            "total_content_items": total_items,
            "unique_keywords": list(unique_keywords),
            "content_list": filtered_content
        }

# Exemplo de uso (apenas para demonstração)
if __name__ == "__main__":
    from dotenv import load_dotenv
    from datetime import datetime
    load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '..', '.env.example'))

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler()
        ]
    )

    collector = CompetitorContentCollector()

    print("Adicionando concorrente...")
    collector.add_competitor("Concorrente A", ["https://www.example.com/concorrenteA"])
    collector.add_competitor("Concorrente B", ["https://www.example.com/concorrenteB"])

    print("Coletando e analisando conteúdo para Concorrente A...")
    new_content_a = collector.collect_and_analyze_content("Concorrente A")
    print(f"Novos itens para Concorrente A: {len(new_content_a)}")

    print("Coletando e analisando conteúdo para Concorrente B...")
    new_content_b = collector.collect_and_analyze_content("Concorrente B")
    print(f"Novos itens para Concorrente B: {len(new_content_b)}")

    summary_all = collector.get_competitor_content_summary()
    print("\nResumo de todo o conteúdo de concorrentes:")
    print(summary_all)

    summary_a = collector.get_competitor_content_summary("Concorrente A")
    print("\nResumo do conteúdo para Concorrente A:")
    print(summary_a)


