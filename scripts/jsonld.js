// Structured data (schema.org JSON-LD) for the home page, built from src/data.js at build time so it
// never drifts from the schedule. Injected into index.html by the `seo-jsonld` plugin in vite.config.js.
// Google reads it for event rich results and to tie the site name "socialscience.ai" to the page.
const SITE = 'https://socialscience.ai/';
const IMAGE = `${SITE}img/og.jpg`; // the share card, reused as every event's image

// "Friday 23 October 2026" + "10:00" in Europe/London, as an ISO string with the right UTC offset (BST or GMT).
const london = (dateLong, hm) => {
  const day = new Date(`${dateLong.replace(/^\w+ /, '')} ${hm} UTC`); // "23 October 2026 10:00 UTC"
  const tz = new Intl.DateTimeFormat('en-GB', { timeZone: 'Europe/London', timeZoneName: 'longOffset' })
    .formatToParts(day)
    .find((p) => p.type === 'timeZoneName').value; // "GMT+01:00" or "GMT"
  const offset = tz === 'GMT' ? '+00:00' : tz.replace('GMT', '');
  return `${day.toISOString().slice(0, 10)}T${hm.padStart(5, '0')}:00${offset}`;
};

export async function buildJsonLd(dataUrl) {
  const { series, venues, days, industry, speakers, industryRoster } = await import(dataUrl);
  const isBreak = (s) => s.kind === 'lunch' || s.kind === 'coffee';
  const timed = (d) => (d.sessions || []).filter((s) => s.start && !isBreak(s));
  const speaker = (id) => speakers.find((s) => s.id === id) || industryRoster.find((s) => s.id === id);
  // A speaker as a schema.org Person: their own site as url, their institution's page about them as sameAs.
  const person = (s) => {
    const p = { '@type': 'Person', name: s.name };
    if (s.url) p.url = s.url;
    if (s.profile) p.sameAs = [s.profile];
    const org = s.company || s.affiliation;
    if (org) p.affiliation = { '@type': 'Organization', name: org };
    return p;
  };

  const place = (key) => {
    const v = venues[key];
    if (!v) {
      return {
        '@type': 'Place',
        name: series.institution,
        address: { '@type': 'PostalAddress', addressLocality: 'London', addressCountry: 'GB' },
      };
    }
    const [street, postcode] = v.address.split(/, London /);
    return {
      '@type': 'Place',
      name: `${v.name}, London School of Economics`,
      address: { '@type': 'PostalAddress', streetAddress: street, addressLocality: 'London', postalCode: postcode, addressCountry: 'GB' },
    };
  };

  const organizer = {
    '@type': 'Organization',
    name: series.host,
    url: series.hostUrl,
    parentOrganization: { '@type': 'CollegeOrUniversity', name: series.institution, url: 'https://www.lse.ac.uk/' },
  };

  // One sentence of context, then the day's talks as “Title” (Speaker). Google asks every Event for a description.
  const describe = (d, lead) => {
    const talks = timed(d)
      .filter((s) => s.kind !== 'intro' && s.title)
      .map((s) => {
        const names = (s.speakers || (s.speaker ? [s.speaker] : [])).map((id) => speaker(id)?.name).filter(Boolean);
        return `“${s.title}”${names.length ? ` (${names.join(' and ')})` : ''}`;
      });
    return talks.length ? `${lead} Talks: ${talks.join('; ')}.` : lead;
  };

  // Registration is free. A day with a Luma link is open now; one without is announced but not open yet
  // (PreOrder), and points at the page's own registration section until its link exists.
  // validFrom is the day registration opened (or will open), when data.js gives it.
  const offer = (d) => {
    const from = d.registrationFrom || (d.lumaUrl ? series.registrationFrom : null);
    return {
      '@type': 'Offer',
      url: d.lumaUrl || `${SITE}#attend`,
      price: '0',
      priceCurrency: 'GBP',
      availability: d.lumaUrl ? 'https://schema.org/InStock' : 'https://schema.org/PreOrder',
      ...(from ? { validFrom: from } : {}),
    };
  };

  const event = (d, name, lead) => {
    const t = timed(d);
    const ids = [...new Set(t.flatMap((s) => s.speakers || (s.speaker ? [s.speaker] : [])))];
    const e = {
      '@type': 'Event',
      name,
      description: describe(d, lead),
      image: [IMAGE],
      startDate: t.length ? london(d.dateLong, t[0].start) : undefined,
      endDate: t.length ? london(d.dateLong, t[t.length - 1].end) : undefined,
      eventAttendanceMode: 'https://schema.org/OfflineEventAttendanceMode',
      eventStatus: 'https://schema.org/EventScheduled',
      location: place(d.venue),
      organizer,
      isAccessibleForFree: true,
      performer: ids.map(speaker).filter(Boolean).map(person),
      url: `${SITE}#schedule`,
      offers: offer(d),
    };
    return e;
  };

  // "A lecture series spanning ..." read as the tail of "Session Day 2 of HAI101 (Human x Artificial Intelligence), a ..."
  const tagline = series.tagline.charAt(0).toLowerCase() + series.tagline.slice(1);
  const subEvent = [
    ...days.map((d) =>
      event(d, `${series.code} ${d.label}: ${series.title}`, `${d.label} of ${series.code} (${series.title}), ${tagline}`),
    ),
    event(industry, `${series.code} ${industry.title}: ${industry.subtitle}`, industry.blurb[0]),
  ];
  const dated = subEvent.filter((e) => e.startDate);

  const graph = [
    {
      '@type': 'WebSite',
      '@id': `${SITE}#website`,
      url: SITE,
      name: 'socialscience.ai',
      alternateName: [series.code, `${series.code} | ${series.title}`],
      publisher: organizer,
      author: person(speakers.find((sp) => sp.id === 'oh')),
    },
    {
      '@type': 'EventSeries',
      '@id': `${SITE}#series`,
      name: `${series.code} | ${series.title}`,
      alternateName: 'socialscience.ai',
      description: series.tagline,
      url: SITE,
      image: IMAGE,
      startDate: dated[0]?.startDate.slice(0, 10),
      endDate: dated[dated.length - 1]?.startDate.slice(0, 10),
      location: {
        '@type': 'Place',
        name: series.institution,
        address: { '@type': 'PostalAddress', addressLocality: 'London', addressCountry: 'GB' },
      },
      organizer,
      isAccessibleForFree: true,
      subEvent,
    },
  ];
  // "<" escaped so no talk title can close the <script> tag this is written into.
  return JSON.stringify({ '@context': 'https://schema.org', '@graph': graph }).replace(/</g, '\\u003c');
}
