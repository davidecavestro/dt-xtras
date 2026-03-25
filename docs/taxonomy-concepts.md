# Taxonomy System: Core Concepts & Definitions

## 🎯 Overview

The taxonomy system provides a structured way to categorize project tags and define semantic relationships between them, enabling both direct categorization and inferred labeling through graph-based relationships.

## 📚 Core Concepts

### 1. Taxonomy (plural: Taxonomies)

**Definition:** A taxonomy is a formal classification scheme that defines:
- **Regex Pattern:** A regular expression with named capture groups for matching tags
- **Relations:** Semantic relationships to other taxonomies, based on capture groups
- **Priority:** Hierarchical ordering for conflict resolution

**Purpose:** Taxonomies provide the rules for categorizing tags and establishing how different tag categories relate to each other.

### 1.1 Associative Taxonomy

**Definition:** An associative taxonomy is a taxonomy where:
- All capture groups in its pattern are used for relations to other taxonomies
- It acts as a junction/associative entity in the Entity-Relationship model
- It connects multiple taxonomy types without being a primary categorization itself

**Characteristics:**
- **Invisible in Tree Projection:** Can be hidden from visual tree structures
- **Direct Component Relationships:** Enables direct edges between its related taxonomies
- **Semantic Foundation:** Provides the underlying meaning for cross-taxonomy relationships

**Example - Deployment Taxonomy:**
```yaml
Deployment Taxonomy:
  pattern: ^deploy:(?P<env>\w+):(?P<customer>\w+):(?P<product_version>[\w-]+:[\d\.]+)$
  relations:
    - group: env         # Links to Environment taxonomy
      targets: env
    - group: customer    # Links to Customer taxonomy
      targets: customer
    - group: product_version  # Links to Product Version taxonomy
      targets: product_version
```

**Behavior:**
- **Normal Mode:** Creates edges `deploy:prod:acme:myapp:1.0.0 ↔ env:prod`, `deploy:prod:acme:myapp:1.0.0 ↔ cust:acme`
- **Associative Mode:** Creates direct edge `env:prod ↔ cust:acme` (deployment tag becomes invisible)

**Benefits:**
1. **Cleaner Visual Trees:** Removes intermediate nodes that don't add categorization value
2. **Simplified Data Model:** Direct relationships between primary taxonomies
3. **Flexible Loading:** Can toggle between visible and invisible modes
4. **Semantic Clarity:** Maintains the meaning of relationships while simplifying visualization

