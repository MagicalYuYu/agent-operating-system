"""LogAnalyzer 分发配置。

使用 setuptools 配置项目打包与安装，提供 console_scripts 入口点。
安装后可通过 `loganalyzer` 命令直接调用。
"""

from setuptools import setup, find_packages

setup(
    # 包的基本信息
    name="loganalyzer",
    version="1.0.0",
    description="一个轻量级、零依赖的 Python 命令行日志分析工具",
    author="AOS Example",
    author_email="aos@example.com",
    url="https://github.com/aos/example-cli-tool",
    license="MIT",

    # Python 版本要求
    python_requires=">=3.10",

    # 包发现配置：仅包含 loganalyzer 目录
    packages=find_packages(
        where=".",
        include=["loganalyzer", "loganalyzer.*"],
    ),

    # 零外部依赖（仅使用标准库）
    install_requires=[],

    # 命令行入口点：安装后可使用 loganalyzer 命令
    entry_points={
        "console_scripts": [
            "loganalyzer = loganalyzer.__main__:main",
        ],
    },

    # 分类器（PyPI 元信息）
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: System :: Logging",
        "Topic :: Utilities",
    ],
)
