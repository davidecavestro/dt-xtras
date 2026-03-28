<template>
  <div class="text-sm text-gray-600 dark:text-gray-400">
    {{ formatDate(model.lastActivity) }}
  </div>
</template>

<script setup>
const props = defineProps(['model'])

const formatDate = (dateString) => {
  if (!dateString) return 'Never'
  try {
    return new Date(dateString).toLocaleDateString()
  } catch {
    return 'Invalid date'
  }
}
</script>
