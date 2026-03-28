<template>
  <div class="flex items-center">
    <span
      :class="[
        'px-2 py-1 text-xs font-semibold rounded-full',
        model.active ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
      ]"
    >
      {{ model.active ? 'Active' : 'Inactive' }}
    </span>
  </div>
</template>

<script setup>
const props = defineProps(['model'])
</script>
