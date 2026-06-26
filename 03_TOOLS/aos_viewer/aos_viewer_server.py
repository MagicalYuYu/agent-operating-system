#!/usr/bin/env python3
"""
AOS Viewer Server — 后端服务 + PyWebView 桌面应用

功能：
  1. HTTP 服务器提供静态文件服务（HTML/CSS/JS）
  2. API 端点提供实时数据（/api/data, /api/refresh）
  3. PyWebView 桌面窗口模式

用法：
  # 浏览器模式（启动 HTTP 服务器）
  python aos_viewer_server.py [--port PORT] [--browser]

  # 桌面窗口模式（PyWebView）
  python aos_viewer_server.py [--desktop]

  # 默认：桌面窗口模式
  python aos_viewer_server.py
"""

import os
import sys
import json
import logging
import threading
import webbrowser
from pathlib import Path
from http.server import HTTPServer, SimpleHTTPRequestHandler
from datetime import datetime

# ═══════════════════════════════════════════════════════
# 路径解析（兼容 PyInstaller 打包环境）
# ═══════════════════════════════════════════════════════

def get_resource_dir():
    """获取资源根目录（兼容开发环境和 PyInstaller 打包环境）"""
    if getattr(sys, 'frozen', False):
        # PyInstaller 打包环境：使用 _MEIPASS 临时目录
        return Path(sys._MEIPASS)
    else:
        # 开发环境：使用脚本所在目录
        return Path(__file__).resolve().parent

def get_aos_root_from_exe():
    """从 exe 所在目录推断 AOS 根目录（打包环境用）"""
    if getattr(sys, 'frozen', False):
        # PyInstaller 打包环境：exe 所在目录的上级即为 AOS 根
        exe_dir = Path(sys.executable).resolve().parent
        # 假设 exe 放在 AOS 根目录或 03_TOOLS/aos_viewer/ 下
        if (exe_dir / "00_BOOT").exists():
            return exe_dir
        elif (exe_dir.parent / "00_BOOT").exists():
            return exe_dir.parent
        elif (exe_dir.parent.parent / "00_BOOT").exists():
            return exe_dir.parent.parent
    return None

RESOURCE_DIR = get_resource_dir()

# 将 scripts/ 加入路径以导入 aos_generate_data
SCRIPTS_DIR = RESOURCE_DIR / "scripts"
if not SCRIPTS_DIR.exists():
    # 开发环境回退：从源文件位置查找
    SCRIPTS_DIR = Path(__file__).resolve().parent.parent / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from aos_generate_data import (
    find_aos_root, parse_system_state, parse_skill_registry,
    parse_projects, parse_memory, parse_references
)


# ═══════════════════════════════════════════════════════
# 数据生成（复用 aos_generate_data.py 的解析器）
# ═══════════════════════════════════════════════════════

def generate_aos_data(aos_root=None):
    """生成 AOS 数据字典（不写文件，直接返回 Python 对象）"""
    if aos_root is None:
        # 打包环境优先从 exe 所在目录推断
        aos_root = get_aos_root_from_exe()
        if aos_root is None:
            aos_root = find_aos_root()

    sys_info, components, stats, events = parse_system_state(aos_root)
    skills = parse_skill_registry(aos_root)
    projects = parse_projects(aos_root)
    memories = parse_memory(aos_root)
    references = parse_references(aos_root)

    # 构建 SUBPROJECT_DATA
    subproject_data = {}
    for p in projects:
        plugins = p.get('plugins', [])
        if not plugins:
            continue
        for plugin in plugins:
            name = plugin.get('name', '')
            if not name:
                continue
            entry = {}
            if plugin.get('metadata'):
                entry['metadata'] = plugin['metadata']
            if plugin.get('readme'):
                entry['readme'] = plugin['readme']
            subproject_data[name] = entry

    data = {
        'version': sys_info.get('version', '1.1.0'),
        'kernelStatus': sys_info.get('kernel_status', 'ACTIVE'),
        'initTime': sys_info.get('init_time', ''),
        'lastUpdate': sys_info.get('last_update', ''),
        'components': components,
        'stats': stats,
        'events': events,
        'skills': skills,
        'projects': projects,
        'memories': memories,
        'references': references,
        'loops': {
            'types': [
                {'name': '自检循环', 'desc': '系统启动时自动执行完整性检查', 'active': 0},
                {'name': '同步循环', 'desc': '定时同步工作目录与 GitHub 仓库', 'active': 0},
                {'name': '迁移循环', 'desc': '批量处理历史内容迁移', 'active': 0},
            ]
        },
        'agents': {
            'modes': [
                {'name': 'PLAN', 'desc': '只读探索+生成计划', 'trigger': '/spec 或 /plan'},
                {'name': 'EXECUTE', 'desc': '读写操作+工具调用', 'trigger': '默认模式'},
                {'name': 'VERIFY', 'desc': '只读验证+输出报告', 'trigger': '新会话中发起'},
            ],
            'protocols': ['Maker/Checker 分离', '状态更新是步骤的一部分', '事前声明优于事后记录', '文件是唯一的跨会话通道']
        },
    }

    return data, subproject_data


