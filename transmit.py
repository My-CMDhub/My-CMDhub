"""Draws the profile's SVGs and rewrites its generated README blocks. Standard library only.

    python3 transmit.py                                   # locally
    SITE_JSON=../site/out/profile.json python3 transmit.py   # against a local site build
    GITHUB_TOKEN=... python3 transmit.py                  # in the Action

Everything the cards and header *say* comes from https://dhruvpatel.net/profile.json, which the site
builds from its own data/figures.ts: the tagline, each project's before → after, its label and its
NOT YET line. Nothing is typed twice, so the profile can't drift from the site. If the site can't be
reached, the last good copy (assets/site.json) is used. What it *shows happening* comes from GitHub:
the last commit, the signal log, and the pulse, which is the contribution calendar's last 84 days.

Writes assets/header-{light,dark}.svg, assets/<slug>-{light,dark}.svg, and the README blocks between
<!--header:…-->, <!--cards:…--> and <!--signal:…--> markers.
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

SITE_URL = 'https://dhruvpatel.net/profile.json'


def site():
    """The site's own words. Falls back to the last copy that loaded, so a site outage changes nothing."""
    cache = ASSETS / 'site.json'
    try:
        if os.environ.get('SITE_JSON'):
            data = json.loads(Path(os.environ['SITE_JSON']).read_text())
        else:
            with urllib.request.urlopen(SITE_URL, timeout=20) as r:
                data = json.load(r)
        cache.write_text(json.dumps(data, ensure_ascii=False, indent=1) + '\n')
        return data
    except (OSError, ValueError) as e:
        print(f'site unreachable ({e}); using assets/site.json')
        return json.loads(cache.read_text())


def wrap(text, width):
    """Greedy word wrap by character count. The card fonts are monospace or close enough to it."""
    lines, cur = [], ''
    for w in text.split():
        if cur and len(cur) + 1 + len(w) > width:
            lines.append(cur)
            cur = w
        else:
            cur = f'{cur} {w}'.strip()
    lines = lines + [cur] if cur else lines
    if len(lines) > 1 and len(lines[-1]) < 4:   # no stranded "s" from "1.7 s": take a word down with it
        head, _, tail = lines[-2].rpartition(' ')
        lines[-2:] = [head, f'{tail} {lines[-1]}'] if head else lines[-2:]
    return lines


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


def strikes(t, items, y=206, cw=7.5, slot=7):
    """One retraction at a time: the old belief, a line drawn through it, then what was measured.
    IBM Plex Mono advances exactly 0.6 em, so 12.5 px text is 7.5 px a character and the strike can be
    sized to the words. Reduced motion shows the first one, already struck."""
    n, total = len(items), slot * len(items)
    pct = lambda sec: f'{sec / total * 100:.2f}%'
    out, css = [], [
        f'@keyframes cyc{{0%{{opacity:0}}{pct(.3)}{{opacity:1}}{pct(slot - .5)}{{opacity:1}}{pct(slot)},100%{{opacity:0}}}}',
        f'@keyframes strk{{0%,{pct(.9)}{{transform:scaleX(0)}}{pct(1.6)},100%{{transform:scaleX(1)}}}}',
        f'@keyframes is{{0%,{pct(1.7)}{{opacity:0}}{pct(2.3)},100%{{opacity:1}}}}',
        '.rt line{transform-box:fill-box;transform-origin:left center}']
    for i, r in enumerate(items):
        was, is_, why = r['was'], r['is'], r['why']
        x_is = 40 + (len(was) + 4) * cw
        anim = lambda k, d=f'{i * slot}s': f'animation:{k} {total}s linear {d} infinite backwards'
        out.append(
            f'<g class="rt" style="opacity:{1 if i == 0 else 0};{anim("cyc")}">'
            f'<text class="m" x="40" y="{y}" font-size="12.5" fill="{t["muted"]}">{escape(was)}</text>'
            f'<line x1="38" y1="{y - 4}" x2="{42 + len(was) * cw:.1f}" y2="{y - 4}" stroke="{t["a"]}" stroke-width="1.6" style="{anim("strk")}"/>'
            f'<text class="m" x="{40 + (len(was) + 1) * cw:.1f}" y="{y}" font-size="12.5" style="{anim("is")}">'
            f'<tspan fill="{t["ink"]}">→ </tspan><tspan fill="{t["b"]}">{escape(is_)}</tspan>'
            f'<tspan fill="{t["muted"]}">  · {escape(why)}</tspan></text></g>')
    return ''.join(out), ''.join(css)


