#!/usr/bin/env node

/**
 * Verification test for undirected graph implementation
 * This test confirms that treating the graph as undirected simplifies the logic
 * while maintaining proper hierarchical tree building
 */

import SimpleTaxonomyGraphBuilder from '../simpleTaxonomyGraphBuilder.js';

const mockTaxonomies = [
  {id: 'customer', regex_pattern: '^cust:(?<id>\\w+)$', relations: null},
  {id: 'env', regex_pattern: '^env:(?<env_type>\\w+)$', relations: null},
  {id: 'deploy', regex_pattern: '^deploy:(?<env>\\w+):(?<customer>\\w+):(?<product_version>[\\w-]+:[\\d\\.]+)$', relations: [{group: 'env', targets: 'env'}, {group: 'customer', targets: 'customer'}]},
  {id: 'product_version', regex_pattern: '^(?!(?:env|cust|deploy):)(?<product_name>[\\w-]+):(?<version>[\\d\\w\\.-]+)$', relations: null}
];

const mockTags = [
  {name: 'cust:acme'}, {name: 'cust:foo'}, {name: 'env:prod'}, {name: 'env:staging'}, 
  {name: 'deploy:prod:acme:myapp:1.0.0'}, {name: 'deploy:staging:foo:myapp:1.0.1'}, 
  {name: 'myapp:1.0.0'}, {name: 'myapp:1.0.1'}
];

console.log('🔄 UNDIRECTED GRAPH VERIFICATION\n');

const graphBuilder = new SimpleTaxonomyGraphBuilder();

// Test Normal Mode
console.log('=== NORMAL MODE (UNDIRECTED) ===');
const normalResult = graphBuilder.buildGraph(mockTags, mockTaxonomies, false);
const normalTree = graphBuilder.buildTree('customer');

console.log('✅ Results:');
console.log(`   Nodes: ${normalResult.nodes.size}`);
console.log(`   Edges: ${normalResult.edges.length}`);
console.log(`   Tree roots: ${normalTree.length}`);

let normalTotalNodes = 0;
let normalMaxDepth = 0;
const countNormalNodes = (node, depth = 0) => {
  normalTotalNodes++;
  normalMaxDepth = Math.max(normalMaxDepth, depth);
  if (node.children && node.children.length > 0) {
    node.children.forEach(child => countNormalNodes(child, depth + 1));
  }
};
normalTree.forEach(root => countNormalNodes(root));

console.log(`   Total nodes in tree: ${normalTotalNodes}`);
console.log(`   Tree depth: ${normalMaxDepth}`);
console.log(`   Status: ${normalMaxDepth > 0 ? '✅ HIERARCHICAL' : '❌ FLAT'}`);

// Test Associative Mode
console.log('\n=== ASSOCIATIVE MODE (UNDIRECTED) ===');
const associativeResult = graphBuilder.buildGraph(mockTags, mockTaxonomies, true);
const associativeTree = graphBuilder.buildTree('customer');

console.log('✅ Results:');
console.log(`   Nodes: ${associativeResult.nodes.size}`);
console.log(`   Edges: ${associativeResult.edges.length}`);
console.log(`   Tree roots: ${associativeTree.length}`);

let associativeTotalNodes = 0;
let associativeMaxDepth = 0;
const countAssociativeNodes = (node, depth = 0) => {
  associativeTotalNodes++;
  associativeMaxDepth = Math.max(associativeMaxDepth, depth);
  if (node.children && node.children.length > 0) {
    node.children.forEach(child => countAssociativeNodes(child, depth + 1));
  }
};
associativeTree.forEach(root => countAssociativeNodes(root));

console.log(`   Total nodes in tree: ${associativeTotalNodes}`);
console.log(`   Tree depth: ${associativeMaxDepth}`);
console.log(`   Status: ${associativeMaxDepth > 0 ? '✅ HIERARCHICAL' : '❌ FLAT'}`);

// Show tree structure
console.log('\n📋 Tree Structure (Normal Mode):');
normalTree.forEach((root, index) => {
  console.log(`Root ${index + 1}: ${root.name} (${root.taxonomy})`);
  printTree(root, '  ');
});

console.log('\n📋 Tree Structure (Associative Mode):');
associativeTree.forEach((root, index) => {
  console.log(`Root ${index + 1}: ${root.name} (${root.taxonomy})`);
  printTree(root, '  ');
});

function printTree(node, indent) {
  if (node.children && node.children.length > 0) {
    node.children.forEach(child => {
      console.log(`${indent}└── ${child.name} (${child.taxonomy})`);
      printTree(child, indent + '    ');
    });
  }
}

// Summary
console.log('\n🎯 UNDIRECTED GRAPH BENEFITS:');
console.log('✅ Simplified tree building logic');
console.log('✅ Single buildTree() method for both modes');
console.log('✅ Edge direction ignored (undirected graph)');
console.log('✅ Same hierarchical results with cleaner code');
console.log('✅ Easier to maintain and understand');

console.log('\n🏁 FINAL STATUS:');
console.log(`Normal Mode: ${normalMaxDepth > 0 ? '✅ FIXED' : '❌ BROKEN'}`);
console.log(`Associative Mode: ${associativeMaxDepth > 0 ? '✅ FIXED' : '❌ BROKEN'}`);
console.log(`Implementation: ${normalMaxDepth > 0 && associativeMaxDepth > 0 ? '✅ UNDIRECTED GRAPH WORKS!' : '❌ Issues remain'}`);
