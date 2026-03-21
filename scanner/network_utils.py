"""
网络工具模块
提供网络相关的工具函数
"""
import socket
import ipaddress
from typing import Tuple, Optional, List


def resolve_hostname(hostname: str) -> Optional[str]:
    """
    解析主机名到IP地址
    :param hostname: 主机名或域名
    :return: IP地址字符串，解析失败返回None
    """
    try:
        # 如果是IP地址，直接返回
        ipaddress.ip_address(hostname)
        return hostname
    except ValueError:
        pass
    
    try:
        # 解析主机名
        ip = socket.gethostbyname(hostname)
        return ip
    except socket.gaierror:
        return None


def validate_ip(ip: str) -> bool:
    """
    验证IP地址格式
    :param ip: IP地址字符串
    :return: 是否有效
    """
    try:
        ipaddress.ip_address(ip)
        return True
    except ValueError:
        return False


def get_service_name(port: int, protocol: str = "tcp") -> str:
    """
    获取端口对应的服务名称
    :param port: 端口号
    :param protocol: 协议类型 (tcp/udp)
    :return: 服务名称
    """
    try:
        return socket.getservbyport(port, protocol)
    except (OSError, OverflowError):
        return "unknown"


def is_valid_port(port: int) -> bool:
    """
    验证端口号是否有效
    :param port: 端口号
    :return: 是否有效
    """
    return 1 <= port <= 65535


def get_local_ip() -> str:
    """
    获取本机IP地址
    :return: 本机IP地址
    """
    try:
        # 创建一个UDP套接字连接到外部地址（不实际发送数据）
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"


def check_host_reachable(host: str, timeout: float = 2.0) -> bool:
    """
    检查主机是否可达
    :param host: 主机地址
    :param timeout: 超时时间
    :return: 是否可达
    """
    try:
        # 尝试连接主机的7端口（Echo服务）
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        # 尝试连接到一个通常关闭的端口，如果连接被拒绝，说明主机可达
        result = sock.connect_ex((host, 7))
        sock.close()
        # 如果返回0表示连接成功（端口开放），其他值表示连接失败但主机可能可达
        # 我们主要关心主机是否响应
        return True
    except socket.error:
        return False


def parse_ip_range(ip_range: str) -> List[str]:
    """
    解析IP范围
    支持格式: 
    - 单个IP: 192.168.1.1
    - CIDR: 192.168.1.0/24
    - 范围: 192.168.1.1-192.168.1.10
    - 范围简写: 192.168.1.1-10
    :param ip_range: IP范围字符串
    :return: IP地址列表
    """
    ips = []
    
    # CIDR格式
    if '/' in ip_range:
        try:
            network = ipaddress.ip_network(ip_range, strict=False)
            ips = [str(ip) for ip in network.hosts()]
        except ValueError:
            pass
    
    # 范围格式
    elif '-' in ip_range:
        parts = ip_range.split('-', 1)
        if len(parts) == 2:
            start_ip = parts[0].strip()
            end_part = parts[1].strip()
            
            # 简写格式: 192.168.1.1-10
            if '.' not in end_part:
                try:
                    start = ipaddress.ip_address(start_ip)
                    end_octet = int(end_part)
                    if 0 <= end_octet <= 255:
                        base = start_ip.rsplit('.', 1)[0]
                        for i in range(start.packed[-1], end_octet + 1):
                            ips.append(f"{base}.{i}")
                except ValueError:
                    pass
            else:
                # 完整格式: 192.168.1.1-192.168.1.10
                try:
                    start = ipaddress.ip_address(start_ip)
                    end = ipaddress.ip_address(end_part)
                    current = start
                    while current <= end:
                        ips.append(str(current))
                        current += 1
                except ValueError:
                    pass
    
    # 单个IP
    else:
        try:
            ipaddress.ip_address(ip_range)
            ips.append(ip_range)
        except ValueError:
            pass
    
    return ips


def get_ip_info(ip: str) -> dict:
    """
    获取IP地址信息
    :param ip: IP地址
    :return: IP信息字典
    """
    info = {
        "ip": ip,
        "version": None,
        "is_private": False,
        "is_loopback": False,
        "hostname": None
    }
    
    try:
        addr = ipaddress.ip_address(ip)
        info["version"] = addr.version
        info["is_private"] = addr.is_private
        info["is_loopback"] = addr.is_loopback
        
        # 尝试反向解析
        try:
            hostname, _, _ = socket.gethostbyaddr(ip)
            info["hostname"] = hostname
        except socket.herror:
            pass
            
    except ValueError:
        pass
    
    return info