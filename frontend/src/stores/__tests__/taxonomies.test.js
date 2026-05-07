import { describe, it, expect, beforeEach } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { useTaxonomyStore } from '../taxonomies'
import { createJsRegExp } from '../../utils/taxonomyParser'

describe('Taxonomy Store - Tag Styling', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
  })

  describe('getTaxonomyBadgeStyle', () => {
    it('returns correct style for taxonomy with custom colors', () => {
      const store = useTaxonomyStore()
      const taxonomy = {
        name: 'security',
        color: '#ff0000'
      }

      const style = store.getTaxonomyBadgeStyle(taxonomy)

      // Should return an object with styling properties
      expect(style).toHaveProperty('backgroundColor')
      expect(style).toHaveProperty('color')
    })

    it('returns empty object when no color provided', () => {
      const store = useTaxonomyStore()
      const taxonomy = { name: 'general' }

      const style = store.getTaxonomyBadgeStyle(taxonomy)

      expect(style).toEqual({})
    })

    it('returns empty object for null/undefined taxonomy', () => {
      const store = useTaxonomyStore()

      expect(store.getTaxonomyBadgeStyle(null)).toEqual({})
      expect(store.getTaxonomyBadgeStyle(undefined)).toEqual({})
    })
  })
})

describe('taxonomyParser - Regex Handling', () => {
  it('creates valid RegExp from valid pattern', () => {
    const regex = createJsRegExp('/^security-/')
    expect(regex).toBeInstanceOf(RegExp)
    expect(regex.test('security-critical')).toBe(true)
    expect(regex.test('other-tag')).toBe(false)
  })

  it('returns null for invalid pattern', () => {
    const regex = createJsRegExp('invalid[(')
    expect(regex).toBeNull()
  })

  it('handles pattern without delimiters', () => {
    const regex = createJsRegExp('security')
    expect(regex).toBeInstanceOf(RegExp)
    expect(regex.test('security-tag')).toBe(true)
  })
})
