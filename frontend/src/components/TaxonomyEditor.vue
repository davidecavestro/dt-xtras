<template>
  <div class="px-4 py-6 sm:px-0 lg:px-8">
    <div class="border-4 border-dashed border-gray-200 dark:border-gray-700 rounded-lg p-6">
      <div class="flex justify-between items-center mb-6">
        <h2 class="text-2xl font-bold text-gray-900 dark:text-white">Taxonomy Builder</h2>
        <button
          @click="addTaxonomy"
          class="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700"
        >
          <Plus class="inline w-4 h-4 mr-2" />
          Add Taxonomy
        </button>
      </div>

      <!-- Main Content - Always Visible -->
      <div class="grid grid-cols-1 lg:grid-cols-2 bg-white dark:bg-gray-800 shadow rounded-lg p-1">
        <!-- Taxonomy Graph Visualization -->
        <div class="bg-white dark:bg-gray-800 shadow rounded-lg p-6 mb-6">
          <div class="flex justify-between items-center mb-4">
            <h3 class="text-lg font-medium text-gray-900 dark:text-white">Taxonomy Relations Graph</h3>
            <button
              @click="resetGraphView"
              class="px-3 py-1 bg-gray-600 text-white text-sm rounded-md hover:bg-gray-700"
            >
              Reset View
            </button>
          </div>

          <div class="border-2 border-gray-200 dark:border-gray-600 rounded-lg bg-gray-50 dark:bg-gray-700" style="height: 400px; position: relative; overflow: hidden;">
            <div ref="cytoscapeContainer" class="w-full h-full"></div>
          </div>
        </div>

        <!-- Taxonomies List -->
        <div class="bg-white dark:bg-gray-800 shadow overflow-hidden sm:rounded-md">
          <div class="px-4 py-5 sm:px-6">
            <h3 class="text-lg leading-6 font-medium text-gray-900 dark:text-white">Existing Taxonomies</h3>
            <p class="mt-1 max-w-2xl text-sm text-gray-500 dark:text-gray-400">
              Taxonomies are processed in priority order (lower numbers first)
            </p>
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
              <div class="flex flex-col gap-2">
                <div class="flex items-center justify-between">
                  <div class="flex items-center space-x-3">
                    <div class="text-gray-400 dark:text-gray-500">
                      <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                        <path d="M10 6a2 2 0 110-4 2 2 0 010 4zM10 12a2 2 0 110-4 2 2 0 010 4zM10 18a2 2 0 110-4 2 2 0 010 4z"/>
                      </svg>
                    </div>
                    <div class="flex-1">
                      <div class="flex items-center">
                        <div
                          class="w-4 h-4 rounded-full mr-2 border border-gray-300 dark:border-gray-600"
                          :style="{ backgroundColor: taxonomy.color || '#3B82F6' }"
                          :title="`Color: ${taxonomy.color || '#3B82F6'}`"
                        ></div>
                        <span class="text-sm font-medium text-gray-900 dark:text-white">{{ taxonomy.name }}</span>
                        <span class="ml-2 px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-blue-100 dark:bg-blue-900/30 text-blue-800 dark:text-blue-200">
                          {{ taxonomy.id }}
                        </span>
                      </div>
                      <div class="mt-1">
                        <code class="text-xs bg-gray-100 dark:bg-gray-700 px-1 py-0.5 rounded text-gray-800 dark:text-gray-200 truncate max-w-xs inline-block" :title="taxonomy.regex_pattern">{{ taxonomy.regex_pattern }}</code>
                      </div>
                    </div>
                  </div>
                </div>
                <div class="flex gap-2 justify-end mx-3 mb-3">
                  <button
                    @click="editTaxonomy(taxonomy)"
                    class="px-3 py-1 bg-blue-600 text-white text-sm rounded-md hover:bg-blue-700 inline-flex items-center gap-1"
                  >
                    <Edit2 class="w-4 h-4" /> Edit
                  </button>
                  <button
                    @click="deleteTaxonomy(taxonomy.id)"
                    class="px-3 py-1 bg-red-600 text-white text-sm rounded-md hover:bg-red-700 inline-flex items-center gap-1"
                  >
                    <Trash2 class="w-4 h-4" /> Remove
                  </button>
                </div>
              </div>
            </li>
          </ul>

          <div v-if="taxonomies.length === 0" class="text-center py-8 text-gray-500 dark:text-gray-400">
            No taxonomies defined yet. Create your first taxonomy to get started.
          </div>
        </div>
      </div>

      <!-- Edit Form View -->
      <div v-if="editingTaxonomy">
      <!-- Taxonomy Form -->
        <div class="bg-white dark:bg-gray-800 shadow rounded-lg p-6 mt-5">
          <div class="flex justify-between items-center mb-4">
            <h3 class="text-lg font-medium text-gray-900 dark:text-white">
              {{ isEditingExisting ? 'Edit Taxonomy' : 'Create Taxonomy' }}
            </h3>
            <button
              @click="cancelEdit"
              class="px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm text-sm font-medium text-gray-700 dark:text-gray-300 bg-white dark:bg-gray-800 hover:bg-gray-50 dark:hover:bg-gray-700"
            >
              ← Back to List
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
                      <input
                        v-model="relation.group"
                        type="text"
                        class="mt-1 block w-full border-gray-300 dark:border-gray-600 dark:bg-gray-700 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm dark:text-white px-3 py-2"
                        placeholder="e.g., customer"
                      />
                    </div>
                    <div>
                      <label class="block text-sm font-medium text-gray-700 dark:text-gray-300">Target Taxonomy</label>
                      <input
                        v-model="relation.targets"
                        type="text"
                        class="mt-1 block w-full border-gray-300 dark:border-gray-600 dark:bg-gray-700 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm dark:text-white px-3 py-2"
                        placeholder="e.g., customer"
                      />
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
</template>

