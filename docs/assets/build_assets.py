#!/usr/bin/env python3
"""
Builds the animated SVG graphics used by the repository README.

    python docs/assets/build_assets.py

Every graphic is written twice (``*-dark.svg`` / ``*-light.svg``) and the README
swaps them with <picture> so they follow the viewer's GitHub theme. Animations
are plain CSS / SMIL inside the SVG, which GitHub renders through <img>.
Palette and type follow the Navixa site (web_app/static/style.css).
"""
import base64
import io
import pathlib
from string import Template

from PIL import Image, ImageOps

HERE = pathlib.Path(__file__).resolve().parent
REPO = HERE.parent.parent

SANS = '"Space Grotesk",-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif'
MONO = '"JetBrains Mono","Fira Code","Cascadia Code",Consolas,"Courier New",monospace'

THEMES = {
    "dark": dict(bg="#0a0a0a", surface="#141414", surface2="#1c1c1c", border="#2a2a2a",
                 text="#ffffff", muted="#a3a3a3", dim="#6b6b6b",
                 accent="#FF6B00", accent2="#FF9A40", ok="#00CC66", warn="#FFB800", danger="#FF2222",
                 glow="0.20", glow2="0.42", grid="0.55", metal="#2b2b2b", box="#c89b5a"),
    "light": dict(bg="#F5F4F0", surface="#FFFFFF", surface2="#ECEAE4", border="#dcd9d2",
                  text="#0E0E0E", muted="#555555", dim="#7a7a7a",
                  accent="#E85D00", accent2="#FF6B00", ok="#00A854", warn="#D99A00", danger="#E01E1E",
                  glow="0.12", glow2="0.26", grid="0.9", metal="#3a3a3a", box="#c89b5a"),
}

BASE_CSS = Template("""
.sans{font-family:$SANS}
.mono{font-family:$MONO}
.fade{opacity:0;animation:fade .9s ease-out forwards}
.rise{opacity:0;animation:rise .9s cubic-bezier(.22,.7,.3,1) forwards}
@keyframes fade{to{opacity:1}}
@keyframes rise{from{opacity:0;transform:translateY(16px)}to{opacity:1;transform:none}}
@keyframes spin{to{transform:rotate(360deg)}}
@keyframes glow{0%,100%{opacity:$glow;transform:scale(1)}50%{opacity:$glow2;transform:scale(1.08)}}
@keyframes float{0%,100%{transform:translate(0,0)}25%{transform:translate(-14px,-18px)}50%{transform:translate(10px,-8px)}75%{transform:translate(-8px,14px)}}
@keyframes dash{to{stroke-dashoffset:-40}}
@keyframes shimmer{from{transform:translateX(-1200px)}to{transform:translateX(1200px)}}
@keyframes grow{to{transform:scaleX(1)}}
@keyframes blink{50%{opacity:0}}
@media (prefers-reduced-motion:reduce){*{animation-duration:.01s!important;animation-delay:0s!important;animation-iteration-count:1!important}}
""").safe_substitute(SANS=SANS, MONO=MONO)
DELAYS = "".join(f".d{i}{{animation-delay:{i*0.12:.2f}s}}" for i in range(0, 40))
GRID = '<pattern id="grid" width="40" height="40" patternUnits="userSpaceOnUse"><path d="M40 0H0V40" stroke="$border" stroke-width="1"/></pattern>'


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;")


def svg(w, h, body, css="", defs="", title="", p=None):
    base = Template(BASE_CSS).safe_substitute(p or THEMES["dark"])
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" fill="none" role="img" aria-label="{esc(title)}">\n'
            f'<title>{esc(title)}</title>\n<style>{base}{DELAYS}{css}</style>\n<defs>{defs}</defs>\n{body}\n</svg>\n')


def write(name, content):
    (HERE / name).write_text(content, encoding="utf-8")
    print(f"  wrote docs/assets/{name}  ({len(content.encode())/1024:.1f} KB)")


def both(builder, name):
    for theme, p in THEMES.items():
        write(f"{name}-{theme}.svg", builder(p, theme))


