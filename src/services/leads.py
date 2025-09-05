#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Módulo de Processamento e Extração de Leads
Processa os resultados de uma busca massiva REAL do RealSearchOrchestrator
para extrair dados de leads (nomes, emails, perfis) e salvá-los localmente.
"""

import os
import logging
import asyncio
import time
import json
import csv
import re
from typing import Dict, List, Any, Optional, Set, Tuple
from datetime import datetime
from urllib.parse import urlparse
# Importa o orquestrador real
from services.real_search_orchestrator import real_search_orchestrator

# Configuração de logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# --- Funções de Extração de Leads ---

def extract_lead_data_from_item(item: Dict[str, Any], source_url: str) -> List[Dict[str, str]]:
    """
    Extrai dados de leads de um item de resultado de busca.
    Tenta extrair de snippet, título e conteúdo bruto.
    """
    leads = []
    combined_text = f"{item.get('title', '')} {item.get('snippet', '')} {item.get('content', '')}".strip()

    if not combined_text:
        return []

    # Padrão para emails
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    emails_found = list(set(re.findall(email_pattern, combined_text))) # Remove duplicatas

    # Padrão mais robusto para nomes próprios brasileiros/portugueses
    # Procura por "Nome Sobrenome" ou "Nome S. Sobrenome"
    # Este é um padrão simplificado, NLP seria mais preciso.
    name_pattern = r'\b[A-ZÀ-ÖØ-öø-ÿ][a-zà-öø-ÿ]+\s+[A-ZÀ-ÖØ-öø-ÿ][a-zà-öø-ÿ]+(?:\s+[A-ZÀ-ÖØ-öø-ÿ][a-zà-öø-ÿ]+)?\b'
    names_found = list(set(re.findall(name_pattern, combined_text))) # Remove duplicatas

    # Heurística: Se encontrou emails, associa a nomes próximos ou usa o título da página
    if emails_found:
        for email in emails_found:
            # Tenta encontrar um nome associado ao email
            # Procura nome dentro de uma janela de caracteres
            email_pos = combined_text.find(email)
            start = max(0, email_pos - 100)
            end = min(len(combined_text), email_pos + len(email) + 100)
            context_around_email = combined_text[start:end]
            
            nearby_names = re.findall(name_pattern, context_around_email)
            lead_name = nearby_names[0] if nearby_names else item.get('title', 'N/A').split(' - ')[0] # Parte antes do '-'

            leads.append({
                'source_url': source_url,
                'full_name': lead_name,
                'email': email,
                'extracted_from': 'email_context_or_title',
                'extracted_at': datetime.now().isoformat()
            })
    elif names_found:
        # Se só encontrou nomes, cria leads com nome e email 'N/A'
        for name in names_found[:3]: # Limita para evitar poluição
             leads.append({
                'source_url': source_url,
                'full_name': name,
                'email': 'N/A',
                'extracted_from': 'text_content',
                'extracted_at': datetime.now().isoformat()
            })

    if leads:
        logger.debug(f"  🎯 Encontrados {len(leads)} leads potenciais em {source_url}")
    return leads

# --- Funções de Salvamento Local ---

def save_leads_locally(leads: List[Dict[str, str]], session_id: str, query: str):
    """
    Salva os leads coletados em arquivos locais (JSON e CSV).
    Também salva um relatório da sessão de coleta de leads.
    """
    if not leads:
        logger.info("📭 Nenhum lead coletado para salvar.")
        return

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_query = re.sub(r'[^\w\s-]', '', query).strip().replace(' ', '_')[:50] # Sanitiza a query para nome de arquivo
    
    base_filename = f"leads_{safe_query}_{session_id}_{timestamp}"

    # 1. Salvar em JSON
    json_filename = f"{base_filename}.json"
    try:
        with open(json_filename, 'w', encoding='utf-8') as f:
            json.dump(leads, f, indent=4, ensure_ascii=False)
        logger.info(f"💾 {len(leads)} leads salvos em {json_filename}")
    except Exception as e:
        logger.error(f"❌ Erro ao salvar leads em JSON: {e}")

    # 2. Salvar em CSV
    csv_filename = f"{base_filename}.csv"
    if leads:
        fieldnames = leads[0].keys()
        try:
            with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(leads)
            logger.info(f"💾 {len(leads)} leads salvos em {csv_filename}")
        except Exception as e:
            logger.error(f"❌ Erro ao salvar leads em CSV: {e}")

    # 3. Salvar relatório da sessão de extração de leads
    report_filename = f"{base_filename}_lead_report.json"
    report_data = {
        'session_id': session_id,
        'original_query': query,
        'leads_extracted': len(leads),
        'unique_emails': len(set(lead['email'] for lead in leads if lead['email'] != 'N/A')),
        'unique_names': len(set(lead['full_name'] for lead in leads if lead['full_name'] != 'N/A')),
        'timestamp': datetime.now().isoformat()
    }
    try:
        with open(report_filename, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=4, ensure_ascii=False)
        logger.info(f"📈 Relatório da extração de leads salvo em {report_filename}")
    except Exception as e:
        logger.error(f"❌ Erro ao salvar relatório de leads: {e}")


# --- Função Principal de Processamento de Leads ---

async def process_leads_from_massive_search(
    query: str,
    context: Optional[Dict[str, Any]] = None,
    session_id: str = None,
    massive_data: Dict[str, Any] = None
) -> List[Dict[str, Any]]:
    """
    Etapa principal: Executa uma busca massiva REAL e processa os resultados para extrair leads.
    
    Esta função:
    1. Chama o RealSearchOrchestrator para fazer a busca massiva.
    2. Processa os resultados retornados.
    3. Extrai dados de leads (nomes, emails) de cada item.
    4. Salva os leads localmente.
    5. Retorna a lista de leads extraídos.
    
    :param query: A query de busca (ex: "designers gráficos em São Paulo")
    :param context: Dicionário com contexto adicional para o orquestrador (opcional)
    :return: Lista de dicionários representando os leads coletados
    """
    # 1. Usa dados massivos já coletados ou executa nova busca
    if massive_data and isinstance(massive_data, dict):
        search_data = massive_data
    else:
        search_data = await real_search_orchestrator.execute_massive_real_search(
            query=query,
            context=context or {},
            session_id=session_id or f"leads_{int(time.time())}"
        )

    if not search_data or not search_data.get('web_intelligence'):
        logger.error("❌ Falha na busca massiva ou nenhum resultado retornado.")
        return []

    web_intel = search_data['web_intelligence']
    
    # Coleta todos os resultados de diferentes fontes
    all_items = []
    all_items.extend(web_intel.get('primary_search', []))
    # Adiciona resultados de queries expandidas
    for expanded_query, results_dict in web_intel.get('expanded_queries', {}).items():
        all_items.extend(results_dict.get('results', []))
    # Adiciona conteúdo profundo
    all_items.extend(web_intel.get('deep_content', {}).get('extracted_data', []))
    # Adiciona resultados de redes sociais
    all_items.extend(web_intel.get('social_media_insights', {}).get('top_profiles', []))
    
    if not all_items:
         logger.warning("⚠️ Nenhum item encontrado para extração de leads.")
         return []

    logger.info(f"📊 Total de itens para processar: {len(all_items)}")

    # --- ETAPA 2: EXTRAÇÃO DE LEADS ---
    logger.info("📖 ETAPA 2: Extraindo dados de leads dos itens coletados...")
    
    all_extracted_leads = []
    for item in all_items:
        url = item.get('url', 'N/A')
        # Extrai leads de cada item
        leads_from_item = extract_lead_data_from_item(item, url)
        all_extracted_leads.extend(leads_from_item)

    if not all_extracted_leads:
        logger.warning("📭 Nenhum lead pôde ser extraído dos itens coletados.")
        # Mesmo assim, salva um relatório vazio para registrar a tentativa
        save_leads_locally([], session_id or f"leads_{int(time.time())}", query)
        return []

    # --- ETAPA 3: REMOÇÃO DE DUPLICATAS E FINALIZAÇÃO ---
    logger.info("🧹 ETAPA 3: Removendo duplicatas e finalizando...")
    
    # Remove duplicatas baseadas em email (prioriza o primeiro encontrado)
    seen_emails: Set[str] = set()
    unique_leads: List[Dict[str, str]] = []
    duplicates_removed = 0

    for lead in all_extracted_leads:
        email = lead.get('email', 'N/A')
        # Se o lead tem um email e ele já foi visto, é duplicado
        if email != 'N/A' and email in seen_emails:
            duplicates_removed += 1
            continue
        # Se o lead tem um email, marca como visto
        if email != 'N/A':
            seen_emails.add(email)
        # Adiciona lead (único por email, ou sem email)
        unique_leads.append(lead)

    logger.info(f"✅ Extração concluída. Leads únicos encontrados: {len(unique_leads)} (Duplicatas removidas: {duplicates_removed})")

    # --- ETAPA 4: SALVAMENTO LOCAL ---
    logger.info("💾 ETAPA 4: Salvando leads localmente...")
    save_leads_locally(unique_leads, session_id or f"leads_{int(time.time())}", query)
    
    # --- ETAPA 5: RELATÓRIO FINAL ---
    logger.info("📈 ETAPA 5: Gerando relatório final...")
    orchestrator_stats = real_search_orchestrator.get_session_statistics()
    lead_report_data = {
        'session_id': session_id or f"leads_{int(time.time())}",
        'original_query': query,
        'orchestrator_stats': orchestrator_stats,
        'leads_extracted': len(unique_leads),
        'unique_emails': len(set(lead['email'] for lead in unique_leads if lead['email'] != 'N/A')),
        'unique_names': len(set(lead['full_name'] for lead in unique_leads if lead['full_name'] != 'N/A')),
        'timestamp': datetime.now().isoformat()
    }
    
    final_report_filename = f"leads_{session_id or f'leads_{int(time.time())}'}_FINAL_REPORT.json"
    try:
        with open(final_report_filename, 'w', encoding='utf-8') as f:
            json.dump(lead_report_data, f, indent=4, ensure_ascii=False)
        logger.info(f"🏁 Relatório final completo salvo em {final_report_filename}")
    except Exception as e:
        logger.error(f"❌ Erro ao salvar relatório final: {e}")

    logger.info(f"🎉 Processo de coleta de leads concluído com sucesso!")
    return unique_leads


# --- Função para Execução Independente ---

async def main():
    """Função principal para demonstrar o uso."""
    
    # 1. Defina sua query de busca
    search_query = "freelancers designers gráficos em porto alegre"
    
    # 2. (Opcional) Defina um contexto para a busca
    search_context = {
        # 'segmento': 'design',
        # 'publico': 'freelancers',
        # 'problema': 'busca por trabalho'
        # O contexto é usado pelo RealSearchOrchestrator para expandir queries
    }
    
    # 3. Certifique-se de que suas chaves de API estão configuradas
    # como variáveis de ambiente (veja resposta anterior sobre quais são necessárias)
    # Ex: os.environ['SERPER_API_KEY'] = 'sua_chave'
    
    # 4. Execute o processo de coleta de leads
    leads = await process_leads_from_massive_search(
        query=search_query,
        context=search_context
    )
    
    # 5. (Opcional) Imprime um resumo no console
    if leads:
        print(f"\n--- Resumo da Coleta de Leads ---")
        print(f"Query: {search_query}")
        print(f"Leads Encontrados: {len(leads)}")
        # Mostra os 5 primeiros
        for lead in leads[:5]:
            print(f"  - Nome: {lead.get('full_name')}, Email: {lead.get('email')}, Fonte: {lead.get('source_url')}")
        print("---")
    else:
        print("Nenhum lead foi encontrado.")

# --- Objeto de Serviço para Compatibilidade ---

class LeadsService:
    """Classe de serviço para compatibilidade com imports existentes"""
    
    @staticmethod
    async def extract_comprehensive_leads(session_id: str) -> Dict[str, Any]:
        """Extrai leads de forma abrangente para uma sessão"""
        try:
            # Carrega dados da sessão
            session_dir = f"analyses_data/{session_id}"
            massive_data = None
            
            if os.path.exists(session_dir):
                for file in os.listdir(session_dir):
                    if "massive_search" in file and file.endswith('.json'):
                        with open(os.path.join(session_dir, file), 'r', encoding='utf-8') as f:
                            massive_data = json.load(f)
                        break
            
            # Processa leads
            leads_extracted = await process_leads_from_massive_search(
                query="comprehensive leads extraction",
                context={"session_id": session_id},
                session_id=session_id,
                massive_data=massive_data
            )
            
            return {
                "leads": leads_extracted,
                "session_id": session_id,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Erro na extração abrangente de leads: {e}")
            return {"leads": [], "error": str(e)}

# Instância global do serviço
leads_service = LeadsService()

if __name__ == "__main__":
    # Executa a função principal
    asyncio.run(main())