import XRegExp from 'xregexp';

export default class SimpleTaxonomyGraphBuilder {
  constructor() {
    this.nodes = new Map();
    this.edges = [];
  }

  buildGraph(tags, taxonomies, associativeMode = false) {
    console.log('Building graph with', tags.length, 'tags and', taxonomies.length, 'taxonomies');
    console.log('Associative mode:', associativeMode);

    // Clear previous data
    this.nodes.clear();
    this.edges = [];

    // Create nodes for all tags
    tags.forEach(tag => {
      const taxonomy = this.findTaxonomyForTag(tag, taxonomies);
      if (taxonomy) {
        this.nodes.set(tag.name, {
          id: tag.name,
          name: tag.name,
          taxonomy: taxonomy.id,
          projectsCount: tag.projectsCount || 0
        });
      }
    });

    console.log('Created', this.nodes.size, 'nodes');

    // Build edges based on mode
    if (associativeMode) {
      this.buildAssociativeRelations(taxonomies, tags);
    } else {
      this.buildNormalRelations(taxonomies, tags);
    }

    console.log('Created', this.edges.length, 'edges');

    return {
      nodes: this.nodes,
      edges: this.edges
    };
  }

  findTaxonomyForTag(tag, taxonomies) {
    return taxonomies.find(taxonomy => {
      try {
        const pattern = taxonomy.regex_pattern.replace(/\\\\/g, '\\');
        const regex = XRegExp(pattern);
        return regex.test(tag.name);
      } catch {
        return false;
      }
    });
  }

