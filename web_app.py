#!/usr/bin/env python3
"""
端口扫描器Web界面
基于Flask实现的图形化界面
"""
import os
import json
import threading
from datetime import datetime

from flask import Flask, render_template, request, jsonify, Response
from scanner.args_parser import parse_ports
from scanner.network_utils import resolve_hostname, validate_ip
from scanner.scanner import PortScanner, ScanStatus
from scanner.output import JSONFormatter

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('FLASK_SECRET_KEY', os.urandom(24).hex())

# 全局变量存储扫描状态
scan_status = {
    'running': False,
    'progress': 0,
    'total': 0,
    'results': [],
    'error': None,
    'statistics': None,
}
scan_status_lock = threading.Lock()


@app.route('/')
def index():
    """主页"""
    return render_template('index.html')


@app.route('/api/scan', methods=['POST'])
def start_scan():
    """开始扫描API"""
    global scan_status
    
    with scan_status_lock:
        if scan_status['running']:
            return jsonify({'error': '扫描正在进行中'}), 400
    
    try:
        data = request.get_json()
        target = data.get('target', '').strip()
        ports_str = data.get('ports', '1-1024').strip()
        scan_type = data.get('scan_type', 'tcp')
        timeout = float(data.get('timeout', 1.0))
        workers = int(data.get('workers', 100))
        
        # 验证输入
        if not target:
            return jsonify({'error': '请输入目标主机'}), 400
        
        # 解析主机名
        ip = resolve_hostname(target)
        if not ip:
            return jsonify({'error': f'无法解析主机名: {target}'}), 400
        
        if not validate_ip(ip):
            return jsonify({'error': f'无效的IP地址: {ip}'}), 400
        
        # 解析端口
        try:
            ports = parse_ports(ports_str)
        except Exception as e:
            return jsonify({'error': f'端口格式错误: {str(e)}'}), 400
        
        # 重置扫描状态（加锁保护）
        with scan_status_lock:
            scan_status = {
                'running': True,
                'progress': 0,
                'total': len(ports),
                'results': [],
                'error': None,
                'statistics': None,
                'target': target,
                'ip': ip,
                'start_time': datetime.now().isoformat(),
            }
        
        # 在后台线程中执行扫描
        def run_scan():
            global scan_status
            try:
                scanner = PortScanner(timeout=timeout, max_workers=workers)
                
                # 设置进度回调
                def update_progress(current, total):
                    with scan_status_lock:
                        scan_status['progress'] = current
                
                scanner.set_progress_callback(update_progress)
                
                # 执行扫描
                results = scanner.scan_ports(ip, ports, scan_type)
                
                # 转换结果格式
                formatted_results = []
                for r in results:
                    formatted_results.append({
                        'host': r.host,
                        'port': r.port,
                        'status': r.status.value,
                        'service': r.service,
                        'response_time': round(r.response_time * 1000, 2)
                    })
                
                with scan_status_lock:
                    scan_status['results'] = formatted_results
                    scan_status['statistics'] = scanner.get_statistics()
                    scan_status['end_time'] = datetime.now().isoformat()
                
            except Exception as e:
                with scan_status_lock:
                    scan_status['error'] = str(e)
            finally:
                with scan_status_lock:
                    scan_status['running'] = False
        
        thread = threading.Thread(target=run_scan)
        thread.daemon = True
        thread.start()
        
        return jsonify({'message': '扫描已开始', 'total_ports': len(ports)})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/status')
def get_status():
    """获取扫描状态API"""
    with scan_status_lock:
        return jsonify(scan_status.copy())


@app.route('/api/stop', methods=['POST'])
def stop_scan():
    """停止扫描API"""
    global scan_status
    with scan_status_lock:
        scan_status['running'] = False
    return jsonify({'message': '扫描已停止'})


@app.route('/api/export/<format>')
def export_results(format):
    """导出结果API"""
    with scan_status_lock:
        if not scan_status.get('results'):
            return jsonify({'error': '没有可导出的结果'}), 400
        results_snapshot = list(scan_status['results'])
        stats_snapshot = scan_status.get('statistics')
    
    try:
        from scanner.scanner import ScanResult
        
        # 转换回ScanResult对象
        results = []
        for r in results_snapshot:
            results.append(ScanResult(
                host=r['host'],
                port=r['port'],
                status=ScanStatus(r['status']),
                service=r['service'],
                response_time=r['response_time'] / 1000
            ))
        
        if format == 'json':
            formatter = JSONFormatter()
            output = formatter.format_results(results, stats_snapshot)
            return Response(
                output,
                mimetype='application/json',
                headers={'Content-Disposition': 'attachment;filename=scan_results.json'}
            )
        elif format == 'csv':
            from scanner.output import CSVFormatter
            formatter = CSVFormatter()
            output = formatter.format_results(results, stats_snapshot)
            return Response(
                output,
                mimetype='text/csv',
                headers={'Content-Disposition': 'attachment;filename=scan_results.csv'}
            )
        else:
            return jsonify({'error': '不支持的导出格式'}), 400
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500


def main():
    """启动Web服务器"""
    os.makedirs('templates', exist_ok=True)
    os.makedirs('static', exist_ok=True)
    
    print("=" * 50)
    print("端口扫描器Web界面")
    print("=" * 50)
    print("正在启动Web服务器...")
    print("请在浏览器中访问: http://127.0.0.1:5000")
    print("按Ctrl+C停止服务器")
    print("=" * 50)
    
    app.run(debug=False, host='127.0.0.1', port=5000)


if __name__ == '__main__':
    main()