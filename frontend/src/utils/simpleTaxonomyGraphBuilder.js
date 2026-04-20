import { createLogger } from './logger'
import { createJsRegExp } from './taxonomyParser'

export default class SimpleTaxonomyGraphBuilder {
  constructor() {
    this.nodes = new Map();
    this.tagTaxonomies = new Map();
    this.edges = [];
    this.logger = createLogger('taxonomy-graph-builder')
  }

  buildGraph(tags, taxonomies, rootTaxonomy, associativeMode = false) {
    this.logger.info('Building graph with', tags.length, 'tags and', taxonomies.length, 'taxonomies');
    this.logger.info('Associative mode:', associativeMode);
    this.logger.info('Root taxonomy:', rootTaxonomy);

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
          associative: taxonomy.associative || false,
          projectsCount: tag.projectsCount || 0
        });
      }
    });

    this.logger.info('Created', this.nodes.size, 'nodes');

    // Build edges based on mode
    if (associativeMode) {
      this.buildAssociativeRelations(taxonomies, tags, rootTaxonomy);
    } else {
      this.buildNormalRelations(taxonomies, tags, rootTaxonomy);
    }

    this.logger.info('Created', this.edges.length, 'edges');

    return {
      nodes: this.nodes,
      edges: this.edges
    };
  }

  buildAssociativeRelations(taxonomies, tags, rootTaxonomy) {
    const associativeNodesToHide = new Set();

    tags.forEach(tag => { // get the taxonomy for the tag
      const taxonomy = this.findTaxonomyForTag(tag, taxonomies);
      if (taxonomy) {
        // create edges based on the taxonomy's capture groups' relation
        const captureGroups = this.getTagValues(tag, taxonomy);
        if (captureGroups && taxonomy.relations && taxonomy.relations.length > 0) {
          if (taxonomy.relations.length === Object.keys(captureGroups).length) {
            associativeNodesToHide.add(tag.name); // mark associative tags to hide
          }
          var groupRelations = taxonomy.relations;
          if (rootTaxonomy) {
            // check if any group in groupRelations is the root taxonomy and get its position
            const rootGroupPosition = groupRelations.findIndex(relation => relation.group === rootTaxonomy);
            this.logger.info('Root group position:', rootGroupPosition);
            if (rootGroupPosition > 0) { // the root group is not in the first position
              // reorder the groupRelations array so that the root group is first
              const rootGroup = groupRelations[rootGroupPosition];
              groupRelations.splice(rootGroupPosition, 1);
              groupRelations.unshift(rootGroup);
            }
          }
          groupRelations.reduce( (prev, relation) => {
            const key = relation.group;
            const relationTarget = relation.targets;
            // find the tag belonging to the relation target taxonomy
            const targetTaxonomy = taxonomies.find(t => t.id === relationTarget);
            const targetTag = tags.find(t => t.taxonomy === targetTaxonomy.id && this.getTagValue(t, targetTaxonomy) === captureGroups[key]);
            // Create edge between previous group and current group
            if (prev && targetTag) {
              this.edges.push({
                id: `${prev}-${targetTag.name}`,
                source: prev,
                target: targetTag.name
              });
            }
            return targetTag?.name;
          }, null); //start with no previous value
        }
      }
    });

    // Filter out associative nodes
    const filteredNodes = new Map();
    this.nodes.forEach((node, nodeId) => {
      if (!associativeNodesToHide.has(nodeId)) {
        filteredNodes.set(nodeId, node);
      }
    });
    this.nodes = filteredNodes;
  }

  buildNormalRelations(taxonomies, tags, rootTaxonomy) {
    // the associative tags are visibile here
    tags.forEach(tag => {
      const taxonomy = this.findTaxonomyForTag(tag, taxonomies);
      if (taxonomy) {
        // create edges based on the taxonomy's capture groups' relation
        const captureGroups = this.getTagValues(tag, taxonomy);
        if (captureGroups && taxonomy.relations && taxonomy.relations.length > 0) {
          // captureGroups is an object with keys as group names and values as group values
          Object.keys(captureGroups).forEach( key => {
            const relation = taxonomy.relations.find(r => r.group === key);
            const relationTarget = relation.targets;
            // find the tag belonging to the relation target taxonomy
            const targetTaxonomy = taxonomies.find(t => t.id === relationTarget);
            const targetTag = tags.find(t => t.taxonomy === targetTaxonomy.id && this.getTagValue(t, targetTaxonomy) === captureGroups[key]);

            // Create edge between tag and target
            this.edges.push({
              id: `${tag.name}-${targetTag.name}`,
              source: tag.name,
              target: targetTag.name
            });
          });
        }
      }
    });
  }

  getTagValues (tag, taxonomy) {
    const regex = createJsRegExp(taxonomy.regex_pattern);
    if (!regex) return null;
    const match = regex.exec(tag.name);
    if (match && match.groups) {
      return match.groups;
    }
    return null;
  }

  getTagValue (tag, taxonomy) {
    const values = this.getTagValues(tag, taxonomy);
    // join all values with colons
    return values ? Object.values(values).join(':') : null;
  }

  findTaxonomyForTag(tag, taxonomies) {
    // use cached taxonomy if available
    if (this.tagTaxonomies.has(tag.name)) {
      return this.tagTaxonomies.get(tag.name);
    }
    // otherwise search
    const taxonomy = taxonomies.find(taxonomy => {
      const regex = createJsRegExp(taxonomy.regex_pattern);
      return regex ? regex.test(tag.name) : false;
    });
    this.tagTaxonomies.set(tag.name, taxonomy);
    return taxonomy;
  }

}