**Examples:**
```yaml
Environment Taxonomy:
  pattern: '^env:(?P<env_type>\\w+)$'
  relations: [{ group: 'deploy', targets: 'env' }]

Customer Taxonomy:
  pattern: '^cust:(?P<customer_id>\\w+)$'
  relations: [{ group: 'deploy', targets: 'customer' }]

Product Version Taxonomy:
  pattern: ^(?!(?:env|cust|deploy):)(?P<product_name>[\w-]+):(?P<version>[\d\w\.-]+)$
  relations: [{ group: 'deploy', targets: 'product_version' }]

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

**Structure:** Tags conventionally follow the format `type:value` where:
- `type` indicates the category (e.g., `env`, `cust`, `myapp`)
- `value` provides the specific instance (e.g., `prod`, `acme`, `1.0.0`)

**Examples:**
- `env:prod` - Production environment
- `cust:acme` - ACME customer
- `myapp:1.0.0` - "myapp" product version 1.0.0
- `deploy:prod:acme:myapp:1.0.0` - Complete deployment specification

### 3. Project Labeling

#### 3.1 Hard Labeling (Direct Labeling)

**Definition:** A project `P` is **hardly labeled** by tag `T` if tag `T` is directly applied to project `P` in Dependency Track.

**Notation:** `HardLabel(P, T)`

**Example:** If project `myapp` has tag `env:prod` in Dependency Track, then:
```
HardLabel(myapp, env:prod) = true
```

#### 3.2 Soft Labeling (Inferred Labeling)

**Definition:** A project `P` is **softly labeled** by tag `S` if the tags graph (defined by taxonomies) contains at least one path from `S` to a tag `T` where `HardLabel(P, T)` is true.

**Notation:** `SoftLabel(P, S) = ∃path(S → T) ∧ HardLabel(P, T)`

**Example:** If project `myapp` has tag `deploy:prod:acme:myapp:1.0.0` and the graph contains:
```
deploy:prod:acme:myapp:1.0.0 → env:prod
deploy:prod:acme:myapp:1.0.0 → cust:acme
deploy:prod:acme:myapp:1.0.0 → myapp:1.0.0
```

Then:
```
SoftLabel(myapp, env:prod) = true
SoftLabel(myapp, cust:acme) = true
SoftLabel(myapp, myapp:1.0.0) = true
```

### 4. Tag Graph

**Definition:** The tag graph is an undirected graph `G = (V, E)` where:
- **Vertices (V):** All tags in the system matching taxonomy patterns
- **Edges (E):** Connections between tags that share components based on taxonomy relations

**Components:** Semantic parts extracted from tags during parsing. Components represent meaningful segments of a tag that can be shared across different tags to establish relationships.

**Component Examples:**
- `deploy:prod:acme:myapp:1.0.0` → `{ env: env:prod, customer: acme, product_version: myapp:1.0.0 }`
- `env:prod` → `{ type: env, value: prod }`
- `cust:acme` → `{ type: cust, value: acme }`

**Edge Formation:** Two tags `T1` and `T2` have an edge if:
1. They belong to taxonomies with defined relations
2. Their parsed components share at least one value
3. The shared component establishes semantic relationship

**Associative Taxonomy Edge Formation:**
When an associative taxonomy is involved, edge formation follows special rules:

**Normal Mode (Visible):**
```
deploy:prod:acme:myapp:1.0.0 ↔ env:prod (via env component)
deploy:prod:acme:myapp:1.0.0 ↔ cust:acme (via customer component)
```

**Associative Mode (Invisible):**
```
env:prod ↔ cust:acme (direct edge via shared deployment)
env:prod ↔ myapp:1.0.0 (direct edge via shared deployment)
cust:acme ↔ myapp:1.0.0 (direct edge via shared deployment)
```

**Implementation:** The associative taxonomy tags are loaded into the graph to establish relationships, but can be hidden during tree projection, creating direct connections between their related taxonomies.

**Example:**
```
deploy:prod:acme:myapp:1.0.0
├── Components: { env: env:prod, customer: acme, product_version: myapp:1.0.0 }
env:prod
├── Components: { type: env, value: prod }
Result: Edge exists (shared 'env' component)
```

### 5. Tree Projection

**Definition:** A tree projection is a hierarchical view of the tag graph with all tags from a selected taxonomy serving as root nodes.

**Properties:**
- **Multiple Roots:** All tags matching the selected taxonomy pattern become root nodes
- **Graph Traversal:** Tree is built by traversing connections in the underlying tag graph
- **Cycle Prevention:** Visited node tracking prevents infinite loops in cyclic graphs
- **Depth-Based Levels:** Tree depth increases with each step from any root node
- **Associative Filtering:** Associative taxonomies can be hidden for cleaner visualization

**Process Flow:**
1. **Load Tag Graph:** Build complete graph with all tags and relationships
2. **Select Root Taxonomy:** User chooses taxonomy (e.g., Customer)
3. **Identify Roots:** All `cust:*` tags become independent root nodes
4. **Traverse Graph:** For each root, explore all connected tags
5. **Build Tree:** Create hierarchical structure with depth tracking

**Associative Taxonomy Impact:**
When associative taxonomies are set to invisible mode:
- **Direct Relationships:** Related taxonomies appear directly connected
- **Cleaner Hierarchy:** Removes intermediate nodes that don't provide categorization
- **Semantic Preservation:** Relationships maintain their meaning through the underlying graph

**Example - Customer as Root Taxonomy:**
```
cust:acme (root)
├── env:prod (via deploy:prod:acme:myapp:1.0.0)
├── env:staging (via deploy:staging:acme:myapp:1.0.1)
├── myapp:1.0.0 (via deploy:prod:acme:myapp:1.0.0)
└── myapp:1.0.1 (via deploy:staging:acme:myapp:1.0.1)

