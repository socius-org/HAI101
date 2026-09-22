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
  hostUrl: 'https://www.lse.ac.uk/cpnss',
  institution: 'London School of Economics and Political Science',
  dates: 'Fridays · 23 Oct, 6 Nov & 13 Nov 2026',
  datesShort: '23 Oct · 6 Nov · 13 Nov 2026',
  location: 'LSE, London',
  format: 'Hybrid',
  registration: 'Registration will open on Luma.',
};

// Confirmed venue for 6 & 13 Nov; 23 Oct is still to be confirmed (days[].venue below).
// mapPin is the LAK label's position on img/lse-campus-map.svg, as % of its width/height.
export const venue = {
  name: 'Lakatos Building',
  code: 'LAK',
  room: 'LAK 2.06',
  address: '7 Portugal Street, London WC2A 2HJ',
  mapsUrl: 'https://www.google.com/maps/search/?api=1&query=Lakatos+Building%2C+7+Portugal+Street%2C+London+WC2A+2HJ',
  mapsEmbedUrl: 'https://www.google.com/maps?q=Lakatos+Building%2C+7+Portugal+Street%2C+London+WC2A+2HJ&z=17&output=embed',
  campusMap: 'lse-campus-map.svg',
  mapPin: { x: 50.2, y: 54.5 },
};

export const intro = [
  'Cognitive science and artificial intelligence were born from that single question in the 1950s, and have pulled apart and back together ever since. They shared the symbolic era, split as AI turned statistical, rejoined through connectionism and Bayesian models of mind, and are now converging once more. The question is what is different this time.',
  'What is different is that the traffic runs both ways. The artificial human is now good enough to be used as an instrument, whether as an experimental subject, a model of a population or a proxy for people. And the machines no longer wait to be studied. They learn like us, explain, evaluate, and have begun to do science themselves.',
  'HAI 101 follows both directions, from what this instrument means for understanding minds and people to what such machines mean for how humans think, learn and know.',
];

export const summary =
  'HAI 101 brings together social, behavioural, cognitive sciences, philosophy, and artificial intelligence to explore the changing relationship between humans and machines. It asks how we model minds, how minds shape machines, and what happens when machines begin to model people, reason about the world, and produce knowledge themselves.';

