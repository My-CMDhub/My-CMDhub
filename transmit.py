"""Draws the profile's SVGs and refreshes the signal log. Standard library only.

    python3 transmit.py            # locally (unauthenticated GitHub API is fine)
    GITHUB_TOKEN=... python3 transmit.py   # in the Action

Writes assets/header-{light,dark}.svg, assets/<card>-{light,dark}.svg, and the README block
between <!--signal:start--> and <!--signal:end-->.
Figures mirror Portfolio/site/data/figures.ts — change them in both places.
"""
import json, math, os, re, urllib.request
from datetime import datetime, timezone
from html import escape
from pathlib import Path

USER = 'My-CMDhub'
SKIP = {'My-CMDhub', 'cicd', 'typescript-backend', 'Agent', 'CommBank-Server', 'CommBank-Web'}
HERE = Path(__file__).parent
ASSETS = HERE / 'assets'
FONTS = json.loads((ASSETS / 'fonts.json').read_text())

THEMES = {
    'light': dict(bg='#EEF0EC', ink='#17191C', ink2='#30343A', muted='#5D646D', rule='#C9CDC6',
                  a='#6E2437', b='#1D6E4B', prov='#7A5C0E', wd='#646B74'),
    'dark': dict(bg='#121513', ink='#E4E7E1', ink2='#C4C9C2', muted='#9AA29B', rule='#343A35',
                 a='#C9707F', b='#63C39B', prov='#D9B45E', wd='#848B85'),
}

CARDS = [
    dict(id='ovela', n='01', name='Ovela', kind='voice receptionist on a real phone line',
         what='The first reply of a call', old='3.7 s', new='0.9 s',
         scale=('linear', 4, 's'), vals=(3.7, 0.9), label='measured · one call each side',
         not_yet='as fast when a tool runs · 1.1–1.7 s'),
    dict(id='agent-os', n='02', name='Agent-OS', kind='a harness a model can operate a Mac through',
         what='A request behind a 3-second action', old='2,864 ms', new='5 ms',
         scale=('log',), vals=(2864, 5), label='measured · median of 5 · log scale',
         not_yet='a model driving it'),
    dict(id='silverpond', n='03', name='Silverpond', kind='multi-tenant agent architecture · internship',
         what='The agent’s first-turn search', old='23.4 s', new='3.9 s',
         scale=('linear', 25, 's'), vals=(23.4, 3.9), label='measured · repeated runs',
         not_yet='a fast cold start · ~43 s'),
    dict(id='capstone', n='04', name='Capstone', kind='ETH payment gateway · IMPACT 2025 winner',
         what='How far a payment may be from the ask', old='±0.5%', new='6 dp',
         scale=('band',), vals=None, label='source · git history of the amount check',
         not_yet='tests for the amount check'),
]


def font_css():
    face = lambda fam, key, style='normal': (
        f"@font-face{{font-family:{fam};font-style:{style};src:url(data:font/woff2;base64,{FONTS[key]}) format('woff2')}}")
    return ''.join([face('C', 'cond'), face('S', 'serifi', 'italic'), face('M', 'mono'), face('MM', 'monom')])


def svg(w, h, t, body, extra_css=''):
    css = f"""{font_css()}
.c{{font-family:C,'Arial Narrow',sans-serif;font-weight:700}} .s{{font-family:S,Georgia,serif;font-style:italic}}
.m{{font-family:M,ui-monospace,monospace}} .mm{{font-family:MM,ui-monospace,monospace}}
@keyframes breathe{{0%,100%{{opacity:1}}50%{{opacity:.25}}}}
.breathe{{animation:breathe 2.8s ease-in-out infinite}}
{extra_css}
@media (prefers-reduced-motion:reduce){{*{{animation:none!important}}}}"""
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">'
            f'<style>{css}</style>'
            f'<rect x=".5" y=".5" width="{w-1}" height="{h-1}" rx="10" fill="{t["bg"]}" stroke="{t["rule"]}"/>'
            f'{body}</svg>')