cust:foo (root)
├── env:prod (via deploy:prod:foo:myapp:1.0.0)
└── myapp:1.0.0 (via deploy:prod:foo:myapp:1.0.0)
```

**Example - Environment as Root Taxonomy (Associative Mode):**
```
env:prod (root)
├── cust:acme (direct via shared deployment)
├── cust:foo (direct via shared deployment)
├── myapp:1.0.0 (direct via shared deployment)
└── myapp:2.0.0 (direct via shared deployment)

env:staging (root)
├── cust:acme (direct via shared deployment)
├── cust:bar (direct via shared deployment)
└── myapp:1.0.1 (direct via shared deployment)
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
4. **Associative Processing:** For associative taxonomies:
   - Load all associative tags into the graph for relationship establishment
   - Optionally hide associative tags during tree projection
   - Create direct edges between related taxonomies when associative tags are invisible

**Associative Mode Implementation:**
```javascript
// When building graph with associative taxonomies hidden
if (taxonomy.isAssociative && !taxonomy.visible) {
  // Create direct edges between related taxonomies
  for (const associativeTag of associativeTags) {
    const relatedTags = getRelatedTags(associativeTag);
    for (let i = 0; i < relatedTags.length; i++) {
      for (let j = i + 1; j < relatedTags.length; j++) {
        addDirectEdge(relatedTags[i], relatedTags[j]);
      }
    }
    // Remove associative tag from visible graph
    removeNode(associativeTag);
  }
}
```

### Tree Derivation

**Algorithm:**
1. **Root Selection:** Select all nodes from the chosen taxonomy as root nodes
2. **Graph Traversal:** For each root node, perform depth-first traversal through the tag graph
3. **Cycle Prevention:** Track visited nodes to prevent cycles and infinite loops
4. **Level Assignment:** Tree depth increases with each traversal step from the root
5. **Tree Construction:** Build hierarchical structure with parent-child relationships

**Implementation Details:**
```javascript
graphToTree(rootTaxonomyId) {
  // 1. Find all root nodes (tags from selected taxonomy)
  const rootNodes = this.graph.nodes()
    .filter(node => node.data('taxonomy') === rootTaxonomyId);

  const visited = new Set();
  const treeData = [];

  // 2. Build tree from each root
  rootNodes.forEach(rootNode => {
    const treeNode = this.buildTreeNode(rootNode, visited, 0);
    if (treeNode) {
      treeData.push(treeNode);
    }
  });

  return treeData;
}

buildTreeNode(node, visited, level) {
  // 3. Prevent cycles
  if (visited.has(node.id())) return null;
  visited.add(node.id());

  // 4. Get all connected nodes (undirected graph)
  const connectedNodes = node.neighborhood().filter(n => n.isNode());

  // 5. Recursively build children (level + 1)
  const children = connectedNodes.map(childNode =>
    this.buildTreeNode(childNode, visited, level + 1)
  ).filter(Boolean);

  return {
    id: node.data('id'),
    name: node.data('name'),
    taxonomy: node.data('taxonomy'),
    level: level,  // 5. Depth from root
    children: children
  };
}
```

**Key Properties:**
- **Multiple Roots:** All tags from the selected taxonomy become independent root nodes
- **Graph-Based:** Tree is derived from the underlying tag graph structure
- **Cycle-Safe:** Visited tracking prevents infinite loops in cyclic graphs
- **Depth-Based:** Tree level represents distance from the root taxonomy

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
