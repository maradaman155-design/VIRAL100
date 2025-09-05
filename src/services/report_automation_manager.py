import os
import logging
from typing import Dict, Any, List
from services.mcp_sequential_thinking_manager import MCPSequentialThinkingManager
from services.mcp_supadata_manager import MCPSupadataManager
from services.ai_manager import ai_manager # Assumindo que ai_manager existe para análise
from services.production_search_manager import production_search_manager # Assumindo que production_search_manager existe para buscas

logger = logging.getLogger(__name__)

class ReportAutomationManager:
    def __init__(self):
        self.mcp_st_manager = MCPSequentialThinkingManager()
        self.mcp_supadata_manager = MCPSupadataManager()

    def generate_report(self, report_params: Dict[str, Any]) -> Dict[str, Any]:
        """Orquestra a geração de um relatório personalizado usando MCP-SequentialThinking-Tools."""
        problem_description = f"Gerar um relatório de mercado personalizado com os seguintes parâmetros: {report_params}"
        
        try:
            # 1. Iniciar processo de pensamento sequencial para o relatório
            st_process = self.mcp_st_manager.start_thinking_process(
                problem_description=problem_description,
                initial_context={"report_params": report_params}
            )
            if "error" in st_process: # Verifica se a chave 'error' existe no dicionário
                logger.error(f"Erro ao iniciar processo ST: {st_process['error']}")
                return {"status": "error", "message": f"Erro ao iniciar processo ST: {st_process['error']}"}
            
            process_id = st_process.get("process_id")
            if not process_id:
                logger.error("ID do processo ST não retornado.")
                return {"status": "error", "message": "ID do processo ST não retornado."}

            report_data = {"sections": []}
            current_step_output = st_process.get("next_step_output", {})

            # Loop para avançar nos passos do MCP-SequentialThinking-Tools
            while current_step_output.get("status") == "in_progress":
                step_type = current_step_output.get("step_type")
                step_instruction = current_step_output.get("instruction")
                
                logger.info(f"Processo ST {process_id}: Executando passo '{step_type}' - {step_instruction}")

                step_result = {}
                if step_type == "collect_data":
                    # Exemplo: Coleta de dados via Supadata ou Search Manager
                    query = current_step_output.get("query", report_params.get("main_topic", "mercado"))
                    source_urls = current_step_output.get("source_urls", [])
                    
                    collected_content = []
                    if source_urls:
                        for url in source_urls:
                            supadata_result = self.mcp_supadata_manager.extract_from_url(url)
                            if "error" not in supadata_result:
                                collected_content.append(supadata_result.get("extracted_text", ""))
                            else:
                                logger.warning(f"Falha ao extrair URL {url} com Supadata: {supadata_result['error']}")
                    
                    # Exemplo de busca adicional se necessário
                    if not collected_content and query:
                        search_results = production_search_manager.perform_search(query)
                        for res in search_results.get("web_results", [])[:3]: # Limita a 3 resultados para exemplo
                            supadata_result = self.mcp_supadata_manager.extract_from_url(res["url"])
                            if "error" not in supadata_result:
                                collected_content.append(supadata_result.get("extracted_text", ""))
                            else:
                                logger.warning(f"Falha ao extrair URL {res['url']} com Supadata: {supadata_result['error']}")

                    step_result = {"collected_data": collected_content}
                    report_data["sections"].append({"title": "Dados Coletados", "content": collected_content})

                elif step_type == "analyze_data":
                    # Exemplo: Análise de dados usando AI Manager
                    data_to_analyze = current_step_output.get("data", report_data["sections"][-1].get("content", ""))
                    analysis_prompt = current_step_output.get("analysis_prompt", "Analise os dados fornecidos e extraia os principais insights.")
                    
                    if data_to_analyze:
                        ai_analysis = ai_manager.generate_text(analysis_prompt + "\n\nDados: " + "\n".join(data_to_analyze))
                        step_result = {"analysis_results": ai_analysis}
                        report_data["sections"].append({"title": "Análise de Dados", "content": ai_analysis})

                elif step_type == "generate_content":
                    # Exemplo: Geração de conteúdo textual para o relatório
                    content_prompt = current_step_output.get("prompt", "Gere um resumo executivo para o relatório.")
                    generated_text = ai_manager.generate_text(content_prompt)
                    step_result = {"generated_content": generated_text}
                    report_data["sections"].append({"title": "Conteúdo Gerado", "content": generated_text})

                elif step_type == "format_report":
                    # Exemplo: Formatação final do relatório (pode ser um placeholder para PDF/DOCX)
                    final_report_content = current_step_output.get("content", report_data)
                    # Aqui você chamaria a lógica de geração de PDF/DOCX
                    step_result = {"final_report_preview": "Relatório formatado pronto para exportação."}
                    report_data["final_report_status"] = "ready"

                # Avançar o processo no MCP-SequentialThinking-Tools com o resultado do passo
                current_step_output = self.mcp_st_manager.advance_thinking_step(process_id, user_input=step_result)
                if "error" in current_step_output: # Verifica se a chave 'error' existe no dicionário
                    logger.error(f"Erro ao avançar processo ST: {current_step_output['error']}")
                    return {"status": "error", "message": f"Erro ao avançar processo ST: {current_step_output['error']}"}

            if current_step_output.get("status") == "completed":
                logger.info(f"Processo ST {process_id} concluído com sucesso.")
                return {"status": "success", "report_data": report_data, "final_mcp_output": current_step_output}
            else:
                logger.error(f"Processo ST {process_id} terminou com status inesperado: {current_step_output.get('status')}")
                return {"status": "error", "message": "Processo de geração de relatório não concluído com sucesso.", "final_mcp_output": current_step_output}

        except Exception as e:
            logger.error(f"Erro geral na geração do relatório: {e}", exc_info=True)
            return {"status": "error", "message": f"Erro interno: {str(e)}"}

# Exemplo de uso (apenas para demonstração)
if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '..', '.env.example'))

    # Configurar logging para ver a saída
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler()
        ]
    )

    # Mock AI Manager e Production Search Manager para teste
    class MockAIManager:
        def generate_text(self, prompt):
            logger.info(f"Mock AI Manager: Gerando texto para prompt: {prompt[:50]}...")
            return "Conteúdo de análise gerado por IA mock." if "analise" in prompt.lower() else "Resumo executivo mock."

    class MockProductionSearchManager:
        def perform_search(self, query):
            logger.info(f"Mock Search Manager: Realizando busca para query: {query}")
            return {"web_results": [
                {"url": "https://example.com/noticia1", "title": "Noticia 1"},
                {"url": "https://example.com/noticia2", "title": "Noticia 2"}
            ]}

    # Substituir os managers reais pelos mocks para teste
    import services.ai_manager
    import services.production_search_manager
    services.ai_manager.ai_manager = MockAIManager()
    services.production_search_manager.production_search_manager = MockProductionSearchManager()

    manager = ReportAutomationManager()

    report_parameters = {
        "report_type": "analise_concorrencia",
        "main_topic": "mercado de IA",
        "competitors": ["Empresa A", "Empresa B"],
        "period": "ultimo_trimestre",
        "source_urls": ["https://www.smithery.ai/", "https://www.google.com/"]
    }

    print("Iniciando geração de relatório...")
    result = manager.generate_report(report_parameters)
    print("Resultado da geração do relatório:")
    print(result)


