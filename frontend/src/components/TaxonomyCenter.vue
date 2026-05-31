<template>
  <div class="px-4 sm:px-0">
    <div class="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
      <div class="flex justify-between items-center mb-6">
        <div>
          <h2 class="text-2xl font-bold text-gray-900 dark:text-white">Taxonomy Center</h2>
          <p class="text-sm text-gray-600 dark:text-gray-400 mt-1">
            Taxonomies define rules for tag patterns and create hierarchical relationships, forming tree structures that organize and categorize your tags
          </p>
        </div>
      </div>

      <!-- Add Taxonomy Button (positioned like "Create Tag" in Tag Center) -->
      <div class="mb-6">
        <button
          @click="addTaxonomy"
          class="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-all cursor-pointer hover:shadow-md flex items-center"
        >
          <Plus class="inline w-4 h-4 mr-2" />
          Add Taxonomy
        </button>
      </div>

      <!-- Main Content - Always Visible -->
      <div class="flex flex-col lg:flex-row gap-6">
          <!-- Taxonomy Graph Visualization -->
          <!-- Graph gets the larger share (2/3); the list keeps 1/3. "Expand"
               grows the graph in-flow to the full content width and hides the
               list, rather than a viewport-fixed overlay (which would render
               behind the sidebar). min-w-0 lets it shrink back on restore. -->
          <div
            :class="['bg-white dark:bg-gray-800 rounded-lg shadow p-6 flex flex-col min-w-0',
                     graphExpanded ? 'w-full basis-full' : 'flex-1 lg:basis-2/3']"
          >
            <div class="flex justify-between items-center mb-4">
              <h3 class="text-lg font-medium text-gray-900 dark:text-white">Taxonomy Relations Graph</h3>
              <!-- Graph controls: zoom in/out, fit to view, expand/collapse -->
              <div class="flex items-center gap-1">
                <button
                  @click="zoomIn"
                  class="p-1.5 rounded-md border border-gray-300 dark:border-gray-600 text-gray-600 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700 cursor-pointer"
                  title="Zoom in"
                >
                  <ZoomIn class="w-4 h-4" />
                </button>
                <button
                  @click="zoomOut"
                  class="p-1.5 rounded-md border border-gray-300 dark:border-gray-600 text-gray-600 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700 cursor-pointer"
                  title="Zoom out"
                >
                  <ZoomOut class="w-4 h-4" />
                </button>
                <button
                  @click="fitGraph"
                  class="p-1.5 rounded-md border border-gray-300 dark:border-gray-600 text-gray-600 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700 cursor-pointer"
                  title="Fit to view"
                >
                  <Scan class="w-4 h-4" />
                </button>
                <button
                  @click="toggleGraphExpand"
                  class="p-1.5 rounded-md border border-gray-300 dark:border-gray-600 text-gray-600 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700 cursor-pointer"
                  :title="graphExpanded ? 'Collapse graph' : 'Expand graph'"
                >
                  <component :is="graphExpanded ? Minimize2 : Maximize2" class="w-4 h-4" />
                </button>
              </div>
            </div>
            <div
              :class="[
                'border-2 border-gray-200 dark:border-gray-600 rounded-lg bg-gray-50 dark:bg-gray-700 overflow-hidden',
                graphExpanded ? 'h-[80vh]' : 'h-[60vh] min-h-96'
              ]"
            >
              <div ref="cytoscapeContainer" class="w-full h-full"></div>
            </div>
          </div>

          <!-- Taxonomies List (hidden while the graph is expanded) -->
          <div v-show="!graphExpanded" class="bg-white dark:bg-gray-800 rounded-lg shadow p-6 flex-1 lg:basis-1/3 min-w-0">
          <div class="px-1 py-5 sm:px-1">
            <div>
              <h3 class="text-lg leading-6 font-medium text-gray-900 dark:text-white">Existing Taxonomies</h3>
              <p class="mt-1 max-w-2xl text-sm text-gray-500 dark:text-gray-400">
                Taxonomies are processed in priority order (lower numbers first)
              </p>
            </div>
          </div>

          <ul class="divide-y divide-gray-200 dark:border-gray-700">
            <li
              v-for="(taxonomy, index) in taxonomies"
              :key="taxonomy.id"
              draggable="true"
              @dragstart="handleDragStart($event, index)"
              @dragover="handleDragOver($event)"
              @drop="handleDrop($event, index)"
              @dragend="handleDragEnd"
              class="cursor-move hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
            >
              <div class="flex flex-col gap-2 py-2">
                <div class="flex items-start justify-between gap-3">
                  <div class="flex items-center space-x-3 flex-1 min-w-0">
                    <div class="text-gray-400 dark:text-gray-500 shrink-0">
                      <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                        <path d="M10 6a2 2 0 110-4 2 2 0 010 4zM10 12a2 2 0 110-4 2 2 0 010 4zM10 18a2 2 0 110-4 2 2 0 010 4z"/>
                      </svg>
                    </div>
                    <div class="flex-1 min-w-0">
                      <div class="font-medium text-gray-900 dark:text-white truncate">{{ taxonomy.name }}</div>
                    </div>
                  </div>
                  <div class="flex items-center gap-3 shrink-0">
                    <span class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-blue-100 dark:bg-blue-900/30 text-blue-800 dark:text-blue-200">
                      {{ taxonomy.id }}
                    </span>
                    <div class="flex gap-1 p-2 shrink-0">
                      <button
                        @click="showTaxonomyTags(taxonomy)"
                        class="p-1 bg-purple-600 text-white text-xs rounded hover:bg-purple-700 inline-flex items-center justify-center transition-colors cursor-pointer"
                        title="Show Tags"
                      >
                        <Folder class="w-3 h-3" />
                      </button>
                      <button
                        @click="createTaxonomyTag(taxonomy)"
                        class="p-1 bg-green-600 text-white text-xs rounded hover:bg-green-700 inline-flex items-center justify-center transition-colors cursor-pointer"
                        title="Create Tag"
                      >
                        <Plus class="w-3 h-3" />
                      </button>
                      <button
                        @click="editTaxonomy(taxonomy)"
                        class="p-1 bg-blue-600 text-white text-xs rounded hover:bg-blue-700 inline-flex items-center justify-center transition-colors cursor-pointer"
                        title="Edit"
                      >
                        <Edit2 class="w-3 h-3" />
                      </button>
                      <button
                        @click="deleteTaxonomy(taxonomy.id)"
                        class="p-1 bg-red-600 text-white text-xs rounded hover:bg-red-700 inline-flex items-center justify-center transition-colors cursor-pointer"
                        title="Remove"
                      >
                        <Trash2 class="w-3 h-3" />
                      </button>
                    </div>
                  </div>
                </div>
                <div class="p-1">
                  <code class="text-xs bg-gray-100 dark:bg-gray-700 px-2 py-1 rounded text-gray-800 dark:text-gray-200 font-mono break-all inline-block hover:bg-gray-200 dark:hover:bg-gray-600 transition-colors" :title="taxonomy.regex_pattern">{{ taxonomy.regex_pattern }}</code>
                </div>
              </div>
            </li>
          </ul>

          <div v-if="taxonomies.length === 0" class="text-center py-8 text-gray-500 dark:text-gray-400">
            No taxonomies defined yet. Create your first taxonomy to get started.
          </div>
        </div>
      </div>

      <!-- Taxonomy Modal -->
      <div v-if="editingTaxonomy" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
        <div class="bg-white dark:bg-gray-800 rounded-lg shadow-xl max-w-4xl w-full mx-4 max-h-[90vh] overflow-y-auto">
          <div class="p-6">
            <div class="flex justify-between items-center mb-4">
              <h3 class="text-lg font-semibold text-gray-900 dark:text-white">
                {{ isEditingExisting ? 'Edit Taxonomy' : 'Create Taxonomy' }}
              </h3>
              <button
                @click="cancelEdit"
                class="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
              >
                ✕
              </button>
            </div>
          <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <!-- ID Field -->
            <div>
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-300">
                ID
                <span v-if="isEditingExisting" class="ml-2 text-xs text-gray-500 dark:text-gray-400">(read-only when editing)</span>
              </label>
              <div class="flex items-center gap-2">
                <input
                  :value="editingTaxonomy.id"
                  @input="editingTaxonomy.id = $event.target.value"
                  type="text"
                  :disabled="isEditingExisting"
                  :class="[
                    'mt-1 block w-full rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm dark:text-white',
                    isEditingExisting
                      ? 'border-gray-200 dark:border-gray-600 bg-gray-50 dark:bg-gray-700 text-gray-500 dark:text-gray-400 cursor-not-allowed'
                      : 'border-gray-300 dark:border-gray-600 dark:bg-gray-700'
                  ]"
                  class="px-3 py-2"
                  placeholder="e.g., customer, env, product"
                />
              </div>
            </div>

            <!-- Name Field -->
            <div>
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-300">Name</label>
              <input
                v-model="editingTaxonomy.name"
                type="text"
                class="mt-1 block w-full rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm dark:bg-gray-700 dark:text-white px-3 py-2"
                placeholder="e.g., Customer, Environment, Product"
              />
            </div>

            <!-- Regex Pattern Field -->
            <div>
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-300">Regex Pattern</label>
              <textarea
                v-model="editingTaxonomy.regex_pattern"
                rows="3"
                class="mt-1 block w-full border-gray-300 dark:border-gray-600 dark:bg-gray-700 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm dark:text-white"
                placeholder="e.g., ^cust:(?<id>\w+)$"
              ></textarea>
              <p class="mt-1 text-sm text-gray-500 dark:text-gray-400">
                Use named capture groups <code><strong>(?&lt;name&gt;regex_pattern)</strong></code> to extract values.
                The group name should match the taxonomy ID for relations.
              </p>
            </div>

            <!-- Color Field -->
            <div>
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-300">Color</label>
              <div class="flex items-center gap-2">
                <input
                  v-model="editingTaxonomy.color"
                  type="color"
                  class="w-16 h-8 border border-gray-300 dark:border-gray-600 rounded cursor-pointer"
                  :title="`Color for ${editingTaxonomy.name || 'taxonomy'}`"
                />
                <input
                  type="text"
                  v-model="editingTaxonomy.color"
                  class="hidden"
                  placeholder="#ef4444"
                />
              </div>
            </div>

            <!-- Relations Section -->
            <div class="mt-6">
              <h4 class="text-sm font-medium text-gray-900 dark:text-white mb-3">Relations (Optional)</h4>
              <div class="space-y-4">
                <div v-for="(relation, index) in editingTaxonomy.relations" :key="index" class="border border-gray-200 dark:border-gray-600 rounded-lg p-4">
                  <div class="grid grid-cols-3 gap-4">
                    <div>
                      <label class="block text-sm font-medium text-gray-700 dark:text-gray-300">Group Name</label>
                      <select
                        v-model="relation.group"
                        class="mt-1 block w-full border-gray-300 dark:border-gray-600 dark:bg-gray-700 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm dark:text-white px-3 py-2"
                      >
                        <option value="">Select a group...</option>
                        <option v-for="group in availableCaptureGroups" :key="group" :value="group">
                          {{ group }}
                        </option>
                      </select>
                    </div>
                    <div>
                      <label class="block text-sm font-medium text-gray-700 dark:text-gray-300">Target Taxonomy</label>
                      <select
                        v-model="relation.targets"
                        class="mt-1 block w-full border-gray-300 dark:border-gray-600 dark:bg-gray-700 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm dark:text-white px-3 py-2"
                      >
                        <option value="">Select a target taxonomy...</option>
                        <option v-for="taxonomy in availableTargetTaxonomies" :key="taxonomy.id" :value="taxonomy.id">
                          {{ taxonomy.name || taxonomy.id }}
                        </option>
                      </select>
                    </div>
                    <div class="mt-2">
                      <button
                        @click="removeRelation(index)"
                        class="px-3 py-1 bg-red-600 text-white text-sm rounded-md hover:bg-red-700 inline-flex items-center gap-1"
                      >
                        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                        </svg> Remove
                      </button>
                    </div>
                  </div>
                </div>
                <button
                  @click="addRelation"
                  class="px-3 py-2 bg-green-600 text-white text-sm rounded-md hover:bg-green-700"
                >
                  Add Relation
                </button>
              </div>
            </div>

            <!-- Regex Tester -->
            <div class="mt-6 p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
              <h4 class="text-sm font-medium text-gray-900 dark:text-white mb-3">Test Regex Pattern</h4>
              <div class="grid grid-cols-1 gap-4">
                <div>
                  <label class="block text-sm font-medium text-gray-700 dark:text-gray-300">Test Tags</label>
                  <input
                    v-model="testTags"
                    type="text"
                    class="mt-1 block w-full border-gray-300 dark:border-gray-600 dark:bg-gray-700 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm dark:text-white"
                    placeholder="e.g., customer:acme or env:production or app:webapp"
                  />
                </div>

                <div>
                  <button
                    @click="testRegex"
                    :disabled="!editingTaxonomy.regex_pattern || !testTags"
                    class="px-3 py-1 bg-blue-600 text-white text-sm rounded-md hover:bg-blue-700 disabled:opacity-50"
                  >
                    Test Pattern
                  </button>
                </div>

                <div v-if="regexTestResult" class="mt-3">
                  <div v-if="regexTestResult.match" class="p-3 bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-md">
                    <p class="text-sm font-medium text-green-800 dark:text-green-200">✅ Match Found</p>
                    <pre class="mt-2 text-xs text-green-700 dark:text-green-300">{{ JSON.stringify(regexTestResult.groups, null, 2) }}</pre>
                  </div>
                  <div v-else class="p-3 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-md">
                    <p class="text-sm font-medium text-red-800 dark:text-red-200">❌ No Match</p>
                    <p v-if="regexTestResult.error" class="mt-1 text-xs text-red-700 dark:text-red-300">{{ regexTestResult.error }}</p>
                  </div>
                </div>
              </div>
            </div>
          </div>

            <div class="mt-6 flex justify-end space-x-3">
              <button
                @click="cancelEdit"
                class="px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm text-sm font-medium text-gray-700 dark:text-gray-300 bg-white dark:bg-gray-800 hover:bg-gray-50 dark:hover:bg-gray-700"
              >
                Cancel
              </button>
              <button
                @click="saveTaxonomy"
                :disabled="!isFormValid"
                class="px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 disabled:opacity-50"
              >
                Save
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Tags Modal -->
    <div v-if="showTagsModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-white dark:bg-gray-800 rounded-lg shadow-xl max-w-2xl w-full mx-4 max-h-[80vh] overflow-y-auto">
        <div class="p-6">
          <div class="flex justify-between items-center mb-4">
            <h3 class="text-lg font-semibold text-gray-900 dark:text-white">
              Tags for {{ selectedTaxonomy?.name }} ({{ taxonomyTags.length }})
            </h3>
            <button
              @click="closeTagsModal"
              class="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
            >
              ✕
            </button>
          </div>

          <div v-if="taxonomyTags.length === 0" class="text-center py-8 text-gray-500 dark:text-gray-400">
            No tags found for this taxonomy pattern.
          </div>

          <div v-else class="space-y-2">
            <div
              v-for="tag in taxonomyTags"
              :key="tag.name"
              class="p-3 border border-gray-200 dark:border-gray-700 rounded-lg flex justify-between items-center"
            >
              <span class="font-mono text-gray-900 dark:text-white">{{ tag.name }}</span>
              <span class="text-xs text-gray-500 dark:text-gray-400">
                Directly tagging {{ tag.projectCount }} projects
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Create Tag Modal -->
    <div v-if="showCreateTagModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-white dark:bg-gray-800 rounded-lg shadow-xl max-w-4xl w-full mx-4 max-h-[80vh] overflow-y-auto">
        <div class="p-6">
          <div class="flex justify-between items-center mb-4">
            <h3 class="text-lg font-semibold text-gray-900 dark:text-white">
              Create Tag for {{ selectedTaxonomy?.name }}
            </h3>
            <button
              @click="closeCreateTagModal"
              class="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
            >
              ✕
            </button>
          </div>

          <!-- Pattern Display -->
          <div class="mb-4 p-3 bg-gray-100 dark:bg-gray-700 rounded-lg">
            <div class="text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Pattern:</div>
            <code class="text-sm bg-gray-200 dark:bg-gray-600 px-3 py-2 rounded text-gray-800 dark:text-gray-200 font-mono break-all hover:bg-gray-300 dark:hover:bg-gray-600 transition-colors">{{ selectedTaxonomy?.regex_pattern }}</code>
          </div>

          <!-- Dynamic Tag Builder -->
          <div class="space-y-4">
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
              @click="createNewTag"
              :disabled="!canCreateTag"
              class="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
            >
              Create Tag
            </button>
            <button
              @click="closeCreateTagModal"
              class="px-4 py-2 bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-md hover:bg-gray-300 dark:hover:bg-gray-600 transition-colors"
            >
              Cancel
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Confirmation Dialog -->
    <Modal
      :show="showConfirmDialog"
      :title="confirmDialogTitle"
      :message="confirmDialogMessage"
      :confirm-text="confirmDialogConfirmText"
      :cancel-text="confirmDialogCancelText"
      :icon="AlertTriangle"
      icon-color="red"
      @confirm="handleConfirm"
      @close="handleCancel"
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, nextTick, watch } from 'vue'
import { useTaxonomyStore } from '../stores/taxonomies'
import { useTagStore } from '../stores/tags'
import { Plus, Trash2, Edit2, Folder, Maximize2, Minimize2, AlertTriangle, ZoomIn, ZoomOut, Scan } from 'lucide-vue-next'
import cytoscape from 'cytoscape'
import Modal from './Modal.vue'
import { useToast } from '../composables/useToast'
import { useConfirmDialog } from '../composables/useConfirmDialog'
import { createLogger } from '../utils/logger'
import { createJsRegExp } from '../utils/taxonomyParser'

