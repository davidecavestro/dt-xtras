<template>
  <div class="px-4 py-6 sm:px-0">
    <div class="bg-white dark:bg-gray-800 shadow overflow-hidden sm:rounded-md">
      <!-- Header -->
      <div class="px-4 py-5 sm:px-6 border-b border-gray-200 dark:border-gray-700">
        <div class="flex justify-between items-center">
          <div>
            <h1 class="text-2xl font-bold text-gray-900 dark:text-white">Project Bulk Actions</h1>
            <p class="mt-1 text-sm text-gray-600 dark:text-gray-400">
              Manage multiple projects at once with bulk operations for cleanup, activation, and maintenance.
            </p>
          </div>
          <div class="flex space-x-3">
            <button
              @click="refreshProjects"
              :disabled="loading"
              class="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50"
            >
              <RefreshCw class="mr-2 h-4 w-4" :class="{ 'animate-spin': loading }" />
              Refresh
            </button>
          </div>
        </div>
      </div>

      <!-- Filters -->
      <div class="px-4 py-4 sm:px-6 border-b border-gray-200 dark:border-gray-700">
        <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
          <!-- Search -->
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Search Projects
            </label>
            <input
              v-model="searchQuery"
              type="text"
              placeholder="Search by name or tags..."
              class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
            />
          </div>

          <!-- Activity Filter -->
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Activity Status
            </label>
            <select
              v-model="activityFilter"
              class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
            >
              <option value="all">All Projects</option>
              <option value="active-dt">Active (DT)</option>
              <option value="inactive-dt">Inactive (DT)</option>
              <option value="recent">Recently Active (Time-based)</option>
              <option value="stale">Stale (Time-based)</option>
              <option value="old">Old (Time-based)</option>
            </select>
          </div>

          <!-- SBOM Upload Filter -->
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Last SBOM Upload
            </label>
            <select
              v-model="sbomFilter"
              class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
            >
              <option value="all">All Projects</option>
              <option value="recent">Recent (Last 7 days)</option>
              <option value="normal">Normal (7-30 days)</option>
              <option value="old">Old (30+ days)</option>
              <option value="very-old">Very Old (90+ days)</option>
            </select>
          </div>
        </div>

        <!-- Quick Filters -->
        <div class="mt-4 flex flex-wrap gap-2">
          <button
            @click="setQuickFilter('inactive-dt')"
            class="px-3 py-1 text-xs font-medium rounded-full bg-gray-100 dark:bg-gray-700 text-gray-800 dark:text-gray-200 hover:bg-gray-200 dark:hover:bg-gray-600"
          >
            Show Inactive (DT) Only
          </button>
          <button
            @click="setQuickFilter('old-sbom')"
            class="px-3 py-1 text-xs font-medium rounded-full bg-gray-100 dark:bg-gray-700 text-gray-800 dark:text-gray-200 hover:bg-gray-200 dark:hover:bg-gray-600"
          >
            Show Old SBOM Only
          </button>
          <button
            @click="setQuickFilter('cleanup-candidates')"
            class="px-3 py-1 text-xs font-medium rounded-full bg-red-100 dark:bg-red-900 text-red-800 dark:text-red-200 hover:bg-red-200 dark:hover:bg-red-800"
          >
            Cleanup Candidates
          </button>
          <button
            @click="clearFilters"
            class="px-3 py-1 text-xs font-medium rounded-full bg-blue-100 dark:bg-blue-900 text-blue-800 dark:text-blue-200 hover:bg-blue-200 dark:hover:bg-blue-800"
          >
            Clear Filters
          </button>
        </div>
      </div>

      <!-- Bulk Actions -->
      <div class="px-4 py-3 sm:px-6 border-b border-gray-200 dark:border-gray-700">
        <div class="flex justify-between items-center">
          <div class="flex items-center space-x-4">
            <label class="flex items-center">
              <input
                type="checkbox"
                v-model="selectAll"
                @change="toggleSelectAll"
                class="rounded border-gray-300 dark:border-gray-600 text-blue-600 focus:ring-blue-500"
              />
              <span class="ml-2 text-sm text-gray-700 dark:text-gray-300">
                Select All ({{ selectedProjects.length }}/{{ filteredProjects.length }})
              </span>
            </label>
          </div>
          <div class="flex flex-wrap gap-2">
            <!-- Bulk Delete -->
            <button
              v-if="selectedProjects.length > 0"
              @click="showDeleteConfirmation = true"
              class="px-4 py-2 border border-red-300 text-sm font-medium rounded-md text-red-700 bg-red-50 hover:bg-red-100 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500"
            >
              <Trash2 class="mr-2 h-4 w-4" />
              Delete Selected ({{ selectedProjects.length }})
            </button>

            <!-- Bulk Activate -->
            <button
              v-if="selectedProjects.length > 0"
              @click="showActivateConfirmation = true"
              class="px-4 py-2 border border-green-300 text-sm font-medium rounded-md text-green-700 bg-green-50 hover:bg-green-100 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500"
            >
              <Power class="mr-2 h-4 w-4" />
              Activate Selected ({{ selectedProjects.length }})
            </button>

            <!-- Bulk Deactivate -->
            <button
              v-if="selectedProjects.length > 0"
              @click="showDeactivateConfirmation = true"
              class="px-4 py-2 border border-yellow-300 text-sm font-medium rounded-md text-yellow-700 bg-yellow-50 hover:bg-yellow-100 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-yellow-500"
            >
              <PowerOff class="mr-2 h-4 w-4" />
              Deactivate Selected ({{ selectedProjects.length }})
            </button>

            <!-- Bulk Refresh -->
            <button
              v-if="selectedProjects.length > 0"
              @click="refreshSelectedProjects"
              class="px-4 py-2 border border-blue-300 text-sm font-medium rounded-md text-blue-700 bg-blue-50 hover:bg-blue-100 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
            >
              <RefreshCw class="mr-2 h-4 w-4" />
              Refresh Selected ({{ selectedProjects.length }})
            </button>
          </div>
        </div>
      </div>

      <!-- Projects List -->
      <div class="px-4 py-4 sm:px-6">
        <div v-if="loading" class="text-center py-8">
          <div class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
          <p class="mt-2 text-sm text-gray-600 dark:text-gray-400">Loading projects...</p>
        </div>

        <div v-else-if="projects.length === 0" class="text-center py-8">
          <Package class="mx-auto h-12 w-12 text-gray-400" />
          <h3 class="mt-2 text-sm font-medium text-gray-900 dark:text-white">No projects found</h3>
          <p class="mt-1 text-sm text-gray-500 dark:text-gray-400">
            <span v-if="searchQuery || activityFilter !== 'all' || sbomFilter !== 'all'">
              Try adjusting your search or filters.
            </span>
            <span v-else>
              No projects exist in Dependency-Track, or you don't have permission to view them.
            </span>
          </p>
          <div class="mt-6">
            <button
              @click="clearFilters"
              v-if="searchQuery || activityFilter !== 'all' || sbomFilter !== 'all'"
              class="inline-flex items-center px-4 py-2 border border-gray-300 dark:border-gray-600 shadow-sm text-sm leading-4 font-medium rounded-md text-gray-700 dark:text-gray-300 bg-white dark:bg-gray-800 hover:bg-gray-50 dark:hover:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
            >
              Clear Filters
            </button>
            <button
              @click="refreshProjects"
              class="ml-3 inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm leading-4 font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
            >
              <RefreshCw class="mr-2 h-4 w-4" />
              Refresh
            </button>
          </div>
        </div>

        <div v-else-if="filteredProjects.length === 0" class="text-center py-8">
          <FolderOpen class="mx-auto h-12 w-12 text-gray-400" />
          <h3 class="mt-2 text-sm font-medium text-gray-900 dark:text-white">No projects found</h3>
          <p class="mt-1 text-sm text-gray-500 dark:text-gray-400">
            Try adjusting your filters or search criteria.
          </p>
        </div>

        <div v-else class="space-y-3">
          <div
            v-for="project in filteredProjects"
            :key="project.uuid"
            class="border border-gray-200 dark:border-gray-600 rounded-lg p-4 hover:bg-gray-50 dark:hover:bg-gray-700"
          >
            <div class="flex items-start justify-between">
              <div class="flex items-start space-x-3 flex-1">
                <input
                  type="checkbox"
                  v-model="selectedProjects"
                  :value="project.uuid"
                  class="mt-1 rounded border-gray-300 dark:border-gray-600 text-blue-600 focus:ring-blue-500"
                />
                <div class="flex-1">
                  <div class="flex items-center space-x-2">
                    <h3 class="text-sm font-medium text-gray-900 dark:text-white">
                      {{ project.name }}
                    </h3>
                    <span class="px-2 py-1 text-xs font-medium rounded-full bg-gray-100 dark:bg-gray-700 text-gray-800 dark:text-gray-200">
                      {{ project.version }}
                    </span>
                  </div>
                  <div class="mt-1 text-sm italic text-gray-600 dark:text-gray-400">
                    🏷 {{ project.tags ? project.tags.join(', ') : 'No tags' }}
                  </div>
                  <div class="mt-2 flex items-center space-x-4 text-xs text-gray-500 dark:text-gray-400">
                    <span class="flex items-center">
                      <Clock class="mr-1 h-3 w-3" />
                      Last activity: {{ formatDate(project.lastActivity) }}
                    </span>
                    <span class="flex items-center">
                      <Package class="mr-1 h-3 w-3" />
                      Last SBOM: {{ formatDate(project.lastSbomUpload) }}
                    </span>
                    <span class="flex items-center">
                      <AlertCircle class="mr-1 h-3 w-3" />
                      {{ getProjectVulnerabilities(project.metrics) }} vulnerabilities
                    </span>
                  </div>
                </div>
              </div>
              <div class="flex flex-col items-end space-y-2">
                <div class="flex items-center space-x-1">
                  <span
                    :class="getActiveStatusClass(project)"
                    class="px-2 py-1 text-xs font-medium rounded-full"
                  >
                    {{ getActiveStatus(project) }}
                  </span>
                  <span
                    :class="getActivityStatusClass(project)"
                    class="px-2 py-1 text-xs font-medium rounded-full"
                  >
                    {{ getActivityStatus(project) }}
                  </span>
                </div>
                <button
                  @click="deleteProject(project)"
                  class="text-red-600 hover:text-red-800 text-xs font-medium"
                >
                  Delete
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Pagination Controls -->
      <div class="px-4 py-4 sm:px-6 border-t border-gray-200 dark:border-gray-700">
        <div class="flex items-center justify-between">
          <div class="text-sm text-gray-700 dark:text-gray-300">
            Showing {{ projects.length }} of {{ totalProjects }} projects
            <span v-if="totalPages > 1"> (Page {{ currentPage }} of {{ totalPages }})</span>
          </div>
          <div class="flex items-center space-x-2">
            <button
              @click="prevPage"
              :disabled="currentPage === 1 || loading"
              class="px-3 py-1 text-sm border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Previous
            </button>

            <div class="flex items-center space-x-1">
              <button
                v-for="page in Math.min(5, totalPages)"
                :key="page"
                @click="goToPage(page)"
                :class="[
                  'px-3 py-1 text-sm border rounded-md',
                  page === currentPage
                    ? 'bg-blue-600 text-white border-blue-600'
                    : 'bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-300 border-gray-300 dark:border-gray-600 hover:bg-gray-50 dark:hover:bg-gray-700'
                ]"
              >
                {{ page }}
              </button>

              <span v-if="totalPages > 5" class="px-2 text-gray-500">...</span>

              <button
                v-if="totalPages > 5"
                @click="goToPage(totalPages)"
                :class="[
                  'px-3 py-1 text-sm border rounded-md',
                  totalPages === currentPage
                    ? 'bg-blue-600 text-white border-blue-600'
                    : 'bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-300 border-gray-300 dark:border-gray-600 hover:bg-gray-50 dark:hover:bg-gray-700'
                ]"
              >
                {{ totalPages }}
              </button>
            </div>

            <button
              @click="nextPage"
              :disabled="currentPage === totalPages || loading"
              class="px-3 py-1 text-sm border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Next
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Delete Confirmation Modal -->
    <div
      v-if="showDeleteConfirmation"
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
              <div class="mx-auto flex-shrink-0 flex items-center justify-center h-12 w-12 rounded-full bg-red-100 dark:bg-red-900 sm:mx-0 sm:h-10 sm:w-10">
                <AlertCircle class="h-6 w-6 text-red-600 dark:text-red-400" />
              </div>
              <div class="mt-3 text-center sm:mt-0 sm:ml-4 sm:text-left">
                <h3 class="text-lg leading-6 font-medium text-gray-900 dark:text-white" id="modal-title">
                  Delete Projects
                </h3>
                <div class="mt-2">
                  <p class="text-sm text-gray-500 dark:text-gray-400">
                    Are you sure you want to delete {{ selectedProjects.length }} project(s)? This action cannot be undone.
                  </p>
                  <div class="mt-3 max-h-32 overflow-y-auto">
                    <ul class="text-sm text-gray-600 dark:text-gray-400">
                      <li v-for="uuid in selectedProjects" :key="uuid" class="py-1">
                        • {{ getProjectName(uuid) }}
                      </li>
                    </ul>
                  </div>
                </div>
              </div>
            </div>
          </div>
          <div class="bg-gray-50 dark:bg-gray-700 px-4 py-3 sm:px-6 sm:flex sm:flex-row-reverse">
            <button
              @click="confirmDelete"
              type="button"
              class="w-full inline-flex justify-center rounded-md border border-transparent shadow-sm px-4 py-2 bg-red-600 text-base font-medium text-white hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500 sm:ml-3 sm:w-auto sm:text-sm"
            >
              Delete
            </button>
            <button
              @click="showDeleteConfirmation = false"
              type="button"
              class="mt-3 w-full inline-flex justify-center rounded-md border border-gray-300 dark:border-gray-600 shadow-sm px-4 py-2 bg-white dark:bg-gray-800 text-base font-medium text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 sm:mt-0 sm:ml-3 sm:w-auto sm:text-sm"
            >
              Cancel
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Activate Confirmation Modal -->
    <div
      v-if="showActivateConfirmation"
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
                <Power class="h-6 w-6 text-green-600 dark:text-green-400" />
              </div>
              <div class="mt-3 text-center sm:mt-0 sm:ml-4 sm:text-left">
                <h3 class="text-lg leading-6 font-medium text-gray-900 dark:text-white" id="modal-title">
                  Activate Projects
                </h3>
                <div class="mt-2">
                  <p class="text-sm text-gray-500 dark:text-gray-400">
                    Are you sure you want to activate {{ selectedProjects.length }} project(s)? This will make them visible and active in Dependency-Track.
                  </p>
                  <div class="mt-3 max-h-32 overflow-y-auto">
                    <ul class="text-sm text-gray-600 dark:text-gray-400">
                      <li v-for="uuid in selectedProjects" :key="uuid" class="py-1">
                        • {{ getProjectName(uuid) }}
                      </li>
                    </ul>
                  </div>
                </div>
              </div>
            </div>
          </div>
          <div class="bg-gray-50 dark:bg-gray-700 px-4 py-3 sm:px-6 sm:flex sm:flex-row-reverse">
            <button
              @click="confirmActivate"
              type="button"
              class="w-full inline-flex justify-center rounded-md border border-transparent shadow-sm px-4 py-2 bg-green-600 text-base font-medium text-white hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500 sm:ml-3 sm:w-auto sm:text-sm"
            >
              Activate
            </button>
            <button
              @click="showActivateConfirmation = false"
              type="button"
              class="mt-3 w-full inline-flex justify-center rounded-md border border-gray-300 dark:border-gray-600 shadow-sm px-4 py-2 bg-white dark:bg-gray-800 text-base font-medium text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 sm:mt-0 sm:ml-3 sm:w-auto sm:text-sm"
            >
              Cancel
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Deactivate Confirmation Modal -->
    <div
      v-if="showDeactivateConfirmation"
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
              <div class="mx-auto flex-shrink-0 flex items-center justify-center h-12 w-12 rounded-full bg-yellow-100 dark:bg-yellow-900 sm:mx-0 sm:h-10 sm:w-10">
                <PowerOff class="h-6 w-6 text-yellow-600 dark:text-yellow-400" />
              </div>
              <div class="mt-3 text-center sm:mt-0 sm:ml-4 sm:text-left">
                <h3 class="text-lg leading-6 font-medium text-gray-900 dark:text-white" id="modal-title">
                  Deactivate Projects
                </h3>
                <div class="mt-2">
                  <p class="text-sm text-gray-500 dark:text-gray-400">
                    Are you sure you want to deactivate {{ selectedProjects.length }} project(s)? This will make them inactive but they won't be deleted.
                  </p>
                  <div class="mt-3 max-h-32 overflow-y-auto">
                    <ul class="text-sm text-gray-600 dark:text-gray-400">
                      <li v-for="uuid in selectedProjects" :key="uuid" class="py-1">
                        • {{ getProjectName(uuid) }}
                      </li>
                    </ul>
                  </div>
                </div>
              </div>
            </div>
          </div>
          <div class="bg-gray-50 dark:bg-gray-700 px-4 py-3 sm:px-6 sm:flex sm:flex-row-reverse">
            <button
              @click="confirmDeactivate"
              type="button"
              class="w-full inline-flex justify-center rounded-md border border-transparent shadow-sm px-4 py-2 bg-yellow-600 text-base font-medium text-white hover:bg-yellow-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-yellow-500 sm:ml-3 sm:w-auto sm:text-sm"
            >
              Deactivate
            </button>
            <button
              @click="showDeactivateConfirmation = false"
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
import { ref, onMounted, computed, watch } from 'vue'
import { RefreshCw, FolderOpen, Clock, Package, AlertCircle, Trash2, Power, PowerOff } from 'lucide-vue-next'
import axios from 'axios'

