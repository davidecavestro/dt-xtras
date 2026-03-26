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

    // Get all relation groups
    const allRelationGroups = new Set();
    taxonomies.forEach(taxonomy => {
      taxonomy.relations?.forEach(relation => {
        if (relation.group) {
          allRelationGroups.add(relation.group);
        }
      });
    });

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

    // Create associative connections
    connectorTags.forEach(connectorTag => {
      const components = this.parseTagComponents(connectorTag.name, connectorTaxonomy);
      if (!components) return;

      const allGroups = Array.from(allRelationGroups);
      const componentValues = [];

      allGroups.forEach(groupName => {
        const componentName = getComponentNameForGroup(connectorTaxonomy, groupName);
        const value = components[componentName];

        if (value) {
          // Find the corresponding node to get taxonomy info
          const node = this.findNodeByComponent(value);
          componentValues.push({
            name: groupName,
            value: value,
            tag: node || this.findTagByComponent(value, tags)
          });
        }
      });

      // Create edges between consecutive components
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
              group: `associative_${sourceComponent.name}_to_${targetComponent.tag.taxonomy || 'unknown'}`
            });
            console.log(`✅ Created associative edge: ${sourceComponent.tag.name} -> ${targetComponent.tag.name} (group: associative_${sourceComponent.name}_to_${targetComponent.tag.taxonomy || 'unknown'})`);
          }
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
    const connectedEdges = this.edges.filter(edge => edge.source === node.id);

    connectedEdges.forEach(edge => {
      const childNode = this.nodes.get(edge.target);
      if (childNode && !visited.has(childNode.id)) {
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

  buildAssociativeTree(rootTaxonomyId) {
    const rootNodes = Array.from(this.nodes.values())
      .filter(node => node.taxonomy === rootTaxonomyId);

    const visited = new Set();
    const treeData = [];

    rootNodes.forEach(rootNode => {
      const treeNode = this.buildAssociativeTreeNode(rootNode, visited, 0);
      if (treeNode) {
        treeData.push(treeNode);
      }
    });

    return treeData;
  }

  buildAssociativeTreeNode(node, visited, level) {
    if (visited.has(node.id)) {
      return null;
    }
    visited.add(node.id);

    const children = [];

    // In associative mode, consider both incoming and outgoing edges
    const incomingEdges = this.edges.filter(edge => edge.target === node.id);
    const outgoingEdges = this.edges.filter(edge => edge.source === node.id);

    // Process incoming edges (reverse direction for tree building)
    incomingEdges.forEach(edge => {
      const parentNode = this.nodes.get(edge.source);
      if (parentNode && !visited.has(parentNode.id)) {
        const childTreeNode = this.buildAssociativeTreeNode(parentNode, visited, level + 1);
        if (childTreeNode) {
          children.push(childTreeNode);
        }
      }
    });

    // Process outgoing edges (normal direction)
    outgoingEdges.forEach(edge => {
      const childNode = this.nodes.get(edge.target);
      if (childNode && !visited.has(childNode.id)) {
        const childTreeNode = this.buildAssociativeTreeNode(childNode, visited, level + 1);
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
}
