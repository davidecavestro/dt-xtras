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
          <TreeView
            :items="taxonomyTree"
            @onSelect="handleNodeSelect"
            class="taxonomy-tree"
          >
            <template #default="{ item, level }">
              <div class="flex items-center py-2 px-3 rounded-md hover:bg-gray-100 dark:hover:bg-gray-700 cursor-pointer"
                   :class="{
                     'bg-blue-50 dark:bg-blue-900/20 border-l-4 border-blue-500': selectedNodeId === item.id,
                     'border-l-4 border-transparent': selectedNodeId !== item.id
                   }"
                   @click="handleNodeClick(item)">
                <!-- Node Icon -->
                <span class="text-lg mr-2">{{ getNodeTypeIcon(item) }}</span>

                <!-- Node Name -->
                <span class="flex-1 text-sm font-medium text-gray-900 dark:text-white">
                  {{ getNodeDisplayName(item) }}
                </span>

                <!-- Node Type Badge -->
                <span
                  v-if="showTypeBadge(item)"
                  class="px-2 py-1 text-xs rounded-full"
                  :class="getTypeBadgeClass(item)"
                >
                  {{ getNodeTypeLabel(item) }}
                </span>

                <!-- Projects Count -->
                <span
                  v-if="showProjectsCount(item)"
                  class="ml-2 px-2 py-1 text-xs bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-300 rounded-full"
                >
                  {{ item.projectsCount || 0 }}
                </span>
              </div>
            </template>
          </TreeView>
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
import { ref, computed, onMounted } from 'vue'
import axios from 'axios'
import XRegExp from 'xregexp'
import TreeView from 'vue3-tree-vue'
import 'vue3-tree-vue/dist/style.css'

