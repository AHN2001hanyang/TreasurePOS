import os
import sys
import threading
import webview
import pystray
from PIL import Image
from app import app, init_db
import pystray
import webview
import pystray
import webview
import PIL

# ----------- 路径与资源准备 -----------
if getattr(sys, 'frozen', False):
    os.chdir(os.path.dirname(sys.executable))
    BASE_PATH = sys._MEIPASS if hasattr(sys, '_MEIPASS') else os.path.dirname(sys.executable)
else:
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    BASE_PATH = os.path.dirname(os.path.abspath(__file__))

ICON_PATH = os.path.join(BASE_PATH, 'icon.ico')

def run_flask():
    init_db()
    app.run(host='127.0.0.1', port=5000, debug=False)

# ----------- 托盘区逻辑 -----------
def on_show(icon, item):
    if webview.windows:
        win = webview.windows[0]
        win.show()
        win.restore()

def on_hide(icon, item):
    if webview.windows:
        win = webview.windows[0]
        win.hide()

def on_exit(icon, item):
    icon.stop()  # 停止托盘
    if webview.windows:
        win = webview.windows[0]
        win.destroy()
    os._exit(0)  # 强制退出全部进程

def create_tray():
    # 加载 icon.ico 作为托盘图标
    image = Image.open(ICON_PATH)
    menu = (
        pystray.MenuItem('显示主界面', on_show),
        pystray.MenuItem('隐藏主界面', on_hide),
        pystray.MenuItem('退出', on_exit)
    )
    tray = pystray.Icon("POS系统", image, "POS系统", menu)
    tray.run()

if __name__ == '__main__':
    # 1. 启动 Flask（后台线程）
    threading.Thread(target=run_flask, daemon=True).start()

    # 2. 启动托盘（需稍等 webview 初始化）
    threading.Timer(1.0, create_tray).start()

    # 3. 打开 pywebview 主窗口
    webview.create_window(
        "POS 시스템",
        "http://127.0.0.1:5000",
        width=1280, height=800,
        # 可以用 icon=ICON_PATH 让部分平台窗口也显示 icon.ico
        # icon=ICON_PATH
    )
    webview.start()
