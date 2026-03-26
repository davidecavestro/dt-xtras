#!/usr/bin/env node

/**
 * Corrected Associative Mode Test
 * Verifies that associative mode follows capture group order from taxonomy pattern
 */

import SimpleTaxonomyGraphBuilder from '../simpleTaxonomyGraphBuilder.js';

const mockTaxonomies = [
  {
    id: 'customer',
    regex_pattern: '^cust:(?<id>\\w+)$',
    relations: null
  },
  {
    id: 'env',
    regex_pattern: '^env:(?<env_type>\\w+)$',
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
    regex_pattern: '^(?!(?:env|cust|deploy):)(?<product_name>[\\w-]+):(?<version>[\\d\\w\\.-]+)$',
    relations: null
  }
];

const mockTags = [
  { name: 'cust:acme' },
  { name: 'cust:foo' },
  { name: 'env:prod' },
  { name: 'env:staging' },
  { name: 'myapp:1.0.0' },
  { name: 'myapp:1.0.1' },
  { name: 'deploy:prod:acme:myapp:1.0.0' },
  { name: 'deploy:staging:foo:myapp:1.0.1' }
];

class CorrectedAssociativeModeTest {
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
    console.log('🧪 Corrected Associative Mode Tests\n');
    
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
  testCaptureGroupOrder() {
    this.test('Capture Group Order Followed', () => {
      this.graphBuilder.buildGraph(mockTags, mockTaxonomies, true);
      
      // Should create edges following capture group order: env -> customer -> product_version
      const edges = this.graphBuilder.edges;
      
      // Should have env -> customer edge
      const envToCustomerEdge = edges.find(e => 
        (e.source.includes('env') && e.target.includes('cust')) ||
        (e.target.includes('env') && e.source.includes('cust'))
      );
      this.assert(envToCustomerEdge, 'Should create env -> customer edge');
      
      // Should have customer -> product_version edge  
      const customerToProductEdge = edges.find(e =>
        (e.source.includes('cust') && e.target.includes('myapp')) ||
        (e.target.includes('cust') && e.source.includes('myapp'))
      );
      this.assert(customerToProductEdge, 'Should create customer -> product_version edge');
      
      // Edge groups should reflect capture group order
      this.assert(envToCustomerEdge.group.includes('env_to_customer'), 
        'Edge group should show env_to_customer');
      this.assert(customerToProductEdge.group.includes('customer_to_product_version'), 
        'Edge group should show customer_to_product_version');
      
      console.log(`   ✅ Created edges following capture group order`);
      console.log(`   ✅ env -> customer: ${envToCustomerEdge.source} -> ${envToCustomerEdge.target}`);
      console.log(`   ✅ customer -> product_version: ${customerToProductEdge.source} -> ${customerToProductEdge.target}`);
    });
  }

  testHierarchicalTreeStructure() {
    this.test('Hierarchical Tree Structure', () => {
      const result = this.graphBuilder.buildGraph(mockTags, mockTaxonomies, true);
      const tree = this.graphBuilder.buildTree('customer');
      
      this.assert(tree.length > 0, 'Should build tree structure');
      
      // Customer taxonomy should be root
      const customerRoots = tree.filter(root => root.taxonomy === 'customer');
      this.assert(customerRoots.length > 0, 'Should have customer roots');
      
      // Should have children (not flat)
      let totalChildren = 0;
      tree.forEach(root => {
        totalChildren += root.children.length;
      });
      this.assert(totalChildren > 0, 'Should have hierarchical structure (not flat)');
      
      console.log(`   ✅ Tree has ${tree.length} roots with ${totalChildren} total children`);
    });
  }

