import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import RiskScoreBadge from '../RiskScoreBadge.vue'

describe('RiskScoreBadge', () => {
  it('renders N/A for zero score', () => {
    const wrapper = mount(RiskScoreBadge, {
      props: { score: 0 }
    })
    expect(wrapper.text()).toBe('N/A')
    expect(wrapper.find('span').classes()).toContain('bg-gray-100')
  })

  it('renders formatted score for non-zero values', () => {
    const wrapper = mount(RiskScoreBadge, {
      props: { score: 7.5 }
    })
    expect(wrapper.text()).toBe('7.5')
  })

  it('applies critical class for score >= 8.0', () => {
    const wrapper = mount(RiskScoreBadge, {
      props: { score: 8.5 }
    })
    expect(wrapper.find('span').classes()).toContain('bg-red-100')
    expect(wrapper.find('span').classes()).toContain('text-red-800')
  })

  it('applies high risk class for score >= 6.5', () => {
    const wrapper = mount(RiskScoreBadge, {
      props: { score: 7.0 }
    })
    expect(wrapper.find('span').classes()).toContain('bg-orange-100')
  })

  it('applies medium risk class for score >= 4.5', () => {
    const wrapper = mount(RiskScoreBadge, {
      props: { score: 5.0 }
    })
    expect(wrapper.find('span').classes()).toContain('bg-yellow-100')
  })

  it('applies low risk class for score >= 2.5', () => {
    const wrapper = mount(RiskScoreBadge, {
      props: { score: 3.0 }
    })
    expect(wrapper.find('span').classes()).toContain('bg-blue-100')
  })

  it('applies minimal risk class for score < 2.5', () => {
    const wrapper = mount(RiskScoreBadge, {
      props: { score: 1.5 }
    })
    expect(wrapper.find('span').classes()).toContain('bg-green-100')
  })

  it('formats score to one decimal place', () => {
    const wrapper = mount(RiskScoreBadge, {
      props: { score: 7.123 }
    })
    expect(wrapper.text()).toBe('7.1')
  })

  it('uses default score of 0 when not provided', () => {
    const wrapper = mount(RiskScoreBadge)
    expect(wrapper.text()).toBe('N/A')
  })
})
