import os
import requests
import math

USERNAME = "ShauryaSingh1709"
TOKEN = os.environ["GH_TOKEN"]

# ---------------- GITHUB DATA ----------------
query = """
query($login:String!) {
  user(login:$login) {
    followers { totalCount }
    repositories(ownerAffiliations: OWNER) { totalCount }
    contributionsCollection {
      contributionCalendar {
        totalContributions
      }
    }
  }
}
"""

r = requests.post(
    "https://api.github.com/graphql",
    json={"query": query, "variables": {"login": USERNAME}},
    headers={"Authorization": f"Bearer {TOKEN}"}
)

data = r.json()

if "data" not in data:
    print(data)
    exit(1)

user = data["data"]["user"]

repos = user["repositories"]["totalCount"] or 0
followers = user["followers"]["totalCount"] or 0
commits = user["contributionsCollection"]["contributionCalendar"]["totalContributions"] or 0

# ---------------- F1 LOGIC ----------------
goal = 3000
progress = min(commits / goal, 1)

# 🏎️ CURVED TRACK (CIRCLE PATH LIKE F1 CIRCUIT)
cx, cy = 700, 260
radius = 400

angle = math.pi * 1.1 + progress * math.pi * 1.6

car_x = cx + radius * math.cos(angle)
car_y = cy + radius * math.sin(angle)

# ---------------- SVG ----------------
svg = f"""
<svg width="1400" height="750" xmlns="http://www.w3.org/2000/svg">

<defs>
    <radialGradient id="bg" cx="50%" cy="50%">
        <stop offset="0%" stop-color="#1a1f2e"/>
        <stop offset="100%" stop-color="#0d1117"/>
    </radialGradient>

    <linearGradient id="neon" x1="0" x2="1">
        <stop offset="0%" stop-color="#00f5ff"/>
        <stop offset="100%" stop-color="#00ff87"/>
    </linearGradient>
</defs>

<!-- BACKGROUND -->
<rect width="100%" height="100%" fill="url(#bg)"/>

<!-- TITLE -->
<text x="50" y="70" fill="white" font-size="34">
🏎️ SHAURYA — F1 DEV CIRCUIT
</text>

<text x="50" y="105" fill="#8b949e" font-size="16">
Live GitHub telemetry powered racing system
</text>

<!-- DASH CARDS -->
<rect x="50" y="140" width="300" height="120" rx="15" fill="#161b22"/>
<text x="80" y="180" fill="#00f5ff">COMMITS</text>
<text x="80" y="220" fill="white" font-size="28">{commits}</text>

<rect x="370" y="140" width="300" height="120" rx="15" fill="#161b22"/>
<text x="400" y="180" fill="#00f5ff">REPOS</text>
<text x="400" y="220" fill="white" font-size="28">{repos}</text>

<rect x="690" y="140" width="300" height="120" rx="15" fill="#161b22"/>
<text x="720" y="180" fill="#00f5ff">FOLLOWERS</text>
<text x="720" y="220" fill="white" font-size="28">{followers}</text>

<rect x="1010" y="140" width="300" height="120" rx="15" fill="#161b22"/>
<text x="1040" y="180" fill="#00f5ff">PROGRESS</text>
<text x="1040" y="220" fill="white" font-size="28">{int(progress*100)}%</text>

<!-- CURVED TRACK -->
<path d="M 300 450
         C 300 200, 1100 200, 1100 450
         C 1100 650, 300 650, 300 450"
      stroke="white" stroke-width="6" fill="none" opacity="0.3"/>

<!-- NEON TRACK -->
<path d="M 300 450
         C 300 200, 1100 200, 1100 450
         C 1100 650, 300 650, 300 450"
      stroke="url(#neon)" stroke-width="3" fill="none"/>

<!-- CAR (MOVES ON CURVE) -->
<text x="{car_x}" y="{car_y}" font-size="38">🏎️</text>

<!-- PROGRESS BAR -->
<rect x="300" y="700" width="800" height="12" fill="#30363d" rx="6"/>
<rect x="300" y="700" width="{progress*800}" height="12" fill="url(#neon)" rx="6"/>

</svg>
"""

os.makedirs("assets", exist_ok=True)

with open("assets/f1-dashboard.svg", "w", encoding="utf-8") as f:
    f.write(svg)

print("🏎️ F1 Circuit Dashboard Updated")
