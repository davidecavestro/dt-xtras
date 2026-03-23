<template>
  <img
    :src="logoSrc"
    :alt="altText"
    :width="size"
    :height="size"
    :class="['logo', className]"
  />
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  size: {
    type: [String, Number],
    default: 40
  },
  variant: {
    type: String,
    default: 'default',
    validator: (value) => ['default', 'light', 'dark', 'monochrome'].includes(value)
  },
  className: {
    type: String,
    default: ''
  }
})

const logoSrc = computed(() => {
  switch (props.variant) {
    case 'dark':
      return '/branding/dt-xtras-logo-dark.svg'
    case 'light':
      return '/branding/dt-xtras-logo.svg'
    case 'monochrome':
      return '/branding/dt-xtras-logo.svg' // Could create a monochrome version
    default:
      return '/branding/dt-xtras-logo.svg'
  }
})

const altText = computed(() => {
  return 'dt-xtras logo'
})
</script>

<style scoped>
.logo {
  transition: all 0.2s ease-in-out;
}

.logo:hover {
  transform: scale(1.05);
}

.logo:active {
  transform: scale(0.95);
}
</style>
