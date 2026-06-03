import os
import math
import datetime
import requests
import sys


USERNAME = "ShauryaSingh1709"
TOKEN = os.environ.get("GH_TOKEN")
GOAL = 3000

if not TOKEN:
    print("ERROR: GH_TOKEN not found in environment variables")
    sys.exit(1)

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json",
}


query = """
query($login:String!) {
  user(login:$login) {
    name
    followers { totalCount }
    repositories(first: 100, ownerAffiliations: OWNER, isFork: false) {
      totalCount
      nodes {
        languages(first: 10, orderBy: {field: SIZE, direction: DESC}) {
          edges {
            size
            node { name color }
          }
        }
      }
    }
    contributionsCollection {
      contributionCalendar {
        totalContributions
        weeks {
          contributionDays {
            contributionCount
            date
            weekday
          }
        }
      }
      restrictedContributionsCount
      totalCommitContributions
      totalIssueContributions
      totalPullRequestContributions
      totalPullRequestReviewContributions
    }
  }
}
"""

try:
    resp = requests.post(
        "https://api.github.com/graphql",
        json={"query": query, "variables": {"login": USERNAME}},
        headers=headers,
        timeout=30,
    )
    resp.raise_for_status()
    data = resp.json()
except Exception as e:
    print(f"ERROR: API request failed: {e}")
    sys.exit(1)

if "data" not in data or data["data"] is None or data["data"]["user"] is None:
    print("ERROR: GitHub API returned unexpected response:")
    print(data)
    sys.exit(1)

user = data["data"]["user"]


followers = user["followers"]["totalCount"] or 0
repos = user["repositories"]["totalCount"] or 0
calendar = user["contributionsCollection"]["contributionCalendar"]
weeks = calendar["weeks"]


today = datetime.date.today()
current_year = today.year
current_month = today.month


month_names_full = [
    "JANUARY", "FEBRUARY", "MARCH", "APRIL", "MAY", "JUNE",
    "JULY", "AUGUST", "SEPTEMBER", "OCTOBER", "NOVEMBER", "DECEMBER",
]
current_month_name = month_names_full[current_month - 1]


current_year_commits = 0
current_month_commits = 0
for w in weeks:
    for d in w["contributionDays"]:
        try:
            day_date = datetime.date.fromisoformat(d["date"])
            if day_date.year == current_year:
                current_year_commits += d["contributionCount"]
                if day_date.month == current_month:
                    current_month_commits += d["contributionCount"]
        except ValueError:
            pass

commits = current_year_commits


total_365days = calendar["totalContributions"] or 0
private_commits = user["contributionsCollection"].get("restrictedContributionsCount", 0) or 0
print(f"📊 Last 365 days total: {total_365days}")
print(f"🔒 Private contributions: {private_commits}")
print(f"📅 Current year ({current_year}) commits: {commits}")
print(f"📆 Current month ({current_month_name}) commits: {current_month_commits}")


lang_totals = {}
lang_colors = {}
for repo in user["repositories"]["nodes"]:
    if repo and repo.get("languages"):
        for edge in repo["languages"]["edges"]:
            name = edge["node"]["name"]
            color = edge["node"].get("color") or "#888888"
            lang_totals[name] = lang_totals.get(name, 0) + edge["size"]
            lang_colors[name] = color

total_lang = sum(lang_totals.values()) if lang_totals else 1
sorted_langs = sorted(lang_totals.items(), key=lambda x: x[1], reverse=True)

top_langs = sorted_langs[:5]
others = sum(v for _, v in sorted_langs[5:])
lang_list = []
for name, size in top_langs:
    lang_list.append((name, size / total_lang * 100, lang_colors.get(name, "#888")))
if others > 0:
    lang_list.append(("Others", others / total_lang * 100, "#8b949e"))

if not lang_list:
    lang_list = [("No Data", 100, "#8b949e")]

top_language = top_langs[0][0] if top_langs else "N/A"
top_language_pct = (top_langs[0][1] / total_lang * 100) if top_langs else 0

