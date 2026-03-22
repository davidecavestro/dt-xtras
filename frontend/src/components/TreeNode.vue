<template>
  <div class="tree-node">
    <div
      class="node-item flex items-center py-2 px-3 rounded-md cursor-pointer hover:bg-gray-100 dark:hover:bg-gray-700"
      :class="{
        'bg-blue-50 dark:bg-blue-900/20 border-l-4 border-blue-500': isSelected,
        'border-l-4 border-transparent': !isSelected
      }"
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
      <component
        :is="nodeIcon"
        class="h-4 w-4 mr-2"
        :class="iconColor"
      />

      <!-- Node Label -->
      <div class="flex-1 min-w-0">
        <div class="flex items-center justify-between">
          <span class="text-sm font-medium text-gray-900 dark:text-white truncate">
            {{ node.name }}
          </span>
          <span v-if="node.projects && node.projects.length > 0" class="text-xs text-gray-500 dark:text-gray-400 ml-2">
            {{ node.projects.length }} projects
          </span>
        </div>
        <div v-if="node.pattern" class="text-xs text-gray-500 dark:text-gray-400 truncate">
          {{ node.pattern }}
        </div>
      </div>
    </div>

    <!-- Children -->
    <div v-if="hasChildren && isExpanded" class="ml-6 mt-1">
      <TreeNode
        v-for="child in node.children"
        :key="child.id"
        :node="child"
        :level="level + 1"
        @select="$emit('select', $event, buildPath(child))"
        :selected-node-id="selectedNodeId"
      />
    </div>
  </div>
</template>

<script>
import { ref, computed } from 'vue'
import { ChevronRight, Folder, Tag, Package } from 'lucide-vue-next'

export default {
  name: 'TreeNode',
  components: {
    ChevronRight,
    Folder,
    Tag,
    Package
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
    selectedNodeId: {
      type: String,
      default: ''
    }
  },
  emits: ['select'],
  setup(props, { emit }) {
    const isExpanded = ref(props.level === 0) // Auto-expand root level

    const hasChildren = computed(() => {
      return props.node.children && props.node.children.length > 0
    })

    const isSelected = computed(() => {
      return props.selectedNodeId === props.node.id
    })

    const nodeIcon = computed(() => {
      if (props.node.type === 'tag') return Tag
      if (props.node.type === 'project') return Package
      return Folder
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

    return {
      isExpanded,
      hasChildren,
      isSelected,
      nodeIcon,
      iconColor,
      toggleExpanded,
      handleSelect,
      buildPath
    }
  }
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