def header(t, last):
    repo, day, msg = last
    msg = escape(msg if len(msg) <= 64 else msg[:63] + '…')
    # an ECG-style blip that travels the line: the profile's pulse
    blip = 'M-60 0 H-14 L-8 -16 L-2 20 L4 -34 L10 12 L15 0 H60'
    body = f"""
<text class="mm" x="40" y="46" font-size="12" letter-spacing="1.2" fill="{t['muted']}">SIGNAL · 37.81°S 144.96°E · MELBOURNE</text>
<circle class="breathe" cx="772" cy="42" r="4.5" fill="{t['b']}"/>
<text class="mm" x="784" y="46" font-size="12" letter-spacing="1.2" fill="{t['b']}">TRANSMITTING</text>
<text class="c" x="36" y="128" font-size="78" letter-spacing="-2.5" fill="{t['ink']}">Dhruv Patel</text>
<text class="s" x="40" y="168" font-size="21" fill="{t['ink2']}">I build the parts around the model, and measure them before I believe them.</text>
<line x1="40" y1="232" x2="860" y2="232" stroke="{t['rule']}" stroke-width="1.5"/>
<clipPath id="k"><rect x="40" y="180" width="820" height="100"/></clipPath>
<g clip-path="url(#k)"><path class="pulse" d="{blip}" transform="translate(40 232)" fill="none" stroke="{t['b']}" stroke-width="2" stroke-linejoin="round"/></g>
<text class="m" x="40" y="266" font-size="12" fill="{t['muted']}"><tspan fill="{t['b']}">●</tspan> last signal · {day} · <tspan fill="{t['ink']}">{escape(repo)}</tspan> · {msg}</text>"""
    css = '@keyframes travel{from{transform:translate(-20px,232px)}to{transform:translate(920px,232px)}}.pulse{animation:travel 7s linear infinite}'
    return svg(900, 300, t, body, css)


def ruler(c, t, x0=32, w=376, y=196):
    """Axis, ticks and markers, same geometry as the site's Ruler at card scale."""
    s = c['scale']
    ticks = []  # (x, label|None)
    if s[0] == 'log':
        pos = lambda v: x0 + math.log10(v) * w / 4
        for d, lab in enumerate(['1 ms', '10 ms', '100 ms', '1 s', '10 s']):
            ticks.append((pos(10 ** d), lab))
            if d < 4:
                ticks += [(pos(k * 10 ** d), None) for k in range(2, 10)]
    elif s[0] == 'linear':
        mx, unit = s[1], s[2]
        major, minor = (1, .1) if mx <= 5 else (5, 1)
        pos = lambda v: x0 + v / mx * w
        for i in range(round(mx / minor) + 1):
            v = round(i * minor, 3)
            is_major = abs(v / major - round(v / major)) < 1e-9
            ticks.append((pos(v), f'{v:g} {unit}' if is_major else None))
    else:
        pos = lambda d: x0 + w / 2 + d / .6 * w / 2
        for i in range(-6, 7):
            ticks.append((pos(i / 10), ('exact' if i == 0 else f"{'+' if i > 0 else '−'}0.5%") if i % 5 == 0 else None))
    out = [f'<line x1="{x0}" y1="{y}" x2="{x0+w}" y2="{y}" stroke="{t["ink"]}" stroke-width="1.2"/>']
    for x, lab in ticks:
        if lab:
            out.append(f'<line x1="{x:.1f}" y1="{y-6}" x2="{x:.1f}" y2="{y+6}" stroke="{t["ink"]}"/>'
                       f'<text class="m" x="{x:.1f}" y="{y+22}" font-size="10" text-anchor="middle" fill="{t["muted"]}">{lab}</text>')
        else:
            out.append(f'<line x1="{x:.1f}" y1="{y-3}" x2="{x:.1f}" y2="{y+3}" stroke="{t["ink"]}" stroke-width=".5"/>')
    css = ''
    if s[0] == 'band':
        short, demo = pos(-.5), pos((0.00182 / 0.00181982 - 1) * 100)
        half = pos(.01) - pos(0)
        out.append(f'<rect x="{pos(-.5):.1f}" y="{y-11}" width="{pos(.5)-pos(-.5):.1f}" height="22" fill="none" stroke="{t["wd"]}" stroke-dasharray="3 4"/>'
                   f'<rect class="band" x="{pos(0)-half:.1f}" y="{y-11}" width="{2*half:.1f}" height="22" fill="{t["b"]}" fill-opacity=".25"/>'
                   f'<circle class="short" cx="{short:.1f}" cy="{y}" r="5.5" fill="{t["a"]}"/>'
                   f'<circle cx="{demo:.1f}" cy="{y}" r="4" fill="{t["b"]}" stroke="{t["bg"]}" stroke-width="1.5"/>')
        css = (f'.band{{transform-box:fill-box;transform-origin:center;animation:shrink 8s cubic-bezier(.22,.8,.2,1) infinite}}'
               f'@keyframes shrink{{0%,8%{{transform:scaleX(50)}}45%,100%{{transform:scaleX(1)}}}}'
               f'.short{{animation:refuse 8s ease infinite}}'
               f'@keyframes refuse{{0%,30%{{fill:{t["b"]}}}40%,100%{{fill:{t["a"]}}}}}')
    else:
        a, b = pos(c['vals'][0]), pos(c['vals'][1])
        out.append(f'<line x1="{a-8:.1f}" y1="{y-20}" x2="{b+10:.1f}" y2="{y-20}" stroke="{t["b"]}" stroke-width="1.6" class="arrow"/>'
                   f'<path d="M{b+3:.1f} {y-20} l8 -4 v8z" fill="{t["b"]}" class="arrow"/>'
                   f'<circle cx="{a:.1f}" cy="{y}" r="5.5" fill="{t["bg"]}" stroke="{t["wd"]}" stroke-width="1.6"/>'
                   f'<circle class="mk" cx="{b:.1f}" cy="{y}" r="6" fill="{t["b"]}"/>')
        # slide old → new, hold, fade, repeat: calm, 8 s
        css = (f'.mk{{animation:slide 8s cubic-bezier(.22,.8,.2,1) infinite}}'
               f'@keyframes slide{{0%{{transform:translateX({a-b:.1f}px);opacity:0}}6%{{transform:translateX({a-b:.1f}px);opacity:1}}40%,88%{{transform:none;opacity:1}}100%{{transform:none;opacity:0}}}}'
               f'.arrow{{animation:arrow 8s ease infinite}}@keyframes arrow{{0%,30%{{opacity:0}}45%,88%{{opacity:1}}100%{{opacity:0}}}}')
    return ''.join(out), css