all_days = []
for w in weeks:
    for d in w["contributionDays"]:
        all_days.append((d["date"], d["contributionCount"]))
all_days.sort()


longest_streak = 0
cur = 0
for _, c in all_days:
    if c > 0:
        cur += 1
        longest_streak = max(longest_streak, cur)
    else:
        cur = 0


week_start = today - datetime.timedelta(days=today.weekday())
this_week = 0
for dstr, c in all_days:
    try:
        d = datetime.date.fromisoformat(dstr)
        if d >= week_start:
            this_week += c
    except ValueError:
        pass


active_days = 0
for dstr, c in all_days:
    try:
        d = datetime.date.fromisoformat(dstr)
        if d.year == current_year and c > 0:
            active_days += 1
    except ValueError:
        pass

avg_per_day = round(commits / max(active_days, 1), 1)

monthly = {}
year_commits = 0

for dstr, c in all_days:
    try:
        d = datetime.date.fromisoformat(dstr)
        if d.year == current_year and d.month <= current_month:
            key = (d.year, d.month)
            monthly[key] = monthly.get(key, 0) + c
            year_commits += c
    except ValueError:
        pass


month_keys = []
for m in range(1, current_month + 1):
    key = (current_year, m)
    month_keys.append(key)
    if key not in monthly:
        monthly[key] = 0

month_vals = [monthly[k] for k in month_keys]


progress = min(commits / max(GOAL, 1), 1)
progress_pct = int(progress * 100)


ist = datetime.timezone(datetime.timedelta(hours=5, minutes=30))
now = datetime.datetime.now(ist)
last_updated = now.strftime("%b %d, %Y %I:%M %p IST")


svg_parts = []

W, H = 1660, 940

svg_parts.append(f'<svg width="{W}" height="{H}" xmlns="http://www.w3.org/2000/svg" '
                 f'font-family="\'Segoe UI\', Arial, sans-serif">')


svg_parts.append('<defs>')
svg_parts.append(
    '<linearGradient id="redgrad" x1="0" x2="1">'
    '<stop offset="0%" stop-color="#ff1e1e"/>'
    '<stop offset="100%" stop-color="#8b0000"/>'
    '</linearGradient>'
)
svg_parts.append(
    '<linearGradient id="linegrad" x1="0" y1="0" x2="0" y2="1">'
    '<stop offset="0%" stop-color="#ff1e1e" stop-opacity="0.4"/>'
    '<stop offset="100%" stop-color="#ff1e1e" stop-opacity="0"/>'
    '</linearGradient>'
)
svg_parts.append('</defs>')


svg_parts.append(f'<rect width="{W}" height="{H}" fill="#010409"/>')


def panel(x, y, w, h, rx=14):
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" '
            f'fill="#0d1117" stroke="#21262d" stroke-width="1.5"/>')


def esc(text):
    return str(text).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")



for i in range(3):
    svg_parts.append(
        f'<rect x="{40 + i * 22}" y="28" width="14" height="44" '
        f'transform="skewX(-20)" fill="url(#redgrad)"/>'
    )

svg_parts.append(
    '<text x="125" y="58" font-size="46" font-weight="bold" fill="#fff">'
    'SHAURYA <tspan fill="#ff1e1e">GP</tspan> DASHBOARD</text>'
)
svg_parts.append(
    '<text x="40" y="92" font-size="18" letter-spacing="3" fill="#8b949e">'
    'RACING THROUGH CODE. WINNING EVERY COMMIT.</text>'
)

svg_parts.append(panel(1050, 22, 330, 64))
svg_parts.append(
    '<text x="1110" y="50" font-size="12" fill="#8b949e">LAST UPDATED</text>'
)
svg_parts.append(
    f'<text x="1110" y="72" font-size="14" font-weight="bold" fill="#fff">'
    f'{esc(last_updated)}</text>'
)