# ----------------------------------------------------------------------------
# HERO — wordmark + animated robot (chassis, scissor lift, suction head, LiDAR)
# ----------------------------------------------------------------------------
def hero(p, theme):
    W, H = 1200, 440
    tagline = "> one dashboard click: navigate, verify, lift, grip, deliver, return"
    tl_w = len(tagline) * 8.4
    chips = [("ROS 2 Humble", 110), ("Jetson Orin Nano", 136), ("Nav2 · SLAM", 104), ("YOLOv8 · OpenCV", 128), ("Teensy 4.1", 96)]
    x = 72
    chip_svg = ""
    for i, (label, w) in enumerate(chips):
        chip_svg += (f'<g class="fade" style="animation-delay:{1.0+i*.1:.2f}s"><rect x="{x}" y="376" width="{w}" height="30" rx="15" fill="$surface" stroke="$border"/>'
                     f'<text class="sans" x="{x+w/2}" y="396" text-anchor="middle" font-size="12" font-weight="600" fill="$text">{esc(label)}</text></g>')
        x += w + 10

    # scissor lift: two X stages between chassis top (y=-20) and platform (y=-120)
    xs = ""
    for i in range(2):
        y0 = -20 - i * 50
        xs += (f'<path d="M-40,{y0} L40,{y0-50} M40,{y0} L-40,{y0-50}" stroke="$accent" stroke-width="4" stroke-linecap="round"/>'
               f'<circle cx="0" cy="{y0-25}" r="4.5" fill="$text"/>')
        for cx in (-40, 40):
            xs += f'<circle cx="{cx}" cy="{y0}" r="4.5" fill="$text"/><circle cx="{cx}" cy="{y0-50}" r="4.5" fill="$text"/>'

    robot = Template(f"""
<g transform="translate(880,250)">
  <circle class="glow" r="150" cy="20" fill="$accent" opacity="$glow" filter="url(#blur2)"/>
  <!-- shelf unit -->
  <g class="fade d6">
    <rect x="178" y="-96" width="6" height="200" fill="$metal"/><rect x="286" y="-96" width="6" height="200" fill="$metal"/>
    <rect x="172" y="-60" width="126" height="6" fill="$metal"/><rect x="172" y="30" width="126" height="6" fill="$metal"/>
    <rect x="200" y="-20" width="48" height="50" rx="3" fill="$box" stroke="#8a6a3a"/>
    <rect x="206" y="-12" width="20" height="20" fill="#fff"/><path d="M209 -9h4v4h-4zM219 -9h4v4h-4zM209 1h4v4h-4zM216 -2h2v2h-2zM218 1h4v4h-4z" fill="#111"/>
    <rect x="256" y="-50" width="36" height="40" rx="3" fill="$box" opacity=".7"/>
    <text class="mono" x="235" y="54" text-anchor="middle" font-size="9" letter-spacing="1.5" fill="$dim">SHELF_A</text>
  </g>
  <!-- camera cone -->
  <path class="cone" d="M118,-4 L198,-26 L198,22 Z" fill="$accent" opacity=".14"/>
  <rect class="scanline" x="196" y="-20" width="56" height="2" fill="$accent2"/>
  <!-- floor -->
  <ellipse cx="0" cy="106" rx="150" ry="8" fill="$text" opacity=".06"/>
  <path d="M-170,104 H330" stroke="$border" stroke-width="1.5"/>
  <!-- lift stack -->
  <g class="lift">{xs}</g>
  <g class="plat">
    <rect x="-78" y="-138" width="156" height="18" rx="4" fill="$surface2" stroke="$border"/>
    <rect x="-78" y="-124" width="156" height="4" fill="$accent"/>
    <rect x="-16" y="-150" width="32" height="12" rx="3" fill="$metal"/>
    <rect x="-7" y="-160" width="14" height="10" fill="$metal"/>
    <rect x="-22" y="-196" width="44" height="36" rx="3" fill="$box" stroke="#8a6a3a"/>
    <rect x="-16" y="-190" width="18" height="18" fill="#fff"/><path d="M-13 -187h4v4h-4zM-3 -187h4v4h-4zM-13 -177h4v4h-4zM-6 -180h2v2h-2zM-4 -177h4v4h-4z" fill="#111"/>
    <path class="hose" d="M20,-146 C40,-146 44,-120 44,-100 S30,-60 30,-40" stroke="$dim" stroke-width="2.5" stroke-dasharray="4 4"/>
  </g>
  <!-- chassis -->
  <rect x="-110" y="-20" width="220" height="92" rx="12" fill="$surface2" stroke="$border"/>
  <rect x="-110" y="58" width="220" height="14" rx="6" fill="$accent"/>
  <path d="M-20,8 l16,14 -16,14 -8,-8 8,-6 -8,-6z" fill="$accent"/>
  <text class="sans" x="18" y="34" font-size="15" font-weight="900" letter-spacing="3" fill="$text">NAVI<tspan fill="$accent">X</tspan>A</text>
  <rect x="110" y="-10" width="14" height="14" rx="3" fill="$metal"/><circle cx="117" cy="-3" r="3.5" fill="$accent2"/>
  <!-- wheels -->
  <g transform="translate(-72,84)"><circle r="22" fill="#111" stroke="$border" stroke-width="3"/><g class="wheel"><path d="M0,-14V14M-14,0H14M-10,-10L10,10M-10,10L10,-10" stroke="$dim" stroke-width="2"/></g><circle r="6" fill="$accent"/></g>
  <g transform="translate(72,84)"><circle r="22" fill="#111" stroke="$border" stroke-width="3"/><g class="wheel"><path d="M0,-14V14M-14,0H14M-10,-10L10,10M-10,10L10,-10" stroke="$dim" stroke-width="2"/></g><circle r="6" fill="$accent"/></g>
  <!-- LiDAR mast + sweep -->
  <rect x="-104" y="-70" width="6" height="50" fill="$metal"/>
  <g transform="translate(-101,-78)">
    <circle class="lidar-ring" r="46" stroke="$accent" stroke-opacity=".35" stroke-width="1" stroke-dasharray="3 7"/>
    <g class="sweep"><path d="M0,0 L46,-16 A48,48 0 0 1 46,16 Z" fill="url(#sweep)"/></g>
    <rect x="-12" y="-10" width="24" height="18" rx="4" fill="#111" stroke="$border"/>
    <circle cx="0" cy="-1" r="4" fill="$accent2"><animate attributeName="opacity" values="1;.3;1" dur="1s" repeatCount="indefinite"/></circle>
  </g>
</g>""").safe_substitute(p)

    body = Template(f"""
<g clip-path="url(#frame)">
  <rect width="{W}" height="{H}" fill="$bg"/>
  <rect width="{W}" height="{H}" fill="url(#grid)" opacity="$grid"/>
  <circle class="orb1" cx="1050" cy="60" r="180" fill="$accent" opacity="$glow" filter="url(#blur)"/>
  <circle class="orb2" cx="140" cy="440" r="150" fill="$accent2" opacity="$glow" filter="url(#blur)"/>

  <text class="sans fade d1" x="72" y="86" font-size="11.5" font-weight="800" letter-spacing="4" fill="$accent">UTB 2026 GRADUATION DESIGN PROJECT · AUTONOMOUS MOBILE ROBOT</text>
  <text class="sans rise d2" x="66" y="206" font-size="118" font-weight="900" letter-spacing="4" fill="$text">NAVI<tspan fill="$accent">X</tspan>A</text>
  <text class="sans fade d5" x="72" y="252" font-size="26" font-weight="500" fill="$muted">Navigate The Future</text>
  <text class="sans fade d6" x="72" y="286" font-size="16" fill="$muted">Pharmaceutical-warehouse picking robot with a scissor lift and a suction head.</text>

  <g clip-path="url(#typeclip)">
    <text class="mono" x="72" y="334" font-size="14" fill="$accent2" textLength="{tl_w:.0f}" lengthAdjust="spacingAndGlyphs">{esc(tagline)}</text>
  </g>
  <rect class="cursor" x="72" y="321" width="8" height="17" fill="$accent2"/>
  {chip_svg}
  {robot}
  <text class="mono fade d12" x="{W-40}" y="{H-20}" text-anchor="end" font-size="12" fill="$dim">navixaa.vercel.app</text>
  <rect class="bline" x="0" y="{H-4}" width="{W}" height="4" fill="url(#line)"/>
</g>
<rect x=".5" y=".5" width="{W-1}" height="{H-1}" rx="28" stroke="$border"/>
""").safe_substitute(p)
    defs = Template(f"""
<clipPath id="frame"><rect width="{W}" height="{H}" rx="28"/></clipPath>
<clipPath id="typeclip"><rect class="typew" x="72" y="318" width="{tl_w+4:.0f}" height="24"/></clipPath>
{GRID}
<linearGradient id="sweep" x1="0" x2="1"><stop offset="0" stop-color="$accent" stop-opacity=".55"/><stop offset="1" stop-color="$accent" stop-opacity="0"/></linearGradient>
<linearGradient id="line" x1="0" x2="1"><stop offset="0" stop-color="$accent" stop-opacity="0"/><stop offset=".3" stop-color="$accent"/><stop offset=".7" stop-color="$accent2"/><stop offset="1" stop-color="$accent" stop-opacity="0"/></linearGradient>
<filter id="blur" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="60"/></filter>
<filter id="blur2" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="40"/></filter>
""").safe_substitute(p)
    css = f"""
.orb1{{animation:float 12s ease-in-out infinite}}.orb2{{animation:float 15s ease-in-out infinite reverse}}
.glow{{animation:glow 5s ease-in-out infinite;transform-origin:0 20px}}
.typew{{transform-origin:72px 0;transform:scaleX(0);animation:typew 2.8s steps({len(tagline)},end) 1.2s forwards}}
@keyframes typew{{to{{transform:scaleX(1)}}}}
.cursor{{animation:cur 2.8s steps({len(tagline)},end) 1.2s forwards,blink 1s step-end infinite}}
@keyframes cur{{to{{transform:translateX({tl_w:.0f}px)}}}}
.bline{{transform-origin:0 0;transform:scaleX(0);animation:grow 1.8s cubic-bezier(.22,.7,.3,1) .3s forwards}}
.lift{{transform-origin:0 -20px;animation:lift 7s ease-in-out infinite}}
@keyframes lift{{0%,15%{{transform:scaleY(.42)}}45%,60%{{transform:scaleY(1)}}90%,100%{{transform:scaleY(.42)}}}}
.plat{{animation:plat 7s ease-in-out infinite}}
@keyframes plat{{0%,15%{{transform:translateY(58px)}}45%,60%{{transform:translateY(0)}}90%,100%{{transform:translateY(58px)}}}}
.wheel{{animation:spin 6s linear infinite}}
.sweep{{animation:spin 2.4s linear infinite}}
.lidar-ring{{animation:spin 30s linear infinite reverse}}
.cone{{animation:cone 2.4s ease-in-out infinite}}
@keyframes cone{{0%,100%{{opacity:.08}}50%{{opacity:.22}}}}
.scanline{{animation:scan 2.4s ease-in-out infinite}}
@keyframes scan{{0%,100%{{transform:translateY(0)}}50%{{transform:translateY(46px)}}}}
.hose{{animation:dash 1.2s linear infinite}}
"""
    return svg(W, H, body, css, defs, "Navixa — autonomous pharmaceutical-warehouse picking robot", p)


