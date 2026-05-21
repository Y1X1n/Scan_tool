#!/usr/bin/env python3
"""
端口扫描器 — 安装配置
"""
from setuptools import setup, find_packages

setup(
    name="port-scanner",
    version="3.0.1",
    description="基于Python的简易端口扫描器",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/Y1X1n/Scan_tool",
    packages=find_packages(),
    include_package_data=True,
    python_requires=">=3.6",
    install_requires=[
        "Flask>=2.0.0",
    ],
    extras_require={
        "dev": ["pytest>=7.0.0"],
        "build": ["PyInstaller>=5.0.0"],
    },
    entry_points={
        "console_scripts": [
            "scan-port=scanner.main:main",
            "scan-port-gui=gui_app:main",
            "scan-port-web=web_app:main",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "Environment :: Console",
        "Environment :: X11 Applications",
        "Environment :: Web Environment",
        "Topic :: Security",
        "Topic :: System :: Networking",
    ],
)
