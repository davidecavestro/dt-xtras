<template>
  <div class="px-4 py-6 sm:px-0">
    <div class="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
      <h2 class="text-2xl font-bold text-gray-900 dark:text-white mb-6">Tag Manager</h2>
      <p class="text-gray-600 dark:text-gray-400 mb-6">
        Manage tags and link them to Dependency-Track projects
      </p>

      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <!-- Tag Input -->
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300">
            Tag
            <span class="ml-2 text-xs text-gray-500 dark:text-gray-400">
              (e.g., env:prod, cust:acme, myapp:1.0.0)
            </span>
          </label>
          <input
            v-model="newTag"
            type="text"
            class="mt-1 block w-full rounded-md border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-white shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
            placeholder="Enter tag..."
            @input="validateTag"
          />
          <div v-if="tagValidation.message" :class="[
            'mt-1 text-xs',
            tagValidation.valid ? 'text-green-600 dark:text-green-400' : 'text-red-600 dark:text-red-400'
          ]">
            {{ tagValidation.message }}
          </div>
        </div>

        <!-- Taxonomy Patterns -->
        <div class="bg-gray-50 dark:bg-gray-700 rounded-lg p-4">
          <h3 class="text-sm font-semibold text-gray-900 dark:text-white mb-3">Taxonomy Patterns</h3>
          <div class="space-y-2">
            <div v-for="taxonomy in taxonomies" :key="taxonomy.id" class="flex items-start">
              <span class="font-medium text-gray-700 dark:text-gray-300 text-sm mr-2 min-w-0">
                {{ taxonomy.name }}:
              </span>
              <code class="text-xs bg-gray-100 dark:bg-gray-600 px-2 py-1 rounded text-gray-800 dark:text-gray-200 break-all">
                {{ taxonomy.regex_pattern }}
              </code>
            </div>
          </div>
        </div>
      </div>

      <!-- Action Buttons -->
      <div class="mt-4 flex gap-2">
        <button
          @click="createTag"
          :disabled="!tagValidation.valid || !newTag.trim()"
          class="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
        >
          Create Tag
        </button>
        <button
          @click="clearForm"
          class="px-4 py-2 bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-md hover:bg-gray-300 dark:hover:bg-gray-600 transition-colors"
        >
          Clear
        </button>
      </div>
    </div>

    <!-- Existing Tags Management -->
    <div class="bg-white dark:bg-gray-800 rounded-lg shadow p-6 mt-6">
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
                'px-3 py-1 text-sm rounded-md',
                tagsViewMode === 'list'
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300'
              ]"
            >
              <ListIcon class="w-4 h-4" />
            </button>
            <button
              @click="tagsViewMode = 'grid'"
              :class="[
                'px-3 py-1 text-sm rounded-md',
                tagsViewMode === 'grid'
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300'
              ]"
            >
              <GridIcon class="w-4 h-4" />
            </button>
            <button
              @click="tagsViewMode = 'deck'"
              :class="[
                'px-3 py-1 text-sm rounded-md',
                tagsViewMode === 'deck'
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300'
              ]"
            >
              <SquareIcon class="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>

      <!-- Tags List -->
      <div v-if="tags.length === 0" class="text-center py-8 text-gray-500 dark:text-gray-400">
        No tags created yet. Create your first tag above.
      </div>

      <!-- List View -->
      <div v-else-if="tagsViewMode === 'list'" class="space-y-3">
        <div
          v-for="tag in tags"
          :key="tag.name"
          class="flex items-center justify-between p-3 border border-gray-200 dark:border-gray-700 rounded-lg"
        >
          <div class="flex-1">
            <!-- Show tag name or edit input -->
            <div v-if="editingTag && editingTag.name === tag.name" class="flex items-center">
              <input
  :data-tag-name="tag.name"
  v-model="editingTagName"
  @keyup.enter="saveEditTag"
  @keyup.escape="cancelEditTag"
  @blur="saveEditTag"
  class="font-medium text-gray-900 dark:text-white bg-transparent border-b border-gray-300 dark:border-gray-600 focus:border-blue-500 focus:outline-none flex-1"
  placeholder="Tag name"
