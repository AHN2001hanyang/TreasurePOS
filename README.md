# 💎 TreasurePOS

<div align="center">

**Flask-based Local POS System with 79mm Receipt Printing & ZPL Support**

[![Python](https://img.shields.io/badge/Python-3.7+-blue.svg)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-2.0+-green.svg)](https://flask.palletsprojects.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey.svg)](https://github.com/yourusername/treasurepos)

**Languages · 语言 · 언어:**  
[🇺🇸 English](#english) · [🇨🇳 简体中文](#简体中文) · [🇰🇷 한국어](#한국어)

</div>

---

## 🚀 Overview

TreasurePOS is a **local-first** Point of Sale system built with Flask, designed for small to medium businesses. It provides comprehensive inventory management, checkout processing, refunds, stock tracking, and data export capabilities. The system generates professional receipts by capturing HTML elements with Playwright, converting them to ZPL format for Zebra-compatible thermal printers.

> 💡 **Quick Start**: Want the Windows executable immediately? Jump to [**Build → PyInstaller**](#-build--pyinstaller-onedir)

---

## ✨ Key Features

<table>
<tr>
<td width="50%">

### 🏠 **Local-First Architecture**
- No external database required
- Runs entirely on your machine
- Data stays under your control

### 💾 **Smart Data Management**
- Persistent user data directory
- Automatic legacy data migration
- Organized file structure

### 🔢 **Precision Arithmetic**
- Integer-safe pricing columns (`*_int`)
- Eliminates floating-point errors
- Financial accuracy guaranteed

</td>
<td width="50%">

### 🔍 **Performance Optimized**
- Fast search & pagination
- Server-side filtering
- Responsive user interface

### 📊 **Import/Export Capabilities**
- Excel (`.xlsx`) import/export
- CSV streaming for large datasets
- Comprehensive sales reports

### 🖨️ **Professional Printing**
- Playwright element screenshot → PNG → ZPL
- Optimized for 79mm thermal paper
- Zebra printer compatibility (Windows)

</td>
</tr>
</table>

### 🎯 **Additional Features**
- 🪟 Optional desktop window with `pywebview`
- 📱 Responsive web interface
- 🔒 Path safety for image handling
- 📈 Sales analytics and reporting
- 🏷️ Barcode-based inventory tracking

> ℹ️ **Note**: This repository contains Python sources and HTML templates. Product images are stored separately in the runtime data directory and served via `/static/images/<file>`.

---

## 📁 Project Structure

```
TreasurePOS/
├── 📄 app.py              # Main Flask application (APIs, DB, printing)
├── 🖥️  main.py             # PyWebView desktop launcher
├── 📂 templates/           # HTML templates
│   ├── index.html         # Main dashboard
│   ├── manage.html        # Inventory management
│   ├── sales.html         # Sales history
│   ├── settings.html      # Configuration
│   ├── stocklog.html      # Stock tracking
│   └── receipt.html       # Receipt template
├── 📖 README.md           # This file
└── 🎨 icon.ico            # Application icon (for packaging)
```

### 🗂️ Runtime Data Directories

TreasurePOS automatically creates a persistent data folder on first launch:

| Platform | Default Location |
|----------|------------------|
| 🪟 **Windows** | `%LOCALAPPDATA%\TreasurePOS` |
| 🍎 **macOS** | `~/Library/Application Support/TreasurePOS` |
| 🐧 **Linux** | `~/.local/share/treasurepos` |

**Data Directory Structure:**
```
TreasurePOS/
├── 🗄️ inventory.db        # SQLite database
├── 📁 uploads/            # Imported Excel files
└── 🖼️ images/             # Product images
```

> 🔄 **Auto-Migration**: Legacy `inventory.db` and `static/images/*` are automatically migrated to the new structure.

---

## 🛠️ Quick Start (Development)

### 1️⃣ **Environment Setup**
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate
```

### 2️⃣ **Install Dependencies**
```bash
pip install flask flask-cors pandas openpyxl pillow playwright pywin32 pywebview
```

### 3️⃣ **Setup Playwright**
```bash
python -m playwright install chromium
```

### 4️⃣ **Launch Application**
```bash
# Web interface only
python app.py

# Desktop window with PyWebView
python main.py
```

### 🌐 **Access Points**
- **Main Interface**: http://127.0.0.1:5000
- **Health Check**: `GET /healthz` → Returns `ok`

### ⚙️ **Environment Variables**
```bash
# Custom port (Windows CMD)
set TREASUREPOS_PORT=5000

# Custom port (PowerShell)
$env:TREASUREPOS_PORT=5000

# Custom port (macOS/Linux)
export TREASUREPOS_PORT=5000

# Custom data directory
set TREASUREPOS_DATA_DIR=D:\TreasurePOSdata  # Windows
export TREASUREPOS_DATA_DIR=/path/to/data    # Unix
```

---

## 📦 Build · PyInstaller (onedir)

### 🚀 **Recommended Windows Build (fast startup · no console)**
```powershell
pyinstaller --onedir --windowed --noconfirm --clean --name TreasurePOS --icon icon.ico ^
  --add-data "templates;templates" ^
  --add-data "static;static" ^
  --add-data "uploads;uploads" ^
  main.py
```
**Launch**: `dist\TreasurePOS\TreasurePOS.exe`

> ℹ️ On macOS/Linux, replace `;` with `:` inside `--add-data` (e.g., `--add-data "templates:templates"`).

### 🖨️ Playwright Runtime (for receipt screenshots)
- **Option A · Use system Microsoft Edge (recommended, smallest bundle)**  
  ```python
  browser = await p.chromium.launch(channel="msedge", headless=True)
  ```
- **Option B · Install Chromium on the target PC**  
  ```powershell
  python -m playwright install chromium
  ```
- **Option C · Bundle Chromium with the app**  
  ```powershell
  set PLAYWRIGHT_BROWSERS_PATH=playwright-browsers
  python -m playwright install chromium
  pyinstaller --onedir --windowed --noconfirm --clean --name TreasurePOS --icon icon.ico ^
    --add-data "templates;templates" ^
    --add-data "static;static" ^
    --add-data "uploads;uploads" ^
    --add-data "playwright-browsers;playwright/driver/package/.local-browsers" ^
    main.py
  ```

## ⚙️ Configuration

### 🌍 **Environment Variables**
| Variable | Description | Default |
|----------|-------------|---------|
| `TREASUREPOS_DATA_DIR` | Persistent data folder | OS-specific |
| `TREASUREPOS_PORT` | Server port | Auto-assigned |
| `PORT` | Alternative port variable | Auto-assigned |

### 🖨️ **Printer Configuration**
Edit `app.py` → `print_receipt()` function:
```python
printer_name = "ZDesigner ZD230-203dpi ZPL"  # Change to your printer's name
```

---

## 🗃️ Database Schema (SQLite)

<details>
<summary><strong>📊 Click to expand database structure</strong></summary>

### **🏷️ items**
| Column | Type | Description |
|--------|------|-------------|
| `barcode` | TEXT (UNIQUE) | Product identifier |
| `name` | TEXT | Product name |
| `qty` | INTEGER | Stock quantity |
| `category` | TEXT | Product category |
| `size` | TEXT | Product size |
| `status` | TEXT | Product status |
| `image` | TEXT | Image filename |
| `discontinued_time` | DATETIME | Discontinuation timestamp |
| `price_int` | INTEGER | Price in cents (preferred) |
| `wholesale_price_int` | INTEGER | Wholesale price in cents |

### **💰 sales**
| Column | Type | Description |
|--------|------|-------------|
| `time` | DATETIME | Sale timestamp |
| `items` | TEXT | Cart JSON snapshot |
| `pay_type` | TEXT | Payment method (`cash`/`card`) |
| `refunded` | BOOLEAN | Refund status |
| `total_int` | INTEGER | Total amount in cents |

### **📦 sale_items**
| Column | Type | Description |
|--------|------|-------------|
| `sale_id` | INTEGER | Reference to sales table |
| `barcode` | TEXT | Product barcode |
| `name` | TEXT | Product name at time of sale |
| `category` | TEXT | Product category |
| `size` | TEXT | Product size |
| `qty` | INTEGER | Quantity sold |
| `price_int` | INTEGER | Unit price in cents |

### **📋 stock_log**
| Column | Type | Description |
|--------|------|-------------|
| `barcode` | TEXT | Product barcode |
| `change` | INTEGER | Stock change amount |
| `type` | TEXT | Change type (`in`, `out`, `sale`, `refund`, `delete_revert`) |
| `time` | DATETIME | Change timestamp |

### **↩️ refund_log**
| Column | Type | Description |
|--------|------|-------------|
| `sale_id` | INTEGER | Reference to refunded sale |
| `reason` | TEXT | Refund reason |
| `amount` | INTEGER | Refund amount |
| `time` | DATETIME | Refund timestamp |

> 💡 **Note**: All monetary calculations prefer integer columns for precision. Legacy float values are fallback only.

</details>

---

## 📥📤 Import / Export

### **📊 Import Products (Excel)**
**Endpoint**: `POST /import/items`

**Required Excel Headers:**
```
barcode | name | price | wholesale_price | qty | category | size | [status] | [image]
```

**Category Options**: `bag`, `top`, `bottom`, `shoes`, `dress`  
**Size Options**: `free`, `s`, `m`, `l`, `xl`  
**Image Paths**: Only `images/filename.jpg` format accepted for security

### **📋 Export Options**

| Export Type | Endpoint | Output Format |
|-------------|----------|---------------|
| **Products** | `GET /export/items` | `상품목록_items.xlsx` |
| **Sales** | `GET /export/sales?start=YYYY-MM-DD&end=YYYY-MM-DD&pay_type=cash\|card&fmt=xlsx\|csv` | Excel or CSV stream |

> 💡 **Tip**: Use `fmt=csv` for large datasets to enable streaming.

---

## 🔌 API Endpoints

<details>
<summary><strong>📡 Click to expand API documentation</strong></summary>

### **📦 Inventory Management**
```http
GET    /api/items                           # List all items
GET    /api/items/search?q=&category=&sort= # Search with pagination
GET    /api/item/<barcode>                  # Get single item
POST   /api/item                            # Add item (JSON/multipart)
PUT    /api/item/<barcode>                  # Update item
DELETE /api/item/<barcode>                  # Delete item
POST   /api/stockio                         # Manual stock adjustment
```

### **💰 Sales Operations**
```http
POST   /api/sale                            # Process checkout
GET    /api/sales?page=&page_size=          # List sales (paginated)
POST   /api/sale/delete                     # Batch delete sales
POST   /api/sale/refund                     # Process refunds
GET    /api/item_sales/<barcode>            # Item sales history
```

### **📊 Analytics & Reports**
```http
GET    /api/sales/top_items?days=&pay_type=           # Top selling products
GET    /api/sales/stats?group=day&start=&end=        # Time-series data
GET    /api/sales/heatmap_hour_weekday?metric=       # Sales heatmap
```

### **🔧 System**
```http
GET    /healthz                             # Health check
GET    /static/images/<filename>            # Serve product images
```

</details>

---

## 🧾 Receipt Customization

The receipt system uses `templates/receipt.html` with a **624px canvas width** (≈79mm paper).

### **🔄 Processing Pipeline**
```
HTML Template → Playwright Screenshot → PNG → ZPL → Zebra Printer
```

### **🎨 Common CSS Customizations**

<details>
<summary><strong>Click to expand styling options</strong></summary>

```css
/* Paper width for 79mm thermal paper */
:root {
    --paper-w: 624px;
}

/* Logo spacing adjustment */
.logo-container {
    margin: 6px 0 30px;
}

/* Table layout optimization */
table {
    table-layout: fixed;
}

th, td {
    padding: 11px 7px;
    word-break: break-word;
    overflow-wrap: anywhere;
    vertical-align: middle;
}

/* Product name column spacing */
td.name-cell {
    padding-right: 12px;
}

/* Center alignment for quantity & unit price columns */
thead th:nth-child(2), tbody td:nth-child(2),
thead th:nth-child(3), tbody td:nth-child(3) {
    text-align: center;
    vertical-align: middle;
}

/* Right alignment for total column */
thead th:nth-child(4), tbody td:nth-child(4) {
    text-align: right;
    vertical-align: middle;
}

/* VAT notice styling */
.vat-notice {
    font-size: 1.1em;
    font-weight: 600;
}

/* Bottom margin for paper tear */
.tail-blank {
    height: 2cm;
}
```

</details>

### **🔒 Security Features**
- **Path Safety**: Only `images/filename.jpg` relative paths accepted
- **Input Validation**: Absolute paths and traversal attempts blocked
- **File Serving**: Controlled via `/static/images/<file>` endpoint

---

## 🔧 Troubleshooting

<details>
<summary><strong>🚨 Common Issues & Solutions</strong></summary>

### **🎭 Playwright Issues**
| Problem | Solution |
|---------|----------|
| Playwright not installed | `python -m playwright install chromium` |
| Element screenshot fails | Ensure Chromium browser is available |
| Receipt rendering errors | Check HTML template syntax |

### **🖨️ Printing Issues**
| Problem | Solution |
|---------|----------|
| Printer not found | Set correct `printer_name` in `app.py` |
| ZPL format errors | Verify printer supports ZPL commands |
| Print quality issues | Adjust DPI settings (default: 203 dpi) |

### **🌐 Network & Port Issues**
| Problem | Solution |
|---------|----------|
| Port already in use | Set `TREASUREPOS_PORT` environment variable |
| Can't access web interface | Use `main.py` for auto port selection |
| Firewall blocking | Add exception for chosen port |

### **🖼️ Image Issues**
| Problem | Solution |
|---------|----------|
| Images don't display | Use only `images/<filename>` relative paths |
| Image upload fails | Check file permissions in data directory |
| Large image sizes | Consider image compression before import |

### **📦 Build Issues**
| Problem | Solution |
|---------|----------|
| EXE missing resources | Add `--collect-all` flags during build |
| Import errors in EXE | Include `--hidden-import` for missing modules |
| Icon not showing | Ensure `icon.ico` exists in project root |

</details>

---

# 🇺🇸 English
*(This is the canonical English documentation above)*

---

# 🇨🇳 简体中文

<div align="center">

**基于 Flask 的本地收银系统，支持 79mm 小票打印和 ZPL 格式**

</div>

## 📋 系统简介

TreasurePOS 是一个 **本地优先** 的 Flask 收银系统，专为中小型企业设计。支持完整的库存管理、结算处理、退款操作、库存跟踪和数据导出功能。系统通过 Playwright 捕获 HTML 元素生成专业小票，转换为 ZPL 格式在 Zebra 兼容的热敏打印机上打印。

## ✨ 主要特色

- 🏠 **本地运行** - 无需外部数据库，完全本地化部署
- 💾 **智能数据管理** - 用户数据目录自动迁移，文件结构清晰
- 🔢 **精确计算** - 整数金额列（`*_int`），避免浮点误差
- 🔍 **高性能搜索** - 服务端搜索分页，响应迅速
- 📊 **导入导出** - Excel 导入导出，大数据集 CSV 流式处理
- 🧾 **专业打印** - HTML 元素截图 → PNG → ZPL 热敏打印

## 🚀 快速开始

### 环境搭建
```bash
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # macOS/Linux

pip install flask flask-cors pandas openpyxl pillow playwright pywin32 pywebview
python -m playwright install chromium
```

### 启动应用
```bash
python app.py      # Web 界面
python main.py     # 桌面窗口
```

- **访问地址**: http://127.0.0.1:5000
- **健康检查**: `/healthz` → 返回 `ok`
- **环境变量**: `TREASUREPOS_PORT`（端口），`TREASUREPOS_DATA_DIR`（数据目录）

## 📦 应用打包（Windows）

```powershell
pyinstaller --onedir --windowed --noconfirm --clean --name TreasurePOS --icon icon.ico ^
  --add-data "templates;templates" ^
  --add-data "static;static" ^
  --add-data "uploads;uploads" ^
  main.py
```
**启动**：`dist\TreasurePOS\TreasurePOS.exe`

> ℹ️ macOS/Linux 把 `--add-data` 中的分号 `;` 改成冒号 `:`（例：`--add-data "templates:templates"`）。

### 🖨️ Playwright 运行方式
- **A · 使用系统 Edge（推荐，体积最小）**
  ```python
  browser = await p.chromium.launch(channel="msedge", headless=True)
  ```
- **B · 在目标机安装 Chromium**
  ```powershell
  python -m playwright install chromium
  ```
- **C · 把 Chromium 一起打进 onedir（离线运行）**
  ```powershell
  set PLAYWRIGHT_BROWSERS_PATH=playwright-browsers
  python -m playwright install chromium
  pyinstaller --onedir --windowed --noconfirm --clean --name TreasurePOS --icon icon.ico ^
    --add-data "templates;templates" ^
    --add-data "static;static" ^
    --add-data "uploads;uploads" ^
    --add-data "playwright-browsers;playwright/driver/package/.local-browsers" ^
    main.py
  ```

## 🧾 小票样式调整

小票模板位于 `templates/receipt.html`，画布宽度 **624px**（≈79mm）

### CSS 样式定制

```css
/* 纸张宽度设置 */
:root { --paper-w: 624px; }

/* Logo 下方间距 */
.logo-container { margin: 6px 0 30px; }

/* 表格第2/3列居中对齐，第4列右对齐 */
thead th:nth-child(2), tbody td:nth-child(2),
thead th:nth-child(3), tbody td:nth-child(3) {
    text-align: center;
    vertical-align: middle;
}

thead th:nth-child(4), tbody td:nth-child(4) {
    text-align: right;
    vertical-align: middle;
}

/* 底部撕纸留白 */
.tail-blank { height: 2cm; }
```

## 🔧 常见问题

| 问题 | 解决方案 |
|------|----------|
| Playwright 未安装 | `python -m playwright install chromium` |
| 打印机无法找到 | 在 `app.py` 中设置正确的 `printer_name` |
| 端口被占用 | 设置 `TREASUREPOS_PORT` 或使用 `main.py` |
| 图片无法显示 | 仅支持 `images/<文件名>` 相对路径格式 |

---

# 🇰🇷 한국어

<div align="center">

**Flask 기반 로컬 POS 시스템 - 79mm 영수증 인쇄 및 ZPL 지원**

</div>

## 📋 시스템 개요

TreasurePOS는 **로컬 우선** Flask 기반 POS 시스템으로 중소기업을 위해 설계되었습니다. 포괄적인 재고 관리, 결제 처리, 환불, 재고 추적 및 데이터 내보내기 기능을 제공합니다. Playwright로 HTML 요소를 캡처하여 전문적인 영수증을 생성하고 ZPL 형식으로 변환하여 Zebra 호환 열전사 프린터에서 인쇄합니다.

## ✨ 주요 기능

- 🏠 **로컬 실행** - 외부 데이터베이스 불필요, 완전 로컬 배포
- 💾 **스마트 데이터 관리** - 사용자 데이터 디렉터리 자동 마이그레이션
- 🔢 **정밀 계산** - 정수 금액 컬럼(`*_int`)으로 부동소수점 오차 방지
- 🔍 **고성능 검색** - 서버 사이드 검색 페이징, 빠른 응답
- 📊 **가져오기/내보내기** - Excel 가져오기/내보내기, CSV 스트리밍
- 🧾 **전문적 인쇄** - HTML 요소 스크린샷 → PNG → ZPL 인쇄

## 🚀 빠른 시작

### 환경 설정
```bash
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # macOS/Linux

pip install flask flask-cors pandas openpyxl pillow playwright pywin32 pywebview
python -m playwright install chromium
```

### 애플리케이션 실행
```bash
python app.py      # 웹 인터페이스
python main.py     # 데스크톱 창
```

- **접속 주소**: http://127.0.0.1:5000
- **상태 확인**: `/healthz` → `ok` 반환
- **환
