import { describe, it, expect, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import Modal from '../Modal.vue'
import { AlertTriangle } from '@lucide/vue'

describe('Modal', () => {
  it('does not render when show is false', () => {
    const wrapper = mount(Modal, {
      props: {
        show: false,
        title: 'Test'
      }
    })

    expect(wrapper.find('[role="dialog"]').exists()).toBe(false)
  })

  it('renders when show is true', () => {
    const wrapper = mount(Modal, {
      props: {
        show: true,
        title: 'Test Modal'
      }
    })

    expect(wrapper.find('[role="dialog"]').exists()).toBe(true)
    expect(wrapper.text()).toContain('Test Modal')
  })

  it('emits confirm event when confirm button clicked', async () => {
    const wrapper = mount(Modal, {
      props: {
        show: true,
        title: 'Confirm?',
        confirmText: 'Yes',
        cancelText: 'No'
      }
    })

    const confirmButton = wrapper.findAll('button').find(b => b.text().includes('Yes'))
    await confirmButton.trigger('click')

    expect(wrapper.emitted('confirm')).toHaveLength(1)
  })

  it('emits cancel and close events when cancel clicked', async () => {
    const wrapper = mount(Modal, {
      props: {
        show: true,
        title: 'Confirm?',
        confirmText: 'Yes',
        cancelText: 'No'
      }
    })

    const cancelButton = wrapper.findAll('button').find(b => b.text().includes('No'))
    await cancelButton.trigger('click')

    expect(wrapper.emitted('cancel')).toHaveLength(1)
    expect(wrapper.emitted('close')).toHaveLength(1)
  })

  it('emits close when backdrop clicked', async () => {
    const wrapper = mount(Modal, {
      props: {
        show: true,
        title: 'Test'
      }
    })

    const backdrop = wrapper.find('.bg-gray-500')
    await backdrop.trigger('click')

    expect(wrapper.emitted('close')).toHaveLength(1)
  })

  it('does not close on backdrop click when closeOnBackdrop is false', async () => {
    const wrapper = mount(Modal, {
      props: {
        show: true,
        title: 'Test',
        closeOnBackdrop: false
      }
    })

    const backdrop = wrapper.find('.bg-gray-500')
    await backdrop.trigger('click')

    expect(wrapper.emitted('close')).toBeUndefined()
  })

  it('renders item list when provided', () => {
    const wrapper = mount(Modal, {
      props: {
        show: true,
        title: 'Items',
        items: ['Item 1', 'Item 2', 'Item 3'],
        itemsLabel: 'Selected items:'
      }
    })

    expect(wrapper.text()).toContain('Selected items:')
    expect(wrapper.text()).toContain('Item 1')
    expect(wrapper.text()).toContain('Item 2')
    expect(wrapper.text()).toContain('Item 3')
  })

  it('applies correct size classes', () => {
    const smallWrapper = mount(Modal, {
      props: { show: true, title: 'Small', size: 'sm' }
    })
    expect(smallWrapper.html()).toContain('sm:max-w-sm')

    const largeWrapper = mount(Modal, {
      props: { show: true, title: 'Large', size: 'lg' }
    })
    expect(largeWrapper.html()).toContain('sm:max-w-2xl')
  })

  it('applies correct icon color classes', () => {
    const wrapper = mount(Modal, {
      props: {
        show: true,
        title: 'Warning',
        icon: AlertTriangle,
        iconColor: 'yellow'
      }
    })

    expect(wrapper.find('.bg-yellow-100').exists()).toBe(true)
    expect(wrapper.find('.text-yellow-600').exists()).toBe(true)
  })

  it('disables confirm button when confirmDisabled is true', () => {
    const wrapper = mount(Modal, {
      props: {
        show: true,
        title: 'Test',
        confirmText: 'Confirm',
        confirmDisabled: true
      }
    })

    const confirmButton = wrapper.findAll('button').find(b => b.text().includes('Confirm'))
    expect(confirmButton.attributes('disabled')).toBeDefined()
    expect(confirmButton.classes()).toContain('opacity-50')
  })

  it('shows loading spinner when loading is true', () => {
    const wrapper = mount(Modal, {
      props: {
        show: true,
        title: 'Loading',
        confirmText: 'Save',
        loading: true
      }
    })

    expect(wrapper.find('.animate-spin').exists()).toBe(true)
  })

  it('uses default button text', () => {
    const wrapper = mount(Modal, {
      props: {
        show: true,
        title: 'Test'
      }
    })

    expect(wrapper.text()).toContain('Confirm')
    expect(wrapper.text()).toContain('Cancel')
  })

  it('validates size prop values', () => {
    const validator = Modal.props.size.validator

    expect(validator('sm')).toBe(true)
    expect(validator('md')).toBe(true)
    expect(validator('lg')).toBe(true)
    expect(validator('xl')).toBe(false)
  })

  it('validates iconColor prop values', () => {
    const validator = Modal.props.iconColor.validator

    expect(validator('red')).toBe(true)
    expect(validator('green')).toBe(true)
    expect(validator('blue')).toBe(true)
    expect(validator('invalid')).toBe(false)
  })

  it('accepts Function type for icon prop (Vue component)', () => {
    // This test prevents the "Invalid prop: type check failed for prop icon" warning
    // Vue components are functions, so icon prop must accept [Object, Function]
    const iconProp = Modal.props.icon

    expect(iconProp.type).toContain(Function)
    expect(iconProp.type).toContain(Object)
  })

  it('renders slot content', () => {
    const wrapper = mount(Modal, {
      props: {
        show: true,
        title: 'Custom Content'
      },
      slots: {
        content: '<div class="custom-slot">Custom content here</div>'
      }
    })

    expect(wrapper.find('.custom-slot').exists()).toBe(true)
    expect(wrapper.text()).toContain('Custom content here')
  })

  it('renders actions slot', () => {
    const wrapper = mount(Modal, {
      props: {
        show: true,
        title: 'Actions'
      },
      slots: {
        actions: '<button class="custom-action">Custom</button>'
      }
    })

    expect(wrapper.find('.custom-action').exists()).toBe(true)
  })
})
