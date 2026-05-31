import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import SearchableSelect from '../SearchableSelect.vue'

const stringOptions = ['alpha', 'argocd', 'beta', 'gamma']
const objectOptions = [
  { name: 'brand:acme', projectsCount: 3 },
  { name: 'brand:globex', projectsCount: 7 },
  { name: 'region:eu', projectsCount: 5 }
]

describe('SearchableSelect', () => {
  it('shows the input with placeholder when nothing is selected', () => {
    const wrapper = mount(SearchableSelect, {
      props: { modelValue: '', options: stringOptions, placeholder: 'Search…' }
    })
    const input = wrapper.find('input')
    expect(input.exists()).toBe(true)
    expect(input.attributes('placeholder')).toBe('Search…')
    // No dropdown until focused.
    expect(wrapper.find('ul').exists()).toBe(false)
  })

  it('filters options by the typed query (case-insensitive substring)', async () => {
    const wrapper = mount(SearchableSelect, {
      props: { modelValue: '', options: stringOptions }
    })
    const input = wrapper.find('input')
    await input.trigger('focus')
    // 'ar' only matches argocd.
    await input.setValue('ar')
    expect(wrapper.findAll('li').map(li => li.text())).toEqual(['argocd'])
    // 'g' matches arGocd and Gamma, but not alpha/beta (order preserved).
    await input.setValue('g')
    expect(wrapper.findAll('li').map(li => li.text())).toEqual(['argocd', 'gamma'])
  })

  it('emits update:modelValue when an option is clicked', async () => {
    const wrapper = mount(SearchableSelect, {
      props: { modelValue: '', options: stringOptions }
    })
    const input = wrapper.find('input')
    await input.trigger('focus')
    await input.setValue('argo')
    await wrapper.find('li').trigger('mousedown')
    expect(wrapper.emitted('update:modelValue')).toBeTruthy()
    expect(wrapper.emitted('update:modelValue')[0]).toEqual(['argocd'])
  })

  it('renders a clearable chip when a value is selected and clears it', async () => {
    const wrapper = mount(SearchableSelect, {
      props: { modelValue: 'argocd', options: stringOptions, label: 'Project' }
    })
    // Chip shows the selection, input is hidden.
    expect(wrapper.text()).toContain('argocd')
    expect(wrapper.find('input').exists()).toBe(false)
    await wrapper.find('button').trigger('click')
    expect(wrapper.emitted('update:modelValue')[0]).toEqual([''])
  })

  it('supports object options with label/value/hint keys', async () => {
    const wrapper = mount(SearchableSelect, {
      props: {
        modelValue: '',
        options: objectOptions,
        labelKey: 'name',
        valueKey: 'name',
        hintKey: 'projectsCount'
      }
    })
    const input = wrapper.find('input')
    await input.trigger('focus')
    await input.setValue('globex')
    const li = wrapper.find('li')
    expect(li.text()).toContain('brand:globex')
    expect(li.text()).toContain('7') // hint
    await li.trigger('mousedown')
    expect(wrapper.emitted('update:modelValue')[0]).toEqual(['brand:globex'])
  })

  it('caps the visible options at `limit` and shows a truncation hint', async () => {
    const many = Array.from({ length: 120 }, (_, i) => `item-${i}`)
    const wrapper = mount(SearchableSelect, {
      props: { modelValue: '', options: many, limit: 50 }
    })
    await wrapper.find('input').trigger('focus')
    // 50 options + 1 truncation hint <li>.
    const items = wrapper.findAll('li')
    expect(items.length).toBe(51)
    expect(wrapper.text()).toContain('Refine your search')
  })

  it('navigates with arrows and selects with Enter', async () => {
    const wrapper = mount(SearchableSelect, {
      props: { modelValue: '', options: stringOptions }
    })
    const input = wrapper.find('input')
    await input.trigger('focus')
    await input.setValue('a') // matches alpha, argocd, beta, gamma
    // First match is highlighted after typing.
    await input.trigger('keydown.down') // move to second match
    await input.trigger('keydown.enter')
    const emitted = wrapper.emitted('update:modelValue')
    expect(emitted).toBeTruthy()
    // alpha (index 0) -> ArrowDown -> argocd (index 1)
    expect(emitted[0]).toEqual(['argocd'])
  })

  it('closes the dropdown on Escape', async () => {
    const wrapper = mount(SearchableSelect, {
      props: { modelValue: '', options: stringOptions }
    })
    const input = wrapper.find('input')
    await input.trigger('focus')
    expect(wrapper.find('ul').exists()).toBe(true)
    await input.trigger('keydown.esc')
    expect(wrapper.find('ul').exists()).toBe(false)
  })
})
