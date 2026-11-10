#!/usr/bin/env python3
"""Add (or replace) a gallery photo on gstreetdjs.com the house way.

Resizes to 697 px tall, stamps the G Street seal + Tony Spinning G logo in the
clearest corner (or the one you pick), writes the SEO metadata into the file,
and adds the photo to the PHOTOS gallery list in index.html and to sitemap.xml.

Run from the repo root. Needs: pip install pillow piexif

New photo:
  python3 .claude/tools/addphoto.py SRC.jpg --slug wedding-dj \
    --caption "Line dance with the bride" \
    --alt "Wedding DJ: guests line dancing with the bride while Tony Spinning G mixes" \
    --title "Wedding DJ" --after wedding-dj-9254 \
    --keywords "Wedding DJ; Wedding reception DJ; Line dance"

Replace an existing photo with a clearer original (keeps its name, caption,
alt text and keywords; only the image and logos change):
  python3 .claude/tools/addphoto.py SRC.jpg --replace club-dj-3608

Options: --corner tl|tr|bl|br forces the logo corner. --halo adds a soft dark
shadow behind the logos for light backgrounds. --cap tl|tr|bl|br puts the caption
in its own corner (use it to keep a caption off someone's face).
"""
import argparse, os, random, re, sys
import piexif
from PIL import Image, ImageFilter, ImageOps, ImageStat

PREFIX = "g-street-djs-tony-spinning-g-"
BRAND = ["G Street DJs", "Tony Spinning G"]
AREA = ["DJ", "DJ services", "Fort Wayne DJ", "Auburn DJ", "Avilla DJ", "Chicago DJ", "Northeast Indiana DJ"]
H_MAX = 697          # gallery photos are 697 px tall
LOGO_H = 0.13        # logo height as a share of photo height
MARGIN = 0.03        # logo margin as a share of photo height (CSS assumes 3% + 13% = 16%)


def u16(s):
    return s.encode("utf-16le") + b"\0\0"


def pick_corner(im):
    """Lower score = darker and calmer = logos read best there."""
    W, H = im.size
    g = im.convert("L"); e = g.filter(ImageFilter.FIND_EDGES)
    bw, bh = int(H * 0.33), int(H * 0.24)
    boxes = {"bl": (0, H - bh, bw, H), "br": (W - bw, H - bh, W, H), "tl": (0, 0, bw, bh), "tr": (W - bw, 0, W, bh)}
    score = {c: ImageStat.Stat(g.crop(b)).mean[0] * 0.6 + ImageStat.Stat(e.crop(b)).mean[0] * 2.5 for c, b in boxes.items()}
    print("corner scores:", {k: round(v, 1) for k, v in score.items()})
    return min(score, key=score.get)


