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
          <FolderIcon v-if="node.type === 'customer'" class="w-4 h-4" :style="{ color: getNodeIconColor(node) }" />
          <Server v-else-if="node.type === 'environment'" class="w-4 h-4" :style="{ color: getNodeIconColor(node) }" />
          <Package v-else-if="node.type === 'project'" class="w-4 h-4" :style="{ color: getNodeIconColor(node) }" />
          <Tag v-else class="w-4 h-4" :style="{ color: getNodeIconColor(node) }" />
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
import { useTaxonomyStore } from '../stores/taxonomies'
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
    const taxonomyStore = useTaxonomyStore()
    const { getTaxonomyBadgeStyle, getTagTaxonomy } = taxonomyStore

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

    const getNodeIconColor = (node) => {
      console.log('getNodeIconColor called for node:', node);

      // For taxonomy nodes, use taxonomy color
      if (node.type === 'taxonomy') {
        // Try to find taxonomy by matching node name with taxonomy patterns
        const { taxonomies } = taxonomyStore

        // Find taxonomy that matches this node's pattern
        const matchingTaxonomy = taxonomies.find(taxonomy => {
          if (!taxonomy.regex_pattern) return false

          // Create regex from pattern and test against node name
          try {
            const regex = new RegExp(taxonomy.regex_pattern)
            return regex.test(node.name)
          } catch (error) {
            console.warn('Invalid regex pattern:', taxonomy.regex_pattern);
            return false
          }
        })

        console.log('Found matching taxonomy:', matchingTaxonomy);
        if (matchingTaxonomy && matchingTaxonomy.color) {
          console.log('Using taxonomy color:', matchingTaxonomy.color);
          return matchingTaxonomy.color
        }
      }

      // Default colors for different node types
      let color;
      switch (node.type) {
        case 'customer':
          color = '#3B82F6' // blue-500
          break
        case 'environment':
          color = '#10B981' // green-500
          break
        case 'project':
          color = '#F97316' // orange-500
          break
        default:
          color = '#8B5CF6' // purple-500 (for tags)
          break
      }
      console.log('Using default color for node type', node.type, ':', color);
      return color
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
      getNodeIconColor,
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
