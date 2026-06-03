import os
import requests
import math

USERNAME = "ShauryaSingh1709"
TOKEN = os.environ.get("GH_TOKEN")

# ---------------- SAFETY CHECK ----------------
if not TOKEN:
    raise Exception("GH_TOKEN not found in environment variables")

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

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

response = requests.post(
    "https://api.github.com/graphql",
    json={"query": query, "variables": {"login": USERNAME}},
    headers=headers
)

data = response.json()

# ---------------- DEBUG SAFETY ----------------
if "data" not in data:
    print("❌ GitHub API ERROR RESPONSE:")
    print(data)
    raise Exception("GraphQL failed - check token/permissions")

user = data["data"]["user"]

repos = user["repositories"]["totalCount"] or 0
followers = user["followers"]["totalCount"] or 0
commits = user["contributionsCollection"]["contributionCalendar"]["totalContributions"] or 0

# ---------------- F1 LOGIC ----------------
goal = 3000
progress = min(commits / goal, 1)

# 🏎️ FORWARD MOVEMENT (FIXED)
start_x, end_x = 120, 1080
car_x = start_x + (end_x - start_x) * progress

# ---------------- SIMPLE CURVE TRACK ----------------
cx, cy = 600, 320
radius = 220

angle = math.pi * 1.2 + progress * math.pi * 1.6

car_curve_x = cx + radius * math.cos(angle)
car_curve_y = cy + radius * math.sin(angle)

# ---------------- SVG ----------------
svg = f"""
<svg width="1400" height="700" xmlns="http://www.w3.org/2000/svg">

<defs>
    <linearGradient id="bg" x1="0" x2="1">
        <stop offset="0%" stop-color="#0d1117"/>
        <stop offset="100%" stop-color="#161b22"/>
    </linearGradient>

    <linearGradient id="neon" x1="0" x2="1">
        <stop offset="0%" stop-color="#00f5ff"/>
        <stop offset="100%" stop-color="#00ff87"/>
    </linearGradient>
</defs>

<!-- BACKGROUND -->
<rect width="100%" height="100%" fill="url(#bg)"/>

<!-- TITLE -->
<text x="50" y="70" fill="white" font-size="32">
🏎️ SHAURYA F1 TELEMETRY DASHBOARD
</text>

<!-- STATS -->
<text x="50" y="120" fill="#58a6ff" font-size="18">
Commits: {commits}
</text>

<text x="50" y="150" fill="#58a6ff" font-size="18">
Repos: {repos}
</text>

<text x="50" y="180" fill="#58a6ff" font-size="18">
Followers: {followers}
</text>

<text x="50" y="210" fill="#58a6ff" font-size="18">
Progress: {int(progress*100)}%
</text>

<!-- TRACK -->
<path d="M 350 450 C 350 200, 1050 200, 1050 450"
      stroke="url(#neon)" stroke-width="4" fill="none"/>

<!-- CAR (CURVE POSITION - REAL F1 STYLE) -->
<text x="{car_curve_x}" y="{car_curve_y}" font-size="36">🏎️</text>

<!-- PROGRESS BAR -->
<rect x="350" y="600" width="700" height="12" fill="#30363d" rx="6"/>
<rect x="350" y="600" width="{progress*700}" height="12" fill="url(#neon)" rx="6"/>

</svg>
"""

# ---------------- SAVE FILE ----------------
os.makedirs("assets", exist_ok=True)

with open("assets/f1-dashboard.svg", "w", encoding="utf-8") as f:
    f.write(svg)

print("🏎️ Dashboard generated successfully!")
