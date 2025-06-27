#!/usr/bin/env python3
"""
Script de Teste Abrangente para o Agente Autônomo
"""
import sys
import os
import time
import json
from datetime import datetime

# Adicionar o diretório do agente ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from agent import AutonomousAgent
    AGENT_AVAILABLE = True
except ImportError as e:
    print(f"Aviso: Não foi possível importar o agente: {e}")
    AGENT_AVAILABLE = False


class AgentTester:
    """Classe para testar todas as funcionalidades do agente"""
    
    def __init__(self):
        self.test_results = []
        self.agent = None
        self.start_time = datetime.now()
        
        if AGENT_AVAILABLE:
            try:
                print("Inicializando agente...")
                self.agent = AutonomousAgent()
                print("Agente inicializado com sucesso!")
            except Exception as e:
                print(f"Erro ao inicializar agente: {e}")
                self.agent = None
    
    def log_test(self, test_name: str, success: bool, details: str = "", execution_time: float = 0):
        """Registra o resultado de um teste"""
        result = {
            "test_name": test_name,
            "success": success,
            "details": details,
            "execution_time": execution_time,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        
        status = "✅ PASSOU" if success else "❌ FALHOU"
        print(f"{status} - {test_name} ({execution_time:.2f}s)")
        if details:
            print(f"   Detalhes: {details}")
    
    def test_agent_initialization(self):
        """Testa a inicialização do agente"""
        start_time = time.time()
        
        if self.agent is None:
            self.log_test(
                "Inicialização do Agente",
                False,
                "Agente não pôde ser inicializado",
                time.time() - start_time
            )
            return False
        
        try:
            status = self.agent.get_status()
            tools_count = len(self.agent.tool_manager.tools)
            
            self.log_test(
                "Inicialização do Agente",
                True,
                f"Agente inicializado com {tools_count} ferramentas",
                time.time() - start_time
            )
            return True
            
        except Exception as e:
            self.log_test(
                "Inicialização do Agente",
                False,
                f"Erro ao obter status: {e}",
                time.time() - start_time
            )
            return False
    
    def test_shell_module(self):
        """Testa o módulo de shell"""
        if not self.agent:
            return False
        
        tests = [
            ("execute_command", {"command": "echo 'Hello World'"}),
            ("list_directory", {"directory_path": "."}),
            ("create_directory", {"directory_path": "test_dir"}),
            ("write_file", {"file_path": "test_file.txt", "content": "Test content"}),
            ("read_file", {"file_path": "test_file.txt"}),
            ("get_file_info", {"file_path": "test_file.txt"}),
            ("delete_file_or_directory", {"path": "test_file.txt"}),
            ("delete_file_or_directory", {"path": "test_dir"})
        ]
        
        for tool_name, params in tests:
            start_time = time.time()
            try:
                result = self.agent.tool_manager.execute_tool(tool_name, params)
                self.log_test(
                    f"Shell - {tool_name}",
                    result.success,
                    result.error if not result.success else "Executado com sucesso",
                    time.time() - start_time
                )
            except Exception as e:
                self.log_test(
                    f"Shell - {tool_name}",
                    False,
                    f"Exceção: {e}",
                    time.time() - start_time
                )
    
    def test_file_manager_module(self):
        """Testa o módulo de gerenciamento de arquivos avançado"""
        if not self.agent:
            return False
        
        tests = [
            ("create_file_with_content", {
                "file_path": "advanced_test.txt",
                "content": "Conteúdo de teste avançado\nLinha 2\nLinha 3"
            }),
            ("edit_file_content", {
                "file_path": "advanced_test.txt",
                "operation": "append",
                "content": "\nLinha adicionada"
            }),
            ("search_in_files", {
                "search_pattern": "teste",
                "directory": "."
            }),
            ("get_file_metadata", {"file_path": "advanced_test.txt"}),
            ("calculate_file_hash", {"file_path": "advanced_test.txt"})
        ]
        
        for tool_name, params in tests:
            start_time = time.time()
            try:
                result = self.agent.tool_manager.execute_tool(tool_name, params)
                self.log_test(
                    f"FileManager - {tool_name}",
                    result.success,
                    result.error if not result.success else "Executado com sucesso",
                    time.time() - start_time
                )
            except Exception as e:
                self.log_test(
                    f"FileManager - {tool_name}",
                    False,
                    f"Exceção: {e}",
                    time.time() - start_time
                )
    
    def test_system_monitor_module(self):
        """Testa o módulo de monitoramento de sistema"""
        if not self.agent:
            return False
        
        tests = [
            ("get_system_info", {}),
            ("get_cpu_info", {}),
            ("get_memory_info", {}),
            ("get_disk_info", {}),
            ("get_process_list", {"limit": 5}),
            ("get_system_performance_summary", {})
        ]
        
        for tool_name, params in tests:
            start_time = time.time()
            try:
                result = self.agent.tool_manager.execute_tool(tool_name, params)
                self.log_test(
                    f"SystemMonitor - {tool_name}",
                    result.success,
                    result.error if not result.success else "Executado com sucesso",
                    time.time() - start_time
                )
            except Exception as e:
                self.log_test(
                    f"SystemMonitor - {tool_name}",
                    False,
                    f"Exceção: {e}",
                    time.time() - start_time
                )
    
    def test_messaging_module(self):
        """Testa o módulo de mensagens"""
        if not self.agent:
            return False
        
        tests = [
            ("send_message", {"message": "Teste de mensagem"}),
            ("send_success_message", {"message": "Teste de sucesso"}),
            ("send_warning_message", {"message": "Teste de aviso"}),
            ("send_error_message", {"message": "Teste de erro"}),
            ("send_progress_update", {"message": "Teste de progresso", "progress": 50})
        ]
        
        for tool_name, params in tests:
            start_time = time.time()
            try:
                result = self.agent.tool_manager.execute_tool(tool_name, params)
                self.log_test(
                    f"Messaging - {tool_name}",
                    result.success,
                    result.error if not result.success else "Executado com sucesso",
                    time.time() - start_time
                )
            except Exception as e:
                self.log_test(
                    f"Messaging - {tool_name}",
                    False,
                    f"Exceção: {e}",
                    time.time() - start_time
                )
    
    def test_web_navigation_module(self):
        """Testa o módulo de navegação web (simulação)"""
        if not self.agent:
            return False
        
        # Testes básicos que não requerem navegação real
        tests = [
            ("take_screenshot", {"save_path": "test_screenshot.png"})
        ]
        
        for tool_name, params in tests:
            start_time = time.time()
            try:
                result = self.agent.tool_manager.execute_tool(tool_name, params)
                self.log_test(
                    f"WebNavigation - {tool_name}",
                    result.success,
                    result.error if not result.success else "Executado com sucesso",
                    time.time() - start_time
                )
            except Exception as e:
                self.log_test(
                    f"WebNavigation - {tool_name}",
                    False,
                    f"Exceção: {e}",
                    time.time() - start_time
                )
    
    def test_search_module(self):
        """Testa o módulo de pesquisa"""
        if not self.agent:
            return False
        
        tests = [
            ("get_search_suggestions", {"query": "python programming"})
        ]
        
        for tool_name, params in tests:
            start_time = time.time()
            try:
                result = self.agent.tool_manager.execute_tool(tool_name, params)
                self.log_test(
                    f"Search - {tool_name}",
                    result.success,
                    result.error if not result.success else "Executado com sucesso",
                    time.time() - start_time
                )
            except Exception as e:
                self.log_test(
                    f"Search - {tool_name}",
                    False,
                    f"Exceção: {e}",
                    time.time() - start_time
                )
    
    def test_memory_system(self):
        """Testa o sistema de memória"""
        if not self.agent:
            return False
        
        start_time = time.time()
        try:
            # Testar adição à memória
            self.agent.memory.add_to_short_term("test_key", "test_value")
            
            # Testar recuperação da memória
            value = self.agent.memory.get_from_short_term("test_key")
            
            success = value == "test_value"
            self.log_test(
                "Sistema de Memória",
                success,
                "Memória funcionando corretamente" if success else "Erro na memória",
                time.time() - start_time
            )
            
        except Exception as e:
            self.log_test(
                "Sistema de Memória",
                False,
                f"Exceção: {e}",
                time.time() - start_time
            )
    
    def test_reasoning_core(self):
        """Testa o núcleo de raciocínio"""
        if not self.agent:
            return False
        
        start_time = time.time()
        try:
            # Testar processamento de requisição simples
            response = self.agent.process_request("Teste de raciocínio")
            
            success = isinstance(response, str) and len(response) > 0
            self.log_test(
                "Núcleo de Raciocínio",
                success,
                "Raciocínio funcionando" if success else "Erro no raciocínio",
                time.time() - start_time
            )
            
        except Exception as e:
            self.log_test(
                "Núcleo de Raciocínio",
                False,
                f"Exceção: {e}",
                time.time() - start_time
            )
    
    def test_complex_scenario(self):
        """Testa um cenário complexo integrando múltiplos módulos"""
        if not self.agent:
            return False
        
        start_time = time.time()
        try:
            # Cenário: Criar arquivo, obter info do sistema, e processar
            steps = [
                ("write_file", {"file_path": "scenario_test.txt", "content": "Teste de cenário complexo"}),
                ("get_system_performance_summary", {}),
                ("get_file_metadata", {"file_path": "scenario_test.txt"}),
                ("delete_file_or_directory", {"path": "scenario_test.txt"})
            ]
            
            all_success = True
            for tool_name, params in steps:
                result = self.agent.tool_manager.execute_tool(tool_name, params)
                if not result.success:
                    all_success = False
                    break
            
            self.log_test(
                "Cenário Complexo",
                all_success,
                "Todos os passos executados" if all_success else "Falha em algum passo",
                time.time() - start_time
            )
            
        except Exception as e:
            self.log_test(
                "Cenário Complexo",
                False,
                f"Exceção: {e}",
                time.time() - start_time
            )
    
    def run_all_tests(self):
        """Executa todos os testes"""
        print("=" * 60)
        print("INICIANDO TESTES ABRANGENTES DO AGENTE AUTÔNOMO")
        print("=" * 60)
        
        # Lista de testes a executar
        test_methods = [
            self.test_agent_initialization,
            self.test_shell_module,
            self.test_file_manager_module,
            self.test_system_monitor_module,
            self.test_messaging_module,
            self.test_web_navigation_module,
            self.test_search_module,
            self.test_memory_system,
            self.test_reasoning_core,
            self.test_complex_scenario
        ]
        
        # Executar testes
        for test_method in test_methods:
            print(f"\n--- Executando {test_method.__name__} ---")
            test_method()
        
        # Gerar relatório final
        self.generate_report()
    
    def generate_report(self):
        """Gera relatório final dos testes"""
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests
        
        total_time = (datetime.now() - self.start_time).total_seconds()
        
        print("\n" + "=" * 60)
        print("RELATÓRIO FINAL DOS TESTES")
        print("=" * 60)
        print(f"Total de testes: {total_tests}")
        print(f"Testes aprovados: {passed_tests} ({(passed_tests/total_tests)*100:.1f}%)")
        print(f"Testes falharam: {failed_tests} ({(failed_tests/total_tests)*100:.1f}%)")
        print(f"Tempo total: {total_time:.2f} segundos")
        
        if failed_tests > 0:
            print("\nTESTS QUE FALHARAM:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"  ❌ {result['test_name']}: {result['details']}")
        
        # Salvar relatório em arquivo
        report_data = {
            "summary": {
                "total_tests": total_tests,
                "passed_tests": passed_tests,
                "failed_tests": failed_tests,
                "success_rate": (passed_tests/total_tests)*100,
                "total_time": total_time,
                "timestamp": datetime.now().isoformat()
            },
            "test_results": self.test_results
        }
        
        with open("test_report.json", "w", encoding="utf-8") as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False)
        
        print(f"\nRelatório detalhado salvo em: test_report.json")
        print("=" * 60)


def main():
    """Função principal"""
    tester = AgentTester()
    tester.run_all_tests()


if __name__ == "__main__":
    main()

