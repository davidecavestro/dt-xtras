<template>
  <div class="px-3 py-4 sm:px-0">
    <!-- Security Dashboard -->
    <div class="bg-white dark:bg-gray-800 shadow overflow-hidden sm:rounded-md">
      <div class="flex justify-between items-center mb-4 p-4">
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
          :disabled="isLoading"
          class="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 flex items-center gap-2"
        >
          <RefreshCw v-if="isLoading" class="animate-spin w-4 h-4" />
          <span v-else>Refresh</span>
        </button>
      </div>

      <div v-if="isLoading" class="text-center py-6">
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

      <div v-else-if="!treeData.value || treeData.value.length === 0" class="text-center py-6">
        <div v-if="isLoading" class="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
        <div v-else class="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
        <h3 class="mt-2 text-sm font-medium text-gray-900 dark:text-white">
          {{ isLoading ? 'Loading tree data...' : 'No tree data available' }}
        </h3>
        <p class="mt-1 text-gray-600 dark:text-gray-400">
          {{ isLoading ? 'Please wait while we load your taxonomy data.' : 'Try adjusting your filters or check your connection.' }}
        </p>
      </div>

      <div v-else class="px-4 py-3 sm:px-6">
        <!-- Security Overview -->
        <div v-if="!filteredSecurityData || filteredSecurityData.length === 0" class="bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 rounded-md p-4 mb-4">
          <div class="flex items-center">
            <AlertCircle class="h-5 w-5 text-yellow-400" />
            <div class="ml-3">
              <h3 class="text-sm font-medium text-yellow-800 dark:text-yellow-200">No security data available</h3>
              <p class="text-sm text-yellow-700 dark:text-yellow-300">
                No projects found with security metrics. Try selecting different tree nodes or check if projects have security data.
              </p>
            </div>
          </div>
        </div>

        <!-- Security Overview (only show if security data exists) -->
        <div v-if="filteredSecurityData && filteredSecurityData.length > 0" class="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-3">
          <div class="bg-blue-50 dark:bg-blue-900/20 p-3 rounded-lg">
            <div class="text-center">
              <div class="text-2xl font-bold text-blue-600 dark:text-blue-300">{{ totalVulnerabilities }}</div>
              <div class="text-sm text-blue-600 dark:text-blue-400">Total Vulnerabilities</div>
            </div>
          </div>

          <div class="bg-orange-50 dark:bg-orange-900/20 p-3 rounded-lg">
            <div class="text-center">
              <div class="text-2xl font-bold text-orange-600 dark:text-orange-300">{{ criticalVulns }}</div>
              <div class="text-sm text-orange-600 dark:text-orange-400">Critical</div>
            </div>
          </div>

          <div class="bg-red-50 dark:bg-red-900/20 p-3 rounded-lg">
            <div class="text-center">
              <div class="text-2xl font-bold text-red-600 dark:text-red-300">{{ highVulns }}</div>
              <div class="text-sm text-red-600 dark:text-red-400">High</div>
            </div>
          </div>

          <div class="bg-yellow-50 dark:bg-yellow-900/20 p-3 rounded-lg">
            <div class="text-center">
              <div class="text-2xl font-bold text-yellow-600 dark:text-yellow-300">{{ mediumVulns }}</div>
              <div class="text-sm text-yellow-600 dark:text-yellow-400">Medium</div>
            </div>
          </div>

          <div class="bg-green-50 dark:bg-green-900/20 p-3 rounded-lg">
            <div class="text-center">
              <div class="text-2xl font-bold text-green-600 dark:text-green-300">{{ lowVulns }}</div>
              <div class="text-sm text-green-600 dark:text-green-400">Low</div>
            </div>
          </div>
        </div>
      </div>
    </div>
    <!-- Tree (1/3) + Related Projects (2/3) -->
    <div class="flex flex-col lg:flex-row gap-4 mt-6" style="min-height: 300px;">
      <!-- Tree Panel (1/3) -->
      <div class="lg:w-2/5 bg-white dark:bg-gray-800 shadow overflow-hidden sm:rounded-md flex flex-col">
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
          <div v-if="isLoading" class="text-center py-4">
            <div class="inline-block animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600"></div>
          </div>

          <div v-else-if="treeData.value && treeData.value.length > 0" class="space-y-1" :key="treeData.value.length">
            <TreeNode
              v-for="node in treeData.value"
              :key="node.id"
              :node="node"
              :selected-node="selectedTreeNode.value"
              :expanded-nodes="expandedNodes.value"
              :search-query="searchQuery.value"
              @select="selectTreeNode"
              @toggle="toggleTreeNode"
            />
          </div>
          <div v-else class="text-center py-4 text-gray-500 dark:text-gray-400">
            No tree data available
          </div>
        </div>
      </div>

      <!-- Related Projects (2/3) -->
      <div class="flex-1 bg-white dark:bg-gray-800 shadow overflow-hidden sm:rounded-md flex flex-col">
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
                  <ListIcon class="w-4 h-4" />
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
                  <SquareIcon class="w-4 h-4" />
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
                  <GridIcon class="w-4 h-4" />
                </button>
              </div>
            </div>

            <div class="text-sm text-gray-600 dark:text-gray-400 mb-4">
              <span v-if="selectedTreeNode && selectedTreeNode.name">
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
                      <div class="text-xs text-gray-500 dark:text-gray-400">Version: {{ project.version }}</div>
                      <div v-if="project.tags && project.tags.length > 0" class="text-xs italic text-gray-500 dark:text-gray-400 mt-1">
                        🏷 {{ tags.value.join(', ') }}
                      </div>
                    </div>
                    <div class="text-right">
                      <a
                        :href="buildDTProjectUrl(project.uuid)"
                        target="_blank"
                        rel="noopener noreferrer"
                        class="text-xs text-blue-600 dark:text-blue-400 hover:text-blue-800 dark:hover:text-blue-300 flex items-center"
                        title="View in Dependency-Track"
                      >
                        <svg class="w-3 h-3 mr-1" fill="currentColor" viewBox="0 0 20 20">
                          <path d="M11 3a1 1 0 100 2h2.586l-6.293 6.293a1 1 0 101.414 1.414L15 6.414V9a1 1 0 102 0V4a1 1 0 00-1-1h-3z"/>
                          <path d="M5 5a2 2 0 00-2 2v8a2 2 0 002 2h8a2 2 0 002-2v-3a1 1 0 10-2 0v3H5V7h3a1 1 0 000-2H5z"/>
                        </svg>
                        DT
                      </a>
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
                  :source="paginatedProjects"
                  :row-height="50"
                  :virtual="false"
                  :theme="isDarkMode ? 'darkCompact' : 'compact'"
                  :resize="true"
                  :autoSizeColumn="{ mode: 'autoSizeOnTextOverlap' }"
                  :stretch="true"
                  :pagination="false"
                  class="w-full border-gray-200 dark:border-gray-700"
                  style="height: 100%;"
                  :readonly="true"
                >
                </vue3-datagrid>

                <!-- Pagination for Grid View -->
                <div v-if="relatedProjects.length > 0" class="mt-4">
                  <Pagination
                    :current-page="currentPage"
                    :page-size="pageSize"
                    :total-items="relatedProjects.length"
                    :page-size-options="[10, 20, 50, 100]"
                    @page-change="onPageSizeChanged"
                    @page-size-change="onPageSizeChanged"
                  />
                </div>
              </div>

              <!-- Deck View -->
              <div v-else-if="projectsViewMode === 'deck'" class="h-full overflow-y-auto">
                <div class="grid gap-4 p-4" style="grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));">
                  <ProjectCard
                    v-for="project in paginatedProjects"
                    :key="project.uuid"
                    :project="project"
                    @select="viewProject"
                    @view="viewProject"
                    @security-details="viewSecurityDetails"
                    @analyze="analyzeProject"
                  />
                </div>

                <!-- Pagination for Deck View -->
                <div v-if="relatedProjects.length > 0" class="mt-4">
                  <Pagination
                    :current-page="currentPage"
                    :page-size="pageSize"
                    :total-items="relatedProjects.length"
                    :page-size-options="[6, 12, 24, 48]"
                    @page-change="onPageChanged"
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
import { ref, computed, watch, onMounted, onUnmounted, nextTick, triggerRef } from 'vue'
import { useRouter } from 'vue-router'
import { storeToRefs } from 'pinia'
import { useProjectStore } from '../stores/projects'
import { useTagStore } from '../stores/tags'
import { useGraphStore } from '../stores/graph'
import axios from 'axios'
import TreeNode from './TreeNode.vue'
import TagsCell from './grid-cells/TagsCell.vue'
import DateCell from './grid-cells/DateCell.vue'
import StatusCell from './grid-cells/StatusCell.vue'
import { buildDTProjectUrl, buildDTProjectFindingsUrl } from '../config.js'
import RiskScoreBadge from './RiskScoreBadge.vue'
import VulnerabilityBar from './VulnerabilityBar.vue'
import { AlertCircle, RefreshCw, Folder, FolderOpen, ListIcon, GridIcon, SquareIcon } from 'lucide-vue-next'
import Vue3Datagrid, { VGridVueTemplate } from '@revolist/vue3-datagrid'
import Pagination from './Pagination.vue'
import ProjectCard from './ProjectCard.vue'
import NameCell from './grid-cells/NameCell.vue'

