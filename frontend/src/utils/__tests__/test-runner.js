#!/usr/bin/env node

/**
 * Test runner for SimpleTaxonomyGraphBuilder
 * This script can be run independently to test the graph builder logic
 */

import SimpleTaxonomyGraphBuilder from '../simpleTaxonomyGraphBuilder.js';

// Mock data based on actual API responses
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

class TestRunner {
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
    console.log('🧪 Running SimpleTaxonomyGraphBuilder Tests\n');

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
  testComponentParsing() {
    this.test('Component Parsing - Deploy Tag', () => {
      const deployTaxonomy = mockTaxonomies.find(t => t.id === 'deploy');
      const result = this.graphBuilder.parseTagComponents('deploy:prod:acme:myapp:1.0.0', deployTaxonomy);

      this.assertEqual(result, {
        env: 'prod',
        customer: 'acme',
        product_version: 'myapp:1.0.0',
        full_tag: 'deploy:prod:acme:myapp:1.0.0'
      });
    });

    this.test('Component Parsing - Env Tag', () => {
      const envTaxonomy = mockTaxonomies.find(t => t.id === 'env');
      const result = this.graphBuilder.parseTagComponents('env:prod', envTaxonomy);

      this.assertEqual(result, {
        env_type: 'prod',
        full_tag: 'env:prod'
      });
    });

    this.test('Component Parsing - Customer Tag', () => {
      const customerTaxonomy = mockTaxonomies.find(t => t.id === 'customer');
      const result = this.graphBuilder.parseTagComponents('cust:acme', customerTaxonomy);

      this.assertEqual(result, {
        id: 'acme',
        full_tag: 'cust:acme'
      });
    });

    this.test('Component Parsing - Non-matching Tag', () => {
      const deployTaxonomy = mockTaxonomies.find(t => t.id === 'deploy');
      const result = this.graphBuilder.parseTagComponents('not:deploy:tag', deployTaxonomy);

      this.assertEqual(result, null);
    });
  }

  testGraphBuilding() {
    this.test('Graph Building - Normal Mode', () => {
      const result = this.graphBuilder.buildGraph(mockTags, mockTaxonomies, false);

      this.assert(result.edges.length > 0, 'Should create edges');
      this.assert(result.nodes.size === 9, 'Should create nodes for all tags');

      // Check for specific expected edges
      const deployToEnvEdge = result.edges.find(edge =>
        edge.source === 'deploy:prod:acme:myapp:1.0.0' && edge.target === 'env:prod'
      );
      this.assert(deployToEnvEdge, 'Should create deploy->env edge');

      const deployToCustomerEdge = result.edges.find(edge =>
        edge.source === 'deploy:prod:acme:myapp:1.0.0' && edge.target === 'cust:acme'
      );
      this.assert(deployToCustomerEdge, 'Should create deploy->customer edge');
    });

    this.test('Graph Building - No Self-Referential Edges', () => {
      const result = this.graphBuilder.buildGraph(mockTags, mockTaxonomies, false);

      const selfReferentialEdges = result.edges.filter(edge => edge.source === edge.target);
      this.assertEqual(selfReferentialEdges.length, 0, 'Should not create self-referential edges');
    });

    this.test('Graph Building - Associative Mode', () => {
      const result = this.graphBuilder.buildGraph(mockTags, mockTaxonomies, true);

      this.assert(result.edges.length > 0, 'Should create associative edges');

      const associativeEdges = result.edges.filter(edge => edge.group.startsWith('associative_'));
      this.assert(associativeEdges.length > 0, 'Should create associative edges with proper group names');
    });
  }

  testTreeBuilding() {
    this.test('Tree Building - Normal Mode', () => {
      this.graphBuilder.buildGraph(mockTags, mockTaxonomies, false);
      const tree = this.graphBuilder.buildNormalTree('customer');

      this.assert(tree.length > 0, 'Should build tree structure');
      this.assert(tree[0].hasOwnProperty('id'), 'Tree nodes should have id');
      this.assert(tree[0].hasOwnProperty('children'), 'Tree nodes should have children');
    });

    this.test('Tree Building - Associative Mode', () => {
      this.graphBuilder.buildGraph(mockTags, mockTaxonomies, true);
      const tree = this.graphBuilder.buildAssociativeTree('customer');

      this.assert(tree.length > 0, 'Should build associative tree structure');
      this.assert(tree[0].hasOwnProperty('id'), 'Tree nodes should have id');
      this.assert(tree[0].hasOwnProperty('children'), 'Tree nodes should have children');
    });
  }

  testErrorHandling() {
    this.test('Error Handling - Empty Taxonomies', () => {
      const result = this.graphBuilder.buildGraph(mockTags, [], false);

      this.assertEqual(result.edges.length, 0, 'Should handle empty taxonomies');
      this.assertEqual(result.nodes.size, 0, 'Should handle empty taxonomies');
    });

    this.test('Error Handling - Empty Tags', () => {
      const result = this.graphBuilder.buildGraph([], mockTaxonomies, false);

      this.assertEqual(result.edges.length, 0, 'Should handle empty tags');
      this.assertEqual(result.nodes.size, 0, 'Should handle empty tags');
    });
  }

  runAllTests() {
    this.testComponentParsing();
    this.testGraphBuilding();
    this.testTreeBuilding();
    this.testErrorHandling();
    return this.run();
  }
}

// Run tests if this script is executed directly
if (import.meta.url === `file://${process.argv[1]}`) {
  const runner = new TestRunner();
  const success = runner.runAllTests();
  process.exit(success ? 0 : 1);
}

export default TestRunner;
