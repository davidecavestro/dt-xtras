// Graph-based taxonomy tree builder using Cytoscape.js
import cytoscape from 'cytoscape';
import XRegExp from 'xregexp';

class TaxonomyGraphBuilder {
  constructor() {
    this.graph = null;
    this.nodeMap = new Map();
  }

  // Initialize graph with all tags and relations
  buildGraph(allTags, availableTaxonomies) {
    console.log('Building graph with', allTags.length, 'tags and', availableTaxonomies.length, 'taxonomies');

    this.graph = cytoscape({
      elements: [],
      styleEnabled: false // Disable styling for performance
    });

    this.nodeMap.clear();

    // Add all tags as nodes
    allTags.forEach(tag => {
      const taxonomy = this.findTaxonomyForTag(tag.name, availableTaxonomies);
      const nodeData = {
        id: tag.name,
        name: tag.name,
        type: 'tag',
        taxonomy: taxonomy.id,
        pattern: taxonomy.regex_pattern,
        projectsCount: tag.projectsCount || 0
      };

      this.graph.add({ data: nodeData });
      this.nodeMap.set(tag.name, nodeData);
    });

    console.log('Added', this.graph.nodes().length, 'nodes to graph');

    // Build edges based on taxonomy relations
    this.buildRelations(availableTaxonomies, allTags);

    console.log('Graph built with', this.graph.nodes().length, 'nodes and', this.graph.edges().length, 'edges');
    return this.graph;
  }

  // Build relations between nodes based on taxonomy connections
  buildRelations(availableTaxonomies, allTags) {
    // Process ALL taxonomy relations to build undirected graph
    for (const taxonomy of availableTaxonomies) {
      if (!taxonomy.relations || taxonomy.relations.length === 0) continue;

      console.log('Processing relations for taxonomy:', taxonomy.id);

      for (const relation of taxonomy.relations) {
        console.log('Processing relation:', relation);
        console.log('Relation keys:', Object.keys(relation));

        // Handle different relation structures
        const sourceId = relation.source || relation.sourceTaxonomy || relation.from || relation.group;
        const targetId = relation.targets || relation.targetTaxonomy || relation.to;

        console.log('Relation source:', sourceId);
        console.log('Relation targets:', targetId);

        if (!sourceId || !targetId) {
          console.log('Skipping relation with missing source/target');
          continue;
        }

        // Find all tags for source taxonomy
        const sourceTaxonomy = availableTaxonomies.find(t => t.id === sourceId);
        if (!sourceTaxonomy) {
          console.log('Source taxonomy not found:', sourceId);
          continue;
        }

        const sourceTags = allTags.filter(tag => {
          try {
            const regex = XRegExp(sourceTaxonomy.regex_pattern);
            return regex.test(tag.name);
          } catch (error) {
            console.error('Invalid regex for source taxonomy:', error);
            return false;
          }
        });

        // Find all tags for target taxonomy
        const targetTaxonomy = availableTaxonomies.find(t => t.id === targetId);
        if (!targetTaxonomy) continue;

        const targetTags = allTags.filter(tag => {
          try {
            const regex = XRegExp(targetTaxonomy.regex_pattern);
            return regex.test(tag.name);
          } catch (error) {
            console.error('Invalid regex for target taxonomy:', error);
            return false;
          }
        });

        console.log('Found', sourceTags.length, 'source tags and', targetTags.length, 'target tags');
        console.log('Source tags:', sourceTags.map(t => t.name));
        console.log('Target tags:', targetTags.map(t => t.name));

        // Build connections based on component matching
        for (const sourceTag of sourceTags) {
          const sourceComponents = this.parseTagComponents(sourceTag.name);
          if (!sourceComponents) {
            console.log('No components for source tag:', sourceTag.name);
            continue;
          }
          console.log('Source components for', sourceTag.name, ':', sourceComponents);

          for (const targetTag of targetTags) {
            const targetComponents = this.parseTagComponents(targetTag.name);
            if (!targetComponents) {
              console.log('No components for target tag:', targetTag.name);
              continue;
            }
            console.log('Target components for', targetTag.name, ':', targetComponents);

            // Check if tags share components (undirected relation)
            const hasConnection = Object.values(sourceComponents).some(comp =>
              Object.values(targetComponents).includes(comp)
            );
            console.log('Connection check between', sourceTag.name, 'and', targetTag.name, ':', hasConnection);

            if (hasConnection) {
              // Add bidirectional edge if not already exists
              const edgeId1 = `${sourceTag.name}-${targetTag.name}`;
              const edgeId2 = `${targetTag.name}-${sourceTag.name}`;

              if (!this.graph.getElementById(edgeId1) && !this.graph.getElementById(edgeId2)) {
                this.graph.add({
                  data: {
                    id: edgeId1,
                    source: sourceTag.name,
                    target: targetTag.name,
                    relation: relation.type || 'connected'
                  }
                });
                console.log('Connected:', sourceTag.name, '<->', targetTag.name);
              }
            }
          }
        }
      }
    }
  }

