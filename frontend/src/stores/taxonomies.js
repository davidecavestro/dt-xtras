import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { parseRegExpLiteral } from 'regexpp'

export const useTaxonomyStore = defineStore('taxonomies', () => {
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
      // Import here to avoid circular dependency
      const { default: axios } = await import('axios')

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

    // Convert hex color to RGB for better opacity handling
    const hex = taxonomy.color.replace('#', '')
    const r = parseInt(hex.substring(0, 2), 16)
    const g = parseInt(hex.substring(2, 4), 16)
    const b = parseInt(hex.substring(4, 6), 16)

    return {
      backgroundColor: `${taxonomy.color}20`, // Add transparency
      color: taxonomy.color,
      borderColor: `${taxonomy.color}40`
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

    // Use regexpp to process the regex pattern in a semantic fashion
    const ast = parseRegExpLiteral(`/${pattern}/`)

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
            console.warn(`No relation found for part ${part.name} or relation has no targets`)
            part.options = []
            results.push({ part: part.name, options: [] })
            continue
          }

          // Find target taxonomy by group name
          const targetTaxonomy = taxonomies.value.find(t =>
            t.regex_pattern && t.regex_pattern.includes(`(?<${relation.targets}>`)
          )

          if (!targetTaxonomy) {
            console.warn(`Could not find taxonomy with group ${relation.targets}`)
            part.options = []
            results.push({ part: part.name, options: [] })
            continue
          }

          // Filter tags for the target taxonomy from the provided tags array
          const targetTags = allTags.filter(tag => tag.taxonomy === targetTaxonomy.id)

          // Extract capture group values from target tags
          const captureGroupValues = new Set()
          const targetRegex = new RegExp(targetTaxonomy.regex_pattern)

          targetTags.forEach(tag => {
            const match = tag.name.match(targetRegex)
            if (match && match.groups && match.groups[relation.targets]) {
              captureGroupValues.add(match.groups[relation.targets])
            }
          })

          console.log(`Extracted ${captureGroupValues.size} values for ${part.name} from ${targetTaxonomy.name}:`, Array.from(captureGroupValues))

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
          console.error(`Error loading dropdown values for part ${part.name}:`, error)
          part.options = []
          results.push({ part: part.name, options: [] })
        }
      }
    }

    return results
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
    clearError
  }
})
