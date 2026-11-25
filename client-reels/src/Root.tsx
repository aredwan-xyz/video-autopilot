import React from 'react';
import {Composition, getInputProps} from 'remotion';
import {FPS, Reel, reelSeconds, type ReelProps} from './Reel';
import {CLIENTS} from './clients';

// render.mjs passes the list of media files that exist on disk; the studio
// shows stand-ins for everything.
// (Named `mediaByClient`, not `available`: input props are merged into every
// composition's props, so the names must not collide.)
const {mediaByClient: available = {}} = getInputProps() as {mediaByClient?: Record<string, string[]>};

export const Root: React.FC = () => (
  <>
    {Object.entries(CLIENTS).flatMap(([client, {brand, reels}]) =>
      reels.flatMap((reel) =>
        reel.hooks.map((h) => (
          <Composition<any, ReelProps>
            key={`${client}-${reel.id}-${h.id}`}
            id={`${client}-${reel.id}-${h.id}`}
            component={Reel}
            width={1080}
            height={1920}
            fps={FPS}
            durationInFrames={Math.round(reelSeconds(reel) * FPS)}
            defaultProps={{client, brand, reel, hookId: h.id, available: available[client] ?? []}}
          />
        )),
      ),
    )}
  </>
);
