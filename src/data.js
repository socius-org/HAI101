// All page content lives here.

export const img = (p) => `${import.meta.env.BASE_URL}img/${p}`;

export const series = {
  code: 'HAI101',
  title: 'Human x Artificial Intelligence',
  tagline:
    'A lecture series spanning the social, behavioural, cognitive sciences, philosophy, and AI.',
  question: 'Can “thinking” be mechanised?',
  host: 'Centre for Philosophy of Natural and Social Science (CPNSS)',
  hostShort: 'LSE CPNSS',
  institution: 'London School of Economics and Political Science',
  dates: 'Fridays · 23 Oct, 6 Nov & 13 Nov 2026',
  datesShort: '23 Oct · 6 Nov · 13 Nov 2026',
  location: 'Location to be announced',
  format: 'Hybrid',
  formatNote: 'In person at LSE, with one or two lectures held online via Zoom.',
  registration: 'Registration will open on Luma.',
};

export const intro = [
  'Cognitive science and artificial intelligence were born from that single question in the 1950s, and they have pulled apart and back together ever since. Shared in the symbolic era, split as AI turned statistical, rejoined through connectionism and Bayesian models of mind, drifting again, and now converging once more. The interesting question is not that they have reunited, but what is different about this convergence.',
  'What is different is that the artificial human is now good enough to be used as an instrument: an experimental subject, a model of a population, a proxy for people. Human & Artificial Intelligence (HAI) 101 takes this on as its subject, asking what this new kind of instrument means for how we can understand minds, people and knowledge.',
];

export const summary =
  'HAI 101 brings together social, behavioural, cognitive sciences, philosophy, and artificial intelligence to explore the changing relationship between humans and machines: how we model minds, how minds shape machines, and what happens when machines begin to model people, reason about the world, and produce knowledge themselves.';

