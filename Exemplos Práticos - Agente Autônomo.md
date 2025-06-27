# Exemplos Práticos - Agente Autônomo

## Exemplos de Uso via Interface Web

### 1. Análise de Sistema
**Comando:** "Analise o estado atual do sistema e me forneça um relatório detalhado"

**O que o agente fará:**
- Obter informações de CPU, memória e disco
- Listar processos principais
- Gerar resumo de performance
- Apresentar dados em formato legível

### 2. Manipulação de Arquivos
**Comando:** "Crie um arquivo de log com timestamp atual e adicione uma entrada de teste"

**O que o agente fará:**
- Criar arquivo com nome baseado em timestamp
- Adicionar entrada de log formatada
- Calcular hash do arquivo
- Confirmar criação bem-sucedida

### 3. Backup Automatizado
**Comando:** "Faça backup de todos os arquivos .py do diretório atual em um arquivo ZIP"

**O que o agente fará:**
- Buscar todos os arquivos Python
- Criar arquivo ZIP com timestamp
- Verificar integridade do backup
- Reportar estatísticas do backup

## Exemplos de Uso via API REST

### 1. Monitoramento de Sistema
```bash
# Obter performance do sistema
curl -X POST http://localhost:5001/api/agent/execute/tool \
  -H "Content-Type: application/json" \
  -d '{
    "tool_name": "get_system_performance_summary",
    "parameters": {}
  }'
```

### 2. Criar e Editar Arquivo
```bash
# Criar arquivo
curl -X POST http://localhost:5001/api/agent/execute/tool \
  -H "Content-Type: application/json" \
  -d '{
    "tool_name": "create_file_with_content",
    "parameters": {
      "file_path": "exemplo.txt",
      "content": "Conteúdo inicial do arquivo"
    }
  }'

# Editar arquivo (adicionar linha)
curl -X POST http://localhost:5001/api/agent/execute/tool \
  -H "Content-Type: application/json" \
  -d '{
    "tool_name": "edit_file_content",
    "parameters": {
      "file_path": "exemplo.txt",
      "operation": "append",
      "content": "\nLinha adicionada via API"
    }
  }'
```

### 3. Busca em Arquivos
```bash
# Buscar padrão em arquivos
curl -X POST http://localhost:5001/api/agent/execute/tool \
  -H "Content-Type: application/json" \
  -d '{
    "tool_name": "search_in_files",
    "parameters": {
      "search_pattern": "import",
      "directory": ".",
      "file_extensions": [".py"]
    }
  }'
```

## Exemplos de Uso via Python

### 1. Script de Automação Básica
```python
from agent import AutonomousAgent

# Inicializar agente
agent = AutonomousAgent()

# Criar relatório de sistema
response = agent.process_request(
    "Crie um relatório de sistema com informações de CPU, memória e disco, "
    "salve em um arquivo chamado relatorio_sistema.txt"
)
print(response)

# Verificar se arquivo foi criado
status = agent.tool_manager.execute_tool("get_file_info", {
    "file_path": "relatorio_sistema.txt"
})
print(f"Arquivo criado: {status.success}")
```

### 2. Monitoramento Contínuo
```python
import time
from agent import AutonomousAgent

agent = AutonomousAgent()

# Monitorar sistema por 5 minutos
for i in range(5):
    # Obter performance
    perf = agent.tool_manager.execute_tool("get_system_performance_summary", {})
    
    if perf.success:
        data = perf.result["performance_summary"]
        cpu_usage = data["cpu"]["usage_percent"]
        memory_usage = data["memory"]["usage_percent"]
        
        print(f"Minuto {i+1}: CPU {cpu_usage:.1f}%, Memória {memory_usage:.1f}%")
        
        # Alerta se uso alto
        if cpu_usage > 80 or memory_usage > 80:
            agent.tool_manager.execute_tool("send_warning_message", {
                "content": f"Uso alto detectado! CPU: {cpu_usage:.1f}%, Memória: {memory_usage:.1f}%"
            })
    
    time.sleep(60)  # Aguardar 1 minuto
```

### 3. Processamento de Arquivos em Lote
```python
import os
from agent import AutonomousAgent

agent = AutonomousAgent()

# Processar todos os arquivos .txt no diretório
txt_files = [f for f in os.listdir('.') if f.endswith('.txt')]

for file in txt_files:
    # Obter metadados
    metadata = agent.tool_manager.execute_tool("get_file_metadata", {
        "file_path": file
    })
    
    if metadata.success:
        info = metadata.result["metadata"]
        print(f"Arquivo: {file}")
        print(f"  Tamanho: {info['size']} bytes")
        print(f"  Modificado: {info['modified']}")
        
        # Calcular hash
        hash_result = agent.tool_manager.execute_tool("calculate_file_hash", {
            "file_path": file
        })
        
        if hash_result.success:
            print(f"  Hash SHA256: {hash_result.result['hash']}")
        
        print()
```

## Cenários de Uso Empresarial

### 1. Automação de DevOps
```python
# Script para verificar saúde de aplicação
def check_application_health():
    agent = AutonomousAgent()
    
    # Verificar processos da aplicação
    processes = agent.tool_manager.execute_tool("get_process_list", {
        "limit": 50,
        "sort_by": "memory_percent"
    })
    
    # Verificar uso de disco
    disk_info = agent.tool_manager.execute_tool("get_disk_info", {})
    
    # Gerar relatório
    report = f"""
    Relatório de Saúde da Aplicação
    ==============================
    
    Processos ativos: {len(processes.result['process_summary']['top_processes'])}
    Uso de disco: {disk_info.result['disk_info']['total_disk_usage']}
    
    Recomendações:
    - Monitorar processos com alto uso de memória
    - Verificar espaço em disco disponível
    """
    
    # Salvar relatório
    agent.tool_manager.execute_tool("write_file", {
        "file_path": f"health_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
        "content": report
    })
```

