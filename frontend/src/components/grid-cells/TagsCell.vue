<template>
  <div class="flex gap-1 overflow-hidden">
    <span
      v-for="tag in (model.tags || [])"
      :key="tag"
      class="inline-block px-2 py-1 text-xs font-medium bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200 rounded-md whitespace-nowrap"
    >
      {{ tag }}
    </span>
  </div>
</template>

<script setup>
const props = defineProps(['model'])
</script>
