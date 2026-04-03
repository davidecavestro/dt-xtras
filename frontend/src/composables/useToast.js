import { ref, reactive } from 'vue'

const toasts = ref([])

export function useToast() {
  const showToast = (options) => {
    const toast = {
      id: Date.now() + Math.random(),
      type: options.type || 'success',
      title: options.title || '',
      message: options.message || '',
      duration: options.duration !== undefined ? options.duration : 3000
    }

    toasts.value.push(toast)

    // Auto remove after duration
    if (toast.duration > 0) {
      setTimeout(() => {
        removeToast(toast.id)
      }, toast.duration)
    }

    return toast.id
  }

  const removeToast = (id) => {
    const index = toasts.value.findIndex(toast => toast.id === id)
    if (index > -1) {
      toasts.value.splice(index, 1)
    }
  }

  const showSuccess = (title, message = '', duration = 3000) => {
    return showToast({
      type: 'success',
      title,
      message,
      duration
    })
  }

  const showError = (title, message = '', duration = 5000) => {
    return showToast({
      type: 'error',
      title,
      message,
      duration
    })
  }

  return {
    toasts,
    showToast,
    removeToast,
    showSuccess,
    showError
  }
}

export default useToast
