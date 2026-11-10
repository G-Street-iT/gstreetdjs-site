# gstreetdjs.com: notes for Claude

Website for G Street DJs LLC (owner/DJ: Tony, "Tony Spinning G"). Service area: Fort Wayne,
Avilla, Auburn and Chicago. Wording must never make the business sound small or limited.

## How the site works
- One page: `index.html` (inline CSS and JS). Photos live in `assets/`. Also `sitemap.xml`, `robots.txt`, `CNAME`.
- Hosted on GitHub Pages from `main`. Merging to `main` deploys in about 2–4 minutes. Pages runs Jekyll,
  which skips dot-folders, so this `.claude/` folder is not published.
- Work on a branch, open a PR, and let Tony check the preview before merging. When Tony asks to
  "update" or "put it live", merge.

## Photos: the house rules (agreed with Tony, Nov 2026)
Use `.claude/tools/addphoto.py` for all of this (see its header for usage). It needs `pip install pillow piexif`.

- **File names:** `g-street-djs-tony-spinning-g-<event-type>-<4 random digits>.jpg`,
  e.g. `...-wedding-dj-4830.jpg`, `...-parkview-field-dj-1936.jpg`. Every photo carries both names.
- **Tag only what the photo shows.** Ask Tony what the event was if it isn't clear; don't guess.
  Keyword stuffing hurts. Don't name a venue unless Tony confirms it (e.g. he wasn't sure about an Elks Lodge).
- **Alt text** leads with the event type ("Wedding DJ: …"). Google uses this most, so it matters more than
  the metadata keywords.
- **Metadata inside each file:** title "G Street DJs - Tony Spinning G - <type>", description = alt text,
  artist "Tony Spinning G - G Street DJs", copyright "G Street DJs LLC", keywords = brand + event types +
  area terms. Never keep camera or GPS data.
- **Size:** 697 px tall, JPEG quality ~80, roughly 50–150 KB.
- **Logos:** G Street seal + Tony Spinning G "G", 13% of photo height with a 3% margin, in whichever corner
  reads most clearly (the script scores corners; Tony is fine with any corner as long as both logos are
  clearly visible). On a light background add `--halo`. Stamp from the clean original, never twice.
- **Captions sit right next to the logos.** CSS positions them from the logo corner (`logo-xx` class,
  16% offset). If the caption would cover a face, use `--cap` to give it its own corner (done for
  "Tony on the decks at a Sweet 16" and "Halloween night on the decks").
- **Gallery list format** (in `index.html`, `const PHOTOS`):
  `["file.jpg", "Caption", "Alt text", "logo corner", "optional caption corner"]`. Keep related event
  types next to each other.
- **sitemap.xml** lists every photo as an `<image:image>` entry. Keep it in step with the gallery.
- Remind Tony to check that families are OK with photos showing minors' faces or names on signs.

## Check before every merge
- Every `assets/...jpg` referenced in `index.html` exists, and `sitemap.xml` parses.
- Load the page in Playwright at about 1280 and 390 px wide: no 404s, no console errors, and gallery
  photos don't overflow the track on phones. Screenshot new photos to check logo and caption placement.
  (Phone screenshots can look zoomed because of the hover effect; real phones don't show it.)

## Confirmed photo facts
- Packed ballroom reception (8652) and the red/yellow banquet hall dance floor (1517): weddings.
- Lavender gown photo (4871): Quinceañera only. Don't tag it Sweet 16.
- Ballpark suite (3972) and the setup room (1936): Parkview Field, home of the Fort Wayne TinCaps.
- Backyard BBQ (7038) replaced the old dark "outdoor tent party" photo.
- Live stream studio (4820): one of Tony's studios, used for webcam/online DJ shows. It's the same room
  as the "DJ booth" close-up (5508).

## Still to do
Tony is looking for clearer originals of these four. They still have the old "TONY spinning G" text
watermark and no logos. When he sends one, swap it in with
`addphoto.py NEW.jpg --replace <slug-number>`, which keeps the existing name and tags:
- Club night: `club-dj-3608`
- DJ booth decks: `mobile-dj-5508` (could be dropped instead, since the studio photo shows the same room)
- Reception in full swing: `wedding-dj-7771`
- Dance floor from the booth (pink lights): `party-dj-7968`