export default {
  name: 'ProjectBulkActions',
  components: {
    RefreshCw,
    FolderOpen,
    Clock,
    Package,
    AlertCircle,
    Trash2,
    Power,
    PowerOff
  },
  setup() {
    const loading = ref(false)
    const projects = ref([])
    const searchQuery = ref('')
    const activityFilter = ref('all')
    const sbomFilter = ref('all')
    const selectedProjects = ref([])
    const selectAll = ref(false)
    const showDeleteConfirmation = ref(false)
    const showActivateConfirmation = ref(false)
    const showDeactivateConfirmation = ref(false)
    const currentPage = ref(1)
    const pageSize = ref(50)
    const totalProjects = ref(0)
    const totalPages = ref(1)

    // Computed properties
    const filteredProjects = computed(() => {
      let filtered = projects.value

      // Search filter
      if (searchQuery.value) {
        const query = searchQuery.value.toLowerCase()
        filtered = filtered.filter(project =>
          project.name.toLowerCase().includes(query) ||
          project.tags.some(tag => tag.toLowerCase().includes(query))
        )
      }

      // Activity filter
      const now = new Date()
      if (activityFilter.value === 'active-dt') {
        filtered = filtered.filter(project => project.active === true)
      } else if (activityFilter.value === 'inactive-dt') {
        filtered = filtered.filter(project => project.active === false)
      } else if (activityFilter.value === 'recent') {
        const thirtyDaysAgo = new Date(now.getTime() - 30 * 24 * 60 * 60 * 1000)
        filtered = filtered.filter(project =>
          project.lastActivity && new Date(project.lastActivity) > thirtyDaysAgo
        )
      } else if (activityFilter.value === 'stale') {
        const thirtyDaysAgo = new Date(now.getTime() - 30 * 24 * 60 * 60 * 1000)
        const ninetyDaysAgo = new Date(now.getTime() - 90 * 24 * 60 * 60 * 1000)
        filtered = filtered.filter(project =>
          project.lastActivity &&
          new Date(project.lastActivity) > ninetyDaysAgo &&
          new Date(project.lastActivity) <= thirtyDaysAgo
        )
      } else if (activityFilter.value === 'old') {
        const ninetyDaysAgo = new Date(now.getTime() - 90 * 24 * 60 * 60 * 1000)
        filtered = filtered.filter(project =>
          !project.lastActivity || new Date(project.lastActivity) <= ninetyDaysAgo
        )
      }

      // SBOM filter
      if (sbomFilter.value === 'recent') {
        const sevenDaysAgo = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000)
        filtered = filtered.filter(project =>
          project.lastSbomUpload && new Date(project.lastSbomUpload) > sevenDaysAgo
        )
      } else if (sbomFilter.value === 'normal') {
        const sevenDaysAgo = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000)
        const thirtyDaysAgo = new Date(now.getTime() - 30 * 24 * 60 * 60 * 1000)
        filtered = filtered.filter(project =>
          project.lastSbomUpload &&
          new Date(project.lastSbomUpload) > thirtyDaysAgo &&
          new Date(project.lastSbomUpload) <= sevenDaysAgo
        )
      } else if (sbomFilter.value === 'old') {
        const thirtyDaysAgo = new Date(now.getTime() - 30 * 24 * 60 * 60 * 1000)
        filtered = filtered.filter(project =>
          !project.lastSbomUpload || new Date(project.lastSbomUpload) <= thirtyDaysAgo
        )
      } else if (sbomFilter.value === 'very-old') {
        const ninetyDaysAgo = new Date(now.getTime() - 90 * 24 * 60 * 60 * 1000)
        filtered = filtered.filter(project =>
          !project.lastSbomUpload || new Date(project.lastSbomUpload) <= ninetyDaysAgo
        )
      }

      return filtered
    })

    // Methods
    const refreshProjects = async () => {
      loading.value = true
      try {
        const params = {
          page: currentPage.value,
          limit: pageSize.value
        }

        // Add search parameter if exists
        if (searchQuery.value) {
          params.search = searchQuery.value
        }

        const response = await axios.get('/api/projects', { params })
        projects.value = response.data

        // Get total count for pagination
        try {
          const countResponse = await axios.get('/api/projects/count', {
            params: { search: searchQuery.value }
          })
          totalProjects.value = countResponse.data.total
          totalPages.value = Math.ceil(totalProjects.value / pageSize.value)
        } catch (countError) {
          console.warn('Could not get project count:', countError)
          // Fallback: assume current page has full results
          totalProjects.value = projects.value.length
          totalPages.value = 1
        }

        // Clear selection when refreshing
        selectedProjects.value = []
        selectAll.value = false
      } catch (error) {
        console.error('Failed to load projects:', error)
      } finally {
        loading.value = false
      }
    }

    const setQuickFilter = (type) => {
      if (type === 'inactive-dt') {
        activityFilter.value = 'inactive-dt'
      } else if (type === 'old-sbom') {
        sbomFilter.value = 'old'
      } else if (type === 'cleanup-candidates') {
        activityFilter.value = 'inactive-dt'
        sbomFilter.value = 'none'
      } else if (type === 'cleanup-candidates-with-sbom') {
        activityFilter.value = 'inactive-dt'
        sbomFilter.value = 'yes'
      }

      // Reset to first page when filters change
      currentPage.value = 1
      refreshProjects()
    }

    const clearFilters = () => {
      searchQuery.value = ''
      activityFilter.value = 'all'
      sbomFilter.value = 'all'

      // Reset to first page when clearing filters
      currentPage.value = 1
      refreshProjects()
    }

    const toggleSelectAll = () => {
      if (selectAll.value) {
        selectedProjects.value = filteredProjects.value.map(p => p.uuid)
      } else {
        selectedProjects.value = []
      }
    }

    const getActiveStatus = (project) => {
      if (project.active === true) return 'Active (DT)'
      if (project.active === false) return 'Inactive (DT)'
      return 'Unknown'
    }

    const getActiveStatusClass = (project) => {
      const status = getActiveStatus(project)
      if (status === 'Active (DT)') return 'bg-green-100 dark:bg-green-900 text-green-800 dark:text-green-200'
      if (status === 'Inactive (DT)') return 'bg-red-100 dark:bg-red-900 text-red-800 dark:text-red-200'
      return 'bg-gray-100 dark:bg-gray-700 text-gray-800 dark:text-gray-200'
    }

    const getActivityStatus = (project) => {

      // Fallback to time-based status if active flag is not available
      const now = new Date()
      const lastActivity = new Date(project.lastActivity)
      const daysDiff = Math.floor((now - lastActivity) / (1000 * 60 * 60 * 24))

      if (daysDiff <= 30) return 'Recently Active'
      if (daysDiff <= 90) return 'Stale'
      return 'Old'
    }

    const getActivityStatusClass = (project) => {
      const status = getActivityStatus(project)
      if (status === 'Active') return 'bg-green-100 dark:bg-green-900 text-green-800 dark:text-green-200'
      if (status === 'Inactive') return 'bg-red-100 dark:bg-red-900 text-red-800 dark:text-red-200'
      if (status === 'Recently Active') return 'bg-green-100 dark:bg-green-900 text-green-800 dark:text-green-200'
      if (status === 'Stale') return 'bg-yellow-100 dark:bg-yellow-900 text-yellow-800 dark:text-yellow-200'
      if (status === 'Old') return 'bg-gray-100 dark:bg-gray-700 text-gray-800 dark:text-gray-200'
      return 'bg-gray-100 dark:bg-gray-700 text-gray-800 dark:text-gray-200'
    }

    const getSbomStatus = (project) => {
      const now = new Date()
      const lastSbom = new Date(project.lastSbomUpload)
      const daysDiff = Math.floor((now - lastSbom) / (1000 * 60 * 60 * 24))

      if (daysDiff <= 7) return 'Recent'
      if (daysDiff <= 30) return 'Normal'
      if (daysDiff <= 90) return 'Old'
      return 'Very Old'
    }

    const getSbomStatusClass = (project) => {
      const status = getSbomStatus(project)
      if (status === 'Recent') return 'bg-green-100 dark:bg-green-900 text-green-800 dark:text-green-200'
      if (status === 'Normal') return 'bg-blue-100 dark:bg-blue-900 text-blue-800 dark:text-blue-200'
      if (status === 'Old') return 'bg-yellow-100 dark:bg-yellow-900 text-yellow-800 dark:text-yellow-200'
      return 'bg-red-100 dark:bg-red-900 text-red-800 dark:text-red-200'
    }

    const formatDate = (dateString) => {
      if (!dateString) return 'Never'
      const date = new Date(dateString)
      const now = new Date()
      const daysDiff = Math.floor((now - date) / (1000 * 60 * 60 * 24))

      if (daysDiff === 0) return 'Today'
      if (daysDiff === 1) return 'Yesterday'
      if (daysDiff < 30) return `${daysDiff} days ago`
      if (daysDiff < 365) return `${Math.floor(daysDiff / 30)} months ago`
      return `${Math.floor(daysDiff / 365)} years ago`
    }

    const getProjectVulnerabilities = (metrics) => {
      if (!metrics) return 0
      return (metrics.critical || 0) + (metrics.high || 0) + (metrics.medium || 0) + (metrics.low || 0)
    }

    const getProjectName = (uuid) => {
      const project = projects.value.find(p => p.uuid === uuid)
      return project ? project.name : 'Unknown'
    }

    const deleteProject = async (project) => {
      if (confirm(`Are you sure you want to delete "${project.name}"? This action cannot be undone.`)) {
        try {
          await axios.delete(`/api/projects/${project.uuid}`)
          projects.value = projects.value.filter(p => p.uuid !== project.uuid)
          selectedProjects.value = selectedProjects.value.filter(uuid => uuid !== project.uuid)
        } catch (error) {
          console.error('Failed to delete project:', error)
          alert('Failed to delete project. Please try again.')
        }
      }
    }

    const confirmDelete = async () => {
      try {
        const deletePromises = selectedProjects.value.map(uuid =>
          axios.delete(`/api/projects/${uuid}`)
        )
        await Promise.all(deletePromises)

        projects.value = projects.value.filter(p => !selectedProjects.value.includes(p.uuid))
        selectedProjects.value = []
        selectAll.value = false
        showDeleteConfirmation.value = false
      } catch (error) {
        console.error('Failed to delete projects:', error)
        alert('Failed to delete some projects. Please try again.')
      }
    }

    const confirmActivate = async () => {
      try {
        const activatePromises = selectedProjects.value.map(uuid =>
          axios.patch(`/api/projects/${uuid}/activate`)
        )
        await Promise.all(activatePromises)

        // Update local project data
        selectedProjects.value.forEach(uuid => {
          const project = projects.value.find(p => p.uuid === uuid)
          if (project) {
            project.active = true
          }
        })

        selectedProjects.value = []
        selectAll.value = false
        showActivateConfirmation.value = false
      } catch (error) {
        console.error('Failed to activate projects:', error)
        alert('Failed to activate some projects. Please try again.')
      }
    }

    const confirmDeactivate = async () => {
      try {
        const deactivatePromises = selectedProjects.value.map(uuid =>
          axios.patch(`/api/projects/${uuid}/deactivate`)
        )
        await Promise.all(deactivatePromises)

        // Update local project data
        selectedProjects.value.forEach(uuid => {
          const project = projects.value.find(p => p.uuid === uuid)
          if (project) {
            project.active = false
          }
        })

        selectedProjects.value = []
        selectAll.value = false
        showDeactivateConfirmation.value = false
      } catch (error) {
        console.error('Failed to deactivate projects:', error)
        alert('Failed to deactivate some projects. Please try again.')
      }
    }

    const refreshSelectedProjects = async () => {
      try {
        const refreshPromises = selectedProjects.value.map(uuid =>
          axios.put(`/api/projects/${uuid}/refresh`)
        )
        await Promise.all(refreshPromises)

        // Refresh the full project list
        await refreshProjects()
      } catch (error) {
        console.error('Failed to refresh projects:', error)
        alert('Failed to refresh some projects. Please try again.')
      }
    }

    const goToPage = (page) => {
      if (page >= 1 && page <= totalPages.value) {
        currentPage.value = page
        refreshProjects()
      }
    }

    const nextPage = () => {
      if (currentPage.value < totalPages.value) {
        currentPage.value++
        refreshProjects()
      }
    }

    const prevPage = () => {
      if (currentPage.value > 1) {
        currentPage.value--
        refreshProjects()
      }
    }

    // Watch for search changes and reset pagination
    watch(searchQuery, () => {
      currentPage.value = 1
      refreshProjects()
    })

    onMounted(() => {
      refreshProjects()
    })

    return {
      loading,
      projects,
      searchQuery,
      activityFilter,
      sbomFilter,
      selectedProjects,
      selectAll,
      showDeleteConfirmation,
      showActivateConfirmation,
      showDeactivateConfirmation,
      currentPage,
      pageSize,
      totalProjects,
      totalPages,
      filteredProjects,
      refreshProjects,
      setQuickFilter,
      clearFilters,
      toggleSelectAll,
      getActiveStatus,
      getActiveStatusClass,
      getActivityStatus,
      getActivityStatusClass,
      getSbomStatus,
      getSbomStatusClass,
      formatDate,
      getProjectVulnerabilities,
      getProjectName,
      deleteProject,
      confirmDelete,
      confirmActivate,
      confirmDeactivate,
      refreshSelectedProjects,
      goToPage,
      nextPage,
      prevPage
    }
  }
}
</script>