/>
              <button
                @click="saveEditTag"
                class="ml-2 p-1 bg-green-600 text-white text-xs rounded hover:bg-green-700"
                title="Save"
              >
                ✓
              </button>
              <button
                @click="cancelEditTag"
                class="ml-1 p-1 bg-gray-600 text-white text-xs rounded hover:bg-gray-700"
                title="Cancel"
              >
                ✕
              </button>
            </div>
            <div v-else>
              <div class="font-medium text-gray-900 dark:text-white">{{ tag.name }}</div>
              <div class="text-sm text-gray-600 dark:text-gray-400">
                Used by {{ tag.projectsCount || 0 }} projects
              </div>
            </div>
          </div>

          <div class="flex gap-1 p-2 flex-shrink-0">
            <button
              @click="viewTagProjects(tag)"
              class="p-1 bg-blue-600 text-white text-xs rounded hover:bg-blue-700 inline-flex items-center justify-center transition-colors"
              title="View Projects"
            >
              <Folder class="w-3 h-3" />
            </button>
            <button
              @click="startEditTag(tag)"
              class="p-1 bg-yellow-600 text-white text-xs rounded hover:bg-yellow-700 inline-flex items-center justify-center transition-colors"
              title="Edit Tag"
            >
              <Edit2 class="w-3 h-3" />
            </button>
            <button
              @click="deleteTag(tag)"
              class="p-1 bg-red-600 text-white text-xs rounded hover:bg-red-700 inline-flex items-center justify-center transition-colors"
              title="Delete"
            >
              <Trash2 class="w-3 h-3" />
            </button>
          </div>
        </div>
      </div>

      <!-- Grid View -->
      <div v-else-if="tagsViewMode === 'grid'" class="overflow-y-auto" style="height: 400px;">
        <vue3-datagrid
          :columns="gridColumns"
          :source="tags"
          :row-height="60"
          :virtual="true"
          :page-size="20"
          :theme="isDarkMode ? 'darkCompact' : 'compact'"
          :filter="true"
          :resize="true"
          :autoSizeColumn="{ mode: 'autoSizeOnTextOverlap' }"
          :stretch="true"
          :readonly="true"
        />
      </div>

      <!-- Deck View (Current Default) -->
      <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        <div
          v-for="tag in tags"
          :key="tag.name"
          class="bg-white dark:bg-gray-700 rounded-lg shadow p-4 border border-gray-200 dark:border-gray-600 hover:shadow-md transition-shadow flex flex-col"
        >
          <div class="flex-1">
            <!-- Show tag name or edit input -->
            <div v-if="editingTag && editingTag.name === tag.name" class="flex items-center">
              <input
  :data-tag-name="tag.name"
  v-model="editingTagName"
  @keyup.enter="saveEditTag"
  @keyup.escape="cancelEditTag"
  @blur="saveEditTag"
  class="font-medium text-gray-900 dark:text-white bg-transparent border-b border-gray-300 dark:border-gray-600 focus:border-blue-500 focus:outline-none flex-1"
  placeholder="Tag name"