export const speakers = [
  {
    id: 'feng',
    name: 'Steven Feng',
    role: 'PhD Candidate, Dept. of Computer Science',
    affiliation: 'Stanford University',
    lab: 'Language & Cognition Lab (PI: Prof. Michael Frank); Computation & Cognition Lab (PI: Prof. Noah Goodman)',
    previously: [
      'Anthropic Research Fellow',
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
    role: 'Assistant Professor, Faculty of Science and Engineering',
    affiliation: 'University of Groningen',
  },
  {
    id: 'thompson',
    name: 'Dr. Jessica Thompson',
    role: 'Postdoctoral Researcher, Dept. of Experimental Psychology',
    affiliation: 'University of Oxford',
    lab: 'Human Information Processing Lab (PI: Prof. Christopher Summerfield)',
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
    lab: 'Independent researcher in the Natural and Artificial Minds programme at the Princeton AI Lab',
    previously: [
      'PhD, Computer Science, University of Tübingen; Max Planck Institute for Biological Cybernetics',
      'MSc, Computational Neuroscience, University of Tübingen; Max Planck Institute for Biological Cybernetics',
    ],
    interests: [
      'Characterising determinants of human behaviour using meta-learning',
      'Discovering mechanisms underlying human behaviour using behaviour-conditioned symbolic program synthesis',
      'Uncovering universal laws of behaviour using agentic AI harnesses in conjunction with large-scale behavioural datasets',
    ],
  },
  {
    id: 'liu',
    name: 'Gabrielle Kaili-May Liu',
    role: 'PhD Candidate',
    affiliation: 'Yale University',
    lab: 'Yale NLP Lab (PI: Prof. Arman Cohan)',
    previously: [
      'S.B., Mathematics with Computer Science; S.B., Brain and Cognitive Sciences, MIT',
      'Google, Johns Hopkins University, National Taiwan University',
    ],
    interestsTbc: true,
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
  liu: 'yale',
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
// venue: true means the day is at `venue` above; null renders as "Venue TBC".
// title: null renders as "Title TBC"; speaker: null renders as "Speaker TBC".
// Add `abstract: '...'` to a session to fill the + panel under the talk title in the
// speaker bio; without it the panel reads "Abstract to be announced."
export const days = [
  {
    id: 'day1',
    label: 'Session Day 1',
    date: 'Fri 23 Oct',
    dateLong: 'Friday 23 October 2026',
    venue: null,
    lumaUrl: null,
    lumaEventId: null,
    sessions: [
      { start: '12:30', end: '13:30', speaker: 'feng', title: null },
      {
        start: '13:45', end: '14:45', speaker: 'gobet', title: 'Impact of AI on Human Expertise: Canaries in the Coalmine',
        abstract: "This talk argues that chess offers a unique preview of how AI may transform human expertise because superhuman chess AI has existed for more than 25 years. Drawing on this long-term case study, it identifies ten major effects of AI, including surpassing expert performance, reshaping training and decision-making, and generating new knowledge. Many of these patterns are already emerging in fields such as medicine, education, software engineering, and mathematics. AI does not make human experts obsolete; instead, expertise increasingly involves selecting appropriate AI tools, interpreting and evaluating AI outputs, and applying contextual, ethical, and practical judgment.",
      },
      {
        start: '15:00', end: '16:00', speaker: 'manning', title: 'Predicting and Understanding Human Behaviour with AI Simulations',
        abstract: "Useful social science theory should predict behaviour in settings it was never built for, yet applying a theory to a new setting almost always requires ad hoc modification. I will argue that AI agents placed in simulations offer an alternative. They provide a way of carrying theory into novel environments, and a new instrument for asking how much structure human behaviour really has. First, I will show how “general” agents can be built from theory-grounded natural language instructions and small amounts of existing human data, validated across distinct but related settings rather than by a standard train-test split. On a pre-committed population of 883,200 novel strategic games, such agents predict human play better than off-the-shelf agents, a cognitive hierarchy model, and game-theoretic equilibria. Second, I will show how prompts themselves can serve as a fittable, interpretable model of a person. Language models are assigned “type vectors” of trait intensities, which are then optimised against 119,147 decisions from 78,657 subjects across ten classic economic games. Three dimensions, Risk Aversion, Strategic Sophistication, and Trust, closely match human behaviour, and the fitted types cluster into fewer than a dozen groups that predict play in held-out games. Together, these results suggest AI simulations are not only a prediction technology, but a tool for discovering how few moving parts a theory of behaviour might need.",
      },
    ],
  },
  {
    id: 'day2',
    label: 'Session Day 2',
    date: 'Fri 6 Nov',
    dateLong: 'Friday 6 November 2026',
    venue: true,
    lumaUrl: null,
    lumaEventId: null,
    sessions: [
      {
        start: '09:15', end: '10:15', speaker: 'jin', title: 'Beyond the Right Answer: Measuring Machine and Human Understanding',
        abstract: "What does it mean to truly understand something, rather than simply produce the right answer? As AI systems become increasingly capable of explaining, reasoning, and producing and evaluating knowledge, that distinction is becoming both harder and more important to make. This talk asks what should count as evidence of understanding in an age of increasingly capable AI. It considers how we evaluate the explanations and reasoning produced by machines, before turning the question back on us: when AI can produce the essays, solutions, and code we once used to judge human understanding, how should we assess what a person actually knows?",
      },
      { start: '10:30', end: '11:30', speaker: 'peters', title: null },
      { start: '11:30', end: '12:30', kind: 'lunch' },
      { start: '12:30', end: '13:30', speaker: 'noichl', title: 'Uncovering the general structure of model transfer between sciences' },
      { start: '13:45', end: '14:45', speaker: 'bishop', title: null },
      {
        start: '15:00', end: '16:00', speaker: 'sabatelli', title: 'When Machines Learn Like Us: Cognitive-Like Phenomena in Neural Learning',
        abstract: "Human learning is full of surprising patterns. We sometimes become worse before getting better, and our judgments can be disproportionately influenced by particularly salient moments. Intriguingly, similar behavioural signatures can also emerge in neural networks. In this talk, I will present two examples. First, I will show how neural networks learning a dominant regularity alongside systematic exceptions can exhibit U-shaped learning: they initially learn the exceptions, subsequently regress towards the general rule, and only later recover. Second, I will introduce Trace-Mediated Peak Bias, a phenomenon in reinforcement learning in which an agent can learn to prefer an objectively worse experience because it contains a particularly large reward. Using controlled experiments, we can trace these effects to competition between regularities and exceptions, the propagation of reward information through time, and the way gradient updates reshape shared neural representations. These results show how cognitive-like behaviour can arise from ordinary neural learning dynamics, without requiring the networks to possess the cognitive processes usually associated with that behaviour.",
      },
    ],
  },
  {
    id: 'day3',
    label: 'Session Day 3',
    date: 'Fri 13 Nov',
    dateLong: 'Friday 13 November 2026',
    venue: true,
    lumaUrl: null,
    lumaEventId: null,
    sessions: [
      { start: '12:30', end: '13:30', speaker: 'thompson', title: null },
      {
        start: '13:45', end: '14:45', speaker: 'jagadish', title: 'Are LLMs the Beginning or End of Cognitive Science?',
        abstract: "Large Language Models (LLMs) are demonstrating remarkable capabilities across the sciences. In less than a year, they have gone from winning International Olympiads to generating proofs for a Millennium Prize problem. For cognitive science, this raises an uncomfortable question: if the system can do the science, what kind of science is left to do? I will argue the opposite of the supposedly obvious conclusion — that LLMs mark the beginning of a new era of cognitive science rather than its end. I will preview three pieces of work in which LLMs serve as a key instrument: (1) as generators of realistic data, enabling tests of ecological rationality; (2) as systems for model discovery, supporting mechanistic insights from rich sources of behaviour; (3) as curators of large-scale behavioural datasets, enabling the search for universal laws of behaviour. Each removes a bottleneck that used to determine which questions were “askable”. Far from closing doors, I believe LLMs put within reach a set of questions that were previously deemed unreachable, making it the best time yet to be doing cognitive science.",
      },
      { start: '15:00', end: '16:00', speaker: 'liu', title: null },
    ],
  },
];

export const scheduleNote =
  'Preliminary schedule. Speaker dates are confirmed; session times (UK time) are indicative and subject to change. There is a 15-minute break between consecutive talks.';

export const fmtTime = (t) => t.replace(/^0/, '');
