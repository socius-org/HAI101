// All page content lives here.

export const img = (p) => `${import.meta.env.BASE_URL}img/${p}`;

export const series = {
  code: 'HAI101',
  title: 'Human x Artificial Intelligence',
  tagline:
    'A lecture series spanning the social, behavioural, cognitive sciences, philosophy, and AI.',
  question: 'What can machines teach us about minds?',
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

// Venues, keyed by building code. days[].venue below names the key for each day.
// mapPin is the label's position on img/lse-campus-map.svg, as % of its width/height.
export const venues = {
  mar: {
    name: 'Marshall Building',
    code: 'MAR',
    room: 'MAR 2.06',
    address: "44 Lincoln's Inn Fields, London WC2A 3LY",
    mapsUrl: 'https://www.google.com/maps/search/?api=1&query=Marshall+Building%2C+44+Lincoln%27s+Inn+Fields%2C+London+WC2A+3LY',
    mapsEmbedUrl: 'https://www.google.com/maps?q=Marshall+Building%2C+44+Lincoln%27s+Inn+Fields%2C+London+WC2A+3LY&z=17&output=embed',
    mapPin: { x: 39.8, y: 41 },
  },
  lak: {
    name: 'Lakatos Building',
    code: 'LAK',
    room: 'LAK 2.06',
    address: '7 Portugal Street, London WC2A 2HJ',
    mapsUrl: 'https://www.google.com/maps/search/?api=1&query=Lakatos+Building%2C+7+Portugal+Street%2C+London+WC2A+2HJ',
    mapsEmbedUrl: 'https://www.google.com/maps?q=Lakatos+Building%2C+7+Portugal+Street%2C+London+WC2A+2HJ&z=17&output=embed',
    mapPin: { x: 50.2, y: 54.5 },
  },
};

export const campus = { map: 'lse-campus-map.svg' };

export const intro = [
  'Machines have become good enough at imitating people that researchers now use them as stand-ins: to run an experiment before recruiting a single participant, to predict how a group will behave, or to test a theory at a scale no human study could reach. At the same time, the machines have become something to study in their own right. They learn in ways that resemble ours, they explain themselves and assess their own answers, and they have started to do science. And the questions we once asked only of people are now being asked of machines.',
];

export const summary =
  'HAI101 brings twelve researchers from the social, behavioural and cognitive sciences, philosophy and AI to ask what machines that stand in for people can teach us about minds, and what the study of minds can teach the machines.';

export const speakers = [
  {
    id: 'oh',
    name: 'Nick Oh',
    role: 'Researcher, CPNSS',
    affiliation: 'London School of Economics',
    lab: 'Advisor: Prof. Fernand Gobet',
    previously: [
      'MSc Data Science and Artificial Intelligence, University of London',
      'BSc Politics and Economics, London School of Economics',
      'Ministry of National Defence, Numen Capital',
    ],
    interests: [
      'Neural networks, from RNNs to LLMs, as cognitive proxies',
      'Testing social-scientific theories at scales impossible with human subjects',
      'Latent-space representation; measuring and steering “feelings” and “beliefs” in machines',
    ],
  },
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
    publications: [
      ['The Dynamics of Quasiregular Neural Learning', 'Sabatelli, 2026'],
      ['Trace-Mediated Peak Bias: An Optimization Perspective on Temporal Credit Assignment', 'Sabatelli, 2026'],
      ['The Deep Quality-Value Family of Deep Reinforcement Learning Algorithms', 'Sabatelli et al., 2020'],
      ['Fisher-Guided Selective Forgetting: Mitigating the Primacy Bias in Deep Reinforcement Learning', 'Falzari & Sabatelli, 2025'],
      ['On the Transferability of Deep-Q Networks', 'Sabatelli & Geurts, 2021'],
    ],
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
    interests: [
      'Computational modelling of human learning, in individuals and in groups',
      'AI alignment and behavioural cloning',
      'Collective intelligence and metascience',
    ],
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
    name: 'Gabrielle Kaili-May Liu (Kaili)',
    role: 'PhD Candidate, Dept. of Computer Science',
    affiliation: 'Yale University',
    lab: 'Yale NLP Lab (PI: Prof. Arman Cohan)',
    previously: [
      'S.B., Mathematics with Computer Science and S.B., Brain and Cognitive Sciences, MIT',
      'Google Research, HLTCOE (Human Language Technology Center of Excellence) at Johns Hopkins University, National Taiwan University',
    ],
    interests: [
      'Metacognition in LLMs: understanding, improving and extending LLM capabilities by drawing inspiration from metacognition',
      'LLM reliability: enabling models to accurately self-assess and faithfully communicate their uncertainty, capabilities and knowledge limits',
      'LLM post-training and evaluation, and recipes for synthetic data generation',
    ],
  },
];

