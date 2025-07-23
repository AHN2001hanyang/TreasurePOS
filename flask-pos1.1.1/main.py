import os
import sys
import threading
import webview
from app import app, init_db

# ----------- 路径与资源准备 -----------
if getattr(sys, 'frozen', False):
    os.chdir(os.path.dirname(sys.executable))
    BASE_PATH = sys._MEIPASS if hasattr(sys, '_MEIPASS') else os.path.dirname(sys.executable)
else:
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    BASE_PATH = os.path.dirname(os.path.abspath(__file__))

# ICON_PATH = os.path.join(BASE_PATH, 'icon.ico')

def run_flask():
    init_db()
    app.run(host='127.0.0.1', port=5000, debug=False)

if __name__ == '__main__':
    # 1. 启动 Flask（后台线程）
    threading.Thread(target=run_flask, daemon=True).start()

    # 2. 打开 pywebview 主窗口
    webview.create_window(
        "POS 시스템",
        "http://127.0.0.1:5000",
        width=1280,
        height=800, # 可选：窗口icon
    )
    # 3. 主窗口关闭后，整个进程会自动退出，无需任何托盘或强制kill
    webview.start()
