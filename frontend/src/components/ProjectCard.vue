<template>
  <div
    class="border border-gray-200 dark:border-gray-700 rounded-lg p-4 hover:shadow-lg transition-shadow cursor-pointer"
    @click="$emit('select', project)"
  >
    <div class="flex items-center justify-between mb-2">
      <h4 class="text-lg font-medium text-gray-900 dark:text-white truncate">
        {{ project.name }}
      </h4>
      <span
        :class="[
          'px-2 py-1 text-xs rounded-full',
          project.active
            ? 'bg-green-100 dark:bg-green-900/30 text-green-800 dark:text-green-200'
            : 'bg-gray-100 dark:bg-gray-700 text-gray-800 dark:text-gray-200'
        ]"
      >
        {{ project.active ? 'Active' : 'Inactive' }}
      </span>
    </div>

    <p v-if="project.description" class="text-sm text-gray-600 dark:text-gray-400 mb-3 line-clamp-2">
      {{ project.description }}
    </p>

    <div class="space-y-2">
      <div class="flex justify-between text-sm">
        <span class="text-gray-500 dark:text-gray-400">Version:</span>
        <span class="font-medium text-gray-900 dark:text-white">
          {{ project.version || 'latest' }}
        </span>
      </div>
      
      <div v-if="project.metrics" class="flex justify-between text-sm">
        <span class="text-gray-500 dark:text-gray-400">Components:</span>
        <span class="font-medium text-gray-900 dark:text-white">
          {{ project.metrics.vulnerableComponents || 0 }}
        </span>
      </div>
      
      <div v-if="project.metrics" class="flex justify-between text-sm">
        <span class="text-gray-500 dark:text-gray-400">Vulnerabilities:</span>
        <span class="font-medium text-gray-900 dark:text-white">
          {{ getProjectVulnerabilities(project.metrics) }}
        </span>
      </div>

      <div v-if="project.tags && project.tags.length > 0" class="flex flex-wrap gap-1 mt-2">
        <span
          v-for="tag in project.tags.slice(0, 3)"
          :key="tag"
          class="px-2 py-1 bg-blue-100 dark:bg-blue-900/30 text-blue-800 dark:text-blue-200 text-xs rounded"
        >
          {{ tag }}
        </span>
        <span
          v-if="project.tags.length > 3"
          class="px-2 py-1 bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-400 text-xs rounded"
        >
          +{{ project.tags.length - 3 }}
        </span>
      </div>

      <!-- Security Badges -->
      <div v-if="project.metrics" class="flex flex-wrap gap-1 mt-2">
        <span v-if="project.metrics.critical > 0" class="px-2 py-1 bg-red-100 dark:bg-red-900 text-red-800 dark:text-red-200 rounded text-xs">
          {{ project.metrics.critical }} Critical
        </span>
        <span v-if="project.metrics.high > 0" class="px-2 py-1 bg-orange-100 dark:bg-orange-900 text-orange-800 dark:text-orange-200 rounded text-xs">
          {{ project.metrics.high }} High
        </span>
        <span v-if="project.metrics.medium > 0" class="px-2 py-1 bg-yellow-100 dark:bg-yellow-900 text-yellow-800 dark:text-yellow-200 rounded text-xs">
          {{ project.metrics.medium }} Medium
        </span>
        <span v-if="project.metrics.low > 0" class="px-2 py-1 bg-blue-100 dark:bg-blue-900 text-blue-800 dark:text-blue-200 rounded text-xs">
          {{ project.metrics.low }} Low
        </span>
        <span v-if="getProjectVulnerabilities(project.metrics) === 0" class="px-2 py-1 bg-green-100 dark:bg-green-900 text-green-800 dark:text-green-200 rounded text-xs">
          No Vulnerabilities
        </span>
      </div>
    </div>

    <div class="flex justify-between items-center mt-4 pt-3 border-t border-gray-200 dark:border-gray-600">
      <span class="text-xs text-gray-500 dark:text-gray-400">
        Updated: {{ formatDate(project.lastActivity) }}
      </span>
      <div class="flex space-x-2">
        <button
          @click.stop="$emit('view', project)"
          class="text-blue-600 dark:text-blue-400 hover:text-blue-900 dark:hover:text-blue-300 text-sm"
        >
          View
        </button>
        <button
          v-if="!project.metrics"
          @click.stop="$emit('security-details', project)"
          class="text-orange-600 dark:text-orange-400 hover:text-orange-900 dark:hover:text-orange-300 text-sm"
        >
          Security Details
        </button>
        <button
          @click.stop="$emit('analyze', project)"
          class="text-green-600 dark:text-green-400 hover:text-green-900 dark:hover:text-green-300 text-sm"
        >
          Analyze
        </button>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'ProjectCard',
  props: {
    project: {
      type: Object,
      required: true
    }
  },
  emits: ['select', 'view', 'security-details', 'analyze'],
  methods: {
    getProjectVulnerabilities(metrics) {
      if (!metrics) return 0
      return (metrics.critical || 0) + (metrics.high || 0) + (metrics.medium || 0) + (metrics.low || 0)
    },
    formatDate(dateString) {
      if (!dateString) return 'Unknown'
      return new Date(dateString).toLocaleDateString()
    }
  }
}
</script>
