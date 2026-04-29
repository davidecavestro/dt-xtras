import { describe, it, expect, vi } from 'vitest'
import { useConfirmDialog } from '../useConfirmDialog.js'

describe('useConfirmDialog', () => {
  it('should initialize with default values', () => {
    const {
      showConfirmDialog,
      confirmDialogTitle,
      confirmDialogMessage,
      confirmDialogConfirmText,
      confirmDialogCancelText
    } = useConfirmDialog()

    expect(showConfirmDialog.value).toBe(false)
    expect(confirmDialogTitle.value).toBe('')
    expect(confirmDialogMessage.value).toBe('')
    expect(confirmDialogConfirmText.value).toBe('Confirm')
    expect(confirmDialogCancelText.value).toBe('Cancel')
  })

  it('should show dialog and set options when calling showConfirm', () => {
    const {
      showConfirmDialog,
      confirmDialogTitle,
      confirmDialogMessage,
      showConfirm,
      handleCancel
    } = useConfirmDialog()

    // Start dialog but will cancel to avoid hanging promise
    showConfirm({
      title: 'Delete Item',
      message: 'Are you sure?'
    })

    expect(showConfirmDialog.value).toBe(true)
    expect(confirmDialogTitle.value).toBe('Delete Item')
    expect(confirmDialogMessage.value).toBe('Are you sure?')

    // Clean up
    handleCancel()
  })

  it('should resolve with true on confirm', async () => {
    const { showConfirm, handleConfirm } = useConfirmDialog()

    const promise = showConfirm({ title: 'Test' })

    handleConfirm()

    const result = await promise
    expect(result).toBe(true)
  })

  it('should resolve with false on cancel', async () => {
    const { showConfirm, handleCancel } = useConfirmDialog()

    const promise = showConfirm({ title: 'Test' })

    handleCancel()

    const result = await promise
    expect(result).toBe(false)
  })

  it('should hide dialog on confirm', () => {
    const { showConfirmDialog, showConfirm, handleConfirm } = useConfirmDialog()

    showConfirm({ title: 'Test' })
    expect(showConfirmDialog.value).toBe(true)

    handleConfirm()
    expect(showConfirmDialog.value).toBe(false)
  })

  it('should hide dialog on cancel', () => {
    const { showConfirmDialog, showConfirm, handleCancel } = useConfirmDialog()

    showConfirm({ title: 'Test' })
    expect(showConfirmDialog.value).toBe(true)

    handleCancel()
    expect(showConfirmDialog.value).toBe(false)
  })

  it('should use custom button text', () => {
    const {
      confirmDialogConfirmText,
      confirmDialogCancelText,
      showConfirm,
      handleCancel
    } = useConfirmDialog()

    // Start dialog but immediately cancel to avoid hanging promise
    showConfirm({
      title: 'Test',
      confirmText: 'Delete',
      cancelText: 'Keep'
    })

    expect(confirmDialogConfirmText.value).toBe('Delete')
    expect(confirmDialogCancelText.value).toBe('Keep')

    // Clean up
    handleCancel()
  })

  it('should use default button text when not specified', () => {
    const {
      confirmDialogConfirmText,
      confirmDialogCancelText,
      showConfirm,
      handleCancel
    } = useConfirmDialog()

    // Start dialog but immediately cancel to avoid hanging promise
    showConfirm({ title: 'Test' })

    expect(confirmDialogConfirmText.value).toBe('Confirm')
    expect(confirmDialogCancelText.value).toBe('Cancel')

    // Clean up
    handleCancel()
  })

  it('should handle multiple dialogs sequentially', async () => {
    const { showConfirmDialog, showConfirm, handleConfirm, handleCancel } = useConfirmDialog()

    // First dialog
    const promise1 = showConfirm({ title: 'First' })
    handleConfirm()
    const result1 = await promise1
    expect(result1).toBe(true)
    expect(showConfirmDialog.value).toBe(false)

    // Second dialog
    const promise2 = showConfirm({ title: 'Second' })
    expect(showConfirmDialog.value).toBe(true)
    handleCancel()
    const result2 = await promise2
    expect(result2).toBe(false)
  })
})
