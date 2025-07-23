# Zebra_pos_system
Python-based POS system for Zebra printers（flask）
ZEBRA ZD230
Zebra_pos_system is an open-source POS (Point of Sale) solution built with Python and Flask, designed specifically for use with Zebra printers (such as the ZD230 series). The system features a simple Korean-language web interface and supports only single-user operation, making it ideal for small shops and personal use. There is no support for multi-user management or multilingual features.

Core functions include product sales registration, inventory management, invoice (receipt) printing, and scanning of 1D barcodes for product entry. The application uses a local SQLite database for fast and secure data storage. Users can manage sales and inventory through a clear web dashboard and print receipts directly via the Zebra printer. The system does not support barcode generation or printing—only scanning of 1D barcodes is provided.

Zebra_pos_system is best suited for personal merchants, small retail shops, and mobile vendors who need simple sales management and automated receipt printing. Developers are welcome to adapt or expand the system as needed. For detailed installation and usage instructions, please refer to the project homepage and README.


Zebra_pos_system은 Python과 Flask로 개발된 오픈소스 POS(포스) 시스템으로, Zebra 프린터(ZD230 등)와 연동하여 발행 영수증을 쉽고 빠르게 출력할 수 있습니다. 본 시스템은 오직 한글(한국어) 인터페이스만 제공하며, 단일 사용자만 지원합니다. 복잡한 다국어 지원이나 다중 사용자 기능은 포함되어 있지 않습니다.

주요 기능은 상품 판매 등록, 재고 정보 관리, 영수증(발표) 인쇄, 그리고 바코드(바코드 리더기로 스캔) 상품 입력입니다. 시스템은 SQLite 로컬 데이터베이스를 사용하여 데이터의 안전성과 속도를 보장하며, 사용자는 웹 기반 화면을 통해 판매 및 재고 현황을 간단하게 확인·관리할 수 있습니다. 바코드 생성 및 인쇄 기능은 제공하지 않고, 1차원 바코드 스캔(입력)만 지원합니다.

Zebra_pos_system은 복잡하지 않고 실용적인 판매·영수증 출력 환경을 원하는 소상공인, 단일 점포, 이동식 매장 등에게 적합합니다. 추가 개발이나 기능 확장이 필요한 경우 누구나 자유롭게 커스터마이징할 수 있습니다. 설치 및 사용 방법은 프로젝트 홈과 README 파일을 참고하세요.


Zebra_pos_system 是一个基于 Python 和 Flask 的开源收银系统（POS），专为 Zebra 打印机（如 ZD230 系列）设计，适合中小型商店和个人用户。系统仅支持韩文界面，使用简单直观，无需复杂设置。支持本地单用户操作，专注于日常销售管理和发票打印，不包含多用户权限管理或多语言功能。

主要功能包括：商品销售登记、库存信息管理、发票（收据）打印，以及一维码（条码）扫描录入商品信息。系统内置 SQLite 本地数据库，保障数据持久化和快速读写。用户可以通过网页界面轻松操作，实现销售、库存数据的管理与查询，并可直接将销售信息通过 Zebra 打印机打印为发票。系统不支持条形码生成与打印，仅支持一维码扫描录入。

Zebra_pos_system 适合需要简易销售管理和自动化发票打印的个人商户、小型便利店、流动摊位等。欢迎开发者根据自身需求二次开发和功能扩展。详细安装与使用说明请参见项目主页和 README 文件。



