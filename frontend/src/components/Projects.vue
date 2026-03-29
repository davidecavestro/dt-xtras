<template>
  <div class="px-4 py-6 sm:px-0">
    <div class="border-4 border-dashed border-gray-200 dark:border-gray-700 rounded-lg p-6">
      <div class="flex justify-between items-center mb-6">
        <h2 class="text-2xl font-bold text-gray-900 dark:text-white">Projects</h2>
        
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

      <!-- Filters -->
      <div class="mb-6 grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
            Search projects
          </label>
          <input
            v-model="filters.search"
            @input="debouncedSearch"
            type="text"
            placeholder="Search projects..."
            class="w-full rounded-md border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-white shadow-sm focus:border-blue-500 focus:ring-blue-500"
          />
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
            Project Status
          </label>
          <select
            v-model="filters.activeOnly"
            @change="fetchProjects"
            class="w-full rounded-md border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-white shadow-sm focus:border-blue-500 focus:ring-blue-500"
          >
            <option :value="false">All Projects</option>
            <option :value="true">Active Only</option>
          </select>
        </div>
      </div>

      <!-- Loading State -->
      <div v-if="pagination.loading.value && data.length === 0" class="text-center py-8">
        <div class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        <p class="mt-2 text-gray-600 dark:text-gray-400">Loading projects...</p>
      </div>

      <!-- Projects Display -->
      <div v-else-if="data.length === 0 && !pagination.loading.value" class="text-center py-8 text-gray-500 dark:text-gray-400">
        <FolderOpen class="mx-auto h-12 w-12 text-gray-400" />
        <h3 class="mt-2 text-sm font-medium text-gray-900 dark:text-white">No projects found</h3>
        <p class="mt-1 text-sm text-gray-500 dark:text-gray-400">
          {{ filters.search || filters.activeOnly ? 'Try adjusting your filters.' : 'No projects have been created yet.' }}
        </p>
      </div>

      <!-- List View -->
      <div v-else-if="projectsViewMode === 'list'" class="max-h-96 overflow-y-auto space-y-2">
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

      <!-- Grid View -->
      <div v-else-if="projectsViewMode === 'grid'" class="overflow-y-auto">
        <vue3-datagrid
          :columns="gridColumns"
          :source="data"
          :row-height="50"
          :virtual="true"
          :page-size="pagination.pageSize.value"
          :page="pagination.currentPage.value"
          :total="pagination.totalItems.value"
          :theme="isDarkMode ? 'darkCompact' : 'compact'"
          :filter="true"
          :resize="true"
          :autoSizeColumn="{ mode: 'autoSizeOnTextOverlap' }"
          :stretch="true"
          @page-changed="onPageChanged"
          @filter-changed="onFilterChanged"
          @search="onSearch"
          @row-click="onRowClick"
          @row-select="onRowSelect"
          :show-selection="true"
          class="w-full border-gray-200 dark:border-gray-700"
          style="height: 500px;"
        >
        </vue3-datagrid>
      </div>

      <!-- Deck View -->
      <div v-else-if="projectsViewMode === 'deck'" class="max-h-96 overflow-y-auto">
        <div class="px-4 py-5 sm:px-6">
          <h3 class="text-lg leading-6 font-medium text-gray-900 dark:text-white">
            Projects ({{ pagination.totalItems.value }} total)
          </h3>
          <p class="mt-1 max-w-2xl text-sm text-gray-500 dark:text-gray-400">
            Software projects being tracked
          </p>
        </div>
        
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 p-4">
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

      <!-- Pagination (for List and Deck views) -->
      <Pagination
        v-if="pagination.totalItems.value > 0 && projectsViewMode !== 'grid'"
        :current-page="pagination.currentPage.value"
        :page-size="pagination.pageSize.value"
        :total-items="pagination.totalItems.value"
        :page-size-options="[10, 20, 50, 100]"
        @page-change="handlePageChange"
        @page-size-change="handlePageSizeChange"
        class="mt-6"
      />
    </div>
  </div>
</template>

<script>
import { ref, onMounted, watch, onUnmounted, computed } from 'vue'
import { FolderOpen } from 'lucide-vue-next'
import { usePaginatedData } from '../composables/usePagination'
import apiService from '../services/api'
import Pagination from './Pagination.vue'
import Vue3Datagrid, { VGridVueTemplate } from '@revolist/vue3-datagrid'
import ProjectCard from './ProjectCard.vue'
import NameCell from './grid-cells/NameCell.vue'
import StatusCell from './grid-cells/StatusCell.vue'
import TagsCell from './grid-cells/TagsCell.vue'
import DateCell from './grid-cells/DateCell.vue'

export default {
  name: 'Projects',
  components: {
    FolderOpen,
    Pagination,
    Vue3Datagrid,
    ProjectCard
  },
  setup() {
    const filters = ref({
      search: '',
      activeOnly: false
    })

    const projectsViewMode = ref('list') // 'list', 'grid', or 'deck'

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

    let searchTimeout = null
    const debouncedSearch = () => {
      clearTimeout(searchTimeout)
      searchTimeout = setTimeout(() => {
        fetchProjects()
      }, 500)
    }

    const { data, pagination, fetchData } = usePaginatedData(
      async (page, limit) => {
        const params = {
          pageNumber: page,
          pageSize: limit
        }
        
        const queryParams = {}
        if (filters.value.search) {
          queryParams.search = filters.value.search
        }
        if (filters.value.activeOnly) {
          queryParams.activeOnly = true
        }

        return apiService.getProjects(params, queryParams)
      },
      { initialPageSize: 20 }
    )

    const fetchProjects = () => {
      return fetchData().catch(error => {
        console.error('Error fetching projects:', error)
        pagination.setError(error.message || 'Failed to fetch projects')
        throw error
      })
    }

    const handlePageChange = (page) => {
      pagination.setPage(page)
      fetchProjects().catch(() => {}) // Ignore errors for page changes
    }

    const handlePageSizeChange = (pageSize) => {
      pagination.setPageSize(pageSize)
      fetchProjects().catch(() => {}) // Ignore errors for page size changes
    }

    // Grid event handlers
    const onPageChanged = (page) => {
      pagination.setPage(page)
      fetchProjects().catch(() => {})
    }

    const onFilterChanged = (filters) => {
      // Handle grid filters
      console.log('Grid filters changed:', filters)
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

    const getProjectVulnerabilities = (metrics) => {
      if (!metrics) return 0
      return (metrics.critical || 0) + (metrics.high || 0) + (metrics.medium || 0) + (metrics.low || 0)
    }

    onMounted(() => {
      fetchProjects()
    })

    return {
      data,
      pagination,
      filters,
      projectsViewMode,
      gridColumns,
      isDarkMode,
      fetchProjects,
      debouncedSearch,
      handlePageChange,
      handlePageSizeChange,
      onPageChanged,
      onFilterChanged,
      onSearch,
      onRowClick,
      onRowSelect,
      viewProject,
      viewSecurityDetails,
      analyzeProject,
      getProjectVulnerabilities
    }
  }
}
</script>
