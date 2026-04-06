<template>
  <div class="p-6">
    <!-- Header with controls -->
    <div class="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-4 mb-6">
      <div class="flex justify-between items-center mb-4">
        <h1 class="text-2xl font-bold text-gray-900 dark:text-white">Projects Grid</h1>

        <div class="flex items-center space-x-4">
          <!-- Search -->
          <div class="relative">
            <input
              v-model="searchQuery"
              type="text"
              placeholder="Search projects..."
              class="px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
              @input="onSearchInput"
            />
          </div>

          <!-- Refresh -->
          <button
            @click="refreshProjects"
            :disabled="loading"
            class="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 flex items-center"
          >
            <svg v-if="!loading" class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 20 20">
              <path fill-rule="evenodd" d="M4 2a1 1 0 011 1v2.101a7.002 7.002 0 0111.601 2.566 1 1 0 11-1.885.666A5.002 5.002 0 005.999 7H9a1 1 0 010 2H4a1 1 0 01-1-1V3a1 1 0 011-1zm.008 9.057a1 1 0 011.276.61A5.002 5.002 0 0014.001 13H11a1 1 0 110-2h5a1 1 0 011 1v5a1 1 0 11-2 0v-2.101a7.002 7.002 0 01-11.601-2.566 1 1 0 01.61-1.276z" clip-rule="evenodd" />
            </svg>
            <span v-else class="inline-block animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></span>
            Refresh
          </button>
        </div>
      </div>
    </div>

    <!-- Grid Container -->
    <div class="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-4">
      <!-- Debug info -->
      <div class="mb-4 p-4 bg-gray-100 dark:bg-gray-700 rounded-lg">
        <p>Projects: {{ projects.length }}</p>
        <p>Loading: {{ loading }}</p>
        <p>Total: {{ totalProjects }}</p>
        <p>Page: {{ currentPage }}</p>
        <p>Grid rendering: {{ !loading && projects.length > 0 }}</p>
      </div>

      <!-- Filter bar -->
      <div class="mb-4 p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
        <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Project Name</label>
            <input
              v-model="filters.name"
              type="text"
              placeholder="Filter by name..."
              class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
              @input="applyFilters"
            />
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Status</label>
            <select
              v-model="filters.active"
              class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
              @change="applyFilters"
            >
              <option value="">All</option>
              <option :value="true">Active</option>
              <option :value="false">Inactive</option>
            </select>
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Version</label>
            <input
              v-model="filters.version"
              type="text"
              placeholder="Filter by version..."
              class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
              @input="applyFilters"
            />
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Tags</label>
            <input
              v-model="filters.tags"
              type="text"
              placeholder="Filter by tags..."
              class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
              @input="applyFilters"
            />
          </div>
        </div>

        <div class="mt-4 flex justify-end">
          <button
            @click="clearFilters"
            class="px-4 py-2 bg-gray-500 text-white rounded-md hover:bg-gray-600"
          >
            Clear Filters
          </button>
        </div>
      </div>

      <!-- Loading state -->
      <div v-if="loading" class="text-center py-12">
        <div class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        <p class="mt-4 text-gray-600 dark:text-gray-400">Loading projects...</p>
      </div>

      <!-- Data Grid -->
      <vue3-datagrid
        v-else-if="!loading && projects.length > 0"
        :columns="gridColumns"
        :source="projects"
        :row-height="50"
        :virtual="true"
        :page-size="pageSize"
        :page="currentPage"
        :total="totalProjects"
        :theme="isDarkMode ? 'darkCompact' : 'compact'"
        :filter="true"
        :resize="true"
        :autoSizeColumn="{ mode: 'autoSizeOnTextOverlap' }"
        :stretch="true"
        @page-changed="onPageChanged"
        @filter-changed="onFilterChanged"
        @search="onSearch"
        @row-click="onRowClick"
        @row-select="onRowSelect"
        :show-selection="true"
        class="w-full border border-gray-200 dark:border-gray-700"
        style="height: 500px;"
        :readonly="true"
      >
      </vue3-datagrid>

      <!-- Empty state -->
      <div v-else-if="!loading && projects.length === 0" class="text-center py-12">
        <svg class="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 20 20">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414 2.414A1 1 0 006.586 13H4" />
        </svg>
        <h3 class="mt-2 text-sm font-medium text-gray-900 dark:text-white">No projects found</h3>
        <p class="mt-1 text-sm text-gray-500 dark:text-gray-400">
          Get started by creating a new project.
        </p>
      </div>
    </div>

    <!-- Bulk Actions -->
    <div v-if="selectedRows.length > 0" class="mt-6 bg-white dark:bg-gray-800 rounded-lg shadow-lg p-4">
      <div class="flex justify-between items-center mb-4">
        <h3 class="text-lg font-semibold text-gray-900 dark:text-white">
          Selected: {{ selectedRows.length }} projects
        </h3>

        <div class="flex space-x-2">
          <button
            @click="bulkActivate"
            :disabled="loadingBulk"
            class="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 disabled:opacity-50 flex items-center"
          >
            <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 20 20">
              <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM9.555 7.168A1 1 0 008 8v4a1 1 0 001.555.832l3-2a1 1 0 000-1.664l-3-2z" clip-rule="evenodd" />
            </svg>
            Activate
          </button>

          <button
            @click="bulkDeactivate"
            :disabled="loadingBulk"
            class="px-4 py-2 bg-yellow-600 text-white rounded-md hover:bg-yellow-700 disabled:opacity-50 flex items-center"
          >
            <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 20 20">
              <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8 7a1 1 0 00-1 1v4a1 1 0 001 1h4a1 1 0 001-1V8a1 1 0 00-1-1H8z" clip-rule="evenodd" />
            </svg>
            Deactivate
          </button>

          <button
            @click="bulkDelete"
            :disabled="loadingBulk"
            class="px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700 disabled:opacity-50 flex items-center"
          >
            <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 20 20">
              <path fill-rule="evenodd" d="M9 2a1 1 0 00-.894.553L7.382 4H4a1 1 0 000 2v10a2 2 0 002 2h8a2 2 0 002-2V6a1 1 0 100-2h-3.382l-.724-1.447A1 1 0 009 2z" clip-rule="evenodd" />
            </svg>
            Delete
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, computed, onUnmounted } from 'vue'
import axios from 'axios'
import Vue3Datagrid, { VGridVueTemplate } from '@revolist/vue3-datagrid'
import { buildDTProjectUrl } from '../config.js'
import NameCell from './grid-cells/NameCell.vue'
import StatusCell from './grid-cells/StatusCell.vue'
import TagsCell from './grid-cells/TagsCell.vue'
import DateCell from './grid-cells/DateCell.vue'

