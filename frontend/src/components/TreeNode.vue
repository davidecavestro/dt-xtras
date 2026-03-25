<template>
  <div class="tree-node">
    <div
      class="node-item flex items-center py-2 px-3 rounded-md cursor-pointer hover:bg-gray-100 dark:hover:bg-gray-700"
      :class="{
        'bg-blue-50 dark:bg-blue-900/20 border-l-4 border-blue-500': isSelected,
        'border-l-4 border-transparent': !isSelected
      }"
      :style="{ marginLeft: `${level * 24}px` }"
      @click="handleSelect"
    >
      <!-- Expand/Collapse Icon -->
      <button
        v-if="hasChildren"
        @click.stop="toggleExpanded"
        class="mr-2 p-1 hover:bg-gray-200 dark:hover:bg-gray-600 rounded"
      >
        <ChevronRight
          class="h-4 w-4 text-gray-500 transition-transform"
          :class="{ 'transform rotate-90': isExpanded }"
        />
      </button>
      <div v-else class="w-6 mr-2"></div>

      <!-- Node Icon -->
      <span class="text-lg mr-2">{{ nodeIcon }}</span>

      <!-- Node Name -->
      <span class="flex-1 text-sm font-medium text-gray-900 dark:text-white">
        {{ displayName }}
      </span>

      <!-- Node Type Badge -->
      <span
        v-if="showTypeBadge"
        class="px-2 py-1 text-xs rounded-full"
        :class="typeBadgeClass"
      >
        {{ nodeTypeLabel }}
      </span>

      <!-- Projects Count -->
      <span
        v-if="showProjectsCount && projectsCount > 0"
        class="ml-2 px-2 py-1 text-xs bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-300 rounded-full"
      >
        {{ projectsCount }}
      </span>
    </div>

    <!-- Children -->
    <div v-if="hasChildren && isExpanded" class="ml-6 mt-1">
      <TreeNode
        v-for="child in node.children"
        :key="child.id"
        :node="child"
        :level="level + 1"
        :selected-node-id="selectedNodeId"
        :get-node-display-name="getNodeDisplayName"
        :get-node-type-icon="getNodeTypeIcon"
        :get-node-type-label="getNodeTypeLabel"
        @select="$emit('select', $event, buildPath(child))"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { ChevronRight, Folder, Tag, Package } from 'lucide-vue-next'

const props = defineProps({
  node: {
    type: Object,
    required: true
  },
  level: {
    type: Number,
    default: 0
  },
  selectedNodeId: {
    type: String,
    default: ''
  },
  getNodeDisplayName: {
    type: Function,
    default: (node) => node.name
  },
  getNodeTypeIcon: {
    type: Function,
    default: () => '🏷️'
  },
  getNodeTypeLabel: {
    type: Function,
    default: (node) => node.taxonomy || 'Unknown'
  }
})

const emit = defineEmits(['select'])

const isExpanded = ref(props.level === 0) // Auto-expand root level

const hasChildren = computed(() => {
  return props.node.children && props.node.children.length > 0
})

const isSelected = computed(() => {
  return props.selectedNodeId === props.node.id
})

const displayName = computed(() => {
  return props.getNodeDisplayName(props.node)
})

const nodeIcon = computed(() => {
  return props.getNodeTypeIcon(props.node)
})

const showTypeBadge = computed(() => {
  return props.node.taxonomy && props.node.type === 'tag'
})

const nodeTypeLabel = computed(() => {
  return props.getNodeTypeLabel(props.node)
})

const typeBadgeClass = computed(() => {
  const classes = {
    'customer': 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200',
    'env': 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200',
    'deploy': 'bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-200',
    'product_version': 'bg-orange-100 text-orange-800 dark:bg-orange-900 dark:text-orange-200'
  }

  return classes[props.node.taxonomy] || 'bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-200'
})

const showProjectsCount = computed(() => {
  return props.node.type === 'tag' && props.node.projectsCount !== undefined
})

const projectsCount = computed(() => {
  return props.node.projectsCount || 0
})

const iconColor = computed(() => {
  if (isSelected.value) return 'text-blue-500'
  if (props.node.type === 'tag') return 'text-green-500'
  if (props.node.type === 'project') return 'text-orange-500'
  return 'text-gray-500'
})

const toggleExpanded = () => {
  isExpanded.value = !isExpanded.value
}

const handleSelect = () => {
  emit('select', props.node)
}

const buildPath = (node) => {
  // Build the full path from root to this node
  // This is a simplified version - we'll need to track the full path
  return node.name
}
</script>

<style scoped>
.tree-node {
  @apply select-none;
}

.node-item {
  transition: all 0.2s ease;
}
</style>
