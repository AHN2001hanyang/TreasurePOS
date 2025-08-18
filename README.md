<<<<<<< HEAD
# TreasurePOS · Flask + SQLite POS (KR/ZH/EN)

> **Languages / 语言 / 언어** · Jump to: [English](#english) · [中文](#中文) · [한국어](#한국어)
=======
TreasurePOS (Flask + Desktop WebView)

KO/ZH/EN local-first POS for small shops. Scan barcodes, switch retail/wholesale price, checkout by cash/card, keep stock logs, view sales analytics (heatmap/aggregation), and print Zebra receipts (ZPL).

语言 | 언어 | Language
中文 • 한국어 • English
>>>>>>> 333e062b556166ffb20c9d7cd836b8f3bc617baa

目录 · Table of Contents · 목차

<<<<<<< HEAD
## English

### Overview
**TreasurePOS** is a local‑first, lightweight POS built with **Flask + SQLite**. It provides a multilingual UI (Korean / Chinese / English), barcode and manual input, stock management, sales records, Excel import/export, server‑side search & pagination, analytics (heatmap + time‑grouped stats), and **robust receipt printing** to Zebra printers via **ZPL**.  
All data lives in a **durable run directory**, so your database and images persist across app moves/updates.

**Printing reliability**
- Amounts are stored/aggregated as **integers** (`*_int` columns) to avoid floating rounding issues.
- Receipt rendering uses **Playwright element screenshot** to capture **only** the `.receipt` block, preventing overlaps or clipped output.
- ZPL is generated with **actual image width/height** and sent with `^PW` / `^LL` to minimize cut‑offs.

### Features
- Multilingual UI (KO/ZH/EN)
- Product CRUD (category / size / status / image)
- Sales, delete (with restock), refunds (auto restock), refund log
- Server‑side search & pagination
- Excel import/export (items, sales), CSV streaming for large exports
- Analytics: heatmap (weekday × hour) and sales stats (day/week/month/year)
- **Zebra ZPL** receipt printing with exact width/height
- Durable data directory (Windows/macOS/Linux), one‑file migration on first run

### Project Structure (key files)
```
app.py                 # Flask server, APIs, printing logic
templates/
  index.html           # POS / checkout
  manage.html          # product management
  sales.html           # sales records
  stocklog.html        # stock logs
  settings.html        # settings
  receipt.html         # receipt template (printing-critical)
static/
  TREASURE.png         # example logo
```

### Durable Data Directory
Default locations:
- **Windows**: `%LOCALAPPDATA%\TreasurePOS`
- **macOS**: `~/Library/Application Support/TreasurePOS`
- **Linux**: `~/.local/share/treasurepos`

Override via env var:
```bash
TREASUREPOS_DATA_DIR=/absolute/path/to/data
```

It contains:
```
inventory.db
uploads/
images/
```

### Requirements
- Python **3.9+**
- Base packages:
  ```bash
  pip install flask flask-cors pandas pillow html2image
  ```
- **Printing (recommended):** Playwright
  ```bash
  pip install playwright
  playwright install chromium
  ```
- **Windows printing:** pywin32
  ```bash
  pip install pywin32
  ```
- **Build EXE (optional):** PyInstaller
  ```bash
  pip install pyinstaller
  ```

### Run
```bash
python app.py
```
Binds to `127.0.0.1` with an **auto port**. Use a fixed port:
```bash
TREASUREPOS_PORT=5000 python app.py
```
Open: `http://127.0.0.1:<port>/`

### Fastest **one-dir** EXE (with icon)
From project root:
```bash
pyinstaller --noconfirm --onedir --clean \
  --name TreasurePOS \
  --icon static/TREASURE.ico \
  --add-data "templates:templates" \
  --add-data "static:static" \
  app.py
```
> On Windows, use `;` instead of `:` in `--add-data`, and carets `^` for line breaks:
> ```bat
> pyinstaller --noconfirm --onedir --clean ^
>   --name TreasurePOS ^
>   --icon static/TREASURE.ico ^
>   --add-data "templates;templates" ^
>   --add-data "static;static" ^
>   app.py
> ```

### Excel Import / Export
- **Export items**: `GET /export/items` → `.xlsx`
- **Export sales**:  
  `GET /export/sales?start=YYYY-MM-DD&end=YYYY-MM-DD&pay_type=card|cash&fmt=xlsx|csv`
- **Import items** (header must match exactly):
  ```csv
  barcode, name, price, wholesale_price, qty, category, size, status, image
  ```
  - `image` must be a **relative path** under `images/` (e.g. `images/123.png`) and passes a whitelist regex.

### Printing: How It Works
- `GET /receipt/<sale_id>` renders `templates/receipt.html`.
- `POST /api/print_receipt/<sale_id>`:
  1. **Playwright** screenshots the `.receipt` element (79mm ≈ 624px width).
  2. Convert PNG → ZPL (`~DG...` + `^XG`).
  3. Send ZPL to Windows printer with **actual image size** (`^PW`/`^LL`).

**Change printer name** in `app.py`:
```python
printer_name = "ZDesigner ZD230-203dpi ZPL"
```

**Tune print darkness / threshold** (`image_to_zpl`):
```python
threshold = 200  # try 190~220
```

### Receipt Layout: Quick Tweaks
Open `templates/receipt.html` (CSS):
- Paper width: `--paper-w: 624px` (79mm @ 203dpi)
- Logo margin: `.logo-container{ margin:6px 0 30px; }`
- VAT (card only): `.vat-row`
- Total: `.footer` (single dashed top border to avoid repeated lines)
- Tail blank: `.tail-blank{ height:calc(2 * var(--cm)); }`

**Column alignment (preset):**
- **Col 1** (name): left + wrapping, with extra right padding to avoid crowding
- **Col 2 & 3** (qty & unit price): **centered horizontally & vertically**
- **Col 4** (subtotal): **right‑aligned**, vertically centered

### Security & Safety
- CORS restricted to `http://127.0.0.1:*` and `http://localhost:*`
- Images must be `images/<safe-name>.{jpg,png,webp}` and pass a regex whitelist
- SQLite with foreign keys enabled, PRAGMA tuned, indices added

### Troubleshooting
- **Repeated lines at bottom**: Ensure only `.footer` uses dashed top border; remove extra `<hr>` below tables.
- **Cut‑off prints**: We set `^PW`/`^LL` using actual image size; increase `+15` slack if needed.
- **Playwright missing**: Install `playwright` and run `playwright install chromium`.
- **win32print missing**: `pip install pywin32`, and verify the exact printer name.

### FAQ
**Do I need “Codex”?** No. Codex is unrelated to printing or downloads and is no longer required.  
**Change paper width?** Edit `--paper-w` and ensure the printer supports that width (79mm @203dpi ≈ 624px).

### License
MIT (or your preferred license).

=======
中文

한국어

English

中文
简介

TreasurePOS 是一个本地优先的收银系统：支持条码扫描/手动输入、零售价/批发价切换、现金/刷卡结算、库存出入库日志、销售统计（按日/周/月/年与小时×星期热力图），并可用 Zebra 条码/小票打印机打印收据（ZPL 模式）。

主要特性

多语言 UI：韩/中/英。

商品管理：条码、名称、价格（零售/批发，整数入库）、库存、分类、尺码、上下架、图片。

结算：购物车、现金/刷卡、退款、删除订单（自动回补库存并留痕）。

统计：订单聚合、热力图（星期×小时，支持指标切换：订单/金额/件数）。

导入导出：Excel（商品、销售）。

打印：Playwright 渲染 → PNG → ZPL → win32print RAW 发送到 Zebra。

数据可迁移：初次运行自动把旧目录 static/images、根目录 inventory.db 迁移到新的运行目录。

技术栈与目录

后端：Flask + SQLite（WAL）

前端：原生 HTML/CSS/JS + Bootstrap-like 样式

截图渲染：Playwright（Chromium，无头）

打印：Zebra（203dpi ZPL）

关键文件

app.py                 # Flask 应用（API/模板/打印）
templates/*.html       # 页面与小票模板（receipt.html）
static/*               # 静态资源
requirements.txt       # 依赖

运行数据目录（很重要）

程序把数据库与运行期图片存放在运行目录（RUN_DIR）：

Windows：%LOCALAPPDATA%\TreasurePOS

macOS：~/Library/Application Support/TreasurePOS

Linux：~/.local/share/treasurepos

可通过环境变量覆盖：TREASUREPOS_DATA_DIR=自定义路径

运行时，用 /static/images/ 路径访问 RUN_DIR/images（已做安全映射与校验）。

首次运行会自动把老位置的 inventory.db 与 static/images/* 迁移到 RUN_DIR。

环境要求

Windows 10/11（推荐，用于 ZPL 打印）

Python 3.9+

打印机：Zebra（ZPL 驱动；示例中用 ZDesigner ZD230-203dpi ZPL）

Node 无需手动安装（Playwright 会自带 Chromium）

安装与运行（开发）
# 1) 创建并激活虚拟环境（可选）
python -m venv venv
venv\Scripts\activate

# 2) 安装 Python 依赖
pip install -r requirements.txt

# 3) 安装 Playwright 及浏览器内核（用于截图渲染收据）
pip install playwright
playwright install chromium

# 4) 运行
python app.py
# 控制台显示端口（默认自动分配或环境变量 TREASUREPOS_PORT），浏览器打开 http://127.0.0.1:<port>

常见使用流程

商品管理：在“商品管理”页面添加/导入 Excel。

Excel 表头必须是：barcode,name,price,wholesale_price,qty,category,size[,status,image]

价格使用整数（单位：韩元/元等），系统将同步写入 *_int 字段。

结算：主页添加到购物车 → 选择价格类型（零售/批发）→ 选现金/刷卡 → 结算。

刷卡会计算并显示 VAT 10%。（仅显示，不修改总额逻辑）

现金会显示 “VAT not included” 提示。

退款/删除订单：在“销售记录”勾选 → 退款/删除。系统自动回补库存并记录到 stock_log/refund_log。

统计：在“销售记录”或“设置”中查看折线/柱状聚合与热力图，并可按支付方式过滤。

打印与 Playwright

路由 /api/print_receipt/<sale_id>：

Playwright 打开 /receipt/<sale_id>?for_print=1，只截取 .receipt 元素；

生成 PNG → 转 ZPL（image_to_zpl）；

计算并注入 ^PW（宽度）和 ^LL（长度），RAW 发送到 Zebra。

关键参数在 app.py：

# Playwright 元素截图宽度：79mm 纸约 624 px（203dpi）
render_receipt_png(url, out_path, width_px=624)

# 黑白阈值：数值越小越黑（更浓重），一般 190~220 可微调
threshold = 200

# ZPL 纸宽/长度按实际图片注入，末尾加 15 dots 余量：
^PW{img_w}
^LL{img_h + 15}


打印机选择在 app.py 里：

printer_name = "ZDesigner ZD230-203dpi ZPL"

打包为 EXE（onedir，启动更快）

在项目根目录执行（包含图标，并收集模板/静态资源）：

pyinstaller main.py ^
  --name TreasurePOS ^
  --icon icon.ico ^
  --noconsole ^
  --onedir ^
  --add-data "templates;templates" ^
  --add-data "static;static" ^
  --hidden-import "playwright.sync_api"


提示

--onedir 启动更快，适合你当前需求；

首次运行后会在运行目录生成数据库和图片目录；

若使用到 Pillow/zlib 等，PyInstaller 会自动打包。

收据与样式微调（最常用）

在 templates/receipt.html 中修改 CSS（已内置这些选择器）：

1）增大“不含增值税”字体

.vat-notice { font-size: 1.2em; font-weight: 700; }


2）Logo 上下留白更多

.logo-container { margin: 6px 0 30px; } /* 下方 30px，可改 36/48 */


3）顶部/尾部空白（裁切安全区）

.top-blank { height: 100px; }         /* 顶部空白，高度可改 */
.tail-blank { height: calc(2 * var(--cm)); }  /* 尾部固定 2cm，可改 1.5/2.5 */


4）表格列对齐与间距

/* 第一列（商品名）右侧留白，第二列（数量）左侧留白，避免太挤 */
td.name-cell{ padding-right:12px; }
tbody td:nth-child(2){ padding-left:12px; }

/* 第 2、3 列完全居中；第 4 列向右对齐且上下居中 */
thead th:nth-child(2), thead th:nth-child(3),
tbody td:nth-child(2), tbody td:nth-child(3){
  text-align:center!important; vertical-align:middle!important;
}
thead th:nth-child(4), tbody td:nth-child(4){
  text-align:right!important; vertical-align:middle!important;
}

/* 多行内容顶对齐，防止“覆盖/重叠”错觉 */
th, td { vertical-align: top; }

/* 如果看到“连续三条横线”，通常是：表格最后一行下边框 + <hr> + .footer 的虚线叠加
   任选其一去掉即可 —— 例如去掉最后一行的底边线： */
tbody tr:last-child td { border-bottom: 0; }


5）打印偏黑/偏淡的微调

# app.py → image_to_zpl()
threshold = 200  # 变黑：降到 190；变淡：升到 210~220


6）纸宽校准

79mm 纸在 203dpi 下 ≈ 631 dots，本项目用 624 px 基本居中；若左右切边，可微调：

render_receipt_png(url, out_path, width_px=624)  # 试 616/632

常见问题（FAQ）

VS Code 提示 “无法解析导入 playwright.sync_api (Pylance)”
这是类型检查告警，不影响运行。安装依赖即可：
pip install playwright；然后：playwright install chromium。
若仍提示，可在 VS Code 选择正确的 Python 解释器或忽略该告警。

GitHub Desktop 弹窗 “Newer commits on remote… Fetch”
说明远端比你本地新。点击 Fetch 拉取，再执行 Push origin。

打印有多余横线
参见上文“表格列对齐与间距”中的 tbody tr:last-child td { border-bottom: 0; } 或移除多余 <hr>。

收据被截/留白不足
调整 .tail-blank 高度（单位 cm→px 已用变量转换）；或放大 ^LL 余量（img_h + 15 → +30）。

变更条码后历史记录不同步
代码已在事务里同步 sale_items/stock_log 的条码；若旧数据缺失会自动回退并兼容。

한국어
소개

TreasurePOS는 로컬 우선(Local-first) 구조의 경량 POS입니다. 바코드 스캔/직접 입력, 소매/도매가 전환, 현금/카드 결제, 재고 입출고 로그, 판매 통계(일/주/월/연, 요일×시간 히트맵), Zebra 프린터(ZPL) 영수증 출력 기능을 제공합니다.

주요 기능

다국어 UI: 한국어/중국어/영어

상품 관리: 바코드·이름·가격(소매/도매, 정수 저장)·재고·분류·사이즈·상태·이미지

결제: 장바구니, 현금/카드, 환불, 주문 삭제(재고 자동 복구/로그 남김)

통계: 집계 그래프 및 히트맵(지표: 주문/매출/판매수량)

엑셀 Import/Export

출력: Playwright로 .receipt 요소만 캡처 → PNG → ZPL → win32print RAW 전송

실행 데이터 경로

Windows: %LOCALAPPDATA%\TreasurePOS

macOS: ~/Library/Application Support/TreasurePOS

Linux: ~/.local/share/treasurepos

환경 변수로 변경 가능: TREASUREPOS_DATA_DIR

최초 실행 시 기존 inventory.db 및 static/images/* 를 자동 이관합니다.

요구 사항

Windows 10/11 권장(프린터)

Python 3.9+

Zebra ZPL 드라이버 (예: ZDesigner ZD230-203dpi ZPL)

설치 & 실행(개발)
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
pip install playwright
playwright install chromium
python app.py

사용 흐름

상품 관리에서 추가/엑셀 Import (헤더: barcode,name,price,wholesale_price,qty,category,size[,status,image])

결제: 장바구니 → 가격 타입(소매/도매) → 현금/카드 선택 → 결제

카드: VAT 10% 표시(계산만 표시, 내부 총액 로직은 정수 저장)

현금: “VAT not included” 안내

환불/삭제: “판매 기록”에서 선택 → 환불/삭제 (재고 복구 및 로그 기록)

통계: 집계/히트맵, 결제수단 필터 지원

출력(Playwright & ZPL)

/api/print_receipt/<sale_id>: Playwright로 /receipt/<sale_id>?for_print=1 열고 .receipt 만 캡처 → PNG → ZPL 변환 → ^PW/^LL 주입 → RAW 인쇄

주요 파라미터 (app.py)

render_receipt_png(..., width_px=624)  # 79mm 용지 약 624 px
threshold = 200  # 190~220 사이 미세 조정
# ^PW{img_w}, ^LL{img_h + 15}
printer_name = "ZDesigner ZD230-203dpi ZPL"

EXE 빌드(onedir, 빠름)
pyinstaller main.py ^
  --name TreasurePOS ^
  --icon icon.ico ^
  --noconsole ^
  --onedir ^
  --add-data "templates;templates" ^
  --add-data "static;static" ^
  --hidden-import "playwright.sync_api"

영수증/스타일 미세 조정

1) “VAT 별도” 글자 확대

.vat-notice { font-size: 1.2em; font-weight: 700; }


2) 로고 하단 여백

.logo-container { margin: 6px 0 30px; }


3) 상단/하단 여백(재단 안전영역)

.top-blank { height: 100px; }
.tail-blank { height: calc(2 * var(--cm)); }


4) 표 정렬/간격

td.name-cell{ padding-right:12px; }
tbody td:nth-child(2){ padding-left:12px; }

thead th:nth-child(2), thead th:nth-child(3),
tbody td:nth-child(2), tbody td:nth-child(3){
  text-align:center!important; vertical-align:middle!important;
}
thead th:nth-child(4), tbody td:nth-child(4){
  text-align:right!important; vertical-align:middle!important;
}

th, td { vertical-align: top; }
tbody tr:last-child td { border-bottom: 0; } /* 중복 라인 방지 */


5) 인쇄 진하게/연하게

