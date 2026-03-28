<template>
  <div class="px-4 py-6 sm:px-0">
    <div class="flex gap-6">
      <!-- Left Panel - Tree Navigation -->
      <div class="w-80 bg-white dark:bg-gray-800 shadow overflow-hidden sm:rounded-md">
        <div class="p-4 border-b border-gray-200 dark:border-gray-700">
          <div class="flex justify-between items-center mb-3">
            <h3 class="text-lg font-medium text-gray-900 dark:text-white">Navigation Tree</h3>
            <button
              @click="clearSelection"
              v-if="selectedTreeNode"
              class="text-xs px-2 py-1 bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-300 rounded hover:bg-gray-200 dark:hover:bg-gray-600"
            >
              Clear Selection
            </button>
          </div>
          <input
            v-model="searchQuery"
            placeholder="Search tags, projects..."
            class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
          />
        </div>

        <div class="p-4 max-h-96 overflow-y-auto">
          <div v-if="loading" class="text-center py-4">
            <div class="inline-block animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600"></div>
          </div>

          <div v-else-if="treeData.length === 0" class="text-center py-4 text-gray-500 dark:text-gray-400">
            No tree data available
          </div>

          <div v-else class="space-y-1">
            <TreeNode
              v-for="node in filteredTreeData"
              :key="node.id"
              :node="node"
              :selected-node="selectedTreeNode"
              :expanded-nodes="expandedNodes"
              :search-query="searchQuery"
              @select="selectTreeNode"
              @toggle="toggleTreeNode"
            />
          </div>
        </div>

        <!-- Selected Node Info -->
        <div v-if="selectedTreeNode" class="p-4 border-t border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-900">
          <h4 class="text-sm font-medium text-gray-900 dark:text-white mb-2">Selected Node</h4>
          <div class="text-xs text-gray-600 dark:text-gray-400 space-y-1">
            <div><strong>Type:</strong> {{ selectedTreeNode.type }}</div>
            <div><strong>Name:</strong> {{ selectedTreeNode.name }}</div>
            <div v-if="selectedTreeNode.projectsCount !== undefined">
              <strong>Projects:</strong> {{ selectedTreeNode.projectsCount }}
            </div>
          </div>

          <!-- Related Projects Header -->
          <div class="mt-4 pt-4 border-t border-gray-200 dark:border-gray-700">
            <h3 class="text-lg leading-6 font-medium text-gray-900 dark:text-white">Related Projects</h3>
            <div class="text-sm text-gray-600 dark:text-gray-400">
              {{ relatedProjects.length }} projects found for "{{ selectedTreeNode.name }}"
            </div>
          </div>

          <!-- Related Projects List -->
          <div v-if="relatedProjects.length === 0" class="text-center py-8">
            <FolderOpen class="mx-auto h-12 w-12 text-gray-400" />
            <h3 class="mt-2 text-sm font-medium text-gray-900 dark:text-white">No related projects found</h3>
            <p class="mt-1 text-sm text-gray-500 dark:text-gray-400">
              Try selecting a different node or check your connections.
            </p>
          </div>

          <div v-else class="max-h-96 overflow-y-auto space-y-2">
            <div
              v-for="project in relatedProjects"
              :key="project.uuid"
              class="p-3 bg-white dark:bg-gray-800 rounded hover:bg-gray-100 dark:hover:bg-gray-600 cursor-pointer border border-gray-200 dark:border-gray-600"
            >
              <div class="flex justify-between items-start mb-2">
                <div class="flex-1">
                  <div class="text-sm font-medium text-gray-900 dark:text-white">{{ project.name }}</div>
                  <div class="text-xs text-gray-500 dark:text-gray-400">{{ project.version || 'latest' }}</div>
                </div>
                <div class="text-right">
                  <div class="text-xs text-gray-500 dark:text-gray-400">
                    {{ project.tags.join(', ') }}
                  </div>
                </div>
              </div>

              <!-- Security Info -->
              <div v-if="project.metrics" class="flex flex-wrap gap-2 text-xs">
                <span v-if="project.metrics.critical > 0" class="px-2 py-1 bg-red-100 dark:bg-red-900 text-red-800 dark:text-red-200 rounded">
                  🔴 {{ project.metrics.critical }} Critical
                </span>
                <span v-if="project.metrics.high > 0" class="px-2 py-1 bg-orange-100 dark:bg-orange-900 text-orange-800 dark:text-orange-200 rounded">
                  🟠 {{ project.metrics.high }} High
                </span>
                <span v-if="project.metrics.medium > 0" class="px-2 py-1 bg-yellow-100 dark:bg-yellow-900 text-yellow-800 dark:text-yellow-200 rounded">
                  🟡 {{ project.metrics.medium }} Medium
                </span>
                <span v-if="project.metrics.low > 0" class="px-2 py-1 bg-blue-100 dark:bg-blue-900 text-blue-800 dark:text-blue-200 rounded">
                  🔵 {{ project.metrics.low }} Low
                </span>
                <span v-if="getProjectVulnerabilities(project.metrics) === 0" class="px-2 py-1 bg-green-100 dark:bg-green-900 text-green-800 dark:text-green-200 rounded">
                  ✅ No Vulnerabilities
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Main Content - Dashboard -->
      <div class="flex-1">
        <div class="bg-white dark:bg-gray-800 shadow overflow-hidden sm:rounded-md">
          <div class="flex justify-between items-center mb-6 p-6">
            <div>
              <h2 class="text-2xl font-bold text-gray-900 dark:text-white">Security Dashboard</h2>
              <p v-if="selectedTreeNode" class="text-sm text-gray-600 dark:text-gray-400 mt-1">
                Filtered by: {{ selectedTreeNode.name }} ({{ selectedTreeNode.type }})
              </p>
            </div>
            <button
              @click="refreshData"
              :disabled="loading"
              class="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 flex items-center gap-2"
            >
              <RefreshCw v-if="loading" class="animate-spin w-4 h-4" />
              <span v-else>Refresh</span>
            </button>
          </div>

          <div v-if="loading" class="text-center py-8">
            <div class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
            <p class="mt-2 text-gray-600 dark:text-gray-400">Loading security data...</p>
          </div>

          <div v-else-if="error" class="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-md p-4">
            <div class="flex items-center">
              <AlertCircle class="h-5 w-5 text-red-400" />
              <div class="ml-3">
                <h3 class="text-sm font-medium text-red-800 dark:text-red-200">Error loading data</h3>
                <div class="mt-2 text-sm text-red-700 dark:text-red-300">{{ error }}</div>
              </div>
            </div>
          </div>

          <div v-else-if="!securityData || securityData.length === 0" class="text-center py-8">
            <div class="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
            <h3 class="mt-2 text-sm font-medium text-gray-900 dark:text-white">No security data available</h3>
            <p class="mt-1 text-gray-600 dark:text-gray-400">Try adjusting your filters or check your connection.</p>
          </div>

          <div v-else class="bg-white dark:bg-gray-800 shadow overflow-hidden sm:rounded-md">
            <div class="px-4 py-5 sm:px-6">
              <div class="flex justify-between items-center mb-6">
                <h3 class="text-lg leading-6 font-medium text-gray-900 dark:text-white">Security Overview</h3>
                <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                  <div class="bg-blue-50 dark:bg-blue-900/20 p-4 rounded-lg">
                    <div class="text-center">
                      <div class="text-3xl font-bold text-blue-600 dark:text-blue-300">{{ totalVulnerabilities }}</div>
                      <div class="text-sm text-blue-600 dark:text-blue-400">Total Vulnerabilities</div>
                    </div>
                  </div>

                  <div class="bg-orange-50 dark:bg-orange-900/20 p-4 rounded-lg">
                    <div class="text-center">
                      <div class="text-3xl font-bold text-orange-600 dark:text-orange-300">{{ criticalVulns }}</div>
                      <div class="text-sm text-orange-600 dark:text-orange-400">Critical</div>
                    </div>
                  </div>

                  <div class="bg-red-50 dark:bg-red-900/20 p-4 rounded-lg">
                    <div class="text-center">
                      <div class="text-3xl font-bold text-red-600 dark:text-red-300">{{ highVulns }}</div>
                      <div class="text-sm text-red-600 dark:text-red-400">High</div>
                    </div>
                  </div>

                  <div class="bg-yellow-50 dark:bg-yellow-900/20 p-4 rounded-lg">
                    <div class="text-center">
                      <div class="text-3xl font-bold text-yellow-600 dark:text-yellow-300">{{ mediumVulns }}</div>
                      <div class="text-sm text-yellow-600 dark:text-yellow-400">Medium</div>
                    </div>
                  </div>

                  <div class="bg-green-50 dark:bg-green-900/20 p-4 rounded-lg">
                    <div class="text-center">
                      <div class="text-3xl font-bold text-green-600 dark:text-green-300">{{ lowVulns }}</div>
                      <div class="text-sm text-green-600 dark:text-green-400">Low</div>
                    </div>
                  </div>

                  <div class="bg-gray-50 dark:bg-gray-700 p-4 rounded-lg">
                    <div class="text-center">
                      <div class="text-3xl font-bold text-gray-600 dark:text-gray-300">{{ infoVulns }}</div>
                      <div class="text-sm text-gray-600 dark:text-gray-400">Info</div>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <div class="mt-8">
              <h3 class="text-lg leading-6 font-medium text-gray-900 dark:text-white">Risk Score Distribution</h3>
              <div class="bg-white dark:bg-gray-800 p-4 rounded-lg">
                <div class="space-y-3">
                  <div v-for="item in riskDistribution" :key="item.range">
                    <div class="flex items-center justify-between mb-1">
                      <span class="text-sm font-medium text-gray-700 dark:text-gray-300 w-24">{{ item.range }}</span>
                      <span class="text-sm text-gray-600 dark:text-gray-400">
                        {{ item.count }}<span v-if="item.range !== 'Info'"> ({{ item.percentage }}%)</span>
                      </span>
                    </div>
                    <div v-if="item.range !== 'Info'" class="bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                      <div class="h-2 rounded-full" :class="getRiskBarColor(item.range)" :style="{ width: `${item.percentage}%` }"></div>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <div class="mt-8">
              <h3 class="text-lg leading-6 font-medium text-gray-900 dark:text-white">Recent Vulnerabilities</h3>
              <div class="bg-white dark:bg-gray-800 shadow overflow-hidden rounded-lg">
                <div v-if="recentVulns.length === 0" class="text-center py-8">
                  <Folder class="mx-auto h-12 w-12 text-gray-400" />
                  <h3 class="mt-2 text-sm font-medium text-gray-900 dark:text-white">No vulnerability details available</h3>
                  <p class="mt-1 text-sm text-gray-500 dark:text-gray-400">Security nodes show aggregated counts, not individual vulnerabilities.</p>
                </div>
                <div v-else class="divide-y divide-gray-200 dark:divide-gray-700">
                  <div v-for="vuln in recentVulns" :key="vuln.id" class="p-4 hover:bg-gray-50 dark:hover:bg-gray-700">
                    <div class="flex items-start justify-between">
                      <div class="flex-1">
                        <div class="flex items-center space-x-2">
                          <div class="w-2 h-2 rounded" :class="getSeverityColor(vuln.severity)"></div>
                          <div>
                            <div class="font-medium text-gray-900 dark:text-white">{{ vuln.vulnId }}</div>
                            <div class="text-sm text-gray-500 dark:text-gray-400">{{ vuln.component }}</div>
                          </div>
                        </div>
                        <div class="text-right">
                          <div class="text-sm text-gray-500 dark:text-gray-400">{{ formatDate(vuln.published) }}</div>
                        </div>
                      </div>
                      <div class="ml-4">
                        <RiskScoreBadge :score="vuln.severity" />
                        <VulnerabilityBar :score="vuln.severity" />
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, computed, watch } from 'vue'
import { AlertCircle, RefreshCw, Folder } from 'lucide-vue-next'
import axios from 'axios'
import RiskScoreBadge from './RiskScoreBadge.vue'
import VulnerabilityBar from './VulnerabilityBar.vue'
import TreeNode from './TreeNode.vue'
import SimpleTaxonomyGraphBuilder from '../utils/simpleTaxonomyGraphBuilder.js'