export default {
  name: 'ProjectsGrid',
  components: {
    Vue3Datagrid
  },
  setup() {
    const projects = ref([])
    const loading = ref(false)
    const loadingBulk = ref(false)
    const selectedRows = ref([])
    const searchQuery = ref('')
    const currentPage = ref(1)
    const pageSize = ref(50)
    const totalProjects = ref(0)
    // Dark mode detection
    const isDarkMode = ref(document.documentElement.classList.contains('dark'))

    // Watch for dark mode changes
    const observer = new MutationObserver(() => {
      isDarkMode.value = document.documentElement.classList.contains('dark')
    })

    onMounted(() => {
      observer.observe(document.documentElement, {
        attributes: true,
        attributeFilter: ['class']
      })
    })

    onUnmounted(() => {
      observer.disconnect()
    })

    // Grid columns configuration
    const gridColumns = computed(() => [
      {
        prop: 'name',
        name: 'Project Name',
        width: 250,
        sortable: true,
        autoSize: true,
        cellTemplate: VGridVueTemplate(NameCell)
      },
      {
        prop: 'version',
        name: 'Version',
        width: 120,
        sortable: true,
        autoSize: true
      },
      {
        prop: 'active',
        name: 'Status',
        width: 100,
        sortable: true,
        autoSize: true,
        cellTemplate: VGridVueTemplate(StatusCell)
      },
      {
        prop: 'lastActivity',
        name: 'Last Activity',
        width: 150,
        sortable: true,
        autoSize: true,
        cellTemplate: VGridVueTemplate(DateCell)
      },
      {
        prop: 'tags',
        name: 'Tags',
        width: 300,
        sortable: false,
        autoSize: true,
        cellTemplate: VGridVueTemplate(TagsCell)
      }
    ])

    // Filter state
    const filters = ref({
      name: '',
      active: '',
      version: '',
      tags: ''
    })

    // Load projects from API
    const loadProjects = async (params = {}) => {
      loading.value = true
      try {
        const requestParams = {
          page: currentPage.value,
          limit: pageSize.value,
          ...params
        }

        // Apply filters
        if (filters.value.name) {
          requestParams.name = filters.value.name
        }
        if (filters.value.active !== '') {
          requestParams.active_only = filters.value.active === 'true'
        }

        console.log('Loading projects with params:', requestParams)
        const response = await axios.get('/api/project', { params: requestParams })
        console.log('Projects response:', response.data)

        // Filter client-side for version and tags since backend might not support them
        let filteredProjects = response.data || []

        if (filters.value.version) {
          filteredProjects = filteredProjects.filter(p =>
            p.version && p.version.toLowerCase().includes(filters.value.version.toLowerCase())
          )
        }

        if (filters.value.tags) {
          filteredProjects = filteredProjects.filter(p =>
            p.tags && p.tags.some(tag =>
              tag.toLowerCase().includes(filters.value.tags.toLowerCase())
            )
          )
        }

        projects.value = filteredProjects

        // Get total count
        try {
          const countParams = {}
          if (filters.value.name) {
            countParams.name = filters.value.name
          }
          if (filters.value.active !== '') {
            countParams.active_only = filters.value.active === 'true'
          }
          const countResponse = await axios.get('/api/project/count', {
            params: countParams
          })
          totalProjects.value = countResponse.data.total || 0
          console.log('Total projects:', totalProjects.value)
        } catch (countError) {
          console.warn('Could not get project count:', countError)
          totalProjects.value = projects.value.length
        }
      } catch (error) {
        console.error('Failed to load projects:', error)
        projects.value = []
      } finally {
        loading.value = false
      }
    }

    // Refresh projects
    const refreshProjects = () => {
      currentPage.value = 1
      loadProjects()
    }

    // Apply filters
    const applyFilters = () => {
      currentPage.value = 1
      loadProjects()
    }

    // Clear filters
    const clearFilters = () => {
      filters.value = {
        name: '',
        active: '',
        version: '',
        tags: ''
      }
      currentPage.value = 1
      loadProjects()
    }

    // Event handlers
    const onPageChanged = (page) => {
      currentPage.value = page
      loadProjects()
    }

    const onFilterChanged = (filters) => {
      console.log('Filters changed:', filters)
      // Apply filters to API call
      loadProjects(filters)
    }

    const onSearch = (searchTerm) => {
      searchQuery.value = searchTerm
      currentPage.value = 1
      loadProjects()
    }

    const onRowClick = (row) => {
      console.log('Row clicked:', row)
    }

    const onRowSelect = (selected) => {
      selectedRows.value = selected
    }

    // Bulk actions
    const bulkActivate = async () => {
      if (selectedRows.value.length === 0) return

      loadingBulk.value = true
      try {
        const activatePromises = selectedRows.value.map(row =>
          axios.patch(`/api/project/${row.uuid}/activate`)
        )
        await Promise.all(activatePromises)

        // Reload projects to update status
        await loadProjects()
        selectedRows.value = []
      } catch (error) {
        console.error('Failed to activate projects:', error)
      } finally {
        loadingBulk.value = false
      }
    }

    const bulkDeactivate = async () => {
      if (selectedRows.value.length === 0) return

      loadingBulk.value = true
      try {
        const deactivatePromises = selectedRows.value.map(row =>
          axios.patch(`/api/project/${row.uuid}/deactivate`)
        )
        await Promise.all(deactivatePromises)

        // Reload projects to update status
        await loadProjects()
        selectedRows.value = []
      } catch (error) {
        console.error('Failed to deactivate projects:', error)
      } finally {
        loadingBulk.value = false
      }
    }

    const bulkDelete = async () => {
      if (selectedRows.value.length === 0) return

      if (!confirm(`Delete ${selectedRows.value.length} selected projects? This action cannot be undone.`)) {
        return
      }

      loadingBulk.value = true
      try {
        const deletePromises = selectedRows.value.map(row =>
          axios.delete(`/api/project/${row.uuid}`)
        )
        await Promise.all(deletePromises)

        // Reload projects
        await loadProjects()
        selectedRows.value = []
      } catch (error) {
        console.error('Failed to delete projects:', error)
      } finally {
        loadingBulk.value = false
      }
    }

    const formatDate = (dateString) => {
      if (!dateString) return 'Never'
      try {
        return new Date(dateString).toLocaleDateString()
      } catch {
        return 'Invalid date'
      }
    }

    const searchDebounce = ref(null)

    onMounted(() => {
      loadProjects()
    })

    return {
      projects,
      loading,
      loadingBulk,
      selectedRows,
      searchQuery,
      currentPage,
      pageSize,
      totalProjects,
      gridColumns,
      isDarkMode,
      filters,
      onPageChanged,
      onFilterChanged,
      onSearch,
      onRowClick,
      onRowSelect,
      bulkActivate,
      bulkDeactivate,
      bulkDelete,
      buildDTProjectUrl,
      formatDate,
      refreshProjects,
      applyFilters,
      clearFilters
    }
  }
}
</script>
