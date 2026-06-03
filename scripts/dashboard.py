import os
import requests

USERNAME = "ShauryaSingh1709"
TOKEN = os.environ["GH_TOKEN"]

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
    json={
        "query": query,
        "variables": {"login": USERNAME}
    },
    headers={
        "Authorization": f"Bearer {TOKEN}"
    }
)

data = r.json()

# safety check
if "data" not in data:
    print("GitHub API Error:", data)
    exit(1)

repos = data["data"]["user"]["repositories"]["totalCount"] or 0

commits = data["data"]["user"]["contributionsCollection"]["contributionCalendar"]["totalContributions"] or 0

print("Repos:", repos)
print("Commits:", commits)
