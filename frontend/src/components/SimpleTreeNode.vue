<template>
  <div class="tree-node" :style="{ marginLeft: props.node.level * 20 + 'px' }">
    <div class="flex items-center py-1">
      <span v-if="props.node.children && props.node.children.length > 0" class="mr-2 text-gray-600 dark:text-gray-400">▼</span>
      <span v-else class="mr-2 text-gray-600 dark:text-gray-400">•</span>
      <span
        class="node-name cursor-pointer hover:underline"
        :class="'taxonomy-' + props.node.taxonomy"
        @click="selectNode"
      >
        {{ props.node.name }}
        <span v-if="props.node.projectsCount > 0" class="text-xs text-gray-500 dark:text-gray-400 ml-1">({{ props.node.projectsCount }})</span>
      </span>
    </div>
    <div v-if="props.node.children && props.node.children.length > 0">
      <SimpleTreeNode v-for="child in props.node.children" :key="child.id" :node="child" @node-selected="selectNode" />
    </div>
  </div>
</template>

<script setup>
import { defineProps, defineEmits } from 'vue';

const emit = defineEmits(['node-selected']);

const props = defineProps({
  node: {
    type: Object,
    required: true
  }
});

const selectNode = () => {
  emit('node-selected', props.node);
};
</script>

<style scoped>
.tree-node {
  border-left: 1px solid #e5e7eb;
  padding-left: 8px;
}

.dark .tree-node {
  border-left-color: #4b5563;
}

.node-name {
  font-weight: 500;
  cursor: pointer;
}

.node-name:hover {
  text-decoration: underline;
}

.taxonomy-customer {
  color: #ef4444;
}

.dark .taxonomy-customer {
  color: #f87171;
}

.taxonomy-env {
  color: #14b8a6;
}

.dark .taxonomy-env {
  color: #2dd4bf;
}

.taxonomy-deploy {
  color: #3b82f6;
}

.dark .taxonomy-deploy {
  color: #60a5fa;
}

.taxonomy-product_version {
  color: #8b5cf6;
}

.dark .taxonomy-product_version {
  color: #a78bfa;
}

.taxonomy-unknown {
  color: #6b7280;
}

.dark .taxonomy-unknown {
  color: #9ca3af;
}
</style>
