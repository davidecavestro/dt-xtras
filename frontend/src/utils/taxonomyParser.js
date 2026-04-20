/**
 * Advanced Taxonomy Pattern Parser
 *
 * This utility provides sophisticated regex parsing for taxonomy patterns
 * using regexpp for proper semantic understanding of groups,
 * assertions, character classes, and pattern structure.
 */

import { parseRegExpLiteral } from 'regexpp'
import { useTaxonomyStore } from '../stores/taxonomies'
import { useTagStore } from '../stores/tags'

/**
 * Parses a taxonomy pattern into semantic parts
 * @param {string} pattern - The regex pattern to parse
 * @param {Array} relations - Available taxonomy relations for dropdown options
 * @returns {Array} Array of parsed parts with type, name, value, etc.
 */
export const parseTaxonomyPattern = (pattern, relations = []) => {
  const parts = []

  // Use regexpp to process the regex pattern in a semantic fashion
  // so that parts are properly extracted
  const ast = parseRegExpLiteral(`/${pattern}/`)

  // The 'alternatives' array contains the top-level branches of the regex
  // We assume a single path for this specific use case
  const elements = ast.pattern.alternatives[0].elements

  elements.forEach(node => {
    // Process each node and build the parts array
    switch (node.type) {
      case "CapturingGroup":
        parts.push({
          type: 'group',
          name: node.name // This is 'grpA' or 'grpB'
        })

        // Check if this capture group has a corresponding relation
        const hasRelation = relations.some(rel => rel.group === node.name)

        // Add capture group part
        parts.push({
          type: hasRelation ? 'dropdown' : 'text', // Use dropdown only if relation exists
          name: node.name,
          value: '',
          options: hasRelation ? relations.filter(rel => rel.group === node.name).map(rel => ({
            value: rel.group,
            label: rel.label || rel.group
          })) : [],
          pattern: node.pattern
        })
        break

      case "Character":
        // Add a new static part if previous one wasn't static, otherwise append to previous
        if (parts.length > 0 && parts[parts.length - 1].type === 'static') {
          parts[parts.length - 1].value += String.fromCodePoint(node.value)
        } else {
          parts.push({
            type: 'static',
            value: String.fromCodePoint(node.value)
          })
        }
        break

      case "CharacterClass":
        // These represent things like [\w-] or \d
        // For "generate" logic, treat these as static placeholders
        parts.push({
          type: 'text',
          value: node.raw
        })
        break

      case "Assertion":
        // Handles ^, $, lookaheads, etc.
        // Mark them as static/meta for generation logic
        if (node.kind === "lookahead" || node.kind === "lookbehind") {
          parts.push({ type: 'assertion', kind: node.kind, raw: node.raw })
        }
        break

      default:
        // Handle Quantifiers (+, *) or other types if necessary
        break
    }
  })

  return parts
}


/**
 * Loads tag values for dropdowns based on the selected taxonomy using the store
 * @param {Array} parts - The parsed parts from the taxonomy pattern
 * @param {Object} selectedTaxonomy - The selected taxonomy object
 * @returns {Promise<void>}
 */
export const loadTagValuesForDropdowns = async (parts, selectedTaxonomy) => {
  try {
    // Use the stores
    const taxonomyStore = useTaxonomyStore()
    const tagStore = useTagStore()

    // Ensure taxonomies and tags are loaded
    await taxonomyStore.loadTaxonomies()
    await tagStore.loadTags()

    // Use the store method to load dropdown values with tags
    await taxonomyStore.loadDropdownValues(parts, selectedTaxonomy, tagStore.tags)

  } catch (error) {
    logger.error('Error loading dropdown values using store:', error)
    // Fallback: set empty options for all dropdown parts
    parts.forEach(part => {
      if (part.type === 'dropdown') {
        part.options = []
      }
    })
  }
}

/**
 * Converts Python-style regex pattern to JavaScript-compatible pattern.
 * Mainly converts named capture groups: (?P<name>...) -> (?<name>...)
 * @param {string} pattern - Python-style regex pattern
 * @returns {string} JavaScript-compatible regex pattern
 */
export const toJsRegexPattern = (pattern) => {
  if (!pattern) return pattern
  // Convert Python's (?P<name>...) to JavaScript's (?<name>...)
  return pattern.replace(/\(\?P</g, '(?<')
}

/**
 * Creates a RegExp from a Python-style pattern.
 * Converts the pattern to JavaScript syntax first.
 * @param {string} pattern - Python-style regex pattern
 * @param {string} flags - RegExp flags (optional)
 * @returns {RegExp|null} JavaScript RegExp or null if invalid
 */
export const createJsRegExp = (pattern, flags = '') => {
  if (!pattern) return null
  try {
    const jsPattern = toJsRegexPattern(pattern)
    return new RegExp(jsPattern, flags)
  } catch (error) {
    return null
  }
}