export default {
  name: 'Dashboard',
  components: {
    AlertCircle,
    RefreshCw,
    Folder,
    RiskScoreBadge,
    VulnerabilityBar,
    TreeNode
  },
  setup() {
    const loading = ref(false)
    const error = ref('')
    const securityData = ref([])
    const expandedNodes = ref(new Set())
    const selectedTreeNode = ref(null)
    const searchQuery = ref('')
    const treeData = ref([])
    const allProjects = ref([])
    const tags = ref([])
    const taxonomiesData = ref([])
    const allTaxonomiesData = ref([])
    const associativeMode = ref(true) // Default to associative mode like graph

    const graphBuilder = new SimpleTaxonomyGraphBuilder()

    // Computed properties for filtered data
    const filteredTreeData = computed(() => {
      if (!searchQuery.value) return treeData.value

      const query = searchQuery.value.toLowerCase()
      const filterNode = (node) => {
        const matchesSearch = node.name.toLowerCase().includes(query)
        const filteredChildren = node.children ? node.children.filter(filterNode) : []

        return {
          ...node,
          children: filteredChildren.length > 0 ? filteredChildren : (matchesSearch ? [] : node.children)
        }
      }

      return treeData.value.map(filterNode).filter(node =>
        node.name.toLowerCase().includes(query) ||
        (node.children && node.children.length > 0)
      )
    })

    const filteredSecurityData = computed(() => {
      if (!selectedTreeNode.value) return securityData.value

      // Find all tags reachable from selected node using same logic as graph
      const reachableTags = findReachableTags(selectedTreeNode.value.id)

      // Filter security data by reachable tags
      return securityData.value.filter(node => {
        // For SecurityNode, check if node matches any reachable tag
        return reachableTags && reachableTags.size > 0 && Array.from(reachableTags).some(tag =>
          node.name.toLowerCase().includes(tag.toLowerCase()) ||
          node.type?.toLowerCase().includes(tag.toLowerCase())
        )
      })
    })

    // Reuse computed properties from original dashboard but with filtered data
    const totalVulnerabilities = computed(() => {
      const data = filteredSecurityData.value
      if (!data || data.length === 0) return 0
      return data.reduce((sum, node) => sum + (node.vulnerabilities || 0), 0)
    })

    const criticalVulns = computed(() => {
      const data = filteredSecurityData.value
      if (!data || data.length === 0) return 0
      return data.reduce((sum, node) => sum + (node.critical || 0), 0)
    })

    const highVulns = computed(() => {
      const data = filteredSecurityData.value
      if (!data || data.length === 0) return 0
      return data.reduce((sum, node) => sum + (node.high || 0), 0)
    })

    const mediumVulns = computed(() => {
      const data = filteredSecurityData.value
      if (!data || data.length === 0) return 0
      return data.reduce((sum, node) => sum + (node.medium || 0), 0)
    })

    const lowVulns = computed(() => {
      const data = filteredSecurityData.value
      if (!data || data.length === 0) return 0
      return data.reduce((sum, node) => sum + (node.low || 0), 0)
    })

    const infoVulns = computed(() => {
      return 0
    })

    const recentVulns = computed(() => {
      return []
    })

    const riskDistribution = computed(() => {
      const data = filteredSecurityData.value
      if (!data || data.length === 0) return []

      const critical = criticalVulns.value
      const high = highVulns.value
      const medium = mediumVulns.value
      const low = lowVulns.value
      const info = infoVulns.value

      const riskTotal = critical + high + medium + low

      const distribution = [
        { range: 'Critical', count: critical, percentage: riskTotal > 0 ? Math.round((critical / riskTotal) * 100) : 0 },
        { range: 'High', count: high, percentage: riskTotal > 0 ? Math.round((high / riskTotal) * 100) : 0 },
        { range: 'Medium', count: medium, percentage: riskTotal > 0 ? Math.round((medium / riskTotal) * 100) : 0 },
        { range: 'Low', count: low, percentage: riskTotal > 0 ? Math.round((low / riskTotal) * 100) : 0 }
      ]

      if (info > 0) {
        distribution.push({ range: 'Info', count: info, percentage: 0 })
      }

      return distribution
    })

    // Helper function to find reachable tags (same as TaxonomyVisualization)
    const findReachableTags = (startNodeId) => {
      if (!startNodeId || !treeData.value || treeData.value.length === 0 || !graphBuilder.edges) return new Set()

      const visited = new Set()
      const queue = [startNodeId]
      const reachableTags = new Set()

      while (queue.length > 0) {
        const currentId = queue.shift()
        if (visited.has(currentId)) continue

        visited.add(currentId)
        reachableTags.add(currentId)

        // Find connected nodes using graph builder's edge structure
        const connectedNodes = treeData.value
          .filter(node => {
            // Check if this node has edges to other nodes
            return graphBuilder.edges && graphBuilder.edges.some(edge =>
              edge.source === currentId || edge.target === currentId
            )
          })
          .map(node => {
            // Return the connected node ID
            const edge = graphBuilder.edges.find(edge =>
              edge.source === currentId ? edge.target : edge.source
            )
            return edge.source === currentId ? edge.target : edge.source
          })

        connectedNodes.forEach(nodeId => {
          if (!visited.has(nodeId)) {
            queue.push(nodeId)
          }
        })
      }

      return reachableTags
    }

    // Tree building function using graph builder data
    const buildTreeFromGraph = (graph) => {
      if (!graph || !graph.nodes) return []

      const nodeMap = new Map()
      const rootNodes = []

      // Create map of all nodes from graph data
      graph.nodes.forEach(node => {
        nodeMap.set(node.id, {
          id: node.id,
          name: node.name,
          type: node.associative ? 'tag' : 'taxonomy', // Distinguish taxonomy nodes from tag nodes
          children: [],
          vulnerabilities: 0, // Will be calculated from security data
          projectsCount: node.projectsCount || 0,
          taxonomy: node.taxonomy,
          associative: node.associative
        })
      })

      // Build tree structure from edges
      graph.edges.forEach(edge => {
        const parent = nodeMap.get(edge.source)
        const child = nodeMap.get(edge.target)

        if (parent && child) {
          parent.children.push(child)
        }
      })

      // Find root nodes (nodes without incoming edges)
      const allTargetIds = new Set(graph.edges.map(edge => edge.target))
      const allSourceIds = new Set(graph.edges.map(edge => edge.source))

      graph.nodes.forEach(node => {
        if (!allTargetIds.has(node.id) && allSourceIds.has(node.id)) {
          rootNodes.push(node.id)
        }
      })

      // Return sorted tree nodes
      return rootNodes.map(nodeId => nodeMap.get(nodeId)).sort((a, b) => {
        // Sort: taxonomy nodes first, then by name
        if (a.type !== b.type) {
          return a.type === 'taxonomy' ? -1 : 1
        }
        return a.name.localeCompare(b.name)
      })
    }

    const relatedProjects = computed(() => {
      if (!selectedTreeNode.value) return []

      // Find all nodes reachable from selected node to root (upward traversal)
      const reachableNodes = findNodesToRoot(selectedTreeNode.value.id)

      // Find all projects that have tags matching any reachable node
      return allProjects.value.filter(project => {
        if (!project.tags || project.tags.length === 0) return false

        return project.tags.some(tag =>
          reachableNodes.has(tag.toLowerCase())
        )
      })
    })

    // Helper function to find all nodes from selected node up to root
    const findNodesToRoot = (startNodeId) => {
      const reachableNodes = new Set()
      const visited = new Set()
      const queue = [startNodeId]

      // First, traverse up to find all parent nodes
      while (queue.length > 0) {
        const currentId = queue.shift()
        if (visited.has(currentId)) continue

        visited.add(currentId)
        reachableNodes.add(currentId)

        // Find parent nodes (nodes that have edges TO current node)
        const parentNodes = treeData.value
          .filter(node => {
            // Check if this node has edges to current node
            return graphBuilder.edges && graphBuilder.edges.some(edge =>
              edge.target === currentId && edge.source !== currentId
            )
          })
          .map(node => {
            // Return parent node ID
            const edge = graphBuilder.edges.find(edge =>
              edge.target === currentId ? edge.source : null
            )
            return edge ? edge.source : null
          })
          .filter(nodeId => nodeId !== null) // Remove null values

        parentNodes.forEach(nodeId => {
          if (!visited.has(nodeId)) {
            queue.push(nodeId)
          }
        })

        // Also traverse down from current node to include children
        const childNodes = treeData.value
          .filter(node => {
            return graphBuilder.edges && graphBuilder.edges.some(edge =>
              edge.source === currentId && edge.target !== currentId
            )
          })
          .map(node => {
            const edge = graphBuilder.edges.find(edge =>
              edge.source === currentId ? edge.target : null
            )
            return edge ? edge.target : null
          })
          .filter(nodeId => nodeId !== null)

        childNodes.forEach(nodeId => {
          if (!visited.has(nodeId)) {
            queue.push(nodeId)
          }
        })
      }

      return reachableNodes
    }

    // Helper function to get total vulnerabilities from project metrics
    const getProjectVulnerabilities = (metrics) => {
      if (!metrics) return 0
      return (metrics.critical || 0) + (metrics.high || 0) + (metrics.medium || 0) + (metrics.low || 0)
    }

    const refreshData = async () => {
      loading.value = true
      error.value = ''

      try {
        // Load all required data
        const [securityResponse, projectsResponse, tagsResponse] = await Promise.all([
          axios.get('/api/aggregate'),
          axios.get('/api/projects'),
          axios.get('/api/tags')
        ])

        securityData.value = securityResponse.data
        allProjects.value = projectsResponse.data
        tags.value = tagsResponse.data

        // Load taxonomies (reuse from TaxonomyVisualization logic)
        const taxonomiesResponse = await axios.get('/api/taxonomies')
        allTaxonomiesData.value = taxonomiesResponse.data
        taxonomiesData.value = associativeMode.value
          ? taxonomiesResponse.data.filter(taxonomy => taxonomy.relations !== undefined)
          : taxonomiesResponse.data

        // Build graph using same logic as TaxonomyVisualization
        const graph = graphBuilder.buildGraph(tagsResponse.data, taxonomiesData.value, null, associativeMode.value)

        // Build tree structure from graph
        treeData.value = buildTreeFromGraph(graph)

        // Auto-expand first few nodes
        if (treeData.value.length > 0) {
          treeData.value.slice(0, 3).forEach(node => expandedNodes.value.add(node.id))
        }
      } catch (err) {
        error.value = err.response?.data?.detail || err.message || 'Failed to load data'
      } finally {
        loading.value = false
      }
    }

    const toggleTreeNode = (nodeId) => {
      if (expandedNodes.value.has(nodeId)) {
        expandedNodes.value.delete(nodeId)
      } else {
        expandedNodes.value.add(nodeId)
      }
    }

    const selectTreeNode = (node) => {
      selectedTreeNode.value = node
    }

    const clearSelection = () => {
      selectedTreeNode.value = null
    }

    const getSeverityColor = (severity) => {
      switch (severity) {
        case 'Critical': return 'bg-red-500'
        case 'High': return 'bg-orange-500'
        case 'Medium': return 'bg-yellow-500'
        case 'Low': return 'bg-green-500'
        case 'Info': return 'bg-gray-500'
        default: return 'bg-blue-500'
      }
    }

    const getRiskBarColor = (range) => {
      switch (range) {
        case 'Critical': return 'bg-orange-500'
        case 'High': return 'bg-red-500'
        case 'Medium': return 'bg-yellow-500'
        case 'Low': return 'bg-green-500'
        case 'Info': return 'bg-gray-500'
        default: return 'bg-blue-500'
      }
    }

    const formatDate = (dateString) => {
      if (!dateString) return 'Unknown'
      return new Date(dateString).toLocaleDateString()
    }

    onMounted(() => {
      refreshData()
    })

    return {
      loading,
      error,
      securityData,
      expandedNodes,
      selectedTreeNode,
      searchQuery,
      treeData,
      filteredTreeData,
      associativeMode,
      relatedProjects,
      refreshData,
      toggleTreeNode,
      selectTreeNode,
      clearSelection,
      totalVulnerabilities,
      criticalVulns,
      highVulns,
      mediumVulns,
      lowVulns,
      infoVulns,
      recentVulns,
      riskDistribution,
      getSeverityColor,
      getRiskBarColor,
      formatDate,
      getProjectVulnerabilities
    }
  }
}
</script>
