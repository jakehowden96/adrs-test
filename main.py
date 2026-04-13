"""MkDocs macros module for the ADR dashboard."""

from pathlib import Path

import yaml


def define_env(env):
    """Define macros available in templates and markdown."""

    def _parse_front_matter(content):
        """Extract YAML front matter from markdown content."""
        if not content.startswith("---"):
            return {}
        end = content.find("---", 3)
        if end == -1:
            return {}
        try:
            return yaml.safe_load(content[3:end]) or {}
        except yaml.YAMLError:
            return {}

    def _scan_adrs():
        """Scan all ADR files and return parsed metadata (cached per build)."""
        if "_adr_cache" in env.variables:
            return env.variables["_adr_cache"]

        docs_dir = Path(env.conf["docs_dir"])
        adrs = []

        for md_file in docs_dir.rglob("*.md"):
            if md_file.name == "index.md":
                continue
            content = md_file.read_text(encoding="utf-8")
            meta = _parse_front_matter(content)
            if not meta.get("adr_number"):
                continue

            rel = md_file.relative_to(docs_dir)
            parts = rel.parts
            if len(parts) < 3:
                continue

            adrs.append(
                {
                    "title": meta.get("title", md_file.stem),
                    "status": meta.get("status", "proposed"),
                    "date": str(meta.get("date", "")),
                    "author": meta.get("author", ""),
                    "adr_number": meta.get("adr_number", ""),
                    "team": parts[0],
                    "project": parts[1],
                    "url": str(rel.with_suffix("")) + "/",
                }
            )

        env.variables["_adr_cache"] = adrs
        return adrs

    @env.macro
    def recently_updated_adrs(limit=5):
        """Render the recently updated ADRs card list for the home page."""
        adrs = _scan_adrs()
        adrs.sort(key=lambda a: a["date"], reverse=True)
        adrs = adrs[:limit]

        if not adrs:
            return '<p class="adr-empty">No ADRs published yet.</p>'

        html_parts = []
        for adr in adrs:
            status_class = f"adr-status-{adr['status'].lower()}"
            html_parts.append(
                f'<a href="{adr["url"]}" class="adr-recent-card">'
                f'<div class="adr-recent-info">'
                f'<span class="adr-recent-title">{adr["title"]}</span>'
                f'<span class="adr-recent-meta">'
                f'{adr["team"].upper()} &middot; {adr["project"].upper()}'
                f"</span>"
                f"</div>"
                f'<div class="adr-recent-right">'
                f'<span class="adr-status-chip {status_class}">'
                f'{adr["status"].capitalize()}'
                f"</span>"
                f'<span class="adr-recent-date">{adr["date"]}</span>'
                f"</div>"
                f"</a>"
            )

        return "".join(html_parts)

    @env.macro
    def total_decisions():
        """Count all ADR files."""
        return len(_scan_adrs())

    @env.macro
    def active_proposals():
        """Count ADRs with status: proposed."""
        return sum(
            1 for adr in _scan_adrs() if adr["status"].lower() == "proposed"
        )

    @env.macro
    def project_adr_table():
        """Render the ADR table for a project index page."""
        page = env.page
        if not page or not page.file:
            return ""

        docs_dir = Path(env.conf["docs_dir"])
        page_path = Path(page.file.src_path)
        project_dir = docs_dir / page_path.parent

        adrs = []
        for md_file in sorted(project_dir.glob("*.md")):
            if md_file.name == "index.md":
                continue
            content = md_file.read_text(encoding="utf-8")
            meta = _parse_front_matter(content)
            if not meta.get("adr_number"):
                continue

            rel = md_file.relative_to(docs_dir)
            adrs.append(
                {
                    "number": meta.get("adr_number", ""),
                    "title": meta.get("title", md_file.stem),
                    "status": meta.get("status", "proposed"),
                    "author": meta.get("author", ""),
                    "date": str(meta.get("date", "")),
                    "url": md_file.stem + "/",
                }
            )

        if not adrs:
            return '<p class="adr-empty">No ADRs in this project yet.</p>'

        rows = []
        for adr in adrs:
            status_class = f"adr-status-{adr['status'].lower()}"
            rows.append(
                f"<tr>"
                f'<td class="adr-table-number">{adr["number"]}</td>'
                f"<td>"
                f'<a href="{adr["url"]}" class="adr-table-link">'
                f'{adr["title"]}'
                f"</a>"
                f"</td>"
                f"<td>"
                f'<span class="adr-status-chip {status_class}">'
                f'{adr["status"].capitalize()}'
                f"</span>"
                f"</td>"
                f'<td>{adr["author"]}</td>'
                f'<td>{adr["date"]}</td>'
                f"</tr>"
            )

        return (
            '<table class="adr-project-table">'
            "<thead><tr>"
            "<th>No.</th><th>Decision Title</th><th>Status</th>"
            "<th>Author</th><th>Last Updated</th>"
            "</tr></thead>"
            f"<tbody>{''.join(rows)}</tbody>"
            "</table>"
        )