def pulse(t, days, x0=40, x1=860, y=262):
    """The contribution calendar as a heartbeat: one beat per week, taller for busier weeks, drawn left
    to right and then held. Same days as the green squares under this README; per day it would be a
    solid comb, because most days have something."""
    weeks = [sum(c for _, c in days[i:i + 7]) for i in range(0, len(days), 7)]
    mx = max(weeks, default=0) or 1
    step = (x1 - x0) / len(weeks)
    d = [f'M{x0} {y}']
    for i, c in enumerate(weeks):
        x = x0 + step * (i + .5)
        if c:
            h = 8 + 30 * math.sqrt(c / mx)
            d.append(f'L{x - 9:.1f} {y} L{x - 5:.1f} {y - 4} L{x - 3:.1f} {y} L{x:.1f} {y - h:.1f} '
                     f'L{x + 3:.1f} {y + h * .35:.1f} L{x + 6:.1f} {y} L{x + 12:.1f} {y - 5} L{x + 17:.1f} {y}')
    d.append(f'L{x1} {y}')
    body = (f'<line x1="{x0}" y1="{y}" x2="{x1}" y2="{y}" stroke="{t["rule"]}" stroke-width="1.5"/>'
            f'<path class="beat" pathLength="1" d="{" ".join(d)}" fill="none" stroke="{t["b"]}" stroke-width="1.8" stroke-linejoin="round"/>'
            f'<circle class="breathe" cx="{x1}" cy="{y}" r="3.5" fill="{t["b"]}"/>')
    css = ('.beat{stroke-dasharray:1;animation:draw 14s cubic-bezier(.4,0,.2,1) infinite}'
           '@keyframes draw{0%{stroke-dashoffset:1}35%,92%{stroke-dashoffset:0}100%{stroke-dashoffset:0;opacity:0}}')
    return body, css


def header(t, last, s, days):
    repo, day, msg = last
    total = sum(c for _, c in days)
    cap = f'{len(days) // 7} weeks · {total:,} contributions'
    room = 74 - len(f'● last signal · {day} · {repo} · ')   # keep clear of the caption on the right
    msg = escape(msg if len(msg) <= room else msg[:room - 1] + '…')
    st, st_css = strikes(t, s['retractions'])
    pl, pl_css = pulse(t, days)
    body = f"""
<text class="mm" x="40" y="46" font-size="12" letter-spacing="1.2" fill="{t['muted']}">SIGNAL · -38.1500° S 144.3500° E · NEAR MELBOURNE</text>
<circle class="breathe" cx="772" cy="42" r="4.5" fill="{t['b']}"/>
<text class="mm" x="784" y="46" font-size="12" letter-spacing="1.2" fill="{t['b']}">MEASURING</text>
<text class="c" x="36" y="128" font-size="78" letter-spacing="-2.5" fill="{t['ink']}">Dhruv Patel</text>
<text class="s" x="40" y="168" font-size="21" fill="{t['ink2']}">{escape(s['tagline'])}</text>
{st}
{pl}
<text class="m" x="40" y="298" font-size="12" fill="{t['muted']}"><tspan fill="{t['b']}">●</tspan> last signal · {day} · <tspan fill="{t['ink']}">{escape(repo)}</tspan> · {msg}</text>
<text class="m" x="860" y="298" font-size="10.5" text-anchor="end" fill="{t['muted']}">{cap}</text>"""
    return svg(900, 324, t, body, st_css + pl_css)


