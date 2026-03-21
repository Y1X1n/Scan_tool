#!/usr/bin/env python3
"""
端口扫描器测试脚本
用于验证各个模块的功能
"""
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from scanner.args_parser import parse_args, parse_ports, validate_ports
from scanner.network_utils import resolve_hostname, validate_ip, get_service_name
from scanner.scanner import PortScanner, ScanStatus
from scanner.output import TextFormatter, JSONFormatter, CSVFormatter, create_formatter


def test_args_parser():
    """测试参数解析模块"""
    print("=" * 50)
    print("测试参数解析模块")
    print("=" * 50)
    
    # 测试端口验证
    test_cases = [
        ("80", True),
        ("80,443", True),
        ("1-1000", True),
        ("80,443,1000-2000", True),
        ("0", False),  # 端口0无效
        ("65536", False),  # 端口65536无效
        ("1-65536", False),  # 包含无效端口
        ("abc", False),  # 非数字
    ]
    
    print("端口验证测试:")
    for ports_str, expected in test_cases:
        result = validate_ports(ports_str)
        status = "✓" if result == expected else "✗"
        print(f"  {status} '{ports_str}' -> {result} (期望: {expected})")
    
    # 测试端口解析
    print("\n端口解析测试:")
    test_parse = [
        ("80", [80]),
        ("80,443", [80, 443]),
        ("1-5", [1, 2, 3, 4, 5]),
        ("1,3,5", [1, 3, 5]),
        ("1-3,5", [1, 2, 3, 5]),
    ]
    
    for ports_str, expected in test_parse:
        result = parse_ports(ports_str)
        status = "✓" if result == expected else "✗"
        print(f"  {status} '{ports_str}' -> {result}")
    
    # 测试参数解析
    print("\n参数解析测试:")
    try:
        args = parse_args(["192.168.1.1", "-p", "80,443", "-t", "0.5"])
        print(f"  ✓ 目标: {args.target}")
        print(f"  ✓ 端口: {args.ports}")
        print(f"  ✓ 超时: {args.timeout}")
    except Exception as e:
        print(f"  ✗ 参数解析失败: {e}")
    
    print()


def test_network_utils():
    """测试网络工具模块"""
    print("=" * 50)
    print("测试网络工具模块")
    print("=" * 50)
    
    # 测试IP验证
    print("IP地址验证测试:")
    test_ips = [
        ("192.168.1.1", True),
        ("10.0.0.1", True),
        ("255.255.255.255", True),
        ("256.1.1.1", False),
        ("192.168.1", False),
        ("abc.def.ghi.jkl", False),
    ]
    
    for ip, expected in test_ips:
        result = validate_ip(ip)
        status = "✓" if result == expected else "✗"
        print(f"  {status} '{ip}' -> {result}")
    
    # 测试主机名解析
    print("\n主机名解析测试:")
    test_hosts = [
        "localhost",
        "127.0.0.1",
        "8.8.8.8",
    ]
    
    for host in test_hosts:
        result = resolve_hostname(host)
        status = "✓" if result else "✗"
        print(f"  {status} '{host}' -> {result}")
    
    # 测试服务名称获取
    print("\n服务名称获取测试:")
    test_services = [
        (22, "ssh"),
        (80, "http"),
        (443, "https"),
        (8080, "http-proxy"),
    ]
    
    for port, expected in test_services:
        result = get_service_name(port)
        status = "✓" if expected in result.lower() else "✗"
        print(f"  {status} 端口 {port} -> '{result}'")
    
    print()


def test_scanner():
    """测试扫描器模块"""
    print("=" * 50)
    print("测试扫描器模块")
    print("=" * 50)
    
    # 测试扫描器初始化
    print("扫描器初始化测试:")
    try:
        scanner = PortScanner(timeout=0.5, max_workers=10)
        print(f"  ✓ 扫描器创建成功")
        print(f"  ✓ 超时时间: {scanner.timeout}")
        print(f"  ✓ 最大线程数: {scanner.max_workers}")
    except Exception as e:
        print(f"  ✗ 扫描器创建失败: {e}")
    
    # 测试单端口扫描（使用本地回环地址）
    print("\n单端口扫描测试 (127.0.0.1:80):")
    try:
        result = scanner.scan_port_tcp("127.0.0.1", 80)
        print(f"  ✓ 端口: {result.port}")
        print(f"  ✓ 状态: {result.status}")
        print(f"  ✓ 响应时间: {result.response_time:.3f}秒")
    except Exception as e:
        print(f"  ✗ 扫描失败: {e}")
    
    print()


