<template>
  <div>
    <a
      :href="getDependencyTrackUrl(model.uuid)"
      target="_blank"
      class="font-medium text-blue-600 dark:text-blue-400 hover:underline"
      @click.stop
    >
      {{ model.name }}
    </a>
  </div>
</template>

<script setup>
const props = defineProps(['model'])

const getDependencyTrackUrl = (projectUuid) => {
  const dtBaseUrl = window.location.origin.replace(':5173', ':8080')
  return `${dtBaseUrl}/#/project/${projectUuid}`
}
</script>
