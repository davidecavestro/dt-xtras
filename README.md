<div align="center">

![DT Taxonomy Logo](/frontend/public/branding/dt-xtras-logo.svg)

# dt-xtras - Dependency-Track Extensions

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Backend Coverage](https://img.shields.io/endpoint?url=https://gist.githubusercontent.com/davidecavestro/609260f0e737a09ab2359c05e6289ea7/raw/dt-xtras-backend-coverage.json)](https://github.com/davidecavestro/dt-xtras/actions/workflows/coverage.yml)
[![Frontend Coverage](https://img.shields.io/endpoint?url=https://gist.githubusercontent.com/davidecavestro/609260f0e737a09ab2359c05e6289ea7/raw/dt-xtras-frontend-coverage.json)](https://github.com/davidecavestro/dt-xtras/actions/workflows/coverage.yml)
[![GitHub Issues](https://img.shields.io/github/issues/davidecavestro/dt-xtras.svg)](https://github.com/davidecavestro/dt-xtras/issues)
[![GitHub Pull Requests](https://img.shields.io/github/issues-pr/davidecavestro/dt-xtras.svg)](https://github.com/davidecavestro/dt-xtras/pulls)
[![GitHub Contributors](https://img.shields.io/github/contributors/davidecavestro/dt-xtras.svg)](https://github.com/davidecavestro/dt-xtras/graphs/contributors)
[![Last Commit](https://img.shields.io/github/last-commit/davidecavestro/dt-xtras.svg)](https://github.com/davidecavestro/dt-xtras/commits/main)

*A set of features that complement Dependency-Track from the outside.*

</div>

## 🎯 About

The project provides a set of features that complement [Dependency-Track](https://dependencytrack.org/).

The **taxonomy system** categorizes project tags and defines semantic relationships between them,
enabling both direct categorization and inferred labeling through graph-based relationships.
<br>
This is entirely dynamic: it's data you define, not hard-coded logic.

**Bulk actions** provide a way to activate/deactivate/delete multiple projects at once, and to
apply/remove/clone tags for multiple projects at once.

### How it fits

dt-xtras sits *beside* Dependency-Track, not in front of it. It adds new features on top of
DT's **public REST API** and keeps its own minimal state (a single `taxonomies.yaml`). It does
**not** modify or replace Dependency-Track — DT's own UI and API stay exactly as they are, and
you keep using them directly for everything they already do.

```text
                         extra features          ┌──────────────────────────────────┐
                      ┌────────────────────────▶ │ dt-xtras  (adds features)        │
                      │                          │ frontend + backend               │
  ┌────────┐          │                          │ (+ taxonomies.yaml)              │
  │  User  │──────────┤                          └────────────────┬─────────────────┘
  └────────┘          │                               │ reads / writes via
                      │                               │ DT's public API only
                      │                               ▼
                      │ core features, as always ┌──────────────────────────────────┐
                      └────────────────────────▶ │ Dependency-Track  (unchanged)    │
                                                 │ Web UI  ───────▶  REST API       │
                                                 └──────────────────────────────────┘
```

So the only thing routed "through" dt-xtras is its own added functionality; core Dependency-Track
workflows continue to go straight to DT.

![Dashboard Screenshot](docs/dashboard-screenshot.png)

### Rationale

The project was created to address the need for more flexible project organization and classification in Dependency-Track.
While Dependency-Track provides basic project tagging and properties, this extension allows for:

- **Hierarchical Classification**: Create complex taxonomies with multiple levels of categorization
- **Inferred Labeling**: Automatically classify projects based on tag patterns and relationships
- **Bulk Operations**: Manage multiple projects and tags efficiently through bulk actions
- **Custom Views**: Create brand, region, product, customer, environment or any other-centric views over your portfolio
- **Mixed Hierarchies**: Combine multiple taxonomies for complex organizational views

Should any feature implemented here be considered for inclusion in the main Dependency-Track project,
it will probably be deprecated in favor of a more integrated approach.


#### Tag Patterns (Examples)

Define your taxonomies from *Taxonomy Center* view.

An example to combine bundles on regions for brands:
- `brand:qualcoz` → Brand classification: *QUALCOZ Ltd*
- `region:eu` → Region classification: *EU*
- `bee:2026.05` → Bundle version classification: *BEE* software having version *2026.05*
- `site:qualcoz:eu:bee:2026.05` → A site serving *Brand QUALCOZ* Ltd for
Region *EU* using the software Bundle *BEE* at version *2026.05*

In the example above, the tag `brand:qualcoz:eu:bee:2026.05` provides all projects tagged as `bee:2026.05` with the following classifications:
- Brand: *QUALCOZ Ltd*
- Region: *EU*
- Bundle: *BEE*
- Version: *2026.05*

Combine environments, customers, and product versions:
- `env:staging` → Environment classification: *staging*
- `customer:acme` → Customer classification: *ACME Inc*
- `myapp:1.0.0` → Product version classification: *MYAPP* version *1.0.0*
- `deploy:acme:prod:myapp:1.0.0` → Customer *ACME Inc* + Environment *PROD* + Product *MYAPP* version *1.0.0*

In the example above, the tag `deploy:acme:prod:myapp:1.0.0` provides all projects tagged as `myapp:1.0.0` with the following classifications:
- Customer: *ACME Inc*
- Environment: *PROD*
- Product: *MYAPP*
- Version: *1.0.0*

### Hierarchy Building

1. Projects are fetched from Dependency-Track API
2. Taxonomies are applied in priority order (lower numbers first)
3. Regex patterns extract values using named capture groups
4. Tag relationships are established based on capture group names and order
5. Security metrics are rolled up from leaf nodes (projects) to root

### Security Metrics

- **Vulnerabilities**: Total count of vulnerabilities
- **Severity Breakdown**: Critical, High, Medium, Low counts
- **Risk Score**: Average inherited risk score from child nodes
- **DT-style Bars**: Visual representation matching Dependency-Track UI

## 🚀 Getting Started

dt-xtras is an **extension**, so it needs a running Dependency-Track instance to point at. You log
in to dt-xtras with your existing Dependency-Track credentials — it never stores them.

The published images on GHCR make a from-scratch run just a few commands — no build required:

1. **Get the compose file and a data directory** (the easiest way is to clone the repo):

   ```bash
   git clone https://github.com/davidecavestro/dt-xtras.git
   cd dt-xtras
   ```

2. **Create your `.env`** from the template and point it at your Dependency-Track:

   ```bash
   cp .env.example .env
   ```

   Then edit `.env`:

   ```bash
   # DT API server base URL — the backend appends /api/v1 itself, so do NOT add it here
   DT_API_URL=http://host.docker.internal:8080
   # DT web UI (used for "view in DT" links)
   DT_FRONTEND_URL=http://localhost:8080
   ```

   (Use `host.docker.internal` to reach a Dependency-Track running on your own machine.)

3. **Start it** — this pulls the official images from GHCR:

   ```bash
   docker compose up -d
   ```

4. **Open** http://localhost:3001 and log in with your Dependency-Track username and password.

To stop: `docker compose down`.

> **Before exposing it to anyone else,** set `JWT_SECRET_KEY` in `.env` to a long random value
> (e.g. `openssl rand -hex 32`). The backend ships with an insecure default that's fine for a
> local trial but must not be used in a shared or production deployment.

> **Pin a version.** `compose.yml` tracks the latest `main` build (`…/backend:main`,
> `…/frontend:main`). For a stable deployment, change those tags to a published
> [release](https://github.com/davidecavestro/dt-xtras/releases) (e.g. `:0.10.1`).
>
> **Build locally instead of pulling:**
> `docker compose -f compose.yml -f compose.build.yml up -d --build`.

See [docker-setup.md](docker-setup.md) for ports, volumes and configuration details.

## License

This project complements Dependency-Track, hence follows the same licensing terms.

## Disclaimer

This is a personal project that strives to be a community project:
it is **not endorsed by, affiliated with, or officially supported by Dependency-Track or any of its associated projects, companies, or organizations.**

### Project Status
- **Alpha**: This project is in early development (raw implementation, partial paging, partial test coverage, missing documentation)
- **Community Driven**: Developed and maintained by the open-source community
- **Independent Addition**: Complements Dependency-Track functionality but is not part of the official Dependency-Track codebase
- **Use at Your Own Risk**: Users should thoroughly test and evaluate this extension before using in production environments
- **No Warranty**: This software is provided "AS IS" without warranties of any kind, either express or implied
- **No Official Support**: Support is provided through community channels (GitHub Issues, Discussions) only

### Relationship to Dependency-Track
- **Almost no storage**: All data is stored in Dependency-Track's database except for taxonomy definitions (a single YAML file)
- **Extension Only**: This project implements additional functionality outside of the core Dependency-Track application
- **API Integration**: Uses Dependency-Track's public APIs for data retrieval and processing
- **Compatibility**: Designed to work with Dependency-Track's existing data models and API endpoints
- **No Modification**: Does not require changes to Dependency-Track core functionality

### Trademarks
- **Dependency-Track®**: Is a registered trademark of OWASP Foundation
- **Project Name**: "dt-xtras" is not associated with or endorsed by the OWASP Foundation or Dependency-Track project
- **Third-Party References**: Any references to third-party products, services, or companies are for compatibility purposes only

### Contact and Support
- **Issues**: Report bugs, feature requests, or questions via [GitHub Issues](https://github.com/davidecavestro/dt-xtras/issues)
- **Discussions**: Community support and discussions via [GitHub Discussions](https://github.com/davidecavestro/dt-xtras/discussions)
- **Documentation**: Project documentation available in this repository
- **Community**: Contributions and improvements are welcome from the community

### Legal Notice
This project is provided as a community extension without any guarantee of compatibility, fitness for purpose, or reliability. Users assume all responsibility for its use and any consequences thereof.
