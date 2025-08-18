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
TreasurePOS는 로컬에서 실행되는 경량 POS 웹앱입니다. 바코드 스캔/수기 입력, 소매/도매가 전환, 결제수단(현금/카드), 재고 입·출고 기록, 매출 통계/히트맵, Excel Import/Export, 언어 전환(한국어/中文/English)을 지원합니다.

### 🔶 주요 특장점 (Highlights)
- **영수증 폭 79mm(= 7.9cm, ≈ 632 dots @203dpi)** — `receipt.html` + `app.py` + ZPL을 **동일 값**으로 맞추면 왜곡/잘림이 없습니다.
- **기본 프린터: Zebra ZD230** — `app.py` 기본값. 다른 Zebra/열감열 프린터도 이름만 바꾸면 사용 가능.
- **Zebra 언어팩 불필요** — `receipt.html`을 이미지로 렌더링 후 ZPL 그래픽으로 전송하므로 OS 폰트만 있으면 **한/중/영 등 유니코드 출력**.
- **설정 페이지에서 UI 언어 전환** — 한국어/中文/English 즉시 전환.

### 🖨️ 폭 동기화(권장, Strict 79mm)
아래 3가지를 **동일 기준**으로 맞추세요. (권장: 79mm → 632 dots@203dpi)

1) **CSS (receipt.html)**  
   ```css
   :root { --paper-w: 632px; }   /* 79mm @203dpi ≈ 632 dots */
   .receipt { width: 79mm; }
   @page { size: 79mm auto; margin: 0; }
   ```

2) **스크린샷(app.py)**  
   - `hti.screenshot(..., size=(W, H))`에서 `W = 632`
   - 또는 아래 **자동 환산 패치** 사용(추천)

3) **ZPL 출력(app.py)**  
   - `^PW{W}`(점폭)과 `^LL{H}`(라벨 길이)를 설정

#### 자동 환산 패치(추천)
```python
# app.py — put near the top
import os

def _get_receipt_cfg():
    mm  = float(os.getenv("RECEIPT_MM", "79"))   # 79mm default
    dpi = int(os.getenv("RECEIPT_DPI", "203"))   # 203 or 300
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

**PowerShell 예시:**
```powershell
$env:RECEIPT_MM="79"
$env:RECEIPT_DPI="203"
$env:PRINTER_NAME="ZDesigner ZD230-203dpi ZPL"
python app.py
```

> **대안(최소 변경, 78mm 유지)**: CSS를 **78mm**로 바꾸고, 기존 `W=624` 그대로 두며 ZPL에 `^PW624`/`^LL{H}`만 추가.

</details>

---

<details>
<summary><b>🇨🇳 中文说明</b></summary>

### 简介
TreasurePOS 是一款**本地运行**的轻量级 POS 网页应用。支持条码扫描/手输、零/批价切换、现金/刷卡、出入库记录、销售统计与热力图、Excel 导入/导出，以及多语言（韩/中/英）切换。

### 🔶 亮点 (Highlights)
- **票据宽 79mm（= 7.9cm，≈ 632 dots@203dpi）** — `receipt.html` + `app.py` + ZPL **三者同值**，可避免缩放/裁切。
- **默认打印机：Zebra ZD230** — `app.py` 默认值。更改名称即可适配其它 Zebra/热敏机。
- **无需购买 Zebra 语言包** — 将 `receipt.html` 渲染为图片再以 ZPL 图像发送；系统装字体即可打印 **中/韩/英**。
- **设置页三语切换** — 中文 / 한국어 / English 即时切换。

### 🖨️ 宽度同步（推荐，严格 79mm）
把下面 3 项**统一**（推荐：79mm → 632 dots@203dpi）：

1) **CSS（receipt.html）**
   ```css
   :root { --paper-w: 632px; }   /* 79mm @203dpi ≈ 632 dots */
   .receipt { width: 79mm; }
   @page { size: 79mm auto; margin: 0; }
   ```

2) **截图（app.py）**
   - `hti.screenshot(..., size=(W, H))` 中 `W = 632`
   - 或使用下方**自动换算补丁**（推荐）

3) **ZPL（app.py）**
   - 设置 `^PW{W}`（打印点宽）与 `^LL{H}`（标签长度）

#### 自动换算补丁（推荐）
```python
# app.py 顶部附近
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

