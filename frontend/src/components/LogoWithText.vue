<template>
  <div :class="['dt-logo-with-text', `variant-${variant}`, className]" :style="{ gap: spacing + 'px' }">
    <LogoCompact
      :size="logoSize"
      :variant="variant"
      class="logo-icon"
    />
    <div class="logo-text" :style="{ fontSize: fontSize + 'px' }">
      <span class="dt">DT</span>
      <span class="xtras">xtras</span>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import LogoCompact from './LogoCompact.vue'

const props = defineProps({
  size: {
    type: String,
    default: 'medium',
    validator: (value) => ['small', 'medium', 'large'].includes(value)
  },
  variant: {
    type: String,
    default: 'default',
    validator: (value) => ['default', 'light', 'dark', 'monochrome'].includes(value)
  },
  showText: {
    type: Boolean,
    default: true
  },
  className: {
    type: String,
    default: ''
  }
})

const logoSize = computed(() => {
  switch (props.size) {
    case 'small': return 20
    case 'medium': return 24
    case 'large': return 32
    default: return 24
  }
})

const fontSize = computed(() => {
  switch (props.size) {
    case 'small': return 14
    case 'medium': return 16
    case 'large': return 20
    default: return 16
  }
})

const spacing = computed(() => {
  switch (props.size) {
    case 'small': return 6
    case 'medium': return 8
    case 'large': return 10
    default: return 8
  }
})
</script>

<style scoped>
.dt-logo-with-text {
  display: flex;
  align-items: center;
  font-weight: 600;
  transition: all 0.2s ease-in-out;
}

.dt-logo-with-text:hover {
  transform: scale(1.02);
}

.dt-logo-with-text:active {
  transform: scale(0.98);
}

.logo-icon {
  flex-shrink: 0;
}

.logo-text {
  display: flex;
  align-items: baseline;
  font-weight: 700;
  letter-spacing: -0.025em;
}

.dt {
  font-weight: 800;
  margin-right: 2px;
}

.xtras {
  font-weight: 500;
  opacity: 0.9;
}

/* Variant styles */
.variant-default .dt {
  color: #10B981;
}

.variant-default .xtras {
  color: #6B7280;
}

.variant-light .dt {
  color: #059669;
}

.variant-light .xtras {
  color: #4B5563;
}

.variant-dark .dt {
  color: #34D399;
}

.variant-dark .xtras {
  color: #9CA3AF;
}

.variant-monochrome .dt {
  color: #374151;
}

.variant-monochrome .xtras {
  color: #6B7280;
}

/* Dark mode support */
@media (prefers-color-scheme: dark) {
  .variant-default .dt {
    color: #34D399;
  }

  .variant-default .xtras {
    color: #D1D5DB;
  }
}
</style>