/>
              <button
                @click="saveEditTag"
                class="ml-2 p-1 bg-green-600 text-white text-xs rounded hover:bg-green-700"
                title="Save"
              >
                ✓
              </button>
              <button
                @click="cancelEditTag"
                class="ml-1 p-1 bg-gray-600 text-white text-xs rounded hover:bg-gray-700"
                title="Cancel"
              >
                ✕
              </button>
            </div>
            <div v-else>
              <div class="font-medium text-gray-900 dark:text-white mb-2">{{ tag.name }}</div>
              <div class="text-sm text-gray-600 dark:text-gray-400">
                Used by {{ tag.projectsCount || 0 }} projects
              </div>
            </div>
          </div>

          <div class="flex justify-end gap-1 pt-2 mt-2 border-t border-gray-200 dark:border-gray-600">
            <button
              @click="viewTagProjects(tag)"
              class="p-1 bg-blue-600 text-white text-xs rounded hover:bg-blue-700 inline-flex items-center justify-center transition-colors"
              title="View Projects"
            >
              <Folder class="w-3 h-3" />
            </button>
            <button
              @click="startEditTag(tag)"
              class="p-1 bg-yellow-600 text-white text-xs rounded hover:bg-yellow-700 inline-flex items-center justify-center transition-colors"
              title="Edit Tag"
            >
              <Edit2 class="w-3 h-3" />
            </button>
            <button
              v-if="tagBelongsToTaxonomy(tag)"
              @click="startAidedEditTag(tag)"
              class="p-1 bg-purple-600 text-white text-xs rounded hover:bg-purple-700 inline-flex items-center justify-center transition-colors"
              title="Aided Edit"
            >
              <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-3 7h3m-3 4h3m-6-4h.01M9 16h.01"></path>
              </svg>
            </button>
            <button
              @click="deleteTag(tag)"
              class="p-1 bg-red-600 text-white text-xs rounded hover:bg-red-700 inline-flex items-center justify-center transition-colors"
              title="Delete"
            >
              <Trash2 class="w-3 h-3" />
            </button>
          </div>
        </div>
      </div>
    </div>


    <!-- Projects Modal -->
    <div v-if="showProjectsModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-white dark:bg-gray-800 rounded-lg shadow-xl max-w-2xl w-full mx-4 max-h-[80vh] overflow-y-auto">
        <div class="p-6">
          <div class="flex justify-between items-center mb-4">
            <h3 class="text-lg font-semibold text-gray-900 dark:text-white">
              Projects with tag: {{ selectedTag?.name }}
            </h3>
            <div class="text-sm text-gray-600 dark:text-gray-400">
              Click project names to view in Dependency Track UI
            </div>
            <button
              @click="closeProjectsModal"
              class="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
            >
              ✕
            </button>
          </div>

          <div v-if="tagProjects.length === 0" class="text-center py-8 text-gray-500 dark:text-gray-400">
            No projects found with this tag.
          </div>

          <div v-else class="space-y-3">
            <div
              v-for="project in tagProjects"
              :key="project.uuid"
              class="p-3 border border-gray-200 dark:border-gray-700 rounded-lg"
            >
              <div class="font-medium text-gray-900 dark:text-white">
                <a
                  :href="buildDTProjectUrl(project.uuid)"
                  target="_blank"
                  class="text-blue-600 hover:text-blue-800 hover:underline"
                  title="View in Dependency Track"
                >
                  {{ project.displayName }}
                </a>
              </div>
              <div class="text-sm text-gray-600 dark:text-gray-400">
                {{ project.name }} v{{ project.version }}
                <span class="ml-2">
                  <a
                    :href="buildDTProjectUrl(project.uuid)"
                    target="_blank"
                    class="text-blue-600 hover:text-blue-800 hover:underline"
                    title="View in Dependency Track"
                  >
                    UUID: {{ project.uuid }}
                  </a>
                </span>
                <span v-if="project.tags && project.tags.length > 0" class="ml-2">
                  All tags: {{ project.tags.join(', ') }}
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Create Tag Modal (Aided Edit) -->
    <div v-if="showCreateTagModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-white dark:bg-gray-800 rounded-lg shadow-xl max-w-4xl w-full mx-4 max-h-[80vh] overflow-y-auto">
        <div class="p-6">
          <div class="flex justify-between items-center mb-4">
            <h3 class="text-lg font-semibold text-gray-900 dark:text-white">
              {{ editingTag ? 'Edit Tag' : 'Create Tag' }} for {{ selectedTaxonomy?.name }}
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
                  <option v-for="option in part.options" :key="option" :value="option">
                    {{ option }}
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
              @click="createOrUpdateTag"
              :disabled="!canCreateTag"
              class="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
            >
              {{ editingTag ? 'Update Tag' : 'Create Tag' }}
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
  </div>
</template>

