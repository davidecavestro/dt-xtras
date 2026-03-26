#!/usr/bin/env node

/**
 * Debug script to understand associative tree building issues
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

console.log('🔍 Debug: Associative Mode Analysis\n');

const graphBuilder = new SimpleTaxonomyGraphBuilder();

// Step 1: Build graph
console.log('Step 1: Building associative graph...');
const result = graphBuilder.buildGraph(mockTags, mockTaxonomies, true);

console.log(`Nodes: ${result.nodes.size}`);
console.log(`Edges: ${result.edges.length}`);

// Step 2: Analyze edges
console.log('\nStep 2: Analyzing edges...');
result.edges.forEach((edge, index) => {
  console.log(`Edge ${index + 1}: ${edge.source} -> ${edge.target} (group: ${edge.group})`);
});

// Step 3: Analyze nodes
console.log('\nStep 3: Analyzing nodes...');
Array.from(result.nodes.values()).forEach(node => {
  console.log(`Node: ${node.name} (taxonomy: ${node.taxonomy})`);
});

// Step 4: Extract taxonomy order
console.log('\nStep 4: Extracting taxonomy order...');
const taxonomyOrder = graphBuilder.extractTaxonomyOrderFromEdges();
console.log('Taxonomy order:', taxonomyOrder);

// Step 5: Build tree
console.log('\nStep 5: Building associative tree...');
const tree = graphBuilder.buildAssociativeTree('customer');

console.log(`Root nodes: ${tree.length}`);
tree.forEach((root, index) => {
  console.log(`Root ${index + 1}: ${root.name} (taxonomy: ${root.taxonomy})`);
  console.log(`  Children: ${root.children.length}`);
  root.children.forEach((child, childIndex) => {
    console.log(`    Child ${childIndex + 1}: ${child.name} (taxonomy: ${child.taxonomy})`);
  });
});

// Step 6: Check if edges are being found correctly
console.log('\nStep 6: Checking edge connections...');
const customerNodes = Array.from(result.nodes.values()).filter(node => node.taxonomy === 'customer');
const envNodes = Array.from(result.nodes.values()).filter(node => node.taxonomy === 'env');

console.log(`Customer nodes: ${customerNodes.map(n => n.name)}`);
console.log(`Environment nodes: ${envNodes.map(n => n.name)}`);

// Check if there are edges between customer and env nodes
const customerToEnvEdges = result.edges.filter(edge => 
  (edge.source.includes('cust') && edge.target.includes('env')) ||
  (edge.target.includes('cust') && edge.source.includes('env'))
);

console.log(`Customer->Environment edges: ${customerToEnvEdges.length}`);
customerToEnvEdges.forEach(edge => {
  console.log(`  ${edge.source} -> ${edge.target} (${edge.group})`);
});
