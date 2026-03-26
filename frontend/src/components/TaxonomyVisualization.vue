<template>
  <div class="p-6 max-w-7xl mx-auto">
    <!-- Header -->
    <div class="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-4 mb-6">
      <h1 class="text-2xl font-bold text-gray-800 dark:text-white mb-4">Tag graph</h1>

      <!-- Controls -->
      <div class="flex items-center space-x-6">
        <!-- Taxonomy Selector -->
        <div class="flex items-center space-x-2">
          <label class="text-sm font-medium text-gray-700 dark:text-gray-300">Root Taxonomy:</label>
          <select
            v-model="selectedTaxonomy"
            @change="updateTree"
            class="px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
            v-if="!loading"
          >
            <option v-for="taxonomy in taxonomiesData" :key="taxonomy.id" :value="taxonomy.id">
              {{ taxonomy.name || taxonomy.id }}
            </option>
          </select>
        </div>

        <!-- Associative Mode Toggle -->
        <div class="flex items-center space-x-2">
          <label class="text-sm font-medium text-gray-700 dark:text-gray-300">Mode:</label>
          <div class="flex items-center space-x-2">
            <input
              type="radio"
              id="normal-mode"
              v-model="associativeMode"
              :value="false"
              @change="updateVisualization"
              class="text-blue-600 focus:ring-blue-500"
            >
            <label for="normal-mode" class="text-sm text-gray-700 dark:text-gray-300">Normal</label>

            <input
              type="radio"
              id="associative-mode"
              v-model="associativeMode"
              :value="true"
              @change="updateVisualization"
              class="text-blue-600 focus:ring-blue-500"
            >
            <label for="associative-mode" class="text-sm text-gray-700 dark:text-gray-300">Associative</label>
          </div>
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

    <!-- Main Content -->
    <div v-if="!loading && !error">
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <!-- Tree Structure -->
        <div class="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-4">
          <h2 class="text-xl font-semibold mb-4 text-gray-900 dark:text-white">Tree Structure</h2>
          <div class="bg-gray-50 dark:bg-gray-700 rounded p-4 overflow-auto max-h-96">
            <!-- Visual Tree -->
            <div class="tree-visualization">
              <SimpleTreeNode v-for="node in treeData" :key="node.id" :node="node" @node-selected="selectNode" />
            </div>
          </div>
        </div>

        <!-- Projects Section -->
        <div class="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-4">
          <h2 class="text-xl font-semibold mb-4 text-gray-900 dark:text-white">
            Projects
            <span v-if="selectedNode" class="text-sm text-gray-500 dark:text-gray-400 ml-2">
              for {{ selectedNode.name }}
            </span>
          </h2>
          <div class="bg-gray-50 dark:bg-gray-700 rounded p-4 overflow-auto max-h-96">
            <div v-if="!selectedNode" class="text-center py-8 text-gray-500 dark:text-gray-400">
              <p>Select a node from the tree to view projects</p>
            </div>
            <div v-else-if="loadingProjects" class="text-center py-8">
              <div class="inline-block animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600"></div>
              <p class="mt-2 text-gray-600 dark:text-gray-400">Loading projects...</p>
            </div>
            <div v-else-if="nodeProjects.length === 0" class="text-center py-8 text-gray-500 dark:text-gray-400">
              <p>No projects found for this node</p>
            </div>
            <div v-else class="space-y-2">
              <div
                v-for="project in nodeProjects"
                :key="project.uuid"
                class="p-3 border border-gray-200 dark:border-gray-600 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-600"
              >
                <h4 class="text-sm font-medium text-gray-900 dark:text-white">{{ project.name }}</h4>
                <p class="text-xs text-gray-500 dark:text-gray-400">
                  {{ project.tags?.join(', ') || 'No tags' }}
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Debug Zone -->
      <div class="mt-6 border-2 border-dashed border-gray-300 dark:border-gray-600 rounded-lg">
        <div class="flex items-center justify-between p-4 cursor-pointer hover:bg-gray-50 dark:hover:bg-gray-700" @click="toggleDebugZone">
          <h3 class="text-lg font-semibold text-gray-700 dark:text-gray-300">🔍 Debug Zone</h3>
          <div class="flex items-center space-x-2">
            <span class="text-sm text-gray-500 dark:text-gray-400">
              {{ debugZoneCollapsed ? '▶ Expand' : '▼ Collapse' }}
            </span>
          </div>
        </div>

        <div v-show="!debugZoneCollapsed" class="p-4 border-t border-gray-300 dark:border-gray-600">
          <div class="flex items-center justify-between mb-4">
            <div class="flex space-x-2">
              <button
                @click="exportGraphData"
                class="px-3 py-1 text-sm bg-blue-600 text-white rounded hover:bg-blue-700"
              >
                📋 Export Graph Data
              </button>
              <button
                @click="validateGraphStructure"
                class="px-3 py-1 text-sm bg-green-600 text-white rounded hover:bg-green-700"
              >
                ✅ Validate Structure
              </button>
              <button
                @click="generateRandomTestGraph"
                class="px-3 py-1 text-sm bg-purple-600 text-white rounded hover:bg-purple-700"
              >
                🎲 Random Test
              </button>
              <button
                @click="toggleCytoscapeView"
                class="px-3 py-1 text-sm bg-indigo-600 text-white rounded hover:bg-indigo-700"
              >
                🌐 {{ showCytoscapeView ? 'Hide' : 'Show' }} Cytoscape
              </button>
            </div>
          </div>
        </div>

        <!-- Graph Data Display -->
        <div class="space-y-4">
          <!-- Cytoscape Graph Display -->
          <div v-if="showCytoscapeView" class="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-4">
            <h4 class="text-md font-semibold text-gray-700 dark:text-gray-300 mb-2">🌐 Cytoscape Graph</h4>
            <div class="mb-4">
              <div class="flex items-center space-x-4 mb-2">
                <label class="text-sm font-medium text-gray-700 dark:text-gray-300">Graph Algorithm:</label>
                <select v-model="cytoscapeAlgorithm" class="px-2 py-1 border border-gray-300 dark:border-gray-600 rounded">
                  <option value="breadthfirst">Breadth-First</option>
                  <option value="depthfirst">Depth-First</option>
                  <option value="cose">CoSE (Cost-Optimized)</option>
                  <option value="circle">Circular</option>
                  <option value="grid">Grid</option>
                  <option value="concentric">Concentric</option>
                </select>
              </div>
              <div class="flex items-center space-x-4 mb-2">
                <label class="text-sm font-medium text-gray-700 dark:text-gray-300">Node Spacing:</label>
                <input
                  v-model.number="cytoscapeNodeSpacing"
                  type="range"
                  min="50"
                  max="200"
                  step="10"
                  class="w-32 px-2 py-1 border border-gray-300 dark:border-gray-600 rounded"
                />
                <span class="text-sm text-gray-600 dark:text-gray-400">{{ cytoscapeNodeSpacing }}px</span>
              </div>
            </div>
            <div ref="cytoscapeContainer" class="w-full h-96 border border-gray-300 dark:border-gray-600 rounded bg-gray-50 dark:bg-gray-700"></div>
          </div>

          <div class="grid grid-cols-1 lg:grid-cols-2 gap-4">
            <!-- Graph Statistics -->
            <div class="bg-gray-50 dark:bg-gray-700 rounded p-4">
              <h4 class="text-md font-semibold text-gray-700 dark:text-gray-300 mb-2">📊 Graph Statistics</h4>
              <div class="grid grid-cols-2 md:grid-cols-4 gap-2 text-sm">
                <div class="text-center">
                  <div class="text-2xl font-bold text-blue-600 dark:text-blue-400">{{ graphData?.nodes.length || 0 }}</div>
                  <div class="text-gray-600 dark:text-gray-400">Total Nodes</div>
                </div>
                <div class="text-center">
                  <div class="text-2xl font-bold text-green-600 dark:text-green-400">{{ graphData?.edges.length || 0 }}</div>
                  <div class="text-gray-600 dark:text-gray-400">Total Edges</div>
                </div>
                <div class="text-center">
                  <div class="text-2xl font-bold text-purple-600 dark:text-purple-400">{{ treeData?.length || 0 }}</div>
                  <div class="text-gray-600 dark:text-gray-400">Tree Nodes</div>
                </div>
                <div class="text-center">
                  <div class="text-2xl font-bold text-orange-600 dark:text-orange-400">{{ totalTreeNodes }}</div>
                  <div class="text-gray-600 dark:text-gray-400">Total Tree Nodes</div>
                </div>
              </div>
            </div>

            <!-- Graph Structure Analysis -->
            <div class="bg-gray-50 dark:bg-gray-700 rounded p-4">
              <h4 class="text-md font-semibold text-gray-700 dark:text-gray-300 mb-2">🔬 Graph Structure Analysis</h4>
              <div class="space-y-2 text-sm">
                <div v-if="graphStructureAnalysis">
                  <div class="font-mono bg-gray-100 dark:bg-gray-800 p-2 rounded">
                    <strong>Nodes:</strong> {{ graphStructureAnalysis.nodes }}
                  </div>
                  <div class="font-mono bg-gray-100 dark:bg-gray-800 p-2 rounded">
                    <strong>Edges:</strong> {{ graphStructureAnalysis.edges }}
                  </div>
                  <div class="font-mono bg-gray-100 dark:bg-gray-800 p-2 rounded">
                    <strong>Cycles:</strong> {{ graphStructureAnalysis.cycles }}
                  </div>
                  <div class="font-mono bg-gray-100 dark:bg-gray-800 p-2 rounded">
                    <strong>Orphans:</strong> {{ graphStructureAnalysis.orphans }}
                  </div>
                </div>
                <button
                  @click="analyzeGraphStructure"
                  class="mt-2 px-3 py-1 text-sm bg-indigo-600 text-white rounded hover:bg-indigo-700"
                >
                  🔬 Analyze Structure
                </button>
              </div>
            </div>
          </div>
        </div>
        </div>
      </div>

      <div v-if="showJsonView" class="mb-6">
        <h4 class="text-md font-medium text-gray-900 dark:text-white mb-3">Tree Structure (JSON)</h4>
        <div class="bg-gray-50 dark:bg-gray-700 rounded p-4 overflow-auto max-h-96">
          <pre class="text-xs text-gray-800 dark:text-gray-200">{{ JSON.stringify(treeData, null, 2) }}</pre>
        </div>
      </div>

      <div v-if="showGraphView">
        <h4 class="text-md font-medium text-gray-900 dark:text-white mb-3">Graph Visualization</h4>
        <div class="flex items-center justify-between mb-3">
          <div class="flex items-center space-x-2">
            <label class="text-sm font-medium text-gray-700 dark:text-gray-300">Layout:</label>
            <select
              v-model="selectedLayout"
              @change="updateGraphLayout"
              class="px-2 py-1 text-sm border border-gray-300 dark:border-gray-600 rounded focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
            >
              <option value="circle">Circle</option>
              <option value="grid">Grid</option>
              <option value="breadthfirst">Breadth First</option>
              <option value="concentric">Concentric</option>
              <option value="cose">CoSE</option>
              <option value="random">Random</option>
            </select>
          </div>
        </div>
        <div class="bg-gray-50 dark:bg-gray-700 rounded p-4 overflow-auto max-h-96">
          <div ref="mainGraphContainer" class="w-full h-96"></div>
        </div>
      </div>

      <!-- Graph Statistics -->
      <div class="mt-6 bg-white dark:bg-gray-800 rounded-lg shadow-lg p-4">
        <h2 class="text-xl font-semibold mb-4 text-gray-900 dark:text-white">Graph Statistics</h2>
        <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div class="text-center">
            <div class="text-2xl font-bold text-blue-600">{{ graphData?.nodes.length || 0 }}</div>
            <div class="text-sm text-gray-600 dark:text-gray-400">Total Nodes</div>
          </div>
          <div class="text-center">
            <div class="text-2xl font-bold text-green-600 dark:text-green-400">{{ graphData?.edges.length || 0 }}</div>
            <div class="text-sm text-gray-600 dark:text-gray-400">Total Edges</div>
          </div>
          <div class="text-center">
            <div class="text-2xl font-bold text-purple-600 dark:text-purple-400">{{ treeData?.length || 0 }}</div>
            <div class="text-sm text-gray-600 dark:text-gray-400">Root Nodes</div>
          </div>
          <div class="text-center">
            <div class="text-2xl font-bold text-orange-600 dark:text-orange-400">{{ totalTreeNodes }}</div>
            <div class="text-sm text-gray-600 dark:text-gray-400">Total Tree Nodes</div>
          </div>
        </div>
      </div>

      <!-- Legend -->
      <div class="mt-6 bg-white dark:bg-gray-800 rounded-lg shadow-lg p-4">
        <h2 class="text-xl font-semibold mb-4 text-gray-900 dark:text-white">Legend</h2>
        <div class="flex flex-wrap gap-4">
          <div class="flex items-center">
            <div class="w-4 h-4 rounded-full bg-red-400 dark:bg-red-500 mr-2"></div>
            <span class="text-sm text-gray-700 dark:text-gray-300">Customer</span>
          </div>
          <div class="flex items-center">
            <div class="w-4 h-4 rounded-full bg-teal-400 dark:bg-teal-500 mr-2"></div>
            <span class="text-sm text-gray-700 dark:text-gray-300">Environment</span>
          </div>
          <div class="flex items-center">
            <div class="w-4 h-4 rounded-full bg-blue-400 dark:bg-blue-500 mr-2"></div>
            <span class="text-sm text-gray-700 dark:text-gray-300">Deployment</span>
          </div>
          <div class="flex items-center">
            <div class="w-4 h-4 rounded-full bg-green-400 dark:bg-green-500 mr-2"></div>
            <span class="text-sm text-gray-700 dark:text-gray-300">Product Version</span>
          </div>
        </div>
      </div>
    </div>