export const speakerById = Object.fromEntries(speakers.map((s) => [s.id, s]));
export const photo = (s) => (s.noPhoto ? null : img(`speakers/${s.id}.jpg`));

// Institution logo per speaker; speakers without one fall back to the affiliation as text.
const LOGOS = {
  feng: 'stanford',
  oh: 'lse',
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
// kind: 'lunch' renders a break; kind: 'intro' is a short opening slot, shown like a talk but not counted as one.
// venue: a key of `venues` above; null renders as "Venue TBC".
// title: null renders as "Title TBC"; speaker: null renders as "Speaker TBC".
// Add `abstract: '...'` to a session to fill the + panel under the talk title in the
// speaker bio; without it the panel reads "Abstract to be announced."
export const days = [
  {
    id: 'day1',
    label: 'Session Day 1',
    date: 'Fri 23 Oct',
    dateLong: 'Friday 23 October 2026',
    venue: 'mar',
    lumaUrl: 'https://luma.com/event/evt-I1pFNdYeOAz79AL',
    lumaEventId: 'evt-I1pFNdYeOAz79AL',
    sessions: [
      {
        start: '10:00', end: '10:15', speaker: 'oh', kind: 'intro', title: 'Introduction to HAI101',
        abstract: 'A short welcome and an outline of the series: the question behind it, and how the three Fridays fit together.',
      },
      {
        start: '10:30', end: '11:30', speaker: 'feng', title: 'The Developing Language Model: How Experience Shapes Learning and Failure',
        abstract: "Language models are usually evaluated as finished systems, but many questions about intelligence are fundamentally developmental: How does the structure of experience shape what is learned? Does accumulating knowledge change how efficiently new information can be acquired? And as models continue to train, which behaviours remain stable, and which depend on the particular path learning takes? I will present a series of studies that use language models as controlled learners to investigate these questions. First, I will examine language learning at unusually small data scales, including how the source and composition of linguistic input, bilingual experience, and the amount and diversity of developmental language affect prediction, grammatical knowledge, and semantic representations. I will then show ongoing work asking whether prior linguistic experience changes the marginal value of new evidence: the same novel-word examples become increasingly useful as a model acquires more language experience. In the second half, I will turn from learning to failure. I will briefly discuss how we can define and measure hallucination in controlled reference worlds, then focus on reinforcement-learning experiments showing that models with similar task performance can differ dramatically in whether they acknowledge their failures. Small numerical or stochastic differences during training can produce very different reporting behaviour, while reference anchoring can substantially reduce this variability. Together, these results motivate studying language models not only by what they can do at the end of training, but as developing systems whose learning history shapes both how they use information and how they behave when things go wrong.",
      },
      { start: '11:30', end: '12:30', kind: 'lunch' },
      {
        start: '12:30', end: '13:30', speaker: 'oh', title: 'Neural Networks as Behavioural and Cognitive Proxy',
        abstract: "Neural networks trained on human behavioural data have become instruments of cognitive science. They tell us how much of behaviour is predictable at all, they show where our interpretable models fall short, and lately they have been proposed as general models of cognition. I will first trace how this came about: from networks fitted to a single kind of behaviour, such as gambles, chess moves, reward learning or reading times, to models that imitate individual players or participants, to language models fine-tuned on data from many experiments at once and offered as general-purpose models of cognition. Along the way I will point to the questions the field is still working out, including what such a model has to get right before it counts as a model of the mind. I will then present one recent example from my own work, in which we fine-tuned fourteen language models, from 135M to 14B parameters, on ten million choices from 160 psychology experiments. The results suggest that on familiar tasks scale barely matters, that size buys transfer to novel tasks, and that the models rely on what participants saw rather than on the shape of the prompt.",
      },
      {
        start: '13:45', end: '14:45', speaker: 'gobet', title: 'Impact of AI on Human Expertise: Canaries in the Coalmine',
        abstract: "This talk argues that chess offers a unique preview of how AI may transform human expertise because superhuman chess AI has existed for more than 25 years. Drawing on this long-term case study, it identifies ten major effects of AI, including surpassing expert performance, reshaping training and decision-making, and generating new knowledge. Many of these patterns are already emerging in fields such as medicine, education, software engineering, and mathematics. AI does not make human experts obsolete; instead, expertise increasingly involves selecting appropriate AI tools, interpreting and evaluating AI outputs, and applying contextual, ethical, and practical judgement.",
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
    venue: 'lak',
    lumaUrl: 'https://luma.com/event/evt-DpbtUKkcgxBm8nM',
    lumaEventId: 'evt-DpbtUKkcgxBm8nM',
    sessions: [
      {
        start: '09:15', end: '10:15', speaker: 'jin', title: 'Beyond the Right Answer: Measuring Machine and Human Understanding',
        abstract: "What does it mean to truly understand something, rather than simply produce the right answer? As AI systems become increasingly capable of explaining, reasoning, and producing and evaluating knowledge, that distinction is becoming both harder and more important to make. This talk asks what should count as evidence of understanding in an age of increasingly capable AI. It considers how we evaluate the explanations and reasoning produced by machines, before turning the question back on us: when AI can produce the essays, solutions, and code we once used to judge human understanding, how should we assess what a person actually knows?",
      },
      { start: '10:30', end: '11:30', speaker: 'peters', title: null },
      { start: '11:30', end: '12:30', kind: 'lunch' },
      {
        start: '12:30', end: '13:30', speaker: 'noichl', title: 'Uncovering the general structure of model transfer between sciences',
        abstract: "An interesting fact about science is that it is quite common for similar models to appear in a variety of domains and disciplines. Some classic examples: the Kuramoto model describes chemicals, neurons and the flashing of fireflies; the Lotka-Volterra models have been applied to fish stocks in the Mediterranean, chemical reactions and labour markets; and a variety of game-theoretic and network models have been applied across many disciplines. Philosophers of science have become increasingly interested in this fact, identifying the phenomenon of model transfer as a key motor of scientific creativity, or even as a deep organising principle of science itself. But what does its organisational structure look like? Is there one place in science where models tend to come from, or pass through, before they are reapplied in other places? In the present contribution we start out by building a background mapping of the sciences based on a large, random sample from the OpenAlex database. Onto this mapping we can project smaller samples from the database to show their distribution and dissemination (see a work-in-progress interactive version at https://huggingface.co/spaces/MaxNoichl/oa-atlas). Using an AI-driven, autonomous research workflow, we generate a number of such samples corresponding to histories of individual cases of model transfer, and use citation network analysis to reconstruct the routes through which these models spread between disciplines over time. We present first results about the degree to which general patterns emerge, and discuss their implications in an increasingly AI-driven scientific environment.",
      },
      { start: '13:45', end: '14:45', speaker: 'bishop', title: null },
      {
        start: '15:00', end: '16:00', speaker: 'sabatelli', title: 'When Machines Learn Like Us: Cognitive-Like Phenomena in Neural Learning',
        abstract: "Human learning is full of surprising patterns. We sometimes become worse before getting better, and our judgements can be disproportionately influenced by particularly salient moments. Intriguingly, similar behavioural signatures can also emerge in neural networks. In this talk, I will present two examples. First, I will show how neural networks learning a dominant regularity alongside systematic exceptions can exhibit U-shaped learning: they initially learn the exceptions, subsequently regress towards the general rule, and only later recover. Second, I will introduce Trace-Mediated Peak Bias, a phenomenon in reinforcement learning in which an agent can learn to prefer an objectively worse experience because it contains a particularly large reward. Using controlled experiments, we can trace these effects to competition between regularities and exceptions, the propagation of reward information through time, and the way gradient updates reshape shared neural representations. These results show how cognitive-like behaviour can arise from ordinary neural learning dynamics, without requiring the networks to possess the cognitive processes usually associated with that behaviour.",
      },
    ],
  },
  {
    id: 'day3',
    label: 'Session Day 3',
    date: 'Fri 13 Nov',
    dateLong: 'Friday 13 November 2026',
    venue: 'lak',
    lumaUrl: 'https://luma.com/event/evt-mPTzB9JGAPIOL1o',
    lumaEventId: 'evt-mPTzB9JGAPIOL1o',
    sessions: [
      {
        start: '12:30', end: '13:30', speaker: 'thompson', title: 'Behavioural Clones as Scientific Instruments: Machine-Learned Curricula and the Future of Discovery in the Behavioural Sciences',
        abstract: "I will introduce a new methodology and preliminary results from a line of research using behavioural cloning to discover effective curricula for human learning. Our pipeline has four stages: (1) collect data from people learning under a diverse set of curricula; (2) train neural networks to mimic individual learners (“behavioural clones”); (3) train AI teachers, using reinforcement learning, to optimise curricula for these simulated learners; and (4) test the resulting teaching policies on new groups of human learners. This work is a proof of principle for a broader approach, enabled by modern machine learning, that could substantially change how discoveries are made in the behavioural sciences and how behavioural interventions are designed. I will discuss the promise and perils of this approach and of related methods now spreading across science and industry, including questions such as what counts as a discovery when an optimiser finds what works but not why.",
      },
      {
        start: '13:45', end: '14:45', speaker: 'jagadish', title: 'Are LLMs the Beginning or End of Cognitive Science?',
        abstract: "Large Language Models (LLMs) are demonstrating remarkable capabilities across the sciences. In less than a year, they have gone from winning International Olympiads to generating proofs for a Millennium Prize problem. For cognitive science, this raises an uncomfortable question: if the system can do the science, what kind of science is left to do? I will argue the opposite of the supposedly obvious conclusion — that LLMs mark the beginning of a new era of cognitive science rather than its end. I will preview three pieces of work in which LLMs serve as a key instrument: (1) as generators of realistic data, enabling tests of ecological rationality; (2) as systems for model discovery, supporting mechanistic insights from rich sources of behaviour; (3) as curators of large-scale behavioural datasets, enabling the search for universal laws of behaviour. Each removes a bottleneck that used to determine which questions were “askable”. Far from closing doors, I believe LLMs put within reach a set of questions that were previously deemed unreachable, making it the best time yet to be doing cognitive science.",
      },
      {
        start: '15:00', end: '16:00', speaker: 'liu', title: 'Reliable Language Models Through the Lens of Metacognition',
        abstract: "Metacognition is a core component of intelligence that describes the ability to monitor and regulate one’s own cognitive processes. Yet even the most capable LLMs continue to exhibit systemic deficiencies in key metacognitive faculties: they hallucinate with high confidence, fail to recognise knowledge boundaries, and misrepresent their internal uncertainty, undermining trustworthiness and reliability. In this talk, we will explore how principles of metacognition from the field of psychology can be leveraged to improve the performance and reliability of modern language generation systems. In particular, I will show how metacognitive methods (prompting, training) can be devised to teach LLMs to accurately gauge their own task performance and internal uncertainty levels and communicate these to humans in a faithful, assistive fashion. Such work opens the door to more transparent and interpretable systems, and has implications for improved alignment and self-directed learning.",
      },
    ],
  },
];

export const fmtTime = (t) => t.replace(/^0/, '');
