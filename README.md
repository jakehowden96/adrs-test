# Architecture Decision Records

This repository hosts published ADR sites for the organisation via GitHub Pages. It is a **deployment target only** — no workflows or scripts run here. ADR source files live in each service's own repository, and each service's pipeline handles building, deploying, and regenerating the landing page.

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

Copy these files from an existing onboarded service (e.g. `partner-portal-service`):

| File | What to change |
|------|---------------|
| `mkdocs.yml` | Update `site_name`, `site_description`, and `nav` entries |
| `requirements-mkdocs.txt` | Keep pinned versions as-is |
| `docs/ADR/index.md` | Update to list your service's ADRs |
| `.github/workflows/deploy-adrs.yml` | Update the four env vars at the top: `TEAM_NAME`, `PROJECT_NAME`, `HOST_REPO`, `PAGES_BASE_URL` |

The `site_url` in `mkdocs.yml` is automatically derived by the pipeline from the env vars — no need to keep it in sync manually.

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

## MkDocs Dependency Versions

All services should use consistent versions to avoid visual inconsistencies:

```
mkdocs==1.6.1
mkdocs-material==9.6.12
```
