<template>
  <div class="px-4 sm:px-0">
    <div class="bg-white dark:bg-gray-800 rounded-lg shadow p-4">
      <div class="flex justify-between items-start mb-6">
        <div>
          <h2 class="text-2xl font-bold text-gray-900 dark:text-white">Project Center</h2>
          <p class="text-sm text-gray-600 dark:text-gray-400 mt-1">
            Browse and manage Dependency-Track projects
          </p>
        </div>
        <button
          @click="refreshProjects"
          class="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500 disabled:opacity-50"
          title="Refresh projects"
        >
          <RefreshCw class="mr-2 h-4 w-4" :class="{ 'animate-spin': isLoading }" />
          Refresh
        </button>
      </div>
    </div>

    <!-- Projects List -->
    <div class="bg-white dark:bg-gray-800 rounded-lg shadow p-4 mt-6">
      <div class="flex justify-between items-center mb-4">
        <h2 class="text-lg font-semibold text-gray-900 dark:text-white">Projects</h2>
        <div class="flex items-center gap-2">
          <div class="text-sm text-gray-600 dark:text-gray-400">
            {{ filteredTotal || 0 }} projects
          </div>
          <!-- View Mode Controls -->
          <div class="flex items-center space-x-2">
            <button
              @click="projectsViewMode = 'list'"
              :class="[
                'px-3 py-1 text-sm rounded-md',
                projectsViewMode === 'list'
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300'
              ]"
            >
              <ListIcon class="w-4 h-4" />
            </button>
            <button
              @click="projectsViewMode = 'deck'"
              :class="[
                'px-3 py-1 text-sm rounded-md cursor-pointer',
                projectsViewMode === 'deck'
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300'
              ]"
              title="Card view"
            >
              <SquareIcon class="w-4 h-4" />
            </button>
            <button
              @click="projectsViewMode = 'table'"
              :class="[
                'px-3 py-1 text-sm rounded-md cursor-pointer',
                projectsViewMode === 'table'
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300'
              ]"
              title="Table view (sortable)"
            >
              <TableIcon class="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>

      <!-- Search and Filters -->
      <div class="bg-white dark:bg-gray-800 rounded-lg shadow p-4 mb-6">
        <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
          <!-- Search (by name, server-side) -->
          <div class="md:col-span-2">
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Search Projects
            </label>
            <input
              v-model="filters.search"
              @input="debouncedSearch"
              type="text"
              placeholder="Search by project name..."
              :disabled="!!selectedTag"
              class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white disabled:opacity-50"
            />
          </div>

          <!-- Tag filter: searchable select (server-side filter via DT's
               per-tag endpoint). Scales to hundreds of tags. -->
          <SearchableSelect
            v-model="selectedTag"
            :options="tagOptions"
            label="Filter by Tag"
            id="tag-filter"
            placeholder="Search tags…"
            hint-key="projectsCount"
          />

          <!-- Quick Actions -->
          <div class="flex items-end space-x-2">
            <label class="flex items-center space-x-2 text-sm text-gray-700 dark:text-gray-300">
              <input
                type="checkbox"
                v-model="filters.showInactive"
                class="rounded border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-blue-600 focus:ring-blue-500"
              />
              <span>Show inactive</span>
            </label>
            <button
              @click="clearFilters"
              v-if="hasActiveFilters"
              class="px-3 py-2 text-xs font-medium rounded-full bg-blue-100 dark:bg-blue-900 text-blue-800 dark:text-blue-200 hover:bg-blue-200 dark:hover:bg-blue-800"
            >
              Clear
            </button>
          </div>
        </div>
      </div>

      <!-- Pagination Controls -->
      <div v-if="filteredTotal > projectStore.pageSize" class="flex items-center justify-between mb-6 px-4">
        <div class="flex items-center space-x-4">
          <div class="text-sm text-gray-700 dark:text-gray-300 hidden sm:block">
            Showing {{ data.length }} of {{ filteredTotal }} projects
          </div>
          <div class="flex items-center space-x-2">
            <label class="text-sm text-gray-600 dark:text-gray-400">Page size:</label>
            <select
              v-model="projectStore.pageSize"
              @change="handlePageSizeChange(projectStore.pageSize)"
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
            @click="handlePageChange(projectStore.currentPage - 1)"
            :disabled="projectStore.currentPage <= 1"
            class="px-3 py-1 text-sm border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
            </svg>
          </button>

          <!-- Page Numbers -->
          <div class="flex items-center space-x-1">
            <button
              v-for="page in Math.min(5, projectStore.totalPages)"
              :key="page"
              @click="handlePageChange(page)"
              :class="[
                'px-3 py-1 text-sm border rounded-md',
                page === projectStore.currentPage
                  ? 'bg-blue-600 text-white border-blue-600'
                  : 'bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-300 border-gray-300 dark:border-gray-600 hover:bg-gray-50 dark:hover:bg-gray-700'
              ]"
            >
              {{ page }}
            </button>
            <span v-if="projectStore.totalPages > 5" class="px-2 text-gray-500">...</span>
            <button
              v-if="projectStore.totalPages > 5"
              @click="handlePageChange(projectStore.totalPages)"
              class="px-3 py-1 text-sm border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700"
            >
              {{ projectStore.totalPages }}
            </button>
          </div>

          <button
            @click="handlePageChange(projectStore.currentPage + 1)"
            :disabled="projectStore.currentPage >= projectStore.totalPages"
            class="px-3 py-1 text-sm border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
            </svg>
          </button>
        </div>
      </div>

      <!-- Loading State -->
      <div v-if="isLoading && data.length === 0" class="text-center py-8">
        <div class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        <p class="mt-2 text-gray-600 dark:text-gray-400">Loading project center...</p>
      </div>

      <!-- Projects Display -->
      <div v-else-if="data.length === 0 && !isLoading" class="text-center py-8 text-gray-500 dark:text-gray-400">
        <FolderOpen class="mx-auto h-12 w-12 text-gray-400" />
        <h3 class="mt-2 text-sm font-medium text-gray-900 dark:text-white">No projects found</h3>
        <p class="mt-1 text-sm text-gray-500 dark:text-gray-400">
          {{ filters.search || filters.activeOnly ? 'Try adjusting your filters.' : 'No projects have been created yet.' }}
        </p>
      </div>

      <!-- List View -->
      <div v-else-if="projectsViewMode === 'list'" class="overflow-y-auto space-y-2">
        <div
          v-for="project in data"
          :key="project.uuid"
          class="p-3 bg-white dark:bg-gray-800 rounded hover:bg-gray-100 dark:hover:bg-gray-600 border border-gray-200 dark:border-gray-600"
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
            <!-- View affordance (browse to the project in DT) -->
            <button
              @click="viewProject(project)"
              class="shrink-0 text-xs text-blue-600 dark:text-blue-400 hover:text-blue-900 dark:hover:text-blue-300 hover:underline hover:shadow-sm transition-all px-2 py-1 rounded"
            >
              View
            </button>
          </div>
        </div>
      </div>

      <!-- Table View: sortable columns (sorting is server-side; ignored while a
           text search is active, since search results are relevance-ordered). -->
      <div v-else-if="projectsViewMode === 'table'" class="overflow-x-auto">
        <table class="w-full text-sm">
          <thead>
            <tr class="text-left text-gray-500 dark:text-gray-400 border-b border-gray-200 dark:border-gray-600">
              <th
                @click="setSort('name')"
                class="py-2 px-2 cursor-pointer select-none whitespace-nowrap"
                title="Sort by name"
              >
                Name<span class="ml-1">{{ sortIcon('name') }}</span>
              </th>
              <th
                @click="setSort('version')"
                class="py-2 px-2 cursor-pointer select-none whitespace-nowrap"
                title="Sort by version"
              >
                Version<span class="ml-1">{{ sortIcon('version') }}</span>
              </th>
              <th class="py-2 px-2 whitespace-nowrap">Status</th>
              <th
                @click="setSort('lastBomImport')"
                class="py-2 px-2 cursor-pointer select-none whitespace-nowrap"
                title="Sort by last activity"
              >
                Last activity<span class="ml-1">{{ sortIcon('lastBomImport') }}</span>
              </th>
              <th class="py-2 px-2 text-right whitespace-nowrap" title="Critical">C</th>
              <th class="py-2 px-2 text-right whitespace-nowrap" title="High">H</th>
              <th class="py-2 px-2 text-right whitespace-nowrap" title="Medium">M</th>
              <th class="py-2 px-2 text-right whitespace-nowrap" title="Low">L</th>
              <th class="py-2 px-2"></th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="project in data"
              :key="project.uuid"
              class="border-b border-gray-100 dark:border-gray-700/60 hover:bg-gray-50 dark:hover:bg-gray-700/40"
            >
              <td class="py-2 px-2 font-medium text-gray-900 dark:text-white truncate max-w-xs" :title="project.name">
                {{ project.displayName || project.name }}
              </td>
              <td class="py-2 px-2 text-gray-600 dark:text-gray-400 whitespace-nowrap">{{ project.version || 'latest' }}</td>
              <td class="py-2 px-2 whitespace-nowrap">
                <span
                  :class="[
                    'px-1.5 py-0.5 text-xs rounded-full',
                    project.active !== false
                      ? 'bg-green-100 dark:bg-green-900/30 text-green-800 dark:text-green-200'
                      : 'bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-300'
                  ]"
                >
                  {{ project.active !== false ? 'Active' : 'Inactive' }}
                </span>
              </td>
              <td class="py-2 px-2 text-gray-600 dark:text-gray-400 whitespace-nowrap">{{ formatDate(project.lastActivity) }}</td>
              <td class="py-2 px-2 text-right tabular-nums" :class="project.metrics?.critical ? 'text-red-600 dark:text-red-400 font-medium' : 'text-gray-400 dark:text-gray-600'">{{ cellCount(project.metrics?.critical) }}</td>
              <td class="py-2 px-2 text-right tabular-nums" :class="project.metrics?.high ? 'text-orange-600 dark:text-orange-400 font-medium' : 'text-gray-400 dark:text-gray-600'">{{ cellCount(project.metrics?.high) }}</td>
              <td class="py-2 px-2 text-right tabular-nums" :class="project.metrics?.medium ? 'text-yellow-600 dark:text-yellow-400 font-medium' : 'text-gray-400 dark:text-gray-600'">{{ cellCount(project.metrics?.medium) }}</td>
              <td class="py-2 px-2 text-right tabular-nums" :class="project.metrics?.low ? 'text-blue-600 dark:text-blue-400 font-medium' : 'text-gray-400 dark:text-gray-600'">{{ cellCount(project.metrics?.low) }}</td>
              <td class="py-2 px-2 text-right whitespace-nowrap">
                <button
                  @click="viewProject(project)"
                  class="text-xs text-blue-600 dark:text-blue-400 hover:underline cursor-pointer"
                >
                  View
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Deck View -->
      <div v-else-if="projectsViewMode === 'deck'" class="overflow-y-auto">
        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-3 gap-4 p-4">
          <ProjectCard
            v-for="project in data"
            :key="project.uuid"
            :project="project"
            :clickable="false"
            :getTagStyle="getTagStyle"
            :getTagDynamicStyle="getTagDynamicStyle"
            @view="viewProject"
            @security-details="viewSecurityDetails"
            @analyze="analyzeProject"
          />
        </div>
      </div>

    </div>
  </div>
