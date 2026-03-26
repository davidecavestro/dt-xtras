# Taxonomy System: Core Concepts

## 🎯 Overview

The taxonomy system categorizes project tags and defines semantic relationships between them, enabling both direct categorization and inferred labeling through graph-based relationships.

## 📚 Core Concepts

### 1. Tag

**Definition:** A label applied to projects, following `type:value` format.

**Examples:**
- `env:prod` - Production environment
- `cust:acme` - ACME customer
- `myapp:1.0.0` - Product version
- `deploy:prod:acme:myapp:1.0.0` - Complete deployment specification

### 2. Taxonomy

**Definition:** Classification scheme defining:
- **Regex Pattern:** Matches tags with named capture groups
- **Relations:** Semantic relationships to other taxonomies
- **Priority:** Hierarchical ordering for conflict resolution

#### 2.1 Associative Taxonomy

**Definition:** Taxonomy where all capture groups establish relations to other taxonomies, acting as a junction entity.

**Characteristics:**
- **Invisible in Trees:** Can be hidden from visual structures
- **Direct Relationships:** Enables direct edges between related taxonomies
- **Semantic Foundation:** Provides meaning for cross-taxonomy relationships

**Example - Deployment Taxonomy:**
```yaml
pattern: ^deploy:(?<env>\w+):(?<customer>\w+):(?<product_version>[\w-]+:[\d\.]+)$
relations:
  - group: env, targets: env
  - group: customer, targets: customer
  - group: product_version, targets: product_version
```

**Behavior:**
- **Normal Mode:** `deploy:prod:acme:myapp:1.0.0` connects to `env:prod`, `cust:acme`, `myapp:1.0.0`
- **Associative Mode:** Direct edges `env:prod ↔ cust:acme`, `cust:acme ↔ myapp:1.0.0` (deployment hidden)

### 3. Project Labeling

#### 3.1 Hard Labeling (Direct)
**Definition:** Project `P` has tag `T` applied directly in Dependency Track.
**Notation:** `HardLabel(P, T)`

#### 3.2 Soft Labeling (Inferred)
**Definition:** Project `P` has tag `S` if graph contains path `S → T` where `HardLabel(P, T)` is true.
**Notation:** `SoftLabel(P, S) = ∃path(S → T) ∧ HardLabel(P, T)`

**Example:** Project with `deploy:prod:acme:myapp:1.0.0` is softly labeled by `env:prod`, `cust:acme`, `myapp:1.0.0`.

### 4. Tag Graph

**Definition:** Undirected graph `G = (V, E)` where:
- **Vertices:** All tags matching taxonomy patterns
- **Edges:** Connections between tags sharing components

**Components:** Semantic parts extracted from tags (e.g., `deploy:prod:acme:myapp:1.0.0` → `{env=prod, customer=acme, product_version=myapp:1.0.0}`)

**Edge Formation:** Tags connect when they share components through taxonomy relations.

### 5. Tree Projection

**Definition:** Hierarchical view of tag graph with selected taxonomy tags as roots.

**Properties:**
- **Multiple Roots:** All tags from selected taxonomy become independent roots
- **Graph Traversal:** Built by traversing underlying graph connections
- **Cycle Prevention:** Visited tracking prevents infinite loops
- **Associative Filtering:** Can hide associative taxonomies for cleaner views

**Example - Customer as Root:**
```
cust:acme (root)
├── deploy:prod:acme:myapp:1.0.0 (via deployment)
└── deploy:prod:foo:myapp:1.0.1 (via deployment)
```

**Example - Environment as Root (Associative Mode):**
```
env:prod (root)
├── cust:acme (direct via deployment)
│    └── myapp:1.0.0 (direct via deployment)
└── cust:foo (direct via deployment)
     └── myapp:1.0.1 (direct via deployment)
```

## 🔧 Implementation Notes

- **Associative taxonomies** provide semantic foundation while hiding intermediate nodes
- **Tree projection** maintains semantic meaning through underlying graph structure
- **Soft labeling** enables automatic project categorization based on graph relationships
