<template>
  <div class="relative px-4 sm:px-0">
    <!-- Main Content Area -->
    <div class="bg-white dark:bg-gray-800 rounded-lg shadow mr-20">
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
          <!-- Project Name Filter: searchable select (scales to hundreds) -->
          <SearchableSelect
            v-model="projectFilter"
            :options="uniqueProjectNames"
            label="Project Name"
            id="project-name-filter"
            placeholder="All projects — search to filter…"
          />

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

      <!-- Large-portfolio notice: this view loads the whole portfolio because its
           activity-age / SBOM-age cleanup filters are computed client-side (DT
           can't filter on those server-side). Fine for typical sizes; flag it
           when it gets big so the load time isn't a surprise. -->
      <div
        v-if="projects.length >= 1000"
        class="mx-4 mt-4 px-4 py-2 text-sm rounded-md bg-amber-50 dark:bg-amber-900/20 text-amber-800 dark:text-amber-200 border border-amber-200 dark:border-amber-800"
      >
        Loaded {{ projects.length }} projects. This view loads the full portfolio to support
        time-based cleanup filters, so it may be slow at very large scale.
      </div>

      <!-- Pagination Controls -->
      <div v-if="totalFiltered > 0" class="flex items-center justify-between mb-6 px-4 pt-4">
        <div class="flex items-center space-x-4">
          <div class="text-sm text-gray-700 dark:text-gray-300 hidden sm:block">
            Showing {{ data.length }} of {{ totalFiltered }} projects
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
              v-for="page in Math.min(5, localTotalPages)"
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
            <span v-if="localTotalPages > 5" class="px-2 text-gray-500">...</span>
            <button
              v-if="localTotalPages > 5"
              @click="goToPage(localTotalPages)"
              :class="[
                'px-3 py-1 text-sm border rounded-md',
                localTotalPages === currentPage
                  ? 'bg-blue-600 text-white border-blue-600'
                  : 'bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-300 border-gray-300 dark:border-gray-600 hover:bg-gray-50 dark:hover:bg-gray-700'
              ]"
            >
              {{ localTotalPages }}
            </button>
          </div>

          <button
            @click="nextPage"
            :disabled="currentPage >= localTotalPages"
            class="px-3 py-1 text-sm border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
            </svg>
          </button>
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
            class="border border-gray-200 dark:border-gray-600 rounded-lg p-4 hover:bg-gray-50 dark:hover:bg-gray-700 cursor-pointer"
            @click="toggleProjectSelection(project.uuid)"
          >
            <div class="flex items-start gap-3">
              <!-- Checkbox -->
              <input
                type="checkbox"
                v-model="selectedProjects"
                :value="project.uuid"
                class="mt-1 rounded border-gray-300 dark:border-gray-600 text-blue-600 focus:ring-blue-500 shrink-0"
                @click.stop
              />
              <!-- Main Content -->
              <div class="flex-1 min-w-0">
                <div class="text-base font-medium text-gray-900 dark:text-white truncate">{{ project.name }}</div>
                <!-- Metrics & Info Line -->
                <div class="flex flex-wrap items-center gap-1.5 mt-1">
                  <!-- Version -->
                  <span class="text-xs font-medium text-gray-600 dark:text-gray-400">{{ project.version || 'latest' }}</span>
                  <!-- Status Badges -->
                  <span
                    :class="getActiveStatusClass(project)"
                    class="px-1.5 py-0.5 text-xs font-medium rounded-full"
                  >
                    {{ getActiveStatus(project) }}
                  </span>
                  <span
                    :class="getActivityStatusClass(project)"
                    class="px-1.5 py-0.5 text-xs font-medium rounded-full"
                  >
                    {{ getActivityStatus(project) }}
                  </span>
                  <!-- Metrics Counters -->
                  <template v-if="project.metrics">
                    <span class="text-xs text-gray-400">|</span>
                    <span class="text-xs text-gray-500 dark:text-gray-400">
                      <span class="font-medium text-gray-900 dark:text-white">{{ project.metrics.vulnerableComponents || 0 }}</span>
                      /
                      <span class="font-medium text-gray-900 dark:text-white">{{ project.metrics.components || project.metrics.vulnerableComponents || 0 }}</span>
                      comp.
                    </span>
                    <span class="text-xs text-gray-400">|</span>
                    <span class="text-xs text-gray-500 dark:text-gray-400">
                      <span class="font-medium text-gray-900 dark:text-white">{{ getProjectVulnerabilities(project.metrics) }}</span>
                      vulns
                    </span>
                  </template>
                  <!-- Security Badges -->
                  <template v-if="project.metrics">
                    <span v-if="project.metrics.critical > 0" class="px-1.5 py-0.5 bg-red-100 dark:bg-red-900 text-red-800 dark:text-red-200 rounded text-xs font-medium">
                      {{ project.metrics.critical }} C
                    </span>
                    <span v-if="project.metrics.high > 0" class="px-1.5 py-0.5 bg-orange-100 dark:bg-orange-900 text-orange-800 dark:text-orange-200 rounded text-xs font-medium">
                      {{ project.metrics.high }} H
                    </span>
                    <span v-if="project.metrics.medium > 0" class="px-1.5 py-0.5 bg-yellow-100 dark:bg-yellow-900 text-yellow-800 dark:text-yellow-200 rounded text-xs font-medium">
                      {{ project.metrics.medium }} M
                    </span>
                    <span v-if="project.metrics.low > 0" class="px-1.5 py-0.5 bg-blue-100 dark:bg-blue-900 text-blue-800 dark:text-blue-200 rounded text-xs font-medium">
                      {{ project.metrics.low }} L
                    </span>
                    <span v-if="getProjectVulnerabilities(project.metrics) === 0" class="px-1.5 py-0.5 bg-green-100 dark:bg-green-900 text-green-800 dark:text-green-200 rounded text-xs font-medium">
                      No Vulns
                    </span>
                  </template>
                  <!-- Tags (at end since variable length) -->
                  <template v-if="project.tags && project.tags.length > 0">
                    <span class="text-xs text-gray-400">|</span>
                    <span
                      v-for="tag in project.tags.slice(0, 3)"
                      :key="tag.name"
                      class="inline-flex items-center px-1.5 py-0.5 rounded-full text-xs font-medium border truncate"
                      :class="getTagStyle(tag)"
                      :style="getTagDynamicStyle(tag)"
                    >
                      {{ tag.name }}
                    </span>
                    <span
                      v-if="project.tags.length > 3"
                      class="px-1.5 py-0.5 bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-400 text-xs rounded-full"
                    >
                      +{{ project.tags.length - 3 }}
                    </span>
                  </template>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Deck View -->
        <div v-else-if="viewMode === 'deck'" class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-3 gap-4 p-4">
          <div
            v-for="project in data"
            :key="project.uuid"
            class="relative cursor-pointer"
            @click="toggleProjectSelection(project.uuid)"
          >
            <input
              type="checkbox"
              v-model="selectedProjects"
              :value="project.uuid"
              class="absolute top-0 left-0 z-10 rounded border-gray-300 dark:border-gray-600 text-blue-600 focus:ring-blue-500 bg-white dark:bg-gray-800"
              @click.stop
            />
            <ProjectCard
              :project="project"
              :show-actions="false"
              :get-tag-style="getTagStyle"
              :get-tag-dynamic-style="getTagDynamicStyle"
              @select="viewProject"
              @view="viewProject"
              @security-details="viewSecurityDetails"
              @analyze="analyzeProject"
            />
          </div>
        </div>
      </div>
    </div>

    <!-- Vertical Bulk Actions Toolbar - Fixed Right -->
    <div class="fixed top-24 right-8 w-16 bg-white dark:bg-gray-800 rounded-lg shadow-lg border border-gray-200 dark:border-gray-700 py-2 flex flex-col items-center gap-2 z-30">
      <!-- Selection Count -->
      <div class="text-xs text-center text-gray-500 dark:text-gray-400 mb-1 px-1">
        {{ selectedProjects.length }}
      </div>

      <!-- Bulk Delete -->
      <button
        @click="showDeleteConfirmation = true"
        :disabled="selectedProjects.length === 0"
        class="w-12 h-12 flex flex-col items-center justify-center rounded-lg border border-red-200 dark:border-red-800 text-red-600 dark:text-red-400 hover:bg-red-50 dark:hover:bg-red-900/30 disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
        title="Delete selected"
      >
        <Trash2 class="h-5 w-5" />
        <span class="text-[10px] mt-0.5">Del</span>
      </button>

      <!-- Bulk Activate -->
      <button
        @click="showActivateConfirmation = true"
        :disabled="selectedProjects.length === 0"
        class="w-12 h-12 flex flex-col items-center justify-center rounded-lg border border-green-200 dark:border-green-800 text-green-600 dark:text-green-400 hover:bg-green-50 dark:hover:bg-green-900/30 disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
        title="Activate selected"
      >
        <Power class="h-5 w-5" />
        <span class="text-[10px] mt-0.5">Act</span>
      </button>

      <!-- Bulk Deactivate -->
      <button
        @click="showDeactivateConfirmation = true"
        :disabled="selectedProjects.length === 0"
        class="w-12 h-12 flex flex-col items-center justify-center rounded-lg border border-yellow-200 dark:border-yellow-800 text-yellow-600 dark:text-yellow-400 hover:bg-yellow-50 dark:hover:bg-yellow-900/30 disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
        title="Deactivate selected"
      >
        <PowerOff class="h-5 w-5" />
        <span class="text-[10px] mt-0.5">Deact</span>
      </button>

      <!-- Bulk Refresh -->
      <button
        @click="refreshSelectedProjects"
        :disabled="selectedProjects.length === 0"
        class="w-12 h-12 flex flex-col items-center justify-center rounded-lg border border-blue-200 dark:border-blue-800 text-blue-600 dark:text-blue-400 hover:bg-blue-50 dark:hover:bg-blue-900/30 disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
        title="Refresh selected"
      >
        <RefreshCw class="h-5 w-5" />
        <span class="text-[10px] mt-0.5">Ref</span>
      </button>

      <!-- Bulk Rename -->
      <button
        @click="showRenameModal = true"
        :disabled="selectedProjects.length === 0"
        class="w-12 h-12 flex flex-col items-center justify-center rounded-lg border border-purple-200 dark:border-purple-800 text-purple-600 dark:text-purple-400 hover:bg-purple-50 dark:hover:bg-purple-900/30 disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
        title="Rename selected"
      >
        <Edit3 class="h-5 w-5" />
        <span class="text-[10px] mt-0.5">Ren</span>
      </button>

      <!-- Select All Divider -->
      <div class="w-10 h-px bg-gray-200 dark:bg-gray-700 my-1"></div>

      <!-- Select All -->
      <label
        class="w-12 h-12 flex flex-col items-center justify-center rounded-lg border border-gray-200 dark:border-gray-700 text-gray-600 dark:text-gray-400 hover:bg-gray-50 dark:hover:bg-gray-700 cursor-pointer transition-colors"
        title="Select all"
      >
        <input
          type="checkbox"
          v-model="selectAll"
          @change="toggleSelectAll"
          class="rounded border-gray-300 dark:border-gray-600 text-blue-600 focus:ring-blue-500 h-4 w-4"
        />
        <span class="text-[10px] mt-0.5">All</span>
      </label>
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
      :loading="isDeleting"
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
      :loading="isActivating"
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
      :loading="isDeactivating"
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

    <!-- Confirmation Dialog -->
    <Modal
      :show="showConfirmDialog"
      :title="confirmDialogTitle"
      :message="confirmDialogMessage"
      :confirm-text="confirmDialogConfirmText"
      :cancel-text="confirmDialogCancelText"
      :icon="AlertTriangle"
      icon-color="red"
      @confirm="handleConfirm"
      @close="handleCancel"
    />
