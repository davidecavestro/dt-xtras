// Simplified taxonomy graph builder - completely dynamic
import XRegExp from 'xregexp';

class SimpleTaxonomyGraphBuilder {
  constructor() {
    this.nodes = new Map();
    this.edges = [];
  }

  buildGraph(allTags, availableTaxonomies, associativeMode = false) {
    this.nodes.clear();
    this.edges = [];

    allTags.forEach(tag => {
      const taxonomy = this.findTaxonomyForTag(tag.name, availableTaxonomies);
      this.nodes.set(tag.name, {
        id: tag.name,
        name: tag.name,
        taxonomy: taxonomy.id,
        projectsCount: tag.projectsCount || 0
      });
    });

    if (associativeMode) {
      this.buildAssociativeRelations(availableTaxonomies, allTags);
    } else {
      this.buildNormalRelations(availableTaxonomies, allTags);
    }

    return {
      nodes: Array.from(this.nodes.values()),
      edges: this.edges
    };
  }

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
      console.log(`🔍 Parsing tag "${tagName}" with pattern "${taxonomy.regex_pattern}"`);
      const regex = new XRegExp(taxonomy.regex_pattern);
      const match = regex.exec(tagName);

      console.log(`📋 Match result:`, match);
      console.log(`📋 Match groups:`, match?.groups);

      if (match) {
        const components = {};

        // XRegExp should provide groups, but if it's undefined, extract manually
        if (match.groups) {
          Object.keys(match.groups).forEach(groupName => {
            if (groupName) {
              components[groupName] = match[groupName];
            }
          });
        } else {
          // Fallback: manually extract from capture groups using regex analysis
          console.log(`⚠️ XRegExp groups undefined, extracting manually`);

          // Get group names from the regex pattern
          const groupMatches = taxonomy.regex_pattern.match(/\(\?P<([^>]+)>/g);
          if (groupMatches) {
            groupMatches.forEach((groupMatch, index) => {
              const groupName = groupMatch.match(/\(\?P<([^>]+)>/)[1];
              if (groupName && match[index + 1]) {
                components[groupName] = match[index + 1];
                console.log(`✅ Extracted ${groupName}: ${match[index + 1]}`);
              }
            });
          }
        }

        components.full_tag = tagName;
        console.log(`✅ Final extracted components:`, components);
        return components;
      }

      return null;
    } catch (error) {
      console.warn(`Error parsing tag ${tagName} with pattern ${taxonomy.regex_pattern}:`, error.message);
      return null;
    }
  }

  buildNormalRelations(availableTaxonomies, allTags) {
    console.log('🔍 Building normal relations...');
    console.log('Available taxonomies:', availableTaxonomies.map(t => ({ id: t.id, hasRelations: !!t.relations?.length })));
    console.log('All tags count:', allTags.length);

    for (const taxonomy of availableTaxonomies) {
      if (!taxonomy.relations?.length) {
        console.log(`⚠️ Taxonomy ${taxonomy.id} has no relations, skipping`);
        continue;
      }

      console.log(`📋 Processing taxonomy ${taxonomy.id} with relations:`, taxonomy.relations);

      for (const relation of taxonomy.relations) {
        const sourceGroup = relation.group;
        const targetTaxonomyId = relation.targets;

        if (!sourceGroup || !targetTaxonomyId) {
          console.log(`⚠️ Invalid relation:`, relation);
          continue;
        }

        const targetTaxonomy = availableTaxonomies.find(t => t.id === targetTaxonomyId);
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

        const sourceTags = allTags.filter(tag => {
          try {
            const pattern = taxonomy.regex_pattern.replace(/\\\\/g, '\\');
            const regex = XRegExp(pattern);
            return regex.test(tag.name);
          } catch {
            return false;
          }
        });

        const targetTags = allTags.filter(tag => {
          try {
            const pattern = targetTaxonomy.regex_pattern.replace(/\\\\/g, '\\');
            const regex = XRegExp(pattern);
            return regex.test(tag.name);
          } catch {
            return false;
          }
        });

        console.log(`📊 Found ${sourceTags.length} source tags and ${targetTags.length} target tags`);

        this.createNormalModeConnections(sourceTags, targetTags, sourceGroup, taxonomy, targetTaxonomy, availableTaxonomies, allTags);
      }
    }

    console.log(`🎯 Total edges created: ${this.edges.length}`);
    console.log('📋 All edges:', this.edges);
  }

