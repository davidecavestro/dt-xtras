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
          <div class="flex items-center space-x-3">
            <!-- View Mode Toggle -->
            <div class="flex items-center space-x-1">
              <button
                @click="viewMode = 'list'"
                :class="[
                  'px-3 py-1 text-sm rounded-md',
                  viewMode === 'list'
                    ? 'bg-blue-600 text-white'
                    : 'bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-300 border border-gray-300 dark:border-gray-600'
                ]"
              >
                <ListIcon class="w-4 h-4" />
              </button>
              <button
                @click="viewMode = 'deck'"
                :class="[
                  'px-3 py-1 text-sm rounded-md',
                  viewMode === 'deck'
                    ? 'bg-blue-600 text-white'
                    : 'bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-300 border border-gray-300 dark:border-gray-600'
                ]"
              >
                <SquareIcon class="w-4 h-4" />
              </button>
            </div>

            <button
              @click="refreshProjects"
              :disabled="isLoading"
              class="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500 disabled:opacity-50"
            >
              <RefreshCw class="mr-2 h-4 w-4" :class="{ 'animate-spin': isLoading }" />
              Refresh
            </button>
          </div>
        </div>
      </div>

      <!-- Filters -->
      <div class="px-4 py-4 sm:px-6 border-b border-gray-200 dark:border-gray-700">
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <!-- Project Name Filter -->
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Project Name
            </label>
            <select
              v-model="projectFilter"
              @change="handleProjectFilterChange(projectFilter)"
              class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
            >
              <option value="">All Projects</option>
              <option
                v-for="projectName in uniqueProjectNames"
                :key="projectName"
                :value="projectName"
              >
                {{ projectName }}
              </option>
            </select>
          </div>

          <!-- Search -->
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Search Projects
            </label>
            <input
              v-model="searchQuery"
              type="text"
              placeholder="Filter by project, version or tags..."
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

      <!-- Pagination Controls -->
      <div v-if="totalProjects > 0" class="flex items-center justify-between mb-6 px-4 pt-4">
        <div class="flex items-center space-x-4">
          <div class="text-sm text-gray-700 dark:text-gray-300 hidden sm:block">
            Showing {{ projects.length }} of {{ totalProjects }} projects
          </div>
          <div class="flex items-center space-x-2">
            <label class="text-sm text-gray-600 dark:text-gray-400">Page size:</label>
            <select
              v-model="pageSize"
              @change="handlePageSizeChange(pageSize)"
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
            @click="prevPage"
            :disabled="currentPage <= 1"
            class="px-3 py-1 text-sm border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
            </svg>
          </button>

          <!-- Page Numbers -->
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
            :disabled="currentPage >= totalPages"
            class="px-3 py-1 text-sm border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
            </svg>
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
                Select All ({{ selectedProjects.length }}/{{ data.length }})
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

            <!-- Bulk Rename -->
            <button
              v-if="selectedProjects.length > 0"
              @click="showRenameModal = true"
              class="px-4 py-2 border border-purple-300 text-sm font-medium rounded-md text-purple-700 bg-purple-50 hover:bg-purple-100 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-purple-500"
            >
              <Edit3 class="mr-2 h-4 w-4" />
              Rename Selected ({{ selectedProjects.length }})
            </button>
          </div>
        </div>
      </div>

      <!-- Projects List -->
      <div class="px-4 py-4 sm:px-6">
        <div v-if="isLoading && data.length === 0" class="text-center py-8">
          <div class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
          <p class="mt-2 text-sm text-gray-600 dark:text-gray-400">Loading projects...</p>
        </div>

        <div v-else-if="data.length === 0 && !isLoading" class="text-center py-8">
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
              class="ml-3 inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm leading-4 font-medium rounded-md text-white bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500"
            >
              <RefreshCw class="mr-2 h-4 w-4" />
              Refresh
            </button>
          </div>
        </div>

        <!-- List View -->
        <div v-else-if="viewMode === 'list'" class="space-y-3">
          <div
            v-for="project in data"
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
                  <div v-if="project.tags && project.tags.length > 0" class="mt-1 text-sm italic text-gray-600 dark:text-gray-400">
                    🏷 {{ project.tags.map( tag => tag.name ).join(', ') }}
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

        <!-- Deck View -->
        <div v-else-if="viewMode === 'deck'" class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-3 gap-4 p-4">
          <div
            v-for="project in data"
            :key="project.uuid"
            class="relative"
          >
            <input
              type="checkbox"
              v-model="selectedProjects"
              :value="project.uuid"
              class="absolute top-2 left-2 z-10 rounded border-gray-300 dark:border-gray-600 text-blue-600 focus:ring-blue-500 bg-white dark:bg-gray-800"
            />
            <ProjectCard
              :project="project"
              @select="viewProject"
              @view="viewProject"
              @security-details="viewSecurityDetails"
              @analyze="analyzeProject"
            />
          </div>
        </div>
      </div>
    </div>

    <!-- Delete Confirmation Modal -->
    <Modal
      :show="showDeleteConfirmation"
      title="Delete Projects"
      :message="`Are you sure you want to delete ${selectedProjects.length} project(s)? This action cannot be undone.`"
      :icon="AlertCircle"
      icon-color="red"
      :items="selectedProjects.map(getProjectName)"
      confirm-text="Delete"
      cancel-text="Cancel"
      @confirm="confirmDelete"
      @close="showDeleteConfirmation = false"
    />

    <!-- Activate Confirmation Modal -->
    <Modal
      :show="showActivateConfirmation"
      title="Activate Projects"
      :message="`Are you sure you want to activate ${selectedProjects.length} project(s)? This will make them visible and active in Dependency-Track.`"
      :icon="Power"
      icon-color="green"
      :items="selectedProjects.map(getProjectName)"
      confirm-text="Activate"
      cancel-text="Cancel"
      @confirm="confirmActivate"
      @close="showActivateConfirmation = false"
    />

    <!-- Deactivate Confirmation Modal -->
    <Modal
      :show="showDeactivateConfirmation"
      title="Deactivate Projects"
      :message="`Are you sure you want to deactivate ${selectedProjects.length} project(s)? This will make them inactive but they won't be deleted.`"
      :icon="PowerOff"
      icon-color="yellow"
      :items="selectedProjects.map(getProjectName)"
      confirm-text="Deactivate"
      cancel-text="Cancel"
      @confirm="confirmDeactivate"
      @close="showDeactivateConfirmation = false"
    />

    <!-- Rename Modal -->
    <Modal
      :show="showRenameModal"
      title="Rename Projects"
      :message="`Enter a new name for the ${selectedProjects.length} selected project(s). All selected projects will be renamed to this name.`"
      :icon="Edit3"
      icon-color="purple"
      confirm-text="Rename"
      cancel-text="Cancel"
      :confirm-disabled="!newProjectName.trim()"
      @confirm="confirmRename"
      @close="showRenameModal = false; newProjectName = ''"
    >
      <template #content>
        <div class="mb-4">
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
            New Project Name
          </label>
          <input
            v-model="newProjectName"
            type="text"
            placeholder="Enter new project name..."
            class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-purple-500 focus:border-purple-500"
            @keyup.enter="confirmRename"
          />
        </div>
        <div class="max-h-32 overflow-y-auto">
          <p class="text-xs text-gray-500 dark:text-gray-400 mb-2">Projects to rename:</p>
          <ul class="text-sm text-gray-600 dark:text-gray-400">
            <li v-for="uuid in selectedProjects" :key="uuid" class="py-1">
              • {{ getProjectName(uuid) }}
            </li>
          </ul>
        </div>
      </template>
    </Modal>
  </div>