const { showSuccess, showError } = useToast()
const {
  showConfirmDialog,
  confirmDialogTitle,
  confirmDialogMessage,
  confirmDialogConfirmText,
  confirmDialogCancelText,
  showConfirm,
  handleConfirm,
  handleCancel
} = useConfirmDialog()
const logger = createLogger('tag-center')

// Store instances
const taxonomyStore = useTaxonomyStore()
const tagStore = useTagStore()

// Reactive data
const editingTaxonomy = ref(null)
const isEditingExisting = ref(false)
const testTags = ref('')
const regexTestResult = ref(null)
const showTagsModal = ref(false)
const showCreateTagModal = ref(false)
const selectedTaxonomy = ref(null)
const taxonomyTags = ref([])
const tagBuilderParts = ref([])
const tagUsage = ref({})
const tagUsageData = ref({})
const taxonomies = ref([])
const draggedIndex = ref(null)
const cytoscapeContainer = ref(null)
const cytoscapeInstance = ref(null)
const graphExpanded = ref(false) // Fullscreen graph toggle

// Toggle the graph between its inline size and the expanded (full content
// width) size. resize()+fit() must run AFTER the browser applies the new layout
// or cytoscape keeps the previous zoom/size, so we wait a frame past nextTick.
// fit() resets the zoom so restoring returns to the original view.
const toggleGraphExpand = () => {
  graphExpanded.value = !graphExpanded.value
  nextTick(() => {
    requestAnimationFrame(() => {
      if (cytoscapeInstance.value) {
        cytoscapeInstance.value.resize()
        cytoscapeInstance.value.fit(undefined, 50)
      }
    })
  })
}

