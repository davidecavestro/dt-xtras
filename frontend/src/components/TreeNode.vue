<template>
  <div>
    <div
      class="flex items-center py-1 px-2 rounded cursor-pointer hover:bg-gray-100 dark:hover:bg-gray-700"
      :class="{
        'bg-blue-50 dark:bg-blue-900/20': isSelected,
        'font-medium': isSelected
      }"
      @click="handleSelect"
    >
      <div class="flex items-center flex-1">
        <!-- Expand/Collapse Icon -->
        <button
          v-if="hasChildren"
          @click.stop="handleToggle"
          class="mr-1 p-1 hover:bg-gray-200 dark:hover:bg-gray-600 rounded text-gray-600 dark:text-gray-400"
        >
          <ChevronRight
            class="w-3 h-3 transition-transform text-gray-600 dark:text-gray-400"
            :class="{ 'rotate-90': isExpanded }"
          />
        </button>
        <div v-else class="w-4 mr-1"></div>

        <!-- Node Icon -->
        <div class="mr-2">
          <FolderIcon v-if="node.type === 'customer'" class="w-4 h-4 text-blue-500" />
          <Server v-else-if="node.type === 'environment'" class="w-4 h-4 text-green-500" />
          <Package v-else-if="node.type === 'project'" class="w-4 h-4 text-orange-500" />
          <Tag v-else class="w-4 h-4 text-purple-500" />
        </div>

        <!-- Node Name with Search Highlight -->
        <span
          class="text-sm text-gray-900 dark:text-white"
          v-html="highlightedName"
        ></span>
        <!-- Vulnerability Indicator -->
        <div v-if="node.vulnerabilities > 0" class="ml-2">
          <div class="w-2 h-2 rounded-full" :class="getVulnColor(node.vulnerabilities)"></div>
        </div>
      </div>
    </div>

    <!-- Children -->
    <div v-if="hasChildren && isExpanded" class="ml-4">
      <TreeNode
        v-for="child in filteredChildren"
        :key="child.id"
        :node="child"
        :selected-node="selectedNode"
        :expanded-nodes="expandedNodes"
        :search-query="searchQuery"
        @select="$emit('select', $event)"
        @toggle="$emit('toggle', $event)"
      />
    </div>
  </div>
</template>

<script>
import { computed } from 'vue'
import { ChevronRight, FolderOpen as FolderIcon, Server, Package, Tag } from 'lucide-vue-next'

export default {
  name: 'TreeNode',
  components: {
    ChevronRight,
    FolderIcon,
    Server,
    Package,
    Tag
  },
  props: {
    node: {
      type: Object,
      required: true
    },
    selectedNode: {
      type: Object,
      default: null
    },
    expandedNodes: {
      type: Set,
      default: () => new Set()
    },
    searchQuery: {
      type: String,
      default: ''
    }
  },
  emits: ['select', 'toggle'],
  setup(props, { emit }) {
    const hasChildren = computed(() => {
      return props.node.children && props.node.children.length > 0
    })

    const isExpanded = computed(() => {
      return props.expandedNodes.has(props.node.id)
    })

    const isSelected = computed(() => {
      return props.selectedNode?.id === props.node.id
    })

    const filteredChildren = computed(() => {
      if (!props.searchQuery || !props.node.children) return props.node.children

      const query = props.searchQuery.toLowerCase()
      return props.node.children.filter(child =>
        child.name.toLowerCase().includes(query)
      )
    })

    const highlightedName = computed(() => {
      if (!props.searchQuery) return props.node.name

      const regex = new RegExp(`(${props.searchQuery})`, 'gi')
      return props.node.name.replace(regex, '<mark class="bg-yellow-200 dark:bg-yellow-800">$1</mark>')
    })

    const getVulnColor = (vulnCount) => {
      if (vulnCount >= 10) return 'bg-red-500 dark:bg-red-600'
      if (vulnCount >= 5) return 'bg-orange-500 dark:bg-orange-600'
      if (vulnCount >= 1) return 'bg-yellow-500 dark:bg-yellow-600'
      return 'bg-green-500 dark:bg-green-600'
    }

    const handleSelect = () => {
      emit('select', props.node)
    }

    const handleToggle = () => {
      emit('toggle', props.node.id)
    }

    return {
      hasChildren,
      isExpanded,
      isSelected,
      filteredChildren,
      highlightedName,
      getVulnColor,
      handleSelect,
      handleToggle
    }
  }
}
</script>

<style scoped>
mark {
  padding: 0 2px;
  border-radius: 2px;
}
</style>
