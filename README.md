<div align="center">
  
<img src="static/TREASURE.png" alt="TreasurePOS" width="260"/>

# **TreasurePOS**
_A fast, local‑first POS with rock‑solid printing_

[![Python](https://img.shields.io/badge/Python-3.9%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-2.x-000?logo=flask)](https://flask.palletsprojects.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

**Languages / 语言 / 언어** ·
[English](#english) · [中文](#中文) · [한국어](#한국어)

</div>

---

## English

> **Highlights**
> - **Stable receipts**: integer money columns, element-screenshot + exact ZPL width/length
> - **Local-first & portable**: persistent data dir on Win/macOS/Linux
> - **Productive**: barcode/manual input, stock, sales/refunds, analytics, Excel I/O

### 1) Overview
**TreasurePOS** is a lightweight POS built with **Flask + SQLite**. It supports a multilingual UI (KO/ZH/EN), server-side search & pagination, Excel import/export, sales analytics (by day/week/month/year + heatmap), and **reliable Zebra ZPL printing** using Playwright element screenshots.

### 2) Features
- 🌐 Multi-language UI (Korean / Chinese / English)  
- 🧾 Product CRUD: category, size, status (normal/sold out/discontinued), image  
- 🛒 Checkout & refund (with auto stock revert)  
- 🔎 Fast server-side search & pagination  
- 📊 Sales stats + weekday×hour heatmap  
- 📥/📤 Excel import/export (items & sales)  
- 🖨️ ZPL receipts with **exact** page width & length  
- 💾 Durable run directory (outside app folder)

### 3) Project Structure
```
app.py                 # Flask server / DB / printing
templates/
  index.html           # POS checkout
  manage.html          # Product management
  sales.html           # Sales records
  stocklog.html        # Stock I/O
  settings.html        # Settings
  receipt.html         # Receipt (printing-critical)
static/
  TREASURE.png         # Logo example (used in README header)
```

### 4) Persistent Data Directory
Default paths:
- **Windows**: `%LOCALAPPDATA%\TreasurePOS`
- **macOS**: `~/Library/Application Support/TreasurePOS`
- **Linux**: `~/.local/share/treasurepos`

Override with environment variable:
```bash
# e.g.
export TREASUREPOS_DATA_DIR="/your/path"
```
Contents:
```
inventory.db
uploads/
images/
```

### 5) Requirements
```bash
# Core
pip install flask flask-cors pandas pillow html2image

# Printing (recommended)
pip install playwright
playwright install chromium

# Windows printing
pip install pywin32

# Build EXE (optional)
pip install pyinstaller
```

### 6) Run
```bash
python app.py
# Default: host=127.0.0.1, port auto
# Fixed port:
# TREASUREPOS_PORT=5000 python app.py
```
Open: `http://127.0.0.1:<port>/`

### 7) Fastest EXE (one-dir) with icon
**Windows (PowerShell/CMD):**
```bat
pyinstaller --noconfirm --onedir --clean ^
  --name TreasurePOS ^
  --icon static/TREASURE.ico ^
  --add-data "templates;templates" ^
  --add-data "static;static" ^
  app.py
```
**macOS/Linux (bash):**
```bash
pyinstaller --noconfirm --onedir --clean \
  --name TreasurePOS \
  --icon static/TREASURE.ico \
  --add-data "templates:templates" \
  --add-data "static:static" \
  app.py
```
Result: `dist/TreasurePOS/` (fast startup one-dir bundle).

### 8) Excel Import / Export
- **Export items:** `GET /export/items` → `.xlsx`  
- **Export sales:** `GET /export/sales?start=YYYY-MM-DD&end=YYYY-MM-DD&pay_type=card|cash&fmt=xlsx|csv`  
- **Import items** (header must exactly match):
  ```csv
  barcode,name,price,wholesale_price,qty,category,size,status,image
  ```
  `image` must be a **relative path** under `images/` (validated).

### 9) Printing (How it works)
1. `GET /receipt/<sale_id>` renders `templates/receipt.html`.  
2. `POST /api/print_receipt/<sale_id>`:
   - Uses **Playwright** to screenshot **only** the `.receipt` element (79 mm ≈ 624 px).  
   - Converts PNG → ZPL (`~DG…` + `^XG`).  
   - Sends ZPL with `^PW` (width) and `^LL` (length) set to the **actual image size**.

**Change printer name** (`app.py`):
```python
printer_name = "ZDesigner ZD230-203dpi ZPL"
```
**Tune B/W threshold** (`image_to_zpl`):
```python
threshold = 200  # try 190~220
```

### 10) Receipt Layout – Quick Tweaks (`templates/receipt.html`)
- Paper width: `--paper-w: 624px;` (79mm at 203 dpi)  
- Logo spacing: `.logo-container{ margin:6px 0 30px; }`  
- Only one dashed border on **.footer** to avoid repeated lines  
- Fixed 2 cm tail: `.tail-blank{ height:calc(2 * var(--cm)); }`  

**Column alignment (already applied):**
- **Col 1 (name):** left, wrapping enabled  
- **Col 2 (qty) & Col 3 (price):** centered **both** vertically & horizontally  
- **Col 4 (subtotal):** right-aligned, vertically centered  
- Extra spacing between name ↔ qty to avoid crowding

### 11) Security & Safety
- CORS: only `http://127.0.0.1:*` and `http://localhost:*`
- Safe image path whitelist: only `images/NAME.(jpg|jpeg|png|webp)`
- Parameterized SQL + indices + WAL mode

### 12) Troubleshooting
- **Three lines at the bottom:** usually multiple `<hr>` or border stacking. Only `.footer` has a dashed top border.  
- **Cut-off print:** we already use actual `^PW` and `^LL`. If needed, increase slack (e.g., `img_h + 15`) or the logo bottom margin.  
- **Playwright not installed:** install it and run `playwright install chromium`. Without Playwright, the endpoint returns a rendered notice (printing disabled).  
- **`win32print` missing:** `pip install pywin32` and verify the exact Windows printer name.

### 13) FAQ
- **Do I need Codex?** No—unrelated and deprecated.  
- **Change paper width?** Edit `--paper-w` (CSS) and ensure the printer supports it.

### 14) License
MIT (or your license).

---

## 中文

> **要点**
> - **稳定打印**：金额使用整数列；元素截图 + 精确 ZPL 宽/高  
> - **本地优先**：跨平台持久化数据目录  
> - **高效实用**：条码/手输、库存、销售/退款、统计、Excel 导入导出

### 1）简介
**TreasurePOS** 基于 **Flask + SQLite** 的轻量级收银系统，支持中/韩/英界面、服务端搜索分页、Excel 导入导出、销售统计（按日/周/月/年 + 热力图）、以及通过 Playwright 元素截图的 **Zebra ZPL 稳定打印**。

### 2）功能
- 多语言界面（中/韩/英）  
- 商品管理：分类、尺码、状态（正常/售罄/下架）、图片  
- 结算与退款（自动回补库存）  
- 服务端搜索与分页  
- 销售统计 & 星期×小时热力图  
- Excel 导入/导出（商品 & 销售）  
- **ZPL 小票打印**：按实际宽高设置 `^PW`/`^LL`  
- 持久化数据目录（不随程序移动而丢失）

### 3）目录结构
同英文。

### 4）持久化目录
默认：
- Windows：`%LOCALAPPDATA%\TreasurePOS`
- macOS：`~/Library/Application Support/TreasurePOS`
- Linux：`~/.local/share/treasurepos`

覆盖：
```bash
export TREASUREPOS_DATA_DIR="/your/path"
```

### 5）环境依赖
同英文（见上）。

### 6）启动
```bash
python app.py
# 固定端口：TREASUREPOS_PORT=5000 python app.py
```
打开：`http://127.0.0.1:<port>/`

### 7）最快 onedir 打包（含图标）
同英文命令。

### 8）Excel 导入/导出
- 导出商品：`GET /export/items`  
- 导出销售：`GET /export/sales?start=YYYY-MM-DD&end=YYYY-MM-DD&pay_type=card|cash&fmt=xlsx|csv`  
- 导入模板（表头必须完全一致）：
  ```csv
  barcode,name,price,wholesale_price,qty,category,size,status,image
  ```
  `image` 必须为 `images/` 下的 **相对路径**，通过白名单校验。

### 9）打印机制
与英文相同：先渲染 `receipt.html`，再用 **Playwright** 截 `.receipt`，PNG→ZPL，并按实际宽高写入 `^PW`/`^LL`。

**修改打印机名称**（`app.py`）：  
```python
printer_name = "ZDesigner ZD230-203dpi ZPL"
```
**黑白阈值**（`image_to_zpl`）：  
```python
threshold = 200  # 建议 190~220
```

### 10）小票排版微调（`templates/receipt.html`）
- 纸宽：`--paper-w: 624px;`（79mm，203dpi）  
- Logo 间距：`.logo-container{ margin:6px 0 30px; }`  
- 仅 `.footer` 顶部使用虚线分隔，避免重复线  
- 固定 2cm 尾部空白：`.tail-blank{ height:calc(2 * var(--cm)); }`  

**列对齐（已实现）：**  
- 第1列（名称）左对齐可换行；  
- 第2、3列（数量、单价）**上下左右居中**；  
- 第4列（小计）**右对齐**、上下居中；  
- 名称与数量之间加内边距，避免贴太近。

### 11）安全
同英文。

### 12）常见问题
同英文（底部多线、裁切、Playwright、win32print）。

### 13）FAQ
- **需要 Codex 吗？** 不需要，且与下载/打印无关。  
- **如何调整纸宽？** 改 CSS 变量 `--paper-w`，并确保打印机支持。

### 14）许可
MIT（或你的许可）。

---

## 한국어

> **요약**
> - **안정적 인쇄**: 정수 금액 컬럼, 요소 스크린샷 + 정확한 ZPL 가로/세로  
> - **로컬 우선**: OS별 지속 디렉터리  
> - **생산성**: 바코드/수동 입력, 재고, 판매/환불, 통계, Excel I/O

### 1) 소개
**TreasurePOS**는 **Flask + SQLite** 기반의 경량 POS입니다. 한/중/영 UI, 서버측 검색/페이지네이션, Excel 가져오기/내보내기, 일/주/월/년 통계(히트맵 포함), **Playwright 요소 스크린샷**을 이용한 안정적인 **Zebra ZPL 인쇄**를 제공합니다.

### 2) 기능
영문과 동일.

### 3) 구조
영문 참조.

### 4) 지속 디렉터리
기본 경로(영문 참조). 환경변수로 변경:
```bash
export TREASUREPOS_DATA_DIR="/your/path"
```

### 5) 요구 사항 / 6) 실행 / 7) onedir 빌드
영문과 동일.

### 8) Excel
영문과 동일.

### 9) 인쇄 방식
- `receipt.html` 렌더 → Playwright로 `.receipt` 요소만 스크린샷 → PNG→ZPL 변환 → `^PW`/`^LL`에 실제 크기 반영 후 전송.  

프린터 이름 수정(`app.py`):
```python
printer_name = "ZDesigner ZD230-203dpi ZPL"
```
흑백 임계값(`image_to_zpl`):
```python
threshold = 200  # 190~220 권장
```

### 10) 영수증 레이아웃 조정
- 용지 폭: `--paper-w: 624px;`  
- 로고 간격: `.logo-container{ margin:6px 0 30px; }`  
- 점선 분리선은 `.footer` 상단 한 곳만 사용  
- 2 cm 꼬리 여백: `.tail-blank{ height:calc(2 * var(--cm)); }`  

**정렬 규칙(적용됨):**  
- 1열(상품명) 좌측 정렬, 줄바꿈 허용  
- 2·3열(수량·단가) **수평/수직 중앙**  
- 4열(소계) **우측 정렬**, 수직 중앙  
- 상품명↔수량 간격 추가

### 11) 보안 / 12) 문제 해결 / 13) FAQ / 14) 라이선스
영문과 동일.
