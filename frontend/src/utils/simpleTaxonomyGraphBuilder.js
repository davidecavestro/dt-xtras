// Simplified taxonomy graph builder
import XRegExp from 'xregexp';

class SimpleTaxonomyGraphBuilder {
  constructor() {
    this.nodes = new Map();
    this.edges = [];
  }

  // Build simple graph structure
  buildGraph(allTags, availableTaxonomies, associativeMode = false) {
    this.nodes.clear();
    this.edges = [];

    // Add nodes
    allTags.forEach(tag => {
      if (associativeMode && tag.name.startsWith('deploy:')) {
        return;
      }

      const taxonomy = this.findTaxonomyForTag(tag.name, availableTaxonomies);
      this.nodes.set(tag.name, {
        id: tag.name,
        name: tag.name,
        taxonomy: taxonomy.id,
        projectsCount: tag.projectsCount || 0
      });
    });

    // Build edges
    this.buildRelations(availableTaxonomies, allTags, associativeMode);

    return {
      nodes: Array.from(this.nodes.values()),
      edges: this.edges
    };
  }

  // Build relations
  buildRelations(availableTaxonomies, allTags, associativeMode = false) {
    if (associativeMode) {
      // Associative Mode: Create direct connections between components
      this.buildAssociativeRelations(availableTaxonomies, allTags);
    } else {
      // Normal Mode: Create connections via deployment tags
      this.buildNormalRelations(availableTaxonomies, allTags);
    }
  }

  // Normal mode relations (existing logic)
  buildNormalRelations(availableTaxonomies, allTags) {
    for (const taxonomy of availableTaxonomies) {
      if (!taxonomy.relations?.length) {
        continue;
      }

      for (const relation of taxonomy.relations) {
        const sourceGroup = relation.group;
        const targetTaxonomyId = relation.targets;

        if (!sourceGroup || !targetTaxonomyId) {
          continue;
        }

        const targetTaxonomy = availableTaxonomies.find(t => t.id === targetTaxonomyId);
        if (!targetTaxonomy) {
          continue;
        }

        // Find matching tags
        const sourceTags = allTags.filter(tag => {
          try {
            // Fix double backslashes in regex patterns
            const pattern = taxonomy.regex_pattern.replace(/\\\\/g, '\\');
            const regex = XRegExp(pattern);
            return regex.test(tag.name);
          } catch {
            return false;
          }
        });

        const targetTags = allTags.filter(tag => {
          try {
            // Fix double backslashes in regex patterns
            const pattern = targetTaxonomy.regex_pattern.replace(/\\\\/g, '\\');
            const regex = XRegExp(pattern);
            return regex.test(tag.name);
          } catch {
            return false;
          }
        });

        // Build connections
        for (const sourceTag of sourceTags) {
          const sourceComponents = this.parseTagComponents(sourceTag.name, taxonomy);
          if (!sourceComponents) {
            continue;
          }

          for (const targetTag of targetTags) {
            const targetComponents = this.parseTagComponents(targetTag.name, targetTaxonomy);
            if (!targetComponents) {
              continue;
            }

            const sourceValue = sourceComponents[sourceGroup];
            const targetValue = targetComponents[sourceGroup];

            if (sourceValue && targetValue && sourceValue === targetValue) {
              const edgeId = `${sourceTag.name}-${targetTag.name}`;
              if (!this.edges.find(e => e.id === edgeId || e.id === `${targetTag.name}-${sourceTag.name}`)) {
                this.edges.push({
                  id: edgeId,
                  source: sourceTag.name,
                  target: targetTag.name,
                  group: sourceGroup
                });
              }
            }
          }
        }
      }
    }
  }

