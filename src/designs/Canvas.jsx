import { useEffect, useRef, useState } from 'react';
import './canvas.css';
import About from './About.jsx';
import {
  series, speakers, speakerById, days, scheduleNote,
  img, photo, logo, initials, fmtTime,
} from '../data.js';

// Timetable runs 9:00–16:00 in 15-minute rows; row 1 is the day header.
const DAY_START = 9 * 60;
const DAY_END = 16 * 60;
const toMin = (t) => {
  const [h, m] = t.split(':').map(Number);
  return h * 60 + m;
};
const rowOf = (t) => (toMin(t) - DAY_START) / 15 + 2;
const HOURS = Array.from({ length: (DAY_END - DAY_START) / 60 + 1 }, (_, i) => 9 + i);

// Each speaker's slot, so the bio panel can show what they are speaking on and when.
const TALKS = {};
days.forEach((d) => d.sessions.forEach((s) => {
  if (s.kind !== 'lunch') TALKS[s.speaker || 'tbc'] = { ...s, date: d.date };
}));

const TBC_SPEAKER = { id: 'tbc', name: 'Speaker TBC', role: 'To be announced', affiliation: 'Affiliation TBC', noPhoto: true };

// Talk title with a + toggle that reveals the abstract (sessions[].abstract in data.js).
function Talk({ talk }) {
  const [open, setOpen] = useState(false);
  return (
    <div className={`cv-detail-talk${open ? ' is-open' : ''}`}>
      <button type="button" className="cv-detail-talk-head" aria-expanded={open} onClick={() => setOpen(!open)}>
        <span>
          <span className="cv-detail-talk-when">
            Talk · {talk.date}, {fmtTime(talk.start)}–{fmtTime(talk.end)}
          </span>
          <span className={talk.title ? 'cv-detail-talk-title' : 'cv-detail-talk-title cv-tbc'}>
            {talk.title || 'Title TBC'}
          </span>
        </span>
        <span className="cv-detail-talk-plus" aria-hidden="true" />
      </button>
      {open && (
        <div className="cv-detail-talk-body">
          <p className={talk.abstract ? '' : 'cv-tbc'}>{talk.abstract || 'Abstract to be announced.'}</p>
          <a href="#schedule">See it in the schedule</a>
        </div>
      )}
    </div>
  );
}