### 2. Backup Automatizado
```python
def automated_backup():
    agent = AutonomousAgent()
    
    # Criar backup de arquivos importantes
    important_dirs = ["/etc", "/home/user/documents", "/var/log"]
    
    for directory in important_dirs:
        if os.path.exists(directory):
            backup_name = f"backup_{os.path.basename(directory)}_{datetime.now().strftime('%Y%m%d')}.tar.gz"
            
            # Criar arquivo compactado
            result = agent.tool_manager.execute_tool("create_archive", {
                "archive_path": backup_name,
                "source_paths": [directory],
                "archive_type": "tar.gz"
            })
            
            if result.success:
                print(f"Backup criado: {backup_name}")
                
                # Calcular hash para verificação
                hash_result = agent.tool_manager.execute_tool("calculate_file_hash", {
                    "file_path": backup_name
                })
                
                if hash_result.success:
                    print(f"Hash de verificação: {hash_result.result['hash']}")
```

### 3. Monitoramento de Segurança
```python
def security_monitoring():
    agent = AutonomousAgent()
    
    # Verificar processos suspeitos
    processes = agent.tool_manager.execute_tool("get_process_list", {
        "limit": 100
    })
    
    suspicious_processes = []
    for process in processes.result['process_summary']['top_processes']:
        # Verificar processos com alto uso de CPU
        if process.get('cpu_percent', 0) > 90:
            suspicious_processes.append(process)
    
    # Verificar conexões de rede
    network_info = agent.tool_manager.execute_tool("get_network_info", {})
    
    # Gerar alerta se necessário
    if suspicious_processes:
        alert_message = f"Processos suspeitos detectados: {len(suspicious_processes)}"
        agent.tool_manager.execute_tool("send_warning_message", {
            "content": alert_message
        })
    
    # Log de auditoria
    audit_log = {
        "timestamp": datetime.now().isoformat(),
        "suspicious_processes": len(suspicious_processes),
        "network_connections": len(network_info.result.get('network_info', {}).get('connections', []))
    }
    
    agent.tool_manager.execute_tool("write_file", {
        "file_path": "security_audit.log",
        "content": json.dumps(audit_log) + "\n"
    })
```

## Integração com Outros Sistemas

### 1. Webhook para Notificações
```python
import requests
from agent import AutonomousAgent

def send_webhook_notification(message, webhook_url):
    agent = AutonomousAgent()
    
    # Obter informações do sistema
    system_info = agent.tool_manager.execute_tool("get_system_performance_summary", {})
    
    payload = {
        "text": message,
        "system_status": system_info.result if system_info.success else "Erro ao obter status"
    }
    
    # Enviar webhook
    response = requests.post(webhook_url, json=payload)
    
    # Log do resultado
    agent.tool_manager.execute_tool("write_file", {
        "file_path": "webhook.log",
        "content": f"{datetime.now()}: Webhook enviado - Status: {response.status_code}\n"
    })
```

### 2. Integração com Banco de Dados
```python
import sqlite3
from agent import AutonomousAgent

def log_system_metrics():
    agent = AutonomousAgent()
    
    # Obter métricas do sistema
    cpu_info = agent.tool_manager.execute_tool("get_cpu_info", {})
    memory_info = agent.tool_manager.execute_tool("get_memory_info", {})
    
    # Conectar ao banco de dados
    conn = sqlite3.connect('system_metrics.db')
    cursor = conn.cursor()
    
    # Criar tabela se não existir
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS metrics (
            timestamp TEXT,
            cpu_percent REAL,
            memory_percent REAL,
            memory_available INTEGER
        )
    ''')
    
    # Inserir dados
    if cpu_info.success and memory_info.success:
        cursor.execute('''
            INSERT INTO metrics VALUES (?, ?, ?, ?)
        ''', (
            datetime.now().isoformat(),
            cpu_info.result['cpu_info']['cpu_percent'],
            memory_info.result['memory_info']['virtual_memory']['percent'],
            memory_info.result['memory_info']['virtual_memory']['available']
        ))
    
    conn.commit()
    conn.close()
```

## Dicas e Melhores Práticas

### 1. Tratamento de Erros
```python
def safe_agent_operation():
    agent = AutonomousAgent()
    
    try:
        result = agent.tool_manager.execute_tool("some_tool", {})
        
        if result.success:
            print("Operação bem-sucedida")
            return result.result
        else:
            print(f"Erro na operação: {result.error}")
            return None
            
    except Exception as e:
        print(f"Exceção capturada: {e}")
        return None
```

### 2. Logging Estruturado
```python
import logging
from agent import AutonomousAgent

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('agent.log'),
        logging.StreamHandler()
    ]
)

def logged_operation():
    agent = AutonomousAgent()
    
    logging.info("Iniciando operação do agente")
    
    result = agent.process_request("Operação de exemplo")
    
    if result:
        logging.info("Operação concluída com sucesso")
    else:
        logging.error("Falha na operação")
    
    return result
```

### 3. Configuração Personalizada
```python
import os
from agent import AutonomousAgent

# Configurar workspace personalizado
custom_workspace = "/tmp/custom_agent_workspace"
os.makedirs(custom_workspace, exist_ok=True)

# Inicializar agente com workspace personalizado
agent = AutonomousAgent(workspace_dir=custom_workspace)

# Verificar configuração
status = agent.get_status()
print(f"Workspace: {status.get('workspace_dir', 'Padrão')}")
```

Estes exemplos demonstram a versatilidade e poder do Agente Autônomo em diferentes cenários de uso, desde automação simples até integração empresarial complexa.

