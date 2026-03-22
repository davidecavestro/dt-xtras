<template>
  <div class="taxonomy-tree-view">
    <!-- Taxonomy Selector -->
    <div class="mb-6">
      <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
        Select Root Taxonomy
      </label>
      <select
        v-model="selectedTaxonomy"
        @change="loadTaxonomyTree"
        class="block w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
      >
        <option value="">Choose a taxonomy...</option>
        <option v-for="taxonomy in availableTaxonomies" :key="taxonomy.id" :value="taxonomy.id">
          {{ taxonomy.name }} ({{ taxonomy.regex_pattern }})
        </option>
      </select>
    </div>

    <!-- Tag Creation Interface -->
    <div v-if="selectedTaxonomy" class="mb-6 bg-blue-50 dark:bg-blue-900/20 rounded-lg p-4">
      <h3 class="text-lg font-medium text-gray-900 dark:text-white mb-4">Create Tags</h3>

      <!-- Relations-based Tag Creation -->
      <div v-if="taxonomyRelations.length > 0" class="mb-6">
        <h4 class="text-md font-medium text-gray-800 dark:text-gray-200 mb-3">Relation Tag (Multi-taxonomy)</h4>
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          <div v-for="relation in taxonomyRelations" :key="relation.group" class="space-y-2">
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300">
              {{ relation.group }}
            </label>
            <select
              v-model="selectedValues[relation.group]"
              class="block w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-white text-sm"
            >
              <option value="">Select {{ relation.group }}...</option>
              <option v-for="tag in getRelatedTags(relation.targets)" :key="tag.name" :value="tag.name">
                {{ tag.name }}
              </option>
            </select>
          </div>
        </div>

        <div class="mt-4 flex items-center justify-between">
          <div class="flex-1">
            <div class="text-sm text-gray-600 dark:text-gray-400">
              Preview: <span class="font-mono font-medium text-gray-900 dark:text-white">{{ buildRelationTag() }}</span>
            </div>
          </div>
          <div class="flex space-x-2">
            <button
              @click="clearRelationForm"
              class="px-3 py-2 text-sm font-medium text-gray-700 dark:text-gray-300 bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-md hover:bg-gray-50 dark:hover:bg-gray-600"
            >
              Clear
            </button>
            <button
              @click="createRelationTag"
              :disabled="!canCreateRelationTag()"
              class="px-3 py-2 text-sm font-medium text-white bg-blue-600 border border-transparent rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Create Relation Tag
            </button>
          </div>
        </div>
      </div>

      <!-- Divider -->
      <div v-if="taxonomyRelations.length > 0" class="border-t border-blue-200 dark:border-blue-800 my-6"></div>

      <!-- General Tag Creation -->
      <div>
        <h4 class="text-md font-medium text-gray-800 dark:text-gray-200 mb-3">Direct Tag ({{ selectedTaxonomyName }})</h4>
        <div class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Tag Name
            </label>
            <div class="flex space-x-2">
              <span class="text-sm text-gray-500 dark:text-gray-400 flex items-center py-2">
                {{ selectedTaxonomyName === 'product_version' ? 'Tag:' : selectedTaxonomyName + ':' }}
              </span>
              <input
                v-model="directTagName"
                @input="validateDirectTag"
                placeholder="Enter tag value..."
                class="flex-1 px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-white text-sm"
              />
            </div>
            <div class="mt-1 text-xs text-gray-500 dark:text-gray-400">
              Pattern: {{ selectedTaxonomyPattern }}
            </div>
            <div v-if="directTagValidation.isValid" class="mt-1 text-xs text-green-600 dark:text-green-400">
              ✓ Tag matches pattern
            </div>
            <div v-else-if="directTagName" class="mt-1 text-xs text-red-600 dark:text-red-400">
              ✗ {{ directTagValidation.error }}
            </div>
          </div>

          <div class="flex items-center justify-between">
            <div class="flex-1">
              <div class="text-sm text-gray-600 dark:text-gray-400">
                Full Tag: <span class="font-mono font-medium text-gray-900 dark:text-white">{{ buildDirectTag() }}</span>
              </div>
            </div>
            <div class="flex space-x-2">
              <button
                @click="clearDirectForm"
                class="px-3 py-2 text-sm font-medium text-gray-700 dark:text-gray-300 bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-md hover:bg-gray-50 dark:hover:bg-gray-600"
              >
                Clear
              </button>
              <button
                @click="createDirectTag"
                :disabled="!canCreateDirectTag()"
                class="px-3 py-2 text-sm font-medium text-white bg-green-600 border border-transparent rounded-md hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Create Tag
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Tree View -->
    <div v-if="selectedTaxonomy && taxonomyTree.length > 0" class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <!-- Tree Panel -->
      <div class="bg-white dark:bg-gray-800 rounded-lg shadow">
        <div class="px-4 py-3 border-b border-gray-200 dark:border-gray-700">
          <h3 class="text-lg font-medium text-gray-900 dark:text-white">Taxonomy Tree</h3>
          <p class="text-sm text-gray-500 dark:text-gray-400">Click any node to filter projects</p>
        </div>
        <div class="p-4">
          <div class="space-y-1">
            <TreeNode
              v-for="node in taxonomyTree"
              :key="node.id"
              :node="node"
              :level="0"
              @select="selectNode"
              :selected-node-id="selectedNodeId"
            />
          </div>
        </div>
      </div>

      <!-- Projects Panel -->
      <div class="bg-white dark:bg-gray-800 rounded-lg shadow">
        <div class="px-4 py-3 border-b border-gray-200 dark:border-gray-700">
          <h3 class="text-lg font-medium text-gray-900 dark:text-white">
            Projects
            <span v-if="selectedNodePath" class="text-sm text-gray-500 dark:text-gray-400">
              - {{ selectedNodePath }}
            </span>
          </h3>
          <p class="text-sm text-gray-500 dark:text-gray-400">
            {{ filteredProjects.length }} project{{ filteredProjects.length !== 1 ? 's' : '' }}
          </p>
        </div>
        <div class="p-4">
          <div v-if="loading" class="text-center py-8">
            <div class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
            <p class="mt-2 text-gray-600 dark:text-gray-400">Loading projects...</p>
          </div>
          <div v-else-if="filteredProjects.length === 0" class="text-center py-8 text-gray-500 dark:text-gray-400">
            <Folder class="mx-auto h-12 w-12 text-gray-400" />
            <h3 class="mt-2 text-sm font-medium text-gray-900 dark:text-white">No projects found</h3>
            <p class="mt-1 text-sm text-gray-500 dark:text-gray-400">
              {{ selectedNodeId ? 'No projects match the selected node.' : 'Select a node to view projects.' }}
            </p>
          </div>
          <div v-else class="space-y-2">
            <div
              v-for="project in filteredProjects"
              :key="project.uuid"
              class="p-3 border border-gray-200 dark:border-gray-700 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 cursor-pointer"
              @click="viewProject(project)"
            >
              <div class="flex items-center justify-between">
                <div>
                  <h4 class="text-sm font-medium text-gray-900 dark:text-white">{{ project.name }}</h4>
                  <p class="text-xs text-gray-500 dark:text-gray-400">
                    {{ project.metrics?.vulnerabilities || 0 }} vulnerabilities
                  </p>
                </div>
                <div class="flex items-center space-x-2">
                  <RiskScoreBadge :score="project.metrics?.inheritedRiskScore || 0" />
                  <span class="text-xs text-gray-400">{{ formatDate(project.metrics?.lastBomImport) }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Empty State -->
    <div v-else-if="!selectedTaxonomy" class="text-center py-12 text-gray-500 dark:text-gray-400">
      <svg class="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"></path>
      </svg>
      <h3 class="mt-2 text-sm font-medium text-gray-900 dark:text-white">Select a Taxonomy</h3>
      <p class="mt-1 text-sm text-gray-500 dark:text-gray-400">
        Choose a taxonomy to explore your projects in a structured view.
      </p>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted, watch } from 'vue'