export const speakers = [
  {
    id: 'feng',
    name: 'Steven Feng',
    role: 'PhD Candidate, Dept. of Computer Science',
    affiliation: 'Stanford University',
    lab: 'Language & Cognition Lab (PI: Prof. Michael Frank); Computation & Cognition Lab (PI: Prof. Noah Goodman)',
    upcoming: 'Anthropic Research Fellow',
    previously: [
      'MLT (Master of Language Technologies), Carnegie Mellon University',
      'BMath, Statistics Major, Computer Science Minor, University of Waterloo',
      'Amazon, NVIDIA & Contextual AI',
    ],
    interests: [
      'Data-centric scaling laws for reasoning and generalisation',
      'Efficient reasoning in SLMs and data-limited regimes',
      'Human and cognitively-inspired learning signals and evaluation for foundation models',
    ],
  },
  {
    id: 'gobet',
    name: 'Prof. Fernand Gobet',
    role: 'Professorial Research Fellow, CPNSS',
    affiliation: 'London School of Economics',
    publications: [
      ['Templates in chess memory: A mechanism for recalling several boards', 'Gobet & Simon, 1996'],
      ['Perception and memory in chess: Studies in the heuristics of the professional eye', 'de Groot, Gobet & Jongman, 1996'],
      ['Expert chess memory: Revisiting the chunking hypothesis', 'Gobet & Simon, 1998'],
      ['Chunking mechanisms in human learning', 'Gobet et al., 2001'],
      ['Deliberate practice: Is that all it takes to become an expert?', 'Hambrick et al., 2014'],
      ['Automating the practice of science: Opportunities, challenges and implications', 'Musslick et al., 2025'],
    ],
  },
  {
    id: 'manning',
    name: 'Benjamin Manning',
    role: 'PhD Candidate, Management Science & Information Technology',
    affiliation: 'Massachusetts Institute of Technology',
    lab: 'Information Technology Group',
    previously: [
      'S.M., Management Research, MIT',
      'M.P.P., Economic & Social Policy, Harvard University',
      'B.A., Mathematics, Washington University in St. Louis',
    ],
    interests: [
      'Making AI systems credibly represent people, and what becomes possible when they do',
      'AI simulations as robust proxies for human subjects, and computational systems for social scientists',
      "AI systems that learn people's preferences and act on their behalf, and the platforms and markets these enable",
    ],
  },
  {
    id: 'jin',
    name: 'Helen Jin',
    role: 'PhD Candidate, Dept. of Computer and Information Science',
    affiliation: 'University of Pennsylvania',
    lab: 'Penn NLP + Brachio Lab (PI: Prof. Eric Wong)',
    previously: [
      'M.S.E., Computer and Information Science, University of Pennsylvania',
      'B.A., Mathematics and Computer Science, Columbia University',
      'Amazon',
    ],
    interests: [
      'Trustworthy and Explainable AI (XAI): evaluating whether AI systems are reliable, stable, expert-aligned, and correct for the right reasons',
      'AI for Scientific Discovery: improving how AI systems reason about and how to verify the feasibility of scientific claims',
      'AI in Education: designing new approaches to support student learning, feedback, and assessment in the age of generative AI',
    ],
  },
  {
    id: 'peters',
    name: 'Prof. Megan Peters',
    role: 'Associate Professor, Dept. of Experimental Psychology',
    affiliation: 'University College London',
    publications: [
      ['Human observers have optimal introspective access to perceptual processes even for visually masked stimuli', 'Peters & Lau, 2015'],
      ['Towards characterizing the canonical computations generating phenomenal experience', 'Peters, 2022'],
      ['Consciousness in artificial intelligence: Insights from the science of consciousness', 'Butlin, Long et al., 2023'],
      ['How brains build higher order representations of uncertainty', 'Peters & Azimi Asrari, 2025'],
      ['Identifying the indicators of consciousness in AI systems', 'Butlin et al., 2025'],
      ['The relative psychometric function: A general analysis framework for relating psychological processes', 'Maniscalco et al., 2026'],
      ['How to discover the natural kind of consciousness – and test for its presence – under population shifts', 'Peters, 2026'],
    ],
  },
  {
    id: 'noichl',
    name: 'Maximilian Noichl',
    role: 'PhD Candidate, Theoretical Philosophy',
    affiliation: 'Utrecht University',
    previously: [
      'MA, History and Philosophy of Science, University of Vienna',
      'BA, Philosophy, University of Vienna',
    ],
    interests: [
      'Data-driven analysis of, and for, philosophy',
      'Combining agent-based models of scientific progress with scientometric data',
      'Building AI systems that use formal tools to reason better about philosophy',
    ],
  },
  {
    id: 'bishop',
    name: 'Dr. Nicholas Bishop',
    role: 'Postdoctoral Researcher, Dept. of Computer Science',
    affiliation: 'University of Oxford',
    lab: 'Large Agent Collider (LAC) project (PIs: Prof. Michael Wooldridge, Prof. Ani Calinescu & Prof. Doyne Farmer)',
    previously: ['PhD, Mechanism Design & Machine Learning, University of Southampton'],
    interests: [
      'ML methods to rapidly calibrate, analyse and validate agent-based models (ABMs) of large-scale complex systems',
      'Generalised variational inference for realistic synthetic populations',
      'Interpretable surrogate models for ABMs via causal abstraction',
      'AI safety; boundedly rational agents scaled through multi-agent systems',
    ],
  },
  {
    id: 'sabatelli',
    name: 'Prof. Matthia Sabatelli',
    role: 'Bio to be confirmed',
    affiliation: 'University of Groningen',
    noPhoto: true,
  },
  {
    id: 'thompson',
    name: 'Dr. Jessica Thompson',
    role: 'Postdoctoral Researcher, Dept. of Experimental Psychology',
    affiliation: 'University of Oxford',
    lab: 'Human Information Processing Lab (PI: Prof. Christopher Summerfield)',
    upcoming: 'Lecturer, University of Glasgow',
    previously: [
      'PhD, Cognitive Science and Neuropsychology, University of Montréal (supervised by Marc Schönwiesner and Yoshua Bengio)',
      'Quebec Artificial Intelligence Institute (Mila)',
    ],
    interestsTbc: true,
  },
  {
    id: 'jagadish',
    name: 'Dr. Akshay Jagadish',
    role: 'Peretsman Scully Postdoctoral Fellow',
    affiliation: 'Princeton University',
    lab: 'Independent researcher in the Natural and Artificial Minds program at the Princeton AI Lab',
    previously: [
      'PhD, Computer Science, University of Tübingen; Max Planck Institute for Biological Cybernetics',
      'MSc, Computational Neuroscience, University of Tübingen; Max Planck Institute for Biological Cybernetics',
    ],
    interests: [
      'Using machine learning and AI methods to discover universal laws of behaviour',
      'Meta-learning and behaviour-conditioned program synthesis for modelling human behaviour',
      'Agentic AI discovery harnesses that work alongside behavioural datasets spanning tasks, domains, and populations',
    ],
  },
];