  // Convert graph to tree structure for UI
  graphToTree(rootTaxonomyId) {
    console.log('Converting graph to tree for taxonomy:', rootTaxonomyId);

    const rootNodes = this.graph.nodes()
      .filter(node => node.data('taxonomy') === rootTaxonomyId);

    console.log('Found', rootNodes.length, 'root nodes for', rootTaxonomyId);
    console.log('Root nodes:', rootNodes.map(n => n.data('name')));

    const visited = new Set();
    const treeData = [];

    rootNodes.forEach(rootNode => {
      const treeNode = this.buildTreeNode(rootNode, visited, 0);
      if (treeNode) {
        treeData.push(treeNode);
      }
    });

    console.log('Final tree structure:', treeData);
    return treeData;
  }

  buildTreeNode(node, visited, level) {
    if (visited.has(node.id())) return null;
    visited.add(node.id());

    const children = [];
    node.outgoers().forEach(childNode => {
      const childTreeNode = this.buildTreeNode(childNode, visited, level + 1);
      if (childTreeNode) {
        children.push(childTreeNode);
      }
    });

    return {
      id: node.data('id'),
      name: node.data('name'),
      type: node.data('type'),
      taxonomy: node.data('taxonomy'),
      pattern: node.data('pattern'),
      projectsCount: node.data('projectsCount'),
      children: this.sortTreeNodes(children),
      projects: [],
      expanded: false,
      level: level,
      icon: this.getNodeIcon(node.data('name'))
    };
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
    }) || { id: 'unknown', regex_pattern: '' };
  }

  parseTagComponents(tagName) {
    console.log('Parsing tag components for:', tagName);

    // Handle deployment tags: deploy:env:prod:cust:acme:myapp:1.0.0
    if (tagName.startsWith('deploy:')) {
      const parts = tagName.split(':');
      if (parts.length >= 6) {
        return {
          deploy: parts[0],
          env: `env:${parts[1]}`,
          customer: `cust:${parts[2]}`,
          product_version: `${parts[3]}:${parts[4]}`,
          full_tag: tagName
        };
      }
    }

    // Handle simple tags: env:prod, cust:acme, myapp:1.0.0
    const parts = tagName.split(':');
    if (parts.length === 2) {
      return {
        type: parts[0],
        value: parts[1],
        full_tag: tagName
      };
    }

    console.log('Could not parse components for:', tagName);
    return null;
  }

  sortTreeNodes(nodes) {
    return nodes.sort((a, b) => {
      // Sort by type first (tags before projects), then by name
      if (a.type !== b.type) {
        return a.type === 'tag' ? -1 : 1;
      }
      return a.name.localeCompare(b.name);
    });
  }

  getNodeIcon(tagName) {
    // Your existing icon logic
    if (tagName.startsWith('cust:')) return '🏢';
    if (tagName.startsWith('env:')) return '🌍';
    if (tagName.startsWith('app:')) return '📱';
    if (tagName.startsWith('deploy:')) return '🚀';
    return '🏷️';
  }

  // Get graph statistics for debugging
  getGraphStats() {
    if (!this.graph) return null;

    return {
      nodes: this.graph.nodes().length,
      edges: this.graph.edges().length,
      taxonomies: [...new Set(this.graph.nodes().map(n => n.data('taxonomy')))],
      connectedComponents: this.graph.components().length
    };
  }
}

export default TaxonomyGraphBuilder;
