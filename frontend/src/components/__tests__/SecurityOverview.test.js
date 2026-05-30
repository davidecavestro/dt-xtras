import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import SecurityOverview from '../SecurityOverview.vue'

describe('SecurityOverview', () => {
  it('shows the no-data message when hasData is false', () => {
    const wrapper = mount(SecurityOverview, { props: { hasData: false } })
    expect(wrapper.text()).toContain('No security data available')
    expect(wrapper.text()).not.toContain('Total Vulnerabilities')
  })

  it('renders the severity counts when hasData is true', () => {
    const wrapper = mount(SecurityOverview, {
      props: { hasData: true, total: 12, critical: 3, high: 4, medium: 2, low: 3 }
    })
    expect(wrapper.text()).toContain('Total Vulnerabilities')
    expect(wrapper.text()).toContain('12')
    expect(wrapper.text()).toContain('Critical')
    expect(wrapper.text()).toContain('High')
    expect(wrapper.text()).toContain('Medium')
    expect(wrapper.text()).toContain('Low')
    expect(wrapper.text()).not.toContain('No security data available')
  })
})
