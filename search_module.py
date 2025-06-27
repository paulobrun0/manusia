"""
Módulo de Pesquisa Web - Busca de informações na internet
"""
import requests
import json
from typing import Dict, Any, List, Optional
from datetime import datetime
from bs4 import BeautifulSoup
from urllib.parse import quote_plus, urljoin


class SearchModule:
    """Módulo para pesquisa de informações na web"""
    
    def __init__(self):
        self.search_history = []
        self.max_history_size = 1000
        self.session = requests.Session()
        
        # Headers para simular um navegador real
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'pt-BR,pt;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        })
    
    def search_web(
        self,
        query: str,
        search_engine: str = "duckduckgo",
        max_results: int = 10,
        safe_search: bool = True
    ) -> Dict[str, Any]:
        """Realiza uma busca na web"""
        try:
            # Registrar busca no histórico
            search_entry = {
                "query": query,
                "search_engine": search_engine,
                "timestamp": datetime.now().isoformat(),
                "max_results": max_results
            }
            
            self.search_history.append(search_entry)
            
            # Limitar tamanho do histórico
            if len(self.search_history) > self.max_history_size:
                self.search_history.pop(0)
            
            # Executar busca baseada no motor escolhido
            if search_engine == "duckduckgo":
                results = self._search_duckduckgo(query, max_results, safe_search)
            elif search_engine == "google":
                results = self._search_google_scraping(query, max_results)
            elif search_engine == "bing":
                results = self._search_bing_scraping(query, max_results)
            else:
                return {
                    "success": False,
                    "error": f"Motor de busca não suportado: {search_engine}",
                    "query": query
                }
            
            # Atualizar entrada do histórico com resultados
            search_entry["results_count"] = len(results)
            search_entry["success"] = True
            
            return {
                "success": True,
                "query": query,
                "search_engine": search_engine,
                "results": results,
                "results_count": len(results),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            # Atualizar histórico com erro
            if self.search_history:
                self.search_history[-1]["success"] = False
                self.search_history[-1]["error"] = str(e)
            
            return {
                "success": False,
                "error": str(e),
                "query": query,
                "search_engine": search_engine
            }
    
    def _search_duckduckgo(self, query: str, max_results: int, safe_search: bool) -> List[Dict[str, Any]]:
        """Busca usando DuckDuckGo"""
        results = []
        
        try:
            # Primeira requisição para obter o token
            search_url = "https://html.duckduckgo.com/html/"
            params = {
                "q": query,
                "s": "0",  # Offset
                "dc": str(max_results),
                "v": "l",  # Layout
                "o": "json",
                "api": "/d.js"
            }
            
            if safe_search:
                params["safe"] = "moderate"
            
            response = self.session.get(search_url, params=params, timeout=10)
            response.raise_for_status()
            
            # Parse HTML
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extrair resultados
            result_divs = soup.find_all('div', class_='result')
            
            for div in result_divs[:max_results]:
                try:
                    # Título e link
                    title_link = div.find('a', class_='result__a')
                    if not title_link:
                        continue
                    
                    title = title_link.get_text(strip=True)
                    url = title_link.get('href', '')
                    
                    # Snippet
                    snippet_elem = div.find('a', class_='result__snippet')
                    snippet = snippet_elem.get_text(strip=True) if snippet_elem else ""
                    
                    # URL exibida
                    url_elem = div.find('span', class_='result__url')
                    display_url = url_elem.get_text(strip=True) if url_elem else url
                    
                    if title and url:
                        results.append({
                            "title": title,
                            "url": url,
                            "snippet": snippet,
                            "display_url": display_url,
                            "source": "duckduckgo"
                        })
                        
                except Exception as e:
                    print(f"Erro ao processar resultado DuckDuckGo: {e}")
                    continue
        
        except Exception as e:
            print(f"Erro na busca DuckDuckGo: {e}")
        
        return results
    
    def _search_google_scraping(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        """Busca usando Google (scraping)"""
        results = []
        
        try:
            search_url = "https://www.google.com/search"
            params = {
                "q": query,
                "num": max_results,
                "hl": "pt-BR",
                "gl": "BR"
            }
            
            response = self.session.get(search_url, params=params, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extrair resultados orgânicos
            result_divs = soup.find_all('div', class_='g')
            
            for div in result_divs[:max_results]:
                try:
                    # Título e link
                    title_elem = div.find('h3')
                    link_elem = div.find('a')
                    
                    if not title_elem or not link_elem:
                        continue
                    
                    title = title_elem.get_text(strip=True)
                    url = link_elem.get('href', '')
                    
                    # Snippet
                    snippet_elem = div.find('span', {'data-ved': True})
                    snippet = snippet_elem.get_text(strip=True) if snippet_elem else ""
                    
                    if title and url and url.startswith('http'):
                        results.append({
                            "title": title,
                            "url": url,
                            "snippet": snippet,
                            "source": "google"
                        })
                        
                except Exception as e:
                    print(f"Erro ao processar resultado Google: {e}")
                    continue
        
        except Exception as e:
            print(f"Erro na busca Google: {e}")
        
        return results
    
    def _search_bing_scraping(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        """Busca usando Bing (scraping)"""
        results = []
        
        try:
            search_url = "https://www.bing.com/search"
            params = {
                "q": query,
                "count": max_results,
                "mkt": "pt-BR"
            }
            
            response = self.session.get(search_url, params=params, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extrair resultados orgânicos
            result_divs = soup.find_all('li', class_='b_algo')
            
            for div in result_divs[:max_results]:
                try:
                    # Título e link
                    title_link = div.find('h2').find('a') if div.find('h2') else None
                    
                    if not title_link:
                        continue
                    
                    title = title_link.get_text(strip=True)
                    url = title_link.get('href', '')
                    
                    # Snippet
                    snippet_elem = div.find('p')
                    snippet = snippet_elem.get_text(strip=True) if snippet_elem else ""
                    
                    if title and url:
                        results.append({
                            "title": title,
                            "url": url,
                            "snippet": snippet,
                            "source": "bing"
                        })
                        
                except Exception as e:
                    print(f"Erro ao processar resultado Bing: {e}")
                    continue
        
        except Exception as e:
            print(f"Erro na busca Bing: {e}")
        
        return results
    
    def fetch_page_content(self, url: str, extract_text: bool = True) -> Dict[str, Any]:
        """Busca o conteúdo de uma página web"""
        try:
            response = self.session.get(url, timeout=15)
            response.raise_for_status()
            
            content_info = {
                "url": url,
                "status_code": response.status_code,
                "content_type": response.headers.get('content-type', ''),
                "content_length": len(response.content),
                "timestamp": datetime.now().isoformat()
            }
            
            if extract_text and 'text/html' in response.headers.get('content-type', ''):
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Remover scripts e estilos
                for script in soup(["script", "style"]):
                    script.decompose()
                
                # Extrair texto
                text = soup.get_text(strip=True, separator=' ')
                content_info["text"] = text
                content_info["text_length"] = len(text)
                
                # Extrair título
                title_elem = soup.find('title')
                content_info["title"] = title_elem.get_text(strip=True) if title_elem else ""
                
                # Extrair meta description
                meta_desc = soup.find('meta', attrs={'name': 'description'})
                content_info["description"] = meta_desc.get('content', '') if meta_desc else ""
                
                # Extrair links
                links = []
                for link in soup.find_all('a', href=True):
                    href = link['href']
                    if href.startswith('http') or href.startswith('/'):
                        links.append({
                            "text": link.get_text(strip=True),
                            "href": urljoin(url, href)
                        })
                content_info["links"] = links[:50]  # Limitar a 50 links
            
            return {
                "success": True,
                "content": content_info
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "url": url
            }
    
    def search_images(self, query: str, max_results: int = 20) -> Dict[str, Any]:
        """Busca imagens na web"""
        try:
            # Usar DuckDuckGo para busca de imagens
            search_url = "https://duckduckgo.com/"
            
            # Primeira requisição para obter tokens
            response = self.session.get(search_url, timeout=10)
            
            # Buscar imagens via API do DuckDuckGo
            api_url = "https://duckduckgo.com/i.js"
            params = {
                "l": "br-pt",
                "o": "json",
                "q": query,
                "vqd": "",  # Token necessário
                "f": ",,,,,",
                "p": "1"
            }
            
            # Esta é uma implementação simplificada
            # Em produção, seria necessário extrair o token VQD corretamente
            
            return {
                "success": False,
                "error": "Busca de imagens requer implementação mais complexa",
                "query": query,
                "note": "Use o módulo de navegação web para busca visual de imagens"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "query": query
            }
    
    def get_search_suggestions(self, query: str) -> Dict[str, Any]:
        """Obtém sugestões de busca"""
        try:
            # Usar API de sugestões do Google
            suggest_url = "https://suggestqueries.google.com/complete/search"
            params = {
                "client": "firefox",
                "q": query,
                "hl": "pt-BR"
            }
            
            response = self.session.get(suggest_url, params=params, timeout=5)
            response.raise_for_status()
            
            # Parse JSON
            suggestions_data = response.json()
            suggestions = suggestions_data[1] if len(suggestions_data) > 1 else []
            
            return {
                "success": True,
                "query": query,
                "suggestions": suggestions[:10],  # Limitar a 10 sugestões
                "count": len(suggestions)
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "query": query
            }
    
    def get_search_history(self, count: int = 20) -> Dict[str, Any]:
        """Retorna o histórico de buscas"""
        try:
            history = self.search_history[-count:] if count > 0 else self.search_history
            
            return {
                "success": True,
                "history": history,
                "total_searches": len(self.search_history),
                "returned_count": len(history)
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def clear_search_history(self) -> Dict[str, Any]:
        """Limpa o histórico de buscas"""
        try:
            cleared_count = len(self.search_history)
            self.search_history.clear()
            
            return {
                "success": True,
                "cleared_searches": cleared_count
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_search_statistics(self) -> Dict[str, Any]:
        """Retorna estatísticas de busca"""
        try:
            stats = {
                "total_searches": len(self.search_history),
                "successful_searches": sum(1 for s in self.search_history if s.get("success", False)),
                "failed_searches": sum(1 for s in self.search_history if not s.get("success", True)),
                "search_engines_used": {},
                "most_searched_terms": {}
            }
            
            # Contar por motor de busca
            for search in self.search_history:
                engine = search.get("search_engine", "unknown")
                stats["search_engines_used"][engine] = stats["search_engines_used"].get(engine, 0) + 1
            
            # Contar termos mais buscados (simplificado)
            for search in self.search_history:
                query = search.get("query", "").lower()
                if query:
                    stats["most_searched_terms"][query] = stats["most_searched_terms"].get(query, 0) + 1
            
            # Ordenar termos mais buscados
            stats["most_searched_terms"] = dict(
                sorted(stats["most_searched_terms"].items(), key=lambda x: x[1], reverse=True)[:10]
            )
            
            return {
                "success": True,
                "statistics": stats
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

