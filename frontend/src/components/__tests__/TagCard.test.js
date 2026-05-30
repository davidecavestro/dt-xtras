import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import TagCard from '../TagCard.vue'

const baseTag = { name: 'brand:acme', projectsCount: 3 }

describe('TagCard', () => {
  it('renders the tag name and project count', () => {
    const wrapper = mount(TagCard, { props: { tag: baseTag } })
    expect(wrapper.text()).toContain('brand:acme')
    expect(wrapper.text()).toContain('Used by 3 projects')
  })

  it('emits view/edit/clone/delete with the tag', async () => {
    const wrapper = mount(TagCard, { props: { tag: baseTag } })
    await wrapper.find('[title="View Projects"]').trigger('click')
    await wrapper.find('[title="Edit Tag"]').trigger('click')
    await wrapper.find('[title="Clone Tag"]').trigger('click')
    await wrapper.find('[title="Delete"]').trigger('click')
    expect(wrapper.emitted('view')[0]).toEqual([baseTag])
    expect(wrapper.emitted('edit')[0]).toEqual([baseTag])
    expect(wrapper.emitted('clone')[0]).toEqual([baseTag])
    expect(wrapper.emitted('delete')[0]).toEqual([baseTag])
  })

  it('hides the aided-edit button unless the tag belongs to a taxonomy', () => {
    const without = mount(TagCard, { props: { tag: baseTag, belongsToTaxonomy: false } })
    expect(without.find('[title="Aided Edit"]').exists()).toBe(false)
    const withTax = mount(TagCard, { props: { tag: baseTag, belongsToTaxonomy: true } })
    expect(withTax.find('[title="Aided Edit"]').exists()).toBe(true)
  })

  it('hides the copy button when the tag has no projects', () => {
    const wrapper = mount(TagCard, { props: { tag: { name: 't', projectsCount: 0 } } })
    expect(wrapper.find('[title="Copy Projects to Tag"]').exists()).toBe(false)
  })

  it('shows an edit input when editing and emits update/save/cancel', async () => {
    const wrapper = mount(TagCard, {
      props: { tag: baseTag, isEditing: true, editName: 'brand:acme' }
    })
    const input = wrapper.find('input')
    expect(input.exists()).toBe(true)

    await input.setValue('brand:new')
    expect(wrapper.emitted('update:editName')[0]).toEqual(['brand:new'])

    await input.trigger('keyup.enter')
    expect(wrapper.emitted('save-edit')).toBeTruthy()

    await input.trigger('keyup.escape')
    expect(wrapper.emitted('cancel-edit')).toBeTruthy()
  })

  it('shows the taxonomy badge when a taxonomy is provided', () => {
    const wrapper = mount(TagCard, {
      props: { tag: baseTag, taxonomy: { name: 'Brand' } }
    })
    expect(wrapper.text()).toContain('Brand')
  })
})