# ----------------------------------------------------------------------------
# MISSION FLOW — eight steps on a conveyor path, packets moving along it
# ----------------------------------------------------------------------------
def mission(p, theme):
    W, H = 1100, 330
    steps = [("Navigate to shelf", "Nav2 · AMCL · /cmd_vel_nav"),
             ("Confirm shelf QR", "/vision/request SHELF_QR → OK"),
             ("Raise the lift", "PICK → EVT LIFT DONE"),
             ("Centre on the box", "BOX_QR · visual servo → OK"),
             ("Grip the box", "STEP EXT → PUMP ON → STEP RET"),
             ("Lower the lift", "LIFT 0 → EVT LIFT DONE"),
             ("Navigate to drop-off", "Nav2 → dropoff pose"),
             ("Release · return home", "DROP · PUMP OFF · Nav2 → home")]
    nw, gap = 240, 30
    x0 = (W - (4 * nw + 3 * gap)) / 2
    y1, y2 = 92, 232
    centers = [(x0 + i * (nw + gap) + nw / 2, y1) for i in range(4)] + [(x0 + (3 - i) * (nw + gap) + nw / 2, y2) for i in range(4)]
    path = f"M{x0-10},{y1} H{W-x0+10} Q{W-x0+40},{y1} {W-x0+40},{y1+30} V{y2-30} Q{W-x0+40},{y2} {W-x0+10},{y2} H{x0-10}"
    nodes = ""
    for i, ((cx, cy), (t, sub)) in enumerate(zip(centers, steps)):
        nodes += Template(f"""
<g class="rise" style="animation-delay:{.4+i*.14:.2f}s">
  <rect x="{cx-nw/2}" y="{cy-32}" width="{nw}" height="64" rx="14" fill="$surface" stroke="$border"/>
  <circle cx="{cx-nw/2+26}" cy="{cy}" r="14" fill="$accent"/>
  <text class="sans" x="{cx-nw/2+26}" y="{cy+5}" text-anchor="middle" font-size="13" font-weight="900" fill="#0a0a0a">{i+1}</text>
  <text class="sans" x="{cx-nw/2+50}" y="{cy-4}" font-size="14" font-weight="800" fill="$text">{esc(t)}</text>
  <text class="mono" x="{cx-nw/2+50}" y="{cy+15}" font-size="9.5" fill="$muted">{esc(sub)}</text>
</g>""").safe_substitute(p)
    body = Template(f"""
<rect width="{W}" height="{H}" rx="24" fill="$bg"/>
<rect width="{W}" height="{H}" rx="24" fill="url(#grid)" opacity="$grid"/>
<path d="{path}" stroke="$border" stroke-width="2"/>
<path class="flow" d="{path}" stroke="$accent" stroke-opacity=".6" stroke-width="2" stroke-dasharray="8 10"/>
<circle r="5" fill="$accent2"><animateMotion dur="12s" repeatCount="indefinite" path="{path}"/></circle>
<circle r="5" fill="$accent2"><animateMotion dur="12s" begin="6s" repeatCount="indefinite" path="{path}"/></circle>
<g class="fade d2">
  <rect x="{x0}" y="18" width="372" height="28" rx="14" fill="$surface" stroke="$accent" stroke-opacity=".6"/>
  <circle cx="{x0+16}" cy="32" r="4" fill="$ok"/>
  <text class="mono" x="{x0+28}" y="36" font-size="10" letter-spacing="1" fill="$text">DASHBOARD PICK → MQTT amr/orders → /mission/start</text>
</g>
<g class="fade d9">
  <rect x="{W-x0-330}" y="{H-46}" width="330" height="28" rx="14" fill="$surface" stroke="$border"/>
  <circle cx="{W-x0-314}" cy="{H-32}" r="4" fill="$ok"/>
  <text class="mono" x="{W-x0-302}" y="{H-28}" font-size="10" letter-spacing="1" fill="$text">MISSION COMPLETE → amr/status state: IDLE</text>
</g>
<text class="mono" x="{x0}" y="{H-28}" font-size="10" letter-spacing="2" fill="$dim">EVT FAULT &lt;what&gt; OR TIMEOUT → STOP · MISSION ABORT</text>
{nodes}
<rect x=".5" y=".5" width="{W-1}" height="{H-1}" rx="24" stroke="$border"/>
""").safe_substitute(p)
    css = ".flow{animation:dash 1.6s linear infinite}"
    return svg(W, H, body, css, Template(GRID).safe_substitute(p), "Mission state machine: eight steps from dashboard click to return home", p)


