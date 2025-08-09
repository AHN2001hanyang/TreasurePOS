# -*- coding: utf-8 -*-
from flask import Flask, render_template, request, jsonify, send_file, redirect, url_for, make_response, after_this_request, Response
from flask_cors import CORS
import sqlite3
from datetime import datetime, timedelta
import json
import pandas as pd
import os
import tempfile
import re
import shutil
import math
import csv
import io

# ===== 多语言字典 + 分类/尺码映射 =====
CATEGORY_CODE = ['bag', 'top', 'bottom', 'shoes']
SIZE_CODE = ['free', 's', 'm', 'l', 'xl']

TEXTS = {
    'ko': {
        'title': '계산대', 'manage': '상품 관리', 'sales': '판매 기록',
        'setting': '설정', 'print': '영수증 출력', 'total': '총액',
        'product': '상품', 'qty': '수량', 'price': '단가', 'wholesale_price': '도매가',
        'subtotal': '합계', 'date': '날짜', 'order': '주문번호',
        'thank': '감사합니다! Thank you! 谢谢光临!', 'contact': '연락처', 'export': '엑셀 내보내기',
        'add': '상품 추가', 'delete': '삭제', 'stocklog': '입출고 관리', 'checkout': '결제하기',
        'print_ok': '영수증 출력 성공', 'print_fail': '영수증 출력 실패', 'sale_ok': '결제 성공!',
        'added': '장바구니에 추가됨', 'remove': '삭제됨', 'empty_cart': '장바구니가 비었습니다',
        'exceed_stock': '재고를 초과했습니다', 'no_product': '상품 없음', 'sold_out': '매진', 'out_of_stock': '재고 없음',
        'search': '검색', 'cart': '장바구니', 'qty_nonnegative': '재고가 0 이하일 수 없습니다.',
        'import': '엑셀 가져오기', 'import_tip': '가져오기 양식：<b>바코드,이름,가격,도매가,재고,분류,사이즈</b> (엑셀 첫 행과 동일해야 함)',
        'save': '저장', 'cancel': '취소', 'edit': '수정', 'confirm_delete': '이 상품을 삭제하시겠습니까?',
        'normal': '정상', 'soldout': '매진', 'discontinued': '절판', 'status': '상태', 'action': '작업',
        'image': '이미지', 'detail': '상세', 'onsale': '판매중', 'discontinued_time': '절판시간',
        'sale_records': '판매 기록', 'no_sale_record': '판매 기록 없음', 'sale_id': '판매ID',
        'loading': '로딩중...', 'restore': '복구', 'size': '사이즈', 'category': '분류',
        'category_bag': '가방', 'category_top': '상의', 'category_bottom': '하의', 'category_shoes': '신발',
        'size_free': 'FREE', 'size_s': 'S', 'size_m': 'M', 'size_l': 'L', 'size_xl': 'XL',
        'retail': '소매가', 'choose_price_type': '가격 선택', 'sort': '정렬',
        'sort_default': '기본순', 'sort_price_asc': '가격↑', 'sort_price_desc': '가격↓',
        'barcode_input': '바코드/수동 입력:', 'barcode_placeholder': '바코드를 스캔하거나 직접 입력하세요',
        'search_placeholder': '바코드 또는 상품명 입력', 'search_tip': '바코드 스캔, 직접 입력, 상품명 검색 가능',
        'all': '전체', 'stock': '재고',
        'heatmap_title': '요일×시간 히트맵', 'metric': '지표', 'metric_orders': '주문수', 'metric_sales': '매출', 'metric_items': '판매수량',
        'mon': '월', 'tue': '화', 'wed': '수', 'thu': '목', 'fri': '금', 'sat': '토', 'sun': '일',
        # ====== 新增：后端 & sales 页面需要的键 ======
        'pay_type': '결제 방식', 'card': '카드', 'cash': '현금',
        'stats': '통계 유형', 'period': '기간', 'filter': '필터',
        'day': '일별', 'week': '주별', 'month': '월별', 'year': '연별',
        'low': '낮음', 'high': '높음',
        'per_page': '페이지당', 'current_page': '현재', 'records': '건',
        'delete_selected': '선택삭제', 'refund': '환불', 'delete_reason': '삭제 사유를 선택하세요:',
        'mistake': '작업 실수', 'confirm': '확인',
        'select_reason': '환불 사유 선택:', 'refund_defect': '하자', 'refund_notfit': '사이즈 안맞음',
        'refund_no_reason': '단순 변심', 'refund_dislike': '마음에 안듦', 'refund_other': '기타',
        'refund_other_detail': '기타 사유 입력(선택)',
        'select_to_delete': '삭제할 기록을 선택하세요', 'delete_ok': '삭제 완료',
        'select_to_refund': '환불할 기록을 선택하세요', 'refund_ok': '환불 완료',
        'order_count': '주문수', 'sales_amount': '매출액', 'vat_included': '부가세 포함',
        'product_detail': '상품 상세',
        'barcode_required': '바코드는 필수입니다',
        'invalid_params': '유효하지 않은 요청입니다', 'db_error': 'DB 오류', 'updated': '업데이트됨', 'deleted': '삭제됨', 'ok': 'ok'
    },
    'zh': {
        'title': '收银台', 'manage': '商品管理', 'sales': '销售记录',
        'setting': '设置', 'print': '打印小票', 'total': '总金额',
        'product': '商品', 'qty': '数量', 'price': '单价', 'wholesale_price': '批发价',
        'subtotal': '小计', 'date': '日期', 'order': '订单号',
        'thank': '谢谢光临! Thank you! 감사합니다!', 'contact': '联系方式', 'export': '导出Excel',
        'add': '添加商品', 'delete': '删除', 'stocklog': '出入库管理', 'checkout': '结算',
        'print_ok': '小票打印成功', 'print_fail': '打印失败', 'sale_ok': '结算成功!',
        'added': '已添加到购物车', 'remove': '已删除', 'empty_cart': '购物车为空',
        'exceed_stock': '超出库存', 'no_product': '无此商品', 'sold_out': '售罄', 'out_of_stock': '库存不足',
        'search': '搜索', 'cart': '购物车', 'qty_nonnegative': '库存不能小于0。',
        'import': '导入Excel', 'import_tip': '导入模板：<b>条码,名称,单价,批发价,库存,分类,尺码</b>（必须与Excel首行一致）',
        'save': '保存', 'cancel': '取消', 'edit': '编辑', 'confirm_delete': '确定删除该商品吗？',
        'normal': '正常', 'soldout': '售罄', 'discontinued': '已下架', 'status': '状态', 'action': '操作',
        'image': '图片', 'detail': '详情', 'onsale': '在售', 'discontinued_time': '下架时间',
        'sale_records': '销售记录', 'no_sale_record': '暂无销售记录', 'sale_id': '销售ID',
        'loading': '加载中...', 'restore': '恢复', 'size': '尺码', 'category': '分类',
        'category_bag': '包', 'category_top': '上衣', 'category_bottom': '下装', 'category_shoes': '鞋',
        'size_free': '均码', 'size_s': 'S', 'size_m': 'M', 'size_l': 'L', 'size_xl': 'XL',
        'retail': '零售价', 'choose_price_type': '选择价格', 'sort': '排序',
        'sort_default': '默认', 'sort_price_asc': '价格↑', 'sort_price_desc': '价格↓',
        'barcode_input': '条码/手动输入:', 'barcode_placeholder': '请扫描或输入条码',
        'search_placeholder': '输入条码或商品名', 'search_tip': '支持条码/手动输入/商品名搜索',
        'all': '全部', 'stock': '库存',
        'heatmap_title': '星期×时段 热力图', 'metric': '指标', 'metric_orders': '订单数', 'metric_sales': '销售额', 'metric_items': '件数',
        'mon': '周一', 'tue': '周二', 'wed': '周三', 'thu': '周四', 'fri': '周五', 'sat': '周六', 'sun': '周日',
        # ====== 新增：后端 & sales 页面需要的键 ======
        'pay_type': '支付方式', 'card': '刷卡', 'cash': '现金',
        'stats': '统计类型', 'period': '时间段', 'filter': '筛选',
        'day': '按日', 'week': '按周', 'month': '按月', 'year': '按年',
        'low': '低', 'high': '高',
        'per_page': '每页', 'current_page': '当前', 'records': '记录',
        'delete_selected': '选择删除', 'refund': '退款', 'delete_reason': '请选择删除原因：',
        'mistake': '操作失误', 'confirm': '确认',
        'select_reason': '选择退款原因：', 'refund_defect': '有瑕疵', 'refund_notfit': '不合身',
        'refund_no_reason': '无理由退货', 'refund_dislike': '不喜欢', 'refund_other': '其他',
        'refund_other_detail': '请填写其他原因（选填）',
        'select_to_delete': '请选择要删除的记录', 'delete_ok': '删除完成',
        'select_to_refund': '请选择要退款的记录', 'refund_ok': '退款完成',
        'order_count': '订单数', 'sales_amount': '销售额', 'vat_included': '含VAT',
        'product_detail': '商品详情',
        'barcode_required': '必须提供条码',
        'invalid_params': '参数无效', 'db_error': '数据库错误', 'updated': '已更新', 'deleted': '已删除', 'ok': 'ok'
    },
    'en': {
        'title': 'POS', 'manage': 'Product Management', 'sales': 'Sales Record',
        'setting': 'Settings', 'print': 'Print Receipt', 'total': 'Total',
        'product': 'Product', 'qty': 'Qty', 'price': 'Price', 'wholesale_price': 'Wholesale',
        'subtotal': 'Subtotal', 'date': 'Date', 'order': 'Order No.',
        'thank': 'Thank you! 감사합니다! 谢谢光临!', 'contact': 'Contact', 'export': 'Export Excel',
        'add': 'Add Product', 'delete': 'Delete', 'stocklog': 'Stock Log', 'checkout': 'Checkout',
        'print_ok': 'Receipt printed', 'print_fail': 'Print failed', 'sale_ok': 'Sale completed!',
        'added': 'Added to cart', 'remove': 'Removed', 'empty_cart': 'Cart is empty',
        'exceed_stock': 'Exceed stock', 'no_product': 'No product', 'sold_out': 'Sold Out', 'out_of_stock': 'Out of Stock',
        'search': 'Search', 'cart': 'Cart', 'qty_nonnegative': 'Stock cannot be less than 0.',
        'import': 'Import Excel', 'import_tip': 'Import format: <b>Barcode,Name,Price,Wholesale,Qty,Category,Size</b> (must match Excel header)',
        'save': 'Save', 'cancel': 'Cancel', 'edit': 'Edit', 'confirm_delete': 'Delete this product?',
        'normal': 'Normal', 'soldout': 'Sold Out', 'discontinued': 'Discontinued', 'status': 'Status', 'action': 'Action',
        'image': 'Image', 'detail': 'Detail', 'onsale': 'On Sale', 'discontinued_time': 'Discontinued Time',
        'sale_records': 'Sales Record', 'no_sale_record': 'No sales record', 'sale_id': 'Sale ID',
        'loading': 'Loading...', 'restore': 'Restore', 'size': 'Size', 'category': 'Category',
        'category_bag': 'Bag', 'category_top': 'Top', 'category_bottom': 'Bottom', 'category_shoes': 'Shoes',
        'size_free': 'FREE', 'size_s': 'S', 'size_m': 'M', 'size_l': 'L', 'size_xl': 'XL',
        'retail': 'Retail', 'choose_price_type': 'Price Type', 'sort': 'Sort',
        'sort_default': 'Default', 'sort_price_asc': 'Price↑', 'sort_price_desc': 'Price↓',
        'barcode_input': 'Barcode/Manual input:', 'barcode_placeholder': 'Scan or enter barcode',
        'search_placeholder': 'Barcode or product name', 'search_tip': 'Supports barcode scan/name/manual input',
        'all': 'All', 'stock': 'Stock',
        'heatmap_title': 'Weekday × Hour Heatmap', 'metric': 'Metric', 'metric_orders': 'Orders', 'metric_sales': 'Sales', 'metric_items': 'Items',
        'mon': 'Mon', 'tue': 'Tue', 'wed': 'Wed', 'thu': 'Thu', 'fri': 'Fri', 'sat': 'Sat', 'sun': 'Sun',
        # ====== New: backend & sales page keys ======
        'pay_type': 'Payment Type', 'card': 'Card', 'cash': 'Cash',
        'stats': 'Stats', 'period': 'Period', 'filter': 'Filter',
        'day': 'Daily', 'week': 'Weekly', 'month': 'Monthly', 'year': 'Yearly',
        'low': 'Low', 'high': 'High',
        'per_page': 'Per page', 'current_page': 'Page', 'records': 'Records',
        'delete_selected': 'Delete Selected', 'refund': 'Refund', 'delete_reason': 'Choose a delete reason:',
        'mistake': 'Mistake', 'confirm': 'Confirm',
        'select_reason': 'Select refund reason:', 'refund_defect': 'Defective', 'refund_notfit': 'Not fit',
        'refund_no_reason': 'No-reason return', 'refund_dislike': 'Dislike', 'refund_other': 'Other',
        'refund_other_detail': 'Enter other reason (optional)',
        'select_to_delete': 'Select records to delete', 'delete_ok': 'Delete completed',
        'select_to_refund': 'Select records to refund', 'refund_ok': 'Refund completed',
        'order_count': 'Orders', 'sales_amount': 'Sales Amount', 'vat_included': 'VAT included',
        'product_detail': 'Product Detail',
        'barcode_required': 'Barcode is required',
        'invalid_params': 'Invalid params', 'db_error': 'DB error', 'updated': 'Updated', 'deleted': 'Deleted', 'ok': 'ok'
    },
}

