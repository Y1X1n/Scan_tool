#!/usr/bin/env python3
"""
端口扫描器打包脚本
用于将应用程序打包成exe文件
"""
import os
import sys
import subprocess
import shutil


def install_pyinstaller():
    """安装PyInstaller"""
    print("正在安装PyInstaller...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
        print("PyInstaller安装成功!")
        return True
    except subprocess.CalledProcessError:
        print("PyInstaller安装失败!")
        return False


def build_exe():
    """打包exe文件"""
    print("=" * 50)
    print("端口扫描器打包工具")
    print("=" * 50)
    
    # 检查PyInstaller是否安装
    try:
        import PyInstaller
        print(f"PyInstaller版本: {PyInstaller.__version__}")
    except ImportError:
        print("未检测到PyInstaller，正在安装...")
        if not install_pyinstaller():
            return False
    
    # 创建打包目录
    build_dir = "build"
    dist_dir = "dist"
    
    # 清理旧的打包文件
    if os.path.exists(build_dir):
        shutil.rmtree(build_dir)
    if os.path.exists(dist_dir):
        shutil.rmtree(dist_dir)
    
    # 定义要打包的程序
    apps = [
        {
            "name": "PortScanner",
            "script": "run.py",
            "description": "端口扫描器命令行版本"
        },
        {
            "name": "PortScannerGUI",
            "script": "gui_app.py",
            "description": "端口扫描器桌面GUI版本"
        },
        {
            "name": "PortScannerWeb",
            "script": "web_app.py",
            "description": "端口扫描器Web界面版本"
        }
    ]
    
    # 选择要打包的程序
    print("\n请选择要打包的程序:")
    for i, app in enumerate(apps, 1):
        print(f"{i}. {app['name']} - {app['description']}")
    print("4. 全部打包")
    print("0. 退出")
    
    choice = input("\n请输入选择 (0-4): ").strip()
    
    if choice == "0":
        print("退出打包程序")
        return True
    
    selected_apps = []
    if choice == "4":
        selected_apps = apps
    elif choice in ["1", "2", "3"]:
        selected_apps = [apps[int(choice) - 1]]
    else:
        print("无效的选择!")
        return False
    
    # 执行打包
    success_count = 0
    for app in selected_apps:
        print(f"\n正在打包: {app['name']}...")
        
        # 构建PyInstaller命令
        cmd = [
            sys.executable, "-m", "PyInstaller",
            "--onefile",  # 打包成单个exe文件
            "--console" if app['name'] != "PortScannerGUI" else "--windowed",  # GUI程序不显示控制台
            "--name", app['name'],
            "--distpath", dist_dir,
            "--workpath", build_dir,
            "--specpath", ".",
            "--clean",  # 清理临时文件
            "--noconfirm",  # 不确认覆盖
        ]
        
        # 添加数据文件
        if app['name'] == "PortScannerWeb":
            # Web版本需要包含模板和静态文件
            if os.path.exists("templates"):
                cmd.extend(["--add-data", "templates;templates"])
            if os.path.exists("static"):
                cmd.extend(["--add-data", "static;static"])
        
        # 添加scanner模块
        cmd.extend(["--hidden-import", "scanner"])
        
        # 添加脚本
        cmd.append(app['script'])
        
        try:
            # 执行打包命令
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                print(f"✓ {app['name']} 打包成功!")
                success_count += 1
                
                # 显示生成的文件
                exe_path = os.path.join(dist_dir, f"{app['name']}.exe")
                if os.path.exists(exe_path):
                    file_size = os.path.getsize(exe_path) / (1024 * 1024)  # MB
                    print(f"  生成文件: {exe_path}")
                    print(f"  文件大小: {file_size:.2f} MB")
            else:
                print(f"✗ {app['name']} 打包失败!")
                print(f"错误信息: {result.stderr}")
                
        except Exception as e:
            print(f"✗ {app['name']} 打包异常: {str(e)}")
    
    # 显示打包结果
    print("\n" + "=" * 50)
    print("打包完成!")
    print(f"成功: {success_count}/{len(selected_apps)}")
    
    if success_count > 0:
        print(f"\n生成的exe文件位于: {os.path.abspath(dist_dir)}")
        print("\n使用说明:")
        print("1. 双击exe文件即可运行")
        print("2. 首次运行可能需要管理员权限")
        print("3. 某些杀毒软件可能会误报，请添加信任")
    
    return success_count > 0


def create_spec_file():
    """创建PyInstaller spec文件（高级配置）"""
    spec_content = """# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['run.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=['scanner'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='PortScanner',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
"""
    
    with open("port_scanner.spec", "w", encoding="utf-8") as f:
        f.write(spec_content)
    
    print("已创建PyInstaller spec文件: port_scanner.spec")


def main():
    """主函数"""
    # 检查Python版本
    if sys.version_info < (3, 6):
        print("错误: 需要Python 3.6或更高版本!")
        return
    
    print(f"Python版本: {sys.version}")
    print(f"当前目录: {os.getcwd()}")
    
    # 检查必要文件
    required_files = ["run.py", "gui_app.py", "web_app.py", "scanner"]
    missing_files = []
    
    for file in required_files:
        if not os.path.exists(file):
            missing_files.append(file)
    
    if missing_files:
        print(f"错误: 缺少必要文件: {', '.join(missing_files)}")
        return
    
    # 运行打包
    if build_exe():
        print("\n打包完成! 您现在可以运行生成的exe文件。")
    else:
        print("\n打包失败! 请检查错误信息。")


if __name__ == "__main__":
    main()