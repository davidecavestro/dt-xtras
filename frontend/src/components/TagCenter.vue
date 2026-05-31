<template>
  <div class="px-4 sm:px-0">
    <div class="bg-white dark:bg-gray-800 rounded-lg shadow p-4">
      <div class="flex justify-between items-start mb-6">
        <div>
          <h2 class="text-2xl font-bold text-gray-900 dark:text-white">Tag Center</h2>
          <p class="text-sm text-gray-600 dark:text-gray-400 mt-1">
            Manage tags and link them to Dependency-Track projects
          </p>
        </div>
        <button
          @click="refreshTags"
          class="px-3 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 transition-all flex items-center gap-2 cursor-pointer hover:shadow-md"
          title="Refresh tags"
        >
          <RefreshCw class="w-4 h-4" :class="{ 'animate-spin': tagsLoading }"/>
          Refresh
        </button>
      </div>

      <!-- Create Tag Button -->
      <div class="mb-6">
        <button
          @click="showCreateTagModal = true"
          class="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-all cursor-pointer hover:shadow-md"
        >
          Create Tag
        </button>
      </div>
    </div>

    <!-- Existing Tags Management -->
    <div class="bg-white dark:bg-gray-800 rounded-lg shadow p-4 mt-6">
      <div class="flex justify-between items-center mb-4">
        <h2 class="text-lg font-semibold text-gray-900 dark:text-white">Existing Tags</h2>
        <div class="flex items-center gap-2">
          <div class="text-sm text-gray-600 dark:text-gray-400">
            {{ tags.length }} tags
          </div>
          <!-- View Mode Controls -->
          <div class="flex items-center space-x-2">
            <button
              @click="tagsViewMode = 'list'"
              :class="[
                'px-3 py-1 text-sm rounded-md cursor-pointer hover:shadow-md transition-all',
                tagsViewMode === 'list'
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300'
              ]"
            >
              <List class="w-4 h-4" />
            </button>
            <button
              @click="tagsViewMode = 'deck'"
              :class="[
                'px-3 py-1 text-sm rounded-md cursor-pointer hover:shadow-md transition-all',
                tagsViewMode === 'deck'
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300'
              ]"
            >
              <Square class="w-4 h-4" />
            </button>
            <!-- <button
              @click="tagsViewMode = 'grid'"
              :class="[
                'px-3 py-1 text-sm rounded-md',
                tagsViewMode === 'grid'
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300'
              ]"
            >
              <GridIcon class="w-4 h-4" />
            </button> -->
          </div>
        </div>
      </div>

      <!-- Search and Filters -->
      <div v-if="tags.length > 0" class="bg-white dark:bg-gray-800 rounded-lg shadow p-4 mb-6">
        <div class="flex flex-col sm:flex-row gap-4">
          <!-- Taxonomy Filter -->
          <div class="sm:w-48">
            <select
              v-model="selectedTaxonomy"
              @change="setTaxonomyFilter(selectedTaxonomy)"
              class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
            >
              <option value="">All Taxonomies</option>
              <option v-for="taxonomy in taxonomies" :key="taxonomy.id" :value="taxonomy.id">
                {{ taxonomy.name }}
              </option>
            </select>
          </div>

          <!-- Search -->
          <div class="flex-1">
            <input
              v-model="searchQuery"
              @input="setSearchQuery(searchQuery)"
              type="text"
              placeholder="Search tags..."
              class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
            />
          </div>

          <!-- Clear Filters -->
          <button
            @click="clearFilters"
            class="px-4 py-2 bg-gray-600 text-white rounded-md hover:bg-gray-700 transition-all cursor-pointer hover:shadow-md"
          >
            Clear Filters
          </button>
        </div>
      </div>

      <!-- Pagination Controls -->
      <div v-if="totalPages > 1" class="flex items-center justify-between mb-6 px-4">
        <div class="flex items-center space-x-4">
          <div class="text-sm text-gray-700 dark:text-gray-300 hidden sm:block">
            Showing {{ paginatedTags.length }} of {{ totalTags }} tags
          </div>
          <div class="flex items-center space-x-2">
            <label class="text-sm text-gray-600 dark:text-gray-400">Page size:</label>
            <select
              v-model="pageSize"
              @change="setPageSize(pageSize)"
              class="text-sm border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-white px-2 py-1"
            >
              <option :value="10">10</option>
              <option :value="20">20</option>
              <option :value="50">50</option>
              <option :value="100">100</option>
            </select>
          </div>
        </div>
        <div class="flex items-center space-x-2">
          <button
            @click="previousPage"
            :disabled="!hasPreviousPage"
            class="px-3 py-1 text-sm border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700 disabled:opacity-50 disabled:cursor-not-allowed cursor-pointer hover:shadow-md transition-all"
          >
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
            </svg>
          </button>

          <!-- Page Numbers -->
          <div class="flex items-center space-x-1">
            <button
              v-for="page in Math.min(5, totalPages)"
              :key="page"
              @click="goToPage(page)"
              :class="[
                'px-3 py-1 text-sm border rounded-md cursor-pointer hover:shadow-md transition-all',
                page === currentPage
                  ? 'bg-blue-600 text-white border-blue-600'
                  : 'bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-300 border-gray-300 dark:border-gray-600 hover:bg-gray-50 dark:hover:bg-gray-700'
              ]"
            >
              {{ page }}
            </button>
            <span v-if="totalPages > 5" class="px-2 text-gray-500">...</span>
            <button
              v-if="totalPages > 5"
              @click="goToPage(totalPages)"
              :class="[
                'px-3 py-1 text-sm border rounded-md cursor-pointer hover:shadow-md transition-all',
                totalPages === currentPage
                  ? 'bg-blue-600 text-white border-blue-600'
                  : 'bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-300 border-gray-300 dark:border-gray-600 hover:bg-gray-50 dark:hover:bg-gray-700'
              ]"
            >
              {{ totalPages }}
            </button>
          </div>

          <button
            @click="nextPage"
            :disabled="!hasNextPage"
            class="px-3 py-1 text-sm border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700 disabled:opacity-50 disabled:cursor-not-allowed cursor-pointer hover:shadow-md transition-all"
          >
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
            </svg>
          </button>
        </div>
      </div>

      <!-- Tags List -->
      <div v-if="tags.length === 0" class="text-center py-8 text-gray-500 dark:text-gray-400">
        No tags created yet. Create your first tag above.
      </div>

      <!-- List View -->
      <div v-else-if="tagsViewMode === 'list'" class="space-y-3">
        <TagCard
          v-for="tag in paginatedTags"
          :key="tag.name"
          mode="list"
          :tag="tag"
          :is-editing="editingTag && editingTag.name === tag.name"
          v-model:edit-name="editingTagName"
          :taxonomy="getTagTaxonomy(tag)"
          :taxonomy-badge-style="getTagTaxonomy(tag) ? getTaxonomyBadgeStyle(getTagTaxonomy(tag)) : {}"
          :belongs-to-taxonomy="tagBelongsToTaxonomy(tag)"
          @view="viewTagProjects"
          @edit="startEditTag"
          @aided-edit="startAidedEditTag"
          @clone="startCloneTag"
          @copy="startCopyProjectsToTag"
          @delete="handleDeleteTag"
          @save-edit="saveEditTag"
          @cancel-edit="cancelEditTag"
        />
      </div>

      <!-- Grid View -->
      <div v-else-if="tagsViewMode === 'grid'" class="overflow-y-auto">
        <vue3-datagrid
          :columns="gridColumns"
          :source="paginatedTags"
          :row-height="60"
          :virtual="false"
          :theme="isDarkMode ? 'darkCompact' : 'compact'"
          :filter="false"
          :resize="true"
          :autoSizeColumn="{ mode: 'autoSizeOnTextOverlap' }"
          :stretch="true"
          :readonly="true"
          :pagination="false"
        />

      </div>

      <!-- Deck View (Current Default) -->
      <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        <TagCard
          v-for="tag in paginatedTags"
          :key="tag.name"
          mode="deck"
          :tag="tag"
          :is-editing="editingTag && editingTag.name === tag.name"
          v-model:edit-name="editingTagName"
          :taxonomy="getTagTaxonomy(tag)"
          :taxonomy-badge-style="getTagTaxonomy(tag) ? getTaxonomyBadgeStyle(getTagTaxonomy(tag)) : {}"
          :belongs-to-taxonomy="tagBelongsToTaxonomy(tag)"
          @view="viewTagProjects"
          @edit="startEditTag"
          @aided-edit="startAidedEditTag"
          @clone="startCloneTag"
          @copy="startCopyProjectsToTag"
          @delete="handleDeleteTag"
          @save-edit="saveEditTag"
          @cancel-edit="cancelEditTag"
        />
      </div>
    </div>


    <!-- Projects Modal -->
    <TagProjectsModal
      :show="showProjectsModal"
      :tag="selectedTag"
      :projects="tagProjects"
      @close="closeProjectsModal"
    />

    <!-- Create Tag Modal (Aided Edit) -->
    <div v-if="showCreateTagModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-white dark:bg-gray-800 rounded-lg shadow-xl max-w-4xl w-full mx-4 max-h-[80vh] overflow-y-auto">
        <div class="p-6">
          <div class="flex justify-between items-center mb-4">
            <h3 class="text-lg font-semibold text-gray-900 dark:text-white">
              {{ editingTag ? 'Edit Tag' : (selectedTaxonomy ? `Create Tag for ${selectedTaxonomy}` : 'Create Tag') }}
            </h3>
            <button
              @click="closeCreateTagModal"
              class="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 cursor-pointer hover:underline transition-all"
            >
              ✕
            </button>
          </div>

          <!-- Free-form Tag Creation (when no taxonomy selected) -->
          <div v-if="!selectedTaxonomy" class="space-y-4">
            <!-- Pattern Display -->
            <div class="mb-4 p-3 bg-gray-100 dark:bg-gray-700 rounded-lg">
              <div class="text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Pattern:</div>
              <div class="text-sm bg-gray-200 dark:bg-gray-600 px-3 py-2 rounded text-gray-800 dark:text-gray-200 font-mono break-all hover:bg-gray-300 dark:hover:bg-gray-600 transition-colors">
                Free-form tag (no pattern restrictions)
              </div>
            </div>

            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300">
              Tag Name
            </label>
            <input
              v-model="newTag"
              type="text"
              @input="validateTag"
              class="mt-1 block w-full rounded-md border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-white shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
              placeholder="Enter new tag name..."
            />
            <div v-if="tagValidation.message" :class="[
              'mt-1 text-xs',
              tagValidation.valid ? 'text-green-600 dark:text-green-400' : 'text-red-600 dark:text-red-400'
            ]">
              {{ tagValidation.message }}
            </div>
          </div>

          <!-- Dynamic Tag Builder (when taxonomy selected) -->
          <div v-else class="space-y-4">
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300">
              Build Tag
            </label>

            <div class="flex flex-wrap items-center gap-2 p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
              <template v-for="(part, index) in tagBuilderParts" :key="index">
                <!-- Static text part -->
                <span v-if="part.type === 'static'" class="text-gray-700 dark:text-gray-300 font-medium">
                  {{ part.value }}
                </span>

                <!-- Dropdown for capture group with existing tags -->
                <select
                  v-else-if="part.type === 'dropdown'"
                  v-model="part.value"
                  class="px-3 py-2 border border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-white rounded-md shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
                >
                  <option value="">Select {{ part.name }}...</option>
                  <option v-for="option in part.options" :key="option.value || option" :value="option.value || option">
                    {{ option.text || option }}
                  </option>
                </select>

                <!-- Text field for capture group without existing tags -->
                <input
                  v-else-if="part.type === 'text'"
                  v-model="part.value"
                  type="text"
                  :placeholder="`Enter ${part.name}...`"
                  class="px-3 py-2 border border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-white rounded-md shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
                />
              </template>
            </div>

            <!-- Generated Tag Preview -->
            <div class="mt-4">
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Generated Tag
              </label>
              <div class="p-3 bg-gray-100 dark:bg-gray-800 rounded-md">
                <span class="font-mono text-gray-900 dark:text-white">
                  {{ generatedTag || 'Complete all fields to see tag...' }}
                </span>
              </div>
            </div>
          </div>

            <!-- Action Buttons -->
          <div class="mt-6 flex gap-2">
            <button
              @click="saveCreateTagModal"
              :disabled="selectedTaxonomy ? (editingTag ? !canEditTag : !canCreateTag) : !tagValidation.valid"
              class="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-all cursor-pointer hover:shadow-md"
            >
              {{ editingTag ? 'Update Tag' : 'Create Tag' }}
            </button>
            <button
              @click="closeCreateTagModal"
              class="px-4 py-2 bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-md hover:bg-gray-300 dark:hover:bg-gray-600 transition-all cursor-pointer hover:shadow-md"
            >
              Cancel
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Clone Tag Modal -->
    <div v-if="showCloneTagModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-white dark:bg-gray-800 rounded-lg shadow-xl max-w-4xl w-full mx-4 max-h-[80vh] overflow-y-auto">
        <div class="p-6">
          <div class="flex justify-between items-center mb-4">
            <h3 class="text-lg font-semibold text-gray-900 dark:text-white">Clone Tag: {{ cloningTag?.name }}</h3>
            <button
              @click="closeCloneTagModal"
              class="text-gray-400 hover:text-gray-500 dark:text-gray-500 dark:hover:text-gray-400 cursor-pointer hover:underline transition-all"
            >
              <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>

          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <!-- Tag Input - Only show when no capture groups -->
            <div v-if="!hasCaptureGroups">
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-300">
                New Tag Name
                <span class="ml-2 text-xs text-gray-500 dark:text-gray-400">
                  (e.g., brand:qualcoz, region:eu, anybnd:2026.5)
                </span>
              </label>
              <input
                ref="cloneTagInput"
                data-clone-tag-input
                v-model="cloneTagName"
                type="text"
                class="mt-1 block w-full rounded-md border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-white shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
                placeholder="Enter new tag name..."
                @input="validateCloneTag"
              />
              <div v-if="cloneTagValidation.message" :class="[
                'mt-1 text-xs',
                cloneTagValidation.valid ? 'text-green-600 dark:text-green-400' : 'text-red-600 dark:text-red-400'
              ]">
                {{ cloneTagValidation.message }}
              </div>
            </div>

            <!-- Project Linking Option -->
            <div v-if="cloningTag.projectsCount" class="bg-gray-50 dark:bg-gray-700 rounded-lg p-4">
              <h3 class="text-sm font-semibold text-gray-900 dark:text-white mb-3">Project Linking</h3>
              <div class="space-y-3">
                <div class="flex items-center">
                  <input
                    id="linkProjects"
                    v-model="linkProjects"
                    type="checkbox"
                    class="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 dark:border-gray-600 rounded dark:bg-gray-700"
                  />
                  <label for="linkProjects" class="ml-2 text-sm text-gray-700 dark:text-gray-300">
                    Link projects from original tag
                  </label>
                </div>
                <div v-if="cloningTag" class="text-xs text-gray-500 dark:text-gray-400">
                  Original tag is linked to {{ cloningTag.projectsCount || 0 }} projects
                </div>
              </div>
            </div>
          </div>

          <!-- Taxonomy Patterns (if original tag belongs to taxonomy) -->
          <div v-if="cloningTag && cloningTag.taxonomy" class="mt-4 bg-gray-50 dark:bg-gray-700 rounded-lg p-4">
            <h3 class="text-sm font-semibold text-gray-900 dark:text-white mb-3">Taxonomy Pattern</h3>
            <div class="flex items-start mb-4">
              <span class="font-medium text-gray-700 dark:text-gray-300 text-sm mr-2 min-w-0">
                {{ taxonomies.find(t => t.id === cloningTag.taxonomy)?.name || cloningTag.taxonomy }}:
              </span>
              <code class="text-xs bg-gray-100 dark:bg-gray-600 px-2 py-1 rounded text-gray-800 dark:text-gray-200 break-all">
                {{ taxonomies.find(t => t.id === cloningTag.taxonomy)?.regex_pattern || 'Pattern not found' }}
              </code>
            </div>

            <!-- Dynamic Tag Builder for Clone - Only show when there are capture groups -->
            <div v-if="hasCaptureGroups" class="space-y-4">
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-300">
                Build Clone
              </label>

              <div class="flex flex-wrap items-center gap-2 p-4 bg-gray-50 dark:bg-gray-600 rounded-lg">
                <template v-for="(part, index) in tagBuilderParts" :key="index">
                  <!-- Static text part -->
                  <span v-if="part.type === 'static'" class="text-gray-700 dark:text-gray-300 font-medium">
                    {{ part.value }}
                  </span>

                  <!-- Dropdown for capture group with existing tags -->
                  <select
                    v-else-if="part.type === 'dropdown'"
                    v-model="part.value"
                    :data-tag-builder-field="index === 0 ? 'first' : null"
                    class="px-3 py-2 border border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-white rounded-md shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
                  >
                    <option value="">Select {{ part.name }}...</option>
                    <option v-for="option in part.options" :key="option.value || option" :value="option.value || option">
                      {{ option.text || option }}
                    </option>
                  </select>

                  <!-- Text field for capture group without existing tags -->
                  <input
                    v-else-if="part.type === 'text'"
                    v-model="part.value"
                    :data-tag-builder-field="index === 0 ? 'first' : null"
                    type="text"
                    :placeholder="'Enter ' + part.name + '...'"
                    class="px-3 py-2 border border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-white rounded-md shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
                  />
                </template>
              </div>

              <!-- Generated Tag Preview -->
              <div class="mt-4 p-3 bg-gray-100 dark:bg-gray-700 rounded-lg">
                <div class="text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Preview:</div>
                <code class="text-sm bg-gray-200 dark:bg-gray-600 px-3 py-2 rounded text-gray-800 dark:text-gray-200 font-mono break-all">
                  {{ generatedTag || 'Start building your tag...' }}
                </code>
              </div>
            </div>
          </div>

          <!-- Action Buttons -->
          <div class="mt-6 flex justify-end gap-2">
            <button
              @click="closeCloneTagModal"
              class="px-4 py-2 bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-md hover:bg-gray-300 dark:hover:bg-gray-600 transition-colors"
            >
              Cancel
            </button>
            <!-- Show simple clone button when no capture groups -->
            <button
              v-if="!hasCaptureGroups"
              @click="cloneTag"
              :disabled="!cloneTagValidation.valid || !cloneTagName.trim()"
              class="px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
            >
              Clone Tag
            </button>
            <!-- Show tag builder clone button when has capture groups -->
            <button
              v-else
              @click="cloneTagFromBuilder"
              :disabled="!generatedTag"
              class="px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
            >
              Clone Tag
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Copy Projects to Tag Modal -->
    <CopyProjectsToTagModal
      :show="showCopyProjectsModal"
      :source-tag="sourceTag"
      :tags="tags"
      @close="closeCopyProjectsModal"
      @copy="handleCopyProjectsToTag"
    />
  </div>

    <!-- Confirmation Dialog -->
    <Modal
      :show="showConfirmDialog"
      :title="confirmDialogTitle"
      :message="confirmDialogMessage"
      confirm-text="Confirm"
      cancel-text="Cancel"
      :icon="AlertTriangle"
      icon-color="red"
      @confirm="handleConfirm"
      @close="handleCancel"
    />
