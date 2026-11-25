import type {Brand, Reel} from '../types';

// Brand kit, from the live site's own system (2026-08-01 design audit):
// near-black base, saffron accent, cream text; Playfair Display + Inter.
export const brand: Brand = {
  name: 'Desi Meal',
  handle: '', // TODO: real Instagram handle — leave empty until confirmed
  colors: {bg: '#15110D', accent: '#F2A516', text: '#F6EBDA', muted: '#B9A88F'},
  displayFont: 'Playfair Display',
  bodyFont: 'Inter',
};

// Copy uses only facts the live site states: halal (no exceptions), tiffin meal
// plans, catering with a 3-step quote process, ordering through delivery apps,
// open 7 days 12–9 PM. No invented dishes, prices or claims.
export const reels: Reel[] = [
  {
    id: 'tiffin',
    title: 'Tiffin plans — the lunch problem',
    hooks: [
      {id: 'a', text: 'Stop eating sad desk lunches.', shot: 'Sad sandwich at a desk → push in', media: 'hook-desk.mp4'},
      {id: 'b', text: 'Home-cooked desi food. Without the cooking.', shot: 'Lid lifting off a steaming tiffin', media: 'hook-tiffin.mp4'},
      {id: 'c', text: 'POV: lunch is sorted for the whole week.', shot: 'Stack of tiffins being packed', media: 'hook-stack.mp4'},
    ],
    scenes: [
      {text: 'Real home-style desi meals', shot: 'Close-up: curry being ladled, steam visible', media: 'tiffin-1.mp4', seconds: 2.6},
      {text: 'Made fresh. Packed in a tiffin.', shot: 'Hands packing containers', media: 'tiffin-2.mp4', seconds: 2.6},
      {text: '100% halal. No exceptions.', shot: 'Full spread on the counter, top-down', media: 'tiffin-3.jpg', seconds: 2.6},
      {text: 'Pick a weekly meal plan', shot: 'Customer opening a tiffin at work', media: 'tiffin-4.mp4', seconds: 2.6},
    ],
    cta: {line: 'Your lunches, handled.', action: 'Tiffin plans · link in bio'},
  },
  {
    id: 'catering',
    title: 'Catering — the easy way to feed a crowd',
    hooks: [
      {id: 'a', text: 'Feeding 50 people this month?', shot: 'Wide: catering trays lined up', media: 'hook-trays.mp4'},
      {id: 'b', text: 'The easiest party you’ll ever host.', shot: 'Guests reaching for food, laughing', media: 'hook-party.mp4'},
      {id: 'c', text: 'Your aunties will ask who catered.', shot: 'Slow pan across a full buffet', media: 'hook-buffet.mp4'},
    ],
    scenes: [
      {text: '① Send your date + guest count', shot: 'Phone typing a message (over-shoulder)', media: 'cater-1.mp4', seconds: 2.6},
      {text: '② Choose your menu', shot: 'Chef plating several dishes', media: 'cater-2.mp4', seconds: 2.6},
      {text: '③ We cook. You host.', shot: 'Trays loaded into the car / set on tables', media: 'cater-3.mp4', seconds: 2.6},
      {text: 'Halal. Home-style. Made for a crowd.', shot: 'Hero shot of the full spread', media: 'cater-4.jpg', seconds: 2.6},
    ],
    cta: {line: 'Get your catering quote.', action: 'DM us or tap the link in bio'},
  },
  {
    id: 'craving',
    title: 'Everyday craving — order tonight',
    hooks: [
      {id: 'a', text: 'Craving desi food at 9 PM? We’re open.', shot: 'Night exterior / sign lit up', media: 'hook-night.mp4'},
      {id: 'b', text: 'This is your sign to skip cooking tonight.', shot: 'Slow-mo pour or tear of bread', media: 'hook-pour.mp4'},
      {id: 'c', text: 'Halal. No exceptions. Ever.', shot: 'Kitchen action, flame or tadka sizzle', media: 'hook-sizzle.mp4'},
    ],
    scenes: [
      {text: 'Cooked fresh, every day', shot: 'Tadka sizzle in a pan', media: 'craving-1.mp4', seconds: 2.4},
      {text: 'Home-style. Never fast-food.', shot: 'Plate being finished, garnish dropped', media: 'craving-2.mp4', seconds: 2.4},
      {text: 'Open 7 days · 12–9 PM', shot: 'Counter / storefront, staff smiling', media: 'craving-3.jpg', seconds: 2.4},
      {text: 'On your favourite delivery app', shot: 'Bag handed over at the door', media: 'craving-4.mp4', seconds: 2.4},
    ],
    cta: {line: 'Dinner’s sorted.', action: 'Order now · link in bio'},
  },
];
