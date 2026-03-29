<template>
  <div class="px-4 py-6 sm:px-0">
    <!-- Security Dashboard -->
    <div class="bg-white dark:bg-gray-800 shadow overflow-hidden sm:rounded-md lg:col-span-3">
      <div class="flex justify-between items-center mb-6 p-6">
        <div>
          <h2 class="text-2xl font-bold text-gray-900 dark:text-white">Security Dashboard</h2>
          <p v-if="selectedTreeNode" class="text-sm text-gray-600 dark:text-gray-400 mt-1">
            Filtered by: {{ selectedTreeNode.name }} ({{ selectedTreeNode.type }})
          </p>
          <p v-else class="text-sm text-gray-600 dark:text-gray-400 mt-1">
            Showing all projects reachable from any root taxonomy
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

      <div v-else-if="(!treeData || treeData.length === 0) || (!filteredSecurityData || filteredSecurityData.length === 0)" class="text-center py-8">
        <div v-if="loading" class="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
        <div v-else class="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
        <h3 class="mt-2 text-sm font-medium text-gray-900 dark:text-white">
          {{ loading ? 'Loading security data...' : 'No security data available' }}
        </h3>
        <p class="mt-1 text-gray-600 dark:text-gray-400">
          {{ loading ? 'Please wait while we load your security data.' : 'Try adjusting your filters or check your connection.' }}
        </p>
      </div>

      <div v-else class="px-4 py-5 sm:px-6">
        <!-- Security Overview -->
        <div class="flex justify-between items-center mb-6">
          <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
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
          </div>
        </div>
      </div>
    </div>
    <!-- Tree (1/3) + Related Projects (2/3) -->
    <div class="flex flex-col lg:flex-row gap-6 mt-6" style="height: calc(100vh - 400px); min-height: 400px;">
      <!-- Tree Panel (1/3) -->
      <div class="flex-1 lg:flex-none lg:w-1/3 bg-white dark:bg-gray-800 shadow overflow-hidden sm:rounded-md flex flex-col">
        <div class="p-4 border-b border-gray-200 dark:border-gray-700 flex-shrink-0">
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

        <div class="flex-1 overflow-y-auto p-4">
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
      </div>

      <!-- Related Projects (2/3) -->
      <div class="flex-1 lg:flex-1 bg-white dark:bg-gray-800 shadow overflow-hidden sm:rounded-md flex flex-col">
        <div class="p-4 flex-shrink-0">
          <!-- Related Projects -->
          <div>
            <div class="flex justify-between items-center mb-4">
              <h3 class="text-lg leading-6 font-medium text-gray-900 dark:text-white">Related Projects</h3>

              <!-- View Mode Controls -->
              <div class="flex items-center space-x-2">
                <button
                  @click="projectsViewMode = 'list'"
                  :class="[
                    'px-3 py-1 text-sm rounded-md',
                    projectsViewMode === 'list'
                      ? 'bg-blue-600 text-white'
                      : 'bg-gray-200 text-gray-700 dark:bg-gray-700 dark:text-gray-300'
                  ]"
                >
                  List
                </button>
                <button
                  @click="projectsViewMode = 'grid'"
                  :class="[
                    'px-3 py-1 text-sm rounded-md',
                    projectsViewMode === 'grid'
                      ? 'bg-blue-600 text-white'
                      : 'bg-gray-200 text-gray-700 dark:bg-gray-700 dark:text-gray-300'
                  ]"
                >
                  Grid
                </button>
                <button
                  @click="projectsViewMode = 'deck'"
                  :class="[
                    'px-3 py-1 text-sm rounded-md',
                    projectsViewMode === 'deck'
                      ? 'bg-blue-600 text-white'
                      : 'bg-gray-200 text-gray-700 dark:bg-gray-700 dark:text-gray-300'
                  ]"
                >
                  Deck
                </button>
              </div>
            </div>

            <div class="text-sm text-gray-600 dark:text-gray-400 mb-4">
              <span v-if="selectedTreeNode">
                {{ relatedProjects.length }} projects found for "{{ selectedTreeNode.name }}"
              </span>
              <span v-else>
                {{ relatedProjects.length }} projects found (all projects reachable from any root taxonomy)
              </span>
            </div>

            <!-- Projects Display -->
            <div class="flex-1 overflow-hidden">
              <div v-if="relatedProjects.length === 0" class="text-center py-8 h-full flex items-center justify-center">
                <div>
                  <FolderOpen class="mx-auto h-12 w-12 text-gray-400" />
                  <h3 class="mt-2 text-sm font-medium text-gray-900 dark:text-white">No related projects found</h3>
                  <p class="mt-1 text-sm text-gray-500 dark:text-gray-400">
                    Try selecting a different node or check your connections.
                  </p>
                </div>
              </div>

              <!-- List View -->
              <div v-else-if="projectsViewMode === 'list'" class="h-full overflow-y-auto space-y-2 p-4">
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
                      No Vulnerabilities
                    </span>
                  </div>
                </div>
              </div>
              <!-- Grid View -->
              <div v-else-if="projectsViewMode === 'grid'" class="h-full overflow-y-auto">
                <vue3-datagrid
                  :columns="gridColumns"
                  :source="relatedProjects"
                  :row-height="50"
                  :virtual="true"
                  :page-size="50"
                  :page="1"
                  :total="relatedProjects.length"
                  :theme="isDarkMode ? 'darkCompact' : 'compact'"
                  :resize="true"
                  :autoSizeColumn="{ mode: 'autoSizeOnTextOverlap' }"
                  :stretch="true"
                  class="w-full border-gray-200 dark:border-gray-700"
                  style="height: 100%;"
                >
                </vue3-datagrid>
              </div>

              <!-- Deck View -->
              <div v-else-if="projectsViewMode === 'deck'" class="h-full overflow-y-auto">
                <div class="px-4 py-5 sm:px-6">
                  <h3 class="text-lg leading-6 font-medium text-gray-900 dark:text-white">
                    Projects ({{ relatedProjects.length }} total)
                  </h3>
                  <p class="mt-1 max-w-2xl text-sm text-gray-500 dark:text-gray-400">
                    Software projects being tracked
                  </p>
                </div>

                <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 p-4">
                  <ProjectCard
                    v-for="project in relatedProjects"
                    :key="project.uuid"
                    :project="project"
                    @select="viewProject"
                    @view="viewProject"
                    @security-details="viewSecurityDetails"
                    @analyze="analyzeProject"
                  />
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
import { ref, onMounted, computed, watch, onUnmounted } from 'vue'
import { AlertCircle, RefreshCw, Folder, FolderOpen } from 'lucide-vue-next'
import axios from 'axios'
import Vue3Datagrid, { VGridVueTemplate } from '@revolist/vue3-datagrid'
import RiskScoreBadge from './RiskScoreBadge.vue'
import VulnerabilityBar from './VulnerabilityBar.vue'
import TreeNode from './TreeNode.vue'
import NameCell from './grid-cells/NameCell.vue'
import StatusCell from './grid-cells/StatusCell.vue'
import TagsCell from './grid-cells/TagsCell.vue'
import DateCell from './grid-cells/DateCell.vue'
import ProjectCard from './ProjectCard.vue'
import SimpleTaxonomyGraphBuilder from '../utils/simpleTaxonomyGraphBuilder.js'

