<template>
  <div class="p-6 max-w-7xl mx-auto">
    <!-- Header -->
    <div class="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-4 mb-6">
      <h1 class="text-2xl font-bold text-gray-800 dark:text-white mb-4">Taxonomy Visualization</h1>

      <!-- Controls -->
      <div class="flex items-center space-x-6">
        <!-- Taxonomy Selector -->
        <div class="flex items-center space-x-2">
          <label class="text-sm font-medium text-gray-700 dark:text-gray-300">Root Taxonomy:</label>
          <select
            v-model="selectedTaxonomy"
            @change="updateTree"
            class="px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
          >
            <option value="customer">Customer</option>
            <option value="env">Environment</option>
            <option value="deploy">Deployment</option>
            <option value="product_version">Product Version</option>
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
      <div class="mt-3 text-sm text-gray-600 dark:text-gray-400">
        <span v-if="associativeMode" class="text-purple-600 font-medium">
          📊 Associative Mode: Deployment tags hidden, showing direct component relationships (env ↔ customer ↔ product)
        </span>
        <span v-else class="text-blue-600 font-medium">
          🌳 Normal Mode: Full tree structure with deployment tags as connectors
        </span>
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
      <div class="mt-6 border-2 border-dashed border-gray-300 dark:border-gray-600 rounded-lg p-4">
        <div class="flex items-center justify-between mb-4">
          <h3 class="text-lg font-semibold text-gray-700 dark:text-gray-300">🔍 Debug Zone</h3>
          <div class="flex space-x-2">
            <button
              @click="toggleJsonView"
              class="px-3 py-1 text-sm bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded hover:bg-gray-300 dark:hover:bg-gray-600"
            >
              {{ showJsonView ? 'Hide' : 'Show' }} JSON
            </button>
            <button
              @click="toggleGraphView"
              class="px-3 py-1 text-sm bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded hover:bg-gray-300 dark:hover:bg-gray-600"
            >
              {{ showGraphView ? 'Hide' : 'Show' }} Graph
            </button>
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
          <div class="bg-gray-50 dark:bg-gray-700 rounded p-4 overflow-auto max-h-96 flex justify-center">
            <div v-html="svgGraph"></div>
          </div>
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
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue';
import SimpleTaxonomyGraphBuilder from '../utils/simpleTaxonomyGraphBuilder.js';
import SimpleTreeNode from './SimpleTreeNode.vue';
import axios from 'axios';

export default {
  name: 'TaxonomyVisualization',
  components: {
    SimpleTreeNode
  },
  setup() {
    const treeData = ref(null);
    const graphData = ref(null);
    const svgGraph = ref('');
    const selectedTaxonomy = ref('customer');
    const associativeMode = ref(false);
    const loading = ref(true);
    const error = ref(null);

    // New reactive variables for collapsible sections and layout
    const showJsonView = ref(false); // Collapsed by default
    const showGraphView = ref(false); // Collapsed by default
    const selectedLayout = ref('breadthfirst'); // Changed to breadth-first by default

    // Node selection and projects
    const selectedNode = ref(null);
    const nodeProjects = ref([]);
    const loadingProjects = ref(false);

    const graphBuilder = new SimpleTaxonomyGraphBuilder();

    const totalTreeNodes = computed(() => {
      const countAllChildren = (node) => {
        if (!node.children || node.children.length === 0) return 1;
        return 1 + node.children.reduce((sum, child) => sum + countAllChildren(child), 0);
      };

      return treeData.value.reduce((total, node) => total + countAllChildren(node), 0);
    });

    const loadData = async () => {
      try {
        loading.value = true;
        error.value = null;

        const [tagsResponse, taxonomiesResponse] = await Promise.all([
          axios.get('/api/tags'),
          axios.get('/api/taxonomies')
        ]);

        if (!tagsResponse.data || !taxonomiesResponse.data) {
          throw new Error('Failed to fetch data');
        }

        const tags = tagsResponse.data;
        const taxonomies = taxonomiesResponse.data;

        // Build graph with current mode
        const graph = graphBuilder.buildGraph(tags.data || tags, taxonomies.data || taxonomies, associativeMode.value);
        graphData.value = graph;
        svgGraph.value = graphBuilder.generateSVG(selectedLayout.value);

        // Build tree
        const tree = graphBuilder.graphToTree(selectedTaxonomy.value);
        treeData.value = tree;

      } catch (err) {
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
      if (graphData.value) {
        // Rebuild graph with new layout
        svgGraph.value = graphBuilder.generateSVG(selectedLayout.value);
      }
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

    onMounted(() => {
      loadData();
    });

    return {
      treeData,
      graphData,
      svgGraph,
      selectedTaxonomy,
      associativeMode,
      loading,
      error,
      totalTreeNodes,
      showJsonView,
      showGraphView,
      selectedLayout,
      selectedNode,
      nodeProjects,
      loadingProjects,
      updateTree,
      updateVisualization,
      toggleJsonView,
      toggleGraphView,
      updateGraphLayout,
      selectNode
    };
  }
};
</script>

<style scoped>
/* Tailwind CSS classes are used via CDN or build process */
</style>
