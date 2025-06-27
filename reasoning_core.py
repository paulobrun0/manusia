"""
Núcleo de Raciocínio do Agente Autônomo
"""
import json
import re
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime

from .memory import Memory
from .tool_manager import ToolManager, ToolResult
from .llm_provider import llm_provider
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.settings import settings


class ReasoningCore:
    """Núcleo de raciocínio do agente"""
    
    def __init__(self, memory: Memory, tool_manager: ToolManager):
        self.memory = memory
        self.tool_manager = tool_manager
        self.llm = llm_provider
        self.max_iterations = 10
        self.current_task = None
        self.task_history = []
        
        print(f"Núcleo de Raciocínio inicializado com provedor: {self.llm.provider}")
        
        # Sistema de prompts
        self.system_prompt = self._get_system_prompt()
    
    def _get_system_prompt(self) -> str:
        """Retorna o prompt do sistema"""
        return """Você é um agente autônomo inteligente capaz de executar tarefas complexas.

SUAS CAPACIDADES:
- Raciocinar sobre problemas complexos
- Planejar sequências de ações
- Usar ferramentas disponíveis para executar tarefas
- Lembrar de conversas e ações anteriores
- Aprender com experiências passadas

PROCESSO DE TRABALHO:
1. Analise a requisição do usuário
2. Consulte sua memória para contexto relevante
3. Planeje as ações necessárias
4. Execute as ferramentas apropriadas
5. Avalie os resultados e ajuste o plano se necessário
6. Comunique o progresso e resultados ao usuário

REGRAS IMPORTANTES:
- Sempre explique seu raciocínio
- Use as ferramentas disponíveis quando necessário
- Mantenha o usuário informado sobre o progresso
- Se encontrar erros, tente soluções alternativas
- Seja preciso e detalhado em suas respostas

FERRAMENTAS DISPONÍVEIS:
{tools}

Para usar uma ferramenta, responda no formato:
```json
{
  "action": "nome_da_ferramenta",
  "parameters": {
    "parametro1": "valor1",
    "parametro2": "valor2"
  },
  "reasoning": "Explicação do por que usar esta ferramenta"
}
```

Se não precisar usar ferramentas, responda normalmente."""
    
    def process_request(self, user_input: str) -> str:
        """Processa uma requisição do usuário"""
        try:
            # Registrar entrada do usuário na memória
            self.memory.add_entry("conversation", user_input, {"role": "user"})
            
            # Iniciar nova tarefa
            self.current_task = {
                "id": datetime.now().isoformat(),
                "input": user_input,
                "start_time": datetime.now(),
                "iterations": 0,
                "actions": [],
                "status": "in_progress"
            }
            
            # Processar com loop de raciocínio
            response = self._reasoning_loop(user_input)
            
            # Finalizar tarefa
            self.current_task["status"] = "completed"
            self.current_task["end_time"] = datetime.now()
            self.current_task["response"] = response
            self.task_history.append(self.current_task)
            
            # Registrar resposta na memória
            self.memory.add_entry("conversation", response, {"role": "assistant"})
            
            return response
            
        except Exception as e:
            error_msg = f"Erro no processamento: {str(e)}"
            self.memory.add_entry("error", error_msg)
            return f"Desculpe, ocorreu um erro: {error_msg}"
    
    def _reasoning_loop(self, user_input: str) -> str:
        """Loop principal de raciocínio"""
        if not self.llm.client:
            return self._simulate_response(user_input)
        
        # Preparar contexto
        context = self._prepare_context(user_input)
        
        # Loop de raciocínio
        for iteration in range(self.max_iterations):
            self.current_task["iterations"] = iteration + 1
            
            try:
                # Preparar prompt completo
                full_prompt = f"{self.system_prompt.format(tools=self._format_tools_for_prompt())}\n\n{context}"
                
                # Gerar resposta do LLM
                response_content = self.llm.generate_response(full_prompt)
                
                # Verificar se é uma ação ou resposta final
                action_match = self._extract_action(response_content)
                
                if action_match:
                    # Executar ação
                    action_result = self._execute_action(action_match)
                    
                    # Adicionar resultado ao contexto
                    context += f"\n\nResultado da ação: {action_result}"
                    
                    # Se a ação foi bem-sucedida e parece ser a final, continuar
                    if action_result.get("success") and iteration < self.max_iterations - 1:
                        continue
                    else:
                        # Gerar resposta final
                        final_prompt = f"Com base nas ações executadas, forneça uma resposta final ao usuário.\n\n{context}"
                        final_response = self.llm.generate_response(final_prompt)
                        return final_response
                else:
                    # Resposta final sem ações
                    return response_content
                    
            except Exception as e:
                self.memory.add_entry("error", f"Erro na iteração {iteration}: {str(e)}")
                if iteration == 0:
                    return f"Erro no processamento: {str(e)}"
                else:
                    return "Ocorreu um erro durante o processamento, mas consegui executar algumas ações."
        
        return "Processo concluído após múltiplas iterações."
    
    def _prepare_context(self, user_input: str) -> str:
        """Prepara o contexto para o LLM"""
        context_parts = []
        
        # Entrada atual do usuário
        context_parts.append(f"Requisição do usuário: {user_input}")
        
        # Histórico de conversação recente
        conversation_history = self.memory.get_conversation_history(10)
        if conversation_history:
            context_parts.append(f"\nHistórico recente:\n{conversation_history}")
        
        # Memória relevante
        relevant_memories = self.memory.search_memory(user_input)
        if relevant_memories:
            memory_context = "\n".join([
                f"- {mem.type}: {mem.content[:200]}..." if len(mem.content) > 200 else f"- {mem.type}: {mem.content}"
                for mem in relevant_memories[:3]
            ])
            context_parts.append(f"\nMemórias relevantes:\n{memory_context}")
        
        return "\n".join(context_parts)
    
    def _format_tools_for_prompt(self) -> str:
        """Formata as ferramentas para o prompt"""
        tools = self.tool_manager.get_tool_definitions()
        
        if not tools:
            return "Nenhuma ferramenta disponível."
        
        tool_descriptions = []
        for tool in tools:
            func_info = tool["function"]
            tool_descriptions.append(
                f"- {func_info['name']}: {func_info['description']}"
            )
        
        return "\n".join(tool_descriptions)
    
    def _extract_action(self, response: str) -> Optional[Dict[str, Any]]:
        """Extrai ação do formato JSON da resposta"""
        try:
            # Procurar por blocos JSON
            json_pattern = r'```json\s*(\{.*?\})\s*```'
            matches = re.findall(json_pattern, response, re.DOTALL)
            
            if matches:
                action_data = json.loads(matches[0])
                if "action" in action_data and "parameters" in action_data:
                    return action_data
            
            return None
            
        except Exception as e:
            self.memory.add_entry("error", f"Erro ao extrair ação: {str(e)}")
            return None
    
    def _execute_action(self, action_data: Dict[str, Any]) -> Dict[str, Any]:
        """Executa uma ação usando o tool manager"""
        action_name = action_data.get("action")
        parameters = action_data.get("parameters", {})
        reasoning = action_data.get("reasoning", "")
        
        # Registrar na memória
        self.memory.add_entry(
            "action",
            f"Executando {action_name} com parâmetros: {parameters}",
            {"reasoning": reasoning}
        )
        
        # Registrar na tarefa atual
        if self.current_task:
            self.current_task["actions"].append({
                "name": action_name,
                "parameters": parameters,
                "reasoning": reasoning,
                "timestamp": datetime.now().isoformat()
            })
        
        # Executar ferramenta
        result = self.tool_manager.execute_tool(action_name, parameters)
        
        # Registrar resultado
        self.memory.add_entry(
            "result",
            f"Resultado de {action_name}: {'Sucesso' if result.success else 'Erro'} - {result.result or result.error}"
        )
        
        return {
            "success": result.success,
            "result": result.result,
            "error": result.error,
            "execution_time": result.execution_time
        }
    
    def _simulate_response(self, user_input: str) -> str:
        """Simula uma resposta quando o LLM não está disponível"""
        self.memory.add_entry("simulation", f"Simulando resposta para: {user_input}")
        
        # Análise simples baseada em palavras-chave
        user_lower = user_input.lower()
        
        if any(word in user_lower for word in ["arquivo", "criar", "escrever", "salvar"]):
            return "Entendi que você quer trabalhar com arquivos. No modo simulação, eu registraria essa ação na memória e executaria as ferramentas apropriadas de manipulação de arquivos."
        
        elif any(word in user_lower for word in ["navegar", "site", "web", "browser"]):
            return "Você quer navegar na web. No modo simulação, eu usaria as ferramentas de navegação para acessar sites e extrair informações."
        
        elif any(word in user_lower for word in ["pesquisar", "buscar", "procurar"]):
            return "Você quer fazer uma pesquisa. No modo simulação, eu usaria as ferramentas de busca para encontrar informações relevantes."
        
        else:
            return f"Recebi sua requisição: '{user_input}'. No modo simulação, eu analisaria a tarefa, planejaria as ações necessárias e executaria as ferramentas apropriadas para completar sua solicitação."
    
    def get_current_task_status(self) -> Optional[Dict[str, Any]]:
        """Retorna o status da tarefa atual"""
        return self.current_task
    
    def get_task_history(self, count: int = 10) -> List[Dict[str, Any]]:
        """Retorna o histórico de tarefas"""
        return self.task_history[-count:] if count > 0 else self.task_history
    
    def clear_task_history(self) -> None:
        """Limpa o histórico de tarefas"""
        self.task_history.clear()
    
    def get_reasoning_statistics(self) -> Dict[str, Any]:
        """Retorna estatísticas do núcleo de raciocínio"""
        return {
            "total_tasks": len(self.task_history),
            "completed_tasks": sum(1 for task in self.task_history if task.get("status") == "completed"),
            "current_task_id": self.current_task.get("id") if self.current_task else None,
            "average_iterations": sum(task.get("iterations", 0) for task in self.task_history) / len(self.task_history) if self.task_history else 0,
            "llm_provider": self.llm.get_provider_info()
        }

