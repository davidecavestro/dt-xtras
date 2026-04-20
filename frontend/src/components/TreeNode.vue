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

        <!-- Metrics: Projects Count -->
        <div
          v-if="getNodeMetrics(node).projectsCount > 0"
          class="ml-2 flex items-center gap-1 px-1.5 py-0.5 rounded text-xs font-medium bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-400"
          :title="`${getNodeMetrics(node).projectsCount} projects`"
        >
          <Package class="w-3 h-3" />
          <span>{{ getNodeMetrics(node).projectsCount }}</span>
        </div>

        <!-- Metrics: Vulnerabilities by Severity -->
        <div
          v-if="getNodeMetrics(node).vulnerabilities > 0"
          class="ml-2 flex items-center gap-1"
        >
          <span
            v-if="getNodeMetrics(node).critical > 0"
            class="px-1.5 py-0.5 rounded text-xs font-medium bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-400"
            :title="`${getNodeMetrics(node).critical} critical vulnerabilities`"
          >
            {{ getNodeMetrics(node).critical }}
          </span>
          <span
            v-if="getNodeMetrics(node).high > 0"
            class="px-1.5 py-0.5 rounded text-xs font-medium bg-orange-100 dark:bg-orange-900/30 text-orange-700 dark:text-orange-400"
            :title="`${getNodeMetrics(node).high} high vulnerabilities`"
          >
            {{ getNodeMetrics(node).high }}
          </span>
          <span
            v-if="getNodeMetrics(node).medium > 0"
            class="px-1.5 py-0.5 rounded text-xs font-medium bg-yellow-100 dark:bg-yellow-900/30 text-yellow-700 dark:text-yellow-400"
            :title="`${getNodeMetrics(node).medium} medium vulnerabilities`"
          >
            {{ getNodeMetrics(node).medium }}
          </span>
          <span
            v-if="getNodeMetrics(node).low > 0"
            class="px-1.5 py-0.5 rounded text-xs font-medium bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-400"
            :title="`${getNodeMetrics(node).low} low vulnerabilities`"
          >
            {{ getNodeMetrics(node).low }}
          </span>
        </div>

        <!-- Legacy: Vulnerability Indicator (fallback for old data) -->
        <div v-else-if="node.vulnerabilities > 0" class="ml-2">
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
import { Folder, ChevronRight, ChevronDown, Tag, Hash, Globe, Layers } from 'lucide-vue-next'
import { createLogger } from '../utils/logger'
import { createJsRegExp } from '../utils/taxonomyParser'

export default {
  name: 'TreeNode',
  components: {
    ChevronRight,
    FolderIcon: Folder,
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
    const logger = createLogger('TreeNode')

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

      try {
        const regex = new RegExp(`(${props.searchQuery})`, 'gi')
        return props.node.name.replace(regex, '<mark class="bg-yellow-200 dark:bg-yellow-800">$1</mark>')
      } catch (e) {
        // If search query has invalid regex chars, just return the original name
        return props.node.name
      }
    })

    const getVulnColor = (vulnCount) => {
      if (vulnCount >= 10) return 'bg-red-500 dark:bg-red-600'
      if (vulnCount >= 5) return 'bg-orange-500 dark:bg-orange-600'
      if (vulnCount >= 1) return 'bg-yellow-500 dark:bg-yellow-600'
      return 'bg-green-500 dark:bg-green-600'
    }

    const getNodeMetrics = (node) => {
      // Debug: Log node structure once per unique node
      if (!node._logged) {
        const result = node.reachable || node.subtree
        logger.info('getNodeMetrics for', node.name, {
          hasReachable: !!node.reachable,
          hasSubtree: !!node.subtree,
          reachableProjects: node.reachable?.projectsCount,
          subtreeProjects: node.subtree?.projectsCount,
          returning: result?.projectsCount || node.projectsCount || 0
        })
        node._logged = true
      }
      // Prefer reachable aggregated metrics (ancestors + descendants + self)
      // This matches the Related Projects count in the dashboard
      if (node.reachable?.metrics) {
        return {
          projectsCount: node.reachable.projectsCount || 0,
          vulnerabilities: node.reachable.metrics.vulnerabilities || 0,
          critical: node.reachable.metrics.critical || 0,
          high: node.reachable.metrics.high || 0,
          medium: node.reachable.metrics.medium || 0,
          low: node.reachable.metrics.low || 0,
          inheritedRiskScore: node.reachable.metrics.inheritedRiskScore || 0
        }
      }
      // Fallback to subtree (descendants only)
      if (node.subtree?.metrics) {
        return {
          projectsCount: node.subtree.projectsCount || 0,
          vulnerabilities: node.subtree.metrics.vulnerabilities || 0,
          critical: node.subtree.metrics.critical || 0,
          high: node.subtree.metrics.high || 0,
          medium: node.subtree.metrics.medium || 0,
          low: node.subtree.metrics.low || 0,
          inheritedRiskScore: node.subtree.metrics.inheritedRiskScore || 0
        }
      }
      // Fallback to direct node metrics
      if (node.metrics) {
        return {
          projectsCount: node.projectsCount || 0,
          vulnerabilities: node.metrics.vulnerabilities || 0,
          critical: node.metrics.critical || 0,
          high: node.metrics.high || 0,
          medium: node.metrics.medium || 0,
          low: node.metrics.low || 0,
          inheritedRiskScore: node.metrics.inheritedRiskScore || 0
        }
      }
      // Legacy fallback for old data format
      return {
        projectsCount: node.projectsCount || 0,
        vulnerabilities: node.vulnerabilities || 0,
        critical: 0,
        high: 0,
        medium: 0,
        low: 0,
        inheritedRiskScore: 0
      }
    }

    const getNodeIconColor = (node) => {
      logger.debug('getNodeIconColor called for node:', node);

      // For taxonomy nodes, use taxonomy color
      if (node.type === 'taxonomy') {
        // Try to find taxonomy by matching node name with taxonomy patterns
        const { taxonomies } = taxonomyStore

        // Find taxonomy that matches this node's pattern
        const matchingTaxonomy = taxonomies.find(taxonomy => {
          if (!taxonomy.regex_pattern) return false

          // Create regex from pattern (converting Python syntax to JavaScript)
          const regex = createJsRegExp(taxonomy.regex_pattern)
          if (!regex) {
            logger.warn('Invalid regex pattern:', taxonomy.regex_pattern);
            return false
          }
          return regex.test(node.name)
        })

        logger.debug('Found matching taxonomy:', matchingTaxonomy);
        if (matchingTaxonomy && matchingTaxonomy.color) {
          logger.debug('Using taxonomy color:', matchingTaxonomy.color);
          return matchingTaxonomy.color
        }
      }

      // Default colors for different node types
      let color;
      switch (node.type) {
        default:
          color = '#8B5CF6' // purple-500 (for tags)
          break
      }
      logger.debug('Using default color for node type', node.type, ':', color);
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
      getNodeMetrics,
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
