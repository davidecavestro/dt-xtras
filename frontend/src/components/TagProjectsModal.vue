<template>
  <div
    v-if="show"
    class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4"
    @click.self="$emit('close')"
  >
    <div
      class="bg-white dark:bg-gray-800 rounded-lg shadow-xl max-w-2xl w-full flex flex-col max-h-[80vh]"
      role="dialog"
      aria-modal="true"
      aria-labelledby="tag-projects-title"
    >
      <!-- Header -->
      <div class="flex items-center justify-between gap-3 p-6 pb-3">
        <h3 id="tag-projects-title" class="text-lg font-semibold text-gray-900 dark:text-white truncate">
          Projects with tag
          <span class="font-mono">{{ tag?.name }}</span>
          <span class="text-sm font-normal text-gray-500 dark:text-gray-400">({{ projects.length }})</span>
        </h3>
        <button
          @click="$emit('close')"
          class="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 text-xl leading-none cursor-pointer shrink-0"
          title="Close"
        >
          ✕
        </button>
      </div>

      <!-- Filter (only worth showing past a handful) -->
      <div v-if="projects.length > 5" class="px-6 pb-3">
        <input
          v-model="query"
          type="text"
          placeholder="Filter projects by name…"
          class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
      </div>

      <!-- List (scrolls; header/filter stay put) -->
      <div class="flex-1 overflow-y-auto px-6 pb-6 min-h-0">
        <div v-if="projects.length === 0" class="text-center py-8 text-gray-500 dark:text-gray-400">
          No projects found with this tag.
        </div>
        <div v-else-if="filteredProjects.length === 0" class="text-center py-8 text-gray-500 dark:text-gray-400">
          No projects match “{{ query }}”.
        </div>
        <div v-else class="space-y-2">
          <div
            v-for="project in filteredProjects"
            :key="project.uuid"
            class="p-3 border border-gray-200 dark:border-gray-700 rounded-lg flex items-center justify-between gap-3"
          >
            <span class="font-medium text-gray-900 dark:text-white truncate" :title="project.name">
              {{ project.name }}
            </span>
            <span class="text-sm text-gray-500 dark:text-gray-400 whitespace-nowrap shrink-0">
              {{ project.version || 'latest' }}
            </span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, watch, onUnmounted } from 'vue'

export default {
  name: 'TagProjectsModal',
  props: {
    show: { type: Boolean, default: false },
    tag: { type: Object, default: null },
    projects: { type: Array, default: () => [] }
  },
  emits: ['close'],
  setup(props, { emit }) {
    const query = ref('')

    const filteredProjects = computed(() => {
      const q = query.value.trim().toLowerCase()
      if (!q) return props.projects
      return props.projects.filter(p => (p.name || '').toLowerCase().includes(q))
    })

    // Close on Escape; reset the filter each time the dialog opens.
    const onKeydown = (e) => {
      if (e.key === 'Escape') emit('close')
    }
    watch(
      () => props.show,
      (open) => {
        if (open) {
          query.value = ''
          document.addEventListener('keydown', onKeydown)
        } else {
          document.removeEventListener('keydown', onKeydown)
        }
      }
    )
    onUnmounted(() => document.removeEventListener('keydown', onKeydown))

    return { query, filteredProjects }
  }
}
</script>