# ═══════════════════════════════════════════════════════
# HTTP 服务器
# ═══════════════════════════════════════════════════════

class AOSViewerHandler(SimpleHTTPRequestHandler):
    """自定义 HTTP 处理器：静态文件 + API 端点"""

    # 缓存数据（首次请求时生成）
    _cached_data = None
    _cached_subproject = None
    _cache_time = None
    _cache_timestamp = None  # 缓存生成的 Unix 时间戳（用于 TTL 判断）
    _cache_ttl = 300  # 缓存有效期（秒），默认 5 分钟
    _aos_root = None

    def __init__(self, *args, **kwargs):
        # 设置静态文件目录为 prototype/（兼容打包环境）
        prototype_dir = RESOURCE_DIR / "prototype"
        if not prototype_dir.exists():
            # 开发环境回退
            prototype_dir = Path(__file__).resolve().parent / "prototype"
        super().__init__(*args, directory=str(prototype_dir), **kwargs)

    def do_GET(self):
        """处理 GET 请求"""
        if self.path == '/api/data':
            self._handle_api_data()
        elif self.path == '/api/refresh':
            self._handle_api_refresh()
        elif self.path == '/api/status':
            self._handle_api_status()
        else:
            # 静态文件服务
            super().do_GET()

    def do_POST(self):
        """处理 POST 请求"""
        if self.path == '/api/refresh':
            self._handle_api_refresh()
        else:
            self.send_error(404)

    def _handle_api_data(self):
        """返回 AOS 数据（JSON）"""
        data, subproject = self._get_data()
        response = {
            'aos_data': data,
            'subproject_data': subproject,
        }
        self._send_json(response)

    def _handle_api_refresh(self):
        """强制刷新数据缓存"""
        AOSViewerHandler._cached_data = None
        AOSViewerHandler._cache_time = None
        data, subproject = self._get_data(force_refresh=True)
        response = {
            'success': True,
            'message': '数据已刷新',
            'stats': {
                'components': len(data.get('components', [])),
                'skills': len(data.get('skills', [])),
                'projects': len(data.get('projects', [])),
                'memories': sum(len(v) for v in data.get('memories', {}).values()),
                'references': len(data.get('references', [])),
                'events': len(data.get('events', [])),
            }
        }
        self._send_json(response)

    def _handle_api_status(self):
        """返回服务器状态"""
        data, _ = self._get_data()
        response = {
            'status': 'running',
            'aos_root': str(AOSViewerHandler._aos_root),
            'cache_time': AOSViewerHandler._cache_time,
            'version': data.get('version', 'unknown'),
            'kernel_status': data.get('kernelStatus', 'unknown'),
        }
        self._send_json(response)

    def _get_data(self, force_refresh=False):
        """获取数据（带缓存 + TTL 机制）

        缓存策略：
        - force_refresh=True → 强制刷新
        - 缓存为空 → 生成新数据
        - 缓存超过 _cache_ttl 秒 → 自动刷新
        - 其他情况 → 返回缓存
        """
        import time
        now_ts = time.time()
        cache_expired = (
            AOSViewerHandler._cache_timestamp is None
            or (now_ts - AOSViewerHandler._cache_timestamp) > AOSViewerHandler._cache_ttl
        )
        if force_refresh or AOSViewerHandler._cached_data is None or cache_expired:
            aos_root = AOSViewerHandler._aos_root or find_aos_root()
            AOSViewerHandler._aos_root = aos_root
            AOSViewerHandler._cached_data, AOSViewerHandler._cached_subproject = generate_aos_data(aos_root)
            AOSViewerHandler._cache_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            AOSViewerHandler._cache_timestamp = now_ts
        return AOSViewerHandler._cached_data, AOSViewerHandler._cached_subproject

    def _send_json(self, data):
        """发送 JSON 响应"""
        self.send_response(200)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode('utf-8'))

    def log_message(self, format, *args):
        """简化日志输出"""
        msg = format % args
        # 过滤掉 favicon 等无关请求
        if 'favicon' not in msg:
            print(f"  [{datetime.now().strftime('%H:%M:%S')}] {msg}")


