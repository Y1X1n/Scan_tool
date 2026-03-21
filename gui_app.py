#!/usr/bin/env python3
"""
端口扫描器桌面GUI
基于Tkinter实现的图形化界面
"""
import sys
import os
import threading
import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from scanner.args_parser import parse_ports
from scanner.network_utils import resolve_hostname, validate_ip
from scanner.scanner import PortScanner, ScanStatus
from scanner.output import TextFormatter, JSONFormatter, CSVFormatter


class PortScannerGUI:
    """端口扫描器GUI类"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("端口扫描器 v1.0.0")
        self.root.geometry("900x700")
        self.root.minsize(800, 600)
        
        # 设置图标（如果有的话）
        try:
            self.root.iconbitmap("icon.ico")
        except:
            pass
        
        # 扫描器实例
        self.scanner = None
        self.scanning = False
        self.results = []
        
        # 创建界面
        self.create_widgets()
        
        # 绑定关闭事件
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def create_widgets(self):
        """创建界面组件"""
        # 创建主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 配置网格权重
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(5, weight=1)
        
        # 标题
        title_label = ttk.Label(main_frame, text="端口扫描器", font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # 扫描配置框架
        config_frame = ttk.LabelFrame(main_frame, text="扫描配置", padding="10")
        config_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        config_frame.columnconfigure(1, weight=1)
        
        # 目标主机
        ttk.Label(config_frame, text="目标主机:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        self.target_var = tk.StringVar(value="127.0.0.1")
        self.target_entry = ttk.Entry(config_frame, textvariable=self.target_var, width=30)
        self.target_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 10))
        
        # 端口范围
        ttk.Label(config_frame, text="端口范围:").grid(row=0, column=2, sticky=tk.W, padx=(0, 10))
        self.ports_var = tk.StringVar(value="1-1024")
        self.ports_entry = ttk.Entry(config_frame, textvariable=self.ports_var, width=20)
        self.ports_entry.grid(row=0, column=3, sticky=(tk.W, tk.E))
        
        # 扫描类型
        ttk.Label(config_frame, text="扫描类型:").grid(row=1, column=0, sticky=tk.W, padx=(0, 10), pady=(10, 0))
        self.scan_type_var = tk.StringVar(value="tcp")
        scan_type_combo = ttk.Combobox(config_frame, textvariable=self.scan_type_var, 
                                       values=["tcp", "udp"], state="readonly", width=10)
        scan_type_combo.grid(row=1, column=1, sticky=tk.W, padx=(0, 10), pady=(10, 0))
        
        # 超时时间
        ttk.Label(config_frame, text="超时(秒):").grid(row=1, column=2, sticky=tk.W, padx=(0, 10), pady=(10, 0))
        self.timeout_var = tk.StringVar(value="1.0")
        timeout_spin = ttk.Spinbox(config_frame, textvariable=self.timeout_var, 
                                   from_=0.1, to=10.0, increment=0.1, width=10)
        timeout_spin.grid(row=1, column=3, sticky=tk.W, pady=(10, 0))
        
        # 并发线程数
        ttk.Label(config_frame, text="并发线程:").grid(row=2, column=0, sticky=tk.W, padx=(0, 10), pady=(10, 0))
        self.workers_var = tk.IntVar(value=100)
        workers_scale = ttk.Scale(config_frame, variable=self.workers_var, 
                                  from_=10, to=500, orient=tk.HORIZONTAL)
        workers_scale.grid(row=2, column=1, sticky=(tk.W, tk.E), padx=(0, 10), pady=(10, 0))
        self.workers_label = ttk.Label(config_frame, text="100")
        self.workers_label.grid(row=2, column=2, sticky=tk.W, pady=(10, 0))
        
        # 更新线程数显示
        def update_workers_label(*args):
            self.workers_label.config(text=str(int(self.workers_var.get())))
        self.workers_var.trace("w", update_workers_label)
        
        # 按钮框架
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=2, column=0, columnspan=3, pady=10)
        
        # 开始扫描按钮
        self.start_btn = ttk.Button(button_frame, text="开始扫描", command=self.start_scan)
        self.start_btn.grid(row=0, column=0, padx=(0, 10))
        
        # 停止扫描按钮
        self.stop_btn = ttk.Button(button_frame, text="停止扫描", command=self.stop_scan, state=tk.DISABLED)
        self.stop_btn.grid(row=0, column=1, padx=(0, 10))
        
        # 清空结果按钮
        self.clear_btn = ttk.Button(button_frame, text="清空结果", command=self.clear_results)
        self.clear_btn.grid(row=0, column=2, padx=(0, 10))
        
        # 导出结果按钮
        self.export_btn = ttk.Button(button_frame, text="导出结果", command=self.export_results, state=tk.DISABLED)
        self.export_btn.grid(row=0, column=3)
        
        # 进度条
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(main_frame, variable=self.progress_var, maximum=100)
        self.progress_bar.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # 状态标签
        self.status_var = tk.StringVar(value="就绪")
        status_label = ttk.Label(main_frame, textvariable=self.status_var)
        status_label.grid(row=4, column=0, columnspan=3, sticky=tk.W, pady=(0, 10))
        
        # 结果框架
        result_frame = ttk.LabelFrame(main_frame, text="扫描结果", padding="10")
        result_frame.grid(row=5, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S))
        result_frame.columnconfigure(0, weight=1)
        result_frame.rowconfigure(0, weight=1)
        
        # 结果文本框
        self.result_text = scrolledtext.ScrolledText(result_frame, height=15, state=tk.DISABLED)
        self.result_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 统计信息框架
        stats_frame = ttk.LabelFrame(main_frame, text="统计信息", padding="10")
        stats_frame.grid(row=6, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(10, 0))
        
        # 统计标签
        self.total_label = ttk.Label(stats_frame, text="总端口: 0")
        self.total_label.grid(row=0, column=0, padx=(0, 20))
        
        self.open_label = ttk.Label(stats_frame, text="开放: 0", foreground="green")
        self.open_label.grid(row=0, column=1, padx=(0, 20))
        
        self.closed_label = ttk.Label(stats_frame, text="关闭: 0", foreground="red")
        self.closed_label.grid(row=0, column=2, padx=(0, 20))
        
        self.filtered_label = ttk.Label(stats_frame, text="过滤: 0", foreground="orange")
        self.filtered_label.grid(row=0, column=3, padx=(0, 20))
        
        self.time_label = ttk.Label(stats_frame, text="耗时: 0.00秒")
        self.time_label.grid(row=0, column=4)
        
        # 菜单栏
        self.create_menu()
    
    def create_menu(self):
        """创建菜单栏"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # 文件菜单
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="文件", menu=file_menu)
        file_menu.add_command(label="导出结果", command=self.export_results)
        file_menu.add_separator()
        file_menu.add_command(label="退出", command=self.on_closing)
        
        # 工具菜单
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="工具", menu=tools_menu)
        tools_menu.add_command(label="快速扫描", command=self.quick_scan)
        tools_menu.add_command(label="清空结果", command=self.clear_results)
        
        # 帮助菜单
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="帮助", menu=help_menu)
        help_menu.add_command(label="使用说明", command=self.show_help)
        help_menu.add_command(label="关于", command=self.show_about)
    
    def start_scan(self):
        """开始扫描"""
        # 验证输入
        target = self.target_var.get().strip()
        ports_str = self.ports_var.get().strip()
        
        if not target:
            messagebox.showerror("错误", "请输入目标主机")
            return
        
        if not ports_str:
            messagebox.showerror("错误", "请输入端口范围")
            return
        
        try:
            timeout = float(self.timeout_var.get())
            if timeout <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("错误", "超时时间必须大于0")
            return
        
        try:
            workers = int(self.workers_var.get())
            if workers <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("错误", "线程数必须大于0")
            return
        
        # 解析主机名
        ip = resolve_hostname(target)
        if not ip:
            messagebox.showerror("错误", f"无法解析主机名: {target}")
            return
        
        if not validate_ip(ip):
            messagebox.showerror("错误", f"无效的IP地址: {ip}")
            return
        
        # 解析端口
        try:
            ports = parse_ports(ports_str)
        except Exception as e:
            messagebox.showerror("错误", f"端口格式错误: {str(e)}")
            return
        
        # 更新UI状态
        self.scanning = True
        self.start_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)
        self.export_btn.config(state=tk.DISABLED)
        self.progress_var.set(0)
        self.status_var.set("正在扫描...")
        
        # 清空结果
        self.result_text.config(state=tk.NORMAL)
        self.result_text.delete(1.0, tk.END)
        self.result_text.config(state=tk.DISABLED)
        
        # 在后台线程中执行扫描
        def run_scan():
            try:
                start_time = datetime.now()
                
                self.scanner = PortScanner(timeout=timeout, max_workers=workers)
                
                # 设置进度回调
                def update_progress(current, total):
                    progress = (current / total) * 100
                    self.root.after(0, lambda: self.progress_var.set(progress))
                    self.root.after(0, lambda: self.status_var.set(f"扫描进度: {current}/{total}"))
                
                self.scanner.set_progress_callback(update_progress)
                
                # 执行扫描
                self.results = self.scanner.scan_ports(ip, ports, self.scan_type_var.get())
                
                # 计算耗时
                end_time = datetime.now()
                scan_time = (end_time - start_time).total_seconds()
                
                # 更新UI
                self.root.after(0, lambda: self.scan_complete(scan_time))
                
            except Exception as e:
                self.root.after(0, lambda: self.scan_error(str(e)))
        
        thread = threading.Thread(target=run_scan)
        thread.daemon = True
        thread.start()
    
    def stop_scan(self):
        """停止扫描"""
        if self.scanner:
            self.scanner.stop_scan()
        self.scanning = False
        self.status_var.set("扫描已停止")
        self.reset_ui()
    
    def scan_complete(self, scan_time):
        """扫描完成"""
        self.scanning = False
        self.status_var.set(f"扫描完成! 耗时: {scan_time:.2f}秒")
        self.reset_ui()
        
        # 显示结果
        self.display_results()
        
        # 更新统计信息
        stats = self.scanner.get_statistics()
        self.update_statistics(stats, scan_time)
        
        self.export_btn.config(state=tk.NORMAL)
    
    def scan_error(self, error_msg):
        """扫描错误"""
        self.scanning = False
        self.status_var.set(f"扫描错误: {error_msg}")
        self.reset_ui()
        messagebox.showerror("扫描错误", error_msg)
    
    def reset_ui(self):
        """重置UI状态"""
        self.start_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
        self.progress_var.set(0)
    
    def display_results(self):
        """显示扫描结果"""
        self.result_text.config(state=tk.NORMAL)
        self.result_text.delete(1.0, tk.END)
        
        # 按端口排序
        sorted_results = sorted(self.results, key=lambda x: x.port)
        
        # 显示结果
        for result in sorted_results:
            status_color = {
                ScanStatus.OPEN: "green",
                ScanStatus.CLOSED: "red",
                ScanStatus.FILTERED: "orange",
                ScanStatus.ERROR: "gray"
            }.get(result.status, "black")
            
            status_text = {
                ScanStatus.OPEN: "开放",
                ScanStatus.CLOSED: "关闭",
                ScanStatus.FILTERED: "过滤",
                ScanStatus.ERROR: "错误"
            }.get(result.status, "未知")
            
            line = f"端口 {result.port:5d} | {status_text:4s} | {result.service:15s} | {result.response_time*1000:8.2f}ms\n"
            
            self.result_text.insert(tk.END, line)
            
            # 设置颜色
            line_start = self.result_text.index(tk.END + "-1c linestart")
            line_end = self.result_text.index(tk.END + "-1c lineend")
            
            # 设置状态部分的颜色
            status_start = f"{line_start} + 14c"
            status_end = f"{line_start} + 18c"
            self.result_text.tag_add(status_text, status_start, status_end)
            self.result_text.tag_config(status_text, foreground=status_color)
        
        self.result_text.config(state=tk.DISABLED)
    
    def update_statistics(self, stats, scan_time):
        """更新统计信息"""
        self.total_label.config(text=f"总端口: {stats['total_ports']}")
        self.open_label.config(text=f"开放: {stats['open_ports']}")
        self.closed_label.config(text=f"关闭: {stats['closed_ports']}")
        self.filtered_label.config(text=f"过滤: {stats['filtered_ports']}")
        self.time_label.config(text=f"耗时: {scan_time:.2f}秒")
    
    def clear_results(self):
        """清空结果"""
        self.result_text.config(state=tk.NORMAL)
        self.result_text.delete(1.0, tk.END)
        self.result_text.config(state=tk.DISABLED)
        
        self.total_label.config(text="总端口: 0")
        self.open_label.config(text="开放: 0")
        self.closed_label.config(text="关闭: 0")
        self.filtered_label.config(text="过滤: 0")
        self.time_label.config(text="耗时: 0.00秒")
        
        self.results = []
        self.export_btn.config(state=tk.DISABLED)
        self.status_var.set("结果已清空")
    
    def export_results(self):
        """导出结果"""
        if not self.results:
            messagebox.showwarning("警告", "没有可导出的结果")
            return
        
        # 选择文件类型
        file_types = [
            ("JSON文件", "*.json"),
            ("CSV文件", "*.csv"),
            ("文本文件", "*.txt"),
            ("所有文件", "*.*")
        ]
        
        filename = filedialog.asksaveasfilename(
            title="导出结果",
            filetypes=file_types,
            defaultextension=".json"
        )
        
        if not filename:
            return
        
        try:
            # 根据扩展名选择格式
            ext = os.path.splitext(filename)[1].lower()
            
            if ext == '.json':
                formatter = JSONFormatter()
            elif ext == '.csv':
                formatter = CSVFormatter()
            else:
                formatter = TextFormatter()
            
            output = formatter.format_results(self.results, self.scanner.get_statistics())
            
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(output)
            
            messagebox.showinfo("成功", f"结果已导出到: {filename}")
            
        except Exception as e:
            messagebox.showerror("错误", f"导出失败: {str(e)}")
    
    def quick_scan(self):
        """快速扫描"""
        self.target_var.set("127.0.0.1")
        self.ports_var.set("80,443,22,21,25,53,110,143,993,995")
        self.start_scan()
    
    def show_help(self):
        """显示帮助"""
        help_text = """
端口扫描器使用说明

1. 目标主机: 输入要扫描的IP地址或域名
2. 端口范围: 支持多种格式
   - 单个端口: 80
   - 端口列表: 80,443,8080
   - 端口范围: 1-1024
   - 混合格式: 22,80,443,8000-9000

3. 扫描类型:
   - TCP连接扫描: 完整的TCP三次握手，准确但较慢
   - UDP扫描: 发送UDP数据包，速度快但可能不准确

4. 超时时间: 连接超时时间，网络慢时可适当增加

5. 并发线程数: 同时扫描的端口数量，数值越大速度越快

注意事项:
- 请确保有足够的权限进行网络扫描
- 扫描大量端口可能需要较长时间
- 请遵守相关法律法规，只在授权范围内使用
        """
        
        help_window = tk.Toplevel(self.root)
        help_window.title("使用说明")
        help_window.geometry("500x400")
        help_window.transient(self.root)
        
        text_widget = scrolledtext.ScrolledText(help_window, wrap=tk.WORD, padx=10, pady=10)
        text_widget.pack(fill=tk.BOTH, expand=True)
        text_widget.insert(tk.END, help_text)
        text_widget.config(state=tk.DISABLED)
    
    def show_about(self):
        """显示关于信息"""
        about_text = """
端口扫描器 v1.0.0

基于Python实现的简易端口扫描器

功能特性:
- 支持TCP/UDP扫描
- 多线程并发扫描
- 多种输出格式
- 图形化界面

作者: 基于Python的简易端口扫描器设计与实现
        """
        
        messagebox.showinfo("关于", about_text)
    
    def on_closing(self):
        """关闭窗口事件"""
        if self.scanning:
            if messagebox.askokcancel("确认", "扫描正在进行中，确定要退出吗？"):
                if self.scanner:
                    self.scanner.stop_scan()
                self.root.destroy()
        else:
            self.root.destroy()
    
    def run(self):
        """运行应用程序"""
        self.root.mainloop()


def main():
    """主函数"""
    app = PortScannerGUI()
    app.run()


if __name__ == "__main__":
    main()