"""
Gerenciador de Ferramentas do Agente
"""
import inspect
import json
from typing import Dict, Any, List, Callable, Optional
from pydantic import BaseModel, Field
from datetime import datetime


class ToolDefinition(BaseModel):
    """Definição de uma ferramenta"""
    name: str
    description: str
    parameters: Dict[str, Any]
    function: Optional[Callable] = Field(exclude=True)
    module: Optional[str] = None
    category: str = "general"


class ToolResult(BaseModel):
    """Resultado da execução de uma ferramenta"""
    success: bool
    result: Any = None
    error: Optional[str] = None
    execution_time: float = 0.0
    timestamp: datetime = Field(default_factory=datetime.now)


class ToolManager:
    """Gerenciador de ferramentas do agente"""
    
    def __init__(self):
        self.tools: Dict[str, ToolDefinition] = {}
        self.execution_history: List[Dict[str, Any]] = []
        self.max_history_size = 1000
    
    def register_tool(
        self,
        name: str,
        function: Callable,
        description: str,
        category: str = "general",
        module: Optional[str] = None
    ) -> None:
        """Registra uma nova ferramenta"""
        
        # Extrair parâmetros da função
        sig = inspect.signature(function)
        parameters = {
            "type": "object",
            "properties": {},
            "required": []
        }
        
        for param_name, param in sig.parameters.items():
            param_info = {
                "type": self._get_param_type(param.annotation),
                "description": f"Parâmetro {param_name}"
            }
            
            parameters["properties"][param_name] = param_info
            
            # Se não tem valor padrão, é obrigatório
            if param.default == inspect.Parameter.empty:
                parameters["required"].append(param_name)
        
        tool_def = ToolDefinition(
            name=name,
            description=description,
            parameters=parameters,
            function=function,
            module=module,
            category=category
        )
        
        self.tools[name] = tool_def
        print(f"Ferramenta '{name}' registrada com sucesso")
    
    def _get_param_type(self, annotation) -> str:
        """Converte anotação de tipo Python para tipo JSON Schema"""
        if annotation == str or annotation == "str":
            return "string"
        elif annotation == int or annotation == "int":
            return "integer"
        elif annotation == float or annotation == "float":
            return "number"
        elif annotation == bool or annotation == "bool":
            return "boolean"
        elif annotation == list or annotation == "list":
            return "array"
        elif annotation == dict or annotation == "dict":
            return "object"
        else:
            return "string"  # Padrão
    
    def get_tool_definitions(self) -> List[Dict[str, Any]]:
        """Retorna as definições de todas as ferramentas em formato OpenAI"""
        definitions = []
        
        for tool in self.tools.values():
            definition = {
                "type": "function",
                "function": {
                    "name": tool.name,
                    "description": tool.description,
                    "parameters": tool.parameters
                }
            }
            definitions.append(definition)
        
        return definitions
    
    def get_tool_by_name(self, name: str) -> Optional[ToolDefinition]:
        """Recupera uma ferramenta pelo nome"""
        return self.tools.get(name)
    
    def list_tools(self, category: Optional[str] = None) -> List[str]:
        """Lista todas as ferramentas disponíveis"""
        if category:
            return [name for name, tool in self.tools.items() if tool.category == category]
        return list(self.tools.keys())
    
    def execute_tool(self, name: str, parameters: Dict[str, Any]) -> ToolResult:
        """Executa uma ferramenta com os parâmetros fornecidos"""
        start_time = datetime.now()
        
        try:
            tool = self.tools.get(name)
            if not tool:
                return ToolResult(
                    success=False,
                    error=f"Ferramenta '{name}' não encontrada",
                    execution_time=0.0
                )
            
            if not tool.function:
                return ToolResult(
                    success=False,
                    error=f"Função não definida para a ferramenta '{name}'",
                    execution_time=0.0
                )
            
            # Validar parâmetros obrigatórios
            required_params = tool.parameters.get("required", [])
            for param in required_params:
                if param not in parameters:
                    return ToolResult(
                        success=False,
                        error=f"Parâmetro obrigatório '{param}' não fornecido",
                        execution_time=0.0
                    )
            
            # Executar a função
            result = tool.function(**parameters)
            
            execution_time = (datetime.now() - start_time).total_seconds()
            
            # Registrar no histórico
            self._add_to_history(name, parameters, result, True, execution_time)
            
            return ToolResult(
                success=True,
                result=result,
                execution_time=execution_time
            )
            
        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            error_msg = str(e)
            
            # Registrar erro no histórico
            self._add_to_history(name, parameters, None, False, execution_time, error_msg)
            
            return ToolResult(
                success=False,
                error=error_msg,
                execution_time=execution_time
            )
    
    def _add_to_history(
        self,
        tool_name: str,
        parameters: Dict[str, Any],
        result: Any,
        success: bool,
        execution_time: float,
        error: Optional[str] = None
    ) -> None:
        """Adiciona uma execução ao histórico"""
        history_entry = {
            "timestamp": datetime.now().isoformat(),
            "tool_name": tool_name,
            "parameters": parameters,
            "result": str(result) if result is not None else None,
            "success": success,
            "execution_time": execution_time,
            "error": error
        }
        
        self.execution_history.append(history_entry)
        
        # Limitar tamanho do histórico
        if len(self.execution_history) > self.max_history_size:
            self.execution_history.pop(0)
    
    def get_execution_history(self, count: int = 10) -> List[Dict[str, Any]]:
        """Retorna o histórico de execuções"""
        return self.execution_history[-count:] if count > 0 else self.execution_history
    
    def get_tool_statistics(self) -> Dict[str, Any]:
        """Retorna estatísticas de uso das ferramentas"""
        stats = {
            "total_executions": len(self.execution_history),
            "successful_executions": sum(1 for h in self.execution_history if h["success"]),
            "failed_executions": sum(1 for h in self.execution_history if not h["success"]),
            "tools_usage": {},
            "average_execution_time": 0.0
        }
        
        if self.execution_history:
            # Estatísticas por ferramenta
            for entry in self.execution_history:
                tool_name = entry["tool_name"]
                if tool_name not in stats["tools_usage"]:
                    stats["tools_usage"][tool_name] = {
                        "count": 0,
                        "success_rate": 0.0,
                        "avg_execution_time": 0.0
                    }
                stats["tools_usage"][tool_name]["count"] += 1
            
            # Calcular taxa de sucesso e tempo médio por ferramenta
            for tool_name in stats["tools_usage"]:
                tool_entries = [e for e in self.execution_history if e["tool_name"] == tool_name]
                successful = sum(1 for e in tool_entries if e["success"])
                stats["tools_usage"][tool_name]["success_rate"] = successful / len(tool_entries)
                stats["tools_usage"][tool_name]["avg_execution_time"] = sum(e["execution_time"] for e in tool_entries) / len(tool_entries)
            
            # Tempo médio geral
            stats["average_execution_time"] = sum(e["execution_time"] for e in self.execution_history) / len(self.execution_history)
        
        return stats
    
    def clear_history(self) -> None:
        """Limpa o histórico de execuções"""
        self.execution_history.clear()
    
    def export_tools_schema(self) -> str:
        """Exporta o schema de todas as ferramentas em JSON"""
        schema = {
            "tools": []
        }
        
        for tool in self.tools.values():
            tool_schema = {
                "name": tool.name,
                "description": tool.description,
                "parameters": tool.parameters,
                "category": tool.category,
                "module": tool.module
            }
            schema["tools"].append(tool_schema)
        
        return json.dumps(schema, indent=2, ensure_ascii=False)

