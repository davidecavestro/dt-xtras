<template>
  <input
    type="checkbox"
    :checked="isSelected"
    @change="toggleSelection($event.target.checked)"
    @click.stop
    class="h-4 w-4 rounded border-gray-300 dark:border-gray-600 text-blue-600 focus:ring-blue-500 dark:focus:ring-blue-500 dark:focus:ring-offset-gray-800"
  />
</template>

<script>
import { computed } from 'vue'

export default {
  name: 'SelectionCell',
  props: {
    modelValue: {
      type: Object,
      required: true
    },
    rowIndex: {
      type: Number,
      required: true
    }
  },
  emits: ['update:modelValue'],
  setup(props, { emit }) {
    const isSelected = computed(() => {
      // Get selected projects from parent component
      const selectedProjects = window.selectedProjects || []
      return selectedProjects.includes(props.modelValue.uuid)
    })

    const toggleSelection = (checked) => {
      // Get selected projects from parent component
      const selectedProjects = window.selectedProjects || []
      const projectUuid = props.modelValue.uuid
      
      if (checked) {
        if (!selectedProjects.includes(projectUuid)) {
          selectedProjects.push(projectUuid)
        }
      } else {
        const index = selectedProjects.indexOf(projectUuid)
        if (index > -1) {
          selectedProjects.splice(index, 1)
        }
      }
      
      // Update window reference
      window.selectedProjects = selectedProjects
      
      // Emit change to trigger reactivity
      emit('update:modelValue', props.modelValue)
    }

    return {
      isSelected,
      toggleSelection
    }
  }
}
</script>
