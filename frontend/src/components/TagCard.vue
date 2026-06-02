<template>
  <div :class="mode === 'list'
    ? 'flex items-center justify-between p-3 border border-gray-200 dark:border-gray-700 rounded-lg'
    : 'bg-white dark:bg-gray-700 rounded-lg shadow p-4 border border-gray-200 dark:border-gray-600 hover:shadow-md transition-shadow flex flex-col'">
    <div class="flex-1">
      <!-- Inline edit input -->
      <div v-if="isEditing" class="flex items-center">
        <input
          :data-tag-name="tag.name"
          :value="editName"
          @input="$emit('update:editName', $event.target.value)"
          @keyup.enter="$emit('save-edit')"
          @keyup.escape="$emit('cancel-edit')"
          class="font-medium text-gray-900 dark:text-white bg-transparent border-b border-gray-300 dark:border-gray-600 focus:border-blue-500 focus:outline-none flex-1"
          placeholder="Tag name"
        />
        <button
          @click="$emit('save-edit')"
          class="ml-2 p-1 bg-green-600 text-white text-xs rounded hover:bg-green-700 cursor-pointer hover:shadow-sm transition-all"
          title="Save"
        >
          ✓
        </button>
        <button
          @click="$emit('cancel-edit')"
          class="ml-1 p-1 bg-gray-600 text-white text-xs rounded hover:bg-gray-700 cursor-pointer hover:shadow-sm transition-all"
          title="Cancel"
        >
          ✕
        </button>
      </div>
      <div v-else>
        <div class="font-medium text-gray-900 dark:text-white flex items-center flex-wrap gap-2" :class="{ 'mb-2': mode === 'deck' }">
          {{ tag.name }}
          <span v-if="taxonomy"
                class="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium border"
                :style="taxonomyBadgeStyle">
                {{ taxonomy.name }}
          </span>
        </div>
        <div class="text-sm text-gray-600 dark:text-gray-400">
          Used by {{ tag.projectsCount || 0 }} projects
        </div>
      </div>
    </div>

    <div :class="mode === 'list'
      ? 'flex gap-1 p-2 flex-shrink-0'
      : 'flex justify-end gap-1 pt-2 mt-2 border-t border-gray-200 dark:border-gray-600'">
      <button
        @click="$emit('view', tag)"
        class="p-1 bg-blue-600 text-white text-xs rounded hover:bg-blue-700 inline-flex items-center justify-center transition-all cursor-pointer hover:shadow-sm"
        title="View Projects"
      >
        <Folder class="w-3 h-3" />
      </button>
      <button
        @click="$emit('edit', tag)"
        class="p-1 bg-yellow-600 text-white text-xs rounded hover:bg-yellow-700 inline-flex items-center justify-center transition-all cursor-pointer hover:shadow-sm"
        title="Edit Tag"
      >
        <Edit2 class="w-3 h-3" />
      </button>
      <button
        v-if="belongsToTaxonomy"
        @click="$emit('aided-edit', tag)"
        class="p-1 bg-purple-600 text-white text-xs rounded hover:bg-purple-700 inline-flex items-center justify-center transition-all cursor-pointer hover:shadow-sm"
        title="Aided Edit"
      >
        <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-3 7h3m-3 4h3m-6-4h.01M9 16h.01"></path>
        </svg>
      </button>
      <button
        @click="$emit('clone', tag)"
        class="p-1 bg-indigo-600 text-white text-xs rounded hover:bg-indigo-700 inline-flex items-center justify-center transition-all cursor-pointer hover:shadow-sm"
        title="Clone Tag"
      >
        <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012-2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z"></path>
        </svg>
      </button>
      <button
        v-if="tag.projectsCount > 0"
        @click="$emit('copy', tag)"
        class="p-1 bg-teal-600 text-white text-xs rounded hover:bg-teal-700 inline-flex items-center justify-center transition-all cursor-pointer hover:shadow-sm"
        title="Copy Projects to Tag"
      >
        <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-2a2 2 0 00-2-2h-2M8 7a2 2 0 002 2h2a2 2 0 002-2m-3 7h3m-3 4h3m-6-4h.01M9 16h.01"></path>
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 21l-4-4 4-4M4 13l4 4 4 4"></path>
        </svg>
      </button>
      <button
        @click="$emit('delete', tag)"
        class="p-1 bg-red-600 text-white text-xs rounded hover:bg-red-700 inline-flex items-center justify-center transition-all cursor-pointer hover:shadow-sm"
        title="Delete"
      >
        <Trash2 class="w-3 h-3" />
      </button>
    </div>
  </div>
</template>

<script>
import { Folder, Edit2, Trash2 } from '@lucide/vue'

export default {
  name: 'TagCard',
  components: { Folder, Edit2, Trash2 },
  props: {
    tag: { type: Object, required: true },
    mode: { type: String, default: 'list' }, // 'list' or 'deck'
    isEditing: { type: Boolean, default: false },
    editName: { type: String, default: '' },
    taxonomy: { type: Object, default: null },
    taxonomyBadgeStyle: { type: Object, default: () => ({}) },
    belongsToTaxonomy: { type: Boolean, default: false }
  },
  emits: ['update:editName', 'save-edit', 'cancel-edit', 'view', 'edit', 'aided-edit', 'clone', 'copy', 'delete']
}
</script>
