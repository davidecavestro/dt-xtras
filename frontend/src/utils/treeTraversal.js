/**
 * Tree traversal utilities for hierarchical tag filtering
 */

/**
 * Find all descendant tags from a starting node in a tree structure
 * @param {string} startNodeId - The ID of the starting node
 * @param {Array} treeData - The tree data structure
 * @returns {Set} - Set of tag IDs (complete tag values) reachable from the start node
 */
export function findReachableTags(startNodeId, treeData) {
  if (!startNodeId || !treeData || treeData.length === 0) return new Set()

  const visited = new Set()
  const queue = [startNodeId]
  const reachableTags = new Set()

  // Helper function to find node in tree
  const findNodeInTree = (nodes, nodeId) => {
    for (const node of nodes) {
      if (node.id === nodeId) return node
      if (node.children && node.children.length > 0) {
        const found = findNodeInTree(node.children, nodeId)
        if (found) return found
      }
    }
    return null
  }

  while (queue.length > 0) {
    const currentId = queue.shift()
    if (visited.has(currentId)) continue

    visited.add(currentId)

    // Find the current node in the tree
    const currentNode = findNodeInTree(treeData, currentId)
    if (currentNode) {
      // Add the node's id (complete tag value) to reachable tags
      if (currentNode.id) {
        reachableTags.add(currentNode.id)
      }

      // Add all children to queue (downward traversal only)
      if (currentNode.children) {
        currentNode.children.forEach(child => {
          if (!visited.has(child.id)) {
            queue.push(child.id)
          }
        })
      }
    }
  }

  return reachableTags
}
