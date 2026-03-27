<template>
  <div class="taxonomy-tree-view">
    <!-- Taxonomy Selector -->
    <div class="mb-6">
      <div class="flex items-center justify-between mb-2">
        <label class="block text-sm font-medium text-gray-700 dark:text-gray-300">
          Select Root Taxonomy
        </label>
        <button
          @click="openTaxonomyManagementDialog"
          class="px-3 py-1 text-sm bg-purple-500 text-white rounded hover:bg-purple-600 transition-colors"
          title="Manage hard-linked taxonomies"
        >
          ⚙️ Manage Taxonomies
        </button>
      </div>
      <select
        v-model="selectedTaxonomy"
        @change="(event) => loadTaxonomyTree(selectedTaxonomy)"
        class="block w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
      >
        <option value="">Choose a taxonomy...</option>
        <option v-for="taxonomy in availableTaxonomies" :key="taxonomy.id" :value="taxonomy.id">
          {{ taxonomy.icon || '🏷️' }} {{ taxonomy.name }} ({{ taxonomy.regex_pattern }})
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
              ✓ Tag matches regex_pattern
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
          <!-- Render hierarchical tree -->
          <div class="taxonomy-tree">
            <TreeNode
              v-for="node in taxonomyTree"
              :key="node.id"
              :node="node"
              :get-node-display-name="getNodeDisplayName"
              :get-node-type-icon="getNodeTypeIcon"
              :get-node-type-label="getNodeTypeLabel"
              @node-click="selectNode"
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
            <FolderIcon class="mx-auto h-12 w-12 text-gray-400" />
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

    <!-- Project Tagging Dialog -->
    <div v-if="showTaggingDialog" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-white dark:bg-gray-800 rounded-lg shadow-xl max-w-4xl w-full mx-4 max-h-[80vh] overflow-hidden">
        <!-- Header -->
        <div class="px-6 py-4 border-b border-gray-200 dark:border-gray-700">
          <div class="flex items-center justify-between">
            <h3 class="text-lg font-semibold text-gray-900 dark:text-white">
              {{ taggingMode === 'direct' ? '🏷️ Direct Tagging' : '🔗 Indirect Tagging' }}
            </h3>
            <button
              @click="closeTaggingDialog"
              class="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
            >
              ✕
            </button>
          </div>
          <p class="mt-2 text-sm text-gray-600 dark:text-gray-400">
            {{ taggingMode === 'direct'
              ? 'Select projects to tag directly with:'
              : 'Select projects that have this tag to tag them with:'
            }}
            <span class="font-mono bg-gray-100 dark:bg-gray-700 px-2 py-1 rounded">
              {{ selectedTagForTagging?.name }}
            </span>
          </p>
        </div>

        <!-- Content -->
        <div class="p-6">
          <!-- Direct Tagging Mode -->
          <div v-if="taggingMode === 'direct'">
            <!-- Search -->
            <div class="mb-4">
              <input
                v-model="taggingSearch"
                placeholder="Search projects..."
                class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
              />
            </div>

            <!-- Projects List -->
            <div class="max-h-60 overflow-y-auto border border-gray-200 dark:border-gray-600 rounded-md">
              <div class="divide-y divide-gray-200 dark:divide-gray-600">
                <div
                  v-for="project in filteredProjectsForTagging"
                  :key="project.uuid"
                  @click="toggleProjectSelection(project)"
                  class="p-3 cursor-pointer hover:bg-gray-50 dark:hover:bg-gray-700 flex items-center justify-between"
                  :class="{
                    'bg-blue-50 dark:bg-blue-900/20': isProjectSelected(project)
                  }"
                >
                  <div class="flex items-center space-x-3">
                    <input
                      type="checkbox"
                      :checked="isProjectSelected(project)"
                      class="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                    />
                    <div>
                      <div class="font-medium text-gray-900 dark:text-white">{{ project.name }}</div>
                      <div class="text-sm text-gray-500 dark:text-gray-400">
                        {{ project.tags?.length || 0 }} tags
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Indirect Tagging Mode -->
          <div v-if="taggingMode === 'indirect'">
            <!-- Source Tag Selection -->
            <div class="mb-4">
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Select source tag:
              </label>
              <select
                @change="selectSourceTagForIndirect($event.target.value)"
                class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
              >
                <option value="">Choose a tag...</option>
                <option
                  v-for="tag in allTags"
                  :key="tag.name"
                  :value="tag.name"
                >
                  {{ tag.name }} ({{ getProjectsWithTag(tag.name).length }} projects)
                </option>
              </select>
            </div>

            <!-- Selected Projects -->
            <div v-if="sourceTagForIndirect">
              <div class="mb-2 text-sm text-gray-600 dark:text-gray-400">
                Projects with tag "{{ sourceTagForIndirect }}":
              </div>
              <div class="max-h-40 overflow-y-auto border border-gray-200 dark:border-gray-600 rounded-md">
                <div class="divide-y divide-gray-200 dark:divide-gray-600">
                  <div
                    v-for="project in selectedProjectsForTagging"
                    :key="project.uuid"
                    class="p-3 bg-gray-50 dark:bg-gray-700"
                  >
                    <div class="font-medium text-gray-900 dark:text-white">{{ project.name }}</div>
                    <div class="text-sm text-gray-500 dark:text-gray-400">
                      {{ project.tags?.join(', ') || 'No tags' }}
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Footer -->
        <div class="px-6 py-4 border-t border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-900">
          <div class="flex items-center justify-between">
            <div class="text-sm text-gray-600 dark:text-gray-400">
              {{ selectedProjectsForTagging.length }} projects selected
            </div>
            <div class="flex space-x-3">
              <button
                @click="closeTaggingDialog"
                class="px-4 py-2 text-gray-700 dark:text-gray-300 bg-gray-200 dark:bg-gray-600 rounded-md hover:bg-gray-300 dark:hover:bg-gray-500 transition-colors"
              >
                Cancel
              </button>
              <button
                @click="applyTagging"
                :disabled="selectedProjectsForTagging.length === 0 || loading"
                class="px-4 py-2 bg-blue-500 text-white rounded-md hover:bg-blue-600 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
              >
                {{ loading ? 'Applying...' : `Tag ${selectedProjectsForTagging.length} Projects` }}
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Taxonomy Management Dialog -->
    <div v-if="showTaxonomyManagementDialog" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-white dark:bg-gray-800 rounded-lg shadow-xl max-w-2xl w-full mx-4 max-h-[80vh] overflow-hidden">
        <!-- Header -->
        <div class="px-6 py-4 border-b border-gray-200 dark:border-gray-700">
          <div class="flex items-center justify-between">
            <h3 class="text-lg font-semibold text-gray-900 dark:text-white">
              ⚙️ Manage Hard-Linked Taxonomies
            </h3>
            <button
              @click="closeTaxonomyManagementDialog"
              class="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
            >
              ✕
            </button>
          </div>
          <p class="mt-2 text-sm text-gray-600 dark:text-gray-400">
            Mark taxonomies as "Hard-Linked" to use their tags as sources for semantic bulk tagging.
            Hard-linked tags (e.g., product versions) will be used to automatically apply taxonomy tags.
          </p>
        </div>

        <!-- Content -->
        <div class="p-6">
          <div class="space-y-3">
            <div
              v-for="taxonomy in availableTaxonomies"
              :key="taxonomy.id"
              class="flex items-center justify-between p-4 border border-gray-200 dark:border-gray-600 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700"
            >
              <div class="flex items-center space-x-3">
                <input
                  type="checkbox"
                  :id="`taxonomy-${taxonomy.id}`"
                  :checked="isTaxonomyHardLinked(taxonomy.id)"
                  @change="toggleHardLinkedTaxonomy(taxonomy.id)"
                  class="rounded border-gray-300 text-purple-600 focus:ring-purple-500"
                />
                <div class="flex items-center space-x-2">
                  <span class="text-lg">{{ taxonomy.icon || '🏷️' }}</span>
                  <div>
                    <div class="font-medium text-gray-900 dark:text-white">
                      {{ taxonomy.name }}
                    </div>
                    <div class="text-sm text-gray-500 dark:text-gray-400">
                      {{ taxonomy.id }} - {{ taxonomy.regex_pattern }}
                    </div>
                  </div>
                </div>
              </div>
              <div class="flex items-center space-x-2">
                <span
                  v-if="isTaxonomyHardLinked(taxonomy.id)"
                  class="px-2 py-1 text-xs bg-purple-100 dark:bg-purple-900/20 text-purple-700 dark:text-purple-300 rounded-full"
                >
                  📎 Hard-Linked
                </span>
                <span
                  v-else
                  class="px-2 py-1 text-xs bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-400 rounded-full"
                >
                  🏷️ Categorization
                </span>
              </div>
            </div>
          </div>

          <!-- Summary -->
          <div class="mt-6 p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
            <h4 class="text-sm font-medium text-gray-900 dark:text-white mb-2">Summary</h4>
            <div class="space-y-1 text-sm text-gray-600 dark:text-gray-400">
              <div>
                📎 Hard-Linked Taxonomies: {{ hardLinkedTaxonomies.size }}
                <span class="ml-2 text-xs">
                  ({{ hardLinkedTags.length }} tags)
                </span>
              </div>
              <div>
                🏷️ Categorization Taxonomies: {{ availableTaxonomies.length - hardLinkedTaxonomies.size }}
                <span class="ml-2 text-xs">
                  ({{ taxonomyTags.length }} tags)
                </span>
              </div>
            </div>
          </div>
        </div>

        <!-- Footer -->
        <div class="px-6 py-4 border-t border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-900">
          <div class="flex justify-end">
            <button
              @click="closeTaxonomyManagementDialog"
              class="px-4 py-2 bg-purple-500 text-white rounded-md hover:bg-purple-600 transition-colors"
            >
              Done
            </button>
          </div>
        </div>
      </div>
    </div>
