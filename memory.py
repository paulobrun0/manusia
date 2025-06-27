"""
Sistema de Memória do Agente
"""
import json
import os
from typing import List, Dict, Any, Optional
from datetime import datetime
from pydantic import BaseModel


class MemoryEntry(BaseModel):
    """Entrada de memória"""
    timestamp: datetime
    type: str  # "conversation", "action", "result", "knowledge"
    content: str
    metadata: Dict[str, Any] = {}


class Memory:
    """Sistema de memória do agente"""
    
    def __init__(self, persist_path: str = "./data/memory"):
        self.persist_path = persist_path
        self.short_term_memory: List[MemoryEntry] = []
        self.long_term_memory: List[MemoryEntry] = []
        self.max_short_term_entries = 50
        
        # Criar diretório se não existir
        os.makedirs(persist_path, exist_ok=True)
        
        # Carregar memória persistente
        self._load_long_term_memory()
    
    def add_entry(self, entry_type: str, content: str, metadata: Dict[str, Any] = None) -> None:
        """Adiciona uma entrada à memória"""
        if metadata is None:
            metadata = {}
            
        entry = MemoryEntry(
            timestamp=datetime.now(),
            type=entry_type,
            content=content,
            metadata=metadata
        )
        
        # Adicionar à memória de curto prazo
        self.short_term_memory.append(entry)
        
        # Limitar tamanho da memória de curto prazo
        if len(self.short_term_memory) > self.max_short_term_entries:
            # Mover entradas antigas para memória de longo prazo
            old_entry = self.short_term_memory.pop(0)
            self.long_term_memory.append(old_entry)
    
    def get_recent_entries(self, count: int = 10, entry_type: Optional[str] = None) -> List[MemoryEntry]:
        """Recupera entradas recentes da memória"""
        entries = self.short_term_memory.copy()
        
        if entry_type:
            entries = [e for e in entries if e.type == entry_type]
        
        return entries[-count:] if count > 0 else entries
    
    def search_memory(self, query: str, entry_type: Optional[str] = None) -> List[MemoryEntry]:
        """Busca na memória por conteúdo relevante"""
        all_entries = self.short_term_memory + self.long_term_memory
        
        if entry_type:
            all_entries = [e for e in all_entries if e.type == entry_type]
        
        # Busca simples por palavras-chave
        query_lower = query.lower()
        relevant_entries = []
        
        for entry in all_entries:
            if query_lower in entry.content.lower():
                relevant_entries.append(entry)
        
        # Ordenar por timestamp (mais recente primeiro)
        relevant_entries.sort(key=lambda x: x.timestamp, reverse=True)
        
        return relevant_entries[:10]  # Retornar até 10 entradas mais relevantes
    
    def get_conversation_history(self, count: int = 20) -> str:
        """Recupera o histórico de conversação formatado"""
        conversation_entries = self.get_recent_entries(count, "conversation")
        
        history = []
        for entry in conversation_entries:
            role = entry.metadata.get("role", "user")
            history.append(f"{role}: {entry.content}")
        
        return "\n".join(history)
    
    def clear_short_term_memory(self) -> None:
        """Limpa a memória de curto prazo"""
        # Mover tudo para memória de longo prazo antes de limpar
        self.long_term_memory.extend(self.short_term_memory)
        self.short_term_memory.clear()
    
    def save_long_term_memory(self) -> None:
        """Salva a memória de longo prazo em arquivo"""
        memory_file = os.path.join(self.persist_path, "long_term_memory.json")
        
        # Converter para formato serializável
        memory_data = []
        for entry in self.long_term_memory:
            memory_data.append({
                "timestamp": entry.timestamp.isoformat(),
                "type": entry.type,
                "content": entry.content,
                "metadata": entry.metadata
            })
        
        with open(memory_file, "w", encoding="utf-8") as f:
            json.dump(memory_data, f, ensure_ascii=False, indent=2)
    
    def _load_long_term_memory(self) -> None:
        """Carrega a memória de longo prazo do arquivo"""
        memory_file = os.path.join(self.persist_path, "long_term_memory.json")
        
        if not os.path.exists(memory_file):
            return
        
        try:
            with open(memory_file, "r", encoding="utf-8") as f:
                memory_data = json.load(f)
            
            for entry_data in memory_data:
                entry = MemoryEntry(
                    timestamp=datetime.fromisoformat(entry_data["timestamp"]),
                    type=entry_data["type"],
                    content=entry_data["content"],
                    metadata=entry_data.get("metadata", {})
                )
                self.long_term_memory.append(entry)
                
        except Exception as e:
            print(f"Erro ao carregar memória de longo prazo: {e}")
    
    def get_memory_summary(self) -> Dict[str, Any]:
        """Retorna um resumo do estado da memória"""
        return {
            "short_term_entries": len(self.short_term_memory),
            "long_term_entries": len(self.long_term_memory),
            "total_entries": len(self.short_term_memory) + len(self.long_term_memory),
            "recent_activity": [
                {
                    "type": entry.type,
                    "timestamp": entry.timestamp.isoformat(),
                    "content_preview": entry.content[:100] + "..." if len(entry.content) > 100 else entry.content
                }
                for entry in self.get_recent_entries(5)
            ]
        }

