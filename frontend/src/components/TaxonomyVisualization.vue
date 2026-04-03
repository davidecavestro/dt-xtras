<template>
  <div class="p-6 max-w-7xl mx-auto">
    <!-- Header -->
    <div class="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-4 mb-6">
      <div class="flex justify-between items-center">
        <h1 class="text-2xl font-bold text-gray-800 dark:text-white mb-4">Tags Graph</h1>

        <!-- View Mode Controls -->
        <div class="flex items-center space-x-2">
          <button
            @click="viewMode = 'list'"
            :class="[
              'px-3 py-1 text-sm rounded-md',
              viewMode === 'list'
                ? 'bg-blue-600 text-white'
                : 'bg-gray-200 text-gray-700 dark:bg-gray-700 dark:text-gray-300'
            ]"
          >
            <List class="w-4 h-4" />
          </button>
          <button
            @click="viewMode = 'grid'"
            :class="[
              'px-3 py-1 text-sm rounded-md',
              viewMode === 'grid'
                ? 'bg-blue-600 text-white'
                : 'bg-gray-200 text-gray-700 dark:bg-gray-700 dark:text-gray-300'
            ]"
          >
            <Grid3X3 class="w-4 h-4" />
          </button>
          <button
            @click="viewMode = 'deck'"
            :class="[
              'px-3 py-1 text-sm rounded-md',
              viewMode === 'deck'
                ? 'bg-blue-600 text-white'
                : 'bg-gray-200 text-gray-700 dark:bg-gray-700 dark:text-gray-300'
            ]"
          >
            <Square class="w-4 h-4" />
          </button>
        </div>
      </div>

      <!-- Controls -->
      <div class="flex items-center space-x-6">
        <!-- Associative Mode Toggle -->
        <div class="flex items-center space-x-2">
          <label class="text-sm font-medium text-gray-700 dark:text-gray-300">Mode:</label>
          <div class="flex items-center space-x-2">
            <input
              type="radio"
              id="associative-mode"
              v-model="associativeMode"
              :value="true"
              @change="updateVisualization"
              class="text-blue-600 focus:ring-blue-500"
            >
            <label for="associative-mode" class="text-sm text-gray-700 dark:text-gray-300">Associative</label>

            <input
              type="radio"
              id="normal-mode"
              v-model="associativeMode"
              :value="false"
              @change="updateVisualization"
              class="text-blue-600 focus:ring-blue-500"
              >
              <label for="normal-mode" class="text-sm text-gray-700 dark:text-gray-300">Raw</label>
          </div>
        </div>

        <!-- Taxonomy Selector -->
        <div class="flex items-center space-x-2">
          <label class="text-sm font-medium text-gray-700 dark:text-gray-300">Force Root Taxonomy:</label>
          <select
            v-model="selectedTaxonomy"
            @change="updateVisualization"
            class="px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
            v-if="!loading"
            :disabled="!associativeMode"
          >
            <option v-for="taxonomy in taxonomiesData" :key="taxonomy.id" :value="taxonomy.id">
              {{ taxonomy.name || taxonomy.id }}
            </option>
          </select>
        </div>
      </div>

      <!-- Mode Description -->
      <div v-if="!loading" class="mt-3 text-sm text-gray-600 dark:text-gray-400">
        {{ modeDescription }}
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="flex justify-center items-center h-64">
      <div class="text-lg">Loading taxonomy data...</div>
    </div>

    <!-- Error State -->
    <div v-if="error" class="bg-red-100 dark:bg-red-900/20 border border-red-400 dark:border-red-600 text-red-700 dark:text-red-300 px-4 py-3 rounded mb-6">
      <strong>Error:</strong> {{ error }}
    </div>

    <!-- Main Graph Content -->
    <div v-if="!loading && !error">
      <!-- Graph and Related Projects Side by Side -->
      <div class="flex flex-col lg:flex-row gap-6">
        <!-- Left: Graph Section -->
        <div class="flex-1">
          <!-- Cytoscape Graph -->
          <div class="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-4">
            <h2 class="text-xl font-semibold mb-4 text-gray-900 dark:text-white">Graph Visualization</h2>
            <div ref="cytoscapeContainer" class="w-full h-96 lg:h-[600px] border border-gray-300 dark:border-gray-600 rounded bg-gray-50 dark:bg-gray-700 resize overflow-hidden"></div>
          </div>

          <!-- Graph Controls -->
          <div class="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-4 mt-6">
            <h2 class="text-xl font-semibold mb-4 text-gray-900 dark:text-white">Graph Controls</h2>

            <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
          <!-- Layout Algorithm -->
          <div>
            <label class="text-sm font-medium text-gray-700 dark:text-gray-300">Layout Algorithm:</label>
            <select
              v-model="layoutAlgorithm"
              @change="updateGraphLayout"
              class="mt-1 block w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
            >
              <option value="dagre">Dagre (Hierarchical)</option>
              <option value="breadthfirst">Breadth-First</option>
              <option value="cose">CoSE (Force-Directed)</option>
              <option value="circle">Circular</option>
              <option value="grid">Grid</option>
              <option value="concentric">Concentric</option>
            </select>
          </div>

          <!-- Node Spacing -->
          <div>
            <label class="text-sm font-medium text-gray-700 dark:text-gray-300">Node Spacing:</label>
            <input
              v-model.number="nodeSpacing"
              @change="updateGraphLayout"
              type="range"
              min="50"
              max="200"
              step="10"
              class="mt-1 block w-full"
            />
            <div class="text-sm text-gray-600 dark:text-gray-400">{{ nodeSpacing }}px</div>
          </div>
        </div>
      </div>
        </div>
        <!-- End Left: Graph Section -->

        <!-- Right: Related Projects Section -->
        <div v-if="associativeMode" class="lg:w-96">
          <div class="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-4">
            <h2 class="text-xl font-semibold mb-4 text-gray-900 dark:text-white">Related Projects</h2>

            <!-- Selected Node Info -->
            <div v-if="selectedNode" class="mb-4 p-3 bg-gray-50 dark:bg-gray-700 rounded">
              <div class="text-sm font-medium text-gray-700 dark:text-gray-300">Selected Node:</div>
              <div class="text-sm text-gray-900 dark:text-white">{{ selectedNode.label || selectedNode.id }}</div>
            </div>

            <!-- Projects List -->
            <div v-if="relatedProjects.length > 0" class="space-y-2">
              <div class="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                {{ relatedProjects.length }} projects found
                <span v-if="relatedProjectsTotal > relatedProjects.length" class="text-xs text-gray-500">
                  (showing {{ relatedProjects.length }} of {{ relatedProjectsTotal }})
                </span>
              </div>

              <!-- Pagination Controls -->
              <div v-if="relatedProjectsTotal > pageSize" class="flex justify-between items-center mb-4">
                <button
                  @click="loadRelatedProjectsPage(1)"
                  :disabled="relatedProjectsPage === 1"
                  class="px-3 py-1 text-sm border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700 disabled:opacity-50 disabled:cursor-not-allowed"
                >
              First
            </button>

            <button
              @click="loadRelatedProjectsPage(relatedProjectsPage - 1)"
              :disabled="relatedProjectsPage === 1"
              class="px-3 py-1 text-sm border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Previous
            </button>

            <div class="text-sm text-gray-600 dark:text-gray-400">
              Page {{ relatedProjectsPage }} of {{ relatedProjectsTotalPages }}
            </div>

            <button
              @click="loadRelatedProjectsPage(relatedProjectsPage + 1)"
              :disabled="relatedProjectsPage >= relatedProjectsTotalPages"
              class="px-3 py-1 text-sm border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Next
            </button>

            <button
              @click="loadRelatedProjectsPage(relatedProjectsTotalPages)"
              :disabled="relatedProjectsPage >= relatedProjectsTotalPages"
              class="px-3 py-1 text-sm border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Last
            </button>
          </div>

          <div v-if="loadingRelatedProjects" class="text-center py-8">
            <div class="inline-block animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600"></div>
            <p class="mt-2 text-sm text-gray-600 dark:text-gray-400">Loading projects...</p>
          </div>

          <div class="max-h-96 overflow-y-auto space-y-2">
            <div
              v-for="project in relatedProjects"
              :key="project.uuid"
              class="p-3 bg-gray-50 dark:bg-gray-700 rounded hover:bg-gray-100 dark:hover:bg-gray-600 cursor-pointer border border-gray-200 dark:border-gray-600"
            >
              <div class="flex justify-between items-start mb-2">
                <div>
                  <div class="text-sm font-medium text-gray-900 dark:text-white">{{ project.name }}</div>
                  <div class="text-xs text-gray-500 dark:text-gray-400">{{ project.version || 'latest' }}</div>
                </div>
                <a
                  :href="buildDTProjectUrl(project.uuid)"
                  target="_blank"
                  rel="noopener noreferrer"
                  class="text-xs text-blue-600 dark:text-blue-400 hover:text-blue-800 dark:hover:text-blue-300 flex items-center"
                  title="View in Dependency-Track"
                >
                  <svg class="w-3 h-3 mr-1" fill="currentColor" viewBox="0 0 20 20">
                    <path d="M11 3a1 1 0 100 2h2.586l-6.293 6.293a1 1 0 101.414 1.414L15 6.414V9a1 1 0 102 0V4a1 1 0 00-1-1h-3z"/>
                    <path d="M5 5a2 2 0 00-2 2v8a2 2 0 002 2h8a2 2 0 002-2v-3a1 1 0 10-2 0v3H5V7h3a1 1 0 000-2H5z"/>
                  </svg>
                  DT
                </a>
              </div>
              <div class="text-xs text-gray-500 dark:text-gray-400 mb-2">{{ project.tags.join(', ') }}</div>

              <!-- Security Info -->
              <div v-if="project.metrics" class="flex flex-wrap gap-2 text-xs">
                <span v-if="project.metrics.critical > 0" class="px-2 py-1 bg-red-100 dark:bg-red-900 text-red-800 dark:text-red-200 rounded">
                  🔴 {{ project.metrics.critical }} Critical
                </span>
                <span v-if="project.metrics.high > 0" class="px-2 py-1 bg-orange-100 dark:bg-orange-900 text-orange-800 dark:text-orange-200 rounded">
                  🟠 {{ project.metrics.high }} High
                </span>
                <span v-if="project.metrics.medium > 0" class="px-2 py-1 bg-yellow-100 dark:bg-yellow-900 text-yellow-800 dark:text-yellow-200 rounded">
                  🟡 {{ project.metrics.medium }} Medium
                </span>
                <span v-if="project.metrics.low > 0" class="px-2 py-1 bg-blue-100 dark:bg-blue-900 text-blue-800 dark:text-blue-200 rounded">
                  🔵 {{ project.metrics.low }} Low
                </span>
                <span v-if="getTotalVulnerabilities(project.metrics) === 0" class="px-2 py-1 bg-green-100 dark:bg-green-900 text-green-800 dark:text-green-200 rounded">
                  ✅ No Vulnerabilities
                </span>
              </div>
            </div>
          </div>
        </div>

        <div v-else class="text-sm text-gray-500 dark:text-gray-400">
          {{ selectedNode ? 'No projects found for this selection' : 'Select a node to see related projects' }}
        </div>
          </div>
        </div>
        <!-- End Right: Related Projects Section -->
      </div>
      <!-- End Graph and Related Projects Container -->
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted, nextTick, watch } from 'vue';
import SimpleTaxonomyGraphBuilder from '../utils/simpleTaxonomyGraphBuilder.js';
import axios from 'axios';
import { List, Grid3X3, Square } from 'lucide-vue-next';
import cytoscape from 'cytoscape';
import { buildDTProjectUrl } from '../config.js';
import dagre from 'cytoscape-dagre';

