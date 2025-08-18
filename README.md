# TreasurePOS (Flask + Desktop WebView)

Local‑first POS for small shops. Scan or type barcodes, switch retail/wholesale price, sell with cash or card, keep stock logs, view sales analytics, and print Zebra receipts (KO/ZH/EN).

> **Heads‑up:** This repository currently contains **duplicate blocks** in `app.py` for the printing pipeline (older Html2Image code alongside the newer Playwright‑based flow). In practice you should keep **one** implementation. This README documents the **recommended Playwright + ZPL** flow.

---

## ✨ Features
- Barcode/manual input, retail/wholesale toggle, cash/card checkout
- Product CRUD + **Excel import/export**
- **Sales logs & stock logs**, filters and charts
- **Multilingual UI**: 한국어 / 中文 / English
- **Zebra thermal printing**: render `receipt.html` → PNG → ZPL graphics → send to Windows printer

## Project Structure
```
/app.py           # Flask backend (routes, DB, printing)
/main.py          # Desktop wrapper (pywebview + health check)
/templates/
  index.html      # Sales (home)
  manage.html     # Manage products (Excel import/export)
  sales.html      # Sales analytics
  stocklog.html   # Stock in/out/adjust logs
  settings.html   # Language switch (KO/ZH/EN)
  receipt.html    # Printable receipt layout
/static/          # assets
/README.md
```

## Requirements
- Python **3.10+** (Windows 10/11 recommended for printing)
- Packages (install below): Flask, Flask‑CORS, pandas, openpyxl, Pillow, **playwright**, **pywin32** (Windows only), pywebview

```bash
pip install -r requirements.txt
pip install playwright pywin32 pywebview
python -m playwright install chromium   # once per machine
```

> If you previously used **Html2Image**, you can remove it; the current recommended flow uses **Playwright**.

## Run (development)
```bash
python app.py        # Flask only (opens at 127.0.0.1:<port>)
# or desktop window:
python main.py
```
`main.py` starts Flask in a background thread and opens a local window via **pywebview**.

## Data location
The app stores the SQLite DB and uploads in a **writable run directory**. By default it’s next to the executable (or the repository) and is **migrated automatically** from older layouts. You can override with:
```bash
# optional – change where the DB/uploads live
set TREASUREPOS_DATA_DIR=C:\TreasurePOS\data       # Windows (PowerShell: $env:TREASUREPOS_DATA_DIR="...")
```
This variable is detected at startup and used by the helpers that compute the run dir and migrate legacy files. (See the code path that looks up `TREASUREPOS_DATA_DIR` and performs `_maybe_migrate_legacy()`.)

## Printing pipeline (recommended)
1) **Render only the `.receipt` element** from `receipt.html` to PNG using **Playwright** at a fixed width (**624px by default**, roughly ~78–79 mm).  
   The helper opens Chromium, waits for fonts, and screenshots the element.
2) **Convert PNG → ZPL graphics** and prepend ZPL header with `^PW` (print width in dots) and `^LL` (label length) based on the actual image width/height.
3) **Send raw ZPL** to a Windows printer (default: `ZDesigner ZD230-203dpi ZPL`).

> You can change the printer name in `app.py` or set an environment variable `PRINTER_NAME` and read it in code.

### Keep CSS ↔ Screenshot ↔ ZPL consistent
- In `receipt.html`, root width is **624px** by default (`:root { --paper-w: 624px; }`) and page size is `@page { size: 79mm auto; }`.
- Playwright screenshots at **624 px** width.
- ZPL sets `^PW` to the PNG pixel width and `^LL` to the PNG pixel height (+ small margin).

If your printer requires **exact 79 mm at 203 dpi (= 632 dots)**, simply:
- Change the CSS variable and screenshot width to **632**, **and**
- Ensure ZPL uses `^PW632` / `^LL{H}`.

### Windows raw printing
The app uses `pywin32` to open the printer and send ASCII ZPL in **RAW** mode. If `pywin32` is missing, the API returns an informative error message rather than crashing.

## Build a Windows executable (onedir)
The simplest onedir build (fast startup) that includes templates and static assets:

```powershell
# from the repo root
pyinstaller --noconfirm --onedir --windowed main.py `
  -i icon.ico `
  --add-data "templates;templates" `
  --add-data "static;static" `
  --hidden-import flask_cors `
  --collect-all playwright
```

Notes:
- The Playwright **Chromium runtime is not bundled** by PyInstaller; on the target machine run once:
  ```powershell
  python -m playwright install chromium
  ```
- If you run the server only, you can also build `app.py` in the same way.
- Make sure the process can write to your chosen data directory (see **Data location**).

## Excel import/export
- Use the **Manage** page to import/export products.
- Expected columns (header names are flexible; map to): **barcode**, **name**, **price**, **wholesale_price**, **qty**, **category**, **size**, **status**, **image**.
- Images should be placed in `/static/images/` (or uploaded via the app); the server exposes them at `/static/images/<filename>`.

## API surface (selected)
- `GET /` – sales screen  
- `GET /manage`, `/sales`, `/stocklog`, `/settings`, `/receipt/<sale_id>` – pages
- `POST /api/print_receipt/<sale_id>` – render & print receipt (**Playwright → ZPL**)
- `GET /api/items`, `POST /api/items` (+ `PUT/DELETE /api/items/<barcode>`) – product CRUD
- `GET /api/items/search?q=...` – search by code or name
- `POST /api/sales` – create a sale (cash/card), writes stock log
- `GET /api/sales` – list sales; `GET /api/stocklog` – stock in/out/adjust logs
- `POST /api/import` / `GET /api/export` – Excel import/export

> See `app.py` for the exact request/response shapes.

## Receipt layout tips
- The logo block has extra bottom margin so it doesn’t crowd the table.
- In the table header and body: **cols 1–3 are centered**, **col 4 stays right‑aligned and vertically centered**, and names wrap naturally.  
- `tail-blank` reserves the exact blank area at the bottom for cutter space.
- VAT notice is bold and slightly larger; cash mode shows “VAT not included”, card mode prints an explicit VAT line.

## Known issues / housekeeping
- **Duplicate printing code** in `app.py` (Html2Image vs Playwright) – keep the Playwright variant and delete the old route to avoid accidental overrides.
- Some older CSS in `receipt.html` may still contain typos (e.g., `!重要`, malformed values). Use the latest fixed stylesheet.
- When packaging, remember the Playwright runtime step on every new machine.

## License
MIT (or your preference).

---

### Quick commands

**Development**
```bash
pip install -r requirements.txt
pip install playwright pywin32 pywebview
python -m playwright install chromium
python main.py
```

**Build (Windows, onedir)**
```powershell
pyinstaller --noconfirm --onedir --windowed main.py `
  -i icon.ico `
  --add-data "templates;templates" `
  --add-data "static;static" `
  --hidden-import flask_cors `
  --collect-all playwright
```
