# 基于Python的简易端口扫描器

一个功能完整、模块化的端口扫描工具，支持TCP/UDP扫描、多线程并发、多种输出格式。

## 项目特性

- 🔍 **多种扫描模式**: 支持TCP连接扫描和UDP扫描
- ⚡ **高性能**: 使用线程池并发扫描，支持自定义线程数
- 📊 **多种输出格式**: 支持文本、JSON、CSV、HTML格式输出
- 🎯 **灵活的端口指定**: 支持单个端口、端口列表、端口范围
- 🖥️ **交互式模式**: 提供友好的交互式命令行界面
- 📈 **实时进度显示**: 显示扫描进度条和统计信息
- 🔧 **模块化设计**: 各功能模块独立，便于维护和扩展
- 🌐 **Web界面**: 提供美观的Web图形化界面
- 🖥️ **桌面GUI**: 基于Tkinter的桌面应用程序
- 📦 **可打包**: 支持打包成exe可执行文件

## 项目结构

```
Scan_tool/
├── scanner/                    # 主模块
│   ├── __init__.py            # 包初始化文件
│   ├── args_parser.py         # 参数解析模块
│   ├── network_utils.py       # 网络工具模块
│   ├── scanner.py             # 扫描核心模块
│   ├── output.py              # 输出格式化模块
│   └── main.py                # 主程序入口
├── templates/                  # Web界面模板
│   └── index.html             # 主页面模板
├── static/                     # 静态资源
│   └── style.css              # 样式文件
├── run.py                      # 命令行启动脚本
├── web_app.py                  # Web界面应用
├── gui_app.py                  # 桌面GUI应用
├── build_exe.py                # 打包脚本
├── test_scanner.py             # 测试脚本
├── requirements.txt            # 依赖列表
└── README.md                   # 项目说明文档
```

## 模块说明

### 1. 参数解析模块 (args_parser.py)
- 解析命令行参数
- 验证参数有效性
- 支持多种端口格式

### 2. 网络工具模块 (network_utils.py)
- 主机名解析
- IP地址验证
- 端口服务识别
- 主机可达性检查

### 3. 扫描核心模块 (scanner.py)
- TCP连接扫描
- UDP扫描
- 多线程并发扫描
- 异步扫描支持

### 4. 输出模块 (output.py)
- 文本格式输出
- JSON格式输出
- CSV格式输出
- HTML格式输出
- 进度条显示

### 5. 主程序 (main.py)
- 协调各个模块
- 提供命令行界面
- 支持交互式模式
- 快速扫描模式

## 安装与使用

### 环境要求
- Python 3.6+
- 操作系统: Windows/Linux/macOS

### 安装步骤

1. 克隆或下载项目
```bash
git clone <项目地址>
cd Scan_tool
```

2. 安装依赖（可选）
```bash
pip install -r requirements.txt
```

### 使用方法

#### 1. 命令行模式

```bash
# 扫描默认端口 (1-1024)
python run.py 192.168.1.1

# 扫描指定端口
python run.py 192.168.1.1 -p 80,443

# 扫描端口范围
python run.py 192.168.1.1 -p 1-1000

# 混合端口格式
python run.py 192.168.1.1 -p 22,80,443,8000-9000

# 设置超时和线程数
python run.py 192.168.1.1 -t 0.5 -w 200

# 只显示开放端口
python run.py 192.168.1.1 --open-only

# 输出为JSON格式
python run.py 192.168.1.1 -o json

# 输出为CSV格式
python run.py 192.168.1.1 -o csv

# 详细输出模式
python run.py 192.168.1.1 -v
```

#### 2. 交互式模式

```bash
python run.py --interactive
```

按照提示输入目标主机、端口范围等参数。

#### 3. 快速扫描模式

```bash
# 快速扫描默认端口
python run.py --quick 192.168.1.1

# 快速扫描指定端口范围
python run.py --quick 192.168.1.1 80-443
```

#### 4. 查看帮助

```bash
python run.py --help
```

#### 5. Web界面模式

```bash
# 启动Web界面
python web_app.py

# 然后在浏览器中访问: http://127.0.0.1:5000
```

