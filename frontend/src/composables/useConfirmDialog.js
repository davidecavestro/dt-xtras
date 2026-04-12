import { ref } from 'vue'

export function useConfirmDialog() {
  const showConfirmDialog = ref(false)
  const confirmDialogTitle = ref('')
  const confirmDialogMessage = ref('')
  const confirmDialogConfirmText = ref('Confirm')
  const confirmDialogCancelText = ref('Cancel')
  const confirmDialogResolve = ref(null)

  const showConfirm = (options) => {
    return new Promise((resolve) => {
      confirmDialogTitle.value = options.title || ''
      confirmDialogMessage.value = options.message || ''
      confirmDialogConfirmText.value = options.confirmText || 'Confirm'
      confirmDialogCancelText.value = options.cancelText || 'Cancel'
      confirmDialogResolve.value = resolve
      showConfirmDialog.value = true
    })
  }

  const handleConfirm = () => {
    showConfirmDialog.value = false
    if (confirmDialogResolve.value) {
      confirmDialogResolve.value(true)
      confirmDialogResolve.value = null
    }
  }

  const handleCancel = () => {
    showConfirmDialog.value = false
    if (confirmDialogResolve.value) {
      confirmDialogResolve.value(false)
      confirmDialogResolve.value = null
    }
  }

  return {
    showConfirmDialog,
    confirmDialogTitle,
    confirmDialogMessage,
    confirmDialogConfirmText,
    confirmDialogCancelText,
    showConfirm,
    handleConfirm,
    handleCancel
  }
}
