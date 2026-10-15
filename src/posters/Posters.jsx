import { useEffect, useState } from 'react';
import { series, days } from '../data.js';

// Unlisted download page for the print files, at /posters. The PDFs live in poster/ at the repo
// root; the posterFiles plugin in vite.config.js copies them to posters/files/ at build time and
// writes files/index.json (name and size) next to them, which is what this page lists.
const FILES = './files/';

const dayName = (n) => {
  const d = days[n - 1];
  return d ? `${d.label} · ${d.dateLong.replace(/ \d{4}$/, '')}` : `Session Day ${n}`;
};

// What each file is, from its name. Order here is the order on the page.
const KINDS = [
  { match: /combined-48x36in\.pdf$/, group: 'Combined, 48 × 36 in', title: 'Combined poster', note: 'Series and speakers side by side, vector' },
  { match: /combined-48x36in-outlined\.pdf$/, group: 'Combined, 48 × 36 in', title: 'Combined poster, outlined', note: 'Text converted to outlines, no fonts embedded: for print shops' },
  { match: /combined-48x36in-flat\.pdf$/, group: 'Combined, 48 × 36 in', title: 'Combined poster, flattened', note: 'A single 200 dpi image: safest for any printer' },
  { match: /-poster-24x36in\.pdf$/, group: 'Single sheets, 24 × 36 in', title: 'Series poster', note: 'Key art, the three days and registration codes' },
  { match: /-speakers-24x36in\.pdf$/, group: 'Single sheets, 24 × 36 in', title: 'Speakers poster', note: 'All twelve speakers with talk titles' },
  { match: /-day1-24x36in\.pdf$/, group: 'Per day, 24 × 36 in', title: dayName(1), note: 'That Friday’s programme with its registration code' },
  { match: /-day2-24x36in\.pdf$/, group: 'Per day, 24 × 36 in', title: dayName(2), note: 'That Friday’s programme with its registration code' },
  { match: /-day3-24x36in\.pdf$/, group: 'Per day, 24 × 36 in', title: dayName(3), note: 'That Friday’s programme with its registration code' },
];

const mb = (bytes) => `${(bytes / 1048576).toFixed(1)} MB`;

export default function Posters() {
  const [files, setFiles] = useState(null);
  const [error, setError] = useState(false);

  useEffect(() => {
    fetch(`${FILES}index.json`)
      .then((r) => (r.ok ? r.json() : Promise.reject(r.status)))
      .then(setFiles)
      .catch(() => setError(true));
  }, []);

  // Known files in KINDS order, then anything else found in poster/ at the end.
  const rows = files
    ? [
        ...KINDS.flatMap((k) => files.filter((f) => k.match.test(f.name)).map((f) => ({ ...f, ...k }))),
        ...files
          .filter((f) => !KINDS.some((k) => k.match.test(f.name)))
          .map((f) => ({ ...f, group: 'Other files', title: f.name, note: '' })),
      ]
    : [];
  const groups = [...new Set(rows.map((r) => r.group))];

  return (
    <div className="ps">
      <main className="ps-wrap">
        <header className="ps-head">
          <span className="ps-mark">{series.code}</span>
          <p className="ps-kicker">Print files</p>
          <h1>Posters</h1>
          <p className="ps-lede">
            Press-ready PDFs for {series.title}. Sizes are in inches. This page is unlisted: it is not linked from the
            site, so share its address directly.
          </p>
        </header>

        {error && (
          <p className="ps-empty">
            The file list could not be loaded. The PDFs are published with the site under <code>/posters/files/</code>.
          </p>
        )}
        {files && rows.length === 0 && <p className="ps-empty">No posters have been published yet.</p>}

        {groups.map((g) => (
          <section key={g} className="ps-group">
            <h2>{g}</h2>
            <ul>
              {rows
                .filter((r) => r.group === g)
                .map((r) => (
                  <li key={r.name}>
                    <div className="ps-text">
                      <a className="ps-title" href={`${FILES}${r.name}`} download>
                        {r.title}
                      </a>
                      {r.note && <p className="ps-note">{r.note}</p>}
                      <p className="ps-file">
                        {r.name} · {mb(r.size)}
                      </p>
                    </div>
                    <a className="ps-dl" href={`${FILES}${r.name}`} download aria-label={`Download ${r.title}`}>
                      Download ↓
                    </a>
                  </li>
                ))}
            </ul>
          </section>
        ))}

        <footer className="ps-foot">
          <a href="../">← socialscience.ai</a>
        </footer>
      </main>
    </div>
  );
}