Web界面提供以下功能：
- 图形化配置扫描参数
- 实时显示扫描进度和结果
- 支持导出JSON和CSV格式
- 响应式设计，支持移动设备

#### 6. 桌面GUI模式

```bash
# 启动桌面GUI
python gui_app.py
```

桌面GUI提供以下功能：
- 本地桌面应用程序
- 实时扫描进度显示
- 结果高亮显示（开放/关闭/过滤）
- 支持导出多种格式
- 内置使用说明和帮助

#### 7. 打包成exe文件

```bash
# 运行打包脚本
python build_exe.py

# 按照提示选择要打包的程序
# 打包完成后在dist目录生成exe文件
```

打包选项：
1. PortScanner - 命令行版本
2. PortScannerGUI - 桌面GUI版本  
3. PortScannerWeb - Web界面版本
4. 全部打包

生成的exe文件可直接双击运行，无需安装Python环境。

## 参数说明

| 参数 | 缩写 | 说明 | 默认值 |
|------|------|------|--------|
| target | - | 目标主机 (IP地址或域名) | 必需 |
| --ports | -p | 端口列表或范围 | 1-1024 |
| --scan-type | -s | 扫描类型 (tcp/udp) | tcp |
| --timeout | -t | 连接超时时间 (秒) | 1.0 |
| --workers | -w | 并发线程数 | 100 |
| --output | -o | 输出格式 (text/json/csv) | text |
| --verbose | -v | 详细输出模式 | false |
| --open-only | - | 只显示开放端口 | false |
| --interactive | - | 交互式模式 | - |
| --quick | - | 快速扫描模式 | - |

## 输出示例

### 文本格式
```
端口扫描报告 - 192.168.1.1
==================================================

扫描统计:
  总端口数: 1024
  已扫描: 1024
  开放: 5
  关闭: 1019
  过滤: 0
  错误: 0

扫描结果:
----------------------------------------------------------------------
端口       状态         服务            响应时间(ms)    
----------------------------------------------------------------------
22         OPEN         ssh             15.23           
80         OPEN         http            12.45           
443        OPEN         https           18.67           
----------------------------------------------------------------------
```

### JSON格式
```json
{
  "scan_time": "2024-01-01T12:00:00",
  "statistics": {
    "total_ports": 1024,
    "open_ports": 5
  },
  "results": [
    {
      "host": "192.168.1.1",
      "port": 22,
      "status": "open",
      "service": "ssh",
      "response_time": 0.015
    }
  ]
}
```

## 模块化设计优势

1. **高内聚低耦合**: 每个模块职责单一，模块间通过接口通信
2. **易于测试**: 每个模块可以独立测试
3. **便于扩展**: 可以轻松添加新的扫描类型或输出格式
4. **容错性强**: 单个模块故障不会影响整个系统
5. **代码复用**: 模块可以在其他项目中复用

## 注意事项

1. **权限要求**: 在Linux/macOS上可能需要root权限进行某些扫描
2. **网络环境**: 扫描速度受网络环境影响
3. **法律合规**: 请只在授权范围内使用本工具
4. **资源占用**: 大规模扫描可能占用较多系统资源
5. **超时设置**: 根据网络情况调整超时时间

## 开发说明

### 添加新的扫描类型

在 `scanner.py` 中添加新的扫描方法:

```python
def scan_port_xxx(self, host: str, port: int) -> ScanResult:
    """
    新扫描类型实现
    """
    # 实现扫描逻辑
    return ScanResult(...)
```

### 添加新的输出格式

在 `output.py` 中添加新的格式化器:

```python
class XXXFormatter(OutputFormatter):
    def format_results(self, results: List[ScanResult], stats: Dict[str, Any] = None) -> str:
        # 实现格式化逻辑
        return formatted_string
```

## 许可证

本项目仅供学习和研究使用，请遵守相关法律法规。

## 作者

基于Python的简易端口扫描器设计与实现

## 版本历史

- v1.0.0 (2024-01-01)
  - 初始版本发布
  - 支持TCP/UDP扫描
  - 支持多线程并发
  - 支持多种输出格式