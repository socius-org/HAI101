import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import { createReadStream, readdirSync, statSync, mkdirSync, copyFileSync, writeFileSync } from 'node:fs';
import { resolve } from 'node:path';

const POSTER_DIR = resolve(__dirname, 'poster');
const listPosters = () =>
  readdirSync(POSTER_DIR)
    .filter((f) => f.toLowerCase().endsWith('.pdf'))
    .sort()
    .map((name) => ({ name, size: statSync(resolve(POSTER_DIR, name)).size }));

// The unlisted /posters page lists the PDFs in poster/ at the repo root. Rather than duplicating
// ~30 MB into public/, this copies them into dist/posters/files/ at build time (with index.json
// giving name and size) and serves them straight from poster/ in dev.
const posterFiles = () => ({
  name: 'poster-files',
  configureServer(server) {
    server.middlewares.use('/posters/files', (req, res, next) => {
      const name = decodeURIComponent((req.url || '/').split('?')[0].slice(1));
      if (name === 'index.json') {
        res.setHeader('Content-Type', 'application/json');
        return res.end(JSON.stringify(listPosters()));
      }
      if (/^[\w.-]+\.pdf$/i.test(name) && listPosters().some((p) => p.name === name)) {
        res.setHeader('Content-Type', 'application/pdf');
        return createReadStream(resolve(POSTER_DIR, name)).pipe(res);
      }
      next();
    });
  },
  closeBundle() {
    const out = resolve(__dirname, 'dist', 'posters', 'files');
    mkdirSync(out, { recursive: true });
    const files = listPosters();
    for (const { name } of files) copyFileSync(resolve(POSTER_DIR, name), resolve(out, name));
    writeFileSync(resolve(out, 'index.json'), JSON.stringify(files));
    console.log(`posters: copied ${files.length} PDFs to dist/posters/files/`);
  },
});

// Relative base so the build works both at socius-org.github.io/HAI101/ and on a custom domain.
export default defineConfig({
  plugins: [react(), posterFiles()],
  base: './',
  build: {
    rollupOptions: {
      input: {
        main: resolve(__dirname, 'index.html'),
        posters: resolve(__dirname, 'posters/index.html'),
      },
    },
  },
});
