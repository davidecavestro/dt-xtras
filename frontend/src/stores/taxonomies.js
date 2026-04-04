import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

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
    clearError
  }
})