def start_server(port=8765, open_browser=True):
    """启动 HTTP 服务器"""
    server = HTTPServer(('127.0.0.1', port), AOSViewerHandler)
    print(f"\n┌─ AOS Viewer Server ─────────────────────────┐")
    print(f"│ 地址: http://127.0.0.1:{port}                │")
    print(f"│ API:  http://127.0.0.1:{port}/api/data       │")
    print(f"│ 刷新: http://127.0.0.1:{port}/api/refresh    │")
    print(f"└──────────────────────────────────────────────┘")

    if open_browser:
        threading.Timer(0.5, lambda: webbrowser.open(f'http://127.0.0.1:{port}')).start()

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n服务器已停止")
        server.shutdown()


# ═══════════════════════════════════════════════════════
# PyWebView 桌面应用
# ═══════════════════════════════════════════════════════

def start_desktop(port=8765):
    """启动 PyWebView 桌面窗口"""
    import webview

    # 先在后台启动 HTTP 服务器
    server = HTTPServer(('127.0.0.1', port), AOSViewerHandler)
    server_thread = threading.Thread(target=server.serve_forever, daemon=True)
    server_thread.start()

    print(f"AOS Viewer 桌面模式启动中... (后端端口: {port})")

    # 计算窗口居中位置
    win_w, win_h = 1280, 800
    try:
        import ctypes
        user32 = ctypes.windll.user32
        screen_w = user32.GetSystemMetrics(0)  # SM_CXSCREEN
        screen_h = user32.GetSystemMetrics(1)  # SM_CYSCREEN
        win_x = (screen_w - win_w) // 2
        win_y = (screen_h - win_h) // 2
    except Exception:
        win_x, win_y = None, None

    # 创建 PyWebView 窗口（frameless 模式，使用自定义标题栏）
    window = webview.create_window(
        title='AOS Viewer',
        url=f'http://127.0.0.1:{port}',
        width=win_w,
        height=win_h,
        x=win_x,
        y=win_y,
        min_size=(960, 600),
        resizable=True,
        frameless=True,
        easy_drag=False,  # 禁用 PyWebView 全局拖拽（会导致文字无法选中），改用前端自定义菜单栏拖拽
        text_select=True,  # 允许文字选中（PyWebView 默认 text_select=False 会注入全局 user-select:none）
    )

    # 暴露窗口控制 API 给前端 JS
    class Api:
        def __init__(self, win):
            self._window = win
            self._is_maximized = False
            # 拖拽状态：记录初始窗口位置和鼠标屏幕坐标
            self._drag_win_x = 0
            self._drag_win_y = 0
            self._drag_mouse_x = 0
            self._drag_mouse_y = 0

        def minimize(self):
            self._window.minimize()

        def toggle_maximize(self):
            """切换最大化/还原（自行跟踪状态）"""
            try:
                if self._is_maximized:
                    self._window.restore()
                    self._is_maximized = False
                else:
                    self._window.maximize()
                    self._is_maximized = True
            except Exception:
                # fallback: 尝试用 resize 还原
                try:
                    if self._is_maximized:
                        self._window.resize(1280, 800)
                        self._is_maximized = False
                    else:
                        self._window.maximize()
                        self._is_maximized = True
                except Exception:
                    pass

        def close(self):
            self._window.destroy()

        def is_desktop(self):
            return True

        def drag_start(self, mouse_x, mouse_y):
            """开始拖拽，记录窗口位置和鼠标屏幕坐标的初始值"""
            try:
                self._drag_win_x = self._window.x
                self._drag_win_y = self._window.y
                self._drag_mouse_x = int(mouse_x)
                self._drag_mouse_y = int(mouse_y)
                return True
            except Exception:
                return False

        def drag_move(self, mouse_x, mouse_y):
            """拖拽移动到新位置（基于初始窗口位置 + 鼠标偏移量计算绝对坐标）
            每次 call 独立计算目标位置，不依赖 self._window.x/y（避免异步桥调用导致的位置过时）
            """
            try:
                dx = int(mouse_x) - self._drag_mouse_x
                dy = int(mouse_y) - self._drag_mouse_y
                self._window.move(self._drag_win_x + dx, self._drag_win_y + dy)
            except Exception:
                pass

    api = Api(window)
    window.expose(api.minimize, api.toggle_maximize, api.close, api.is_desktop, api.drag_start, api.drag_move)

    # ═══════════════════════════════════════════════════════
    # frameless 模式：手动添加 resize 边框（Windows API）
    # ═══════════════════════════════════════════════════════
    def add_resize_border():
        """为 frameless 窗口添加 resize 边框 + 消除顶部残留标题栏"""
        try:
            import ctypes
            user32 = ctypes.windll.user32
            # 获取窗口句柄
            hwnd = None
            try:
                hwnd = window.hwnd
            except AttributeError:
                pass
            if not hwnd:
                hwnd = user32.FindWindowW(None, "AOS Viewer")
            if not hwnd:
                log.info("[resize] 未找到窗口句柄")
                return
            log.info(f"[resize] hwnd={hwnd}")

            # 1. 移除 WS_CAPTION 和 WS_THICKFRAME 的组合残留
            GWL_STYLE = -16
            GWL_EXSTYLE = -20
            WS_THICKFRAME = 0x00040000
            WS_CAPTION = 0x00C00000
            WS_EX_APPWINDOW = 0x00040000
            SWP_FRAMECHANGED = 0x0020
            SWP_NOMOVE = 0x0002
            SWP_NOSIZE = 0x0001

            current_style = user32.GetWindowLongW(hwnd, GWL_STYLE)
            # 添加 WS_THICKFRAME，移除 WS_CAPTION
            new_style = (current_style | WS_THICKFRAME) & ~WS_CAPTION
            user32.SetWindowLongW(hwnd, GWL_STYLE, new_style)

            # 确保 WS_EX_APPWINDOW（任务栏显示）
            current_exstyle = user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
            user32.SetWindowLongW(hwnd, GWL_EXSTYLE, current_exstyle | WS_EX_APPWINDOW)

            user32.SetWindowPos(hwnd, 0, 0, 0, 0, 0,
                              SWP_NOMOVE | SWP_NOSIZE | SWP_FRAMECHANGED)

            # 2. DWM 扩展帧到客户区
            try:
                dwmapi = ctypes.windll.dwmapi
                margins = (ctypes.c_int * 4)(0, 0, 1, 0)
                dwmapi.DwmExtendFrameIntoClientArea(hwnd, margins)
                log.info("[resize] DWM 帧扩展完成")
            except Exception as e:
                log.warning(f"[resize] DWM 帧扩展失败: {e}")

            log.info("[resize] resize 边框已添加（frameless + WS_THICKFRAME - WS_CAPTION）")
        except Exception as e:
            log.error(f"[resize] 添加 resize 边框失败: {e}")

    window.events.shown += add_resize_border

    def on_closing():
        server.shutdown()

    window.events.closing += on_closing

    # 持久化存储路径（localStorage、Cookie 等 WebView 数据）
    # 使用 Windows 标准 %APPDATA% 目录，确保持久化且不污染 AOS 目录
    # 修复问题：旧版 private_mode=True 导致设置重启后清空
    app_data_dir = os.path.join(
        os.environ.get('APPDATA', os.path.expanduser('~')),
        'AOS_Viewer'
    )
    os.makedirs(app_data_dir, exist_ok=True)

    webview.start(debug=False, private_mode=False, storage_path=app_data_dir)
    print("AOS Viewer 已关闭")


