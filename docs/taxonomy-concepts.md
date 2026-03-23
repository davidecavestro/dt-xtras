# Taxonomy System: Core Concepts & Definitions

## 🎯 Overview

The taxonomy system provides a structured way to categorize project tags and define semantic relationships between them, enabling both direct categorization and inferred labeling through graph-based relationships.

## 📚 Core Concepts

### 1. Taxonomy (plural: Taxonomies)

**Definition:** A taxonomy is a formal classification scheme that defines:
- **Regex Pattern:** A regular expression with named capture groups for matching tags
- **Relations:** Semantic relationships to other taxonomies
- **Priority:** Hierarchical ordering for conflict resolution

**Purpose:** Taxonomies provide the rules for categorizing tags and establishing how different tag categories relate to each other.

**Examples:**
```yaml
Environment Taxonomy:
  pattern: '^env:(?P<env_type>\\w+)$'
  relations: [{ group: 'deploy', targets: 'env' }]

Customer Taxonomy:
  pattern: '^cust:(?P<customer_id>\\w+)$'
  relations: [{ group: 'deploy', targets: 'customer' }]

Deployment Taxonomy:
  pattern: '^deploy:(?P<env>\\w+):(?P<customer>\\w+):(?P<product_version>[\\w-]+:[\\d\\.]+)$'
  relations: [
    { group: 'env', targets: 'env' },
    { group: 'customer', targets: 'customer' },
    { group: 'product_version', targets: 'product_version' }
  ]
```

### 2. Tag

**Definition:** A label that can be applied to a project in Dependency Track.

**Structure:** Tags follow the format `type:value` where:
- `type` indicates the category (e.g., `env`, `cust`, `myapp`)
- `value` provides the specific instance (e.g., `prod`, `acme`, `1.0.0`)

**Examples:**
- `env:prod` - Production environment
- `cust:acme` - ACME customer
- `myapp:1.0.0` - Application version 1.0.0
- `deploy:prod:acme:myapp:1.0.0` - Complete deployment specification

### 3. Project Labeling

#### 3.1 Hard Labeling (Direct Labeling)

**Definition:** A project `P` is **hardly labeled** by tag `T` if tag `T` is directly applied to project `P` in Dependency Track.

**Notation:** `HardLabel(P, T)`

**Example:** If project `webapp-frontend` has tag `env:prod` in Dependency Track, then:
```
HardLabel(webapp-frontend, env:prod) = true
```

#### 3.2 Soft Labeling (Inferred Labeling)

**Definition:** A project `P` is **softly labeled** by tag `S` if the tags graph (defined by taxonomies) contains at least one path from `S` to a tag `T` where `HardLabel(P, T)` is true.

**Notation:** `SoftLabel(P, S) = ∃path(S → T) ∧ HardLabel(P, T)`

**Example:** If project `webapp-frontend` has tag `deploy:prod:acme:myapp:1.0.0` and the graph contains:
```
deploy:prod:acme:myapp:1.0.0 → env:prod
deploy:prod:acme:myapp:1.0.0 → cust:acme
deploy:prod:acme:myapp:1.0.0 → myapp:1.0.0
```

Then:
```
SoftLabel(webapp-frontend, env:prod) = true
SoftLabel(webapp-frontend, cust:acme) = true
SoftLabel(webapp-frontend, myapp:1.0.0) = true
```

### 4. Tag Graph

**Definition:** The tag graph is an undirected graph `G = (V, E)` where:
- **Vertices (V):** All tags in the system
- **Edges (E):** Connections between tags that share components based on taxonomy relations

**Edge Formation:** Two tags `T1` and `T2` have an edge if:
1. They belong to taxonomies with defined relations
2. Their parsed components share at least one value
3. The shared component establishes semantic relationship

**Example:**
```
deploy:prod:acme:myapp:1.0.0
├── Components: { env: env:prod, customer: acme, product_version: myapp:1.0.0 }
env:prod
├── Components: { type: env, value: prod }
Result: Edge exists (shared 'env' component)
```