  testMultipleDeployments() {
    this.test('Multiple Deployments Handled', () => {
      const result = this.graphBuilder.buildGraph(mockTags, mockTaxonomies, true);
      
      // Should handle multiple deployment tags
      const edges = this.graphBuilder.edges;
      
      // Should have edges for both deployments
      const prodDeploymentEdges = edges.filter(e => 
        e.source.includes('prod') && e.target.includes('acme') ||
        e.target.includes('prod') && e.source.includes('acme')
      );
      const stagingDeploymentEdges = edges.filter(e =>
        e.source.includes('staging') && e.target.includes('foo') ||
        e.target.includes('staging') && e.source.includes('foo')
      );
      
      this.assert(prodDeploymentEdges.length > 0, 'Should handle prod deployment');
      this.assert(stagingDeploymentEdges.length > 0, 'Should handle staging deployment');
      
      console.log(`   ✅ Prod deployment edges: ${prodDeploymentEdges.length}`);
      console.log(`   ✅ Staging deployment edges: ${stagingDeploymentEdges.length}`);
    });
  }

  testNoConnectorNodes() {
    this.test('Connector Nodes Hidden', () => {
      const result = this.graphBuilder.buildGraph(mockTags, mockTaxonomies, true);
      
      // Connector nodes (deploy:*) should not appear in tree
      const tree = this.graphBuilder.buildTree('customer');
      const allNodes = [];
      
      const collectNodes = (nodes) => {
        nodes.forEach(node => {
          allNodes.push(node);
          if (node.children) {
            collectNodes(node.children);
          }
        });
      };
      
      collectNodes(tree);
      
      const connectorNodes = allNodes.filter(node => 
        node.name.startsWith('deploy:')
      );
      
      this.assertEqual(connectorNodes.length, 0, 
        'Connector nodes should be hidden in associative mode');
      
      console.log(`   ✅ No connector nodes in tree (${allNodes.length} total nodes)`);
    });
  }

  testEdgeDirectionConsistency() {
    this.test('Edge Direction Consistency', () => {
      const result = this.graphBuilder.buildGraph(mockTags, mockTaxonomies, true);
      const edges = this.graphBuilder.edges;
      
      // All edges should have associative_ prefix
      const associativeEdges = edges.filter(e => e.group.startsWith('associative_'));
      this.assertEqual(associativeEdges.length, edges.length, 
        'All edges should have associative_ prefix');
      
      // Edge groups should follow pattern: associative_{source}_to_{target}
      associativeEdges.forEach(edge => {
        this.assert(edge.group.includes('_to_'), 
          `Edge group should follow pattern: ${edge.group}`);
      });
      
      console.log(`   ✅ All ${edges.length} edges have proper associative naming`);
    });
  }

  testExpectedStructure() {
    this.test('Expected Hierarchical Structure', () => {
      const result = this.graphBuilder.buildGraph(mockTags, mockTaxonomies, true);
      const tree = this.graphBuilder.buildTree('customer');
      
      // Expected structure based on capture group order:
      // env:prod -> cust:acme -> myapp:1.0.0
      // env:staging -> cust:foo -> myapp:1.0.1
      
      let foundExpectedStructure = false;
      
      tree.forEach(root => {
        if (root.taxonomy === 'customer') {
          const hasEnvChild = root.children.some(child => child.taxonomy === 'env');
          const hasProductChild = root.children.some(child => child.taxonomy === 'product_version');
          
          if (hasEnvChild && hasProductChild) {
            foundExpectedStructure = true;
          }
        }
      });
      
      this.assert(foundExpectedStructure, 
        'Should create expected hierarchical structure');
      
      console.log(`   ✅ Found expected hierarchical structure`);
    });
  }

  runAllTests() {
    this.testCaptureGroupOrder();
    this.testHierarchicalTreeStructure();
    this.testMultipleDeployments();
    this.testNoConnectorNodes();
    this.testEdgeDirectionConsistency();
    this.testExpectedStructure();
    return this.run();
  }
}

// Run tests if this script is executed directly
if (import.meta.url === `file://${process.argv[1]}`) {
  const tester = new CorrectedAssociativeModeTest();
  const success = tester.runAllTests();
  process.exit(success ? 0 : 1);
}

export default CorrectedAssociativeModeTest;
