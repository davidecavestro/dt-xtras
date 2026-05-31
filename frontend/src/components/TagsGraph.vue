<template>
  <div class="px-4 sm:px-0">
    <!-- Header -->
    <div class="bg-white dark:bg-gray-800 rounded-lg shadow p-4 mb-6">
      <div class="flex justify-between items-center">
        <h1 class="text-2xl font-bold text-gray-900 dark:text-white">Tags Graph</h1>

      </div>

      <!-- Controls -->
      <div class="flex items-center space-x-6 mt-4">
        <!-- Hierarchical Mode Toggle -->
        <div class="flex items-center space-x-2">
          <label class="text-sm font-medium text-gray-700 dark:text-gray-300">Mode:</label>
          <div class="flex items-center space-x-2">
            <input
              type="radio"
              id="hierarchical-mode"
              v-model="hierarchicalMode"
              :value="true"
              @change="updateVisualization"
              class="text-blue-600 focus:ring-blue-500"
            >
            <label for="hierarchical-mode" class="text-sm text-gray-700 dark:text-gray-300">Hierarchical</label>

            <input
              type="radio"
              id="normal-mode"
              v-model="hierarchicalMode"
              :value="false"
              @change="updateVisualization"
              class="text-blue-600 focus:ring-blue-500"
              >
              <label for="normal-mode" class="text-sm text-gray-700 dark:text-gray-300">Raw</label>
          </div>
        </div>

        <!-- Root Taxonomy Selector (hierarchical mode only) -->
        <!-- Only lists taxonomies that appear as tree roots, so every choice
             yields a non-empty tree. "All" clears the filter. -->
        <div v-if="hierarchicalMode && rootTaxonomyOptions.length" class="flex items-center space-x-2">
          <label for="root-taxonomy" class="text-sm font-medium text-gray-700 dark:text-gray-300">Root:</label>
          <select
            id="root-taxonomy"
            v-model="selectedTaxonomy"
            @change="updateVisualization"
            :disabled="loading"
            class="px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
          >
            <option :value="null">All</option>
            <option v-for="taxonomy in rootTaxonomyOptions" :key="taxonomy.id" :value="taxonomy.id">
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
        <!-- min-w-0 lets this flex item shrink back to its share; without it an
             oversized cytoscape canvas keeps the item wide on restore, pushing
             the list out and adding scrollbars. -->
        <div class="flex-1 min-w-0">
          <!-- Collapsible Graph Controls -->
          <div class="bg-white dark:bg-gray-800 rounded-lg shadow mb-4">
            <button
              @click="controlsCollapsed = !controlsCollapsed"
              class="w-full px-4 py-2 flex items-center justify-between text-left hover:bg-gray-50 dark:hover:bg-gray-700 rounded-lg transition-colors"
            >
              <span class="text-sm font-semibold text-gray-900 dark:text-white">Graph Controls</span>
              <svg
                class="w-4 h-4 text-gray-500 dark:text-gray-400 transform transition-transform"
                :class="{ 'rotate-180': !controlsCollapsed }"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
              </svg>
            </button>
            <div v-if="!controlsCollapsed" class="px-4 pb-4">
              <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                <!-- Layout Algorithm -->
                <div>
                  <label class="text-xs font-medium text-gray-700 dark:text-gray-300">Layout:</label>
                  <select
                    v-model="layoutAlgorithm"
                    @change="updateGraphLayout"
                    class="mt-1 block w-full px-2 py-1.5 text-sm border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                  >
                    <option value="dagre">Dagre</option>
                    <option value="breadthfirst">Breadth-First</option>
                    <option value="cose">CoSE</option>
                    <option value="circle">Circular</option>
                    <option value="grid">Grid</option>
                    <option value="concentric">Concentric</option>
                  </select>
                </div>

                <!-- Node Spacing -->
                <div>
                  <label class="text-xs font-medium text-gray-700 dark:text-gray-300">Spacing: {{ nodeSpacing }}px</label>
                  <input
                    v-model.number="nodeSpacing"
                    @change="updateGraphLayout"
                    type="range"
                    min="50"
                    max="200"
                    step="10"
                    class="mt-1 block w-full h-1.5"
                  />
                </div>
              </div>
            </div>
          </div>

          <!-- Cytoscape Graph -->
          <!-- "Expand" grows the graph in-flow inside the content area (which is
               already offset past the sidebar) and hides the side list, rather
               than using a viewport-fixed overlay - that would render behind the
               sidebar (trapped under the content's z-10 stacking context). -->
          <div class="relative bg-white dark:bg-gray-800 rounded-lg shadow p-3">
            <!-- Graph controls: zoom in/out, fit to view, expand/collapse -->
            <div class="absolute top-5 right-5 z-10 flex flex-col gap-1">
              <button
                @click="zoomIn"
                class="p-1.5 rounded-md bg-white/80 dark:bg-gray-700/80 border border-gray-300 dark:border-gray-600 text-gray-600 dark:text-gray-300 hover:bg-white dark:hover:bg-gray-700 shadow-sm cursor-pointer"
                title="Zoom in"
              >
                <ZoomIn class="w-4 h-4" />
              </button>
              <button
                @click="zoomOut"
                class="p-1.5 rounded-md bg-white/80 dark:bg-gray-700/80 border border-gray-300 dark:border-gray-600 text-gray-600 dark:text-gray-300 hover:bg-white dark:hover:bg-gray-700 shadow-sm cursor-pointer"
                title="Zoom out"
              >
                <ZoomOut class="w-4 h-4" />
              </button>
              <button
                @click="resetZoom"
                class="p-1.5 rounded-md bg-white/80 dark:bg-gray-700/80 border border-gray-300 dark:border-gray-600 text-gray-600 dark:text-gray-300 hover:bg-white dark:hover:bg-gray-700 shadow-sm cursor-pointer"
                title="Fit to view"
              >
                <Scan class="w-4 h-4" />
              </button>
              <button
                @click="toggleGraphExpand"
                class="p-1.5 rounded-md bg-white/80 dark:bg-gray-700/80 border border-gray-300 dark:border-gray-600 text-gray-600 dark:text-gray-300 hover:bg-white dark:hover:bg-gray-700 shadow-sm cursor-pointer"
                :title="graphExpanded ? 'Collapse graph' : 'Expand graph'"
              >
                <component :is="graphExpanded ? Minimize2 : Maximize2" class="w-4 h-4" />
              </button>
            </div>
            <div
              ref="cytoscapeContainer"
              :class="[
                'w-full border border-gray-300 dark:border-gray-600 rounded bg-gray-50 dark:bg-gray-700 overflow-hidden',
                graphExpanded ? 'h-[80vh]' : 'h-[60vh] min-h-96'
              ]"
            ></div>
          </div>
        </div>
        <!-- End Left: Graph Section -->

        <!-- Right: Related Projects Section (hidden while the graph is expanded) -->
        <div v-if="hierarchicalMode && !graphExpanded" class="lg:w-96">
          <div class="bg-white dark:bg-gray-800 rounded-lg shadow p-4">
            <h2 class="text-xl font-semibold mb-1 text-gray-900 dark:text-white">Related Projects</h2>

            <!-- Selected Node Info -->
            <div v-if="selectedNode" class="flex items-center gap-2 my-1">
              <span class="text-sm text-gray-600 dark:text-gray-400">Focusing on:</span>
              <span class="font-mono text-sm text-gray-900 dark:text-white">"{{ selectedNode.title || selectedNode.id }}"</span>
              <span
                class="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium border"
                  :style="getTaxonomyBadgeStyleForNode(selectedNode)"
              >
                  {{ getTaxonomyNameForNode(selectedNode) }}
              </span>
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

          <div class="space-y-2">
            <div
              v-for="project in relatedProjects"
              :key="project.uuid"
              class="p-3 bg-gray-50 dark:bg-gray-700 rounded hover:bg-gray-100 dark:hover:bg-gray-600 cursor-pointer border border-gray-200 dark:border-gray-600"
            >
              <div class="min-w-0">
                <div class="text-sm font-medium text-gray-900 dark:text-white truncate">{{ project.name }}</div>
                <!-- Metrics & Info Line -->
                <div class="flex flex-wrap items-center gap-1.5 mt-1">
                  <!-- Version -->
                  <span class="text-xs font-medium text-gray-600 dark:text-gray-400">{{ project.version || 'latest' }}</span>
                  <!-- Metrics Counters -->
                  <template v-if="project.metrics">
                    <span class="text-xs text-gray-400">|</span>
                    <span class="text-xs text-gray-500 dark:text-gray-400">
                      <span class="font-medium text-gray-900 dark:text-white">{{ project.metrics.vulnerableComponents || 0 }}</span>
                      /
                      <span class="font-medium text-gray-900 dark:text-white">{{ project.metrics.components || project.metrics.vulnerableComponents || 0 }}</span>
                      comp.
                    </span>
                    <span class="text-xs text-gray-400">|</span>
                    <span class="text-xs text-gray-500 dark:text-gray-400">
                      <span class="font-medium text-gray-900 dark:text-white">{{ getTotalVulnerabilities(project.metrics) }}</span>
                      vulns
                    </span>
                  </template>
                  <!-- Security Badges -->
                  <template v-if="project.metrics">
                    <span v-if="project.metrics.critical > 0" class="px-1.5 py-0.5 bg-red-100 dark:bg-red-900 text-red-800 dark:text-red-200 rounded text-xs font-medium">
                      {{ project.metrics.critical }} C
                    </span>
                    <span v-if="project.metrics.high > 0" class="px-1.5 py-0.5 bg-orange-100 dark:bg-orange-900 text-orange-800 dark:text-orange-200 rounded text-xs font-medium">
                      {{ project.metrics.high }} H
                    </span>
                    <span v-if="project.metrics.medium > 0" class="px-1.5 py-0.5 bg-yellow-100 dark:bg-yellow-900 text-yellow-800 dark:text-yellow-200 rounded text-xs font-medium">
                      {{ project.metrics.medium }} M
                    </span>
                    <span v-if="project.metrics.low > 0" class="px-1.5 py-0.5 bg-blue-100 dark:bg-blue-900 text-blue-800 dark:text-blue-200 rounded text-xs font-medium">
                      {{ project.metrics.low }} L
                    </span>
                    <span v-if="getTotalVulnerabilities(project.metrics) === 0" class="px-1.5 py-0.5 bg-green-100 dark:bg-green-900 text-green-800 dark:text-green-200 rounded text-xs font-medium">
                      No Vulns
                    </span>
                  </template>
                  <!-- Tags (at end since variable length) -->
                  <template v-if="project.tags && project.tags.length > 0">
                    <span class="text-xs text-gray-400">|</span>
                    <span
                      v-for="tag in project.tags.slice(0, 3)"
                      :key="tag.name"
                      class="inline-flex items-center px-1.5 py-0.5 rounded-full text-xs font-medium border truncate"
                      :class="getTagStyle(tag)"
                      :style="getTagDynamicStyle(tag)"
                    >
                      {{ tag.name }}
                    </span>
                    <span
                      v-if="project.tags.length > 3"
                      class="px-1.5 py-0.5 bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-400 text-xs rounded-full"
                    >
                      +{{ project.tags.length - 3 }}
                    </span>
                  </template>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div v-else class="text-sm text-gray-500 dark:text-gray-400">
          {{ selectedNode ? 'No projects found for this selection' : 'Select a node to see related projects' }}
        </div>
      </div>
      <!-- End Related Projects inner container -->
    </div>
    <!-- End Right: Related Projects Section -->
  </div>
  <!-- End Graph and Related Projects Container -->