  createNormalModeConnections(sourceTags, targetTags, sourceGroup, sourceTaxonomy, targetTaxonomy, availableTaxonomies, allTags) {
    // Helper to get the actual component name from a taxonomy for a given group
    const getComponentNameForGroup = (taxonomy, group) => {
      try {
        // Simple string matching to find component names
        const pattern = taxonomy.regex_pattern;
        const matches = pattern.match(/\(\?P<([^>]+)>/g);

        if (matches) {
          for (const match of matches) {
            const componentName = match.match(/\(\?P<([^>]+)>/)[1];
            // Check if this component name matches the group name (case insensitive)
            if (componentName.toLowerCase() === group.toLowerCase() ||
                taxonomy.id.toLowerCase() === group.toLowerCase()) {
              return componentName;
            }
          }
        }
      } catch {
        // Fallback to group name
      }
      return group; // Fallback
    };

    // Get actual component names for source and target
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

  buildAssociativeRelations(availableTaxonomies, allTags) {
    const connectorTaxonomies = availableTaxonomies.filter(t => {
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
    const connectorTags = allTags.filter(tag => {
      try {
        const regex = XRegExp(connectorTaxonomy.regex_pattern);
        return regex.test(tag.name);
      } catch {
        return false;
      }
    });

    const allRelationGroups = new Set();
    availableTaxonomies.forEach(taxonomy => {
      taxonomy.relations?.forEach(relation => {
        if (relation.group) {
          allRelationGroups.add(relation.group);
        }
      });
    });

    connectorTags.forEach(connectorTag => {
      const components = this.parseTagComponents(connectorTag.name, connectorTaxonomy);
      if (!components) return;

      const allGroups = Array.from(allRelationGroups);
      const componentValues = [];

      allGroups.forEach(groupName => {
        const value = components[groupName];
        if (value) {
          componentValues.push({
            name: groupName,
            value: value,
            tag: this.findTagByComponent(value, allTags)
          });
        }
      });

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
              group: `associative_${sourceComponent.name}_to_${targetComponent.tag.taxonomy}`
            });
          }
        }
      }
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

  graphToTree(rootTaxonomyId) {
    const isAssociativeMode = this.edges.some(edge =>
      edge.group && edge.group.startsWith('associative_')
    );

    if (isAssociativeMode) {
      return this.buildAssociativeTree(rootTaxonomyId);
    } else {
      return this.buildNormalTree(rootTaxonomyId);
    }
  }

  extractTaxonomyOrderFromEdges() {
    const taxonomyOrder = [];
    const seenTaxonomies = new Set();

    this.edges.forEach(edge => {
      if (edge.group && edge.group.startsWith('associative_')) {
        const match = edge.group.match(/associative_(.+)_to_(.+)/);
        if (match) {
          const [, sourceGroup, targetTaxonomy] = match;

          if (!seenTaxonomies.has(sourceGroup)) {
            taxonomyOrder.push(sourceGroup);
            seenTaxonomies.add(sourceGroup);
          }

          if (!seenTaxonomies.has(targetTaxonomy)) {
            taxonomyOrder.push(targetTaxonomy);
            seenTaxonomies.add(targetTaxonomy);
          }
        }
      }
    });

    return taxonomyOrder;
  }

  buildAssociativeTree(rootTaxonomyId) {
    const taxonomyOrder = this.extractTaxonomyOrderFromEdges();
    const rootNodes = Array.from(this.nodes.values())
      .filter(node => node.taxonomy === rootTaxonomyId);

    const visited = new Set();
    const treeData = [];

    rootNodes.forEach(rootNode => {
      const treeNode = this.buildAssociativeTreeNode(rootNode, visited, 0, taxonomyOrder);
      if (treeNode) {
        treeData.push(treeNode);
      }
    });

    return treeData;
  }

  extractTaxonomyOrderFromEdges() {
    const taxonomyOrder = [];
    const seenTaxonomies = new Set();

    this.edges.forEach(edge => {
      if (edge.group && edge.group.startsWith('associative_')) {
        const match = edge.group.match(/associative_(.+)_to_(.+)/);
        if (match) {
          const [, sourceGroup, targetTaxonomy] = match;

          if (!seenTaxonomies.has(sourceGroup)) {
            taxonomyOrder.push(sourceGroup);
            seenTaxonomies.add(sourceGroup);
          }

          if (!seenTaxonomies.has(targetTaxonomy)) {
            taxonomyOrder.push(targetTaxonomy);
            seenTaxonomies.add(targetTaxonomy);
          }
        }
      }
    });

    return taxonomyOrder;
  }

  buildAssociativeTreeNode(node, visited, level, taxonomyOrder) {
    if (visited.has(node.id)) {
      return null;
    }
    visited.add(node.id);

    const children = [];

    // Find children based on taxonomy order
    // Need to map group names to taxonomy IDs dynamically
    const nodeIndexInOrder = taxonomyOrder.findIndex(orderItem => {
      // Check if this node's taxonomy matches the current order item
      // Order items can be either group names or taxonomy IDs
      return orderItem === node.taxonomy ||
             this.getTaxonomyIdForGroup(orderItem, this.edges) === node.taxonomy;
    });

    if (nodeIndexInOrder !== -1) {
      // Find next taxonomy items in order
      for (let i = nodeIndexInOrder + 1; i < taxonomyOrder.length; i++) {
        const nextOrderItem = taxonomyOrder[i];
        const nextTaxonomyId = this.getTaxonomyIdForGroup(nextOrderItem, this.edges);

        const childrenOfNextTaxonomy = this.findChildrenInTaxonomy(node, nextTaxonomyId);

        childrenOfNextTaxonomy.forEach(childNode => {
          if (!visited.has(childNode.id)) {
            const childTreeNode = this.buildAssociativeTreeNode(childNode, visited, level + 1, taxonomyOrder);
            if (childTreeNode) {
              children.push(childTreeNode);
            }
          }
        });
      }
    }

    return {
      id: node.id,
      name: node.name,
      taxonomy: node.taxonomy,
      projectsCount: node.projectsCount,
      level,
      children: children.sort((a, b) => a.name.localeCompare(b.name))
    };
  }

  // Helper to map group names to taxonomy IDs based on edges
  getTaxonomyIdForGroup(groupName, edges) {
    // Check if groupName is actually a taxonomy ID already
    const taxonomyNodes = Array.from(this.nodes.values()).filter(node => node.taxonomy === groupName);
    if (taxonomyNodes.length > 0) {
      return groupName; // It's already a taxonomy ID
    }

    // Look for edges that connect this group to a taxonomy
    const connectingEdges = edges.filter(edge =>
      edge.group && edge.group.startsWith('associative_') &&
      edge.group.includes(`_to_${groupName}`)
    );

    if (connectingEdges.length > 0) {
      const targetTaxonomy = connectingEdges[0].group.match(/associative_(.+)_to_(.+)/)[2];
      return targetTaxonomy;
    }

    return groupName; // Fallback to group name
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

  findChildrenInTaxonomy(parentNode, targetTaxonomy) {
    return Array.from(this.nodes.values())
      .filter(node =>
        node.taxonomy === targetTaxonomy &&
        this.edges.some(edge =>
          (edge.source === parentNode.id && edge.target === node.id) ||
          (edge.target === parentNode.id && edge.source === node.id)
        )
      );
  }

  buildNormalTree(rootTaxonomyId) {
    const rootNodes = Array.from(this.nodes.values())
      .filter(node => node.taxonomy === rootTaxonomyId);

    const visited = new Set();
    const treeData = [];

    rootNodes.forEach(rootNode => {
      const treeNode = this.buildNormalTreeNode(rootNode, visited, 0);
      if (treeNode) {
        treeData.push(treeNode);
      }
    });

    return treeData;
  }

  buildNormalTreeNode(node, visited, level) {
    if (visited.has(node.id)) {
      return null;
    }
    visited.add(node.id);

    const children = [];
    const connectedEdges = this.edges.filter(edge =>
      edge.source === node.id || edge.target === node.id
    );

    connectedEdges.forEach(edge => {
      const childId = edge.source === node.id ? edge.target : edge.source;
      const childNode = this.nodes.get(childId);

      if (childNode && !visited.has(childId)) {
        const childTreeNode = this.buildNormalTreeNode(childNode, visited, level + 1);
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

  generateSVG(layout = 'circle') {
    const width = 800;
    const height = 600;
    const nodeRadius = 20;

    const positions = this.calculateLayout(width, height, layout);

    let svg = `<svg width="${width}" height="${height}" xmlns="http://www.w3.org/2000/svg">`;

    this.edges.forEach(edge => {
      const source = positions[edge.source];
      const target = positions[edge.target];

      if (!source || !target) {
        console.warn(`Missing position for edge: ${edge.source} -> ${edge.target}`);
        return;
      }

      svg += `<line x1="${source.x}" y1="${source.y}" x2="${target.x}" y2="${target.y}" stroke="#ccc" stroke-width="2"/>`;
    });

    Array.from(this.nodes.values()).forEach(node => {
      const pos = positions[node.id];

      if (!pos) {
        console.warn(`Missing position for node: ${node.id}`);
        return;
      }

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
    const positions = {};
    const centerX = width / 2;
    const centerY = height / 2;

    nodes.forEach(node => {
      positions[node.id] = {
        x: Math.random() * (width - 100) + 50,
        y: Math.random() * (height - 100) + 50
      };
    });

    for (let iter = 0; iter < 50; iter++) {
      nodes.forEach((node1, i) => {
        nodes.forEach((node2, j) => {
          if (i !== j) {
            const pos1 = positions[node1.id];
            const pos2 = positions[node2.id];

            if (!pos1 || !pos2) return;

            const dx = pos2.x - pos1.x;
            const dy = pos2.y - pos1.y;
            const distance = Math.sqrt(dx * dx + dy * dy) || 1;
            const force = 1000 / (distance * distance);

            pos1.x -= (dx / distance) * force;
            pos1.y -= (dy / distance) * force;
          }
        });
      });

      this.edges.forEach(edge => {
        const source = positions[edge.source];
        const target = positions[edge.target];

        if (!source || !target) return;

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

      nodes.forEach(node => {
        const pos = positions[node.id];
        if (pos) {
          pos.x = Math.max(50, Math.min(width - 50, pos.x));
          pos.y = Math.max(50, Math.min(height - 50, pos.y));
        }
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
    const levels = [];
    const visited = new Set();
    const nodeMap = new Map(nodes.map(n => [n.id, n]));

    const roots = nodes.filter(node =>
      !this.edges.some(edge => edge.target === node.id)
    );

    if (roots.length === 0 && nodes.length > 0) {
      roots.push(nodes[0]);
    }

    const queue = roots.map(node => ({ node, level: 0 }));

    while (queue.length > 0) {
      const { node, level } = queue.shift();

      if (visited.has(node.id)) continue;
      visited.add(node.id);

      if (!levels[level]) levels[level] = [];
      levels[level].push(node);

      this.edges
        .filter(edge => edge.source === node.id)
        .forEach(edge => {
          const targetNode = nodeMap.get(edge.target);
          if (targetNode && !visited.has(targetNode.id)) {
            queue.push({ node: targetNode, level: level + 1 });
          }
        });
    }

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