# ----------------------------------------------------------------------------
# VISION PIPELINE — QR read chain + cup-centring loop
# ----------------------------------------------------------------------------
def vision(p, theme):
    W, H = 1100, 300
    top = [("Astra Pro", "RGB 640×480 · depth optional"), ("YOLOv8", "localise box · QR · barcode"),
           ("Enhance", "crop · upscale · CLAHE"), ("Decode", "OpenCV QR → pyzbar → full frame"),
           ("Consensus", "same value N frames"), ("/vision/result", "OK <sku> | FAIL")]
    bot = [("Pixel offset", "box centre vs frame centre"), ("P-controller", "angular.z · EMA smoothing · clamp"),
           ("/cmd_vel_vision", "twist_mux priority 50"), ("Robot rotates", "cup over box → OK")]
    nw, gap, nh = 160, 18, 60
    x0 = (W - (6 * nw + 5 * gap)) / 2
    y1 = 92
    nodes = links = packets = ""
    for i, (a, b) in enumerate(top):
        x = x0 + i * (nw + gap)
        hi = i == len(top) - 1
        nodes += f"""
<g class="rise" style="animation-delay:{.3+i*.12:.2f}s">
  <rect x="{x}" y="{y1}" width="{nw}" height="{nh}" rx="14" fill="$surface" stroke="{'$accent' if hi else '$border'}"/>
  <text class="sans" x="{x+nw/2}" y="{y1+26}" text-anchor="middle" font-size="13" font-weight="800" fill="$text">{esc(a)}</text>
  <text class="mono" x="{x+nw/2}" y="{y1+44}" text-anchor="middle" font-size="9" fill="$muted">{esc(b)}</text>
</g>"""
        if i < len(top) - 1:
            d = f"M{x+nw},{y1+nh/2} H{x+nw+gap}"
            links += f'<path class="flow" d="{d}" stroke="$accent" stroke-opacity=".7" stroke-width="1.5" stroke-dasharray="4 6"/>'
            packets += f'<circle r="3" fill="$accent2"><animateMotion dur="1s" begin="{i*0.17:.2f}s" repeatCount="indefinite" path="{d}"/></circle>'
    bw, bgap = 220, 24
    bx0 = (W - (4 * bw + 3 * bgap)) / 2
    y2 = 212
    for i, (a, b) in enumerate(bot):
        x = bx0 + i * (bw + bgap)
        nodes += f"""
<g class="rise" style="animation-delay:{1.1+i*.12:.2f}s">
  <rect x="{x}" y="{y2}" width="{bw}" height="{nh}" rx="14" fill="$surface" stroke="$border"/>
  <text class="sans" x="{x+bw/2}" y="{y2+26}" text-anchor="middle" font-size="13" font-weight="800" fill="$text">{esc(a)}</text>
  <text class="mono" x="{x+bw/2}" y="{y2+44}" text-anchor="middle" font-size="9" fill="$muted">{esc(b)}</text>
</g>"""
        if i < len(bot) - 1:
            d = f"M{x+bw},{y2+nh/2} H{x+bw+bgap}"
            links += f'<path class="flow" d="{d}" stroke="$accent" stroke-opacity=".7" stroke-width="1.5" stroke-dasharray="4 6"/>'
            packets += f'<circle r="3" fill="$accent2"><animateMotion dur="1.1s" begin="{i*0.2:.2f}s" repeatCount="indefinite" path="{d}"/></circle>'
    # loop arrow: from Robot rotates back up to YOLOv8
    yolo_x = x0 + (nw + gap) + nw / 2
    last_x = bx0 + 3 * (bw + bgap) + bw / 2
    loop = f"M{last_x},{y2} V{y2-24} H{yolo_x} V{y1+nh}"
    body = Template(f"""
<rect width="{W}" height="{H}" rx="24" fill="$bg"/>
<rect width="{W}" height="{H}" rx="24" fill="url(#grid)" opacity="$grid"/>
<text class="mono" x="{x0}" y="{y1-30}" font-size="10" letter-spacing="2" fill="$accent">READ CHAIN — SHELF_QR AND BOX_QR</text>
<text class="mono" x="{bx0}" y="{y2-6}" font-size="10" letter-spacing="2" fill="$accent">CENTRING LOOP — BOX_QR ONLY · NO CUP SERVO, THE WHOLE ROBOT TURNS</text>
<path class="flow" d="{loop}" stroke="$dim" stroke-width="1.5" stroke-dasharray="4 6" fill="none"/>
<circle r="3" fill="$accent2"><animateMotion dur="2.4s" repeatCount="indefinite" path="{loop}"/></circle>
{links}
{packets}
{nodes}
<text class="mono" x="{W-40}" y="{H-14}" text-anchor="end" font-size="9.5" letter-spacing="1.5" fill="$dim">DEPTH_ENABLED=0 → RGB-ONLY FALLBACK · MISSION NEVER USES VISION DEPTH</text>
<rect x=".5" y=".5" width="{W-1}" height="{H-1}" rx="24" stroke="$border"/>
""").safe_substitute(p)
    css = ".flow{animation:dash 1.2s linear infinite}"
    return svg(W, H, body, css, Template(GRID).safe_substitute(p), "Vision pipeline: YOLOv8 localisation, multi-decoder QR read and visual-servo centring", p)


