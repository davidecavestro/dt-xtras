import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import CopyProjectsToTagModal from '../CopyProjectsToTagModal.vue'

const tags = [{ name: 'brand:acme' }, { name: 'brand:other' }, { name: 'region:eu' }]

describe('CopyProjectsToTagModal', () => {
  it('renders nothing when show is false', () => {
    const wrapper = mount(CopyProjectsToTagModal, {
      props: { show: false, sourceTag: { name: 'brand:acme' }, tags }
    })
    expect(wrapper.text()).toBe('')
  })

  it('shows the source tag and emits close on cancel', async () => {
    const wrapper = mount(CopyProjectsToTagModal, {
      props: { show: true, sourceTag: { name: 'brand:acme' }, tags }
    })
    expect(wrapper.text()).toContain('brand:acme')
    const cancelBtn = wrapper.findAll('button').find(b => b.text() === 'Cancel')
    await cancelBtn.trigger('click')
    expect(wrapper.emitted('close')).toBeTruthy()
  })

  it('excludes the source tag from targets and emits copy with the chosen target', async () => {
    const wrapper = mount(CopyProjectsToTagModal, {
      props: { show: false, sourceTag: { name: 'brand:acme' }, tags }
    })
    await wrapper.setProps({ show: true }) // triggers the open watcher -> populates targets
    expect(wrapper.vm.filteredTargetTags.map(t => t.name)).toEqual(['brand:other', 'region:eu'])

    wrapper.vm.selectTargetTag({ name: 'brand:other' })
    wrapper.vm.confirmCopy()
    expect(wrapper.emitted('copy')[0]).toEqual(['brand:other'])
  })

  it('does not emit copy when the target equals the source', () => {
    const wrapper = mount(CopyProjectsToTagModal, {
      props: { show: true, sourceTag: { name: 'brand:acme' }, tags }
    })
    wrapper.vm.selectTargetTag({ name: 'brand:acme' })
    wrapper.vm.confirmCopy()
    expect(wrapper.emitted('copy')).toBeFalsy()
  })
})
