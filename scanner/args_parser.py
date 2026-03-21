"""
参数解析模块
处理命令行参数并提供默认值
"""
import argparse
import sys
from typing import List, Optional


def parse_args(args: Optional[List[str]] = None) -> argparse.Namespace:
    """
    解析命令行参数
    :param args: 参数列表，默认为sys.argv[1:]
    :return: 解析后的参数对象
    """
    parser = argparse.ArgumentParser(
        description="简易端口扫描器 - 基于Python实现",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  %(prog)s 192.168.1.1                 # 扫描默认端口 (1-1024)
  %(prog)s 192.168.1.1 -p 80,443       # 扫描指定端口
  %(prog)s 192.168.1.1 -p 1-1000       # 扫描端口范围
  %(prog)s 192.168.1.1 -t 0.5 -w 100   # 设置超时和线程数
        """
    )
    
    # 目标参数
    parser.add_argument(
        "target",
        help="目标主机 (IP地址或域名)"
    )
    
    # 端口参数
    parser.add_argument(
        "-p", "--ports",
        dest="ports",
        help="端口列表，用逗号分隔或范围 (例如: 80,443 或 1-1000)，默认: 1-1024",
        default="1-1024"
    )
    
    # 扫描类型
    parser.add_argument(
        "-s", "--scan-type",
        dest="scan_type",
        choices=["tcp", "udp"],
        default="tcp",
        help="扫描类型: tcp (TCP连接扫描), udp (UDP扫描)，默认: tcp"
    )
    
    # 超时时间
    parser.add_argument(
        "-t", "--timeout",
        dest="timeout",
        type=float,
        default=1.0,
        help="连接超时时间 (秒)，默认: 1.0"
    )
    
    # 线程数
    parser.add_argument(
        "-w", "--workers",
        dest="workers",
        type=int,
        default=100,
        help="并发线程数，默认: 100"
    )
    
    # 输出格式
    parser.add_argument(
        "-o", "--output",
        dest="output_format",
        choices=["text", "json", "csv"],
        default="text",
        help="输出格式: text, json, csv，默认: text"
    )
    
    # 详细输出
    parser.add_argument(
        "-v", "--verbose",
        dest="verbose",
        action="store_true",
        help="显示详细扫描信息"
    )
    
    # 只显示开放端口
    parser.add_argument(
        "--open-only",
        dest="open_only",
        action="store_true",
        help="只显示开放的端口"
    )
    
    # 版本信息
    parser.add_argument(
        "--version",
        action="version",
        version="%(prog)s 1.0.0"
    )
    
    # 解析参数
    parsed_args = parser.parse_args(args)
    
    # 验证参数
    validate_args(parsed_args)
    
    return parsed_args


def validate_args(args: argparse.Namespace) -> None:
    """
    验证参数有效性
    :param args: 解析后的参数对象
    :raises: SystemExit 如果参数无效
    """
    # 验证端口参数
    if not validate_ports(args.ports):
        print(f"错误: 端口参数格式无效 '{args.ports}'")
        print("正确格式: 80,443 或 1-1000 或 80,443,1000-2000")
        sys.exit(1)
    
    # 验证超时时间
    if args.timeout <= 0:
        print("错误: 超时时间必须大于0")
        sys.exit(1)
    
    # 验证线程数
    if args.workers <= 0:
        print("错误: 线程数必须大于0")
        sys.exit(1)


def validate_ports(ports_str: str) -> bool:
    """
    验证端口字符串格式
    :param ports_str: 端口字符串
    :return: 是否有效
    """
    import re
    
    # 端口格式正则表达式
    # 支持: 80 | 80,443 | 1-1000 | 80,443,1000-2000
    pattern = r'^(\d+(-\d+)?)(,\d+(-\d+)?)*$'
    
    if not re.match(pattern, ports_str):
        return False
    
    # 验证每个端口范围
    parts = ports_str.split(',')
    for part in parts:
        if '-' in part:
            start, end = part.split('-', 1)
            if not (1 <= int(start) <= 65535 and 1 <= int(end) <= 65535):
                return False
            if int(start) > int(end):
                return False
        else:
            port = int(part)
            if not (1 <= port <= 65535):
                return False
    
    return True


def parse_ports(ports_str: str) -> List[int]:
    """
    解析端口字符串为端口列表
    :param ports_str: 端口字符串
    :return: 端口列表
    """
    ports = []
    parts = ports_str.split(',')
    
    for part in parts:
        if '-' in part:
            start, end = part.split('-', 1)
            ports.extend(range(int(start), int(end) + 1))
        else:
            ports.append(int(part))
    
    # 去重并排序
    return sorted(set(ports))