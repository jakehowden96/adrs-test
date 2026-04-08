#!/usr/bin/env python3
"""Scans the repo root for team/project directories and generates index.html."""

import os
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
EXCLUDE_DIRS = {".git", ".github", "scripts", "node_modules", "__pycache__"}


def discover_projects() -> dict[str, list[str]]:
    """Return {team_name: [project_name, ...]} by scanning two levels deep."""
    teams: dict[str, list[str]] = {}
    for team_dir in sorted(REPO_ROOT.iterdir()):
        if not team_dir.is_dir() or team_dir.name in EXCLUDE_DIRS or team_dir.name.startswith("."):
            continue
        projects = sorted(
            p.name for p in team_dir.iterdir()
            if p.is_dir() and not p.name.startswith(".")
        )
        if projects:
            teams[team_dir.name] = projects
    return teams


def generate_html(teams: dict[str, list[str]]) -> str:
    if not teams:
        team_sections = '<p class="empty">No ADRs published yet.</p>'
    else:
        sections = []
        for team, projects in teams.items():
            links = "\n".join(
                f'            <a href="/{team}/{project}/" class="project">{project}</a>'
                for project in projects
            )
            sections.append(
                f'        <div class="team">\n'
                f'          <h2>{team}</h2>\n'
                f'{links}\n'
                f'        </div>'
            )
        team_sections = "\n".join(sections)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Architecture Decision Records</title>
  <style>
    * {{ margin: 0; padding: 0; box-sizing: border-box; }}
    body {{
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
      background: #f5f5f5;
      color: #1a1a1a;
      min-height: 100vh;
      display: flex;
      flex-direction: column;
      align-items: center;
      padding: 3rem 1rem;
    }}
    header {{
      text-align: center;
      margin-bottom: 3rem;
    }}
    header h1 {{
      font-size: 2rem;
      font-weight: 700;
      margin-bottom: 0.25rem;
    }}
    header p {{
      color: #666;
      font-size: 1rem;
    }}
    .container {{
      width: 100%;
      max-width: 640px;
    }}
    .team {{
      margin-bottom: 2rem;
    }}
    .team h2 {{
      font-size: 0.85rem;
      font-weight: 600;
      text-transform: uppercase;
      letter-spacing: 0.05em;
      color: #666;
      margin-bottom: 0.5rem;
      padding-bottom: 0.25rem;
      border-bottom: 1px solid #ddd;
    }}
    .project {{
      display: block;
      padding: 0.75rem 1rem;
      margin-bottom: 0.5rem;
      background: #fff;
      border-radius: 6px;
      text-decoration: none;
      color: #1a73e8;
      font-weight: 500;
      transition: box-shadow 0.15s;
    }}
    .project:hover {{
      box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }}
    .empty {{
      color: #999;
      text-align: center;
      padding: 2rem;
    }}
  </style>
</head>
<body>
  <header>
    <h1>Architecture Decision Records</h1>
    <p>confusedcom</p>
  </header>
  <div class="container">
{team_sections}
  </div>
</body>
</html>
"""


def main() -> None:
    teams = discover_projects()
    html = generate_html(teams)
    output = REPO_ROOT / "index.html"
    output.write_text(html)
    print(f"Generated {output} with {sum(len(p) for p in teams.values())} project(s) across {len(teams)} team(s)")


if __name__ == "__main__":
    main()
