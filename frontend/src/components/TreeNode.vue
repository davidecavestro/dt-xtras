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
      <div class="flex items-center flex-1 min-w-0">
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
          class="text-sm text-gray-900 dark:text-white flex-1 min-w-0 truncate"
          v-html="highlightedName"
        ></span>

        <!-- Metrics (right-aligned, fixed width so every row's counters line up):
             projects count + the four severities. Zero renders as '-', counts
             cap at '99+', so each slot is the same size on every node. -->
        <div class="ml-2 flex items-center gap-1 shrink-0 tabular-nums">
          <!-- Projects Count -->
          <div
            class="flex items-center gap-1 px-1.5 py-0.5 rounded text-xs font-medium"
            :class="metrics.projectsCount > 0
              ? 'bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-400'
              : 'text-gray-400 dark:text-gray-600'"
            :title="`${metrics.projectsCount} projects`"
          >
            <Package class="w-3 h-3" />
            <span class="inline-block min-w-6 text-right">{{ countLabel(metrics.projectsCount) }}</span>
          </div>

          <!-- Vulnerabilities by Severity (always shown for alignment) -->
          <span
            class="inline-block min-w-8 text-center px-1.5 py-0.5 rounded text-xs font-medium"
            :class="severityBadgeClass(metrics.critical, 'critical')"
            :title="`${metrics.critical} critical vulnerabilities`"
          >{{ countLabel(metrics.critical) }}</span>
          <span
            class="inline-block min-w-8 text-center px-1.5 py-0.5 rounded text-xs font-medium"
            :class="severityBadgeClass(metrics.high, 'high')"
            :title="`${metrics.high} high vulnerabilities`"
          >{{ countLabel(metrics.high) }}</span>
          <span
            class="inline-block min-w-8 text-center px-1.5 py-0.5 rounded text-xs font-medium"
            :class="severityBadgeClass(metrics.medium, 'medium')"
            :title="`${metrics.medium} medium vulnerabilities`"
          >{{ countLabel(metrics.medium) }}</span>
          <span
            class="inline-block min-w-8 text-center px-1.5 py-0.5 rounded text-xs font-medium"
            :class="severityBadgeClass(metrics.low, 'low')"
            :title="`${metrics.low} low vulnerabilities`"
          >{{ countLabel(metrics.low) }}</span>
        </div>
        <!-- /metrics -->
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
import { Folder, ChevronRight, ChevronDown, Tag, Hash, Globe, Layers, Server, Package } from 'lucide-vue-next'
import { createLogger } from '../utils/logger'
import { createJsRegExp } from '../utils/taxonomyParser'

export default {
  name: 'TreeNode',
  components: {
    ChevronRight,
    FolderIcon: Folder,
    Tag,
    Server,
    Package
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
      return props.selectedNode === props.node
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
      // Hierarchical tree format: direct metrics with severity counts
      if (node.metrics && (node.metrics.critical !== undefined || node.metrics.high !== undefined)) {
        const vulnCount = (node.metrics.critical || 0) + (node.metrics.high || 0) +
                         (node.metrics.medium || 0) + (node.metrics.low || 0)
        return {
          projectsCount: node.projectsCount || 0,
          vulnerabilities: vulnCount,
          critical: node.metrics.critical || 0,
          high: node.metrics.high || 0,
          medium: node.metrics.medium || 0,
          low: node.metrics.low || 0,
          inheritedRiskScore: node.metrics.inheritedRiskScore || 0
        }
      }
      // Network/graph tree format with vulnerabilities wrapper
      if (node.metrics && node.metrics.vulnerabilities !== undefined) {
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

      // Use color from backend if available (hierarchical tree includes this)
      if (node.color) {
        return node.color
      }

      // For taxonomy nodes, use taxonomy color from store
      if (node.type === 'taxonomy') {
        const { taxonomies } = taxonomyStore

        // Find taxonomy by matching node name with taxonomy patterns
        const matchingTaxonomy = taxonomies.find(taxonomy => {
          if (!taxonomy.regex_pattern) return false

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

      // Default color
      return '#8B5CF6' // purple-500
    }

    const handleSelect = () => {
      emit('select', props.node)
    }

    const handleToggle = () => {
      emit('toggle', props.node.id)
    }

    // This node's metrics, used by the right-aligned counters.
    const metrics = computed(() => getNodeMetrics(props.node))

    // Fixed-width counter label: '-' for zero, '99+' for anything over 99, so
    // every node's counters occupy the same width and line up.
    const countLabel = (n) => (n > 99 ? '99+' : (n > 0 ? String(n) : '-'))

    const SEVERITY_COLORS = {
      critical: 'bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-400',
      high: 'bg-orange-100 dark:bg-orange-900/30 text-orange-700 dark:text-orange-400',
      medium: 'bg-yellow-100 dark:bg-yellow-900/30 text-yellow-700 dark:text-yellow-400',
      low: 'bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-400'
    }
    // Zero counts get no fill - just a faint dash on the default background, so
    // an empty severity reads as a "hole", not a filled badge.
    const MUTED_BADGE = 'text-gray-400 dark:text-gray-600'
    const severityBadgeClass = (count, severity) => (count > 0 ? SEVERITY_COLORS[severity] : MUTED_BADGE)

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
      handleToggle,
      metrics,
      countLabel,
      severityBadgeClass
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
