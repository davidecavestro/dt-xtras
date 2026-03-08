<template>
  <div class="px-4 py-6 sm:px-0">
    <div class="border-4 border-dashed border-gray-200 dark:border-gray-700 rounded-lg p-6">
      <div class="flex justify-between items-center mb-6">
        <h2 class="text-2xl font-bold text-gray-900 dark:text-white">Security Dashboard</h2>
        <button
          @click="refreshData"
          :disabled="loading"
          class="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50"
        >
          <RefreshCw :class="{ 'animate-spin': loading }" class="inline w-4 h-4 mr-2" />
          Refresh
        </button>
      </div>

      <div v-if="loading" class="text-center py-8">
        <div class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        <p class="mt-2 text-gray-600 dark:text-gray-400">Loading security data...</p>
      </div>

      <div v-else-if="error" class="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-md p-4">
        <div class="flex">
          <AlertCircle class="h-5 w-5 text-red-400" />
          <div class="ml-3">
            <h3 class="text-sm font-medium text-red-800 dark:text-red-200">Error loading data</h3>
            <div class="mt-2 text-sm text-red-700 dark:text-red-300">{{ error }}</div>
          </div>
        </div>
      </div>

      <div v-else>
        <div class="bg-white dark:bg-gray-800 shadow overflow-hidden sm:rounded-md">
          <div class="px-4 py-5 sm:px-6">
            <h3 class="text-lg leading-6 font-medium text-gray-900 dark:text-white">Hierarchical Security View</h3>
            <p class="mt-1 max-w-2xl text-sm text-gray-500 dark:text-gray-400">
              Security metrics rolled up by taxonomy hierarchy
            </p>
          </div>

          <div class="border-t border-gray-200 dark:border-gray-700">
            <table class="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
              <thead class="bg-gray-50 dark:bg-gray-700">
                <tr>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                    Name
                  </th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                    Type
                  </th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                    Vulnerabilities
                  </th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                    Risk Score
                  </th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                    Severity Breakdown
                  </th>
                </tr>
              </thead>
              <tbody class="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
                <template v-for="node in securityData" :key="node.id">
                  <SecurityRow
                    :node="node"
                    :level="0"
                    :expanded-nodes="expandedNodes"
                    @toggle="toggleNode"
                  />
                </template>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import { AlertCircle, RefreshCw } from 'lucide-vue-next'
import SecurityRow from './SecurityRow.vue'
import axios from 'axios'

export default {
  name: 'Dashboard',
  components: {
    AlertCircle,
    RefreshCw,
    SecurityRow
  },
  setup() {
    const loading = ref(false)
    const error = ref('')
    const securityData = ref([])
    const expandedNodes = ref(new Set())

    const refreshData = async () => {
      loading.value = true
      error.value = ''

      try {
        const response = await axios.get('/api/aggregate')
        securityData.value = response.data
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

    onMounted(() => {
      refreshData()
    })

    return {
      loading,
      error,
      securityData,
      expandedNodes,
      refreshData,
      toggleNode
    }
  }
}
</script>
