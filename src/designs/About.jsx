import './about.css';
import { series, intro, summary, img } from '../data.js';

// Magazine-style spread: a detail of the key art beside the essay.
export default function About() {
  return (
    <section className="cv-wrap cv-about ab" id="about">
      <div className="ab-art" style={{ backgroundImage: `url(${img('keyart.jpg')})` }} role="img" aria-label="Detail of the painting: brushstrokes and painted numbers streaming from the sitter's head">
        <span className="cv-mark cv-mark-dark">{series.code}</span>
      </div>
      <div className="ab-body">
        <p className="cv-kicker">About the series</p>
        <h2 className="ab-question">{series.question}</h2>
        <div className="ab-essay">
          {intro.map((p) => <p key={p.slice(0, 24)}>{p}</p>)}
        </div>
        <p className="ab-pull">
          <span className="cv-mark">{summary}</span>
        </p>
      </div>
    </section>
  );
}