threshold = 200  # 진하게: 190, 연하게: 210~220


6) 용지 폭 보정

render_receipt_png(..., width_px=624)  # 좌우 컷팅 시 616/632 등으로 조정

자주 묻는 질문

Pylance가 playwright.sync_api 임포트 불가 경고 → pip install playwright 와 playwright install chromium 후에도 뜨면 무시 가능(형상 검사 경고) 혹은 인터프리터 선택 확인.

GitHub Desktop “Newer commits on remote… Fetch” → 원격이 최신. Fetch 후 Push.

하단에 선이 여러 개 겹침 → 마지막 행 border-bottom 또는 <hr>/.footer 의 라인이 중복. tbody tr:last-child td { border-bottom: 0; } 로 해결.

English
Overview

TreasurePOS is a local-first POS for small shops: barcode scan/typing, retail/wholesale price switch, cash/card checkout, stock logs, sales analytics (heatmap & aggregates), and Zebra receipt printing (ZPL).

Features

Multi-language UI: KO/ZH/EN

Products: barcode, name, prices (retail/wholesale, stored as integers), qty, category, size, status, image

Checkout: cart, cash/card, refund, delete (auto restock + logs)

Analytics: daily/weekly/monthly/yearly plus weekday×hour heatmap

Excel import/export