export const speakerById = Object.fromEntries(speakers.map((s) => [s.id, s]));
export const photo = (s) => (s.noPhoto ? null : img(`speakers/${s.id}.jpg`));

// Institution logo per speaker; speakers without one fall back to the affiliation as text.
const LOGOS = {
  feng: 'stanford',
  gobet: 'lse',
  manning: 'mit',
  jin: 'penn',
  peters: 'ucl',
  noichl: 'utrecht',
  bishop: 'oxford',
  thompson: 'oxford',
  jagadish: 'princeton',
  sabatelli: 'groningen',
};
export const logo = (s) => (LOGOS[s.id] ? img(`logos/${LOGOS[s.id]}.png`) : null);
export const initials = (name) =>
  name
    .replace(/^(Prof\.|Dr\.)\s*/, '')
    .split(/\s+/)
    .map((w) => w[0])
    .slice(0, 2)
    .join('');

// Registration runs on Luma, one event per day. Set `lumaUrl` (the public event link) and `lumaEventId`
// (evt-..., from the event's embed settings) to switch that day's button from "opens soon" to live.
// title: null renders as "Title TBC"; speaker: null renders as "Speaker TBC".
// Add `abstract: '...'` (3-4 sentences) to a session to fill the + panel under the talk title in the
// speaker bio; without it the panel reads "Abstract to be announced."
export const days = [
  {
    id: 'day1',
    label: 'Session Day 1',
    date: 'Fri 23 Oct',
    dateLong: 'Friday 23 October 2026',
    lumaUrl: null,
    lumaEventId: null,
    sessions: [
      { start: '12:30', end: '13:30', speaker: 'feng', title: null },
      { start: '13:45', end: '14:45', speaker: 'gobet', title: 'Impact of AI on Human Expertise: Canaries in the Coalmine' },
      { start: '15:00', end: '16:00', speaker: 'manning', title: 'Predicting and Understanding Human Behaviour with AI Simulations' },
    ],
  },
  {
    id: 'day2',
    label: 'Session Day 2',
    date: 'Fri 6 Nov',
    dateLong: 'Friday 6 November 2026',
    lumaUrl: null,
    lumaEventId: null,
    sessions: [
      { start: '09:15', end: '10:15', speaker: 'jin', title: 'Beyond the Right Answer: Measuring Machine and Human Understanding' },
      { start: '10:30', end: '11:30', speaker: 'peters', title: null },
      { start: '11:30', end: '12:30', kind: 'lunch' },
      { start: '12:30', end: '13:30', speaker: 'noichl', title: 'Uncovering the general structure of model transfer between sciences' },
      { start: '13:45', end: '14:45', speaker: 'bishop', title: null },
      { start: '15:00', end: '16:00', speaker: 'sabatelli', title: null },
    ],
  },
  {
    id: 'day3',
    label: 'Session Day 3',
    date: 'Fri 13 Nov',
    dateLong: 'Friday 13 November 2026',
    lumaUrl: null,
    lumaEventId: null,
    sessions: [
      { start: '12:30', end: '13:30', speaker: 'thompson', title: null },
      { start: '13:45', end: '14:45', speaker: 'jagadish', title: 'Are LLMs the beginning or end of Cognitive Science?' },
      { start: '15:00', end: '16:00', speaker: null, title: null },
    ],
  },
];

export const scheduleNote =
  'Preliminary schedule. Speaker dates are confirmed; session times (UK time) are indicative and subject to change. There is a 15-minute break between consecutive talks.';

export const fmtTime = (t) => t.replace(/^0/, '');
