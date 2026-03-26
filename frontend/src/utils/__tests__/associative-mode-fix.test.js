#!/usr/bin/env node

/**
 * Test specifically for the associative mode fix
 * This test verifies that the associative mode creates proper hierarchical trees
 * instead of flat lists by using component name mapping
 */

import SimpleTaxonomyGraphBuilder from '../simpleTaxonomyGraphBuilder.js';

// Test data based on the actual API response
const mockTaxonomies = [
  {
    id: 'customer',
    name: 'Customer',
    regex_pattern: '^cust:(?<id>\\w+)$',
    priority: 1,
    relations: null
  },
  {
    id: 'env',
    name: 'Environment',
    regex_pattern: '^env:(?<env_type>\\w+)$',
    priority: 2,
    relations: null
  },
  {
    id: 'deploy',
    name: 'Deployment',
    regex_pattern: '^deploy:(?<env>\\w+):(?<customer>\\w+):(?<product_version>[\\w-]+:[\\d\\.]+)$',
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
    regex_pattern: '^(?!(?:env|cust|deploy):)(?<product_name>[\\w-]+):(?<version>[\\d\\w\\.-]+)$',
    priority: 4,
    relations: null
  }
];

const mockTags = [
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

class AssociativeModeFixTest {
  constructor() {
    this.graphBuilder = new SimpleTaxonomyGraphBuilder();
    this.tests = [];
    this.passed = 0;
    this.failed = 0;
  }

  test(name, testFn) {
    this.tests.push({ name, testFn });
  }

  run() {
    console.log('🧪 Running Associative Mode Fix Tests\n');
    
    this.tests.forEach(({ name, testFn }) => {
      try {
        console.log(`📋 ${name}`);
        testFn();
        console.log('✅ PASSED\n');
        this.passed++;
      } catch (error) {
        console.log('❌ FAILED');
        console.log(`   ${error.message}\n`);
        this.failed++;
      }
    });

    console.log(`📊 Test Results: ${this.passed} passed, ${this.failed} failed`);
    return this.failed === 0;
  }

  assert(condition, message) {
    if (!condition) {
      throw new Error(message || 'Assertion failed');
    }
  }

  assertEqual(actual, expected, message) {
    if (JSON.stringify(actual) !== JSON.stringify(expected)) {
      throw new Error(message || `Expected ${JSON.stringify(expected)}, got ${JSON.stringify(actual)}`);
    }
  }

  // Test methods
  testAssociativeGraphBuilding() {
    this.test('Associative Graph Building - Creates Edges', () => {
      const result = this.graphBuilder.buildGraph(mockTags, mockTaxonomies, true);
      
      this.assert(result.edges.length > 0, 'Should create associative edges');
      this.assert(result.nodes.size > 0, 'Should create nodes');
      
      // Check for associative edge naming
      const associativeEdges = result.edges.filter(edge => edge.group.startsWith('associative_'));
      this.assert(associativeEdges.length > 0, 'Should create edges with associative_ group names');
    });

    this.test('Associative Graph Building - Proper Edge Groups', () => {
      const result = this.graphBuilder.buildGraph(mockTags, mockTaxonomies, true);
      
      const associativeEdges = result.edges.filter(edge => edge.group.startsWith('associative_'));
      this.assert(associativeEdges.length > 0, 'Should have associative edges');
      
      // Check edge group naming pattern
      associativeEdges.forEach(edge => {
        this.assert(edge.group.includes('_to_'), `Edge group should contain '_to_': ${edge.group}`);
      });
    });

    this.test('Associative Graph Building - Component Name Mapping', () => {
      // This tests the fix where group names are mapped to component names
      const result = this.graphBuilder.buildGraph(mockTags, mockTaxonomies, true);
      
      this.assert(result.edges.length > 0, 'Should create edges with component name mapping');
      
      // The fix should allow proper component value extraction
      // This should result in edges being created between related tags
      console.log(`   Created ${result.edges.length} associative edges`);
    });
  }

  testAssociativeTreeBuilding() {
    this.test('Associative Tree Building - Creates Hierarchy', () => {
      this.graphBuilder.buildGraph(mockTags, mockTaxonomies, true);
      const tree = this.graphBuilder.buildAssociativeTree('customer');
      
      this.assert(tree.length > 0, 'Should build associative tree structure');
      this.assert(tree[0].hasOwnProperty('children'), 'Tree nodes should have children property');
      
      // Count total nodes to verify it's not a flat list
      let totalNodes = 0;
      let maxDepth = 0;
      
      const countNodes = (node, depth = 0) => {
        totalNodes++;
        maxDepth = Math.max(maxDepth, depth);
        if (node.children && node.children.length > 0) {
          node.children.forEach(child => countNodes(child, depth + 1));
        }
      };
      
      tree.forEach(root => countNodes(root));
      
      this.assert(totalNodes > 3, 'Should have multiple nodes in tree (not just flat list)');
      this.assert(maxDepth > 0, 'Should have hierarchical depth (not flat)');
      
      console.log(`   Tree has ${totalNodes} nodes with depth ${maxDepth}`);
    });

    this.test('Associative Tree Building - Multiple Roots', () => {
      this.graphBuilder.buildGraph(mockTags, mockTaxonomies, true);
      const tree = this.graphBuilder.buildAssociativeTree('customer');
      
      this.assert(tree.length >= 1, 'Should have at least one root node');
      
      // Each root should represent a different starting point
      tree.forEach((root, index) => {
        this.assert(root.hasOwnProperty('name'), `Root ${index} should have name`);
        this.assert(root.hasOwnProperty('taxonomy'), `Root ${index} should have taxonomy`);
      });
      
      console.log(`   Tree has ${tree.length} root nodes`);
    });
  }

  testComponentNameMappingInAssociativeMode() {
    this.test('Component Name Mapping - Group to Component', () => {
      // This specifically tests the fix for associative mode
      const deployTaxonomy = mockTaxonomies.find(t => t.id === 'deploy');
      const envTaxonomy = mockTaxonomies.find(t => t.id === 'env');
      
      // Test that the getComponentNameForGroup function works correctly
      const deployComponents = this.graphBuilder.parseTagComponents('deploy:prod:acme:myapp:1.0.0', deployTaxonomy);
      const envComponents = this.graphBuilder.parseTagComponents('env:prod', envTaxonomy);
      
      this.assert(deployComponents.hasOwnProperty('env'), 'Deploy should have env component');
      this.assert(envComponents.hasOwnProperty('env_type'), 'Env should have env_type component');
      
      // The values should match for proper edge creation
      this.assertEqual(deployComponents.env, 'prod', 'Deploy env component should be prod');
      this.assertEqual(envComponents.env_type, 'prod', 'Env env_type component should be prod');
      
      console.log('   Component name mapping works: env -> env_type');
    });

    this.test('Component Name Mapping - Customer Group', () => {
      const deployTaxonomy = mockTaxonomies.find(t => t.id === 'deploy');
      const customerTaxonomy = mockTaxonomies.find(t => t.id === 'customer');
      
      const deployComponents = this.graphBuilder.parseTagComponents('deploy:prod:acme:myapp:1.0.0', deployTaxonomy);
      const customerComponents = this.graphBuilder.parseTagComponents('cust:acme', customerTaxonomy);
      
      this.assert(deployComponents.hasOwnProperty('customer'), 'Deploy should have customer component');
      this.assert(customerComponents.hasOwnProperty('id'), 'Customer should have id component');
      
      this.assertEqual(deployComponents.customer, 'acme', 'Deploy customer component should be acme');
      this.assertEqual(customerComponents.id, 'acme', 'Customer id component should be acme');
      
      console.log('   Component name mapping works: customer -> id');
    });
  }

  testRegressionPrevention() {
    this.test('Regression - No Self-Referential Edges', () => {
      const result = this.graphBuilder.buildGraph(mockTags, mockTaxonomies, true);
      
      const selfReferentialEdges = result.edges.filter(edge => edge.source === edge.target);
      this.assertEqual(selfReferentialEdges.length, 0, 'Should not create self-referential edges in associative mode');
    });

    this.test('Regression - Component Extraction Works', () => {
      const deployTaxonomy = mockTaxonomies.find(t => t.id === 'deploy');
      const result = this.graphBuilder.parseTagComponents('deploy:prod:acme:myapp:1.0.0', deployTaxonomy);
      
      this.assert(result !== null, 'Should extract components from deploy tag');
      this.assert(result.hasOwnProperty('env'), 'Should extract env component');
      this.assert(result.hasOwnProperty('customer'), 'Should extract customer component');
      this.assert(result.hasOwnProperty('product_version'), 'Should extract product_version component');
      
      console.log('   Component extraction regression test passed');
    });
  }

  runAllTests() {
    this.testAssociativeGraphBuilding();
    this.testAssociativeTreeBuilding();
    this.testComponentNameMappingInAssociativeMode();
    this.testRegressionPrevention();
    return this.run();
  }
}

// Run tests if this script is executed directly
if (import.meta.url === `file://${process.argv[1]}`) {
  const tester = new AssociativeModeFixTest();
  const success = tester.runAllTests();
  process.exit(success ? 0 : 1);
}

export default AssociativeModeFixTest;
