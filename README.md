# Architecture Decision Records

This repository hosts the published ADR sites for the `confusedcom` organisation. It is a **deployment target only** — ADR source files live in each service's own repository.

## URL Structure

```
https://<custom-domain>/<team>/<project>/
```

For example: `https://adrs.confused.com/partnerships/partner-portal-service/`

## How It Works

1. A developer writes an ADR in their service repo (e.g. `partner-portal-service/docs/ADR/`)
2. On merge to `main`, a GitHub Action in the service repo builds the MkDocs site
3. The action pushes the built HTML to this repo under `<team>/<project>/`
4. GitHub Pages serves it at the custom domain
5. The landing page (`index.html`) is auto-regenerated to include new teams/projects

## Onboarding a New Service

### 1. Add files to your service repo

Copy these files from an existing onboarded service (e.g. `partner-portal-service`):

| File | What to change |
|------|---------------|
| `mkdocs.yml` | Update `site_name`, `site_url` (set to `https://<domain>/<team>/<project>/`), `site_description`, and `nav` |
| `requirements-mkdocs.txt` | Keep pinned versions as-is |
| `docs/ADR/index.md` | Update to list your service's ADRs |
| `.github/workflows/deploy-adrs.yml` | Update `TARGET_DIR` to `<team>/<project>` |

### 2. Set up authentication

Generate an SSH key pair and add:
- **Public key** as a deploy key (write access) on this repo (`confusedcom/adrs`)
- **Private key** as a secret named `ADR_DEPLOY_KEY` on your service repo

### 3. Push and verify

Merge your changes to `main`. The workflow will build your MkDocs site and push it here. The landing page updates automatically.

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
