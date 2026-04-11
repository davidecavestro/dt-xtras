import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useGraphStore = defineStore('graph', () => {
  // State
  const nodes = ref([])
  const edges = ref([])
  const loading = ref(false)
  const error = ref('')
  const lastUpdate = ref(0)

  // Graph parameters
  const rootTaxonomy = ref(null)
  const associativeMode = ref(true)

  // Computed properties
  const graphData = computed(() => ({
    nodes: nodes.value,
    edges: edges.value
  }))

  const nodeCount = computed(() => nodes.value.length)
  const edgeCount = computed(() => edges.value.length)

  const nodeIds = computed(() => nodes.value.map(node => node.id))
  const edgeIds = computed(() => edges.value.map(edge => edge.id))

  // Find nodes by taxonomy
  const nodesByTaxonomy = computed(() => {
    const grouped = {}
    nodes.value.forEach(node => {
      const taxonomy = node.taxonomy || 'unknown'
      if (!grouped[taxonomy]) {
        grouped[taxonomy] = []
      }
      grouped[taxonomy].push(node)
    })
    return grouped
  })

  // Find associative nodes
  const associativeNodes = computed(() =>
    nodes.value.filter(node => node.associative)
  )

  // Find root nodes (nodes without incoming edges)
  const rootNodes = computed(() => {
    const targetIds = new Set(edges.value.map(edge => edge.target))
    const sourceIds = new Set(edges.value.map(edge => edge.source))
    return nodes.value.filter(node =>
      !targetIds.has(node.id) && sourceIds.has(node.id)
    )
  })

  // Methods
  const loadGraph = async (params = {}) => {
    if (loading.value) return

    loading.value = true
    error.value = null

    try {
      // Import here to avoid circular dependency
      const { default: axios } = await import('axios')

      // Build query parameters - backend already supports all needed features
      const queryParams = {
        root_taxonomy: params.rootTaxonomy || rootTaxonomy.value,
        associative_mode: params.associativeMode !== undefined ? params.associativeMode : associativeMode.value
      }

      const response = await axios.get('/api/graph', { params: queryParams })

      // Update state
      nodes.value = response.data.nodes || []
      edges.value = response.data.edges || []

      // Update timestamp to trigger watchers
      lastUpdate.value = Date.now()

      return response.data
    } catch (err) {
      error.value = err.response?.data?.detail || err.message || 'Failed to load graph data'
      logger.error('Error loading graph:', err)

      // Reset state on error
      nodes.value = []
      edges.value = []

      throw err
    } finally {
      loading.value = false
    }
  }

  // Method for loading tag-based graphs (uses same backend endpoint)
  const loadTagGraph = async (params = {}) => {
    return await loadGraph(params)
  }

  const refreshGraph = async (params = {}) => {
    return await loadGraph(params)
  }

  const clearGraph = () => {
    nodes.value = []
    edges.value = []
    error.value = null
    lastUpdate.value = 0
  }

  const setRootTaxonomy = (taxonomy) => {
    rootTaxonomy.value = taxonomy
  }

  const setAssociativeMode = (mode) => {
    associativeMode.value = mode
  }

  // Find node by ID
  const getNodeById = (id) => {
    return nodes.value.find(node => node.id === id)
  }

  // Find edges connected to a node
  const getEdgesForNode = (nodeId, direction = 'both') => {
    return edges.value.filter(edge => {
      if (direction === 'source') {
        return edge.source === nodeId
      } else if (direction === 'target') {
        return edge.target === nodeId
      } else {
        return edge.source === nodeId || edge.target === nodeId
      }
    })
  }

  // Find connected nodes
  const getConnectedNodes = (nodeId, direction = 'both') => {
    const connectedEdges = getEdgesForNode(nodeId, direction)
    const connectedNodeIds = connectedEdges.map(edge =>
      edge.source === nodeId ? edge.target : edge.source
    )
    return nodes.value.filter(node => connectedNodeIds.includes(node.id))
  }

  // Find all nodes reachable from a starting node (BFS)
  const findReachableNodes = (startNodeId) => {
    if (!startNodeId || nodes.value.length === 0 || edges.value.length === 0) return new Set()

    const visited = new Set()
    const queue = [startNodeId]
    const reachableNodes = new Set()

    while (queue.length > 0) {
      const currentId = queue.shift()
      if (visited.has(currentId)) continue

      visited.add(currentId)
      reachableNodes.add(currentId)

      // Find connected nodes
      const connectedNodes = getConnectedNodes(currentId)
      connectedNodes.forEach(node => {
        if (!visited.has(node.id)) {
          queue.push(node.id)
        }
      })
    }

    return reachableNodes
  }

  // Find path from one node to another
  const findPath = (startNodeId, endNodeId) => {
    if (!startNodeId || !endNodeId) return null
    if (startNodeId === endNodeId) return [startNodeId]

    const visited = new Set()
    const queue = [{ node: startNodeId, path: [startNodeId] }]

    while (queue.length > 0) {
      const { node: currentId, path } = queue.shift()

      if (visited.has(currentId)) continue
      visited.add(currentId)

      const connectedNodes = getConnectedNodes(currentId)
      for (const connectedNode of connectedNodes) {
        const newPath = [...path, connectedNode.id]

        if (connectedNode.id === endNodeId) {
          return newPath
        }

        if (!visited.has(connectedNode.id)) {
          queue.push({ node: connectedNode.id, path: newPath })
        }
      }
    }

    return null
  }

  return {
    // State
    nodes,
    edges,
    loading,
    error,
    lastUpdate,
    rootTaxonomy,
    associativeMode,

    // Computed properties
    graphData,
    nodeCount,
    edgeCount,
    nodeIds,
    edgeIds,
    nodesByTaxonomy,
    associativeNodes,
    rootNodes,

    // Methods
    loadGraph,
    loadTagGraph,
    refreshGraph,
    clearGraph,
    setRootTaxonomy,
    setAssociativeMode,
    getNodeById,
    getEdgesForNode,
    getConnectedNodes,
    findReachableNodes,
    findPath
  }
})