</template>

<script>
import { ref, computed, onMounted, nextTick, watch } from 'vue'
import { storeToRefs } from 'pinia'
import { useRouter } from 'vue-router'
import { useTagStore } from '../stores/tags'
import { useTaxonomyStore } from '../stores/taxonomies'
import { useProjectStore } from '../stores/projects'
import useToast from '../composables/useToast'
import { createLogger } from '../utils/logger'
import { useConfirmDialog } from '../composables/useConfirmDialog'
import { createJsRegExp } from '../utils/taxonomyParser'
import { RefreshCw, Edit2, Copy, Tag, Grid3X3, List, Square, Folder, Trash2, AlertTriangle } from 'lucide-vue-next'
import Modal from './Modal.vue'
import TagProjectsModal from './TagProjectsModal.vue'
import CopyProjectsToTagModal from './CopyProjectsToTagModal.vue'
import TagCard from './TagCard.vue'
import Vue3Datagrid, { VGridVueTemplate } from '@revolist/vue3-datagrid'
import { buildDTProjectUrl } from '../config.js'

// URL encoding utility
const encodeTagName = (tagName) => {
  return encodeURIComponent(tagName)
}

export default {
  name: 'TagCenter',
  components: {
    Vue3Datagrid,
    VGridVueTemplate,
    List,
    Grid3X3,
    Square,
    Edit2,
    Copy,
    Tag,
    Folder,
    Trash2,
    RefreshCw,
    AlertTriangle,
    Modal,
    TagProjectsModal,
    CopyProjectsToTagModal,
    TagCard
  },
  setup() {
    const logger = createLogger('tag-center')
    const router = useRouter()
    const tagStore = useTagStore()
    const taxonomyStore = useTaxonomyStore()
    const projectStore = useProjectStore()
    const { showSuccess, showError } = useToast()
    const { showConfirmDialog, confirmDialogTitle, confirmDialogMessage, confirmDialogConfirmText, confirmDialogCancelText, showConfirm, handleConfirm, handleCancel } = useConfirmDialog()
    const { taxonomies, loading: taxonomiesLoading } = storeToRefs(taxonomyStore)
    const { getTaxonomyBadgeStyle, getTagTaxonomy, loadTaxonomies } = taxonomyStore

    // Use tag store
    const {
      tags,
      isLoading: tagsLoading,
      error: tagsError,
      currentPage,
      pageSize,
      totalTags,
      totalPages,
      searchQuery,
      selectedTaxonomy,
      filteredTags,
      paginatedTags,
      hasPreviousPage,
      hasNextPage
    } = storeToRefs(tagStore)

    const {
      loadTags,
      createTag,
      updateTag,
      deleteTag,
      setSearchQuery,
      setTaxonomyFilter,
      setPageSize,
      goToPage,
      nextPage,
      previousPage,
      clearFilters
    } = tagStore

    // Create Tag Modal state
    const showCreateTagModal = ref(false)
    const tagBuilderParts = ref([])
    const editingTag = ref(null)
    const editInput = ref(null) // Ref for edit input focus
    const isSavingTag = ref(false)

    // Clone Tag Modal state
    const showCloneTagModal = ref(false)
    const cloningTag = ref(null)
    const cloneTagName = ref('')
    const cloneTagValidation = ref({ valid: false, message: '' })
    const linkProjects = ref(false)
    const sourceTag = ref(null)

    // Local state not in store
    const projects = ref([])
    const newTag = ref('')
    const tagValidation = ref({ valid: false, message: '' })
    const showProjectsModal = ref(false)
    const selectedTag = ref(null)
    const tagProjects = ref([])
    const tagsViewMode = ref('deck') // 'list', 'grid', or 'deck'
    const editingTagName = ref('')

    // Dark mode detection
    const isDarkMode = computed(() => {
      if (typeof window !== 'undefined') {
        return document.documentElement.classList.contains('dark')
      }
      return false
    })

    // Grid columns for tags grid view
    const gridColumns = computed(() => [
      {
        prop: 'taxonomy',
        name: 'Taxonomy',
        sortable: true
      },
      {
        prop: 'name',
        name: 'Tag',
        sortable: true
      },
      {
        prop: 'projectsCount',
        name: 'Projects Count',
        sortable: true
      },
      /* ,
      {
        prop: 'actions',
        name: 'Actions',
        sortable: false,
        cellTemplate: VGridVueTemplate(TagActionsCell)
      } */
    ])

    // Tag actions cell template
    const TagActionsCell = {
      template: (props) => {
        const taxonomy = props.model.taxonomy ?
          (taxonomies.value.find(t => t.id === props.model.taxonomy) ||
          { name: props.model.taxonomy }) :
          { name: 'No taxonomy' };

        return {
          template: `
            <div class="flex gap-2">
              <button @click="viewProjects" class="px-2 py-1 text-xs bg-blue-600 text-white rounded hover:bg-blue-700">View</button>
              <button @click="removeTag" class="px-2 py-1 text-xs bg-red-600 text-white rounded hover:bg-red-700">Delete</button>
            </div>
          `,
          methods: {
            viewProjects: () => {
              // Emit event to parent or call directly
              logger.info('View projects for tag:', props.model.name)
            },
            edit: () => {
              logger.info('Edit tag:', props.model.name)
            },
            removeTag: () => {
              logger.info('Delete tag:', props.model.name)
            }
          }
        }
      }
    }

    // Methods
    const loadProjects = async () => {
      try {
        // Load projects from store instead of direct API call
        await tagStore.loadTags()
        logger.info('TagCenter - tags loaded:', tagStore.tags.length, tagStore.tags);
        projects.value = tagStore.tags.map(tag => ({
          id: tag.id, // Use tag id
          uuid: tag.id,
          name: tag.name,
          version: '', // Tags don't have versions
          displayName: tag.name,
          tags: [] // Tags don't have child tags
        }))
      } catch (error) {
        logger.error('Error loading projects:', error)
        projects.value = []
      }
    }

    const validateTag = () => {
      if (!newTag.value.trim()) {
        tagValidation.value = { valid: false, message: 'Tag is required' }
        return
      }

      const tag = newTag.value.trim()

      // Check for duplicates first
      if (tags.value.some(existing => existing.name === tag)) {
        tagValidation.value = {
          valid: false,
          message: '❌ Tag already exists'
        }
        return
      }

      // Check if tag matches any taxonomy regex_patternattern
      const matchingTaxonomy = taxonomies.value.find(taxonomy => {
        try {
          // Use native RegExp for JS regex compatibility
          const regex = createJsRegExp(taxonomy.regex_pattern)
          const matches = regex.test(tag)
          return matches
        } catch (error) {
          logger.error('Invalid regex regex_pattern:', taxonomy.regex_pattern, error)
          return false
        }
      })

      if (matchingTaxonomy) {
        tagValidation.value = {
          valid: true,
          message: `✅ Matches ${matchingTaxonomy.name} taxonomy (${matchingTaxonomy.id})`
        }
      } else {
        tagValidation.value = {
          valid: true,
          message: '✅ Custom tag'
        }
      }
    }

    const selectSuggestedTag = (tag) => {
      newTag.value = tag
      validateTag()
    }

    const handleCreateTag = async () => {
      if (!tagValidation.value.valid || !newTag.value.trim()) return

      try {
        const response = await tagStore.createTag({
          name: newTag.value.trim()
        })

        if (response) {
          // Add new tag to our list
          tags.value.push(response)
          newTag.value = ''
          tagValidation.value = { valid: false, message: '' }
          // Close the modal after successful creation
          showCreateTagModal.value = false
        }
      } catch (error) {
        logger.error('Error creating tag:', error)
        tagValidation.value = {
          valid: false,
          message: `❌ Error: ${tagStore.error || error.message}`
        }
      }
    }


    const handleDeleteTag = async (tag) => {
      const confirmed = await showConfirm({
        title: 'Delete Tag',
        message: `Are you sure you want to delete tag "${tag.name}"?`,
        confirmText: 'Delete',
        cancelText: 'Cancel'
      })

      if (!confirmed) return

      try {
        await tagStore.deleteTag(tag.name)

        showSuccess(`Tag "${tag.name}" deleted successfully`)
      } catch (error) {
        logger.error('Error deleting tag:', error)
        showError('Failed to delete tag', 'Please try again.')
      }
    }

    const viewTagProjects = async (tag) => {
      selectedTag.value = tag
      showProjectsModal.value = true

      try {
        tagProjects.value = await tagStore.getTagProjects(tag.name)
      } catch (error) {
        logger.error('Error loading tag projects:', error)
        tagProjects.value = []
      }
    }

    const closeProjectsModal = () => {
      showProjectsModal.value = false
      selectedTag.value = null
      tagProjects.value = []
    }

    const clearForm = () => {
      newTag.value = ''
      tagValidation.value = { valid: false, message: '' }
    }

    const formatDate = (dateString) => {
      return new Date(dateString).toLocaleString()
    }

    // Clone Tag functionality
    const startCloneTag = async (tag) => {
      logger.info('🔧 Clone Tag clicked for tag:', tag)
      cloningTag.value = tag
      cloneTagName.value = ''
      cloneTagValidation.value = { valid: false, message: '' }
      linkProjects.value = false

      // Initialize tag builder if tag has taxonomy
      if (tag.taxonomy) {
        try {
          logger.info('🔧 Available taxonomies:', taxonomies.value.map(t => ({ name: t.name, id: t.id })))
          logger.info('🔧 Available taxonomy names:', taxonomies.value.map(t => `'${t.name}'`).join(', '))
          logger.info('🔧 Looking for taxonomy:', `'${tag.taxonomy}'`)
          logger.info('🔧 Tag taxonomy type:', typeof tag.taxonomy)
          logger.info('🔧 Tag taxonomy length:', tag.taxonomy.length)

          // Find the taxonomy object by ID (since tag.taxonomy contains the ID, not the name)
          const taxonomy = taxonomies.value.find(t => t.id === tag.taxonomy)
          if (!taxonomy) {
            logger.error('Taxonomy not found by ID:', tag.taxonomy)
            // Try finding by name as fallback
            const taxonomyByName = taxonomies.value.find(t => t.name === tag.taxonomy)
            if (taxonomyByName) {
              logger.info('🔧 Found taxonomy by name instead:', taxonomyByName)
              // Use the found taxonomy and proceed with the same logic
              const parts = taxonomyStore.parseTaxonomyPattern(taxonomyByName.regex_pattern, taxonomyByName.relations)
              await taxonomyStore.loadDropdownValues(parts, taxonomyByName, tagStore.tags)
              const regex = createJsRegExp(taxonomyByName.regex_pattern)
              const match = tag.name.match(regex)

              if (match) {
                tagBuilderParts.value = parts.map((part) => {
                  if (part.type === 'static') {
                    return part
                  } else if (part.type === 'dropdown' || part.type === 'text') {
                    const currentValue = match.groups?.[part.name] || ''
                    return {
                      ...part,
                      value: currentValue
                    }
                  }
                  return part
                })
              } else {
                tagBuilderParts.value = parts
              }
              logger.info('🔧 Clone tag builder initialized (fallback):', tagBuilderParts.value)
            } else {
              tagBuilderParts.value = []
            }
          } else {
            logger.info('Found taxonomy by ID:', taxonomy)
            // Parse taxonomy pattern to extract parts
            const parts = taxonomyStore.parseTaxonomyPattern(taxonomy.regex_pattern, taxonomy.relations)

            // Load dropdown options for parts
            await taxonomyStore.loadDropdownValues(parts, taxonomy, tagStore.tags)

            // Parse the original tag to pre-populate values
            const regex = createJsRegExp(taxonomy.regex_pattern)
            logger.info('🔧 Regex pattern:', taxonomy.regex_pattern)
            logger.info('🔧 Testing against tag:', tag.name)
            const match = tag.name.match(regex)
            logger.info('🔧 Regex match result:', match)

            if (match) {
              logger.info('Match groups:', JSON.stringify(match.groups))
              logger.info('Parts before mapping:', JSON.stringify(parts))
              // Pre-populate tag builder parts with original tag values
              tagBuilderParts.value = parts.map((part) => {
                if (part.type === 'static') {
                  return part
                } else if (part.type === 'dropdown' || part.type === 'text') {
                  // Use named capture group value from match.groups
                  const currentValue = match.groups?.[part.name] || ''
                  logger.info(`🔧 Setting ${part.name} to: "${currentValue}"`)
                  return {
                    ...part,
                    value: currentValue
                  }
                }
                return part
              })
              logger.info('🔧 Tag builder parts after mapping:', JSON.stringify(tagBuilderParts.value))
            } else {
              // If no match, just load empty parts with dropdown options
              tagBuilderParts.value = parts
            }

            logger.info('🔧 Clone tag builder initialized:', JSON.stringify(tagBuilderParts.value))
          }

          logger.info('🔧 Clone tag builder initialized:', JSON.stringify(tagBuilderParts.value))
        } catch (error) {
          logger.error('Error initializing clone tag builder:', error)
          tagBuilderParts.value = []
        }
      } else {
        // Clear tag builder if no taxonomy
        tagBuilderParts.value = []
      }

      showCloneTagModal.value = true

      // Focus the first field after modal opens
      nextTick(() => {
        if (!hasCaptureGroups.value) {
          // Focus simple text input
          const input = document.querySelector('[data-clone-tag-input]')
          if (input) {
            input.focus()
          }
        } else {
          // Focus first tag builder field
          const firstField = document.querySelector('[data-tag-builder-field="first"]')
          if (firstField) {
            firstField.focus()
          }
        }
      })
    }

    const validateCloneTag = () => {
      const tagName = cloneTagName.value.trim()

      if (!tagName) {
        cloneTagValidation.value = { valid: false, message: 'Tag name is required' }
        return
      }

      // Check if tag already exists
      if (tags.value.some(t => t.name === tagName)) {
        cloneTagValidation.value = { valid: false, message: 'Tag already exists' }
        return
      }

      cloneTagValidation.value = { valid: true, message: 'Tag name is valid' }
    }

    const closeCloneTagModal = () => {
      showCloneTagModal.value = false
      cloningTag.value = null
      cloneTagName.value = ''
      cloneTagValidation.value = { valid: false, message: '' }
      linkProjects.value = false
    }

    // Copy Projects to Tag functionality. Target-tag selection and its search
    // dropdown live in the CopyProjectsToTagModal child; the parent only owns the
    // source tag, open/close state, and the actual copy API call.
    const showCopyProjectsModal = ref(false)

    const startCopyProjectsToTag = (tag) => {
      logger.info('🔗 Starting copy projects to tag for:', tag)
      // Handle both reactive proxy and regular objects
      const tagObj = tag.name ? tag : { name: tag, taxonomy: tag.taxonomy, projectsCount: tag.projectsCount }
      sourceTag.value = tagObj
      showCopyProjectsModal.value = true
    }

    const handleCopyProjectsToTag = async (targetTagName) => {
      const sourceTagName = sourceTag.value?.name ? sourceTag.value.name : sourceTag.value

      try {
        // Get all projects that have source tag
        const sourceTagProjects = await tagStore.getTagProjects(sourceTagName)
        const projectsToCopy = sourceTagProjects || []

        if (projectsToCopy.length === 0) {
          showError('No projects found to copy')
          return
        }

        // Use the generic proxy endpoint to add target tag to all projects
        await tagStore.linkTagsToProjects(targetTagName, projectsToCopy.map(project => project.uuid))

        showSuccess(`Successfully copied ${projectsToCopy.length} projects from "${sourceTagName}" to "${targetTagName}"`)
        closeCopyProjectsModal()
        await loadTags() // Refresh tags to update project counts
      } catch (error) {
        logger.error('Error copying projects:', error)
        showError('Failed to copy projects', error.response?.data?.message || error.message || 'Unknown error')
      }
    }

    const closeCopyProjectsModal = () => {
      showCopyProjectsModal.value = false
      sourceTag.value = null
    }

    const cloneTagFromBuilder = async () => {
      if (!generatedTag.value) {
        showError('Cannot clone tag', 'Generated tag name is empty')
        return
      }

      // Validate against the original tag's taxonomy
      const taxonomy = taxonomies.value.find(t => t.id === cloningTag.value?.taxonomy)
      if (taxonomy && !createJsRegExp(taxonomy.regex_pattern).test(generatedTag.value)) {
        showError('Invalid tag name', `Tag must match pattern: ${taxonomy.regex_pattern}`)
        return
      }

      try {
        const newTagName = generatedTag.value

        // Create new tag
        const response = await tagStore.createTag({
          name: newTagName
        })

        if (response) {
          // Add new tag to our list
          tags.value.push(response)

          // If linking projects is enabled, get projects from original tag and link them
          if (linkProjects.value && cloningTag.value && cloningTag.value.projectsCount > 0) {
            try {
              const projects = await tagStore.getTagProjects(cloningTag.value.name)

              if (projects && projects.length > 0) {
                // Link each project to new tag using the correct DT API endpoint
                const projectUuids = projects.map(p => p.uuid)
                await tagStore.linkTagsToProjects(newTagName, projectUuids)

                showSuccess(`Tag "${newTagName}" created and linked to ${projects.length} projects`)
              } else {
                showSuccess(`Tag "${newTagName}" created successfully`)
              }
            } catch (error) {
              logger.error('Error linking projects:', error)
              showSuccess(`Tag "${newTagName}" created but failed to link some projects`)
            }
          } else {
            showSuccess(`Tag "${newTagName}" created successfully`)
          }

          // Close modal and refresh tags
          closeCloneTagModal()
          await loadTags()
        }
      } catch (error) {
        logger.error('Error cloning tag:', error)
        showError('Failed to clone tag', 'Please try again.')
      }
    }

    const cloneTag = async () => {
      if (!cloneTagValidation.value.valid || !cloneTagName.value.trim()) {
        return
      }

      try {
        const newTagName = cloneTagName.value.trim()

        // Create the new tag
        const response = await tagStore.createTag({
          name: newTagName
        })

        if (response) {
          // Add new tag to our list
          tags.value.push(response)

          // If linking projects is enabled, get projects from original tag and link them
          if (linkProjects.value && cloningTag.value && cloningTag.value.projectsCount > 0) {
            try {
              const projects = await tagStore.getTagProjects(cloningTag.value.name)

              if (projects && projects.length > 0) {
                // Link each project to new tag using the correct DT API endpoint
                const projectUuids = projects.map(p => p.uuid)
                await tagStore.linkTagsToProjects(newTagName, projectUuids)

                showSuccess(`Tag "${newTagName}" created and linked to ${projects.length} projects`)
              } else {
                showSuccess(`Tag "${newTagName}" created successfully`)
              }
            } catch (error) {
              logger.error('Error linking projects:', error)
              showSuccess(`Tag "${newTagName}" created but failed to link some projects`)
            }
          } else {
            showSuccess(`Tag "${newTagName}" created successfully`)
          }

          // Close modal and refresh tags
          closeCloneTagModal()
          await loadTags()
        }
      } catch (error) {
        logger.error('Error cloning tag:', error)
        cloneTagValidation.value = {
          valid: false,
          message: `❌ Error: ${tagStore.error || error.message}`
        }
      }
    }

    // Edit tag functionality
    const startEditTag = (tag) => {
      logger.info('🔧 Starting edit for tag:', tag)

      editingTag.value = tag
      editingTagName.value = tag.name

      // focus the editor after DOM update using Vue refs
      nextTick(() => {
        // Try multiple approaches to find and focus the input
        const attempts = [
          () => document.querySelector(`input[data-tag-name="${tag.name}"]`),
          () => document.querySelector(`input[data-tag-name="${tag.name}"]`),
          () => document.querySelector('input[data-tag-name="' + tag.name + '"]')
        ]

        for (const attempt of attempts) {
          const input = attempt()
          if (input) {
            input.focus()
            // input.select()
            return
          }
        }

        logger.info('🔧 Input not found, trying alternative approach')
      })
    }

    const cancelEditTag = () => {
      editingTag.value = null
      editingTagName.value = ''
    }

    const saveEditTag = async () => {
      if (!editingTag.value || !editingTagName.value.trim() || isSavingTag.value) {
        return
      }

      isSavingTag.value = true

      try {
        await tagStore.updateTag(editingTag.value.name, {
          name: editingTagName.value.trim()
        })

        // Update the tag in the local state
        const tagIndex = tags.value.findIndex(t => t.name === editingTag.value.name)
        if (tagIndex !== -1) {
          tags.value[tagIndex].name = editingTagName.value.trim()
        }

        // Reset editing state
        editingTag.value = null
        editingTagName.value = ''
        showSuccess('Tag updated successfully')
      } catch (error) {
        logger.error('Error updating tag:', error)
        showError('Failed to update tag', 'Please try again.')
      } finally {
        isSavingTag.value = false
      }
    }

    // Refresh functionality
    const refreshTags = async () => {
      try {
        await Promise.all([
          loadTaxonomies(),
          loadTags(),
          loadProjects()
        ])
        showSuccess('Tags refreshed successfully')
      } catch (error) {
        logger.error('Error refreshing tags:', error)
        showError('Failed to refresh tags', 'Please try again.')
      }
    }

    // Lifecycle
    onMounted(() => {
      loadTaxonomies()
      loadTags()
      loadProjects()
    })

    // Computed properties for tag creation
    const generatedTag = computed(() => {
      if (!tagBuilderParts.value.length) return ''
      return tagBuilderParts.value.map(part => {
        if (part.type === 'static') return part.value
        return part.value || ''
      }).join('')
    })

    const canCreateTag = computed(() => {
      const taxonomy = taxonomies.value.find(t => t.id === selectedTaxonomy.value?.id)
      // check that generatedTag is compatible with the tag pattern
      return generatedTag.value.length > 0 && taxonomy && createJsRegExp(taxonomy.regex_pattern).test(generatedTag.value)
    })

    // Separate validation for clone tag that doesn't depend on selectedTaxonomy
    const canCloneTag = computed(() => {
      if (!cloningTag.value || !cloningTag.value.taxonomy) {
        return false
      }

      const taxonomy = taxonomies.value.find(t => t.id === cloningTag.value.taxonomy)
      if (!taxonomy) {
        return false
      }

      // check that generatedTag is compatible with the tag pattern
      return generatedTag.value.length > 0 && createJsRegExp(taxonomy.regex_pattern).test(generatedTag.value)
    })

    // Separate validation for edit tag that doesn't depend on selectedTaxonomy
    const canEditTag = computed(() => {
      if (!editingTag.value || !editingTag.value.taxonomy) {
        return false
      }

      const taxonomy = taxonomies.value.find(t => t.id === editingTag.value.taxonomy)
      if (!taxonomy) {
        return false
      }

      // check that generatedTag is compatible with the tag pattern
      return generatedTag.value.length > 0 && createJsRegExp(taxonomy.regex_pattern).test(generatedTag.value)
    })

    // Check if tag has capture groups (for showing simple vs advanced clone)
    const hasCaptureGroups = computed(() => {
      return tagBuilderParts.value.some(part =>
        part.type === 'text' || part.type === 'dropdown'
      )
    })

    // Methods for aided editing
    const tagBelongsToTaxonomy = (tag) => {
      return tag.taxonomy && tag.taxonomy.trim() !== ''
    }

    const startAidedEditTag = async (tag) => {
      logger.info('🔧 Aided Edit clicked for tag:', tag)
      logger.info('🔧 Current tagBuilderParts before Aided Edit:', tagBuilderParts.value)
      try {
        // Find taxonomy that matches this tag pattern
        const matchingTaxonomy = taxonomies.value.find(taxonomy => {
          const regex = createJsRegExp(taxonomy.regex_pattern)
          return regex.test(tag.name)
        })

        logger.info('🔧 Matching taxonomy:', matchingTaxonomy)

        if (!matchingTaxonomy) {
          showError('No matching taxonomy found for this tag')
          return
        }

        selectedTaxonomy.value = matchingTaxonomy || ""
        editingTag.value = tag

        logger.info('🔧 Set selectedTaxonomy and editingTag')

        // Parse the tag using the taxonomy pattern to pre-populate fields
        const regex = createJsRegExp(matchingTaxonomy.regex_pattern)
        const match = tag.name.match(regex)

        logger.info('🔧 Regex match result:', match)

        if (match) {
          // Parse taxonomy pattern to extract parts
          const parts = taxonomyStore.parseTaxonomyPattern(matchingTaxonomy.regex_pattern, matchingTaxonomy.relations)

          logger.info('Parsed parts:', parts)

          // Load dropdown options for parts
          await taxonomyStore.loadDropdownValues(parts, matchingTaxonomy, tagStore.tags)

          // Pre-populate tag builder parts with existing tag values
          tagBuilderParts.value = parts.map((part) => {
            if (part.type === 'static') {
              return part
            } else if (part.type === 'dropdown' || part.type === 'text') {
              // Use the named capture group value from match.groups
              const currentValue = match.groups?.[part.name] || ''
              return {
                ...part,
                value: currentValue
              }
            }
            return part
          })

          logger.info('🔧 Final tagBuilderParts:', tagBuilderParts.value)
        } else {
          // If no match, just load empty parts with dropdown options
          const parts = taxonomyStore.parseTaxonomyPattern(matchingTaxonomy.regex_pattern, matchingTaxonomy.relations)
          await taxonomyStore.loadDropdownValues(parts, matchingTaxonomy, tagStore.tags)
          tagBuilderParts.value = parts
        }

        showCreateTagModal.value = true
        logger.info('🔧 Modal should be open now')
      } catch (error) {
        logger.error('Error starting aided edit:', error)
        showError('Failed to open edit modal')
      }
    }

    const closeCreateTagModal = () => {
      showCreateTagModal.value = false
      selectedTaxonomy.value = ""
      tagBuilderParts.value = []
      editingTag.value = null
    }

    const createOrUpdateTag = async () => {
      if (!canCreateTag.value || !generatedTag.value) return

      try {
        if (editingTag.value) {
          // Update existing tag (Aided Edit mode)
          if (!selectedTaxonomy.value) {
            showError('No taxonomy selected for editing')
            return
          }

          await tagStore.updateTag(editingTag.value.name, {
            name: generatedTag.value,
            taxonomy_id: selectedTaxonomy.value.id
          })
          showSuccess(`Tag "${generatedTag.value}" updated successfully!`)
        } else {
          // Create new tag (regular Create mode)
          const response = await tagStore.createTag({
            name: generatedTag.value
          })

          if (response) {
            // Add new tag to our list
            tags.value.push(response)
            newTag.value = ''
            tagValidation.value = { valid: false, message: '' }
          }
        }

        // Close modal after successful operation
        closeCreateTagModal()
      } catch (error) {
        logger.error('Error creating/updating tag:', error)
        showError('Failed to save tag')
      }
    }

    const saveCreateTagModal = async () => {
      if (selectedTaxonomy.value) {
        await createOrUpdateTag()
        return
      }

      await handleCreateTag()
    }

    return {
      // Tag store state
      tags,
      tagsLoading,
      tagsError,
      currentPage,
      pageSize,
      totalTags,
      totalPages,
      searchQuery,
      filteredTags,
      paginatedTags,
      hasPreviousPage,
      hasNextPage,

      // Tag store methods
      loadTags,
      setSearchQuery,
      setTaxonomyFilter,
      setPageSize,
      goToPage,
      nextPage,
      previousPage,
      clearFilters,

      // Local state
      projects,
      newTag,
      tagValidation,
      showProjectsModal,
      selectedTag,
      tagProjects,
      tagsViewMode,
      showCreateTagModal,
      editingTag,
      editingTagName,

      // Copy Projects to Tag state
      showCopyProjectsModal,
      sourceTag,
      startCopyProjectsToTag,
      handleCopyProjectsToTag,
      closeCopyProjectsModal,

      // Taxonomy store functions
      taxonomies,
      getTagTaxonomy,
      getTaxonomyBadgeStyle,
      selectedTaxonomy,

      // Clone Tag state
      showCloneTagModal,
      cloningTag,
      cloneTagName,
      cloneTagValidation,
      linkProjects,

      // Other functions
      isDarkMode,
      gridColumns,
      validateTag,
      selectSuggestedTag,
      handleCreateTag,
      handleDeleteTag,
      clearForm,
      viewTagProjects,
      startEditTag,
      startAidedEditTag,
      startCloneTag,
      validateCloneTag,
      cloneTag,
      cloneTagFromBuilder,
      closeCloneTagModal,
      tagBelongsToTaxonomy,
      cancelEditTag,
      saveEditTag,
      refreshTags,
      formatDate,
      closeProjectsModal,
      closeCreateTagModal,
      createOrUpdateTag,
      saveCreateTagModal,
      buildDTProjectUrl,

      // Tag builder properties
      tagBuilderParts,
      generatedTag,
      canCreateTag,
      canCloneTag,
      canEditTag,
      hasCaptureGroups,

      // Confirmation dialog
      showConfirmDialog,
      confirmDialogTitle,
      confirmDialogMessage,
      confirmDialogConfirmText,
      confirmDialogCancelText,
      handleConfirm,
      handleCancel,

      // Components
      AlertTriangle
    }
  }
}
</script>