  parseTagComponents(tagName, taxonomy) {
    if (!taxonomy?.regex_pattern) {
      return null;
    }

    try {
      const regex = new XRegExp(taxonomy.regex_pattern);
      const match = regex.exec(tagName);

      if (match) {
        const components = {};

        if (match.groups) {
          Object.keys(match.groups).forEach(groupName => {
            if (groupName) {
              components[groupName] = match[groupName];
            }
          });
        } else {
          // Fallback: manual extraction of capture groups
          const groupMatches = taxonomy.regex_pattern.match(/\(\?P<([^>]+)>/g);
          if (groupMatches) {
            groupMatches.forEach((groupMatch, index) => {
              const groupName = groupMatch.match(/\(\?P<([^>]+)>/)[1];
              if (groupName && match[index + 1]) {
                components[groupName] = match[index + 1];
              }
            });
          }
        }

        components.full_tag = tagName;
        return components;
      }

      return null;
    } catch (error) {
      console.warn('Error parsing tag', tagName, 'with pattern', taxonomy.regex_pattern, ':', error.message);
      return null;
    }
  }

  buildNormalRelations(taxonomies, tags) {
    console.log('Building normal relations...');

    for (const taxonomy of taxonomies) {
      if (!taxonomy.relations?.length) {
        console.log(`⚠️ Taxonomy ${taxonomy.id} has no relations, skipping`);
        continue;
      }

      for (const relation of taxonomy.relations) {
        const sourceGroup = relation.group;
        const targetTaxonomyId = relation.targets;

        if (!sourceGroup || !targetTaxonomyId) {
          console.log(`⚠️ Invalid relation:`, relation);
          continue;
        }

        const targetTaxonomy = taxonomies.find(t => t.id === targetTaxonomyId);
        if (!targetTaxonomy) {
          console.log(`⚠️ Target taxonomy ${targetTaxonomyId} not found`);
          continue;
        }

        // Skip self-referential connections
        if (taxonomy.id === targetTaxonomyId) {
          console.log(`⚠️ Skipping self-referential connection: ${taxonomy.id} -> ${targetTaxonomyId}`);
          continue;
        }

        console.log(`🔗 Building connection: ${taxonomy.id} -> ${targetTaxonomyId} via group ${sourceGroup}`);

        const sourceTags = tags.filter(tag => {
          try {
            const pattern = taxonomy.regex_pattern.replace(/\\\\/g, '\\');
            const regex = XRegExp(pattern);
            return regex.test(tag.name);
          } catch {
            return false;
          }
        });

        const targetTags = tags.filter(tag => {
          try {
            const pattern = targetTaxonomy.regex_pattern.replace(/\\\\/g, '\\');
            const regex = XRegExp(pattern);
            return regex.test(tag.name);
          } catch {
            return false;
          }
        });

        console.log(`📊 Found ${sourceTags.length} source tags and ${targetTags.length} target tags`);

        this.createNormalModeConnections(sourceTags, targetTags, sourceGroup, taxonomy, targetTaxonomy, taxonomies, tags);
      }
    }

    console.log(`🎯 Total edges created: ${this.edges.length}`);
  }

  createNormalModeConnections(sourceTags, targetTags, sourceGroup, sourceTaxonomy, targetTaxonomy, availableTaxonomies, allTags) {
    // Helper to get the actual component name from a taxonomy for a given group
    const getComponentNameForGroup = (taxonomy, group) => {
      try {
        const pattern = taxonomy.regex_pattern;
        const matches = pattern.match(/\(\?P<([^>]+)>/g);

        if (matches) {
          for (const match of matches) {
            const componentName = match.match(/\(\?P<([^>]+)>/)[1];
            if (componentName.toLowerCase() === group.toLowerCase() ||
                taxonomy.id.toLowerCase() === group.toLowerCase()) {
              return componentName;
            }
          }
        }
      } catch {
        // Fallback to group name
      }
      return group;
    };

    const sourceComponentName = getComponentNameForGroup(sourceTaxonomy, sourceGroup);
    const targetComponentName = getComponentNameForGroup(targetTaxonomy, sourceGroup);

    console.log(`🔧 Component mapping: group "${sourceGroup}" -> source: "${sourceComponentName}", target: "${targetComponentName}"`);

    // Create direct connections between source and target tags when component values match
    sourceTags.forEach(sourceTag => {
      const sourceComponents = this.parseTagComponents(sourceTag.name, sourceTaxonomy);
      if (!sourceComponents) {
        console.log(`⚠️ Failed to parse source tag: ${sourceTag.name}`);
        return;
      }

      const sourceValue = sourceComponents[sourceComponentName];
      if (!sourceValue) {
        console.log(`⚠️ Source tag ${sourceTag.name} has no component ${sourceComponentName}`);
        return;
      }

      console.log(`🔗 Looking for matches for source ${sourceTag.name} with ${sourceComponentName}="${sourceValue}"`);

      targetTags.forEach(targetTag => {
        const targetComponents = this.parseTagComponents(targetTag.name, targetTaxonomy);
        if (!targetComponents) {
          console.log(`⚠️ Failed to parse target tag: ${targetTag.name}`);
          return;
        }

        const targetValue = targetComponents[targetComponentName];
        if (!targetValue) {
          console.log(`⚠️ Target tag ${targetTag.name} has no component ${targetComponentName}`);
          return;
        }

        console.log(`🔗 Checking connection: ${sourceTag.name} (${sourceValue}) -> ${targetTag.name} (${targetValue})`);

        if (sourceValue === targetValue) {
          const edgeId = `${sourceTag.name}-${targetTag.name}`;

          if (!this.nodes.has(sourceTag.name) || !this.nodes.has(targetTag.name)) {
            console.warn(`Skipping edge - missing nodes: ${sourceTag.name} -> ${targetTag.name}`);
            return;
          }

          if (!this.edges.find(e => e.id === edgeId || e.id === `${targetTag.name}-${sourceTag.name}`)) {
            this.edges.push({
              id: edgeId,
              source: sourceTag.name,
              target: targetTag.name,
              group: sourceGroup
            });
            console.log(`✅ Created edge: ${sourceTag.name} -> ${targetTag.name} (group: ${sourceGroup})`);
          } else {
            console.log(`⚠️ Edge already exists: ${sourceTag.name} -> ${targetTag.name}`);
          }
        }
      });
    });

    console.log(`🎯 Final edges after processing: ${this.edges.length}`);
  }

  buildAssociativeRelations(taxonomies, tags) {
    console.log('Building associative relations...');

    // Find connector taxonomies (those with multiple capture groups)
    const connectorTaxonomies = taxonomies.filter(t => {
      try {
        const match = t.regex_pattern.match(/\(\?P<[^>]+>/g);
        return match && match.length > 1;
      } catch {
        return false;
      }
    });

    if (connectorTaxonomies.length === 0) {
      console.warn('No connector taxonomy found - cannot build associative structure');
      return;
    }

    const connectorTaxonomy = connectorTaxonomies[0];
    console.log('Using connector taxonomy:', connectorTaxonomy.id);

    // Find connector tags
    const connectorTags = tags.filter(tag => {
      try {
        const regex = XRegExp(connectorTaxonomy.regex_pattern);
        return regex.test(tag.name);
      } catch {
        return false;
      }
    });

    console.log(`Found ${connectorTags.length} connector tags`);

    // Helper to get component name for group
    const getComponentNameForGroup = (taxonomy, group) => {
      try {
        const pattern = taxonomy.regex_pattern;
        const matches = pattern.match(/\(\?P<([^>]+)>/g);

        if (matches) {
          for (const match of matches) {
            const componentName = match.match(/\(\?P<([^>]+)>/)[1];
            if (componentName.toLowerCase() === group.toLowerCase() ||
                taxonomy.id.toLowerCase() === group.toLowerCase()) {
              return componentName;
            }
          }
        }
      } catch {
        // Fallback to group name
      }
      return group;
    };

    // Create associative connections following capture group order
    connectorTags.forEach(connectorTag => {
      const components = this.parseTagComponents(connectorTag.name, connectorTaxonomy);
      if (!components) return;

      // Get the ordered list of capture groups from the taxonomy pattern
      const captureGroups = [];
      const matches = connectorTaxonomy.regex_pattern.match(/\(\?P<([^>]+)>/g);
      if (matches) {
        matches.forEach(match => {
          const groupName = match.match(/\(\?P<([^>]+)>/)[1];
          captureGroups.push(groupName);
        });
      }

      console.log(`Capture groups order for ${connectorTag.name}:`, captureGroups);

      // Find the corresponding taxonomy nodes for each capture group
      const taxonomyNodes = [];
      captureGroups.forEach(groupName => {
        const componentName = getComponentNameForGroup(connectorTaxonomy, groupName);
        const componentValue = components[componentName];

        if (componentValue) {
          // Find the corresponding node to get taxonomy info
          const node = this.findNodeByComponent(componentValue);
          if (node) {
            taxonomyNodes.push({
              groupName: groupName,
              node: node,
              value: componentValue
            });
          }
        }
      });

      console.log(`Taxonomy nodes for ${connectorTag.name}:`, taxonomyNodes.map(n => `${n.groupName}:${n.node.name}`));

      // Create hierarchical edges following capture group order
      // This creates a chain: first -> second -> third -> ...
      for (let i = 0; i < taxonomyNodes.length - 1; i++) {
        const sourceNode = taxonomyNodes[i];
        const targetNode = taxonomyNodes[i + 1];

        const edgeId = `${sourceNode.node.name}-${targetNode.node.name}`;

        if (!this.edges.find(e => e.id === edgeId || e.id === `${targetNode.node.name}-${sourceNode.node.name}`)) {
          this.edges.push({
            id: edgeId,
            source: sourceNode.node.name,
            target: targetNode.node.name,
            group: `associative_${sourceNode.groupName}_to_${targetNode.groupName}`
          });
          console.log(`✅ Created associative edge: ${sourceNode.node.name} -> ${targetNode.node.name} (group: associative_${sourceNode.groupName}_to_${targetNode.groupName})`);
        }
      }
    });

    console.log(`🎯 Total associative edges created: ${this.edges.length}`);
  }

  findNodeByComponent(componentValue) {
    return Array.from(this.nodes.values()).find(node => {
      if (node.name === componentValue) {
        return true;
      }
      if (node.name.includes(componentValue)) {
        return true;
      }
      if (componentValue.includes(node.name)) {
        return true;
      }
      return false;
    });
  }

  findTagByComponent(componentValue, allTags) {
    return allTags.find(tag => {
      if (tag.name === componentValue) {
        return true;
      }
      if (tag.name.includes(componentValue)) {
        return true;
      }
      if (componentValue.includes(tag.name)) {
        return true;
      }
      return false;
    });
  }

  // UNDIRECTED GRAPH: Tree building treats edges as undirected
  buildTree(rootTaxonomyId) {
    const rootNodes = Array.from(this.nodes.values())
      .filter(node => node.taxonomy === rootTaxonomyId);

    const visited = new Set();
    const treeData = [];

    rootNodes.forEach(rootNode => {
      const treeNode = this.buildTreeNode(rootNode, visited, 0);
      if (treeNode) {
        treeData.push(treeNode);
      }
    });

    return treeData;
  }

  buildTreeNode(node, visited, level) {
    if (visited.has(node.id)) {
      return null;
    }
    visited.add(node.id);

    const children = [];

    // Since the graph is undirected, we consider all connected nodes
    // regardless of edge direction
    const connectedEdges = this.edges.filter(edge =>
      edge.source === node.id || edge.target === node.id
    );

    connectedEdges.forEach(edge => {
      // Find the connected node (the other end of the edge)
      const connectedNodeId = edge.source === node.id ? edge.target : edge.source;
      const connectedNode = this.nodes.get(connectedNodeId);

      if (connectedNode && !visited.has(connectedNode.id)) {
        const childTreeNode = this.buildTreeNode(connectedNode, visited, level + 1);
        if (childTreeNode) {
          children.push(childTreeNode);
        }
      }
    });

    return {
      id: node.id,
      name: node.name,
      taxonomy: node.taxonomy,
      projectsCount: node.projectsCount,
      level,
      children: children.sort((a, b) => a.name.localeCompare(b.name))
    };
  }

  // Legacy methods for compatibility
  buildNormalTree(rootTaxonomyId) {
    return this.buildTree(rootTaxonomyId);
  }

  buildAssociativeTree(rootTaxonomyId) {
    return this.buildTree(rootTaxonomyId);
  }

  graphToTree(rootTaxonomyId) {
    return this.buildTree(rootTaxonomyId);
  }

  // Generate SVG representation for graph visualization
  generateSVG(layout = 'breadthfirst') {
    if (!this.nodes || this.nodes.size === 0) {
      return '';
    }

    // Convert nodes to graph format
    const graphNodes = Array.from(this.nodes.values()).map(node => ({
      id: node.id,
      name: node.name,
      taxonomy: node.taxonomy,
      projectsCount: node.projectsCount
    }));

    // Convert edges to graph format
    const graphEdges = this.edges.map(edge => ({
      source: edge.source,
      target: edge.target,
      group: edge.group
    }));

    // Generate basic SVG layout
    const width = 800;
    const height = 600;
    const nodeRadius = 30;

    // Simple layout positioning
    const positions = this.calculateLayout(graphNodes, layout, width, height);

    // Generate SVG
    let svg = `<svg width="${width}" height="${height}" xmlns="http://www.w3.org/2000/svg">`;

    // Add edges
    graphEdges.forEach(edge => {
      const sourcePos = positions[edge.source];
      const targetPos = positions[edge.target];
      if (sourcePos && targetPos) {
        svg += `<line x1="${sourcePos.x}" y1="${sourcePos.y}" x2="${targetPos.x}" y2="${targetPos.y}" stroke="#94a3b8" stroke-width="2"/>`;
      }
    });

    // Add nodes
    graphNodes.forEach(node => {
      const pos = positions[node.id];
      if (pos) {
        const color = this.getNodeColor(node.taxonomy);
        svg += `<circle cx="${pos.x}" cy="${pos.y}" r="${nodeRadius}" fill="${color}" stroke="#1e293b" stroke-width="2"/>`;
        svg += `<text x="${pos.x}" y="${pos.y + 5}" text-anchor="middle" fill="white" font-size="12" font-weight="bold">${node.name}</text>`;
      }
    });

    svg += '</svg>';

    return svg;
  }

  calculateLayout(nodes, layout, width, height) {
    const positions = {};
    const centerX = width / 2;
    const centerY = height / 2;
    const margin = 50;

    switch (layout) {
      case 'circle':
        return this.circleLayout(nodes, centerX, centerY, Math.min(width, height) / 2 - margin);

      case 'grid':
        return this.gridLayout(nodes, width, height, margin);

      case 'breadthfirst':
        return this.breadthFirstLayout(nodes, centerX, centerY, width, height, margin);

      case 'concentric':
        return this.concentricLayout(nodes, centerX, centerY, width, height, margin);

      case 'cose':
        return this.forceDirectedLayout(nodes, width, height, margin);

      case 'random':
        return this.randomLayout(nodes, width, height, margin);

      default:
        return this.breadthFirstLayout(nodes, centerX, centerY, width, height, margin);
    }
  }

  circleLayout(nodes, centerX, centerY, radius) {
    const positions = {};
    const angleStep = (2 * Math.PI) / nodes.length;

    nodes.forEach((node, index) => {
      const angle = index * angleStep;
      positions[node.id] = {
        x: centerX + radius * Math.cos(angle),
        y: centerY + radius * Math.sin(angle)
      };
    });

    return positions;
  }

  gridLayout(nodes, width, height, margin) {
    const positions = {};
    const cols = Math.ceil(Math.sqrt(nodes.length));
    const cellWidth = (width - 2 * margin) / cols;
    const cellHeight = (height - 2 * margin) / Math.ceil(nodes.length / cols);

    nodes.forEach((node, index) => {
      const row = Math.floor(index / cols);
      const col = index % cols;
      positions[node.id] = {
        x: margin + col * cellWidth + cellWidth / 2,
        y: margin + row * cellHeight + cellHeight / 2
      };
    });

    return positions;
  }

  breadthFirstLayout(nodes, centerX, centerY, width, height, margin) {
    const positions = {};
    const levels = this.calculateLevels(nodes);
    const maxLevel = Math.max(...Object.values(levels));

    // Group nodes by level
    const nodesByLevel = {};
    nodes.forEach(node => {
      const level = levels[node.id] || 0;
      if (!nodesByLevel[level]) {
        nodesByLevel[level] = [];
      }
      nodesByLevel[level].push(node);
    });

    // Position nodes by level
    Object.keys(nodesByLevel).forEach(level => {
      const levelNodes = nodesByLevel[level];
      const levelY = margin + (height - 2 * margin) * (parseInt(level) / maxLevel);
      const levelWidth = width - 2 * margin;
      const nodeSpacing = levelWidth / (levelNodes.length + 1);

      levelNodes.forEach((node, index) => {
        positions[node.id] = {
          x: margin + nodeSpacing * (index + 1),
          y: levelY
        };
      });
    });

    return positions;
  }

  concentricLayout(nodes, centerX, centerY, width, height, margin) {
    const positions = {};
    const levels = this.calculateLevels(nodes);
    const maxLevel = Math.max(...Object.values(levels));
    const maxRadius = Math.min(width, height) / 2 - margin;

    // Group nodes by level
    const nodesByLevel = {};
    nodes.forEach(node => {
      const level = levels[node.id] || 0;
      if (!nodesByLevel[level]) {
        nodesByLevel[level] = [];
      }
      nodesByLevel[level].push(node);
    });

    // Position nodes in concentric circles
    Object.keys(nodesByLevel).forEach(level => {
      const levelNodes = nodesByLevel[level];
      const radius = maxRadius * (parseInt(level) / maxLevel);
      const angleStep = (2 * Math.PI) / levelNodes.length;

      levelNodes.forEach((node, index) => {
        const angle = index * angleStep;
        positions[node.id] = {
          x: centerX + radius * Math.cos(angle),
          y: centerY + radius * Math.sin(angle)
        };
      });
    });

    return positions;
  }

  forceDirectedLayout(nodes, width, height, margin, iterations = 100) {
    const positions = this.randomLayout(nodes, width, height, margin);

    // Simple force-directed simulation
    for (let iter = 0; iter < iterations; iter++) {
      const forces = {};

      // Initialize forces
      nodes.forEach(node => {
        forces[node.id] = { x: 0, y: 0 };
      });

      // Repulsion between all nodes
      nodes.forEach((node1, i) => {
        nodes.forEach((node2, j) => {
          if (i !== j) {
            const dx = positions[node2.id].x - positions[node1.id].x;
            const dy = positions[node2.id].y - positions[node1.id].y;
            const distance = Math.sqrt(dx * dx + dy * dy);
            if (distance > 0) {
              const force = 1000 / (distance * distance);
              forces[node1.id].x -= force * dx / distance;
              forces[node1.id].y -= force * dy / distance;
            }
          }
        });
      });

      // Attraction along edges
      this.edges.forEach(edge => {
        const sourcePos = positions[edge.source];
        const targetPos = positions[edge.target];
        if (sourcePos && targetPos) {
          const dx = targetPos.x - sourcePos.x;
          const dy = targetPos.y - sourcePos.y;
          const distance = Math.sqrt(dx * dx + dy * dy);
          const force = distance * 0.01;

          forces[edge.source].x += force * dx / distance;
          forces[edge.source].y += force * dy / distance;
          forces[edge.target].x -= force * dx / distance;
          forces[edge.target].y -= force * dy / distance;
        }
      });

      // Apply forces
      nodes.forEach(node => {
        positions[node.id].x += forces[node.id].x * 0.1;
        positions[node.id].y += forces[node.id].y * 0.1;

        // Keep within bounds
        positions[node.id].x = Math.max(margin, Math.min(width - margin, positions[node.id].x));
        positions[node.id].y = Math.max(margin, Math.min(height - margin, positions[node.id].y));
      });
    }

    return positions;
  }

  randomLayout(nodes, width, height, margin) {
    const positions = {};

    nodes.forEach(node => {
      positions[node.id] = {
        x: margin + Math.random() * (width - 2 * margin),
        y: margin + Math.random() * (height - 2 * margin)
      };
    });

    return positions;
  }

  calculateLevels(nodes) {
    const levels = {};
    const visited = new Set();

    // Find root nodes (nodes with no incoming edges)
    const rootNodes = nodes.filter(node =>
      !this.edges.some(edge => edge.target === node.id)
    );

    // BFS to calculate levels
    const queue = rootNodes.map(node => ({ node, level: 0 }));

    while (queue.length > 0) {
      const { node, level } = queue.shift();

      if (visited.has(node.id)) {
        continue;
      }

      visited.add(node.id);
      levels[node.id] = level;

      // Add connected nodes to queue
      const connectedEdges = this.edges.filter(edge =>
        edge.source === node.id || edge.target === node.id
      );

      connectedEdges.forEach(edge => {
        const connectedNodeId = edge.source === node.id ? edge.target : edge.source;
        const connectedNode = nodes.find(n => n.id === connectedNodeId);

        if (connectedNode && !visited.has(connectedNode.id)) {
          queue.push({ node: connectedNode, level: level + 1 });
        }
      });
    }

    return levels;
  }

  getNodeColor(taxonomy) {
    const colors = {
      'customer': '#3b82f6',      // blue
      'env': '#10b981',           // green
      'deploy': '#f59e0b',        // yellow
      'product_version': '#ef4444', // red
      'default': '#6b7280'        // gray
    };

    return colors[taxonomy] || colors.default;
  }
}
