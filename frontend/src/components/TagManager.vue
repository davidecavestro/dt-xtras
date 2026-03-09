<template>
  <div class="max-w-7xl mx-auto p-6 space-y-6">
    <!-- Header -->
    <div class="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
      <h1 class="text-2xl font-bold text-gray-900 dark:text-white">Tag Management</h1>
      <p class="text-gray-600 dark:text-gray-400 mt-2">
        Manage tags and link them to Dependency-Track projects
      </p>
    </div>

    <!-- Tag Creation Form -->
    <div class="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
      <h2 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">Create New Tag</h2>

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

        <!-- Taxonomy Hints -->
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300">
            Taxonomy Hints
          </label>
          <div class="mt-1 space-y-2">
            <div v-for="taxonomy in taxonomies" :key="taxonomy.id" class="text-xs">
              <span class="font-medium text-gray-700 dark:text-gray-300">{{ taxonomy.name }}:</span>
              <span class="text-gray-600 dark:text-gray-400 ml-1">{{ taxonomy.pattern }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Suggested Tags -->
      <div v-if="suggestedTags.length > 0" class="mt-4">
        <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
          Suggested Tags
        </label>
        <div class="flex flex-wrap gap-2">
          <button
            v-for="tag in suggestedTags"
            :key="tag"
            @click="selectSuggestedTag(tag)"
            class="px-3 py-1 text-xs bg-blue-100 dark:bg-blue-900 text-blue-800 dark:text-blue-200 rounded-full hover:bg-blue-200 dark:hover:bg-blue-800 transition-colors"
          >
            {{ tag }}
          </button>
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
    <div class="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
      <div class="flex justify-between items-center mb-4">
        <h2 class="text-lg font-semibold text-gray-900 dark:text-white">Existing Tags</h2>
        <button
          @click="refreshTags"
          class="px-3 py-1 text-sm bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-md hover:bg-gray-300 dark:hover:bg-gray-600 transition-colors"
        >
          Refresh
        </button>
      </div>

      <!-- Tags List -->
      <div v-if="tags.length === 0" class="text-center py-8 text-gray-500 dark:text-gray-400">
        No tags created yet. Create your first tag above.
      </div>

      <div v-else class="space-y-3">
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

          <div class="flex gap-2">
            <button
              @click="viewTagProjects(tag)"
              class="px-3 py-1 text-sm bg-blue-100 dark:bg-blue-900 text-blue-800 dark:text-blue-200 rounded hover:bg-blue-200 dark:hover:bg-blue-800 transition-colors"
            >
              View Projects
            </button>
            <button
              @click="editTag(tag)"
              class="px-3 py-1 text-sm bg-yellow-100 dark:bg-yellow-900 text-yellow-800 dark:text-yellow-200 rounded hover:bg-yellow-200 dark:hover:bg-yellow-800 transition-colors"
            >
              Edit
            </button>
            <button
              @click="deleteTag(tag)"
              class="px-3 py-1 text-sm bg-red-100 dark:bg-red-900 text-red-800 dark:text-red-200 rounded hover:bg-red-200 dark:hover:bg-red-800 transition-colors"
            >
              Delete
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Project Linking -->
    <div class="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
      <div class="flex items-center justify-between mb-4">
        <h2 class="text-lg font-semibold text-gray-900 dark:text-white">Link Tags to Projects</h2>
        <div class="text-sm text-gray-600 dark:text-gray-400">
          Click project names to view in Dependency Track UI
        </div>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <!-- Project Selection -->
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300">
            Select Projects
          </label>
          <div class="mt-1 border border-gray-300 dark:border-gray-600 rounded-md max-h-48 overflow-y-auto">
            <div v-for="project in projects" :key="project.uuid" class="p-2 hover:bg-gray-50 dark:hover:bg-gray-700">
              <label class="flex items-center">
                <input
                  type="checkbox"
                  :value="project.uuid"
                  v-model="selectedProjects"
                  class="mr-2 rounded border-gray-300 dark:border-gray-600 text-blue-600 focus:ring-blue-500"
                />
                <div>
                  <div class="font-medium text-gray-900 dark:text-white">
                  <a
                    :href="`http://localhost:3000/projects/${project.uuid}`"
                    target="_blank"
                    class="text-blue-600 hover:text-blue-800 hover:underline"
                    title="View in Dependency Track"
                  >
                    {{ project.displayName }}
                  </a>
                </div>
                  <div class="text-xs text-gray-600 dark:text-gray-400">
                    {{ project.name }} v{{ project.version }}
                    <span class="ml-2">
                      <a
                        :href="`http://localhost:3000/projects/${project.uuid}`"
                        target="_blank"
                        class="text-blue-600 hover:text-blue-800 hover:underline"
                        title="View in Dependency Track"
                      >
                        UUID: {{ project.uuid.slice(0, 8) }}...
                      </a>
                    </span>
                    <span v-if="project.tags.length > 0" class="ml-2">
                      Tags: {{ project.tags.join(', ') }}
                    </span>
                  </div>
                </div>
              </label>
            </div>
          </div>
        </div>

        <!-- Tag Selection -->
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300">
            Select Tags to Apply
          </label>
          <div class="mt-1 border border-gray-300 dark:border-gray-600 rounded-md max-h-48 overflow-y-auto">
            <div v-for="tag in tags" :key="tag.name" class="p-2 hover:bg-gray-50 dark:hover:bg-gray-700">
              <label class="flex items-center">
                <input
                  type="checkbox"
                  :value="tag.name"
                  v-model="selectedTags"
                  class="mr-2 rounded border-gray-300 dark:border-gray-600 text-blue-600 focus:ring-blue-500"
                />
                <div>
                  <div class="font-medium text-gray-900 dark:text-white">{{ tag.name }}</div>
                  <div class="text-xs text-gray-600 dark:text-gray-400">
                    {{ tag.projectsCount || 0 }} projects
                  </div>
                </div>
              </label>
            </div>
          </div>
        </div>
      </div>

      <!-- Link Actions -->
      <div class="mt-4 flex gap-2">
        <button
          @click="linkTagsToProjects"
          :disabled="selectedProjects.length === 0 || selectedTags.length === 0"
          class="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
        >
          Link Tags to Projects ({{ selectedProjects.length }} projects, {{ selectedTags.length }} tags)
        </button>
        <button
          @click="unlinkTagsFromProjects"
          :disabled="selectedProjects.length === 0 || selectedTags.length === 0"
          class="px-4 py-2 bg-orange-600 text-white rounded-md hover:bg-orange-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
        >
          Unlink Tags from Projects
        </button>
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
                  :href="`http://localhost:3000/projects/${project.uuid}`"
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
                    :href="`http://localhost:3000/projects/${project.uuid}`"
                    target="_blank"
                    class="text-blue-600 hover:text-blue-800 hover:underline"
                    title="View in Dependency Track"
                  >
                    UUID: {{ project.uuid }}
                  </a>
                </span>
                <span v-if="project.tags.length > 0" class="ml-2">
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
import axios from 'axios'
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'

export default {
  name: 'TagManager',
  setup() {
    const router = useRouter()

    // State
    const taxonomies = ref([])
    const tags = ref([])
    const projects = ref([])
    const newTag = ref('')
    const selectedProjects = ref([])
    const selectedTags = ref([])
    const tagValidation = ref({ valid: false, message: '' })
    const showProjectsModal = ref(false)
    const selectedTag = ref(null)
    const tagProjects = ref([])
    const loading = ref(false)

    // Computed
    const suggestedTags = computed(() => {
      if (!taxonomies.value.length || !newTag.value) return []

      const suggestions = []
      const input = newTag.value.toLowerCase()

      taxonomies.value.forEach(taxonomy => {
        // Generate example tags based on taxonomy patterns
        if (taxonomy.id === 'customer') {
          suggestions.push(`cust:acme`, `cust:beta`, `cust:demo`)
        } else if (taxonomy.id === 'env') {
          suggestions.push(`env:prod`, `env:staging`, `env:dev`)
        } else if (taxonomy.id === 'product_version') {
          suggestions.push(`myapp:1.0.0`, `webapp:2.1.0`, `api:3.0.0`)
        } else if (taxonomy.id === 'deploy') {
          suggestions.push(`deploy:prod:cust:acme:myapp:1.0.0`)
        }
      })

      return suggestions.filter(tag =>
        tag.toLowerCase().includes(input) &&
        !tags.value.some(existing => existing.name === tag)
      ).slice(0, 8)
    })

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
        const response = await axios.get('/api/project-versions')
        const projectVersions = response.data
        // Convert to project format with tags and version
        projects.value = projectVersions.map(pv => ({
          id: pv.id,
          uuid: pv.project_uuid,
          name: pv.name,
          version: pv.version,
          displayName: `${pv.name}:${pv.version}`,
          tags: pv.tags || []
        }))
      } catch (error) {
        console.error('Error loading projects:', error)
        // If project-versions fails, try loading from DT API directly
        try {
          const dtResponse = await axios.get('/api/v1/project')
          // DT API projects have version info, use the actual version
          projects.value = dtResponse.data.map(project => ({
            id: project.uuid, // Use uuid as id for DT API projects
            uuid: project.uuid,
            name: project.name,
            version: project.version || 'latest',
            displayName: project.version ? `${project.name}:${project.version}` : `${project.name}:latest`,
            tags: project.tags || []
          }))
        } catch (dtError) {
          console.error('Error loading projects from DT API:', dtError)
          projects.value = []
        }
      }
    }

    const validateTag = () => {
      if (!newTag.value.trim()) {
        tagValidation.value = { valid: false, message: 'Tag is required' }
        return
      }

      const tag = newTag.value.trim()

      // Check if tag matches any taxonomy pattern
      const matchingTaxonomy = taxonomies.value.find(taxonomy => {
        try {
          const regex = new RegExp(taxonomy.regex_pattern)
          return regex.test(tag)
        } catch (error) {
          return false
        }
      })

      if (matchingTaxonomy) {
        tagValidation.value = {
          valid: true,
          message: `✅ Matches ${matchingTaxonomy.name} taxonomy`
        }
      } else {
        tagValidation.value = {
          valid: true,
          message: '⚠️ Custom tag (no taxonomy match)'
        }
      }

      // Check for duplicates
      if (tags.value.some(existing => existing.name === tag)) {
        tagValidation.value = {
          valid: false,
          message: '❌ Tag already exists'
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
        const response = await axios.post('/api/tags', {
          name: newTag.value.trim()
        })

        if (response.data) {
          // Add the new tag to our list
          tags.value.push(response.data)
          newTag.value = ''
          tagValidation.value = { valid: false, message: '' }
        }
      } catch (error) {
        console.error('Error creating tag:', error)
        alert('Failed to create tag. Please try again.')
      }
    }

    const editTag = (tag) => {
      // TODO: Implement tag editing
      console.log('Edit tag:', tag)
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

    const linkTagsToProjects = async () => {
      if (selectedProjects.value.length === 0 || selectedTags.value.length === 0) return

      try {
        const tagNames = selectedTags.value.map(tagName =>
          tags.value.find(t => t.name === tagName)?.name
        ).filter(Boolean)

        for (const tagName of tagNames) {
          // Get DT API token from our backend
          const tokenResponse = await axios.get('/api/dt-token')
          const dtToken = tokenResponse.data.token

          // Direct call to DT API with proper authentication
          const response = await axios.post(`/api/v1/tag/${tagName}/project`, selectedProjects.value, {
            headers: {
              'Authorization': `Bearer ${dtToken}`
            }
          })

          if (response.status === 204) {
            // Success - update local project tags
            selectedProjects.value.forEach(projectUuid => {
              const project = projects.value.find(p => p.uuid === projectUuid)
              if (project && !project.tags.includes(tagName)) {
                project.tags.push(tagName)
              }
            })
          }
        }

        await loadProjects()
        await loadTags()
        selectedProjects.value = []
        selectedTags.value = []
      } catch (error) {
        console.error('Error linking tags:', error)
        alert('Failed to link tags to projects. Please try again.')
      }
    }

    const unlinkTagsFromProjects = async () => {
      if (selectedProjects.value.length === 0 || selectedTags.value.length === 0) return

      try {
        const tagNames = selectedTags.value.map(tagName =>
          tags.value.find(t => t.name === tagName)?.name
        ).filter(Boolean)

        for (const tagName of tagNames) {
          // Use DT API endpoint to untag projects
          const response = await axios.delete(`/api/v1/tag/${tagName}/project`, {
            data: selectedProjects.value
          })

          if (response.status === 204) {
            // Success - update local project tags
            selectedProjects.value.forEach(projectUuid => {
              const project = projects.value.find(p => p.uuid === projectUuid)
              if (project) {
                project.tags = project.tags.filter(tag => tag !== tagName)
              }
            })
          }
        }

        await loadProjects()
        await loadTags()
        selectedProjects.value = []
        selectedTags.value = []
      } catch (error) {
        console.error('Error unlinking tags:', error)
        alert('Failed to unlink tags from projects. Please try again.')
      }
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
      selectedProjects,
      selectedTags,
      tagValidation,
      suggestedTags,
      showProjectsModal,
      selectedTag,
      tagProjects,
      loading,
      validateTag,
      selectSuggestedTag,
      createTag,
      clearForm,
      editTag,
      deleteTag,
      viewTagProjects,
      closeProjectsModal,
      linkTagsToProjects,
      unlinkTagsFromProjects,
      refreshTags,
      formatDate
    }
  }
}
</script>
