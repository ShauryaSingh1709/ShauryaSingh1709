import os
import requests

USERNAME = "ShauryaSingh1709"
TOKEN = os.environ["GH_TOKEN"]

# ---------------- FETCH DATA ----------------
query = """
query($login:String!) {
  user(login:$login) {
    repositories(ownerAffiliations: OWNER) {
      totalCount
    }
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
    print("Error:", data)
    exit(1)

repos = data["data"]["user"]["repositories"]["totalCount"] or 0
commits = data["data"]["user"]["contributionsCollection"]["contributionCalendar"]["totalContributions"] or 0

# ---------------- F1 LOGIC ----------------
goal = 3000
progress = min(commits / goal, 1)
car_x = 100 + progress * 900

# ---------------- SVG GENERATION ----------------
svg = f"""
<svg width="1200" height="400" xmlns="http://www.w3.org/2000/svg">

<rect width="100%" height="100%" fill="#0d1117"/>

<text x="40" y="60" fill="white" font-size="30">
🏎️ SHAURYA GP DASHBOARD
</text>

<text x="40" y="110" fill="#58a6ff" font-size="20">
Commits: {commits}
</text>

<text x="40" y="140" fill="#58a6ff" font-size="20">
Repos: {repos}
</text>

<text x="40" y="170" fill="#58a6ff" font-size="20">
Progress: {int(progress*100)}%
</text>

<!-- Track -->
<line x1="100" y1="300" x2="1100" y2="300" stroke="white" stroke-width="8"/>

<!-- Car -->
<text x="{car_x}" y="290" font-size="40">🏎️</text>

<!-- Progress Bar -->
<rect x="100" y="330" width="1000" height="10" fill="#30363d"/>
<rect x="100" y="330" width="{progress*1000}" height="10" fill="#2ea043"/>

</svg>
"""

# ---------------- SAVE FILE ----------------
os.makedirs("assets", exist_ok=True)

with open("assets/f1-dashboard.svg", "w", encoding="utf-8") as f:
    f.write(svg)

print("Dashboard Generated 🚀")
