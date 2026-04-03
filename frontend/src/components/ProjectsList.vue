<template>
  <div class="px-4 py-6 sm:px-0">
    <div class="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
      <div class="flex justify-between items-center mb-6">
        <h2 class="text-2xl font-bold text-gray-900 dark:text-white">Projects</h2>
        <button
          @click="refreshData"
          :disabled="pagination.loading"
          class="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50"
        >
          <RefreshCw :class="{ 'animate-spin': pagination.loading }" class="inline w-4 h-4 mr-2" />
          Refresh
        </button>
      </div>

      <!-- Filters -->
      <div class="bg-white dark:bg-gray-800 shadow rounded-lg p-4 mb-6">
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Search
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
              Active Only
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
      </div>

      <!-- Error State -->
      <div v-if="pagination.error" class="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-md p-4 mb-6">
        <div class="flex">
          <AlertCircle class="h-5 w-5 text-red-400" />
          <div class="ml-3">
            <h3 class="text-sm font-medium text-red-800 dark:text-red-200">Error loading data</h3>
            <div class="mt-2 text-sm text-red-700 dark:text-red-300">{{ pagination.error }}</div>
          </div>
        </div>
      </div>

      <!-- Loading State -->
      <div v-if="pagination.loading.value && data.length === 0" class="text-center py-8">
        <div class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        <p class="mt-2 text-gray-600 dark:text-gray-400">Loading projects...</p>
      </div>

      <!-- Projects Grid -->
      <div v-else class="bg-white dark:bg-gray-800 shadow overflow-hidden sm:rounded-md">
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

        <!-- Empty State -->
        <div v-if="data.length === 0 && !pagination.loading.value" class="text-center py-8 text-gray-500 dark:text-gray-400">
          <Folder class="mx-auto h-12 w-12 text-gray-400" />
          <h3 class="mt-2 text-sm font-medium text-gray-900 dark:text-white">No projects found</h3>
          <p class="mt-1 text-sm text-gray-500 dark:text-gray-400">
            {{ filters.search || filters.activeOnly ? 'Try adjusting your filters.' : 'No projects have been created yet.' }}
          </p>
        </div>

        <!-- Pagination -->
        <Pagination
          v-if="pagination.totalItems.value > 0"
          :current-page="pagination.currentPage.value"
          :page-size="pagination.pageSize.value"
          :total-items="pagination.totalItems.value"
          :page-size-options="[10, 20, 50, 100]"
          @page-change="handlePageChange"
          @page-size-change="handlePageSizeChange"
        />
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, watch } from 'vue'
import { AlertCircle, RefreshCw, Folder } from 'lucide-vue-next'
import { usePaginatedData } from '../composables/usePagination'
import apiService from '../services/api'
import Pagination from './Pagination.vue'
import RiskScoreBadge from './RiskScoreBadge.vue'
import { useTagStore } from '../stores/tags.js'
import ProjectCard from './ProjectCard.vue'

export default {
  name: 'ProjectsList',
  components: {
    AlertCircle,
    RefreshCw,
    Folder,
    Pagination,
    ProjectCard,
    RiskScoreBadge
  },
  setup() {
    const filters = ref({
      search: '',
      activeOnly: false
    })

    const tagStore = useTagStore()

    // Debounce search input
    let searchTimeout = null
    const debouncedSearch = () => {
      clearTimeout(searchTimeout)
      searchTimeout = setTimeout(() => {
        fetchProjects()
      }, 500)
    }

    // Use the paginated data composable
    const { data, pagination, fetchData, refresh } = usePaginatedData(
      async (params) => {
        const queryParams = {}

        // Apply filters
        if (filters.value.search) {
          queryParams.search = filters.value.search
        }
        if (filters.value.activeOnly) {
          queryParams.active_only = true
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

    const refreshData = () => {
      return refresh()
    }

    const handlePageChange = (page) => {
      pagination.setPage(page)
      fetchProjects().catch(() => {}) // Ignore errors for page changes
    }

    const handlePageSizeChange = (pageSize) => {
      pagination.setPageSize(pageSize)
      fetchProjects().catch(() => {}) // Ignore errors for page size changes
    }

    const formatDate = (dateString) => {
      if (!dateString) return 'Never'
      return new Date(dateString).toLocaleDateString()
    }

    const viewProject = (project) => {
      // Navigate to project details
      if (!project) return
      console.log('View project:', project)
    }

    const viewSecurityDetails = (project) => {
      // Fetch and display security details from aggregate endpoint
      if (!project) return
      console.log('View security details for project:', project)
      // TODO: Navigate to security details or show modal
    }

    const analyzeProject = (project) => {
      // Trigger project analysis
      if (!project) return
      console.log('Analyze project:', project)
    }

    onMounted(() => {
      fetchProjects()
    })

    // Watch for tag updates and refresh projects
    watch(
      () => tagStore.lastUpdate,
      () => {
        console.log('Tag store updated, refreshing projects...')
        fetchProjects()
      }
    )

    return {
      data,
      pagination,
      filters,
      fetchProjects,
      refreshData,
      handlePageChange,
      handlePageSizeChange,
      formatDate,
      viewProject,
      viewSecurityDetails,
      analyzeProject
    }
  }
}
</script>
