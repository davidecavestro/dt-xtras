<template>
  <div class="h-full flex flex-col bg-gray-50 dark:bg-gray-900">
    <!-- Header -->
    <div class="bg-white dark:bg-gray-800 shadow-sm border-b border-gray-200 dark:border-gray-700 px-6 py-4">
      <h1 class="text-2xl font-bold text-gray-900 dark:text-white">Tag Bulk Actions</h1>
      <p class="text-gray-600 dark:text-gray-400 mt-1">Link and unlink tags from projects in bulk</p>
    </div>

    <!-- Action Buttons -->
    <div class="bg-white dark:bg-gray-800 shadow-sm border-b border-gray-200 dark:border-gray-700 px-6 py-3">
      <div class="flex items-center justify-between">
        <div class="flex items-center space-x-3">
          <button
            @click="confirmLink"
            :disabled="selectedTags.length === 0 || selectedProjects.length === 0 || loading"
            class="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors flex items-center"
          >
            <Link class="w-4 h-4 mr-2" />
            Link Selected ({{ selectedTags.length }} tags × {{ selectedProjects.length }} projects)
          </button>

          <button
            @click="confirmUnlink"
            :disabled="selectedTags.length === 0 || selectedProjects.length === 0 || loading"
            class="px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors flex items-center"
          >
            <Unlink class="w-4 h-4 mr-2" />
            Unlink Selected
          </button>

          <button
            @click="clearSelection"
            :disabled="selectedTags.length === 0 && selectedProjects.length === 0"
            class="px-4 py-2 bg-gray-600 text-white rounded-md hover:bg-gray-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
          >
            Clear Selection
          </button>
        </div>

        <button
          @click="refreshData"
          :disabled="loading"
          class="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors flex items-center"
        >
          <RefreshCw :class="['w-4 h-4', loading && 'animate-spin']" />
          Refresh
        </button>
      </div>
    </div>

    <!-- Status Message -->
    <div v-if="statusMessage" :class="['px-6 py-3 text-sm', statusMessageClass]">
      {{ statusMessage }}
    </div>

    <!-- Main Content -->
    <div class="flex-1 flex overflow-hidden">
      <!-- Left Column - Tags -->
      <div class="w-1/3 flex flex-col border-r border-gray-200 dark:border-gray-700">
        <div class="p-4 bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700">
          <h2 class="text-lg font-semibold text-gray-900 dark:text-white mb-3">Tags</h2>

          <!-- Tag Search -->
          <div class="mb-3">
            <input
              v-model="tagSearchQuery"
              @input="setTagSearchQuery(tagSearchQuery)"
              type="text"
              placeholder="Search by tag name..."
              class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
            />
          </div>

          <!-- Tag Pagination Controls -->
          <div v-if="totalTagPages > 1" class="mb-4 flex items-center justify-between">
            <div class="flex items-center space-x-4">
              <div class="text-sm text-gray-700 dark:text-gray-300">
                Showing {{ paginatedTags.length }} of {{ totalTags }} tags
              </div>
              <div class="flex items-center space-x-2">
                <label class="text-sm text-gray-600 dark:text-gray-400">Page size:</label>
                <select
                  v-model="tagPageSize"
                  @change="setTagPageSize(tagPageSize)"
                  class="text-sm border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-white px-2 py-1"
                >
                  <option :value="10">10</option>
                  <option :value="20">20</option>
                  <option :value="50">50</option>
                  <option :value="100">100</option>
                </select>
              </div>
            </div>
            <div class="flex items-center space-x-2">
              <button
                @click="previousTagPage"
                :disabled="!hasPreviousTagPage || tagsLoading"
                class="px-3 py-1 text-sm border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="m15 19-7-7 7 7" />
                </svg>
              </button>

              <div class="flex items-center space-x-1">
                <button
                  v-for="page in Math.min(5, totalTagPages)"
                  :key="page"
                  @click="goToTagPage(page)"
                  :class="[
                  'px-3 py-1 text-sm border rounded-md',
                  page === currentTagPage
                    ? 'bg-blue-600 text-white border-blue-600'
                    : 'bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-300 border-gray-300 dark:border-gray-600 hover:bg-gray-50 dark:hover:bg-gray-700'
                ]"
                >
                  {{ page }}
                </button>
                <span v-if="totalTagPages > 5" class="px-2 text-gray-500">...</span>
                <button
                  v-if="totalTagPages > 5"
                  @click="goToTagPage(totalTagPages)"
                  :class="[
                  'px-3 py-1 text-sm border rounded-md',
                  totalTagPages === currentTagPage
                    ? 'bg-blue-600 text-white border-blue-600'
                    : 'bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-300 border-gray-300 dark:border-gray-600 hover:bg-gray-50 dark:hover:bg-gray-700'
                ]"
                >
                  {{ totalTagPages }}
                </button>
              </div>

              <button
                @click="nextTagPage"
                :disabled="!hasNextTagPage || tagsLoading"
                class="px-3 py-1 text-sm border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="m9 5 7 7 7" />
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
                </svg>
              </button>
            </div>
          </div>

          <!-- Select All Tags -->
          <label class="flex items-center mb-3">
            <input
              type="checkbox"
              v-model="selectAllTags"
              @change="toggleSelectAllTags"
              class="rounded border-gray-300 dark:border-gray-600 text-blue-600 focus:ring-blue-500 mr-2"
            />
            <span class="text-sm font-medium text-gray-700 dark:text-gray-300">
              Select All Tags (Current Page)
            </span>
          </label>

          <div v-if="tagsLoading" class="text-center py-4">
            <div class="inline-block animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600"></div>
            <p class="text-sm text-gray-600 dark:text-gray-400 mt-2">Loading tags...</p>
          </div>

          <div v-else class="space-y-2">
            <div
              v-for="tag in paginatedTags"
              :key="tag.name"
              class="flex items-center p-2 hover:bg-gray-50 dark:hover:bg-gray-700 rounded"
            >
              <input
                type="checkbox"
                :value="tag.name"
                v-model="selectedTags"
                class="mr-3 rounded border-gray-300 dark:border-gray-600 text-blue-600 focus:ring-blue-500"
              />
              <div class="flex-1">
                <div class="font-medium text-gray-900 dark:text-white flex items-center flex-wrap gap-2">
                  {{ tag.name }}
                  <span v-if="getTagTaxonomy(tag)"
                        class="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium border"
                        :style="getTaxonomyBadgeStyle(getTagTaxonomy(tag))">
                    {{ getTagTaxonomy(tag).name }}
                  </span>
                </div>
                <div class="text-sm text-gray-600 dark:text-gray-400">
                  Used by {{ tag.projectsCount || 0 }} projects
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Center Column - Selected Items -->
      <div class="w-1/3 flex flex-col border-r border-gray-200 dark:border-gray-700">
        <div class="p-4 bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700">
          <h2 class="text-lg font-semibold text-gray-900 dark:text-white mb-3">Selected Items</h2>

          <!-- Selected Tags Section -->
          <div class="mb-4">
            <h3 class="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Selected Tags ({{ selectedTags.length }})
            </h3>
            <div v-if="selectedTags.length === 0" class="text-sm text-gray-500 dark:text-gray-400 italic">
              No tags selected
            </div>
            <div v-else class="space-y-1">
              <div
                v-for="tagName in selectedTags"
                :key="tagName"
                class="flex items-center justify-between p-2 bg-gray-50 dark:bg-gray-700 rounded"
              >
                <span class="text-sm text-gray-900 dark:text-white">{{ tagName }}</span>
                <button
                  @click="toggleTagSelection(tagName)"
                  class="text-red-500 hover:text-red-700 text-xs"
                >
                  ✕
                </button>
              </div>
            </div>
          </div>

          <!-- Selected Projects Section -->
          <div>
            <h3 class="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Selected Projects ({{ selectedProjects.length }})
            </h3>
            <div v-if="selectedProjects.length === 0" class="text-sm text-gray-500 dark:text-gray-400 italic">
              No projects selected
            </div>
            <div v-else class="space-y-1">
              <div
                v-for="projectUuid in selectedProjects"
                :key="projectUuid"
                class="flex items-center justify-between p-2 bg-gray-50 dark:bg-gray-700 rounded"
              >
                <div class="flex-1">
                  <div class="text-sm font-medium text-gray-900 dark:text-white">
                    {{ getProjectName(projectUuid) }}
                  </div>
                  <div class="text-xs text-gray-600 dark:text-gray-400">
                    {{ getProjectVersion(projectUuid) }}
                  </div>
                </div>
                <button
                  @click="toggleProjectSelection(projectUuid)"
                  class="text-red-500 hover:text-red-700 text-xs ml-2"
                >
                  ✕
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Right Column - Projects -->
      <div class="w-1/3 flex flex-col bg-white dark:bg-gray-800">
        <div class="p-4 border-b border-gray-200 dark:border-gray-700">
          <h2 class="text-lg font-semibold text-gray-900 dark:text-white mb-3">Projects</h2>

          <!-- Project Search -->
          <div class="mb-3">
            <input
              v-model="projectSearchQuery"
              @input="setProjectSearchQuery(projectSearchQuery)"
              type="text"
              placeholder="Search by project name..."
              class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
            />
          </div>

          <!-- Active Filter -->
          <div class="mb-3 flex items-center">
            <input
              id="activeOnly"
              v-model="activeOnly"
              @change="setActiveFilter(activeOnly)"
              type="checkbox"
              class="rounded border-gray-300 dark:border-gray-600 text-blue-600 focus:ring-blue-500 mr-2"
            />
            <label for="activeOnly" class="text-sm text-gray-700 dark:text-gray-300">
              Active projects only
            </label>
          </div>

          <!-- Project Pagination Controls -->
          <div v-if="totalProjectPages > 1" class="mb-4 flex items-center justify-between">
            <div class="flex items-center space-x-4">
              <div class="text-sm text-gray-700 dark:text-gray-300">
                Showing {{ paginatedProjects.length }} of {{ totalProjects }} projects
              </div>
              <div class="flex items-center space-x-2">
                <label class="text-sm text-gray-600 dark:text-gray-400">Page size:</label>
                <select
                  v-model="projectPageSize"
                  @change="setProjectPageSize(projectPageSize)"
                  class="text-sm border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-white px-2 py-1"
                >
                  <option :value="10">10</option>
                  <option :value="20">20</option>
                  <option :value="50">50</option>
                  <option :value="100">100</option>
                </select>
              </div>
            </div>
            <div class="flex items-center space-x-2">
              <button
                @click="previousProjectPage"
                :disabled="!hasPreviousProjectPage || projectsLoading"
                class="px-3 py-1 text-sm border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="m15 19-7-7 7 7" />
                </svg>
              </button>

              <div class="flex items-center space-x-1">
                <button
                  v-for="page in Math.min(5, totalProjectPages)"
                  :key="page"
                  @click="goToProjectPage(page)"
                  :class="[
                  'px-3 py-1 text-sm border rounded-md',
                  page === currentProjectPage
                    ? 'bg-blue-600 text-white border-blue-600'
                    : 'bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-300 border-gray-300 dark:border-gray-600 hover:bg-gray-50 dark:hover:bg-gray-700'
              ]"
                >
                  {{ page }}
                </button>
                <span v-if="totalProjectPages > 5" class="px-2 text-gray-500">...</span>
                <button
                  v-if="totalProjectPages > 5"
                  @click="goToProjectPage(totalProjectPages)"
                  :class="[
                  'px-3 py-1 text-sm border rounded-md',
                  totalProjectPages === currentProjectPage
                    ? 'bg-blue-600 text-white border-blue-600'
                    : 'bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-300 border-gray-300 dark:border-gray-600 hover:bg-gray-50 dark:hover:bg-gray-700'
              ]"
                >
                  {{ totalProjectPages }}
                </button>
              </div>

              <button
                @click="nextProjectPage"
                :disabled="!hasNextProjectPage || projectsLoading"
                class="px-3 py-1 text-sm border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="m9 5 7 7 7" />
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
                </svg>
              </button>
            </div>
          </div>

          <!-- Select All Projects -->
          <label class="flex items-center">
            <input
              type="checkbox"
              v-model="selectAllProjects"
              @change="toggleSelectAllProjects"
              class="rounded border-gray-300 dark:border-gray-600 text-blue-600 focus:ring-blue-500 mr-2"
            />
            <span class="text-sm font-medium text-gray-700 dark:text-gray-300">
              Select All Projects (Current Page)
            </span>
          </label>
        </div>

        <div v-if="projectsLoading" class="text-center py-4 px-4 bg-white dark:bg-gray-800">
          <div class="inline-block animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600"></div>
          <p class="text-sm text-gray-600 dark:text-gray-400 mt-2">Loading projects...</p>
        </div>

        <div v-else class="flex-1 overflow-y-auto px-4 pb-4 bg-white dark:bg-gray-800">
          <div class="space-y-2">
            <div
              v-for="project in paginatedProjects"
              :key="project.uuid"
              class="flex items-center p-2 hover:bg-gray-50 dark:hover:bg-gray-700 rounded"
            >
              <input
                type="checkbox"
                :value="project.uuid"
                v-model="selectedProjects"
                class="mr-3 rounded border-gray-300 dark:border-gray-600 text-blue-600 focus:ring-blue-500"
              />
              <div class="flex-1">
                <div class="font-medium text-gray-900 dark:text-white">
                  {{ project.displayName || project.name }}
                </div>
                <div class="text-sm text-gray-600 dark:text-gray-400">
                  Version: {{ project.version }}
                  <span class="ml-2" :class="getActivityStatusClass(project)">
                    {{ getActivityStatus(project) }}
                  </span>
                </div>
                <div v-if="project.tags && project.tags.length > 0" class="text-sm text-gray-600 dark:text-gray-400">
                  Tags: {{ project.tags.join(', ') }}
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Link Confirmation Modal -->
    <div v-if="showLinkConfirmation" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-white dark:bg-gray-800 rounded-lg p-6 max-w-md w-full mx-4">
        <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">Confirm Link Action</h3>
        <p class="text-gray-600 dark:text-gray-400 mb-6">
          Are you sure you want to link {{ selectedTags.length }} tag(s) to {{ selectedProjects.length }} project(s)?
        </p>
        <div class="flex justify-end space-x-3">
          <button
            @click="showLinkConfirmation = false"
            class="px-4 py-2 bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-md hover:bg-gray-300 dark:hover:bg-gray-600 transition-colors"
          >
            Cancel
          </button>
          <button
            @click="confirmLink"
            :disabled="loading"
            class="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
          >
            Link
          </button>
        </div>
      </div>
    </div>

    <!-- Unlink Confirmation Modal -->
    <div v-if="showUnlinkConfirmation" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-white dark:bg-gray-800 rounded-lg p-6 max-w-md w-full mx-4">
        <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">Confirm Unlink Action</h3>
        <p class="text-gray-600 dark:text-gray-400 mb-6">
          Are you sure you want to unlink {{ selectedTags.length }} tag(s) from {{ selectedProjects.length }} project(s)?
        </p>
        <div class="flex justify-end space-x-3">
          <button
            @click="showUnlinkConfirmation = false"
            class="px-4 py-2 bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-md hover:bg-gray-300 dark:hover:bg-gray-600 transition-colors"
          >
            Cancel
          </button>
          <button
            @click="confirmUnlink"
            :disabled="loading"
            class="px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
          >
            Unlink
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted, watch } from 'vue'
import { storeToRefs } from 'pinia'
import { useTaxonomyStore } from '../stores/taxonomies'
import { useTagStore } from '../stores/tags'
import { useProjectStore } from '../stores/projects'
import { useToast } from '../composables/useToast'
import { X, Link, Unlink, RefreshCw, Folder } from 'lucide-vue-next'
import { buildDTProjectUrl } from '../config.js'
import axios from 'axios'

