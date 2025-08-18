# TreasurePOS (Flask + Desktop WebView)

Local‑first POS for small shops. Scan or type barcodes, switch retail/wholesale price, sell with cash or card, keep stock logs, view sales analytics, and print Zebra receipts. UI available in **한국어 / 中文 / English**.

---

## ✨ Features
- Fast barcode or manual entry with **retail / wholesale** price toggle
- Product CRUD with **Excel import/export**
- **Sales history** (cash / card), refunds, and **stock in/out logs**
- **Analytics**: daily/weekly/monthly, heatmap (weekday × hour)
- **Multilingual UI** (KO/ZH/EN) and responsive desktop window (pywebview)
- **Thermal printing (Zebra)**: `receipt.html` → PNG → ZPL → Windows RAW print

## Project Structure
```
/app.py           # Flask backend (routes, DB, Playwright→ZPL printing)
/main.py          # Desktop wrapper (pywebview + health check)
/templates/
  index.html      # POS (sales) home
  manage.html     # Product management (Excel import/export)
  sales.html      # Sales analytics & charts
  stocklog.html   # Stock in/out/adjustment logs
  settings.html   # Settings (language selection)
  receipt.html    # Receipt layout (printed)
/static/          # Images, fonts, styles
/README.md
```

## Requirements
- **Python 3.10+** (Windows 10/11 recommended for printing)
- Dependencies (install below): `Flask`, `flask-cors`, `pandas`, `openpyxl`, `Pillow`, **`playwright`**, **`pywin32`** (Windows printing only), `pywebview`

```bash
pip install -r requirements.txt
pip install playwright pywin32 pywebview
python -m playwright install chromium   # run once per machine
```

> Tip: If VS Code shows “_Pylance: cannot resolve import 'playwright.sync_api'_”, you likely need to install the package in the **active interpreter** and then restart VS Code.

## Run (development)
```bash
# Flask only
python app.py

# Desktop window (recommended for non‑technical users)
python main.py
```
`main.py` launches the Flask server in the background and opens a local window with **pywebview**.

## Data Location
The app stores the SQLite database and uploads in a **writable run directory**, and will **migrate legacy files** automatically on first run.

Default locations (unless `TREASUREPOS_DATA_DIR` is set):
- **Windows:** `%LOCALAPPDATA%\TreasurePOS`
- **macOS:** `~/Library/Application Support/TreasurePOS`
- **Linux:** `~/.local/share/treasurepos`

You can override with:
```bash
# Windows (PowerShell)
$env:TREASUREPOS_DATA_DIR="D:\TreasurePOS\data"
# or classic CMD
set TREASUREPOS_DATA_DIR=D:\TreasurePOS\data
```

## Printing Pipeline (recommended)
1. **Render only the `.receipt` element** of `receipt.html` with **Playwright** at a fixed width (default **624 px**, ≈79 mm on 203 dpi printers).  
   The code waits for network idle and fonts, then screenshots the element to PNG.
2. **Convert PNG → ZPL graphics** and emit ZPL header with:
   - `^PW{w}` → print width in printer dots (taken from the PNG width)
   - `^LL{h}` → label length in dots (taken from the PNG height, plus a tiny margin)
3. **Send raw ZPL to Windows** using `pywin32` (printer name defaults to `ZDesigner ZD230-203dpi ZPL`, change it in `app.py`).

**Keeping sizes consistent**  
- In `receipt.html`, the CSS variable `--paper-w` controls the width used by Playwright.  
- Playwright screenshots at the same width.  
- ZPL uses the real PNG width/height for `^PW`/`^LL`.  
If your device needs a strict **79 mm = 632 dots (203 dpi)**, set **`--paper-w: 632px`** and screenshot width to **632**.

## Receipt Layout Notes
- The table uses **fixed column widths**; names wrap naturally.
- Alignment: **col‑1 (name) left**, **col‑2 (qty) centered**, **col‑3 (unit price) centered**, **col‑4 (subtotal) right + vertically centered**.
- VAT line appears only for card payments; cash shows **“VAT not included”** notice.
- `tail-blank` reserves a **2 cm** cutter space and prevents the footer from being cramped.

## Import / Export (Excel)
Use **Manage → Import/Export**. The expected fields are:

| field | meaning |
|---|---|
| `barcode` | unique product code |
| `name` | product name |
| `price` | retail price (integer KRW recommended) |
| `wholesale_price` | wholesale price |
| `qty` | stock quantity |
| `category` | one of: `bag`, `top`, `bottom`, `shoes`, `dress` |
| `size` | `free`, `s`, `m`, `l`, `xl` |
| `status` | `정상` / `매진` / `절판` |
| `image` | **relative** path under `static/images/` (validated) |

## Build a Windows Executable (onedir)
A fast‑startup **onedir** build that bundles templates/static and uses your `icon.ico`:

```powershell
pyinstaller --noconfirm --onedir --windowed main.py `
  -i icon.ico `
  --add-data "templates;templates" `
  --add-data "static;static" `
  --hidden-import flask_cors `
  --collect-all playwright
```

> On the target machine, run **once** (Playwright runtime is not bundled by PyInstaller):
> ```powershell
> python -m playwright install chromium
> ```

## Troubleshooting
- **Playwright import missing** – `pip install playwright` in the active venv, then `python -m playwright install chromium`.
- **“Three lines” appear near footer** – ensure your template only uses the intended `<hr>` elements; ZPL now sets `^LL` to the **actual image height**, avoiding extra trailing lines caused by label length mismatches.
- **Nothing prints** – verify the **printer name** in `app.py` and that the device mode is **ZPL**.
- **Receipt alignment** – adjust the `<colgroup>` widths and the CSS rules in `receipt.html` to fine‑tune centering and right alignment as needed.

## Roadmap
- Optional env‑configurable printer name
- Inventory receiving UI polish
- More receipt themes

## License
**Apache‑2.0**

---

### Quick Start

```bash
pip install -r requirements.txt
pip install playwright pywin32 pywebview
python -m playwright install chromium
python main.py
```

### Build (Windows onedir)

```powershell
pyinstaller --noconfirm --onedir --windowed main.py `
  -i icon.ico `
  --add-data "templates;templates" `
  --add-data "static;static" `
  --hidden-import flask_cors `
  --collect-all playwright
```