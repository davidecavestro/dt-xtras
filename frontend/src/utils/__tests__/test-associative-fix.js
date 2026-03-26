#!/usr/bin/env node

/**
 * Test to verify associative mode fix is working
 */

import SimpleTaxonomyGraphBuilder from '../simpleTaxonomyGraphBuilder.js';

const mockTaxonomies = [
  {id: 'customer', regex_pattern: '^cust:(?<id>\\w+)$', relations: null},
  {id: 'env', regex_pattern: '^env:(?<env_type>\\w+)$', relations: null},
  {id: 'deploy', regex_pattern: '^deploy:(?<env>\\w+):(?<customer>\\w+):(?<product_version>[\\w-]+:[\\d\\.]+)$', relations: [{group: 'env', targets: 'env'}, {group: 'customer', targets: 'customer'}]},
  {id: 'product_version', regex_pattern: '^(?!(?:env|cust|deploy):)(?<product_name>[\\w-]+):(?<version>[\\d\\w\\.-]+)$', relations: null}
];

const mockTags = [
  {name: 'cust:acme'}, {name: 'env:prod'}, {name: 'deploy:prod:acme:myapp:1.0.0'}
];

console.log('🧪 Testing Associative Mode Fix\n');

const graphBuilder = new SimpleTaxonomyGraphBuilder();
const result = graphBuilder.buildGraph(mockTags, mockTaxonomies, true);

console.log('Nodes:', result.nodes.size);
console.log('Edges:', result.edges.length);

result.edges.forEach(edge => {
  console.log('Edge:', edge.source, '->', edge.target, '(group:', edge.group + ')');
});

// Test tree building
const tree = graphBuilder.buildAssociativeTree('customer');
console.log('\nAssociative Tree:');
console.log('Root nodes:', tree.length);
if (tree.length > 0) {
  tree.forEach((root, index) => {
    console.log(`Root ${index + 1}: ${root.name} (taxonomy: ${root.taxonomy})`);
    console.log(`  Children: ${root.children.length}`);
    root.children.forEach((child, childIndex) => {
      console.log(`    Child ${childIndex + 1}: ${child.name} (taxonomy: ${child.taxonomy})`);
    });
  });
}

// Check if it's still flat
let totalChildren = 0;
tree.forEach(root => {
  totalChildren += root.children.length;
});

console.log(`\nTotal root nodes: ${tree.length}`);
console.log(`Total children: ${totalChildren}`);
console.log(`Is flat list: ${tree.length > 0 && totalChildren === 0 ? 'YES' : 'NO'}`);
