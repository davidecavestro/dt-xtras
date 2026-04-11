<template>
  <div class="px-3 py-4 sm:px-0">
    <!-- Security Dashboard -->
    <div class="bg-white dark:bg-gray-800 shadow overflow-hidden sm:rounded-md">
      <div class="flex justify-between items-center mb-4 p-4">
        <div>
          <h2 class="text-2xl font-bold text-gray-900 dark:text-white">Security Dashboard</h2>
          <div v-if="selectedTreeNode" class="flex items-center gap-2 mt-1">
            <span class="text-sm text-gray-600 dark:text-gray-400">Selected:</span>
            <span class="font-mono text-sm text-gray-900 dark:text-white">{{ selectedTreeNode.name }}</span>
            <span
              class="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium border"
              :style="getTaxonomyBadgeStyleForNode(selectedTreeNode)"
            >
              {{ getTaxonomyNameForNode(selectedTreeNode) }}
            </span>
          </div>
          <p v-else class="text-sm text-gray-600 dark:text-gray-400 mt-1">
            Showing all projects reachable from any root taxonomy
          </p>
        </div>
        <button
          @click="refreshData"
          :disabled="shouldShowLoading"
          class="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 flex items-center gap-2"
        >
          <RefreshCw v-if="shouldShowLoading" class="animate-spin w-4 h-4" />
          <span v-else>Refresh</span>
        </button>
      </div>

      <div v-if="shouldShowLoading" class="text-center py-6">
        <div class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        <p class="mt-2 text-gray-600 dark:text-gray-400">Loading dashboard data...</p>
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

      <div v-else-if="!treeData || treeData.length === 0" class="text-center py-6">
        <div v-if="shouldShowLoading" class="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
        <div v-else class="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
        <h3 class="mt-2 text-sm font-medium text-gray-900 dark:text-white">
          {{ shouldShowLoading ? 'Loading tree data...' : 'No tree data available' }}
        </h3>
        <p class="mt-1 text-gray-600 dark:text-gray-400">
          {{ shouldShowLoading ? 'Please wait while we load your taxonomy data.' : 'Try adjusting your filters or check your connection.' }}
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
          <div v-if="shouldShowLoading" class="text-center py-4">
            <div class="inline-block animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600"></div>
          </div>

          <div v-else-if="treeData && treeData.length > 0" class="space-y-1" :key="treeData.length">
            <TreeNode
              v-for="node in treeData"
              :key="node.id"
              :node="node"
              :selected-node="selectedTreeNode"
              :expanded-nodes="expandedNodes"
              :search-query="searchQuery"
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
                <!-- <button
                  @click="projectsViewMode = 'grid'"
                  :class="[
                    'px-3 py-1 text-sm rounded-md',
                    projectsViewMode === 'grid'
                      ? 'bg-blue-600 text-white'
                      : 'bg-gray-200 text-gray-700 dark:bg-gray-700 dark:text-gray-300'
                  ]"
                >
                  <GridIcon class="w-4 h-4" />
                </button> -->
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

            <!-- Pagination Controls -->
            <div v-if="relatedProjects.length > pageSize" class="flex items-center justify-between mb-4 px-4">
              <div class="flex items-center space-x-4">
                <div class="text-sm text-gray-700 dark:text-gray-300">
                  Showing {{ paginatedProjects.length }} of {{ relatedProjects.length }} projects
                </div>
                <div class="flex items-center space-x-2">
                  <label class="text-sm text-gray-600 dark:text-gray-400">Page size:</label>
                  <select
                    v-model="pageSize"
                    @change="onPageSizeChanged(pageSize)"
                    class="text-sm border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-white px-2 py-1"
                  >
                    <option :value="10">10</option>
                    <option :value="20">20</option>
                    <option :value="50">50</option>
                    <option :value="100">100</option>
                  </select>
                </div>
              </div>
              <div class="flex items-center space-x-2">
                <button
                  @click="onPageChanged(currentPage - 1)"
                  :disabled="currentPage === 1"
                  class="px-3 py-1 text-sm border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
                  </svg>
                </button>

                <!-- Page Numbers -->
                <div class="flex items-center space-x-1">
                  <button
                    v-for="page in Math.min(5, Math.ceil(relatedProjects.length / pageSize))"
                    :key="page"
                    @click="onPageChanged(page)"
                    :class="[
                      'px-3 py-1 text-sm border rounded-md',
                      page === currentPage
                        ? 'bg-blue-600 text-white border-blue-600'
                        : 'bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-300 border-gray-300 dark:border-gray-600 hover:bg-gray-50 dark:hover:bg-gray-700'
                    ]"
                  >
                    {{ page }}
                  </button>
                  <span v-if="Math.ceil(relatedProjects.length / pageSize) > 5" class="px-2 text-gray-500">...</span>
                  <button
                    v-if="Math.ceil(relatedProjects.length / pageSize) > 5"
                    @click="onPageChanged(Math.ceil(relatedProjects.length / pageSize))"
                    class="px-3 py-1 text-sm border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700"
                  >
                    {{ Math.ceil(relatedProjects.length / pageSize) }}
                  </button>
                </div>

                <button
                  @click="onPageChanged(currentPage + 1)"
                  :disabled="currentPage >= Math.ceil(relatedProjects.length / pageSize)"
                  class="px-3 py-1 text-sm border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
                  </svg>
                </button>
              </div>
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
              <div v-else-if="projectsViewMode === 'list'" class="h-full flex flex-col">
                <div class="flex-1 overflow-y-auto space-y-2 p-4">
                  <div
                    v-for="project in paginatedProjects"
                    :key="project.uuid"
                    class="p-3 bg-white dark:bg-gray-800 rounded hover:bg-gray-100 dark:hover:bg-gray-600 cursor-pointer border border-gray-200 dark:border-gray-600"
                  >
                    <div class="flex justify-between items-start mb-2">
                      <div class="flex-1">
                        <div class="text-sm font-medium text-gray-900 dark:text-white">{{ project.name }}</div>
                        <div class="text-xs text-gray-500 dark:text-gray-400">Version: {{ project.version }}</div>
                        <div v-if="project.tags && project.tags.length > 0" class="text-xs italic text-gray-500 dark:text-gray-400 mt-1">
                          🏷 {{ project.tags.map( tag => tag.name).join(', ') }}
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

              </div>
              <!-- Grid View -->
              <div v-else-if="projectsViewMode === 'grid'" class="h-full flex flex-col">

                <div class="flex-1 overflow-y-auto">
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
                </div>
              </div>

              <!-- Deck View -->
              <div v-else-if="projectsViewMode === 'deck'" class="h-full flex flex-col">

                <div class="flex-1 overflow-y-auto">
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
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { storeToRefs } from 'pinia'
import { useProjectStore } from '../stores/projects'
import { useTagStore } from '../stores/tags'
import { useGraphStore } from '../stores/graph'
import { useTaxonomyStore } from '../stores/taxonomies'
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
    const taxonomyStore = useTaxonomyStore()
    const { edges, graphData, nodes, rootNodes, loading: graphLoading } = storeToRefs(graphStore)
    const { isLoading: projectLoading, error, projects } = storeToRefs(projectStore)
    const { tags, isLoading: tagLoading } = storeToRefs(tagStore)
    const { taxonomies, loading: taxonomiesLoading } = storeToRefs(taxonomyStore)
    const { getTaxonomyBadgeStyle, getTaxonomyByName } = taxonomyStore

    // Coordinated loading state - wait for all stores to be ready
    const isDataReady = computed(() => {
      try {
        return (
          !projectLoading.value &&
          !tagLoading.value &&
          !graphLoading.value &&
          !taxonomiesLoading.value &&
          projects.value && projects.value.length > 0 &&
          nodes.value && nodes.value.length > 0 &&
          edges.value && edges.value.length > 0
        );
      } catch (err) {
        console.warn('Error in isDataReady computed:', err);
        return false;
      }
    })

    const shouldShowLoading = computed(() => !isDataReady.value)

    // Helper function to get taxonomy name for tree nodes
    const getTaxonomyNameForNode = (node) => {
      if (!node) return 'unknown'

      let taxonomy = getTaxonomyByNode(node)

      // If still not found, return 'unknown'
      return taxonomy ? taxonomy.name : 'unknown'
    }

    const getTaxonomyByNode = (node) => {
      if (!node) return {}

      // Try to find taxonomy sorted by priority by matching regex pattern
      return taxonomies.value
        .filter(t => node.name.match(new RegExp(t.regex_pattern)))
        .sort((a, b) => a.priority - b.priority)[0]
    }

    // Helper function to get taxonomy badge style for tree nodes
    const getTaxonomyBadgeStyleForNode = (node) => {
      if (!node) return {}

      // Try to find taxonomy sorted by priority by matching regex pattern
      let taxonomy = getTaxonomyByNode(node)

      // If still not found, use a default color
      if (!taxonomy) {
        return {
          backgroundColor: '#6b728020',
          color: '#6b7280',
          borderColor: '#6b728040'
        }
      }

      return getTaxonomyBadgeStyle(taxonomy)
    }

    // Local state
    const expandedNodes = ref(new Set())
    const treeData = ref([])
    const searchQuery = ref('')
    const selectedTreeNode = ref(null)


    // Initialize data on component mount
    onMounted(() => {
      refreshData()
    })

    // Methods from stores - call directly on store instances to maintain context
    // const { loadProjects } = projectStore
    // const { loadTags } = tagStore
    // const { findReachableNodes } = graphStore

    const setAssociativeMode = (isAssociative) => {
      graphStore.setAssociativeMode(isAssociative);
    };

    const associativeMode = ref(true) // Default to associative mode like graph
    const projectsViewMode = ref('deck') // 'list', 'grid', or 'deck'

    // Uniform pagination constants
    const DEFAULT_PAGE_SIZE = 20
    const PAGE_SIZE_OPTIONS = [10, 20, 50, 100]

    // Pagination state
    const currentPage = ref(1)
    const pageSize = ref(DEFAULT_PAGE_SIZE)

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
      if (!treeData.value || !Array.isArray(treeData.value)) return []
      if (!searchQuery.value) return treeData.value

      const query = searchQuery.value.toLowerCase()
      const filterNode = (node) => {
        if (!node || !node.name) return false
        if (node.name.toLowerCase().includes(query)) return true

        if (node.children && Array.isArray(node.children) && node.children.length > 0) {
          node.children = node.children.map(filterNode)
          return node.children.some(child => child && child.name && child.name.toLowerCase().includes(query))
        }

        return false
      }

      return treeData.value.map(filterNode).filter(node =>
        node && node.name && node.name.toLowerCase().includes(query) ||
        (node.children && Array.isArray(node.children) && node.children.length > 0)
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

    // Helper function to find reachable tags using tree structure
    const findReachableTags = (startNodeId) => {
      console.log('findReachableTags called with startNodeId:', startNodeId);
      console.log('treeData available:', !!treeData.value, 'length:', treeData.value?.length);

      if (!startNodeId || !treeData.value || treeData.value.length === 0) return new Set()

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
        reachableTags.add(currentId)

        // Find the current node in the tree
        const currentNode = findNodeInTree(treeData.value, currentId)
        if (currentNode && currentNode.children) {
          // Add all children to queue (downward traversal)
          currentNode.children.forEach(child => {
            if (!visited.has(child.id)) {
              queue.push(child.id)
            }
          })
        }

        // Also find parent nodes (upward traversal)
        const findParent = (nodes, targetId, parent = null) => {
          for (const node of nodes) {
            if (node.id === targetId) return parent
            if (node.children && node.children.length > 0) {
              const found = findParent(node.children, targetId, node)
              if (found) return found
            }
          }
          return null
        }

        const parentNode = findParent(treeData.value, currentId)
        if (parentNode && !visited.has(parentNode.id)) {
          queue.push(parentNode.id)
        }
      }

      console.log('findReachableTags returning:', Array.from(reachableTags));
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
      if (!graph || !nodes.value || !edges.value) {
        console.log('buildTreeFromGraph: missing data', { graph: !!graph, nodes: nodes.value?.length, edges: edges.value?.length });
        return [];
      }

      console.log('buildTreeFromGraph: building tree from', nodes.value.length, 'nodes and', edges.value.length, 'edges');

      const nodeMap = new Map()
      const rootNodesArray = []

      // Create map of all nodes from graph data (excluding associative tag nodes)
      const allTargetIds = new Set(edges.value.map(edge => edge?.target).filter(Boolean))
      const allSourceIds = new Set(edges.value.map(edge => edge?.source).filter(Boolean))

      nodes.value.forEach(node => {
        // Skip associative tag nodes
        if (node.associative) {
          return; // Skip this node
        }

        // Include all non-associative nodes, even those without edges
        nodeMap.set(node.id, {
          id: node.id,
          name: node.name,
          type: 'taxonomy',
          children: [],
          vulnerabilities: 0,
          projectsCount: node.projectsCount || 0,
        })
      })

      // Build tree structure from edges
      edges.value.forEach(edge => {
        const parentNode = nodeMap.get(edge.source)
        const childNode = nodeMap.get(edge.target)

        // Only add edge if both nodes exist
        if (parentNode && childNode) {
          parentNode.children.push(childNode)
          console.log('Added edge:', edge.source, '->', edge.target)
        }
      })

      // Find root nodes (nodes without incoming edges)
      nodeMap.forEach((nodeData, nodeId) => {
        const hasIncomingEdge = allTargetIds.has(nodeId)
        if (!hasIncomingEdge) {
          rootNodesArray.push(nodeId)
          console.log('Found root node:', nodeId, nodeData.name)
        }
      })

      // If no root nodes found, use all available nodes as root (fallback)
      if (rootNodesArray.length === 0) {
        console.log('No root nodes found, using all nodes as roots');
        nodeMap.forEach((nodeData, nodeId) => {
          rootNodesArray.push(nodeId)
        })
      }

      // Return sorted tree nodes - nodes with children first, then leaves
      const result = rootNodesArray.map(nodeId => nodeMap.get(nodeId)).filter(Boolean).sort((a, b) => {
        // First sort by whether node has children (nodes with children first)
        const aHasChildren = a.children && a.children.length > 0
        const bHasChildren = b.children && b.children.length > 0

        if (aHasChildren && !bHasChildren) {
          return -1 // a comes first (has children)
        }
        if (!aHasChildren && bHasChildren) {
          return 1 // b comes first (has children)
        }

        // If both have children or both are leaves, sort by name as usual
        return a.name.localeCompare(b.name)
      });

      console.log('buildTreeFromGraph: returning', result.length, 'root nodes with children:',
        result.map(n => ({ name: n.name, children: n.children.length })));

      return result;
    }

    const relatedProjects = computed(() => {
      try {
        // If no projects loaded yet, return empty
        if (!projects.value || projects.value.length === 0) return []

        // If no tree data yet but projects are loaded, return all projects
        if (!treeData.value || treeData.value.length === 0) {
          return projects.value || []
        }

        if (!selectedTreeNode.value) {
          return projects.value || []
        }

        const reachableNodes = findReachableTags(selectedTreeNode.value?.id)

        return (projects.value || []).filter(project => {
          if (!project || !project.tags || project.tags.length === 0) {
            return false
          }

          return project.tags.some(tag =>
            tag && tag.name && reachableNodes.has(tag.name)
          )
        })
      } catch (err) {
        console.error('Error in relatedProjects computed:', err);
        return []
      }
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

    // Helper function to expand all nodes recursively
    const expandAll = (nodes) => {
      if (!nodes || !Array.isArray(nodes)) return

      const expanded = new Set()

      // Recursive function to collect all node IDs
      const collectAllNodeIds = (nodeList) => {
        if (!nodeList || !Array.isArray(nodeList)) return

        nodeList.forEach(node => {
          if (!node || !node.id) return
          expanded.add(node.id)
          if (node.children && Array.isArray(node.children) && node.children.length > 0) {
            collectAllNodeIds(node.children)
          }
        })
      }

      collectAllNodeIds(nodes)
      expandedNodes.value = expanded
    };

    const refreshData = async () => {
      try {
        // Load all data in parallel for better performance
        const results = await Promise.all([
          projectStore.loadProjects(),
          tagStore.loadTags(),
          taxonomyStore.loadTaxonomies(),
          graphStore.loadGraph({
            rootTaxonomy: null,
            associativeMode: associativeMode.value
          })
        ]);

        // Check if any promises failed
        const failures = results.filter(result => result.status === 'rejected');
        if (failures.length > 0) {
          console.warn('Some data loading operations failed:', failures);
        }

        // Build proper hierarchical tree structure from graph data
        if (nodes.value && nodes.value.length > 0 &&
            edges.value && edges.value.length > 0) {

          try {
            // Build hierarchical tree from graph data
            treeData.value = buildTreeFromGraph(graphData.value);

            // Update all reachable nodes for computed property
            await updateAllReachableNodes();

            if (treeData.value && treeData.value.length > 0) {
              expandAll(treeData.value);
            }
          } catch (treeErr) {
            console.error('Error building tree:', treeErr);
            treeData.value = [];
          }
        } else {
          // Clear tree data if no nodes/edges available
          treeData.value = [];
        }
      } catch (err) {
        console.error('Error in refreshData:', err);
        error.value = err?.message || 'Failed to load data';
        treeData.value = [];
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
      // Coordinated loading state
      shouldShowLoading,
      isDataReady,

      // Graph data
      graphData,
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
      PAGE_SIZE_OPTIONS,

      // Methods
      refreshData,
      selectTreeNode,
      toggleTreeNode,
      clearSelection,
      findReachableTags,
      setAssociativeMode,
      buildTreeFromGraph,
      buildTreeFromTaxonomies,
      updateAllReachableNodes,
      expandAll,
      onPageChanged,
      getTaxonomyBadgeStyle,
      getTaxonomyBadgeStyleForNode,
      getTaxonomyNameForNode,
      onPageSizeChanged,

      // Project action handlers
      viewProject,
      viewSecurityDetails,
      analyzeProject,

      // Helper functions
      buildDTProjectUrl,
      buildDTProjectFindingsUrl,
      getProjectVulnerabilities
    }
  }
}
</script>