</template>

<script>
import { ref, computed, onMounted, nextTick, watch } from 'vue';
import SimpleTaxonomyGraphBuilder from '../utils/simpleTaxonomyGraphBuilder.js';
import SimpleTreeNode from './SimpleTreeNode.vue';
import axios from 'axios';
import cytoscape from 'cytoscape';

export default {
  name: 'TaxonomyVisualization',
  components: {
    SimpleTreeNode
  },
  setup() {
    // Reactive variables
    const treeData = ref(null);
    const graphData = ref(null);
    const selectedTaxonomy = ref('customer');
    const associativeMode = ref(false);
    const loading = ref(true);
    const error = ref(null);
    const taxonomiesData = ref([]);

    // Enhanced debugging variables
    const showCytoscapeView = ref(false);
    const cytoscapeAlgorithm = ref('breadthfirst');
    const cytoscapeNodeSpacing = ref(100);
    const graphStructureAnalysis = ref({ nodes: [], edges: [], cycles: 0, orphans: 0 });
    const debugMode = ref(false);
    const debugZoneCollapsed = ref(true); // Debug Zone collapsed by default

    // Missing reactive variables
    const showJsonView = ref(false);
    const showGraphView = ref(false);
    const selectedLayout = ref('breadthfirst');

    // Node selection and projects
    const selectedNode = ref(null);
    const nodeProjects = ref([]);
    const loadingProjects = ref(false);
    const cytoscapeContainer = ref(null);
    const mainGraphContainer = ref(null);

    const graphBuilder = new SimpleTaxonomyGraphBuilder();
    const cytoscapeInstance = ref(null);
    const mainCytoscapeInstance = ref(null);

    // Computed properties
    const totalTreeNodes = computed(() => {
      const countAllChildren = (node) => {
        if (!node.children || node.children.length === 0) return 1;
        return 1 + node.children.reduce((sum, child) => sum + countAllChildren(child), 0);
      };
      return treeData.value?.reduce((total, node) => total + countAllChildren(node), 0) || 0;
    });

    const modeDescription = computed(() => {
      if (associativeMode.value) {
        return 'Associative mode links child nodes to parent nodes, creating hierarchical relationships. Each node can have multiple parents, allowing for complex organizational structures like security taxonomies with overlapping classifications.';
      } else {
        return 'Normal mode creates simple parent-child relationships where each node has exactly one parent (except the root), forming a traditional tree structure.';
      }
    });

    // Methods
    const loadData = async () => {
      try {
        loading.value = true;
        error.value = null;

        console.log('🔍 Starting data load...');

        const [tagsResponse, taxonomiesResponse] = await Promise.all([
          axios.get('/api/tags'),
          axios.get('/api/taxonomies')
        ]);

        console.log('📊 API Responses:');
        console.log('Tags response:', tagsResponse.data);
        console.log('Taxonomies response:', taxonomiesResponse.data);

        if (!tagsResponse.data || !taxonomiesResponse.data) {
          throw new Error('Failed to fetch data');
        }

        const tags = tagsResponse.data;
        const taxonomies = taxonomiesResponse.data;

        console.log('📋 Processed data:');
        console.log('Tags count:', Array.isArray(tags) ? tags.length : (tags.data ? tags.data.length : 0));
        console.log('Taxonomies count:', taxonomies.length);
        console.log('Tags sample:', Array.isArray(tags) ? tags.slice(0, 3) : (tags.data ? tags.data.slice(0, 3) : []));
        console.log('Taxonomies sample:', taxonomies.slice(0, 2));

        // Store taxonomies data for dynamic descriptions
        taxonomiesData.value = taxonomies;

        // Build graph with current mode
        console.log('🔧 Building graph...');
        const graph = graphBuilder.buildGraph(tags.data || tags, taxonomiesData.value || taxonomies, associativeMode.value);
        graphData.value = graph;

        console.log('📈 Graph built:');
        console.log('Graph nodes:', graph.nodes);
        console.log('Graph edges:', graph.edges);

        // Build tree
        console.log('🌳 Building tree...');
        const tree = graphBuilder.graphToTree(selectedTaxonomy.value);
        treeData.value = tree;
        console.log('Tree built:', tree);

      } catch (err) {
        console.error('❌ Error loading data:', err);
        error.value = err.response?.data?.detail || err.message;

        if (err.response?.status === 403) {
          error.value = 'Authentication required. Please log in first.';
        }
      } finally {
        loading.value = false;
      }
    };

    const updateTree = () => {
      if (graphData.value) {
        const tree = graphBuilder.graphToTree(selectedTaxonomy.value);
        treeData.value = tree;
      }
    };

    const updateVisualization = () => {
      // Rebuild the entire visualization when mode changes
      loadData();
    };

    const toggleJsonView = () => {
      showJsonView.value = !showJsonView.value;
    };

    const toggleGraphView = () => {
      showGraphView.value = !showGraphView.value;
    };

    const updateGraphLayout = () => {
      if (graphData.value && showGraphView.value) {
        // Rebuild main Cytoscape graph
        nextTick(() => {
          renderMainCytoscapeGraph();
        });
      }
    };

    const renderMainCytoscapeGraph = () => {
      if (!graphData.value || !mainGraphContainer.value) return;

      // Destroy existing instance
      if (mainCytoscapeInstance.value) {
        mainCytoscapeInstance.value.destroy();
      }

      // Convert graph data to Cytoscape format
      const nodes = Array.from(graphData.value.nodes.values()).map(node => ({
        data: {
          id: node.id,
          label: node.name,
          taxonomy: node.taxonomy,
          projectsCount: node.projectsCount || 0
        }
      }));

      const edges = graphData.value.edges.map(edge => ({
        data: {
          id: edge.id || `${edge.source}-${edge.target}`,
          source: edge.source,
          target: edge.target
        }
      }));

      console.log('🎨 Rendering main Cytoscape graph:', { nodes, edges });

      // Initialize main Cytoscape
      mainCytoscapeInstance.value = cytoscape({
        container: mainGraphContainer.value,
        elements: [...nodes, ...edges],
        style: [
          {
            selector: 'node',
            style: {
              'background-color': 'data(taxonomy)',
              'background-color': function(ele) {
                const taxonomyColors = {
                  'customer': '#ef4444',
                  'environment': '#14b8a6',
                  'deployment': '#3b82f6',
                  'product_version': '#22c55e'
                };
                return taxonomyColors[ele.data('taxonomy')] || '#6b7280';
              },
              'label': 'data(label)',
              'text-valign': 'center',
              'text-halign': 'center',
              'color': '#ffffff',
              'font-size': '14px',
              'width': '80px',
              'height': '80px'
            }
          },
          {
            selector: 'edge',
            style: {
              'width': 3,
              'line-color': '#9ca3af',
              'target-arrow-color': '#9ca3af',
              'target-arrow-shape': 'triangle',
              'curve-style': 'bezier'
            }
          }
        ],
        layout: {
          name: selectedLayout.value,
          nodeSpacing: 100,
          animate: true,
          animationDuration: 1000
        }
      });

      // Add event listeners
      mainCytoscapeInstance.value.on('tap', 'node', function(evt) {
        const node = evt.target;
        console.log('Main graph node clicked:', node.data());
        selectNode(node.data());
      });
    };

    const selectNode = async (node) => {
      selectedNode.value = node;
      await loadProjectsForNode(node);
    };

    const loadProjectsForNode = async (node) => {
      if (!node) return;

      loadingProjects.value = true;
      try {
        console.log('Loading projects for node:', node);

        // Get all projects first, then filter locally for more accurate results
        const response = await axios.get('/api/projects');
        const allProjects = response.data || [];

        // Get all descendant tags of this node (including the node itself)
        const getAllDescendantTags = (node) => {
          const tags = [node.name];

          if (node.children) {
            node.children.forEach(child => {
              tags.push(...getAllDescendantTags(child));
            });
          }

          return tags;
        };

        const descendantTags = getAllDescendantTags(node);
        console.log(`Looking for projects with any of these tags:`, descendantTags);

        // Filter projects that have any of the descendant tags
        nodeProjects.value = allProjects.filter(project => {
          if (!project.tags || project.tags.length === 0) return false;

          return project.tags.some(tag => {
            const tagName = typeof tag === 'string' ? tag : tag.name;
            return descendantTags.includes(tagName);
          });
        });

        console.log(`Found ${nodeProjects.value.length} projects for node "${node.name}" and its descendants`);
        console.log('Matching projects:', nodeProjects.value.map(p => ({ name: p.name, tags: p.tags })));
      } catch (error) {
        console.error('Error loading projects for node:', error);
        nodeProjects.value = [];
      } finally {
        loadingProjects.value = false;
      }
    };

    // Enhanced debugging methods
    const exportGraphData = () => {
      const data = {
        nodes: graphData.value?.nodes || [],
        edges: graphData.value?.edges || [],
        metadata: {
          taxonomy: selectedTaxonomy.value,
          mode: associativeMode.value ? 'associative' : 'normal',
          algorithm: cytoscapeAlgorithm.value,
          nodeSpacing: cytoscapeNodeSpacing.value,
          timestamp: new Date().toISOString(),
          structure: graphStructureAnalysis.value
        }
      }

      // Create download link
      const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `graph-data-${new Date().toISOString().split('T')[0]}.json`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);

      console.log('Graph data exported:', data);
    };

    const validateGraphStructure = () => {
      const analysis = {
        nodes: graphData.value?.nodes?.length || 0,
        edges: graphData.value?.edges?.length || 0,
        cycles: graphStructureAnalysis.value?.cycles || 0,
        orphans: graphStructureAnalysis.value?.orphans || 0,
        issues: []
      };

      // Check for common structural issues
      if (graphData.value?.nodes) {
        const nodeIds = new Set(graphData.value.nodes.map(n => n.id));
        const edgeNodes = new Set();

        graphData.value.edges.forEach((edge, index) => {
          // Check for duplicate edges
          if (graphData.value.edges.filter((e, i) => i !== index && e.source === edge.source && e.target === edge.target).length > 1) {
            analysis.issues.push(`Duplicate edge ${index + 1}: ${edge.source} -> ${edge.target}`);
          }

          // Check for self-loops
          if (edge.source === edge.target) {
            analysis.issues.push(`Self-loop at edge ${index}: ${edge.source}`);
          }

          // Check for missing nodes
          if (!nodeIds.has(edge.source) || !nodeIds.has(edge.target)) {
            analysis.issues.push(`Missing node in edge ${index}: ${edge.source} -> ${edge.target}`);
          }

          edgeNodes.add(edge.source);
          edgeNodes.add(edge.target);
        });

        // Check for orphaned nodes
        graphData.value.nodes.forEach((node, index) => {
          const hasIncomingEdges = graphData.value.edges.some(e => e.target === node.id);
          const hasOutgoingEdges = graphData.value.edges.some(e => e.source === node.id);

          if (!hasIncomingEdges && !hasOutgoingEdges && node.id !== selectedTaxonomy.value) {
            analysis.orphans++;
          }
        });
      }

      graphStructureAnalysis.value = analysis;
      console.log('Graph structure analysis:', analysis);

      return analysis.issues.length === 0;
    };

    const analyzeGraphStructure = () => {
      debugMode.value = !debugMode.value;
      console.log('Analyzing graph structure...');
    };

    const generateRandomTestGraph = () => {
      const testNodes = [];
      const testEdges = [];

      // Generate a complex test graph
      for (let i = 0; i < 10; i++) {
        const nodeId = `test-node-${i}`;
        testNodes.push({
          id: nodeId,
          name: `Test Node ${i}`,
          taxonomy: 'test',
          projectsCount: Math.floor(Math.random() * 5)
        });
      }

      // Create some test edges
      for (let i = 0; i < 15; i++) {
        const source = `test-node-${Math.floor(Math.random() * 10)}`;
        const target = `test-node-${Math.floor(Math.random() * 10)}`;
        testEdges.push({
          id: `test-edge-${i}`,
          source,
          target
        });
      }

      graphData.value = {
        nodes: testNodes,
        edges: testEdges
      };

      console.log('Generated random test graph with', testNodes.length, 'nodes and', testEdges.length, 'edges');
    };

    const toggleDebugZone = () => {
      debugZoneCollapsed.value = !debugZoneCollapsed.value;
    };

    const toggleCytoscapeView = () => {
      showCytoscapeView.value = !showCytoscapeView.value;

      // Initialize Cytoscape when showing
      if (showCytoscapeView.value && graphData.value) {
        nextTick(() => {
          renderCytoscapeGraph();
        });
      }
    };

    const renderCytoscapeGraph = () => {
      if (!graphData.value || !cytoscapeContainer.value) return;

      // Destroy existing instance
      if (cytoscapeInstance.value) {
        cytoscapeInstance.value.destroy();
      }

      // Convert graph data to Cytoscape format
      const nodes = Array.from(graphData.value.nodes.values()).map(node => ({
        data: {
          id: node.id,
          label: node.name,
          taxonomy: node.taxonomy,
          projectsCount: node.projectsCount || 0
        }
      }));

      const edges = graphData.value.edges.map(edge => ({
        data: {
          id: edge.id || `${edge.source}-${edge.target}`,
          source: edge.source,
          target: edge.target
        }
      }));

      console.log('🎨 Rendering Cytoscape graph:', { nodes, edges });

      // Initialize Cytoscape
      cytoscapeInstance.value = cytoscape({
        container: cytoscapeContainer.value,
        elements: [...nodes, ...edges],
        style: [
          {
            selector: 'node',
            style: {
              'background-color': 'data(taxonomy)',
              'background-color': function(ele) {
                const taxonomyColors = {
                  'customer': '#ef4444',
                  'environment': '#14b8a6',
                  'deployment': '#3b82f6',
                  'product_version': '#22c55e'
                };
                return taxonomyColors[ele.data('taxonomy')] || '#6b7280';
              },
              'label': 'data(label)',
              'text-valign': 'center',
              'text-halign': 'center',
              'color': '#ffffff',
              'font-size': '12px',
              'width': '60px',
              'height': '60px'
            }
          },
          {
            selector: 'edge',
            style: {
              'width': 2,
              'line-color': '#9ca3af',
              'target-arrow-color': '#9ca3af',
              'target-arrow-shape': 'triangle',
              'curve-style': 'bezier'
            }
          }
        ],
        layout: {
          name: cytoscapeAlgorithm.value,
          nodeSpacing: cytoscapeNodeSpacing.value,
          animate: true,
          animationDuration: 1000
        }
      });

      // Add event listeners
      cytoscapeInstance.value.on('tap', 'node', function(evt) {
        const node = evt.target;
        console.log('Node clicked:', node.data());
        selectNode(node.data());
      });
    };

    // Watch for graph data changes
    watch([graphData, showCytoscapeView, cytoscapeAlgorithm, cytoscapeNodeSpacing], () => {
      if (showCytoscapeView.value && graphData.value) {
        nextTick(() => {
          renderCytoscapeGraph();
        });
      }
    }, { deep: true });

    watch([graphData, showGraphView, selectedLayout], () => {
      if (showGraphView.value && graphData.value) {
        nextTick(() => {
          renderMainCytoscapeGraph();
        });
      }
    }, { deep: true });

    onMounted(() => {
      loadData();
    });

    return {
      // Component data
      treeData,
      graphData,
      selectedTaxonomy,
      associativeMode,
      loading,
      error,
      taxonomiesData,
      totalTreeNodes,
      showJsonView,
      showGraphView,
      selectedLayout,
      selectedNode,
      nodeProjects,
      loadingProjects,
      modeDescription,
      graphBuilder,
      cytoscapeContainer,
      cytoscapeInstance,
      mainGraphContainer,
      mainCytoscapeInstance,

      // Enhanced debugging variables
      showCytoscapeView,
      cytoscapeAlgorithm,
      cytoscapeNodeSpacing,
      graphStructureAnalysis,
      debugMode,
      debugZoneCollapsed,

      // Enhanced debugging methods
      exportGraphData,
      validateGraphStructure,
      analyzeGraphStructure,
      generateRandomTestGraph,
      toggleDebugZone,
      toggleCytoscapeView,

      // Existing methods
      updateTree,
      updateVisualization,
      toggleJsonView,
      toggleGraphView,
      updateGraphLayout,
      selectNode,
      loadProjectsForNode
    };
  }
};
</script>

<style scoped>
/* Tailwind CSS classes are used via CDN or build process */
</style>
