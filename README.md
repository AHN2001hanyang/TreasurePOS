# TreasurePOS — Flask-based Local POS (79 mm Receipt, ZPL)

**Languages · 语言 · 언어:** [🇺🇸 English](#-english) · [🇨🇳 简体中文](#-简体中文) · [🇰🇷 한국어](#-한국어)

---

This README refreshes and expands your original file. It reflects the **current codebase** (`app.py`, `main.py`, templates & static) and corrects outdated parts (e.g., **Playwright** is now used for receipt screenshots, not `html2image`). It also documents data paths, APIs, packaging, and receipt customization.

> If you just want to build the EXE quickly, jump to: [Build (PyInstaller, onedir)](#build-pyinstaller-onedir).

---

## ✨ Highlights

- **Local-first** Flask app, UI via templates under `templates/` and assets under `static/`
- **Persistent data dir** (auto-migration on first run): DB & images live outside the code folder
- **Inventory, sales, refunds, stock I/O** with integer-safe pricing columns (`*_int`)
- **Fast search & pagination** endpoints
- **Excel import/export** (`xlsx`) and **CSV streaming** for sales
- **Element-level receipt rendering** with **Playwright** → PNG → **ZPL** → Windows printing (pywin32)
- **79 mm paper** layout (CSS canvas `624px` wide by default), font & spacing tuned for 203 dpi
- **pywebview shell** (`main.py`) for a desktop-like window experience

---

## 🗂️ Project Layout

```
flask-pos2.0/
├─ app.py              # Flask app (APIs, printing, DB & file handling)
├─ main.py             # pywebview launcher (starts Flask in background and opens a window)
├─ templates/          # HTML templates (index, manage, sales, settings, stocklog, receipt)
├─ static/             # CSS/JS/images (runtime images are mapped from a separate folder)
├─ inventory.db        # (legacy location, auto-migrated on first run)
├─ uploads/            # (legacy location, auto-migrated)
├─ requirements.txt
└─ icon.ico
```

### Runtime data directories

At runtime everything is stored in a **persistent, user-space folder** (created automatically):

- **Windows:** `%LOCALAPPDATA%\TreasurePOS`
- **macOS:** `~/Library/Application Support/TreasurePOS`
- **Linux:** `~/.local/share/treasurepos`

Override with env var **`TREASUREPOS_DATA_DIR`** if you want a custom path.

Folders created inside the data dir:

```
inventory.db          # SQLite DB
uploads/              # imported Excel files (if applicable)
images/               # product images (served via /static/images/<name>)
```

On first run, the app will **migrate** any legacy `inventory.db` and `static/images/*` into the new runtime folders.

---

## ▶️ Run From Source (Dev)

```bash
# 1) Create venv & install deps
python -m venv venv
venv\Scripts\activate   # macOS/Linux: source venv/bin/activate
pip install -r requirements.txt

# 2) (One-time) install Playwright browser
python -m playwright install chromium

# 3) Start dev server
python app.py

# By default the app binds 127.0.0.1 on an OS-chosen port (0).
# To stick to a port (e.g. 5000), set:
#   set TREASUREPOS_PORT=5000   (PowerShell: $env:TREASUREPOS_PORT=5000)
#   or export TREASUREPOS_PORT=5000  (macOS/Linux)
```

**Access:** http://127.0.0.1:5000 (or the chosen port).  
**Health check:** `/healthz` → `ok`.

> `main.py` starts Flask on an available port and opens a **desktop window** via **pywebview**. You can run it directly for a desktop-like UX:
>
> ```bash
> python main.py
> ```

---

## 🛠️ Build (PyInstaller, onedir)

**Fast onedir build with icon (Windows):**

```powershell
pyinstaller --noconfirm --clean --onedir --name TreasurePOS --icon icon.ico main.py ^
  --add-data "templates;templates" ^
  --add-data "static;static" ^
  --hidden-import "playwright.sync_api" ^
  --hidden-import "win32timezone"
```

After build, run: `dist/TreasurePOS/TreasurePOS.exe`.

> **First launch** on a new machine: a small pop-up may appear while **Playwright** downloads **Chromium**. If not already installed, run:
>
> ```powershell
> TreasurePOS\TreasurePOS.exe --install-browser
> # or from Python:
> python -m playwright install chromium
> ```

If packaging misses some resources, you can try adding:

```powershell
# More aggressive resource collection (if needed)
--collect-all playwright --collect-all PIL --collect-all flask_cors --collect-all pywebview
```

---

## ⚙️ Configuration (Env Vars)

- `TREASUREPOS_DATA_DIR` — override persistent data directory
- `TREASUREPOS_PORT` or `PORT` — bind port for Flask; if not set, OS assigns a free one
- Printer name is currently **hardcoded** in `app.py` under `print_receipt()`:
  ```python
  printer_name = "ZDesigner ZD230-203dpi ZPL"
  ```
  Change it to match your installed Windows printer (Control Panel → Printers).

---

## 🧱 Database & Models

SQLite DB (`inventory.db`) with the following tables (created/migrated automatically):

- **items**
  - `barcode` (unique), `name`, `qty`, `category`, `size`, `status`, `image`, `discontinued_time`
  - Pricing stored in both float (legacy) and **integer cents** columns:
    - `price_int`, `wholesale_price_int` (integer, preferred for arithmetic)
- **sales**
  - `time`, `items` (JSON cart snapshot), `pay_type` (`cash`/`card`), `refunded`
  - `total_int` (integer total; preferred), legacy `total` kept for compatibility
- **sale_items**
  - One row per item per sale: `sale_id`, `barcode`, `name`, `category`, `size`, `qty`, `price_int` (+ legacy `price`)
- **stock_log**
  - Manual or automatic stock changes (`in`, `out`, `sale`, `refund`, `delete_revert`)
- **refund_log**
  - Reason & amount for refunds/deletions

> Arithmetic is always done using **integer** columns (`*_int`) when present; legacy float columns are only read as **fallback**.

---

## 📦 Import / Export

### Import Products (Excel)

- Endpoint: `POST /import/items`  
- Excel header **must** be:  
  `barcode, name, price, wholesale_price, qty, category, size, [status], [image]`
- **Category** allowed: `bag, top, bottom, shoes, dress` (`pants` is normalized to `bottom`)
- **Size** allowed: `free, s, m, l, xl`
- **Image** supports only controlled relative paths like `images/abc.jpg`. Any path outside this pattern is **ignored** for safety.
- Negative qty is automatically rejected.

### Export

- **Items:** `GET /export/items` → `상품목록_items.xlsx`
- **Sales:** `GET /export/sales?start=YYYY-MM-DD&end=YYYY-MM-DD&pay_type=cash|card&fmt=xlsx|csv`
  - `fmt=csv` returns a **streamed CSV** for large datasets

---

## 🔎 APIs (Selected)

- `GET /api/items` — list all items (split to on-sale & discontinued)
- `GET /api/items/search?q=&category=&sort=&page=&page_size=` — server-side search & pagination
- `GET /api/item/<barcode>` — single item
- `POST /api/item` — add item (JSON or form-data with image)
- `PUT /api/item/<barcode>` — edit item (supports changing barcode and image)
- `DELETE /api/item/<barcode>` — delete item (and its image on disk)
- `POST /api/stockio` — manual stock in/out (`{"barcode":"...", "change":5, "type":"in|out"}`)
- `POST /api/sale` — checkout (writes `sales`, `sale_items`, `stock_log` atomically)
- `GET /api/sales?page=&page_size=&pay_type=` — paginated sales
- `POST /api/sale/delete` — batch delete sales with stock revert
- `POST /api/sale/refund` — batch refund with stock revert
- `GET /api/sales/top_items?days=&pay_type=` — top 10 selling items (by qty)
- `GET /api/sales/stats?group=day|week|month|year&start=&end=&pay_type=` — sales charts
- `GET /api/sales/heatmap_hour_weekday?metric=orders|sales|items&start=&end=&pay_type=` — heatmap
- `GET /api/item_sales/<barcode>` — sales detail for a single item
- `GET /healthz` — health check

---

## 🖨️ Receipt Rendering & Printing (ZPL)

- The template is **`templates/receipt.html`**. Canvas width is set to **`624px`** (≈79 mm).  
  If your printer is strict 203 dpi you can switch to **`632px`** in the CSS.
- Rendering pipeline:
  1. `render_receipt_png(url, out_path, width_px=624)` — **Playwright** opens `/receipt/<id>` and takes an **element screenshot** of `.receipt` (no extra blank space).
  2. Convert PNG → **ZPL (~DG + ^XG)** via `image_to_zpl()`.
  3. Print with **pywin32** (Windows). Non-Windows returns a JSON note saying rendering succeeded.

- ZPL footer uses the **actual image width/height** to set `^PW` and `^LL` dynamically so the paper advances correctly.

### Customizing your receipt

Open `templates/receipt.html` and tweak these safe knobs:

- **Logo & spacing:** `.logo-container{ margin:6px 0 24px; }`
- **Table alignment:** *Column 2 & 3 are centered; Column 4 is right-aligned & vertically centered; Names wrap; qty is centered.*
- **VAT notice:** text size is slightly larger; “not included” wording shown only for cash.
- **Bottom blank:** `.tail-blank{ height: calc(2 * var(--cm)); }` ensures a fixed ~2 cm tear margin.

> If you see **multiple horizontal lines** before totals, make sure you have **only one** `<hr>` in the template and avoid table borders that clash with it.

---

## 🧰 Troubleshooting

- **Playwright not available**: install with `python -m playwright install chromium`.
- **Printer not found**: edit `printer_name` in `app.py` (`print_receipt`) to your actual Windows printer.
- **Port already used**: set `TREASUREPOS_PORT` to a free port (e.g. 5001) or use `main.py` which auto-picks a port.
- **Images not showing**: only file names like `images/xxx.png` are allowed; anything else is blocked by the safety filter.
- **EXE missing resources**: rebuild with additional `--collect-all` flags (see build section).

---

## 📜 License

Private project — choose a license that fits your distribution model (MIT/Apache-2.0/Proprietary).

---

# 🇨🇳 简体中文

## 概述

TreasurePOS 是一个**本地优先**的收银系统，基于 Flask。库存、销售、退款、出入库都包含在内；导入/导出 Excel，销售支持 CSV 流式导出。小票使用 **Playwright** 截图元素（`.receipt`），再转 **ZPL** 发送到条码打印机（Windows 下使用 pywin32）。

### 主要特点

- 数据持久化到用户数据目录（自动迁移旧库与旧图片）
- 价格用 **整数**列（`*_int`）计算，避免浮点误差
- 高性能搜索/分页 API
- Excel 导入导出 & CSV 导出
- 79 mm 小票（默认 624px 画布）
- 桌面壳：`main.py` 通过 pywebview 打开窗口

## 安装与运行

```bash
python -m venv venv
venv\Scripts\activate    # macOS/Linux: source venv/bin/activate
pip install -r requirements.txt
python -m playwright install chromium
python app.py                 # 或 python main.py 启动桌面窗口
# 如需固定端口： set TREASUREPOS_PORT=5000
```

## 打包（onedir，带图标）

```powershell
pyinstaller --noconfirm --clean --onedir --name TreasurePOS --icon icon.ico main.py ^
  --add-data "templates;templates" ^
  --add-data "static;static" ^
  --hidden-import "playwright.sync_api" ^
  --hidden-import "win32timezone"
```

首次运行若缺浏览器，请执行：`python -m playwright install chromium`。

## 配置

- `TREASUREPOS_DATA_DIR`：自定义数据目录
- `TREASUREPOS_PORT`/`PORT`：端口
- 打印机名在 `app.py` 的 `print_receipt()` 中修改

## 常用 API

- `POST /import/items` 导入；`GET /export/items` 导出商品
- `GET /export/sales?...&fmt=csv` 导出销售 CSV
- `POST /api/sale` 结算；`POST /api/sale/refund` 退款；`POST /api/sale/delete` 删除订单（回补库存）
- `GET /api/items/search` 搜索分页；`GET /api/sales/stats` 统计；`GET /api/sales/heatmap_hour_weekday` 热力图

## 自定义小票

编辑 `templates/receipt.html`：Logo 间距、表格对齐、VAT 文案和底部空白等均可直接改 CSS 变量/类名。

---

# 🇰🇷 한국어

## 개요

TreasurePOS는 **로컬 우선** Flask 기반 POS입니다. 재고·판매·환불·입출고를 지원하며, 엑셀 가져오기/내보내기와 판매 CSV 스트리밍을 제공합니다. 영수증은 **Playwright**로 `.receipt` 요소만 캡처하여 PNG로 만들고, 이를 **ZPL**로 변환해 Windows 프린터( pywin32 )로 출력합니다.

### 특징

- 사용자 데이터 폴더에 **영구 저장**(최초 실행 시 기존 DB/이미지 자동 마이그레이션)
- 금액은 **정수 컬럼**(`*_int`)으로 계산해 오차 방지
- 고성능 검색/페이지네이션 API
- Excel 입·출력 & CSV 내보내기
- 79 mm 용지(기본 624px 캔버스)
- `main.py`로 데스크톱 창(pywebview) 실행 가능

## 설치 및 실행

```bash
python -m venv venv
venv\Scripts\activate   # macOS/Linux: source venv/bin/activate
pip install -r requirements.txt
python -m playwright install chromium
python app.py             # 또는 python main.py
# 고정 포트가 필요하면: set TREASUREPOS_PORT=5000
```

## 빌드(onedir, 아이콘 포함)

```powershell
pyinstaller --noconfirm --clean --onedir --name TreasurePOS --icon icon.ico main.py ^
  --add-data "templates;templates" ^
  --add-data "static;static" ^
  --hidden-import "playwright.sync_api" ^
  --hidden-import "win32timezone"
```

최초 실행 시 브라우저가 없으면 `python -m playwright install chromium`을 먼저 실행하세요.

## 환경 변수

- `TREASUREPOS_DATA_DIR` — 데이터 폴더 지정
- `TREASUREPOS_PORT`/`PORT` — 포트
- 프린터 이름은 `app.py` 의 `print_receipt()` 내부에서 변경

## 주요 API

- `POST /import/items` 상품 엑셀 가져오기 · `GET /export/items` 내보내기
- `GET /export/sales?...&fmt=csv` 판매 CSV
- `POST /api/sale` 결제 · `POST /api/sale/refund` 환불 · `POST /api/sale/delete` 삭제(재고 복원)
- `GET /api/items/search` 검색/페이지 · `GET /api/sales/stats` 통계 · `GET /api/sales/heatmap_hour_weekday` 히트맵

## 영수증 커스터마이즈

`templates/receipt.html`에서 로고 간격, 표 정렬, VAT 문구, 하단 공백 등을 간단히 CSS로 조정할 수 있습니다.

---

*This README supersedes the previous one. Below is the original content preserved for reference.*

<details>
<summary>Original README (collapsed)</summary>

{old_text}

</details>
