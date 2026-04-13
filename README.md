# Architecture Decision Records

A unified portal for ADR documentation across the organisation, built with MkDocs Material. Service repos push their ADR markdown here; the host repo builds and deploys a single cohesive site with shared navigation, search, and styling.

## URL Structure

```
https://jakehowden96.github.io/adrs-test/
https://jakehowden96.github.io/adrs-test/<team>/<project>/
```

## How It Works

1. A developer writes an ADR in their service repo (e.g. `partner-portal-service/docs/adr/`)
2. On merge to `main`, a GitHub Action pushes the raw markdown to this repo under `docs/<team>/<project>/`
3. A host-side workflow rebuilds the unified MkDocs site
4. GitHub Pages serves the content as a single cohesive portal

## ADR Front Matter Convention

Every ADR markdown file must include this front matter:

```yaml
---
title: Use PostgreSQL for Transactional Persistence
adr_number: "001"
status: accepted    # proposed | accepted | deprecated | superseded | rejected
date: 2023-10-12
author: Jake Howden
---
```

- `adr_number`: Zero-padded string (`"001"`, `"002"`). Controls filename: `001-use-postgresql.md`
- `status`: Drives the status chip rendered on the page. One of: `proposed`, `accepted`, `deprecated`, `superseded`, `rejected`
- `date`: The date the decision was made (ISO 8601), not the commit date
- `author`: The decision author

## Onboarding a New Service

### 1. Add files to your service repo

**`docs/adr/`** — your ADR markdown files with the front matter convention above. No `index.md` is needed — the host repo generates one automatically.

**`.github/workflows/deploy-adrs.yml`** — a thin workflow that calls the reusable workflow:

```yaml
name: Deploy ADRs

on:
  push:
    branches: [main]
    paths:
      - "docs/adr/**"
  workflow_dispatch:

jobs:
  deploy:
    uses: jakehowden96/adrs-test/.github/workflows/deploy-adrs.yml@main
    with:
      team_name: <your-team>        # e.g. partnership-experiences
      project_name: <your-project>  # e.g. partner-portal-service
```

Authentication is handled by an org-level GitHub App with `contents:write` permission on this repo. No per-repo secret setup is needed — service repos inherit access automatically.

### 2. Push and verify

Merge your changes to `main`. The workflow will push your markdown here and trigger a site rebuild automatically.

## Folder Convention

```
docs/<team_name>/<project_name>/
```

- `team_name`: lowercase, hyphen-separated (e.g. `partnership-experiences`, `platform`)
- `project_name`: typically the repo name, lowercase, hyphen-separated

When a service changes team, update `team_name` in the workflow and re-run the pipeline. The reusable workflow automatically removes the project from the old team directory and places it under the new one.

## Local Development

```bash
pip install -r requirements.txt
mkdocs serve
```

The site will be available at `http://127.0.0.1:8000/`.

## Configuration

MkDocs config, theme overrides, and dependency versions are managed centrally in this repo. No `mkdocs.yml` is needed in service repos — they only push raw markdown.
