<template>
  <div class="px-4 py-6 sm:px-0">
    <div class="bg-white dark:bg-gray-800 shadow overflow-hidden sm:rounded-md">
      <div class="flex justify-between items-center mb-6">
        <h2 class="text-2xl font-bold text-gray-900 dark:text-white">Security Dashboard</h2>
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

      <div v-else-if="!securityData || securityData.length === 0" class="text-center py-8">
        <div class="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
        <h3 class="mt-2 text-sm font-medium text-gray-900 dark:text-white">No security data available</h3>
        <p class="mt-1 text-gray-600 dark:text-gray-400">Try adjusting your filters or check your connection.</p>
      </div>

      <div v-else class="bg-white dark:bg-gray-800 shadow overflow-hidden sm:rounded-md">
        <div class="px-4 py-5 sm:px-6">
          <div class="flex justify-between items-center mb-6">
            <h3 class="text-lg leading-6 font-medium text-gray-900 dark:text-white">Security Overview</h3>
            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
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

              <div class="bg-gray-50 dark:bg-gray-700 p-4 rounded-lg">
                <div class="text-center">
                  <div class="text-3xl font-bold text-gray-600 dark:text-gray-300">{{ infoVulns }}</div>
                  <div class="text-sm text-gray-600 dark:text-gray-400">Info</div>
                </div>
              </div>
            </div>
          </div>

          <div class="mt-8">
            <h3 class="text-lg leading-6 font-medium text-gray-900 dark:text-white">Risk Score Distribution</h3>
            <div class="bg-white dark:bg-gray-800 p-4 rounded-lg">
              <div class="space-y-2">
                <div v-for="(range, count) in riskDistribution" :key="range" class="flex items-center justify-between">
                  <span class="text-sm text-gray-600 dark:text-gray-400">{{ range }}</span>
                  <div class="flex-1 bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                    <div class="h-2 bg-gray-600 dark:bg-gray-800 rounded-full" :style="{ width: `${(count / totalVulns) * 100}%` }"></div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div class="mt-8">
            <h3 class="text-lg leading-6 font-medium text-gray-900 dark:text-white">Recent Vulnerabilities</h3>
            <div class="bg-white dark:bg-gray-800 shadow overflow-hidden rounded-lg">
              <div v-if="recentVulns.length === 0" class="text-center py-8">
                <component :is="Folder" class="mx-auto h-12 w-12 text-gray-400" />
                <h3 class="mt-2 text-sm font-medium text-gray-900 dark:text-white">No vulnerabilities found</h3>
                <p class="mt-1 text-sm text-gray-500 dark:text-gray-400">Try adjusting your filters or check your connection.</p>
              </div>
              <div v-else class="divide-y divide-gray-200 dark:divide-gray-700">
                <div v-for="vuln in recentVulns" :key="vuln.id" class="p-4 hover:bg-gray-50 dark:hover:bg-gray-700">
                  <div class="flex items-start justify-between">
                    <div class="flex-1">
                      <div class="flex items-center space-x-2">
                        <div class="w-2 h-2 rounded" :class="getSeverityColor(vuln.severity)"></div>
                        <div>
                          <div class="font-medium text-gray-900 dark:text-white">{{ vuln.vulnId }}</div>
                          <div class="text-sm text-gray-500 dark:text-gray-400">{{ vuln.component }}</div>
                        </div>
                      </div>
                      <div class="text-right">
                        <div class="text-sm text-gray-500 dark:text-gray-400">{{ formatDate(vuln.published) }}</div>
                      </div>
                    </div>
                    <div class="ml-4">
                      <RiskScoreBadge :score="vuln.severity" />
                      <VulnerabilityBar :score="vuln.severity" />
                    </div>
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
import { ref, onMounted, computed } from 'vue'
import { AlertCircle, RefreshCw } from 'lucide-vue-next'
import axios from 'axios'

