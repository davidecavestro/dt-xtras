<template>
  <tr>
    <td class="px-6 py-4 whitespace-nowrap">
      <div class="flex items-center">
        <button
          v-if="node.children && node.children.length > 0"
          @click="$emit('toggle', node.id)"
          class="mr-2 text-gray-400 hover:text-gray-600"
        >
          <ChevronRight
            :class="{ 'rotate-90': isExpanded }"
            class="w-4 h-4 transition-transform"
          />
        </button>
        <div
          v-else
          class="w-6 mr-2"
        ></div>
        <div
          class="text-sm font-medium text-gray-900"
          :style="{ marginLeft: level * 20 + 'px' }"
        >
          {{ node.name }}
        </div>
      </div>
    </td>

    <td class="px-6 py-4 whitespace-nowrap">
      <span
        class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full"
        :class="getTypeClass(node.type)"
      >
        {{ node.type }}
      </span>
    </td>

    <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
      {{ node.vulnerabilities.toLocaleString() }}
    </td>

    <td class="px-6 py-4 whitespace-nowrap">
      <RiskScoreBadge :score="node.inheritedRiskScore" />
    </td>

    <td class="px-6 py-4 whitespace-nowrap">
      <VulnerabilityBar
        :critical="node.critical"
        :high="node.high"
        :medium="node.medium"
        :low="node.low"
        :total="node.vulnerabilities"
      />
    </td>
  </tr>

  <!-- Child rows -->
  <template v-if="isExpanded && node.children">
    <SecurityRow
      v-for="child in node.children"
      :key="child.id"
      :node="child"
      :level="level + 1"
      :expanded-nodes="expandedNodes"
      @toggle="$emit('toggle', $event)"
    />
  </template>
</template>

<script>
import { computed } from 'vue'
import { ChevronRight } from 'lucide-vue-next'
import RiskScoreBadge from './RiskScoreBadge.vue'
import VulnerabilityBar from './VulnerabilityBar.vue'

export default {
  name: 'SecurityRow',
  components: {
    ChevronRight,
    RiskScoreBadge,
    VulnerabilityBar
  },
  props: {
    node: {
      type: Object,
      required: true
    },
    level: {
      type: Number,
      default: 0
    },
    expandedNodes: {
      type: Set,
      required: true
    }
  },
  emits: ['toggle'],
  setup(props) {
    const isExpanded = computed(() => {
      return props.expandedNodes.has(props.node.id)
    })

    const getTypeClass = (type) => {
      const classes = {
        'customer': 'bg-purple-100 text-purple-800',
        'env': 'bg-blue-100 text-blue-800',
        'product': 'bg-green-100 text-green-800',
        'project': 'bg-gray-100 text-gray-800'
      }
      return classes[type] || 'bg-gray-100 text-gray-800'
    }

    return {
      isExpanded,
      getTypeClass
    }
  }
}
</script>
