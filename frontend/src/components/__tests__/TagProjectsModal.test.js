import { describe, it, expect, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import TagProjectsModal from '../TagProjectsModal.vue'

vi.mock('../../config.js', () => ({
  buildDTProjectUrl: (uuid) => `http://dt/projects/${uuid}`
}))

describe('TagProjectsModal', () => {
  it('renders nothing when show is false', () => {
    const wrapper = mount(TagProjectsModal, { props: { show: false, tag: { name: 'x' }, projects: [] } })
    expect(wrapper.text()).toBe('')
  })

  it('shows the empty state when there are no projects', () => {
    const wrapper = mount(TagProjectsModal, { props: { show: true, tag: { name: 'brand:acme' }, projects: [] } })
    expect(wrapper.text()).toContain('Projects with tag: brand:acme')
    expect(wrapper.text()).toContain('No projects found with this tag.')
  })

  it('renders project links and emits close', async () => {
    const wrapper = mount(TagProjectsModal, {
      props: {
        show: true,
        tag: { name: 'brand:acme' },
        projects: [{ uuid: 'u1', name: 'proj-one', version: '1.0' }]
      }
    })
    expect(wrapper.text()).toContain('proj-one')
    expect(wrapper.find('a').attributes('href')).toBe('http://dt/projects/u1')

    await wrapper.find('button').trigger('click')
    expect(wrapper.emitted('close')).toBeTruthy()
  })
})