Printing: Playwright → PNG → ZPL → win32print RAW to Zebra

Runtime data directory

Windows: %LOCALAPPDATA%\TreasurePOS

macOS: ~/Library/Application Support/TreasurePOS

Linux: ~/.local/share/treasurepos

Override with TREASUREPOS_DATA_DIR.

On first run, legacy inventory.db and static/images/* are migrated automatically.

Requirements

Windows 10/11 (recommended for ZPL)

Python 3.9+

Zebra printer with ZPL driver (e.g., ZDesigner ZD230-203dpi ZPL)

Install & Run (dev)
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
pip install playwright
playwright install chromium
python app.py

Printing pipeline

/api/print_receipt/<sale_id> opens /receipt/<sale_id>?for_print=1 with Playwright, screenshots the .receipt element, converts PNG to ZPL, injects ^PW/^LL, then sends RAW to the Zebra driver.
>>>>>>> 333e062b556166ffb20c9d7cd836b8f3bc617baa

Key parameters in app.py:

<<<<<<< HEAD
## 中文

### 简介
**TreasurePOS** 是一个 **本地优先** 的轻量级收银系统（Flask + SQLite）。支持中/韩/英三语界面、条码与手动输入、库存管理、销售记录、Excel 导入导出、服务端搜索与分页、统计与热力图，以及 **Zebra ZPL** 小票打印。数据保存在 **持久化目录** 中，更新或移动程序也不会丢失。

**打印更可靠**
- 金额统一使用 **整数**（`*_int` 列）存储与汇总，避免浮点取整误差。
- 使用 **Playwright** 对 `.receipt` 元素进行截图，只截内容区域，避免覆盖或裁切。
- 发送 ZPL 时用 **实际图片宽高** 写入 `^PW`/`^LL`，尽量避免被切边。

### 功能
- 多语言（中/韩/英）
- 商品增删改查（分类/尺码/状态/图片）
- 销售、删除（回补库存）、退款（自动回补）、退款日志
- 服务端搜索与分页
- Excel 导入/导出（商品、销售），大数据量 CSV 流式导出
- 统计：按日/周/月/年；热力图：星期 × 小时
- **Zebra ZPL** 小票打印（精确宽高）
- 跨平台持久化目录，首次运行可自动迁移旧数据

### 目录结构（关键文件）
```
app.py                 # Flask 后端与打印逻辑
templates/
  index.html           # 收银台
  manage.html          # 商品管理
  sales.html           # 销售记录
  stocklog.html        # 出入库记录
  settings.html        # 设置
  receipt.html         # 小票模板（打印关键）
static/
  TREASURE.png         # 示例 LOGO
```

### 持久化目录
默认路径：
- **Windows**：`%LOCALAPPDATA%\TreasurePOS`
- **macOS**：`~/Library/Application Support/TreasurePOS`
- **Linux**：`~/.local/share/treasurepos`

可用环境变量覆盖：
```bash
TREASUREPOS_DATA_DIR=/绝对/路径
```

目录包含：
```
inventory.db
uploads/
images/
```

### 环境依赖
- Python **3.9+**
- 基础依赖：
  ```bash
  pip install flask flask-cors pandas pillow html2image
  ```
- **打印推荐**：Playwright
  ```bash
  pip install playwright
  playwright install chromium
  ```
- **Windows 打印**：pywin32
  ```bash
  pip install pywin32
  ```
- **打包 EXE（可选）**：PyInstaller
  ```bash
  pip install pyinstaller
  ```

### 启动
```bash
python app.py
```
默认绑定 `127.0.0.1` 并自动分配端口。固定端口：
```bash
TREASUREPOS_PORT=5000 python app.py
```
浏览器打开：`http://127.0.0.1:<port>/`

### 最快 **onedir** 打包（含图标）
项目根目录执行：
```bash
pyinstaller --noconfirm --onedir --clean ^
  --name TreasurePOS ^
  --icon static/TREASURE.ico ^
  --add-data "templates;templates" ^
  --add-data "static;static" ^
  app.py
```
> macOS/Linux 把 `^` 换成 `\`，并将 `--add-data` 写成 `src:dest`。

### Excel 导入 / 导出
- **导出商品**：`GET /export/items` → `.xlsx`
- **导出销售**：  
  `GET /export/sales?start=YYYY-MM-DD&end=YYYY-MM-DD&pay_type=card|cash&fmt=xlsx|csv`
- **导入商品**（表头必须完全一致）：
  ```csv
  barcode, name, price, wholesale_price, qty, category, size, status, image
  ```
  - `image` 必须是 `images/` 下的 **相对路径**（如 `images/123.png`），会做白名单校验。

### 打印说明
- `GET /receipt/<sale_id>` 渲染小票页面 `receipt.html`。
- `POST /api/print_receipt/<sale_id>`：
  1. 使用 **Playwright** 截取 `.receipt` 元素（79mm ≈ 624px 宽）。  
  2. 将 PNG 转为 ZPL（`~DG...` + `^XG`）。  
  3. 以 **实际图片尺寸** 设置 `^PW`/`^LL` 并发送到 Windows 打印机。

**修改打印机名称**（`app.py`）：
```python
printer_name = "ZDesigner ZD230-203dpi ZPL"
```

**黑白阈值微调**（`image_to_zpl`）：
```python
threshold = 200  # 推荐 190~220 之间试调
```

### 小票排版微调
编辑 `templates/receipt.html`（CSS）：
- 纸宽：`--paper-w: 624px`（79mm @ 203dpi）
- Logo 间距：`.logo-container{ margin:6px 0 30px; }`
- VAT（刷卡显示）：`.vat-row`
- 合计：`.footer`（仅此处使用虚线边框，避免“重复三条线”）
- 尾部空白：`.tail-blank{ height:calc(2 * var(--cm)); }`

**列对齐（已设置）**：
- **第 1 列**（商品名）：左对齐，可换行，并与第 2 列留出空隙；
- **第 2、3 列**（数量、单价）：**上下左右均居中**；
- **第 4 列**（小计）：**右对齐**，上下居中。

### 安全与稳定
- CORS 仅允许本机端口
- 图片路径必须位于 `images/` 且通过正则白名单
- SQLite 开启外键、PRAGMA 优化、关键索引齐全

### 故障排查
- **底部出现 3 条线**：通常是 `<hr>` 叠加。模板仅在 `.footer` 上有一条虚线分隔。  
- **打印被裁切**：`^PW`/`^LL` 用实际图片尺寸；可把余量 `+15` 适当增大。  
- **Playwright 缺失**：安装 `playwright` 并执行 `playwright install chromium`。  
- **win32print 缺失**：`pip install pywin32`，并核对打印机名。

### FAQ
**需要 Codex 吗？** 不需要，Codex 与下载/打印无关，已不再使用。  
**如何改纸宽？** 修改 CSS 变量 `--paper-w`，并确保打印机支持该宽度（79mm @203dpi ≈ 624px）。

### 许可证
MIT（或自选许可证）。


---

## 한국어

### 소개
**TreasurePOS**는 **Flask + SQLite** 기반의 로컬 우선 경량 POS입니다. 한/중/영 UI, 바코드/수동 입력, 재고 관리, 판매 기록, Excel 가져오기/내보내기, 서버측 검색/페이지네이션, 통계/히트맵, **Zebra ZPL** 영수증 인쇄를 제공합니다. 모든 데이터는 **지속 디렉터리**에 저장됩니다.

**인쇄 신뢰성**
- 금액을 **정수형**(`*_int`)으로 저장/집계하여 반올림 문제 방지
- **Playwright**로 `.receipt` 요소만 스크린샷 → 겹침/절단 최소화
- 실제 이미지 크기로 `^PW`/`^LL` 설정하여 컷오프 방지

### 기능
- 다국어 UI(한/중/영)
- 상품 CRUD(카테고리/사이즈/상태/이미지)
- 판매/삭제(재고 복구), 환불(자동 복구), 환불 로그
- 서버측 검색 & 페이지네이션
- Excel 가져오기/내보내기, 대량 CSV 스트리밍
- 통계(일/주/월/년), 요일×시간 히트맵
- **Zebra ZPL** 인쇄(정확한 크기)
- OS별 지속 디렉터리, 최초 실행 시 구데이터 마이그레이션

### 프로젝트 구조
```
app.py                 # Flask 서버/인쇄 로직
templates/
  index.html           # POS/결제
  manage.html          # 상품 관리
  sales.html           # 판매 기록
  stocklog.html        # 입출고 기록
  settings.html        # 설정
  receipt.html         # 영수증 템플릿(핵심)
static/
  TREASURE.png         # 예시 로고
```

### 지속 디렉터리
기본 경로:
- **Windows**: `%LOCALAPPDATA%\TreasurePOS`
- **macOS**: `~/Library/Application Support/TreasurePOS`
- **Linux**: `~/.local/share/treasurepos`

환경변수로 변경:
```bash
TREASUREPOS_DATA_DIR=/절대/경로
```

### 요구 사항
- Python **3.9+**
- 기본 패키지:
  ```bash
  pip install flask flask-cors pandas pillow html2image
  ```
- **인쇄(권장)**: Playwright
  ```bash
  pip install playwright
  playwright install chromium
  ```
- **Windows 인쇄**: pywin32
  ```bash
  pip install pywin32
  ```
- **EXE 빌드(선택)**: PyInstaller
  ```bash
  pip install pyinstaller
  ```

### 실행
```bash
python app.py
```
기본은 `127.0.0.1`, 자동 포트. 고정 포트:
```bash
TREASUREPOS_PORT=5000 python app.py
```
브라우저: `http://127.0.0.1:<port>/`

### 가장 빠른 **one‑dir** 빌드(아이콘 포함)
프로젝트 루트에서:
```bash
pyinstaller --noconfirm --onedir --clean \
  --name TreasurePOS \
  --icon static/TREASURE.ico \
  --add-data "templates:templates" \
  --add-data "static:static" \
  app.py
```
> Windows에선 `:` 대신 `;`, 줄바꿈은 `^` 사용.

### Excel
- **상품 내보내기**: `GET /export/items`  
- **판매 내보내기**:  
  `GET /export/sales?start=YYYY-MM-DD&end=YYYY-MM-DD&pay_type=card|cash&fmt=xlsx|csv`
- **가져오기 헤더**(완전 동일해야 함):
  ```csv
  barcode, name, price, wholesale_price, qty, category, size, status, image
  ```
  - `image`는 `images/xxx.png`와 같은 **상대 경로**여야 하며 화이트리스트 검증을 통과합니다.

### 인쇄 동작
- `GET /receipt/<sale_id>` → `receipt.html` 렌더
- `POST /api/print_receipt/<sale_id>`:
  1. **Playwright**로 `.receipt` 요소 스크린샷(79mm ≈ 624px)  
  2. PNG → ZPL 변환  
  3. 실제 이미지 크기로 `^PW`/`^LL` 설정 후 Windows 프린터로 전송

**프린터 이름 변경**(`app.py`):
```python
printer_name = "ZDesigner ZD230-203dpi ZPL"
```

**흑백 임계값 조정**(`image_to_zpl`):
```python
threshold = 200  # 190~220 권장
```

### 영수증 레이아웃 미세 조정
`templates/receipt.html`의 CSS:
- 용지 폭: `--paper-w: 624px` (79mm @ 203dpi)
- 로고 여백: `.logo-container{ margin:6px 0 30px; }`
- VAT(카드): `.vat-row`
- 합계: `.footer` (점선 상단만 사용 → 중복 라인 방지)
- 꼬리 여백: `.tail-blank{ height:calc(2 * var(--cm)); }`

**정렬 규칙(적용됨)**:
- **1열**(상품명): 좌측 정렬, 줄바꿈 허용
- **2·3열**(수량·단가): **상하좌우 중앙**
- **4열**(소계): **우측 정렬**, 수직 중앙

### 보안 & 안정성
- CORS: 로컬 호스트만 허용
- 이미지 경로: `images/` 하위 + 정규식 화이트리스트
- SQLite 외래키/PRAGMA 최적화/필수 인덱스 적용

### 문제 해결
- **아래 3줄 반복**: `<hr>` 중복/경계선 중첩. 현재 템플릿은 `.footer`에만 점선을 사용.  
- **절단**: 실제 이미지 크기로 `^PW`/`^LL` 설정. 필요시 `+15` 여유 늘리기.  
- **Playwright 미설치**: `pip install playwright && playwright install chromium`.  
- **win32print 없음**: `pip install pywin32` 후 프린터명 확인.

### 자주 묻는 질문
**Codex 필요?** 아닙니다. 인쇄/다운로드와 무관합니다.  
**용지 폭 변경?** CSS 변수 `--paper-w` 수정 후, 프린터 최대 폭과 일치시켜 주세요.

### 라이선스
MIT (또는 원하는 라이선스).
=======
render_receipt_png(..., width_px=624)  # 79mm ≈ 624 px @203dpi
threshold = 200                        # 190=blacker, 210~220=lighter
# ZPL sizing:
^PW{img_w}
^LL{img_h + 15}
printer_name = "ZDesigner ZD230-203dpi ZPL"

Build EXE (onedir, fast startup)
pyinstaller main.py ^
  --name TreasurePOS ^
  --icon icon.ico ^
  --noconsole ^
  --onedir ^
  --add-data "templates;templates" ^
  --add-data "static;static" ^
  --hidden-import "playwright.sync_api"

Receipt/UI micro-tuning

1) Larger “VAT not included”

.vat-notice { font-size: 1.2em; font-weight: 700; }


2) More space under logo

.logo-container { margin: 6px 0 30px; }


3) Top & tail blank (safe trim area)

.top-blank { height: 100px; }
.tail-blank { height: calc(2 * var(--cm)); }  /* 2cm; adjust as needed */


4) Column alignment & spacing

td.name-cell{ padding-right:12px; }
tbody td:nth-child(2){ padding-left:12px; }

thead th:nth-child(2), thead th:nth-child(3),
tbody td:nth-child(2), tbody td:nth-child(3){
  text-align:center!important; vertical-align:middle!important;
}
thead th:nth-child(4), tbody td:nth-child(4){
  text-align:right!important; vertical-align:middle!important;
}

th, td { vertical-align: top; }
tbody tr:last-child td { border-bottom: 0; } /* prevent triple lines */


5) Print darker/lighter

threshold = 200  # lower => darker, higher => lighter


6) Paper width fine-tune

render_receipt_png(..., width_px=624)  # try 616/632 if left/right is cut

FAQ

Pylance “cannot import playwright.sync_api”: install playwright and run playwright install chromium. The warning is from the type checker; runtime is fine once installed.

GitHub Desktop “Newer commits on remote… Fetch”: click Fetch to pull, then Push origin.

Extra horizontal lines: last row bottom border + <hr> + .footer border may stack. Remove one (e.g., tbody tr:last-child td { border-bottom: 0; }).

License

Apache-2.0
>>>>>>> 333e062b556166ffb20c9d7cd836b8f3bc617baa