**PowerShell 示例：**
```powershell
$env:RECEIPT_MM="79"
$env:RECEIPT_DPI="203"
$env:PRINTER_NAME="ZDesigner ZD230-203dpi ZPL"
python app.py
```

> **最小变动方案（保持 78mm）**：把 CSS 改成 **78mm**，`W=624` 保持不变，只在 ZPL 里加 `^PW624`/`^LL{H}`。

</details>

---

<details>
<summary><b>🇺🇸 English Guide</b></summary>

### Overview
TreasurePOS is a **local‑first** Flask POS with barcode/manual input, retail/wholesale toggle, cash/card payments, stock logs, analytics & heatmap, Excel import/export, and multilingual UI (KO/ZH/EN).

### 🔶 Highlights
- **79 mm width (= 7.9 cm, ≈ 632 dots @203 dpi)** — keep **CSS + screenshot W + ZPL** identical to avoid scaling/clipping.
- **Default printer: Zebra ZD230** — change the name to use other Zebra/thermal printers.
- **No Zebra language pack** — `receipt.html` → image → ZPL graphic; with OS fonts, Unicode (KO/ZH/EN) prints fine.
- **Language switch in Settings** — toggle KO/ZH/EN instantly.

### 🖨️ Width sync (Recommended, strict 79 mm)
Align all three (recommended: 79 mm → 632 dots @203 dpi):

1) **CSS (receipt.html)**
   ```css
   :root { --paper-w: 632px; }   /* 79mm @203dpi ≈ 632 dots */
   .receipt { width: 79mm; }
   @page { size: 79mm auto; margin: 0; }
   ```

2) **Screenshot (app.py)**
   - `hti.screenshot(..., size=(W, H))` with `W = 632`
   - Or use the **auto‑convert patch** below (recommended).

3) **ZPL (app.py)**
   - Set `^PW{W}` (print width in dots) and `^LL{H}` (label length).

#### Auto‑convert patch (recommended)
```python
# app.py — near the top
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

**PowerShell example:**
```powershell
$env:RECEIPT_MM="79"
$env:RECEIPT_DPI="203"
$env:PRINTER_NAME="ZDesigner ZD230-203dpi ZPL"
python app.py
```

> **Minimal‑change alternative (keep ~78 mm)**: change CSS to **78 mm**, keep `W=624`, and add `^PW624`/`^LL{H}` in ZPL.

</details>

---

## ✅ Consistency checklist (CSS ↔ Screenshot ↔ ZPL)
- **CSS width** in `receipt.html` uses the same millimeters as your target (e.g., **79 mm**).  
- **Screenshot width `W`** equals the computed **printer dots**: `W = RECEIPT_MM × (RECEIPT_DPI / 25.4)` (79 mm@203 dpi ≈ **632**).  
- **ZPL** sets `^PW{W}` and a suitable `^LL{H}`.  
Keeping all three aligned avoids margins, shrinking, or clipping.

## Configuration
- **Environment**: `TREASUREPOS_DATA_DIR` (data root), `RECEIPT_MM`, `RECEIPT_DPI`, `PRINTER_NAME`.
- **Default printer**: `ZDesigner ZD230-203dpi ZPL` (editable).
- **Change form factors**: set `RECEIPT_MM=58/72/79/80` and correct `DPI`; CSS + screenshot + ZPL update together.

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
- **Pip uninstall doesn’t work in venv** → use `python -m pip ...` and avoid inheriting global site‑packages.
- **Squares instead of characters** → install a CJK font (e.g., Noto Sans CJK) and set it in `receipt.html`.
- **Nothing prints** → verify driver, printer name, and app permission on Windows.
- **Too wide/narrow** → re‑align CSS mm, screenshot `W`, and ZPL `^PW` (see checklist).

## Roadmap
- Refund workflow improvements
- More payment methods (e.g., mobile)
- Role‑based access (multi‑user)
- Cloud‑optional sync (opt‑in)

## License
MIT recommended for small shops. Add your license file as needed.