def ruler(c, t, x0=32, w=376, y=196):
    """Axis, ticks and markers, same geometry as the site's Ruler at card scale."""
    s = c['ruler']
    ticks = []  # (x, label|None)
    if s['scale'] == 'log':
        pos = lambda v: x0 + math.log10(v) * w / 4
        for d, lab in enumerate(['1 ms', '10 ms', '100 ms', '1 s', '10 s']):
            ticks.append((pos(10 ** d), lab))
            if d < 4:
                ticks += [(pos(k * 10 ** d), None) for k in range(2, 10)]
    elif s['scale'] == 'linear':
        mx, unit = s['max'], s['unit']
        major, minor = (1, .1) if mx <= 5 else (5, 1)
        pos = lambda v: x0 + v / mx * w
        for i in range(round(mx / minor) + 1):
            v = round(i * minor, 3)
            is_major = abs(v / major - round(v / major)) < 1e-9
            ticks.append((pos(v), f'{v:g} {unit}'.strip() if is_major else None))
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
    if s['scale'] == 'band':
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
        a, b = pos(s['from']), pos(s['to'])
        out.append(f'<line x1="{a-8:.1f}" y1="{y-20}" x2="{b+10:.1f}" y2="{y-20}" stroke="{t["b"]}" stroke-width="1.6" class="arrow"/>'
                   f'<path d="M{b+3:.1f} {y-20} l8 -4 v8z" fill="{t["b"]}" class="arrow"/>'
                   f'<circle cx="{a:.1f}" cy="{y}" r="5.5" fill="{t["bg"]}" stroke="{t["wd"]}" stroke-width="1.6"/>'
                   f'<circle class="mk" cx="{b:.1f}" cy="{y}" r="6" fill="{t["b"]}"/>')
        # slide old → new, hold, fade, repeat: calm, 8 s
        css = (f'.mk{{animation:slide 8s cubic-bezier(.22,.8,.2,1) infinite}}'
               f'@keyframes slide{{0%{{transform:translateX({a-b:.1f}px);opacity:0}}6%{{transform:translateX({a-b:.1f}px);opacity:1}}40%,88%{{transform:none;opacity:1}}100%{{transform:none;opacity:0}}}}'
               f'.arrow{{animation:arrow 8s ease infinite}}@keyframes arrow{{0%,30%{{opacity:0}}45%,88%{{opacity:1}}100%{{opacity:0}}}}')
    return ''.join(out), css


def card_lines(c):
    """Each card's wrapped text, worked out once so every card can be given the tallest one's height."""
    label = f"{c['label']['status']} · {c['label']['note']}"
    return dict(kind=wrap(c['kind'], 56), what=wrap(c['what'], 54), label=wrap(label, 62)[:2],
                not_yet=wrap(c['notYet'], 52))


def card_height(c):
    L = card_lines(c)
    return 231 + 14 * len(L['kind']) + 18 * len(L['what']) + 14 * len(L['label']) + 13 * len(L['not_yet'])


def card(c, n, t, height):
    L = card_lines(c)
    y = 90
    kind = ''.join(f'<text class="m" x="32" y="{y + 14 * i}" font-size="11" fill="{t["muted"]}">{escape(l)}</text>' for i, l in enumerate(L['kind']))
    y += 14 * (len(L['kind']) - 1) + 30
    what = ''.join(f'<text class="s" x="32" y="{y + 18 * i}" font-size="14" fill="{t["ink2"]}">{escape(l)}</text>' for i, l in enumerate(L['what']))
    y += 18 * (len(L['what']) - 1) + 40
    big = (f'<text class="c" x="32" y="{y}" font-size="40" letter-spacing="-1" fill="{t["wd"]}">{escape(c["from"])} '
           f'<tspan fill="{t["ink"]}">→</tspan> <tspan fill="{t["b"]}">{escape(c["to"])}</tspan></text>')
    r, css = ruler(c, t, y=y + 36)
    y += 88
    label = ''.join(f'<text class="mm" x="32" y="{y + 14 * i}" font-size="10.5" fill="{t["b"]}">{escape(l)}</text>' for i, l in enumerate(L['label']))
    y += 14 * (len(L['label']) - 1) + 22
    ny = ''.join(f'<text class="m" x="{86 if i == 0 else 32}" y="{y + 13 * i}" font-size="10" fill="{t["muted"]}">{escape(l)}</text>' for i, l in enumerate(L['not_yet']))
    body = f"""
<text class="mm" x="32" y="38" font-size="10.5" letter-spacing="1.2" fill="{t['muted']}">SIGNAL {n:02d}</text>
<text class="mm" x="408" y="38" font-size="10.5" text-anchor="end" fill="{t['a']}">↗</text>
<text class="c" x="32" y="70" font-size="27" letter-spacing="-.3" fill="{t['a']}">{escape(c['name'])}</text>
{kind}{what}{big}
{r}
{label}
<text class="mm" x="32" y="{y}" font-size="10" letter-spacing="1" fill="{t['prov']}">NOT YET</text>{ny}"""
    return svg(440, height, t, body, css)


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