<script setup>
import { ref, computed, onMounted, nextTick, watch } from 'vue'
import { Plus, Trash2, Edit2 } from 'lucide-vue-next'
import axios from 'axios'
import cytoscape from 'cytoscape'

// Reactive data
const taxonomies = ref([])
const editingTaxonomy = ref(null)
const testTags = ref('')
const regexTestResult = ref(null)

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
const cytoscapeContainer = ref(null)
const cytoscapeInstance = ref(null)
const draggedIndex = ref(null)

    const isFormValid = computed(() => {
      return editingTaxonomy.value &&
             editingTaxonomy.value.id &&
             editingTaxonomy.value.name &&
             editingTaxonomy.value.regex_pattern !== undefined
    })

    const isEditingExisting = computed(() => {
      return editingTaxonomy.value &&
             taxonomies.value.some(t => t.id === editingTaxonomy.value.id)
    })

    const loadTaxonomies = async () => {
      try {
        const response = await axios.get('/api/taxonomies')
        taxonomies.value = response.data
      } catch (error) {
        console.error('Error loading taxonomies:', error)
      }
    }

    const addTaxonomy = () => {
      editingTaxonomy.value = {
        id: '',
        name: '',
        regex_pattern: '^.*$', // Default regex_pattern - matches anything
        priority: 1,
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
      testTags.value = ''
      regexTestResult.value = null
    }

    const saveTaxonomy = async () => {
      try {
        if (editingTaxonomy.value.id && taxonomies.value.some(t => t.id === editingTaxonomy.value.id && t !== editingTaxonomy.value)) {
          // Update existing
          await axios.put(`/api/taxonomies/${editingTaxonomy.value.id}`, editingTaxonomy.value)
        } else {
          // Create new
          await axios.post('/api/taxonomies', editingTaxonomy.value)
        }

        await loadTaxonomies()
        cancelEdit()
      } catch (error) {
        console.error('Error saving taxonomy:', error)
        alert('Error saving taxonomy: ' + (error.response?.data?.detail || error.message))
      }
    }

    const deleteTaxonomy = async (id) => {
      if (!confirm('Are you sure you want to delete this taxonomy?')) {
        return
      }

      try {
        await axios.delete(`/api/taxonomies/${id}`)
        await loadTaxonomies()
      } catch (error) {
        console.error('Error deleting taxonomy:', error)
        alert('Error deleting taxonomy: ' + (error.response?.data?.detail || error.message))
      }
    }

    const testRegex = () => {
      if (!editingTaxonomy.value.regex_pattern || !testTags.value) {
        return
      }

      try {
        const regex = new RegExp(editingTaxonomy.value.regex_pattern)
        const match = testTags.value.match(regex)

        if (match) {
          regexTestResult.value = {
            success: true,
            match: match[0],
            groups: match.slice(1),
            message: '✅ Pattern matches!'
          }
        } else {
          regexTestResult.value = {
            success: false,
            match: null,
            groups: [],
            message: '❌ Pattern does not match test string'
          }
        }
      } catch (error) {
        regexTestResult.value = {
          success: false,
          match: null,
          groups: [],
          message: `❌ Invalid regex: ${error.message}`
        }
      }
    }

    // Graph visualization methods
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
          associative: taxonomy.associative || false,
          priority: taxonomy.priority,
          relations: taxonomy.relations || [],
          color: taxonomy.color || '#3B82F6'
        }
      }));

      // Convert relations to Cytoscape edges
      const edges = [];
      taxonomies.value.forEach(taxonomy => {
        if (taxonomy.relations) {
          taxonomy.relations.forEach(relation => {
            if (relation.targets) {
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

      console.log('🎨 Rendering TaxonomyEditor Cytoscape graph:', { nodes, edges });

      // Initialize Cytoscape
      cytoscapeInstance.value = cytoscape({
        container: cytoscapeContainer.value,
        elements: [...nodes, ...edges],
        style: [
          {
            selector: 'node',
            style: {
              'shape': function(ele) {
                return ele.data('associative') ? 'round-rectangle' : 'round-tag';
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
              'box-shadow': '0 0 20px rgba(59, 130, 246, 0.5)',
              'text-shadow': '0 0 8px rgba(59, 130, 246, 0.8)',
              'font-weight': 'bold'
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

        await axios.put('/api/taxonomies/reorder', taxonomiesWithPriority);
        console.log('Taxonomy order saved successfully');
      } catch (error) {
        console.error('Error saving taxonomy order:', error);
        // Optionally revert the order if save fails
        await loadTaxonomies();
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

    const getNodeIcon = (node) => {
      // Use user-defined icon or suggest based on ID regex_pattern
      if (node.icon) return node.icon

      // Suggest icons based on common patterns (optional, can be overridden)
      const suggestions = {
        'env': '🌍',
        'customer': '👥',
        'cust': '👥',
        'deploy': '🚀',
        'product': '📦',
        'version': '🔖',
        'app': '📱',
        'service': '⚙️',
        'team': '�',
        'project': '�'
      }

      // Check if ID contains any known patterns
      for (const [regex_pattern, icon] of Object.entries(suggestions)) {
        if (node.id.toLowerCase().includes(regex_pattern)) {
          return icon
        }
      }

      return '📁' // Default icon
    }

    onMounted(() => {
      loadTaxonomies()

      // Listen for edit events from graph
      window.addEventListener('editTaxonomyFromGraph', (event) => {
        const { taxonomy } = event.detail;
        editTaxonomy(taxonomy);
      });
    })

    // Rebuild graph when taxonomies change
    watch(taxonomies, () => {
      nextTick(() => {
        renderCytoscapeGraph();
      })
    }, { deep: true })
</script>
