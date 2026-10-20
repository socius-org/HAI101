import { useEffect, useRef, useState } from 'react';
import './canvas.css';
import About from './About.jsx';
import {
  series, venues, speakers, speakerById, days, industry, industryRoster, industryById, reading, logos,
  img, photo, initials, fmtTime,
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
// Industry Day talks (industry.sessions) count too, so a speaker moved there keeps a talk on their card.
const TALKS = {};
const INDUSTRY_DAY = { ...industry, id: 'industry', label: industry.title, date: industry.date || industry.title, sessions: industry.sessions || [] };
// The timetable's columns: the three academic Fridays and Industry Day.
const SCHEDULE_DAYS = [...days, INDUSTRY_DAY];
// A session's speaker, academic or Industry Day; the line under their name is the company on Industry Day.
const bySpeaker = (id) => (id ? speakerById[id] || industryById[id] : null);
const affil = (sp) => sp?.company || sp?.affiliation || 'Affiliation TBC';
// A session names one speaker (`speaker`) or several giving a joint talk (`speakers`).
const speakerIds = (s) => s.speakers || (s.speaker ? [s.speaker] : []);
const sessionSpeakers = (s) => speakerIds(s).map(bySpeaker).filter(Boolean);
// A talk given inside an open-floor slot (sessions[].talk), as a session of its own.
const socialTalk = (s) => (s.kind === 'social' && s.talk ? { ...s.talk, start: s.start, end: s.end } : null);
SCHEDULE_DAYS.forEach((d) => d.sessions.forEach((s) => {
  if (!s.kind) {
    const ids = speakerIds(s);
    (ids.length ? ids : ['tbc']).forEach((id) => { TALKS[id] = { ...s, date: d.date }; });
  } else if (socialTalk(s)) TALKS[s.talk.speaker] = { ...socialTalk(s), date: d.date };
}));
// "Fernand Gobet and Nick Oh": names joined for a sentence.
const joinNames = (names) =>
  names.length > 1 ? `${names.slice(0, -1).join(', ')} and ${names[names.length - 1]}` : names[0] || '';
const shortName = (id) => bySpeaker(id)?.name.replace(/^(Prof\.|Dr\.) /, '') || id;
const hostNames = (s) => joinNames((s.hosts || []).map(shortName));
// "Xiaomin Li and Yuexing Hao · MatrAIx": who gives a session, and where they are from.
function Who({ s }) {
  const sps = sessionSpeakers(s);
  const affils = [...new Set(sps.map(affil))];
  return (
    <>
      {sps.length ? joinNames(sps.map((sp) => sp.name)) : 'Speaker TBC'}{' '}
      <span>· {sps.length ? affils.join(' · ') : 'Affiliation TBC'}</span>
    </>
  );
}
const hostLine = (s) => `with ${hostNames(s)}${s.cohost ? ` · co-hosted with ${s.cohost}` : ''}`;
// "Talk by Youngjin Yoo · with ..." when the slot carries a talk.
const socialLine = (s) => `${s.talk ? `Talk by ${shortName(s.talk.speaker)} · ` : ''}${hostLine(s)}`;
// Hosts of an open-floor slot get it on their card and detail too, labelled by the slot's title.
const HOSTING = {};
days.forEach((d) => d.sessions.forEach((s) => {
  if (s.kind === 'social') (s.hosts || []).forEach((id) => {
    HOSTING[id] = { ...s, date: d.date, label: s.title, title: socialLine(s), abstract: s.blurb };
  });
}));
// "Fri 23 Oct, 10:30–11:30", or just the date while the time is unset.
const when = (t, sep = ', ') => `${t.date}${t.start ? `${sep}${fmtTime(t.start)}–${fmtTime(t.end)}` : ''}`;

// Abstracts are plain strings; any http(s) URL in them is rendered as a link.
const URL_RE = /(https?:\/\/[^\s)]+)/g;
const linkify = (text) =>
  text.split(URL_RE).map((part, i) =>
    i % 2 === 1 ? (   // odd parts are the captured URLs
      <a key={i} href={part} target="_blank" rel="noreferrer">{part.replace(/^https?:\/\//, '')}</a>
    ) : (
      part
    )
  );

const TBC_SPEAKER = { id: 'tbc', name: 'Speaker TBC', role: 'To be announced', affiliation: 'Affiliation TBC', noPhoto: true };

// The paper plate under a card: one logo, two side by side (a split plate), or the affiliation as text.
function LogoPlate({ srcs, alt }) {
  return (
    <span className={`cv-card-school${srcs.length > 1 ? ' is-split' : ''}`}>
      {srcs.length ? srcs.map((src) => <img key={src} src={src} alt={alt} loading="lazy" />) : <span>{alt}</span>}
    </span>
  );
}

// Talk title with a + toggle that reveals the abstract (sessions[].abstract in data.js).
function Talk({ talk }) {
  const [open, setOpen] = useState(false);
  return (
    <div className={`cv-detail-talk${open ? ' is-open' : ''}`}>
      <button type="button" className="cv-detail-talk-head" aria-expanded={open} onClick={() => setOpen(!open)}>
        <span>
          <span className="cv-detail-talk-when">
            {talk.label || 'Talk'} · {when(talk)}
          </span>
          <span className={talk.title ? 'cv-detail-talk-title' : 'cv-detail-talk-title cv-tbc'}>
            {talk.title || 'Title TBC'}
          </span>
        </span>
        <span className="cv-detail-talk-plus" aria-hidden="true" />
      </button>
      {open && (
        <div className="cv-detail-talk-body">
          <p className={talk.abstract ? '' : 'cv-tbc'}>{talk.abstract ? linkify(talk.abstract) : 'Abstract to be announced.'}</p>        </div>
      )}
    </div>
  );
}

// Speakers joining by video (sessions[].remote in data.js) are screened in the room; nothing is streamed.
function OnScreen() {
  return <span className="cv-onscreen">On screen</span>;
}
const onScreenNote = (where) => `Speaker joins live by video, shown on screen in ${where}. No live stream or public link.`;

// Pop-up with a session's abstract, opened from the + on a schedule slot.
function TalkDialog({ talk, onClose, onSpeaker }) {
  const ref = useRef(null);
  useEffect(() => {
    if (talk && !ref.current.open) ref.current.showModal();
  }, [talk]);
  const sps = talk ? sessionSpeakers(talk) : [];

  return (
    <dialog
      ref={ref}
      className="cv-dialog"
      aria-labelledby="cv-dialog-title"
      onClose={onClose}
      onClick={(e) => e.target === ref.current && ref.current.close()}
    >
      {talk && (
        <div className="cv-dialog-inner">
          <button type="button" className="cv-dialog-close" aria-label="Close" onClick={() => ref.current.close()} />
          <p className="cv-kicker">
            {talk.dateLong}{talk.start ? ` · ${fmtTime(talk.start)}–${fmtTime(talk.end)}` : ''}
          </p>
          <h3 id="cv-dialog-title" className={talk.title ? '' : 'cv-tbc'}>{talk.title || 'Title TBC'}</h3>
          <p className="cv-dialog-who"><Who s={talk} /></p>
          {talk.remote && (
            <p className="cv-dialog-onscreen">
              <OnScreen /> {onScreenNote(talk.room || 'the room')}
            </p>
          )}
          <p className={talk.abstract ? 'cv-dialog-abstract' : 'cv-dialog-abstract cv-tbc'}>
            {talk.abstract ? linkify(talk.abstract) : 'Abstract to be announced.'}
          </p>
          {sps.map((sp) => (
            <button key={sp.id} type="button" className="cv-dialog-link" onClick={() => { ref.current.close(); onSpeaker(sp.id); }}>
              {sps.length > 1 ? `About ${shortName(sp.id)}` : 'About the speaker'}
            </button>
          ))}
        </div>
      )}
    </dialog>
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
      {HOSTING[s.id] && <Talk talk={HOSTING[s.id]} />}
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
  // The placeholder card only appears while some session still has no speaker.
  // Academic speakers who moved to Industry Day (industry.speakers[].ref) are shown there, not here.
  const mainSpeakers = speakers.filter((s) => !industryById[s.id]);
  const roster = TALKS.tbc ? [...mainSpeakers, TBC_SPEAKER] : mainSpeakers;
  const [activeId, setActiveId] = useState(roster[0].id);
  const active = roster.find((s) => s.id === activeId);
  const detailRef = useRef(null);
  // Industry Day has its own cards and detail panel, selected like the academic roster.
  const [activeInd, setActiveInd] = useState(industryRoster[0]?.id ?? null);
  const indDetailRef = useRef(null);
  // ?talk=<speaker id> opens that talk's pop-up on load, so a talk can be linked to directly.
  const [openTalk, setOpenTalk] = useState(() => {
    const id = new URLSearchParams(window.location.search).get('talk');
    for (const d of [...days, INDUSTRY_DAY]) {
      const s = d.sessions.find((x) => id && (speakerIds(x).includes(id) || x.talk?.speaker === id));
      if (s) return { ...(socialTalk(s) || s), dateLong: d.dateLong };
    }
    return null;
  });

  // On narrow screens the bio sits below the photo grid, so go straight to it.
  const showSpeaker = (id) => {
    const narrow = window.matchMedia('(max-width: 900px)').matches;
    let target;
    if (speakerById[id]) {
      setActiveId(id);
      target = narrow ? detailRef.current : document.getElementById('speakers');
    } else {
      setActiveInd(id);
      target = narrow ? indDetailRef.current : document.getElementById('industry');
    }
    requestAnimationFrame(() => target?.scrollIntoView({ block: 'start' }));
  };

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
            <a href="#reading" className="cv-bar">Reading</a>
            <a href="#speakers" className="cv-bar">Main Session</a>
            <a href="#industry" className="cv-bar">Industry Day</a>
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
              <span className="cv-mark cv-mark-dark">{series.format} · {series.location}</span>{' '}
              <span className="cv-mark">+ {industry.title} · {industry.date || 'date TBC'}</span>
            </p>
          </div>
          <img className="cv-lse" src={img('lse.png')} alt="LSE" />
        </div>
      </section>

      <About />

      <section className="cv-wrap cv-reading" id="reading">
        <div className="cv-reading-grid">
          <div className="cv-reading-head">
            <p className="cv-kicker">{reading.kicker}</p>
            <h2 className="cv-h2">{reading.title}</h2>
            <p className="cv-reading-authors">{reading.authors}</p>
          </div>
          <a className="cv-reading-cover" href={`${import.meta.env.BASE_URL}${reading.file}`} target="_blank" rel="noreferrer">
            <img src={img(reading.cover)} alt={`First page of ${reading.title}`} loading="lazy" />
          </a>
          <div className="cv-reading-body">
            {reading.blurb.map((p) => <p key={p.slice(0, 40)} className="cv-reading-blurb">{p}</p>)}
            <p className="cv-reading-meta">{reading.meta}</p>
            <a className="cv-register-btn" href={`${import.meta.env.BASE_URL}${reading.file}`} target="_blank" rel="noreferrer">
              Read the note (PDF)
            </a>
          </div>
        </div>
      </section>

      <section className="cv-dark" id="speakers">
        <div className="cv-wrap">
          <p className="cv-kicker">The line-up</p>
          <h2 className="cv-h2">Main Session</h2>
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
                    <span className="cv-card-name">
                      {s.name}
                      {(TALKS[s.id] || HOSTING[s.id]) && (
                        <span className="cv-card-when">{when(TALKS[s.id] || HOSTING[s.id], ' · ').replace(/–.*$/, '')}</span>
                      )}
                    </span>
                  </span>
                  <LogoPlate srcs={logos(s)} alt={s.affiliation} />
                </button>
              ))}
            </div>
            <div ref={detailRef} className="cv-detail-holder">
              <Detail key={active.id} s={active} />
            </div>
          </div>
        </div>
      </section>

      <section className="cv-dark cv-industry" id="industry">
        {/* row 1: the pitch beside the facts; row 2: cards beside the chosen speaker's bio, as in Speakers */}
        <div className="cv-wrap cv-industry-grid">
          <div>
            <p className="cv-kicker">Coming soon</p>
            <h2 className="cv-h2">{industry.title}</h2>
            <p className="cv-industry-sub">
              <span className="cv-mark">{industry.subtitle}</span>
            </p>
            {industry.blurb.map((p) => <p key={p.slice(0, 40)} className="cv-industry-blurb">{p}</p>)}
          </div>
          <div>
            <dl className="cv-industry-facts">
              <div>
                <dt>Date</dt>
                <dd className={industry.date ? '' : 'cv-tbc'}>{industry.date || 'To be confirmed'}</dd>
              </div>
              <div>
                <dt>Venue</dt>
                <dd className={industry.venue ? '' : 'cv-tbc'}>{industry.venue ? venues[industry.venue].label : 'To be confirmed'}</dd>
              </div>
              <div>
                <dt>Speakers</dt>
                <dd className={industryRoster.length ? '' : 'cv-tbc'}>
                  {industryRoster.length ? `${industryRoster.length} confirmed · more to follow` : 'To be confirmed'}
                </dd>
              </div>
            </dl>
            {industry.companies?.length > 0 && (
              <div className="cv-industry-companies">
                <p className="cv-kicker">Companies taking part</p>
                <ul>
                  {industry.companies.map((c) => (
                    <li key={c.name} className={c.mark ? 'is-mark' : ''}>
                      {c.url ? (
                        <a href={c.url} target="_blank" rel="noreferrer" aria-label={c.name}>
                          <img src={img(c.logo)} alt={c.mark ? '' : c.name} loading="lazy" />
                          {c.mark && <span>{c.name}</span>}
                        </a>
                      ) : (
                        <span className="cv-industry-company">
                          <img src={img(c.logo)} alt={c.mark ? '' : c.name} loading="lazy" />
                          {c.mark && <span>{c.name}</span>}
                        </span>
                      )}
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        </div>
        <div className="cv-wrap cv-speakers cv-industry-speakers">
          <div className="cv-cards cv-industry-cards" aria-label="Industry Day speakers">
            {Array.from({ length: Math.max(industry.slots, industryRoster.length) }, (_, i) => {
              const s = industryRoster[i];
              if (!s) {
                return (
                  <div key={i} className="cv-card is-hidden">
                    <span className="cv-card-photo">
                      <span className="cv-card-blank" aria-hidden="true">?</span>
                      <span className="cv-card-name">To be revealed</span>
                    </span>
                    <LogoPlate srcs={[]} alt="Industry" />
                  </div>
                );
              }
              return (
                <button
                  key={s.id}
                  type="button"
                  className={`cv-card${s.id === activeInd ? ' on' : ''}`}
                  aria-pressed={s.id === activeInd}
                  onClick={() => {
                    setActiveInd(s.id);
                    if (window.matchMedia('(max-width: 900px)').matches) {
                      requestAnimationFrame(() => indDetailRef.current?.scrollIntoView({ block: 'start' }));
                    }
                  }}
                >
                  <span className="cv-card-photo">
                    {s.photo ? (
                      <img src={img(s.photo)} alt="" loading="lazy" />
                    ) : (
                      <span className="cv-card-blank" aria-hidden="true">{initials(s.name)}</span>
                    )}
                    <span className="cv-card-name">
                      {s.name}
                      {TALKS[s.id] && (
                        <span className="cv-card-when">{when(TALKS[s.id], ' · ').replace(/–.*$/, '')}</span>
                      )}
                    </span>
                  </span>
                  <LogoPlate srcs={(s.logos || []).map(img)} alt={s.company} />
                </button>
              );
            })}
          </div>
          <div ref={indDetailRef} className="cv-detail-holder">
            {activeInd && industryById[activeInd] && <Detail key={activeInd} s={industryById[activeInd]} />}
          </div>
        </div>
      </section>

      <section className="cv-wrap" id="schedule">
        <p className="cv-kicker">Schedule</p>
        <h2 className="cv-h2">Four Fridays</h2>

        {/* desktop: timetable */}
        <div
          className="cv-table"
          role="table"
          aria-label="Timetable"
          style={{ gridTemplateColumns: `84px repeat(${SCHEDULE_DAYS.length}, 1fr)` }}
        >
          <div className="cv-corner" style={{ gridColumn: 1, gridRow: 1 }} />
          {SCHEDULE_DAYS.map((d, i) => (
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
          {/* talks without a slot yet (Industry Day, as speakers confirm) are listed under the column */}
          {SCHEDULE_DAYS.map((d, i) => {
            const untimed = d.sessions.filter((s) => !s.start);
            if (!untimed.length) return null;
            return (
              <div key={d.id + '-tbc'} className="cv-slot-tbc" style={{ gridColumn: i + 2, gridRow: rowOf('16:00') + 1 }}>
                <span className="cv-slot-tbc-head">Times to be announced</span>
                {untimed.map((s) => (
                  <button
                    key={speakerIds(s).join('+') || s.title}
                    type="button"
                    className="cv-slot-tbc-item"
                    aria-haspopup="dialog"
                    onClick={() => setOpenTalk({ ...s, dateLong: d.dateLong, room: venues[d.venue]?.room })}
                  >
                    <span className={s.title ? 'cv-slot-title' : 'cv-slot-title cv-tbc'}>{s.title || 'Title TBC'}</span>
                    <span className="cv-slot-who"><Who s={s} /></span>
                  </button>
                ))}
              </div>
            );
          })}
          {SCHEDULE_DAYS.map((d, i) =>
            d.sessions.filter((s) => s.start).map((s) => {
              const style = { gridColumn: i + 2, gridRow: `${rowOf(s.start)} / ${rowOf(s.end)}` };
              if (s.kind === 'lunch') {
                return (
                  <div key={d.id + s.start} className="cv-slot cv-slot-break" style={style}>
                    Lunch break
                  </div>
                );
              }
              if (s.kind === 'intro') {
                return (
                  <div key={d.id + s.start} className="cv-slot cv-slot-intro" style={style}>
                    <time>{fmtTime(s.start)}–{fmtTime(s.end)}</time>
                    <span className="cv-slot-title">{s.title}</span>
                  </div>
                );
              }
              if (s.kind === 'social') {
                const Tag = s.talk ? 'button' : 'div';
                return (
                  <Tag
                    key={d.id + s.start}
                    type={s.talk ? 'button' : undefined}
                    className={`cv-slot cv-slot-social${s.talk ? ' has-talk' : ''}`}
                    style={style}
                    aria-haspopup={s.talk ? 'dialog' : undefined}
                    onClick={s.talk ? () => setOpenTalk({ ...socialTalk(s), dateLong: d.dateLong, room: venues[d.venue]?.room }) : undefined}
                  >
                    {s.talk && <span className="cv-plus" aria-hidden="true" />}
                    <span className="cv-slot-meta"><time>{fmtTime(s.start)}–{fmtTime(s.end)}</time></span>
                    <span className="cv-slot-title">{s.title}</span>
                    <span className="cv-slot-who">{socialLine(s)}</span>
                    {s.blurb && <span className="cv-slot-blurb">{s.blurb}</span>}
                  </Tag>
                );
              }
              return (
                <button
                  key={d.id + s.start}
                  type="button"
                  className="cv-slot"
                  style={style}
                  aria-haspopup="dialog"
                  onClick={() => setOpenTalk({ ...s, dateLong: d.dateLong, room: venues[d.venue]?.room })}
                >
                  <span className="cv-plus" aria-hidden="true" />
                  <span className="cv-slot-meta">
                    <time>{fmtTime(s.start)}–{fmtTime(s.end)}</time>
                    {s.remote && <OnScreen />}
                  </span>
                  <span className={s.title ? 'cv-slot-title' : 'cv-slot-title cv-tbc'}>{s.title || 'Title TBC'}</span>
                  <span className="cv-slot-who"><Who s={s} /></span>
                </button>
              );
            })
          )}
        </div>

        {/* mobile: stacked lists */}
        <div className="cv-list">
          {SCHEDULE_DAYS.map((d) => (
            <div key={d.id}>
              <h3>
                <span className="cv-mark cv-mark-dark">{d.date}</span>
              </h3>
              <ol>
                {d.sessions.map((s) => {
                  const sp = bySpeaker(s.speaker);
                  return (
                    <li key={s.start || speakerIds(s).join('+') || s.title} className={s.kind === 'lunch' ? 'cv-list-break' : ''}>
                      {s.start ? <time>{fmtTime(s.start)}–{fmtTime(s.end)}</time> : <time className="cv-tbc">Time TBC</time>}
                      {s.kind === 'lunch' ? (
                        <p>Lunch break</p>
                      ) : s.kind === 'intro' ? (
                        <p>
                          <span className="cv-slot-title">{s.title}</span>
                          <span className="cv-slot-who">{sp ? sp.name : 'Speaker TBC'}</span>
                        </p>
                      ) : s.kind === 'social' && !s.talk ? (
                        <p>
                          <span className="cv-slot-title">{s.title}</span>
                          <span className="cv-slot-who">{socialLine(s)}</span>
                        </p>
                      ) : s.kind === 'social' ? (
                        <button
                          type="button"
                          className="cv-list-open"
                          aria-haspopup="dialog"
                          onClick={() => setOpenTalk({ ...socialTalk(s), dateLong: d.dateLong, room: venues[d.venue]?.room })}
                        >
                          <span>
                            <span className="cv-slot-title">{s.title}</span>
                            <span className="cv-slot-who">{socialLine(s)}</span>
                          </span>
                          <span className="cv-plus" aria-hidden="true" />
                        </button>
                      ) : (
                        <button
                          type="button"
                          className="cv-list-open"
                          aria-haspopup="dialog"
                          onClick={() => setOpenTalk({ ...s, dateLong: d.dateLong, room: venues[d.venue]?.room })}
                        >
                          <span>
                            <span className={s.title ? 'cv-slot-title' : 'cv-slot-title cv-tbc'}>{s.title || 'Title TBC'}</span>
                            <span className="cv-slot-who"><Who s={s} /></span>
                            {s.remote && <OnScreen />}
                          </span>
                          <span className="cv-plus" aria-hidden="true" />
                        </button>
                      )}
                    </li>
                  );
                })}
              </ol>
            </div>
          ))}
        </div>

        <p className="cv-note">All times are UK time.</p>
        {SCHEDULE_DAYS.some((d) => d.sessions.some((s) => s.remote)) && (
          <p className="cv-note cv-note-onscreen">
            <OnScreen /> {onScreenNote('the room')}
          </p>
        )}
      </section>

      <section className="cv-wrap cv-attend" id="attend">
        <div className="cv-attend-head">
          <div>
            <p className="cv-kicker">Attend</p>
            <h2 className="cv-h2">On the LSE campus</h2>
          </div>
          <div>
            <ul className="cv-venues">
              {Object.entries(venues).map(([key, v]) => {
                const when = days.filter((d) => d.venue === key).map((d) => d.date.replace(/^Fri /, ''));
                return (
                  <li key={key}>
                    <strong>{v.label}</strong> · {when.join(' & ')}
                    <br />
                    {v.address} · <a href={v.mapsUrl} target="_blank" rel="noreferrer">Google Maps →</a>
                  </li>
                );
              })}
            </ul>
            <p>{series.registration}</p>
          </div>
        </div>

        <div className="cv-maps">
          {Object.values(venues).map((v) => (
            <figure key={v.code} className="cv-map">
              <iframe
                src={v.mapsEmbedUrl}
                title={`${v.name} on Google Maps`}
                loading="lazy"
                allowFullScreen
                referrerPolicy="no-referrer-when-downgrade"
              />
              <figcaption>
                {v.name}, {v.address}. <a href={v.mapsUrl} target="_blank" rel="noreferrer">Open in Google Maps</a>.
              </figcaption>
            </figure>
          ))}
        </div>

        <ol className="cv-register">
          {SCHEDULE_DAYS.map((d) => {
            const talks = d.sessions.filter((s) => !s.kind || socialTalk(s));
            const timed = d.sessions.filter((s) => s.start && s.kind !== 'lunch');
            const growing = d.id === 'industry' && talks.length < (industry.slots || 0);
            return (
              <li key={d.id}>
                <h3>{d.dateLong}</h3>
                <p>
                  {talks.length} {talks.length === 1 ? 'talk' : 'talks'}{growing ? ' so far' : ''}
                  {timed.length > 0 && ` · ${fmtTime(timed[0].start)}–${fmtTime(timed[timed.length - 1].end)}`}
                  <br />
                  {d.venue ? (
                    venues[d.venue].label
                  ) : (
                    <span className="cv-tbc">Venue TBC</span>
                  )}
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
            Hosted by the{' '}
            <a href={series.hostUrl} target="_blank" rel="noreferrer">{series.host}</a>
            <br />
            {series.institution}
          </p>
        </div>
        <p className="cv-footer-org">
          Supported by
          <a href="https://cookiylabs.com" target="_blank" rel="noreferrer">
            <img src={img('logos/cookiy.svg')} alt="" />
            Cookiy Labs
          </a>
        </p>
      </footer>

      <TalkDialog talk={openTalk} onClose={() => setOpenTalk(null)} onSpeaker={showSpeaker} />
    </div>
  );
}