# ----------------------------------------------------------------------------
# STAT TILES · EYEBROW · DIVIDER · FOOTER
# ----------------------------------------------------------------------------
def stats(p, theme):
    W, H = 1100, 150
    tiles = [("30 kg", "Max payload", "scissor lift + suction head"),
             ("434 mm", "Lift stroke", "1.32 m reach at full height"),
             ("360°", "LiDAR coverage", "RPLIDAR C1 · 12 m range"),
             ("8", "Mission steps", "from one dashboard click"),
             ("24/7", "Operation", "two isolated 6S Li-ion rails"),
             ("4", "Subsystems", "10 integrated technologies")]
    n = len(tiles); gap = 16; tw = (W - gap * (n - 1)) / n
    body = ""
    for i, (big, cap, sub) in enumerate(tiles):
        x = i * (tw + gap)
        fs = 34 if len(big) <= 4 else 28
        body += f"""
<g class="rise" style="animation-delay:{.2+i*.12:.2f}s">
  <rect x="{x+.5}" y=".5" width="{tw-1}" height="{H-1}" rx="20" fill="$surface" stroke="$border"/>
  <rect x="{x+22}" y="0" width="{tw-44}" height="2" fill="url(#top)"/>
  <text class="sans" x="{x+22}" y="62" font-size="{fs}" font-weight="900" letter-spacing="-1" fill="$accent">{esc(big)}</text>
  <text class="sans" x="{x+22}" y="92" font-size="13" font-weight="700" fill="$text">{esc(cap)}</text>
  <text class="sans" x="{x+22}" y="112" font-size="11" fill="$muted">{esc(sub)}</text>
</g>"""
    defs = Template('<linearGradient id="top" x1="0" x2="1"><stop offset="0" stop-color="$accent" stop-opacity="0"/><stop offset=".5" stop-color="$accent"/><stop offset="1" stop-color="$accent" stop-opacity="0"/></linearGradient>').safe_substitute(p)
    return svg(W, H, Template(body).safe_substitute(p), "", defs, "Key figures", p)


