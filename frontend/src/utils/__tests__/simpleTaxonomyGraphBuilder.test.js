import SimpleTaxonomyGraphBuilder from '../simpleTaxonomyGraphBuilder.js';
import XRegExp from 'xregexp';

describe('SimpleTaxonomyGraphBuilder', () => {
  let graphBuilder;
  let mockTaxonomies;
  let mockTags;

  beforeEach(() => {
    graphBuilder = new SimpleTaxonomyGraphBuilder();
    
    // Mock taxonomies based on the actual API response
    mockTaxonomies = [
      {
        id: 'customer',
        name: 'Customer',
        regex_pattern: '^cust:(?P<id>\\w+)$',
        priority: 1,
        relations: null
      },
      {
        id: 'env',
        name: 'Environment',
        regex_pattern: '^env:(?P<env_type>\\w+)$',
        priority: 2,
        relations: null
      },
      {
        id: 'deploy',
        name: 'Deployment',
        regex_pattern: '^deploy:(?P<env>\\w+):(?P<customer>\\w+):(?P<product_version>[\\w-]+:[\\d\\.]+)$',
        priority: 3,
        relations: [
          { group: 'env', targets: 'env' },
          { group: 'customer', targets: 'customer' },
          { group: 'product_version', targets: 'product_version' }
        ]
      },
      {
        id: 'product_version',
        name: 'Product Version',
        regex_pattern: '^(?!(?:env|cust|deploy):)(?P<product_name>[\\w-]+):(?P<version>[\\d\\w\\.-]+)$',
        priority: 4,
        relations: null
      }
    ];

    // Mock tags based on the actual API response
    mockTags = [
      { name: 'cust:acme', projectsCount: 0 },
      { name: 'cust:foo', projectsCount: 0 },
      { name: 'cust:fuffa', projectsCount: 0 },
      { name: 'env:prod', projectsCount: 0 },
      { name: 'env:staging', projectsCount: 0 },
      { name: 'deploy:prod:acme:myapp:1.0.0', projectsCount: 0 },
      { name: 'deploy:staging:foo:myapp:1.0.1', projectsCount: 0 },
      { name: 'myapp:1.0.0', projectsCount: 2 },
      { name: 'myapp:1.0.1', projectsCount: 1 }
    ];
  });

  describe('parseTagComponents', () => {
    test('should parse deployment tags correctly', () => {
      const deployTaxonomy = mockTaxonomies.find(t => t.id === 'deploy');
      const result = graphBuilder.parseTagComponents('deploy:prod:acme:myapp:1.0.0', deployTaxonomy);
      
      expect(result).toEqual({
        env: 'prod',
        customer: 'acme',
        product_version: 'myapp:1.0.0',
        full_tag: 'deploy:prod:acme:myapp:1.0.0'
      });
    });

    test('should parse environment tags correctly', () => {
      const envTaxonomy = mockTaxonomies.find(t => t.id === 'env');
      const result = graphBuilder.parseTagComponents('env:prod', envTaxonomy);
      
      expect(result).toEqual({
        env_type: 'prod',
        full_tag: 'env:prod'
      });
    });

    test('should parse customer tags correctly', () => {
      const customerTaxonomy = mockTaxonomies.find(t => t.id === 'customer');
      const result = graphBuilder.parseTagComponents('cust:acme', customerTaxonomy);
      
      expect(result).toEqual({
        id: 'acme',
        full_tag: 'cust:acme'
      });
    });

    test('should parse product version tags correctly', () => {
      const productTaxonomy = mockTaxonomies.find(t => t.id === 'product_version');
      const result = graphBuilder.parseTagComponents('myapp:1.0.0', productTaxonomy);
      
      expect(result).toEqual({
        product_name: 'myapp',
        version: '1.0.0',
        full_tag: 'myapp:1.0.0'
      });
    });

    test('should return null for non-matching tags', () => {
      const deployTaxonomy = mockTaxonomies.find(t => t.id === 'deploy');
      const result = graphBuilder.parseTagComponents('not:deploy:tag', deployTaxonomy);
      
      expect(result).toBeNull();
    });

    test('should handle invalid regex patterns gracefully', () => {
      const invalidTaxonomy = {
        id: 'invalid',
        regex_pattern: '[invalid regex'
      };
      
      const result = graphBuilder.parseTagComponents('some:tag', invalidTaxonomy);
      expect(result).toBeNull();
    });
  });

  describe('buildGraph - Normal Mode', () => {
    test('should create edges between related taxonomies', () => {
      const result = graphBuilder.buildGraph(mockTags, mockTaxonomies, false);
      
      expect(result.edges).toHaveLength(4); // Should create edges for deploy->env and deploy->customer connections
      expect(result.nodes.size).toBe(9); // All tags should be nodes
    });

    test('should skip self-referential connections', () => {
      const result = graphBuilder.buildGraph(mockTags, mockTaxonomies, false);
      
      // Should not have edges like myapp:1.0.0 -> myapp:1.0.0
      const selfReferentialEdges = result.edges.filter(edge => edge.source === edge.target);
      expect(selfReferentialEdges).toHaveLength(0);
    });

    test('should create edges with correct group names', () => {
      const result = graphBuilder.buildGraph(mockTags, mockTaxonomies, false);
      
      // Should have edges with group 'env' and 'customer'
      const envEdges = result.edges.filter(edge => edge.group === 'env');
      const customerEdges = result.edges.filter(edge => edge.group === 'customer');
      
      expect(envEdges.length).toBeGreaterThan(0);
      expect(customerEdges.length).toBeGreaterThan(0);
    });
  });

  describe('buildGraph - Associative Mode', () => {
    test('should create associative edges between components', () => {
      const result = graphBuilder.buildGraph(mockTags, mockTaxonomies, true);
      
      expect(result.edges.length).toBeGreaterThan(0);
      expect(result.nodes.size).toBe(9);
    });

    test('should create edges with associative group names', () => {
      const result = graphBuilder.buildGraph(mockTags, mockTaxonomies, true);
      
      const associativeEdges = result.edges.filter(edge => edge.group.startsWith('associative_'));
      expect(associativeEdges.length).toBeGreaterThan(0);
    });
  });

  describe('buildNormalTree', () => {
    test('should build hierarchical tree structure', () => {
      // Build graph first
      graphBuilder.buildGraph(mockTags, mockTaxonomies, false);
      
      const tree = graphBuilder.buildNormalTree('customer');
      
      expect(tree.length).toBeGreaterThan(0);
      expect(tree[0]).toHaveProperty('id');
      expect(tree[0]).toHaveProperty('name');
      expect(tree[0]).toHaveProperty('children');
    });
  });

  describe('buildAssociativeTree', () => {
    test('should build associative tree structure', () => {
      // Build graph first
      graphBuilder.buildGraph(mockTags, mockTaxonomies, true);
      
      const tree = graphBuilder.buildAssociativeTree('customer');
      
      expect(tree.length).toBeGreaterThan(0);
      expect(tree[0]).toHaveProperty('id');
      expect(tree[0]).toHaveProperty('name');
      expect(tree[0]).toHaveProperty('children');
    });
  });

  describe('Component Name Mapping', () => {
    test('should map group names to component names correctly', () => {
      // This tests the internal logic of getComponentNameForGroup
      const envTaxonomy = mockTaxonomies.find(t => t.id === 'env');
      const customerTaxonomy = mockTaxonomies.find(t => t.id === 'customer');
      
      // Test that 'env' group maps to 'env_type' component in env taxonomy
      const envComponents = graphBuilder.parseTagComponents('env:prod', envTaxonomy);
      expect(envComponents).toHaveProperty('env_type');
      
      // Test that 'customer' group maps to 'id' component in customer taxonomy
      const customerComponents = graphBuilder.parseTagComponents('cust:acme', customerTaxonomy);
      expect(customerComponents).toHaveProperty('id');
    });
  });

  describe('Edge Creation Logic', () => {
    test('should create edges when component values match', () => {
      const result = graphBuilder.buildGraph(mockTags, mockTaxonomies, false);
      
      // Should create edge: deploy:prod:acme:myapp:1.0.0 -> env:prod (both have 'prod' value)
      const deployToEnvEdge = result.edges.find(edge => 
        edge.source === 'deploy:prod:acme:myapp:1.0.0' && edge.target === 'env:prod'
      );
      expect(deployToEnvEdge).toBeDefined();
      expect(deployToEnvEdge.group).toBe('env');
    });

    test('should create edges for customer connections', () => {
      const result = graphBuilder.buildGraph(mockTags, mockTaxonomies, false);
      
      // Should create edge: deploy:prod:acme:myapp:1.0.0 -> cust:acme (both have 'acme' value)
      const deployToCustomerEdge = result.edges.find(edge => 
        edge.source === 'deploy:prod:acme:myapp:1.0.0' && edge.target === 'cust:acme'
      );
      expect(deployToCustomerEdge).toBeDefined();
      expect(deployToCustomerEdge.group).toBe('customer');
    });
  });

  describe('Error Handling', () => {
    test('should handle empty taxonomies gracefully', () => {
      const result = graphBuilder.buildGraph(mockTags, [], false);
      
      expect(result.edges).toHaveLength(0);
      expect(result.nodes.size).toBe(0);
    });

    test('should handle empty tags gracefully', () => {
      const result = graphBuilder.buildGraph([], mockTaxonomies, false);
      
      expect(result.edges).toHaveLength(0);
      expect(result.nodes.size).toBe(0);
    });

    test('should handle missing relations gracefully', () => {
      const taxonomiesWithoutRelations = mockTaxonomies.map(t => ({ ...t, relations: null }));
      const result = graphBuilder.buildGraph(mockTags, taxonomiesWithoutRelations, false);
      
      expect(result.edges).toHaveLength(0);
      expect(result.nodes.size).toBe(9); // Nodes should still be created
    });
  });

  describe('Integration Tests', () => {
    test('should work end-to-end with realistic data', () => {
      const result = graphBuilder.buildGraph(mockTags, mockTaxonomies, false);
      
      // Verify graph structure
      expect(result.nodes.size).toBe(9);
      expect(result.edges.length).toBeGreaterThan(0);
      
      // Verify specific expected edges exist
      const expectedEdges = [
        { source: 'deploy:prod:acme:myapp:1.0.0', target: 'env:prod', group: 'env' },
        { source: 'deploy:prod:acme:myapp:1.0.0', target: 'cust:acme', group: 'customer' },
        { source: 'deploy:staging:foo:myapp:1.0.1', target: 'env:staging', group: 'env' },
        { source: 'deploy:staging:foo:myapp:1.0.1', target: 'cust:foo', group: 'customer' }
      ];
      
      expectedEdges.forEach(expectedEdge => {
        const foundEdge = result.edges.find(edge => 
          edge.source === expectedEdge.source && 
          edge.target === expectedEdge.target && 
          edge.group === expectedEdge.group
        );
        expect(foundEdge).toBeDefined();
      });
    });
  });
});
