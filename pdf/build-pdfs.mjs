// Batch-convert every Markdown note in the repo to an A4 PDF, applying
// pdf/a4-print.css (headings stay with their content; tables/code don't split).
//
//   cd pdf && npm install && npm run build
//
// PDFs are written to pdf/out/ mirroring the repo folder structure.
// (First run downloads a Chromium build via Puppeteer — a one-time ~150 MB.)

import { mdToPdf } from 'md-to-pdf';
import { globby } from 'globby';
import { promises as fs } from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const REPO = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const CSS = path.join(REPO, 'pdf', 'a4-print.css');
const OUT = path.join(REPO, 'pdf', 'out');

const files = await globby(['**/*.md'], {
  cwd: REPO,
  gitignore: true,
  ignore: ['node_modules/**', 'pdf/**', '**/node_modules/**'],
});

console.log(`Converting ${files.length} Markdown files to A4 PDF…\n`);

let ok = 0, fail = 0;
for (const rel of files) {
  const src = path.join(REPO, rel);
  const dest = path.join(OUT, rel.replace(/\.md$/i, '.pdf'));
  try {
    await fs.mkdir(path.dirname(dest), { recursive: true });
    const pdf = await mdToPdf(
      { path: src },
      {
        stylesheet: [CSS],
        pdf_options: {
          format: 'A4',
          printBackground: true,
          margin: { top: '18mm', bottom: '18mm', left: '16mm', right: '16mm' },
        },
        launch_options: { args: ['--no-sandbox'] },
      },
    );
    if (pdf?.content) {
      await fs.writeFile(dest, pdf.content);
      console.log('  ✓', rel);
      ok++;
    }
  } catch (err) {
    console.error('  ✗', rel, '—', err.message);
    fail++;
  }
}

console.log(`\nDone. ${ok} succeeded, ${fail} failed. PDFs are in pdf/out/.`);
