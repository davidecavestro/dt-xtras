import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import Toast from '../Toast.vue'

describe('Toast', () => {
  beforeEach(() => {
    vi.useFakeTimers()
  })

  afterEach(() => {
    vi.useRealTimers()
  })

  it('renders success toast with correct styling', async () => {
    const wrapper = mount(Toast, {
      props: {
        type: 'success',
        title: 'Success!',
        message: 'Operation completed'
      },
      global: {
        stubs: {
          transition: false // Don't stub transition, let it render
        }
      },
      attachTo: document.body
    })

    // Wait for onMounted to set show=true
    await flushPromises()
    await vi.advanceTimersByTimeAsync(0)

    expect(wrapper.text()).toContain('Success!')
    expect(wrapper.text()).toContain('Operation completed')
    expect(wrapper.find('.border-green-400').exists()).toBe(true)

    wrapper.unmount()
  })

  it('renders error toast with correct styling', async () => {
    const wrapper = mount(Toast, {
      props: {
        type: 'error',
        title: 'Error!',
        message: 'Something went wrong'
      },
      attachTo: document.body
    })

    await flushPromises()
    await vi.advanceTimersByTimeAsync(0)

    expect(wrapper.text()).toContain('Error!')
    expect(wrapper.find('.border-red-400').exists()).toBe(true)

    wrapper.unmount()
  })

  it('only shows message when provided', async () => {
    const wrapper = mount(Toast, {
      props: {
        type: 'success',
        title: 'Title only'
      },
      attachTo: document.body
    })

    await flushPromises()
    await vi.advanceTimersByTimeAsync(0)

    expect(wrapper.text()).toContain('Title only')
    // Message paragraph should not exist
    expect(wrapper.findAll('p').length).toBe(1)

    wrapper.unmount()
  })

  it('closes when clicking close button', async () => {
    const wrapper = mount(Toast, {
      props: {
        type: 'success',
        title: 'Test'
      },
      attachTo: document.body
    })

    // Wait for mount (show becomes true)
    await flushPromises()
    await vi.advanceTimersByTimeAsync(0)

    const closeButton = wrapper.find('button')
    await closeButton.trigger('click')

    // After close, component should hide
    expect(wrapper.find('.pointer-events-auto').exists()).toBe(false)

    wrapper.unmount()
  })

  it('auto-closes after duration', async () => {
    const wrapper = mount(Toast, {
      props: {
        type: 'success',
        title: 'Test',
        duration: 3000
      },
      attachTo: document.body
    })

    // Wait for mount
    await flushPromises()
    await vi.advanceTimersByTimeAsync(0)
    expect(wrapper.find('.pointer-events-auto').exists()).toBe(true)

    // Advance past duration
    await vi.advanceTimersByTimeAsync(3000)
    expect(wrapper.find('.pointer-events-auto').exists()).toBe(false)

    wrapper.unmount()
  })

  it('does not auto-close when duration is 0', async () => {
    const wrapper = mount(Toast, {
      props: {
        type: 'success',
        title: 'Persistent',
        duration: 0
      },
      attachTo: document.body
    })

    // Wait for mount
    await flushPromises()
    await vi.advanceTimersByTimeAsync(0)
    expect(wrapper.find('.pointer-events-auto').exists()).toBe(true)

    // Advance time - should still be visible
    await vi.advanceTimersByTimeAsync(10000)
    expect(wrapper.find('.pointer-events-auto').exists()).toBe(true)

    wrapper.unmount()
  })

  it('uses default duration of 3000ms', () => {
    const wrapper = mount(Toast, {
      props: {
        type: 'success',
        title: 'Test'
      }
    })

    // Check default prop value
    expect(wrapper.props('duration')).toBe(3000)
  })

  it('uses default type of success', () => {
    const wrapper = mount(Toast, {
      props: {
        title: 'Test'
      }
    })

    expect(wrapper.props('type')).toBe('success')
  })

  it('requires title prop', () => {
    // Vue will warn about missing required prop in development
    const wrapper = mount(Toast, {
      props: {
        type: 'success'
      }
    })

    // title is required but has no default, so it will be undefined if not passed
    expect(wrapper.props('title')).toBeUndefined()
  })

  it('validates type prop values', () => {
    // The validator should accept 'success' and 'error'
    const validator = Toast.props.type.validator

    expect(validator('success')).toBe(true)
    expect(validator('error')).toBe(true)
    expect(validator('warning')).toBe(false)
    expect(validator('info')).toBe(false)
  })
})
