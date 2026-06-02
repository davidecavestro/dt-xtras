<template>
  <div class="px-4 py-3 sm:px-6">
    <!-- No security data -->
    <div v-if="!hasData" class="bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 rounded-md p-4 mb-4">
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

    <!-- Security overview cards -->
    <div v-else class="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-3">
      <div class="bg-blue-50 dark:bg-blue-900/20 p-3 rounded-lg">
        <div class="text-center">
          <div class="text-2xl font-bold text-blue-600 dark:text-blue-300">{{ total }}</div>
          <div class="text-sm text-blue-600 dark:text-blue-400">Total Vulnerabilities</div>
        </div>
      </div>

      <div class="bg-orange-50 dark:bg-orange-900/20 p-3 rounded-lg">
        <div class="text-center">
          <div class="text-2xl font-bold text-orange-600 dark:text-orange-300">{{ critical }}</div>
          <div class="text-sm text-orange-600 dark:text-orange-400">Critical</div>
        </div>
      </div>

      <div class="bg-red-50 dark:bg-red-900/20 p-3 rounded-lg">
        <div class="text-center">
          <div class="text-2xl font-bold text-red-600 dark:text-red-300">{{ high }}</div>
          <div class="text-sm text-red-600 dark:text-red-400">High</div>
        </div>
      </div>

      <div class="bg-yellow-50 dark:bg-yellow-900/20 p-3 rounded-lg">
        <div class="text-center">
          <div class="text-2xl font-bold text-yellow-600 dark:text-yellow-300">{{ medium }}</div>
          <div class="text-sm text-yellow-600 dark:text-yellow-400">Medium</div>
        </div>
      </div>

      <div class="bg-green-50 dark:bg-green-900/20 p-3 rounded-lg">
        <div class="text-center">
          <div class="text-2xl font-bold text-green-600 dark:text-green-300">{{ low }}</div>
          <div class="text-sm text-green-600 dark:text-green-400">Low</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { AlertCircle } from '@lucide/vue'

export default {
  name: 'SecurityOverview',
  components: { AlertCircle },
  props: {
    hasData: { type: Boolean, default: false },
    total: { type: Number, default: 0 },
    critical: { type: Number, default: 0 },
    high: { type: Number, default: 0 },
    medium: { type: Number, default: 0 },
    low: { type: Number, default: 0 }
  }
}
</script>