def stamp(im, corner, halo):
    W, H = im.size
    s, pad = int(H * LOGO_H), int(H * MARGIN); gap = int(pad * 0.5)
    logos = []
    for p in ("assets/gstreet-seal.webp", "assets/tony-g.webp"):
        lg = Image.open(p).convert("RGBA"); lg.thumbnail((s, s), Image.LANCZOS)
        if not halo:
            lg.putalpha(lg.getchannel("A").point(lambda v: int(v * 0.88)))
        logos.append(lg)
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    x = pad if corner[1] == "l" else W - pad - (sum(l.width for l in logos) + gap)
    for lg in logos:
        y = pad + (s - lg.height) // 2 if corner[0] == "t" else H - pad - s + (s - lg.height) // 2
        layer.alpha_composite(lg, (x, y)); x += lg.width + gap
    out = im.convert("RGBA")
    if halo:
        a = layer.getchannel("A").filter(ImageFilter.MaxFilter(9)).filter(ImageFilter.GaussianBlur(10)).point(lambda v: int(v * 0.75))
        shadow = Image.new("RGBA", (W, H), (15, 15, 15, 255)); shadow.putalpha(a); out.alpha_composite(shadow)
    out.alpha_composite(layer)
    return out.convert("RGB")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("src")
    ap.add_argument("--replace", help="existing photo to replace, e.g. club-dj-3608 (no prefix/extension)")
    ap.add_argument("--slug", help="event-type slug for a new photo, e.g. wedding-dj")
    ap.add_argument("--caption"); ap.add_argument("--alt"); ap.add_argument("--title")
    ap.add_argument("--after", help="insert after the gallery entry whose file contains this text")
    ap.add_argument("--keywords", default="", help="'; '-separated event keywords (brand and area terms are added for you)")
    ap.add_argument("--corner", choices=["tl", "tr", "bl", "br"])
    ap.add_argument("--cap", choices=["tl", "tr", "bl", "br"])
    ap.add_argument("--halo", action="store_true")
    a = ap.parse_args()
    if not os.path.exists("index.html"):
        sys.exit("run from the gstreetdjs-site repo root")

    im = ImageOps.exif_transpose(Image.open(a.src)).convert("RGB")
    H = min(H_MAX, im.height); im = im.resize((round(im.width * H / im.height), H), Image.LANCZOS)
    corner = a.corner or pick_corner(im)
    html = open("index.html", encoding="utf-8").read()

    if a.replace:
        name = f"{PREFIX}{a.replace}.jpg"; path = "assets/" + name
        exif = Image.open(path).info.get("exif")          # keep the existing tags
        stamp(im, corner, a.halo).save(path, "JPEG", quality=80, progressive=True, optimize=True, exif=exif)
        lines = [l for l in html.splitlines(True) if l.lstrip().startswith(f'["{name}"')]
        if len(lines) == 1:                               # record the (possibly new) logo corner
            fields = re.findall(r'"((?:[^"\\]|\\.)*)"', lines[0])
            fields = fields[:3] + [corner] + ([a.cap] if a.cap else fields[4:5])
            html = html.replace(lines[0], "  [" + ", ".join(f'"{f}"' for f in fields) + "],\n")
            open("index.html", "w", encoding="utf-8").write(html)
        print("replaced", name, "logos:", corner)
        return

    for req in ("slug", "caption", "alt", "title", "after"):
        if not getattr(a, req):
            sys.exit(f"--{req} is required for a new photo")
    used = {f[-8:-4] for f in os.listdir("assets") if f.startswith(PREFIX)}
    n = str(random.choice([x for x in range(1000, 10000) if str(x) not in used]))
    name = f"{PREFIX}{a.slug}-{n}.jpg"; path = "assets/" + name
    kw = [k.strip() for k in a.keywords.split(";") if k.strip()]
    exif = piexif.dump({"0th": {
        piexif.ImageIFD.ImageDescription: a.alt.encode(),
        piexif.ImageIFD.Artist: b"Tony Spinning G - G Street DJs",
        piexif.ImageIFD.Copyright: b"G Street DJs LLC",
        piexif.ImageIFD.XPTitle: u16("G Street DJs - Tony Spinning G - " + a.title),
        piexif.ImageIFD.XPSubject: u16(a.alt),
        piexif.ImageIFD.XPKeywords: u16("; ".join(BRAND + kw + AREA)),
    }, "Exif": {}, "GPS": {}, "1st": {}, "thumbnail": None})
    stamp(im, corner, a.halo).save(path, "JPEG", quality=80, progressive=True, optimize=True, exif=exif)

    anchor = [l for l in html.splitlines(True) if a.after in l and l.lstrip().startswith("[")]
    if len(anchor) != 1:
        sys.exit(f"--after '{a.after}' must match exactly one gallery entry (matched {len(anchor)})")
    extra = f', "{a.cap}"' if a.cap else ""
    html = html.replace(anchor[0], anchor[0] + f'  ["{name}", "{a.caption}", "{a.alt}", "{corner}"{extra}],\n')
    open("index.html", "w", encoding="utf-8").write(html)
    sm = open("sitemap.xml", encoding="utf-8").read().replace(
        "\n  </url>", f"\n    <image:image><image:loc>https://gstreetdjs.com/assets/{name}</image:loc></image:image>\n  </url>")
    open("sitemap.xml", "w", encoding="utf-8").write(sm)
    print("added", name, f"{im.width}x{H}", "logos:", corner)


if __name__ == "__main__":
    main()
