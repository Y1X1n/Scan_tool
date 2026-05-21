"""
输出模块
负责格式化扫描结果并输出到不同格式
"""
import json
import csv
import io
import sys
from typing import List, Dict, Any, TextIO
from datetime import datetime

from .scanner import ScanResult, ScanStatus


class OutputFormatter:
    """输出格式化器基类"""
    
    def __init__(self, output_file: TextIO = None):
        """
        初始化输出格式化器
        :param output_file: 输出文件对象，默认为stdout
        """
        self.output_file = output_file or sys.stdout
    
    def format_results(self, results: List[ScanResult], stats: Dict[str, Any] = None) -> str:
        """
        格式化扫描结果
        :param results: 扫描结果列表
        :param stats: 统计信息
        :return: 格式化后的字符串
        """
        raise NotImplementedError
    
    def output(self, results: List[ScanResult], stats: Dict[str, Any] = None) -> None:
        """
        输出扫描结果
        :param results: 扫描结果列表
        :param stats: 统计信息
        """
        formatted = self.format_results(results, stats)
        self.output_file.write(formatted)
        self.output_file.flush()


class TextFormatter(OutputFormatter):
    """文本格式化器"""
    
    def format_results(self, results: List[ScanResult], stats: Dict[str, Any] = None) -> str:
        """
        格式化为文本格式
        :param results: 扫描结果列表
        :param stats: 统计信息
        :return: 格式化后的文本
        """
        output_lines = []
        
        # 添加标题
        if results:
            host = results[0].host
            output_lines.append(f"端口扫描报告 - {host}")
            output_lines.append("=" * 50)
            output_lines.append("")
        
        # 添加统计信息
        if stats:
            output_lines.append("扫描统计:")
            output_lines.append(f"  总端口数: {stats.get('total_ports', 0)}")
            output_lines.append(f"  已扫描: {stats.get('scanned_ports', 0)}")
            output_lines.append(f"  开放: {stats.get('open_ports', 0)}")
            output_lines.append(f"  关闭: {stats.get('closed_ports', 0)}")
            output_lines.append(f"  过滤: {stats.get('filtered_ports', 0)}")
            output_lines.append(f"  错误: {stats.get('error_ports', 0)}")
            output_lines.append("")
        
        # 添加结果表格
        if results:
            output_lines.append("扫描结果:")
            output_lines.append("-" * 70)
            output_lines.append(f"{'端口':<10} {'状态':<12} {'服务':<15} {'响应时间(ms)':<15}")
            output_lines.append("-" * 70)
            
            # 按端口排序
            sorted_results = sorted(results, key=lambda x: x.port)
            
            for result in sorted_results:
                status_str = result.status.value.upper()
                
                # 根据状态添加颜色代码（如果支持）
                if result.status == ScanStatus.OPEN:
                    status_str = f"\033[32m{status_str}\033[0m"  # 绿色
                elif result.status == ScanStatus.FILTERED:
                    status_str = f"\033[33m{status_str}\033[0m"  # 黄色
                elif result.status == ScanStatus.ERROR:
                    status_str = f"\033[31m{status_str}\033[0m"  # 红色
                
                response_time = f"{result.response_time * 1000:.2f}"
                
                output_lines.append(
                    f"{result.port:<10} {status_str:<12} {result.service:<15} {response_time:<15}"
                )
            
            output_lines.append("-" * 70)
        
        # 添加时间戳
        output_lines.append("")
        output_lines.append(f"扫描完成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        return "\n".join(output_lines)


class JSONFormatter(OutputFormatter):
    """JSON格式化器"""
    
    def format_results(self, results: List[ScanResult], stats: Dict[str, Any] = None) -> str:
        """
        格式化为JSON格式
        :param results: 扫描结果列表
        :param stats: 统计信息
        :return: JSON字符串
        """
        output_data = {
            "scan_time": datetime.now().isoformat(),
            "statistics": stats or {},
            "results": []
        }
        
        # 添加结果
        for result in results:
            result_data = {
                "host": result.host,
                "port": result.port,
                "status": result.status.value,
                "service": result.service,
                "response_time": result.response_time,
            }
            
            if result.error:
                result_data["error"] = result.error
            
            output_data["results"].append(result_data)
        
        return json.dumps(output_data, indent=2, ensure_ascii=False)


class CSVFormatter(OutputFormatter):
    """CSV格式化器"""
    
    def format_results(self, results: List[ScanResult], stats: Dict[str, Any] = None) -> str:
        """
        格式化为CSV格式
        :param results: 扫描结果列表
        :param stats: 统计信息
        :return: CSV字符串
        """
        output = io.StringIO()
        writer = csv.writer(output)
        
        # 写入标题行
        writer.writerow(["Host", "Port", "Status", "Service", "ResponseTime(ms)", "Error"])
        
        # 写入数据行
        for result in sorted(results, key=lambda x: x.port):
            writer.writerow([
                result.host,
                result.port,
                result.status.value,
                result.service,
                f"{result.response_time * 1000:.2f}",
                result.error or ""
            ])
        
        return output.getvalue()


class HTMLFormatter(OutputFormatter):
    """HTML格式化器"""
    
    def format_results(self, results: List[ScanResult], stats: Dict[str, Any] = None) -> str:
        """
        格式化为HTML格式
        :param results: 扫描结果列表
        :param stats: 统计信息
        :return: HTML字符串
        """
        html = []
        html.append("<!DOCTYPE html>")
        html.append("<html lang='zh-CN'>")
        html.append("<head>")
        html.append("  <meta charset='UTF-8'>")
        html.append("  <title>端口扫描报告</title>")
        html.append("  <style>")
        html.append("    body { font-family: Arial, sans-serif; margin: 20px; }")
        html.append("    h1 { color: #333; }")
        html.append("    .stats { background: #f5f5f5; padding: 15px; border-radius: 5px; margin: 20px 0; }")
        html.append("    table { border-collapse: collapse; width: 100%; }")
        html.append("    th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }")
        html.append("    th { background-color: #4CAF50; color: white; }")
        html.append("    tr:nth-child(even) { background-color: #f2f2f2; }")
        html.append("    .open { color: green; font-weight: bold; }")
        html.append("    .closed { color: red; }")
        html.append("    .filtered { color: orange; }")
        html.append("    .error { color: red; }")
        html.append("  </style>")
        html.append("</head>")
        html.append("<body>")
        
        # 标题
        if results:
            host = results[0].host
            html.append(f"<h1>端口扫描报告 - {host}</h1>")
        
        # 统计信息
        if stats:
            html.append("<div class='stats'>")
            html.append("<h2>扫描统计</h2>")
            html.append(f"<p>总端口数: {stats.get('total_ports', 0)}</p>")
            html.append(f"<p>开放端口: {stats.get('open_ports', 0)}</p>")
            html.append(f"<p>关闭端口: {stats.get('closed_ports', 0)}</p>")
            html.append("</div>")
        
        # 结果表格
        html.append("<h2>扫描结果</h2>")
        html.append("<table>")
        html.append("  <tr>")
        html.append("    <th>端口</th>")
        html.append("    <th>状态</th>")
        html.append("    <th>服务</th>")
        html.append("    <th>响应时间</th>")
        html.append("  </tr>")
        
        for result in sorted(results, key=lambda x: x.port):
            status_class = result.status.value.lower()
            status_text = result.status.value.upper()
            
            html.append("  <tr>")
            html.append(f"    <td>{result.port}</td>")
            html.append(f"    <td class='{status_class}'>{status_text}</td>")
            html.append(f"    <td>{result.service}</td>")
            html.append(f"    <td>{result.response_time * 1000:.2f} ms</td>")
            html.append("  </tr>")
        
        html.append("</table>")
        
        # 时间戳
        html.append(f"<p>扫描完成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>")
        
        html.append("</body>")
        html.append("</html>")
        
        return "\n".join(html)


def create_formatter(format_type: str, output_file: TextIO = None) -> OutputFormatter:
    """
    创建格式化器工厂函数
    :param format_type: 格式类型 (text, json, csv, html)
    :param output_file: 输出文件对象
    :return: 格式化器实例
    """
    formatters = {
        "text": TextFormatter,
        "json": JSONFormatter,
        "csv": CSVFormatter,
        "html": HTMLFormatter
    }
    
    formatter_class = formatters.get(format_type.lower(), TextFormatter)
    return formatter_class(output_file)


def print_banner() -> None:
    """打印程序横幅"""
    banner = r"""
    ____             __                  _____                                 
   / __ \____  _____/ /_____  _____     / ___/_________ _____  ____  ___  _____
  / /_/ / __ \/ ___/ //_/ _ \/ ___/     \__ \/ ___/ __ `/ __ \/ __ \/ _ \/ ___/
 / ____/ /_/ / /  / ,< /  __/ /         ___/ / /__/ /_/ / / / / / / /  __/ /    
/_/    \____/_/  /_/|_|\___/_/         /____/\___/\__,_/_/ /_/_/ /_/\___/_/     
                                                                                
"""
    print(banner)
    print("简易端口扫描器 v3.0.1")
    print("基于Python实现")
    print("=" * 50)


def print_progress(current: int, total: int, width: int = 50) -> None:
    """
    打印进度条
    :param current: 当前进度
    :param total: 总数
    :param width: 进度条宽度
    """
    if total == 0:
        return
    
    percent = current / total
    filled = int(width * percent)
    bar = "█" * filled + "░" * (width - filled)
    
    sys.stdout.write(f"\r扫描进度: [{bar}] {percent:.1%} ({current}/{total})")
    sys.stdout.flush()
    
    if current == total:
        print()  # 完成后换行


def print_scan_summary(stats: Dict[str, Any]) -> None:
    """
    打印扫描摘要
    :param stats: 统计信息
    """
    print("\n" + "=" * 50)
    print("扫描摘要:")
    print(f"  开放端口: {stats.get('open_ports', 0)}")
    print(f"  关闭端口: {stats.get('closed_ports', 0)}")
    print(f"  过滤端口: {stats.get('filtered_ports', 0)}")
    print(f"  错误数量: {stats.get('error_ports', 0)}")
    print("=" * 50)