  // Associative mode relations (new logic)
  buildAssociativeRelations(availableTaxonomies, allTags) {
    // Find deployment tags to process
    const deploymentTaxonomy = availableTaxonomies.find(t => t.id === 'deploy');
    if (!deploymentTaxonomy) return;

    const deploymentTags = allTags.filter(tag => tag.name.startsWith('deploy:'));

    deploymentTags.forEach(deploymentTag => {
      const components = this.parseTagComponents(deploymentTag.name, deploymentTaxonomy);
      if (!components) return;

      // Create direct connections between components in the order they appear
      const componentOrder = ['env', 'customer', 'product_version'];
      const componentValues = [];

      componentOrder.forEach(componentName => {
        const value = components[componentName];
        if (value) {
          componentValues.push({
            name: componentName,
            value: value,
            tag: this.findTagByComponent(value, allTags)
          });
        }
      });

      // Create direct edges between consecutive components
      for (let i = 0; i < componentValues.length - 1; i++) {
        const sourceComponent = componentValues[i];
        const targetComponent = componentValues[i + 1];

        if (sourceComponent.tag && targetComponent.tag) {
          const edgeId = `${sourceComponent.tag.name}-${targetComponent.tag.name}`;
          if (!this.edges.find(e => e.id === edgeId || e.id === `${targetComponent.tag.name}-${sourceComponent.tag.name}`)) {
            this.edges.push({
              id: edgeId,
              source: sourceComponent.tag.name,
              target: targetComponent.tag.name,
              group: `associative_${sourceComponent.name}_to_${targetComponent.name}`
            });
          }
        }
      }
    });
  }

  // Helper to find tag by component value
  findTagByComponent(componentValue, allTags) {
    return allTags.find(tag => {
      if (componentValue.startsWith('env:') && tag.name.startsWith('env:')) {
        return tag.name === componentValue;
      }
      if (componentValue.startsWith('cust:') && tag.name.startsWith('cust:')) {
        return tag.name === componentValue;
      }
      if (!componentValue.startsWith('env:') && !componentValue.startsWith('cust:') && !componentValue.startsWith('deploy:')) {
        return tag.name === componentValue;
      }
      return false;
    });
  }

  // Convert to tree structure
  graphToTree(rootTaxonomyId) {
    console.log('Building tree for root taxonomy:', rootTaxonomyId);
    const rootNodes = Array.from(this.nodes.values())
      .filter(node => node.taxonomy === rootTaxonomyId);

    console.log('Found root nodes:', rootNodes.map(n => n.name));

    const visited = new Set();
    const treeData = [];

    rootNodes.forEach(rootNode => {
      const treeNode = this.buildTreeNode(rootNode, visited, 0);
      console.log('Built tree node for', rootNode.name, ':', treeNode);
      if (treeNode) {
        treeData.push(treeNode);
      }
    });

    console.log('Final tree data:', treeData);
    return treeData;
  }

  buildTreeNode(node, visited, level) {
    if (visited.has(node.id)) {
      console.log('Node already visited, skipping:', node.id);
      return null;
    }
    visited.add(node.id);

    const children = [];
    const connectedEdges = this.edges.filter(edge =>
      edge.source === node.id || edge.target === node.id
    );

    console.log('Connected edges for', node.id, ':', connectedEdges);

    connectedEdges.forEach(edge => {
      const childId = edge.source === node.id ? edge.target : edge.source;
      const childNode = this.nodes.get(childId);

      if (childNode && !visited.has(childId)) {
        console.log('Adding child:', childId, 'to parent:', node.id);
        const childTreeNode = this.buildTreeNode(childNode, visited, level + 1);
        if (childTreeNode) {
          children.push(childTreeNode);
        }
      }
    });

    const result = {
      id: node.id,
      name: node.name,
      taxonomy: node.taxonomy,
      projectsCount: node.projectsCount,
      level,
      children: children.sort((a, b) => a.name.localeCompare(b.name))
    };

    console.log('Final tree node for', node.id, ':', result);
    return result;
  }

  // Helper methods
  findTaxonomyForTag(tagName, taxonomies) {
    return taxonomies.find(t => {
      try {
        const regex = XRegExp(t.regex_pattern);
        return regex.test(tagName);
      } catch {
        return false;
      }
    }) || { id: 'unknown' };
  }