def test_output():
    """测试输出模块"""
    print("=" * 50)
    print("测试输出模块")
    print("=" * 50)
    
    # 创建模拟扫描结果
    from scanner.scanner import ScanResult
    mock_results = [
        ScanResult("192.168.1.1", 22, ScanStatus.OPEN, "ssh", 0.015),
        ScanResult("192.168.1.1", 80, ScanStatus.OPEN, "http", 0.012),
        ScanResult("192.168.1.1", 443, ScanStatus.OPEN, "https", 0.018),
        ScanResult("192.168.1.1", 8080, ScanStatus.CLOSED, "http-proxy", 0.001),
    ]
    
    mock_stats = {
        "total_ports": 4,
        "scanned_ports": 4,
        "open_ports": 3,
        "closed_ports": 1,
        "filtered_ports": 0,
        "error_ports": 0
    }
    
    # 测试文本格式化器
    print("文本格式化器测试:")
    try:
        formatter = TextFormatter()
        output = formatter.format_results(mock_results, mock_stats)
        lines = output.split('\n')
        print(f"  ✓ 输出行数: {len(lines)}")
        print(f"  ✓ 包含标题: {'端口扫描报告' in output}")
        print(f"  ✓ 包含统计: {'扫描统计' in output}")
    except Exception as e:
        print(f"  ✗ 文本格式化失败: {e}")
    
    # 测试JSON格式化器
    print("\nJSON格式化器测试:")
    try:
        formatter = JSONFormatter()
        output = formatter.format_results(mock_results, mock_stats)
        import json
        data = json.loads(output)
        print(f"  ✓ JSON解析成功")
        print(f"  ✓ 结果数量: {len(data['results'])}")
    except Exception as e:
        print(f"  ✗ JSON格式化失败: {e}")
    
    # 测试CSV格式化器
    print("\nCSV格式化器测试:")
    try:
        formatter = CSVFormatter()
        output = formatter.format_results(mock_results, mock_stats)
        lines = output.strip().split('\n')
        print(f"  ✓ CSV行数: {len(lines)}")
        print(f"  ✓ 包含标题行: {'Host' in lines[0]}")
    except Exception as e:
        print(f"  ✗ CSV格式化失败: {e}")
    
    print()


def test_integration():
    """集成测试"""
    print("=" * 50)
    print("集成测试")
    print("=" * 50)
    
    # 测试完整流程
    print("完整扫描流程测试:")
    try:
        # 解析参数
        args = parse_args(["127.0.0.1", "-p", "80,443", "-t", "0.5", "-w", "5"])
        print(f"  ✓ 参数解析成功")
        
        # 解析端口
        ports = parse_ports(args.ports)
        print(f"  ✓ 端口解析成功: {len(ports)}个端口")
        
        # 创建扫描器
        scanner = PortScanner(timeout=args.timeout, max_workers=args.workers)
        print(f"  ✓ 扫描器创建成功")
        
        # 执行扫描
        results = scanner.scan_ports("127.0.0.1", ports[:2], args.scan_type)  # 只扫描前2个端口
        print(f"  ✓ 扫描执行成功: {len(results)}个结果")
        
        # 格式化输出
        formatter = create_formatter(args.output_format)
        output = formatter.format_results(results, scanner.get_statistics())
        print(f"  ✓ 输出格式化成功")
        
        print(f"\n  扫描完成! 共扫描 {len(results)} 个端口")
        
    except Exception as e:
        print(f"  ✗ 集成测试失败: {e}")
    
    print()


def main():
    """主测试函数"""
    print("\n" + "=" * 50)
    print("端口扫描器模块测试")
    print("=" * 50)
    print()
    
    # 运行各项测试
    test_args_parser()
    test_network_utils()
    test_scanner()
    test_output()
    test_integration()
    
    print("=" * 50)
    print("测试完成!")
    print("=" * 50)


if __name__ == "__main__":
    main()