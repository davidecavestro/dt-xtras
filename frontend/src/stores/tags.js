import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useTagStore = defineStore('tags', () => {
  const lastUpdate = ref(null)
  const isLoading = ref(false)
  const error = ref(null)

  const createTag = async (tagData) => {
    isLoading.value = true
    error.value = null
    
    try {
      // Import here to avoid circular dependency
      const { default: axios } = await import('axios')
      
      const response = await axios.post('/api/tags', tagData)
      
      // Update timestamp to trigger watchers
      lastUpdate.value = Date.now()
      
      return response.data
    } catch (err) {
      error.value = err.response?.data?.detail || err.message || 'Failed to create tag'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  const deleteTag = async (tagName) => {
    isLoading.value = true
    error.value = null
    
    try {
      const { default: axios } = await import('axios')
      
      await axios.delete(`/api/tags/${tagName}`)
      
      // Update timestamp to trigger watchers
      lastUpdate.value = Date.now()
      
      return true
    } catch (err) {
      error.value = err.response?.data?.detail || err.message || 'Failed to delete tag'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  return {
    lastUpdate,
    isLoading,
    error,
    createTag,
    deleteTag
  }
})
