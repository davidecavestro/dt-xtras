<template>
  <div class="lg:w-2/5 bg-white dark:bg-gray-800 rounded-lg shadow overflow-hidden flex flex-col">
    <div class="p-4 border-b border-gray-200 dark:border-gray-700 flex-shrink-0">
      <div class="flex justify-between items-center mb-3">
        <h3 class="text-lg font-medium text-gray-900 dark:text-white">Navigation Tree</h3>
        <div class="flex items-center gap-2">
          <!-- Tree Mode Toggle -->
          <div class="flex bg-gray-100 dark:bg-gray-700 rounded">
            <button
              @click="$emit('set-tree-mode', 'network')"
              :class="treeMode === 'network' ? 'bg-white dark:bg-gray-600 shadow-sm' : ''"
              class="px-2 py-1 text-xs rounded transition-all cursor-pointer hover:shadow-md"
              title="Network View (shared nodes)"
            >
              <Share2 class="w-4 h-4" />
            </button>
            <button
              @click="$emit('set-tree-mode', 'hierarchical')"
              :class="treeMode === 'hierarchical' ? 'bg-white dark:bg-gray-600 shadow-sm' : ''"
              class="px-2 py-1 text-xs rounded transition-all cursor-pointer hover:shadow-md"
              title="Hierarchical View (distinct paths)"
            >
              <GitBranch class="w-4 h-4" />
            </button>
          </div>
          <!-- View Toggle -->
          <div class="flex bg-gray-100 dark:bg-gray-700 rounded">
            <button
              @click="treeViewMode = 'tree'"
              :class="treeViewMode === 'tree' ? 'bg-white dark:bg-gray-600 shadow-sm' : ''"
              class="px-2 py-1 text-xs rounded transition-all cursor-pointer hover:shadow-md"
              title="Tree View"
            >
              <ListIcon class="w-4 h-4" />
            </button>
            <button
              @click="treeViewMode = 'table'"
              :class="treeViewMode === 'table' ? 'bg-white dark:bg-gray-600 shadow-sm' : ''"
              class="px-2 py-1 text-xs rounded transition-all cursor-pointer hover:shadow-md"
              title="Table View"
            >
              <Table class="w-4 h-4" />
            </button>
          </div>
          <button
            @click="$emit('clear')"
            v-if="selectedTreeNode"
            class="text-xs px-2 py-1 bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-300 rounded hover:bg-gray-200 dark:hover:bg-gray-600 cursor-pointer hover:shadow-md transition-all"
          >
            Clear
          </button>
        </div>
      </div>
      <input
        v-model="searchQuery"
        placeholder="Search tags, projects..."
        class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
      />
    </div>

    <div class="flex-1 overflow-y-auto p-4">
      <div v-if="shouldShowLoading" class="text-center py-4">
        <div class="inline-block animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600"></div>
      </div>

      <!-- Tree View -->
      <div v-else-if="treeViewMode === 'tree' && treeData && treeData.length > 0" class="space-y-1" :key="treeData.length">
        <TreeNode
          v-for="node in treeData"
          :key="node.id"
          :node="node"
          :selected-node="selectedTreeNode"
          :expanded-nodes="expandedNodes"
          :search-query="searchQuery"
          @select="$emit('select', $event)"
          @toggle="$emit('toggle', $event)"
        />
      </div>

      <!-- Table View -->
      <div v-else-if="treeViewMode === 'table' && treeData && treeData.length > 0" :key="'table-' + treeData.length">
        <TreeTable
          :nodes="treeData"
          :selected-node="selectedTreeNode"
          :sort-by="treeSortBy"
          :sort-desc="treeSortDesc"
          @select="$emit('select', $event)"
          @toggle="$emit('toggle', $event)"
        />
      </div>

      <div v-else class="text-center py-4 text-gray-500 dark:text-gray-400">
        No tree data available
      </div>
    </div>
  </div>
</template>

<script>
import { ref } from 'vue'
import TreeNode from './TreeNode.vue'
import TreeTable from './TreeTable.vue'
import { ListIcon, Table, Share2, GitBranch } from 'lucide-vue-next'

export default {
  name: 'NavigationTreePanel',
  components: { TreeNode, TreeTable, ListIcon, Table, Share2, GitBranch },
  props: {
    treeMode: { type: String, default: 'hierarchical' },
    treeData: { type: Array, default: () => [] },
    selectedTreeNode: { type: Object, default: null },
    expandedNodes: { type: Set, default: () => new Set() },
    treeSortBy: { type: String, default: 'name' },
    treeSortDesc: { type: Boolean, default: false },
    shouldShowLoading: { type: Boolean, default: false }
  },
  // 'set-tree-mode' triggers a data reload in the parent (it owns treeData);
  // tree view mode and the search box are purely local to this panel.
  emits: ['set-tree-mode', 'select', 'toggle', 'clear'],
  setup() {
    const treeViewMode = ref('tree') // 'tree' or 'table'
    const searchQuery = ref('')
    return { treeViewMode, searchQuery }
  }
}
</script>
