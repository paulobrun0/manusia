"""
Módulo de Mensagens - Comunicação com o usuário
"""
from typing import Dict, Any, List, Optional
from datetime import datetime
from enum import Enum


class MessageType(Enum):
    """Tipos de mensagem"""
    INFO = "info"
    SUCCESS = "success"
    WARNING = "warning"
    ERROR = "error"
    QUESTION = "question"
    PROGRESS = "progress"


class MessagingModule:
    """Módulo para comunicação com o usuário"""
    
    def __init__(self):
        self.message_history = []
        self.pending_questions = []
        self.max_history_size = 1000
    
    def send_message(
        self,
        content: str,
        message_type: MessageType = MessageType.INFO,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Envia uma mensagem ao usuário"""
        try:
            if metadata is None:
                metadata = {}
            
            message = {
                "id": len(self.message_history) + 1,
                "timestamp": datetime.now().isoformat(),
                "type": message_type.value,
                "content": content,
                "metadata": metadata,
                "delivered": True
            }
            
            # Adicionar ao histórico
            self.message_history.append(message)
            
            # Limitar tamanho do histórico
            if len(self.message_history) > self.max_history_size:
                self.message_history.pop(0)
            
            # Simular entrega da mensagem (em implementação real, seria enviada para a interface)
            print(f"[{message_type.value.upper()}] {content}")
            
            return {
                "success": True,
                "message_id": message["id"],
                "delivered": True,
                "timestamp": message["timestamp"]
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "content": content
            }
    
    def send_info(self, content: str, metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Envia uma mensagem informativa"""
        return self.send_message(content, MessageType.INFO, metadata)
    
    def send_success(self, content: str, metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Envia uma mensagem de sucesso"""
        return self.send_message(content, MessageType.SUCCESS, metadata)
    
    def send_warning(self, content: str, metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Envia uma mensagem de aviso"""
        return self.send_message(content, MessageType.WARNING, metadata)
    
    def send_error(self, content: str, metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Envia uma mensagem de erro"""
        return self.send_message(content, MessageType.ERROR, metadata)
    
    def ask_question(
        self,
        question: str,
        options: Optional[List[str]] = None,
        timeout: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Faz uma pergunta ao usuário"""
        try:
            if metadata is None:
                metadata = {}
            
            question_data = {
                "id": len(self.pending_questions) + 1,
                "timestamp": datetime.now().isoformat(),
                "question": question,
                "options": options,
                "timeout": timeout,
                "metadata": metadata,
                "status": "pending",
                "answer": None
            }
            
            self.pending_questions.append(question_data)
            
            # Simular pergunta (em implementação real, seria enviada para a interface)
            print(f"[PERGUNTA] {question}")
            if options:
                for i, option in enumerate(options, 1):
                    print(f"  {i}. {option}")
            
            # Para simulação, retornar uma resposta padrão
            # Em implementação real, aguardaria resposta do usuário
            default_answer = "Sim" if not options else options[0]
            question_data["answer"] = default_answer
            question_data["status"] = "answered"
            question_data["answered_at"] = datetime.now().isoformat()
            
            print(f"[RESPOSTA SIMULADA] {default_answer}")
            
            return {
                "success": True,
                "question_id": question_data["id"],
                "answer": default_answer,
                "simulated": True
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "question": question
            }
    
    def send_progress_update(
        self,
        task_name: str,
        progress: float,
        status: str,
        details: Optional[str] = None
    ) -> Dict[str, Any]:
        """Envia uma atualização de progresso"""
        progress_data = {
            "task_name": task_name,
            "progress": min(100.0, max(0.0, progress)),  # Garantir que está entre 0 e 100
            "status": status,
            "details": details
        }
        
        content = f"Progresso da tarefa '{task_name}': {progress:.1f}% - {status}"
        if details:
            content += f" ({details})"
        
        return self.send_message(content, MessageType.PROGRESS, progress_data)
    
    def send_file_attachment(
        self,
        file_path: str,
        description: Optional[str] = None,
        file_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """Envia um arquivo como anexo"""
        try:
            import os
            
            if not os.path.exists(file_path):
                return {
                    "success": False,
                    "error": f"Arquivo não encontrado: {file_path}",
                    "file_path": file_path
                }
            
            file_info = {
                "file_path": file_path,
                "file_name": os.path.basename(file_path),
                "file_size": os.path.getsize(file_path),
                "file_type": file_type or "unknown",
                "description": description
            }
            
            content = f"Arquivo anexado: {file_info['file_name']}"
            if description:
                content += f" - {description}"
            
            return self.send_message(content, MessageType.INFO, {"attachment": file_info})
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "file_path": file_path
            }
    
    def get_message_history(self, count: int = 20, message_type: Optional[MessageType] = None) -> Dict[str, Any]:
        """Retorna o histórico de mensagens"""
        try:
            messages = self.message_history.copy()
            
            if message_type:
                messages = [msg for msg in messages if msg["type"] == message_type.value]
            
            if count > 0:
                messages = messages[-count:]
            
            return {
                "success": True,
                "messages": messages,
                "total_messages": len(self.message_history),
                "filtered_count": len(messages)
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_pending_questions(self) -> Dict[str, Any]:
        """Retorna perguntas pendentes"""
        try:
            pending = [q for q in self.pending_questions if q["status"] == "pending"]
            
            return {
                "success": True,
                "pending_questions": pending,
                "count": len(pending)
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def answer_question(self, question_id: int, answer: str) -> Dict[str, Any]:
        """Responde a uma pergunta pendente"""
        try:
            question = None
            for q in self.pending_questions:
                if q["id"] == question_id:
                    question = q
                    break
            
            if not question:
                return {
                    "success": False,
                    "error": f"Pergunta com ID {question_id} não encontrada"
                }
            
            if question["status"] != "pending":
                return {
                    "success": False,
                    "error": f"Pergunta já foi respondida: {question['answer']}"
                }
            
            question["answer"] = answer
            question["status"] = "answered"
            question["answered_at"] = datetime.now().isoformat()
            
            return {
                "success": True,
                "question_id": question_id,
                "answer": answer,
                "answered_at": question["answered_at"]
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "question_id": question_id
            }
    
    def clear_message_history(self) -> Dict[str, Any]:
        """Limpa o histórico de mensagens"""
        try:
            cleared_count = len(self.message_history)
            self.message_history.clear()
            
            return {
                "success": True,
                "cleared_messages": cleared_count
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_messaging_statistics(self) -> Dict[str, Any]:
        """Retorna estatísticas do sistema de mensagens"""
        try:
            stats = {
                "total_messages": len(self.message_history),
                "pending_questions": len([q for q in self.pending_questions if q["status"] == "pending"]),
                "answered_questions": len([q for q in self.pending_questions if q["status"] == "answered"]),
                "message_types": {}
            }
            
            # Contar mensagens por tipo
            for message in self.message_history:
                msg_type = message["type"]
                stats["message_types"][msg_type] = stats["message_types"].get(msg_type, 0) + 1
            
            return {
                "success": True,
                "statistics": stats
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