<script>
import { ref, computed, watch, onMounted, nextTick } from 'vue'
import axios from 'axios'
import { buildDTProjectUrl } from '../config.js'
import { useRouter } from 'vue-router'
import { useTagStore } from '../stores/tags.js'
import { useToast } from '../composables/useToast.js'
import { List as ListIcon, Grid as GridIcon, Square as SquareIcon, Folder, Trash2, Edit2 } from 'lucide-vue-next'
import Vue3Datagrid, { VGridVueTemplate } from '@revolist/vue3-datagrid'

export default {
  name: 'TagManager',
  components: {
    Vue3Datagrid,
    VGridVueTemplate,
    ListIcon,
    GridIcon,
    SquareIcon,
    Folder,
    Trash2,
    Edit2
  },
  setup() {
    const router = useRouter()
    const tagStore = useTagStore()
    const { showSuccess, showError } = useToast()

    // State
    const taxonomies = ref([])
    const tags = ref([])
    const projects = ref([])
    const newTag = ref('')
    const tagValidation = ref({ valid: false, message: '' })
    const showProjectsModal = ref(false)
    const selectedTag = ref(null)
    const tagProjects = ref([])
    const loading = ref(false)
    const tagsViewMode = ref('deck') // 'list', 'grid', or 'deck'

    // Create Tag Modal state
    const showCreateTagModal = ref(false)
    const selectedTaxonomy = ref(null)
    const tagBuilderParts = ref([])
    const editingTag = ref(null)
    const editInput = ref(null) // Ref for edit input focus

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
              console.log('View projects for tag:', props.model.name)
            },
            edit: () => {
              console.log('Edit tag:', props.model.name)
            },
            removeTag: () => {
              console.log('Delete tag:', props.model.name)
            }
          }
        }
      }
    }

    // Methods
    const loadTaxonomies = async () => {
      try {
        const response = await axios.get('/api/taxonomies')
        taxonomies.value = response.data
      } catch (error) {
        console.error('Error loading taxonomies:', error)
      }
    }

    const loadTags = async () => {
      loading.value = true
      try {
        const response = await axios.get('/api/tags')
        tags.value = response.data
      } catch (error) {
        console.error('Error loading tags:', error)
        tags.value = []
      } finally {
        loading.value = false
      }
    }

    const loadProjects = async () => {
      try {
        // Load projects from our backend - auth service handles token automatically
        const response = await axios.get('/api/projects')

        projects.value = response.data.map(project => ({
          id: project.uuid, // Use uuid as id
          uuid: project.uuid,
          name: project.name,
          version: project.version || 'latest',
          displayName: project.version ? `${project.name}:${project.version}` : `${project.name}:latest`,
          tags: project.tags || []
        }))
      } catch (error) {
        console.error('Error loading projects:', error)
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
          const regex = new RegExp(taxonomy.regex_pattern)
          const matches = regex.test(tag)
          return matches
        } catch (error) {
          console.error('Invalid regex regex_pattern:', taxonomy.regex_pattern, error)
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

    const createTag = async () => {
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
        }
      } catch (error) {
        console.error('Error creating tag:', error)
        tagValidation.value = {
          valid: false,
          message: `❌ Error: ${tagStore.error || error.message}`
        }
      }
    }


    const deleteTag = async (tag) => {
      if (!confirm(`Are you sure you want to delete tag "${tag.name}"?`)) return

      try {
        await axios.delete(`/api/tags/${tag.name}`)

        // Remove the tag from our list
        const index = tags.value.findIndex(t => t.name === tag.name)
        if (index > -1) {
          tags.value.splice(index, 1)
          showSuccess('Tag deleted successfully')
        }
      } catch (error) {
        console.error('Error deleting tag:', error)
        showError('Failed to delete tag', 'Please try again.')
      }
    }

    const viewTagProjects = async (tag) => {
      selectedTag.value = tag
      showProjectsModal.value = true

      try {
        const response = await axios.get(`/api/tags/${tag.name}/projects`)
        tagProjects.value = response.data
      } catch (error) {
        console.error('Error loading tag projects:', error)
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


    const refreshTags = () => {
      loadTags()
      loadProjects()
    }

    const formatDate = (dateString) => {
      return new Date(dateString).toLocaleString()
    }

    // Edit tag functionality
    const editingTagName = ref('')

    const startEditTag = (tag) => {
      editingTag.value = tag
      editingTagName.value = tag.name
      // focus the editor after DOM update
      nextTick(() => {
        const input = document.querySelector(`input[data-tag-name="${tag.name}"]`)
        if (input) {
          input.focus()
          /* input.select() */
        }
      })
    }

    const cancelEditTag = () => {
      editingTag.value = null
      editingTagName.value = ''
    }

    const saveEditTag = async () => {
      if (!editingTag.value || !editingTagName.value.trim()) {
        return
      }

      try {
        await axios.put(`/api/tags/${editingTag.value.name}`, {
          name: editingTagName.value.trim()
        })

        // Update the tag in the local state
        const tagIndex = tags.value.findIndex(t => t.name === editingTag.value.name)
        if (tagIndex !== -1) {
          tags.value[tagIndex].name = editingTagName.value.trim()
        }

        cancelEditTag()
        showSuccess('Tag updated successfully')
      } catch (error) {
        console.error('Error updating tag:', error)
        showError('Failed to update tag', 'Please try again.')
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
      return tagBuilderParts.value.every(part =>
        part.type === 'static' || (part.value && part.value.trim())
      )
    })

    // Methods for aided editing
    const tagBelongsToTaxonomy = (tag) => {
      return tag.taxonomy && tag.taxonomy.trim() !== ''
    }

    const startAidedEditTag = async (tag) => {
      try {
        // Find taxonomy that matches this tag pattern
        const matchingTaxonomy = taxonomies.value.find(taxonomy => {
          const regex = new RegExp(taxonomy.regex_pattern)
          return regex.test(tag.name)
        })

        if (!matchingTaxonomy) {
          showError('No matching taxonomy found for this tag')
          return
        }

        selectedTaxonomy.value = matchingTaxonomy
        editingTag.value = tag

        // Parse the tag using the taxonomy pattern to pre-populate fields
        const regex = new RegExp(matchingTaxonomy.regex_pattern)
        const match = tag.name.match(regex)

        if (match) {
          // Parse taxonomy pattern to extract parts
          const parts = parseTaxonomyPattern(matchingTaxonomy.regex_pattern)

          // Load dropdown options for parts
          await loadTagValuesForDropdowns(parts)

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
        } else {
          // If no match, just load empty parts with dropdown options
          const parts = parseTaxonomyPattern(matchingTaxonomy.regex_pattern)
          await loadTagValuesForDropdowns(parts)
          tagBuilderParts.value = parts
        }

        showCreateTagModal.value = true
      } catch (error) {
        console.error('Error starting aided edit:', error)
        showError('Failed to open edit modal')
      }
    }

    const parseTaxonomyPattern = (pattern) => {
      const parts = []
      let lastIndex = 0

      // Remove regex anchors (^ and $) from pattern for display
      const cleanPattern = pattern.replace(/^\^|\$$/g, '')

      // Find all capture groups: (?<name>pattern)
      const captureGroupRegex = /\(\?<([^>]+)>([^)]+)\)/g
      let match

      while ((match = captureGroupRegex.exec(cleanPattern)) !== null) {
        // Add static text before this capture group
        if (match.index > lastIndex) {
          const staticText = cleanPattern.substring(lastIndex, match.index)
          if (staticText) {
            parts.push({
              type: 'static',
              value: staticText
            })
          }
        }

        // Check if this capture group has a corresponding relation
        const hasRelation = selectedTaxonomy.value?.relations?.some(rel => rel.group === match[1])

        // Add capture group part
        parts.push({
          type: hasRelation ? 'dropdown' : 'text', // Use dropdown only if relation exists
          name: match[1],
          value: '',
          options: [],
          pattern: match[2]
        })

        lastIndex = captureGroupRegex.lastIndex
      }

      // Add any remaining static text
      if (lastIndex < cleanPattern.length) {
        const staticText = cleanPattern.substring(lastIndex)
        if (staticText) {
          parts.push({
            type: 'static',
            value: staticText
          })
        }
      }

      return parts
    }

    const loadTagValuesForDropdowns = async (parts) => {
      for (const part of parts) {
        if (part.type === 'dropdown' && part.name) {
          // For associative taxonomies get tags from related taxonomies
          if (selectedTaxonomy.value.relations && selectedTaxonomy.value.relations.length > 0) {
            // Find related taxonomy for this part
            const relation = selectedTaxonomy.value.relations.find(rel => rel.group === part.name)
            if (relation && relation.targets) {
              const targetTaxonomyId = relation.targets

              // Get tags from the related taxonomy
              const response = await axios.get(`/api/taxonomies/${targetTaxonomyId}/tags`)
              const relatedTags = response.data || []

              // Extract values from related tags using their own regex pattern
              const targetTaxonomy = taxonomies.value.find(t => t.id === targetTaxonomyId)
              if (targetTaxonomy && targetTaxonomy.regex_pattern) {
                const uniqueValues = [...new Set(relatedTags.map(tag => {
                  try {
                    const regex = new RegExp(targetTaxonomy.regex_pattern)
                    const tag_name = tag.name || tag // Handle both tag object and string
                    const match = tag_name.match(regex)
                    if (match){
                      if (match.length > 2){ // multiple capture groups, try to rejoin them by convention to discard the prefix
                        return match[1] + ':' + match[2]
                      } else if (match.length === 2){ // single capture group, use the captured value
                        return match[1]
                      }
                    }
                    return tag_name
                  } catch (e){
                    console.error(`Regex error for related tag ${tag.name}:`, e)
                    return tag.name || tag // Fallback to tag name
                  }
                }).filter(Boolean))]

                part.options = uniqueValues.sort()
              } else {
                // If no regex pattern, use tag names as-is
                const tagNames = relatedTags.map(tag => tag.name || tag).filter(Boolean)
                part.options = tagNames.sort()
              }
            }
          }
        }
      }
    }

    const closeCreateTagModal = () => {
      showCreateTagModal.value = false
      selectedTaxonomy.value = null
      tagBuilderParts.value = []
      editingTag.value = null
    }

    const createOrUpdateTag = async () => {
      if (!canCreateTag.value || !generatedTag.value) return

      try {
        if (editingTag.value) {
          // Update existing tag
          await axios.put(`/api/tags/${editingTag.value.name}`, {
            name: generatedTag.value,
            taxonomy_id: selectedTaxonomy.value.id
          })
          showSuccess(`Tag "${generatedTag.value}" updated successfully!`)
        } else {
          // Create new tag
          await axios.post('/api/tags', {
            name: generatedTag.value,
            taxonomy_id: selectedTaxonomy.value.id
          })
          showSuccess(`Tag "${generatedTag.value}" created successfully!`)
        }

        await loadTags()
        closeCreateTagModal()
      } catch (error) {
        console.error('Error creating/updating tag:', error)
        showError('Failed to save tag')
      }
    }

    return {
      taxonomies,
      tags,
      projects,
      newTag,
      editingTag,
      editingTagName,
      tagValidation,
      showProjectsModal,
      selectedTag,
      tagProjects,
      loading,
      tagsViewMode,
      isDarkMode,
      gridColumns,
      validateTag,
      selectSuggestedTag,
      createTag,
      clearForm,
      deleteTag,
      viewTagProjects,
      startEditTag,
      startAidedEditTag,
      tagBelongsToTaxonomy,
      cancelEditTag,
      saveEditTag,
      refreshTags,
      formatDate,
      closeProjectsModal,
      // Create Tag Modal
      showCreateTagModal,
      selectedTaxonomy,
      tagBuilderParts,
      generatedTag,
      canCreateTag,
      closeCreateTagModal,
      createOrUpdateTag,
      buildDTProjectUrl
    }
  }
}
</script>