  parseTagComponents(tagName, taxonomy) {
    if (!taxonomy?.regex_pattern) {
      return null;
    }

    try {
      // Special handling for deployment tags
      if (taxonomy.id === 'deploy' && tagName.startsWith('deploy:')) {
        const parts = tagName.split(':');
        if (parts.length >= 5) {
          const components = {
            env: `env:${parts[1]}`,
            customer: `cust:${parts[2]}`,
            product_version: `${parts[3]}:${parts[4]}`,
            full_tag: tagName
          };
          return components;
        }
      }

      // Special handling for customer tags
      if (taxonomy.id === 'customer' && tagName.startsWith('cust:')) {
        const parts = tagName.split(':');
        if (parts.length === 2) {
          const components = {
            id: parts[1],  // This matches the relation group name
            customer: `cust:${parts[1]}`,  // This matches deployment component
            full_tag: tagName
          };
          return components;
        }
      }

      // Special handling for environment tags
      if (taxonomy.id === 'env' && tagName.startsWith('env:')) {
        const parts = tagName.split(':');
        if (parts.length === 2) {
          const components = {
            env_type: parts[1],  // This matches the relation group name
            env: `env:${parts[1]}`,  // This matches deployment component
            full_tag: tagName
          };
          return components;
        }
      }

      // Special handling for product version tags
      if (taxonomy.id === 'product_version' && !tagName.startsWith('env:') && !tagName.startsWith('cust:') && !tagName.startsWith('deploy:')) {
        const parts = tagName.split(':');
        if (parts.length === 2) {
          const components = {
            product_name: parts[0],
            version: parts[1],
            product_version: tagName,  // This matches deployment component
            full_tag: tagName
          };
          return components;
        }
      }

      return null;
    } catch (error) {
      return null;
    }
  }

  // Generate SVG graph
  generateSVG(layout = 'circle') {
    const width = 800;
    const height = 600;
    const nodeRadius = 20;

    // Layout based on parameter
    const positions = this.calculateLayout(width, height, layout);

    let svg = `<svg width="${width}" height="${height}" xmlns="http://www.w3.org/2000/svg">`;

    // Draw edges
    this.edges.forEach(edge => {
      const source = positions[edge.source];
      const target = positions[edge.target];
      svg += `<line x1="${source.x}" y1="${source.y}" x2="${target.x}" y2="${target.y}" stroke="#ccc" stroke-width="2"/>`;
    });

    // Draw nodes
    Array.from(this.nodes.values()).forEach(node => {
      const pos = positions[node.id];
      const color = this.getNodeColor(node.taxonomy);
      svg += `<circle cx="${pos.x}" cy="${pos.y}" r="${nodeRadius}" fill="${color}" stroke="#333" stroke-width="2"/>`;
      svg += `<text x="${pos.x}" y="${pos.y + 5}" text-anchor="middle" font-size="10" fill="white">${node.name}</text>`;
    });

    svg += '</svg>';
    return svg;
  }

  calculateLayout(width, height, layout = 'circle') {
    const positions = {};
    const nodes = Array.from(this.nodes.values());

    switch (layout) {
      case 'grid':
        return this.calculateGridLayout(width, height, nodes);
      case 'breadthfirst':
        return this.calculateBreadthFirstLayout(width, height, nodes);
      case 'concentric':
        return this.calculateConcentricLayout(width, height, nodes);
      case 'cose':
        return this.calculateCoSELayout(width, height, nodes);
      case 'random':
        return this.calculateRandomLayout(width, height, nodes);
      case 'circle':
      default:
        return this.calculateCircularLayout(width, height, nodes);
    }
  }

  calculateCircularLayout(width, height, nodes) {
    const positions = {};
    const centerX = width / 2;
    const centerY = height / 2;
    const radius = Math.min(width, height) / 3;

    nodes.forEach((node, index) => {
      const angle = (2 * Math.PI * index) / nodes.length;
      positions[node.id] = {
        x: centerX + radius * Math.cos(angle),
        y: centerY + radius * Math.sin(angle)
      };
    });

    return positions;
  }

  calculateGridLayout(width, height, nodes) {
    const positions = {};
    const cols = Math.ceil(Math.sqrt(nodes.length));
    const rows = Math.ceil(nodes.length / cols);
    const cellWidth = width / (cols + 1);
    const cellHeight = height / (rows + 1);

    nodes.forEach((node, index) => {
      const col = index % cols;
      const row = Math.floor(index / cols);
      positions[node.id] = {
        x: cellWidth * (col + 1),
        y: cellHeight * (row + 1)
      };
    });

    return positions;
  }

  calculateBreadthFirstLayout(width, height, nodes) {
    const positions = {};
    const levels = this.groupNodesByLevel(nodes);
    const levelHeight = height / (levels.length + 1);

    levels.forEach((levelNodes, levelIndex) => {
      const levelWidth = width / (levelNodes.length + 1);
      levelNodes.forEach((node, nodeIndex) => {
        positions[node.id] = {
          x: levelWidth * (nodeIndex + 1),
          y: levelHeight * (levelIndex + 1)
        };
      });
    });

    return positions;
  }

