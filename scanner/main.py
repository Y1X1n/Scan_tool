"""
主程序入口
协调各个模块，实现完整的扫描流程
"""
import sys
import time
from typing import List, Optional

from .args_parser import parse_args, parse_ports
from .network_utils import resolve_hostname, validate_ip, check_host_reachable
from .scanner import PortScanner, ScanResult
from .output import (
    create_formatter, 
    print_banner, 
    print_progress, 
    print_scan_summary,
    TextFormatter
)


def main(args: Optional[List[str]] = None) -> int:
    """
    主函数
    :param args: 命令行参数列表
    :return: 退出码
    """
    try:
        # 打印横幅
        print_banner()
        
        # 解析命令行参数
        parsed_args = parse_args(args)
        
        # 显示扫描配置
        print(f"目标主机: {parsed_args.target}")
        print(f"端口范围: {parsed_args.ports}")
        print(f"扫描类型: {parsed_args.scan_type}")
        print(f"超时时间: {parsed_args.timeout}秒")
        print(f"并发线程: {parsed_args.workers}")
        print(f"输出格式: {parsed_args.output_format}")
        print("-" * 50)
        
        # 解析端口列表
        ports = parse_ports(parsed_args.ports)
        print(f"待扫描端口数: {len(ports)}")
        
        # 解析主机名
        print("正在解析主机名...")
        target_ip = resolve_hostname(parsed_args.target)
        
        if not target_ip:
            print(f"错误: 无法解析主机名 '{parsed_args.target}'")
            return 1
        
        if target_ip != parsed_args.target:
            print(f"解析结果: {parsed_args.target} -> {target_ip}")
        
        # 验证IP地址
        if not validate_ip(target_ip):
            print(f"错误: 无效的IP地址 '{target_ip}'")
            return 1
        
        # 检查主机可达性（可选）
        if parsed_args.verbose:
            print("检查主机可达性...")
            reachable = check_host_reachable(target_ip, timeout=2.0)
            if reachable:
                print("主机可达")
            else:
                print("警告: 主机可能不可达，但将继续扫描")
        
        # 创建扫描器
        scanner = PortScanner(
            timeout=parsed_args.timeout,
            max_workers=parsed_args.workers
        )
        
        # 设置回调函数
        if not parsed_args.verbose:
            # 非详细模式下显示进度条
            scanner.set_progress_callback(
                lambda current, total: print_progress(current, total)
            )
        
        # 执行扫描
        print("\n开始扫描...")
        start_time = time.time()
        
        results = scanner.scan_ports(
            host=target_ip,
            ports=ports,
            scan_type=parsed_args.scan_type
        )
        
        scan_time = time.time() - start_time
        print(f"\n扫描完成! 耗时: {scan_time:.2f}秒")
        
        # 获取统计信息
        stats = scanner.get_statistics()
        
        # 根据需要过滤结果
        if parsed_args.open_only:
            results = scanner.get_open_ports()
            print(f"开放端口数: {len(results)}")
        
        # 输出结果
        formatter = create_formatter(parsed_args.output_format)
        formatter.output(results, stats)
        
        # 打印摘要
        if parsed_args.verbose:
            print_scan_summary(stats)
        
        # 返回退出码
        if stats.get("open_ports", 0) > 0:
            return 0  # 有开放端口，成功
        else:
            return 0  # 没有开放端口也是正常情况
            
    except KeyboardInterrupt:
        print("\n\n扫描被用户中断")
        return 130
    except Exception as e:
        print(f"\n错误: {str(e)}")
        if args and "-v" in args or "--verbose" in args:
            import traceback
            traceback.print_exc()
        return 1


def run_interactive() -> int:
    """
    交互式运行模式
    :return: 退出码
    """
    print_banner()
    print("进入交互式模式")
    print("=" * 50)
    
    try:
        # 获取目标主机
        target = input("请输入目标主机 (IP地址或域名): ").strip()
        if not target:
            print("错误: 目标主机不能为空")
            return 1
        
        # 获取端口范围
        ports_str = input("请输入端口范围 (默认: 1-1024): ").strip()
        if not ports_str:
            ports_str = "1-1024"
        
        # 获取扫描类型
        scan_type = input("请选择扫描类型 (tcp/udp, 默认: tcp): ").strip().lower()
        if scan_type not in ["tcp", "udp"]:
            scan_type = "tcp"
        
        # 获取超时时间
        timeout_str = input("请输入超时时间 (秒, 默认: 1.0): ").strip()
        try:
            timeout = float(timeout_str) if timeout_str else 1.0
        except ValueError:
            timeout = 1.0
        
        # 获取线程数
        workers_str = input("请输入并发线程数 (默认: 100): ").strip()
        try:
            workers = int(workers_str) if workers_str else 100
        except ValueError:
            workers = 100
        
        # 构建参数列表
        args = [target, "-p", ports_str, "-s", scan_type, "-t", str(timeout), "-w", str(workers)]
        
        # 调用主函数
        return main(args)
        
    except KeyboardInterrupt:
        print("\n\n程序被用户中断")
        return 130
    except Exception as e:
        print(f"\n错误: {str(e)}")
        return 1


def run_quick_scan(target: str, ports: str = "1-1024") -> int:
    """
    快速扫描模式
    :param target: 目标主机
    :param ports: 端口范围
    :return: 退出码
    """
    args = [target, "-p", ports, "-o", "text", "--open-only"]
    return main(args)


if __name__ == "__main__":
    # 检查是否有交互式参数
    if len(sys.argv) > 1 and sys.argv[1] == "--interactive":
        sys.exit(run_interactive())
    else:
        sys.exit(main())