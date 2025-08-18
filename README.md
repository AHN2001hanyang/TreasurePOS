# TreasurePOS · Flask POS for 79 mm Receipts (ZPL)

[![Python](https://img.shields.io/badge/Python-3.9%2B-blue.svg)](#)
[![Flask](https://img.shields.io/badge/Flask-2.x-black.svg)](#)
[![Playwright](https://img.shields.io/badge/Playwright-Chromium-green.svg)](#)
[![Platform](https://img.shields.io/badge/OS-Windows%20%7C%20macOS%20%7C%20Linux-informational.svg)](#)
[![Packaging](https://img.shields.io/badge/PyInstaller-onedir-orange.svg)](#)

> A local‑first Point of Sale built with Flask. Element‑level receipt rendering (Playwright ➜ PNG ➜ ZPL) for **79 mm** printers, safe integer pricing, fast search, Excel import/export, and a desktop window via **pywebview**.

**Languages · 语言 · 언어:**  
**[🇺🇸 English](#-english)** · **[🇨🇳 简体中文](#-简体中文)** · **[🇰🇷 한국어](#-한국어)**

---

## Table of Contents

- [Highlights](#-highlights)
- [Project Layout](#-project-layout)
- [Runtime Data \& Paths](#-runtime-data--paths)
- [Run From Source](#-run-from-source)
- [Build (PyInstaller, onedir)](#-build-pyinstaller-onedir)
- [Configuration](#-configuration)
- [Database](#-database)
- [Import / Export](#-import--export)
- [Core APIs](#-core-apis)
- [Receipt Rendering & Printing](#-receipt-rendering--printing)
- [Customize the Receipt](#-customize-the-receipt)
- [Troubleshooting](#-troubleshooting)
- [i18n](#-i18n)
- [License](#-license)
- [简体中文](#-简体中文)
- [한국어](#-한국어)

---

## ✨ Highlights

- **Local‑first** Flask app with templates under `templates/` and assets under `static/`  
- **Persistent data dir** (auto‑migration of old DB & images on first run)
- **Integer‑safe pricing** (`*_int` columns) to avoid floating‑point issues
- **Fast search & pagination** (`/api/items/search`) and **top‑10** view
- **Excel import/export** (xlsx) and **CSV streaming** for sales
- **Element screenshot** of `.receipt` using **Playwright** ➜ PNG ➜ **ZPL** printing (Windows via pywin32)
- **79 mm paper** layout (CSS canvas **624 px** width tuned for 203 dpi)
- **pywebview shell** (`main.py`) for a desktop‑like window

---

## 🗂 Project Layout

```
flask-pos2.0/
├─ app.py              # Flask app: APIs, DB, printing, file safety
├─ main.py             # pywebview launcher: starts Flask & opens a window
├─ templates/          # index.html, manage.html, sales.html, settings.html, stocklog.html, receipt.html
├─ static/             # static assets; runtime images are mapped from a separate folder
├─ requirements.txt
└─ icon.ico
```

> **Note:** Legacy `inventory.db` and `static/images/*` are **auto‑migrated** to the runtime data directory on first run.

---

## 📂 Runtime Data & Paths

All runtime data lives in a **persistent user directory** (created automatically). You can override via `TREASUREPOS_DATA_DIR`.

| Platform | Default path |
|---|---|
| **Windows** | `%LOCALAPPDATA%\\TreasurePOS` |
| **macOS** | `~/Library/Application Support/TreasurePOS` |
| **Linux** | `~/.local/share/treasurepos` |

Inside this directory the app creates:

```
inventory.db   # SQLite DB
uploads/       # Excel uploads (if any)
images/        # product images (served via /static/images/<name>)
```

The route `/static/images/<filename>` is mapped to that **runtime** `images` folder; file names are **whitelisted** (no `..`, no absolute paths).

---

## ▶️ Run From Source

```bash
# 1) Create venv & install dependencies
python -m venv venv
# Windows
venv\Scripts\activate
# macOS/Linux
# source venv/bin/activate

pip install -r requirements.txt

# 2) Install Playwright browser (one time per machine)
python -m playwright install chromium

# 3) Start
python app.py
# or desktop window:
python main.py
```

- By default the server binds to **127.0.0.1** on an **OS‑chosen port** (0).  
  Set a port explicitly via env var `TREASUREPOS_PORT=5000` (or `PORT`).

**Health check:** `GET /healthz` → `ok`

---

## 🛠 Build (PyInstaller, onedir)

**Windows (fast onedir, with icon):**

```powershell
pyinstaller --noconfirm --clean --onedir --name TreasurePOS --icon icon.ico main.py ^
  --add-data "templates;templates" ^
  --add-data "static;static" ^
  --hidden-import "playwright.sync_api" ^
  --hidden-import "win32timezone"
```

Run: `dist/TreasurePOS/TreasurePOS.exe`

> **Playwright browsers**: on the first print action Playwright may download **Chromium** automatically (internet required).  
> If you prefer to preinstall during development:
> ```bash
> python -m playwright install chromium
> ```
> Advanced (optional): set `PLAYWRIGHT_BROWSERS_PATH=0` before installing to keep browsers **inside the project** so you can ship them with your build.

If packaging misses resources, add (use sparingly):

```powershell
--collect-all playwright --collect-all PIL --collect-all flask_cors --collect-all pywebview
```

---

## ⚙️ Configuration

- `TREASUREPOS_DATA_DIR` — custom data directory
- `TREASUREPOS_PORT` or `PORT` — preferred port
- Printer name is **hardcoded** in `app.py > print_receipt()`:
  ```python
  printer_name = "ZDesigner ZD230-203dpi ZPL"
  ```
  Change it to match your Windows printer.

---

## 🧱 Database

SQLite (`inventory.db`) with auto‑migrations. Key tables:

- **items** — `barcode` (unique), `name`, `qty`, `category`, `size`, `status`, `image`, `discontinued_time`, and **integer** pricing `price_int`, `wholesale_price_int` (legacy floats kept for compatibility).
- **sales** — `time`, `items` (JSON snapshot), `pay_type` (`cash`/`card`), `refunded`, **integer** `total_int`.
- **sale_items** — per‑item lines with `price_int`, `qty`, `category`, `size`.
- **stock_log** — `in`, `out`, `sale`, `refund`, `delete_revert`.
- **refund_log** — reason + amount.

> All math uses **integer** columns when present; floats are fallback only.

Indexes are created for common lookups (`items(barcode/name/category)`, `sales(time/pay_type)`, etc.).

---

## 📦 Import / Export

### Import Products (Excel)

- Endpoint: `POST /import/items`  
- Required header (case‑sensitive):  
  `barcode, name, price, wholesale_price, qty, category, size, [status], [image]`
- Category: `bag, top, bottom, shoes, dress` (`pants` normalized to `bottom`)
- Size: `free, s, m, l, xl`
- Image: only **relative** `images/<file>` is accepted (safe whitelist).

### Export

- **Items:** `GET /export/items` → `상품목록_items.xlsx`
- **Sales:** `GET /export/sales?start=YYYY-MM-DD&end=YYYY-MM-DD&pay_type=cash|card&fmt=xlsx|csv`  
  `fmt=csv` streams CSV (better for large ranges).

---

## 🔎 Core APIs

| Method | Path | Notes |
|---|---|---|
| GET | `/api/items` | split result: `onsale`, `discontinued` |
| GET | `/api/items/search?q=&category=&sort=&page=&page_size=` | server‑side search & pagination |
| GET | `/api/item/<barcode>` | single item (integer prices) |
| POST | `/api/item` | add (JSON or multipart with `image`) |
| PUT | `/api/item/<barcode>` | edit (supports **changing** barcode & image) |
| DELETE | `/api/item/<barcode>` | delete item (and remove its image) |
| POST | `/api/stockio` | manual stock in/out (`{"barcode","change","type":"in|out"}`) |
| POST | `/api/sale` | checkout (atomic: `sales`, `sale_items`, `stock_log`) |
| GET | `/api/sales?page=&page_size=&pay_type=` | paginated sales (integer totals) |
| POST | `/api/sale/delete` | batch delete sales (restocks if not refunded) |
| POST | `/api/sale/refund` | batch refund (restocks) |
| GET | `/api/sales/top_items?days=&pay_type=` | top 10 items by qty |
| GET | `/api/sales/stats?group=day|week|month|year&start=&end=&pay_type=` | totals/ orders grouped |
| GET | `/api/sales/heatmap_hour_weekday?metric=orders|sales|items&start=&end=&pay_type=` | heatmap data |
| GET | `/api/item_sales/<barcode>` | sale lines for one item |
| GET | `/healthz` | health check |

---

## 🖨️ Receipt Rendering & Printing

**Template:** `templates/receipt.html` (canvas width **624 px** ≈ 79 mm).

Pipeline in `app.py`:

1. **Playwright** opens `GET /receipt/<sale_id>?for_print=1` and takes an **element screenshot** of `.receipt` (no extra margins). Function: `render_receipt_png()`.
2. PNG ➜ **ZPL** (`~DG` + `^XG`) via `image_to_zpl()`.
3. Printer job (**Windows**): pywin32 writes raw ZPL to your configured printer in `print_receipt()`.

The ZPL wrapper sets **`^PW`** (width) and **`^LL`** (length) from the real image size to avoid over/under‑feed.

---

## 🎨 Customize the Receipt

Open `templates/receipt.html`. Useful knobs:

- **Canvas width:** `:root { --paper-w: 624px; }`
- **Logo spacing:** `.logo-container { margin: 6px 0 24px; }`
- **Table alignment:** Column 2 & 3 centered; Column 4 right‑aligned & vertically centered; names wrap nicely.
- **Bottom tear margin:** `.tail-blank { height: calc(2 * var(--cm)); }`
- **No overlap:** totals block is isolated in its own container (`.totals`), and the screenshot is element‑based, so long names/quantities won’t overlap totals.

If you ever see **multiple horizontal lines**, ensure there’s only **one** `<hr>` around the table and that table borders don’t duplicate the line (only `border-bottom` on rows).

---

## 🧰 Troubleshooting

- **Playwright missing** → `python -m playwright install chromium`  
- **Printer not found** → set your printer name in `print_receipt()`  
- **Port conflict** → set `TREASUREPOS_PORT` to a free port (e.g., 5001)  
- **Images not loading** → only `images/<file>` paths are allowed; others are sanitized away  
- **EXE lacks resources** → add `--collect-all` flags (see build section)

---

## 🌐 i18n

Language dictionary lives in `app.py` (`TEXTS`). Default is **Korean** if no cookie is present. Switch language via:
```
/set_lang/ko   /set_lang/zh   /set_lang/en
```

---

## 📜 License

Choose a license suitable for your distribution (MIT/Apache‑2.0/Proprietary).

---

# 🇨🇳 简体中文

## ✨ 特性

- **本地优先**：模板在 `templates/`，静态资源在 `static/`
- **数据持久化**：首次运行自动迁移旧 DB 和图片
- **整数金额列**（`*_int`）避免浮点误差
- **服务端搜索/分页**、TOP10
- **Excel 导入/导出**，销售支持 **CSV 流式**导出
- **Playwright** 仅截取 `.receipt` 元素 ➜ PNG ➜ **ZPL** 打印（Windows 使用 pywin32）
- **79 mm** 小票（画布 **624px**）
- `main.py` 提供 **pywebview** 桌面壳

## ▶️ 运行

```bash
python -m venv venv
venv\Scripts\activate  # macOS/Linux: source venv/bin/activate
pip install -r requirements.txt
python -m playwright install chromium
python app.py     # 或 python main.py
```

**端口**：默认随机；通过 `TREASUREPOS_PORT`/`PORT` 指定。  
**健康检查**：`/healthz` 返回 `ok`。

## 🛠 打包（onedir，带图标）

```powershell
pyinstaller --noconfirm --clean --onedir --name TreasurePOS --icon icon.ico main.py ^
  --add-data "templates;templates" ^
  --add-data "static;static" ^
  --hidden-import "playwright.sync_api" ^
  --hidden-import "win32timezone"
```

> **Playwright 浏览器**：首次打印可能自动下载 **Chromium**（需联网）。也可在打包前执行：  
> `python -m playwright install chromium`。  
> 进阶：设置 `PLAYWRIGHT_BROWSERS_PATH=0` 将浏览器装进项目目录，便于随包分发。

## ⚙️ 配置

- `TREASUREPOS_DATA_DIR` — 自定义数据目录
- `TREASUREPOS_PORT`/`PORT` — 监听端口
- 打印机名在 `app.py > print_receipt()` 中修改：
  ```python
  printer_name = "ZDesigner ZD230-203dpi ZPL"
  ```

## 📦 导入导出

- 导入：`POST /import/items`（Excel 表头需为 `barcode, name, price, wholesale_price, qty, category, size, [status], [image]`）  
- 导出：`GET /export/items`、`GET /export/sales?...&fmt=xlsx|csv`（CSV 为流式）

## 🔎 常用接口

见上文英文表格（路径一致）。

## 🎨 自定义小票

在 `templates/receipt.html` 调整：Logo 间距、列对齐、底部留白等；`.totals` 独立容器避免覆盖。

## 🧰 排错

Playwright 未安装 / 打印机未找到 / 端口冲突 / 图片路径不安全 / EXE 资源缺失 —— 见英文部分对应解决方案。

---

# 🇰🇷 한국어

## ✨ 특징

- **로컬 우선**: `templates/`, `static/` 구조
- **영구 데이터 디렉터리**: 첫 실행 시 기존 DB·이미지 자동 마이그레이션
- **정수 금액 컬럼**(`*_int`)으로 계산
- **서버 측 검색/페이지네이션**, TOP10
- **Excel 가져오기/내보내기**, 판매 **CSV 스트리밍**
- **Playwright**가 `.receipt` 요소만 캡처 ➜ PNG ➜ **ZPL** 인쇄(Windows pywin32)
- **79 mm** 용지(캔버스 **624px**)
- `main.py` 로 **pywebview** 데스크톱 창 제공

## ▶️ 실행

```bash
python -m venv venv
venv\Scripts\activate   # macOS/Linux: source venv/bin/activate
pip install -r requirements.txt
python -m playwright install chromium
python app.py           # 또는 python main.py
```

**포트**: 기본은 자동 선택; `TREASUREPOS_PORT`/`PORT` 로 지정.  
**상태 확인**: `/healthz` → `ok`.

## 🛠 빌드 (onedir, 아이콘 포함)

```powershell
pyinstaller --noconfirm --clean --onedir --name TreasurePOS --icon icon.ico main.py ^
  --add-data "templates;templates" ^
  --add-data "static;static" ^
  --hidden-import "playwright.sync_api" ^
  --hidden-import "win32timezone"
```

> **Playwright 브라우저**: 첫 인쇄 시 **Chromium**이 자동 다운로드될 수 있습니다(인터넷 필요).  
> 사전 설치하려면 `python -m playwright install chromium` 실행.  
> 고급: `PLAYWRIGHT_BROWSERS_PATH=0` 설정 후 설치하면 프로젝트 폴더에 브라우저가 위치합니다.

## ⚙️ 설정

- `TREASUREPOS_DATA_DIR` — 데이터 경로
- `TREASUREPOS_PORT`/`PORT` — 포트
- 프린터 이름: `app.py > print_receipt()`에서 변경
  ```python
  printer_name = "ZDesigner ZD230-203dpi ZPL"
  ```

## 📦 가져오기/내보내기

- 가져오기: `POST /import/items` (엑셀 헤더 필수: `barcode, name, price, wholesale_price, qty, category, size, [status], [image]`)  
- 내보내기: `GET /export/items`, `GET /export/sales?...&fmt=xlsx|csv`

## 🔎 주요 API

영문 표와 동일.

## 🎨 영수증 커스터마이즈

`templates/receipt.html` 에서 로고 간격/열 정렬/하단 여백 등을 CSS로 조정. `.totals` 분리로 콘텐츠 겹침 방지.

## 🧰 문제 해결

Playwright 설치/프린터 이름/포트 충돌/이미지 경로/EXE 리소스 이슈 등은 영문 절을 참고하세요.
