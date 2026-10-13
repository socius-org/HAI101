import { useEffect, useRef } from 'react';
import './about.css';
import { series, intro, summary, img } from '../data.js';

// Magazine-style spread: the rotating semantic map beside the essay. The map is a short looping
// video built by semantic-map/ (see its README).
export default function About() {
  const video = useRef(null);
  useEffect(() => {
    // Leave the poster frame for people who asked for less motion.
    if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) video.current?.pause();
  }, []);

  return (
    <section className="cv-wrap cv-about ab" id="about">
      <figure className="ab-art ab-map">
        <video
          ref={video}
          src={img('map/rotation.mp4')}
          poster={img('map/rotation.jpg')}
          autoPlay
          muted
          loop
          playsInline
          aria-label="Rotating 3D map of the speakers' published papers, each paper a dot coloured by speaker"
        />
        <figcaption>
          Every dot is one of the speakers' papers, coloured by speaker and placed by topic: abstracts from OpenAlex,
          embedded with the SPECTER2 scientific-text model and laid out in 3D by UMAP. Nearby dots are papers about
          similar things.
        </figcaption>
      </figure>
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
