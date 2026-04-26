<template>
  <div class="w-full">
    <!-- Table Header -->
    <div class="grid grid-cols-7 gap-2 px-2 py-2 bg-gray-100 dark:bg-gray-700 rounded-t-md text-xs font-semibold text-gray-700 dark:text-gray-300">
      <div class="col-span-2">Tag Name</div>
      <div class="text-center">Projects</div>
      <div class="text-center text-red-600 dark:text-red-400">Critical</div>
      <div class="text-center text-orange-600 dark:text-orange-400">High</div>
      <div class="text-center text-yellow-600 dark:text-yellow-400">Medium</div>
      <div class="text-center text-blue-600 dark:text-blue-400">Low</div>
    </div>

    <!-- Table Body -->
    <div class="space-y-0.5">
      <TreeTableRow
        v-for="node in sortedNodes"
        :key="node.id"
        :node="node"
        :selected-node="selectedNode"
        :level="0"
        @select="$emit('select', $event)"
        @toggle="$emit('toggle', $event)"
      />
    </div>

    <!-- Empty State -->
    <div v-if="!nodes || nodes.length === 0" class="text-center py-8 text-gray-500 dark:text-gray-400 bg-white dark:bg-gray-800">
      No data available
    </div>
  </div>
</template>

<script>
import { computed } from 'vue'
import TreeTableRow from './TreeTableRow.vue'

export default {
  name: 'TreeTable',
  components: { TreeTableRow },
  props: {
    nodes: {
      type: Array,
      default: () => []
    },
    selectedNode: {
      type: Object,
      default: null
    },
    sortBy: {
      type: String,
      default: 'name'
    },
    sortDesc: {
      type: Boolean,
      default: false
    }
  },
  emits: ['select', 'toggle'],
  setup(props) {
    const getNodeMetrics = (node) => {
      // Prefer reachable aggregated metrics (ancestors + descendants + self)
      if (node.reachable?.metrics) {
        return {
          projectsCount: node.reachable.projectsCount || 0,
          vulnerabilities: node.reachable.metrics.vulnerabilities || 0,
          critical: node.reachable.metrics.critical || 0,
          high: node.reachable.metrics.high || 0,
          medium: node.reachable.metrics.medium || 0,
          low: node.reachable.metrics.low || 0
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
          low: node.subtree.metrics.low || 0
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
          low: node.metrics.low || 0
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
          low: node.metrics.low || 0
        }
      }
      // Legacy fallback
      return {
        projectsCount: node.projectsCount || 0,
        vulnerabilities: 0,
        critical: 0,
        high: 0,
        medium: 0,
        low: 0
      }
    }

    const sortedNodes = computed(() => {
      const nodes = [...(props.nodes || [])]

      const sortFn = (a, b) => {
        // Prioritize nodes with children over leaf nodes
        const aHasChildren = a.children && a.children.length > 0
        const bHasChildren = b.children && b.children.length > 0

        if (aHasChildren && !bHasChildren) return -1
        if (!aHasChildren && bHasChildren) return 1

        const metricsA = getNodeMetrics(a)
        const metricsB = getNodeMetrics(b)

        let valA, valB
        switch (props.sortBy) {
          case 'projects':
            valA = metricsA.projectsCount
            valB = metricsB.projectsCount
            break
          case 'critical':
            valA = metricsA.critical
            valB = metricsB.critical
            break
          case 'high':
            valA = metricsA.high
            valB = metricsB.high
            break
          case 'medium':
            valA = metricsA.medium
            valB = metricsB.medium
            break
          case 'low':
            valA = metricsA.low
            valB = metricsB.low
            break
          case 'vulnerabilities':
            valA = metricsA.vulnerabilities
            valB = metricsB.vulnerabilities
            break
          default:
            valA = a.name?.toLowerCase() || ''
            valB = b.name?.toLowerCase() || ''
        }

        if (typeof valA === 'string') {
          return props.sortDesc ? valB.localeCompare(valA) : valA.localeCompare(valB)
        }
        return props.sortDesc ? valB - valA : valA - valB
      }

      return nodes.sort(sortFn)
    })

    return { sortedNodes }
  }
}
</script>
