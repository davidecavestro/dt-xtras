
export default class SimpleTaxonomyGraphBuilder {
  constructor() {
    this.nodes = new Map();
    this.tagTaxonomies = new Map();
    this.edges = [];
  }

  findTaxonomyForTag(tag, taxonomies) {
    // use cached taxonomy if available
    if (this.tagTaxonomies.has(tag.name)) {
      return this.tagTaxonomies.get(tag.name);
    }
    // otherwise search
    const taxonomy = taxonomies.find(taxonomy => {
      try {
        const regex = new RegExp(taxonomy.regex_pattern);
        return regex.test(tag.name);
      } catch {
        return false;
      }
    });
    this.tagTaxonomies.set(tag.name, taxonomy);
    return taxonomy;
  }

  buildGraph(tags, taxonomies, associativeMode = false) {
    console.log('Building graph with', tags.length, 'tags and', taxonomies.length, 'taxonomies');
    console.log('Associative mode:', associativeMode);

    // Clear previous data
    this.nodes.clear();
    this.tagTaxonomies.clear();
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

  buildAssociativeRelations(taxonomies, tags) {
    tags.forEach(tag => { // get the taxonomy for the tag
      const taxonomy = this.findTaxonomyForTag(tag, taxonomies);
      if (taxonomy) {
        // create edges based on the taxonomy's capture groups' relation
        const regex = new RegExp(taxonomy.regex_pattern);
        const match = regex.exec(tag.name);
        if (match && taxonomy.relations) {
          // captureGroups is an object with keys as group names and values as group values
          const captureGroups = match.groups;
          Object.keys(captureGroups).forEach(key => {
            const group = captureGroups[key];
            // Create edge between tag and target
            this.edges.push({
              id:  `${tag.name}-${key}`,
              source: tag.name,
              target: group
            });
          });
        }
      }
    });
  }

  buildNormalRelations(taxonomies, tags) {
    // TODO: Implement normal relation logic
    // This should create edges based on the taxonomy's relations configuration
  }

  graphToTree(rootTaxonomyId) {
    // TODO: Implement tree building logic
    // This should build a hierarchical tree structure from the graph
    // For now, return an empty array as a placeholder
    return [];
  }

}