export default {
  name: 'Dashboard',
  components: {
    AlertCircle,
    RefreshCw,
    Folder,
    FolderOpen,
    Vue3Datagrid,
    ProjectCard,
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
    const projectsViewMode = ref('list') // 'list', 'grid', or 'deck'

    const graphBuilder = new SimpleTaxonomyGraphBuilder()

    // Grid columns for projects grid view
    const gridColumns = computed(() => [
      {
        prop: 'name',
        name: 'Project Name',
        width: 200,
        sortable: true,
        cellTemplate: VGridVueTemplate(NameCell)
      },
      {
        prop: 'version',
        name: 'Version',
        width: 100,
        sortable: true
      },
      {
        prop: 'active',
        name: 'Status',
        width: 80,
        sortable: true,
        cellTemplate: VGridVueTemplate(StatusCell)
      },
      {
        prop: 'lastActivity',
        name: 'Last Activity',
        width: 120,
        sortable: true,
        cellTemplate: VGridVueTemplate(DateCell)
      },
      {
        prop: 'tags',
        name: 'Tags',
        width: 250,
        sortable: false,
        cellTemplate: VGridVueTemplate(TagsCell)
      }
    ])

    // Dark mode detection for grid
    const isDarkMode = ref(document.documentElement.classList.contains('dark'))
    const observer = new MutationObserver(() => {
      isDarkMode.value = document.documentElement.classList.contains('dark')
    })

    onMounted(() => {
      observer.observe(document.documentElement, {
        attributes: true,
        attributeFilter: ['class']
      })
    })

    onUnmounted(() => {
      observer.disconnect()
    })

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
      // Get related projects for the selected node (or all projects if no node selected)
      const related = relatedProjects.value

      // If no related projects, return empty array
      if (!related || related.length === 0) return []

      // Extract security data from related projects only
      return related
        .filter(project => project.metrics)
        .map(project => ({
          name: project.name,
          type: 'project',
          vulnerabilities: getProjectVulnerabilities(project.metrics),
          critical: project.metrics.critical || 0,
          high: project.metrics.high || 0,
          medium: project.metrics.medium || 0,
          low: project.metrics.low || 0,
          metrics: project.metrics,
          uuid: project.uuid
        }))
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
      // Wait for tree data to be available
      if (!treeData.value || treeData.value.length === 0) return []

      if (!selectedTreeNode.value) {
        // When no node selected, return all projects reachable from any root
        const allReachableNodes = findAllReachableFromRoots()

        return allProjects.value.filter(project => {
          if (!project.tags || project.tags.length === 0) return false
          return project.tags.some(tag =>
            allReachableNodes.has(tag.toLowerCase())
          )
        })
      }

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

    // Helper function to find all nodes reachable from any root
    const findAllReachableFromRoots = () => {
      // Build graph from current data
      const graph = graphBuilder.buildGraph(tags.value, taxonomiesData.value, null, associativeMode.value)

      if (!graph) return new Set()

      // Handle different graph structures
      let nodes = []
      let edges = []

      if (Array.isArray(graph.nodes)) {
        nodes = graph.nodes
      } else if (graph.nodes && typeof graph.nodes === 'object') {
        // Check if it's a Map
        if (graph.nodes instanceof Map) {
          nodes = Array.from(graph.nodes.values())
        } else {
          // If nodes is a regular object, try to get values
          nodes = Object.values(graph.nodes)
        }
      } else {
        return new Set()
      }

      if (Array.isArray(graph.edges)) {
        edges = graph.edges
      } else if (graph.edges && typeof graph.edges === 'object') {
        // Check if it's a Map
        if (graph.edges instanceof Map) {
          edges = Array.from(graph.edges.values())
        } else {
          // If edges is a regular object, try to get values
          edges = Object.values(graph.edges)
        }
      } else {
        return new Set()
      }

      if (nodes.length === 0) return new Set()

      const allReachableNodes = new Set()
      const visited = new Set()

      // Find all root nodes
      const allTargetIds = new Set(edges.map(edge => edge.target))
      const allSourceIds = new Set(edges.map(edge => edge.source))

      const rootNodes = nodes
        .filter(node => !allTargetIds.has(node.id) && allSourceIds.has(node.id))
        .map(node => node.id)

      // If no root nodes found, try alternative approach - use all nodes as starting points
      const startNodes = rootNodes.length > 0 ? rootNodes : nodes.map(n => n.id)

      // Start BFS from all root nodes (or all nodes if no roots found)
      const queue = [...startNodes]

      while (queue.length > 0) {
        const currentId = queue.shift()

        if (visited.has(currentId)) continue
        visited.add(currentId)
        allReachableNodes.add(currentId)

        // Find all child nodes
        const childNodes = edges
          .filter(edge => edge.source === currentId)
          .map(edge => edge.target)
          .filter(nodeId => nodeId !== null)

        childNodes.forEach(nodeId => {
          if (!visited.has(nodeId)) {
            queue.push(nodeId)
          }
        })
      }

      return allReachableNodes
    }

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

    // Project action handlers
    const viewProject = (project) => {
      console.log('View project:', project.name)
      // TODO: Navigate to project details page
    }

    const viewSecurityDetails = (project) => {
      console.log('View security details:', project.name)
      // TODO: Navigate to security details page
    }

    const analyzeProject = (project) => {
      console.log('Analyze project:', project.name)
      // TODO: Navigate to project analysis page
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
      filteredSecurityData,
      associativeMode,
      relatedProjects,
      projectsViewMode,
      gridColumns,
      isDarkMode,
      refreshData,
      toggleTreeNode,
      selectTreeNode,
      clearSelection,
      viewProject,
      viewSecurityDetails,
      analyzeProject,
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