</template>

<script>
import { ref, onMounted, computed, watch } from 'vue'
import { storeToRefs } from 'pinia'
import { useProjectStore } from '../stores/projects'
import { useTaxonomyStore } from '../stores/taxonomies'
import { useToast } from '../composables/useToast'
import { useConfirmDialog } from '../composables/useConfirmDialog'
import { createLogger } from '../utils/logger'
import { createJsRegExp } from '../utils/taxonomyParser'
import { RefreshCw, FolderOpen, Clock, Package, AlertCircle, AlertTriangle, Trash2, Power, PowerOff, List as ListIcon, Square as SquareIcon, Edit3 } from '@lucide/vue'
import ProjectCard from './ProjectCard.vue'
import SearchableSelect from './SearchableSelect.vue'
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
    SearchableSelect,
    Modal
  },
  setup() {
    const projectStore = useProjectStore()
    const taxonomyStore = useTaxonomyStore()
    const { projects, isLoading, currentPage, pageSize, totalProjects, totalPages, searchQuery, paginatedProjects } = storeToRefs(projectStore)
    const { taxonomies } = storeToRefs(taxonomyStore)
    const { showSuccess, showError } = useToast()
    const {
      showConfirmDialog,
      confirmDialogTitle,
      confirmDialogMessage,
      confirmDialogConfirmText,
      confirmDialogCancelText,
      showConfirm,
      handleConfirm,
      handleCancel
    } = useConfirmDialog()
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

    // Loading states for batch operations
    const isDeleting = ref(false)
    const isActivating = ref(false)
    const isDeactivating = ref(false)

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

    // Paginate the locally-filtered set. `filteredProjects` applies all filters
    // (name / search / activity / SBOM) over the WHOLE loaded portfolio; we then
    // slice the requested page from that. Filtering before pagination is what
    // makes the filters actually take effect - previously the filters were
    // applied to an already-paginated single page, so they did nothing once the
    // match wasn't on the current page.
    const totalFiltered = computed(() => filteredProjects.value.length)
    const localTotalPages = computed(() => Math.max(1, Math.ceil(totalFiltered.value / pageSize.value)))
    const data = computed(() => {
      const start = (currentPage.value - 1) * pageSize.value
      return filteredProjects.value.slice(start, start + pageSize.value)
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

    const toggleProjectSelection = (uuid) => {
      const index = selectedProjects.value.indexOf(uuid)
      if (index === -1) {
        selectedProjects.value.push(uuid)
      } else {
        selectedProjects.value.splice(index, 1)
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

    // Tag styling functions
    const { getTaxonomyBadgeStyle } = taxonomyStore

    const getTagStyle = (tag) => {
      let hasTaxonomy = tag.taxonomy
      if (!hasTaxonomy) {
        hasTaxonomy = taxonomies.value.find(taxonomy => {
          if (!taxonomy.regex_pattern) return false
          const regex = createJsRegExp(taxonomy.regex_pattern)
          return regex ? regex.test(tag.name) : false
        })
      }
      if (hasTaxonomy) {
        tag._taxonomy = hasTaxonomy
      }
      if (hasTaxonomy) {
        return 'taxonomy'
      }
      return 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300'
    }

    const getTagDynamicStyle = (tag) => {
      let hasTaxonomy = tag.taxonomy
      if (!hasTaxonomy) {
        hasTaxonomy = taxonomies.value.find(taxonomy => {
          if (!taxonomy.regex_pattern) return false
          const regex = createJsRegExp(taxonomy.regex_pattern)
          return regex ? regex.test(tag.name) : false
        })
      }
      if (hasTaxonomy) {
        return getTaxonomyBadgeStyle(hasTaxonomy)
      }
      return {}
    }

    const getProjectName = (uuid) => {
      const project = projects.value.find(p => p.uuid === uuid)
      return project ? project.name : 'Unknown'
    }

    const deleteProject = async (project) => {
      const confirmed = await showConfirm({
        title: 'Delete Project',
        message: `Are you sure you want to delete "${project.name}"? This action cannot be undone.`,
        confirmText: 'Delete',
        cancelText: 'Cancel'
      })
      if (!confirmed) return

      try {
        await projectStore.deleteProject(project.uuid)
        selectedProjects.value = selectedProjects.value.filter(uuid => uuid !== project.uuid)
      } catch (error) {
        logger.error('Failed to delete project:', error)
        showError('Failed to delete project. Please try again.')
      }
    }

    const confirmDelete = async () => {
      isDeleting.value = true
      try {
        const result = await projectStore.bulkDeleteProjects(selectedProjects.value)

        // Store handles state updates, just clear local selection
        selectedProjects.value = []
        selectAll.value = false
        showDeleteConfirmation.value = false

        // Show appropriate message based on results
        if (result && result.failed > 0) {
          if (result.success > 0) {
            showSuccess(`Successfully deleted ${result.success} projects. ${result.failed} projects failed to delete.`)
          } else {
            showError('Failed to delete any projects. Please try again.')
          }
        } else {
          showSuccess('Successfully deleted all selected projects.')
        }
      } catch (error) {
        logger.error('Failed to delete projects:', error)
        showError('Failed to delete projects. Please try again.')
      } finally {
        isDeleting.value = false
      }
    }

    const confirmActivate = async () => {
      isActivating.value = true
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
        showSuccess('Successfully activated all selected projects.')
      } catch (error) {
        logger.error('Failed to activate projects:', error)
        showError('Failed to activate some projects. Please try again.')
      } finally {
        isActivating.value = false
      }
    }

    const confirmDeactivate = async () => {
      isDeactivating.value = true
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
        showSuccess('Successfully deactivated all selected projects.')
      } catch (error) {
        logger.error('Failed to deactivate projects:', error)
        showError('Failed to deactivate some projects. Please try again.')
      } finally {
        isDeactivating.value = false
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

    // Pagination is local to this view (it filters the full loaded portfolio
    // client-side, so it can't delegate paging to the store, whose page bounds
    // are based on the store's own filters).
    const goToPage = (page) => {
      currentPage.value = Math.min(Math.max(1, page), localTotalPages.value)
    }

    const nextPage = () => {
      if (currentPage.value < localTotalPages.value) currentPage.value += 1
    }

    const prevPage = () => {
      if (currentPage.value > 1) currentPage.value -= 1
    }

    const handlePageSizeChange = (newPageSize) => {
      pageSize.value = newPageSize
      currentPage.value = 1
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
    watch([activityFilter, sbomFilter, projectFilter], () => {
      // Reset to first page when filters change
      currentPage.value = 1
    }, { deep: true })

    // Search filters locally (via filteredProjects); reset to the first page.
    watch(() => searchQuery.value, () => {
      currentPage.value = 1
    })

    onMounted(() => {
      refreshProjects()
    })

    return {
      isLoading,
      projects,
      searchQuery,
      projectFilter,
      uniqueProjectNames,
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
      totalFiltered,
      localTotalPages,
      viewMode,
      data,
      refreshProjects,
      setQuickFilter,
      handleProjectFilterChange,
      clearFilters,
      toggleSelectAll,
      toggleProjectSelection,
      getActiveStatus,
      getActiveStatusClass,
      getActivityStatus,
      getActivityStatusClass,
      getSbomStatus,
      getSbomStatusClass,
      formatDate,
      getProjectVulnerabilities,
      getTagStyle,
      getTagDynamicStyle,
      getProjectName,
      deleteProject,
      isDeleting,
      isActivating,
      isDeactivating,
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
      analyzeProject,
      // Confirmation dialog (single-project delete)
      showConfirmDialog,
      confirmDialogTitle,
      confirmDialogMessage,
      confirmDialogConfirmText,
      confirmDialogCancelText,
      handleConfirm,
      handleCancel,
      // Icons for Modal components
      Power,
      PowerOff,
      Edit3,
      AlertCircle,
      AlertTriangle
    }
  }
}
</script>