// Zoom controls (mirror TagsGraph): animate so the change is smooth, and use
// the same fit padding as expand/restore so "fit" behaves consistently.
const zoomIn = () => {
  if (cytoscapeInstance.value) {
    cytoscapeInstance.value.animate({ zoom: cytoscapeInstance.value.zoom() * 1.2 }, { duration: 200 })
  }
}
const zoomOut = () => {
  if (cytoscapeInstance.value) {
    cytoscapeInstance.value.animate({ zoom: cytoscapeInstance.value.zoom() / 1.2 }, { duration: 200 })
  }
}
const fitGraph = () => {
  if (cytoscapeInstance.value) {
    cytoscapeInstance.value.animate({ fit: { padding: 50 } }, { duration: 300 })
  }
}


// Mobile detection
const isMobile = computed(() => {
  return window.innerWidth < 1024 // lg breakpoint
})

// Dark mode detection
const isDarkMode = computed(() => {
  return document.documentElement.classList.contains('dark')
})

// Graph visualization data
const graphNodes = ref([])
const graphEdges = ref([])
const selectedGraphNode = ref(null)
const hoverNode = ref(null)
const panX = ref(0)
const panY = ref(0)
const zoomLevel = ref(1)
const isPanning = ref(false)
const panStart = ref({ x: 0, y: 0 })
const graphSvg = ref(null)
const graphGroup = ref(null)

    const isFormValid = computed(() => {
      return editingTaxonomy.value &&
             editingTaxonomy.value.id &&
             editingTaxonomy.value.name &&
             editingTaxonomy.value.regex_pattern !== undefined
    })

    const availableTargetTaxonomies = computed(() => {
      // Return all taxonomies except the one being edited
      return taxonomies.value.filter(t => t.id !== editingTaxonomy.value?.id)
    })

    const availableCaptureGroups = computed(() => {
      // Extract capture groups from current taxonomy's regex pattern
      if (!editingTaxonomy.value?.regex_pattern) return []

      const captureGroupRegex = /\(\?<([^>]+)>([^)]+)\)/g
      const groups = new Set()
      let match

      while ((match = captureGroupRegex.exec(editingTaxonomy.value.regex_pattern)) !== null) {
        groups.add(match[1])
      }

      return Array.from(groups).sort()
    })

    const addTaxonomy = () => {
      // Default to the next free priority so new taxonomies don't all collide at
      // 1 (priority is the conflict-resolution order - lower number wins).
      const nextPriority = taxonomies.value.length
        ? Math.max(...taxonomies.value.map(t => t.priority || 0)) + 1
        : 1
      editingTaxonomy.value = {
        id: '',
        name: '',
        regex_pattern: '^.*$', // Default regex_pattern - matches anything
        priority: nextPriority,
        color: '#ef4444',
        relations: []
      }
      testTags.value = ''
      regexTestResult.value = null
    }

    const editTaxonomy = (taxonomy) => {
      editingTaxonomy.value = {
        ...taxonomy,
        color: taxonomy.color || '#ef4444', // Ensure color always exists
        relations: taxonomy.relations || []
      }
      testTags.value = ''
      regexTestResult.value = null
    }

    const addRelation = () => {
      if (!editingTaxonomy.value.relations) {
        editingTaxonomy.value.relations = []
      }
      editingTaxonomy.value.relations.push({
        group: '',
        targets: ''
      })
    }

    const removeRelation = (index) => {
      editingTaxonomy.value.relations.splice(index, 1)
    }

    const cancelEdit = () => {
      editingTaxonomy.value = null
      isEditingExisting.value = false
      testTags.value = ''
      regexTestResult.value = null
    }

    const saveTaxonomy = async () => {
      try {
        if (editingTaxonomy.value.id && taxonomies.value.some(t => t.id === editingTaxonomy.value.id && t !== editingTaxonomy.value)) {
          // Update existing
          await taxonomyStore.updateTaxonomy(editingTaxonomy.value.id, editingTaxonomy.value)
        } else {
          // Create new
          await taxonomyStore.createTaxonomy(editingTaxonomy.value)
        }

        await loadTaxonomies()
        showSuccess('Taxonomy saved successfully!')
        editingTaxonomy.value = null
      } catch (error) {
        logger.error('Error saving taxonomy:', error)
        showError('Error saving taxonomy: ' + (error.response?.data?.detail || error.message))
      }
    }

    const deleteTaxonomy = async (id) => {
      const confirmed = await showConfirm({
        title: 'Delete Taxonomy',
        message: 'Are you sure you want to delete this taxonomy?',
        confirmText: 'Delete',
        cancelText: 'Cancel'
      })
      if (!confirmed) {
        return
      }

      try {
        // Get the taxonomy being deleted to know its priority
        const deletedTaxonomy = taxonomies.value.find(t => t.id === id)
        if (!deletedTaxonomy) {
          throw new Error('Taxonomy not found')
        }

        // Delete the taxonomy
        await taxonomyStore.deleteTaxonomy(id)

        // Reorder priorities for remaining taxonomies
        const remainingTaxonomies = taxonomies.value.filter(t => t.id !== id && t.priority > deletedTaxonomy.priority)

        if (remainingTaxonomies.length > 0) {
          // Create new priority order
          const newOrder = taxonomies.value
            .filter(t => t.id !== id)
            .map(taxonomy => {
              if (taxonomy.priority > deletedTaxonomy.priority) {
                return { ...taxonomy, priority: taxonomy.priority - 1 }
              }
              return taxonomy
            })

          // Update priorities in backend
          await taxonomyStore.reorderTaxonomies(newOrder)
        }

        await loadTaxonomies()
      } catch (error) {
        logger.error('Error deleting taxonomy:', error)
        showError('Error deleting taxonomy: ' + (error.response?.data?.detail || error.message))
      }
    }

    const testRegex = () => {
      if (!editingTaxonomy.value.regex_pattern || !testTags.value) {
        return
      }

      const regex = createJsRegExp(editingTaxonomy.value.regex_pattern)
      if (!regex) {
        regexTestResult.value = {
          success: false,
          match: null,
          groups: [],
          message: 'Invalid regex pattern (converted from Python syntax)'
        }
        return
      }

      const match = testTags.value.match(regex)
      if (match) {
        regexTestResult.value = {
          success: true,
          match: match[0],
          groups: match.slice(1),
          message: 'Pattern matches!'
        }
      } else {
        regexTestResult.value = {
          success: false,
          match: null,
          groups: [],
          message: 'Pattern does not match test string'
        }
      }
    }

    const renderCytoscapeGraph = () => {
      if (!taxonomies.value || !cytoscapeContainer.value) return;

      // Destroy existing instance
      if (cytoscapeInstance.value) {
        cytoscapeInstance.value.destroy();
      }

      // Convert taxonomies to Cytoscape nodes
      const nodes = taxonomies.value.map(taxonomy => ({
        data: {
          id: taxonomy.id,
          label: taxonomy.name,
          hierarchical: taxonomy.hierarchical || false,
          priority: taxonomy.priority,
          relations: taxonomy.relations || [],
          color: taxonomy.color || '#3B82F6'
        }
      }));

      // Convert relations to Cytoscape edges
      const edges = [];
      const taxonomyIds = new Set(taxonomies.value.map(t => t.id));

      taxonomies.value.forEach(taxonomy => {
        if (taxonomy.relations) {
          taxonomy.relations.forEach(relation => {
            if (relation.targets && taxonomyIds.has(relation.targets)) {
              edges.push({
                data: {
                  id: `${taxonomy.id}-${relation.targets}`,
                  source: taxonomy.id,
                  target: relation.targets,
                  label: relation.group || 'related'
                }
              });
            }
          });
        }
      });

      logger.info('🎨 Rendering TaxonomyEditor Cytoscape graph:', { nodes, edges });

      // Initialize Cytoscape
      cytoscapeInstance.value = cytoscape({
        container: cytoscapeContainer.value,
        elements: [...nodes, ...edges],
        style: [
          {
            selector: 'node',
            style: {
              'shape': function(ele) {
                return ele.data('hierarchical') ? 'round-rectangle' : 'barrel';
              },
              'background-color': 'data(color)',
              'color': function(ele) {
                // Get background color
                const bgColor = ele.data('color') || '#3B82F6';
                // Convert hex to RGB for luminance calculation
                const hex = bgColor.replace('#', '');
                const r = parseInt(hex.substr(0, 2), 16);
                const g = parseInt(hex.substr(2, 2), 16);
                const b = parseInt(hex.substr(4, 2), 16);
                // Calculate luminance
                const luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255;
                // Return black text for light backgrounds, white for dark
                return luminance > 0.5 ? '#000000' : '#FFFFFF';
              },
              'label': 'data(label)',
              'text-valign': 'center',
              'text-halign': 'center',
              'font-size': '14px',
              'width': '150px',
              'height': '60px',
              'border-width': '2px',
              'border-color': '#1E40AF'
            }
          },
          {
            selector: 'node:selected',
            style: {
              'border-color': '#1E40AF',
              'border-width': '4px',
              'border-style': 'solid',
              'background-opacity': 0.8,
              'font-weight': 'bold',
              'color': '#1E40AF'
            }
          },
          {
            selector: 'edge',
            style: {
              'width': 2,
              'line-color': '#6B7280',
              'target-arrow-color': '#6B7280',
              'target-arrow-shape': 'triangle',
              'curve-style': 'bezier',
              'label': 'data(label)',
              'font-size': '10px',
              'color': '#374151'
            }
          }
        ],
        layout: {
          name: 'dagre',
          radius: 150,
          animate: true,
          animationDuration: 1000
        }
      });

      // Add event listeners
      cytoscapeInstance.value.on('tap', 'node', function(evt) {
        const node = evt.target;
        const taxonomyData = taxonomies.value?.find(t => t.id === node.data('id'));
        if (taxonomyData) {
          editTaxonomy(taxonomyData);
        }
      });

      cytoscapeInstance.value.on('tap', function(evt) {
        if (evt.target === cytoscapeInstance.value) {
          // Clicked on background, deselect
          selectedGraphNode.value = null;
          cytoscapeInstance.value.$('node').unselect();
        }
      });

      // Enable editing from graph
      cytoscapeInstance.value.on('dblclick', 'node', function(evt) {
        const node = evt.target;
        const taxonomyData = taxonomies.value?.find(t => t.id === node.data('id'));
        if (taxonomyData) {
          editTaxonomy(taxonomyData);
        }
      });
    };

    const selectGraphNode = (node) => {
      selectedGraphNode.value = node;
      editTaxonomy(node.id);

      // Select node in Cytoscape
      if (cytoscapeInstance.value) {
        cytoscapeInstance.value.$('node').unselect();
        cytoscapeInstance.value.$(`node[id="${node.id}"]`).select();
      }
    }

    const resetGraphView = () => {
      if (cytoscapeInstance.value) {
        cytoscapeInstance.value.fit();
      }
    }

    // Drag and Drop handlers
    const handleDragStart = (event, index) => {
      draggedIndex.value = index;
      event.dataTransfer.effectAllowed = 'move';
      event.target.style.opacity = '0.5';
    };

    const handleDragOver = (event) => {
      event.preventDefault();
      event.dataTransfer.dropEffect = 'move';
    };

    const handleDrop = (event, dropIndex) => {
      event.preventDefault();

      if (draggedIndex.value !== null && draggedIndex.value !== dropIndex) {
        const draggedTaxonomy = taxonomies.value[draggedIndex.value];
        const newTaxonomies = [...taxonomies.value];

        // Remove from old position
        newTaxonomies.splice(draggedIndex.value, 1);

        // Insert at new position
        newTaxonomies.splice(dropIndex, 0, draggedTaxonomy);

        // Update the array
        taxonomies.value = newTaxonomies;

        // Save the new order to backend
        saveTaxonomyOrder();
      }
    };

    const handleDragEnd = (event) => {
      event.target.style.opacity = '';
      draggedIndex.value = null;
    };

    const saveTaxonomyOrder = async () => {
      try {
        const taxonomiesWithPriority = taxonomies.value.map((taxonomy, index) => ({
          ...taxonomy,
          priority: index + 1
        }));

        await taxonomyStore.reorderTaxonomies(taxonomiesWithPriority);
        logger.info('Taxonomy order saved successfully');
      } catch (error) {
        logger.error('Error saving taxonomy order:', error);
      }
    };

    const getNodeColor = (node) => {
      if (node.selected) return '#3B82F6'

      // Use user-defined color or generate one based on taxonomy ID
      if (node.color) return node.color

      // Generate consistent color based on taxonomy ID hash
      const hash = node.id.split('').reduce((acc, char) => acc + char.charCodeAt(0), 0)
      const hue = hash % 360
      return `hsl(${hue}, 70%, 50%)`
    }

    onMounted(() => {
      loadTaxonomies()

      // Listen for edit events from graph
      window.addEventListener('editTaxonomyFromGraph', (event) => {
        const { taxonomy } = event.detail;
        editTaxonomy(taxonomy);
      });

      // Add resize observer to handle container resizing
      if (cytoscapeContainer.value) {
        const resizeObserver = new ResizeObserver(() => {
          if (cytoscapeInstance.value) {
            cytoscapeInstance.value.resize();
          }
        });
        resizeObserver.observe(cytoscapeContainer.value);
      }
    })

    // Rebuild graph when taxonomies change
    watch(taxonomies, () => {
      nextTick(() => {
        renderCytoscapeGraph();
      })
    }, { deep: true })

    // Computed properties for tag creation
    const generatedTag = computed(() => {
      return tagBuilderParts.value.map(part => {
        if (part.type === 'static') {
          return part.value
        } else {
          return part.value || ''
        }
      }).join('')
    })

    const canCreateTag = computed(() => {
      const result = tagBuilderParts.value.filter( part => ['text', 'dropdown'].includes(part.type)).every(part =>
        part.value && part.value.trim()
      )
      logger.info('Debug canCreateTag:', {
        tagBuilderParts: tagBuilderParts.value,
        result,
        generatedTag: generatedTag.value
      })
      return result
    })

    // Methods for tag management
    const loadTaxonomies = async () => {
      try {
        await taxonomyStore.loadTaxonomies()
        taxonomies.value = taxonomyStore.taxonomies
      } catch (error) {
        logger.error('Error loading taxonomies:', error)
      }
    }

    const showTaxonomyTags = async (taxonomy) => {
      selectedTaxonomy.value = taxonomy
      try {
        taxonomyTags.value = await taxonomyStore.getTaxonomyTags(taxonomy.id)

        // Load usage data for tags
        const usagePromises = taxonomyTags.value.map(async (tag) => {
          const tagName = tag.name
          try {
            const usageData = await taxonomyStore.getTagUsage(tagName)
            return { [tagName]: usageData.length }
          } catch (error) {
            return { [tagName]: 0 }
          }
        })

        const usageResults = await Promise.all(usagePromises)
        tagUsage.value = usageResults.reduce((acc, result) => ({ ...acc, ...result }), {})

        showTagsModal.value = true
      } catch (error) {
        logger.error('Error loading taxonomy tags:', error)
        showError('Error loading taxonomy tags: ' + (error.response?.data?.detail || error.message))
      }
    }

    const closeTagsModal = () => {
      showTagsModal.value = false
      selectedTaxonomy.value = null
      taxonomyTags.value = []
      tagUsageData.value = {}
    }

    const createTaxonomyTag = async (taxonomy) => {
      selectedTaxonomy.value = taxonomy

      try {
        // Ensure tags are loaded first
        if (tagStore.tags.length === 0) {
          await tagStore.loadTags()
        }

        // Parse the regex pattern to extract static parts and capture groups
        const parts = taxonomyStore.parseTaxonomyPattern(taxonomy.regex_pattern, taxonomy.relations)
        logger.info('Debug createTaxonomyTag - parsed parts:', parts)

        // Load existing tag values for dropdowns
        await taxonomyStore.loadDropdownValues(parts, taxonomy, tagStore.tags)
        logger.info('Debug createTaxonomyTag - parts after loadDropdownValues:', parts)

        tagBuilderParts.value = parts
        logger.info('Debug createTaxonomyTag - tagBuilderParts set to:', tagBuilderParts.value)
        showCreateTagModal.value = true
      } catch (error) {
        logger.error('Error parsing taxonomy pattern:', error)
        tagBuilderParts.value = []
        showCreateTagModal.value = true
      }
    }

    const closeCreateTagModal = () => {
      showCreateTagModal.value = false
      selectedTaxonomy.value = null
      tagBuilderParts.value = []
    }

    const getTagUsageCount = (tag) => {
      return tagUsageData.value[tag] || 0
    }

    const createNewTag = async () => {
      if (!canCreateTag.value || !generatedTag.value) return

      try {
        await taxonomyStore.createTaxonomyTag(generatedTag.value, selectedTaxonomy.value.id)

        // Refresh the tags list
        await showTaxonomyTags(selectedTaxonomy.value)

        // Clear the tag builder
        tagBuilderParts.value.forEach(part => {
          if (part.type !== 'static') {
            part.value = ''
          }
        })

        showSuccess('Tag created successfully!')
        closeCreateTagModal()
      } catch (error) {
        logger.error('Error creating tag:', error)
        showError('Error creating tag: ' + (error.response?.data?.detail || error.message))
      }
    }

    </script>
