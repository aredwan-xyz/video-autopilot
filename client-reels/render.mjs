// Render every reel × hook for a client to out/<client>/<reel>-<hook>.mp4
//   node render.mjs desi-meal            all reels
//   node render.mjs desi-meal tiffin     one reel, all hooks
import fs from 'node:fs';
import path from 'node:path';
import {bundle} from '@remotion/bundler';
import {getCompositions, renderMedia, selectComposition} from '@remotion/renderer';

const [client = 'desi-meal', only] = process.argv.slice(2);
const root = path.dirname(new URL(import.meta.url).pathname);
const mediaDir = path.join(root, 'public', client);
const available = fs.existsSync(mediaDir)
  ? fs.readdirSync(mediaDir).filter((f) => /\.(jpe?g|png|webp|mp4|mov|webm)$/i.test(f))
  : [];
console.log(`${client}: ${available.length} media file(s) found in public/${client}/`);

const serveUrl = await bundle({entryPoint: path.join(root, 'src/index.ts')});
const inputProps = {mediaByClient: {[client]: available}};
const outDir = path.join(root, 'out', client);
fs.mkdirSync(outDir, {recursive: true});

const ids = (await getCompositions(serveUrl, {inputProps})).map((c) => c.id);
const targets = ids.filter((id) => id.startsWith(`${client}-`) && (!only || id.startsWith(`${client}-${only}-`)));

for (const id of targets) {
  const composition = await selectComposition({serveUrl, id, inputProps});
  const file = path.join(outDir, `${id.slice(client.length + 1)}.mp4`);
  await renderMedia({
    composition, serveUrl, codec: 'h264', outputLocation: file, inputProps,
    crf: 18, pixelFormat: 'yuv420p', // Meta-safe H.264
  });
  console.log('✓', path.relative(root, file));
}
console.log(`done: ${targets.length} reel(s) → out/${client}/`);
