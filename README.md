TreasurePOS (Flask + Desktop WebView)

KO/ZH/EN local-first POS for small shops. Scan barcodes, switch retail/wholesale price, checkout by cash/card, keep stock logs, view sales analytics (heatmap/aggregation), and print Zebra receipts (ZPL).

语言 | 언어 | Language
中文 • 한국어 • English

目录 · Table of Contents · 목차

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

Key parameters in app.py:

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
