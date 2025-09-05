#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ARQV30 Enhanced v2.0 - Auto Save Manager
Sistema de salvamento automático e imediato de todos os resultados
"""

import os
import json
import time
import logging
import random
import string
import re
from datetime import datetime
from typing import Dict, Any, Optional, List
import uuid
from pathlib import Path
import shutil
from datetime import timedelta
import gzip
import traceback

logger = logging.getLogger(__name__)

class AutoSaveManager:
    """Gerenciador de salvamento automático ultra-robusto"""

    def __init__(self):
        """Inicializa o gerenciador de salvamento"""
        self.base_dir = Path("relatorios_intermediarios")
        self.base_dir.mkdir(exist_ok=True)

        # Subdiretórios para organização
        self.subdirs = {
            'pesquisa_web': self.base_dir / 'pesquisa_web',
            'drivers_mentais': self.base_dir / 'drivers_mentais',
            'provas_visuais': self.base_dir / 'provas_visuais',
            'anti_objecao': self.base_dir / 'anti_objecao',
            'pre_pitch': self.base_dir / 'pre_pitch',
            'avatar': self.base_dir / 'avatar',
            'analise_completa': self.base_dir / 'analise_completa',
            'erros': self.base_dir / 'erros',
            'logs': self.base_dir / 'logs'
        }

        # Cria todos os subdiretórios
        for subdir in self.subdirs.values():
            subdir.mkdir(exist_ok=True)

        self.session_id = None
        self.analysis_id = None
        self.current_session_id = None # Adicionado para uso interno

        logger.info(f"✅ Auto Save Manager inicializado: {self.base_dir}")

    def _list_session_files(self, session_id: str) -> List[str]:
        """Lista arquivos de uma sessão específica"""
        files = []
        try:
            # Procura em todos os diretórios
            for subdir in ['logs', 'analise_completa', 'pesquisa_web', 'erros']:
                session_dir = os.path.join(self.base_dir, subdir, session_id)
                if os.path.exists(session_dir):
                    for file in os.listdir(session_dir):
                        if file.endswith('.txt'):
                            files.append(os.path.join(session_dir, file))
        except Exception as e:
            logger.error(f"❌ Erro ao listar arquivos da sessão {session_id}: {e}")
        
        return files

    def _clean_segment_name(self, segmento: str) -> str:
        """Limpa nome do segmento para usar como nome de pasta"""
        # Remove caracteres especiais e substitui espaços por underscores
        clean_name = re.sub(r'[^\w\s-]', '', segmento.strip())
        clean_name = re.sub(r'[-\s]+', '_', clean_name)
        return clean_name.lower()

    def iniciar_sessao(self, session_id: Optional[str] = None, segmento: str = None) -> str:
        """Inicia uma nova sessão de salvamento com pasta por segmento"""

        if not session_id:
            timestamp = int(time.time() * 1000)
            random_id = ''.join(random.choices(string.ascii_lowercase + string.digits, k=9))
            session_id = f"session_{timestamp}_{random_id}"

        self.current_session_id = session_id
        self.session_id = session_id # Define session_id para ser consistente com o resto do código
        self.analysis_id = f"analysis_{int(time.time())}_{uuid.uuid4().hex[:8]}" # Mantido para compatibilidade

        # Cria pasta específica por segmento se fornecido
        if segmento:
            segmento_clean = self._clean_segment_name(segmento)
            segmento_path = os.path.join(str(self.base_dir), "por_segmento", segmento_clean)
            os.makedirs(segmento_path, exist_ok=True)

            # Cria link simbólico da sessão na pasta do segmento
            session_path = os.path.join(str(self.base_dir), session_id)
            segmento_session_path = os.path.join(segmento_path, session_id)

            try:
                if not os.path.exists(segmento_session_path):
                    os.symlink(session_path, segmento_session_path)
            except OSError as e:
                logger.warning(f"Could not create symlink for session {session_id} in segment {segmento_clean}: {e}. Falling back to copy.")
                # Fallback: copia em vez de link simbólico se symlink falhar
                try:
                    shutil.copytree(session_path, segmento_session_path)
                except Exception as copy_e:
                    logger.error(f"Failed to copy session {session_id} to {segmento_session_path}: {copy_e}")

        # Salva metadados da sessão
        self.salvar_etapa("session_metadata", {
            "session_id": session_id,
            "segmento": segmento,
            "segmento_path": segmento_clean if segmento else None,
            "started_at": time.time(),
            "started_at_formatted": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "version": "ARQV30 Enhanced v2.0"
        }, categoria="logs") # Salva em logs para metadados da sessão

        logger.info(f"🚀 Sessão iniciada: {session_id}" + (f" (Segmento: {segmento})" if segmento else ""))
        return session_id

    def salvar_etapa(
        self,
        nome_etapa: str,
        dados: Any,
        status: str = "sucesso",
        timestamp: Optional[float] = None,
        categoria: str = "geral"
    ) -> str:
        """Salva etapa imediatamente com timestamp único"""

        timestamp = timestamp or time.time()
        timestamp_str = datetime.fromtimestamp(timestamp).strftime("%Y%m%d_%H%M%S_%f")[:-3]

        # Determina diretório baseado na categoria
        if categoria in self.subdirs:
            save_dir = self.subdirs[categoria]
        else:
            save_dir = self.base_dir

        # Se há sessão ativa, cria subdiretório
        if self.current_session_id: # Usando current_session_id para consistência
            save_dir = save_dir / self.current_session_id
            save_dir.mkdir(exist_ok=True)

        # Nome do arquivo TXT para dados limpos
        filename = f"{nome_etapa}_{timestamp_str}.txt"
        filepath = save_dir / filename

        try:
            # CORREÇÃO CRÍTICA: Limpa referências circulares ANTES de tentar salvar
            clean_dados = self._remove_circular_references_safe(dados)
            
            # Prepara dados para salvamento
            save_data = {
                "etapa": nome_etapa,
                "status": status,
                "dados": clean_dados,
                "timestamp": timestamp,
                "timestamp_iso": datetime.fromtimestamp(timestamp).isoformat(),
                "session_id": self.current_session_id,
                "analysis_id": self.analysis_id,
                "categoria": categoria,
                "tamanho_dados": len(str(clean_dados)) if clean_dados else 0
            }

            # Salva arquivo TXT limpo (sem dados brutos JSON)
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(f"ETAPA: {nome_etapa}\n")
                f.write(f"STATUS: {status}\n")
                f.write(f"TIMESTAMP: {datetime.fromtimestamp(timestamp).strftime('%d/%m/%Y %H:%M:%S')}\n")
                f.write(f"SESSÃO: {self.current_session_id}\n")
                f.write(f"CATEGORIA: {categoria}\n")
                f.write(f"TAMANHO: {len(str(dados)) if dados else 0} caracteres\n")
                f.write("=" * 50 + "\n")

                # Escreve dados de forma legível (não JSON bruto)
                if isinstance(dados, dict):
                    for key, value in dados.items():
                        f.write(f"\n{key.upper()}:\n")
                        if isinstance(value, list):
                            for item in value[:10]:  # Limita a 10 itens
                                f.write(f"• {str(item)[:200]}\n")
                        elif isinstance(value, dict):
                            for subkey, subvalue in list(value.items())[:5]:  # Limita a 5 subitens
                                f.write(f"  {subkey}: {str(subvalue)[:100]}\n")
                        else:
                            f.write(f"{str(value)[:500]}\n")
                elif isinstance(dados, list):
                    for i, item in enumerate(dados[:20], 1):  # Limita a 20 itens
                        f.write(f"{i}. {str(item)[:200]}\n")
                else:
                    f.write(f"DADOS: {str(dados)[:1000]}\n")

            # Log de sucesso
            logger.info(f"💾 Etapa '{nome_etapa}' salva: {filepath}")

            # Salva também backup JSON para dados críticos
            if categoria in ['analise_completa', 'pesquisa_web'] and len(str(clean_dados)) > 1000:
                json_filepath = save_dir / f"{nome_etapa}_{timestamp_str}.json"
                try:
                    # Tenta serializar para JSON para verificar se há referências circulares
                    json.dumps(save_data, default=str)
                    with open(json_filepath, "w", encoding="utf-8") as f:
                        json.dump(save_data, f, ensure_ascii=False, indent=2, default=str)
                except (ValueError, TypeError) as json_error:
                    logger.warning(f"⚠️ Não foi possível salvar JSON para {nome_etapa}: {json_error}")
                    # Salva versão simplificada
                    simplified_data = {
                        "etapa": nome_etapa,
                        "status": status,
                        "timestamp": timestamp,
                        "session_id": self.current_session_id,
                        "error": f"Dados simplificados devido a: {str(json_error)}"
                    }
                    with open(json_filepath, "w", encoding="utf-8") as f:
                        json.dump(simplified_data, f, ensure_ascii=False, indent=2)

            return str(filepath)

        except Exception as e:
            # Salvamento de emergência em caso de erro
            emergency_path = self.base_dir / f"EMERGENCY_{nome_etapa}_{timestamp_str}.txt"
            try:
                with open(emergency_path, "w", encoding="utf-8") as f:
                    f.write(f"ERRO AO SALVAR: {str(e)}\n")
                    f.write(f"DADOS: {str(dados)[:1000]}...\n")
                    f.write(f"STATUS: {status}\n")
                    f.write(f"TIMESTAMP: {timestamp}\n")

                logger.error(f"❌ Erro ao salvar '{nome_etapa}': {e}")
                logger.info(f"🆘 Backup de emergência salvo: {emergency_path}")

            except Exception as emergency_error:
                logger.critical(f"🚨 FALHA CRÍTICA no salvamento de emergência: {emergency_error}")

            return str(emergency_path)

    def salvar_erro(self, etapa: str, erro: Exception, contexto: Dict[str, Any] = None) -> str:
        """Salva erro com contexto completo"""

        erro_data = {
            "etapa": etapa,
            "tipo_erro": type(erro).__name__,
            "mensagem_erro": str(erro),
            "contexto": contexto or {},
            "stack_trace": self._get_stack_trace(erro),
            "timestamp_erro": time.time()
        }

        return self.salvar_etapa(f"ERRO_{etapa}", erro_data, status="erro", categoria="erros")

    def salvar_progresso(self, etapa_atual: str, progresso: float, detalhes: str = "") -> str:
        """Salva progresso atual"""

        progresso_data = {
            "etapa_atual": etapa_atual,
            "progresso_percentual": progresso,
            "detalhes": detalhes,
            "timestamp_progresso": time.time()
        }

        return self.salvar_etapa("progresso", progresso_data, categoria="logs")

    def recuperar_etapa(self, nome_etapa: str, session_id: str = None) -> Optional[Dict[str, Any]]:
        """Recupera dados de uma etapa específica"""

        session_id = session_id or self.current_session_id
        if not session_id:
            logger.error("❌ Nenhuma sessão ativa")
            return None

        # Busca em todos os subdiretórios
        for categoria, subdir in self.subdirs.items():
            session_dir = subdir / session_id
            if session_dir.exists():
                # Busca arquivos que começam com o nome da etapa
                for filepath in session_dir.glob(f"{nome_etapa}_*.json"):
                    try:
                        with open(filepath, "r", encoding="utf-8") as f:
                            data = json.load(f)

                        if data.get("status") == "sucesso":
                            logger.info(f"📂 Etapa '{nome_etapa}' recuperada: {filepath}")
                            return data

                    except Exception as e:
                        logger.error(f"❌ Erro ao recuperar {filepath}: {e}")
                        continue

        return None

    def listar_etapas_salvas(self, session_id: str = None) -> Dict[str, Any]:
        """Lista todas as etapas salvas de uma sessão"""

        session_id = session_id or self.current_session_id
        if not session_id:
            return {}

        etapas_encontradas = {}

        for categoria, subdir in self.subdirs.items():
            session_dir = subdir / session_id
            if session_dir.exists():
                for filepath in session_dir.glob("*.json"):
                    try:
                        with open(filepath, "r", encoding="utf-8") as f:
                            data = json.load(f)

                        etapa = data.get("etapa", "unknown")
                        if etapa not in etapas_encontradas:
                            etapas_encontradas[etapa] = []

                        etapas_encontradas[etapa].append({
                            "arquivo": str(filepath),
                            "status": data.get("status"),
                            "timestamp": data.get("timestamp"),
                            "categoria": categoria,
                            "tamanho": data.get("tamanho_dados", 0)
                        })

                    except Exception as e:
                        logger.error(f"❌ Erro ao ler {filepath}: {e}")
                        continue

        return etapas_encontradas

    def consolidar_sessao(self, session_id: str = None) -> str:
        """Consolida todas as etapas de uma sessão em um relatório final"""

        session_id = session_id or self.current_session_id
        etapas = self.listar_etapas_salvas(session_id)

        # Recupera dados de cada etapa
        relatorio_consolidado = {
            "session_id": session_id,
            "analysis_id": self.analysis_id,
            "consolidado_em": datetime.now().isoformat(),
            "etapas_processadas": {},
            "estatisticas": {
                "total_etapas": len(etapas),
                "etapas_sucesso": 0,
                "etapas_erro": 0,
                "etapas_fallback": 0
            }
        }

        for etapa_nome, arquivos in etapas.items():
            # Pega o arquivo mais recente de cada etapa
            arquivo_mais_recente = max(arquivos, key=lambda x: x["timestamp"])

            try:
                with open(arquivo_mais_recente["arquivo"], "r", encoding="utf-8") as f:
                    dados_etapa = json.load(f)

                relatorio_consolidado["etapas_processadas"][etapa_nome] = dados_etapa

                # Atualiza estatísticas
                status = dados_etapa.get("status", "unknown")
                if status == "sucesso":
                    relatorio_consolidado["estatisticas"]["etapas_sucesso"] += 1
                elif status == "erro":
                    relatorio_consolidado["estatisticas"]["etapas_erro"] += 1
                elif "fallback" in status:
                    relatorio_consolidado["estatisticas"]["etapas_fallback"] += 1

            except Exception as e:
                logger.error(f"❌ Erro ao consolidar etapa {etapa_nome}: {e}")
                continue

        # Salva relatório consolidado
        timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
        relatorio_path = self.subdirs["analise_completa"] / f"CONSOLIDADO_{session_id}_{timestamp_str}.json"

        with open(relatorio_path, "w", encoding="utf-8") as f:
            json.dump(relatorio_consolidado, f, ensure_ascii=False, indent=2, default=str)

        logger.info(f"📋 Relatório consolidado salvo: {relatorio_path}")
        return str(relatorio_path)

    def _salvar_backup_compactado(self, filepath: Path, data: Dict[str, Any]):
        """Salva backup compactado para dados grandes"""
        try:
            backup_path = filepath.with_suffix('.json.gz')
            with gzip.open(backup_path, 'wt', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2, default=str)

            logger.info(f"🗜️ Backup compactado salvo: {backup_path}")

        except Exception as e:
            logger.error(f"❌ Erro ao salvar backup compactado: {e}")

    def _get_stack_trace(self, erro: Exception) -> str:
        """Obtém stack trace do erro"""
        return traceback.format_exc()

    def _remove_circular_references_safe(self, obj, max_depth=10, seen=None):
        """Remove referências circulares de forma segura e robusta"""
        if seen is None:
            seen = set()
        
        if max_depth <= 0:
            return f"<Max depth reached: {type(obj).__name__}>"
        
        try:
            # Para tipos primitivos, retorna diretamente SEM verificar ID
            if obj is None or isinstance(obj, (str, int, float, bool)):
                return obj
            
            # Para tipos complexos, verifica circularidade
            obj_id = id(obj)
            if obj_id in seen:
                return f"<Circular reference: {type(obj).__name__}>"
            
            # Para dicionários
            if isinstance(obj, dict):
                seen.add(obj_id)
                clean_dict = {}
                for key, value in obj.items():
                    try:
                        # Evita chaves problemáticas conhecidas
                        if str(key).lower() in ['services', 'orchestrators', '_services', '_orchestrators', 'component_registry', 'sync_lock']:
                            clean_dict[key] = f"<Excluded: {type(value).__name__}>"
                        else:
                            # Cria uma nova cópia do seen para cada recursão
                            new_seen = seen.copy()
                            clean_dict[key] = self._remove_circular_references_safe(
                                value, max_depth - 1, new_seen
                            )
                    except Exception as e:
                        clean_dict[key] = f"<Error processing key '{key}': {str(e)[:50]}>"
                seen.remove(obj_id)
                return clean_dict
            
            # Para listas e tuplas
            elif isinstance(obj, (list, tuple)):
                seen.add(obj_id)
                clean_list = []
                for i, item in enumerate(obj[:50]):  # Limita a 50 itens
                    try:
                        new_seen = seen.copy()
                        clean_list.append(
                            self._remove_circular_references_safe(item, max_depth - 1, new_seen)
                        )
                    except Exception as e:
                        clean_list.append(f"<Error processing item {i}: {str(e)[:50]}>")
                seen.remove(obj_id)
                return clean_list if isinstance(obj, list) else tuple(clean_list)
            
            # Para objetos com __dict__
            elif hasattr(obj, '__dict__'):
                return f"<Object: {type(obj).__name__}>"
            
            # Para outros tipos, tenta converter para string
            else:
                try:
                    str_repr = str(obj)
                    if len(str_repr) > 200:
                        return str_repr[:200] + "..."
                    return str_repr
                except:
                    return f"<Unserializable: {type(obj).__name__}>"
                    
        except Exception as e:
            logger.error(f"❌ Erro crítico na remoção de referências circulares: {e}")
            return f"<Error cleaning {type(obj).__name__}: {str(e)[:100]}>"

    def limpar_sessoes_antigas(self, dias: int = 7):
        """Remove sessões mais antigas que X dias"""
        try:
            cutoff_time = time.time() - (dias * 24 * 60 * 60)
            removidas = 0

            for subdir in self.subdirs.values():
                if subdir.is_dir():
                    for item in subdir.iterdir():
                        if item.is_dir():
                            # Verifica se é mais antiga que o cutoff
                            if item.stat().st_mtime < cutoff_time:
                                shutil.rmtree(item)
                                removidas += 1
                                logger.info(f"🗑️ Sessão antiga removida: {item}")

            # Também limpa pastas de segmento antigas
            segmento_base_path = self.base_dir / "por_segmento"
            if segmento_base_path.is_dir():
                 for segmento_dir in segmento_base_path.iterdir():
                     if segmento_dir.is_dir():
                         if segmento_dir.stat().st_mtime < cutoff_time:
                            shutil.rmtree(segmento_dir)
                            removidas += 1
                            logger.info(f"🗑️ Pasta de segmento antiga removida: {segmento_dir}")

            logger.info(f"🧹 Limpeza concluída: {removidas} sessões/segmentos antigos removidos")

        except Exception as e:
            logger.error(f"❌ Erro na limpeza de sessões antigas: {e}")

    def listar_sessoes(self) -> List[str]:
        """Lista todas as sessões salvas"""
        try:
            session_path = os.path.join(self.base_dir, "logs") # Correção: base_dir em vez de base_path
            if not os.path.exists(session_path):
                return []

            sessoes = []
            for item in os.listdir(session_path):
                # Verifica se o item é um diretório e começa com 'session_'
                item_path = os.path.join(session_path, item)
                if os.path.isdir(item_path) and item.startswith('session_'):
                    sessoes.append(item)

            return sessoes

        except Exception as e:
            logger.error(f"Erro ao listar sessões: {e}")
            return []

    def obter_info_sessao(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Obtém informações de uma sessão específica"""
        try:
            # A lógica original de `obter_info_sessao` utilizava `self.base_path`, que não estava definido.
            # Assumindo que `self.base_dir` é o caminho correto.
            session_dir_path = self.base_dir / "logs" / session_id
            
            if not session_dir_path.exists():
                # Tenta encontrar em outras categorias se não for encontrada em logs
                for subdir in self.subdirs.values():
                    if subdir != self.subdirs['logs']: # Evita verificar a pasta de logs novamente
                        potential_session_path = subdir / session_id
                        if potential_session_path.exists():
                            session_dir_path = potential_session_path
                            break
                else: # Se o loop terminar sem encontrar
                    logger.info(f"Sessão '{session_id}' não encontrada em nenhum diretório.")
                    return None

            etapas = {}
            for arquivo in os.listdir(session_dir_path):
                if arquivo.endswith('.txt') or arquivo.endswith('.json'):
                    # Extrai o nome da etapa do nome do arquivo.
                    # Assume que o nome da etapa é tudo antes do primeiro '_' seguido por um timestamp numérico.
                    parts = arquivo.split('_')
                    if len(parts) > 1 and parts[1].startswith('20') and parts[1][:4].isdigit(): # Verifica se a segunda parte parece um timestamp
                        etapa_nome = '_'.join(parts[:-1]) # Reconstroi o nome da etapa, caso contenha underscores
                        timestamp_str = parts[-1].replace('.txt', '').replace('.json', '')
                    else: # Caso o padrão não seja encontrado, usa o nome do arquivo como etapa
                        etapa_nome = arquivo.replace('.txt', '').replace('.json', '')
                        timestamp_str = 'unknown'

                    arquivo_path = session_dir_path / arquivo

                    with open(arquivo_path, 'r', encoding='utf-8') as f:
                        if arquivo.endswith('.json'):
                            dados = json.load(f)
                        else:
                            dados = f.read()

                    etapas[etapa_nome] = {
                        'arquivo': arquivo,
                        'dados': dados,
                        'timestamp': timestamp_str
                    }

            return {
                'session_id': session_id,
                'etapas': etapas,
                'total_etapas': len(etapas)
            }

        except Exception as e:
            logger.error(f"Erro ao obter info da sessão {session_id}: {e}")
            return None


# Instância global
auto_save_manager = AutoSaveManager()

# Função de conveniência
def salvar_etapa(nome_etapa: str, dados: Any, status: str = "sucesso", categoria: str = "geral") -> str:
    """Função de conveniência para salvamento rápido"""
    return auto_save_manager.salvar_etapa(nome_etapa, dados, status, categoria=categoria)

def salvar_erro(etapa: str, erro: Exception, contexto: Dict[str, Any] = None) -> str:
    """Função de conveniência para salvamento de erros"""
    return auto_save_manager.salvar_erro(etapa, erro, contexto)