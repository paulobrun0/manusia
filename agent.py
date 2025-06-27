"""
Rotas para integração com o Agente Autônomo
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))

from flask import Blueprint, request, jsonify
from datetime import datetime
import threading
import time

# Importar o agente autônomo
try:
    from agent import AutonomousAgent
except ImportError:
    # Fallback para modo simulação
    AutonomousAgent = None

agent_bp = Blueprint('agent', __name__)

# Instância global do agente
agent_instance = None
agent_lock = threading.Lock()

def get_agent():
    """Obtém ou cria a instância do agente"""
    global agent_instance
    
    with agent_lock:
        if agent_instance is None and AutonomousAgent is not None:
            try:
                agent_instance = AutonomousAgent()
            except Exception as e:
                print(f"Erro ao inicializar agente: {e}")
                agent_instance = None
    
    return agent_instance

@agent_bp.route('/status', methods=['GET'])
def get_agent_status():
    """Retorna o status do agente"""
    try:
        agent = get_agent()
        
        if agent is None:
            return jsonify({
                "success": False,
                "error": "Agente não disponível",
                "mode": "simulation"
            }), 503
        
        status = agent.get_status()
        return jsonify({
            "success": True,
            "status": status,
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@agent_bp.route('/tools', methods=['GET'])
def get_available_tools():
    """Retorna as ferramentas disponíveis"""
    try:
        agent = get_agent()
        
        if agent is None:
            return jsonify({
                "success": False,
                "error": "Agente não disponível",
                "mode": "simulation"
            }), 503
        
        tools = agent.list_available_tools()
        return jsonify({
            "success": True,
            "tools": tools,
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@agent_bp.route('/chat', methods=['POST'])
def chat_with_agent():
    """Processa uma mensagem de chat com o agente"""
    try:
        data = request.get_json()
        
        if not data or 'message' not in data:
            return jsonify({
                "success": False,
                "error": "Mensagem é obrigatória"
            }), 400
        
        message = data['message'].strip()
        if not message:
            return jsonify({
                "success": False,
                "error": "Mensagem não pode estar vazia"
            }), 400
        
        agent = get_agent()
        
        if agent is None:
            # Modo simulação
            response = f"[SIMULAÇÃO] Recebi sua mensagem: '{message}'. Em modo real, o agente processaria esta requisição usando suas 37 ferramentas disponíveis."
        else:
            # Processar com o agente real
            response = agent.process_request(message)
        
        return jsonify({
            "success": True,
            "message": message,
            "response": response,
            "timestamp": datetime.now().isoformat(),
            "mode": "simulation" if agent is None else "real"
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@agent_bp.route('/memory', methods=['GET'])
def get_memory_summary():
    """Retorna resumo da memória do agente"""
    try:
        agent = get_agent()
        
        if agent is None:
            return jsonify({
                "success": False,
                "error": "Agente não disponível",
                "mode": "simulation"
            }), 503
        
        memory_summary = agent.get_memory_summary()
        return jsonify({
            "success": True,
            "memory": memory_summary,
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@agent_bp.route('/memory/clear', methods=['POST'])
def clear_memory():
    """Limpa a memória do agente"""
    try:
        data = request.get_json() or {}
        memory_type = data.get('type', 'short_term')
        
        agent = get_agent()
        
        if agent is None:
            return jsonify({
                "success": False,
                "error": "Agente não disponível",
                "mode": "simulation"
            }), 503
        
        result = agent.clear_memory(memory_type)
        return jsonify({
            "success": result.get("success", False),
            "result": result,
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@agent_bp.route('/system/performance', methods=['GET'])
def get_system_performance():
    """Retorna informações de performance do sistema"""
    try:
        agent = get_agent()
        
        if agent is None:
            return jsonify({
                "success": False,
                "error": "Agente não disponível",
                "mode": "simulation"
            }), 503
        
        # Usar a ferramenta de monitoramento do sistema
        performance = agent.system_monitor_module.get_system_performance_summary()
        
        return jsonify({
            "success": True,
            "performance": performance,
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@agent_bp.route('/execute/tool', methods=['POST'])
def execute_tool():
    """Executa uma ferramenta específica"""
    try:
        data = request.get_json()
        
        if not data or 'tool_name' not in data:
            return jsonify({
                "success": False,
                "error": "Nome da ferramenta é obrigatório"
            }), 400
        
        tool_name = data['tool_name']
        parameters = data.get('parameters', {})
        
        agent = get_agent()
        
        if agent is None:
            return jsonify({
                "success": False,
                "error": "Agente não disponível",
                "mode": "simulation"
            }), 503
        
        # Executar ferramenta
        result = agent.tool_manager.execute_tool(tool_name, parameters)
        
        return jsonify({
            "success": result.success,
            "tool_name": tool_name,
            "parameters": parameters,
            "result": result.result if result.success else None,
            "error": result.error if not result.success else None,
            "execution_time": result.execution_time,
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@agent_bp.route('/save', methods=['POST'])
def save_agent_state():
    """Salva o estado do agente"""
    try:
        agent = get_agent()
        
        if agent is None:
            return jsonify({
                "success": False,
                "error": "Agente não disponível",
                "mode": "simulation"
            }), 503
        
        result = agent.save_state()
        return jsonify({
            "success": result.get("success", False),
            "result": result,
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@agent_bp.route('/health', methods=['GET'])
def health_check():
    """Verifica a saúde da API"""
    return jsonify({
        "success": True,
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "agent_available": get_agent() is not None
    })

