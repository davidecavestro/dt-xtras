import { describe, it, expect } from 'vitest'
import {
  toJsRegexPattern,
  createJsRegExp,
  parseTaxonomyPattern
} from '../taxonomyParser.js'

describe('taxonomyParser', () => {
  describe('toJsRegexPattern', () => {
    it('should convert Python named capture groups to JS syntax', () => {
      const pythonPattern = '(?P<name>\\w+)'
      const result = toJsRegexPattern(pythonPattern)
      expect(result).toBe('(?<name>\\w+)')
    })

    it('should handle patterns without named groups', () => {
      const pattern = '^(\\w+):(.*)$'
      const result = toJsRegexPattern(pattern)
      expect(result).toBe(pattern)
    })

    it('should handle multiple Python named groups', () => {
      const pythonPattern = '(?P<brand>\\w+):(?P<region>\\w+)'
      const result = toJsRegexPattern(pythonPattern)
      expect(result).toBe('(?<brand>\\w+):(?<region>\\w+)')
    })

    it('should return empty string for empty input', () => {
      expect(toJsRegexPattern('')).toBe('')
    })

    it('should return null/undefined as-is', () => {
      expect(toJsRegexPattern(null)).toBe(null)
      expect(toJsRegexPattern(undefined)).toBe(undefined)
    })
  })

  describe('createJsRegExp', () => {
    it('should create valid RegExp from Python pattern', () => {
      const pythonPattern = '(?P<name>\\w+)'
      const result = createJsRegExp(pythonPattern)
      expect(result).toBeInstanceOf(RegExp)
      expect(result.source).toBe('(?<name>\\w+)')
    })

    it('should support flags', () => {
      const pattern = 'test'
      const result = createJsRegExp(pattern, 'gi')
      expect(result.flags).toBe('gi')
    })

    it('should return null for invalid pattern', () => {
      const invalidPattern = '(?P<invalid'
      const result = createJsRegExp(invalidPattern)
      expect(result).toBe(null)
    })

    it('should return null for empty pattern', () => {
      expect(createJsRegExp('')).toBe(null)
      expect(createJsRegExp(null)).toBe(null)
      expect(createJsRegExp(undefined)).toBe(null)
    })
  })

  describe('parseTaxonomyPattern', () => {
    it('should parse simple capturing group', () => {
      const pattern = '(?<brand>\\w+)'
      const result = parseTaxonomyPattern(pattern)

      expect(result.length).toBeGreaterThan(0)
      const groupPart = result.find(p => p.type === 'group')
      expect(groupPart).toBeDefined()
      expect(groupPart.name).toBe('brand')
    })

    it('should parse pattern with static characters', () => {
      const pattern = 'brand:(?<name>\\w+)'
      const result = parseTaxonomyPattern(pattern)

      const staticPart = result.find(p => p.type === 'static')
      expect(staticPart).toBeDefined()
      expect(staticPart.value).toContain('brand:')
    })

    it('should include text/dropdown input for capture group', () => {
      const pattern = '(?<region>\\w+)'
      const result = parseTaxonomyPattern(pattern)

      const inputPart = result.find(p => p.name === 'region' && (p.type === 'text' || p.type === 'dropdown'))
      expect(inputPart).toBeDefined()
    })

    it('should handle quantifier patterns', () => {
      const pattern = '\\w+'
      const result = parseTaxonomyPattern(pattern)

      // Quantifiers are handled in default case (no output)
      expect(result.length).toBe(0)
    })

    it('should handle complex pattern with multiple groups', () => {
      const pattern = '(?<brand>\\w+):(?<region>\\w+)'
      const result = parseTaxonomyPattern(pattern)

      const brandGroup = result.find(p => p.name === 'brand')
      const regionGroup = result.find(p => p.name === 'region')
      expect(brandGroup).toBeDefined()
      expect(regionGroup).toBeDefined()
    })
  })
})
