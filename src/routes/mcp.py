from flask import Blueprint, request, jsonify
import logging
from services.mcp_sequential_thinking_manager import MCPSequentialThinkingManager
from services.mcp_supadata_manager import MCPSupadataManager

mcp_bp = Blueprint("mcp", __name__)
logger = logging.getLogger(__name__)

# Inicializa os managers (pode ser feito uma vez na inicialização da aplicação)
try:
    sequential_thinking_manager = MCPSequentialThinkingManager()
    supadata_manager = MCPSupadataManager()
except ValueError as e:
    logger.error(f"Erro ao inicializar managers MCP: {e}")
    sequential_thinking_manager = None
    supadata_manager = None

@mcp_bp.route("/mcp/sequential_thinking/start", methods=["POST"])
def start_sequential_thinking():
    if not sequential_thinking_manager:
        return jsonify({"error": "Serviço MCP Sequential Thinking não configurado."}), 500
    data = request.json
    problem_description = data.get("problem_description")
    initial_context = data.get("initial_context")

    if not problem_description:
        return jsonify({"error": "problem_description é obrigatório."}), 400

    result = sequential_thinking_manager.start_thinking_process(problem_description, initial_context)
    return jsonify(result)

@mcp_bp.route("/mcp/sequential_thinking/advance", methods=["POST"])
def advance_sequential_thinking():
    if not sequential_thinking_manager:
        return jsonify({"error": "Serviço MCP Sequential Thinking não configurado."}), 500
    data = request.json
    process_id = data.get("process_id")
    user_input = data.get("user_input")

    if not process_id:
        return jsonify({"error": "process_id é obrigatório."}), 400

    result = sequential_thinking_manager.advance_thinking_step(process_id, user_input)
    return jsonify(result)

@mcp_bp.route("/mcp/sequential_thinking/status", methods=["POST"])
def get_sequential_thinking_status():
    if not sequential_thinking_manager:
        return jsonify({"error": "Serviço MCP Sequential Thinking não configurado."}), 500
    data = request.json
    process_id = data.get("process_id")

    if not process_id:
        return jsonify({"error": "process_id é obrigatório."}), 400

    result = sequential_thinking_manager.get_process_status(process_id)
    return jsonify(result)

@mcp_bp.route("/mcp/supadata/extract_url", methods=["POST"])
def supadata_extract_url():
    if not supadata_manager:
        return jsonify({"error": "Serviço MCP Supadata não configurado."}), 500
    data = request.json
    url = data.get("url")

    if not url:
        return jsonify({"error": "url é obrigatório."}), 400

    result = supadata_manager.extract_from_url(url)
    return jsonify(result)

@mcp_bp.route("/mcp/supadata/extract_video", methods=["POST"])
def supadata_extract_video():
    if not supadata_manager:
        return jsonify({"error": "Serviço MCP Supadata não configurado."}), 500
    data = request.json
    video_url = data.get("video_url")

    if not video_url:
        return jsonify({"error": "video_url é obrigatório."}), 400

    result = supadata_manager.extract_from_video(video_url)
    return jsonify(result)


