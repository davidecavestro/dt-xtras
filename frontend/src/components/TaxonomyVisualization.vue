<template>
  <div class="p-6 max-w-7xl mx-auto">
    <!-- Header -->
    <div class="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-4 mb-6">
      <h1 class="text-2xl font-bold text-gray-800 dark:text-white mb-4">Tags Graph</h1>

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
      <!-- Cytoscape Graph -->
      <div class="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-4">
        <h2 class="text-xl font-semibold mb-4 text-gray-900 dark:text-white">Graph Visualization</h2>
        <div ref="cytoscapeContainer" class="w-full h-96 lg:h-[600px] border border-gray-300 dark:border-gray-600 rounded bg-gray-50 dark:bg-gray-700 resize overflow-hidden"></div>
      </div>

      <!-- Graph Controls -->
      <div class="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-4 mb-6 mt-6">
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

      <!-- Legend -->
      <div class="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-4 mt-6">
        <h2 class="text-xl font-semibold mb-4 text-gray-900 dark:text-white">Legend</h2>
        <div class="flex flex-wrap gap-4">
          <div v-for="(color, taxonomy) in taxonomyColors" :key="taxonomy" class="flex items-center">
            <div class="w-4 h-4 rounded-full mr-2" :style="{ backgroundColor: color }"></div>
            <span class="text-sm text-gray-700 dark:text-gray-300">{{ getTaxonomyDisplayName(taxonomy) }}</span>
          </div>
        </div>
      </div>

      <!-- Selected Node Details -->
      <div v-if="selectedNode" class="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-4 mt-6">
        <h2 class="text-xl font-semibold mb-4 text-gray-900 dark:text-white">Selected Node</h2>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <h3 class="text-sm font-medium text-gray-700 dark:text-gray-300">Node Details</h3>
            <div class="mt-2 space-y-1 text-sm">
              <div><strong>ID:</strong> {{ selectedNode.id }}</div>
              <div><strong>Name:</strong> {{ selectedNode.label }}</div>
              <div><strong>Taxonomy:</strong> {{ getTaxonomyDisplayName(selectedNode.taxonomy) }}</div>
              <div><strong>Projects:</strong> {{ selectedNode.projectsCount || 0 }}</div>
            </div>
          </div>
          <div>
            <h3 class="text-sm font-medium text-gray-700 dark:text-gray-300">Connections</h3>
            <div class="mt-2 space-y-1 text-sm">
              <div><strong>Incoming:</strong> {{ getNodeConnections(selectedNode.id, 'target').length }}</div>
              <div><strong>Outgoing:</strong> {{ getNodeConnections(selectedNode.id, 'source').length }}</div>
              <div><strong>Total:</strong> {{ getNodeConnections(selectedNode.id, 'source').length + getNodeConnections(selectedNode.id, 'target').length }}</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted, nextTick, watch } from 'vue';
import SimpleTaxonomyGraphBuilder from '../utils/simpleTaxonomyGraphBuilder.js';
import axios from 'axios';
import cytoscape from 'cytoscape';
import dagre from 'cytoscape-dagre';

// Register dagre extension
cytoscape.use(dagre);

export default {
  name: 'TaxonomyVisualization',
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
        return 'Associative mode creates direct connections between related taxonomies, hiding intermediate connector nodes. Each connection represents a semantic relationship between taxonomy elements.';
      } else {
        return 'Normal mode creates hierarchical relationships where child nodes connect to parent nodes through defined taxonomy relations.';
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

        const tags = tagsResponse.data;
        const taxonomies = taxonomiesResponse.data;

        if (!tags || !taxonomies) {
          throw new Error('Failed to fetch data');
        }

        // Store taxonomies data filtering associative taxonomies for graph building, but keep all for colors
        allTaxonomiesData.value = taxonomies; // Store all taxonomies for color mapping
        taxonomiesData.value = associativeMode.value ? taxonomies.filter(taxonomy => taxonomy.relations !== undefined) : taxonomies;

        // Build graph with current mode
        const graph = graphBuilder.buildGraph(tags.data || tags, taxonomiesData.value, selectedTaxonomy.value, associativeMode.value);
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
        const tags = tagsResponse.data;

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
              'font-size': '12px',
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
        console.log('Edge clicked:', edge.data());
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

      // Methods
      loadData,
      updateVisualization,
      rebuildGraph,
      updateGraphLayout,
      selectNode,
      getTaxonomyDisplayName,
      getNodeConnections
    };
  }
};
</script>