svg_parts.append(panel(1395, 22, 230, 64))
svg_parts.append(
    '<text x="1455" y="50" font-size="12" fill="#8b949e">SEASON GOAL</text>'
)
svg_parts.append(
    f'<text x="1455" y="72" font-size="15" font-weight="bold" fill="#fff">'
    f'{GOAL:,} COMMITS</text>'
)


sp_x, sp_y, sp_w, sp_h = 20, 120, 1090, 250
svg_parts.append(panel(sp_x, sp_y, sp_w, sp_h))
svg_parts.append(
    f'<text x="{sp_x + 25}" y="{sp_y + 35}" font-size="16" font-weight="bold" '
    f'fill="#fff" letter-spacing="1">SEASON {current_year} PROGRESS</text>'
)
svg_parts.append(
    f'<text x="{sp_x + 25}" y="{sp_y + 95}" font-size="56" font-weight="bold" '
    f'fill="#fff">{progress_pct}%</text>'
)
svg_parts.append(
    f'<text x="{sp_x + 25}" y="{sp_y + 125}" font-size="15">'
    f'<tspan fill="#ff1e1e" font-weight="bold">{commits:,}</tspan>'
    f'<tspan fill="#8b949e"> / {GOAL:,} commits</tspan></text>'
)
svg_parts.append(
    f'<text x="{sp_x + 45}" y="{sp_y + 170}" font-size="13" fill="#fff">'
    f'Keep pushing!</text>'
)
svg_parts.append(
    f'<text x="{sp_x + 45}" y="{sp_y + 190}" font-size="13" fill="#8b949e">'
    f'The podium awaits.</text>'
)

track_x1 = sp_x + 270
track_x2 = sp_x + 1050
track_y = sp_y + 145
car_x = track_x1 + (track_x2 - track_x1) * progress

svg_parts.append(
    f'<line x1="{track_x1}" y1="{track_y}" x2="{car_x:.1f}" y2="{track_y}" '
    f'stroke="#ff1e1e" stroke-width="4"/>'
)
svg_parts.append(
    f'<line x1="{car_x:.1f}" y1="{track_y}" x2="{track_x2}" y2="{track_y}" '
    f'stroke="#30363d" stroke-width="4"/>'
)

stop_data = [
    ("START", 0), ("750", 0.25), ("1,500", 0.5),
    ("2,250", 0.75), ("3,000", 1.0),
]
stop_labels = [
    "", "PIT STOP 1", "PIT STOP 2", "PIT STOP 3", "FINISH"
]

for idx, (label, frac) in enumerate(stop_data):
    px = track_x1 + (track_x2 - track_x1) * frac
    color = "#ff1e1e" if frac <= progress else "#30363d"
    svg_parts.append(
        f'<circle cx="{px:.1f}" cy="{track_y}" r="9" fill="#010409" '
        f'stroke="{color}" stroke-width="3"/>'
    )
    lc = "#ff1e1e" if label == "3,000" else "#fff"
    svg_parts.append(
        f'<text x="{px:.1f}" y="{track_y + 35}" font-size="12" '
        f'fill="{lc}" font-weight="bold" text-anchor="middle">{label}</text>'
    )
    if stop_labels[idx]:
        svg_parts.append(
            f'<text x="{px:.1f}" y="{track_y + 52}" font-size="10" '
            f'fill="#8b949e" text-anchor="middle">{stop_labels[idx]}</text>'
        )


svg_parts.append(
    f'<g transform="translate({car_x:.1f}, {track_y - 15}) scale(-1, 1)">'
    f'<text x="0" y="0" font-size="36" text-anchor="middle">&#x1F3CE;&#xFE0F;</text>'
    f'</g>'
)
svg_parts.append(
    f'<text x="{car_x:.1f}" y="{track_y - 55}" font-size="12" font-weight="bold" '
    f'fill="#ff1e1e" text-anchor="middle">YOU ARE HERE</text>'
)
svg_parts.append(
    f'<polygon points="{car_x - 8:.1f},{track_y - 47} {car_x + 8:.1f},{track_y - 47} '
    f'{car_x:.1f},{track_y - 37}" fill="#ff1e1e"/>'
)


