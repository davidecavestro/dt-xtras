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
            <div class="font-medium text-gray-900 dark:text-white">{{ tag.name }}</div>
            <div class="text-sm text-gray-600 dark:text-gray-400">
              Used by {{ tag.projectsCount || 0 }} projects
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
          class="bg-white dark:bg-gray-700 rounded-lg shadow p-4 border border-gray-200 dark:border-gray-600 hover:shadow-md transition-shadow"
        >
          <div class="flex justify-between items-center">
            <div class="flex-1">
              <div class="font-medium text-gray-900 dark:text-white mb-2">{{ tag.name }}</div>
              <div class="text-sm text-gray-600 dark:text-gray-400">
                Used by {{ tag.projectsCount || 0 }} projects
              </div>
            </div>

            <div class="flex gap-1 p-1 flex-shrink-0">
              <button
                @click="viewTagProjects(tag)"
                class="p-1 bg-blue-600 text-white text-xs rounded hover:bg-blue-700 inline-flex items-center justify-center transition-colors"
                title="View Projects"
              >
                <Folder class="w-3 h-3" />
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
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import axios from 'axios'
import { buildDTProjectUrl } from '../config.js'
import auth from '../services/auth.js'
import { useRouter } from 'vue-router'
import { useTagStore } from '../stores/tags.js'
import { List as ListIcon, Grid as GridIcon, Square as SquareIcon, Folder, Trash2 } from 'lucide-vue-next'
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
    Trash2
  },
  setup() {
    const router = useRouter()
    const tagStore = useTagStore()

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
        }
      } catch (error) {
        console.error('Error deleting tag:', error)
        alert('Failed to delete tag. Please try again.')
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

    // Lifecycle
    onMounted(() => {
      loadTaxonomies()
      loadTags()
      loadProjects()
    })

    return {
      taxonomies,
      tags,
      projects,
      newTag,
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
      closeProjectsModal,
      refreshTags,
      formatDate,
      buildDTProjectUrl
    }
  }
}
</script>
