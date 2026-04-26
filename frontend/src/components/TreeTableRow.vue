<template>
  <div>
    <!-- Row -->
    <div
      class="grid grid-cols-7 gap-2 px-2 py-1.5 text-sm cursor-pointer bg-white dark:bg-gray-800 hover:bg-gray-50 dark:hover:bg-gray-700"
      :class="{
        'bg-blue-50 dark:bg-blue-900/30': isSelected,
        'border-l-2 border-blue-500': isSelected
      }"
      @click="$emit('select', node)"
    >
      <!-- Tag Name with Expand/Collapse -->
      <div class="col-span-2 flex items-center gap-1">
        <button
          v-if="hasChildren"
          @click.stop="$emit('toggle', node.id)"
          class="p-0.5 hover:bg-gray-200 dark:hover:bg-gray-600 rounded"
        >
          <ChevronRight
            class="w-3 h-3 transition-transform text-gray-500 dark:text-gray-400"
            :class="{ 'rotate-90': isExpanded }"
          />
        </button>
        <span v-else class="w-4"></span>

        <span class="truncate text-gray-900 dark:text-gray-100" :style="{ paddingLeft: `${level * 12}px` }">
          {{ node.name }}
        </span>
      </div>

      <!-- Projects Count -->
      <div class="text-center font-medium text-gray-700 dark:text-gray-300">
        {{ metrics.projectsCount }}
      </div>

      <!-- Critical -->
      <div class="text-center font-semibold" :class="metrics.critical > 0 ? 'text-red-600 dark:text-red-400' : 'text-gray-400 dark:text-gray-600'">
        {{ metrics.critical }}
      </div>

      <!-- High -->
      <div class="text-center font-semibold" :class="metrics.high > 0 ? 'text-orange-600 dark:text-orange-400' : 'text-gray-400 dark:text-gray-600'">
        {{ metrics.high }}
      </div>

      <!-- Medium -->
      <div class="text-center font-semibold" :class="metrics.medium > 0 ? 'text-yellow-600 dark:text-yellow-400' : 'text-gray-400 dark:text-gray-600'">
        {{ metrics.medium }}
      </div>

      <!-- Low -->
      <div class="text-center font-semibold" :class="metrics.low > 0 ? 'text-blue-600 dark:text-blue-400' : 'text-gray-400 dark:text-gray-600'">
        {{ metrics.low }}
      </div>
    </div>

    <!-- Children -->
    <div v-if="hasChildren && isExpanded" class="">
      <TreeTableRow
        v-for="child in node.children"
        :key="child.id"
        :node="child"
        :selected-node="selectedNode"
        :level="level + 1"
        @select="$emit('select', $event)"
        @toggle="$emit('toggle', $event)"
      />
    </div>
  </div>
</template>

<script>
import { computed } from 'vue'
import { ChevronRight } from 'lucide-vue-next'

export default {
  name: 'TreeTableRow',
  components: { ChevronRight },
  props: {
    node: {
      type: Object,
      required: true
    },
    selectedNode: {
      type: Object,
      default: null
    },
    level: {
      type: Number,
      default: 0
    }
  },
  emits: ['select', 'toggle'],
  setup(props) {
    const hasChildren = computed(() => {
      return props.node.children && props.node.children.length > 0
    })

    const isExpanded = computed(() => {
      // For now, default to expanded. Could be controlled via state
      return true
    })

    const isSelected = computed(() => {
      return props.selectedNode === props.node
    })

    const metrics = computed(() => {
      const node = props.node
      // Prefer reachable aggregated metrics (ancestors + descendants + self)
      if (node.reachable?.metrics) {
        return {
          projectsCount: node.reachable.projectsCount || 0,
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
          critical: node.subtree.metrics.critical || 0,
          high: node.subtree.metrics.high || 0,
          medium: node.subtree.metrics.medium || 0,
          low: node.subtree.metrics.low || 0
        }
      }
      // Hierarchical tree format: direct metrics with severity counts
      if (node.metrics && (node.metrics.critical !== undefined || node.metrics.high !== undefined)) {
        return {
          projectsCount: node.projectsCount || 0,
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
          critical: node.metrics.critical || 0,
          high: node.metrics.high || 0,
          medium: node.metrics.medium || 0,
          low: node.metrics.low || 0
        }
      }
      // Legacy fallback
      return {
        projectsCount: node.projectsCount || 0,
        critical: 0,
        high: 0,
        medium: 0,
        low: 0
      }
    })

    return { hasChildren, isExpanded, isSelected, metrics }
  }
}
</script>
