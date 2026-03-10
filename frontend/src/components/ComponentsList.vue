<template>
  <div class="px-4 py-6 sm:px-0">
    <div class="border-4 border-dashed border-gray-200 dark:border-gray-700 rounded-lg p-6">
      <div class="flex justify-between items-center mb-6">
        <h2 class="text-2xl font-bold text-gray-900 dark:text-white">Components</h2>
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
        <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Search
            </label>
            <input
              v-model="filters.search"
              @input="debouncedSearch"
              type="text"
              placeholder="Search components..."
              class="w-full rounded-md border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-white shadow-sm focus:border-blue-500 focus:ring-blue-500"
            />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Project
            </label>
            <select
              v-model="filters.project"
              @change="fetchComponents"
              class="w-full rounded-md border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-white shadow-sm focus:border-blue-500 focus:ring-blue-500"
            >
              <option value="">All Projects</option>
              <option v-for="project in projects" :key="project.uuid" :value="project.uuid">
                {{ project.name }}
              </option>
            </select>
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Vulnerable Only
            </label>
            <select
              v-model="filters.vulnerableOnly"
              @change="fetchComponents"
              class="w-full rounded-md border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-white shadow-sm focus:border-blue-500 focus:ring-blue-500"
            >
              <option :value="false">All Components</option>
              <option :value="true">Vulnerable Only</option>
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
      <div v-if="pagination.loading && data.length === 0" class="text-center py-8">
        <div class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        <p class="mt-2 text-gray-600 dark:text-gray-400">Loading components...</p>
      </div>

      <!-- Components Table -->
      <div v-else class="bg-white dark:bg-gray-800 shadow overflow-hidden sm:rounded-md">
        <div class="px-4 py-5 sm:px-6">
          <h3 class="text-lg leading-6 font-medium text-gray-900 dark:text-white">
            Components ({{ pagination.totalItems }} total)
          </h3>
          <p class="mt-1 max-w-2xl text-sm text-gray-500 dark:text-gray-400">
            Software components across all projects
          </p>
        </div>

        <div class="overflow-x-auto">
          <table class="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
            <thead class="bg-gray-50 dark:bg-gray-700">
              <tr>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                  Component
                </th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                  Version
                </th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                  Project
                </th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                  Vulnerabilities
                </th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                  Risk Score
                </th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody class="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
              <tr v-for="component in data" :key="component.uuid" class="hover:bg-gray-50 dark:hover:bg-gray-700">
                <td class="px-6 py-4 whitespace-nowrap">
                  <div class="text-sm font-medium text-gray-900 dark:text-white">
                    {{ component.name || component.purl?.split('@')[0] || 'Unknown' }}
                  </div>
                  <div class="text-sm text-gray-500 dark:text-gray-400">
                    {{ component.purl || 'No PURL' }}
                  </div>
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white">
                  {{ component.version || extractVersionFromPurl(component.purl) || 'Unknown' }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white">
                  {{ component.project?.name || 'Unknown' }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                  <VulnerabilityBar :vulnerabilities="component.vulnerabilities" />
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                  <RiskScoreBadge :score="component.riskScore" />
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm font-medium">
                  <button
                    @click="viewComponent(component)"
                    class="text-blue-600 dark:text-blue-400 hover:text-blue-900 dark:hover:text-blue-300 mr-3"
                  >
                    View
                  </button>
                  <button
                    @click="analyzeComponent(component)"
                    class="text-green-600 dark:text-green-400 hover:text-green-900 dark:hover:text-green-300"
                  >
                    Analyze
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- Empty State -->
        <div v-if="data.length === 0 && !pagination.loading" class="text-center py-8 text-gray-500 dark:text-gray-400">
          <component :is="Package" class="mx-auto h-12 w-12 text-gray-400" />
          <h3 class="mt-2 text-sm font-medium text-gray-900 dark:text-white">No components found</h3>
          <p class="mt-1 text-sm text-gray-500 dark:text-gray-400">
            {{ filters.search || filters.project || filters.vulnerableOnly ? 'Try adjusting your filters.' : 'No components have been added yet.' }}
          </p>
        </div>

        <!-- Pagination -->
        <Pagination
          v-if="pagination.totalItems > 0"
          :current-page="pagination.currentPage"
          :page-size="pagination.pageSize"
          :total-items="pagination.totalItems"
          :page-size-options="[10, 20, 50, 100]"
          @page-change="handlePageChange"
          @page-size-change="handlePageSizeChange"
        />
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, computed } from 'vue'
import { AlertCircle, RefreshCw, Package } from 'lucide-vue-next'
import { usePaginatedData } from '../composables/usePagination'
import apiService from '../services/api'
import Pagination from './Pagination.vue'
import VulnerabilityBar from './VulnerabilityBar.vue'
import RiskScoreBadge from './RiskScoreBadge.vue'

export default {
  name: 'ComponentsList',
  components: {
    AlertCircle,
    RefreshCw,
    Package,
    Pagination,
    VulnerabilityBar,
    RiskScoreBadge
  },
  setup() {
    const projects = ref([])
    const filters = ref({
      search: '',
      project: '',
      vulnerableOnly: false
    })

    // Debounce search input
    let searchTimeout = null
    const debouncedSearch = () => {
      clearTimeout(searchTimeout)
      searchTimeout = setTimeout(() => {
        fetchComponents()
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
        if (filters.value.project) {
          queryParams.project = filters.value.project
        }
        if (filters.value.vulnerableOnly) {
          queryParams.vulnerableOnly = true
        }

        return apiService.getComponents(params, queryParams)
      },
      {
        initialPageSize: 20
      }
    )

    const fetchComponents = () => {
      return fetchData()
    }

    const refreshData = () => {
      return refresh()
    }

    const handlePageChange = (page) => {
      pagination.setPage(page)
      fetchComponents()
    }

    const handlePageSizeChange = (pageSize) => {
      pagination.setPageSize(pageSize)
      fetchComponents()
    }

    const extractVersionFromPurl = (purl) => {
      if (!purl) return null
      const match = purl.match(/@([^@]+)$/)
      return match ? match[1] : null
    }

    const viewComponent = (component) => {
      // Navigate to component details
      console.log('View component:', component)
    }

    const analyzeComponent = (component) => {
      // Trigger component analysis
      console.log('Analyze component:', component)
    }

    const loadProjects = async () => {
      try {
        const response = await apiService.getProjects({ pageSize: 1000 })
        projects.value = response.data || response
      } catch (error) {
        console.error('Error loading projects:', error)
      }
    }

    onMounted(() => {
      loadProjects()
      fetchComponents()
    })

    return {
      data,
      pagination,
      projects,
      filters,
      fetchComponents,
      refreshData,
      handlePageChange,
      handlePageSizeChange,
      debouncedSearch,
      extractVersionFromPurl,
      viewComponent,
      analyzeComponent
    }
  }
}
</script>
