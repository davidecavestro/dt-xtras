<template>
  <div
    class="border border-gray-200 dark:border-gray-700 rounded-lg p-3 hover:shadow-lg transition-shadow min-w-0 h-full flex flex-col cursor-pointer"
    @click="$emit('select', project)"
  >
    <!-- Compact Header -->
    <div class="flex items-start justify-between gap-2 mb-2">
      <h4 class="text-base font-medium text-gray-900 dark:text-white truncate min-w-0 flex-1" :title="project.name">
        {{ project.name }}
      </h4>
      <span
        :class="[
          'px-1.5 py-0.5 text-xs rounded-full whitespace-nowrap shrink-0',
          project.active
            ? 'bg-green-100 dark:bg-green-900/30 text-green-800 dark:text-green-200'
            : 'bg-gray-100 dark:bg-gray-700 text-gray-800 dark:text-gray-200'
        ]"
      >
        {{ project.active ? 'Active' : 'Inactive' }}
      </span>
    </div>

    <!-- Compact Metrics Row -->
    <div v-if="project.metrics" class="flex items-center gap-3 text-xs mb-2">
      <span class="text-gray-500 dark:text-gray-400">
        {{ project.version || 'latest' }}
      </span>
      <span class="text-gray-300 dark:text-gray-600">|</span>
      <span class="text-gray-500 dark:text-gray-400">
        <span class="font-medium text-gray-900 dark:text-white" title="Vulnerable components">{{ project.metrics.vulnerableComponents || 0 }}</span> / <span class="font-medium text-gray-900 dark:text-white" title="Total components">{{ project.metrics.components || project.metrics.vulnerableComponents || 0 }}</span> vuln. comp.
      </span>
      <span class="text-gray-300 dark:text-gray-600">|</span>
      <span class="text-gray-500 dark:text-gray-400">
        <span class="font-medium text-gray-900 dark:text-white" title="Total vulnerabilities">{{ getProjectVulnerabilities(project.metrics) }}</span> vulns
      </span>
    </div>
    <div v-else class="flex items-center gap-2 text-xs mb-2">
      <span class="text-gray-500 dark:text-gray-400" title="Version">{{ project.version || 'latest' }}</span>
    </div>

    <!-- Security Badges & Tags -->
    <div class="flex flex-wrap gap-1 mb-2">
      <!-- Security Badges -->
      <template v-if="project.metrics">
        <span v-if="project.metrics.critical > 0" class="px-1.5 py-0.5 bg-red-100 dark:bg-red-900 text-red-800 dark:text-red-200 rounded text-xs font-medium">
          {{ project.metrics.critical }} C
        </span>
        <span v-if="project.metrics.high > 0" class="px-1.5 py-0.5 bg-orange-100 dark:bg-orange-900 text-orange-800 dark:text-orange-200 rounded text-xs font-medium">
          {{ project.metrics.high }} H
        </span>
        <span v-if="project.metrics.medium > 0" class="px-1.5 py-0.5 bg-yellow-100 dark:bg-yellow-900 text-yellow-800 dark:text-yellow-200 rounded text-xs font-medium">
          {{ project.metrics.medium }} M
        </span>
        <span v-if="project.metrics.low > 0" class="px-1.5 py-0.5 bg-blue-100 dark:bg-blue-900 text-blue-800 dark:text-blue-200 rounded text-xs font-medium">
          {{ project.metrics.low }} L
        </span>
        <span v-if="getProjectVulnerabilities(project.metrics) === 0" class="px-1.5 py-0.5 bg-green-100 dark:bg-green-900 text-green-800 dark:text-green-200 rounded text-xs font-medium">
          No Vulns
        </span>
      </template>

      <!-- Tags -->
      <template v-if="project.tags && project.tags.length > 0">
        <span
          v-for="tag in project.tags.slice(0, 3)"
          :key="tag.name || tag"
          class="inline-flex items-center px-1.5 py-0.5 rounded-full text-xs font-medium border truncate flex-shrink-0"
          :class="getTagStyle(tag)"
          :style="getTagDynamicStyle(tag)"
        >
          {{ tag.name || tag }}
        </span>
        <span
          v-if="project.tags.length > 3"
          class="px-1.5 py-0.5 bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-400 text-xs rounded-full flex-shrink-0"
        >
          +{{ project.tags.length - 3 }}
        </span>
      </template>
    </div>

    <!-- Compact Footer -->
    <div class="mt-auto pt-2 border-t border-gray-200 dark:border-gray-600 flex items-center justify-between gap-2">
      <span class="text-xs text-gray-500 dark:text-gray-400 truncate">
        {{ formatDate(project.lastActivity) }}
      </span>
      <div class="flex items-center gap-2 shrink-0">
        <button
          @click.stop="$emit('view', project)"
          class="text-xs text-blue-600 dark:text-blue-400 hover:text-blue-900 dark:hover:text-blue-300"
        >
          View
        </button>
        <button
          @click.stop="$emit('analyze', project)"
          class="text-xs text-green-600 dark:text-green-400 hover:text-green-900 dark:hover:text-green-300"
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
    },
    getTagStyle: {
      type: Function,
      default: () => 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300'
    },
    getTagDynamicStyle: {
      type: Function,
      default: () => ({})
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
