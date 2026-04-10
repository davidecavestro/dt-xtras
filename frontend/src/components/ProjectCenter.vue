<template>
  <div class="px-4 py-6 sm:px-0">
    <div class="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
      <h2 class="text-2xl font-bold text-gray-900 dark:text-white mb-6">Project Center</h2>
      <p class="text-gray-600 dark:text-gray-400 mb-6">
        Browse and manage Dependency-Track projects
      </p>
    </div>

    <!-- Projects List -->
    <div class="bg-white dark:bg-gray-800 rounded-lg shadow p-6 mt-6">
      <div class="flex justify-between items-center mb-4">
        <h2 class="text-lg font-semibold text-gray-900 dark:text-white">Projects</h2>
        <div class="flex items-center gap-2">
          <div class="text-sm text-gray-600 dark:text-gray-400">
            {{ totalProjects || 0 }} projects
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
                'px-3 py-1 text-sm rounded-md',
                projectsViewMode === 'deck'
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300'
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
                  : 'bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300'
              ]"
            >
              <GridIcon class="w-4 h-4" />
            </button> -->
          </div>
        </div>
      </div>

      <!-- Search and Filters -->
      <div class="bg-white dark:bg-gray-800 rounded-lg shadow p-4 mb-6">
        <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
          <!-- Search -->
          <div class="md:col-span-2">
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Search Projects
            </label>
            <input
              v-model="filters.search"
              @input="debouncedSearch"
              type="text"
              placeholder="Search by name or tags..."
              class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
            />
          </div>

          <!-- Activity Filter -->
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Activity Status
            </label>
            <select
              v-model="filters.activityFilter"
              class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
            >
              <option value="all">All Projects</option>
              <option value="active">Active Only</option>
              <option value="inactive">Inactive Only</option>
              <option value="recent">Recent (Last 7 days)</option>
              <option value="old">Old (30+ days)</option>
            </select>
          </div>

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
      <div v-if="totalProjects > projectStore.pageSize" class="flex items-center justify-between mb-6 px-4">
        <div class="flex items-center space-x-4">
          <div class="text-sm text-gray-700 dark:text-gray-300">
            Showing {{ data.length }} of {{ totalProjects }} projects
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
          class="p-3 bg-white dark:bg-gray-800 rounded hover:bg-gray-100 dark:hover:bg-gray-600 cursor-pointer border border-gray-200 dark:border-gray-600"
          @click="viewProject(project)"
        >
          <div class="flex justify-between items-start mb-2">
            <div class="flex-1">
              <div class="text-sm font-medium text-gray-900 dark:text-white">{{ project.name }}</div>
              <div class="text-xs text-gray-500 dark:text-gray-400">{{ project.version || 'latest' }}</div>
              <div v-if="project.tags && project.tags.length > 0" class="text-xs italic text-gray-500 dark:text-gray-400 mt-1">
                🏷 {{ Array.isArray(project.tags) ? project.tags.map( tag => tag.name ).join(', ') : 'No tags' }}
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
              ✅ No Vulnerabilities
            </span>
          </div>
        </div>
      </div>

      <!-- Grid View -->
      <div v-else-if="projectsViewMode === 'grid'" class="overflow-y-auto">
        <vue3-datagrid
          :columns="gridColumns"
          :source="data"
          :row-height="50"
          :virtual="false"
          :theme="isDarkMode ? 'darkCompact' : 'compact'"
          :filter="false"
          :resize="true"
          :autoSizeColumn="{ mode: 'autoSizeOnTextOverlap' }"
          :stretch="true"
          :pagination="false"
          @row-click="onRowClick"
          @row-select="onRowSelect"
          :show-selection="true"
          class="w-full border-gray-200 dark:border-gray-700"
          style="height: 500px;"
        >
        </vue3-datagrid>
      </div>

      <!-- Deck View -->
      <div v-else-if="projectsViewMode === 'deck'" class="overflow-y-auto">
        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-3 gap-4 p-4">
          <ProjectCard
            v-for="project in data"
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
</template>

<script>
import { ref, onMounted, watch, onUnmounted, computed } from 'vue'
import { storeToRefs } from 'pinia'
import { FolderOpen, List as ListIcon, Grid as GridIcon, Square as SquareIcon } from 'lucide-vue-next'
import Vue3Datagrid, { VGridVueTemplate } from '@revolist/vue3-datagrid'
import ProjectCard from './ProjectCard.vue'
import NameCell from './grid-cells/NameCell.vue'
import StatusCell from './grid-cells/StatusCell.vue'
import TagsCell from './grid-cells/TagsCell.vue'
import DateCell from './grid-cells/DateCell.vue'
import { buildDTProjectUrl, buildDTProjectFindingsUrl } from '../config.js'
import { useProjectStore } from '../stores/projects'

