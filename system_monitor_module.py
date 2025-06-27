"""
Módulo de Monitoramento de Sistema
"""
import os
import psutil
import subprocess
import platform
from typing import Dict, Any, List, Optional
from datetime import datetime


class SystemMonitorModule:
    """Módulo para monitoramento de sistema e processos"""
    
    def __init__(self):
        self.monitoring_history = []
        self.max_history_size = 1000
    
    def _log_monitoring(self, operation: str, data: Dict[str, Any]) -> None:
        """Registra uma operação de monitoramento"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "operation": operation,
            "data": data
        }
        
        self.monitoring_history.append(log_entry)
        
        # Limitar tamanho do histórico
        if len(self.monitoring_history) > self.max_history_size:
            self.monitoring_history.pop(0)
    
    def get_system_info(self) -> Dict[str, Any]:
        """Obtém informações gerais do sistema"""
        try:
            # Informações do sistema operacional
            system_info = {
                "platform": platform.platform(),
                "system": platform.system(),
                "release": platform.release(),
                "version": platform.version(),
                "machine": platform.machine(),
                "processor": platform.processor(),
                "architecture": platform.architecture(),
                "hostname": platform.node(),
                "python_version": platform.python_version()
            }
            
            # Informações de boot
            boot_time = psutil.boot_time()
            system_info["boot_time"] = datetime.fromtimestamp(boot_time).isoformat()
            system_info["uptime_seconds"] = datetime.now().timestamp() - boot_time
            
            # Informações de usuários
            users = []
            for user in psutil.users():
                users.append({
                    "name": user.name,
                    "terminal": user.terminal,
                    "host": user.host,
                    "started": datetime.fromtimestamp(user.started).isoformat()
                })
            system_info["users"] = users
            
            self._log_monitoring("system_info", system_info)
            
            return {
                "success": True,
                "system_info": system_info,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_cpu_info(self) -> Dict[str, Any]:
        """Obtém informações da CPU"""
        try:
            cpu_info = {
                "physical_cores": psutil.cpu_count(logical=False),
                "logical_cores": psutil.cpu_count(logical=True),
                "cpu_percent": psutil.cpu_percent(interval=1),
                "cpu_percent_per_core": psutil.cpu_percent(interval=1, percpu=True),
                "cpu_freq": psutil.cpu_freq()._asdict() if psutil.cpu_freq() else None,
                "load_average": os.getloadavg() if hasattr(os, 'getloadavg') else None
            }
            
            # Estatísticas de CPU
            cpu_stats = psutil.cpu_stats()
            cpu_info["cpu_stats"] = {
                "ctx_switches": cpu_stats.ctx_switches,
                "interrupts": cpu_stats.interrupts,
                "soft_interrupts": cpu_stats.soft_interrupts,
                "syscalls": cpu_stats.syscalls
            }
            
            # Tempos de CPU
            cpu_times = psutil.cpu_times()
            cpu_info["cpu_times"] = {
                "user": cpu_times.user,
                "system": cpu_times.system,
                "idle": cpu_times.idle,
                "nice": getattr(cpu_times, 'nice', 0),
                "iowait": getattr(cpu_times, 'iowait', 0),
                "irq": getattr(cpu_times, 'irq', 0),
                "softirq": getattr(cpu_times, 'softirq', 0)
            }
            
            self._log_monitoring("cpu_info", cpu_info)
            
            return {
                "success": True,
                "cpu_info": cpu_info,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_memory_info(self) -> Dict[str, Any]:
        """Obtém informações de memória"""
        try:
            # Memória virtual (RAM)
            virtual_memory = psutil.virtual_memory()
            memory_info = {
                "virtual_memory": {
                    "total": virtual_memory.total,
                    "available": virtual_memory.available,
                    "used": virtual_memory.used,
                    "free": virtual_memory.free,
                    "percent": virtual_memory.percent,
                    "active": getattr(virtual_memory, 'active', 0),
                    "inactive": getattr(virtual_memory, 'inactive', 0),
                    "buffers": getattr(virtual_memory, 'buffers', 0),
                    "cached": getattr(virtual_memory, 'cached', 0)
                }
            }
            
            # Memória swap
            swap_memory = psutil.swap_memory()
            memory_info["swap_memory"] = {
                "total": swap_memory.total,
                "used": swap_memory.used,
                "free": swap_memory.free,
                "percent": swap_memory.percent,
                "sin": swap_memory.sin,
                "sout": swap_memory.sout
            }
            
            # Converter bytes para formato legível
            def bytes_to_human(bytes_value):
                for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
                    if bytes_value < 1024.0:
                        return f"{bytes_value:.2f} {unit}"
                    bytes_value /= 1024.0
                return f"{bytes_value:.2f} PB"
            
            memory_info["human_readable"] = {
                "virtual_total": bytes_to_human(virtual_memory.total),
                "virtual_used": bytes_to_human(virtual_memory.used),
                "virtual_available": bytes_to_human(virtual_memory.available),
                "swap_total": bytes_to_human(swap_memory.total),
                "swap_used": bytes_to_human(swap_memory.used)
            }
            
            self._log_monitoring("memory_info", memory_info)
            
            return {
                "success": True,
                "memory_info": memory_info,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_disk_info(self) -> Dict[str, Any]:
        """Obtém informações de disco"""
        try:
            disk_info = {
                "partitions": [],
                "disk_io": None,
                "total_disk_usage": {"total": 0, "used": 0, "free": 0}
            }
            
            # Informações de partições
            for partition in psutil.disk_partitions():
                try:
                    partition_usage = psutil.disk_usage(partition.mountpoint)
                    
                    partition_info = {
                        "device": partition.device,
                        "mountpoint": partition.mountpoint,
                        "fstype": partition.fstype,
                        "total": partition_usage.total,
                        "used": partition_usage.used,
                        "free": partition_usage.free,
                        "percent": (partition_usage.used / partition_usage.total) * 100
                    }
                    
                    disk_info["partitions"].append(partition_info)
                    
                    # Somar para total geral
                    disk_info["total_disk_usage"]["total"] += partition_usage.total
                    disk_info["total_disk_usage"]["used"] += partition_usage.used
                    disk_info["total_disk_usage"]["free"] += partition_usage.free
                    
                except PermissionError:
                    # Ignorar partições sem permissão
                    continue
            
            # I/O de disco
            try:
                disk_io = psutil.disk_io_counters()
                if disk_io:
                    disk_info["disk_io"] = {
                        "read_count": disk_io.read_count,
                        "write_count": disk_io.write_count,
                        "read_bytes": disk_io.read_bytes,
                        "write_bytes": disk_io.write_bytes,
                        "read_time": disk_io.read_time,
                        "write_time": disk_io.write_time
                    }
            except Exception:
                pass
            
            self._log_monitoring("disk_info", disk_info)
            
            return {
                "success": True,
                "disk_info": disk_info,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_network_info(self) -> Dict[str, Any]:
        """Obtém informações de rede"""
        try:
            network_info = {
                "interfaces": {},
                "connections": [],
                "io_counters": None
            }
            
            # Interfaces de rede
            for interface_name, addresses in psutil.net_if_addrs().items():
                interface_info = {
                    "addresses": [],
                    "stats": None
                }
                
                # Endereços da interface
                for addr in addresses:
                    address_info = {
                        "family": str(addr.family),
                        "address": addr.address,
                        "netmask": addr.netmask,
                        "broadcast": addr.broadcast
                    }
                    interface_info["addresses"].append(address_info)
                
                # Estatísticas da interface
                try:
                    stats = psutil.net_if_stats()[interface_name]
                    interface_info["stats"] = {
                        "isup": stats.isup,
                        "duplex": str(stats.duplex),
                        "speed": stats.speed,
                        "mtu": stats.mtu
                    }
                except KeyError:
                    pass
                
                network_info["interfaces"][interface_name] = interface_info
            
            # Conexões de rede
            try:
                for conn in psutil.net_connections(kind='inet')[:20]:  # Limitar a 20
                    connection_info = {
                        "fd": conn.fd,
                        "family": str(conn.family),
                        "type": str(conn.type),
                        "local_address": f"{conn.laddr.ip}:{conn.laddr.port}" if conn.laddr else None,
                        "remote_address": f"{conn.raddr.ip}:{conn.raddr.port}" if conn.raddr else None,
                        "status": str(conn.status),
                        "pid": conn.pid
                    }
                    network_info["connections"].append(connection_info)
            except (PermissionError, psutil.AccessDenied):
                # Pode não ter permissão para ver todas as conexões
                pass
            
            # Contadores de I/O de rede
            try:
                io_counters = psutil.net_io_counters()
                if io_counters:
                    network_info["io_counters"] = {
                        "bytes_sent": io_counters.bytes_sent,
                        "bytes_recv": io_counters.bytes_recv,
                        "packets_sent": io_counters.packets_sent,
                        "packets_recv": io_counters.packets_recv,
                        "errin": io_counters.errin,
                        "errout": io_counters.errout,
                        "dropin": io_counters.dropin,
                        "dropout": io_counters.dropout
                    }
            except Exception:
                pass
            
            self._log_monitoring("network_info", network_info)
            
            return {
                "success": True,
                "network_info": network_info,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_process_list(self, limit: int = 20, sort_by: str = "cpu_percent") -> Dict[str, Any]:
        """Obtém lista de processos"""
        try:
            processes = []
            
            for proc in psutil.process_iter(['pid', 'name', 'username', 'cpu_percent', 'memory_percent', 'status', 'create_time']):
                try:
                    process_info = proc.info
                    process_info['create_time'] = datetime.fromtimestamp(process_info['create_time']).isoformat()
                    processes.append(process_info)
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    continue
            
            # Ordenar processos
            if sort_by == "cpu_percent":
                processes.sort(key=lambda x: x.get('cpu_percent', 0), reverse=True)
            elif sort_by == "memory_percent":
                processes.sort(key=lambda x: x.get('memory_percent', 0), reverse=True)
            elif sort_by == "pid":
                processes.sort(key=lambda x: x.get('pid', 0))
            
            # Limitar resultados
            processes = processes[:limit]
            
            process_summary = {
                "total_processes": len(list(psutil.process_iter())),
                "running_processes": len([p for p in processes if p.get('status') == 'running']),
                "sleeping_processes": len([p for p in processes if p.get('status') == 'sleeping']),
                "top_processes": processes
            }
            
            self._log_monitoring("process_list", {"count": len(processes), "sort_by": sort_by})
            
            return {
                "success": True,
                "process_summary": process_summary,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_process_info(self, pid: int) -> Dict[str, Any]:
        """Obtém informações detalhadas de um processo específico"""
        try:
            proc = psutil.Process(pid)
            
            process_info = {
                "pid": proc.pid,
                "name": proc.name(),
                "exe": proc.exe() if proc.exe() else None,
                "cmdline": proc.cmdline(),
                "status": proc.status(),
                "username": proc.username(),
                "create_time": datetime.fromtimestamp(proc.create_time()).isoformat(),
                "cpu_percent": proc.cpu_percent(),
                "memory_percent": proc.memory_percent(),
                "num_threads": proc.num_threads(),
                "num_fds": proc.num_fds() if hasattr(proc, 'num_fds') else None,
                "ppid": proc.ppid()
            }
            
            # Informações de memória
            try:
                memory_info = proc.memory_info()
                process_info["memory_info"] = {
                    "rss": memory_info.rss,
                    "vms": memory_info.vms,
                    "shared": getattr(memory_info, 'shared', 0),
                    "text": getattr(memory_info, 'text', 0),
                    "lib": getattr(memory_info, 'lib', 0),
                    "data": getattr(memory_info, 'data', 0),
                    "dirty": getattr(memory_info, 'dirty', 0)
                }
            except Exception:
                pass
            
            # Informações de CPU
            try:
                cpu_times = proc.cpu_times()
                process_info["cpu_times"] = {
                    "user": cpu_times.user,
                    "system": cpu_times.system,
                    "children_user": getattr(cpu_times, 'children_user', 0),
                    "children_system": getattr(cpu_times, 'children_system', 0)
                }
            except Exception:
                pass
            
            # Conexões de rede do processo
            try:
                connections = []
                for conn in proc.connections():
                    connection_info = {
                        "fd": conn.fd,
                        "family": str(conn.family),
                        "type": str(conn.type),
                        "local_address": f"{conn.laddr.ip}:{conn.laddr.port}" if conn.laddr else None,
                        "remote_address": f"{conn.raddr.ip}:{conn.raddr.port}" if conn.raddr else None,
                        "status": str(conn.status)
                    }
                    connections.append(connection_info)
                process_info["connections"] = connections
            except (psutil.AccessDenied, psutil.NoSuchProcess):
                pass
            
            self._log_monitoring("process_info", {"pid": pid})
            
            return {
                "success": True,
                "process_info": process_info,
                "timestamp": datetime.now().isoformat()
            }
            
        except psutil.NoSuchProcess:
            return {
                "success": False,
                "error": f"Processo com PID {pid} não encontrado",
                "pid": pid
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "pid": pid
            }
    
    def kill_process(self, pid: int, force: bool = False) -> Dict[str, Any]:
        """Termina um processo"""
        try:
            proc = psutil.Process(pid)
            process_name = proc.name()
            
            if force:
                proc.kill()  # SIGKILL
                action = "killed"
            else:
                proc.terminate()  # SIGTERM
                action = "terminated"
            
            # Aguardar um pouco para verificar se o processo terminou
            try:
                proc.wait(timeout=3)
                terminated = True
            except psutil.TimeoutExpired:
                terminated = False
            
            self._log_monitoring("kill_process", {
                "pid": pid,
                "process_name": process_name,
                "action": action,
                "force": force,
                "terminated": terminated
            })
            
            return {
                "success": True,
                "pid": pid,
                "process_name": process_name,
                "action": action,
                "terminated": terminated
            }
            
        except psutil.NoSuchProcess:
            return {
                "success": False,
                "error": f"Processo com PID {pid} não encontrado",
                "pid": pid
            }
        except psutil.AccessDenied:
            return {
                "success": False,
                "error": f"Permissão negada para terminar processo {pid}",
                "pid": pid
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "pid": pid
            }
    
    def get_system_performance_summary(self) -> Dict[str, Any]:
        """Obtém um resumo de performance do sistema"""
        try:
            summary = {
                "timestamp": datetime.now().isoformat(),
                "cpu": {
                    "usage_percent": psutil.cpu_percent(interval=1),
                    "load_average": os.getloadavg() if hasattr(os, 'getloadavg') else None
                },
                "memory": {
                    "usage_percent": psutil.virtual_memory().percent,
                    "available_gb": psutil.virtual_memory().available / (1024**3)
                },
                "disk": {
                    "usage_percent": psutil.disk_usage('/').percent,
                    "free_gb": psutil.disk_usage('/').free / (1024**3)
                },
                "network": {
                    "bytes_sent": psutil.net_io_counters().bytes_sent if psutil.net_io_counters() else 0,
                    "bytes_recv": psutil.net_io_counters().bytes_recv if psutil.net_io_counters() else 0
                },
                "processes": {
                    "total": len(list(psutil.process_iter())),
                    "running": len([p for p in psutil.process_iter() if p.status() == 'running'])
                }
            }
            
            # Determinar status geral do sistema
            cpu_high = summary["cpu"]["usage_percent"] > 80
            memory_high = summary["memory"]["usage_percent"] > 80
            disk_high = summary["disk"]["usage_percent"] > 90
            
            if cpu_high or memory_high or disk_high:
                summary["system_status"] = "warning"
                summary["warnings"] = []
                if cpu_high:
                    summary["warnings"].append("CPU usage high")
                if memory_high:
                    summary["warnings"].append("Memory usage high")
                if disk_high:
                    summary["warnings"].append("Disk usage high")
            else:
                summary["system_status"] = "normal"
            
            self._log_monitoring("performance_summary", summary)
            
            return {
                "success": True,
                "performance_summary": summary
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_monitoring_history(self, count: int = 20) -> Dict[str, Any]:
        """Retorna o histórico de monitoramento"""
        try:
            history = self.monitoring_history[-count:] if count > 0 else self.monitoring_history
            
            return {
                "success": True,
                "history": history,
                "total_entries": len(self.monitoring_history),
                "returned_count": len(history)
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

