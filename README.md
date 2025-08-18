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
- **영수증 폭 고정 79mm (≈624px @ 203dpi)** — 기본값 79mm. `receipt.html`의 CSS에서 손쉽게 변경 가능합니다.
  ```css
  :root { --paper-w: 624px; }   /* ≈79mm @203dpi */
  .receipt { width: 79mm; }     /* mm 단위도 직접 사용 가능 */
  ```
- **기본 프린터: Zebra ZD230** — `app.py`에 프린터 이름이 하드코딩되어 있습니다. 환경에 맞게 수정하면 다른 Zebra/열감열 프린터도 동작합니다.
  ```python
  printer_name = "ZDesigner ZD230-203dpi ZPL"
  ```
- **Zebra 언어팩(다국어 폰트) 불필요** — `receipt.html`을 이미지로 렌더링 후 ZPL 그래픽으로 전송하므로, OS에 해당 언어 폰트만 설치되어 있으면 **한/중/영 등 유니코드 텍스트를 그대로 출력**합니다. 현재 샘플은 한국어이며, `receipt.html`을 수정해 **임의의 언어**로 변경 가능.
- **설정 페이지에서 UI 언어 전환** — Settings에서 한국어/中文/English 즉시 전환.

### 주요 화면
- **판매(홈)**: 스캔/수기 입력, 검색/카테고리, 장바구니, 소매/도매가, 현금/카드 결제, 잔돈/영수증 출력  
- **상품관리**: Excel Import/Export, 이미지, 단종/품절, 카테고리·사이즈 정규화(pants→bottom 자동 보정)  
- **매출**: 기간/결제수단 필터, 일/주/월/년 집계, Top10, 요일×시간 히트맵, 환불/삭제  
- **입출고**: 날짜/바코드별 입고/출고/조정 기록, 내보내기  
- **설정**: 언어 전환(한국어/English/中文)

### 설치
```bash
python -m pip install flask flask-cors pandas pillow html2image pywin32
```

### 실행
```bash
python app.py      # 개발 콘솔
python main.py     # 데스크탑 창(내장 브라우저)
```

### 데이터 경로
- Windows: `%LOCALAPPDATA%/TreasurePOS`  
- macOS: `~/Library/Application Support/TreasurePOS`  
- Linux: `~/.local/share/treasurepos`  
- 환경변수 `TREASUREPOS_DATA_DIR`로 변경 가능

### Excel Import/Export
- **Export**: `상품관리 → 내보내기` (Excel/CSV)
- **Import**: `상품관리 → 가져오기` (권장 열)
  ```text
  barcode, name, price, wholesale_price, qty, category, size, status, image
  ```
- 카테고리 보정: `pants` → `bottom` 자동 정규화

### 매출 분석
- 일/주/월/년 집계, Top10, 요일×시간 히트맵
- 결제수단(현금/카드) 필터 및 CSV/Excel 내보내기

### 영수증 출력(Windows)
- ZPL 호환 프린터(예: Zebra ZD230) 권장
- 드라이버 설치 후 코드의 프린터 이름을 환경에 맞게 수정
- 결제 완료 후 **영수증 출력** 버튼 클릭

</details>

---

<details>
<summary><b>🇨🇳 中文说明</b></summary>

### 简介
TreasurePOS 是一款**本地运行**的轻量级 POS 网页应用。支持条码扫描/手输、零售价/批发价切换、付款方式（现金/刷卡）、库存出入库记录、销售统计与热力图、Excel 导入/导出，以及多语言（韩/中/英）切换。

### 🔶 亮点 (Highlights)
- **票据宽度固定 79mm（≈624px @ 203dpi）** — 默认 79mm，可在 `receipt.html` 的 CSS 里修改：
  ```css
  :root { --paper-w: 624px; }   /* ≈79mm @203dpi */
  .receipt { width: 79mm; }     /* 也可直接使用毫米单位 */
  ```
- **默认打印机：Zebra ZD230** — `app.py` 里硬编码打印机名称。按实际环境调整即可兼容其他 Zebra/热敏机。
  ```python
  printer_name = "ZDesigner ZD230-203dpi ZPL"
  ```
- **无需购买 Zebra 语言包** — 小票由 `receipt.html` 渲染为图片，再以 ZPL 图像方式发送；只要系统装有相应字体，就能直接打印 **中/韩/英等任意 Unicode 文本**。当前示例为韩文，可在 `receipt.html` 修改文本/字体以支持 **任意语言**。
- **设置页切换 UI 语言** — Settings 页面可在 中文 / 한국어 / English 之间一键切换。

