#!/usr/bin/env python3
"""
端口扫描器启动脚本
提供便捷的命令行入口
"""
import sys
from scanner.main import main, run_interactive, run_quick_scan


def show_help():
    """显示帮助信息"""
    help_text = """
端口扫描器使用方法:

1. 命令行模式:
   python run.py <目标> [选项]
   
   示例:
   python run.py 192.168.1.1                 # 扫描默认端口 (1-1024)
   python run.py 192.168.1.1 -p 80,443       # 扫描指定端口
   python run.py 192.168.1.1 -p 1-1000       # 扫描端口范围
   python run.py example.com -t 0.5 -w 100   # 设置超时和线程数

2. 交互式模式:
   python run.py --interactive

3. 快速扫描模式:
   python run.py --quick <目标> [端口范围]
   
   示例:
   python run.py --quick 192.168.1.1         # 快速扫描默认端口
   python run.py --quick 192.168.1.1 80-443  # 快速扫描指定范围

4. 查看帮助:
   python run.py --help

参数说明:
  -p, --ports     端口列表，用逗号分隔或范围 (例如: 80,443 或 1-1000)
  -s, --scan-type 扫描类型: tcp (默认), udp
  -t, --timeout   连接超时时间 (秒)，默认: 1.0
  -w, --workers   并发线程数，默认: 100
  -o, --output    输出格式: text (默认), json, csv
  -v, --verbose   显示详细扫描信息
  --open-only     只显示开放的端口
  --version       显示版本信息

注意事项:
  - 请确保有足够的权限进行网络扫描
  - 扫描大量端口可能需要较长时间
  - 请遵守相关法律法规，只在授权范围内使用
"""
    print(help_text)


if __name__ == "__main__":
    # 检查参数
    if len(sys.argv) == 1:
        # 没有参数，显示帮助
        show_help()
        sys.exit(0)
    
    # 检查特殊参数
    if sys.argv[1] in ["--help", "-h", "help"]:
        show_help()
        sys.exit(0)
    
    if sys.argv[1] == "--interactive":
        sys.exit(run_interactive())
    
    if sys.argv[1] == "--quick":
        if len(sys.argv) < 3:
            print("错误: 快速扫描模式需要指定目标主机")
            print("用法: python run.py --quick <目标> [端口范围]")
            sys.exit(1)
        
        target = sys.argv[2]
        ports = sys.argv[3] if len(sys.argv) > 3 else "1-1024"
        sys.exit(run_quick_scan(target, ports))
    
    # 普通模式
    sys.exit(main())