import './about.css';
import { series, intro, summary, img } from '../data.js';

// Magazine-style spread: the "mechanised thinking" plate beside the essay.
export default function About() {
  return (
    <section className="cv-wrap cv-about ab" id="about">
      <div className="ab-art" style={{ backgroundImage: `url(${img('mechanised_thinking.jpg')})` }} role="img" aria-label="Antique engraving of a human brain, annotated with dotted arcs, letters and red arrows like a diagram of a machine" />
      <div className="ab-body">
        <p className="cv-kicker">About the series</p>
        <h2 className="ab-question">{series.question}</h2>
        <div className="ab-essay">
          {intro.map((p) => <p key={p.slice(0, 40)}>{p}</p>)}
        </div>
        <p className="ab-pull">
          <span className="cv-mark">{summary}</span>
        </p>
      </div>
    </section>
  );
}