def eyebrow(text, p, theme):
    tw = len(text) * 10.6
    W, H = int(tw + 60), 26
    body = Template(f"""
<rect class="eline" x="0" y="12" width="34" height="2" rx="1" fill="$accent"/>
<text class="sans fade d3" x="46" y="18" font-size="11" font-weight="800" letter-spacing="4.5" fill="$accent" textLength="{tw:.0f}" lengthAdjust="spacing">{esc(text)}</text>
""").safe_substitute(p)
    css = ".eline{transform-origin:0 0;transform:scaleX(0);animation:grow .8s cubic-bezier(.22,.7,.3,1) forwards}"
    return svg(W, H, body, css, "", text, p)


def divider(p, theme):
    W, H = 1200, 14
    body = Template(f'<rect x="0" y="6" width="{W}" height="1" fill="$border"/><rect class="sh" x="0" y="5" width="420" height="3" rx="1.5" fill="url(#g)"/>').safe_substitute(p)
    defs = Template('<linearGradient id="g" x1="0" x2="1"><stop offset="0" stop-color="$accent" stop-opacity="0"/><stop offset=".5" stop-color="$accent"/><stop offset="1" stop-color="$accent" stop-opacity="0"/></linearGradient>').safe_substitute(p)
    return svg(W, H, body, ".sh{animation:shimmer 5s ease-in-out infinite}", defs, "divider", p)


