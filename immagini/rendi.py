#!/usr/bin/env python3
"""Render the site's raster images from their sources in this folder (14.10.2026).

    favicon.svg  ->  favicon.ico (16 + 32 px), apple-touch-icon.png (180 px), icon-512.png
    card.html    ->  og-de.png, og-fr.png, og-it.png, og-en.png (1200 x 630, the share card)

genera.main() only copies the results to docs/; run this by hand after changing a source:

    /opt/homebrew/bin/python3 immagini/rendi.py

Needs Google Chrome (headless, its own throwaway profile) and Pillow. The card is set in the site's
own fonts (../fonts), loaded from disk: nothing is fetched from the network. The mark is a bold "A"
with a brass bar (design A2 "Brass", step 4), deliberately no cross, coat of arms or anything that
reads as an authority's emblem: the register is not an official publication.
"""
from __future__ import annotations

import html
import io
import pathlib
import struct
import subprocess
import sys
import tempfile

from PIL import Image

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import lingue  # noqa: E402

CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"


def shot(page: pathlib.Path, w: int, h: int, out: pathlib.Path, transparent: bool = False) -> Image.Image:
    with tempfile.TemporaryDirectory() as prof:
        cmd = [CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars", f"--user-data-dir={prof}",
               "--no-first-run", "--disable-background-networking", "--allow-file-access-from-files",
               "--force-device-scale-factor=1", f"--window-size={w},{h}", "--virtual-time-budget=4000",
               f"--screenshot={out}"]
        if transparent:
            cmd.append("--default-background-color=00000000")
        subprocess.run(cmd + [page.as_uri()], check=True, capture_output=True)
    return Image.open(out).convert("RGBA")


def ico(images: list) -> bytes:
    """An .ico holding PNG images (every browser since 2007 reads them)."""
    pngs = []
    for im in images:
        b = io.BytesIO()
        im.save(b, "PNG", optimize=True)
        pngs.append((im.size, b.getvalue()))
    head = struct.pack("<HHH", 0, 1, len(pngs))
    off = 6 + 16 * len(pngs)
    entries, data = b"", b""
    for (w, h), png in pngs:
        entries += struct.pack("<BBBBHHII", w % 256, h % 256, 0, 0, 1, 32, len(png), off + len(data))
        data += png
    return head + entries + data


def icons(tmp: pathlib.Path) -> None:
    svg = (HERE / "favicon.svg").read_text()
    # iOS rounds the corners itself and fills transparency with black: a full square for the
    # home-screen icon and the logo
    square = svg.replace(' rx="14"', "").replace(
        '<rect x=".75" y=".75" width="62.5" height="62.5" rx="13.25" fill="none" stroke="#c9a24e" '
        'stroke-opacity=".6" stroke-width="1.5"/>', "")
    (tmp / "r.svg").write_text(svg)
    (tmp / "s.svg").write_text(square)
    (tmp / "icons.html").write_text(
        "<!doctype html><style>html,body{margin:0;background:transparent}img{position:absolute;top:0}</style>"
        '<img src="r.svg" style="left:0;width:16px;height:16px">'
        '<img src="r.svg" style="left:20px;width:32px;height:32px">'
        '<img src="s.svg" style="left:60px;width:180px;height:180px">'
        '<img src="s.svg" style="left:0;top:200px;width:512px;height:512px">')
    sheet = shot(tmp / "icons.html", 520, 720, tmp / "icons.png", transparent=True)
    i16, i32 = sheet.crop((0, 0, 16, 16)), sheet.crop((20, 0, 52, 32))
    (HERE / "favicon.ico").write_bytes(ico([i16, i32]))
    sheet.crop((60, 0, 240, 180)).convert("RGB").save(HERE / "apple-touch-icon.png", optimize=True)
    sheet.crop((0, 200, 512, 712)).convert("RGB").save(HERE / "icon-512.png", optimize=True)


def cards(tmp: pathlib.Path) -> None:
    tpl = (HERE / "card.html").read_text()
    fonts = (HERE.parent / "fonts").as_uri()
    for lang in lingue.LANGS:
        page = (tpl.replace("{fonts}", fonts).replace("{lang}", lang)
                .replace("{mark}", (HERE / "favicon.svg").as_uri())
                .replace("{site}", html.escape(lingue.t("site", lang)))
                .replace("{tagline}", html.escape(lingue.p("tagline", lang)))
                .replace("{words}", html.escape(" · ".join(lingue.t(k, lang) for k in
                                                          ("nav_tenders", "awards", "companies")))))
        (tmp / f"card-{lang}.html").write_text(page)
        im = shot(tmp / f"card-{lang}.html", 1200, 630, tmp / f"card-{lang}.png").convert("RGB")
        # 256 colours, dithered, keep the card sharp, the glows free of bands and the file under 100 KB:
        # a median-cut palette of 255 plus the mark's brass (design A2, step 4), which median cut alone dulled
        pal = im.quantize(255, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE).getpalette()[:765]
        pimg = Image.new("P", (1, 1))
        pimg.putpalette(pal + [0xc9, 0xa2, 0x4e])
        q = im.quantize(palette=pimg, dither=Image.Dither.FLOYDSTEINBERG)
        q.save(HERE / f"og-{lang}.png", optimize=True)
        print(f"og-{lang}.png", (HERE / f"og-{lang}.png").stat().st_size, "bytes")


if __name__ == "__main__":
    with tempfile.TemporaryDirectory() as t:
        icons(pathlib.Path(t))
        cards(pathlib.Path(t))
    for n in ("favicon.ico", "apple-touch-icon.png", "icon-512.png"):
        print(n, (HERE / n).stat().st_size, "bytes")
