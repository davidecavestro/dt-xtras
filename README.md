# dt-xtras - Dependency-Track Taxonomy & Security Aggregator

A comprehensive security aggregation system that extends Dependency-Track with custom taxonomy-based hierarchical views and security roll-up calculations.

## Features

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

### Taxonomy System
Taxonomies define hierarchical levels using regex patterns with named capture groups. The system supports both basic and relational taxonomy definitions:

#### Basic Taxonomy
```yaml
taxonomies:
  - id: "customer"
    name: "Customer"
    pattern: '^cust:(?P<id>\w+)$'
    priority: 1
```

#### Relational Taxonomy
```yaml
taxonomies:
  - id: "environment"
    name: "Deploy Environment"
    pattern: '^env:(?P<env_type>\w+):(?P<customer>cust:\w+)$'
    priority: 2
    relations:
      - group: "customer"
        targets: "customer"
```

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

1. **Start the development environment:**
   ```bash
   # From project root
   docker compose -f .devcontainer/compose.yml up -d
   ```

2. **Backend setup:**
   ```bash
   cd backend
   pip install -r requirements.txt
   python main.py
   ```

3. **Frontend setup:**
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

### Environment Variables
- `DT_API_URL`: Dependency-Track API URL (default: `http://localhost:8081`)
- `DT_API_KEY`: Dependency-Track API key (optional, for authenticated access)

## API Endpoints

### Taxonomy Management
- `GET /api/taxonomies` - List all taxonomies
- `POST /api/taxonomies` - Create new taxonomy
- `PUT /api/taxonomies/{id}` - Update taxonomy
- `DELETE /api/taxonomies/{id}` - Delete taxonomy

### Aggregation
- `GET /api/aggregate` - Get hierarchical security data with roll-up calculations

### Proxy
- `ANY /api/v1/*` - Proxy to Dependency-Track API

## Usage Examples

### Creating Taxonomies

1. **Customer Level:**
   ```json
   {
     "id": "customer",
     "name": "Customer",
     "regex_pattern": "customer:(?P<customer>[^\\s]+)",
     "priority": 1
   }
   ```

2. **Environment Level:**
   ```json
   {
     "id": "env",
     "name": "Environment",
     "regex_pattern": "env:(?P<env>[^\\s]+)",
     "priority": 2
   }
   ```

3. **Product Level:**
   ```json
   {
     "id": "product",
     "name": "Product",
     "regex_pattern": "product:(?P<product>[^\\s]+)",
     "priority": 3
   }
   ```

### Project Tagging
Tag your Dependency-Track projects with hierarchical information:
```
customer:acme env:production product:webapp
customer:globex env:staging product:api
```

### Resulting Hierarchy
```
├── acme (Customer)
│   ├── production (Environment)
│   │   └── webapp (Product)
│   │       └── [Project UUIDs...]
│   └── staging (Environment)
│       └── api (Product)
│           └── [Project UUIDs...]
└── globex (Customer)
    └── staging (Environment)
        └── api (Product)
            └── [Project UUIDs...]
```

## File Structure

```
dt-extras/
├── backend/
│   ├── main.py              # FastAPI application
│   └── requirements.txt     # Python dependencies
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── Dashboard.vue
│   │   │   ├── SecurityRow.vue
│   │   │   ├── VulnerabilityBar.vue
│   │   │   ├── RiskScoreBadge.vue
│   │   │   └── TaxonomyEditor.vue
│   │   ├── App.vue
│   │   ├── main.js
│   │   └── style.css
│   ├── package.json
│   └── vite.config.js
├── api/
│   └── taxonomies.json      # Taxonomy configuration storage
├── .devcontainer/
│   ├── Dockerfile
│   ├── compose.yml
│   └── devcontainer.json
└── README.md
```

## Development Notes

### Backend
- Uses filesystem storage (`api/taxonomies.json`) for simplicity
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

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly with the development environment
5. Submit a pull request

## License

This project extends Dependency-Track and follows the same licensing terms.