def footer(p, theme):
    W, H = 1200, 220
    body = Template(f"""
<g clip-path="url(#f)">
  <rect width="{W}" height="{H}" fill="$bg"/>
  <rect width="{W}" height="{H}" fill="url(#grid)" opacity="$grid"/>
  <circle class="orb1" cx="180" cy="220" r="200" fill="$accent" opacity="$glow" filter="url(#blur)"/>
  <circle class="orb2" cx="1020" cy="0" r="220" fill="$accent2" opacity="$glow" filter="url(#blur)"/>
  <text class="sans fade d1" x="600" y="64" text-anchor="middle" font-size="11" font-weight="800" letter-spacing="5" fill="$accent">UNIVERSITY OF TECHNOLOGY BAHRAIN · CAPSTONE 2026</text>
  <text class="sans rise d3" x="600" y="122" text-anchor="middle" font-size="48" font-weight="900" letter-spacing="-1" fill="$text">Navigate The Future.</text>
  <text class="sans fade d5" x="600" y="156" text-anchor="middle" font-size="15" fill="$muted">Built by four engineers across mechatronics and informatics: navigation, vision, firmware and payload.</text>
  <path class="wave" d="M0,196 C150,176 250,216 400,196 S650,176 800,196 S1050,216 1200,196 S1450,176 1600,196 S1850,216 2000,196 S2250,176 2400,196 V220 H0 Z" fill="$accent" opacity=".22"/>
  <path class="wave2" d="M0,204 C150,188 250,220 400,204 S650,188 800,204 S1050,220 1200,204 S1450,188 1600,204 S1850,220 2000,204 S2250,188 2400,204 V220 H0 Z" fill="$accent2" opacity=".3"/>
</g>
<rect x=".5" y=".5" width="{W-1}" height="{H-1}" rx="28" stroke="$border"/>
""").safe_substitute(p)
    defs = Template(f'<clipPath id="f"><rect width="{W}" height="{H}" rx="28"/></clipPath>{GRID}<filter id="blur" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="60"/></filter>').safe_substitute(p)
    css = ".orb1{animation:float 12s ease-in-out infinite}.orb2{animation:float 14s ease-in-out infinite reverse}.wave{animation:wv 9s linear infinite}.wave2{animation:wv 6s linear infinite}@keyframes wv{to{transform:translateX(-800px)}}"
    return svg(W, H, body, css, defs, "Navigate The Future", p)