// Register dagre extension
cytoscape.use(dagre);

export default {
  name: 'TaxonomyVisualization',
  components: {
    List,
    Grid3X3,
    Square
  },
  setup() {
    // Reactive variables
    const graphData = ref(null);
    const loading = ref(true);
    const error = ref(null);
    const tags = ref(null);
    const taxonomies = ref(null);
    const taxonomiesData = ref(null);
    const allTaxonomiesData = ref(null); // For color mapping
    const selectedTaxonomy = ref(null);
    const associativeMode = ref(true);
    const selectedNode = ref(null);
    const cytoscapeContainer = ref(null);
    const cytoscapeInstance = ref(null);
    const layoutAlgorithm = ref('dagre');
    const nodeSpacing = ref(50);
    const relatedProjects = ref([]);
    const relatedProjectsPage = ref(1);
    const relatedProjectsTotal = ref(0);
    const relatedProjectsTotalPages = ref(1);
    const pageSize = ref(20); // Dashboard shows fewer projects per page
    const loadingRelatedProjects = ref(false);
    const viewMode = ref('graph'); // 'graph', 'list', 'grid', or 'deck'

    const graphBuilder = new SimpleTaxonomyGraphBuilder();

    // Taxonomy colors - now dynamic based on user choices
    const taxonomyColors = computed(() => {
      const colors = {};
      if (allTaxonomiesData.value) {
        allTaxonomiesData.value.forEach(taxonomy => {
          colors[taxonomy.id] = taxonomy.color || '#6b7280';
        });
      }
      return colors;
    });

    // Computed properties
    const modeDescription = computed(() => {
      if (associativeMode.value) {
        return 'Associative mode creates direct connections between related taxonomies, hiding intermediate connector nodes. Each connection represents a semantic relationship between taxonomy elements. This mode shows projects related to your selection in the Related Projects panel.';
      } else {
        return 'Normal mode creates hierarchical relationships where child nodes connect to parent nodes through defined taxonomy relations. This mode does not show related projects - use Associative mode to see project relationships.';
      }
    });

    const taxonomyNodes = computed(() => {
      if (!graphData.value?.nodes) return {};
      const nodes = {};
      Array.from(graphData.value.nodes.values()).forEach(node => {
        if (!nodes[node.taxonomy]) {
          nodes[node.taxonomy] = [];
        }
        nodes[node.taxonomy].push(node);
      });
      return nodes;
    });

    // Methods
    const loadData = async () => {
      try {
        loading.value = true;
        error.value = null;

        const [tagsResponse, taxonomiesResponse] = await Promise.all([
          axios.get('/api/tags'),
          axios.get('/api/taxonomies')
        ]);

        console.log('Tags response:', tagsResponse);
        console.log('Taxonomies response:', taxonomiesResponse);

        const tags = tagsResponse.data.tags || tagsResponse.data;
        const taxonomies = taxonomiesResponse.data;

        if (!tags || !taxonomies) {
          throw new Error('Failed to fetch data');
        }

        // Store taxonomies data filtering associative taxonomies for graph building, but keep all for colors
        allTaxonomiesData.value = taxonomies; // Store all taxonomies for color mapping
        taxonomiesData.value = associativeMode.value ? taxonomies.filter(taxonomy => taxonomy.relations !== undefined) : taxonomies;

        // Build graph with current mode
        const graph = graphBuilder.buildGraph(tags, taxonomiesData.value, selectedTaxonomy.value, associativeMode.value);
        graphData.value = graph;

      } catch (err) {
        console.error('Error loading data:', err);
        error.value = err.response?.data?.detail || err.message;

        if (err.response?.status === 403) {
          error.value = 'Authentication required. Please log in first.';
        }
      } finally {
        loading.value = false;
      }
    };

    const updateVisualization = () => {
      if (taxonomiesData.value) {
        // Rebuild graph with new mode
        rebuildGraph();
      }
    };

    const rebuildGraph = async () => {
      try {
        loading.value = true;

        // Get fresh tags data
        const tagsResponse = await axios.get('/api/tags');
        const tags = tagsResponse.data.tags || tagsResponse.data;

        if (!tags) {
          throw new Error('Failed to fetch tags');
        }

        // Rebuild graph with current mode
        const graph = graphBuilder.buildGraph(tags, taxonomiesData.value, selectedTaxonomy.value, associativeMode.value);
        graphData.value = graph;

        // Re-render Cytoscape after graph is built
        nextTick(() => {
          renderCytoscapeGraph();
        });

      } catch (err) {
        console.error('Error rebuilding graph:', err);
        error.value = err.response?.data?.detail || err.message;
      } finally {
        loading.value = false;
      }
    };

    const renderCytoscapeGraph = () => {
      if (!graphData.value || !cytoscapeContainer.value) return;

      // Destroy existing instance
      if (cytoscapeInstance.value) {
        cytoscapeInstance.value.destroy();
      }

      // Convert graph data to Cytoscape format
      const nodes = Array.from(graphData.value.nodes.values()).map(node => {
        // Extract capture group from tag name if it matches taxonomy pattern
        const taxonomy = taxonomiesData.value?.find(t => t.id === node.taxonomy);
        let captureGroups = [];
        if (taxonomy && taxonomy.regex_pattern) {
          try {
            const regex = new RegExp(taxonomy.regex_pattern);
            const match = regex.exec(node.id);
            if (match && match.groups) {
              captureGroups = Object.values(match.groups).filter(g => g); // Get all non-empty capture groups
            }
          } catch (e) {
            console.warn('Invalid regex pattern:', taxonomy.regex_pattern);
          }
        }

        const taxonomyName = taxonomy?.name || node.taxonomy;

        return {
          data: {
            id: node.id,
            label: `${taxonomyName}\n${captureGroups.length > 0 ? '\n' + captureGroups.join('\n') : ''}`, // Show taxonomy name and capture groups
            taxonomy: node.taxonomy,
            captureGroups: captureGroups,
            associative: node.associative || false,
            projectsCount: node.projectsCount || 0
          }
        };
      });

      const edges = graphData.value.edges.map(edge => ({
        data: {
          id: edge.id || `${edge.source}-${edge.target}`,
          source: edge.source,
          target: edge.target,
          group: edge.group || 'default'
        }
      }));

      // Initialize Cytoscape
      cytoscapeInstance.value = cytoscape({
        container: cytoscapeContainer.value,
        elements: [...nodes, ...edges],
        style: [
          {
            selector: 'node',
            style: {
              'shape': function(ele) {
                return ele.data('associative') ? 'round-rectangle' : 'barrel';
              },
              'background-color': function(ele) {
                const colors = taxonomyColors.value;
                return colors[ele.data('taxonomy')] || '#6b7280';
              },
              'color': function(ele) {
                // Get background color
                const colors = taxonomyColors.value;
                const bgColor = colors[ele.data('taxonomy')] || '#6b7280';
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
              'text-wrap': 'wrap',
              'text-max-width': '120px',
              'width': function(ele) {
                return ele.data('associative') ? '250px' : '180px';
              },
              'height': '80px',
              'padding': '10px'
            }
          },
          {
            selector: 'edge',
            style: {
              'width': 3,
              'line-color': '#9ca3af',
              'target-arrow-color': '#9ca3af',
              'target-arrow-shape': 'triangle',
              'curve-style': 'bezier',
              'arrow-scale': 1.2
            }
          }
        ],
        layout: layoutAlgorithm.value === 'dagre' ? {
          name: 'dagre',
          nodeSep: nodeSpacing.value,
          edgeSep: nodeSpacing.value / 2,
          rankSep: nodeSpacing.value,
          rankDir: 'TB',
          animate: true,
          animationDuration: 1000,
          fit: true,
          padding: 50
        } : {
          name: layoutAlgorithm.value,
          nodeSpacing: nodeSpacing.value,
          animate: true,
          animationDuration: 1000,
          fit: true,
          padding: 50
        }
      });

      // Add event listeners
      cytoscapeInstance.value.on('tap', 'node', function(evt) {
        const node = evt.target;
        selectNode(node.data());
      });

      cytoscapeInstance.value.on('tap', 'edge', function(evt) {
        const edge = evt.target;
        selectNode(edge.data());
      });

      // Add hover effects
      cytoscapeInstance.value.on('mouseover', 'node', function(evt) {
        const node = evt.target;
        node.style({
          'width': function(ele) {
            return ele.data('associative') ? '280px' : '180px';
          },
          'height': '80px',
          'font-size': '16px',
          'z-index': 1000
        });
      });

      cytoscapeInstance.value.on('mouseout', 'node', function(evt) {
        const node = evt.target;
        node.style({
          'width': function(ele) {
            return ele.data('associative') ? '250px' : '150px';
          },          'height': '60px',
          'font-size': '14px',
          'z-index': 1
        });
      });

      // Enable editing from graph
      cytoscapeInstance.value.on('dblclick', 'node', function(evt) {
        const node = evt.target;
        const taxonomyData = taxonomiesData.value?.find(t => t.id === node.data('taxonomy'));
        if (taxonomyData) {
          // Emit event to open TaxonomyEditor with this taxonomy
          const editEvent = new CustomEvent('editTaxonomyFromGraph', {
            detail: { taxonomy: taxonomyData }
          });
          window.dispatchEvent(editEvent);
        }
      });
    };

    const updateGraphLayout = () => {
      if (cytoscapeInstance.value) {
        const layoutConfig = layoutAlgorithm.value === 'dagre' ? {
          name: 'dagre',
          nodeSep: nodeSpacing.value,
          edgeSep: nodeSpacing.value / 2,
          rankSep: nodeSpacing.value,
          rankDir: 'TB',
          animate: true,
          animationDuration: 1000,
          fit: true,
          padding: 50
        } : {
          name: layoutAlgorithm.value,
          nodeSpacing: nodeSpacing.value,
          animate: true,
          animationDuration: 1000,
          fit: true,
          padding: 50
        };

        cytoscapeInstance.value.layout(layoutConfig).run();
      }
    };

    const selectNode = (node) => {
      selectedNode.value = node;
      updateRelatedProjects(node);
      console.log('Selected node:', node);
    };

    const getTaxonomyDisplayName = (taxonomyId) => {
      const taxonomy = taxonomiesData.value.find(t => t.id === taxonomyId);
      return taxonomy ? taxonomy.name || taxonomy.id : taxonomyId;
    };

    const getNodeConnections = (nodeId, direction) => {
      if (!graphData.value?.edges) return 0;
      return graphData.value.edges.filter(edge => edge[direction] === nodeId);
    };

    // Find all reachable tags from a selected node
    const findReachableTags = (startNodeId) => {
      if (!graphData.value?.nodes || !graphData.value?.edges) return new Set();

      const visited = new Set();
      const queue = [startNodeId];
      const reachableTags = new Set();

      while (queue.length > 0) {
        const currentId = queue.shift();
        if (visited.has(currentId)) continue;

        visited.add(currentId);
        reachableTags.add(currentId);

        // Find all connected nodes (both incoming and outgoing)
        const connectedNodes = graphData.value.edges
          .filter(edge => edge.source === currentId || edge.target === currentId)
          .map(edge => edge.source === currentId ? edge.target : edge.source);

        connectedNodes.forEach(nodeId => {
          if (!visited.has(nodeId)) {
            queue.push(nodeId);
          }
        });
      }

      return reachableTags;
    };

    // Get projects for a set of tags (with pagination)
    const getProjectsForTags = async (tagIds, page = 1) => {
      if (!tagIds || tagIds.size === 0) return [];

      try {
        loadingRelatedProjects.value = true;

        // Get projects with pagination support
        const response = await axios.get('/api/projects', {
          params: {
            limit: pageSize.value,
            offset: (page - 1) * pageSize.value
          }
        });
        const allProjects = response.data;

        // Filter projects that have any of the specified tags
        const filteredProjects = allProjects.filter(project => {
          const projectTags = project.tags || [];
          return Array.from(tagIds).some(tagId => projectTags.includes(tagId));
        });

        // Get total count for pagination
        try {
          const countResponse = await axios.get('/api/projects/count');
          relatedProjectsTotal.value = countResponse.data.total;
          relatedProjectsTotalPages.value = Math.ceil(relatedProjectsTotal.value / pageSize.value);
        } catch (countError) {
          console.warn('Could not get project count:', countError);
          relatedProjectsTotal.value = filteredProjects.length;
          relatedProjectsTotalPages.value = 1;
        }

        relatedProjects.value = filteredProjects;
        relatedProjectsPage.value = page;
        return filteredProjects;
      } catch (error) {
        console.error('Error fetching projects for tags:', error);
        return [];
      } finally {
        loadingRelatedProjects.value = false;
      }
    };

    // Load a specific page of related projects
    const loadRelatedProjectsPage = (page) => {
      if (selectedNode.value) {
        const reachableTags = findReachableTags(selectedNode.value.id);
        getProjectsForTags(reachableTags, page);
      }
    };

    // Update related projects when node is selected
    const updateRelatedProjects = async (node) => {
      if (!node) {
        relatedProjects.value = [];
        relatedProjectsTotal.value = 0;
        relatedProjectsTotalPages.value = 1;
        return;
      }

      const reachableTags = findReachableTags(node.id);
      await getProjectsForTags(reachableTags, 1); // Start with page 1
    };

    // Helper function to get total vulnerability count
    const getTotalVulnerabilities = (metrics) => {
      if (!metrics) return 0;
      return (metrics.critical || 0) + (metrics.high || 0) + (metrics.medium || 0) + (metrics.low || 0);
    };

    // Zoom control functions
    const zoomIn = () => {
      if (cytoscapeInstance.value) {
        cytoscapeInstance.value.animate({
          zoom: cytoscapeInstance.value.zoom() * 1.2
        }, {
          duration: 200
        });
      }
    };

    const zoomOut = () => {
      if (cytoscapeInstance.value) {
        cytoscapeInstance.value.animate({
          zoom: cytoscapeInstance.value.zoom() / 1.2
        }, {
          duration: 200
        });
      }
    };

    const resetZoom = () => {
      if (cytoscapeInstance.value) {
        cytoscapeInstance.value.animate({
          fit: {
            padding: 50
          }
        }, {
          duration: 300
        });
      }
    };

    // Lifecycle
    onMounted(() => {
      loadData();

      // Add resize observer to handle container resizing
      if (cytoscapeContainer.value) {
        const resizeObserver = new ResizeObserver(() => {
          if (cytoscapeInstance.value) {
            cytoscapeInstance.value.resize();
          }
        });
        resizeObserver.observe(cytoscapeContainer.value);
      }
    });

    // Watch for data changes
    watch([graphData, layoutAlgorithm, nodeSpacing], () => {
      if (graphData.value) {
        nextTick(() => {
          renderCytoscapeGraph();
        });
      }
    });

    // Watch for mode changes to rebuild graph
    watch(associativeMode, () => {
      if (taxonomiesData.value) {
        rebuildGraph();
      }
    });

    return {
      // Reactive data
      graphData,
      selectedTaxonomy,
      associativeMode,
      loading,
      error,
      taxonomiesData,
      layoutAlgorithm,
      nodeSpacing,
      selectedNode,
      cytoscapeContainer,
      taxonomyColors,
      modeDescription,
      taxonomyNodes,
      relatedProjects,
      relatedProjectsPage,
      relatedProjectsTotal,
      relatedProjectsTotalPages,
      pageSize,
      loadingRelatedProjects,
      viewMode,

      // Methods
      loadData,
      getTaxonomyDisplayName,
      getNodeConnections,
      findReachableTags,
      getProjectsForTags,
      loadRelatedProjectsPage,
      updateRelatedProjects,
      buildDTProjectUrl,
      getTotalVulnerabilities,
      zoomIn,
      zoomOut,
      resetZoom
    };
  }
};
</script>