</template>

<script>
import { ref, computed, onMounted, defineComponent } from 'vue'
import axios from 'axios'
import TaxonomyGraphBuilder from '../utils/taxonomyGraphBuilder.js'
import TreeView from 'vue3-tree-vue'
import 'vue3-tree-vue/dist/style.css'
import { FolderIcon } from '@heroicons/vue/24/outline'
import RiskScoreBadge from './RiskScoreBadge.vue'
import TreeNode from './TreeNode.vue'

export default {
  name: 'TaxonomyTreeView',
  components: {
    TreeView,
    TreeNode,
    FolderIcon,
    RiskScoreBadge
  },
  setup() {
    // Graph-based tree builder
    const graphBuilder = new TaxonomyGraphBuilder()
    let builtGraph = null

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

    // Project tagging state
    const showTaggingDialog = ref(false)
    const taggingMode = ref('direct') // 'direct' or 'indirect'
    const selectedProjectsForTagging = ref([])
    const selectedTagForTagging = ref(null)
    const sourceTagForIndirect = ref(null)
    const availableProjectsForTagging = ref([])
    const taggingSearch = ref('')

    // Taxonomy management state
    const showTaxonomyManagementDialog = ref(false)
    const hardLinkedTaxonomies = ref(new Set()) // Taxonomies marked as hard-linked
    const hardLinkedTags = ref([]) // Tags from hard-linked taxonomies (product versions)
    const taxonomyTags = ref([]) // Tags from non-hard-linked taxonomies (categorization)

    // Load taxonomies
    const loadTaxonomies = async () => {
      try {
        loading.value = true
        const response = await axios.get('/api/taxonomies')
        availableTaxonomies.value = response.data || []

        // Initialize hard-linked taxonomies (in real app, this would come from backend)
        initializeHardLinkedTaxonomies()

        // Load projects after taxonomies are loaded
        await loadAllProjects()
      } catch (error) {
        console.error('Error loading taxonomies:', error)
      } finally {
        loading.value = false
      }
    }

    // Initialize hard-linked taxonomies with default icons
    const initializeHardLinkedTaxonomies = () => {
      // Default some common taxonomies as hard-linked with icons
      const defaultHardLinked = ['product_version', 'version', 'app']
      const taxonomyIcons = {
        'product_version': '📦',
        'version': '📦',
        'app': '📱',
        'environment': '🌍',
        'env': '🌍',
        'customer': '🏢',
        'cust': '🏢',
        'deploy': '🚀',
        'deployment': '🚀',
        'team': '👥',
        'project': '📋',
        'service': '⚙️',
        'component': '🧩'
      }

      // Set default icons for taxonomies
      availableTaxonomies.value.forEach(taxonomy => {
        if (!taxonomy.icon) {
          taxonomy.icon = taxonomyIcons[taxonomy.id] || '🏷️'
        }
      })

      // Initialize hard-linked set (in real app, this would be stored in backend)
      defaultHardLinked.forEach(taxonomyId => {
        if (availableTaxonomies.value.find(t => t.id === taxonomyId)) {
          hardLinkedTaxonomies.value.add(taxonomyId)
        }
      })
    }

    // Load taxonomy tree structure
    const loadTaxonomyTree = async (taxonomyId) => {
      try {
        loading.value = true
        console.log('Loading taxonomy tree for:', taxonomyId)

        const taxonomy = availableTaxonomies.value.find(t => t.id === taxonomyId)
        if (!taxonomy) {
          console.error('Taxonomy not found:', taxonomyId)
          return
        }

        console.log('Found taxonomy:', taxonomy.id, 'with regex_pattern:', taxonomy.regex_pattern)
        console.log('Taxonomy relations:', taxonomy.relations)

        // Set relations for tag creation
        taxonomyRelations.value = taxonomy.relations || []
        selectedValues.value = {}

        // Get all tags (if not already fetched)
        if (!allTags.value || allTags.value.length === 0) {
          const tagsResponse = await axios.get('/api/tags')
          allTags.value = tagsResponse.data || []
        }
        console.log('All tags loaded:', allTags.value.length, 'tags')
        console.log('Sample tags:', allTags.value.slice(0, 5))

        // Build graph once if not already built
        if (!builtGraph) {
          console.log('Building graph for the first time...')
          builtGraph = graphBuilder.buildGraph(allTags.value, availableTaxonomies.value)

          // Log graph statistics
          const stats = graphBuilder.getGraphStats()
          console.log('Graph statistics:', stats)
        } else {
          console.log('Using existing graph...')
        }

        // Extract tree for specific taxonomy
        console.log('Extracting tree for taxonomy:', taxonomyId)
        taxonomyTree.value = graphBuilder.graphToTree(taxonomyId)
        console.log('Final tree structure:', taxonomyTree.value)
        console.log('Tree length:', taxonomyTree.value.length)

        await loadAllProjects()
      } catch (error) {
        console.error('Error loading taxonomy tree:', error)
      } finally {
        loading.value = false
      }
    }

    // Filter tags by regex regex_pattern (kept for tag creation)
    const filterTagsByPattern = (tags, regex_pattern) => {
      console.log('Filtering tags with regex_pattern:', regex_pattern)
      console.log('Total tags to filter:', tags.length)

      try {
        // Use native RegExp for JS regex compatibility
        const regex = new RegExp(regex_pattern)
        console.log('Regex created successfully')

        const matchingTags = tags.filter(tag => {
          const matches = regex.test(tag.name)
          if (matches && tags.length < 20) {
            console.log('Tag matches regex_pattern:', tag.name)
          }
          return matches
        })

        console.log('Found', matchingTags.length, 'matching tags')
        return matchingTags
      } catch (error) {
        console.error('Invalid regex regex_pattern:', regex_pattern, error)
        return []
      }
    }

    // Parse tag components (kept for tag creation)
    const parseTagComponents = (tagName) => {
      // Handle complex tags: env:prod:myapp:1.0.0
      const parts = tagName.split(':')
      if (parts.length === 5) {
        return {
          environment: parts[1],
          customer: parts[2],
          product_version: `${parts[3]}:${parts[4]}`
        }
      }

      // Handle simple tags: env:prod, cust:acme, myapp:1.0.0
      const simpleParts = tagName.split(':')
      if (simpleParts.length === 2) {
        return {
          type: simpleParts[0],
          value: simpleParts[1],
          full_tag: tagName
        }
      }

      console.log('Could not parse components for:', tagName)
      return null
    }

    // Load all projects
    const loadAllProjects = async () => {
      try {
        const response = await axios.get('/api/projects')
        allProjects.value = response.data || []

        // Categorize tags after loading projects
        categorizeTags()
      } catch (error) {
        console.error('Error loading projects:', error)
      }
    }
    const categorizeTags = () => {
      const allTagNames = new Set()

      // Collect all tag names from projects
      allProjects.value.forEach(project => {
        if (project.tags) {
          project.tags.forEach(tag => {
            const tagName = typeof tag === 'string' ? tag : tag.name
            allTagNames.add(tagName)
          })
        }
      })

      // Convert to array and categorize based on hard-linked taxonomies
      const tagsArray = Array.from(allTagNames).map(name => ({ name }))

      hardLinkedTags.value = tagsArray.filter(tag => isHardLinkedTag(tag.name))
      taxonomyTags.value = tagsArray.filter(tag => isTaxonomyTag(tag.name))

      console.log('Hard-linked taxonomies:', Array.from(hardLinkedTaxonomies.value))
      console.log('Hard-linked tags (product versions):', hardLinkedTags.value)
      console.log('Taxonomy tags (categorization):', taxonomyTags.value)
    }

    // Check if a tag is hard-linked (from hard-linked taxonomies)
    const isHardLinkedTag = (tagName) => {
      // Check if tag belongs to any hard-linked taxonomy
      return Array.from(hardLinkedTaxonomies.value).some(taxonomyId =>
        tagName.startsWith(`${taxonomyId}:`)
      )
    }

    // Check if a tag is a taxonomy tag (from non-hard-linked taxonomies)
    const isTaxonomyTag = (tagName) => {
      // Taxonomy tags have prefixes that match available taxonomies but are NOT hard-linked
      const taxonomyPrefixes = availableTaxonomies.value
        .filter(t => !hardLinkedTaxonomies.value.has(t.id))
        .map(t => `${t.id}:`)
      return taxonomyPrefixes.some(prefix => tagName.startsWith(prefix))
    }

    // Toggle hard-linked status for a taxonomy
    const toggleHardLinkedTaxonomy = (taxonomyId) => {
      if (hardLinkedTaxonomies.value.has(taxonomyId)) {
        hardLinkedTaxonomies.value.delete(taxonomyId)
        console.log('Removed hard-linked taxonomy:', taxonomyId)
      } else {
        hardLinkedTaxonomies.value.add(taxonomyId)
        console.log('Added hard-linked taxonomy:', taxonomyId)
      }

      // Re-categorize tags after changing hard-linked taxonomies
      categorizeTags()
    }

    // Check if a taxonomy is hard-linked
    const isTaxonomyHardLinked = (taxonomyId) => {
      return hardLinkedTaxonomies.value.has(taxonomyId)
    }

    // Open taxonomy management dialog
    const openTaxonomyManagementDialog = () => {
      showTaxonomyManagementDialog.value = true
    }

    // Close taxonomy management dialog
    const closeTaxonomyManagementDialog = () => {
      showTaxonomyManagementDialog.value = false
    }

    // Get projects with hard-linked tag (source for semantic tagging)
    const getProjectsWithHardLinkedTag = (tagName) => {
      return allProjects.value.filter(project => {
        if (!project.tags) return false
        return project.tags.some(tag => {
          const tagStr = typeof tag === 'string' ? tag : tag.name
          return tagStr === tagName
        })
      })
    }

    // Apply semantic bulk tagging
    const applySemanticBulkTagging = async (taxonomyTag, hardLinkedTag) => {
      console.log('Applying semantic bulk tagging:')
      console.log('  Taxonomy tag:', taxonomyTag.name)
      console.log('  Hard-linked tag:', hardLinkedTag.name)

      // Get projects that have the hard-linked tag
      const sourceProjects = getProjectsWithHardLinkedTag(hardLinkedTag.name)
      console.log('  Source projects:', sourceProjects.length)

      if (sourceProjects.length === 0) {
        console.log('No projects found with hard-linked tag:', hardLinkedTag.name)
        return { success: true, tagged: 0, message: 'No projects found with source tag' }
      }

      try {
        // Apply taxonomy tag to all source projects
        const taggingPromises = sourceProjects.map(project =>
          axios.post(`/api/projects/${project.uuid}/tags`, {
            tag_name: taxonomyTag.name
          })
        )

        await Promise.all(taggingPromises)

        console.log('Successfully tagged projects with ' + taxonomyTag.name)

        return {
          success: true,
          tagged: sourceProjects.length,
          projects: sourceProjects.map(p => p.name)
        }

      } catch (error) {
        console.error('Error applying semantic bulk tagging:', error)
        return {
          success: false,
          error: error.response?.data?.message || error.message
        }
      }
    }

    // Select a node in the tree
    const selectNode = (node, path) => {
      selectedNodeId.value = node.id
      selectedNodePath.value = path

      // Filter projects based on selected node
      filterProjectsByNode(node)
    }

    // Toggle node expansion for tree rendering
    const toggleNodeExpansion = (node) => {
      console.log('Toggling expansion for:', node.name)
      node.expanded = !node.expanded
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

      // Find the taxonomy to get its display name
      const taxonomy = availableTaxonomies.value.find(t => t.id === node.taxonomy)
      return taxonomy ? taxonomy.name : node.taxonomy
    }

    const getTypeBadgeClass = (node) => {
      // Dynamic color classes for taxonomies
      const taxonomyColors = {
        'customer': 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200',
        'env': 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200',
        'deploy': 'bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-200',
        'product_version': 'bg-orange-100 text-orange-800 dark:bg-orange-900 dark:text-orange-200'
      }

      // Use predefined color if available, otherwise use a default
      return taxonomyColors[node.taxonomy] || 'bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-200'
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
      if (node.type === 'project') return '📁'

      // Use taxonomy icon if available
      if (node.taxonomy) {
        const taxonomy = availableTaxonomies.value.find(t => t.id === node.taxonomy)
        if (taxonomy && taxonomy.icon) {
          return taxonomy.icon
        }
      }

      // Fallback to type-based icons
      switch (node.type) {
        case 'relation': return '🔗'
        case 'tag':
          // Suggest icons based on common patterns (optional, can be overridden)
          const suggestions = {
            'prod': '🚀',
            'production': '🚀',
            'staging': '🧪',
            'stage': '🧪',
            'dev': '🔧',
            'development': '🔧',
            'test': '🧪',
            'env': '🌍',
            'customer': '🏢',
            'cust': '🏢',
            'deploy': '🚀',
            'product': '📦',
            'version': '🔖',
            'app': '📱',
            'service': '⚙️',
            'xtras': '⚡'
          }

          // Check if tag name contains any known patterns
          for (const [regex_pattern, icon] of Object.entries(suggestions)) {
            if (node.name.toLowerCase().includes(regex_pattern)) {
              return icon
            }
          }

          return '🏷️' // Default tag icon
        default: return '🏷️'
      }
    }

    // Enhanced project filtering based on selected node
    const filterProjectsByNode = (node) => {
      if (!node) {
        filteredProjects.value = allProjects.value
        selectedNodePath.value = ''
        return
      }

      const nodeTags = Array.isArray(node.tags) ? node.tags : []
      const matchingProjects = allProjects.value.filter(project => {
        const projectTags = Array.isArray(project.tags) ? project.tags : []
        return nodeTags.some(nodeTag => {
          const tagStr = typeof nodeTag === 'string' ? nodeTag : nodeTag.name
          return projectTags.some(projectTag => {
            const projectTagStr = typeof projectTag === 'string' ? projectTag : projectTag.name
            return tagStr === projectTagStr
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
      console.log('Available taxonomies:', availableTaxonomies.value.map(t => ({ id: t.id, regex_pattern: t.regex_pattern })))

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
      console.log('Using regex_pattern:', taxonomy.regex_pattern)

      // For most taxonomies, the full tag is taxonomy:value
      // But for product_version, the tag should be just the user input
      const fullTag = taxonomy.id === 'product_version' ? directTagName.value : `${taxonomy.id}:${directTagName.value}`
      console.log('Full tag to validate:', fullTag)

      try {
        const regex = new RegExp(taxonomy.regex_pattern)
        const isValid = regex.test(fullTag)
        console.log('Validation result:', isValid)

        directTagValidation.value = {
          isValid,
          error: isValid ? '' : `Tag does not match regex_pattern: ${taxonomy.regex_pattern}`
        }
      } catch (error) {
        console.error('Error validating direct tag:', error)
        directTagValidation.value = {
          isValid: false,
          error: 'Invalid regex regex_pattern'
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
      // Find tags that match the target taxonomy regex_pattern
      const targetTax = availableTaxonomies.value.find(t => t.id === targetTaxonomy)
      if (!targetTax) return []

      return filterTagsByPattern(allTags.value, targetTax.regex_pattern)
    }

    const buildRelationTag = () => {
      const taxonomy = availableTaxonomies.value.find(t => t.id === selectedTaxonomy.value)
      if (!taxonomy || !taxonomy.relations) return ''

      // Build tag based on taxonomy regex_pattern and selected values
      let tagPattern = taxonomy.id

      // Order relations according to the taxonomy regex_pattern or user-defined order
      // This should be configurable by the user in the future
      const relationOrder = taxonomy.relation_order ||
        taxonomy.relations.map(r => r.group).filter(Boolean) ||
        []

      for (const relationName of relationOrder) {
        const value = selectedValues.value[relationName]
        if (value) {
          // Extract the actual tag value (remove taxonomy prefix if present)
          const tagValue = value.includes(':') ? value.split(':')[1] : value
          tagPattern += `:${tagValue}`
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

    // Project tagging functions
    const openTaggingDialog = (mode, tag = null) => {
      taggingMode.value = mode
      selectedTagForTagging.value = tag
      selectedProjectsForTagging.value = []
      sourceTagForIndirect.value = null
      taggingSearch.value = ''

      // Load all available projects for tagging
      availableProjectsForTagging.value = [...allProjects.value]

      showTaggingDialog.value = true
    }

    const closeTaggingDialog = () => {
      showTaggingDialog.value = false
      selectedProjectsForTagging.value = []
      selectedTagForTagging.value = null
      sourceTagForIndirect.value = null
      taggingSearch.value = ''
    }

    const toggleProjectSelection = (project) => {
      const index = selectedProjectsForTagging.value.findIndex(p => p.uuid === project.uuid)
      if (index > -1) {
        selectedProjectsForTagging.value.splice(index, 1)
      } else {
        selectedProjectsForTagging.value.push(project)
      }
    }

    const isProjectSelected = (project) => {
      return selectedProjectsForTagging.value.some(p => p.uuid === project.uuid)
    }

    const filteredProjectsForTagging = computed(() => {
      if (!taggingSearch.value) return availableProjectsForTagging.value

      const search = taggingSearch.value.toLowerCase()
      return availableProjectsForTagging.value.filter(project =>
        project.name.toLowerCase().includes(search)
      )
    })

    const getProjectsWithTag = (tagName) => {
      return allProjects.value.filter(project =>
        project.tags && project.tags.some(tag =>
          typeof tag === 'string' ? tag === tagName : tag.name === tagName
        )
      )
    }

    const selectSourceTagForIndirect = (tagName) => {
      sourceTagForIndirect.value = tagName
      // Show projects that have this tag
      const projectsWithTag = getProjectsWithTag(tagName)
      selectedProjectsForTagging.value = projectsWithTag
    }

    const applyTagging = async () => {
      if (!selectedTagForTagging.value || selectedProjectsForTagging.value.length === 0) {
        return
      }

      try {
        loading.value = true

        const selectedTag = selectedTagForTagging.value
        const projects = selectedProjectsForTagging.value

        console.log('Applying tag:', selectedTag.name, 'to', projects.length, 'projects')

        // Check if this is a taxonomy tag that should trigger semantic bulk tagging
        if (isTaxonomyTag(selectedTag.name)) {
          console.log('Taxonomy tag detected - checking for semantic bulk tagging opportunities')

          // Find hard-linked tags that could be sources for semantic tagging
          const semanticResults = []

          for (const hardTag of hardLinkedTags.value) {
            // Check if there's a semantic relationship between this taxonomy tag and hard tag
            const semanticRelation = findSemanticRelation(selectedTag.name, hardTag.name)

            if (semanticRelation) {
              console.log('Found semantic relation:', semanticRelation)
              const result = await applySemanticBulkTagging(selectedTag, hardTag)
              semanticResults.push({
                hardTag: hardTag.name,
                relation: semanticRelation,
                result: result
              })
            }
          }

          // Apply direct tagging as well
          const directPromises = projects.map(project =>
            axios.post(`/api/projects/${project.uuid}/tags`, {
              tag_name: selectedTag.name
            })
          )

          await Promise.all(directPromises)

          console.log('Semantic bulk tagging results:', semanticResults)

        } else {
          // Simple direct tagging for non-taxonomy tags
          const taggingPromises = projects.map(project =>
            axios.post(`/api/projects/${project.uuid}/tags`, {
              tag_name: selectedTag.name
            })
          )

          await Promise.all(taggingPromises)
          console.log('Direct tagging completed')
        }

        // Refresh data and close dialog
        await loadAllProjects()
        if (selectedNodeId.value) {
          const selectedNode = taxonomyTree.value.find(node => node.id === selectedNodeId.value)
          if (selectedNode) {
            filterProjectsByNode(selectedNode)
          }
        }
        closeTaggingDialog()

      } catch (error) {
        console.error('Error applying tags:', error)
        alert('Error applying tags: ' + (error.response?.data?.message || error.message))
      } finally {
        loading.value = false
      }
    }

    // Find semantic relationship between taxonomy tag and hard-linked tag
    const findSemanticRelation = (taxonomyTag, hardLinkedTag) => {
      // Parse taxonomy tag to extract components
      const taxonomyComponents = parseTagComponents(taxonomyTag)
      if (!taxonomyComponents) return null

      // Check if hard-linked tag appears in taxonomy components
      const hardLinkedComponent = Object.values(taxonomyComponents).find(
        component => component === hardLinkedTag
      )

      if (hardLinkedComponent) {
        // Find which component matches
        const matchingComponent = findMatchingComponent(taxonomyComponents, hardLinkedTag)

        return {
          component: matchingComponent,
          hardTag: hardLinkedTag,
          taxonomyTag: taxonomyTag,
          description: `${taxonomyTag} contains ${hardLinkedTag} in ${matchingComponent} component`
        }
      }

      return null
    }

    // Find which component matches
    const findMatchingComponent = (taxonomyComponents, hardLinkedTag) => {
      return Object.keys(taxonomyComponents).find(
        key => taxonomyComponents[key] === hardLinkedTag
      )
    }

    // Check if a tag has semantic relationships (implies other tags)
    const checkIfSemanticTag = (tag) => {
      if (!tag || !tag.name) return false

      // Check if this tag is defined by taxonomy relations
      const taxonomy = availableTaxonomies.value.find(t => t.id === tag.taxonomy)
      if (!taxonomy || !taxonomy.relations || taxonomy.relations.length === 0) {
        return false
      }

      // Check if tag regex_pattern contains relationship indicators
      const hasRelationIndicators = taxonomy.relations.some(relation => {
        const relationPattern = relation.regex_pattern
        // Simple check: does tag name contain relation indicators like ':' or '_'?
        return relationPattern.includes(':') || relationPattern.includes('_')
      })

      return hasRelationIndicators
    }

    // Apply semantic tagging with implied relationships
    const applySemanticTagging = async () => {
      const selectedTag = selectedTagForTagging.value
      const projects = selectedProjectsForTagging.value

      console.log('Applying semantic tag:', selectedTag.name, 'to', projects.length, 'projects')

      // Apply main tag first
      const mainTagPromises = projects.map(project =>
        axios.post(`/api/projects/${project.uuid}/tags`, {
          tag_name: selectedTag.name
        })
      )

      await Promise.all(mainTagPromises)

      // Then apply implied tags based on taxonomy relations
      const impliedTags = await getImpliedTags(selectedTag)
      console.log('Implied tags to apply:', impliedTags)

      if (impliedTags.length > 0) {
        const impliedTagPromises = projects.map(project =>
          axios.post(`/api/projects/${project.uuid}/tags`, {
            tag_name: impliedTags[0].name // Apply first implied tag
          })
        )

        await Promise.all(impliedTagPromises)
      }

      console.log('Semantic tagging completed')
    }

    // Get implied tags based on taxonomy relationships
    const getImpliedTags = async (tag) => {
      const taxonomy = availableTaxonomies.value.find(t => t.id === tag.taxonomy)
      if (!taxonomy || !taxonomy.relations) return []

      const impliedTags = []

      for (const relation of taxonomy.relations) {
        if (relation.source === tag.taxonomy) {
          // This relation defines what other tags this tag implies
          const targetTaxonomy = availableTaxonomies.value.find(t => t.id === relation.targets)
          if (targetTaxonomy) {
            // Parse the tag to extract the components
            const components = parseTagComponents(tag.name, taxonomy)
            if (components) {
              // Create implied tag for the target taxonomy
              const impliedTag = {
                name: buildImpliedTagName(relation, components),
                taxonomy: targetTaxonomy.id
              }
              impliedTags.push(impliedTag)
            }
          }
        }
      }

      return impliedTags
    }

    // Build implied tag name based on relation and components
    const buildImpliedTagName = (relation, components) => {
      if (!components) return ''

      // Generic component mapping based on relation definition
      // User can define source_component and target_component in relations
      const sourceComponent = components[relation.source_component]
      const targetComponent = components[relation.target_component]

      if (sourceComponent && targetComponent) {
        return `${sourceComponent}:${targetComponent}`
      } else if (sourceComponent) {
        return sourceComponent
      } else if (targetComponent) {
        return targetComponent
      }

      return ''
    }

    // Apply direct tagging only (for non-semantic tags)
    const applyDirectTaggingOnly = async () => {
      const selectedTag = selectedTagForTagging.value
      const projects = selectedProjectsForTagging.value

      console.log('Applying direct tag:', selectedTag.name, 'to', projects.length, 'projects')

      const taggingPromises = projects.map(project =>
        axios.post(`/api/projects/${project.uuid}/tags`, {
          tag_name: selectedTag.name
        })
      )

      await Promise.all(taggingPromises)
      console.log('Direct tagging completed')
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
      showTaggingDialog,
      taggingMode,
      selectedProjectsForTagging,
      selectedTagForTagging,
      sourceTagForIndirect,
      availableProjectsForTagging,
      taggingSearch,
      filteredProjectsForTagging,
      showTaxonomyManagementDialog,
      hardLinkedTaxonomies,
      toggleHardLinkedTaxonomy,
      isTaxonomyHardLinked,
      openTaxonomyManagementDialog,
      closeTaxonomyManagementDialog,
      initializeHardLinkedTaxonomies,
      hardLinkedTags,
      taxonomyTags,
      categorizeTags,
      isHardLinkedTag,
      isTaxonomyTag,
      getProjectsWithHardLinkedTag,
      applySemanticBulkTagging,
      findSemanticRelation,
      openTaggingDialog,
      closeTaggingDialog,
      toggleProjectSelection,
      isProjectSelected,
      selectSourceTagForIndirect,
      applyTagging,
      viewProject,
      formatDate
    }
  }
}
</script>

<style scoped>
.taxonomy-tree-view {
  padding: 1.5rem;
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

.dark .taxonomy-tree :deep(.treeview-item-arrow) {
  color: #9ca3af;
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

/* Dark theme fixes for custom tree node content */
.dark .taxonomy-tree :deep(span) {
  color: #f9fafb !important; /* Force white text for all spans in dark theme */
}

.dark .taxonomy-tree :deep(.flex.items-center) {
  color: #f9fafb !important; /* White text for dark theme */
}

.dark .taxonomy-tree :deep(.flex.items-center .font-medium) {
  color: #f9fafb !important; /* White text for node names */
}

.dark .taxonomy-tree :deep(.flex.items-center .text-sm) {
  color: #d1d5db !important; /* Light gray for secondary text */
}

.dark .taxonomy-tree :deep(.bg-gray-100) {
  background-color: #374151 !important; /* Darker background for badges */
  color: #d1d5db !important;
}

.dark .taxonomy-tree :deep(.bg-blue-50) {
  background-color: rgba(59, 130, 246, 0.2) !important; /* Darker blue for selection */
}

.dark .taxonomy-tree :deep(.text-gray-600) {
  color: #9ca3af !important; /* Lighter gray for muted text */
}

.dark .taxonomy-tree :deep(.text-gray-900) {
  color: #f9fafb !important; /* White for primary text */
}

.dark .taxonomy-tree :deep(.text-gray-500) {
  color: #9ca3af !important; /* Lighter gray for secondary text */
}

/* Most specific targeting for tree node text */
.dark .taxonomy-tree :deep(.treeview-item-content span) {
  color: #f9fafb !important;
}

.dark .taxonomy-tree :deep(.treeview-item-content .flex span) {
  color: #f9fafb !important;
}

.dark .taxonomy-tree :deep(.treeview-item-content .flex .flex-1 span) {
  color: #f9fafb !important;
}

/* Dark theme hover and selection fixes */
.dark .taxonomy-tree :deep(.treeview-item:hover) {
  background-color: rgba(55, 65, 81, 0.5);
}

.dark .taxonomy-tree :deep(.treeview-item.selected) {
  background-color: rgba(59, 130, 246, 0.2);
  border-left-color: #60a5fa;
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
