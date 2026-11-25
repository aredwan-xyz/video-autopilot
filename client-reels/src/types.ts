export type Brand = {
  name: string;
  handle: string; // shown on the end card; "" hides it
  colors: {bg: string; accent: string; text: string; muted: string};
  displayFont: 'Playfair Display';
  bodyFont: 'Inter';
};

export type Scene = {
  /** On-screen line. Keep it under ~8 words: it is read, not heard. */
  text: string;
  /** What footage belongs here. Shown on the stand-in until real media exists. */
  shot: string;
  /** File name in public/<client>/ (jpg/png/mp4/mov). Missing file => stand-in. */
  media?: string;
  seconds: number;
};

export type Reel = {
  id: string;
  title: string;
  /** One reel, several opening lines: each renders as its own MP4 for A/B testing. */
  hooks: {id: string; text: string; shot: string; media?: string}[];
  scenes: Scene[];
  cta: {line: string; action: string};
};