# ═══════════════════════════════════════════════════════
# 日志重定向（隐藏控制台时，日志写入文件便于排查）
# ═══════════════════════════════════════════════════════

def setup_logging():
    """配置日志输出到文件（打包环境无控制台时使用）"""
    log = logging.getLogger('aos_viewer')
    log.setLevel(logging.DEBUG)

    if getattr(sys, 'frozen', False):
        # 打包环境：日志写入 AOS 标准 06_LOGS/aos_viewer/ 目录
        # 若找不到 AOS 根目录，回退到 %APPDATA%\AOS_Viewer\logs\
        aos_root = get_aos_root_from_exe()
        if aos_root:
            log_dir = aos_root / "06_LOGS" / "aos_viewer"
        else:
            log_dir = Path(
                os.environ.get('APPDATA', os.path.expanduser('~'))
            ) / 'AOS_Viewer' / 'logs'
        log_dir.mkdir(parents=True, exist_ok=True)
        log_file = log_dir / f"aos_viewer_{datetime.now().strftime('%Y%m%d')}.log"
        handler = logging.FileHandler(log_file, encoding='utf-8', mode='a')
        handler.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s', datefmt='%H:%M:%S')
        handler.setFormatter(formatter)
        log.addHandler(handler)

        log.info(f"{'='*60}")
        log.info(f"AOS Viewer 启动 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        log.info(f"exe 路径: {sys.executable}")
        log.info(f"工作目录: {os.getcwd()}")
        log.info(f"sys.frozen: {getattr(sys, 'frozen', False)}")
        log.info(f"_MEIPASS: {getattr(sys, '_MEIPASS', 'N/A')}")
        log.info(f"{'='*60}")

        # 同时重定向 stdout/stderr 到日志文件（捕获 print 输出）
        class StreamToLogger:
            def __init__(self, logger, level=logging.INFO):
                self.logger = logger
                self.level = level
            def write(self, message):
                if message and message.strip():
                    self.logger.log(self.level, message.rstrip())
            def flush(self):
                for h in self.logger.handlers:
                    h.flush()

        sys.stdout = StreamToLogger(log, logging.INFO)
        sys.stderr = StreamToLogger(log, logging.ERROR)
    else:
        # 开发环境：输出到控制台
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s', datefmt='%H:%M:%S')
        handler.setFormatter(formatter)
        log.addHandler(handler)
        log.info(f"AOS Viewer 开发模式启动 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    return log


# ═══════════════════════════════════════════════════════
# 命令行入口
# ═══════════════════════════════════════════════════════

if __name__ == '__main__':
    # 打包环境下隐藏控制台时，配置日志文件
    log = setup_logging()

    import argparse

    parser = argparse.ArgumentParser(description='AOS Viewer Server')
    parser.add_argument('--port', type=int, default=8765, help='HTTP 端口（默认 8765）')
    parser.add_argument('--browser', action='store_true', help='浏览器模式（启动 HTTP 服务器并打开浏览器）')
    parser.add_argument('--desktop', action='store_true', help='桌面窗口模式（PyWebView）')
    parser.add_argument('--no-open', action='store_true', help='不自动打开浏览器')

    args = parser.parse_args()

    # 默认使用桌面模式
    if args.desktop or (not args.browser):
        start_desktop(args.port)
    else:
        start_server(args.port, open_browser=not args.no_open)
