<template>
  <div
    class="border border-gray-200 dark:border-gray-700 rounded-lg p-4 hover:shadow-lg transition-shadow cursor-pointer min-w-0 h-full flex flex-col"
    @click="$emit('select', project)"
  >
    <!-- Header with responsive layout -->
    <div class="mb-2 flex-shrink-0">
      <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2">
        <h4 class="text-lg font-medium text-gray-900 dark:text-white truncate min-w-0">
          {{ project.name }}
        </h4>
        <span
          :class="[
            'px-2 py-1 text-xs rounded-full whitespace-nowrap',
            project.active
              ? 'bg-green-100 dark:bg-green-900/30 text-green-800 dark:text-green-200'
              : 'bg-gray-100 dark:bg-gray-700 text-gray-800 dark:text-gray-200'
          ]"
        >
          {{ project.active ? 'Active' : 'Inactive' }}
        </span>
      </div>
    </div>

    <p v-if="project.description" class="text-sm text-gray-600 dark:text-gray-400 mb-3 line-clamp-2 flex-shrink-0">
      {{ project.description }}
    </p>

    <!-- Main content area -->
    <div class="flex-1 overflow-y-auto">
      <div class="space-y-2">
        <!-- Responsive metric rows -->
        <div class="grid grid-cols-1 gap-1 text-xs">
          <div class="flex items-center gap-1">
            <span class="text-gray-500 dark:text-gray-400 whitespace-nowrap text-xs">Version:</span>
            <span class="font-medium text-gray-900 dark:text-white truncate flex-1">
              {{ project.version }}
            </span>
          </div>

          <div v-if="project.metrics" class="flex items-center gap-1">
            <span class="text-gray-500 dark:text-gray-400 whitespace-nowrap text-xs">Components:</span>
            <span class="font-medium text-gray-900 dark:text-white truncate flex-1">
              {{ project.metrics.vulnerableComponents || 0 }}
            </span>
          </div>
        </div>

        <div v-if="project.metrics" class="text-xs">
          <div class="flex items-center gap-1">
            <span class="text-gray-500 dark:text-gray-400 whitespace-nowrap text-xs">Vulnerabilities:</span>
            <span class="font-medium text-gray-900 dark:text-white truncate flex-1">
              {{ getProjectVulnerabilities(project.metrics) }}
            </span>
          </div>
        </div>

        <!-- Responsive tags -->
        <div v-if="project.tags && project.tags.length > 0" class="flex flex-wrap gap-1 mt-2">
          <span
            v-for="(tag, index) in project.tags"
            :key="tag"
            class="px-1 py-1 bg-blue-100 dark:bg-blue-900/30 text-blue-800 dark:text-blue-200 text-xs rounded truncate flex-shrink-0"
          >
            {{ tag.name }}
          </span>
          <!-- Only show +X if there are more tags than can be displayed -->
          <span
            v-if="project.tags.length > 3"
            class="px-1 py-1 bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-400 text-xs rounded whitespace-nowrap flex-shrink-0"
          >
            +{{ project.tags.length - 3 }}
          </span>
        </div>
      </div>
    </div>


    <!-- Security Badges - Always at Bottom -->
    <div v-if="project.metrics" class="flex flex-wrap gap-1 mt-2 pt-2 border-gray-200 dark:border-gray-600">
      <span v-if="project.metrics.critical > 0" class="px-1 py-1 bg-red-100 dark:bg-red-900 text-red-800 dark:text-red-200 rounded text-xs flex-shrink-0">
        {{ project.metrics.critical }} Critical
      </span>
      <span v-if="project.metrics.high > 0" class="px-1 py-1 bg-orange-100 dark:bg-orange-900 text-orange-800 dark:text-orange-200 rounded text-xs flex-shrink-0">
        {{ project.metrics.high }} High
      </span>
      <span v-if="project.metrics.medium > 0" class="px-1 py-1 bg-yellow-100 dark:bg-yellow-900 text-yellow-800 dark:text-yellow-200 rounded text-xs flex-shrink-0">
        {{ project.metrics.medium }} Medium
      </span>
      <span v-if="project.metrics.low > 0" class="px-1 py-1 bg-blue-100 dark:bg-blue-900 text-blue-800 dark:text-blue-200 rounded text-xs flex-shrink-0">
        {{ project.metrics.low }} Low
      </span>
      <span v-if="getProjectVulnerabilities(project.metrics) === 0" class="px-1 py-1 bg-green-100 dark:bg-green-900 text-green-800 dark:text-green-200 rounded text-xs flex-shrink-0">
        No Vulnerabilities
      </span>
    </div>
    <!-- Footer stuck to bottom -->
    <div class="mt-3 pt-2 border-t border-gray-200 dark:border-gray-600 flex-shrink-0">
      <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2">
        <span class="text-xs text-gray-500 dark:text-gray-400 truncate min-w-0">
          Updated: {{ formatDate(project.lastActivity) }}
        </span>
        <div class="flex flex-wrap gap-2">
          <button
            @click.stop="$emit('view', project)"
            class="text-blue-600 dark:text-blue-400 hover:text-blue-900 dark:hover:text-blue-300 text-sm whitespace-nowrap"
          >
            View
          </button>
          <button
            v-if="!project.metrics"
            @click.stop="$emit('security-details', project)"
            class="text-orange-600 dark:text-orange-400 hover:text-orange-900 dark:hover:text-orange-300 text-sm whitespace-nowrap"
          >
            Security Details
          </button>
          <button
            @click.stop="$emit('analyze', project)"
            class="text-green-600 dark:text-green-400 hover:text-green-900 dark:hover:text-green-300 text-sm whitespace-nowrap"
          >
            Analyze
          </button>
        </div>
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
