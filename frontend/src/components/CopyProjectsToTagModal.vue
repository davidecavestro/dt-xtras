<template>
  <div v-if="show" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-[60] p-4">
    <div class="bg-white dark:bg-gray-800 rounded-lg shadow-xl w-full max-w-2xl mx-auto max-h-[calc(100vh-2rem)] overflow-y">
      <div class="p-6">
        <div class="flex justify-between items-center mb-4">
          <h3 class="text-lg font-semibold text-gray-900 dark:text-white">
            Copy Projects from "{{ sourceTag?.name }}" to Another Tag
          </h3>
          <button
            @click="$emit('close')"
            class="text-gray-400 hover:text-gray-600 dark:text-gray-500 dark:hover:text-gray-300"
          >
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <!-- Source Tag Display -->
        <div class="mb-4 p-3 bg-gray-50 dark:bg-gray-700 rounded">
          <div class="text-sm text-gray-600 dark:text-gray-400 mb-1">Source Tag:</div>
          <div class="font-medium text-gray-900 dark:text-white">{{ sourceTag?.name }}</div>
        </div>

        <!-- Target Tag Selection -->
        <div class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Select Target Tag
            </label>
            <div class="relative">
              <input
                v-model="targetTagSearch"
                @input="filterTargetTags"
                @focus="showTargetTagDropdown = true"
                @blur="hideTargetTagDropdown"
                type="text"
                placeholder="Search and select a tag..."
                class="w-full px-4 py-3 text-base border border-gray-300 dark:border-gray-600 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
              />

              <!-- Dropdown for filtered tags -->
              <div v-if="showTargetTagDropdown" class="absolute z-[60] w-full mt-1 bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-md shadow-lg">
                <div class="max-h-96 overflow-y-auto">
                  <div
                    v-for="t in filteredTargetTags"
                    :key="t.name"
                    @click="selectTargetTag(t)"
                    class="px-4 py-3 hover:bg-gray-100 dark:hover:bg-gray-600 cursor-pointer text-gray-900 dark:text-white border-b border-gray-100 dark:border-gray-600 last:border-b-0"
                  >
                    <div class="font-medium">{{ t.name }}</div>
                    <span v-if="t.projectsCount" class="text-sm text-gray-500 dark:text-gray-400">
                      {{ t.projectsCount }} projects
                    </span>
                  </div>
                  <div v-if="filteredTargetTags.length === 0" class="px-4 py-3 text-gray-500 dark:text-gray-400">
                    No tags found
                  </div>
                </div>
              </div>
            </div>

            <!-- Selected target tag display -->
            <div v-if="targetTag" class="mt-2 p-2 bg-blue-50 dark:bg-blue-900/20 rounded border border-blue-200 dark:border-blue-800">
              <div class="text-sm text-blue-600 dark:text-blue-400">Selected target tag:</div>
              <div class="font-medium text-blue-900 dark:text-blue-300">{{ targetTag.name }}</div>
            </div>
          </div>

          <div v-if="validation.message" class="text-sm" :class="validation.valid ? 'text-green-600 dark:text-green-400' : 'text-red-600 dark:text-red-400'">
            {{ validation.message }}
          </div>
        </div>

        <div class="flex justify-end space-x-3 mt-6">
          <button
            @click="$emit('close')"
            class="px-4 py-2 bg-gray-600 text-white rounded-md hover:bg-gray-700 transition-colors"
          >
            Cancel
          </button>
          <button
            @click="confirmCopy"
            :disabled="!sourceTag || !targetTag"
            class="px-4 py-2 bg-teal-600 text-white rounded-md hover:bg-teal-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Copy Projects
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, watch } from 'vue'

export default {
  name: 'CopyProjectsToTagModal',
  props: {
    show: { type: Boolean, default: false },
    sourceTag: { type: Object, default: null },
    tags: { type: Array, default: () => [] }
  },
  // 'copy' carries the chosen target tag name; the parent performs the API call.
  emits: ['close', 'copy'],
  setup(props, { emit }) {
    const targetTag = ref(null)
    const targetTagSearch = ref('')
    const showTargetTagDropdown = ref(false)
    const filteredTargetTags = ref([])
    const validation = ref({ valid: true, message: '' })

    const filterTargetTags = () => {
      const searchTerm = targetTagSearch.value.toLowerCase()
      const sourceTagName = props.sourceTag?.name || ''
      filteredTargetTags.value = props.tags.filter(tag => {
        const isNotSourceTag = tag.name !== sourceTagName
        const matchesSearch = tag.name.toLowerCase().includes(searchTerm)
        return isNotSourceTag && matchesSearch
      })
    }

    const selectTargetTag = (tag) => {
      targetTag.value = tag
      targetTagSearch.value = tag.name
      showTargetTagDropdown.value = false
    }

    const hideTargetTagDropdown = () => {
      // Delay hiding to allow click events to register
      setTimeout(() => {
        showTargetTagDropdown.value = false
      }, 200)
    }

    const confirmCopy = () => {
      if (!props.sourceTag || !targetTag.value) {
        validation.value = { valid: false, message: 'Please select a target tag' }
        return
      }
      const sourceTagName = props.sourceTag.name || props.sourceTag
      const targetTagName = targetTag.value.name || targetTag.value
      if (sourceTagName === targetTagName) {
        validation.value = { valid: false, message: 'Cannot copy projects to the same tag' }
        return
      }
      emit('copy', targetTagName)
    }

    // Reset local state whenever the modal is (re)opened.
    watch(
      () => props.show,
      (open) => {
        if (open) {
          targetTag.value = null
          targetTagSearch.value = ''
          showTargetTagDropdown.value = false
          validation.value = { valid: true, message: '' }
          filterTargetTags()
        }
      }
    )

    return {
      targetTag,
      targetTagSearch,
      showTargetTagDropdown,
      filteredTargetTags,
      validation,
      filterTargetTags,
      selectTargetTag,
      hideTargetTagDropdown,
      confirmCopy
    }
  }
}
</script>
