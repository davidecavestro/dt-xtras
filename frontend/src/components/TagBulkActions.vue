<template>
  <div class="px-4 py-6 sm:px-0">
    <div class="bg-white dark:bg-gray-800 shadow overflow-hidden sm:rounded-md">
      <!-- Header -->
      <div class="px-4 py-5 sm:px-6 border-b border-gray-200 dark:border-gray-700">
        <div class="flex justify-between items-center">
          <div>
            <h1 class="text-2xl font-bold text-gray-900 dark:text-white">Tag Bulk Actions</h1>
            <p class="mt-1 text-sm text-gray-600 dark:text-gray-400">
              Manage multiple tags at once with bulk operations for linking and unlinking projects.
            </p>
          </div>
          <div class="flex space-x-3">
            <button
              @click="refreshData"
              :disabled="loading"
              class="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50"
            >
              <RefreshCw class="mr-2 h-4 w-4" :class="{ 'animate-spin': loading }" />
              Refresh
            </button>
          </div>
        </div>
      </div>

      <!-- Tag Selection -->
      <div class="px-4 py-4 sm:px-6 border-b border-gray-200 dark:border-gray-700">
        <div class="flex justify-between items-center mb-4">
          <h2 class="text-lg font-semibold text-gray-900 dark:text-white">Select Tags</h2>
          <div class="text-sm text-gray-600 dark:text-gray-400">
            {{ selectedTags.length }} of {{ totalTags }} tags selected
            <span v-if="totalTagPages > 1"> (Page {{ currentTagPage }} of {{ totalTagPages }})</span>
          </div>
        </div>

        <!-- Tag Search -->
        <div class="mb-4">
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Search Tags
          </label>
          <input
            v-model="tagSearchQuery"
            type="text"
            placeholder="Search by tag name..."
            class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
          />
        </div>

        <!-- Tags Grid -->
        <div class="border border-gray-300 dark:border-gray-600 rounded-md max-h-64 overflow-y-auto">
          <div class="p-2">
            <label class="flex items-center mb-2">
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

            <div v-if="loadingTags" class="text-center py-4">
              <div class="inline-block animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600"></div>
              <p class="text-sm text-gray-600 dark:text-gray-400 mt-2">Loading tags...</p>
            </div>

            <div v-else class="space-y-2">
              <div
                v-for="tag in filteredTags"
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
                  <div class="font-medium text-gray-900 dark:text-white">
                    {{ tag.name }}
                    <span v-if="tag.custom" class="ml-2 text-xs text-gray-500 dark:text-gray-400">(custom)</span>
                  </div>
                  <div class="text-sm text-gray-600 dark:text-gray-400">
                    Used by {{ tag.projectsCount || 0 }} projects
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Tag Pagination Controls -->
        <div v-if="totalTagPages > 1" class="mt-4 flex items-center justify-between">
          <div class="text-sm text-gray-700 dark:text-gray-300">
            Showing {{ tags.length }} of {{ totalTags }} tags
          </div>
          <div class="flex items-center space-x-2">
            <button
              @click="prevTagPage"
              :disabled="currentTagPage === 1 || loadingTags"
              class="px-3 py-1 text-sm border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Previous
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
              :disabled="currentTagPage === totalTagPages || loadingTags"
              class="px-3 py-1 text-sm border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Next
            </button>
          </div>
        </div>
      </div>

      <!-- Project Selection -->
      <div class="px-4 py-4 sm:px-6 border-b border-gray-200 dark:border-gray-700">
        <div class="flex justify-between items-center mb-4">
          <h2 class="text-lg font-semibold text-gray-900 dark:text-white">Select Projects</h2>
          <div class="text-sm text-gray-600 dark:text-gray-400">
            {{ selectedProjects.length }} of {{ totalProjects }} projects selected
            <span v-if="totalProjectPages > 1"> (Page {{ currentProjectPage }} of {{ totalProjectPages }})</span>
          </div>
        </div>

        <!-- Project Search -->
        <div class="mb-4">
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Search Projects
          </label>
          <input
            v-model="projectSearchQuery"
            type="text"
            placeholder="Search by project name or tags..."
            class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
          />

          <!-- Active/Inactive Filter -->
          <div class="mt-3 flex items-center">
            <input
              type="checkbox"
              id="activeOnly"
              v-model="activeOnly"
              class="rounded border-gray-300 dark:border-gray-600 text-blue-600 focus:ring-blue-500 mr-2"
            />
            <label for="activeOnly" class="text-sm text-gray-700 dark:text-gray-300">
              Active projects only
            </label>
          </div>
        </div>

        <!-- Projects Grid -->
        <div class="border border-gray-300 dark:border-gray-600 rounded-md max-h-64 overflow-y-auto">
          <div class="p-2">
            <label class="flex items-center mb-2">
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

            <div v-if="loadingProjects" class="text-center py-4">
              <div class="inline-block animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600"></div>
              <p class="text-sm text-gray-600 dark:text-gray-400 mt-2">Loading projects...</p>
            </div>

            <div v-else class="space-y-2">
              <div
                v-for="project in filteredProjects"
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
                    <a
                      :href="buildDTProjectUrl(project.uuid)"
                      target="_blank"
                      class="text-blue-600 hover:text-blue-800 hover:underline"
                      title="View in Dependency Track"
                    >
                      {{ project.displayName }}
                    </a>
                  </div>
                  <div class="text-sm text-gray-600 dark:text-gray-400">
                    {{ project.name }} v{{ project.version }}
                    <div v-if="project.tags && project.tags.length > 0" class="mt-1">
                      Current tags: {{ project.tags.join(', ') }}
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Project Pagination Controls -->
        <div v-if="totalProjectPages > 1" class="mt-4 flex items-center justify-between">
          <div class="text-sm text-gray-700 dark:text-gray-300">
            Showing {{ projects.length }} of {{ totalProjects }} projects
          </div>
          <div class="flex items-center space-x-2">
            <button
              @click="prevProjectPage"
              :disabled="currentProjectPage === 1 || loadingProjects"
              class="px-3 py-1 text-sm border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Previous
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
              :disabled="currentProjectPage === totalProjectPages || loadingProjects"
              class="px-3 py-1 text-sm border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Next
            </button>
          </div>
        </div>
      </div>

      <!-- Bulk Actions -->
      <div class="px-4 py-4 sm:px-6">
        <div class="flex flex-wrap gap-3">
          <!-- Link Tags to Projects -->
          <button
            @click="showLinkConfirmation = true"
            :disabled="selectedTags.length === 0 || selectedProjects.length === 0"
            class="px-4 py-2 border border-green-300 text-sm font-medium rounded-md text-green-700 bg-green-50 hover:bg-green-100 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <Link class="mr-2 h-4 w-4" />
            Link Tags to Projects
            <span class="ml-2 text-xs bg-green-200 dark:bg-green-800 px-2 py-1 rounded">
              {{ selectedTags.length }} tags → {{ selectedProjects.length }} projects
            </span>
          </button>

          <!-- Unlink Tags from Projects -->
          <button
            @click="showUnlinkConfirmation = true"
            :disabled="selectedTags.length === 0 || selectedProjects.length === 0"
            class="px-4 py-2 border border-orange-300 text-sm font-medium rounded-md text-orange-700 bg-orange-50 hover:bg-orange-100 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-orange-500 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <Unlink class="mr-2 h-4 w-4" />
            Unlink Tags from Projects
            <span class="ml-2 text-xs bg-orange-200 dark:bg-orange-800 px-2 py-1 rounded">
              {{ selectedTags.length }} tags ← {{ selectedProjects.length }} projects
            </span>
          </button>

          <!-- Clear Selection -->
          <button
            @click="clearSelection"
            class="px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-gray-50 hover:bg-gray-100 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-gray-500"
          >
            <X class="mr-2 h-4 w-4" />
            Clear Selection
          </button>
        </div>

        <!-- Status Messages -->
        <div v-if="statusMessage" class="mt-4 p-3 rounded-md" :class="statusMessageClass">
          {{ statusMessage }}
        </div>
      </div>
    </div>

    <!-- Link Confirmation Modal -->
    <div
      v-if="showLinkConfirmation"
      class="fixed inset-0 z-50 overflow-y-auto"
      aria-labelledby="modal-title"
      role="dialog"
      aria-modal="true"
    >
      <div class="flex items-end justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0">
        <div class="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity" aria-hidden="true"></div>
        <span class="hidden sm:inline-block sm:align-middle sm:h-screen" aria-hidden="true">&#8203;</span>
        <div class="inline-block align-bottom bg-white dark:bg-gray-800 rounded-lg text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-lg sm:w-full">
          <div class="bg-white dark:bg-gray-800 px-4 pt-5 pb-4 sm:p-6 sm:pb-4">
            <div class="sm:flex sm:items-start">
              <div class="mx-auto flex-shrink-0 flex items-center justify-center h-12 w-12 rounded-full bg-green-100 dark:bg-green-900 sm:mx-0 sm:h-10 sm:w-10">
                <Link class="h-6 w-6 text-green-600 dark:text-green-400" />
              </div>
              <div class="mt-3 text-center sm:mt-0 sm:ml-4 sm:text-left">
                <h3 class="text-lg leading-6 font-medium text-gray-900 dark:text-white" id="modal-title">
                  Link Tags to Projects
                </h3>
                <div class="mt-2">
                  <p class="text-sm text-gray-500 dark:text-gray-400">
                    Are you sure you want to link {{ selectedTags.length }} tag(s) to {{ selectedProjects.length }} project(s)?
                  </p>
                  <div class="mt-3 space-y-2">
                    <div>
                      <strong>Tags to link:</strong>
                      <ul class="text-sm text-gray-600 dark:text-gray-400 ml-4">
                        <li v-for="tagName in selectedTags" :key="tagName" class="py-1">
                          • {{ tagName }}
                        </li>
                      </ul>
                    </div>
                    <div>
                      <strong>Projects to affect:</strong>
                      <ul class="text-sm text-gray-600 dark:text-gray-400 ml-4">
                        <li v-for="projectUuid in selectedProjects" :key="projectUuid" class="py-1">
                          • {{ getProjectName(projectUuid) }}
                        </li>
                      </ul>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
          <div class="bg-gray-50 dark:bg-gray-700 px-4 py-3 sm:px-6 sm:flex sm:flex-row-reverse">
            <button
              @click="confirmLink"
              type="button"
              class="w-full inline-flex justify-center rounded-md border border-transparent shadow-sm px-4 py-2 bg-green-600 text-base font-medium text-white hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500 sm:ml-3 sm:w-auto sm:text-sm"
            >
              Link Tags
            </button>
            <button
              @click="showLinkConfirmation = false"
              type="button"
              class="mt-3 w-full inline-flex justify-center rounded-md border border-gray-300 dark:border-gray-600 shadow-sm px-4 py-2 bg-white dark:bg-gray-800 text-base font-medium text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 sm:mt-0 sm:ml-3 sm:w-auto sm:text-sm"
            >
              Cancel
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Unlink Confirmation Modal -->
    <div
      v-if="showUnlinkConfirmation"
      class="fixed inset-0 z-50 overflow-y-auto"
      aria-labelledby="modal-title"
      role="dialog"
      aria-modal="true"
    >
      <div class="flex items-end justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0">
        <div class="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity" aria-hidden="true"></div>
        <span class="hidden sm:inline-block sm:align-middle sm:h-screen" aria-hidden="true">&#8203;</span>
        <div class="inline-block align-bottom bg-white dark:bg-gray-800 rounded-lg text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-lg sm:w-full">
          <div class="bg-white dark:bg-gray-800 px-4 pt-5 pb-4 sm:p-6 sm:pb-4">
            <div class="sm:flex sm:items-start">
              <div class="mx-auto flex-shrink-0 flex items-center justify-center h-12 w-12 rounded-full bg-orange-100 dark:bg-orange-900 sm:mx-0 sm:h-10 sm:w-10">
                <Unlink class="h-6 w-6 text-orange-600 dark:text-orange-400" />
              </div>
              <div class="mt-3 text-center sm:mt-0 sm:ml-4 sm:text-left">
                <h3 class="text-lg leading-6 font-medium text-gray-900 dark:text-white" id="modal-title">
                  Unlink Tags from Projects
                </h3>
                <div class="mt-2">
                  <p class="text-sm text-gray-500 dark:text-gray-400">
                    Are you sure you want to unlink {{ selectedTags.length }} tag(s) from {{ selectedProjects.length }} project(s)?
                  </p>
                  <div class="mt-3 space-y-2">
                    <div>
                      <strong>Tags to unlink:</strong>
                      <ul class="text-sm text-gray-600 dark:text-gray-400 ml-4">
                        <li v-for="tagName in selectedTags" :key="tagName" class="py-1">
                          • {{ tagName }}
                        </li>
                      </ul>
                    </div>
                    <div>
                      <strong>Projects to affect:</strong>
                      <ul class="text-sm text-gray-600 dark:text-gray-400 ml-4">
                        <li v-for="projectUuid in selectedProjects" :key="projectUuid" class="py-1">
                          • {{ getProjectName(projectUuid) }}
                        </li>
                      </ul>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
          <div class="bg-gray-50 dark:bg-gray-700 px-4 py-3 sm:px-6 sm:flex sm:flex-row-reverse">
            <button
              @click="confirmUnlink"
              type="button"
              class="w-full inline-flex justify-center rounded-md border border-transparent shadow-sm px-4 py-2 bg-orange-600 text-base font-medium text-white hover:bg-orange-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-orange-500 sm:ml-3 sm:w-auto sm:text-sm"
            >
              Unlink Tags
            </button>
            <button
              @click="showUnlinkConfirmation = false"
              type="button"
              class="mt-3 w-full inline-flex justify-center rounded-md border border-gray-300 dark:border-gray-600 shadow-sm px-4 py-2 bg-white dark:bg-gray-800 text-base font-medium text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 sm:mt-0 sm:ml-3 sm:w-auto sm:text-sm"
            >
              Cancel
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted, watch } from 'vue'
import axios from 'axios'
import { buildDTProjectUrl } from '../config.js'
import { RefreshCw, Link, Unlink, X } from 'lucide-vue-next'