import { Folder } from 'lucide-vue-next'
import XRegExp from 'xregexp'
import TreeNode from './TreeNode.vue'
import RiskScoreBadge from './RiskScoreBadge.vue'
import axios from 'axios'

export default {
  name: 'TaxonomyTreeView',
  components: {
    Folder,
    TreeNode,
    RiskScoreBadge
  },
  setup() {
    const selectedTaxonomy = ref('')
    const availableTaxonomies = ref([])
    const taxonomyTree = ref([])
    const taxonomyRelations = ref([])
    const selectedValues = ref({})
    const directTagName = ref('')
    const directTagValidation = ref({ isValid: false, error: '' })
    const allTags = ref([])
    const selectedNodeId = ref('')
    const selectedNodePath = ref('')
    const allProjects = ref([])
    const filteredProjects = ref([])
    const loading = ref(false)

    // Load available taxonomies
    const loadTaxonomies = async () => {
      try {
        console.log('Loading taxonomies...')
        const response = await axios.get('/api/taxonomies')
        console.log('Taxonomies response:', response)
        availableTaxonomies.value = response.data || []
        console.log('Available taxonomies:', availableTaxonomies.value)
      } catch (error) {
        console.error('Error loading taxonomies:', error)
      }
    }

    // Load taxonomy tree structure
    const loadTaxonomyTree = async () => {
      if (!selectedTaxonomy.value) {
        taxonomyTree.value = []
        taxonomyRelations.value = []
        return
      }

      loading.value = true
      try {
        // Get taxonomy details
        const taxonomy = availableTaxonomies.value.find(t => t.id === selectedTaxonomy.value)
        if (!taxonomy) return

        // Set relations for tag creation
        taxonomyRelations.value = taxonomy.relations || []
        selectedValues.value = {}

        // Get all tags
        const tagsResponse = await axios.get('/api/tags')
        allTags.value = tagsResponse.data || []

        // Filter tags that match the taxonomy pattern
        const rootTags = filterTagsByPattern(allTags.value, taxonomy.regex_pattern)

        // Build tree structure
        taxonomyTree.value = await buildTreeFromTags(rootTags, taxonomy, allTags.value)

        // Load all projects for filtering
        await loadAllProjects()
      } catch (error) {
        console.error('Error loading taxonomy tree:', error)
      } finally {
        loading.value = false
      }
    }

    // Filter tags by regex pattern
    const filterTagsByPattern = (tags, pattern) => {
      try {
        // Use XRegExp for Python/JS regex compatibility
        const regex = XRegExp(pattern)
        return tags.filter(tag => regex.test(tag.name))
      } catch (error) {
        console.error('Invalid regex pattern:', pattern, error)
        return []
      }
    }

    // Build tree structure from tags
    const buildTreeFromTags = async (rootTags, taxonomy, allTags) => {
      return rootTags.map(tag => {
        const node = {
          id: tag.name,
          name: tag.name,
          type: 'tag',
          taxonomy: taxonomy.id,
          pattern: taxonomy.regex_pattern,
          projectsCount: tag.projectsCount || 0,
          children: [],
          projects: []
        }

        // Build hierarchical structure based on tag naming patterns
        // For deployment example: env:production:customer:acme:product_version:myapp:1.0.0
        const tagParts = tag.name.split(':')

        if (tagParts.length > 1) {
          // Find child tags that extend this tag's path
          const childTags = allTags.filter(childTag => {
            const childParts = childTag.name.split(':')
            // Child tag should start with parent tag's path and have more parts
            return childTag.name.startsWith(tag.name + ':') && childParts.length === tagParts.length + 1
          })

          node.children = childTags.map(childTag => ({
            id: childTag.name,
            name: childTag.name,
            type: 'tag',
            taxonomy: 'derived', // Mark as derived from hierarchy
            projectsCount: childTag.projectsCount || 0,
            children: [],
            projects: []
          }))
        }

        return node
      })
    }

    // Load all projects
    const loadAllProjects = async () => {
      try {
        const response = await axios.get('/api/projects')
        allProjects.value = response.data || []
      } catch (error) {
        console.error('Error loading projects:', error)
      }
    }

    // Select a node in the tree
    const selectNode = (node, path) => {
      selectedNodeId.value = node.id
      selectedNodePath.value = path

      // Filter projects based on selected node
      filterProjectsByNode(node)
    }

    // Filter projects based on selected node
    const filterProjectsByNode = (node) => {
      // This is a simplified filtering logic
      // We'll need to implement the actual filtering based on taxonomy patterns
      filteredProjects.value = allProjects.value.filter(project => {
        // Check if project has tags matching the selected node or its descendants
        return project.tags && project.tags.some(tag =>
          tag.includes(node.name) || tag.includes(node.pattern)
        )
      })
    }

    // View project details
    const viewProject = (project) => {
      console.log('View project:', project)
      // TODO: Navigate to project details or show modal
    }

    // Format date
    const formatDate = (dateString) => {
      if (!dateString) return 'Unknown'
      return new Date(dateString).toLocaleDateString()
    }

    // Computed properties for direct tag creation
    const selectedTaxonomyName = computed(() => {
      const taxonomy = availableTaxonomies.value.find(t => t.id === selectedTaxonomy.value)
      return taxonomy ? taxonomy.id : ''
    })

    const selectedTaxonomyPattern = computed(() => {
      const taxonomy = availableTaxonomies.value.find(t => t.id === selectedTaxonomy.value)
      return taxonomy ? taxonomy.regex_pattern : ''
    })

    // Direct tag creation functions
    const validateDirectTag = () => {
      const taxonomy = availableTaxonomies.value.find(t => t.id === selectedTaxonomy.value)
      if (!taxonomy || !directTagName.value) {
        directTagValidation.value = { isValid: false, error: '' }
        return
      }

      try {
        // For most taxonomies, the full tag is taxonomy:value
        // But for product_version, the tag should be just the user input
        const fullTag = taxonomy.id === 'product_version' ? directTagName.value : `${taxonomy.id}:${directTagName.value}`
        const regex = XRegExp(taxonomy.regex_pattern)
        const isValid = regex.test(fullTag)

        directTagValidation.value = {
          isValid,
          error: isValid ? '' : `Tag "${fullTag}" does not match pattern: ${taxonomy.regex_pattern}`
        }
      } catch (error) {
        directTagValidation.value = {
          isValid: false,
          error: 'Invalid regex pattern'
        }
      }
    }

    const buildDirectTag = () => {
      if (!selectedTaxonomyName.value || !directTagName.value) return ''

      // For product_version, the tag is just the user input
      // For other taxonomies, it's taxonomy:value
      return selectedTaxonomyName.value === 'product_version' ? directTagName.value : `${selectedTaxonomyName.value}:${directTagName.value}`
    }

    const canCreateDirectTag = () => {
      return selectedTaxonomy.value && directTagName.value && directTagValidation.value.isValid
    }

    const clearDirectForm = () => {
      directTagName.value = ''
      directTagValidation.value = { isValid: false, error: '' }
    }

    // Tag creation functions
    const getRelatedTags = (targetTaxonomy) => {
      // Find tags that match the target taxonomy pattern
      const targetTax = availableTaxonomies.value.find(t => t.id === targetTaxonomy)
      if (!targetTax) return []

      return filterTagsByPattern(allTags.value, targetTax.regex_pattern)
    }

    const buildRelationTag = () => {
      const taxonomy = availableTaxonomies.value.find(t => t.id === selectedTaxonomy.value)
      if (!taxonomy || !taxonomy.relations) return ''

      // Build tag based on taxonomy pattern and selected values
      // For deployment taxonomy: deploy:env:customer:product_version
      let tagPattern = taxonomy.id

      // Order relations according to the taxonomy pattern
      const orderedRelations = ['env', 'customer', 'product_version']

      for (const relationName of orderedRelations) {
        const relation = taxonomy.relations.find(r => r.group === relationName)
        if (relation) {
          const value = selectedValues.value[relation.group]
          if (value) {
            tagPattern += `:${value}`
          }
        }
      }

      return tagPattern
    }

    const canCreateRelationTag = () => {
      const taxonomy = availableTaxonomies.value.find(t => t.id === selectedTaxonomy.value)
      if (!taxonomy || !taxonomy.relations) return false

      // Check if all required relations have values
      return taxonomy.relations.every(relation => selectedValues.value[relation.group])
    }

    const clearRelationForm = () => {
      selectedValues.value = {}
    }

    const createRelationTag = async () => {
      const tagName = buildRelationTag()
      if (!tagName) {
        console.error('Cannot create tag: no tag name generated')
        return
      }

      try {
        loading.value = true
        const response = await axios.post('/api/tags', { name: tagName })
        console.log('Created relation tag:', response.data)

        // Refresh tags and tree
        await loadTaxonomyTree()

        // Clear form
        clearRelationForm()
      } catch (error) {
        console.error('Error creating relation tag:', error)
        alert(`Error creating tag: ${error.response?.data?.message || error.message}`)
      } finally {
        loading.value = false
      }
    }

    const createDirectTag = async () => {
      const tagName = buildDirectTag()
      if (!tagName) {
        console.error('Cannot create tag: no tag name generated')
        return
      }

      try {
        loading.value = true
        const response = await axios.post('/api/tags', { name: tagName })
        console.log('Created direct tag:', response.data)

        // Refresh tags and tree
        await loadTaxonomyTree()

        // Clear form
        clearDirectForm()
      } catch (error) {
        console.error('Error creating direct tag:', error)
        alert(`Error creating tag: ${error.response?.data?.message || error.message}`)
      } finally {
        loading.value = false
      }
    }

    onMounted(() => {
      loadTaxonomies()
    })

    return {
      selectedTaxonomy,
      availableTaxonomies,
      taxonomyTree,
      taxonomyRelations,
      selectedValues,
      directTagName,
      directTagValidation,
      selectedTaxonomyName,
      selectedTaxonomyPattern,
      selectedNodeId,
      selectedNodePath,
      filteredProjects,
      loading,
      loadTaxonomyTree,
      getRelatedTags,
      buildRelationTag,
      canCreateRelationTag,
      clearRelationForm,
      createRelationTag,
      validateDirectTag,
      buildDirectTag,
      canCreateDirectTag,
      clearDirectForm,
      createDirectTag,
      selectNode,
      viewProject,
      formatDate
    }
  }
}
</script>

<style scoped>
.taxonomy-tree-view {
  @apply p-6;
}
</style>
