<template>
  <div v-if="show" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
    <div class="bg-white dark:bg-gray-800 rounded-lg shadow-xl max-w-2xl w-full mx-4 max-h-[80vh] overflow-y-auto">
      <div class="p-6">
        <div class="flex justify-between items-center mb-4">
          <h3 class="text-lg font-semibold text-gray-900 dark:text-white">
            Projects with tag: {{ tag?.name }}
          </h3>
          <div class="text-sm text-gray-600 dark:text-gray-400">
            Click project names to view in Dependency Track UI
          </div>
          <button
            @click="$emit('close')"
            class="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 cursor-pointer hover:underline transition-all"
          >
            ✕
          </button>
        </div>

        <div v-if="projects.length === 0" class="text-center py-8 text-gray-500 dark:text-gray-400">
          No projects found with this tag.
        </div>

        <div v-else class="space-y-3">
          <div
            v-for="project in projects"
            :key="project.uuid"
            class="p-3 border border-gray-200 dark:border-gray-700 rounded-lg"
          >
            <div class="flex items-start justify-between">
              <div class="flex-1 min-w-0">
                <div class="font-medium text-gray-900 dark:text-white mb-1">
                  <a
                    :href="buildDTProjectUrl(project.uuid)"
                    target="_blank"
                    class="text-blue-600 hover:text-blue-800 hover:underline"
                    title="View in Dependency Track"
                  >
                    {{ project.name }}
                  </a>
                </div>
                <div class="text-sm text-gray-600 dark:text-gray-400 flex items-center flex-wrap gap-2">
                  <span>Version: {{ project.version }}</span>
                  <a
                    :href="buildDTProjectUrl(project.uuid)"
                    target="_blank"
                    rel="noopener noreferrer"
                    class="text-xs text-blue-600 dark:text-blue-400 hover:text-blue-800 dark:hover:text-blue-300 flex items-center"
                    title="View in Dependency-Track"
                  >
                    <svg class="w-3 h-3 mr-1" fill="currentColor" viewBox="0 0 20 20">
                      <path d="M11 3a1 1 0 100 2h2.586l-6.293 6.293a1 1 0 101.414 1.414L15 6.414V9a1 1 0 102 0V4a1 1 0 00-1-1h-3z"/>
                      <path d="M5 5a2 2 0 00-2 2v8a2 2 0 002 2h8a2 2 0 002-2v-3a1 1 0 10-2 0v3H5V7h3a1 1 0 000-2H5z"/>
                    </svg>
                    DT
                  </a>
                  <span v-if="project.tags && project.tags.length > 0">
                    Tags: {{ project.tags.join(', ') }}
                  </span>
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
import { buildDTProjectUrl } from '../config.js'

export default {
  name: 'TagProjectsModal',
  props: {
    show: { type: Boolean, default: false },
    tag: { type: Object, default: null },
    projects: { type: Array, default: () => [] }
  },
  emits: ['close'],
  setup() {
    return { buildDTProjectUrl }
  }
}
</script>