export default {
  name: 'TagBulkActions',
  components: {
    RefreshCw,
    Link,
    Unlink,
    X
  },
  setup() {
    // State
    const loading = ref(false)
    const loadingTags = ref(false)
    const loadingProjects = ref(false)
    const tags = ref([])
    const projects = ref([])
    const selectedTags = ref([])
    const selectedProjects = ref([])
    const tagSearchQuery = ref('')
    const projectSearchQuery = ref('')
    const activeOnly = ref(false)
    const selectAllTags = ref(false)
    const selectAllProjects = ref(false)
    const showLinkConfirmation = ref(false)
    const showUnlinkConfirmation = ref(false)
    const statusMessage = ref('')
    const statusMessageClass = ref('')

    // Pagination state
    const currentTagPage = ref(1)
    const currentProjectPage = ref(1)
    const pageSize = ref(20)
    const totalTags = ref(0)
    const totalProjects = ref(0)
    const totalTagPages = ref(1)
    const totalProjectPages = ref(1)

    // Computed properties
    const filteredTags = computed(() => {
      if (!tagSearchQuery.value) return tags.value

      const query = tagSearchQuery.value.toLowerCase()
      return tags.value.filter(tag =>
        tag.name.toLowerCase().includes(query)
      )
    })

    const filteredProjects = computed(() => {
      if (!projectSearchQuery.value) return projects.value

      const query = projectSearchQuery.value.toLowerCase()
      return projects.value.filter(project =>
        project.name.toLowerCase().includes(query) ||
        project.displayName.toLowerCase().includes(query) ||
        (project.tags && project.tags.some(tag => tag.toLowerCase().includes(query)))
      )
    })

    // Methods
    const loadTags = async () => {
      loadingTags.value = true
      try {
        const params = {
          page: currentTagPage.value,
          limit: pageSize.value
        }

        // Add search parameter if exists
        if (tagSearchQuery.value) {
          params.search = tagSearchQuery.value
        }

        const response = await axios.get('/api/tags', { params })
        tags.value = response.data

        // For tags, we'll use a simpler approach without count endpoint
        // Assume we have more pages if we get a full page
        totalTags.value = tags.value.length >= pageSize.value ?
          (currentTagPage.value * pageSize.value) + 1 :
          ((currentTagPage.value - 1) * pageSize.value) + tags.value.length
        totalTagPages.value = tags.value.length >= pageSize.value ?
          currentTagPage.value + 1 :
          currentTagPage.value
      } catch (error) {
        console.error('Error loading tags:', error)
        tags.value = []
        totalTags.value = 0
        totalTagPages.value = 1
      } finally {
        loadingTags.value = false
      }
    }

    const loadProjects = async () => {
      loadingProjects.value = true
      try {
        const params = {
          page: currentProjectPage.value,
          limit: pageSize.value
        }

        // Add search parameter if exists
        if (projectSearchQuery.value) {
          params.search = projectSearchQuery.value
        }

        // Add active/inactive filter
        if (activeOnly.value) {
          params.active_only = true
        }

        const response = await axios.get('/api/projects', { params })
        projects.value = response.data.map(project => ({
          id: project.uuid,
          uuid: project.uuid,
          name: project.name,
          version: project.version || 'latest',
          displayName: project.version ? `${project.name}:${project.version}` : `${project.name}:latest`,
          tags: project.tags || [],
          active: project.active
        }))

        // Get total count for pagination
        try {
          const countParams = {}
          if (projectSearchQuery.value) {
            countParams.search = projectSearchQuery.value
          }
          if (activeOnly.value) {
            countParams.active_only = true
          }

          const countResponse = await axios.get('/api/projects/count', {
            params: countParams
          })
          totalProjects.value = countResponse.data.total
          totalProjectPages.value = Math.ceil(totalProjects.value / pageSize.value)
        } catch (countError) {
          console.warn('Could not get project count:', countError)
          // Fallback: assume current page has full results
          totalProjects.value = projects.value.length
          totalProjectPages.value = 1
        }
      } catch (error) {
        console.error('Error loading projects:', error)
        projects.value = []
      } finally {
        loadingProjects.value = false
      }
    }

    const refreshData = async () => {
      loading.value = true
      try {
        await Promise.all([loadTags(), loadProjects()])
        clearSelection()
      } finally {
        loading.value = false
      }
    }

    // Tag pagination methods
    const prevTagPage = () => {
      if (currentTagPage.value > 1) {
        currentTagPage.value--
        loadTags()
      }
    }

    const nextTagPage = () => {
      if (currentTagPage.value < totalTagPages.value) {
        currentTagPage.value++
        loadTags()
      }
    }

    const goToTagPage = (page) => {
      currentTagPage.value = page
      loadTags()
    }

    // Project pagination methods
    const prevProjectPage = () => {
      if (currentProjectPage.value > 1) {
        currentProjectPage.value--
        loadProjects()
      }
    }

    const nextProjectPage = () => {
      if (currentProjectPage.value < totalProjectPages.value) {
        currentProjectPage.value++
        loadProjects()
      }
    }

    const goToProjectPage = (page) => {
      currentProjectPage.value = page
      loadProjects()
    }

    const toggleSelectAllTags = () => {
      if (selectAllTags.value) {
        selectedTags.value = filteredTags.value.map(tag => tag.name)
      } else {
        selectedTags.value = []
      }
    }

    const toggleSelectAllProjects = () => {
      if (selectAllProjects.value) {
        selectedProjects.value = filteredProjects.value.map(project => project.uuid)
      } else {
        selectedProjects.value = []
      }
    }

    const getProjectName = (projectUuid) => {
      const project = projects.value.find(p => p.uuid === projectUuid)
      return project ? project.displayName : projectUuid.slice(0, 8) + '...'
    }

    const clearSelection = () => {
      selectedTags.value = []
      selectedProjects.value = []
      selectAllTags.value = false
      selectAllProjects.value = false
      tagSearchQuery.value = ''
      projectSearchQuery.value = ''
      activeOnly.value = false
      currentTagPage.value = 1
      currentProjectPage.value = 1
      statusMessage.value = ''
    }

    const showStatus = (message, isError = false) => {
      statusMessage.value = message
      statusMessageClass.value = isError
        ? 'bg-red-100 dark:bg-red-900 text-red-800 dark:text-red-200 border border-red-200 dark:border-red-800'
        : 'bg-green-100 dark:bg-green-900 text-green-800 dark:text-green-200 border border-green-200 dark:border-green-800'

      setTimeout(() => {
        statusMessage.value = ''
      }, 5000)
    }

    const confirmLink = async () => {
      showLinkConfirmation.value = false

      try {
        for (const tagName of selectedTags.value) {
          const response = await axios.post(`/api/v1/tag/${tagName}/project`, selectedProjects.value)

          if (response.status === 204) {
            // Update local project tags
            selectedProjects.value.forEach(projectUuid => {
              const project = projects.value.find(p => p.uuid === projectUuid)
              if (project && !project.tags.includes(tagName)) {
                project.tags.push(tagName)
              }
            })
          }
        }

        await refreshData()
        showStatus(`Successfully linked ${selectedTags.value.length} tag(s) to ${selectedProjects.value.length} project(s)`)
      } catch (error) {
        console.error('Error linking tags:', error)
        showStatus('Failed to link tags to projects. Please try again.', true)
      }
    }

    const confirmUnlink = async () => {
      showUnlinkConfirmation.value = false

      try {
        for (const tagName of selectedTags.value) {
          const response = await axios.delete(`/api/v1/tag/${tagName}/project`, {
            data: selectedProjects.value
          })

          if (response.status === 204) {
            // Update local project tags
            selectedProjects.value.forEach(projectUuid => {
              const project = projects.value.find(p => p.uuid === projectUuid)
              if (project) {
                project.tags = project.tags.filter(tag => tag !== tagName)
              }
            })
          }
        }

        await refreshData()
        showStatus(`Successfully unlinked ${selectedTags.value.length} tag(s) from ${selectedProjects.value.length} project(s)`)
      } catch (error) {
        console.error('Error unlinking tags:', error)
        showStatus('Failed to unlink tags from projects. Please try again.', true)
      }
    }

    // Lifecycle
    onMounted(() => {
      refreshData()
    })

    // Watchers for search queries and filters
    watch(tagSearchQuery, () => {
      currentTagPage.value = 1
      loadTags()
    })

    watch(projectSearchQuery, () => {
      currentProjectPage.value = 1
      loadProjects()
    })

    watch(activeOnly, () => {
      currentProjectPage.value = 1
      loadProjects()
    })

    return {
      loading,
      loadingTags,
      loadingProjects,
      tags,
      projects,
      selectedTags,
      selectedProjects,
      tagSearchQuery,
      projectSearchQuery,
      activeOnly,
      selectAllTags,
      selectAllProjects,
      showLinkConfirmation,
      showUnlinkConfirmation,
      statusMessage,
      statusMessageClass,
      // Pagination state
      currentTagPage,
      currentProjectPage,
      totalTags,
      totalProjects,
      totalTagPages,
      totalProjectPages,
      filteredTags,
      filteredProjects,
      refreshData,
      // Tag pagination methods
      prevTagPage,
      nextTagPage,
      goToTagPage,
      // Project pagination methods
      prevProjectPage,
      nextProjectPage,
      goToProjectPage,
      toggleSelectAllTags,
      toggleSelectAllProjects,
      getProjectName,
      clearSelection,
      confirmLink,
      confirmUnlink,
      buildDTProjectUrl
    }
  }
}
</script>