export default {
  name: 'Dashboard',
  components: {
    AlertCircle,
    RefreshCw
  },
  setup() {
    const loading = ref(false)
    const error = ref('')
    const securityData = ref([])
    const expandedNodes = ref(new Set())

    // Computed properties
    const totalVulnerabilities = computed(() => {
      if (!securityData.value || securityData.value.length === 0) return 0
      return securityData.value.reduce((sum, node) => sum + (node.vulnerabilities || 0), 0)
    })

    const criticalVulns = computed(() => {
      if (!securityData.value || securityData.value.length === 0) return 0
      return securityData.value.reduce((sum, node) => sum + (node.vulnerabilities || 0), 0)
    })

    const highVulns = computed(() => {
      if (!securityData.value || securityData.value.length === 0) return 0
      return securityData.value.reduce((sum, node) => sum + (node.vulnerabilities || 0), 0)
    })

    const mediumVulns = computed(() => {
      if (!securityData.value || securityData.value.length === 0) return 0
      return securityData.value.reduce((sum, node) => sum + (node.vulnerabilities || 0), 0)
    })

    const lowVulns = computed(() => {
      if (!securityData.value || securityData.value.length === 0) return 0
      return securityData.value.reduce((sum, node) => sum + (node.vulnerabilities || 0), 0)
    })

    const infoVulns = computed(() => {
      if (!securityData.value || securityData.value.length === 0) return 0
      return securityData.value.reduce((sum, node) => sum + (node.vulnerabilities || 0), 0)
    })

    const recentVulns = computed(() => {
      if (!securityData.value || !Array.isArray(securityData.value)) return []
      return securityData.value
        .flatMap(node => node.vulnerabilities || [])
        .sort((a, b) => new Date(b.published) - new Date(a.published) < 0 ? 1 : -1)
        .slice(0, 10)
    })

    const riskDistribution = computed(() => {
      if (!securityData.value || securityData.value.length === 0) return []

      const total = totalVulnerabilities.value
      const critical = criticalVulns.value
      const high = highVulns.value
      const medium = mediumVulns.value
      const low = lowVulns.value
      const info = infoVulns.value

      return [
        { range: 'Critical', count: critical, percentage: total > 0 ? Math.round((critical / total) * 100) : 0 },
        { range: 'High', count: high, percentage: total > 0 ? Math.round((high / total) * 100) : 0 },
        { range: 'Medium', count: medium, percentage: total > 0 ? Math.round((medium / total) * 100) : 0 },
        { range: 'Low', count: low, percentage: total > 0 ? Math.round((low / total) * 100) : 0 },
        { range: 'Info', count: info, percentage: total > 0 ? Math.round((info / total) * 100) : 0 }
      ]
    })

    const refreshData = async () => {
      loading.value = true
      error.value = ''

      try {
        const response = await axios.get('/api/aggregate')
        securityData.value = response.data
        // Auto-expand first few nodes for better initial view
        if (response.data && response.data.length > 0) {
          const rootNodes = response.data.filter(node => !node.parent)
          rootNodes.slice(0, 3).forEach(nodeId => expandedNodes.value.add(nodeId))
        }
      } catch (err) {
        error.value = err.response?.data?.detail || err.message || 'Failed to load security data'
      } finally {
        loading.value = false
      }
    }

    const toggleNode = (nodeId) => {
      if (expandedNodes.value.has(nodeId)) {
        expandedNodes.value.delete(nodeId)
      } else {
        expandedNodes.value.add(nodeId)
      }
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

    const formatDate = (dateString) => {
      if (!dateString) return 'Unknown'
      return new Date(dateString).toLocaleDateString()
    }

    onMounted(() => {
      refreshData()
    })

    return {
      loading,
      error,
      securityData,
      expandedNodes,
      refreshData,
      toggleNode,
      totalVulnerabilities,
      criticalVulns,
      highVulns,
      mediumVulns,
      lowVulns,
      infoVulns,
      recentVulns,
      riskDistribution
    }
  }
}
</script>