def card(c, t):
    r, css = ruler(c, t)
    body = f"""
<text class="mm" x="32" y="38" font-size="10.5" letter-spacing="1.2" fill="{t['muted']}">SIGNAL {c['n']}</text>
<text class="mm" x="408" y="38" font-size="10.5" text-anchor="end" fill="{t['a']}">↗</text>
<text class="c" x="32" y="70" font-size="27" letter-spacing="-.3" fill="{t['a']}">{c['name']}</text>
<text class="m" x="32" y="90" font-size="11" fill="{t['muted']}">{escape(c['kind'])}</text>
<text class="s" x="32" y="120" font-size="14" fill="{t['ink2']}">{escape(c['what'])}</text>
<text class="c" x="32" y="160" font-size="40" letter-spacing="-1" fill="{t['wd']}">{c['old']} <tspan fill="{t['ink']}">→</tspan> <tspan fill="{t['b']}">{c['new']}</tspan></text>
{r}
<text class="mm" x="32" y="248" font-size="10.5" fill="{t['b']}">{escape(c['label'])}</text>
<text class="mm" x="32" y="270" font-size="10" letter-spacing="1" fill="{t['prov']}">NOT YET <tspan class="m" letter-spacing="0" fill="{t['muted']}">{escape(c['not_yet'])}</tspan></text>"""
    return svg(440, 292, t, body, css)


def api(path):
    req = urllib.request.Request(f'https://api.github.com/{path}', headers={'Accept': 'application/vnd.github+json'})
    if os.environ.get('GITHUB_TOKEN'):
        req.add_header('Authorization', f"Bearer {os.environ['GITHUB_TOKEN']}")
    with urllib.request.urlopen(req, timeout=20) as r:
        return json.load(r)


def recent(n=5):
    rows = []
    for repo in api(f'users/{USER}/repos?sort=pushed&per_page=30&type=owner'):
        if repo['name'] in SKIP or repo['private'] or repo['archived']:
            continue
        subjects = [x['commit']['message'].split('\n')[0] for x in api(f"repos/{USER}/{repo['name']}/commits?per_page=10")]
        msg = next((m for m in subjects if not m.startswith('Merge')), '')
        rows.append((repo['name'], repo['html_url'], repo['pushed_at'][:10], msg))
        if len(rows) == n:
            break
    return rows


def ago(day):
    d = (datetime.now(timezone.utc).date() - datetime.fromisoformat(day).date()).days
    if d < 14:
        return 'today' if d == 0 else 'yesterday' if d == 1 else f'{d} days ago'
    return datetime.fromisoformat(day).strftime('%b %Y')


def main():
    rows = recent()
    for name, t in THEMES.items():
        (ASSETS / f'header-{name}.svg').write_text(header(t, (rows[0][0], rows[0][2], rows[0][3])))
        for c in CARDS:
            (ASSETS / f"{c['id']}-{name}.svg").write_text(card(c, t))
    table = '\n'.join(['| | repo | latest change |', '|:--|:--|:--|'] + [
        f"| `{ago(d)}` | [{n}]({u}) | {m.replace('|', '/')} |" for n, u, d, m in rows])
    readme = HERE / 'README.md'
    text = readme.read_text()
    text = re.sub(r'(<!--signal:start-->).*?(<!--signal:end-->)', lambda m: f'{m[1]}\n{table}\n{m[2]}', text, flags=re.S)
    readme.write_text(text)


if __name__ == '__main__':
    main()
