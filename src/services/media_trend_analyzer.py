import os
import logging
from typing import List, Dict, Any
from services.mcp_supadata_manager import MCPSupadataManager
from services.ai_manager import ai_manager # Para análise de tópicos e sumarização

logger = logging.getLogger(__name__)

class MediaTrendAnalyzer:
    def __init__(self):
        self.mcp_supadata_manager = MCPSupadataManager()
        self.analyzed_media_db = [] # Mock de um banco de dados para armazenar mídia analisada

    def analyze_video_trends(self, video_urls: List[str]) -> List[Dict[str, Any]]:
        """Analisa tendências de vídeo a partir de uma lista de URLs."""
        analyzed_results = []
        for url in video_urls:
            logger.info(f"Analisando vídeo: {url}")
            extracted_data = self.mcp_supadata_manager.extract_from_video(url)

            if "error" not in extracted_data:
                transcript = extracted_data.get("extracted_text", "")
                title = extracted_data.get("title", "Sem Título")
                
                # Simula análise de tópicos e palavras-chave com AI Manager
                topics_prompt = f"Analise a seguinte transcrição de vídeo e identifique os 3 principais tópicos e 5 palavras-chave relevantes: {transcript[:1000]}..."
                ai_analysis = ai_manager.generate_text(topics_prompt)
                
                # Mock de extração de tópicos e palavras-chave do resultado da IA
                topics = [f"Tópico {i+1}" for i in range(3)] # Placeholder
                keywords = [f"keyword{i+1}" for i in range(5)] # Placeholder

                analysis_result = {
                    "url": url,
                    "title": title,
                    "transcript_preview": transcript[:200] + "..." if len(transcript) > 200 else transcript,
                    "main_topics": topics,
                    "keywords": keywords,
                    "ai_analysis_summary": ai_analysis,
                    "timestamp": datetime.now().isoformat()
                }
                self.analyzed_media_db.append(analysis_result)
                analyzed_results.append(analysis_result)
            else:
                logger.warning(f"Falha ao extrair conteúdo de vídeo {url} com Supadata: {extracted_data["error"]}")
        
        logger.info(f"Total de vídeos analisados: {len(analyzed_results)}")
        return analyzed_results

    def get_analyzed_media_summary(self) -> Dict[str, Any]:
        """Retorna um resumo da mídia analisada."""
        total_analyzed = len(self.analyzed_media_db)
        all_topics = set()
        all_keywords = set()

        for media in self.analyzed_media_db:
            all_topics.update(media["main_topics"])
            all_keywords.update(media["keywords"])

        return {
            "total_analyzed_media": total_analyzed,
            "unique_topics": list(all_topics),
            "unique_keywords": list(all_keywords),
            "analyzed_media_list": self.analyzed_media_db
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

    # Mock AI Manager para teste
    class MockAIManager:
        def generate_text(self, prompt):
            logger.info(f"Mock AI Manager: Gerando texto para prompt: {prompt[:50]}...")
            return "Análise de IA mock: Tópicos principais são tecnologia e mercado. Palavras-chave: inovação, futuro, dados."

    import services.ai_manager
    services.ai_manager.ai_manager = MockAIManager()

    analyzer = MediaTrendAnalyzer()

    print("Iniciando análise de tendências de vídeo...")
    video_urls_to_analyze = [
        "https://www.youtube.com/watch?v=dQw4w9WgXcQ", # Exemplo, substitua por um vídeo real
        "https://www.youtube.com/watch?v=another_video_id" # Outro exemplo
    ]
    results = analyzer.analyze_video_trends(video_urls_to_analyze)
    print("Resultados da análise de vídeo:")
    for r in results:
        print(f"- URL: {r["url"]}, Tópicos: {r["main_topics"]}, Palavras-chave: {r["keywords"]}")

    summary = analyzer.get_analyzed_media_summary()
    print("\nResumo da mídia analisada:")
    print(summary)


