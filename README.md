# Zebra_pos_system
Python-based POS system for Zebra printers（flask）
ZEBRA ZD230
Zebra_pos_system is an open-source POS (Point-of-Sale) system designed specifically for Korean small business owners, supporting only single-user mode and providing a full Korean-language interface. Developed using Python and Flask, this application is optimized for use with Zebra printers (such as the ZD230 series), making it ideal for retail shops, convenience stores, and small restaurants in Korea that require basic, local-language sales and inventory management.

Unlike more complex POS solutions, Zebra_pos_system is intentionally simple: there is no multi-user support, no language switching, and no user authentication or permissions modules. The system is intended to run on a single computer and is operated by one user at a time, with all data stored locally in an SQLite database for security and privacy. All operations, including sales, inventory management, and receipt/barcode printing, are performed through a web browser interface in Korean, supporting Windows, Mac, and Linux systems.

Key features include product registration and management, real-time inventory updates, sales transaction recording, and direct Korean-language receipt and barcode printing via Zebra printers. The system also allows for basic data export (such as to Excel files) for accounting or reporting purposes. The absence of multi-user or multilingual modules means Zebra_pos_system is highly reliable and easy to deploy, with minimal setup required.

This project is open-source, tailored for small Korean businesses and shop owners who need straightforward POS and inventory functionality in a single-user, Korean-only environment. Community suggestions and contributions are welcome, especially from users wishing to improve or extend the software. Please refer to the README file for detailed installation, deployment, and usage instructions.


Zebra_pos_system은 한국 소상공인을 위해 개발된 단일 사용자용 오픈소스 POS(판매시점 관리) 시스템입니다. Python과 Flask로 제작되었으며, 모든 화면과 출력이 한국어로 제공됩니다. Zebra 프린터(ZD230 시리즈 등)와 연동되어 소매점, 편의점, 작은 음식점 등에서 사용할 수 있도록 설계되었습니다. 시스템은 상품 판매, 재고 관리, 영수증 및 바코드 출력 등 필수 기능에 집중하여, 복잡한 다국어 지원이나 다중 사용자/권한 기능 없이 쉽고 빠르게 사용할 수 있습니다.

본 시스템은 단일 사용자를 위한 솔루션으로, 로그인이나 사용자 관리 절차 없이 한 대의 컴퓨터에서 운영됩니다. 모든 데이터는 로컬 SQLite 데이터베이스에 저장되어, 네트워크 연결 없이도 안전하게 사용할 수 있습니다. 웹 브라우저를 통해 POS 기능을 실행할 수 있으며, Windows, Mac, Linux 환경에서 바로 설치하고 사용할 수 있습니다.

주요 기능은 상품 등록 및 관리, 재고 실시간 확인, 판매 내역 기록, 영수증 및 바코드의 한국어 출력, 그리고 기본적인 데이터 내보내기(엑셀 등)를 포함합니다. 단순성과 안정성에 중점을 두었으며, 누구나 쉽게 배포하고 유지관리할 수 있습니다.

Zebra_pos_system은 한글 전용, 단일 사용자 환경에 최적화되어 있으며, 복잡한 시스템이 필요 없는 소규모 매장에서 활용하기에 적합합니다. 프로젝트는 오픈소스로 운영되며, 사용 경험 및 기능 개선 의견을 환영합니다. 자세한 설치 및 사용법은 README 파일을 참고해 주세요.


Zebra_pos_system 是一个专为韩国本地中小商户开发的单用户版开源 POS（收银系统），使用 Python 与 Flask 框架实现，界面语言为韩文。该系统主要配合 Zebra 打印机（如 ZD230 系列）使用，适用于零售、便利店、小型餐饮等业务场景。项目集成了商品销售、库存管理、小票和条码打印等基础功能，简洁高效，适合对多语言和多用户权限没有需求的个人或小型商户。

本系统设计理念是简单易用，界面全部为韩文，方便韩国用户直接上手，无需额外的语言切换或复杂配置。数据采用本地 SQLite 数据库存储，保障单台设备上的业务数据安全。操作全部通过浏览器完成，支持 Windows、Mac 和 Linux 等主流桌面操作系统，无需专业 IT 支持即可安装部署。

功能方面，用户可录入和管理商品信息、实时更新库存、生成销售单据，并直接通过 Zebra 打印机打印韩文收据和条码标签。支持简单的数据导出，便于日常对账和报表统计。由于是单用户系统，无需登录或用户管理模块，进一步简化了操作流程。

Zebra_pos_system 以开源形式发布，适合需要基础收银和库存功能、仅使用韩文、仅在单台电脑上操作的商户。欢迎有相关需求的用户和开发者提出建议或参与代码完善。安装、部署和功能文档请参考仓库 README 文件。