### 5. Tree Projection

**Definition:** A tree projection is a hierarchical view of the tag graph with a selected taxonomy as root nodes.

**Properties:**
- **Root Selection:** Tags from the selected taxonomy become root nodes
- **Hierarchy Derivation:** Children are connected nodes from other taxonomies
- **Cycle Prevention:** Graph cycles are cut to maintain tree structure
- **BFS Traversal:** Breadth-first search ensures proper level assignment

**Example:** Environment taxonomy tree projection:
```
env:prod (root)
├── deploy:prod:acme:myapp:1.0.0 (child)
└── deploy:prod:foo:myapp:1.0.0 (child)

env:staging (root)
├── deploy:staging:acme:myapp:1.0.1 (child)
└── deploy:staging:bar:myapp:2.0.0 (child)
```

## 🔧 Technical Implementation

### Tag Component Parsing

**Purpose:** Extract semantic components from tag names for relationship matching.

**Algorithm:**
```javascript
parseTagComponents(tagName) {
  // Deployment tags: deploy:prod:acme:myapp:1.0.0
  if (tagName.startsWith('deploy:')) {
    const parts = tagName.split(':')
    if (parts.length >= 5) {
      return {
        deploy: parts[0],
        env: `env:${parts[1]}`,
        customer: `cust:${parts[2]}`,
        product_version: `${parts[3]}:${parts[4]}`,
        full_tag: tagName
      }
    }
  }

  // Simple tags: env:prod, cust:acme, myapp:1.0.0
  const parts = tagName.split(':')
  if (parts.length === 2) {
    return {
      type: parts[0],
      value: parts[1],
      full_tag: tagName
    }
  }

  return null
}
```

### Graph Construction

**Algorithm:**
1. Initialize all tags as graph nodes
2. For each taxonomy relation:
   - Find all tags matching source taxonomy pattern
   - Find all tags matching target taxonomy pattern
   - Create edges between tags sharing components
3. Build undirected adjacency list

### Tree Derivation

**Algorithm:**
1. Select taxonomy for tree roots
2. Perform BFS from root nodes through graph
3. Track visited nodes to prevent cycles
4. Assign levels based on distance from roots
5. Build hierarchical structure

## 📊 Use Cases

### 1. Project Discovery
Find all projects with specific characteristics:
```sql
-- Find all production projects
SELECT * FROM projects
WHERE SoftLabel(project, 'env:prod') = true

-- Find all ACME customer projects
SELECT * FROM projects
WHERE SoftLabel(project, 'cust:acme') = true
```

### 2. Impact Analysis
Understand deployment implications:
```
If we update env:prod infrastructure:
→ Affects all projects SoftLabel(project, 'env:prod') = true
→ Includes projects with deploy:prod:cust:* tags
→ Enables targeted notifications and testing
```

### 3. Compliance Reporting
Generate compliance metrics:
```
Customer ACME projects:
→ HardLabel(project, 'cust:acme') = direct ACME projects
→ SoftLabel(project, 'cust:acme') = ACME deployments
→ Combined view gives complete ACME footprint
```

## 🎯 Benefits

1. **Semantic Understanding:** Tags convey meaning through relationships
2. **Scalable Categorization:** New tags automatically inherit relationships
3. **Flexible Queries:** Both direct and indirect labeling support
4. **Visual Navigation:** Tree projections provide intuitive browsing
5. **Automated Inference:** Soft labeling reduces manual tagging effort

## 🔄 Future Enhancements

1. **Visual Graph Editor:** Interactive taxonomy relationship management
2. **Advanced Inference Rules:** Custom relationship types and weights
3. **Temporal Relations:** Time-based tag relationships
4. **Multi-level Hierarchies:** Nested taxonomy support
5. **Machine Learning:** Automatic taxonomy discovery from tag patterns
