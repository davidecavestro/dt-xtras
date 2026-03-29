<template>
  <div>
    <a
      :href="buildDTProjectUrl(model.uuid)"
      target="_blank"
      class="font-medium text-blue-600 dark:text-blue-400 hover:underline"
      @click.stop
    >
      {{ model.name }}
    </a>
  </div>
</template>

<script setup>
import { buildDTProjectUrl } from '../../config.js'

const props = defineProps(['model'])
</script>