</div>
</div>
</template>

<script>
import { ref, computed, onMounted, nextTick, watch } from 'vue';
import { storeToRefs } from 'pinia';
import { List, Grid3X3, Square, Maximize2, Minimize2, ZoomIn, ZoomOut, Scan } from 'lucide-vue-next';
import cytoscape from 'cytoscape';
import { buildDTProjectUrl } from '../config.js';
import dagre from 'cytoscape-dagre';
import { useTagStore } from '../stores/tags';
import { useTaxonomyStore } from '../stores/taxonomies';
import { useProjectStore } from '../stores/projects';
import { useGraphStore } from '../stores/graph';
import { createLogger } from '../utils/logger';
import { createJsRegExp } from '../utils/taxonomyParser';

// Register dagre extension
cytoscape.use(dagre);
const logger = createLogger('tags-graph')

export default {
  name: 'TagsGraph',
  components: {
    List,
    Grid3X3,
    Square,
    ZoomIn,
    ZoomOut,
    Scan
  },
  setup() {
    // Use stores
    const tagStore = useTagStore();
    const taxonomyStore = useTaxonomyStore();
    const projectStore = useProjectStore();

    // Store instances
    const graphStore = useGraphStore();

    // Store references
    const { tags, isLoading: tagsLoading, error: tagsError } = storeToRefs(tagStore);
    const { taxonomies, isLoading: taxonomiesLoading, error: taxonomiesError } = storeToRefs(taxonomyStore);
    const { projects, isLoading: projectsLoading } = storeToRefs(projectStore);

    // Reactive variables
    const graphData = ref(null);
    const loading = ref(true);
    const error = ref(null);
    const selectedTaxonomy = ref(null);
    // Taxonomy ids that actually appear as hierarchical-tree roots. These are the
    // only values that produce a non-empty tree when forced as root (the path
    // generators like `site` never appear as nodes). Captured from the unfiltered
    // load so the dropdown stays stable regardless of the current selection.
    const rootEligibleTaxonomyIds = ref([]);
    const rootTaxonomyOptions = computed(() =>
      rootEligibleTaxonomyIds.value
        .map(id => taxonomies.value.find(t => t.id === id))
        .filter(Boolean)
    );
    const hierarchicalMode = ref(true);
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
    const controlsCollapsed = ref(true); // Collapsed by default
    const graphExpanded = ref(false); // Fullscreen graph toggle

    // Toggle the graph between its inline size and the expanded (full content
    // width) size. resize()+fit() must run AFTER the browser has applied the new
    // layout, otherwise cytoscape keeps the previous zoom/size - so we wait a
    // frame past nextTick. fit() resets the zoom so restoring returns to the
    // original view instead of keeping the expanded zoom level.
    const toggleGraphExpand = () => {
      graphExpanded.value = !graphExpanded.value;
      nextTick(() => {
        requestAnimationFrame(() => {
          if (cytoscapeInstance.value) {
            cytoscapeInstance.value.resize();
            cytoscapeInstance.value.fit(undefined, 50);
          }
        });
      });
    };

    // Use graph store reactive references
    const { nodes, edges, treeData, loading: graphLoading, error: graphError } = storeToRefs(graphStore);

    // Taxonomy colors - now dynamic based on user choices
    const taxonomyColors = computed(() => {
      const colors = {};
      if (taxonomies.value) {
        taxonomies.value.forEach(taxonomy => {
          colors[taxonomy.id] = taxonomy.color || '#6b7280';
        });
      }
      return colors;
    });

    // Computed properties
    const modeDescription = computed(() => {
      if (hierarchicalMode.value) {
        return 'Hierarchical mode creates direct connections between related taxonomies, hiding intermediate connector nodes. Each connection represents a semantic relationship between taxonomy elements. This mode shows projects related to your selection in the Related Projects panel.';
      } else {
        return 'Raw mode creates relationships where nodes connect to others through defined taxonomy relations. This mode does not show related projects - use Hierarchical mode to see project relationships.';
      }
    });

    const taxonomyNodes = computed(() => {
      if (!graphData.value?.nodes) return {};
      const nodes = {};
      const nodeList = Array.isArray(graphData.value.nodes) ? graphData.value.nodes : [];
      nodeList.forEach(node => {
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

        // Load hierarchical tree or network graph based on mode
        if (hierarchicalMode.value) {
          // Hierarchical mode: use hierarchical tree endpoint
          await graphStore.loadHierarchicalTree({
            rootTaxonomy: selectedTaxonomy.value
          });
          logger.info('Hierarchical tree loaded:', treeData.value?.length, 'roots');
          // Capture the root-eligible taxonomies from the unfiltered tree.
          if (!selectedTaxonomy.value) {
            rootEligibleTaxonomyIds.value = [
              ...new Set((treeData.value || []).map(r => r.taxonomy).filter(Boolean))
            ];
          }
        } else {
          // Raw mode: use network graph endpoint
          await graphStore.loadTagGraph({
            rootTaxonomy: selectedTaxonomy.value,
            hierarchicalMode: false
          });
          logger.info('Network graph loaded:', nodes.value?.length, 'nodes,', edges.value?.length, 'edges');
        }

        if (hierarchicalMode.value) {
          // For hierarchical mode, convert tree to graph format for Cytoscape
          if (!treeData.value) {
            throw new Error('Failed to load hierarchical tree data');
          }
          graphData.value = convertTreeToGraph(treeData.value);
        } else {
          // For network mode, use nodes/edges directly
          if (!nodes.value || !edges.value) {
            throw new Error('Failed to load graph data');
          }
          graphData.value = {
            nodes: nodes.value,
            edges: edges.value
          };
          logger.info('Raw mode graphData set in loadData:', {
            nodeCount: nodes.value.length,
            edgeCount: edges.value.length,
            sampleEdge: edges.value[0]
          });
        }

      } catch (err) {
        logger.error('Error loading data:', err);
        error.value = err.response?.data?.detail || err.message;

        if (err.response?.status === 403) {
          error.value = 'Authentication required. Please check your API credentials.';
        } else if (err.response?.status === 404) {
          error.value = 'API endpoint not found. Please check the server configuration.';
        } else if (err.code === 'ECONNABORTED') {
          error.value = 'Request timeout. Please check your network connection and try again.';
        }
      } finally {
        loading.value = false;
      }
    };

    // Convert hierarchical tree to graph format for Cytoscape
    const convertTreeToGraph = (tree) => {
      const nodes = new Map();
      const edges = [];

      const processNode = (node, parentId = null) => {
        // Add node
        nodes.set(node.id, {
          id: node.id,
          label: node.name,
          taxonomy: node.taxonomy,
          hierarchical: true,
          projectsCount: node.projectsCount || 0,
          metrics: node.metrics || {}
        });

        // Add edge from parent
        if (parentId) {
          edges.push({
            id: `${parentId}-${node.id}`,
            source: parentId,
            target: node.id,
            group: 'hierarchical'
          });
        }

        // Process children
        if (node.children && node.children.length > 0) {
          node.children.forEach(child => processNode(child, node.id));
        }
      };

      tree.forEach(rootNode => processNode(rootNode));

      return {
        nodes: Array.from(nodes.values()),
        edges: edges
      };
    };

    const updateVisualization = () => {
      if (taxonomies.value) {
        logger.info('Updating visualization with selected taxonomy:', selectedTaxonomy.value);
        // Rebuild graph with new mode and taxonomy selection
        rebuildGraph();
      }
    };

    const rebuildGraph = async () => {
      try {
        loading.value = true;

        logger.info('Rebuilding graph with:', {
          selectedTaxonomy: selectedTaxonomy.value,
          hierarchicalMode: hierarchicalMode.value
        });

        // Rebuild graph with current mode using graph store
        if (hierarchicalMode.value) {
          // Hierarchical mode: use hierarchical tree endpoint
          await graphStore.loadHierarchicalTree({
            rootTaxonomy: selectedTaxonomy.value
          });
          logger.info('Hierarchical tree rebuilt:', treeData.value?.length, 'roots');
        } else {
          // Raw mode: use network graph endpoint
          await graphStore.loadTagGraph({
            rootTaxonomy: selectedTaxonomy.value,
            hierarchicalMode: false
          });
          logger.info('Network graph rebuilt:', nodes.value?.length, 'nodes,', edges.value?.length, 'edges');
        }

        if (hierarchicalMode.value) {
          // For hierarchical mode, convert tree to graph format for Cytoscape
          if (!treeData.value) {
            throw new Error('Failed to load hierarchical tree data');
          }
          graphData.value = convertTreeToGraph(treeData.value);
        } else {
          // For network mode, use nodes/edges directly
          if (!nodes.value || !edges.value) {
            throw new Error('Failed to load graph data');
          }
          graphData.value = {
            nodes: nodes.value,
            edges: edges.value
          };
        }

        logger.info('Graph rebuilt with nodes:', graphData.value?.nodes?.size || graphData.value?.nodes?.length, 'edges:', graphData.value?.edges?.length);

        // Re-render Cytoscape after graph is built
        nextTick(() => {
          renderCytoscapeGraph();
        });

      } catch (err) {
        logger.error('Error rebuilding graph:', err);
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
      const nodeList = Array.isArray(graphData.value.nodes) ? graphData.value.nodes : [];
      const nodes = nodeList.map(node => {
        // Extract capture group from tag name if it matches taxonomy pattern
        const taxonomy = taxonomies.value?.find(t => t.id === node.taxonomy);
        let captureGroups = [];
        if (taxonomy && taxonomy.regex_pattern) {
          const regex = createJsRegExp(taxonomy.regex_pattern);
          if (regex) {
            const match = regex.exec(node.id);
            if (match && match.groups) {
              captureGroups = Object.values(match.groups).filter(g => g); // Get all non-empty capture groups
            }
          } else {
            logger.warn('Invalid regex pattern:', taxonomy.regex_pattern);
          }
        }

        const taxonomyName = taxonomy?.name || node.taxonomy;

        return {
          data: {
            id: node.id,
            title: node.label,
            label: `${taxonomyName}\n${captureGroups.length > 0 ? '\n' + captureGroups.join('\n') : ''}`, // Show taxonomy name and capture groups
            taxonomy: node.taxonomy,
            captureGroups: captureGroups,
            hierarchical: node.hierarchical || false,
            projectsCount: node.projectsCount || 0
          }
        };
      });

      // Safety check for edges array
      const edgeList = Array.isArray(graphData.value.edges) ? graphData.value.edges : [];
      logger.info('Rendering graph with', nodes.length, 'nodes and', edgeList.length, 'edges');

      const edges = edgeList.map(edge => ({
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
                return ele.data('hierarchical') ? 'round-rectangle' : 'barrel';
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
                return ele.data('hierarchical') ? '250px' : '180px';
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
            return ele.data('hierarchical') ? '280px' : '180px';
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
            return ele.data('hierarchical') ? '250px' : '150px';
          },
          'height': '60px',
          'font-size': '14px',
          'z-index': 1
        });
      });

      // Enable editing from graph
      cytoscapeInstance.value.on('dblclick', 'node', function(evt) {
        const node = evt.target;
        const taxonomyData = taxonomies.value?.find(t => t.id === node.data('taxonomy'));
        if (taxonomyData) {
          // Emit event to open TaxonomyCenter with this taxonomy
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
      logger.info('Selected node:', node);
    };

    const getTaxonomyDisplayName = (taxonomyId) => {
      const taxonomy = taxonomies.value.find(t => t.id === taxonomyId);
      return taxonomy ? taxonomy.name || taxonomy.id : taxonomyId;
    };

    // Helper function to get taxonomy by node (similar to Dashboard)
    const getTaxonomyByNode = (node) => {
      if (!node) return {}

      // Handle tree nodes (from Dashboard) with type and taxonomy properties
      if (node.type === 'taxonomy' && node.taxonomy) {
        return taxonomies.value.find(t => t.id === node.taxonomy)
      }
      // Resolve by node name, honouring priority (shared store resolver).
      // Use node.name (tree nodes) or node.id (Cytoscape graph nodes) for matching.
      const nodeName = node.name || node.id || ''
      return getTaxonomyForTag(nodeName)
    }

    // Helper function to get taxonomy name for nodes
    const getTaxonomyNameForNode = (node) => {
      if (!node) return 'unknown'

      let taxonomy = getTaxonomyByNode(node)

      // If still not found, return 'unknown'
      return taxonomy ? taxonomy.name : 'unknown'
    }

    // Helper function to get taxonomy badge style for nodes
    const getTaxonomyBadgeStyleForNode = (node) => {
      if (!node) return {}

      // Try to find taxonomy sorted by priority by matching regex pattern
      let taxonomy = getTaxonomyByNode(node)

      // If still not found, use a default color
      if (!taxonomy) {
        return {
          backgroundColor: '#6b728020',
          color: '#6b7280',
          borderColor: '#6b728040'
        }
      }

      return getTaxonomyBadgeStyle(taxonomy)
    }

    const getNodeConnections = (nodeId, direction) => {
      if (!graphData.value?.edges) return 0;
      return graphData.value.edges.filter(edge => edge[direction] === nodeId);
    };

    // Find all reachable tags from a selected node following DAG edges (descendants only)
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

        // Follow directed edges forward (source -> target) to get descendants
        // In the DAG, edges represent hierarchical relationships (parent -> child)
        const childNodes = graphData.value.edges
          .filter(edge => edge.source === currentId)
          .map(edge => edge.target);

        childNodes.forEach(nodeId => {
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

        // Convert Set to Array for easier handling
        const tagArray = Array.from(tagIds);
        logger.info('🔍 Getting projects for tags:', tagArray);
        logger.info('📊 Available projects in store:', projects.value);
        logger.info('📊 Projects with tags:', projects.value.filter(p => p.tags && p.tags.length > 0));

        // Ensure projects are loaded before filtering
        if (projects.value.length === 0) {
          logger.info('⚠️ No projects loaded, attempting to load...');
          await projectStore.loadProjects();
        }

        // Use project store to get projects by tags
        const allProjects = projectStore.getProjectsByTags(tagArray);
        logger.info('📊 Filtered projects count:', allProjects.length);

        // Apply pagination
        const startIndex = (page - 1) * pageSize.value;
        const endIndex = startIndex + pageSize.value;
        const paginatedProjects = allProjects.slice(startIndex, endIndex);

        relatedProjectsTotal.value = allProjects.length;
        relatedProjectsTotalPages.value = Math.ceil(allProjects.length / pageSize.value);
        relatedProjects.value = paginatedProjects;
        relatedProjectsPage.value = page;

        logger.info(`📊 Total projects found: ${allProjects.length}, showing page ${page}`);
        return paginatedProjects;
      } catch (error) {
        logger.error('Error fetching projects for tags:', error);
        relatedProjects.value = [];
        relatedProjectsTotal.value = 0;
        relatedProjectsTotalPages.value = 1;
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

    // Tag styling functions
    const { getTaxonomyBadgeStyle, getTaxonomyByName, getTaxonomyForTag } = taxonomyStore;

    const getTagStyle = (tag) => {
      let hasTaxonomy = tag.taxonomy
      if (!hasTaxonomy) {
        hasTaxonomy = getTaxonomyForTag(tag.name)
      }
      if (hasTaxonomy) {
        tag._taxonomy = hasTaxonomy
      }
      if (hasTaxonomy) {
        return 'taxonomy'
      }
      return 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300'
    }

    const getTagDynamicStyle = (tag) => {
      let hasTaxonomy = tag.taxonomy
      if (!hasTaxonomy) {
        hasTaxonomy = getTaxonomyForTag(tag.name)
      }
      if (hasTaxonomy) {
        return getTaxonomyBadgeStyle(hasTaxonomy)
      }
      return {}
    }

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
    onMounted(async () => {
      // Ensure taxonomies are loaded first
      if (taxonomies.value.length === 0) {
        await taxonomyStore.loadTaxonomies();
      }

      // Then load graph data
      await loadData();

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
    watch(hierarchicalMode, () => {
      if (taxonomies.value) {
        rebuildGraph();
      }
    });

    // Watch for taxonomy selection changes to rebuild graph
    watch(selectedTaxonomy, (newTaxonomy) => {
      logger.info('Selected taxonomy changed to:', newTaxonomy);
      if (taxonomies.value && newTaxonomy) {
        rebuildGraph();
      }
    });

    // Watch for taxonomies to be loaded and re-render if needed
    watch(taxonomies, (newTaxonomies) => {
      if (newTaxonomies && newTaxonomies.length > 0 && graphData.value) {
        logger.info('Taxonomies loaded, re-rendering graph with colors');
        nextTick(() => {
          renderCytoscapeGraph();
        });
      }
    });

    return {
      // Reactive data
      graphData,
      selectedTaxonomy,
      hierarchicalMode,
      loading,
      error,
      taxonomies,
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
      controlsCollapsed,
      rootTaxonomyOptions,
      graphExpanded,
      toggleGraphExpand,
      Maximize2,
      Minimize2,

      // Methods
      loadData,
      getTaxonomyDisplayName,
      getTaxonomyNameForNode,
      getTaxonomyBadgeStyleForNode,
      getNodeConnections,
      findReachableTags,
      getProjectsForTags,
      loadRelatedProjectsPage,
      updateRelatedProjects,
      buildDTProjectUrl,
      getTotalVulnerabilities,
      getTagStyle,
      getTagDynamicStyle,
      zoomIn,
      zoomOut,
      resetZoom
    };
  }
};
</script>
