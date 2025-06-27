# Guia de Instalação Rápida - Agente Autônomo

## Instalação em 5 Minutos

### 1. Pré-requisitos
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install python3.11 python3.11-pip python3.11-venv git curl

# Verificar versão do Python
python3.11 --version
```

### 2. Download e Configuração
```bash
# Baixar o projeto
git clone <repository-url>
cd agente_autonomo

# Instalar dependências
pip3.11 install -r requirements.txt

# Instalar psutil (necessário para monitoramento)
pip3.11 install psutil
```

### 3. Teste Rápido
```bash
# Testar o agente
python3.11 agent.py

# Executar testes (opcional)
python3.11 test_agent.py
```

### 4. Interface Web
```bash
# Navegar para interface web
cd web_interface

# Ativar ambiente virtual
source venv/bin/activate

# Instalar dependências web
pip install flask-cors

# Executar interface web
python src/main.py
```

### 5. Acesso
- **Agente CLI:** Execute `python3.11 agent.py`
- **Interface Web:** Acesse `http://localhost:5001`
- **API REST:** Use `http://localhost:5001/api/agent/`

## Solução de Problemas Comuns

### Erro: ModuleNotFoundError
```bash
pip3.11 install -r requirements.txt
pip3.11 install psutil flask-cors
```

### Erro: Permission Denied
```bash
chmod +x agent.py
sudo chown -R $USER:$USER agente_autonomo/
```

### Porta em Uso
```bash
# Matar processos na porta 5001
sudo lsof -ti:5001 | xargs kill -9

# Ou usar porta diferente editando web_interface/src/main.py
```

### Dependências Selenium (para navegação web)
```bash
# Instalar Chrome/Chromium
sudo apt install chromium-browser

# Instalar ChromeDriver
sudo apt install chromium-chromedriver
```

## Configuração Avançada

### Variáveis de Ambiente
```bash
# Opcional: Para funcionalidades de IA avançadas
export OPENAI_API_KEY="sua_chave_aqui"

# Configurar workspace personalizado
export AGENT_WORKSPACE="/caminho/personalizado"
```

### Configuração de Produção
```bash
# Usar servidor WSGI para produção
pip install gunicorn

# Executar com Gunicorn
cd web_interface
gunicorn -w 4 -b 0.0.0.0:5001 src.main:app
```

## Verificação da Instalação

### Teste Básico
```bash
curl http://localhost:5001/api/agent/health
```

**Resposta esperada:**
```json
{
  "success": true,
  "status": "healthy",
  "agent_available": false
}
```

### Teste do Chat
```bash
curl -X POST http://localhost:5001/api/agent/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Olá!"}'
```

## Próximos Passos

1. **Explore a Interface Web:** Acesse `http://localhost:5001`
2. **Leia a Documentação:** Consulte `README.md`
3. **Execute Testes:** Use `python3.11 test_agent.py`
4. **Experimente a API:** Teste os endpoints REST
5. **Personalize:** Modifique configurações conforme necessário

## Suporte

- **Documentação Completa:** `README.md`
- **Testes:** `test_agent.py`
- **Logs:** Verifique `web_interface/flask.log`
- **Issues:** Reporte problemas no repositório

