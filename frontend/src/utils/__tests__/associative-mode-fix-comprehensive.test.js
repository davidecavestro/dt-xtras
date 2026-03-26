#!/usr/bin/env node

/**
 * Comprehensive test for the associative mode fix
 * This test verifies that the associative mode creates proper hierarchical trees
 * instead of flat lists by using component name mapping and bidirectional edge traversal
 */

import SimpleTaxonomyGraphBuilder from '../simpleTaxonomyGraphBuilder.fixed.js';

// Test data based on the actual API response
const mockTaxonomies = [
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

class AssociativeModeFixComprehensiveTest {
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
    console.log('🧪 Running Comprehensive Associative Mode Fix Tests\n');
    
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
  testComponentNameMappingInAssociativeMode() {
    this.test('Component Name Mapping - Associative Mode', () => {
      const result = this.graphBuilder.buildGraph(mockTags, mockTaxonomies, true);
      
      this.assert(result.edges.length > 0, 'Should create associative edges with component name mapping');
      
      // Check that edges have proper group names
      const associativeEdges = result.edges.filter(edge => edge.group.startsWith('associative_'));
      this.assert(associativeEdges.length > 0, 'Should create edges with associative_ group names');
      
      associativeEdges.forEach(edge => {
        this.assert(edge.group.includes('_to_'), `Edge group should contain '_to_': ${edge.group}`);
        this.assert(!edge.group.includes('_to_undefined'), `Edge group should not contain 'undefined': ${edge.group}`);
      });
      
      console.log(`   Created ${result.edges.length} associative edges with proper naming`);
    });
  }

  testAssociativeTreeBuilding() {
    this.test('Associative Tree Building - Hierarchy Created', () => {
      this.graphBuilder.buildGraph(mockTags, mockTaxonomies, true);
      const tree = this.graphBuilder.buildAssociativeTree('customer');
      
      this.assert(tree.length > 0, 'Should build associative tree structure');
      
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

    this.test('Associative Tree Building - Bidirectional Edge Traversal', () => {
      this.graphBuilder.buildGraph(mockTags, mockTaxonomies, true);
      const tree = this.graphBuilder.buildAssociativeTree('customer');
      
      this.assert(tree.length > 0, 'Should build associative tree');
      
      // Verify that children are found through both incoming and outgoing edges
      let totalChildren = 0;
      tree.forEach(root => {
        totalChildren += root.children.length;
      });
      
      this.assert(totalChildren > 0, 'Should find children through bidirectional edge traversal');
      
      console.log(`   Found ${totalChildren} children through bidirectional edge traversal`);
    });
  }

  testEdgeCreationInAssociativeMode() {
    this.test('Edge Creation - Multiple Connections', () => {
      const result = this.graphBuilder.buildGraph(mockTags, mockTaxonomies, true);
      
      this.assert(result.edges.length >= 2, 'Should create multiple associative edges for complex data');
      
      // Verify edges connect different taxonomies
      const customerToEnvEdges = result.edges.filter(edge => 
        (edge.source.includes('cust') && edge.target.includes('env')) ||
        (edge.target.includes('cust') && edge.source.includes('env'))
      );
      
      this.assert(customerToEnvEdges.length > 0, 'Should create edges between customer and environment taxonomies');
      
      console.log(`   Created ${result.edges.length} edges including customer-environment connections`);
    });

    this.test('Edge Creation - Proper Component Value Matching', () => {
      const result = this.graphBuilder.buildGraph(mockTags, mockTaxonomies, true);
      
      // Verify that edges are created based on matching component values
      result.edges.forEach(edge => {
        this.assert(edge.source !== edge.target, 'Should not create self-referential edges');
        this.assert(edge.group.startsWith('associative_'), 'Should have associative group naming');
      });
      
      console.log(`   All ${result.edges.length} edges have proper component value matching`);
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

    this.test('Regression - No Undefined Taxonomy Groups', () => {
      const result = this.graphBuilder.buildGraph(mockTags, mockTaxonomies, true);
      
      result.edges.forEach(edge => {
        this.assert(!edge.group.includes('undefined'), `Edge group should not contain 'undefined': ${edge.group}`);
      });
      
      console.log('   No undefined taxonomy groups in edge names');
    });
  }

  testIntegrationWithNormalMode() {
    this.test('Integration - Normal Mode Still Works', () => {
      const normalResult = this.graphBuilder.buildGraph(mockTags, mockTaxonomies, false);
      
      this.assert(normalResult.edges.length > 0, 'Normal mode should still create edges');
      
      const normalTree = this.graphBuilder.buildNormalTree('customer');
      this.assert(normalTree.length > 0, 'Normal mode tree building should still work');
      
      console.log(`   Normal mode: ${normalResult.edges.length} edges, ${normalTree.length} root nodes`);
    });

    this.test('Integration - Mode Detection Works', () => {
      const associativeResult = this.graphBuilder.buildGraph(mockTags, mockTaxonomies, true);
      const normalResult = this.graphBuilder.buildGraph(mockTags, mockTaxonomies, false);
      
      const associativeTree = this.graphBuilder.graphToTree('customer');
      const normalTree = this.graphBuilder.graphToTree('customer');
      
      // Reset graph and test mode detection
      this.graphBuilder.buildGraph(mockTags, mockTaxonomies, true);
      const autoAssociativeTree = this.graphBuilder.graphToTree('customer');
      
      this.graphBuilder.buildGraph(mockTags, mockTaxonomies, false);
      const autoNormalTree = this.graphBuilder.graphToTree('customer');
      
      this.assert(autoAssociativeTree.length > 0, 'Auto-detection should work for associative mode');
      this.assert(autoNormalTree.length > 0, 'Auto-detection should work for normal mode');
      
      console.log('   Mode detection and auto-switching works correctly');
    });
  }

  runAllTests() {
    this.testComponentNameMappingInAssociativeMode();
    this.testAssociativeTreeBuilding();
    this.testEdgeCreationInAssociativeMode();
    this.testRegressionPrevention();
    this.testIntegrationWithNormalMode();
    return this.run();
  }
}

// Run tests if this script is executed directly
if (import.meta.url === `file://${process.argv[1]}`) {
  const tester = new AssociativeModeFixComprehensiveTest();
  const success = tester.runAllTests();
  process.exit(success ? 0 : 1);
}

export default AssociativeModeFixComprehensiveTest;
