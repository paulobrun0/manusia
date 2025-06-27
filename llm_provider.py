"""
Provedor de LLM que suporta OpenAI e Gemini
"""
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from typing import Optional, Dict, Any
from config.settings import settings


class LLMProvider:
    """Provedor de LLM que abstrai OpenAI e Gemini"""
    
    def __init__(self):
        self.provider = settings.llm_provider
        self.client = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Inicializa o cliente baseado no provedor configurado"""
        try:
            if self.provider == "gemini":
                self._initialize_gemini()
            elif self.provider == "openai":
                self._initialize_openai()
            else:
                raise ValueError(f"Provedor LLM não suportado: {self.provider}")
        except Exception as e:
            print(f"Erro ao inicializar provedor LLM {self.provider}: {e}")
            print("Usando modo simulação")
            self.client = None
    
    def _initialize_gemini(self):
        """Inicializa o cliente Gemini"""
        try:
            import google.generativeai as genai
            
            api_key = settings.gemini_api_key or os.getenv("GEMINI_API_KEY")
            if not api_key:
                raise ValueError("Chave da API do Gemini não encontrada")
            
            genai.configure(api_key=api_key)
            self.client = genai.GenerativeModel(settings.get_current_model())
            print(f"Cliente Gemini inicializado com modelo: {settings.get_current_model()}")
            
        except ImportError:
            raise ImportError("Biblioteca google-generativeai não encontrada. Instale com: pip install google-generativeai")
    
    def _initialize_openai(self):
        """Inicializa o cliente OpenAI"""
        try:
            from openai import OpenAI
            
            api_key = settings.openai_api_key or os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise ValueError("Chave da API do OpenAI não encontrada")
            
            self.client = OpenAI(api_key=api_key)
            print(f"Cliente OpenAI inicializado com modelo: {settings.get_current_model()}")
            
        except ImportError:
            raise ImportError("Biblioteca openai não encontrada. Instale com: pip install openai")
    
    def generate_response(self, prompt: str, **kwargs) -> str:
        """Gera uma resposta usando o provedor configurado"""
        if not self.client:
            return f"[SIMULAÇÃO - {self.provider.upper()}] Resposta para: {prompt[:100]}..."
        
        try:
            if self.provider == "gemini":
                return self._generate_gemini_response(prompt, **kwargs)
            elif self.provider == "openai":
                return self._generate_openai_response(prompt, **kwargs)
        except Exception as e:
            print(f"Erro ao gerar resposta: {e}")
            return f"[ERRO] Não foi possível gerar resposta: {e}"
    
    def _generate_gemini_response(self, prompt: str, **kwargs) -> str:
        """Gera resposta usando Gemini"""
        try:
            response = self.client.generate_content(
                prompt,
                generation_config={
                    "temperature": kwargs.get("temperature", settings.temperature),
                    "max_output_tokens": kwargs.get("max_tokens", settings.max_tokens),
                }
            )
            return response.text
        except Exception as e:
            raise Exception(f"Erro na API do Gemini: {e}")
    
    def _generate_openai_response(self, prompt: str, **kwargs) -> str:
        """Gera resposta usando OpenAI"""
        try:
            response = self.client.chat.completions.create(
                model=settings.get_current_model(),
                messages=[{"role": "user", "content": prompt}],
                temperature=kwargs.get("temperature", settings.temperature),
                max_tokens=kwargs.get("max_tokens", settings.max_tokens)
            )
            return response.choices[0].message.content
        except Exception as e:
            raise Exception(f"Erro na API do OpenAI: {e}")
    
    def generate_structured_response(self, prompt: str, schema: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """Gera uma resposta estruturada (JSON)"""
        if not self.client:
            return {"error": "Cliente não disponível", "mode": "simulation"}
        
        try:
            if self.provider == "gemini":
                return self._generate_gemini_structured_response(prompt, schema, **kwargs)
            elif self.provider == "openai":
                return self._generate_openai_structured_response(prompt, schema, **kwargs)
        except Exception as e:
            print(f"Erro ao gerar resposta estruturada: {e}")
            return {"error": str(e)}
    
    def _generate_gemini_structured_response(self, prompt: str, schema: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """Gera resposta estruturada usando Gemini"""
        import json
        
        structured_prompt = f"""
        {prompt}
        
        Responda APENAS com um JSON válido seguindo este schema:
        {json.dumps(schema, indent=2)}
        
        Não inclua explicações ou texto adicional, apenas o JSON.
        """
        
        response = self._generate_gemini_response(structured_prompt, **kwargs)
        
        try:
            # Tentar extrair JSON da resposta
            import re
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            else:
                return json.loads(response)
        except json.JSONDecodeError:
            return {"error": "Resposta não é um JSON válido", "raw_response": response}
    
    def _generate_openai_structured_response(self, prompt: str, schema: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """Gera resposta estruturada usando OpenAI"""
        import json
        
        structured_prompt = f"""
        {prompt}
        
        Responda APENAS com um JSON válido seguindo este schema:
        {json.dumps(schema, indent=2)}
        """
        
        try:
            response = self.client.chat.completions.create(
                model=settings.get_current_model(),
                messages=[{"role": "user", "content": structured_prompt}],
                temperature=kwargs.get("temperature", 0.1),  # Baixa temperatura para respostas estruturadas
                max_tokens=kwargs.get("max_tokens", settings.max_tokens),
                response_format={"type": "json_object"}  # Força resposta JSON
            )
            return json.loads(response.choices[0].message.content)
        except Exception as e:
            return {"error": str(e)}
    
    def get_provider_info(self) -> Dict[str, Any]:
        """Retorna informações sobre o provedor atual"""
        return {
            "provider": self.provider,
            "model": settings.get_current_model(),
            "available": self.client is not None,
            "temperature": settings.temperature,
            "max_tokens": settings.max_tokens
        }


# Instância global do provedor LLM
llm_provider = LLMProvider()

