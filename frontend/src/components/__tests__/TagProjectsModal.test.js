import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import TagProjectsModal from '../TagProjectsModal.vue'

describe('TagProjectsModal', () => {
  it('renders nothing when show is false', () => {
    const wrapper = mount(TagProjectsModal, { props: { show: false, tag: { name: 'x' }, projects: [] } })
    expect(wrapper.text()).toBe('')
  })

  it('shows the title, count, and empty state when there are no projects', () => {
    const wrapper = mount(TagProjectsModal, { props: { show: true, tag: { name: 'brand:acme' }, projects: [] } })
    expect(wrapper.text()).toContain('Projects with tag')
    expect(wrapper.text()).toContain('brand:acme')
    expect(wrapper.text()).toContain('(0)')
    expect(wrapper.text()).toContain('No projects found with this tag.')
  })

  it('renders projects (name + version), no DT link, and emits close', async () => {
    const wrapper = mount(TagProjectsModal, {
      props: {
        show: true,
        tag: { name: 'brand:acme' },
        projects: [{ uuid: 'u1', name: 'proj-one', version: '1.0' }]
      }
    })
    expect(wrapper.text()).toContain('proj-one')
    expect(wrapper.text()).toContain('1.0')
    // DT browsing link was intentionally removed.
    expect(wrapper.find('a').exists()).toBe(false)

    await wrapper.find('button').trigger('click')
    expect(wrapper.emitted('close')).toBeTruthy()
  })

  it('filters projects by name when there are several', async () => {
    const projects = Array.from({ length: 8 }, (_, i) => ({ uuid: `u${i}`, name: `alpha-${i}`, version: '1.0' }))
    projects.push({ uuid: 'beta', name: 'beta-svc', version: '2.0' })
    const wrapper = mount(TagProjectsModal, {
      props: { show: true, tag: { name: 't' }, projects }
    })
    const input = wrapper.find('input')
    expect(input.exists()).toBe(true) // filter shows past 5 projects
    await input.setValue('beta')
    expect(wrapper.text()).toContain('beta-svc')
    expect(wrapper.text()).not.toContain('alpha-0')
  })
})
