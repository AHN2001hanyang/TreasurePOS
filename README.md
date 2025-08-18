# TreasurePOS — Local‑First Flask POS (KR / ZH / EN)

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-2.x-lightgrey)](https://flask.palletsprojects.com/)
[![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-informational)](#)
[![License](https://img.shields.io/badge/License-MIT%20(recommended)-green)](#license)

A lightweight, **local‑first** POS web app that runs entirely on your computer. Supports barcode scanning/manual input, retail/wholesale pricing, cash/card payments, stock logs, **Excel import/export**, **sales analytics & heatmap**, and **multilingual UI (KO/ZH/EN)**.  
**Windows‑only** thermal receipt printing is built‑in (Zebra ZPL pipeline).

---

## Quick Start
```bash
# 1) Create & activate a clean venv
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate

# 2) Install deps
python -m pip install --upgrade pip
python -m pip install flask flask-cors pandas pillow html2image pywin32

# 3) Run (choose either)
python app.py         # console
python main.py        # desktop window (embedded browser)

# 4) Visit
# http://127.0.0.1:5000  (port may vary)
```

> **Tip:** Data lives under a local app folder (`%LOCALAPPDATA%/TreasurePOS` on Windows, see details below). Copy this folder to migrate/backup.

---

<details>
<summary><b>🇰🇷 한국어 안내</b></summary>

### 개요
TreasurePOS는 로컬에서 실행되는 경량 POS 웹앱입니다. 바코드 스캔/수기 입력, 소매/도매가 전환, 결제수단(현금/카드) 선택, 재고 입·출고 기록, 매출 통계/히트맵, Excel Import/Export, 언어 전환(한국어/中文/English)을 지원합니다.

### 🔶 주요 특장점 (Highlights)
- **영수증 폭 기본 79mm (≈624px @ 203dpi)** — `receipt.html`의 CSS에서 쉽게 변경 가능합니다.
  ```css
  :root { --paper-w: 624px; }   /* ≈79mm @203dpi */
  .receipt { width: 79mm; }     /* mm 단위도 직접 사용 가능 */
  ```
- **기본 프린터: Zebra ZD230** — `app.py`의 프린터 이름이 기본값으로 설정되어 있습니다. 환경에 맞게 수정하면 다른 Zebra/열감열 프린터도 동작합니다.
  ```python
  printer_name = "ZDesigner ZD230-203dpi ZPL"
  ```
- **Zebra 언어팩 불필요** — `receipt.html`을 이미지로 렌더링한 뒤 ZPL 그래픽으로 전송하므로, OS에 폰트만 있으면 **한/중/영 등 유니코드 텍스트 출력**이 가능합니다.
- **설정 페이지에서 UI 언어 전환** — Settings에서 한국어/中文/English 즉시 전환.

### 🖨️ 영수증 폭 & app.py 설정
CSS만 바꾸면 화면 폭만 변하고, 프린터 실제 점폭(dots)은 그대로일 수 있습니다. 아래처럼 **app.py도 함께** 설정하세요.

**① 환경변수 방식(권장):**
```powershell
# Windows PowerShell 예시
$env:RECEIPT_MM="79"         # 58 / 72 / 79 / 80 등
$env:RECEIPT_DPI="203"       # 203 또는 300
$env:PRINTER_NAME="ZDesigner ZD230-203dpi ZPL"
python app.py
```

**② 코드 패치 예시(app.py):**
```python
import os

def _get_receipt_cfg():
    mm  = float(os.getenv("RECEIPT_MM", "79"))
    dpi = int(os.getenv("RECEIPT_DPI", "203"))
    dpmm = dpi / 25.4
    width_dots = int(round(mm * dpmm))
    return mm, dpi, width_dots

def _calc_canvas_size(height_rows_hint=None):
    mm, dpi, W = _get_receipt_cfg()
    H = height_rows_hint if height_rows_hint else 1500
    return W, H

# ... print_receipt 내에서 ...
H = _estimate_receipt_height(sale_id)
W, _ = _calc_canvas_size(H)
hti.screenshot(url=url, save_as=tmp_save_name, size=(W, H))
zpl = (
    zpl_img
    + f"^XA\n^PW{W}\n^LL{H}\n^FO0,0^XGRECEIPT.GRF,1,1^FS\n^XZ\n"
)
```

> **표 참고 (203dpi 기준)**: 58mm→464 dots, 72mm→576, **79mm→632**, 80mm→640. 300dpi는 각각 ×(300/203) 정도로 증가합니다.

</details>

---

<details>
<summary><b>🇨🇳 中文说明</b></summary>

### 简介
TreasurePOS 是一款**本地运行**的轻量级 POS 网页应用。支持条码扫描/手输、零售价/批发价切换、付款方式（现金/刷卡）、库存出入库记录、销售统计与热力图、Excel 导入/导出，以及多语言（韩/中/英）切换。

### 🔶 亮点 (Highlights)
- **默认票据宽度 79mm（≈624px @203dpi）** — 可在 `receipt.html` 的 CSS 中修改：
  ```css
  :root { --paper-w: 624px; }   /* ≈79mm @203dpi */
  .receipt { width: 79mm; }
  ```
- **默认打印机：Zebra ZD230** — `app.py` 中默认写了打印机名，按实际环境修改即可兼容其它 Zebra/热敏机。
  ```python
  printer_name = "ZDesigner ZD230-203dpi ZPL"
  ```
- **无需购买 Zebra 语言包** — 将 `receipt.html` 渲染为图片后以 ZPL 图像发送；只要系统安装了字体，即可打印 **中/韩/英等 Unicode 文本**。
- **设置页可切换 UI 语言** — 中文 / 한국어 / English 任意切换。

### 🖨️ 宽度与 app.py 同步设置
仅改 CSS 会导致**页面宽**与**打印点宽**不一致。请同时调整 **app.py**：

**① 环境变量（推荐）：**
```powershell
$env:RECEIPT_MM="79"
$env:RECEIPT_DPI="203"         # 203 or 300
$env:PRINTER_NAME="ZDesigner ZD230-203dpi ZPL"
python app.py
```

**② 代码改动示例（app.py）：**
```python
import os

def _get_receipt_cfg():
    mm  = float(os.getenv("RECEIPT_MM", "79"))
    dpi = int(os.getenv("RECEIPT_DPI", "203"))
    dpmm = dpi / 25.4
    width_dots = int(round(mm * dpmm))
    return mm, dpi, width_dots

def _calc_canvas_size(height_rows_hint=None):
    mm, dpi, W = _get_receipt_cfg()
    H = height_rows_hint if height_rows_hint else 1500
    return W, H

# ... 在 print_receipt 内 ...
H = _estimate_receipt_height(sale_id)
W, _ = _calc_canvas_size(H)
hti.screenshot(url=url, save_as=tmp_save_name, size=(W, H))
zpl = (
    zpl_img
    + f"^XA\n^PW{W}\n^LL{H}\n^FO0,0^XGRECEIPT.GRF,1,1^FS\n^XZ\n"
)
```

> **对照表（203dpi）**：58mm→464 dots，72mm→576，**79mm→632**，80mm→640；300dpi 时按比例增大。

</details>

---

<details>
<summary><b>🇺🇸 English Guide</b></summary>

### Overview
TreasurePOS is a **local‑first** Flask POS app with barcode/manual input, retail/wholesale toggle, cash/card payments, stock logs, analytics & heatmap, Excel import/export, and multilingual UI (KO/ZH/EN).

### 🔶 Highlights
- **Receipt width 79 mm by default (≈624 px @203 dpi)** — change in `receipt.html`:
  ```css
  :root { --paper-w: 624px; }   /* ≈79mm @203dpi */
  .receipt { width: 79mm; }
  ```
- **Default printer: Zebra ZD230** — hard‑coded printer name in `app.py`; edit to match other Zebra/thermal printers.
  ```python
  printer_name = "ZDesigner ZD230-203dpi ZPL"
  ```
- **No Zebra language pack needed** — we render `receipt.html` to an image and send as ZPL graphic; with proper OS fonts, any Unicode prints.
- **Settings page language switch** — toggle KO/ZH/EN instantly.

### 🖨️ Keep width in sync (receipt.html + app.py)
Changing CSS alone affects the **screen width** but not **printer dot width**. Update **app.py** as well:

**1) Environment variables (recommended):**
```powershell
$env:RECEIPT_MM="79"            # 58 / 72 / 79 / 80 ...
$env:RECEIPT_DPI="203"          # 203 or 300
$env:PRINTER_NAME="ZDesigner ZD230-203dpi ZPL"
python app.py
```

**2) Code patch (app.py):**
```python
import os

def _get_receipt_cfg():
    mm  = float(os.getenv("RECEIPT_MM", "79"))
    dpi = int(os.getenv("RECEIPT_DPI", "203"))
    dpmm = dpi / 25.4
    width_dots = int(round(mm * dpmm))
    return mm, dpi, width_dots

def _calc_canvas_size(height_rows_hint=None):
    mm, dpi, W = _get_receipt_cfg()
    H = height_rows_hint if height_rows_hint else 1500
    return W, H

# ... inside print_receipt ...
H = _estimate_receipt_height(sale_id)
W, _ = _calc_canvas_size(H)
hti.screenshot(url=url, save_as=tmp_save_name, size=(W, H))
zpl = (
    zpl_img
    + f"^XA\n^PW{W}\n^LL{H}\n^FO0,0^XGRECEIPT.GRF,1,1^FS\n^XZ\n"
)
```

> **Cheat sheet (203 dpi)**: 58 mm→464 dots, 72 mm→576, **79 mm→632**, 80 mm→640. 300 dpi scales accordingly.

</details>

---

## Configuration
- **Environment variable**: `TREASUREPOS_DATA_DIR` to change the data root.
- **Receipt width**: Change CSS in `receipt.html` (e.g., `79mm`) **and** printer dots via `RECEIPT_MM/RECEIPT_DPI` or code patch.
- **Printer name**: Use `PRINTER_NAME` env var or edit in `app.py` (default `ZDesigner ZD230-203dpi ZPL`).

## Project Structure (simplified)
```
/app.py           # Flask backend (API/routes, printing pipeline)
/main.py          # Desktop wrapper (webview + health check)
/templates/
  index.html      # Sales (Home)
  manage.html     # Manage products (Excel import/export ...)
  sales.html      # Sales analytics (charts, heatmap)
  stocklog.html   # Stock in/out/adjust logs
  settings.html   # Language switch (KO/ZH/EN)
  receipt.html    # Printable receipt layout (render → image → ZPL)
/static/          # JS/CSS/assets (if applicable)
```

## Troubleshooting
- **Pip uninstall doesn’t work in venv**: ensure you’re using the venv’s interpreter (`python -m pip ...`) and **do not** inherit global site‑packages.
- **Non‑Latin characters print as squares**: install a font on your OS that covers the target script (e.g., Noto Sans CJK) and use it in `receipt.html`.
- **Nothing prints**: verify printer driver, printer name, and that the app runs with sufficient permission on Windows.
- **Image too wide/narrow**: keep CSS `mm` and `RECEIPT_MM/RECEIPT_DPI` in sync; adjust `--paper-w` or dots.

## Roadmap
- Refund workflow improvements
- More payment methods (e.g., mobile)
- Role‑based access (multi‑user)
- Cloud‑optional sync (opt‑in)

## License
MIT recommended for small shops. Add your license file as needed.