# ----------------------------------------------------------------------------
# TEAM CARDS — fixed geometry so the four columns always line up
# ----------------------------------------------------------------------------
TEAM = [
    ("nathalie", "Nathalie Ahmed", "TEAM LEAD · NAVIGATION & SLAM", "Mechatronics Engineering",
     ["Nav2, SLAM Toolbox and EKF, the mission", "coordinator and the serial bridge."]),
    ("abdalla", "Abdalla Elradi", "VISION · WEB GUI & MQTT BRIDGE", "Informatics Engineering",
     ["YOLOv8 + QR vision node, visual-servo", "centring, dashboard and ROS ↔ MQTT bridge."]),
    ("mahanna", "Mahanna Alhumaimi", "PAYLOAD · CAD & FABRICATION", "Mechatronics Engineering",
     ["Scissor lift and gripper mechanism,", "CAD design and chassis fabrication."]),
    ("zahra", "Zahra Jassim", "MOTION CONTROL · TEENSY FIRMWARE", "Informatics Engineering",
     ["Unified Teensy firmware for drive, lift,", "stepper and pump; project reports."]),
]


def team_card(slug, name, role, dept, blurb, p, theme):
    W, H = 360, 460
    photo = REPO / "web_app" / "static" / "images" / f"team-{slug}.jpg"
    im = ImageOps.fit(ImageOps.exif_transpose(Image.open(photo)).convert("RGB"), (360, 360), Image.LANCZOS, centering=(0.5, 0.3))
    buf = io.BytesIO(); im.save(buf, "JPEG", quality=84, optimize=True)
    b64 = base64.b64encode(buf.getvalue()).decode()
    lines = "".join(f'<text class="sans" x="180" y="{352 + i*20}" text-anchor="middle" font-size="12.5" fill="$muted">{esc(l)}</text>' for i, l in enumerate(blurb))
    body = Template(f"""
<rect x=".5" y=".5" width="{W-1}" height="{H-1}" rx="28" fill="$surface" stroke="$border"/>
<rect x="24" y="0" width="{W-48}" height="2" fill="url(#top)"/>
<g transform="translate(180,124)">
  <circle class="glow" r="96" fill="$accent" opacity="$glow" filter="url(#blur)"/>
  <circle r="94" stroke="$accent" stroke-width="2"/>
  <g clip-path="url(#ph)"><image href="data:image/jpeg;base64,{b64}" x="-88" y="-88" width="176" height="176" preserveAspectRatio="xMidYMid slice"/></g>
  <circle r="88" stroke="$text" stroke-opacity=".12"/>
</g>
<text class="sans rise d2" x="180" y="258" text-anchor="middle" font-size="22" font-weight="800" fill="$text">{esc(name)}</text>
<text class="sans fade d4" x="180" y="283" text-anchor="middle" font-size="10.5" font-weight="800" letter-spacing="2.5" fill="$accent">{esc(role)}</text>
<text class="sans fade d5" x="180" y="306" text-anchor="middle" font-size="13" fill="$muted">{esc(dept)}</text>
<rect x="150" y="324" width="60" height="1.5" fill="$border"/>
<g class="fade d6">{lines}</g>
<text class="mono" x="180" y="{H-22}" text-anchor="middle" font-size="9.5" letter-spacing="2.5" fill="$dim">NAVIXA TEAM · UTB 2026</text>
""").safe_substitute(p)
    defs = Template('<clipPath id="ph"><circle r="88"/></clipPath>'
                    '<linearGradient id="top" x1="0" x2="1"><stop offset="0" stop-color="$accent" stop-opacity="0"/><stop offset=".5" stop-color="$accent"/><stop offset="1" stop-color="$accent" stop-opacity="0"/></linearGradient>'
                    '<filter id="blur" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="22"/></filter>').safe_substitute(p)
    css = ".glow{animation:glow 4s ease-in-out infinite}"
    return svg(W, H, body, css, defs, f"{name} — {dept}", p)


EYEBROWS = {"overview": "WHAT NAVIXA DOES", "mission": "ONE CLICK, EIGHT STEPS", "architecture": "SYSTEM ARCHITECTURE",
            "hardware": "BUILT ON REAL HARDWARE", "software": "SOFTWARE STACK", "vision": "PERCEPTION",
            "quickstart": "RUN IT", "docs": "TESTING & DOCUMENTATION", "build": "BEHIND THE BUILD", "team": "THE TEAM"}


def main():
    both(hero, "hero"); both(mission, "mission"); both(vision, "vision"); both(stats, "stats")
    both(divider, "divider"); both(footer, "footer")
    for key, text in EYEBROWS.items():
        for theme, p in THEMES.items():
            write(f"eyebrow-{key}-{theme}.svg", eyebrow(text, p, theme))
    for slug, name, role, dept, blurb in TEAM:
        for theme, p in THEMES.items():
            write(f"team-{slug}-{theme}.svg", team_card(slug, name, role, dept, blurb, p, theme))
    print("done")


if __name__ == "__main__":
    main()
