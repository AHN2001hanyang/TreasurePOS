# main.py - 禁用代理 + 端口健康复用/自动切换 的原生窗口启动器（完整可替换）
import os, sys, threading, time, socket, urllib.request, logging
from logging.handlers import RotatingFileHandler
import webview

# ---------------- 运行目录 ----------------
if getattr(sys, 'frozen', False):
    os.chdir(os.path.dirname(sys.executable))
else:
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

# ---------------- 禁用本机代理（避免被系统代理劫持 127.0.0.1） ----------------
os.environ['NO_PROXY'] = '127.0.0.1,localhost'
os.environ['no_proxy'] = '127.0.0.1,localhost'

# ---------------- 日志（控制台 + 文件，启动/异常都可追溯） ----------------
LOG_DIR = os.path.join(os.getcwd(), 'logs'); os.makedirs(LOG_DIR, exist_ok=True)
LOG_PATH = os.path.join(LOG_DIR, 'treasurepos.log')
fmt = logging.Formatter('[%(asctime)s] %(levelname)s %(name)s: %(message)s','%Y-%m-%d %H:%M:%S')
root = logging.getLogger(); root.setLevel(logging.INFO)
ch = logging.StreamHandler(sys.stdout); ch.setFormatter(fmt); root.addHandler(ch)
fh = RotatingFileHandler(LOG_PATH, maxBytes=5*1024*1024, backupCount=3, encoding='utf-8'); fh.setFormatter(fmt); root.addHandler(fh)
logging.getLogger('pywebview').setLevel(logging.INFO)
logging.getLogger('werkzeug').setLevel(logging.INFO)

PREFERRED_PORT = 5000

# ---------------- 基础探测 ----------------
def is_listening(port: int) -> bool:
    try:
        with socket.create_connection(('127.0.0.1', port), timeout=0.25):
            return True
    except Exception:
        return False

def pick_port(preferred: int) -> int:
    """优先 5001~5010，最后让 OS 分配随机可用端口"""
    if not is_listening(preferred):
        return preferred
    for p in range(preferred + 1, preferred + 11):
        if not is_listening(p):
            return p
    s = socket.socket(); s.bind(('127.0.0.1', 0))
    p = s.getsockname()[1]; s.close()
    return p

def wait_port(port: int, timeout: float = 12.0) -> bool:
    t0 = time.time()
    while time.time() - t0 < timeout:
        if is_listening(port):
            return True
        time.sleep(0.12)
    return False

# 不使用系统代理的 opener（本地健康检查走直连）
_NO_PROXY_OPENER = urllib.request.build_opener(urllib.request.ProxyHandler({}))

def http_ok(url: str, path: str) -> bool:
    try:
        with _NO_PROXY_OPENER.open(url + path, timeout=0.9) as r:
            return 200 <= r.status < 400
    except Exception:
        return False

def wait_http_ready(base_url: str, timeout: float = 8.0) -> bool:
    """等待 /healthz 或 / 有 2xx/3xx 响应；不阻塞太久"""
    t0 = time.time()
    while time.time() - t0 < timeout:
        if http_ok(base_url, '/healthz') or http_ok(base_url, '/'):
            return True
        time.sleep(0.2)
    return False

# ---------------- 启动 Flask ----------------
def run_flask(port: int):
    try:
        from app import app, init_db
        init_db()
        logging.info(f'Flask 服务启动中：127.0.0.1:{port}')
        app.run(host='127.0.0.1', port=port, debug=False, use_reloader=False, threaded=True)
    except Exception as e:
        logging.exception(f'Flask 启动失败：{e}')

# ---------------- 程序入口 ----------------
if __name__ == '__main__':
    preferred = PREFERRED_PORT
    preferred_url = f'http://127.0.0.1:{preferred}'

    # 1) 若 5000 已有“健康 HTTP 服务”，直接复用
    if is_listening(preferred) and (http_ok(preferred_url, '/healthz') or http_ok(preferred_url, '/')):
        use_port = preferred
        logging.info('检测到端口 5000 上已有健康服务，复用该服务')
    else:
        # 2) 自己启动：5000 空闲则用 5000；若 5000 被占但不健康，则自动换口
        use_port = pick_port(preferred)
        if use_port == preferred:
            logging.info(f'准备在端口 {use_port} 启动服务...')
        else:
            logging.info(f'端口 5000 被占用或不健康，改用端口 {use_port}')
        threading.Thread(target=run_flask, args=(use_port,), daemon=True).start()

        # 等端口开放
        if not wait_port(use_port, timeout=15.0):
            logging.error('端口迟迟不可用，服务未就绪'); sys.exit(1)

        # 再做一次 HTTP 轻量确认（失败也不阻断窗口打开）
        base_url_tmp = f'http://127.0.0.1:{use_port}'
        if not wait_http_ready(base_url_tmp, timeout=8.0):
            logging.warning('HTTP 就绪探测未通过，但端口已开，将先打开窗口等待页面加载')

    final_url = f'http://127.0.0.1:{use_port}'
    wnd = webview.create_window("POS 시스템", final_url, width=1280, height=800, min_size=(900, 600), resizable=True)
    try:
        webview.start(gui='edgechromium', debug=False)
    except Exception as e:
        logging.warning(f'edgechromium 不可用，回退默认：{e}')
        webview.start(debug=False)
