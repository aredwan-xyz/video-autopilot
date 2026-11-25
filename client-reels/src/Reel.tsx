import React from 'react';
import {
  AbsoluteFill, Img, OffthreadVideo, Sequence, interpolate, spring,
  staticFile, useCurrentFrame, useVideoConfig,
} from 'remotion';
import {loadFont as loadPlayfair} from '@remotion/google-fonts/PlayfairDisplay';
import {loadFont as loadInter} from '@remotion/google-fonts/Inter';
import type {Brand, Reel as ReelT} from './types';

const playfair = loadPlayfair('normal', {weights: ['700', '900'], subsets: ['latin']}).fontFamily;
const inter = loadInter('normal', {weights: ['500', '700'], subsets: ['latin']}).fontFamily;

export const FPS = 30;
export const HOOK_S = 2.4;
export const CTA_S = 2.8;

// Meta Reels UI covers roughly the top 250px and bottom ~420px of a 1920px frame,
// plus the action rail on the right. All text lives inside this box.
const SAFE = {top: 260, bottom: 440, side: 90, rightRail: 150};

export type ReelProps = {
  client: string;
  brand: Brand;
  reel: ReelT;
  hookId: string;
  available: string[]; // media files that actually exist in public/<client>/
};

export const reelSeconds = (r: ReelT) =>
  HOOK_S + r.scenes.reduce((s, x) => s + x.seconds, 0) + CTA_S;

const Media: React.FC<{client: string; file?: string; available: string[]; shot: string; brand: Brand; seed: number}> = (
  {client, file, available, shot, brand, seed},
) => {
  const frame = useCurrentFrame();
  const {durationInFrames} = useVideoConfig();
  const zoom = interpolate(frame, [0, durationInFrames], [1.04, 1.14]); // slow push-in keeps stills alive
  const shade = (
    <AbsoluteFill style={{background: 'linear-gradient(180deg, rgba(0,0,0,.35) 0%, rgba(0,0,0,.05) 35%, rgba(0,0,0,.55) 100%)'}} />
  );

  if (file && available.includes(file)) {
    const src = staticFile(`${client}/${file}`);
    const isVideo = /\.(mp4|mov|webm)$/i.test(file);
    return (
      <AbsoluteFill style={{overflow: 'hidden'}}>
        {isVideo
          ? <OffthreadVideo src={src} muted style={{width: '100%', height: '100%', objectFit: 'cover'}} />
          : <Img src={src} style={{width: '100%', height: '100%', objectFit: 'cover', transform: `scale(${zoom})`}} />}
        {shade}
      </AbsoluteFill>
    );
  }

  // Stand-in: on-brand moving gradient + the shot that belongs here, so the
  // client review doubles as a shot list.
  const drift = interpolate(frame, [0, durationInFrames], [0, 40]);
  const hue = seed % 2 === 0 ? brand.colors.accent : '#C2410C';
  return (
    <AbsoluteFill style={{background: brand.colors.bg, overflow: 'hidden'}}>
      <div style={{
        position: 'absolute', width: 1500, height: 1500, borderRadius: '50%',
        left: -300 + drift * 3, top: 500 - drift * 4, filter: 'blur(160px)', opacity: 0.55,
        background: `radial-gradient(circle, ${hue} 0%, transparent 65%)`,
      }} />
      <div style={{
        position: 'absolute', left: SAFE.side, right: SAFE.rightRail, top: SAFE.top + 30,
        fontFamily: inter, fontWeight: 700, fontSize: 30, letterSpacing: 4, textTransform: 'uppercase',
        color: brand.colors.muted, border: `2px dashed ${brand.colors.muted}66`, borderRadius: 18, padding: '18px 24px',
      }}>
        Footage · {shot}
      </div>
    </AbsoluteFill>
  );
};

