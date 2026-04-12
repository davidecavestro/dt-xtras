<template>
  <div class="h-full flex flex-col bg-gray-50 dark:bg-gray-900 relative">
    <!-- Fixed Header with Title, Buttons, and Selected Items -->
    <div class="fixed top-0 left-64 right-0 bg-white dark:bg-gray-800 shadow-sm border-b border-gray-200 dark:border-gray-700 px-6 py-4 z-10" style="--header-height: auto">
      <!-- Title and Description -->
      <div class="mb-4">
        <h1 class="text-2xl font-bold text-gray-900 dark:text-white">Tag Bulk Actions</h1>
        <p class="text-gray-600 dark:text-gray-400 mt-1">Link and unlink tags from projects in bulk</p>
      </div>

      <!-- Action Buttons -->
      <div class="mb-4">
        <!-- Primary Actions Row -->
        <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
          <div class="flex flex-col sm:flex-row sm:items-center gap-2 sm:gap-3">
            <button
              @click="confirmLink"
              :disabled="selectedTags.length === 0 || selectedProjects.length === 0 || loading"
              class="w-full sm:w-auto px-3 sm:px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors flex items-center justify-center sm:justify-start"
            >
              <Link class="w-4 h-4 mr-2 flex-shrink-0" />
              <span class="text-sm sm:text-base">Link Selected</span>
            </button>

            <button
              @click="confirmUnlink"
              :disabled="selectedTags.length === 0 || selectedProjects.length === 0 || loading"
              class="w-full sm:w-auto px-3 sm:px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors flex items-center justify-center sm:justify-start"
            >
              <Unlink class="w-4 h-4 mr-2 flex-shrink-0" />
              <span class="text-sm sm:text-base">Unlink Selected</span>
            </button>

            <button
              @click="clearSelection"
              :disabled="selectedTags.length === 0 && selectedProjects.length === 0"
              class="w-full sm:w-auto px-3 sm:px-4 py-2 bg-gray-600 text-white rounded-md hover:bg-gray-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors flex items-center justify-center sm:justify-start"
            >
              <span class="text-sm sm:text-base">Clear Selection</span>
            </button>
          </div>

          <button
            @click="refreshData"
            :disabled="loading"
            class="w-full sm:w-auto px-3 sm:px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors flex items-center justify-center sm:justify-start"
          >
            <RefreshCw :class="['w-4 h-4 mr-2 flex-shrink-0', loading && 'animate-spin']" />
            <span class="text-sm sm:text-base">Refresh</span>
          </button>
        </div>
      </div>

      <!-- Selected Items -->
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4 md:gap-6">
        <!-- Selected Tags -->
        <div>
          <h3 class="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Selected Tags ({{ selectedTags.length }})
          </h3>
          <div v-if="selectedTags.length === 0" class="text-sm text-gray-500 dark:text-gray-400 italic">
            No tags selected
          </div>
          <div v-else class="flex flex-wrap gap-2 max-h-24 overflow-y-auto">
            <span
              v-for="tagName in selectedTags"
              :key="tagName"
              @click="toggleTagSelection(tagName)"
              class="inline-flex items-center px-2 sm:px-3 py-1 rounded-full text-xs font-medium border cursor-pointer hover:opacity-80 transition-opacity"
              :style="getSelectedTagStyle(tagName)"
            >
              <span class="truncate max-w-20 sm:max-w-none">{{ tagName }}</span>
              <button
                @click.stop="toggleTagSelection(tagName)"
                class="ml-1 sm:ml-2 text-red-500 hover:text-red-700 text-xs font-bold flex-shrink-0"
                title="Remove tag"
              >
                ×
              </button>
            </span>
          </div>
        </div>

        <!-- Selected Projects -->
        <div>
          <h3 class="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Selected Projects ({{ selectedProjects.length }})
          </h3>
          <div v-if="selectedProjects.length === 0" class="text-sm text-gray-500 dark:text-gray-400 italic">
            No projects selected
          </div>
          <div v-else class="flex flex-wrap gap-2 max-h-24 overflow-y-auto">
            <span
              v-for="projectUuid in selectedProjects"
              :key="projectUuid"
              @click="toggleProjectSelection(projectUuid)"
              class="inline-flex items-center px-2 sm:px-3 py-1 rounded-full text-xs font-medium border cursor-pointer hover:opacity-80 transition-opacity"
              :style="getSelectedProjectStyle(projectUuid)"
            >
              <span class="truncate max-w-24 sm:max-w-none">{{ getProjectName(projectUuid) }}:{{ getProjectVersion(projectUuid) }}</span>
              <button
                @click.stop="toggleProjectSelection(projectUuid)"
                class="ml-1 sm:ml-2 text-red-500 hover:text-red-700 text-xs font-bold flex-shrink-0"
                title="Remove project"
              >
                ×
              </button>
            </span>
          </div>
        </div>
      </div>
    </div>

    <!-- Status Message -->
    <div v-if="statusMessage" :class="['fixed top-80 left-64 right-0 px-6 py-3 text-sm z-20', statusMessageClass]">
      {{ statusMessage }}
    </div>

    <!-- Main Content - Two Scrollable Columns -->
    <div class="flex-1 flex overflow-hidden" style="padding-top: var(--header-height, 12rem)">
      <!-- Left Column - Tags -->
      <div class="w-1/2 flex flex-col border-r border-gray-200 dark:border-gray-700">
        <div class="p-4 bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700">
          <h2 class="text-lg font-semibold text-gray-900 dark:text-white mb-3">Tags</h2>

          <!-- Tag Search -->
          <div class="mb-3">
            <div class="flex gap-2">
              <select
                v-model="selectedTaxonomy"
                @change="setTaxonomyFilter(selectedTaxonomy)"
                class="px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-white min-w-0 sm:min-w-32"
              >
                <option value="">All Taxonomies</option>
                <option
                  v-for="taxonomy in taxonomies"
                  :key="taxonomy.id"
                  :value="taxonomy.id"
                >
                  {{ taxonomy.name }}
                </option>
              </select>
              <input
                v-model="tagSearchQuery"
                @input="setTagSearchQuery(tagSearchQuery)"
                type="text"
                placeholder="Search by tag name..."
                class="flex-1 px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
              />
            </div>
          </div>

          <!-- Tag Pagination Controls -->
          <div v-if="totalTagPages > 1" class="mb-4 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
            <!-- Info and Page Size -->
            <div class="flex flex-col sm:flex-row sm:items-center gap-2 sm:gap-4">
              <div class="text-sm text-gray-700 dark:text-gray-300 hidden sm:block">
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
            <!-- Navigation Buttons -->
            <div class="flex items-center justify-center sm:justify-end space-x-2">
              <button
                @click="previousTagPage"
                :disabled="!hasPreviousTagPage || tagsLoading"
                class="px-3 py-1 text-sm border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
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

          <div v-else class="flex-1 overflow-y-auto">
            <div class="space-y-2">
              <div
                v-for="tag in paginatedTags"
                :key="tag.name"
                class="flex items-center p-2 hover:bg-gray-50 dark:hover:bg-gray-700 rounded cursor-pointer"
                @click="toggleTagSelection(tag.name)"
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
      </div>

      <!-- Right Column - Projects -->
      <div class="w-1/2 flex flex-col bg-white dark:bg-gray-800">
        <div class="p-4 border-b border-gray-200 dark:border-gray-700">
          <h2 class="text-lg font-semibold text-gray-900 dark:text-white mb-3">Projects</h2>

          <!-- Project Search -->
          <div class="mb-3">
            <div class="flex gap-2">
              <select
                v-model="projectFilter"
                @change="handleProjectFilterChange(projectFilter)"
                class="px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-white min-w-0 sm:min-w-32"
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
              <input
                v-model="projectSearchQuery"
                @input="setProjectSearchQuery(projectSearchQuery)"
                type="text"
                placeholder="Filter by project, version or tags..."
                class="flex-1 px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
              />
            </div>
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
          <div v-if="totalProjectPages > 1" class="mb-4 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
            <!-- Info and Page Size -->
            <div class="flex flex-col sm:flex-row sm:items-center gap-2 sm:gap-4">
              <div class="text-sm text-gray-700 dark:text-gray-300 hidden sm:block">
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
            <!-- Navigation Buttons -->
            <div class="flex items-center justify-center sm:justify-end space-x-2">
              <button
                @click="previousProjectPage"
                :disabled="!hasPreviousProjectPage || projectsLoading"
                class="px-3 py-1 text-sm border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
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
              class="flex items-center p-2 hover:bg-gray-50 dark:hover:bg-gray-700 rounded cursor-pointer"
              @click="toggleProjectSelection(project.uuid)"
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
                <div v-if="project.tags && project.tags.length > 0" class="text-sm flex flex-wrap gap-1 mt-1">
                  <!-- Existing tags -->
                  <span
                    v-for="tag in project.tags"
                    :key="tag.name"
                    class="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium border"
                    :class="getTagStyle(tag, project.uuid)"
                    :style="getTagDynamicStyle(tag, project.uuid)"
                  >
                    {{ tag.name }}
                  </span>
                  <!-- Temporary preview tags (selected tags that don't exist on this project) -->
                  <span
                    v-for="selectedTag in selectedTags"
                    :key="'preview-' + selectedTag"
                    v-show="selectedProjects.includes(project.uuid) && (!project.tags || !project.tags.some(t => t.name === selectedTag))"
                    class="inline-flex items-center px-2 py-1 rounded-full text-xs font-bold border bg-blue-100 dark:bg-blue-900 text-blue-600 dark:text-blue-400 border-blue-300 dark:border-blue-700"
                  >
                    {{ selectedTag }}
                  </span>
                </div>
                <!-- Handle case where project has no tags but selected tags should show as preview -->
                <div v-else-if="selectedTags.length > 0 && selectedProjects.includes(project.uuid)" class="text-sm flex flex-wrap gap-1 mt-1">
                  <span
                    v-for="selectedTag in selectedTags"
                    :key="'preview-' + selectedTag"
                    class="inline-flex items-center px-2 py-1 rounded-full text-xs font-bold border bg-blue-100 dark:bg-blue-900 text-blue-600 dark:text-blue-400 border-blue-300 dark:border-blue-700"
                  >
                    {{ selectedTag }}
                  </span>
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
        <div v-if="projectsToBeLinked.length > 0" class="mb-4 p-3 bg-green-50 dark:bg-green-900 rounded-md">
          <p class="text-sm font-medium text-green-800 dark:text-green-200 mb-2">
            Projects that will have tags added:
          </p>
          <ul class="list-disc list-inside text-sm text-green-700 dark:text-green-300 space-y-1">
            <li v-for="project in projectsToBeLinked" :key="project.uuid" class="flex items-center">
              <span class="font-medium">{{ getProjectName(project.uuid) }}</span>
              <span class="text-xs text-green-600 dark:text-green-400 ml-2">({{ getProjectVersion(project.uuid) }})</span>
            </li>
          </ul>
        </div>
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
        <div v-if="projectsToBeUnlinked.length > 0" class="mb-4 p-3 bg-red-50 dark:bg-red-900 rounded-md">
          <p class="text-sm font-medium text-red-800 dark:text-red-200 mb-2">
            Projects that will have tags removed:
          </p>
          <ul class="list-disc list-inside text-sm text-red-700 dark:text-red-300 space-y-1">
            <li v-for="project in projectsToBeUnlinked" :key="project.uuid" class="flex items-center">
              <span class="font-medium">{{ getProjectName(project.uuid) }}</span>
              <span class="text-xs text-gray-600 dark:text-gray-400 ml-2">({{ getProjectVersion(project.uuid) }})</span>
            </li>
          </ul>
        </div>
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
      selectedTaxonomy,
      filteredTags,
      paginatedTags,
      hasPreviousPage: hasPreviousTagPage,
      hasNextPage: hasNextTagPage
    } = storeToRefs(tagStore)

    const {
      loadTags,
      setSearchQuery: setTagSearchQuery,
      setTaxonomyFilter,
      goToPage: goToTagPage,
      nextPage: nextTagPage,
      previousPage: previousTagPage,
      clearFilters: clearTagFilters,
      setPageSize: setTagPageSize,
      linkTagsToProjects,
      unlinkTagsFromProjects
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
      projectFilter,
      filteredProjects,
      paginatedProjects,
      hasPreviousPage: hasPreviousProjectPage,
      hasNextPage: hasNextProjectPage,
      activeOnly
    } = storeToRefs(projectStore)

    const {
      loadProjects,
      setSearchQuery: setProjectSearchQuery,
      setProjectFilter,
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
    const selectedProjectFilter = ref('')

    // Computed property for unique project names
    const uniqueProjectNames = computed(() => {
      if (!projects.value) return []
      const names = new Set()
      projects.value.forEach(project => {
        const name = project.displayName || project.name
        if (name) names.add(name)
      })
      return Array.from(names).sort()
    })

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

    // Computed properties to track projects affected by bulk operations
    const projectsToBeLinked = computed(() => {
      if (selectedTags.value.length === 0 || selectedProjects.value.length === 0) return []

      return paginatedProjects.value.filter(project =>
        !selectedProjects.value.includes(project.uuid)
      )
    })

    const projectsToBeUnlinked = computed(() => {
      if (selectedTags.value.length === 0 || selectedProjects.value.length === 0) return []

      return paginatedProjects.value.filter(project =>
        selectedProjects.value.includes(project.uuid)
      )
    })

    const getProjectStyle = (projectUuid) => {
      const willBeUnlinked = projectsToBeUnlinked.value.some(p => p.uuid === projectUuid)
      const willBeLinked = projectsToBeLinked.value.some(p => p.uuid === projectUuid)

      if (willBeUnlinked) {
        return 'line-through text-red-600 dark:text-red-400'
      } else if (willBeLinked) {
        return 'font-bold text-green-600 dark:text-green-400'
      }
      return ''
    }

    const getTagStyle = (tag, projectUuid) => {
      const isProjectSelected = selectedProjects.value.includes(projectUuid)
      const isTagSelected = selectedTags.value.includes(tag.name)

      // Try to get taxonomy from tag object first, then fallback to store lookup
      let hasTaxonomy = getTagTaxonomy(tag)

      // If tag doesn't have taxonomy info, try to find it by matching tag name with taxonomies
      if (!hasTaxonomy) {
        hasTaxonomy = taxonomies.value.find(taxonomy => {
          if (!taxonomy.regex_pattern) return false
          try {
            return new RegExp(taxonomy.regex_pattern).test(tag.name)
          } catch (e) {
            return false
          }
        })
      }

      const project = projects.value.find(p => p.uuid === projectUuid)
      const tagExistsOnProject = project && project.tags && project.tags.some(t => t.name === tag.name)

      // Store taxonomy reference for style application
      if (hasTaxonomy) {
        tag._taxonomy = hasTaxonomy
      }

      // Red strikethrough: tag exists on selected project and will be unlinked
      if (isProjectSelected && isTagSelected && tagExistsOnProject) {
        return 'line-through text-red-600 dark:text-red-400 bg-red-50 dark:bg-red-900 border-red-200 dark:border-red-700'
      }

      // Green bold: tag doesn't exist on selected project but will be linked (visual preview)
      if (isProjectSelected && isTagSelected && !tagExistsOnProject) {
        return 'font-bold text-green-600 dark:text-green-400'
      }

      // Show taxonomy colors for existing tags on selected projects (not in selection)
      if (hasTaxonomy && isProjectSelected && !isTagSelected) {
        return 'taxonomy'
      }

      // Show taxonomy colors for tags on unselected projects
      if (hasTaxonomy && !isProjectSelected) {
        return 'taxonomy'
      }

      return 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300'
    }

    const getTagStyleForTemplate = (tag, projectUuid) => {
      const styleClass = getTagStyle(tag, projectUuid)
      return styleClass
    }

    const getTagDynamicStyle = (tag, projectUuid) => {
      const isProjectSelected = selectedProjects.value.includes(projectUuid)
      const isTagSelected = selectedTags.value.includes(tag.name)

      // Get taxonomy using same logic as getTagStyle
      let hasTaxonomy = getTagTaxonomy(tag)
      if (!hasTaxonomy) {
        hasTaxonomy = taxonomies.value.find(taxonomy => {
          if (!taxonomy.regex_pattern) return false
          try {
            return new RegExp(taxonomy.regex_pattern).test(tag.name)
          } catch (e) {
            return false
          }
        })
      }

      const project = projects.value.find(p => p.uuid === projectUuid)
      const tagExistsOnProject = project && project.tags && project.tags.some(t => t.name === tag.name)

      // Return taxonomy style if it's a taxonomy tag
      if (hasTaxonomy &&
          ((isProjectSelected && !isTagSelected) || !isProjectSelected)) {
        return getTaxonomyBadgeStyle(hasTaxonomy)
      }

      return {}
    }

    const getSelectedTagStyle = (tagName) => {
      // Find taxonomy for this tag name
      let hasTaxonomy = taxonomies.value.find(taxonomy => {
        if (!taxonomy.regex_pattern) return false
        try {
          return new RegExp(taxonomy.regex_pattern).test(tagName)
        } catch (e) {
          return false
        }
      })

      // Return taxonomy style if found, otherwise default style
      if (hasTaxonomy) {
        return getTaxonomyBadgeStyle(hasTaxonomy)
      }

      return {
        backgroundColor: '#e5e7eb',
        color: '#374151',
        borderColor: '#d1d5db'
      }
    }

    const getSelectedProjectStyle = (projectUuid) => {
      // Projects don't have taxonomy colors, so return default styling
      // The CSS classes from getProjectStyle will handle the red strikethrough for unlinking
      return {
        backgroundColor: '#e5e7eb',
        color: '#374151',
        borderColor: '#d1d5db'
      }
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
        // for every selected tag, invoke the api that link it to the selected projects
        await Promise.all(selectedTags.value.map(async (tag) => {
          await linkTagsToProjects(tag, selectedProjects.value)
        }))


        statusMessage.value = `Successfully linked ${selectedTags.value.length} tags to ${selectedProjects.value.length} projects`
        statusMessageClass.value = 'text-green-600 dark:text-green-400'

        // Reload data to reflect changes
        await refreshData()
      } catch (error) {
        logger.error('Error linking tags to projects:', error)
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
        // for every selected tag, invoke the api that link it to the selected projects
        await Promise.all(selectedTags.value.map(async (tag) => {
          await unlinkTagsFromProjects(tag, selectedProjects.value)
        }))

        statusMessage.value = `Successfully unlinked ${selectedTags.value.length} tags from ${selectedProjects.value.length} projects`
        statusMessageClass.value = 'text-green-600 dark:text-green-400'

        // Reload data to reflect changes
        await refreshData()
      } catch (error) {
        logger.error('Error unlinking tags from projects:', error)
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

    const handleProjectFilterChange = (projectName) => {
      if (projectName) {
        // Set project filter to the selected project name
        setProjectFilter(projectName)
        selectedProjectFilter.value = projectName
      } else {
        // Clear filter
        selectedProjectFilter.value = ''
        setProjectFilter('')
      }
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
      projectFilter,
      selectedTaxonomy,
      filteredTags,
      filteredProjects,
      paginatedTags,
      paginatedProjects,
      hasPreviousTagPage,
      hasNextTagPage,
      hasPreviousProjectPage,
      hasNextProjectPage,
      activeOnly,

      // Local computed
      uniqueProjectNames,

      // Store methods
      loadTags,
      loadProjects,
      setTagSearchQuery,
      setTaxonomyFilter,
      setProjectSearchQuery,
      setProjectFilter,
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

      // Computed properties for visual indicators
      projectsToBeLinked,
      projectsToBeUnlinked,
      getProjectStyle,
      getTagStyle,
      getTagDynamicStyle,
      getSelectedTagStyle,
      getSelectedProjectStyle,

      // Local methods
      toggleSelectAllTags,
      toggleSelectAllProjects,
      getProjectName,
      getProjectVersion,
      toggleTagSelection,
      toggleProjectSelection,
      confirmLink,
      confirmUnlink,
      clearSelection,
      buildDTProjectUrl,
      handleProjectFilterChange,
      refreshData,

      // Local state
      selectedProjectFilter
    }
  }
}
</script>
