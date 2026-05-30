<template>
  <div class="px-4 py-6 sm:px-0">
    <div class="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
      <div class="flex justify-between items-center mb-6">
        <h2 class="text-2xl font-bold text-gray-900 dark:text-white">Vulnerabilities</h2>
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
              placeholder="Search vulnerabilities..."
              class="w-full rounded-md border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-white shadow-sm focus:border-blue-500 focus:ring-blue-500"
            />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Severity
            </label>
            <select
              v-model="filters.severity"
              @change="fetchVulnerabilities"
              class="w-full rounded-md border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-white shadow-sm focus:border-blue-500 focus:ring-blue-500"
            >
              <option value="">All Severities</option>
              <option value="CRITICAL">Critical</option>
              <option value="HIGH">High</option>
              <option value="MEDIUM">Medium</option>
              <option value="LOW">Low</option>
              <option value="INFO">Info</option>
            </select>
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Analyzer
            </label>
            <select
              v-model="filters.analyzer"
              @change="fetchVulnerabilities"
              class="w-full rounded-md border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-white shadow-sm focus:border-blue-500 focus:ring-blue-500"
            >
              <option value="">All Analyzers</option>
              <option value="OSSINDEX">OSS Index</option>
              <option value="NVD">NVD</option>
              <option value="Snyk">Snyk</option>
              <option value="VulnDB">VulnDB</option>
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
        <p class="mt-2 text-gray-600 dark:text-gray-400">Loading vulnerabilities...</p>
      </div>

      <!-- Vulnerabilities Table -->
      <div v-else class="bg-white dark:bg-gray-800 shadow overflow-hidden sm:rounded-md">
        <div class="px-4 py-5 sm:px-6">
          <h3 class="text-lg leading-6 font-medium text-gray-900 dark:text-white">
            Vulnerabilities ({{ pagination.totalItems }} total)
          </h3>
          <p class="mt-1 max-w-2xl text-sm text-gray-500 dark:text-gray-400">
            Security vulnerabilities identified across all components
          </p>
        </div>

        <div class="overflow-x-auto">
          <table class="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
            <thead class="bg-gray-50 dark:bg-gray-700">
              <tr>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                  Vulnerability
                </th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                  Severity
                </th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                  CVSS Score
                </th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                  Affected Components
                </th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                  Published
                </th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody class="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
              <tr v-for="vulnerability in data" :key="vulnerability.uuid" class="hover:bg-gray-50 dark:hover:bg-gray-700">
                <td class="px-6 py-4 whitespace-nowrap">
                  <div class="text-sm font-medium text-gray-900 dark:text-white">
                    {{ vulnerability.vulnId || vulnerability.cve || 'Unknown' }}
                  </div>
                  <div class="text-sm text-gray-500 dark:text-gray-400">
                    {{ vulnerability.source || 'Unknown Source' }}
                  </div>
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                  <span
                    :class="[
                      'px-2 py-1 inline-flex text-xs leading-5 font-semibold rounded-full',
                      getSeverityClass(vulnerability.severity)
                    ]"
                  >
                    {{ vulnerability.severity || 'UNKNOWN' }}
                  </span>
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white">
                  {{ vulnerability.cvssScore || 'N/A' }}
                  <div v-if="vulnerability.cvssVector" class="text-xs text-gray-500 dark:text-gray-400">
                    {{ vulnerability.cvssVector }}
                  </div>
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white">
                  {{ vulnerability.affectedComponents || 0 }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white">
                  {{ formatDate(vulnerability.published) }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm font-medium">
                  <button
                    @click="viewVulnerability(vulnerability)"
                    class="text-blue-600 dark:text-blue-400 hover:text-blue-900 dark:hover:text-blue-300 mr-3"
                  >
                    View
                  </button>
                  <button
                    @click="analyzeVulnerability(vulnerability)"
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
          <component :is="Shield" class="mx-auto h-12 w-12 text-gray-400" />
          <h3 class="mt-2 text-sm font-medium text-gray-900 dark:text-white">No vulnerabilities found</h3>
          <p class="mt-1 text-sm text-gray-500 dark:text-gray-400">
            {{ filters.search || filters.severity || filters.analyzer ? 'Try adjusting your filters.' : 'No vulnerabilities have been identified.' }}
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
import { ref, computed, onMounted } from 'vue'
import { AlertCircle, RefreshCw, Shield } from 'lucide-vue-next'
import Pagination from './Pagination.vue'
import { usePaginatedData } from '../composables/usePagination'
import { useVulnerabilityStore } from '../stores/vulnerabilities.js'
import { createLogger } from '../utils/logger'

export default {
  name: 'VulnerabilitiesList',
  components: {
    AlertCircle,
    RefreshCw,
    Shield,
    Pagination
  },
  setup() {
    const logger = createLogger('VulnerabilitiesList')
    const vulnerabilityStore = useVulnerabilityStore()
    const filters = ref({
      search: '',
      severity: '',
      analyzer: ''
    })

    // Tailwind classes for each severity badge.
    const classes = {
      CRITICAL: 'bg-red-100 text-red-800 dark:bg-red-900/40 dark:text-red-200',
      HIGH: 'bg-orange-100 text-orange-800 dark:bg-orange-900/40 dark:text-orange-200',
      MEDIUM: 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/40 dark:text-yellow-200',
      LOW: 'bg-blue-100 text-blue-800 dark:bg-blue-900/40 dark:text-blue-200',
      INFO: 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-200'
    }

    // Debounce search input
    let searchTimeout = null
    const debouncedSearch = () => {
      clearTimeout(searchTimeout)
      searchTimeout = setTimeout(() => {
        fetchVulnerabilities()
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
        if (filters.value.severity) {
          queryParams.severity = filters.value.severity
        }
        if (filters.value.analyzer) {
          queryParams.analyzer = filters.value.analyzer
        }

        return vulnerabilityStore.fetchVulnerabilitiesPaginated(params, queryParams)
      },
      {
        initialPageSize: 20
      }
    )

    const fetchVulnerabilities = () => {
      return fetchData().catch(error => {
        logger.error('Error fetching vulnerabilities:', error)
        pagination.setError(error.message || 'Failed to fetch vulnerabilities')
        throw error
      })
    }

    const refreshData = () => {
      return refresh()
    }

    const handlePageChange = (page) => {
      pagination.setPage(page)
      fetchVulnerabilities().catch(() => {}) // Ignore errors for page changes
    }

    const handlePageSizeChange = (pageSize) => {
      pagination.setPageSize(pageSize)
      fetchVulnerabilities().catch(() => {}) // Ignore errors for page size changes
    }

    const getSeverityClass = (severity) => {
      if (!severity) return classes.INFO
      return classes[severity] || classes.INFO
    }

    const formatDate = (dateString) => {
      if (!dateString) return 'Unknown'
      try {
        return new Date(dateString).toLocaleDateString()
      } catch (error) {
        logger.error('Date parsing error:', error)
        return 'Invalid Date'
      }
    }

    const viewVulnerability = (vulnerability) => {
      // Navigate to vulnerability details
      if (!vulnerability) return
      logger.info('View vulnerability:', vulnerability)
    }

    const analyzeVulnerability = (vulnerability) => {
      // Trigger vulnerability analysis
      if (!vulnerability) return
      logger.info('Analyze vulnerability:', vulnerability)
    }

    onMounted(() => {
      fetchVulnerabilities()
    })

    return {
      data,
      pagination,
      filters,
      fetchVulnerabilities,
      refreshData,
      handlePageChange,
      handlePageSizeChange,
      formatDate,
      getSeverityClass,
      viewVulnerability,
      analyzeVulnerability
    }
  }
}
</script>
