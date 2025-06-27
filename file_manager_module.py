"""
Módulo de Gerenciamento de Arquivos Avançado
"""
import os
import json
import csv
import shutil
import zipfile
import tarfile
import hashlib
import mimetypes
from typing import Dict, Any, List, Optional, Union
from datetime import datetime
from pathlib import Path
import subprocess


class FileManagerModule:
    """Módulo avançado para gerenciamento de arquivos e sistema"""
    
    def __init__(self, base_directory: str = "/tmp/agent_workspace"):
        self.base_directory = Path(base_directory)
        self.base_directory.mkdir(parents=True, exist_ok=True)
        self.operation_history = []
        self.max_history_size = 1000
        
        # Tipos de arquivo suportados
        self.supported_text_formats = ['.txt', '.md', '.py', '.js', '.html', '.css', '.json', '.xml', '.csv']
        self.supported_archive_formats = ['.zip', '.tar', '.tar.gz', '.tar.bz2']
        self.supported_image_formats = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg']
    
    def _log_operation(self, operation: str, details: Dict[str, Any]) -> None:
        """Registra uma operação no histórico"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "operation": operation,
            "details": details
        }
        
        self.operation_history.append(log_entry)
        
        # Limitar tamanho do histórico
        if len(self.operation_history) > self.max_history_size:
            self.operation_history.pop(0)
    
    def _resolve_path(self, path: str) -> Path:
        """Resolve um caminho relativo ou absoluto"""
        path_obj = Path(path)
        if not path_obj.is_absolute():
            path_obj = self.base_directory / path_obj
        return path_obj.resolve()
    
    def create_file_with_content(
        self,
        file_path: str,
        content: str,
        encoding: str = "utf-8",
        backup_existing: bool = True
    ) -> Dict[str, Any]:
        """Cria um arquivo com conteúdo, com opção de backup"""
        try:
            resolved_path = self._resolve_path(file_path)
            
            # Criar diretórios pai se necessário
            resolved_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Fazer backup se o arquivo existir
            backup_path = None
            if backup_existing and resolved_path.exists():
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_path = resolved_path.with_suffix(f".backup_{timestamp}{resolved_path.suffix}")
                shutil.copy2(resolved_path, backup_path)
            
            # Escrever conteúdo
            with open(resolved_path, 'w', encoding=encoding) as f:
                f.write(content)
            
            # Registrar operação
            self._log_operation("create_file", {
                "file_path": str(resolved_path),
                "content_length": len(content),
                "encoding": encoding,
                "backup_created": backup_path is not None,
                "backup_path": str(backup_path) if backup_path else None
            })
            
            return {
                "success": True,
                "file_path": str(resolved_path),
                "content_length": len(content),
                "backup_path": str(backup_path) if backup_path else None,
                "created": True
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "file_path": file_path
            }
    
    def edit_file_content(
        self,
        file_path: str,
        operation: str,
        content: str = "",
        line_number: Optional[int] = None,
        search_text: str = "",
        replace_text: str = "",
        encoding: str = "utf-8"
    ) -> Dict[str, Any]:
        """Edita o conteúdo de um arquivo de várias formas"""
        try:
            resolved_path = self._resolve_path(file_path)
            
            if not resolved_path.exists():
                return {
                    "success": False,
                    "error": f"Arquivo não encontrado: {resolved_path}",
                    "file_path": str(resolved_path)
                }
            
            # Ler conteúdo atual
            with open(resolved_path, 'r', encoding=encoding) as f:
                lines = f.readlines()
            
            original_content = ''.join(lines)
            
            # Executar operação
            if operation == "append":
                lines.append(content + '\n' if not content.endswith('\n') else content)
            
            elif operation == "prepend":
                lines.insert(0, content + '\n' if not content.endswith('\n') else content)
            
            elif operation == "insert_at_line":
                if line_number is None or line_number < 1:
                    return {"success": False, "error": "Número da linha é obrigatório para inserção"}
                
                # Ajustar para índice baseado em 0
                insert_index = min(line_number - 1, len(lines))
                lines.insert(insert_index, content + '\n' if not content.endswith('\n') else content)
            
            elif operation == "replace_line":
                if line_number is None or line_number < 1 or line_number > len(lines):
                    return {"success": False, "error": "Número da linha inválido"}
                
                lines[line_number - 1] = content + '\n' if not content.endswith('\n') else content
            
            elif operation == "delete_line":
                if line_number is None or line_number < 1 or line_number > len(lines):
                    return {"success": False, "error": "Número da linha inválido"}
                
                del lines[line_number - 1]
            
            elif operation == "find_replace":
                if not search_text:
                    return {"success": False, "error": "Texto de busca é obrigatório"}
                
                new_content = original_content.replace(search_text, replace_text)
                lines = new_content.splitlines(keepends=True)
            
            else:
                return {"success": False, "error": f"Operação não suportada: {operation}"}
            
            # Escrever conteúdo modificado
            with open(resolved_path, 'w', encoding=encoding) as f:
                f.writelines(lines)
            
            new_content = ''.join(lines)
            
            # Registrar operação
            self._log_operation("edit_file", {
                "file_path": str(resolved_path),
                "operation": operation,
                "original_length": len(original_content),
                "new_length": len(new_content),
                "line_number": line_number,
                "search_text": search_text[:100] if search_text else None,
                "replace_text": replace_text[:100] if replace_text else None
            })
            
            return {
                "success": True,
                "file_path": str(resolved_path),
                "operation": operation,
                "original_length": len(original_content),
                "new_length": len(new_content),
                "lines_count": len(lines)
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "file_path": file_path,
                "operation": operation
            }
    
    def search_in_files(
        self,
        search_pattern: str,
        directory: str = ".",
        file_extensions: Optional[List[str]] = None,
        case_sensitive: bool = False,
        max_results: int = 100
    ) -> Dict[str, Any]:
        """Busca por padrão em arquivos"""
        try:
            search_dir = self._resolve_path(directory)
            
            if not search_dir.exists():
                return {
                    "success": False,
                    "error": f"Diretório não encontrado: {search_dir}",
                    "directory": str(search_dir)
                }
            
            results = []
            files_searched = 0
            
            # Preparar padrão de busca
            pattern = search_pattern if case_sensitive else search_pattern.lower()
            
            # Buscar em arquivos
            for file_path in search_dir.rglob("*"):
                if file_path.is_file():
                    # Filtrar por extensão se especificado
                    if file_extensions and file_path.suffix.lower() not in file_extensions:
                        continue
                    
                    # Verificar se é arquivo de texto
                    if file_path.suffix.lower() not in self.supported_text_formats:
                        continue
                    
                    try:
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            lines = f.readlines()
                        
                        files_searched += 1
                        
                        # Buscar em cada linha
                        for line_num, line in enumerate(lines, 1):
                            search_line = line if case_sensitive else line.lower()
                            
                            if pattern in search_line:
                                results.append({
                                    "file_path": str(file_path),
                                    "line_number": line_num,
                                    "line_content": line.strip(),
                                    "match_position": search_line.find(pattern)
                                })
                                
                                if len(results) >= max_results:
                                    break
                        
                        if len(results) >= max_results:
                            break
                            
                    except Exception as e:
                        # Ignorar arquivos que não podem ser lidos
                        continue
            
            # Registrar operação
            self._log_operation("search_files", {
                "pattern": search_pattern,
                "directory": str(search_dir),
                "files_searched": files_searched,
                "matches_found": len(results),
                "case_sensitive": case_sensitive
            })
            
            return {
                "success": True,
                "pattern": search_pattern,
                "directory": str(search_dir),
                "results": results,
                "matches_found": len(results),
                "files_searched": files_searched
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "pattern": search_pattern,
                "directory": directory
            }
    
    def create_archive(
        self,
        archive_path: str,
        source_paths: List[str],
        archive_type: str = "zip",
        compression_level: int = 6
    ) -> Dict[str, Any]:
        """Cria um arquivo compactado"""
        try:
            resolved_archive_path = self._resolve_path(archive_path)
            resolved_archive_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Resolver caminhos de origem
            resolved_sources = []
            for source in source_paths:
                source_path = self._resolve_path(source)
                if source_path.exists():
                    resolved_sources.append(source_path)
                else:
                    return {
                        "success": False,
                        "error": f"Caminho de origem não encontrado: {source_path}",
                        "source": source
                    }
            
            files_added = 0
            
            if archive_type == "zip":
                with zipfile.ZipFile(resolved_archive_path, 'w', zipfile.ZIP_DEFLATED, compresslevel=compression_level) as zf:
                    for source_path in resolved_sources:
                        if source_path.is_file():
                            zf.write(source_path, source_path.name)
                            files_added += 1
                        elif source_path.is_dir():
                            for file_path in source_path.rglob("*"):
                                if file_path.is_file():
                                    arcname = file_path.relative_to(source_path.parent)
                                    zf.write(file_path, arcname)
                                    files_added += 1
            
            elif archive_type in ["tar", "tar.gz", "tar.bz2"]:
                mode = "w"
                if archive_type == "tar.gz":
                    mode = "w:gz"
                elif archive_type == "tar.bz2":
                    mode = "w:bz2"
                
                with tarfile.open(resolved_archive_path, mode) as tf:
                    for source_path in resolved_sources:
                        if source_path.is_file():
                            tf.add(source_path, source_path.name)
                            files_added += 1
                        elif source_path.is_dir():
                            tf.add(source_path, source_path.name)
                            # Contar arquivos no diretório
                            for file_path in source_path.rglob("*"):
                                if file_path.is_file():
                                    files_added += 1
            
            else:
                return {
                    "success": False,
                    "error": f"Tipo de arquivo não suportado: {archive_type}",
                    "archive_type": archive_type
                }
            
            # Registrar operação
            self._log_operation("create_archive", {
                "archive_path": str(resolved_archive_path),
                "source_paths": [str(p) for p in resolved_sources],
                "archive_type": archive_type,
                "files_added": files_added,
                "archive_size": resolved_archive_path.stat().st_size
            })
            
            return {
                "success": True,
                "archive_path": str(resolved_archive_path),
                "archive_type": archive_type,
                "files_added": files_added,
                "archive_size": resolved_archive_path.stat().st_size
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "archive_path": archive_path,
                "archive_type": archive_type
            }
    
    def extract_archive(
        self,
        archive_path: str,
        destination: str = ".",
        extract_all: bool = True,
        specific_files: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Extrai um arquivo compactado"""
        try:
            resolved_archive_path = self._resolve_path(archive_path)
            resolved_destination = self._resolve_path(destination)
            
            if not resolved_archive_path.exists():
                return {
                    "success": False,
                    "error": f"Arquivo não encontrado: {resolved_archive_path}",
                    "archive_path": str(resolved_archive_path)
                }
            
            resolved_destination.mkdir(parents=True, exist_ok=True)
            
            files_extracted = 0
            archive_type = None
            
            # Detectar tipo de arquivo
            if resolved_archive_path.suffix.lower() == '.zip':
                archive_type = "zip"
                with zipfile.ZipFile(resolved_archive_path, 'r') as zf:
                    if extract_all:
                        zf.extractall(resolved_destination)
                        files_extracted = len(zf.namelist())
                    elif specific_files:
                        for file_name in specific_files:
                            if file_name in zf.namelist():
                                zf.extract(file_name, resolved_destination)
                                files_extracted += 1
            
            elif resolved_archive_path.suffix.lower() in ['.tar', '.gz', '.bz2'] or '.tar.' in resolved_archive_path.name:
                archive_type = "tar"
                with tarfile.open(resolved_archive_path, 'r:*') as tf:
                    if extract_all:
                        tf.extractall(resolved_destination)
                        files_extracted = len(tf.getnames())
                    elif specific_files:
                        for file_name in specific_files:
                            try:
                                tf.extract(file_name, resolved_destination)
                                files_extracted += 1
                            except KeyError:
                                continue
            
            else:
                return {
                    "success": False,
                    "error": f"Tipo de arquivo não suportado: {resolved_archive_path.suffix}",
                    "archive_path": str(resolved_archive_path)
                }
            
            # Registrar operação
            self._log_operation("extract_archive", {
                "archive_path": str(resolved_archive_path),
                "destination": str(resolved_destination),
                "archive_type": archive_type,
                "files_extracted": files_extracted,
                "extract_all": extract_all
            })
            
            return {
                "success": True,
                "archive_path": str(resolved_archive_path),
                "destination": str(resolved_destination),
                "archive_type": archive_type,
                "files_extracted": files_extracted
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "archive_path": archive_path,
                "destination": destination
            }
    
    def calculate_file_hash(
        self,
        file_path: str,
        algorithm: str = "sha256"
    ) -> Dict[str, Any]:
        """Calcula o hash de um arquivo"""
        try:
            resolved_path = self._resolve_path(file_path)
            
            if not resolved_path.exists():
                return {
                    "success": False,
                    "error": f"Arquivo não encontrado: {resolved_path}",
                    "file_path": str(resolved_path)
                }
            
            # Verificar algoritmo suportado
            if algorithm not in hashlib.algorithms_available:
                return {
                    "success": False,
                    "error": f"Algoritmo de hash não suportado: {algorithm}",
                    "algorithm": algorithm
                }
            
            # Calcular hash
            hash_obj = hashlib.new(algorithm)
            
            with open(resolved_path, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_obj.update(chunk)
            
            file_hash = hash_obj.hexdigest()
            file_size = resolved_path.stat().st_size
            
            # Registrar operação
            self._log_operation("calculate_hash", {
                "file_path": str(resolved_path),
                "algorithm": algorithm,
                "file_size": file_size,
                "hash": file_hash
            })
            
            return {
                "success": True,
                "file_path": str(resolved_path),
                "algorithm": algorithm,
                "hash": file_hash,
                "file_size": file_size
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "file_path": file_path,
                "algorithm": algorithm
            }
    
    def get_file_metadata(self, file_path: str) -> Dict[str, Any]:
        """Obtém metadados detalhados de um arquivo"""
        try:
            resolved_path = self._resolve_path(file_path)
            
            if not resolved_path.exists():
                return {
                    "success": False,
                    "error": f"Arquivo não encontrado: {resolved_path}",
                    "file_path": str(resolved_path)
                }
            
            stat = resolved_path.stat()
            
            # Informações básicas
            metadata = {
                "file_path": str(resolved_path),
                "name": resolved_path.name,
                "extension": resolved_path.suffix,
                "size": stat.st_size,
                "created": datetime.fromtimestamp(stat.st_ctime).isoformat(),
                "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                "accessed": datetime.fromtimestamp(stat.st_atime).isoformat(),
                "permissions": oct(stat.st_mode)[-3:],
                "is_file": resolved_path.is_file(),
                "is_directory": resolved_path.is_dir(),
                "is_symlink": resolved_path.is_symlink()
            }
            
            # Tipo MIME
            mime_type, encoding = mimetypes.guess_type(str(resolved_path))
            metadata["mime_type"] = mime_type
            metadata["encoding"] = encoding
            
            # Informações específicas para arquivos de texto
            if resolved_path.is_file() and resolved_path.suffix.lower() in self.supported_text_formats:
                try:
                    with open(resolved_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                        lines = content.splitlines()
                        
                    metadata["text_info"] = {
                        "lines_count": len(lines),
                        "characters_count": len(content),
                        "words_count": len(content.split()),
                        "encoding_detected": "utf-8"
                    }
                except Exception:
                    pass
            
            return {
                "success": True,
                "metadata": metadata
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "file_path": file_path
            }
    
    def monitor_directory_changes(
        self,
        directory: str,
        duration_seconds: int = 60
    ) -> Dict[str, Any]:
        """Monitora mudanças em um diretório por um período"""
        try:
            resolved_dir = self._resolve_path(directory)
            
            if not resolved_dir.exists():
                return {
                    "success": False,
                    "error": f"Diretório não encontrado: {resolved_dir}",
                    "directory": str(resolved_dir)
                }
            
            # Capturar estado inicial
            initial_state = {}
            for file_path in resolved_dir.rglob("*"):
                if file_path.is_file():
                    stat = file_path.stat()
                    initial_state[str(file_path)] = {
                        "size": stat.st_size,
                        "modified": stat.st_mtime
                    }
            
            # Simular monitoramento (em implementação real, usaria watchdog ou similar)
            import time
            time.sleep(min(duration_seconds, 5))  # Limitar para teste
            
            # Capturar estado final
            final_state = {}
            for file_path in resolved_dir.rglob("*"):
                if file_path.is_file():
                    stat = file_path.stat()
                    final_state[str(file_path)] = {
                        "size": stat.st_size,
                        "modified": stat.st_mtime
                    }
            
            # Detectar mudanças
            changes = {
                "created": [],
                "modified": [],
                "deleted": []
            }
            
            # Arquivos criados
            for file_path in final_state:
                if file_path not in initial_state:
                    changes["created"].append(file_path)
            
            # Arquivos deletados
            for file_path in initial_state:
                if file_path not in final_state:
                    changes["deleted"].append(file_path)
            
            # Arquivos modificados
            for file_path in initial_state:
                if file_path in final_state:
                    if (initial_state[file_path]["modified"] != final_state[file_path]["modified"] or
                        initial_state[file_path]["size"] != final_state[file_path]["size"]):
                        changes["modified"].append(file_path)
            
            total_changes = len(changes["created"]) + len(changes["modified"]) + len(changes["deleted"])
            
            # Registrar operação
            self._log_operation("monitor_directory", {
                "directory": str(resolved_dir),
                "duration_seconds": duration_seconds,
                "total_changes": total_changes,
                "changes": changes
            })
            
            return {
                "success": True,
                "directory": str(resolved_dir),
                "duration_seconds": duration_seconds,
                "changes": changes,
                "total_changes": total_changes
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "directory": directory
            }
    
    def get_operation_history(self, count: int = 20) -> Dict[str, Any]:
        """Retorna o histórico de operações"""
        try:
            history = self.operation_history[-count:] if count > 0 else self.operation_history
            
            return {
                "success": True,
                "history": history,
                "total_operations": len(self.operation_history),
                "returned_count": len(history)
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def clear_operation_history(self) -> Dict[str, Any]:
        """Limpa o histórico de operações"""
        try:
            cleared_count = len(self.operation_history)
            self.operation_history.clear()
            
            return {
                "success": True,
                "cleared_operations": cleared_count
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

