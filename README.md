<div align="center">

![DT Taxonomy Logo](/frontend/public/branding/dt-xtras-logo.svg)

# dt-xtras - Dependency-Track Extensions

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Vue.js](https://img.shields.io/badge/Vue.js-3.x-green.svg)](https://vuejs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-red.svg)](https://fastapi.tiangolo.com/)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind%20CSS-3.x-38B2AC.svg)](https://tailwindcss.com/)
[![GitHub Issues](https://img.shields.io/github/issues/davidecavestro/dt-xtras.svg)](https://github.com/davidecavestro/dt-xtras/issues)
[![GitHub Pull Requests](https://img.shields.io/github/issues-pr/davidecavestro/dt-xtras.svg)](https://github.com/davidecavestro/dt-xtras/pulls)
[![GitHub Contributors](https://img.shields.io/github/contributors/davidecavestro/dt-xtras.svg)](https://github.com/davidecavestro/dt-xtras/graphs/contributors)
[![Last Commit](https://img.shields.io/github/last-commit/davidecavestro/dt-xtras.svg)](https://github.com/davidecavestro/dt-xtras/commits/main)

*A comprehensive security aggregation system that extends Dependency-Track with custom taxonomy-based hierarchical views and security roll-up calculations.*

</div>

## 🎯 About

### Backend (FastAPI)

- **Taxonomy CRUD API**: Create, read, update, and delete taxonomy configurations
- **Aggregation Engine**: Fetches projects from Dependency-Track and applies regex-based taxonomy parsing
- **Relational Linker**: Automatically establishes parent-child relationships based on regex capture groups
- **Security Roll-up**: Calculates aggregated vulnerability metrics and risk scores across hierarchy levels
- **DT API Proxy**: Proxies standard `/api/v1` calls to avoid CORS and enable deep-linking

### Frontend (Vue 3 + Tailwind CSS)

- **Hierarchical Dashboard**: Tree-table view with expandable/collapsible nodes
- **DT-style Visualizations**: Vulnerability severity bars and risk score badges
- **Taxonomy Editor**: Interactive regex pattern testing and taxonomy management
- **Tag Manager**: Complete CRUD operations for tags with project linking
- **Real-time Updates**: Live data refresh with loading states
- **Dark Theme Support**: Complete dark mode implementation with user preference persistence

## Code Quality & Maintenance

### Linting & Formatting

The project includes comprehensive code quality tools:

- **VS Code Settings**: Automatic formatting on save, trailing whitespace cleanup
- **Prettier**: Code formatting for Vue, JavaScript, TypeScript, JSON, YAML, Markdown
- **Black**: Python code formatting
- **Pre-commit Hooks**: Automatic whitespace cleanup and formatting checks
- **Custom Scripts**: Manual cleanup commands for trailing whitespaces

### Cleanup Commands

```bash
# Clean all trailing whitespaces
npm run cleanup
# or
./scripts/cleanup-whitespace.sh

# Run all linting checks
npm run lint
# or
pre-commit run --all-files

# Format all files
npm run format
```

## Architecture

### Taxonomy & Project Version Architecture

The system provides a flexible, multi-perspective approach to security data organization:

#### Project Versions (First-Class Entities)

- **Lifecycle Management**: Create, update, delete project versions via API
- **Tag-Based Classification**: Projects are tagged with `myapp:version`, `customer:id`, `env:type` patterns
- **Independent Operations**: Project versions can exist independently of DT project tags
- **Aggregation Source**: Security hierarchy can be built from project versions OR raw DT projects

#### Taxonomy System (Hierarchical Views)

- **Multiple Perspectives**: Define different hierarchical views on the same underlying data
- **Flexible Relations**: Link taxonomy levels using regex capture groups and explicit relations
- **User-Defined Hierarchies**: End users can create custom hierarchies via the taxonomy editor
- **No Imposed Model**: The system doesn't enforce a single "correct" hierarchy

#### Data Flow

```
DT Projects → Tags → Project Versions API → Taxonomy Processing → Security Hierarchy
     ↓              ↓                    ↓                      ↓
Raw Data → Classification → Structured Data → Hierarchical Views
```

#### Taxonomy Examples

##### Basic Taxonomy

```yaml
taxonomies:
  - id: "customer"
    name: "Customer"
    pattern: '^cust:(?P<id>\w+)$'
    priority: 1
```

##### Advanced Deployment Taxonomy

```yaml
taxonomies:
  - id: "customer"
    name: "Customer"
    pattern: '^cust:(?P<id>\w+)$'
    priority: 1

  - id: "env"
    name: "Environment"
    pattern: '^env:(?P<env_type>\w+)$'
    priority: 2

  - id: "deploy"
    name: "Deployment"
    pattern: '^deploy:(?P<env>\w+):(?P<customer>cust:\w+):(?P<product_version>[\w-]+:[\d\.]+)$'
    priority: 3
    relations:
      - group: "env"
        targets: "env"
      - group: "customer"
        targets: "customer"
      - group: "product_version"
        targets: "product_version"

  - id: "product_version"
    name: "Product Version"
    pattern: '^(?!(?:env|cust|deploy):)(?P<product_name>[\w-]+):(?P<version>[\d\w\.-]+)$'
    priority: 4
```

#### Advanced Deployment Model

This sophisticated deployment model provides:

1. **Environment Enumeration** (`env` taxonomy): Lists environment types (prod, staging, dev)
2. **Deployment Composition** (`deploy` taxonomy): Links environment + customer + product version
3. **Multi-Parent Relations**: Deployments link to all three parent taxonomies simultaneously
4. **Complete Traceability**: Full deployment context in single tag

#### Example Tag Flow

```
DT Project: myapp:1.0.0
Tags Added: deploy:prod:cust:acme:myapp:1.0.0, env:prod, cust:acme
Result:
├── Environment: prod
├── Customer: acme
├── Product Version: myapp:1.0.0
└── Deployment: prod:acme:myapp:1.0.0
    ├── Parent: env:prod
    ├── Parent: customer:acme
    └── Parent: product_version:myapp:1.0.0
```

#### Use Cases

1. **Product-Centric View**: Create product version taxonomy to see `myapp:1.0.0` deployments
2. **Customer-Centric View**: Create customer taxonomy to see all products per customer
3. **Environment-Centric View**: Create environment taxonomy to see deployment distributions
4. **Mixed Hierarchies**: Combine multiple taxonomies for complex organizational views

#### Tag Patterns (Examples)

- `myapp:1.0.0` → Product version classification
- `webapp:0.0.1-RELEASE` → Product version with release suffix
- `myapp:1.2` → Product version with two components
- `myapp:1` → Simple product version
- `cust:acme env:prod myapp:1.0.0` → Customer + Environment + Product version
- `env:staging web:frontend:2.1.0` → Environment + Product version

#### Supported Version Formats

The product version taxonomy supports various version formats:

- **Semantic Versions**: `1.2.3`, `2.0.0`
- **Release Suffixes**: `0.0.1-RELEASE`, `1.2.3-BETA`
- **Simple Versions**: `1.2`, `1`

#### Format Specification

- **`id`**: Unique identifier for the taxonomy level
- **`name`**: Display name for the UI
- **`pattern`**: Regex pattern with named capture groups
- **`priority`**: Processing order (lower numbers = higher priority)
- **`relations`**: Optional parent-child relationship definitions
  - **`group`**: Capture group name to match
  - **`targets`**: Target taxonomy ID for parent relationship

### Hierarchy Building

1. Projects are fetched from Dependency-Track API
2. Taxonomies are applied in priority order (lower numbers first)
3. Regex patterns extract values using named capture groups
4. Parent-child relationships are established based on capture group names
5. Security metrics are rolled up from leaf nodes (projects) to root

### Security Metrics

- **Vulnerabilities**: Total count of vulnerabilities
- **Severity Breakdown**: Critical, High, Medium, Low counts
- **Risk Score**: Average inherited risk score from child nodes
- **DT-style Bars**: Visual representation matching Dependency-Track UI

## Setup

### Prerequisites

- Docker and Docker Compose
- Node.js 20+ (for development)
- Python 3.11+ (for development)

### Development Setup

1. **Open in VS Code with Devcontainer:**
   - Open the project in VS Code
   - Reopen in Container when prompted
   - Run `./.devcontainer/start.sh` to see available commands

2. **Or start manually:**

   ```bash
   # From project root
   docker compose -f .devcontainer/compose.yml up -d
   ```

3. **Backend setup:**

   ```bash
   cd backend
   pip install -r requirements.txt
   python main.py
   ```

4. **Frontend setup:**
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

### API Endpoints

#### Taxonomy Management

- `GET /api/taxonomies` - List all taxonomies
- `POST /api/taxonomies` - Create new taxonomy
- `PUT /api/taxonomies/{id}` - Update existing taxonomy
- `DELETE /api/taxonomies/{id}` - Delete taxonomy

#### Tag Management

- `GET /api/tags` - List all tags with project counts
- `POST /api/tags` - Create new tag
- `PUT /api/tags/{id}` - Update existing tag
- `DELETE /api/tags/{id}` - Delete tag
- `GET /api/tags/{id}/projects` - Get projects using specific tag

#### Project Version Management

- `GET /api/project-versions` - List all project versions with taxonomy relationships
- `POST /api/project-versions` - Create new project version (tags existing project)
- `PUT /api/project-versions/{id}` - Update project version
- `DELETE /api/project-versions/{id}` - Delete project version

#### Security Aggregation

- `GET /api/aggregate` - Get hierarchical security data with roll-up calculations

### Environment Variables

- `DT_API_URL`: Dependency-Track API URL (default: `http://localhost:8081`)
- `DT_API_KEY`: Dependency-Track API key (optional, for authenticated access)

## Development Workflow

### Quick Start

```bash
# Start all services
./scripts/start-services.sh

# Or start individually
./scripts/start-backend.sh    # Backend on port 8000
./scripts/start-frontend.sh   # Frontend on port 5173

# Stop all services
./scripts/stop-services.sh
```

### Code Quality

```bash
# Clean trailing whitespaces
npm run cleanup

# Run all linting checks
npm run lint

# Format all files
npm run format
```

### Environment Variables

- `DT_API_URL`: Dependency-Track API URL (default: `http://localhost:8081`)
- `DT_API_KEY`: Dependency-Track API key (optional, for authenticated access)

- `GET /api/aggregate` - Get hierarchical security data with roll-up calculations

### DT API Proxy

- `ANY /api/v1/*` - Proxy to Dependency-Track API

## Usage Examples

### Creating Taxonomies

1. **Customer Level:**

   ```bash
   curl -X POST http://localhost:8000/api/taxonomies \
     -H "Content-Type: application/json" \
     -d '{"id": "customer", "name": "Customer", "pattern": "^cust:(?P<id>\\w+)$", "priority": 1}'
   ```

2. **Environment Level with Customer Relations:**
   ```bash
   curl -X POST http://localhost:8000/api/taxonomies \
     -H "Content-Type: application/json" \
     -d '{
       "id": "environment",
       "name": "Deploy Environment",
       "pattern": "^env:(?P<env_type>\\w+):(?P<customer>cust:\\w+)$",
       "priority": 2,
       "relations": [
         {"group": "customer", "targets": "customer"}
       ]
     }'
   ```

### Managing Project Versions

```bash
# List all project versions
curl http://localhost:8000/api/project-versions

# Create a new project version (tags existing project)
curl -X POST http://localhost:8000/api/project-versions \
  -H "Content-Type: application/json" \
  -d '{
    "name": "MyApp",
    "version": "1.0.0",
    "customer_id": "acme",
    "project_uuid": "existing-project-uuid"
  }'
```

## File Structure

```
dt-extras/
├── api/
│   ├── taxonomies.yaml          # Main configuration (user-defined)
│   └── taxonomies.example.yaml  # Example configuration (reference)
├── backend/
│   └── main.py                 # FastAPI application
├── frontend/
│   └── src/                   # Vue.js application
├── scripts/
│   ├── start-services.sh        # Start all services
│   ├── start-backend.sh         # Start backend only
│   ├── start-frontend.sh        # Start frontend only
│   ├── stop-services.sh         # Stop all services
│   └── cleanup-whitespace.sh   # Clean trailing whitespaces
├── .vscode/
│   ├── settings.json            # VS Code preferences
│   └── tasks.json             # IDE task definitions
└── api/
    └── taxonomies.yaml          # User's active taxonomy definitions
```

### Configuration Management

#### Template-Based Initialization

The system uses a template-based approach for configuration management:

1. **First Run**: Copies `taxonomies.example.yaml` to `taxonomies.yaml` if missing
2. **Template Reference**: Example file serves as documentation and starting point
3. **Single Config**: Only `taxonomies.yaml` is the active configuration
4. **Direct Editing**: Users modify the main file directly - no versioning complexity

#### File Strategy

- **Main Config**: `api/taxonomies.yaml` - User's active taxonomy definitions (tracked)
- **Template**: `api/taxonomies.example.yaml` - Documentation and reference (ignored)
- **Clean Git History**: Linear progression of configuration changes
- **No Backup Bloat**: No accumulation of `.bak` files

#### Benefits

- **Always Current**: No stale versioned configurations
- **Simple Workflow**: Edit one file, see immediate results
- **Clear Documentation**: Template file shows exactly what's possible
- **Version Control Ready**: Clean git history of actual changes

## Development Notes

### Backend

- Uses filesystem storage (`api/taxonomies.yaml`) for simplicity
- Implements recursive roll-up calculations for security metrics
- Handles Dependency-Track API authentication via headers

### Frontend

- Vue 3 Composition API with reactive state management
- Tailwind CSS for responsive, modern UI
- Real-time regex testing in taxonomy editor
- Expandable tree-table with hierarchical indentation

### Integration

- Proxy endpoints enable seamless integration with existing Dependency-Track UI
- Project UUIDs are used as leaf node keys for deep-linking
- CORS handled through proxy to avoid browser security restrictions

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly with the development environment
5. Submit a pull request

## License

This project extends Dependency-Track and follows the same licensing terms.

## Disclaimer

**⚠️ IMPORTANT NOTICE**

This is a **community project** and is **not endorsed by, affiliated with, or officially supported by Dependency-Track or any of its associated projects, companies, or organizations.**

### Project Status
- **Community Driven**: Developed and maintained by the open-source community
- **Independent Extension**: Extends Dependency-Track functionality but is not part of the official Dependency-Track codebase
- **Use at Your Own Risk**: Users should thoroughly test and evaluate this extension before using in production environments
- **No Warranty**: This software is provided "AS IS" without warranties of any kind, either express or implied
- **No Official Support**: Support is provided through community channels (GitHub Issues, Discussions) only

### Relationship to Dependency-Track
- **Extension Only**: This project adds functionality to Dependency-Track but does not modify the core Dependency-Track application
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