  calculateConcentricLayout(width, height, nodes) {
    const positions = {};
    const levels = this.groupNodesByLevel(nodes);
    const centerX = width / 2;
    const centerY = height / 2;
    const maxRadius = Math.min(width, height) / 2 - 50;

    levels.forEach((levelNodes, levelIndex) => {
      const radius = (maxRadius / levels.length) * (levelIndex + 1);
      const angleStep = (2 * Math.PI) / levelNodes.length;

      levelNodes.forEach((node, nodeIndex) => {
        const angle = angleStep * nodeIndex;
        positions[node.id] = {
          x: centerX + radius * Math.cos(angle),
          y: centerY + radius * Math.sin(angle)
        };
      });
    });

    return positions;
  }

  calculateCoSELayout(width, height, nodes) {
    // Simplified CoSE (Compound Spring Embedder) layout
    const positions = {};
    const centerX = width / 2;
    const centerY = height / 2;

    // Initialize with random positions
    nodes.forEach(node => {
      positions[node.id] = {
        x: Math.random() * (width - 100) + 50,
        y: Math.random() * (height - 100) + 50
      };
    });

    // Simple force-directed simulation
    for (let iter = 0; iter < 50; iter++) {
      // Apply repulsive forces between all nodes
      nodes.forEach((node1, i) => {
        nodes.forEach((node2, j) => {
          if (i !== j) {
            const dx = positions[node2.id].x - positions[node1.id].x;
            const dy = positions[node2.id].y - positions[node1.id].y;
            const distance = Math.sqrt(dx * dx + dy * dy) || 1;
            const force = 1000 / (distance * distance);

            positions[node1.id].x -= (dx / distance) * force;
            positions[node1.id].y -= (dy / distance) * force;
          }
        });
      });

      // Apply attractive forces for connected nodes
      this.edges.forEach(edge => {
        const source = positions[edge.source];
        const target = positions[edge.target];
        const dx = target.x - source.x;
        const dy = target.y - source.y;
        const distance = Math.sqrt(dx * dx + dy * dy) || 1;
        const force = distance / 100;

        const fx = (dx / distance) * force;
        const fy = (dy / distance) * force;

        source.x += fx;
        source.y += fy;
        target.x -= fx;
        target.y -= fy;
      });

      // Keep nodes within bounds
      nodes.forEach(node => {
        positions[node.id].x = Math.max(50, Math.min(width - 50, positions[node.id].x));
        positions[node.id].y = Math.max(50, Math.min(height - 50, positions[node.id].y));
      });
    }

    return positions;
  }

  calculateRandomLayout(width, height, nodes) {
    const positions = {};

    nodes.forEach(node => {
      positions[node.id] = {
        x: Math.random() * (width - 100) + 50,
        y: Math.random() * (height - 100) + 50
      };
    });

    return positions;
  }

  groupNodesByLevel(nodes) {
    // Simple level grouping based on connections
    const levels = [];
    const visited = new Set();
    const nodeMap = new Map(nodes.map(n => [n.id, n]));

    // Find root nodes (nodes with no incoming edges)
    const roots = nodes.filter(node =>
      !this.edges.some(edge => edge.target === node.id)
    );

    if (roots.length === 0 && nodes.length > 0) {
      // If no clear roots, use first node as root
      roots.push(nodes[0]);
    }

    // BFS to group by levels
    const queue = roots.map(node => ({ node, level: 0 }));

    while (queue.length > 0) {
      const { node, level } = queue.shift();

      if (visited.has(node.id)) continue;
      visited.add(node.id);

      if (!levels[level]) levels[level] = [];
      levels[level].push(node);

      // Find connected nodes
      this.edges
        .filter(edge => edge.source === node.id)
        .forEach(edge => {
          const targetNode = nodeMap.get(edge.target);
          if (targetNode && !visited.has(targetNode.id)) {
            queue.push({ node: targetNode, level: level + 1 });
          }
        });
    }

    // Add any unvisited nodes
    nodes.forEach(node => {
      if (!visited.has(node.id)) {
        if (!levels[0]) levels[0] = [];
        levels[0].push(node);
      }
    });

    return levels.filter(level => level.length > 0);
  }

  getNodeColor(taxonomy) {
    const colors = {
      customer: '#FF6B6B',
      env: '#4ECDC4',
      deploy: '#45B7D1',
      product_version: '#96CEB4'
    };
    return colors[taxonomy] || '#999';
  }
}

export default SimpleTaxonomyGraphBuilder;