qs_x, qs_y, qs_w, qs_h = 1130, 120, 510, 250
svg_parts.append(panel(qs_x, qs_y, qs_w, qs_h))
svg_parts.append(
    f'<text x="{qs_x + 25}" y="{qs_y + 35}" font-size="16" font-weight="bold" '
    f'fill="#fff" letter-spacing="1">QUICK STATS</text>'
)

stat_cards = [
    ("TOTAL COMMITS", f"{commits:,}", "This Season", "#ff4d4d"),
    ("REPOSITORIES", str(repos), "Active", "#58a6ff"),
    ("FOLLOWERS", str(followers), "People", "#bc8cff"),
    ("CONTRIBUTIONS", f"{commits:,}", "Total", "#3fb950"),
    ("LONGEST STREAK", str(longest_streak), "Days in a row", "#ff8c00"),
    ("AVG / DAY", str(avg_per_day), "Commits", "#58a6ff"),
]
cw, ch = 158, 92
for i, (title, val, sub, col) in enumerate(stat_cards):
    cx = qs_x + 20 + (i % 3) * (cw + 8)
    cy = qs_y + 50 + (i // 3) * (ch + 8)
    svg_parts.append(
        f'<rect x="{cx}" y="{cy}" width="{cw}" height="{ch}" rx="10" '
        f'fill="#0a0d12" stroke="#21262d"/>'
    )
    svg_parts.append(
        f'<text x="{cx + 15}" y="{cy + 25}" font-size="9.5" fill="#8b949e">{title}</text>'
    )
    svg_parts.append(
        f'<text x="{cx + 15}" y="{cy + 52}" font-size="24" font-weight="bold" '
        f'fill="{col}">{val}</text>'
    )
    svg_parts.append(
        f'<text x="{cx + 15}" y="{cy + 75}" font-size="11" fill="#8b949e">{sub}</text>'
    )


cc_x, cc_y, cc_w, cc_h = 20, 390, 545, 350
svg_parts.append(panel(cc_x, cc_y, cc_w, cc_h))
svg_parts.append(
    f'<text x="{cc_x + 25}" y="{cc_y + 35}" font-size="16" font-weight="bold" '
    f'fill="#fff" letter-spacing="1">CONTRIBUTION CALENDAR</text>'
)

cell = 7
gap = 2
grid_x = cc_x + 30
grid_y = cc_y + 60
max_day_val = max((c for _, c in all_days), default=1)
max_day_val = max(max_day_val, 1)


def heat_color(count):
    if count == 0:
        return "#161b22"
    r = count / max_day_val
    if r < 0.25:
        return "#0e4429"
    if r < 0.5:
        return "#006d32"
    if r < 0.75:
        return "#26a641"
    return "#39d353"


recent_weeks = weeks[-52:] if len(weeks) >= 52 else weeks
for wi, w in enumerate(recent_weeks):
    for d in w["contributionDays"]:
        wd = d["weekday"]
        x = grid_x + wi * (cell + gap)
        y = grid_y + wd * (cell + gap)
        svg_parts.append(
            f'<rect x="{x}" y="{y}" width="{cell}" height="{cell}" rx="2" '
            f'fill="{heat_color(d["contributionCount"])}"/>'
        )

ly = grid_y + 7 * (cell + gap) + 15
svg_parts.append(
    f'<text x="{grid_x}" y="{ly + 8}" font-size="11" fill="#8b949e">Less</text>'
)
legend_colors = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353"]
for i, col in enumerate(legend_colors):
    svg_parts.append(
        f'<rect x="{grid_x + 38 + i * 14}" y="{ly}" width="{cell}" '
        f'height="{cell}" rx="2" fill="{col}"/>'
    )
svg_parts.append(
    f'<text x="{grid_x + 115}" y="{ly + 8}" font-size="11" fill="#8b949e">More</text>'
)

mt_y = cc_y + 220
svg_parts.append(
    f'<text x="{cc_x + 25}" y="{mt_y}" font-size="13" font-weight="bold" '
    f'fill="#fff" letter-spacing="1">CONTRIBUTION METRICS</text>'
)
metrics = [
    ("DAYS ACTIVE", str(active_days), "Days", "#fff"),
    ("AVG / DAY", str(avg_per_day), "Commits", "#58a6ff"),
    ("THIS WEEK", str(this_week), "Commits", "#3fb950"),
]
mw = 160
for i, (title, val, sub, col) in enumerate(metrics):
    mx = cc_x + 25 + i * (mw + 8)
    my = mt_y + 15
    svg_parts.append(
        f'<rect x="{mx}" y="{my}" width="{mw}" height="78" rx="10" '
        f'fill="#0a0d12" stroke="#21262d"/>'
    )
    svg_parts.append(
        f'<text x="{mx + 15}" y="{my + 25}" font-size="9.5" fill="#8b949e">{title}</text>'
    )
    svg_parts.append(
        f'<text x="{mx + 15}" y="{my + 55}" font-size="22" font-weight="bold" '
        f'fill="{col}">{val}</text>'
    )
    svg_parts.append(
        f'<text x="{mx + 70}" y="{my + 55}" font-size="11" fill="#8b949e">{sub}</text>'
    )

co_x, co_y, co_w, co_h = 580, 390, 510, 350
svg_parts.append(panel(co_x, co_y, co_w, co_h))
svg_parts.append(
    f'<text x="{co_x + 25}" y="{co_y + 35}" font-size="16" font-weight="bold" '
    f'fill="#fff" letter-spacing="1">COMMITS OVER TIME</text>'
)

gx = co_x + 55
gy = co_y + 60
gw = co_w - 80
gh = 175
mx_val = max(month_vals) if month_vals else 1
mx_val = max(mx_val, 1)

for i in range(5):
    yy = gy + gh - (gh * i / 4)
    val = int(mx_val * i / 4)
    svg_parts.append(
        f'<line x1="{gx}" y1="{yy:.1f}" x2="{gx + gw}" y2="{yy:.1f}" '
        f'stroke="#21262d" stroke-width="1"/>'
    )
    svg_parts.append(
        f'<text x="{gx - 10}" y="{yy + 4:.1f}" font-size="10" fill="#8b949e" '
        f'text-anchor="end">{val}</text>'
    )

n = len(month_vals)
if n > 0:
    pts = []
    for i, v in enumerate(month_vals):
        divisor = max(n - 1, 1)
        px = gx + (gw * i / divisor) if n > 1 else gx + gw / 2
        py = gy + gh - (gh * v / mx_val)
        pts.append((px, py))

    if len(pts) > 1:
        line_path = "M " + " L ".join(f"{x:.1f} {y:.1f}" for x, y in pts)
        area_path = (
            line_path
            + f" L {pts[-1][0]:.1f} {gy + gh} L {pts[0][0]:.1f} {gy + gh} Z"
        )
        svg_parts.append(f'<path d="{area_path}" fill="url(#linegrad)"/>')
        svg_parts.append(
            f'<path d="{line_path}" fill="none" stroke="#ff1e1e" stroke-width="2.5"/>'
        )

    for px, py in pts:
        svg_parts.append(
            f'<circle cx="{px:.1f}" cy="{py:.1f}" r="3" fill="#ff1e1e"/>'
        )

month_names = [
    "Jan", "Feb", "Mar", "Apr", "May", "Jun",
    "Jul", "Aug", "Sep", "Oct", "Nov", "Dec",
]
for i, k in enumerate(month_keys):
    divisor = max(n - 1, 1)
    px = gx + (gw * i / divisor) if n > 1 else gx + gw / 2
    lbl = f"{month_names[k[1] - 1]} '{str(k[0])[2:]}"
    svg_parts.append(
        f'<text x="{px:.1f}" y="{gy + gh + 20}" font-size="10" fill="#8b949e" '
        f'text-anchor="middle">{lbl}</text>'
    )


svg_parts.append(
    f'<rect x="{co_x + 25}" y="{co_y + 285}" width="{co_w - 50}" height="45" '
    f'rx="10" fill="#0a0d12" stroke="#21262d"/>'
)
svg_parts.append(
    f'<text x="{co_x + co_w / 2:.1f}" y="{co_y + 313}" font-size="14" fill="#fff" '
    f'text-anchor="middle">TOTAL COMMITS IN {current_month_name}: '
    f'<tspan fill="#ff1e1e" font-weight="bold">{current_month_commits}</tspan></text>'
)


lb_x, lb_y, lb_w, lb_h = 1105, 390, 535, 350
svg_parts.append(panel(lb_x, lb_y, lb_w, lb_h))
svg_parts.append(
    f'<text x="{lb_x + 25}" y="{lb_y + 35}" font-size="16" font-weight="bold" '
    f'fill="#fff" letter-spacing="1">&lt;/&gt;  LANGUAGES BREAKDOWN</text>'
)

donut_cx = lb_x + 130
donut_cy = lb_y + 165
R = 75
r_inner = 45
start_angle = -90.0


def polar_xy(cx_p, cy_p, r_p, ang):
    rad = math.radians(ang)
    return cx_p + r_p * math.cos(rad), cy_p + r_p * math.sin(rad)


for name, pct, color in lang_list:
    if pct <= 0:
        continue
    sweep = pct / 100 * 360
    sweep = min(sweep, 359.99)
    end_angle = start_angle + sweep
    x1, y1 = polar_xy(donut_cx, donut_cy, R, start_angle)
    x2, y2 = polar_xy(donut_cx, donut_cy, R, end_angle)
    xi1, yi1 = polar_xy(donut_cx, donut_cy, r_inner, end_angle)
    xi2, yi2 = polar_xy(donut_cx, donut_cy, r_inner, start_angle)
    large = 1 if sweep > 180 else 0
    d = (
        f"M {x1:.2f} {y1:.2f} A {R} {R} 0 {large} 1 {x2:.2f} {y2:.2f} "
        f"L {xi1:.2f} {yi1:.2f} A {r_inner} {r_inner} 0 {large} 0 "
        f"{xi2:.2f} {yi2:.2f} Z"
    )
    svg_parts.append(f'<path d="{d}" fill="{color}"/>')
    start_angle = end_angle

svg_parts.append(
    f'<text x="{donut_cx}" y="{donut_cy - 8}" font-size="10" fill="#8b949e" '
    f'text-anchor="middle">TOP LANGUAGE</text>'
)
svg_parts.append(
    f'<text x="{donut_cx}" y="{donut_cy + 12}" font-size="18" font-weight="bold" '
    f'fill="#fff" text-anchor="middle">{esc(top_language)}</text>'
)
svg_parts.append(
    f'<text x="{donut_cx}" y="{donut_cy + 30}" font-size="12" fill="#8b949e" '
    f'text-anchor="middle">{top_language_pct:.1f}%</text>'
)

leg_x = lb_x + 270
leg_y = lb_y + 70
for i, (name, pct, color) in enumerate(lang_list):
    ly2 = leg_y + i * 30
    svg_parts.append(
        f'<rect x="{leg_x}" y="{ly2}" width="13" height="13" rx="3" fill="{color}"/>'
    )
    svg_parts.append(
        f'<text x="{leg_x + 22}" y="{ly2 + 11}" font-size="13" fill="#fff">'
        f'{esc(name)}</text>'
    )
    svg_parts.append(
        f'<text x="{lb_x + lb_w - 25}" y="{ly2 + 11}" font-size="13" '
        f'font-weight="bold" fill="#8b949e" text-anchor="end">{pct:.1f}%</text>'
    )

svg_parts.append(
    f'<text x="{lb_x + lb_w / 2:.1f}" y="{lb_y + lb_h - 20}" font-size="12" '
    f'fill="#8b949e" text-anchor="middle">Most used languages across repositories</text>'
)


ac_x, ac_y, ac_w, ac_h = 20, 760, 1190, 160
svg_parts.append(panel(ac_x, ac_y, ac_w, ac_h))
svg_parts.append(
    f'<text x="{ac_x + 25}" y="{ac_y + 35}" font-size="16" font-weight="bold" '
    f'fill="#fff" letter-spacing="1">ACHIEVEMENTS UNLOCKED</text>'
)

achievements = [
    ("FIRST COMMIT", "Journey Started", commits >= 1, "#ff4d4d"),
    ("CENTURY CLUB", "100 Commits", commits >= 100, "#58a6ff"),
    ("CONSISTENCY", "7 Day Streak", longest_streak >= 7, "#3fb950"),
    ("HALF SEASON", "1,500 Commits", commits >= 1500, "#ffb000"),
    ("LEGEND", "3,000 Commits", commits >= 3000, "#bc8cff"),
]
aw = 220
for i, (title, sub, unlocked, col) in enumerate(achievements):
    ax = ac_x + 25 + i * (aw + 12)
    ay = ac_y + 55
    op = "1" if unlocked else "0.4"
    svg_parts.append(f'<g opacity="{op}">')
    svg_parts.append(
        f'<rect x="{ax}" y="{ay}" width="{aw}" height="85" rx="10" '
        f'fill="#0a0d12" stroke="{col}" stroke-width="1.5"/>'
    )
    svg_parts.append(
        f'<circle cx="{ax + 38}" cy="{ay + 42}" r="24" fill="{col}" '
        f'fill-opacity="0.2" stroke="{col}"/>'
    )
    svg_parts.append(
        f'<text x="{ax + 72}" y="{ay + 30}" font-size="11" font-weight="bold" '
        f'fill="{col}">{title}</text>'
    )
    svg_parts.append(
        f'<text x="{ax + 72}" y="{ay + 50}" font-size="13" font-weight="bold" '
        f'fill="#fff">{sub}</text>'
    )
    status = "Unlocked" if unlocked else "Locked"
    svg_parts.append(
        f'<text x="{ax + 72}" y="{ay + 70}" font-size="11" fill="#8b949e">'
        f'{status}</text>'
    )
    svg_parts.append("</g>")


q_x, q_y, q_w, q_h = 1225, 760, 415, 160
svg_parts.append(panel(q_x, q_y, q_w, q_h))
svg_parts.append(
    f'<text x="{q_x + 30}" y="{q_y + 55}" font-size="44" fill="#ff1e1e" '
    f'font-weight="bold">&quot;</text>'
)
svg_parts.append(
    f'<text x="{q_x + 70}" y="{q_y + 70}" font-size="16" font-style="italic" '
    f'fill="#fff">You need to keep pushing,</text>'
)
svg_parts.append(
    f'<text x="{q_x + 70}" y="{q_y + 95}" font-size="16" font-style="italic" '
    f'fill="#fff">never give up. Smooth Operator.</text>'
)
svg_parts.append(
    f'<text x="{q_x + q_w - 30}" y="{q_y + 130}" font-size="13" fill="#ff1e1e" '
    f'text-anchor="end">- Carlos Sainz</text>'
)

svg_parts.append("</svg>")


os.makedirs("assets", exist_ok=True)

final_svg = "\n".join(svg_parts)

with open("assets/f1-dashboard.svg", "w", encoding="utf-8") as f:
    f.write(final_svg)

print("✅ Dashboard generated successfully!")
print(f"  Commits: {commits} | Repos: {repos} | Followers: {followers}")
print(f"  Progress: {progress_pct}% | Streak: {longest_streak} | Top Lang: {top_language}")
print(f"  {current_month_name} commits: {current_month_commits}")