### 页面
- **销售（首页）**：扫描/手输、搜索与分类、购物车、零售/批发价、现金/刷卡、找零与打印小票  
- **商品管理**：Excel 导入/导出、图片、售罄/下架、类别/尺码统一（pants→bottom 自动矫正）  
- **销售**：按时间/方式筛选，日/周/月/年汇总，Top10，星期×小时热力图，退款/删除  
- **出入库**：按日期/条码查询入库/出库/调整，导出  
- **设置**：语言切换（한국어/English/中文）

### 安装
```bash
python -m pip install flask flask-cors pandas pillow html2image pywin32
```

### 运行
```bash
python app.py      # 控制台
python main.py     # 桌面窗口（内置浏览器）
```

### 数据目录
- Windows：`%LOCALAPPDATA%/TreasurePOS`  
- macOS：`~/Library/Application Support/TreasurePOS`  
- Linux：`~/.local/share/treasurepos`  
- 也可用环境变量 `TREASUREPOS_DATA_DIR` 指定

### Excel 导入/导出
- **导出**：商品管理 → 导出（Excel/CSV）  
- **导入**：上传 Excel（建议列）
  ```text
  barcode, name, price, wholesale_price, qty, category, size, status, image
  ```
- 类别统一：`pants` → `bottom` 自动处理

### 销售统计
- 按 日/周/月/年 聚合，Top10，星期×小时热力图  
- 按支付方式筛选（现金/刷卡），导出 CSV/Excel

### 打印小票（Windows）
- 推荐 ZPL 协议热敏机（如 Zebra ZD230）  
- 安装驱动后在代码中修改打印机名称  
- 结账后点击 **打印小票**

</details>

---

<details>
<summary><b>🇺🇸 English Guide</b></summary>

### Overview
TreasurePOS is a **local‑first** Flask POS web app with barcode/manual input, retail/wholesale toggle, cash/card payments, stock in/out logs, sales analytics & heatmap, Excel import/export, and multilingual UI (KO/ZH/EN).

### 🔶 Highlights
- **Receipt width set to 79 mm (≈624 px @ 203 dpi)** — 79 mm by default; change it in `receipt.html` CSS:
  ```css
  :root { --paper-w: 624px; }   /* ≈79mm @203dpi */
  .receipt { width: 79mm; }
  ```
- **Default printer: Zebra ZD230** — Printer name is hard‑coded in `app.py`. Adjust to match your environment for other Zebra/thermal printers.
  ```python
  printer_name = "ZDesigner ZD230-203dpi ZPL"
  ```
- **No Zebra language pack required** — The receipt is rendered from `receipt.html` to an image, then sent as a ZPL graphic; with proper OS fonts installed, **any Unicode text** (KO/ZH/EN, etc.) prints correctly. Current sample strings are Korean—edit `receipt.html` to switch to **any language**.
- **In‑app language switch** — Use **Settings** to toggle KO/ZH/EN on the fly.

### Pages
- **Sales (Home)**, **Manage**, **Sales**, **Stock Log**, **Settings** — search, categories, cart, retail/wholesale, payments, analytics/heatmap, Excel import/export, language switch.

### Installation
```bash
python -m pip install flask flask-cors pandas pillow html2image pywin32
```

### Run
```bash
python app.py      # dev console
python main.py     # desktop window (embedded browser)
```

### Data location
- Windows: `%LOCALAPPDATA%/TreasurePOS`
- macOS: `~/Library/Application Support/TreasurePOS`
- Linux: `~/.local/share/treasurepos`
- Override with `TREASUREPOS_DATA_DIR`

### Excel Import/Export
- **Export** from Manage page (Excel/CSV)
- **Import** Excel with columns:
  ```text
  barcode, name, price, wholesale_price, qty, category, size, status, image
  ```
- Category normalization: `pants` → `bottom`

### Sales analytics
- Aggregations by day/week/month/year, Top10, weekday×hour heatmap; filter by payment type; export CSV/Excel

### Receipt printing (Windows)
- ZPL‑compatible printer recommended (e.g., Zebra ZD230); install driver and update printer name; click **Print Receipt** after checkout.

</details>

---

## Configuration
- **Environment variable**: `TREASUREPOS_DATA_DIR` to change the data root.
- **Receipt width**: Adjust CSS in `receipt.html` (`79mm` by default).
- **Printer name**: Edit the hard‑coded name in `app.py` (`ZDesigner ZD230-203dpi ZPL`).

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
- **Image too wide/narrow**: tweak `79mm` width or adjust `--paper-w` px value.

## Roadmap
- Refund workflow improvements
- More payment methods (e.g., mobile)
- Role‑based access (multi‑user)
- Cloud‑optional sync (opt‑in)

## License
MIT recommended for small shops. Add your license file as needed.