# Converting the notes to A4 PDF (print-friendly)

Markdown itself has **no** control over page size or page breaks — that's decided by whatever tool turns Markdown into PDF, using **CSS**. So the fix for *"a heading shouldn't sit alone at the bottom of a page"* lives in one stylesheet, [`a4-print.css`](a4-print.css), applied at conversion time. It covers **every** note at once; the `.md` files are not modified.

What the stylesheet enforces:
- **Headings stay with their content** (`break-after: avoid`) — no orphan headings.
- **Tables, code blocks, blockquotes, list items, images don't split** across pages.
- Wide code/tables **wrap to fit A4** instead of overflowing the margin.
- A4 portrait, sensible margins, repeated table headers on long tables.

Pick whichever route suits you.

---

## Route A — VS Code, no coding (easiest)

1. Install the **“Markdown PDF”** extension (author: *yzane*) in VS Code.
2. Open **Settings (JSON)** and add:
   ```jsonc
   "markdown-pdf.styles": ["pdf/a4-print.css"],
   "markdown-pdf.format": "A4",
   "markdown-pdf.margin.top": "18mm",
   "markdown-pdf.margin.bottom": "18mm",
   "markdown-pdf.margin.left": "16mm",
   "markdown-pdf.margin.right": "16mm",
   "markdown-pdf.printBackground": true
   ```
3. Open any `.md`, right-click → **“Markdown PDF: Export (pdf)”**.
   (Or “Export (pdf) — all” style commands to batch a folder.)

The extension uses the same Chromium engine as Route B, so the page-break rules are honored identically.

---

## Route B — one command for the whole repo

Converts **every** `.md` in the repo to a PDF under `pdf/out/`, mirroring the folder structure.

```bash
cd pdf
npm install        # first time only (downloads a Chromium build, ~150 MB)
npm run build
```

Output: `pdf/out/08_Databricks/07_Storage_Access_ABFSS_and_Volumes.pdf`, etc.
Re-run any time after editing notes. `pdf/out/` and `node_modules/` are git-ignored.

---

## Tuning

- **Want each `#` (H1) section to start on a new page?** Open `a4-print.css` and uncomment the last rule (`h1 { break-before: page; }`).
- **Margins / font size:** edit the `@page` and `body` rules at the top of `a4-print.css`.
- **A table is still too wide:** it has many columns — reduce content or set that table narrower; `table-layout: fixed` already wraps cell text.

> Note: a single table or code block **taller than a whole A4 page** must break somewhere — no CSS can prevent that. The rules keep everything that *fits* on one page together.
