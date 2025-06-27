"""
Módulo de Shell - Ferramentas para execução de comandos do sistema
"""
import os
import subprocess
import time
from typing import Dict, Any, List
from .windows_compatibility import windows_compat


class ShellModule:
    """Módulo para execução de comandos shell com compatibilidade Windows/Linux"""
    
    def __init__(self, workspace_dir: str):
        self.workspace_dir = workspace_dir
        self.compat = windows_compat
        
        # Garantir que o diretório de trabalho existe
        self.compat.create_directory(workspace_dir, recursive=True)
    
    def get_tools(self) -> List[Dict[str, Any]]:
        """Retorna as ferramentas disponíveis"""
        return [
            {
                "type": "function",
                "function": {
                    "name": "execute_command",
                    "description": "Executa um comando no shell do sistema (compatível com Windows e Linux)",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "command": {
                                "type": "string",
                                "description": "Comando a ser executado"
                            },
                            "args": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "Argumentos do comando (opcional)"
                            },
                            "working_dir": {
                                "type": "string",
                                "description": "Diretório de trabalho (opcional)"
                            }
                        },
                        "required": ["command"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "list_directory",
                    "description": "Lista o conteúdo de um diretório",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "path": {
                                "type": "string",
                                "description": "Caminho do diretório (opcional, padrão: diretório atual)"
                            }
                        }
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_system_info",
                    "description": "Obtém informações do sistema operacional",
                    "parameters": {
                        "type": "object",
                        "properties": {}
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_environment_variables",
                    "description": "Obtém variáveis de ambiente do sistema",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "name": {
                                "type": "string",
                                "description": "Nome da variável específica (opcional)"
                            }
                        }
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "find_executable",
                    "description": "Encontra um executável no PATH do sistema",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "name": {
                                "type": "string",
                                "description": "Nome do executável"
                            }
                        },
                        "required": ["name"]
                    }
                }
            }
        ]
    
    def execute_command(self, command: str, args: List[str] = None, working_dir: str = None) -> Dict[str, Any]:
        """Executa um comando no shell"""
        try:
            # Usar diretório de trabalho especificado ou padrão
            if working_dir:
                work_dir = self.compat.normalize_path(working_dir)
            else:
                work_dir = self.workspace_dir
            
            # Salvar diretório atual
            original_dir = os.getcwd()
            
            try:
                # Mudar para diretório de trabalho
                os.chdir(work_dir)
                
                # Executar comando
                start_time = time.time()
                returncode, stdout, stderr = self.compat.execute_command(command, args)
                execution_time = time.time() - start_time
                
                return {
                    "success": returncode == 0,
                    "returncode": returncode,
                    "stdout": stdout,
                    "stderr": stderr,
                    "execution_time": execution_time,
                    "working_directory": work_dir,
                    "system": self.compat.is_windows and "Windows" or "Linux"
                }
                
            finally:
                # Restaurar diretório original
                os.chdir(original_dir)
                
        except Exception as e:
            return {
                "success": False,
                "error": f"Erro ao executar comando: {str(e)}",
                "system": self.compat.is_windows and "Windows" or "Linux"
            }
    
    def list_directory(self, path: str = None) -> Dict[str, Any]:
        """Lista o conteúdo de um diretório"""
        try:
            if path is None:
                path = self.workspace_dir
            
            items = self.compat.list_directory(path)
            
            return {
                "success": True,
                "path": self.compat.normalize_path(path),
                "items": items,
                "count": len(items),
                "system": self.compat.is_windows and "Windows" or "Linux"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Erro ao listar diretório: {str(e)}",
                "system": self.compat.is_windows and "Windows" or "Linux"
            }
    
    def get_system_info(self) -> Dict[str, Any]:
        """Obtém informações do sistema"""
        try:
            info = self.compat.get_system_info()
            
            # Adicionar informações específicas do módulo
            info.update({
                "workspace_directory": self.workspace_dir,
                "current_directory": os.getcwd(),
                "path_separator": self.compat.path_separator,
                "dir_separator": self.compat.dir_separator,
                "temp_directory": self.compat.get_temp_directory(),
                "home_directory": self.compat.get_home_directory()
            })
            
            return {
                "success": True,
                "system_info": info
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Erro ao obter informações do sistema: {str(e)}"
            }
    
    def get_environment_variables(self, name: str = None) -> Dict[str, Any]:
        """Obtém variáveis de ambiente"""
        try:
            if name:
                # Variável específica
                value = self.compat.get_environment_variable(name)
                return {
                    "success": True,
                    "variable": name,
                    "value": value,
                    "found": value is not None
                }
            else:
                # Todas as variáveis (limitado para evitar sobrecarga)
                important_vars = ["PATH", "HOME", "USER", "USERPROFILE", "TEMP", "TMP", "PYTHONPATH"]
                variables = {}
                
                for var in important_vars:
                    value = self.compat.get_environment_variable(var)
                    if value is not None:
                        variables[var] = value
                
                return {
                    "success": True,
                    "variables": variables,
                    "count": len(variables)
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"Erro ao obter variáveis de ambiente: {str(e)}"
            }
    
    def find_executable(self, name: str) -> Dict[str, Any]:
        """Encontra um executável no PATH"""
        try:
            path = self.compat.find_executable(name)
            
            return {
                "success": True,
                "executable": name,
                "path": path,
                "found": path is not None,
                "system": self.compat.is_windows and "Windows" or "Linux"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Erro ao procurar executável: {str(e)}"
            }

