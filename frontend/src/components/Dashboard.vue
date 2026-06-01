<template>
  <div class="px-4 sm:px-0">
    <!-- Security Dashboard -->
    <div class="bg-white dark:bg-gray-800 rounded-lg shadow overflow-hidden">
      <div class="flex justify-between items-center mb-4 p-4">
        <div>
          <h2 class="text-2xl font-bold text-gray-900 dark:text-white">Security Dashboard</h2>
          <div v-if="selectedTreeNode" class="flex items-center gap-2 mt-1">
            <span class="text-sm text-gray-600 dark:text-gray-400">Focusing on:</span>
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
          class="px-3 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 transition-all flex items-center gap-2 cursor-pointer hover:shadow-md"
        >
          <RefreshCw class="w-4 h-4" :class="{ 'animate-spin': projectLoading || tagLoading }"/>
          <span>Refresh</span>
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

      <SecurityOverview
        :has-data="filteredSecurityData && filteredSecurityData.length > 0"
        :total="totalVulnerabilities"
        :critical="criticalVulns"
        :high="highVulns"
        :medium="mediumVulns"
        :low="lowVulns"
      />
    </div>
    <!-- Tree (1/3) + Related Projects (2/3) -->
    <div class="flex flex-col lg:flex-row gap-4 mt-6" style="min-height: 300px;">
      <!-- Tree Panel (1/3) -->
      <NavigationTreePanel
        :tree-mode="treeMode"
        :tree-data="treeData"
        :selected-tree-node="selectedTreeNode"
        :expanded-nodes="expandedNodes"
        :tree-sort-by="treeSortBy"
        :tree-sort-desc="treeSortDesc"
        :should-show-loading="shouldShowLoading"
        @set-tree-mode="setTreeMode"
        @select="selectTreeNode"
        @toggle="toggleTreeNode"
        @clear="clearSelection"
        @expand-all="expandAllTreeNodes"
        @collapse-all="collapseAllTreeNodes"
      />

      <!-- Related Projects (2/3) -->
      <div class="flex-1 bg-white dark:bg-gray-800 rounded-lg shadow overflow-hidden flex flex-col">
        <div class="p-4 shrink-0">
          <!-- Related Projects -->
          <div>
            <div class="flex justify-between items-center mb-4">
              <h3 class="text-lg leading-6 font-medium text-gray-900 dark:text-white">Related Projects</h3>

              <!-- View Mode Controls -->
              <div class="flex items-center space-x-2">
                <button
                  @click="projectsViewMode = 'list'"
                  :class="[
                    'px-3 py-1 text-sm rounded-md cursor-pointer hover:shadow-md transition-all',
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
                    'px-3 py-1 text-sm rounded-md cursor-pointer hover:shadow-md transition-all',
                    projectsViewMode === 'deck'
                      ? 'bg-blue-600 text-white'
                      : 'bg-gray-200 text-gray-700 dark:bg-gray-700 dark:text-gray-300'
                  ]"
                  title="Card view"
                >
                  <SquareIcon class="w-4 h-4" />
                </button>
                <button
                  @click="projectsViewMode = 'table'"
                  :class="[
                    'px-3 py-1 text-sm rounded-md cursor-pointer hover:shadow-md transition-all',
                    projectsViewMode === 'table'
                      ? 'bg-blue-600 text-white'
                      : 'bg-gray-200 text-gray-700 dark:bg-gray-700 dark:text-gray-300'
                  ]"
                  title="Table view (sortable)"
                >
                  <Table class="w-4 h-4" />
                </button>
              </div>
            </div>

            <div class="text-sm text-gray-600 dark:text-gray-400 mb-4">
              <span v-if="selectedTreeNode && selectedTreeNode.name">
                {{ relatedProjects.length }} projects found for {{ getTaxonomyNameForNode(selectedTreeNode) }} "{{ selectedTreeNode.name }}"
              </span>
              <span v-else>
                {{ relatedProjects.length }} projects found (all projects reachable from any root taxonomy)
              </span>
            </div>

            <!-- Pagination Controls -->
            <Pagination
              v-if="relatedProjects.length > pageSize"
              :current-page="currentPage"
              :page-size="pageSize"
              :total-items="relatedProjects.length"
              :page-size-options="PAGE_SIZE_OPTIONS"
              @page-change="onPageChanged"
              @page-size-change="onPageSizeChanged"
            />

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
                    <div class="flex justify-between items-start gap-2">
                      <div class="flex-1 min-w-0">
                        <div class="text-base font-medium text-gray-900 dark:text-white truncate">{{ project.name }}</div>
                        <!-- Metrics & Info Line -->
                        <div class="flex flex-wrap items-center gap-1.5 mt-1">
                          <!-- Version -->
                          <span class="text-xs font-medium text-gray-600 dark:text-gray-400">{{ project.version || 'latest' }}</span>
                          <!-- Metrics Counters -->
                          <template v-if="project.metrics">
                            <span class="text-xs text-gray-300 dark:text-gray-600">|</span>
                            <span class="text-xs text-gray-500 dark:text-gray-400">
                              <span class="font-medium text-gray-900 dark:text-white">{{ project.metrics.vulnerableComponents || 0 }}</span>
                              /
                              <span class="font-medium text-gray-900 dark:text-white">{{ project.metrics.components || project.metrics.vulnerableComponents || 0 }}</span>
                              comp.
                            </span>
                            <span class="text-xs text-gray-300 dark:text-gray-600">|</span>
                            <span class="text-xs text-gray-500 dark:text-gray-400">
                              <span class="font-medium text-gray-900 dark:text-white">{{ getProjectVulnerabilities(project.metrics) }}</span>
                              vulns
                            </span>
                          </template>
                          <!-- Security Badges -->
                          <template v-if="project.metrics">
                            <span v-if="project.metrics.critical > 0" class="px-1.5 py-0.5 bg-red-100 dark:bg-red-900 text-red-800 dark:text-red-200 rounded text-xs font-medium">
                              {{ project.metrics.critical }} C
                            </span>
                            <span v-if="project.metrics.high > 0" class="px-1.5 py-0.5 bg-orange-100 dark:bg-orange-900 text-orange-800 dark:text-orange-200 rounded text-xs font-medium">
                              {{ project.metrics.high }} H
                            </span>
                            <span v-if="project.metrics.medium > 0" class="px-1.5 py-0.5 bg-yellow-100 dark:bg-yellow-900 text-yellow-800 dark:text-yellow-200 rounded text-xs font-medium">
                              {{ project.metrics.medium }} M
                            </span>
                            <span v-if="project.metrics.low > 0" class="px-1.5 py-0.5 bg-blue-100 dark:bg-blue-900 text-blue-800 dark:text-blue-200 rounded text-xs font-medium">
                              {{ project.metrics.low }} L
                            </span>
                            <span v-if="getProjectVulnerabilities(project.metrics) === 0" class="px-1.5 py-0.5 bg-green-100 dark:bg-green-900 text-green-800 dark:text-green-200 rounded text-xs font-medium">
                              No Vulns
                            </span>
                          </template>
                          <!-- Tags (at end since variable length) -->
                          <template v-if="project.tags && project.tags.length > 0">
                            <span class="text-xs text-gray-300 dark:text-gray-600">|</span>
                            <span
                              v-for="tag in project.tags.slice(0, 3)"
                              :key="tag.name"
                              class="inline-flex items-center px-1.5 py-0.5 rounded-full text-xs font-medium border truncate"
                              :class="getTagStyle(tag)"
                              :style="getTagDynamicStyle(tag)"
                            >
                              {{ tag.name }}
                            </span>
                            <span
                              v-if="project.tags.length > 3"
                              class="px-1.5 py-0.5 bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-400 text-xs rounded-full"
                            >
                              +{{ project.tags.length - 3 }}
                            </span>
                          </template>
                        </div>
                      </div>
                    </div>
                  </div>
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
                      :getTagStyle="getTagStyle"
                      :getTagDynamicStyle="getTagDynamicStyle"
                      @select="viewProject"
                      @view="viewProject"
                      @security-details="viewSecurityDetails"
                      @analyze="analyzeProject"
                    />
                  </div>
                </div>
              </div>

              <!-- Table View (sortable; related projects are in-memory, so sort
                   is client-side over the whole set, then paginated) -->
              <div v-else-if="projectsViewMode === 'table'" class="h-full flex flex-col">
                <div class="flex-1 overflow-auto p-4">
                  <table class="w-full text-sm">
                    <thead>
                      <tr class="text-left text-gray-500 dark:text-gray-400 border-b border-gray-200 dark:border-gray-600">
                        <th @click="setProjectsSort('name')" class="py-2 px-2 cursor-pointer select-none whitespace-nowrap" title="Sort by name">
                          Name<span class="ml-1">{{ projectsSortIcon('name') }}</span>
                        </th>
                        <th @click="setProjectsSort('version')" class="py-2 px-2 cursor-pointer select-none whitespace-nowrap" title="Sort by version">
                          Version<span class="ml-1">{{ projectsSortIcon('version') }}</span>
                        </th>
                        <th @click="setProjectsSort('lastActivity')" class="py-2 px-2 cursor-pointer select-none whitespace-nowrap" title="Sort by last activity">
                          Last activity<span class="ml-1">{{ projectsSortIcon('lastActivity') }}</span>
                        </th>
                        <th @click="setProjectsSort('critical')" class="py-2 px-2 text-right cursor-pointer select-none" title="Critical">C<span class="ml-0.5">{{ projectsSortIcon('critical') }}</span></th>
                        <th @click="setProjectsSort('high')" class="py-2 px-2 text-right cursor-pointer select-none" title="High">H<span class="ml-0.5">{{ projectsSortIcon('high') }}</span></th>
                        <th @click="setProjectsSort('medium')" class="py-2 px-2 text-right cursor-pointer select-none" title="Medium">M<span class="ml-0.5">{{ projectsSortIcon('medium') }}</span></th>
                        <th @click="setProjectsSort('low')" class="py-2 px-2 text-right cursor-pointer select-none" title="Low">L<span class="ml-0.5">{{ projectsSortIcon('low') }}</span></th>
                        <th class="py-2 px-2"></th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr
                        v-for="project in projectTableRows"
                        :key="project.uuid"
                        class="border-b border-gray-100 dark:border-gray-700/60 hover:bg-gray-50 dark:hover:bg-gray-700/40"
                      >
                        <td class="py-2 px-2 font-medium text-gray-900 dark:text-white truncate max-w-xs" :title="project.name">{{ project.name }}</td>
                        <td class="py-2 px-2 text-gray-600 dark:text-gray-400 whitespace-nowrap">{{ project.version || 'latest' }}</td>
                        <td class="py-2 px-2 text-gray-600 dark:text-gray-400 whitespace-nowrap">{{ formatDate(project.lastActivity) }}</td>
                        <td class="py-2 px-2 text-right tabular-nums" :class="project.metrics?.critical ? 'text-red-600 dark:text-red-400 font-medium' : 'text-gray-400 dark:text-gray-600'">{{ cellCount(project.metrics?.critical) }}</td>
                        <td class="py-2 px-2 text-right tabular-nums" :class="project.metrics?.high ? 'text-orange-600 dark:text-orange-400 font-medium' : 'text-gray-400 dark:text-gray-600'">{{ cellCount(project.metrics?.high) }}</td>
                        <td class="py-2 px-2 text-right tabular-nums" :class="project.metrics?.medium ? 'text-yellow-600 dark:text-yellow-400 font-medium' : 'text-gray-400 dark:text-gray-600'">{{ cellCount(project.metrics?.medium) }}</td>
                        <td class="py-2 px-2 text-right tabular-nums" :class="project.metrics?.low ? 'text-blue-600 dark:text-blue-400 font-medium' : 'text-gray-400 dark:text-gray-600'">{{ cellCount(project.metrics?.low) }}</td>
                        <td class="py-2 px-2 text-right whitespace-nowrap">
                          <button @click="viewProject(project)" class="text-xs text-blue-600 dark:text-blue-400 hover:underline cursor-pointer">View</button>
                        </td>
                      </tr>
                    </tbody>
                  </table>
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
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { storeToRefs } from 'pinia'
import { useProjectStore } from '../stores/projects'
import { useTagStore } from '../stores/tags'
import { useGraphStore } from '../stores/graph'
import { useTaxonomyStore } from '../stores/taxonomies'
import TreeNode from './TreeNode.vue'
import TreeTable from './TreeTable.vue'
import { buildDTProjectUrl, buildDTProjectFindingsUrl } from '../config.js'
import RiskScoreBadge from './RiskScoreBadge.vue'
import VulnerabilityBar from './VulnerabilityBar.vue'
import { AlertCircle, RefreshCw, Folder, FolderOpen, ListIcon, SquareIcon, Table, Share2, GitBranch } from 'lucide-vue-next'
import Pagination from './Pagination.vue'
import ProjectCard from './ProjectCard.vue'
import SecurityOverview from './SecurityOverview.vue'
import NavigationTreePanel from './NavigationTreePanel.vue'
import { createLogger } from '../utils/logger'
import { findReachableTags } from '../utils/treeTraversal'