function Detail({ s }) {
  return (
    <div className="cv-detail" aria-live="polite">
      <p className="cv-kicker">{s.affiliation}</p>
      <h3>{s.name}</h3>
      <p className="cv-detail-role">{s.role}</p>
      {s.lab && <p className="cv-detail-lab">{s.lab}</p>}
      {TALKS[s.id] && <Talk talk={TALKS[s.id]} />}
      {s.upcoming && (
        <div className="cv-detail-block">
          <h4>Upcoming</h4>
          <p>{s.upcoming}</p>
        </div>
      )}
      {s.previously && (
        <div className="cv-detail-block">
          <h4>Previously</h4>
          <ul>{s.previously.map((p) => <li key={p}>{p}</li>)}</ul>
        </div>
      )}
      {(s.interests || s.interestsTbc) && (
        <div className="cv-detail-block">
          <h4>Research interests</h4>
          {s.interests ? <ul>{s.interests.map((p) => <li key={p}>{p}</li>)}</ul> : <p>TBC</p>}
        </div>
      )}
      {s.publications && (
        <div className="cv-detail-block">
          <h4>Selected publications</h4>
          <ul>
            {s.publications.map(([t, a]) => (
              <li key={t}>
                {t} <span className="cv-dim">({a})</span>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}

export default function Canvas() {
  const roster = [...speakers, TBC_SPEAKER];
  const [activeId, setActiveId] = useState(roster[0].id);
  const active = roster.find((s) => s.id === activeId);
  const detailRef = useRef(null);

  // Luma's checkout script turns the register links into an in-page overlay; without it they
  // still work as plain links to the event page.
  useEffect(() => {
    if (!days.some((d) => d.lumaEventId) || document.getElementById('luma-checkout')) return;
    const s = document.createElement('script');
    s.id = 'luma-checkout';
    s.src = 'https://embed.lu.ma/checkout-button.js';
    s.onload = () => window.luma?.initCheckout?.();
    document.body.appendChild(s);
  }, []);

  const select = (id) => {
    setActiveId(id);
    // On narrow screens the detail panel sits below the grid, so bring it into view.
    if (window.matchMedia('(max-width: 900px)').matches) {
      requestAnimationFrame(() => detailRef.current?.scrollIntoView({ block: 'start' }));
    }
  };

  return (
    <div className="cv">
      <section className="cv-hero" id="top" style={{ backgroundImage: `url(${img('keyart.jpg')})` }}>
        <header className="cv-nav">
          <a href="#top" className="cv-bar cv-bar-dark">{series.code}</a>
          <nav aria-label="Sections">
            <a href="#about" className="cv-bar">About</a>
            <a href="#speakers" className="cv-bar">Speakers</a>
            <a href="#schedule" className="cv-bar">Schedule</a>
            <a href="#attend" className="cv-bar">Register</a>
          </nav>
        </header>

        <div className="cv-hero-body">
          <div>
            <h1>
              <span className="cv-mark cv-mark-dark">Human x Artificial Intelligence</span>
            </h1>
            <p className="cv-hero-tag">
              <span className="cv-mark">{series.tagline}</span>
            </p>
            <p className="cv-hero-meta">
              <span className="cv-mark cv-mark-dark">{series.datesShort}</span>{' '}
              <span className="cv-mark cv-mark-dark">{series.format} · {series.location}</span>
            </p>
          </div>
          <img className="cv-lse" src={img('lse.png')} alt="LSE" />
        </div>
      </section>

      <About />

      <section className="cv-dark" id="speakers">
        <div className="cv-wrap">
          <p className="cv-kicker">Confirmed so far</p>
          <h2 className="cv-h2">Speakers</h2>
          <div className="cv-speakers">
            <div className="cv-cards">
              {roster.map((s) => (
                <button
                  key={s.id}
                  type="button"
                  className={`cv-card${s.id === activeId ? ' on' : ''}`}
                  aria-pressed={s.id === activeId}
                  onClick={() => select(s.id)}
                >
                  <span className="cv-card-photo">
                    {photo(s) ? (
                      <img src={photo(s)} alt="" loading="lazy" />
                    ) : (
                      <span className="cv-card-blank" aria-hidden="true">
                        {s.id === 'tbc' ? '?' : initials(s.name)}
                      </span>
                    )}
                    <span className="cv-card-name">{s.name}</span>
                  </span>
                  <span className="cv-card-school">
                    {logo(s) ? <img src={logo(s)} alt={s.affiliation} loading="lazy" /> : <span>{s.affiliation}</span>}
                  </span>
                </button>
              ))}
            </div>
            <div ref={detailRef} className="cv-detail-holder">
              <Detail key={active.id} s={active} />
            </div>
          </div>
        </div>
      </section>

      <section className="cv-wrap" id="schedule">
        <p className="cv-kicker">Preliminary schedule</p>
        <h2 className="cv-h2">Three Fridays</h2>

        {/* desktop: timetable */}
        <div className="cv-table" role="table" aria-label="Timetable">
          <div className="cv-corner" style={{ gridColumn: 1, gridRow: 1 }} />
          {days.map((d, i) => (
            <div key={d.id} className="cv-dayhead" style={{ gridColumn: i + 2, gridRow: 1 }}>
              <span>{d.label}</span>
              {d.date}
            </div>
          ))}
          {HOURS.map((h) => (
            <div key={h} className="cv-hour" style={{ gridColumn: '1 / -1', gridRow: rowOf(`${h}:00`) }}>
              <span>{h}:00</span>
            </div>
          ))}
          {days.map((d, i) =>
            d.sessions.map((s) => {
              const sp = s.speaker ? speakerById[s.speaker] : null;
              const style = { gridColumn: i + 2, gridRow: `${rowOf(s.start)} / ${rowOf(s.end)}` };
              if (s.kind === 'lunch') {
                return (
                  <div key={d.id + s.start} className="cv-slot cv-slot-break" style={style}>
                    Lunch break
                  </div>
                );
              }
              return (
                <div key={d.id + s.start} className="cv-slot" style={style}>
                  <time>{fmtTime(s.start)}–{fmtTime(s.end)}</time>
                  <p className={s.title ? 'cv-slot-title' : 'cv-slot-title cv-tbc'}>{s.title || 'Title TBC'}</p>
                  <p className="cv-slot-who">
                    {sp ? sp.name : 'Speaker TBC'} <span>· {sp ? sp.affiliation : 'Affiliation TBC'}</span>
                  </p>
                </div>
              );
            })
          )}
        </div>

        {/* mobile: stacked lists */}
        <div className="cv-list">
          {days.map((d) => (
            <div key={d.id}>
              <h3>
                <span className="cv-mark cv-mark-dark">{d.date}</span>
              </h3>
              <ol>
                {d.sessions.map((s) => {
                  const sp = s.speaker ? speakerById[s.speaker] : null;
                  return (
                    <li key={s.start} className={s.kind === 'lunch' ? 'cv-list-break' : ''}>
                      <time>{fmtTime(s.start)}–{fmtTime(s.end)}</time>
                      {s.kind === 'lunch' ? (
                        <p>Lunch break</p>
                      ) : (
                        <div>
                          <p className={s.title ? 'cv-slot-title' : 'cv-slot-title cv-tbc'}>{s.title || 'Title TBC'}</p>
                          <p className="cv-slot-who">
                            {sp ? sp.name : 'Speaker TBC'} <span>· {sp ? sp.affiliation : 'Affiliation TBC'}</span>
                          </p>
                        </div>
                      )}
                    </li>
                  );
                })}
              </ol>
            </div>
          ))}
        </div>

        <p className="cv-note">{scheduleNote}</p>
      </section>

      <section className="cv-wrap cv-attend" id="attend">
        <div className="cv-attend-head">
          <div>
            <p className="cv-kicker">Attend</p>
            <h2 className="cv-h2">{series.location}</h2>
          </div>
          <div>
            <p>{series.formatNote}</p>
            <p>{series.registration}</p>
          </div>
        </div>
        <ol className="cv-register">
          {days.map((d) => {
            const talks = d.sessions.filter((s) => s.kind !== 'lunch');
            return (
              <li key={d.id}>
                <h3>{d.dateLong}</h3>
                <p>
                  {talks.length} talks · {fmtTime(talks[0].start)}–{fmtTime(talks[talks.length - 1].end)}
                </p>
                {d.lumaUrl ? (
                  <a
                    className="cv-register-btn"
                    href={d.lumaUrl}
                    target="_blank"
                    rel="noreferrer"
                    data-luma-action={d.lumaEventId ? 'checkout' : undefined}
                    data-luma-event-id={d.lumaEventId || undefined}
                  >
                    Register on Luma
                  </a>
                ) : (
                  <span className="cv-register-btn is-soon">Registration opens soon</span>
                )}
              </li>
            );
          })}
        </ol>
      </section>

      <footer className="cv-wrap cv-footer">
        <div className="cv-footer-host">
          <img src={img('lse.png')} alt="LSE" />
          <p>
            Hosted by the {series.host}
            <br />
            {series.institution}
          </p>
        </div>
        <p>
          Organised with{' '}
          <a href="https://socius.org" target="_blank" rel="noreferrer">socius labs</a>
        </p>
      </footer>
    </div>
  );
}