export default {
  name: 'TagBulkActions',
  components: {
    RefreshCw,
    Link,
    Unlink,
    X,
    Folder
  },
  setup() {
    // Use stores
    const taxonomyStore = useTaxonomyStore()
    const tagStore = useTagStore()
    const projectStore = useProjectStore()
    const { showSuccess, showError } = useToast()

    // Use taxonomy store
    const { taxonomies, loading: taxonomiesLoading } = storeToRefs(taxonomyStore)
    const { getTaxonomyBadgeStyle, getTagTaxonomy, loadTaxonomies } = taxonomyStore

    // Use tag store
    const {
      tags,
      isLoading: tagsLoading,
      error: tagsError,
      currentPage: currentTagPage,
      pageSize: tagPageSize,
      totalTags,
      totalPages: totalTagPages,
      searchQuery: tagSearchQuery,
      filteredTags,
      paginatedTags,
      hasPreviousPage: hasPreviousTagPage,
      hasNextPage: hasNextTagPage
    } = storeToRefs(tagStore)

    const {
      loadTags,
      setSearchQuery: setTagSearchQuery,
      goToPage: goToTagPage,
      nextPage: nextTagPage,
      previousPage: previousTagPage,
      clearFilters: clearTagFilters,
      setPageSize: setTagPageSize
    } = tagStore

    // Use project store
    const {
      projects,
      isLoading: projectsLoading,
      error: projectsError,
      currentPage: currentProjectPage,
      pageSize: projectPageSize,
      totalProjects,
      totalPages: totalProjectPages,
      searchQuery: projectSearchQuery,
      filteredProjects,
      paginatedProjects,
      hasPreviousPage: hasPreviousProjectPage,
      hasNextPage: hasNextProjectPage,
      activeOnly
    } = storeToRefs(projectStore)

    const {
      loadProjects,
      setSearchQuery: setProjectSearchQuery,
      setActiveFilter,
      goToPage: goToProjectPage,
      nextPage: nextProjectPage,
      previousPage: previousProjectPage,
      clearFilters: clearProjectFilters,
      getActivityStatus,
      getActivityStatusClass,
      setPageSize: setProjectPageSize
    } = projectStore

    // Local state
    const selectedTags = ref([])
    const selectedProjects = ref([])
    const selectAllTags = ref(false)
    const selectAllProjects = ref(false)
    const showLinkConfirmation = ref(false)
    const showUnlinkConfirmation = ref(false)
    const statusMessage = ref('')
    const statusMessageClass = ref('')
    const loading = ref(false)

    // Local methods
    const toggleSelectAllTags = () => {
      if (selectAllTags.value) {
        selectedTags.value = paginatedTags.value.map(tag => tag.name)
      } else {
        selectedTags.value = []
      }
    }

    const toggleSelectAllProjects = () => {
      if (selectAllProjects.value) {
        selectedProjects.value = paginatedProjects.value.map(project => project.uuid)
      } else {
        selectedProjects.value = []
      }
    }

    const getProjectName = (projectUuid) => {
      const project = projects.value.find(p => p.uuid === projectUuid)
      return project ? (project.displayName || project.name) : 'Unknown Project'
    }

    const getProjectVersion = (projectUuid) => {
      const project = projects.value.find(p => p.uuid === projectUuid)
      return project ? project.version : 'Unknown'
    }

    const toggleTagSelection = (tagName) => {
      const index = selectedTags.value.indexOf(tagName)
      if (index > -1) {
        selectedTags.value.splice(index, 1)
      } else {
        selectedTags.value.push(tagName)
      }
    }

    const toggleProjectSelection = (projectUuid) => {
      const index = selectedProjects.value.indexOf(projectUuid)
      if (index > -1) {
        selectedProjects.value.splice(index, 1)
      } else {
        selectedProjects.value.push(projectUuid)
      }
    }

    const confirmLink = async () => {
      showLinkConfirmation.value = false
      statusMessage.value = ''
      statusMessageClass.value = ''
      loading.value = true

      try {
        const response = await axios.post('/api/tags/link', {
          tags: selectedTags.value,
          projects: selectedProjects.value
        })

        statusMessage.value = `Successfully linked ${selectedTags.value.length} tags to ${selectedProjects.value.length} projects`
        statusMessageClass.value = 'text-green-600 dark:text-green-400'

        // Reload data to reflect changes
        await refreshData()
      } catch (error) {
        console.error('Error linking tags to projects:', error)
        statusMessage.value = 'Error linking tags to projects'
        statusMessageClass.value = 'text-red-600 dark:text-red-400'
      } finally {
        loading.value = false
      }
    }

    const confirmUnlink = async () => {
      showUnlinkConfirmation.value = false
      statusMessage.value = ''
      statusMessageClass.value = ''
      loading.value = true

      try {
        const response = await axios.post('/api/tags/unlink', {
          tags: selectedTags.value,
          projects: selectedProjects.value
        })

        statusMessage.value = `Successfully unlinked ${selectedTags.value.length} tags from ${selectedProjects.value.length} projects`
        statusMessageClass.value = 'text-green-600 dark:text-green-400'

        // Reload data to reflect changes
        await refreshData()
      } catch (error) {
        console.error('Error unlinking tags from projects:', error)
        statusMessage.value = 'Error unlinking tags from projects'
        statusMessageClass.value = 'text-red-600 dark:text-red-400'
      } finally {
        loading.value = false
      }
    }

    const buildDTProjectUrl = (projectUuid) => {
      const project = projects.value.find(p => p.uuid === projectUuid)
      if (!project) return '#'
      return buildDTProjectUrl(project.name, project.version)
    }

    const clearSelection = () => {
      selectedTags.value = []
      selectedProjects.value = []
      selectAllTags.value = false
      selectAllProjects.value = false
    }

    const refreshData = async () => {
      loading.value = true
      try {
        await Promise.all([loadTaxonomies(), loadTags(), loadProjects()])
        clearSelection()
      } finally {
        loading.value = false
      }
    }

    // Watchers for select all checkboxes
    watch(paginatedTags, () => {
      selectAllTags.value = paginatedTags.value.length > 0 &&
        paginatedTags.value.every(tag => selectedTags.value.includes(tag.name))
    })

    watch(paginatedProjects, () => {
      selectAllProjects.value = paginatedProjects.value.length > 0 &&
        paginatedProjects.value.every(project => selectedProjects.value.includes(project.uuid))
    })

    // Lifecycle
    onMounted(() => {
      refreshData()
    })

    return {
      // Local state
      loading,
      selectedTags,
      selectedProjects,
      selectAllTags,
      selectAllProjects,
      showLinkConfirmation,
      showUnlinkConfirmation,
      statusMessage,
      statusMessageClass,

      // Store states
      tags,
      projects,
      tagsLoading,
      projectsLoading,
      tagsError,
      projectsError,

      // Store pagination states
      currentTagPage,
      currentProjectPage,
      tagPageSize,
      projectPageSize,
      totalTags,
      totalProjects,
      totalTagPages,
      totalProjectPages,
      tagSearchQuery,
      projectSearchQuery,
      filteredTags,
      filteredProjects,
      paginatedTags,
      paginatedProjects,
      hasPreviousTagPage,
      hasNextTagPage,
      hasPreviousProjectPage,
      hasNextProjectPage,
      activeOnly,

      // Store methods
      loadTags,
      loadProjects,
      setTagSearchQuery,
      setProjectSearchQuery,
      setActiveFilter,
      goToTagPage,
      goToProjectPage,
      nextTagPage,
      nextProjectPage,
      previousTagPage,
      previousProjectPage,
      clearTagFilters,
      clearProjectFilters,
      getActivityStatus,
      getActivityStatusClass,
      setTagPageSize,
      setProjectPageSize,

      // Taxonomy store functions
      taxonomies,
      getTagTaxonomy,
      getTaxonomyBadgeStyle,

      // Local methods
      toggleSelectAllTags,
      toggleSelectAllProjects,
      getProjectName,
      getProjectVersion,
      toggleTagSelection,
      toggleProjectSelection,
      confirmLink,
      confirmUnlink,
      buildDTProjectUrl,
      refreshData
    }
  }
}
</script>