const Caption: React.FC<{text: string; brand: Brand; size: number; serif: boolean}> = ({text, brand, size, serif}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const words = text.split(' ');
  return (
    <div style={{
      position: 'absolute', left: SAFE.side, right: SAFE.rightRail, top: 0, bottom: 0,
      paddingTop: SAFE.top, paddingBottom: SAFE.bottom,
      display: 'flex', alignItems: 'center', justifyContent: 'center', flexWrap: 'wrap', alignContent: 'center',
      gap: `0 ${size * 0.28}px`, textAlign: 'center',
    }}>
      {words.map((w, i) => {
        const s = spring({frame: frame - i * 3, fps, config: {damping: 14, stiffness: 180}});
        const highlight = i === words.length - 1;
        return (
          <span key={i} style={{
            display: 'inline-block', transform: `translateY(${(1 - s) * 40}px) scale(${0.85 + s * 0.15})`, opacity: s,
            fontFamily: serif ? playfair : inter, fontWeight: serif ? 900 : 700, fontSize: size, lineHeight: 1.08,
            color: highlight ? brand.colors.accent : brand.colors.text,
            textShadow: '0 4px 24px rgba(0,0,0,.65), 0 2px 4px rgba(0,0,0,.8)',
          }}>{w}</span>
        );
      })}
    </div>
  );
};

const EndCard: React.FC<{brand: Brand; line: string; action: string}> = ({brand, line, action}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const pop = spring({frame: frame - 10, fps, config: {damping: 12}});
  return (
    <AbsoluteFill style={{background: brand.colors.bg, alignItems: 'center', justifyContent: 'center', paddingBottom: SAFE.bottom - SAFE.top}}>
      <div style={{fontFamily: playfair, fontWeight: 900, fontSize: 96, color: brand.colors.accent, letterSpacing: -1}}>
        {brand.name}
      </div>
      <div style={{fontFamily: playfair, fontWeight: 700, fontSize: 60, color: brand.colors.text, marginTop: 28, textAlign: 'center', padding: '0 120px'}}>
        {line}
      </div>
      <div style={{
        marginTop: 56, transform: `scale(${pop})`, background: brand.colors.accent, color: brand.colors.bg,
        fontFamily: inter, fontWeight: 700, fontSize: 40, padding: '26px 48px', borderRadius: 999,
      }}>{action}</div>
      {brand.handle && <div style={{marginTop: 34, fontFamily: inter, fontSize: 34, color: brand.colors.muted}}>{brand.handle}</div>}
    </AbsoluteFill>
  );
};

export const Reel: React.FC<ReelProps> = ({client, brand, reel, hookId, available}) => {
  const frame = useCurrentFrame();
  const {durationInFrames} = useVideoConfig();
  const hook = reel.hooks.find((h) => h.id === hookId) ?? reel.hooks[0];
  let at = Math.round(HOOK_S * FPS);

  return (
    <AbsoluteFill style={{background: brand.colors.bg}}>
      <Sequence durationInFrames={at}>
        <Media client={client} file={hook.media} available={available} shot={hook.shot} brand={brand} seed={0} />
        <Caption text={hook.text} brand={brand} size={104} serif />
      </Sequence>
      {reel.scenes.map((sc, i) => {
        const from = at;
        const len = Math.round(sc.seconds * FPS);
        at += len;
        return (
          <Sequence key={i} from={from} durationInFrames={len}>
            <Media client={client} file={sc.media} available={available} shot={sc.shot} brand={brand} seed={i + 1} />
            <Caption text={sc.text} brand={brand} size={84} serif={false} />
          </Sequence>
        );
      })}
      <Sequence from={at}>
        <EndCard brand={brand} line={reel.cta.line} action={reel.cta.action} />
      </Sequence>
      {/* Progress bar at the top edge: the bottom is covered by the Reels UI. */}
      <div style={{position: 'absolute', top: 0, left: 0, height: 10, width: `${(frame / durationInFrames) * 100}%`, background: brand.colors.accent}} />
    </AbsoluteFill>
  );
};
