# ADR Hosting Platform — Setup Plan

## What This Is

A platform for hosting Architecture Decision Records (ADRs) from multiple service repos under a single GitHub Pages URL. Each service repo owns its ADR source markdown, builds it with MkDocs, and pushes the rendered HTML to this repo. This repo is the static file deployment target — it holds no ADR source content.

## Target URL Structure

```
https://<custom-domain>/<team>/<project>/
```

Example: `https://adrs.confused.com/partnerships/partner-portal-service/`

## Architecture

```
Service Repos (own ADR source + MkDocs config + GitHub Action)
  ┌─────────────────────────┐    ┌─────────────────────────┐
  │ partner-portal-service  │    │ other-service            │
  │  docs/ADR/*.md          │    │  docs/ADR/*.md           │
  │  mkdocs.yml             │    │  mkdocs.yml              │
  │  .github/workflows/     │    │  .github/workflows/      │
  │    deploy-adrs.yml      │    │    deploy-adrs.yml       │
  └──────────┬──────────────┘    └──────────┬──────────────┘
             │ pushes built HTML              │ pushes built HTML
             ▼                                ▼
  ┌──────────────────────────────────────────────────────────┐
  │ confusedcom/adrs  (this repo — GitHub Pages host)        │
  │  index.html  (auto-generated landing page)               │
  │  partnerships/partner-portal-service/  ← built HTML      │
  │  other-team/other-service/             ← built HTML      │
  │  CNAME                                                   │
  └──────────────────────────────────────────────────────────┘
             │
             ▼
        GitHub Pages serves the custom domain
```

## What's Been Done

All files in this repo are created and ready to push:

- `CNAME` — set to `adrs.confused.com` (update if the actual domain differs)
- `scripts/generate-index.py` — scans two levels of subdirectories, generates a styled `index.html` landing page
- `.github/workflows/generate-landing-page.yml` — rebuilds `index.html` on push to main
- `index.html` — initial empty-state landing page (regenerates automatically when services push content)
- `README.md` — documents the architecture, folder convention, and onboarding steps

The first service repo (`confusedcom/partner-portal-service`) also has all files ready locally at `~/Documents/repos/partner-portal/partner-portal-service/`:

- `mkdocs.yml` — MkDocs Material theme config, `site_url` pointed at the subfolder
- `requirements-mkdocs.txt` — pinned `mkdocs==1.6.1`, `mkdocs-material==9.6.12`
- `docs/ADR/index.md` — landing page listing the service's ADRs
- `.github/workflows/deploy-adrs.yml` — builds MkDocs, pushes HTML to this repo under `partnerships/partner-portal-service/`
- `.gitignore` — updated with `site/` entry

The MkDocs build has been verified locally (`mkdocs build --strict` passes).

## What Still Needs Doing

### 1. Create this repo on GitHub

Push this directory as `confusedcom/adrs`.

### 2. Enable GitHub Pages

Settings > Pages > Deploy from branch `main`, root `/`. Enable HTTPS enforcement.

### 3. DNS

Add a CNAME record for the custom domain pointing to `confusedcom.github.io`. Update the `CNAME` file in this repo if the domain is not `adrs.confused.com`.

### 4. Deploy key for cross-repo push

Each service repo needs to push built HTML to this repo. For `partner-portal-service`:

1. Generate an SSH key pair: `ssh-keygen -t ed25519 -f adr-deploy-key -C "adr-deploy"`
2. Add the **public key** as a deploy key with **write access** on `confusedcom/adrs`
3. Add the **private key** as a repository secret named `ADR_DEPLOY_KEY` on `confusedcom/partner-portal-service`

> At scale (3+ services), consider migrating to a GitHub App with `contents: write` on this repo to avoid per-repo key proliferation.

### 5. Push partner-portal-service changes

The MkDocs config, ADR index page, and GitHub Action workflow need to be merged to `main` on `partner-portal-service`. The workflow triggers on push to `main` when `docs/ADR/**` or `mkdocs.yml` change, and also supports `workflow_dispatch` for manual runs.

### 6. Verify end-to-end

- Trigger the `deploy-adrs` workflow (manually or by pushing an ADR change)
- Confirm built HTML appears in this repo under `partnerships/partner-portal-service/`
- Confirm `generate-landing-page` workflow fires and `index.html` updates
- Browse the custom domain and verify navigation, search, and dark/light toggle work

## Onboarding Other Services

See `README.md` in this repo. In short: copy `mkdocs.yml`, `requirements-mkdocs.txt`, and `deploy-adrs.yml` from `partner-portal-service`, update `site_url` and `TARGET_DIR` to `<team>/<project>`, set up a deploy key, and merge to main. The landing page updates automatically.

## Key Design Decisions

- **No central content repo** — each service owns its ADR source and pipeline. This repo is deployment-only.
- **MkDocs Material theme** — chosen for built-in search, dark/light toggle, and clean rendering.
- **Deploy key auth** — simplest starting point. One key per service repo, scoped to this repo only.
- **Race condition handling** — service workflows retry pushes with rebase (3 attempts, random jitter) since each writes to its own subfolder.
- **Landing page auto-generation** — `scripts/generate-index.py` scans directories on push, no manual maintenance needed.
- **CI/CD independence** — service application pipelines run on Azure DevOps; ADR deployment runs on GitHub Actions. No interference.
