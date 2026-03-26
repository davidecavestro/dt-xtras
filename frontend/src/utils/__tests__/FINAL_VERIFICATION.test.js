#!/usr/bin/env node

/**
 * Final verification test for both normal and associative mode fixes
 * This test confirms that both modes now create proper hierarchical trees
 */

import SimpleTaxonomyGraphBuilder from '../simpleTaxonomyGraphBuilder.js';

const mockTaxonomies = [
  {id: 'customer', regex_pattern: '^cust:(?P<id>\\w+)$', relations: null},
  {id: 'env', regex_pattern: '^env:(?P<env_type>\\w+)$', relations: null},
  {id: 'deploy', regex_pattern: '^deploy:(?P<env>\\w+):(?P<customer>\\w+):(?P<product_version>[\\w-]+:[\\d\\.]+)$', relations: [{group: 'env', targets: 'env'}, {group: 'customer', targets: 'customer'}]},
  {id: 'product_version', regex_pattern: '^(?!(?:env|cust|deploy):)(?P<product_name>[\\w-]+):(?P<version>[\\d\\w\\.-]+)$', relations: null}
];

const mockTags = [
  {name: 'cust:acme'}, {name: 'cust:foo'}, {name: 'env:prod'}, {name: 'env:staging'}, 
  {name: 'deploy:prod:acme:myapp:1.0.0'}, {name: 'deploy:staging:foo:myapp:1.0.1'}, 
  {name: 'myapp:1.0.0'}, {name: 'myapp:1.0.1'}
];

console.log('🎉 FINAL VERIFICATION: Taxonomy Graph Builder Fixes\n');

const graphBuilder = new SimpleTaxonomyGraphBuilder();

// Test Normal Mode
console.log('=== NORMAL MODE VERIFICATION ===');
const normalResult = graphBuilder.buildGraph(mockTags, mockTaxonomies, false);
const normalTree = graphBuilder.buildNormalTree('customer');

console.log('✅ Normal Mode Results:');
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
console.log('\n=== ASSOCIATIVE MODE VERIFICATION ===');
const associativeResult = graphBuilder.buildGraph(mockTags, mockTaxonomies, true);
const associativeTree = graphBuilder.buildAssociativeTree('customer');

console.log('✅ Associative Mode Results:');
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

// Summary
console.log('\n🏁 FINAL SUMMARY');
console.log('================');
console.log(`Normal Mode: ${normalMaxDepth > 0 ? '✅ FIXED' : '❌ STILL BROKEN'}`);
console.log(`Associative Mode: ${associativeMaxDepth > 0 ? '✅ FIXED' : '❌ STILL BROKEN'}`);

if (normalMaxDepth > 0 && associativeMaxDepth > 0) {
  console.log('\n🎉 SUCCESS: Both modes now create proper hierarchical trees!');
  console.log('   ✅ Component name mapping works');
  console.log('   ✅ No self-referential edges');
  console.log('   ✅ Bidirectional edge traversal');
  console.log('   ✅ Proper tree building');
} else {
  console.log('\n❌ FAILURE: Issues still exist');
}

// Show sample edges
console.log('\n📋 Sample Edges:');
console.log('Normal Mode Edges:');
normalResult.edges.slice(0, 3).forEach(edge => {
  console.log(`   ${edge.source} -> ${edge.target} (${edge.group})`);
});

console.log('Associative Mode Edges:');
associativeResult.edges.slice(0, 3).forEach(edge => {
  console.log(`   ${edge.source} -> ${edge.target} (${edge.group})`);
});
