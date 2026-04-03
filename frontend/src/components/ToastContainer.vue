<template>
  <teleport to="body">
    <div class="fixed bottom-0 right-0 z-50 p-4 space-y-4">
      <Toast
        v-for="toast in toasts"
        :key="toast.id"
        :type="toast.type"
        :title="toast.title"
        :message="toast.message"
        :duration="toast.duration"
        @close="removeToast(toast.id)"
      />
    </div>
  </teleport>
</template>

<script>
import { useToast } from '../composables/useToast.js'
import Toast from './Toast.vue'

export default {
  name: 'ToastContainer',
  components: {
    Toast
  },
  setup() {
    const { toasts, removeToast } = useToast()

    return {
      toasts,
      removeToast
    }
  }
}
</script>
