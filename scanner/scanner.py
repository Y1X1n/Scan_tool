"""
扫描核心模块
实现端口扫描的主要逻辑
"""
import socket
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Callable, Optional, Any
from dataclasses import dataclass
from enum import Enum

from . import network_utils


class ScanStatus(Enum):
    """扫描状态枚举"""
    OPEN = "open"
    CLOSED = "closed"
    FILTERED = "filtered"
    ERROR = "error"


@dataclass
class ScanResult:
    """扫描结果数据类"""
    host: str
    port: int
    status: ScanStatus
    service: str = "unknown"
    response_time: float = 0.0
    error: Optional[str] = None


class PortScanner:
    """端口扫描器类"""
    
    def __init__(self, timeout: float = 1.0, max_workers: int = 100):
        """
        初始化扫描器
        :param timeout: 连接超时时间（秒）
        :param max_workers: 最大工作线程数
        """
        self.timeout = timeout
        self.max_workers = max_workers
        self.results: List[ScanResult] = []
        self.scanning = False
        self.progress_callback: Optional[Callable[[int, int], None]] = None
        self.result_callback: Optional[Callable[[ScanResult], None]] = None
        
        # 统计信息
        self.stats = {
            "total": 0,
            "scanned": 0,
            "open": 0,
            "closed": 0,
            "filtered": 0,
            "errors": 0
        }
    
    def set_progress_callback(self, callback: Callable[[int, int], None]) -> None:
        """设置进度回调函数"""
        self.progress_callback = callback
    
    def set_result_callback(self, callback: Callable[[ScanResult], None]) -> None:
        """设置结果回调函数"""
        self.result_callback = callback
    
    def scan_port_tcp(self, host: str, port: int) -> ScanResult:
        """
        TCP连接扫描
        :param host: 目标主机
        :param port: 目标端口
        :return: 扫描结果
        """
        start_time = time.time()
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(self.timeout)
        
        try:
            # 尝试连接
            result = sock.connect_ex((host, port))
            response_time = time.time() - start_time
            
            if result == 0:
                # 连接成功，端口开放
                service = network_utils.get_service_name(port, "tcp")
                status = ScanStatus.OPEN
                self.stats["open"] += 1
            else:
                # 连接失败，端口关闭
                service = "unknown"
                status = ScanStatus.CLOSED
                self.stats["closed"] += 1
            
            return ScanResult(
                host=host,
                port=port,
                status=status,
                service=service,
                response_time=response_time
            )
            
        except socket.timeout:
            # 超时，可能被过滤
            self.stats["filtered"] += 1
            return ScanResult(
                host=host,
                port=port,
                status=ScanStatus.FILTERED,
                response_time=time.time() - start_time,
                error="Connection timeout"
            )
        except socket.error as e:
            # 其他错误
            self.stats["errors"] += 1
            return ScanResult(
                host=host,
                port=port,
                status=ScanStatus.ERROR,
                response_time=time.time() - start_time,
                error=str(e)
            )
        finally:
            sock.close()
    
    def scan_port_udp(self, host: str, port: int) -> ScanResult:
        """
        UDP扫描（简易实现）
        :param host: 目标主机
        :param port: 目标端口
        :return: 扫描结果
        """
        start_time = time.time()
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(self.timeout)
        
        try:
            # 发送空数据包
            sock.sendto(b"", (host, port))
            
            try:
                # 尝试接收响应
                data, addr = sock.recvfrom(1024)
                response_time = time.time() - start_time
                service = network_utils.get_service_name(port, "udp")
                status = ScanStatus.OPEN
                self.stats["open"] += 1
            except socket.timeout:
                # 没有响应，可能开放或过滤
                response_time = time.time() - start_time
                service = "unknown"
                status = ScanStatus.FILTERED
                self.stats["filtered"] += 1
            
            return ScanResult(
                host=host,
                port=port,
                status=status,
                service=service,
                response_time=response_time
            )
            
        except socket.error as e:
            self.stats["errors"] += 1
            return ScanResult(
                host=host,
                port=port,
                status=ScanStatus.ERROR,
                response_time=time.time() - start_time,
                error=str(e)
            )
        finally:
            sock.close()
    
    def scan_single_port(self, host: str, port: int, scan_type: str = "tcp") -> ScanResult:
        """
        扫描单个端口
        :param host: 目标主机
        :param port: 目标端口
        :param scan_type: 扫描类型 (tcp/udp)
        :return: 扫描结果
        """
        self.stats["scanned"] += 1
        
        # 更新进度
        if self.progress_callback:
            self.progress_callback(self.stats["scanned"], self.stats["total"])
        
        # 根据扫描类型选择方法
        if scan_type.lower() == "udp":
            result = self.scan_port_udp(host, port)
        else:
            result = self.scan_port_tcp(host, port)
        
        # 调用结果回调
        if self.result_callback:
            self.result_callback(result)
        
        return result
    
    def scan_ports(self, host: str, ports: List[int], scan_type: str = "tcp") -> List[ScanResult]:
        """
        扫描多个端口
        :param host: 目标主机
        :param ports: 端口列表
        :param scan_type: 扫描类型
        :return: 扫描结果列表
        """
        self.scanning = True
        self.results = []
        
        # 重置统计
        self.stats = {
            "total": len(ports),
            "scanned": 0,
            "open": 0,
            "closed": 0,
            "filtered": 0,
            "errors": 0
        }
        
        # 使用线程池并发扫描
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # 提交所有任务
            future_to_port = {
                executor.submit(self.scan_single_port, host, port, scan_type): port
                for port in ports
            }
            
            # 收集结果
            for future in as_completed(future_to_port):
                if not self.scanning:
                    # 如果扫描被取消
                    executor.shutdown(wait=False)
                    break
                
                try:
                    result = future.result()
                    self.results.append(result)
                except Exception as e:
                    port = future_to_port[future]
                    self.results.append(ScanResult(
                        host=host,
                        port=port,
                        status=ScanStatus.ERROR,
                        error=str(e)
                    ))
        
        self.scanning = False
        return self.results
    
    def stop_scan(self) -> None:
        """停止扫描"""
        self.scanning = False
    
    def get_open_ports(self) -> List[ScanResult]:
        """获取开放端口列表"""
        return [r for r in self.results if r.status == ScanStatus.OPEN]
    
    def get_statistics(self) -> Dict[str, Any]:
        """获取扫描统计信息"""
        return {
            "total_ports": self.stats["total"],
            "scanned_ports": self.stats["scanned"],
            "open_ports": self.stats["open"],
            "closed_ports": self.stats["closed"],
            "filtered_ports": self.stats["filtered"],
            "error_ports": self.stats["errors"]
        }