def days(n=84):
    """Contributions per day for the last n days: the same numbers as the profile's green squares.
    The calendar needs a token (GraphQL); without one, public push events stand in."""
    if os.environ.get('GITHUB_TOKEN'):
        q = ('{user(login:"%s"){contributionsCollection{contributionCalendar{weeks{contributionDays'
             '{date contributionCount}}}}}}' % USER)
        req = urllib.request.Request('https://api.github.com/graphql', json.dumps({'query': q}).encode(),
                                     {'Authorization': f"Bearer {os.environ['GITHUB_TOKEN']}"})
        try:
            with urllib.request.urlopen(req, timeout=20) as r:
                weeks = json.load(r)['data']['user']['contributionsCollection']['contributionCalendar']['weeks']
            return [(d['date'], d['contributionCount']) for w in weeks for d in w['contributionDays']][-n:]
        except (OSError, KeyError, TypeError) as e:
            print(f'contribution calendar unavailable ({e}); counting public pushes')
    per = {}
    for page in (1, 2, 3):
        for e in api(f'users/{USER}/events/public?per_page=100&page={page}'):
            if e['type'] == 'PushEvent':
                per[e['created_at'][:10]] = per.get(e['created_at'][:10], 0) + 1
    today = datetime.now(timezone.utc).date()
    return [((d := today.fromordinal(today.toordinal() - i)).isoformat(), per.get(d.isoformat(), 0)) for i in range(n - 1, -1, -1)]


def block(text, name, body):
    """Replace what sits between <!--name:start--> and <!--name:end-->."""
    return re.sub(rf'(<!--{name}:start-->).*?(<!--{name}:end-->)', lambda m: f'{m[1]}\n{body}\n{m[2]}', text, flags=re.S)


RAW = f'https://raw.githubusercontent.com/{USER}/{USER}/main/assets'


def pic(slug, alt, href, width):
    return (f'<a href="{href}"><picture><source media="(prefers-color-scheme: dark)" srcset="{RAW}/{slug}-dark.svg">'
            f'<img alt="{escape(alt)}" src="{RAW}/{slug}-light.svg" width="{width}"></picture></a>')


def shield(s):
    return s.replace('-', '--').replace('_', '__').replace(' ', '%20').replace('→', '%E2%86%92').replace('\u00a0', '%20')


def ago(day):
    d = (datetime.now(timezone.utc).date() - datetime.fromisoformat(day).date()).days
    if d < 14:
        return 'today' if d == 0 else 'yesterday' if d == 1 else f'{d} days ago'
    return datetime.fromisoformat(day).strftime('%b %Y')


def main():
    s = site()
    rows, cal = recent(), days()
    projects = [c for c in s['scenes'] if c['group'] == 'project']
    interns = [c for c in s['scenes'] if c['group'] == 'internship']
    height = max(card_height(c) for c in projects)
    for name, t in THEMES.items():
        (ASSETS / f'header-{name}.svg').write_text(header(t, (rows[0][0], rows[0][2], rows[0][3]), s, cal))
        for n, c in enumerate(projects, 1):
            (ASSETS / f"{c['slug']}-{name}.svg").write_text(card(c, n, t, height))

    alt = lambda c: f"{c['name']}: {c['what']}, {c['from']} to {c['to']}. Not yet: {c['notYet']}.".replace('\u00a0', ' ')
    cells = [pic(c['slug'], alt(c), f"https://github.com/{USER}/{c['repo']}" if c.get('repo') else c['href'], '49%')
             for c in projects]
    grid = '\n'.join(f'<p>\n' + '\n'.join(cells[i:i + 2]) + '\n</p>' for i in range(0, len(cells), 2))
    badges = '\n'.join(
        f'<a href="{c["href"]}"><img alt="{escape(c["name"])} internship: {escape(c["from"])} to {escape(c["to"])}" '
        f'src="https://img.shields.io/badge/{shield(c["name"].lower())}-{shield(c["from"] + " → " + c["to"])}-6E2437?style=flat-square&labelColor=17191C"></a>'
        for c in interns)
    table = '\n'.join(['| | repo | latest change |', '|:--|:--|:--|'] + [
        f"| `{ago(d)}` | [{n}]({u}) | {m.replace('|', '/')} |" for n, u, d, m in rows])

    readme = HERE / 'README.md'
    text = readme.read_text()
    text = block(text, 'header', pic('header', f"Dhruv Patel: {s['tagline']} Near Melbourne.", 'https://dhruvpatel.net', '100%'))
    text = block(text, 'cards', f'{grid}\n\n<p><sub>internships&nbsp;</sub>\n{badges}\n</p>')
    text = block(text, 'signal', table)
    readme.write_text(text)
    for old in ASSETS.glob('*-light.svg'):   # a project the site no longer lists loses its card
        slug = old.name[:-len('-light.svg')]
        if slug != 'header' and slug not in {c['slug'] for c in projects}:
            old.unlink(); (ASSETS / f'{slug}-dark.svg').unlink(missing_ok=True)


if __name__ == '__main__':
    main()
