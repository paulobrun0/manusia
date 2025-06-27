"""
Módulo de Compatibilidade com Windows
"""
import os
import platform
import subprocess
from typing import Dict, List, Optional, Tuple


class WindowsCompatibility:
    """Classe para lidar com compatibilidade entre Windows e Linux"""
    
    def __init__(self):
        self.is_windows = platform.system().lower() == "windows"
        self.is_linux = platform.system().lower() == "linux"
        
        # Mapeamento de comandos
        self.command_mapping = {
            # Comandos básicos
            "ls": "dir" if self.is_windows else "ls",
            "cat": "type" if self.is_windows else "cat",
            "clear": "cls" if self.is_windows else "clear",
            "rm": "del" if self.is_windows else "rm",
            "cp": "copy" if self.is_windows else "cp",
            "mv": "move" if self.is_windows else "mv",
            "mkdir": "mkdir",  # Mesmo comando
            "rmdir": "rmdir",  # Mesmo comando
            "pwd": "cd" if self.is_windows else "pwd",
            
            # Comandos de sistema
            "ps": "tasklist" if self.is_windows else "ps",
            "kill": "taskkill" if self.is_windows else "kill",
            "which": "where" if self.is_windows else "which",
            "find": "findstr" if self.is_windows else "grep",
            
            # Comandos de rede
            "ping": "ping",  # Mesmo comando
            "netstat": "netstat",  # Mesmo comando
            "ipconfig": "ipconfig" if self.is_windows else "ifconfig",
        }
        
        # Extensões de arquivo executável
        self.executable_extensions = [".exe", ".bat", ".cmd"] if self.is_windows else [""]
        
        # Separador de PATH
        self.path_separator = ";" if self.is_windows else ":"
        
        # Separador de diretório
        self.dir_separator = "\\" if self.is_windows else "/"
    
    def normalize_path(self, path: str) -> str:
        """Normaliza um caminho para o sistema operacional atual"""
        if self.is_windows:
            # Converter / para \
            path = path.replace("/", "\\")
            # Adicionar drive se necessário
            if not os.path.isabs(path) and not path.startswith("\\"):
                path = os.path.abspath(path)
        else:
            # Converter \ para /
            path = path.replace("\\", "/")
        
        return os.path.normpath(path)
    
    def get_command(self, linux_command: str) -> str:
        """Retorna o comando equivalente para o sistema atual"""
        return self.command_mapping.get(linux_command, linux_command)
    
    def execute_command(self, command: str, args: List[str] = None, shell: bool = True) -> Tuple[int, str, str]:
        """Executa um comando de forma compatível com o sistema"""
        if args is None:
            args = []
        
        # Mapear comando se necessário
        mapped_command = self.get_command(command)
        
        # Construir comando completo
        if args:
            full_command = [mapped_command] + args
        else:
            full_command = mapped_command
        
        try:
            # Executar comando
            if shell and isinstance(full_command, list):
                full_command = " ".join(full_command)
            
            result = subprocess.run(
                full_command,
                shell=shell,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            return result.returncode, result.stdout, result.stderr
            
        except subprocess.TimeoutExpired:
            return 1, "", "Comando expirou após 30 segundos"
        except Exception as e:
            return 1, "", f"Erro ao executar comando: {str(e)}"
    
    def list_directory(self, path: str = ".") -> List[Dict[str, str]]:
        """Lista o conteúdo de um diretório de forma compatível"""
        normalized_path = self.normalize_path(path)
        
        try:
            items = []
            for item in os.listdir(normalized_path):
                item_path = os.path.join(normalized_path, item)
                stat = os.stat(item_path)
                
                items.append({
                    "name": item,
                    "type": "directory" if os.path.isdir(item_path) else "file",
                    "size": stat.st_size,
                    "modified": stat.st_mtime,
                    "path": item_path
                })
            
            return items
            
        except Exception as e:
            return [{"error": f"Erro ao listar diretório: {str(e)}"}]
    
    def get_system_info(self) -> Dict[str, str]:
        """Obtém informações do sistema de forma compatível"""
        info = {
            "system": platform.system(),
            "release": platform.release(),
            "version": platform.version(),
            "machine": platform.machine(),
            "processor": platform.processor(),
            "architecture": platform.architecture()[0],
            "hostname": platform.node(),
            "python_version": platform.python_version(),
        }
        
        # Informações específicas do Windows
        if self.is_windows:
            try:
                import winreg
                with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, 
                                  r"SOFTWARE\Microsoft\Windows NT\CurrentVersion") as key:
                    info["windows_edition"] = winreg.QueryValueEx(key, "EditionID")[0]
                    info["windows_build"] = winreg.QueryValueEx(key, "CurrentBuild")[0]
            except:
                pass
        
        return info
    
    def get_environment_variable(self, name: str) -> Optional[str]:
        """Obtém uma variável de ambiente"""
        return os.environ.get(name)
    
    def set_environment_variable(self, name: str, value: str) -> bool:
        """Define uma variável de ambiente"""
        try:
            os.environ[name] = value
            return True
        except Exception:
            return False
    
    def get_path_variable(self) -> List[str]:
        """Obtém os diretórios do PATH"""
        path = self.get_environment_variable("PATH")
        if path:
            return path.split(self.path_separator)
        return []
    
    def find_executable(self, name: str) -> Optional[str]:
        """Encontra um executável no PATH"""
        # Adicionar extensões do Windows se necessário
        if self.is_windows and not any(name.endswith(ext) for ext in self.executable_extensions):
            candidates = [name + ext for ext in self.executable_extensions]
        else:
            candidates = [name]
        
        # Procurar nos diretórios do PATH
        for directory in self.get_path_variable():
            for candidate in candidates:
                full_path = os.path.join(directory, candidate)
                if os.path.isfile(full_path) and os.access(full_path, os.X_OK):
                    return full_path
        
        return None
    
    def get_temp_directory(self) -> str:
        """Obtém o diretório temporário do sistema"""
        if self.is_windows:
            return os.environ.get("TEMP", os.environ.get("TMP", "C:\\temp"))
        else:
            return "/tmp"
    
    def get_home_directory(self) -> str:
        """Obtém o diretório home do usuário"""
        if self.is_windows:
            return os.environ.get("USERPROFILE", "C:\\Users\\Default")
        else:
            return os.environ.get("HOME", "/home/user")
    
    def create_directory(self, path: str, recursive: bool = True) -> bool:
        """Cria um diretório de forma compatível"""
        try:
            normalized_path = self.normalize_path(path)
            if recursive:
                os.makedirs(normalized_path, exist_ok=True)
            else:
                os.mkdir(normalized_path)
            return True
        except Exception:
            return False
    
    def remove_file(self, path: str) -> bool:
        """Remove um arquivo de forma compatível"""
        try:
            normalized_path = self.normalize_path(path)
            os.remove(normalized_path)
            return True
        except Exception:
            return False
    
    def remove_directory(self, path: str, recursive: bool = False) -> bool:
        """Remove um diretório de forma compatível"""
        try:
            normalized_path = self.normalize_path(path)
            if recursive:
                import shutil
                shutil.rmtree(normalized_path)
            else:
                os.rmdir(normalized_path)
            return True
        except Exception:
            return False
    
    def copy_file(self, source: str, destination: str) -> bool:
        """Copia um arquivo de forma compatível"""
        try:
            import shutil
            source_path = self.normalize_path(source)
            dest_path = self.normalize_path(destination)
            shutil.copy2(source_path, dest_path)
            return True
        except Exception:
            return False
    
    def move_file(self, source: str, destination: str) -> bool:
        """Move um arquivo de forma compatível"""
        try:
            import shutil
            source_path = self.normalize_path(source)
            dest_path = self.normalize_path(destination)
            shutil.move(source_path, dest_path)
            return True
        except Exception:
            return False
    
    def get_file_permissions(self, path: str) -> Optional[str]:
        """Obtém as permissões de um arquivo"""
        try:
            normalized_path = self.normalize_path(path)
            stat = os.stat(normalized_path)
            
            if self.is_windows:
                # No Windows, usar os.access para verificar permissões básicas
                permissions = []
                if os.access(normalized_path, os.R_OK):
                    permissions.append("r")
                if os.access(normalized_path, os.W_OK):
                    permissions.append("w")
                if os.access(normalized_path, os.X_OK):
                    permissions.append("x")
                return "".join(permissions)
            else:
                # No Linux, usar stat.st_mode
                import stat as stat_module
                mode = stat.st_mode
                permissions = stat_module.filemode(mode)
                return permissions
                
        except Exception:
            return None
    
    def get_disk_usage(self, path: str = ".") -> Optional[Dict[str, int]]:
        """Obtém informações de uso do disco"""
        try:
            normalized_path = self.normalize_path(path)
            
            if self.is_windows:
                import shutil
                total, used, free = shutil.disk_usage(normalized_path)
            else:
                statvfs = os.statvfs(normalized_path)
                total = statvfs.f_frsize * statvfs.f_blocks
                free = statvfs.f_frsize * statvfs.f_available
                used = total - free
            
            return {
                "total": total,
                "used": used,
                "free": free,
                "percent_used": (used / total) * 100 if total > 0 else 0
            }
            
        except Exception:
            return None


# Instância global de compatibilidade
windows_compat = WindowsCompatibility()