def get_lang():
    lang = request.cookies.get('lang')
    if lang not in TEXTS:
        lang = 'ko'
    return lang

def t(key: str, default: str = None, lang: str = None) -> str:
    """多语言取词：优先当前语言；其次英文；最后用 key 或 default"""
    lang = lang or get_lang()
    return TEXTS.get(lang, TEXTS['ko']).get(key, TEXTS['en'].get(key, default if default is not None else key))

base_path = os.path.abspath(os.path.dirname(__file__))

app = Flask(
    __name__,
    template_folder=os.path.join(base_path, 'templates'),
    static_folder=os.path.join(base_path, 'static')
)

# 仅允许本机端口 5000（固定 5000）
CORS(app, resources={
    r"/*": {"origins": [re.compile(r"^http://127\.0\.0\.1:\d+$"),
                       re.compile(r"^http://localhost:\d+$")]}
})

UPLOAD_FOLDER = os.path.join(base_path, 'uploads')
IMAGE_FOLDER = os.path.join(app.static_folder, 'images')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(IMAGE_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# ===== 安全校验：仅允许 static/images 下的受控相对路径 =====
SAFE_IMAGE_RE = re.compile(r'^images/[A-Za-z0-9_\-]+\.(?:jpe?g|png|webp)$', re.I)
def is_safe_image_relpath(p: str) -> bool:
    if not p:
        return False
    p = p.replace('\\', '/')
    # 禁止绝对路径、盘符、上跳
    if p.startswith('/') or '..' in p or re.match(r'^[A-Za-z]:[\\/]', p):
        return False
    if not SAFE_IMAGE_RE.fullmatch(p):
        return False
    abs_path = os.path.normpath(os.path.join(app.static_folder, p))
    try:
        return os.path.commonpath([abs_path, IMAGE_FOLDER]) == IMAGE_FOLDER
    except Exception:
        return False

# ---- SQLite 连接助手 ----
def connect_db():
    db_path = os.path.join(base_path, 'inventory.db')
    conn = sqlite3.connect(db_path)
    conn.execute('PRAGMA foreign_keys=ON')
    conn.execute('PRAGMA synchronous=NORMAL')
    conn.execute('PRAGMA temp_store=MEMORY')
    conn.execute('PRAGMA cache_size=-4000')  # ~4MB
    return conn

# ---- 通用：金额转“整数”（四舍五入） ----
def to_amount_int(v, default=0):
    try:
        if pd.isna(v):
            return default
    except Exception:
        pass
    try:
        return int(round(float(v)))
    except Exception:
        return default


@app.route('/healthz', methods=['GET'])
def healthz():
    return 'ok', 200

# ---- 数据库初始化（添加 *_int 字段，及 sale_items.price_int） ----
def init_db():
    db_path = os.path.join(base_path, 'inventory.db')
    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    c.execute('PRAGMA journal_mode=WAL')
    c.execute('PRAGMA synchronous=NORMAL')

    c.execute('''
        CREATE TABLE IF NOT EXISTS items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            barcode TEXT UNIQUE,
            name TEXT,
            price REAL DEFAULT 0,
            wholesale_price REAL DEFAULT 0,
            qty INTEGER DEFAULT 0,
            size TEXT DEFAULT 'free',
            category TEXT DEFAULT 'bag',
            status TEXT DEFAULT '',
            image TEXT,
            discontinued_time TEXT
        )
    ''')
    # 兼容老库：增加整数金额列
    for ddl in [
        'ALTER TABLE items ADD COLUMN price_int INTEGER DEFAULT 0',
        'ALTER TABLE items ADD COLUMN wholesale_price_int INTEGER DEFAULT 0',
        'ALTER TABLE items ADD COLUMN size TEXT DEFAULT "free"',
        'ALTER TABLE items ADD COLUMN category TEXT DEFAULT "bag"',
        'ALTER TABLE items ADD COLUMN image TEXT',
        'ALTER TABLE items ADD COLUMN discontinued_time TEXT'
    ]:
        try: c.execute(ddl)
        except: pass

    c.execute('''
        CREATE TABLE IF NOT EXISTS sales (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            time TEXT,
            items TEXT,
            total REAL,
            refunded INTEGER DEFAULT 0,
            pay_type TEXT DEFAULT "cash"
        )
    ''')
    try: c.execute('ALTER TABLE sales ADD COLUMN pay_type TEXT DEFAULT "cash"')
    except: pass
    try: c.execute('ALTER TABLE sales ADD COLUMN total_int INTEGER DEFAULT 0')
    except: pass

    c.execute('''
        CREATE TABLE IF NOT EXISTS sale_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sale_id INTEGER,
            barcode TEXT,
            name TEXT,
            category TEXT,
            size TEXT,
            qty INTEGER,
            price REAL
        )
    ''')
    try: c.execute('ALTER TABLE sale_items ADD COLUMN price_int INTEGER DEFAULT 0')
    except: pass

    c.execute('''
        CREATE TABLE IF NOT EXISTS stock_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            time TEXT,
            barcode TEXT,
            change INTEGER,
            type TEXT
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS refund_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sale_id INTEGER,
            time TEXT,
            reason TEXT,
            detail TEXT,
            amount REAL
        )
    ''')

    # 索引
    c.execute('CREATE INDEX IF NOT EXISTS idx_items_barcode ON items(barcode)')
    c.execute('CREATE INDEX IF NOT EXISTS idx_items_name ON items(name)')
    c.execute('CREATE INDEX IF NOT EXISTS idx_items_cat_stat ON items(category, status)')
    c.execute('CREATE INDEX IF NOT EXISTS idx_items_cat_id ON items(category, id)')
    c.execute('CREATE INDEX IF NOT EXISTS idx_sales_time ON sales(time)')
    c.execute('CREATE INDEX IF NOT EXISTS idx_sales_paytype ON sales(pay_type)')
    c.execute('CREATE INDEX IF NOT EXISTS idx_stocklog_barcode ON stock_log(barcode)')
    c.execute('CREATE INDEX IF NOT EXISTS idx_refundlog_saleid ON refund_log(sale_id)')
    c.execute('CREATE INDEX IF NOT EXISTS idx_saleitems_barcode ON sale_items(barcode)')
    c.execute('CREATE INDEX IF NOT EXISTS idx_saleitems_saleid ON sale_items(sale_id)')

    conn.commit()
    c.execute('ANALYZE')
    c.execute('PRAGMA optimize')
    conn.close()

def safe_filename(filename):
    return re.sub(r'[^A-Za-z0-9_\-]', '_', filename or '')

@app.route('/set_lang/<lang>')
def set_lang(lang):
    if lang not in TEXTS:
        lang = 'ko'
    resp = make_response(redirect(request.referrer or url_for('settings')))
    resp.set_cookie('lang', lang, max_age=3600*24*365)
    return resp

@app.route('/')
def index():
    lang = get_lang()
    return render_template('index.html', lang=lang, texts=TEXTS[lang], categories=CATEGORY_CODE, sizes=SIZE_CODE)

@app.route('/manage')
def manage():
    lang = get_lang()
    return render_template('manage.html', lang=lang, texts=TEXTS[lang], categories=CATEGORY_CODE, sizes=SIZE_CODE)

@app.route('/sales')
def sales_page():
    lang = get_lang()
    return render_template('sales.html', lang=lang, texts=TEXTS[lang])

@app.route('/stocklog')
def stocklog():
    lang = get_lang()
    return render_template('stocklog.html', lang=lang, texts=TEXTS[lang])

@app.route('/settings')
def settings():
    lang = get_lang()
    return render_template('settings.html', lang=lang, texts=TEXTS[lang])

# ---- 工具：安全类型转换 ----
def to_int(v, default=0):
    try:
        if pd.isna(v):
            return default
    except Exception:
        pass
    try:
        return int(float(v))
    except Exception:
        return default

def to_float(v, default=0.0):
    try:
        if pd.isna(v):
            return default
    except Exception:
        pass
    try:
        return float(v)
    except Exception:
        return default

def norm_category(cat):
    cat = (cat or '').strip().lower()
    return cat if cat in CATEGORY_CODE else CATEGORY_CODE[0]

def norm_size(sz):
    sz = (sz or '').strip().lower()
    return sz if sz in SIZE_CODE else SIZE_CODE[0]

# ---- Excel 导入导出接口 ----
@app.route('/export/items')
def export_items():
    conn = connect_db()
    # 导出用整数列；旧数据回落到 ROUND(price)
    df = pd.read_sql_query(
        '''
        SELECT barcode,
               name,
               COALESCE(price_int, CAST(ROUND(price) AS INTEGER)) AS price,
               COALESCE(wholesale_price_int, CAST(ROUND(wholesale_price) AS INTEGER)) AS wholesale_price,
               qty, category, size, status, discontinued_time, image
        FROM items 
        ORDER BY category,
          CASE WHEN status="절판" THEN ifnull(discontinued_time, "9999-12-31 23:59:59")
               ELSE "9999-12-31 23:59:59" END DESC,
          id DESC
        ''', conn)
    conn.close()
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx')
    df.to_excel(tmp.name, index=False)
    tmp_path = tmp.name
    tmp.close()

    @after_this_request
    def _cleanup(response):
        try:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
        except Exception:
            pass
        return response

    return send_file(tmp_path, as_attachment=True, download_name='상품목록_items.xlsx')

@app.route('/export/sales')
def export_sales():
    """支持过滤 + CSV 流式导出（金额为整数）"""
    start = request.args.get('start')
    end = request.args.get('end')
    pay_type = request.args.get('pay_type')
    fmt = (request.args.get('fmt') or 'xlsx').lower()

    where = []
    params = []
    if start and end:
        where.append("time BETWEEN ? AND ?")
        params += [start + " 00:00:00", end + " 23:59:59"]
    if pay_type in ('cash', 'card'):
        where.append("pay_type=?")
        params.append(pay_type)
    where_sql = (' WHERE ' + ' AND '.join(where)) if where else ''
    sql = f'''
        SELECT id, time, items,
               COALESCE(total_int, CAST(ROUND(total) AS INTEGER)) AS total,
               pay_type
        FROM sales{where_sql}
        ORDER BY id DESC
    '''

    if fmt == 'csv':
        def generate():
            conn = connect_db()
            c = conn.cursor()
            yield "id,time,items,total,pay_type\n"
            c.execute(sql, params)
            buf = io.StringIO()
            writer = csv.writer(buf)
            while True:
                rows = c.fetchmany(1000)
                if not rows:
                    break
                for rid, t, items, total, pt in rows:
                    buf.seek(0); buf.truncate(0)
                    writer.writerow([rid, t, (items or '').replace('\n',' ').replace('\r',' '), int(total or 0), pt])
                    yield buf.getvalue()
            conn.close()
        headers = {'Content-Disposition': 'attachment; filename="sales.csv"'}
        return Response(generate(), mimetype='text/csv; charset=utf-8', headers=headers)

    # 默认 xlsx
    conn = connect_db()
    df = pd.read_sql_query(sql, conn, params=params)
    conn.close()
    df['items'] = df['items'].apply(lambda x: x.replace('\n', ' ') if x else '')
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx')
    df.to_excel(tmp.name, index=False)
    tmp_path = tmp.name
    tmp.close()

    @after_this_request
    def _cleanup(response):
        try:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
        except Exception:
            pass
        return response

    return send_file(tmp_path, as_attachment=True, download_name='판매기록_sales.xlsx')

@app.route('/import/items', methods=['POST'])
def import_items():
    file = request.files.get('file')
    if not file:
        return jsonify({'msg': '파일이 없습니다'}), 400
    try:
        df = pd.read_excel(file)
    except Exception as e:
        return jsonify({'msg': f'엑셀 오류: {e}'}), 400

    conn = connect_db()
    c = conn.cursor()
    for _, row in df.iterrows():
        barcode = str(row.get('barcode', '')).strip()
        name = str(row.get('name', '')).strip()
        if not barcode or not name:
            continue
        qty = to_int(row.get('qty', 0), 0)
        if qty < 0:
            continue
        price_i = to_amount_int(row.get('price', 0), 0)
        wholesale_i = to_amount_int(row.get('wholesale_price', 0), 0)
        category = norm_category(row.get('category', 'bag'))
        size = norm_size(row.get('size', 'free'))
        status = str(row.get('status', '정상'))
        image = str(row.get('image', '') or '')
        c.execute('''INSERT OR REPLACE INTO items
            (barcode, name, price, price_int, wholesale_price, wholesale_price_int, qty, category, size, status, image)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
            (barcode, name, price_i, price_i, wholesale_i, wholesale_i, qty, category, size, status, image)
        )
    conn.commit()
    conn.close()
    return redirect('/manage')

# ---- 业务逻辑接口 ----
def _save_and_validate_image(file_storage, save_name_base: str) -> str:
    """保存并验证图片，返回 static 下相对路径，如 'images/xxx.jpg'；失败返回空串"""
    try:
        from PIL import Image as PILImage
    except Exception:
        ext = os.path.splitext(file_storage.filename)[1]
        img_fname = f"{save_name_base}{ext}"
        img_save_path = os.path.join(IMAGE_FOLDER, img_fname)
        file_storage.save(img_save_path)
        return f'images/{img_fname}'

    ext = os.path.splitext(file_storage.filename)[1].lower()
    if ext not in ('.jpg', '.jpeg', '.png', '.webp'):
        return ''
    img_fname = f"{save_name_base}{ext}"
    img_save_path = os.path.join(IMAGE_FOLDER, img_fname)
    file_storage.save(img_save_path)

    try:
        with PILImage.open(img_save_path) as im:
            im.verify()
        with PILImage.open(img_save_path) as im:
            im = im.convert('RGB')
            w, h = im.size
            max_side = max(w, h)
            if max_side > 1400:
                scale = 1400.0 / max_side
                im = im.resize((int(w*scale), int(h*scale)))
            im.save(img_save_path, optimize=True, quality=86)
    except Exception:
        try:
            os.remove(img_save_path)
        except Exception:
            pass
        return ''
    return f'images/{img_fname}'

@app.route('/api/item', methods=['POST'])
def add_item():
    if request.content_type and request.content_type.startswith('multipart'):
        barcode = (request.form.get('barcode') or '').strip()
        if not barcode:
            return jsonify({'msg': t('barcode_required')}), 400
        barcode_safe = safe_filename(barcode)
        name = request.form.get('name', '이름 없음')
        price_i = to_amount_int(request.form.get('price', 0), 0)
        wholesale_i = to_amount_int(request.form.get('wholesale_price', 0), 0)
        qty = to_int(request.form.get('qty', 0), 0)
        category = norm_category(request.form.get('category', CATEGORY_CODE[0]))
        size = norm_size(request.form.get('size', SIZE_CODE[0]))
        if qty < 0:
            return jsonify({'msg': TEXTS[get_lang()]['qty_nonnegative']}), 400
        status = request.form.get('status', '정상')
        image = request.files.get('image')
        image_path = ''
        if image:
            image_path = _save_and_validate_image(image, barcode_safe)
    else:
        data = request.json or {}
        barcode = (data.get('barcode') or '').strip()
        if not barcode:
            return jsonify({'msg': t('barcode_required')}), 400
        barcode_safe = safe_filename(barcode)
        name = data.get('name', '이름 없음')
        price_i = to_amount_int(data.get('price', 0), 0)
        wholesale_i = to_amount_int(data.get('wholesale_price', 0), 0)
        qty = to_int(data.get('qty', 0), 0)
        category = norm_category(data.get('category', CATEGORY_CODE[0]))
        size = norm_size(data.get('size', SIZE_CODE[0]))
        if qty < 0:
            return jsonify({'msg': TEXTS[get_lang()]['qty_nonnegative']}), 400
        status = data.get('status', '정상')
        image_path = data.get('image', '') or ''
        # 仅允许受控的相对路径
        if not is_safe_image_relpath(image_path):
            image_path = ''

    discontinued_time = None
    if status == '절판':
        discontinued_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn = connect_db()
    c = conn.cursor()
    c.execute('''
        INSERT OR IGNORE INTO items
        (barcode, name, price, price_int, wholesale_price, wholesale_price_int, qty, category, size, status, image, discontinued_time)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''',
        (barcode, name, price_i, price_i, wholesale_i, wholesale_i, qty, category, size, status, image_path, discontinued_time)
    )
    conn.commit()
    conn.close()
    return jsonify({'msg': t('ok')})

@app.route('/api/item/<barcode>', methods=['PUT'])
def edit_item(barcode):
    barcode = (barcode or '').strip()
    if not barcode:
        return jsonify({'msg': t('barcode_required')}), 400
    barcode_safe = safe_filename(barcode)

    if request.content_type and request.content_type.startswith('multipart'):
        name = request.form.get('name')
        price_i = to_amount_int(request.form.get('price', 0), 0)
        wholesale_i = to_amount_int(request.form.get('wholesale_price', 0), 0)
        qty = to_int(request.form.get('qty', 0), 0)
        category = norm_category(request.form.get('category', CATEGORY_CODE[0]))
        size = norm_size(request.form.get('size', SIZE_CODE[0]))
        if qty < 0:
            return jsonify({'msg': TEXTS[get_lang()]['qty_nonnegative']}), 400
        status = request.form.get('status', '정상')
        image = request.files.get('image')
        image_old = request.form.get('image_old', '')
        image_path = ''
        if image:
            image_path = _save_and_validate_image(image, barcode_safe)
        elif image_old and is_safe_image_relpath(image_old):
            image_path = image_old
        else:
            image_path = ''
    else:
        data = request.json or {}
        name = data.get('name')
        price_i = to_amount_int(data.get('price', 0), 0)
        wholesale_i = to_amount_int(data.get('wholesale_price', 0), 0)
        qty = to_int(data.get('qty', 0), 0)
        category = norm_category(data.get('category', CATEGORY_CODE[0]))
        size = norm_size(data.get('size', SIZE_CODE[0]))
        if qty < 0:
            return jsonify({'msg': TEXTS[get_lang()]['qty_nonnegative']}), 400
        status = data.get('status', '정상')
        image_path = data.get('image', '') or ''
        if not is_safe_image_relpath(image_path):
            image_path = ''

    conn = connect_db()
    c = conn.cursor()
    c.execute('SELECT status, discontinued_time FROM items WHERE barcode=?', (barcode,))
    row = c.fetchone()
    prev_status = row[0] if row else ''
    prev_dis_time = row[1] if row else None

    discontinued_time = prev_dis_time
    if status == '절판' and prev_status != '절판':
        discontinued_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    elif status != '절판':
        discontinued_time = None

    c.execute('''
        UPDATE items SET name=?, price=?, price_int=?, wholesale_price=?, wholesale_price_int=?, qty=?, category=?, size=?, status=?, image=?, discontinued_time=?
        WHERE barcode=?
        ''',
        (name, price_i, price_i, wholesale_i, wholesale_i, qty, category, size, status, image_path, discontinued_time, barcode)
    )
    conn.commit()
    conn.close()
    return jsonify({'msg': t('updated')})

@app.route('/api/item/<barcode>', methods=['GET'])
def get_item(barcode):
    conn = connect_db()
    c = conn.cursor()
    # 输出整数价格（旧数据自动回落）
    c.execute('''
        SELECT barcode, name,
               COALESCE(price_int, CAST(ROUND(price) AS INTEGER)) AS price,
               COALESCE(wholesale_price_int, CAST(ROUND(wholesale_price) AS INTEGER)) AS wholesale_price,
               qty, category, size, status, image, discontinued_time
        FROM items WHERE barcode=?
    ''', (barcode,))
    row = c.fetchone()
    conn.close()
    if row:
        show_status = row[7]
        if row[4] == 0 and row[7] != '절판':
            show_status = '매진'
        return jsonify({
            'barcode': row[0], 'name': row[1], 'price': int(row[2] or 0), 'wholesale_price': int(row[3] or 0), 'qty': row[4],
            'category': row[5], 'size': row[6], 'status': show_status, 'image': row[8], 'discontinued_time': row[9]
        })
    else:
        return jsonify({'error': 'Not found'}), 404

@app.route('/api/item/<barcode>', methods=['DELETE'])
def del_item(barcode):
    conn = connect_db()
    c = conn.cursor()
    c.execute('SELECT image FROM items WHERE barcode=?', (barcode,))
    row = c.fetchone()
    if row and row[0] and is_safe_image_relpath(row[0]):
        img_path = os.path.normpath(os.path.join(app.static_folder, row[0]))
        try:
            if os.path.exists(img_path):
                os.remove(img_path)
        except Exception:
            pass
    c.execute('DELETE FROM items WHERE barcode=?', (barcode,))
    conn.commit()
    conn.close()
    return jsonify({'msg': t('deleted')})

@app.route('/api/item_restore/<barcode>', methods=['POST'])
def restore_item(barcode):
    conn = connect_db()
    c = conn.cursor()
    c.execute('UPDATE items SET status="정상", discontinued_time=NULL WHERE barcode=?', (barcode,))
    conn.commit()
    conn.close()
    return jsonify({'success': True})

# ========= TOP10（原有） =========
@app.route('/api/sales/top_items')
def api_sales_top_items():
    days = int(request.args.get('days', 60) or 60)
    pay_type = request.args.get('pay_type')
    since = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d %H:%M:%S")

    conn = connect_db()
    c = conn.cursor()
    sql = "SELECT time, items FROM sales WHERE time >= ?"
    params = [since]
    if pay_type in ('cash', 'card'):
        sql += " AND pay_type=?"
        params.append(pay_type)
    c.execute(sql, params)

    agg = {}
    for _, items_json in c.fetchall():
        try:
            items = json.loads(items_json) if items_json else {}
        except Exception:
            continue
        for bc, it in items.items():
            key = (bc, it.get('name',''), it.get('category',''), it.get('size',''))
            agg[key] = agg.get(key, 0) + int(it.get('qty', 0) or 0)

    conn.close()
    top = sorted(
        [{'barcode':k[0], 'name':k[1], 'category':k[2], 'size':k[3], 'count':v} for k,v in agg.items()],
        key=lambda x: x['count'], reverse=True
    )[:10]
    return jsonify(top)

# ========= 原 get_items（兼容） =========
@app.route('/api/items', methods=['GET'])
def get_items():
    category = request.args.get('category', None)
    sort = request.args.get('sort', None)
    conn = connect_db()
    c = conn.cursor()
    base_sql = '''
        SELECT barcode, name,
               COALESCE(price_int, CAST(ROUND(price) AS INTEGER)) AS price,
               COALESCE(wholesale_price_int, CAST(ROUND(wholesale_price) AS INTEGER)) AS wholesale_price,
               qty, category, size, status, image, discontinued_time
        FROM items
    '''
    cond = []
    params = []
    if category and category in CATEGORY_CODE:
        cond.append('category=?')
        params.append(category)
    if cond:
        base_sql += ' WHERE ' + ' AND '.join(cond)
    if sort == 'price_asc':
        base_sql += ' ORDER BY category, price ASC'
    elif sort == 'price_desc':
        base_sql += ' ORDER BY category, price DESC'
    else:
        base_sql += ' ORDER BY category, CASE WHEN status="절판" THEN ifnull(discontinued_time, "9999-12-31 23:59:59") ELSE "9999-12-31 23:59:59" END DESC, id DESC'
    c.execute(base_sql, params)
    rows = c.fetchall()
    conn.close()
    onsale = []
    discontinued = []
    for r in rows:
        show_status = r[7]
        if r[4] == 0 and r[7] != '절판':
            show_status = '매진'
        item = {
            'barcode': r[0], 'name': r[1], 'price': int(r[2] or 0), 'wholesale_price': int(r[3] or 0), 'qty': r[4], 'category': r[5], 'size': r[6],
            'status': show_status, 'image': r[8], 'discontinued_time': r[9]
        }
        if r[7] == '절판':
            discontinued.append(item)
        else:
            onsale.append(item)
    return jsonify({'onsale': onsale, 'discontinued': discontinued})

# ========= 新：高性能服务器端搜索/分页（整数价格） =========
@app.route('/api/items/search', methods=['GET'])
def search_items():
    q = (request.args.get('q') or '').strip()
    category = request.args.get('category')
    sort = request.args.get('sort')
    try:
        page = max(1, int(request.args.get('page', 1) or 1))
    except Exception:
        page = 1
    try:
        page_size = max(1, min(200, int(request.args.get('page_size', 50) or 50)))
    except Exception:
        page_size = 50
    offset = (page - 1) * page_size

    where = []
    params = []
    if q:
        where.append('(barcode = ? OR name LIKE ?)')
        params += [q, f'%{q}%']
    if category in CATEGORY_CODE:
        where.append('category=?')
        params.append(category)
    where_sql = (' WHERE ' + ' AND '.join(where)) if where else ''

    order_sql = ''
    if sort == 'price_asc':
        order_sql = ' ORDER BY price ASC'
    elif sort == 'price_desc':
        order_sql = ' ORDER BY price DESC'
    else:
        order_sql = ' ORDER BY CASE WHEN status="절판" THEN ifnull(discontinued_time, "9999-12-31 23:59:59") ELSE "9999-12-31 23:59:59" END DESC, id DESC'

    conn = connect_db()
    c = conn.cursor()
    c.execute(f'SELECT COUNT(*) FROM items{where_sql}', params)
    total = c.fetchone()[0]
    c.execute(f'''
        SELECT barcode, name,
               COALESCE(price_int, CAST(ROUND(price) AS INTEGER)) AS price,
               COALESCE(wholesale_price_int, CAST(ROUND(wholesale_price) AS INTEGER)) AS wholesale_price,
               qty, category, size, status, image, discontinued_time
        FROM items
        {where_sql}
        {order_sql}
        LIMIT ? OFFSET ?
    ''', params + [page_size, offset])
    rows = c.fetchall()
    conn.close()

    items = []
    for r in rows:
        show_status = r[7]
        if r[4] == 0 and r[7] != '절판':
            show_status = '매진'
        items.append({
            'barcode': r[0], 'name': r[1], 'price': int(r[2] or 0), 'wholesale_price': int(r[3] or 0), 'qty': r[4],
            'category': r[5], 'size': r[6], 'status': show_status, 'image': r[8], 'discontinued_time': r[9]
        })
    return jsonify({'items': items, 'total': total, 'page': page, 'page_size': page_size})

@app.route('/api/item_sales/<barcode>')
def api_item_sales(barcode):
    """优先走 sale_items（整数价）；老库无明细或无 *_int 列时回退旧逻辑"""
    conn = connect_db()
    c = conn.cursor()
    try:
        # 如果有明细与 price_int
        c.execute('SELECT 1 FROM sale_items WHERE barcode=? LIMIT 1', (barcode,))
        test = c.fetchone()
        if test is not None:
            c.execute('''
              SELECT s.id, s.time, si.qty,
                     COALESCE(si.price_int, CAST(ROUND(si.price) AS INTEGER)) AS price_i,
                     COALESCE(s.total_int, CAST(ROUND(s.total) AS INTEGER)) AS order_total_i
              FROM sales s
              JOIN sale_items si ON s.id=si.sale_id
              WHERE si.barcode=?
              ORDER BY s.id DESC
            ''', (barcode,))
            rows = c.fetchall()
            conn.close()
            result = []
            for sale_id, time, qty, price_i, order_total_i in rows:
                result.append({
                    "sale_id": sale_id,
                    "time": time,
                    "qty": int(qty or 0),
                    "price": int(price_i or 0),
                    "subtotal": int((price_i or 0) * int(qty or 0)),
                    "order_total": int(order_total_i or 0),
                    "size": "",
                    "category": "",
                    "price_type": "零售"
                })
            return jsonify(result)
    except Exception:
        pass

    # 回退：遍历 JSON（把价格/总额四舍五入为整数）
    c.execute('SELECT id, time, items, total FROM sales ORDER BY id DESC')
    all_sales = []
    for sale_id, time, items_json, total in c.fetchall():
        try:
            items = json.loads(items_json)
            if barcode in items:
                price = to_amount_int(items[barcode].get('price', 0), 0)
                qty = int(items[barcode].get('qty', 0) or 0)
                all_sales.append({
                    "sale_id": sale_id,
                    "time": time,
                    "qty": qty,
                    "price": price,
                    "subtotal": price * qty,
                    "order_total": to_amount_int(total, 0),
                    "size": items[barcode].get('size', ''),
                    "category": items[barcode].get('category', ''),
                    "price_type": items[barcode].get('price_type', '零售')
                })
        except Exception:
            continue
    conn.close()
    return jsonify(all_sales)

# ======= 销售结算接口（整笔事务 + 明细；金额为整数） =======
@app.route('/api/sale', methods=['POST'])
def sale():
    data = request.json or {}
    cart = data.get('cart', {}) or {}
    total_i = to_amount_int(data.get('total', 0), 0)
    pay_type = data.get('pay_type', 'cash')
    time_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    conn = connect_db()
    c = conn.cursor()

    try:
        # 校验
        for barcode, item in cart.items():
            c.execute('SELECT qty, status FROM items WHERE barcode=?', (barcode,))
            row = c.fetchone()
            if not row:
                return jsonify({'msg': f"{t('no_product')}: {barcode}"}), 400
            if row[0] < item.get('qty', 0):
                name = item.get('name', '')
                return jsonify({'msg': f"{name}: {t('out_of_stock')}"}), 400
            if row[1] == '절판':
                name = item.get('name', '')
                return jsonify({'msg': f"{name}: {t('discontinued')}"}), 400

        c.execute('BEGIN IMMEDIATE')

        # INSERT sales（写 total_int，total 也写整数以兼容旧字段）
        c.execute('INSERT INTO sales (time, items, total, total_int, refunded, pay_type) VALUES (?, ?, ?, ?, ?, ?)',
                  (time_str, json.dumps(cart, ensure_ascii=False), total_i, total_i, 0, pay_type))
        sale_id = c.lastrowid

        # UPDATE items & INSERT stock_log & INSERT sale_items（写 price_int）
        for barcode, item in cart.items():
            qty = int(item.get('qty', 0) or 0)
            price_i = to_amount_int(item.get('price', 0), 0)
            name = str(item.get('name', '') or '')
            category = str(item.get('category', '') or '')
            size = str(item.get('size', '') or '')

            c.execute('UPDATE items SET qty = qty - ? WHERE barcode = ?', (qty, barcode))
            c.execute('INSERT INTO stock_log (time, barcode, change, type) VALUES (?, ?, ?, ?)',
                      (time_str, barcode, -qty, 'sale'))
            c.execute('INSERT INTO sale_items (sale_id, barcode, name, category, size, qty, price, price_int) VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
                      (sale_id, barcode, name, category, size, qty, price_i, price_i))

        conn.commit()
        return jsonify({'msg': t('ok'), 'sale_id': sale_id})
    except Exception as e:
        try:
            conn.rollback()
        except Exception:
            pass
        return jsonify({'msg': f"{t('db_error')}: {e}"}), 500
    finally:
        conn.close()

# ========= 销售分页（支持 pay_type 过滤；总额为整数） =========
@app.route('/api/sales')
def api_sales():
    try:
        page = max(1, int(request.args.get('page', 1) or 1))
    except Exception:
        page = 1
    try:
        page_size = max(1, min(200, int(request.args.get('page_size', 20) or 20)))
    except Exception:
        page_size = 20

    pay_type = request.args.get('pay_type')  # 'cash' / 'card' / None
    offset = (page - 1) * page_size

    conn = connect_db()
    c = conn.cursor()

    where = []
    params = []
    if pay_type in ('cash', 'card'):
        where.append('pay_type=?')
        params.append(pay_type)
    where_sql = (' WHERE ' + ' AND '.join(where)) if where else ''

    c.execute(f'SELECT COUNT(*) FROM sales{where_sql}', params)
    total = c.fetchone()[0]

    c.execute(f'''
        SELECT id, time, items,
               COALESCE(total_int, CAST(ROUND(total) AS INTEGER)) AS total_i,
               refunded, pay_type 
        FROM sales
        {where_sql}
        ORDER BY id DESC LIMIT ? OFFSET ?
    ''', params + [page_size, offset])

    sales = []
    for sale_id, time, items_json, total_i, refunded, ptype in c.fetchall():
        try:
            items = json.loads(items_json)
        except Exception:
            items = {}
        sales.append({
            'id': sale_id,
            'time': time,
            'items': items,
            'total': int(total_i or 0),
            'refunded': refunded,
            'pay_type': ptype or 'cash'
        })
    conn.close()
    return jsonify({'sales': sales, 'total': total})

# ========= 批量删除（含库存回补 & 事务） =========
@app.route('/api/sale/delete', methods=['POST'])
def api_delete_sales():
    data = request.get_json(force=True) or {}
    ids = data.get('ids', []) or []
    reason = data.get('reason', 'mistake')
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    conn = connect_db()
    c = conn.cursor()

    deleted = 0
    failed = 0
    not_found = 0
    restocked = 0
    skipped_already_refunded = 0

    for sale_id in ids:
        c.execute('SELECT items, COALESCE(total_int, CAST(ROUND(total) AS INTEGER)) AS amount, refunded FROM sales WHERE id=?', (sale_id,))
        row = c.fetchone()
        if not row:
            not_found += 1
            continue

        items_json, amount, refunded = row
        try:
            c.execute('BEGIN IMMEDIATE')
            items = json.loads(items_json) if items_json else {}

            if not refunded:
                for bc, it in items.items():
                    qty = int(it.get('qty', 0) or 0)
                    if qty <= 0:
                        continue
                    c.execute('UPDATE items SET qty = qty + ? WHERE barcode = ?', (qty, bc))
                    c.execute('INSERT INTO stock_log (time, barcode, change, type) VALUES (?, ?, ?, ?)',
                              (now, bc, qty, 'delete_revert'))
                    restocked += 1
            else:
                skipped_already_refunded += 1

            c.execute('DELETE FROM sales WHERE id=?', (sale_id,))
            c.execute('INSERT INTO refund_log (sale_id, time, reason, detail, amount) VALUES (?, ?, ?, ?, ?)',
                      (sale_id, now, 'delete', reason, amount))
            conn.commit()
            deleted += 1
        except Exception:
            conn.rollback()
            failed += 1

    conn.close()
    return jsonify({'success': True, 'deleted': deleted, 'failed': failed, 'not_found': not_found, 'restocked': restocked, 'skipped_already_refunded': skipped_already_refunded})

# ========= 退款（含库存回补 & 防重复） =========
@app.route('/api/sale/refund', methods=['POST'])
def api_refund_sale():
    data = request.get_json(force=True) or {}
    ids = data.get('ids', []) or []
    reason = data.get('reason', 'refund')
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    conn = connect_db()
    c = conn.cursor()

    updated = 0
    failed = 0
    skipped_already_refunded = 0
    restocked = 0

    for sale_id in ids:
        c.execute('SELECT items, COALESCE(total_int, CAST(ROUND(total) AS INTEGER)) AS amount, refunded FROM sales WHERE id=?', (sale_id,))
        row = c.fetchone()
        if not row:
            continue

        items_json, amount, refunded = row
        if refunded:
            skipped_already_refunded += 1
            continue

        try:
            c.execute('BEGIN IMMEDIATE')
            items = json.loads(items_json) if items_json else {}
            for bc, it in items.items():
                qty = int(it.get('qty', 0) or 0)
                if qty <= 0:
                    continue
                c.execute('UPDATE items SET qty = qty + ? WHERE barcode = ?', (qty, bc))
                c.execute('INSERT INTO stock_log (time, barcode, change, type) VALUES (?, ?, ?, ?)',
                          (now, bc, qty, 'refund'))
                restocked += 1

            c.execute('UPDATE sales SET refunded=1 WHERE id=?', (sale_id,))
            c.execute('INSERT INTO refund_log (sale_id, time, reason, detail, amount) VALUES (?, ?, ?, ?, ?)',
                      (sale_id, now, reason, '', amount))
            conn.commit()
            updated += 1
        except Exception:
            conn.rollback()
            failed += 1

    conn.close()
    return jsonify({'success': True, 'updated': updated, 'failed': failed, 'restocked': restocked, 'skipped_already_refunded': skipped_already_refunded})

@app.route('/api/sales/refund_stats')
def api_refund_stats():
    conn = connect_db()
    c = conn.cursor()
    c.execute("SELECT reason, count(*), sum(amount) FROM refund_log GROUP BY reason")
    result = []
    for reason, cnt, total in c.fetchall():
        result.append({'reason': reason, 'count': cnt, 'amount': total or 0})
    conn.close()
    return jsonify(result)

# ========= 销售统计（按整数总额） =========
@app.route('/api/sales/stats')
def api_sales_stats():
    group = request.args.get('group', 'day')
    start = request.args.get('start')
    end = request.args.get('end')
    pay_type = request.args.get('pay_type')

    conn = connect_db()
    c = conn.cursor()
    query = '''
        SELECT time, COALESCE(total_int, CAST(ROUND(total) AS INTEGER)) AS total_i, pay_type
        FROM sales
    '''
    cond = []
    params = []

    if start and end:
        cond.append("time BETWEEN ? AND ?")
        params += [start + " 00:00:00", end + " 23:59:59"]
    if pay_type in ('cash', 'card'):
        cond.append("pay_type=?")
        params.append(pay_type)

    if cond:
        query += " WHERE " + " AND ".join(cond)

    c.execute(query, params)
    rows = c.fetchall()
    conn.close()

    if not rows:
        return jsonify({'labels': [], 'sales': [], 'orders': []})

    df = pd.DataFrame(rows, columns=['time', 'total', 'pay_type'])
    df['time'] = pd.to_datetime(df['time'])
    if group == 'month':
        df['label'] = df['time'].dt.strftime('%Y-%m')
    elif group == 'year':
        df['label'] = df['time'].dt.strftime('%Y')
    elif group == 'week':
        df['label'] = df['time'].dt.strftime('%Y-%W')
    else:
        df['label'] = df['time'].dt.strftime('%Y-%m-%d')

    stats = df.groupby('label').agg({'total': 'sum', 'time': 'count'}).reset_index()
    stats = stats.sort_values('label')
    return jsonify({
        'labels': stats['label'].tolist(),
        'sales': [int(x) for x in stats['total'].tolist()],
        'orders': [int(x) for x in stats['time'].tolist()]
    })

# ========= 热力图：星期 × 小时（按整数总额） =========
@app.route('/api/sales/heatmap_hour_weekday')
def api_heatmap_hour_weekday():
    start = request.args.get('start')
    end = request.args.get('end')
    pay_type = request.args.get('pay_type')
    metric = request.args.get('metric', 'orders')

    conn = connect_db()
    c = conn.cursor()
    query = '''
        SELECT time, items, COALESCE(total_int, CAST(ROUND(total) AS INTEGER)) AS total_i, pay_type
        FROM sales
    '''
    cond = []
    params = []

    if start and end:
        cond.append("time BETWEEN ? AND ?")
        params += [start + " 00:00:00", end + " 23:59:59"]
    if pay_type in ('cash', 'card'):
        cond.append("pay_type=?")
        params.append(pay_type)
    if cond:
        query += " WHERE " + " AND ".join(cond)

    c.execute(query, params)
    rows = c.fetchall()
    conn.close()

    matrix = [[0 for _ in range(24)] for _ in range(7)]
    sum_orders = 0
    sum_sales = 0
    sum_items = 0

    for t, items_json, total_i, _ in rows:
        try:
            dt = datetime.strptime(t, "%Y-%m-%d %H:%M:%S")
        except Exception:
            try:
                dt = pd.to_datetime(t).to_pydatetime()
            except Exception:
                continue
        weekday = dt.weekday()
        hour = dt.hour

        sum_orders += 1
        sum_sales += int(total_i or 0)
        count_items = 0
        try:
            items = json.loads(items_json) if items_json else {}
            for _, it in items.items():
                count_items += int(it.get('qty', 0) or 0)
        except Exception:
            pass
        sum_items += count_items

        if metric == 'sales':
            matrix[weekday][hour] += int(total_i or 0)
        elif metric == 'items':
            matrix[weekday][hour] += count_items
        else:
            matrix[weekday][hour] += 1

    # 本地化星期标签
    lang = get_lang()
    week_labels = [TEXTS[lang]['mon'], TEXTS[lang]['tue'], TEXTS[lang]['wed'],
                   TEXTS[lang]['thu'], TEXTS[lang]['fri'], TEXTS[lang]['sat'], TEXTS[lang]['sun']]

    return jsonify({
        'week_labels': week_labels,
        'hours': list(range(24)),
        'matrix': matrix,
        'sum_orders': sum_orders,
        'sum_sales': int(sum_sales),
        'sum_items': sum_items
    })

#-------------------- 手动出入库------------------
@app.route('/api/stockio', methods=['POST'])
def api_stockio():
    data = request.get_json(force=True) or {}
    barcode = (data.get('barcode') or '').strip()
    change = to_int(data.get('change'), 0)
    io_type = data.get('type', 'in')  # in / out

    if not barcode or change <= 0:
        return jsonify({'msg': t('invalid_params')}), 400

    delta = change if io_type == 'in' else -change

    conn = connect_db()
    c = conn.cursor()
    c.execute('SELECT qty FROM items WHERE barcode=?', (barcode,))
    row = c.fetchone()
    if not row:
        conn.close()
        return jsonify({'msg': t('no_product')}), 404

    old_qty = int(row[0] or 0)
    new_qty = old_qty + delta
    if new_qty < 0:
        conn.close()
        return jsonify({'msg': t('out_of_stock')}), 400

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        c.execute('BEGIN IMMEDIATE')
        c.execute('UPDATE items SET qty=? WHERE barcode=?', (new_qty, barcode))
        c.execute('INSERT INTO stock_log (time, barcode, change, type) VALUES (?, ?, ?, ?)',
                  (now, barcode, delta, io_type))
        conn.commit()
    except Exception:
        conn.rollback()
        conn.close()
        return jsonify({'msg': t('db_error')}), 500

    conn.close()
    return jsonify({'msg': t('ok'), 'old_qty': old_qty, 'new_qty': new_qty})

# ===================== 收据详情 & 打印 =====================
@app.route('/receipt/<int:sale_id>')
def receipt(sale_id):
    lang = get_lang()
    conn = connect_db()
    c = conn.cursor()
    c.execute('SELECT time, items, COALESCE(total_int, CAST(ROUND(total) AS INTEGER)) AS total_i, pay_type FROM sales WHERE id=?', (sale_id,))
    row = c.fetchone()
    conn.close()
    if not row:
        return f'No such sale_id: {sale_id}', 404
    time, items_json, subtotal_i, pay_type = row
    items = json.loads(items_json) if items_json else {}
    # VAT 仅前端显示，但这里也按整数显示
    vat = int(round(subtotal_i * 0.10)) if pay_type == 'card' else 0
    total_with_vat = (subtotal_i + vat) if pay_type == 'card' else subtotal_i
    return render_template(
        'receipt.html',
        sale_id=sale_id,
        time=time,
        items=items,
        subtotal=subtotal_i,
        vat=vat,
        total=total_with_vat,
        lang=lang,
        texts=TEXTS[lang],
        pay_type=pay_type
    )

# （可选）ZPL 打印（保持不变）
from html2image import Html2Image
from PIL import Image, ImageOps
from PIL import Image as PILImage  # for type hints

def image_to_zpl(image_path, image_name="RECEIPT.GRF"):
    img = Image.open(image_path).convert("L")
    threshold = 200
    img = img.point(lambda x: 255 if x > threshold else 0, mode='1')
    img = ImageOps.invert(img.convert('L')).convert('1')
    w, h = img.size
    row_bytes = (w + 7) // 8
    total_bytes = row_bytes * h
    data = img.tobytes()
    zpl_data = ""
    idx = 0
    for _ in range(h):
        row = ""
        for _ in range(row_bytes):
            byte = data[idx] if idx < len(data) else 0
            row += "{:02X}".format(byte)
            idx += 1
        zpl_data += row + "\n"
    header = f"~DG{image_name},{total_bytes},{row_bytes},\n"
    return header + zpl_data

def _estimate_receipt_height(sale_id: int) -> int:
    CM_TO_PX = 37.7952755906
    BASE = 1000
    PER_ROW = 90
    EXTRA_BOTTOM = int(3 * CM_TO_PX) + 48
    VAT_ROW = 44
    SAFETY = 150

    n_rows = 0
    extra_wrap_px = 0
    is_card = False
    try:
        conn = connect_db()
        c = conn.cursor()
        c.execute('SELECT items, pay_type FROM sales WHERE id=?', (sale_id,))
        row = c.fetchone()
        conn.close()
        if row and row[0]:
            items = json.loads(row[0])
            n_rows = len(items)
            for it in items.values():
                name_len = len(str(it.get('name','')))
                if name_len > 16:
                    extra_lines = math.ceil((name_len-16)/16.0)
                    extra_wrap_px += extra_lines * 20
        if row and row[1] == 'card':
            is_card = True
    except Exception:
        return 1500

    height = BASE + n_rows*PER_ROW + extra_wrap_px + (VAT_ROW if is_card else 0) + EXTRA_BOTTOM + SAFETY
    return max(900, min(int(height), 6000))

@app.route('/api/print_receipt/<int:sale_id>', methods=['POST'])
def print_receipt(sale_id):
    from flask import jsonify

    H = _estimate_receipt_height(sale_id)
    W = 624

    tmp_img_path = None
    try:
        base_url = (request.host_url or "http://127.0.0.1:5000").rstrip('/')
        url = f"{base_url}/receipt/{sale_id}?for_print=1"
        hti = Html2Image()

        with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmpf:
            tmp_img_path = tmpf.name

        tmp_save_name = f"receipt_{sale_id}.png"
        hti.screenshot(url=url, save_as=tmp_save_name, size=(W, H))
        shutil.move(tmp_save_name, tmp_img_path)
    except Exception as e:
        try:
            if tmp_img_path and os.path.exists(tmp_img_path):
                os.remove(tmp_img_path)
        except Exception:
            pass
        return jsonify({'msg': 'Image render error: ' + str(e)}), 500

    hPrinter = None
    try:
        try:
            import win32print
        except Exception as e:
            if tmp_img_path and os.path.exists(tmp_img_path):
                os.remove(tmp_img_path)
            return jsonify({'msg': 'Print error: win32print not available: ' + str(e)}), 500

        zpl_img = image_to_zpl(tmp_img_path)
        zpl = zpl_img + "^XA\n^FO0,0^XGRECEIPT.GRF,1,1^FS\n^XZ\n"

        printer_name = "ZDesigner ZD230-203dpi ZPL"  # 硬编码按你要求保留
        hPrinter = win32print.OpenPrinter(printer_name)
        win32print.StartDocPrinter(hPrinter, 1, ("Receipt", None, "RAW"))
        win32print.StartPagePrinter(hPrinter)
        win32print.WritePrinter(hPrinter, zpl.encode("ascii"))
        win32print.EndPagePrinter(hPrinter)
        win32print.EndDocPrinter(hPrinter)
        return jsonify({'msg': 'ok'})
    except Exception as e:
        return jsonify({'msg': 'Print error: ' + str(e)}), 500
    finally:
        try:
            if hPrinter:
                win32print.ClosePrinter(hPrinter)
        except Exception:
            pass
        try:
            if tmp_img_path and os.path.exists(tmp_img_path):
                os.remove(tmp_img_path)
        except Exception:
            pass

if __name__ == '__main__':
    init_db()
    port = int(os.environ.get('TREASUREPOS_PORT') or os.environ.get('PORT') or '0')  # 0=自动分配
    app.run(host='127.0.0.1', port=port, debug=False, use_reloader=False)
