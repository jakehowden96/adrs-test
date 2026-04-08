# Architecture Decision Records

This repository hosts published ADR sites for the organisation via GitHub Pages. It is a **deployment target only**. ADR source files live in each service's own repository. This repo provides a [reusable workflow](https://docs.github.com/en/actions/sharing-automations/reusing-workflows) that handles building, deploying, and regenerating the landing page — service repos call it with just their team and project name.

## URL Structure

```
https://jakehowden96.github.io/adrs-test/<team>/<project>/
```

For example: `https://jakehowden96.github.io/adrs-test/partnerships/partner-portal-service/`

## How It Works

1. A developer writes an ADR in their service repo (e.g. `partner-portal-service/docs/ADR/`)
2. On merge to `main`, a GitHub Action in the service repo builds the MkDocs site
3. The action pushes the built HTML to this repo under `<team>/<project>/`
4. The action regenerates the landing page (`index.html`) to include all teams/projects
5. GitHub Pages serves the content

## Onboarding a New Service

### 1. Add files to your service repo

You only need two things:

**`docs/ADR/`** — your ADR markdown files (at minimum an `index.md`)

**`.github/workflows/deploy-adrs.yml`** — a thin workflow that calls the reusable workflow in this repo:

```yaml
name: Deploy ADRs

on:
  push:
    branches: [main]
    paths:
      - "docs/ADR/**"
  workflow_dispatch:

jobs:
  deploy:
    uses: jakehowden96/adrs-test/.github/workflows/deploy-adrs.yml@main
    with:
      team_name: <your-team>        # e.g. partnerships
      project_name: <your-project>  # e.g. partner-portal-service
    secrets:
      deploy_key: ${{ secrets.ADR_DEPLOY_KEY }}
```

### 2. Set up authentication

Generate an SSH key pair and add:
- **Public key** as a deploy key (write access) on this repo
- **Private key** as a secret named `ADR_DEPLOY_KEY` on your service repo

### 3. Push and verify

Merge your changes to `main`. The workflow will build your MkDocs site, push it here, and regenerate the landing page automatically.

## Folder Convention

```
<team_name>/<project_name>/
```

- `team_name`: lowercase, hyphen-separated (e.g. `partnerships`, `platform`)
- `project_name`: typically the repo name, lowercase, hyphen-separated

## MkDocs Configuration

MkDocs config, theme, and dependency versions are managed centrally in the reusable workflow. No `mkdocs.yml` or `requirements-mkdocs.txt` is needed in service repos.