export default {
  name: 'TaxonomyTreeView',
  components: {
    TreeView
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

    // Load taxonomies
    const loadTaxonomies = async () => {
      try {
        loading.value = true
        const response = await axios.get('/api/taxonomies')
        availableTaxonomies.value = response.data || []

        // Load projects after taxonomies are loaded
        await loadAllProjects()
      } catch (error) {
        console.error('Error loading taxonomies:', error)
      } finally {
        loading.value = false
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

    // Build tree structure from tags with proper hierarchy
    const buildTreeFromTags = async (rootTags, taxonomy, allTags) => {
      const nodeMap = new Map()
      const rootNodes = []

      // First, create nodes for all tags that match this taxonomy
      rootTags.forEach(tag => {
        const node = {
          id: tag.name,
          name: tag.name,
          type: 'tag',
          taxonomy: taxonomy.id,
          pattern: taxonomy.regex_pattern,
          projectsCount: tag.projectsCount || 0,
          children: [],
          projects: [],
          expanded: false
        }
        nodeMap.set(tag.name, node)
        rootNodes.push(node)
      })

      // If taxonomy has relations, build hierarchical structure
      if (taxonomy.relations && taxonomy.relations.length > 0) {
        await buildRelationHierarchy(rootNodes, taxonomy, allTags, nodeMap)
      }

      // Sort nodes alphabetically for better organization
      return sortTreeNodes(rootNodes)
    }

    // Build hierarchical structure based on taxonomy relations
    const buildRelationHierarchy = async (nodes, taxonomy, allTags, nodeMap) => {
      for (const node of nodes) {
        // Parse the tag to extract components
        const components = parseTagComponents(node.name, taxonomy)

        if (components && taxonomy.relations) {
          // Build children based on relations
          for (const relation of taxonomy.relations) {
            const childTags = findRelatedTags(components, relation, allTags)

            for (const childTag of childTags) {
              if (!nodeMap.has(childTag.name)) {
                const childNode = {
                  id: childTag.name,
                  name: childTag.name,
                  type: 'tag',
                  taxonomy: relation.targets,
                  projectsCount: childTag.projectsCount || 0,
                  children: [],
                  projects: [],
                  expanded: false
                }
                nodeMap.set(childTag.name, childNode)
                node.children.push(childNode)
              }
            }
          }
        }
      }
    }

    // Parse tag components based on taxonomy pattern
    const parseTagComponents = (tagName, taxonomy) => {
      if (!tagName || !taxonomy || !taxonomy.regex_pattern) return null

      try {
        const regex = XRegExp(taxonomy.regex_pattern)
        const match = XRegExp.exec(tagName, regex)
        return match ? match : null
      } catch (error) {
        console.error('Error parsing tag components:', error, 'tagName:', tagName, 'pattern:', taxonomy.regex_pattern)
        return null
      }
    }

    // Find tags related to a specific component
    const findRelatedTags = (components, relation, allTags) => {
      const relatedTaxonomy = availableTaxonomies.value.find(t => t.id === relation.targets)
      if (!relatedTaxonomy) return []

      // Extract the component value (e.g., 'acme' from 'cust:acme')
      const componentValue = components[relation.group]
      if (!componentValue) return []

      // Find tags in the related taxonomy that match this component
      return allTags.filter(tag => {
        try {
          const regex = XRegExp(relatedTaxonomy.regex_pattern)
          return regex.test(tag.name) && tag.name.includes(componentValue)
        } catch (error) {
          return false
        }
      })
    }

    // Sort tree nodes alphabetically
    const sortTreeNodes = (nodes) => {
      return nodes.sort((a, b) => {
        // Sort by type first (tags before projects), then by name
        if (a.type !== b.type) {
          return a.type === 'tag' ? -1 : 1
        }
        return a.name.localeCompare(b.name)
      }).map(node => ({
        ...node,
        children: node.children.length > 0 ? sortTreeNodes(node.children) : node.children
      }))
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

    // Handle node click for vue3-tree-vue
    const handleNodeClick = (node) => {
      selectNode(node, node.name)
    }

    // Handle node selection for TreeView
    const handleNodeSelect = (item) => {
      selectNode(item, item.name)
    }

    // Helper functions for tree display
    const showTypeBadge = (node) => {
      return node.taxonomy && node.type === 'tag'
    }

    const getNodeTypeLabel = (node) => {
      if (node.type === 'project') return 'Project'

      const taxonomyLabels = {
        'customer': 'Customer',
        'env': 'Environment',
        'deploy': 'Deployment',
        'product_version': 'Version'
      }

      return taxonomyLabels[node.taxonomy] || node.taxonomy
    }

    const getTypeBadgeClass = (node) => {
      const classes = {
        'customer': 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200',
        'env': 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200',
        'deploy': 'bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-200',
        'product_version': 'bg-orange-100 text-orange-800 dark:bg-orange-900 dark:text-orange-200'
      }

      return classes[node.taxonomy] || 'bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-200'
    }

    const showProjectsCount = (node) => {
      return node.type === 'tag' && node.projectsCount !== undefined
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

    // Get node display name with taxonomy context
    const getNodeDisplayName = (node) => {
      if (!node || !availableTaxonomies.value) return node?.name || 'Unknown'
      const taxonomy = availableTaxonomies.value.find(t => t.id === node.taxonomy)
      const taxonomyName = taxonomy ? taxonomy.name : node.taxonomy

      // For better UX, show just the value part for related taxonomies
      if (node.taxonomy !== selectedTaxonomy.value) {
        const parts = node.name.split(':')
        return parts.length > 1 ? parts[parts.length - 1] : node.name
      }

      return node.name
    }

    // Get node type icon
    const getNodeTypeIcon = (node) => {
      if (!node) return '🏷️'
      if (node.type === 'project') return '📁'

      // Different icons for different taxonomies
      switch (node.taxonomy) {
        case 'customer': return '🏢'
        case 'env': return '🌍'
        case 'deploy': return '🚀'
        case 'product_version': return '📦'
        default: return '🏷️'
      }
    }

    // Enhanced project filtering based on selected node
    const filterProjectsByNode = (node) => {
      if (!node) {
        filteredProjects.value = allProjects.value
        return
      }

      // Get all tags under this node (including descendants)
      const allNodeTags = getAllNodeTags(node)

      // Filter projects that have any of the tags
      filteredProjects.value = allProjects.value.filter(project => {
        if (!project.tags || project.tags.length === 0) return false

        return project.tags.some(projectTag => {
          // Handle both string tags and object tags
          const tagName = typeof projectTag === 'string' ? projectTag : projectTag.name

          if (!tagName) return false

          return allNodeTags.some(nodeTag => {
            // Exact match
            if (tagName === nodeTag) return true

            // Hierarchical match - if project tag starts with node tag
            if (tagName.startsWith(nodeTag + ':')) return true

            // Component match - if project tag contains components of node tag
            return hasComponentMatch(tagName, nodeTag)
          })
        })
      })
    }

    // Get all tags under a node (including all descendants)
    const getAllNodeTags = (node) => {
      const tags = [node.name]

      if (node.children && node.children.length > 0) {
        node.children.forEach(child => {
          tags.push(...getAllNodeTags(child))
        })
      }

      return tags
    }

    // Check if tags have matching components
    const hasComponentMatch = (projectTag, nodeTag) => {
      const projectParts = projectTag.split(':')
      const nodeParts = nodeTag.split(':')

      // Check if all parts of node tag exist in project tag
      return nodeParts.every(part => projectParts.includes(part))
    }

    const selectedTaxonomyName = computed(() => {
      if (!selectedTaxonomy.value || !availableTaxonomies.value) return ''
      const taxonomy = availableTaxonomies.value.find(t => t.id === selectedTaxonomy.value)
      return taxonomy ? taxonomy.id : ''
    })

    const selectedTaxonomyPattern = computed(() => {
      if (!selectedTaxonomy.value || !availableTaxonomies.value) return ''
      const taxonomy = availableTaxonomies.value.find(t => t.id === selectedTaxonomy.value)
      return taxonomy ? taxonomy.regex_pattern : ''
    })

    // Direct tag creation functions
    const validateDirectTag = () => {
      console.log('Validating direct tag...')
      console.log('Selected taxonomy:', selectedTaxonomy.value)
      console.log('Available taxonomies:', availableTaxonomies.value.map(t => ({ id: t.id, pattern: t.regex_pattern })))

      if (!selectedTaxonomy.value || !availableTaxonomies.value || !directTagName.value) {
        directTagValidation.value = { isValid: false, error: '' }
        return
      }

      const taxonomy = availableTaxonomies.value.find(t => t.id === selectedTaxonomy.value)
      if (!taxonomy) {
        directTagValidation.value = { isValid: false, error: 'Taxonomy not found' }
        return
      }

      console.log('Found taxonomy:', taxonomy)
      console.log('Using pattern:', taxonomy.regex_pattern)

      try {
        // For most taxonomies, the full tag is taxonomy:value
        // But for product_version, the tag should be just the user input
        const fullTag = taxonomy.id === 'product_version' ? directTagName.value : `${taxonomy.id}:${directTagName.value}`
        console.log('Full tag to validate:', fullTag)

        const regex = XRegExp(taxonomy.regex_pattern)
        const isValid = regex.test(fullTag)
        console.log('Validation result:', isValid)

        directTagValidation.value = {
          isValid,
          error: isValid ? '' : `Tag "${fullTag}" does not match pattern: ${taxonomy.regex_pattern}`
        }
      } catch (error) {
        console.error('Error validating direct tag:', error)
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
      try {
        loadTaxonomies()
      } catch (error) {
        console.error('Error initializing TaxonomyTreeView:', error)
      }
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
      handleNodeClick,
      handleNodeSelect,
      getNodeDisplayName,
      getNodeTypeIcon,
      showTypeBadge,
      getNodeTypeLabel,
      getTypeBadgeClass,
      showProjectsCount,
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

/* Custom styling for vue3-tree-vue */
.taxonomy-tree {
  --tree-node-padding: 8px;
  --tree-node-hover-bg: rgba(0, 0, 0, 0.05);
  --tree-node-selected-bg: rgba(59, 130, 246, 0.1);
}

.taxonomy-tree :deep(.treeview-item) {
  margin: 2px 0;
  border-radius: 6px;
  transition: all 0.2s ease;
}

.taxonomy-tree :deep(.treeview-item:hover) {
  background-color: var(--tree-node-hover-bg);
}

.taxonomy-tree :deep(.treeview-item.selected) {
  background-color: var(--tree-node-selected-bg);
  border-left: 4px solid #3b82f6;
}

.taxonomy-tree :deep(.treeview-item-content) {
  padding: var(--tree-node-padding);
  display: flex;
  align-items: center;
}

.taxonomy-tree :deep(.treeview-item-arrow) {
  margin-right: 8px;
  color: #6b7280;
  transition: transform 0.2s ease;
}

.taxonomy-tree :deep(.treeview-item-arrow.expanded) {
  transform: rotate(90deg);
}

.taxonomy-tree :deep(.treeview-item-text) {
  flex: 1;
  font-size: 14px;
  font-weight: 500;
  color: #1f2937;
}

.dark .taxonomy-tree :deep(.treeview-item-text) {
  color: #f9fafb;
}

.taxonomy-tree :deep(.treeview-item-icon) {
  margin-right: 8px;
  font-size: 16px;
}

/* Responsive adjustments */
@media (max-width: 768px) {
  .taxonomy-tree :deep(.treeview-item-content) {
    padding: 6px;
  }

  .taxonomy-tree :deep(.treeview-item-text) {
    font-size: 13px;
  }
}
</style>