</template>

<script>
import { ref, onMounted, computed, watch } from 'vue'
import { storeToRefs } from 'pinia'
import { useProjectStore } from '../stores/projects'
import { useToast } from '../composables/useToast'
import { createLogger } from '../utils/logger'
import { RefreshCw, FolderOpen, Clock, Package, AlertCircle, Trash2, Power, PowerOff, List as ListIcon, Square as SquareIcon, Edit3 } from 'lucide-vue-next'
import ProjectCard from './ProjectCard.vue'
import Modal from './Modal.vue'

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
    PowerOff,
    ListIcon,
    SquareIcon,
    Edit3,
    ProjectCard,
    Modal
  },
  setup() {
    const projectStore = useProjectStore()
    const { projects, isLoading, currentPage, pageSize, totalProjects, totalPages, searchQuery, paginatedProjects } = storeToRefs(projectStore)
    const { showSuccess, showError } = useToast()
    const logger = createLogger('ProjectBulkActions')
    const activityFilter = ref('all')
    const sbomFilter = ref('all')
    const projectFilter = ref('')
    const selectedProjects = ref([])
    const selectAll = ref(false)
    const showDeleteConfirmation = ref(false)
    const showActivateConfirmation = ref(false)
    const showDeactivateConfirmation = ref(false)
    const showRenameModal = ref(false)
    const newProjectName = ref('')
    const viewMode = ref('deck') // 'list' or 'deck'

    // Computed properties
    const uniqueProjectNames = computed(() => {
      if (!projects.value) return []
      const names = new Set()
      projects.value.forEach(project => {
        const name = project.name
        if (name) names.add(name)
      })
      return Array.from(names).sort()
    })

    const filteredProjects = computed(() => {
      let filtered = projects.value || []
      logger.debug('Raw projects count:', projects.value?.length)
      logger.debug('Search query:', searchQuery.value)
      logger.debug('Project filter:', projectFilter.value)
      logger.debug('Activity filter:', activityFilter.value)
      logger.debug('SBOM filter:', sbomFilter.value)

      // Project name filter (exact match)
      if (projectFilter.value) {
        const filterName = projectFilter.value.toLowerCase()
        filtered = filtered.filter(project =>
          (project.name && project.name.toLowerCase() === filterName)
        )
      }

      // Search filter
      if (searchQuery.value) {
        const query = searchQuery.value.toLowerCase()
        filtered = filtered.filter(project =>
          (project.name && project.name.toLowerCase().includes(query)) ||
          (project.tags && project.tags.some(tag => tag && tag.toLowerCase && tag.toLowerCase().includes(query)))
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

      logger.debug('Final filtered projects count:', filtered.length)
      return filtered
    })

    // Use store's paginatedProjects but apply additional filters
    const data = computed(() => {
      let projectsToShow = paginatedProjects.value || []

      // Apply project name filter (exact match)
      if (projectFilter.value) {
        const filterName = projectFilter.value.toLowerCase()
        projectsToShow = projectsToShow.filter(project =>
          (project.name && project.name.toLowerCase() === filterName)
        )
      }

      // Apply additional filters that aren't in store
      const now = new Date()

      // Activity filter
      if (activityFilter.value === 'active-dt') {
        projectsToShow = projectsToShow.filter(project => project.active === true)
      } else if (activityFilter.value === 'inactive-dt') {
        projectsToShow = projectsToShow.filter(project => project.active === false)
      } else if (activityFilter.value === 'recent') {
        const thirtyDaysAgo = new Date(now.getTime() - 30 * 24 * 60 * 60 * 1000)
        projectsToShow = projectsToShow.filter(project =>
          project.lastActivity && new Date(project.lastActivity) > thirtyDaysAgo
        )
      } else if (activityFilter.value === 'stale') {
        const thirtyDaysAgo = new Date(now.getTime() - 30 * 24 * 60 * 60 * 1000)
        const ninetyDaysAgo = new Date(now.getTime() - 90 * 24 * 60 * 60 * 1000)
        projectsToShow = projectsToShow.filter(project =>
          project.lastActivity &&
          new Date(project.lastActivity) > ninetyDaysAgo &&
          new Date(project.lastActivity) <= thirtyDaysAgo
        )
      } else if (activityFilter.value === 'old') {
        const ninetyDaysAgo = new Date(now.getTime() - 90 * 24 * 60 * 60 * 1000)
        projectsToShow = projectsToShow.filter(project =>
          !project.lastActivity || new Date(project.lastActivity) <= ninetyDaysAgo
        )
      }

      // SBOM filter
      if (sbomFilter.value === 'recent') {
        const sevenDaysAgo = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000)
        projectsToShow = projectsToShow.filter(project =>
          project.lastSbomUpload && new Date(project.lastSbomUpload) > sevenDaysAgo
        )
      } else if (sbomFilter.value === 'normal') {
        const sevenDaysAgo = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000)
        const thirtyDaysAgo = new Date(now.getTime() - 30 * 24 * 60 * 60 * 1000)
        projectsToShow = projectsToShow.filter(project =>
          project.lastSbomUpload &&
          new Date(project.lastSbomUpload) > thirtyDaysAgo &&
          new Date(project.lastSbomUpload) <= sevenDaysAgo
        )
      } else if (sbomFilter.value === 'old') {
        const thirtyDaysAgo = new Date(now.getTime() - 30 * 24 * 60 * 60 * 1000)
        projectsToShow = projectsToShow.filter(project =>
          !project.lastSbomUpload || new Date(project.lastSbomUpload) <= thirtyDaysAgo
        )
      } else if (sbomFilter.value === 'very-old') {
        const ninetyDaysAgo = new Date(now.getTime() - 90 * 24 * 60 * 60 * 1000)
        projectsToShow = projectsToShow.filter(project =>
          !project.lastSbomUpload || new Date(project.lastSbomUpload) <= ninetyDaysAgo
        )
      }

      return projectsToShow
    })

    // Methods
    const refreshProjects = async () => {
      try {
        await projectStore.loadProjects()
        logger.debug('Projects after loading:', projects.value)
        logger.debug('Projects length:', projects.value?.length)

        // Clear selection when refreshing
        selectedProjects.value = []
        selectAll.value = false
      } catch (error) {
        logger.error('Failed to load projects:', error)
        showError('Failed to load projects')
      }
    }

    const setQuickFilter = (type) => {
      if (type === 'inactive-dt') {
        activityFilter.value = 'inactive-dt'
      } else if (type === 'old-sbom') {
        sbomFilter.value = 'old'
      } else if (type === 'cleanup-candidates') {
        activityFilter.value = 'inactive-dt'
        sbomFilter.value = 'very-old'
      } else if (type === 'cleanup-candidates-with-sbom') {
        activityFilter.value = 'inactive-dt'
        sbomFilter.value = 'recent'
      }

      // Reset to first page when filters change
      currentPage.value = 1
    }

    const handleProjectFilterChange = (projectName) => {
      // Reset to first page when filter changes
      currentPage.value = 1
    }

    const clearFilters = () => {
      searchQuery.value = ''
      projectFilter.value = ''
      activityFilter.value = 'all'
      sbomFilter.value = 'all'

      // Reset to first page when clearing filters
      currentPage.value = 1
      refreshProjects()
    }

    const toggleSelectAll = () => {
      if (selectAll.value) {
        selectedProjects.value = data.value.map(p => p.uuid)
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
          await projectStore.deleteProject(project.uuid)
          selectedProjects.value = selectedProjects.value.filter(uuid => uuid !== project.uuid)
        } catch (error) {
          logger.error('Failed to delete project:', error)
          showError('Failed to delete project. Please try again.')
        }
      }
    }

    const confirmDelete = async () => {
      try {
        await projectStore.bulkDeleteProjects(selectedProjects.value)

        // Store handles state updates, just clear local selection
        selectedProjects.value = []
        selectAll.value = false
        showDeleteConfirmation.value = false
      } catch (error) {
        logger.error('Failed to delete projects:', error)
        showError('Failed to delete some projects. Please try again.')
      }
    }

    const confirmActivate = async () => {
      try {
        await projectStore.bulkActivateProjects(selectedProjects.value)

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
        logger.error('Failed to activate projects:', error)
        showError('Failed to activate some projects. Please try again.')
      }
    }

    const confirmDeactivate = async () => {
      try {
        await projectStore.bulkDeactivateProjects(selectedProjects.value)

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
        logger.error('Failed to deactivate projects:', error)
        showError('Failed to deactivate some projects. Please try again.')
      }
    }

    const confirmRename = async () => {
      if (!newProjectName.value.trim()) {
        showError('Please enter a new project name')
        return
      }

      try {
        const result = await projectStore.bulkRenameProjects(selectedProjects.value, newProjectName.value.trim())

        showSuccess(`Renamed ${result.successCount} projects to '${newProjectName.value}'`)

        selectedProjects.value = []
        selectAll.value = false
        newProjectName.value = ''
        showRenameModal.value = false
      } catch (error) {
        logger.error('Failed to rename projects:', error)
        showError('Failed to rename some projects. Please try again.')
      }
    }

    const refreshSelectedProjects = async () => {
      try {
        await projectStore.bulkRefreshProjects(selectedProjects.value)

        // Refresh full project list
        await refreshProjects()
      } catch (error) {
        logger.error('Failed to refresh projects:', error)
        showError('Failed to refresh some projects. Please try again.')
      }
    }

    const goToPage = (page) => {
      projectStore.goToPage(page)
    }

    const nextPage = () => {
      projectStore.nextPage()
    }

    const prevPage = () => {
      projectStore.previousPage()
    }

    const handlePageSizeChange = (newPageSize) => {
      projectStore.setPageSize(newPageSize)
    }

    // ProjectCard event handlers
    const viewProject = (project) => {
      logger.info('View project:', project)
      // TODO: Navigate to project details
    }

    const viewSecurityDetails = (project) => {
      logger.info('View security details:', project)
      // TODO: Navigate to security details
    }

    const analyzeProject = (project) => {
      logger.info('Analyze project:', project)
      // TODO: Navigate to project analysis
    }

    // Watch for filter changes and reset to first page
    watch([activityFilter, sbomFilter], () => {
      // Reset to first page when filters change
      currentPage.value = 1
    }, { deep: true })

    // Watch for search changes and update store
    watch(() => searchQuery.value, (newValue) => {
      projectStore.setSearchQuery(newValue)
    })

    onMounted(() => {
      refreshProjects()
    })

    return {
      isLoading,
      projects,
      searchQuery,
      projectFilter,
      activityFilter,
      sbomFilter,
      selectedProjects,
      selectAll,
      showDeleteConfirmation,
      showActivateConfirmation,
      showDeactivateConfirmation,
      showRenameModal,
      newProjectName,
      currentPage,
      pageSize,
      totalProjects,
      totalPages,
      viewMode,
      uniqueProjectNames,
      filteredProjects,
      paginatedProjects,
      data,
      refreshProjects,
      setQuickFilter,
      handleProjectFilterChange,
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
      confirmRename,
      refreshSelectedProjects,
      goToPage,
      nextPage,
      prevPage,
      handlePageSizeChange,
      viewProject,
      viewSecurityDetails,
      analyzeProject
    }
  }
}
</script>
