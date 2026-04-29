import { describe, it, expect, vi, beforeEach } from 'vitest'
import { useToast } from '../useToast.js'

describe('useToast', () => {
  beforeEach(() => {
    vi.useFakeTimers()
    // Clear all toasts between tests
    const { toasts } = useToast()
    toasts.value = []
  })

  it('should add toast to list when showing', () => {
    const { toasts, showToast } = useToast()

    showToast({ message: 'Test message' })

    expect(toasts.value.length).toBe(1)
    expect(toasts.value[0].message).toBe('Test message')
  })

  it('should assign unique ids to toasts', () => {
    const { toasts, showToast } = useToast()

    const id1 = showToast({ message: 'First' })
    const id2 = showToast({ message: 'Second' })

    expect(id1).not.toBe(id2)
    expect(toasts.value[0].id).toBe(id1)
    expect(toasts.value[1].id).toBe(id2)
  })

  it('should have default type as success', () => {
    const { toasts, showToast } = useToast()

    showToast({ message: 'Test' })

    expect(toasts.value[0].type).toBe('success')
  })

  it('should allow custom type', () => {
    const { toasts, showToast } = useToast()

    showToast({ type: 'error', message: 'Error!' })

    expect(toasts.value[0].type).toBe('error')
  })

  it('should have default duration of 3000ms', () => {
    const { toasts, showToast } = useToast()
    // Clear any previous toasts
    toasts.value = []

    const id = showToast({ message: 'Test' })

    expect(toasts.value.find(t => t.id === id).duration).toBe(3000)
  })

  it('should allow custom duration', () => {
    const { toasts, showToast } = useToast()
    // Clear any previous toasts
    toasts.value = []

    const id = showToast({ message: 'Test', duration: 5000 })

    expect(toasts.value.find(t => t.id === id).duration).toBe(5000)
  })

  it('should auto-remove toast after duration', () => {
    const { toasts, showToast } = useToast()

    showToast({ message: 'Test', duration: 3000 })
    expect(toasts.value.length).toBe(1)

    vi.advanceTimersByTime(3000)
    expect(toasts.value.length).toBe(0)
  })

  it('should not auto-remove if duration is 0', () => {
    const { toasts, showToast } = useToast()

    showToast({ message: 'Persistent', duration: 0 })
    expect(toasts.value.length).toBe(1)

    vi.advanceTimersByTime(10000)
    expect(toasts.value.length).toBe(1)
  })

  it('should remove toast by id', () => {
    const { toasts, showToast, removeToast } = useToast()

    const id = showToast({ message: 'Test' })
    expect(toasts.value.length).toBe(1)

    removeToast(id)
    expect(toasts.value.length).toBe(0)
  })

  it('should not fail when removing non-existent toast', () => {
    const { removeToast } = useToast()

    expect(() => removeToast(99999)).not.toThrow()
  })

  it('should show success toast with helper', () => {
    const { toasts, showSuccess } = useToast()

    showSuccess('Success Title', 'Success message', 2000)

    expect(toasts.value.length).toBe(1)
    expect(toasts.value[0].type).toBe('success')
    expect(toasts.value[0].title).toBe('Success Title')
    expect(toasts.value[0].message).toBe('Success message')
    expect(toasts.value[0].duration).toBe(2000)
  })

  it('should show error toast with helper', () => {
    const { toasts, showError } = useToast()
    // Clear any previous toasts
    toasts.value = []

    showError('Error Title', 'Error message')

    expect(toasts.value.length).toBe(1)
    expect(toasts.value[0].type).toBe('error')
    expect(toasts.value[0].title).toBe('Error Title')
    expect(toasts.value[0].message).toBe('Error message')
    expect(toasts.value[0].duration).toBe(5000) // default error duration
  })

  it('should use default values for error toast', () => {
    const { toasts, showError } = useToast()
    // Clear any previous toasts
    toasts.value = []

    showError('Title only')

    expect(toasts.value[0].message).toBe('')
  })
})