export default {
  name: 'ProjectCenter',
  components: {
    FolderOpen,
    ListIcon,
    GridIcon,
    SquareIcon,
    Vue3Datagrid,
    ProjectCard,
    NameCell,
    StatusCell,
    TagsCell,
    DateCell
  },
  setup() {
    const projectStore = useProjectStore()
    const { projects, isLoading, error, totalProjects } = storeToRefs(projectStore)

    const filters = ref({
      search: '',
      showInactive: false,
      activityFilter: 'all'
    })

    const projectsViewMode = ref('deck') // 'list', 'grid', or 'deck'

    // Grid columns for projects grid view
    const gridColumns = computed(() => [
      {
        field: 'name',
        headerName: 'Project',
        flexGrow: 4,
        minWidth: 200,
        cellRenderer: NameCell
      },
      {
        field: 'version',
        headerName: 'Version',
        width: 120,
        cellRenderer: NameCell
      },
      {
        field: 'lastActivity',
        headerName: 'Last Activity',
        width: 150,
        cellRenderer: DateCell
      },
      {
        field: 'vulnerabilities.critical',
        headerName: 'Critical',
        width: 100,
        cellRenderer: StatusCell
      },
      {
        field: 'vulnerabilities.high',
        headerName: 'High',
        width: 80,
        cellRenderer: StatusCell
      },
      {
        field: 'vulnerabilities.medium',
        headerName: 'Medium',
        width: 100,
        cellRenderer: StatusCell
      },
      {
        field: 'vulnerabilities.low',
        headerName: 'Low',
        width: 80,
        cellRenderer: StatusCell
      },
      {
        field: 'vulnerabilities',
        headerName: 'Total',
        width: 100,
        cellRenderer: StatusCell
      }
    ])

    // Reactive data for grid and deck views
    const data = computed(() => {
      const startIndex = (projectStore.currentPage - 1) * projectStore.pageSize
      const endIndex = startIndex + projectStore.pageSize
      return projects.value.slice(startIndex, endIndex)
    })

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

    let searchTimeout = null
    const debouncedSearch = () => {
      clearTimeout(searchTimeout)
      searchTimeout = setTimeout(() => {
        fetchProjects()
      }, 500)
    }

    // Use store directly instead of composable
    const fetchProjects = async () => {
      await projectStore.loadProjects()
      return projectStore.projects
    }

    const handlePageChange = (page) => {
      projectStore.currentPage = page
      fetchProjects().catch(() => {}) // Ignore errors for page changes
    }

    const handlePageSizeChange = (pageSize) => {
      projectStore.pageSize = pageSize
      fetchProjects().catch(() => {}) // Ignore errors for page size changes
    }

    const onPageChanged = (page) => {
      projectStore.currentPage = page
      fetchProjects().catch(() => {})
    }

    // Grid event handlers
    const onFilterChanged = (filters) => {
      // Use store filters instead
      projectStore.searchQuery = filters.search
      fetchProjects().catch(() => {})
    }

    const onSearch = (searchTerm) => {
      // Handle grid search
      console.log('Grid search:', searchTerm)
    }

    const onRowClick = (row, event) => {
      viewProject(row.data)
    }

    const onRowSelect = (selectedRows) => {
      console.log('Selected rows:', selectedRows)
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

    const analyzeProject = (project) => {
      // Navigate to project analysis page
      window.open(buildDTProjectFindingsUrl(project.uuid), '_blank')
    }

    const getProjectVulnerabilities = (metrics) => {
      if (!metrics) return 0
      return (metrics.critical || 0) + (metrics.high || 0) + (metrics.medium || 0) + (metrics.low || 0)
    }

    // Computed property to check if any filters are active
    const hasActiveFilters = computed(() => {
      return filters.value.search ||
             filters.value.showInactive ||
             filters.value.activityFilter !== 'all'
    })

    // Clear all filters
    const clearFilters = () => {
      filters.value = {
        search: '',
        showInactive: false,
        activityFilter: 'all'
      }
    }

    // Watch for filter changes and refetch data
    watch(filters, async () => {
      // Use store pagination instead
      projectStore.currentPage = 1 // Reset to first page when filters change
      await fetchProjects()
    }, { deep: true })

    onMounted(() => {
      fetchProjects()
    })

    return {
      data,
      totalProjects,
      isLoading,
      error,
      projectStore,
      filters,
      projectsViewMode,
      gridColumns,
      isDarkMode,
      hasActiveFilters,
      fetchProjects,
      debouncedSearch,
      handlePageChange,
      handlePageSizeChange,
      clearFilters,
      onPageChanged,
      onFilterChanged,
      onSearch,
      onRowClick,
      onRowSelect,
      viewProject,
      viewSecurityDetails,
      analyzeProject,
      getProjectVulnerabilities,
      buildDTProjectUrl,
      buildDTProjectFindingsUrl
    }
  }
}
</script>
