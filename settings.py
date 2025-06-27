"""
Configurações do Agente Autônomo
"""
import os
import platform
from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Configurações do sistema"""
    
    # API Keys
    openai_api_key: Optional[str] = None
    gemini_api_key: Optional[str] = None
    
    # Configurações do LLM
    llm_provider: str = "gemini"  # "openai" ou "gemini"
    default_model: str = "gemini-2.5-flash"  # Para Gemini
    openai_model: str = "gpt-4"  # Para OpenAI
    max_tokens: int = 4000
    temperature: float = 0.1
    
    # Configurações de memória
    memory_max_tokens: int = 8000
    memory_persist_path: str = "./data/memory"
    
    # Configurações de logging
    log_level: str = "INFO"
    log_file: str = "./logs/agent.log"
    
    # Configurações de segurança
    max_execution_time: int = 300  # 5 minutos
    allowed_file_extensions: list = [".txt", ".md", ".py", ".json", ".csv", ".html", ".css", ".js"]
    
    # Configurações de sistema operacional
    os_type: str = "auto"  # "auto", "windows", "linux"
    
    # Configurações do agente programador
    enable_code_execution: bool = True
    supported_languages: list = ["python", "javascript", "html", "css", "bash", "powershell"]
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
    
    def get_os_type(self) -> str:
        """Detecta o tipo de sistema operacional"""
        if self.os_type == "auto":
            return "windows" if platform.system().lower() == "windows" else "linux"
        return self.os_type
    
    def get_current_model(self) -> str:
        """Retorna o modelo atual baseado no provedor"""
        if self.llm_provider == "gemini":
            return self.default_model
        else:
            return self.openai_model


# Instância global das configurações
settings = Settings()