</template>

<script>
import { ref, onMounted, watch, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { storeToRefs } from 'pinia'
import { RefreshCw, FolderOpen, List as ListIcon, Table as TableIcon, Square as SquareIcon } from '@lucide/vue'
import ProjectCard from './ProjectCard.vue'
import SearchableSelect from './SearchableSelect.vue'
import { createLogger } from '../utils/logger'
import { useToast } from '../composables/useToast'
import { buildDTProjectUrl, buildDTProjectFindingsUrl } from '../config.js'
import { useProjectStore } from '../stores/projects'
import { useTaxonomyStore } from '../stores/taxonomies'
import { useTagStore } from '../stores/tags'
import { createJsRegExp } from '../utils/taxonomyParser'

export default {
  name: 'ProjectCenter',
  components: {
    FolderOpen,
    ListIcon,
    TableIcon,
    SquareIcon,
    RefreshCw,
    ProjectCard,
    SearchableSelect
  },
  setup() {
    const logger = createLogger('ProjectCenter')
    const route = useRoute()
    const router = useRouter()
    const projectStore = useProjectStore()
    const { error } = storeToRefs(projectStore)
    const { showSuccess, showError } = useToast()
    const taxonomyStore = useTaxonomyStore()
    const { taxonomies } = storeToRefs(taxonomyStore)
    const { getTaxonomyBadgeStyle, getTagTaxonomy, loadTaxonomies } = taxonomyStore
    const tagStore = useTagStore()

    const filters = ref({
      search: '',
      showInactive: false
    })

    // Server-side browsing state (see fetchProjects): the current page's rows,
    // DT's real total, a loading flag, the selected tag filter and its options.
    const loading = ref(false)
    const selectedTag = ref('')
    const tagOptions = ref([])

    const projectsViewMode = ref('deck') // 'list', 'deck', or 'table'

    // Server-side sort state for the table view (empty = DT's default order).
    const sortName = ref('')
    const sortOrder = ref('asc')

    // The current server page of projects and DT's real total. Populated by
    // fetchProjects(); there is no client-side filtering or slicing any more.
    const data = ref([])
    const filteredTotal = ref(0)

    let searchTimeout = null
    const debouncedSearch = () => {
      clearTimeout(searchTimeout)
      searchTimeout = setTimeout(() => {
        projectStore.currentPage = 1 // new query -> first page
        fetchProjects().catch(() => {})
      }, 500)
    }

    // Server-side fetch of a single page: name search, the active filter and the
    // selected tag are all applied by DT. DT's per-tag endpoint has no name
    // search, so when a tag is selected the search box is ignored (and disabled).
    const fetchProjects = async () => {
      loading.value = true
      try {
        const { rows, total } = await projectStore.fetchProjectsPage({
          page: projectStore.currentPage,
          pageSize: projectStore.pageSize,
          search: filters.value.search,
          excludeInactive: !filters.value.showInactive,
          tag: selectedTag.value,
          sortName: sortName.value,
          sortOrder: sortOrder.value
        })
        data.value = rows
        filteredTotal.value = total
        projectStore.totalProjects = total
        projectStore.totalPages = Math.max(1, Math.ceil(total / projectStore.pageSize))
        return rows
      } finally {
        loading.value = false
      }
    }

    const handlePageChange = (page) => {
      projectStore.currentPage = page
      fetchProjects().catch(() => {}) // Ignore errors for page changes
    }

    const handlePageSizeChange = (pageSize) => {
      projectStore.pageSize = pageSize
      projectStore.currentPage = 1 // page count changed; restart from the first page
      fetchProjects().catch(() => {}) // Ignore errors for page size changes
    }

    // Table view: sortable columns (server-side). Clicking a header toggles
    // asc/desc; switching column starts at asc. Sorting resets to page 1.
    const setSort = (field) => {
      if (sortName.value === field) {
        sortOrder.value = sortOrder.value === 'asc' ? 'desc' : 'asc'
      } else {
        sortName.value = field
        sortOrder.value = 'asc'
      }
      projectStore.currentPage = 1
      fetchProjects().catch(() => {})
    }
    const sortIcon = (field) => (sortName.value === field ? (sortOrder.value === 'asc' ? '▲' : '▼') : '')
    const cellCount = (n) => (n > 0 ? n : '-')
    const formatDate = (dateString) => {
      if (!dateString) return 'Never'
      try {
        return new Date(dateString).toLocaleDateString()
      } catch {
        return 'Invalid date'
      }
    }

    // Project action handlers
    const viewProject = (project) => {
      // Navigate to project details page
      window.open(buildDTProjectUrl(project.uuid), '_blank')
    }

    const viewSecurityDetails = (project) => {
      // Navigate to security details page
      window.open(buildDTProjectFindingsUrl(project.uuid), '_blank')
    }

    const analyzeProject = async (project) => {
      // Trigger a re-analysis in Dependency-Track (via the batch refresh endpoint
      // with a single project) rather than browsing to DT's findings view.
      try {
        await projectStore.bulkRefreshProjects([project.uuid])
        showSuccess(`Re-analysis triggered for ${project.name}`)
      } catch (error) {
        logger.error('Error triggering analysis:', error)
        showError('Failed to trigger analysis', 'Please try again.')
      }
    }

    const getProjectVulnerabilities = (metrics) => {
      if (!metrics) return 0
      return (metrics.critical || 0) + (metrics.high || 0) + (metrics.medium || 0) + (metrics.low || 0)
    }

    // Computed property to check if any filters are active
    const hasActiveFilters = computed(() => {
      return filters.value.search ||
             filters.value.showInactive ||
             selectedTag.value
    })

    // Clear all filters and reload the first page.
    const clearFilters = () => {
      filters.value = { search: '', showInactive: false }
      selectedTag.value = ''
      projectStore.currentPage = 1
      fetchProjects().catch(() => {})
    }

    // Tag styling function
    const getTagStyle = (tag) => {
      // Try to get taxonomy from tag object first, then fallback to store lookup
      let hasTaxonomy = getTagTaxonomy(tag)

      // If tag doesn't have taxonomy info, try to find it by matching tag name with taxonomies
      if (!hasTaxonomy) {
        hasTaxonomy = taxonomies.value.find(taxonomy => {
          if (!taxonomy.regex_pattern) return false
          const regex = createJsRegExp(taxonomy.regex_pattern)
          return regex ? regex.test(tag.name) : false
        })
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
      let hasTaxonomy = getTagTaxonomy(tag)
      if (!hasTaxonomy) {
        hasTaxonomy = taxonomies.value.find(taxonomy => {
          if (!taxonomy.regex_pattern) return false
          const regex = createJsRegExp(taxonomy.regex_pattern)
          return regex ? regex.test(tag.name) : false
        })
      }

      // Return taxonomy style if it's a taxonomy tag
      if (hasTaxonomy) {
        return getTaxonomyBadgeStyle(hasTaxonomy)
      }

      return {}
    }

    // Refresh functionality
    const refreshProjects = async () => {
      try {
        await Promise.all([
          fetchProjects(),
          loadTaxonomies()
        ])
        showSuccess('Projects refreshed successfully')
      } catch (error) {
        logger.error('Error refreshing projects:', error)
        showError('Failed to refresh projects', 'Please try again.')
      }
    }

    // --- Shareable views: reflect the filter/view state in the URL query so a
    // bookmarked or shared link restores the same view. Defaults are omitted to
    // keep links clean (deck view, page 1, page size 20, ascending sort).
    const DEFAULT_PAGE_SIZE = 20

    const applyQueryToState = () => {
      const q = route.query
      if (typeof q.q === 'string') filters.value.search = q.q
      if (typeof q.tag === 'string') selectedTag.value = q.tag
      filters.value.showInactive = q.inactive === '1'
      if (['list', 'deck', 'table'].includes(q.view)) projectsViewMode.value = q.view
      if (typeof q.sort === 'string') sortName.value = q.sort
      if (q.order === 'asc' || q.order === 'desc') sortOrder.value = q.order
      const page = parseInt(q.page, 10)
      if (page > 0) projectStore.currentPage = page
      const size = parseInt(q.size, 10)
      if (size > 0) projectStore.pageSize = size
    }

    const syncStateToQuery = () => {
      const query = {}
      if (filters.value.search) query.q = filters.value.search
      if (selectedTag.value) query.tag = selectedTag.value
      if (filters.value.showInactive) query.inactive = '1'
      if (projectsViewMode.value !== 'deck') query.view = projectsViewMode.value
      if (sortName.value) {
        query.sort = sortName.value
        if (sortOrder.value !== 'asc') query.order = sortOrder.value
      }
      if (projectStore.currentPage > 1) query.page = String(projectStore.currentPage)
      if (projectStore.pageSize !== DEFAULT_PAGE_SIZE) query.size = String(projectStore.pageSize)
      // replace (not push) so filter tweaks don't spam browser history.
      router.replace({ query }).catch(() => {})
    }

    // The active filter and tag filter refetch immediately (resetting to page 1).
    // Name search is debounced separately via debouncedSearch().
    watch(() => filters.value.showInactive, () => {
      projectStore.currentPage = 1
      fetchProjects().catch(() => {})
    })
    watch(selectedTag, () => {
      projectStore.currentPage = 1
      fetchProjects().catch(() => {})
    })

    // Mirror any view/filter change into the URL.
    watch(
      () => [
        filters.value.search,
        selectedTag.value,
        filters.value.showInactive,
        projectsViewMode.value,
        sortName.value,
        sortOrder.value,
        projectStore.currentPage,
        projectStore.pageSize
      ],
      syncStateToQuery
    )

    onMounted(async () => {
      // Restore state from the URL before the first fetch so shared links land
      // on the intended page/filters.
      applyQueryToState()
      fetchProjects().catch(() => {})
      loadTaxonomies()
      // Load the tag list for the filter dropdown.
      try {
        await tagStore.loadTags()
        tagOptions.value = tagStore.tags || []
      } catch (e) {
        logger.error('Failed to load tags for filter:', e)
      }
    })

    return {
      data,
      filteredTotal,
      isLoading: loading,
      error,
      projectStore,
      filters,
      selectedTag,
      tagOptions,
      projectsViewMode,
      sortName,
      sortOrder,
      setSort,
      sortIcon,
      cellCount,
      formatDate,
      hasActiveFilters,
      fetchProjects,
      refreshProjects,
      debouncedSearch,
      handlePageChange,
      handlePageSizeChange,
      clearFilters,
      viewProject,
      viewSecurityDetails,
      analyzeProject,
      getProjectVulnerabilities,
      getTagStyle,
      getTagDynamicStyle,
      buildDTProjectUrl,
      buildDTProjectFindingsUrl
    }
  }
}
</script>
