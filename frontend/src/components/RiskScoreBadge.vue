<template>
  <span
    class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium"
    :class="riskClass"
  >
    {{ formattedScore }}
  </span>
</template>

<script>
import { computed } from 'vue'

export default {
  name: 'RiskScoreBadge',
  props: {
    score: {
      type: Number,
      default: 0
    }
  },
  setup(props) {
    const formattedScore = computed(() => {
      if (props.score === 0) return 'N/A'
      return props.score.toFixed(1)
    })

    const riskClass = computed(() => {
      if (props.score === 0) return 'bg-gray-100 text-gray-800'
      if (props.score >= 8.0) return 'bg-red-100 text-red-800'
      if (props.score >= 6.5) return 'bg-orange-100 text-orange-800'
      if (props.score >= 4.5) return 'bg-yellow-100 text-yellow-800'
      if (props.score >= 2.5) return 'bg-blue-100 text-blue-800'
      return 'bg-green-100 text-green-800'
    })

    return {
      formattedScore,
      riskClass
    }
  }
}
</script>
