import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import axios from 'axios'
import { parseRegExpLiteral } from 'regexpp'
import { createLogger } from '../utils/logger'
import { toJsRegexPattern, createJsRegExp } from '../utils/taxonomyParser'

export const useTaxonomyStore = defineStore('taxonomies', () => {
  const logger = createLogger('taxonomies')
  // State
  const taxonomies = ref([])
  const loading = ref(false)
  const error = ref(null)
  const lastUpdate = ref(null)

  // Computed properties
  const taxonomyById = computed(() => {
    const taxonomyMap = {}
    taxonomies.value.forEach(taxonomy => {
      taxonomyMap[taxonomy.id] = taxonomy
    })
    return taxonomyMap
  })

  const taxonomyByName = computed(() => {
    const taxonomyMap = {}
    taxonomies.value.forEach(taxonomy => {
      taxonomyMap[taxonomy.name] = taxonomy
    })
    return taxonomyMap
  })

  // Methods
  const loadTaxonomies = async () => {
    if (loading.value) return

    loading.value = true
    error.value = null

    try {
      const response = await axios.get('/api/taxonomies')
      taxonomies.value = response.data

      // Update timestamp to trigger watchers
      lastUpdate.value = Date.now()

      return response.data
    } catch (err) {
      error.value = err.response?.data?.detail || err.message || 'Failed to load taxonomies'
      throw err
    } finally {
      loading.value = false
    }
  }

  const getTaxonomyById = (id) => {
    return taxonomyById.value[id] || null
  }

  const getTaxonomyByName = (name) => {
    return taxonomyByName.value[name] || null
  }

  const getTaxonomyBadgeStyle = (taxonomy) => {
    if (!taxonomy || !taxonomy.color) return {}

    // Convert hex color to RGB
    const hex = taxonomy.color.replace('#', '')
    const r = parseInt(hex.substring(0, 2), 16)
    const g = parseInt(hex.substring(2, 4), 16)
    const b = parseInt(hex.substring(4, 6), 16)

    // Calculate luminance to determine if color is light or dark
    const luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255
    const isLightColor = luminance > 0.5

    // Detect if we're in dark mode - check for dark class on html or body element
    const isDarkMode = typeof document !== 'undefined' &&
                      (document.documentElement.classList.contains('dark') ||
                       document.body.classList.contains('dark'))

    let backgroundColor, textColor, borderColor

    if (isDarkMode) {
      // Dark mode: use more opaque backgrounds for light colors, less for dark colors
      if (isLightColor) {
        backgroundColor = `${taxonomy.color}40` // More opaque for light colors
        textColor = taxonomy.color
        borderColor = `${taxonomy.color}60`
      } else {
        backgroundColor = `${taxonomy.color}20` // Less opaque for dark colors
        textColor = `${taxonomy.color}cc` // Lighten text for dark colors
        borderColor = `${taxonomy.color}40`
      }
    } else {
      // Light mode: use more opaque backgrounds for dark colors, less for light colors
      if (isLightColor) {
        backgroundColor = `${taxonomy.color}30` // More opaque for light colors
        // For light colors, use a much darker text color for better contrast
        textColor = adjustColorBrightness(taxonomy.color, -0.6) // Darken by 60%
        borderColor = `${taxonomy.color}60`
      } else {
        backgroundColor = `${taxonomy.color}20` // Less opaque for dark colors
        textColor = taxonomy.color
        borderColor = `${taxonomy.color}40`
      }
    }

    // Helper function to adjust color brightness
    function adjustColorBrightness(hexColor, factor) {
      const hex = hexColor.replace('#', '')
      const r = parseInt(hex.substring(0, 2), 16)
      const g = parseInt(hex.substring(2, 4), 16)
      const b = parseInt(hex.substring(4, 6), 16)

      const adjust = (value) => {
        const adjusted = Math.round(value + (255 - value) * factor)
        return Math.max(0, Math.min(255, adjusted))
      }

      const newR = adjust(r).toString(16).padStart(2, '0')
      const newG = adjust(g).toString(16).padStart(2, '0')
      const newB = adjust(b).toString(16).padStart(2, '0')

      return `#${newR}${newG}${newB}`
    }

    return {
      backgroundColor,
      color: textColor,
      borderColor
    }
  }

  const getTagTaxonomy = (tag) => {
    if (!tag.taxonomy) return null

    // Tags use taxonomy IDs, so match by ID
    const taxonomyId = tag.taxonomy
    return getTaxonomyById(taxonomyId)
  }

  const refreshTaxonomies = async () => {
    await loadTaxonomies()
  }

  // Parse taxonomy pattern into semantic parts
  const parseTaxonomyPattern = (pattern, relations = []) => {
    const parts = []

    // Convert Python-style pattern to JavaScript-style before parsing
    const jsPattern = toJsRegexPattern(pattern)

    // Use regexpp to process the regex pattern in a semantic fashion
    const ast = parseRegExpLiteral(`/${jsPattern}/`)

    // The 'alternatives' array contains the top-level branches of the regex
    const elements = ast.pattern.alternatives[0].elements

    elements.forEach(node => {
      // Process each node and build the parts array
      switch (node.type) {
        case "CapturingGroup":
          parts.push({
            type: 'group',
            name: node.name
          })

          // Check if this capture group has a corresponding relation
          const hasRelation = relations.some(rel => rel.group === node.name)

          // Add capture group part
          parts.push({
            type: hasRelation ? 'dropdown' : 'text',
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
          parts.push({
            type: 'text',
            value: node.raw
          })
          break

        case "Assertion":
          if (node.kind === "lookahead" || node.kind === "lookbehind") {
            parts.push({ type: 'assertion', kind: node.kind, raw: node.raw })
          }
          break

        default:
          break
      }
    })

    return parts
  }

  // Load dropdown values for tag builder parts
  const loadDropdownValues = async (parts, selectedTaxonomy, allTags = []) => {
    const results = []

    for (const part of parts) {
      if (part.type === 'dropdown' && part.name) {
        try {
          // Find the relation for this part
          const relation = selectedTaxonomy.relations?.find(rel => rel.group === part.name)

          if (!relation || !relation.targets) {
            logger.warn(`No relation found for part ${part.name} or relation has no targets`)
            part.options = []
            results.push({ part: part.name, options: [] })
            continue
          }

          // Find target taxonomy by group name - more flexible matching
          const targetTaxonomy = taxonomies.value.find(t => {
            if (!t.regex_pattern) return false

            // Try exact match first
            if (t.regex_pattern.includes(`(?<${relation.targets}>`)) {
              return true
            }

            // Try to match by taxonomy id if relation targets matches taxonomy id
            if (t.id === relation.targets) {
              return true
            }

            // Try to match by taxonomy name if relation targets matches taxonomy name
            if (t.name.toLowerCase() === relation.targets.toLowerCase()) {
              return true
            }

            return false
          })

          if (!targetTaxonomy) {
            logger.warn(`Could not find taxonomy with group ${relation.targets}`)
            part.options = []
            results.push({ part: part.name, options: [] })
            continue
          }

          // Filter tags for the target taxonomy from the provided tags array
          const targetTags = allTags.filter(tag => tag.taxonomy === targetTaxonomy.id)

          // Extract capture group values from target tags
          const captureGroupValues = new Set()
          const targetRegex = createJsRegExp(targetTaxonomy.regex_pattern)

          if (!targetRegex) {
            logger.warn(`Invalid regex pattern for taxonomy ${targetTaxonomy.id}:`, targetTaxonomy.regex_pattern)
            part.options = []
            results.push({ part: part.name, options: [] })
            continue
          }

          targetTags.forEach(tag => {
            const match = tag.name.match(targetRegex)
            if (match && match.groups) {
              // Try to find the appropriate capture group
              let value = null

              // First try the relation targets as capture group name
              if (match.groups[relation.targets]) {
                value = match.groups[relation.targets]
              } else {
                // If that doesn't work, try to find the first capture group
                const groupNames = Object.keys(match.groups)
                if (groupNames.length > 1) {
                  value = tag.name
                } else if (groupNames.length > 0) {
                  value = match.groups[groupNames[0]]
                }
              }

              if (value) {
                captureGroupValues.add(value)
              }
            }
          })

          logger.info(`Extracted ${captureGroupValues.size} values for ${part.name} from ${targetTaxonomy.name}:`, Array.from(captureGroupValues))

          // Convert to dropdown options
          const options = Array.from(captureGroupValues)
            .sort()
            .map(value => ({
              value: value,
              text: value
            }))
            .filter(Boolean)

          part.options = options
          results.push({ part: part.name, options })

        } catch (error) {
          logger.error(`Error loading dropdown values for part ${part.name}:`, error)
          part.options = []
          results.push({ part: part.name, options: [] })
        }
      }
    }

    return results
  }

  // CRUD operations for taxonomies
  const createTaxonomy = async (taxonomyData) => {
    loading.value = true
    error.value = null

    try {
      const response = await axios.post('/api/taxonomies', taxonomyData)
      await loadTaxonomies() // Refresh the list
      return response.data
    } catch (err) {
      error.value = err.response?.data?.detail || err.message || 'Failed to create taxonomy'
      throw err
    } finally {
      loading.value = false
    }
  }

  const updateTaxonomy = async (id, taxonomyData) => {
    loading.value = true
    error.value = null

    try {
      const response = await axios.put(`/api/taxonomies/${id}`, taxonomyData)
      await loadTaxonomies() // Refresh the list
      return response.data
    } catch (err) {
      error.value = err.response?.data?.detail || err.message || 'Failed to update taxonomy'
      throw err
    } finally {
      loading.value = false
    }
  }

  const deleteTaxonomy = async (id) => {
    loading.value = true
    error.value = null

    try {
      const response = await axios.delete(`/api/taxonomies/${id}`)
      await loadTaxonomies() // Refresh the list
      return response.data
    } catch (err) {
      error.value = err.response?.data?.detail || err.message || 'Failed to delete taxonomy'
      throw err
    } finally {
      loading.value = false
    }
  }

  const reorderTaxonomies = async (taxonomyOrder) => {
    loading.value = true
    error.value = null

    try {
      const response = await axios.put('/api/taxonomies/reorder', taxonomyOrder)
      await loadTaxonomies() // Refresh the list
      return response.data
    } catch (err) {
      error.value = err.response?.data?.detail || err.message || 'Failed to reorder taxonomies'
      throw err
    } finally {
      loading.value = false
    }
  }

  // Get tags for a specific taxonomy
  const getTaxonomyTags = async (taxonomyId) => {
    try {
      const response = await axios.get(`/api/taxonomies/${taxonomyId}/tag`)
      return response.data || []
    } catch (err) {
      error.value = err.response?.data?.detail || err.message || 'Failed to load taxonomy tags'
      throw err
    }
  }

  // Get tag usage data
  const getTagUsage = async (tagName) => {
    try {
      const response = await axios.get(`/api/tag/${tagName}/project`)
      return response.data || []
    } catch (err) {
      // Return empty array on error for usage data (non-critical)
      return []
    }
  }

  // Create a tag for a specific taxonomy
  const createTaxonomyTag = async (tagName, taxonomyId) => {
    try {
      const response = await axios.post('/api/tag', {
        name: tagName,
        taxonomy_id: taxonomyId
      })
      return response.data
    } catch (err) {
      error.value = err.response?.data?.detail || err.message || 'Failed to create tag'
      throw err
    }
  }

  // Clear error
  const clearError = () => {
    error.value = null
  }

  return {
    // State
    taxonomies,
    loading,
    error,
    lastUpdate,

    // Computed
    taxonomyById,
    taxonomyByName,

    // Methods
    loadTaxonomies,
    getTaxonomyById,
    getTaxonomyByName,
    getTaxonomyBadgeStyle,
    getTagTaxonomy,
    refreshTaxonomies,
    parseTaxonomyPattern,
    loadDropdownValues,
    clearError,
    createTaxonomy,
    updateTaxonomy,
    deleteTaxonomy,
    reorderTaxonomies,
    getTaxonomyTags,
    getTagUsage,
    createTaxonomyTag
  }
})