export default {
  name: 'Dashboard',
  components: {
    AlertCircle,
    RefreshCw,
    Folder,
    FolderOpen,
    ListIcon,
    SquareIcon,
    Table,
    Share2,
    GitBranch,
    Pagination,
    ProjectCard,
    RiskScoreBadge,
    VulnerabilityBar,
    TreeNode,
    TreeTable,
    SecurityOverview,
    NavigationTreePanel
  },
  setup() {
    const router = useRouter()
    const logger = createLogger('app')

    // Use stores
    const projectStore = useProjectStore()
    const tagStore = useTagStore()
    const graphStore = useGraphStore()
    const taxonomyStore = useTaxonomyStore()
    const { edges, graphData, nodes, rootNodes, loading: graphLoading } = storeToRefs(graphStore)
    const { isLoading: projectLoading, error, projects } = storeToRefs(projectStore)
    const { tags, isLoading: tagLoading } = storeToRefs(tagStore)
    const { taxonomies, loading: taxonomiesLoading } = storeToRefs(taxonomyStore)
    const { getTaxonomyBadgeStyle, getTaxonomyByName, getTaxonomyForTag } = taxonomyStore

    // Coordinated loading state - wait for all stores to be ready
    const isDataReady = computed(() => {
      try {
        // Check if all loading states are complete
        const allLoaded = !projectLoading.value &&
          !tagLoading.value &&
          !graphLoading.value &&
          !taxonomiesLoading.value;

        if (!allLoaded) return false;

        // Check if we have projects data
        const hasProjects = projects.value && projects.value.length > 0;

        // Check for tree data (hierarchical mode has treeData but empty nodes/edges)
        const hasTreeData = treeData.value && treeData.value.length > 0;
        const hasGraphData = nodes.value && nodes.value.length > 0 &&
                              edges.value && edges.value.length > 0;

        // Data is ready if we have projects and either tree structure
        return hasProjects && (hasTreeData || hasGraphData);
      } catch (err) {
        logger.warn('Error in isDataReady computed:', err);
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

      if (node.type=='taxonomy' && node.taxonomy) {
        return taxonomies.value.find(t => t.id === node.taxonomy)
      }
      // Resolve by tag name, honouring priority (shared store resolver).
      return getTaxonomyForTag(node.name)
    }

    // Helper function to get taxonomy badge style for tree nodes
    // Tag styling functions for ProjectCard
    const getTagStyle = (tag) => {
      // Try to get taxonomy from tag object first
      let hasTaxonomy = tag.taxonomy

      // If tag doesn't have taxonomy info, resolve by name (priority-aware).
      if (!hasTaxonomy) {
        hasTaxonomy = getTaxonomyForTag(tag.name)
      }

      // Store taxonomy reference for style application
      if (hasTaxonomy) {
        tag._taxonomy = hasTaxonomy
      }

      // Return taxonomy style if it's a taxonomy tag
      if (hasTaxonomy) {
        return 'taxonomy'
      }

      // Default style for non-taxonomy tags
      return 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300'
    }

    const getTagDynamicStyle = (tag) => {
      // Get taxonomy using same logic as getTagStyle
      let hasTaxonomy = tag.taxonomy
      if (!hasTaxonomy) {
        hasTaxonomy = getTaxonomyForTag(tag.name)
      }

      // Return taxonomy style if it's a taxonomy tag
      if (hasTaxonomy) {
        return getTaxonomyBadgeStyle(hasTaxonomy)
      }

      return {}
    }

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
    const selectedTreeNode = ref(null)
    const treeSortBy = ref('name')
    const treeSortDesc = ref(false)
    const treeMode = ref('hierarchical') // 'network' or 'hierarchical'


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

    const setTreeMode = async (mode) => {
      treeMode.value = mode;
      // Reload tree with appropriate endpoint
      if (mode === 'hierarchical') {
        await graphStore.loadHierarchicalTree();
        // Sync tree data from store
        treeData.value = graphStore.treeData || [];
      } else {
        await graphStore.loadGraph({
          rootTaxonomy: null,
          associativeMode: associativeMode.value
        });
        // Sync tree data from store
        treeData.value = graphStore.treeData || [];
      }
    };

    const associativeMode = ref(true) // Default to hierarchical mode like graph
    const projectsViewMode = ref('deck') // 'list', 'grid', or 'deck'

    // Uniform pagination constants
    const DEFAULT_PAGE_SIZE = 20
    const PAGE_SIZE_OPTIONS = [10, 20, 50, 100]

    // Pagination state
    const currentPage = ref(1)
    const pageSize = ref(DEFAULT_PAGE_SIZE)

    // Local state for reachable nodes
    const allReachableNodes = ref(new Set())

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

        const reachableNodes = findReachableTags(selectedTreeNode.value?.id, treeData.value)

        return (projects.value || []).filter(project => {
          if (!project || !project.tags || project.tags.length === 0) {
            return false
          }

          return project.tags.some(tag =>
            tag && tag.name && reachableNodes.has(tag.name)
          )
        })
      } catch (err) {
        logger.error('Error in relatedProjects computed:', err);
        return []
      }
    })

    // Helper function to update all reachable nodes
    const updateAllReachableNodes = async () => {
      const allReachable = new Set()

      // Get all root nodes and find all reachable nodes from them
      if (rootNodes.value && rootNodes.value.length > 0) {
        rootNodes.value.forEach(rootNode => {
          const reachable = findReachableTags(rootNode.id, treeData.value)
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
        // Load tree based on current mode
        const treeLoader = treeMode.value === 'hierarchical'
          ? graphStore.loadHierarchicalTree()
          : graphStore.loadGraph({ rootTaxonomy: null, associativeMode: associativeMode.value });

        // Load all data in parallel for better performance
        const results = await Promise.all([
          projectStore.loadProjects(),
          tagStore.loadTags(),
          taxonomyStore.loadTaxonomies(),
          treeLoader
        ])

        // Sync tree data from store (works for both network and hierarchical modes)
        try {
          // Use tree data from backend (populated for both graph and hierarchical endpoints)
          treeData.value = graphStore.treeData || [];

          // Automatically expand all nodes for better UX
          if (treeData.value.length > 0) {
            expandAll(treeData.value);
          }

          // Update all reachable nodes for computed property
          if (treeData.value.length > 0) {
            await updateAllReachableNodes();
          }
        } catch (treeErr) {
          logger.error('Error building tree:', treeErr);
          treeData.value = [];
        }
      } catch (err) {
        logger.error('Error in refreshData:', err);
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

    // Collect every node id in the tree (recursively) so we can expand all at once.
    const collectTreeNodeIds = (nodes, acc = new Set()) => {
      for (const node of nodes || []) {
        if (node && node.id) acc.add(node.id);
        if (node && node.children && node.children.length) {
          collectTreeNodeIds(node.children, acc);
        }
      }
      return acc;
    };

    const expandAllTreeNodes = () => {
      expandedNodes.value = collectTreeNodeIds(treeData.value);
    };

    const collapseAllTreeNodes = () => {
      expandedNodes.value = new Set();
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

    // Table view (client-side sort over the full related set, then paginate).
    const projectsSortName = ref('')
    const projectsSortOrder = ref('asc')
    const SEVERITY_FIELDS = ['critical', 'high', 'medium', 'low']
    const setProjectsSort = (field) => {
      if (projectsSortName.value === field) {
        projectsSortOrder.value = projectsSortOrder.value === 'asc' ? 'desc' : 'asc'
      } else {
        projectsSortName.value = field
        projectsSortOrder.value = 'asc'
      }
      currentPage.value = 1
    }
    const projectsSortIcon = (field) => (projectsSortName.value === field ? (projectsSortOrder.value === 'asc' ? '▲' : '▼') : '')
    const cellCount = (n) => (n > 0 ? n : '-')
    const sortedRelatedProjects = computed(() => {
      const list = [...(relatedProjects.value || [])]
      const field = projectsSortName.value
      if (!field) return list
      const dir = projectsSortOrder.value === 'desc' ? -1 : 1
      const numeric = SEVERITY_FIELDS.includes(field)
      return list.sort((a, b) => {
        if (numeric) {
          return ((a.metrics?.[field] || 0) - (b.metrics?.[field] || 0)) * dir
        }
        const av = (a[field] ?? '').toString().toLowerCase()
        const bv = (b[field] ?? '').toString().toLowerCase()
        return av < bv ? -dir : av > bv ? dir : 0
      })
    })
    const projectTableRows = computed(() => {
      if (!currentPage.value || !pageSize.value) return []
      const start = (currentPage.value - 1) * pageSize.value
      return sortedRelatedProjects.value.slice(start, start + pageSize.value)
    })

    return {
      // Coordinated loading state
      shouldShowLoading,
      projectLoading,
      tagLoading,
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
      expandedNodes,
      selectedTreeNode,
      allReachableNodes,
      treeSortBy,
      treeSortDesc,
      treeMode,
      setTreeMode,

      // Project data
      relatedProjects,
      paginatedProjects,
      projectTableRows,
      projectsSortName,
      projectsSortOrder,
      setProjectsSort,
      projectsSortIcon,
      cellCount,
      formatDate,
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
      expandAllTreeNodes,
      collapseAllTreeNodes,
      clearSelection,
      setAssociativeMode,
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
      getProjectVulnerabilities,
      getTagStyle,
      getTagDynamicStyle
    }
  }
}
</script>
