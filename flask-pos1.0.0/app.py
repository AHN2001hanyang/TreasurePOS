from flask import Flask, render_template, request, jsonify, send_file, redirect, url_for
from flask_cors import CORS
import sqlite3
from datetime import datetime
import json
import pandas as pd
import os
import sys

# ------ 关键补丁：自动识别资源路径 ------
if getattr(sys, 'frozen', False):
    base_path = sys._MEIPASS
else:
    base_path = os.path.abspath(os.path.dirname(__file__))

template_dir = os.path.join(base_path, 'templates')
static_dir   = os.path.join(base_path, 'static')

app = Flask(
    __name__,
    template_folder=template_dir,
    static_folder=static_dir
)
CORS(app)

UPLOAD_FOLDER = os.path.join(base_path, 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def init_db():
    conn = sqlite3.connect('inventory.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            barcode TEXT UNIQUE,
            name TEXT,
            price REAL DEFAULT 0,
            qty INTEGER DEFAULT 0
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS sales (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            time TEXT,
            items TEXT,
            total REAL
        )
    ''')
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
            detail TEXT
        )
    ''')
    conn.commit()
    conn.close()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/manage')
def manage():
    return render_template('manage.html')

@app.route('/sales')
def sales():
    return render_template('sales.html')

@app.route('/stocklog')
def stocklog():
    return render_template('stocklog.html')

@app.route('/api/item', methods=['POST'])
def add_item():
    data = request.json
    barcode = data.get('barcode')
    name = data.get('name', 'Unnamed Product')
    price = float(data.get('price', 0))
    qty = int(data.get('qty', 0))
    conn = sqlite3.connect('inventory.db')
    c = conn.cursor()
    c.execute('INSERT OR IGNORE INTO items (barcode, name, price, qty) VALUES (?, ?, ?, ?)',
              (barcode, name, price, qty))
    conn.commit()
    conn.close()
    return jsonify({'msg': 'ok'})

@app.route('/api/item/<barcode>', methods=['GET'])
def get_item(barcode):
    conn = sqlite3.connect('inventory.db')
    c = conn.cursor()
    c.execute('SELECT barcode, name, price, qty FROM items WHERE barcode=?', (barcode,))
    row = c.fetchone()
    conn.close()
    if row:
        return jsonify({'barcode': row[0], 'name': row[1], 'price': row[2], 'qty': row[3]})
    else:
        return jsonify({'error': 'Not found'}), 404

@app.route('/api/item/<barcode>', methods=['PUT'])
def edit_item(barcode):
    data = request.json
    name = data.get('name')
    price = float(data.get('price', 0))
    qty = int(data.get('qty', 0))
    conn = sqlite3.connect('inventory.db')
    c = conn.cursor()
    c.execute('UPDATE items SET name=?, price=?, qty=? WHERE barcode=?',
              (name, price, qty, barcode))
    conn.commit()
    conn.close()
    return jsonify({'msg': 'updated'})

@app.route('/api/item/<barcode>', methods=['DELETE'])
def del_item(barcode):
    conn = sqlite3.connect('inventory.db')
    c = conn.cursor()
    c.execute('DELETE FROM items WHERE barcode=?', (barcode,))
    conn.commit()
    conn.close()
    return jsonify({'msg': 'deleted'})

@app.route('/api/items', methods=['GET'])
def get_items():
    conn = sqlite3.connect('inventory.db')
    c = conn.cursor()
    c.execute('SELECT barcode, name, price, qty FROM items')
    rows = c.fetchall()
    conn.close()
    return jsonify([
        {'barcode': r[0], 'name': r[1], 'price': r[2], 'qty': r[3]}
        for r in rows
    ])

@app.route('/api/sale', methods=['POST'])
def sale():
    data = request.json
    cart = data.get('cart', {})
    total = float(data.get('total', 0))
    time_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    conn = sqlite3.connect('inventory.db')
    c = conn.cursor()
    c.execute('INSERT INTO sales (time, items, total) VALUES (?, ?, ?)', 
        (time_str, json.dumps(cart, ensure_ascii=False), total))
    sale_id = c.lastrowid

    for barcode, item in cart.items():
        c.execute('UPDATE items SET qty = qty - ? WHERE barcode = ?', (item['qty'], barcode))
        c.execute('INSERT INTO stock_log (time, barcode, change, type) VALUES (?, ?, ?, ?)', 
            (time_str, barcode, -item['qty'], 'sale'))
    conn.commit()
    conn.close()
    return jsonify({'msg': 'ok', 'sale_id': sale_id})

@app.route('/api/sales', methods=['GET'])
def get_sales():
    try:
        page = int(request.args.get('page', 1))
        page_size = int(request.args.get('page_size', 20))
    except:
        page = 1
        page_size = 20
    offset = (page - 1) * page_size

    conn = sqlite3.connect('inventory.db')
    c = conn.cursor()
    c.execute('SELECT COUNT(*) FROM sales')
    total = c.fetchone()[0]

    c.execute('SELECT id, time, items, total FROM sales ORDER BY time DESC LIMIT ? OFFSET ?', (page_size, offset))
    rows = c.fetchall()
    conn.close()
    result = []
    for row in rows:
        result.append({
            'id': row[0],
            'time': row[1],
            'items': json.loads(row[2]),
            'total': row[3]
        })
    return jsonify({
        'sales': result,
        'total': total,
        'page': page,
        'page_size': page_size
    })

@app.route('/api/sale/delete', methods=['POST'])
def delete_sale():
    """
    批量删除销售记录，原因为refund时写入refund_log，为mistake时不写入
    - 只要有一笔负库存就整体失败
    - 返回操作统计，接口结构统一
    """
    data = request.json
    ids = data.get('ids', [])
    # 强制保证全部是int类型
    ids = [int(i) for i in ids if str(i).isdigit()]
    reason = data.get('reason', 'refund')
    time_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    deleted, not_found, failed, failed_ids = 0, 0, 0, []
    conn = sqlite3.connect('inventory.db')
    try:
        conn.execute('BEGIN')
        c = conn.cursor()
        # 整体检查库存
        for sale_id in ids:
            c.execute('SELECT items FROM sales WHERE id=?', (sale_id,))
            row = c.fetchone()
            if not row:
                not_found += 1
                continue
            items = json.loads(row[0])
            for bc, item in items.items():
                c.execute('SELECT qty FROM items WHERE barcode=?', (bc,))
                qrow = c.fetchone()
                if not qrow:
                    failed += 1
                    failed_ids.append(sale_id)
                    break
                current_qty = qrow[0]
                # 只要任意商品会导致负库存，则全局失败
                if current_qty + item['qty'] < 0:
                    failed += 1
                    failed_ids.append(sale_id)
                    break
        if failed > 0:
            conn.rollback()
            return jsonify({'success': False, 'msg': '删除失败：存在负库存或条码不存在', 'deleted': deleted, 'not_found': not_found, 'failed': failed, 'failed_ids': failed_ids, 'code': 2}), 400

        # 执行实际删除
        for sale_id in ids:
            c.execute('SELECT items FROM sales WHERE id=?', (sale_id,))
            row = c.fetchone()
            if not row:
                continue
            items = json.loads(row[0])
            for bc, item in items.items():
                c.execute('UPDATE items SET qty = qty + ? WHERE barcode = ?', (item['qty'], bc))
                c.execute('INSERT INTO stock_log (time, barcode, change, type) VALUES (?, ?, ?, ?)',
                        (time_str, bc, item['qty'], 'restore' if reason == 'mistake' else 'refund'))
            c.execute('DELETE FROM sales WHERE id=?', (sale_id,))
            # 仅退款才写入refund_log
            if reason != 'mistake':
                c.execute('INSERT INTO refund_log (sale_id, time, reason, detail) VALUES (?, ?, ?, ?)',
                        (sale_id, time_str, reason, json.dumps(items, ensure_ascii=False)))
            deleted += 1
        conn.commit()
        return jsonify({
            'success': True,
            'msg': "ok",
            'deleted': deleted,
            'not_found': not_found,
            'failed': failed,
            'failed_ids': failed_ids,
            'code': 0
        })
    except Exception as e:
        conn.rollback()
        return jsonify({'success': False, 'msg': str(e), 'deleted': deleted, 'not_found': not_found, 'failed': failed, 'failed_ids': failed_ids, 'code': 1}), 500
    finally:
        conn.close()

@app.route('/api/sales/stats')
def sales_stats():
    agg_type = request.args.get('type', 'day')
    conn = sqlite3.connect('inventory.db')
    c = conn.cursor()
    if agg_type == 'month':
        c.execute("SELECT substr(time,1,7) as ym, SUM(total) FROM sales GROUP BY ym ORDER BY ym")
    elif agg_type == 'year':
        c.execute("SELECT substr(time,1,4) as y, SUM(total) FROM sales GROUP BY y ORDER BY y")
    else:
        c.execute("SELECT substr(time,1,10) as d, SUM(total) FROM sales GROUP BY d ORDER BY d")
    rows = c.fetchall()
    conn.close()
    return jsonify({'labels': [r[0] for r in rows], 'values': [r[1] for r in rows]})

@app.route('/api/stocklog', methods=['GET'])
def stock_log():
    conn = sqlite3.connect('inventory.db')
    c = conn.cursor()
    c.execute('SELECT time, barcode, change, type FROM stock_log ORDER BY time DESC')
    rows = c.fetchall()
    conn.close()
    result = []
    for row in rows:
        result.append({
            'time': row[0],
            'barcode': row[1],
            'change': row[2],
            'type': row[3]
        })
    return jsonify(result)

@app.route('/receipt/<sale_id>')
def receipt(sale_id):
    conn = sqlite3.connect('inventory.db')
    c = conn.cursor()
    c.execute('SELECT time, items, total FROM sales WHERE id=?', (sale_id,))
    row = c.fetchone()
    conn.close()
    if not row:
        return "Not found", 404
    items = json.loads(row[1])
    return render_template('receipt.html', time=row[0], items=items, total=row[2], sale_id=sale_id)

@app.route('/export/sales')
def export_sales():
    conn = sqlite3.connect('inventory.db')
    c = conn.cursor()
    c.execute('SELECT time, items, total FROM sales ORDER BY time DESC')
    rows = c.fetchall()
    conn.close()
    data = []
    for row in rows:
        items = json.loads(row[1])
        for bc, item in items.items():
            data.append({
                'Time': row[0],
                'Barcode': bc,
                'Product': item['name'],
                'Quantity': item['qty'],
                'Price': item['price'],
                'Subtotal': item['qty'] * item['price'],
                'Total': row[2]
            })
    df = pd.DataFrame(data)
    outpath = 'sales_export.xlsx'
    df.to_excel(outpath, index=False)
    return send_file(outpath, as_attachment=True)

@app.route('/export/stocklog')
def export_stocklog():
    conn = sqlite3.connect('inventory.db')
    c = conn.cursor()
    c.execute('SELECT time, barcode, change, type FROM stock_log ORDER BY time DESC')
    rows = c.fetchall()
    conn.close()
    df = pd.DataFrame(rows, columns=['Time', 'Barcode', 'Change', 'Type'])
    outpath = 'stocklog_export.xlsx'
    df.to_excel(outpath, index=False)
    return send_file(outpath, as_attachment=True)

@app.route('/export/items')
def export_items():
    conn = sqlite3.connect('inventory.db')
    c = conn.cursor()
    c.execute('SELECT barcode, name, price, qty FROM items')
    rows = c.fetchall()
    conn.close()
    df = pd.DataFrame(rows, columns=['Barcode', 'Product', 'Price', 'Stock'])
    outpath = 'items_export.xlsx'
    df.to_excel(outpath, index=False)
    return send_file(outpath, as_attachment=True)

@app.route('/import/items', methods=['POST'])
def import_items():
    file = request.files.get('file')
    if not file:
        return "No file uploaded!", 400
    path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    file.save(path)
    df = pd.read_excel(path)
    conn = sqlite3.connect('inventory.db')
    c = conn.cursor()
    for _, row in df.iterrows():
        c.execute('INSERT OR REPLACE INTO items (barcode, name, price, qty) VALUES (?, ?, ?, ?)',
                  (str(row['Barcode']), str(row['Product']), float(row['Price']), int(row['Stock'])))
    conn.commit()
    conn.close()
    os.remove(path)
    return redirect(url_for('manage'))

@app.route('/api/print_receipt/<int:sale_id>', methods=['POST'])
def print_receipt(sale_id):
    import win32print
    conn = sqlite3.connect('inventory.db')
    c = conn.cursor()
    c.execute('SELECT time, items, total FROM sales WHERE id=?', (sale_id,))
    row = c.fetchone()
    conn.close()
    if not row:
        return jsonify({'msg': 'Not found'}), 404

    items = json.loads(row[1])
    total = row[2]
    time_str = row[0]

    logo_height = 300
    y = logo_height + 20
    line_height = 36

    zpl_lines = [
        "^XA",
        "^PW600",
        "^CI28",
        "^FO80,10^XGE:TREASURE.GRF,3,3^FS",
        f"^FO10,{y}^GB580,3,3^FS",
        f"^FO10,{y+20}^A0N,28,28^FDOrder No:^FS^FO180,{y+20}^A0N,28,28^FD{sale_id}^FS",
        f"^FO10,{y+58}^A0N,28,28^FDDate:^FS^FO90,{y+58}^A0N,28,28^FD{time_str}^FS",
        f"^FO10,{y+90}^GB580,2,2^FS",
        f"^FO10,{y+110}^A0N,26,26^FDProduct^FS",
        f"^FO180,{y+110}^A0N,26,26^FDQty^FS",
        f"^FO270,{y+110}^A0N,26,26^FDPrice^FS",
        f"^FO450,{y+110}^A0N,26,26^FDSubtotal^FS"
    ]

    cur_y = y + 140
    for bc, item in items.items():
        pname = (item['name'][:12] + '..') if len(item['name']) > 14 else item['name']
        qty = item['qty']
        price = "{:.2f}".format(item['price'])
        subtotal = "{:.2f}".format(item['qty'] * item['price'])
        zpl_lines.append(f"^FO10,{cur_y}^A0N,26,26^FD{pname}^FS")
        zpl_lines.append(f"^FO180,{cur_y}^A0N,26,26^FD{qty}^FS")
        zpl_lines.append(f"^FO270,{cur_y}^A0N,26,26^FD{price}^FS")
        zpl_lines.append(f"^FO450,{cur_y}^A0N,26,26^FD{subtotal}^FS")
        cur_y += line_height

    cur_y += 10
    zpl_lines.append(f"^FO10,{cur_y}^GB580,2,2^FS")
    cur_y += 30
    zpl_lines.append(f"^FO10,{cur_y}^A0N,32,32^FDTotal:      {total:.2f}^FS")
    cur_y += 40
    zpl_lines.append(f"^FO10,{cur_y}^A0N,22,22^FDThank you for shopping!^FS")
    cur_y += 30
    zpl_lines.append(f"^FO10,{cur_y}^A0N,26,26^FDContact: 010-7757-9705^FS")
    cur_y += 25
    zpl_lines.append(f"^FO10,{cur_y}^A0N,26,26^FDSeoul, DDP 3F,02^FS")
    cur_y += 200
    zpl_lines.append("^XZ")

    zpl_lines.insert(1, f"^LL{cur_y+30}")

    zpl = '\n'.join(zpl_lines)

    try:
        printer_name = win32print.GetDefaultPrinter()
        hPrinter = win32print.OpenPrinter(printer_name)
        job = win32print.StartDocPrinter(hPrinter, 1, ("Receipt", None, "RAW"))
        win32print.StartPagePrinter(hPrinter)
        win32print.WritePrinter(hPrinter, zpl.encode("ascii"))
        win32print.EndPagePrinter(hPrinter)
        win32print.EndDocPrinter(hPrinter)
        win32print.ClosePrinter(hPrinter)
        return jsonify({'msg': 'ok'})
    except Exception as e:
        return jsonify({'msg': 'Print error: '+str(e)}), 500

@app.route('/api/stockio', methods=['POST'])
def stockio():
    data = request.json
    barcode = data.get('barcode')
    change = int(data.get('change', 0))
    io_type = data.get('type')  # 'in' or 'out'
    if not barcode or not change or io_type not in ('in', 'out'):
        return jsonify({'msg': 'Parameter error'}), 400
    time_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn = sqlite3.connect('inventory.db')
    c = conn.cursor()
    c.execute('UPDATE items SET qty = qty + ? WHERE barcode = ?', (change if io_type == 'in' else -change, barcode))
    c.execute('INSERT INTO stock_log (time, barcode, change, type) VALUES (?, ?, ?, ?)',
              (time_str, barcode, change if io_type == 'in' else -change, io_type))
    conn.commit()
    conn.close()
    return jsonify({'msg': 'ok'})

@app.route('/stockio')
def stockio_page():
    return render_template('stockio.html')

@app.route('/settings')
def settings():
    return render_template('settings.html')

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
