"""
Módulo de Navegação Web - Automação de navegador e extração de conteúdo
"""
import time
import requests
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException
from bs4 import BeautifulSoup


class WebNavigationModule:
    """Módulo para navegação web e automação de browser"""
    
    def __init__(self, headless: bool = True, timeout: int = 30):
        self.headless = headless
        self.timeout = timeout
        self.driver = None
        self.current_url = None
        self.navigation_history = []
        self.page_content_cache = {}
        
        # Configurar opções do Chrome
        self.chrome_options = Options()
        if headless:
            self.chrome_options.add_argument("--headless")
        self.chrome_options.add_argument("--no-sandbox")
        self.chrome_options.add_argument("--disable-dev-shm-usage")
        self.chrome_options.add_argument("--disable-gpu")
        self.chrome_options.add_argument("--window-size=1920,1080")
        self.chrome_options.add_argument("--user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
    
    def _ensure_driver(self) -> bool:
        """Garante que o driver está inicializado"""
        if self.driver is None:
            try:
                self.driver = webdriver.Chrome(options=self.chrome_options)
                self.driver.set_page_load_timeout(self.timeout)
                return True
            except Exception as e:
                print(f"Erro ao inicializar driver: {e}")
                return False
        return True
    
    def navigate_to_url(self, url: str, wait_for_element: Optional[str] = None) -> Dict[str, Any]:
        """Navega para uma URL específica"""
        try:
            if not self._ensure_driver():
                return {
                    "success": False,
                    "error": "Falha ao inicializar o driver do navegador",
                    "url": url
                }
            
            # Registrar no histórico
            self.navigation_history.append({
                "url": url,
                "timestamp": datetime.now().isoformat(),
                "action": "navigate"
            })
            
            # Navegar
            self.driver.get(url)
            self.current_url = url
            
            # Aguardar elemento específico se fornecido
            if wait_for_element:
                try:
                    WebDriverWait(self.driver, 10).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, wait_for_element))
                    )
                except TimeoutException:
                    pass  # Continuar mesmo se o elemento não for encontrado
            
            # Aguardar carregamento da página
            time.sleep(2)
            
            # Extrair informações básicas da página
            page_info = self._extract_page_info()
            
            return {
                "success": True,
                "url": url,
                "title": page_info.get("title", ""),
                "status": "loaded",
                "page_info": page_info
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "url": url
            }
    
    def click_element(self, selector: str, selector_type: str = "css") -> Dict[str, Any]:
        """Clica em um elemento da página"""
        try:
            if not self.driver:
                return {
                    "success": False,
                    "error": "Driver não inicializado",
                    "selector": selector
                }
            
            # Determinar tipo de seletor
            by_type = By.CSS_SELECTOR if selector_type == "css" else By.XPATH
            
            # Aguardar elemento ser clicável
            element = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((by_type, selector))
            )
            
            # Rolar até o elemento
            self.driver.execute_script("arguments[0].scrollIntoView(true);", element)
            time.sleep(1)
            
            # Clicar
            element.click()
            
            # Registrar ação
            self.navigation_history.append({
                "action": "click",
                "selector": selector,
                "timestamp": datetime.now().isoformat(),
                "url": self.current_url
            })
            
            return {
                "success": True,
                "selector": selector,
                "action": "clicked",
                "current_url": self.driver.current_url
            }
            
        except TimeoutException:
            return {
                "success": False,
                "error": f"Elemento não encontrado ou não clicável: {selector}",
                "selector": selector
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "selector": selector
            }
    
    def input_text(self, selector: str, text: str, clear_first: bool = True, press_enter: bool = False) -> Dict[str, Any]:
        """Insere texto em um campo de entrada"""
        try:
            if not self.driver:
                return {
                    "success": False,
                    "error": "Driver não inicializado",
                    "selector": selector
                }
            
            # Aguardar elemento
            element = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, selector))
            )
            
            # Rolar até o elemento
            self.driver.execute_script("arguments[0].scrollIntoView(true);", element)
            time.sleep(1)
            
            # Limpar campo se solicitado
            if clear_first:
                element.clear()
            
            # Inserir texto
            element.send_keys(text)
            
            # Pressionar Enter se solicitado
            if press_enter:
                element.send_keys(Keys.RETURN)
            
            # Registrar ação
            self.navigation_history.append({
                "action": "input",
                "selector": selector,
                "text": text,
                "timestamp": datetime.now().isoformat(),
                "url": self.current_url
            })
            
            return {
                "success": True,
                "selector": selector,
                "text": text,
                "action": "text_entered"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "selector": selector,
                "text": text
            }
    
    def scroll_page(self, direction: str = "down", pixels: int = 500) -> Dict[str, Any]:
        """Rola a página"""
        try:
            if not self.driver:
                return {
                    "success": False,
                    "error": "Driver não inicializado"
                }
            
            if direction == "down":
                self.driver.execute_script(f"window.scrollBy(0, {pixels});")
            elif direction == "up":
                self.driver.execute_script(f"window.scrollBy(0, -{pixels});")
            elif direction == "top":
                self.driver.execute_script("window.scrollTo(0, 0);")
            elif direction == "bottom":
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            
            time.sleep(1)  # Aguardar carregamento
            
            return {
                "success": True,
                "direction": direction,
                "pixels": pixels,
                "action": "scrolled"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "direction": direction
            }
    
    def extract_page_content(self, include_links: bool = True, include_images: bool = True) -> Dict[str, Any]:
        """Extrai o conteúdo da página atual"""
        try:
            if not self.driver:
                return {
                    "success": False,
                    "error": "Driver não inicializado"
                }
            
            # Obter HTML da página
            html = self.driver.page_source
            soup = BeautifulSoup(html, 'html.parser')
            
            # Extrair informações básicas
            content = {
                "url": self.driver.current_url,
                "title": self.driver.title,
                "text": soup.get_text(strip=True, separator=' '),
                "timestamp": datetime.now().isoformat()
            }
            
            # Extrair links se solicitado
            if include_links:
                links = []
                for link in soup.find_all('a', href=True):
                    links.append({
                        "text": link.get_text(strip=True),
                        "href": link['href'],
                        "title": link.get('title', '')
                    })
                content["links"] = links
            
            # Extrair imagens se solicitado
            if include_images:
                images = []
                for img in soup.find_all('img', src=True):
                    images.append({
                        "src": img['src'],
                        "alt": img.get('alt', ''),
                        "title": img.get('title', '')
                    })
                content["images"] = images
            
            # Extrair formulários
            forms = []
            for form in soup.find_all('form'):
                form_data = {
                    "action": form.get('action', ''),
                    "method": form.get('method', 'get'),
                    "inputs": []
                }
                
                for input_elem in form.find_all(['input', 'textarea', 'select']):
                    form_data["inputs"].append({
                        "type": input_elem.get('type', ''),
                        "name": input_elem.get('name', ''),
                        "placeholder": input_elem.get('placeholder', ''),
                        "required": input_elem.has_attr('required')
                    })
                
                forms.append(form_data)
            
            content["forms"] = forms
            
            # Cache do conteúdo
            self.page_content_cache[self.driver.current_url] = content
            
            return {
                "success": True,
                "content": content,
                "content_length": len(content["text"]),
                "links_count": len(content.get("links", [])),
                "images_count": len(content.get("images", []))
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "url": self.current_url
            }
    
    def search_web(self, query: str, search_engine: str = "google", max_results: int = 10) -> Dict[str, Any]:
        """Realiza uma busca na web"""
        try:
            search_urls = {
                "google": f"https://www.google.com/search?q={query.replace(' ', '+')}",
                "bing": f"https://www.bing.com/search?q={query.replace(' ', '+')}",
                "duckduckgo": f"https://duckduckgo.com/?q={query.replace(' ', '+')}"
            }
            
            if search_engine not in search_urls:
                return {
                    "success": False,
                    "error": f"Motor de busca não suportado: {search_engine}",
                    "query": query
                }
            
            # Navegar para a página de busca
            search_url = search_urls[search_engine]
            nav_result = self.navigate_to_url(search_url)
            
            if not nav_result["success"]:
                return nav_result
            
            # Aguardar carregamento dos resultados
            time.sleep(3)
            
            # Extrair resultados de busca
            results = self._extract_search_results(search_engine, max_results)
            
            return {
                "success": True,
                "query": query,
                "search_engine": search_engine,
                "results": results,
                "results_count": len(results),
                "search_url": search_url
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "query": query,
                "search_engine": search_engine
            }
    
    def _extract_search_results(self, search_engine: str, max_results: int) -> List[Dict[str, Any]]:
        """Extrai resultados de busca da página"""
        results = []
        
        try:
            if search_engine == "google":
                # Seletores para resultados do Google
                result_elements = self.driver.find_elements(By.CSS_SELECTOR, "div.g")
                
                for element in result_elements[:max_results]:
                    try:
                        title_elem = element.find_element(By.CSS_SELECTOR, "h3")
                        link_elem = element.find_element(By.CSS_SELECTOR, "a")
                        snippet_elem = element.find_element(By.CSS_SELECTOR, "span[data-ved]")
                        
                        results.append({
                            "title": title_elem.text,
                            "url": link_elem.get_attribute("href"),
                            "snippet": snippet_elem.text if snippet_elem else ""
                        })
                    except NoSuchElementException:
                        continue
            
            elif search_engine == "bing":
                # Seletores para resultados do Bing
                result_elements = self.driver.find_elements(By.CSS_SELECTOR, "li.b_algo")
                
                for element in result_elements[:max_results]:
                    try:
                        title_elem = element.find_element(By.CSS_SELECTOR, "h2 a")
                        snippet_elem = element.find_element(By.CSS_SELECTOR, "p")
                        
                        results.append({
                            "title": title_elem.text,
                            "url": title_elem.get_attribute("href"),
                            "snippet": snippet_elem.text if snippet_elem else ""
                        })
                    except NoSuchElementException:
                        continue
            
            elif search_engine == "duckduckgo":
                # Seletores para resultados do DuckDuckGo
                result_elements = self.driver.find_elements(By.CSS_SELECTOR, "article[data-testid='result']")
                
                for element in result_elements[:max_results]:
                    try:
                        title_elem = element.find_element(By.CSS_SELECTOR, "h2 a")
                        snippet_elem = element.find_element(By.CSS_SELECTOR, "span[data-result='snippet']")
                        
                        results.append({
                            "title": title_elem.text,
                            "url": title_elem.get_attribute("href"),
                            "snippet": snippet_elem.text if snippet_elem else ""
                        })
                    except NoSuchElementException:
                        continue
        
        except Exception as e:
            print(f"Erro ao extrair resultados de busca: {e}")
        
        return results
    
    def _extract_page_info(self) -> Dict[str, Any]:
        """Extrai informações básicas da página atual"""
        try:
            if not self.driver:
                return {}
            
            return {
                "title": self.driver.title,
                "url": self.driver.current_url,
                "page_source_length": len(self.driver.page_source),
                "timestamp": datetime.now().isoformat()
            }
        except Exception:
            return {}
    
    def take_screenshot(self, filename: str = None) -> Dict[str, Any]:
        """Captura uma screenshot da página atual"""
        try:
            if not self.driver:
                return {
                    "success": False,
                    "error": "Driver não inicializado"
                }
            
            if filename is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"screenshot_{timestamp}.png"
            
            # Garantir que o diretório existe
            import os
            os.makedirs(os.path.dirname(filename) if os.path.dirname(filename) else ".", exist_ok=True)
            
            # Capturar screenshot
            success = self.driver.save_screenshot(filename)
            
            return {
                "success": success,
                "filename": filename,
                "url": self.current_url,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "filename": filename
            }
    
    def get_navigation_history(self, count: int = 20) -> Dict[str, Any]:
        """Retorna o histórico de navegação"""
        return {
            "success": True,
            "history": self.navigation_history[-count:] if count > 0 else self.navigation_history,
            "total_actions": len(self.navigation_history),
            "current_url": self.current_url
        }
    
    def close_browser(self) -> Dict[str, Any]:
        """Fecha o navegador"""
        try:
            if self.driver:
                self.driver.quit()
                self.driver = None
                self.current_url = None
            
            return {
                "success": True,
                "action": "browser_closed"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_current_page_info(self) -> Dict[str, Any]:
        """Retorna informações da página atual"""
        try:
            if not self.driver:
                return {
                    "success": False,
                    "error": "Driver não inicializado"
                }
            
            return {
                "success": True,
                "url": self.driver.current_url,
                "title": self.driver.title,
                "page_source_length": len(self.driver.page_source),
                "window_size": self.driver.get_window_size(),
                "cookies_count": len(self.driver.get_cookies())
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def execute_javascript(self, script: str) -> Dict[str, Any]:
        """Executa JavaScript na página atual"""
        try:
            if not self.driver:
                return {
                    "success": False,
                    "error": "Driver não inicializado"
                }
            
            result = self.driver.execute_script(script)
            
            return {
                "success": True,
                "script": script,
                "result": result,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "script": script
            }

