# TreasurePOS · Flask‑based Local POS (79 mm Receipt, ZPL)

**Languages · 语言 · 언어:** [English](#english) · [简体中文](#简体中文) · [한국어](#한국어)

---

TreasurePOS is a **local‑first** POS built with Flask. It handles inventory, checkout, refunds, stock I/O, and exports. Receipts are rendered as an HTML element (`.receipt`), **screenshot with Playwright** to PNG, converted to **ZPL**, and printed on Zebra‑compatible printers (Windows via pywin32).  
Data is stored in a persistent **user data directory** (outside the repo) and legacy data is migrated automatically on first run.

> If you just want the Windows EXE fast, jump to **[Build → PyInstaller (onedir)](#build--pyinstaller-onedir)**.

---

## Highlights

- Local‑first Flask app (no external DB required)
- Persistent **data directory** with **auto‑migration** (DB + images)
- Integer‑safe pricing columns (`*_int`) for precise arithmetic
- Fast search & pagination endpoints
- Excel (`xlsx`) import/export, **CSV streaming** for sales
- **Playwright element screenshot** → PNG → **ZPL** → Windows printing
- Optimized **79 mm** receipt layout (canvas **624px** wide), tuned for 203 dpi
- Optional **pywebview shell** (`main.py`) for a desktop‑like window

---

## Project Layout

> This repository ships the Python sources and **HTML templates**. Product images are **not** bundled. At runtime, images live in the data directory under `images/`, and are served via a dedicated route (`/static/images/<file>`). You can reference them with `url_for('serve_runtime_image', filename='name.png')` in templates.

```
.
├─ app.py              # Flask app: APIs, DB, printing (Playwright→ZPL), runtime paths
├─ main.py             # pywebview launcher (starts Flask and opens window)
├─ templates/          # HTML templates (index, manage, sales, settings, stocklog, receipt)
├─ README.md
└─ icon.ico            # (optional) your app icon for packaging
```

### Runtime data directories

At first launch TreasurePOS creates a persistent data folder (or use `TREASUREPOS_DATA_DIR` to override):

- **Windows:** `%LOCALAPPDATA%\TreasurePOS`
- **macOS:** `~/Library/Application Support/TreasurePOS`
- **Linux:** `~/.local/share/treasurepos`

It contains:

```
inventory.db          # SQLite database
uploads/              # Imported Excel files (if any)
images/               # Product images (served at /static/images/<file>)
```

The app migrates any legacy `inventory.db` and `static/images/*` into these runtime folders automatically.

---

## Quickstart (Dev)

```bash
# 1) Create and activate a virtualenv
python -m venv venv
# Windows:
venv\Scripts\activate
# macOS/Linux:
# source venv/bin/activate

# 2) Install dependencies
pip install flask flask-cors pandas openpyxl pillow playwright pywin32

# 3) Install Playwright browser once
python -m playwright install chromium

# 4) Run the Flask app (binds 127.0.0.1 on a free port by default)
python app.py

# Or launch the desktop window with pywebview:
python main.py
```

Access: http://127.0.0.1:5000 (or the chosen port).  
Health check: `GET /healthz` → `ok`.

Environment overrides:
```bash
# choose a fixed port
# Windows (cmd):   set TREASUREPOS_PORT=5000
# PowerShell:      $env:TREASUREPOS_PORT=5000
# macOS/Linux:     export TREASUREPOS_PORT=5000

# set a custom data dir
# Windows (cmd):   set TREASUREPOS_DATA_DIR=D:\TreasurePOSdata
# macOS/Linux:     export TREASUREPOS_DATA_DIR=/path/to/TreasurePOSdata
```

---

## Build · PyInstaller (onedir)

**Fast Windows build with icon (recommended):**
```powershell
pyinstaller --noconfirm --clean --onedir --name TreasurePOS --icon icon.ico main.py ^
  --add-data "templates;templates" ^
  --hidden-import "playwright.sync_api" ^
  --hidden-import "win32timezone"
```

Run the app: `dist\TreasurePOS\TreasurePOS.exe`

> If Chromium isn’t installed on the target machine, run once:
> ```powershell
> python -m playwright install chromium
> ```

If packaging misses resources on your setup, add collectors:
```powershell
--collect-all playwright --collect-all PIL --collect-all flask_cors --collect-all pywebview
```

---

## Configuration

- `TREASUREPOS_DATA_DIR` — persistent data folder
- `TREASUREPOS_PORT` or `PORT` — server port (default: OS‑assigned free port)
- **Printer name** — in `app.py` → `print_receipt()`, set:
  ```python
  printer_name = "ZDesigner ZD230-203dpi ZPL"  # change to your printer’s name
  ```

---

## Database (SQLite)

**items**
- `barcode` (unique), `name`, `qty`, `category`, `size`, `status`, `image`, `discontinued_time`
- Prices kept in legacy float and integer columns:
  - `price_int`, `wholesale_price_int` (integers are preferred for all math)

**sales**
- `time`, `items` (cart JSON snapshot), `pay_type` (`cash`/`card`), `refunded`
- `total_int` (preferred), legacy `total` for fallback

**sale_items**
- Per‑item detail for each sale: `sale_id`, `barcode`, `name`, `category`, `size`, `qty`, `price_int` (+ legacy `price`)

**stock_log**
- Tracks stock changes (`in`, `out`, `sale`, `refund`, `delete_revert`)

**refund_log**
- Reason & amount (for refunds/deletes)

_All write paths prefer integer columns; legacy float values are only used as a last resort._

---

## Import / Export

**Import products (Excel):** `POST /import/items`  
Excel header must be:
```
barcode, name, price, wholesale_price, qty, category, size, [status], [image]
```
- Category: `bag, top, bottom, shoes, dress` (`pants` is normalized to `bottom`)
- Size: `free, s, m, l, xl`
- Image: only **controlled relative paths** like `images/abc.jpg` are accepted for safety

**Export:**
- Items: `GET /export/items` → `상품목록_items.xlsx`
- Sales: `GET /export/sales?start=YYYY-MM-DD&end=YYYY-MM-DD&pay_type=cash|card&fmt=xlsx|csv`
  - `fmt=csv` streams a CSV for large datasets

---

## Selected API Endpoints

- `GET /api/items` — list items (on‑sale & discontinued split)
- `GET /api/items/search?q=&category=&sort=&page=&page_size=` — server‑side search/pagination
- `GET /api/item/<barcode>` — fetch one item
- `POST /api/item` — add (JSON or multipart with image)
- `PUT /api/item/<barcode>` — edit (supports barcode change + image)
- `DELETE /api/item/<barcode>` — delete (also removes image file if any)
- `POST /api/stockio` — manual stock I/O (`{"barcode":"...","change":5,"type":"in|out"}`)
- `POST /api/sale` — checkout transaction (writes `sales`, `sale_items`, `stock_log` atomically)
- `GET /api/sales?page=&page_size=&pay_type=` — paginated sales
- `POST /api/sale/delete` — batch delete (with stock revert)
- `POST /api/sale/refund` — batch refund (with stock revert)
- `GET /api/sales/top_items?days=&pay_type=` — top products by quantity
- `GET /api/sales/stats?group=day|week|month|year&start=&end=&pay_type=` — time‑series charts
- `GET /api/sales/heatmap_hour_weekday?metric=orders|sales|items&start=&end=&pay_type=` — weekday×hour heatmap
- `GET /api/item_sales/<barcode>` — sale detail for one item

---

## Receipt Rendering & Fine‑Tuning

The receipt template is `templates/receipt.html`. Canvas width is **624px** (~79 mm).  
Pipeline: Playwright opens `/receipt/<id>`, captures **only** the `.receipt` element → PNG → ZPL (`~DG + ^XG`). `^PW`/`^LL` are set dynamically to match the image size so paper advances precisely.

**Common customizations (CSS):**

```css
/* Canvas width for 79 mm paper */
:root { --paper-w: 624px; }

/* Logo spacing (more bottom space) */
.logo-container { margin: 6px 0 30px; }

/* Table spacing & wrapping */
table { table-layout: fixed; }
th, td { padding: 11px 7px; word-break: break-word; overflow-wrap: anywhere; }

/* Name column more space to the right */
td.name-cell { padding-right: 12px; }

/* Columns: #2 & #3 center both axes; #4 right & vertical‑middle */
thead th:nth-child(2),
tbody td:nth-child(2),
thead th:nth-child(3),
tbody td:nth-child(3) {
  text-align: center;
  vertical-align: middle;
}
thead th:nth-child(4),
tbody td:nth-child(4) {
  text-align: right;
  vertical-align: middle;
}

/* VAT notice a bit larger (cash only) */
.vat-notice { font-size: 1.1em; font-weight: 600; }

/* Bottom tear margin: ~2 cm fixed space */
.tail-blank { height: 2cm; }
```

If you see stacked lines above totals, ensure you don’t mix multiple `<hr>` and table borders in the same spot. Keep one separator (`<hr>`) and borders on table rows—avoid both on the same boundary.

---

## Troubleshooting

- **Playwright not installed** → `python -m playwright install chromium`
- **Printer not found** → set `printer_name` in `app.py` to your installed Zebra (exact Control Panel name)
- **Port in use** → set `TREASUREPOS_PORT` to a free one or run `main.py` (auto‑selects a port)
- **Images don’t show** → only relative `images/<file>` is accepted for safety; anything else is ignored
- **EXE misses stuff** → rebuild with the `--collect-all` flags in the build section

---

# 简体中文

TreasurePOS 是一个 **本地优先** 的 Flask 收银系统。支持库存、结算、退款、出入库；商品导入/导出（Excel）、销售导出（CSV 流式）。小票用 Playwright 对 `.receipt` **元素截图**→PNG→**ZPL** 打印（Windows 通过 pywin32）。数据持久化在用户数据目录，首次运行会自动迁移旧库/图片。

## 亮点

- 单机本地运行，无需外部数据库
- 用户数据目录（DB+图片）**自动迁移**
- 金额使用 **整数列** 计算（`*_int`），避免小数误差
- 高性能搜索/分页 API
- Excel 导入导出、销售 CSV
- **元素截图** 渲染小票 → ZPL 打印
- 79 mm 小票（默认 624px 画布）
- `main.py` 提供桌面窗口（pywebview）

## 目录结构（仓库）

> 仓库包含 Python 源码与 **模板**；**不包含**产品图片。运行时图片位于数据目录的 `images/`，并通过路由 `/static/images/<file>` 对外提供；模板里可用 `url_for('serve_runtime_image', filename='xxx.png')` 引用。

```
app.py, main.py, templates/, README.md, icon.ico
```

## 开发运行

```bash
python -m venv venv
venv\Scripts\activate   # macOS/Linux: source venv/bin/activate
pip install flask flask-cors pandas openpyxl pillow playwright pywin32
python -m playwright install chromium
python app.py           # 或 python main.py
```

- 访问：http://127.0.0.1:5000  
- 健康检查：`/healthz` → `ok`  
- 环境变量：`TREASUREPOS_PORT`（端口）、`TREASUREPOS_DATA_DIR`（数据目录）

## 打包（onedir，带图标）

```powershell
pyinstaller --noconfirm --clean --onedir --name TreasurePOS --icon icon.ico main.py ^
  --add-data "templates;templates" ^
  --hidden-import "playwright.sync_api" ^
  --hidden-import "win32timezone"
```

首次运行如缺浏览器：`python -m playwright install chromium`。

## 收据微调（CSS）

- 画布：`--paper-w: 624px`（≈79 mm）  
- 第 2/3 列 **上下左右居中**；第 4 列 **右对齐且垂直居中**：
  ```css
  thead th:nth-child(2), tbody td:nth-child(2),
  thead th:nth-child(3), tbody td:nth-child(3) { text-align:center; vertical-align:middle; }
  thead th:nth-child(4), tbody td:nth-child(4) { text-align:right; vertical-align:middle; }
  ```
- Logo 下间距：`.logo-container { margin: 6px 0 30px; }`  
- 底部留白：`.tail-blank { height: 2cm; }`

## 常见问题

- Playwright 未安装 → `python -m playwright install chromium`
- 打印机找不到 → 修改 `app.py` 中 `printer_name` 为系统里的 Zebra 名称
- 端口占用 → 设置 `TREASUREPOS_PORT` 或使用 `main.py` 自动选端口
- 图片不显示 → 仅允许 `images/<文件>` 相对路径，其它路径会被忽略

---

# 한국어

TreasurePOS는 **로컬 우선** Flask 기반 POS입니다. 재고/결제/환불/입출고를 지원하고, Excel 가져오기/내보내기 및 판매 CSV 스트리밍을 제공합니다. 영수증은 Playwright로 `.receipt` **요소만 캡처**→PNG→**ZPL**로 변환하여 Zebra 프린터(Windows, pywin32)로 출력합니다. 데이터는 사용자 데이터 디렉터리에 저장되며, 첫 실행 시 기존 DB/이미지를 자동 마이그레이션합니다.

## 특징

- 외부 DB 없이 단일 실행
- 사용자 데이터 폴더(그 안에 DB/이미지) **자동 마이그레이션**
- 금액은 **정수 컬럼**으로 계산 (`*_int`)
- 빠른 검색/페이지 API
- Excel 입·출력, 판매 CSV
- **요소 스크린샷** 기반 영수증 → ZPL 출력
- 79 mm 용지(기본 624px 폭)
- 데스크톱 창 (`main.py`, pywebview)

## 리포지토리 구성

> 리포지토리에는 파이썬 소스와 **템플릿**이 포함됩니다. 제품 이미지는 **동봉되지 않으며**, 실행 시 데이터 디렉터리의 `images/` 에 저장됩니다. 라우트 `/static/images/<file>` 로 제공되며, 템플릿에서 `url_for('serve_runtime_image', filename='xxx.png')` 로 참조할 수 있습니다.

```
app.py, main.py, templates/, README.md, icon.ico
```

## 개발 실행

```bash
python -m venv venv
venv\Scripts\activate   # macOS/Linux: source venv/bin/activate
pip install flask flask-cors pandas openpyxl pillow playwright pywin32
python -m playwright install chromium
python app.py           # 또는 python main.py
```

- 접속: http://127.0.0.1:5000  
- 헬스체크: `/healthz` → `ok`  
- 환경변수: `TREASUREPOS_PORT`(포트), `TREASUREPOS_DATA_DIR`(데이터 폴더)

## 빌드 (onedir, 아이콘)

```powershell
pyinstaller --noconfirm --clean --onedir --name TreasurePOS --icon icon.ico main.py ^
  --add-data "templates;templates" ^
  --hidden-import "playwright.sync_api" ^
  --hidden-import "win32timezone"
```

최초 실행에 브라우저가 없으면: `python -m playwright install chromium`

## 영수증 미세조정 (CSS)

- 폭: `--paper-w: 624px` (≈79 mm)  
- 2/3열 **수직·수평 중앙정렬**, 4열 **우측정렬 + 수직 중앙**:
  ```css
  thead th:nth-child(2), tbody td:nth-child(2),
  thead th:nth-child(3), tbody td:nth-child(3) { text-align:center; vertical-align:middle; }
  thead th:nth-child(4), tbody td:nth-child(4) { text-align:right; vertical-align:middle; }
  ```
- 로고 하단 여백: `.logo-container { margin: 6px 0 30px; }`  
- 하단 여백: `.tail-blank { height: 2cm; }`

## 문제 해결

- Playwright 미설치 → `python -m playwright install chromium`
- 프린터 이름 불일치 → `app.py` 의 `printer_name` 를 시스템의 Zebra 이름으로 수정
- 포트 충돌 → `TREASUREPOS_PORT` 지정 또는 `main.py` 사용
- 이미지 미표시 → `images/<파일>` 형태만 허용하며, 그 외 경로는 무시됨

---

**License:** Choose what fits your distribution (MIT/Apache‑2.0/Proprietary).

