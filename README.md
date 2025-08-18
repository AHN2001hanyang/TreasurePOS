# TreasurePOS (Flask + Desktop WebView)
**한국어 · 中文 · English** — local‑first POS for small shops. Scan/type barcodes, switch retail/wholesale, sell with cash or card, keep stock logs, view sales analytics, and print Zebra receipts.

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-2.x-lightgrey)](https://flask.palletsprojects.com/)
[![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-informational)](#)
[![License](https://img.shields.io/badge/License-Apache--2.0-green)](#license)

> **Printing**: Windows‑only (uses `pywin32` to talk RAW ZPL to Zebra). Pages are rendered with **Playwright (Chromium)** → PNG → **ZPL graphic**. This preserves Korean/Chinese/English text without special printer fonts.

---

## Features
- Barcode scan / manual input, product search & quick add
- Retail / wholesale price toggle (per item)
- Cash / card payments (VAT shown only for card by default)
- Stock in/out log and corrections
- Sales analytics (daily/weekly/monthly/yearly) and **weekday × hour heatmap**
- **Excel import/export** (items & sales)
- Multilingual UI: **KO / ZH / EN**
- Receipts: responsive HTML (`templates/receipt.html`) → **Playwright** element screenshot → **ZPL**

## Folder layout
```
app.py                # Flask backend + printing pipeline (Playwright + ZPL)
main.py               # Desktop wrapper (embedded webview -> http://127.0.0.1:<port>)
/templates            # HTML pages (index/manage/sales/stocklog/settings/receipt)
/static               # static assets (images, JS/CSS)
/uploads              # Excel uploads (runtime)
```

## Where is my data?
All runtime data lives in a user folder so upgrades don’t overwrite your database or images:

- **Windows**: `%LOCALAPPDATA%\TreasurePOS`
- **macOS**: `~/Library/Application Support/TreasurePOS`
- **Linux**: `~/.local/share/treasurepos`

Subfolders: `inventory.db`, `uploads/`, `images/`. First run auto‑migrates legacy files from the repo directory.

---

## Quick start (dev)
```bash
# 1) Create & activate venv
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate

# 2) Install dependencies
python -m pip install --upgrade pip
python -m pip install flask flask-cors pandas pillow pywin32 playwright

# 3) Install a Playwright browser
python -m playwright install chromium

# 4) Run the server or desktop wrapper
python app.py     # console
python main.py    # desktop window (embedded browser)

# 5) Open the UI (port is auto-assigned, shown in console)
# http://127.0.0.1:<port>
```

### Printing notes (Zebra)
- Default printer name in `app.py` is **`ZDesigner ZD230-203dpi ZPL`** — change it to yours.
- Receipt width defaults to **624 px** (~78–79 mm at 203 dpi). The code sets `^PW` (print width) and `^LL` (label length) from the actual PNG size so there’s no clipping.
- To change paper width:
  1) Update `--paper-w` (and optionally `@page size`) in `templates/receipt.html`.
  2) Adjust the `width_px` argument in `render_receipt_png()` (Playwright screenshot).
  3) The ZPL generator already reads the PNG’s width/height and sets `^PW/^LL` accordingly.

---

## Build Windows executable (fast **onedir**)
> Keep Playwright installed on the target machine (once per PC): `python -m playwright install chromium`.

```powershell
# From repo root (activate venv first)
pip install pyinstaller

pyinstaller main.py `
  --noconfirm --onedir `
  --name TreasurePOS `
  --icon icon.ico `
  --add-data "templates;templates" `
  --add-data "static;static" `
  --hidden-import "playwright.sync_api"

# The app starts faster in onedir mode. Launch: dist/TreasurePOS/TreasurePOS.exe
```

If you need to run the Flask server as the entry point instead, replace `main.py` with `app.py` in the command above.

---

## Troubleshooting
- **Playwright import error** (`Unable to import 'playwright.sync_api'`)  
  → Install both the library and the browser:
  ```bash
  pip install playwright
  python -m playwright install chromium
  ```
- **Printed text shows as squares**  
  → Install a CJK font (e.g., *Noto Sans CJK*). The ZPL path uses an image, so any system font will work.
- **Nothing prints**  
  → Check Windows “Devices and Printers”, the exact printer name, and that the user has permission to print.
- **Extra lines under the table**  
  → In `receipt.html` keep only the intended `<hr>` elements; the template uses a single dashed border before the total.

---

## International guides

<details>
<summary><b>🇰🇷 한국어</b></summary>

### 소개
TreasurePOS는 로컬에서 동작하는 경량 POS입니다. 바코드 스캔/직접입력, 소매/도매가 전환, 현금/카드 결제, 재고 입·출고, 매출 통계/히트맵, Excel 가져오기/내보내기, 다국어(KO/ZH/EN)를 지원합니다.

### 설치
```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -U pip
pip install flask flask-cors pandas pillow pywin32 playwright
python -m playwright install chromium
python main.py
```

### 프린트
- 기본 프린터 이름: `ZDesigner ZD230-203dpi ZPL` (코드에서 변경 가능)
- `receipt.html`의 폭과 Playwright 스크린샷 폭(기본 624px), ZPL의 `^PW/^LL`이 **자동 동기화**되어 잘림이 없습니다.

</details>

<details>
<summary><b>🇨🇳 中文</b></summary>

### 介绍
TreasurePOS 是一款**本地运行**的轻量级 POS。支持条码扫描/手输、零/批价切换、现金/刷卡、出入库记录、销售统计与热力图、Excel 导入/导出、多语言（韩/中/英）。

### 安装
```bash
python -m venv .venv
source .venv/bin/activate   # Windows 用 .venv\Scripts\activate
pip install -U pip
pip install flask flask-cors pandas pillow pywin32 playwright
python -m playwright install chromium
python main.py
```

### 打印
- 默认打印机名：`ZDesigner ZD230-203dpi ZPL`（在代码中改成你的）  
- `receipt.html` 的宽度与 Playwright 截图宽度（默认 624px）一致，ZPL 根据 PNG 尺寸自动设置 `^PW/^LL`，不会裁切。

</details>

<details>
<summary><b>🇺🇸 English</b></summary>

### Overview
Local‑first POS built with Flask. Barcode/manual input, retail/wholesale toggle, cash/card, stock logs, analytics & heatmap, Excel import/export, multilingual UI.

### Install
```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -U pip
pip install flask flask-cors pandas pillow pywin32 playwright
python -m playwright install chromium
python main.py
```

### Printing
- Change the Windows printer name in `app.py` if needed.  
- Keep receipt width consistent (HTML/CSS ↔ Playwright screenshot). ZPL width/length are derived from the PNG.

</details>

---

## License
Apache‑2.0. See `LICENSE`.

---

### Credits
- Flask, Playwright, Pandas, Pillow
- Zebra ZPL