export default {
  name: 'Dashboard',
  components: {
    AlertCircle,
    RefreshCw,
    Folder,
    FolderOpen,
    ListIcon,
    GridIcon,
    SquareIcon,
    Vue3Datagrid,
    Pagination,
    ProjectCard,
    RiskScoreBadge,
    VulnerabilityBar,
    TreeNode,
    TagsCell,
    DateCell,
    StatusCell,
    NameCell
  },
  setup() {
    const router = useRouter()

    // Use stores
    const projectStore = useProjectStore()
    const tagStore = useTagStore()
    const graphStore = useGraphStore()
    const { edges, graphData, nodes, rootNodes } = storeToRefs(graphStore)
    const { isLoading, error } = storeToRefs(projectStore)
    const { tags } = storeToRefs(tagStore)

    // Local state
    const expandedNodes = ref(new Set())
    const treeData = ref([])
    const searchQuery = ref('')
    const selectedTreeNode = ref(null)

    // Initialize data on component mount
    onMounted(() => {
      refreshData()
    })

    // Methods from stores
    const { loadProjects } = projectStore
    const { loadTags } = tagStore
    const {
      loadGraph: loadGraphAction,
      findReachableNodes,
    } = graphStore

    const setAssociativeMode = (isAssociative) => {
      graphStore.setAssociativeMode(isAssociative);
    };

    const associativeMode = ref(true) // Default to associative mode like graph
    const projectsViewMode = ref('list') // 'list', 'grid', or 'deck'

    // Pagination state
    const currentPage = ref(1)
    const pageSize = ref(20)

    // Local state for reachable nodes
    const allReachableNodes = ref(new Set())

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
        if (node.name.toLowerCase().includes(query)) return true

        if (node.children && node.children.length > 0) {
          node.children = node.children.map(filterNode)
          return node.children.some(child => child.name.toLowerCase().includes(query))
        }

        return false
      }

      return treeData.value.map(filterNode).filter(node =>
        node.name.toLowerCase().includes(query) ||
        (node.children && node.children.length > 0)
      )
    })

    const filteredSecurityData = computed(() => {
      const related = relatedProjects.value

      return related.filter(project => project.tags && project.tags.length > 0)
        .map(project => ({
          name: project.name,
          type: 'project',
          vulnerabilities: getProjectVulnerabilities(project.metrics),
          critical: project.metrics.critical,
          high: project.metrics.high,
          medium: project.metrics.medium,
          low: project.metrics.low,
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
      const total = critical + high + medium + low

      if (total === 0) return []

      return [
        { level: 'Critical', count: critical, percentage: (critical / total) * 100 },
        { level: 'High', count: high, percentage: (high / total) * 100 },
        { level: 'Medium', count: medium, percentage: (medium / total) * 100 },
        { level: 'Low', count: low, percentage: (low / total) * 100 }
      ]

      return distribution
    })

    // Helper function to find reachable tags (same as TaxonomyVisualization)
    const findReachableTags = (startNodeId) => {
      if (!startNodeId || !graphData.value || !graphData.value.nodes || !edges.value) return new Set()

      const visited = new Set()
      const queue = [startNodeId]
      const reachableTags = new Set()

      while (queue.length > 0) {
        const currentId = queue.shift()
        if (visited.has(currentId)) continue

        visited.add(currentId)
        reachableTags.add(currentId)

        // Find connected nodes using graph builder's edge structure
        const connectedNodes = edges.value
          .filter(edge =>
            (edge.source === currentId && edge.target !== currentId) || (edge.target === currentId && edge.source !== currentId)
          )
          .map(edge =>
            edge.target === currentId ? edge.source : edge.target
          )
          .filter(nodeId => nodeId !== null)

        connectedNodes.forEach(nodeId => {
          if (!visited.has(nodeId)) {
            queue.push(nodeId)
          }
        })
      }

      return reachableTags
    }

    // Tree building function using taxonomy data
    const buildTreeFromTaxonomies = (taxonomies) => {
      if (!taxonomies || !taxonomies.nodes) return []

      const nodeMap = new Map()
      const rootNodesArray = []

      // Create map of all nodes from taxonomy data
      taxonomies.nodes.forEach(node => {
        nodeMap.set(node.id, {
          id: node.id,
          name: node.name,
          type: 'taxonomy', // All taxonomy nodes are taxonomy type
          children: [],
          vulnerabilities: 0, // Will be calculated from security data
          projectsCount: node.projectsCount || 0,
        })
      })

      // Build tree structure from edges
      const edgeMap = new Map()
      taxonomies.edges.forEach(edge => {
        // Deduplicate edges by using the edge ID as key
        if (!edgeMap.has(edge.id)) {
          edgeMap.set(edge.id, edge)
        }
      })

      // Find root nodes (nodes without incoming edges)
      const allTargetIds = new Set(taxonomies.edges.map(edge => edge.target))
      const allSourceIds = new Set(taxonomies.edges.map(edge => edge.source))

      taxonomies.nodes.forEach(node => {
        if (!allTargetIds.has(node.id) && allSourceIds.has(node.id)) {
          rootNodesArray.push(node.id)
        }
      })

      // Return sorted tree nodes
      return rootNodesArray.map(nodeId => nodeMap.get(nodeId)).sort((a, b) => {
        // Sort: taxonomy nodes first, then by name
        if (a.type !== b.type) {
          return a.type === 'taxonomy' ? -1 : 1
        }
        return a.name.localeCompare(b.name)
      })
    }

    // Tree building function using graph builder data
    const buildTreeFromGraph = (graph) => {
      if (!graph || !nodes.value) return []

      const nodeMap = new Map()
      const rootNodesArray = []

      // Create map of all nodes from graph data
      nodes.value.forEach(node => {
        nodeMap.set(node.id, {
          id: node.id,
          name: node.name,
          type: node.associative ? 'tag' : 'taxonomy', // Distinguish taxonomy nodes from tag nodes
          children: [],
          vulnerabilities: 0, // Will be calculated from security data
          projectsCount: node.projectsCount || 0,
        })
      })

      // Build tree structure from edges
      edges.value.forEach(edge => {
        const parentNode = nodeMap.get(edge.source)
        const childNode = nodeMap.get(edge.target)

        if (parentNode && childNode) {
          parentNode.children.push(childNode)
        }
      })

      // Find root nodes (nodes without incoming edges)
      const allTargetIds = new Set(edges.value.map(edge => edge.target))
      const allSourceIds = new Set(edges.value.map(edge => edge.source))

      nodes.value.forEach(node => {
        if (!allTargetIds.has(node.id) && allSourceIds.has(node.id)) {
          rootNodesArray.push(node.id)
        }
      })

      // Return sorted tree nodes
      return rootNodesArray.map(nodeId => nodeMap.get(nodeId)).sort((a, b) => {
        // Sort: taxonomy nodes first, then by name
        if (a.type !== b.type) {
          return a.type === 'taxonomy' ? -1 : 1
        }
        return a.name.localeCompare(b.name)
      })
    }

    const relatedProjects = computed(() => {
      if (!treeData.value || treeData.value.length === 0) return []

      if (!selectedTreeNode.value) {
        return projectStore.projects
      }

      const reachableNodes = findReachableTags(selectedTreeNode.value.id)

      return projectStore.projects.filter(project => {
        if (!project.tags || project.tags.length === 0) {
          return false
        }

        return project.tags.some(tag =>
          reachableNodes.has(tag)
        )
      })
    })

    // Helper function to update all reachable nodes
    const updateAllReachableNodes = async () => {
      const allReachable = new Set()

      // Get all root nodes and find all reachable nodes from them
      if (rootNodes.value && rootNodes.value.length > 0) {
        rootNodes.value.forEach(rootNode => {
          const reachable = findReachableTags(rootNode.id)
          reachable.forEach(nodeId => allReachable.add(nodeId))
        })
      }

      allReachableNodes.value = allReachable;
    };

    // Helper function to get total vulnerabilities from project metrics
    const getProjectVulnerabilities = (metrics) => {
      if (!metrics) return 0
      return (metrics.critical || 0) + (metrics.high || 0) + (metrics.medium || 0) + (metrics.low || 0)
    }

    // Load graph
    const loadGraph = async () => {
      await graphStore.loadGraph();
    };

    // Helper function to expand all nodes
    const expandAll = (nodes) => {
      const expanded = new Set()
      nodes.forEach(node => expanded.add(node.id))
      expandedNodes.value = expanded
    };

    const refreshData = async () => {
      isLoading.value = true;
      error.value = '';

      try {
        // Load data using stores
        await Promise.all([
          loadProjects(),
          tagStore.loadTags()
        ]);

        // Load graph data with associative mode
        await loadGraphAction({
          rootTaxonomy: null,
          associativeMode: associativeMode.value
        });

        // Build tree structure from graph
        treeData.value = buildTreeFromGraph(graphData.value);

        // Update all reachable nodes for the computed property
        await updateAllReachableNodes();
        if (treeData.value) {
          expandAll(treeData.value);
        }
      } catch (err) {
        error.value = err.message || 'Failed to load data';
        throw err;
      } finally {
        isLoading.value = false;
      }
    };

    const toggleTreeNode = (nodeId) => {
      if (expandedNodes.value.has(nodeId)) {
        expandedNodes.value.delete(nodeId);
      } else {
        expandedNodes.value.add(nodeId);
      }
    };

    const selectTreeNode = (node) => {
      if (node && node.id) {
        selectedTreeNode.value = node
      }
    }

    const clearSelection = () => {
      selectedTreeNode.value = null;
    };

    const getSeverityColor = (severity) => {
      switch (severity) {
        case 'Critical': return 'bg-red-500';
        case 'High': return 'bg-orange-500';
        case 'Medium': return 'bg-yellow-500';
        case 'Low': return 'bg-green-500';
        case 'Info': return 'bg-gray-500';
        default: return 'bg-blue-500';
      }
    };

    const getRiskBarColor = (range) => {
      switch (range) {
        case 'Critical': return 'bg-orange-500';
        case 'High': return 'bg-red-500';
        case 'Medium': return 'bg-yellow-500';
        case 'Low': return 'bg-green-500';
        case 'Info': return 'bg-gray-500';
        default: return 'bg-blue-500';
      }
    };

    const formatDate = (dateString) => {
      if (!dateString) return 'Unknown';
      return new Date(dateString).toLocaleDateString();
    };

    // Project action handlers
    const viewProject = (project) => {
      // Navigate to project details page
      window.open(buildDTProjectUrl(project.uuid), '_blank');
    };

    const viewSecurityDetails = (project) => {
      // Navigate to security details page
      window.open(buildDTProjectFindingsUrl(project.uuid), '_blank');
    };

    const analyzeProject = (project) => {
      // Navigate to project analysis page
      window.open(buildDTProjectFindingsUrl(project.uuid), '_blank');
    };

    // Pagination handler
    const onPageChanged = (page) => {
      currentPage.value = page;
    };

    const onPageSizeChanged = (newPageSize) => {
      pageSize.value = newPageSize;
      currentPage.value = 1; // Reset to first page when changing page size
    };

    // Computed property for paginated projects
    const paginatedProjects = computed(() => {
      // Defensive check to prevent undefined access
      if (!currentPage.value || !pageSize.value || !relatedProjects.value) {
        return []
      }
      const start = (currentPage.value - 1) * pageSize.value
      const end = start + pageSize.value
      return relatedProjects.value.slice(start, end)
    })

    return {
      // Graph data
      graphData,
      isLoading,
      error,
      nodes,
      edges,
      rootNodes,

      // Tag data
      tags: tags.value,

      // Tree data
      treeData,
      filteredTreeData,
      expandedNodes,
      searchQuery,
      selectedTreeNode,
      allReachableNodes,

      // Project data
      relatedProjects,
      paginatedProjects,
      filteredSecurityData,
      totalVulnerabilities,
      criticalVulns,
      highVulns,
      mediumVulns,
      lowVulns,
      riskDistribution,

      // UI state
      associativeMode,
      projectsViewMode,

      // Pagination
      currentPage,
      pageSize,

      // Methods
      refreshData,
      selectTreeNode,
      findReachableTags,
      setAssociativeMode,
      buildTreeFromGraph,
      buildTreeFromTaxonomies,
      updateAllReachableNodes,
      expandAll,
      onPageChanged,
      onPageSizeChanged
    }
  }
}
</script>
