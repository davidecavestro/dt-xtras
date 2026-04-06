<template>
  <div class="px-4 py-6 sm:px-0">
    <div class="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
      <h2 class="text-2xl font-bold text-gray-900 dark:text-white mb-6">Tag Center</h2>
      <p class="text-gray-600 dark:text-gray-400 mb-6">
        Manage tags and link them to Dependency-Track projects
      </p>

      <!-- Create Tag Button -->
      <div class="mb-6">
        <button
          @click="showCreateTagModal = true"
          class="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
        >
          Create Tag
        </button>
      </div>
    </div>

    <!-- Existing Tags Management -->
    <div class="bg-white dark:bg-gray-800 rounded-lg shadow p-6 mt-6">
      <div class="flex justify-between items-center mb-4">
        <h2 class="text-lg font-semibold text-gray-900 dark:text-white">Existing Tags</h2>
        <div class="flex items-center gap-2">
          <div class="text-sm text-gray-600 dark:text-gray-400">
            {{ tags.length }} tags
          </div>
          <!-- View Mode Controls -->
          <div class="flex items-center space-x-2">
            <button
              @click="tagsViewMode = 'list'"
              :class="[
                'px-3 py-1 text-sm rounded-md',
                tagsViewMode === 'list'
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300'
              ]"
            >
              <ListIcon class="w-4 h-4" />
            </button>
            <button
              @click="tagsViewMode = 'deck'"
              :class="[
                'px-3 py-1 text-sm rounded-md',
                tagsViewMode === 'deck'
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300'
              ]"
            >
              <SquareIcon class="w-4 h-4" />
            </button>
            <button
              @click="tagsViewMode = 'grid'"
              :class="[
                'px-3 py-1 text-sm rounded-md',
                tagsViewMode === 'grid'
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300'
              ]"
            >
              <GridIcon class="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>

      <!-- Search and Filters -->
      <div v-if="tags.length > 0" class="bg-white dark:bg-gray-800 rounded-lg shadow p-4 mb-6">
        <div class="flex flex-col sm:flex-row gap-4">
          <!-- Search -->
          <div class="flex-1">
            <input
              v-model="searchQuery"
              @input="setSearchQuery(searchQuery)"
              type="text"
              placeholder="Search tags..."
              class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
            />
          </div>

          <!-- Taxonomy Filter -->
          <div class="sm:w-48">
            <select
              v-model="selectedTaxonomy"
              @change="setTaxonomyFilter(selectedTaxonomy)"
              class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
            >
              <option value="">All Taxonomies</option>
              <option v-for="taxonomy in taxonomies" :key="taxonomy.id" :value="taxonomy.id">
                {{ taxonomy.name }}
              </option>
            </select>
          </div>

          <!-- Clear Filters -->
          <button
            @click="clearFilters"
            class="px-4 py-2 bg-gray-600 text-white rounded-md hover:bg-gray-700 transition-colors"
          >
            Clear Filters
          </button>
        </div>

        <!-- Results Count -->
        <div class="mt-3 text-sm text-gray-600 dark:text-gray-400">
          Showing {{ paginatedTags.length }} of {{ totalTags }} tags
        </div>
      </div>

      <!-- Pagination Controls -->
      <div v-if="totalPages > 1" class="flex items-center justify-between mb-6 px-4">
        <div class="flex items-center space-x-4">
          <div class="text-sm text-gray-700 dark:text-gray-300">
            Showing {{ paginatedTags.length }} of {{ totalTags }} tags
          </div>
          <div class="flex items-center space-x-2">
            <label class="text-sm text-gray-600 dark:text-gray-400">Page size:</label>
            <select
              v-model="pageSize"
              @change="setPageSize(pageSize)"
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
            @click="previousPage"
            :disabled="!hasPreviousPage"
            class="px-3 py-1 text-sm border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
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
            :disabled="!hasNextPage"
            class="px-3 py-1 text-sm border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
            </svg>
          </button>
        </div>
      </div>

      <!-- Tags List -->
      <div v-if="tags.length === 0" class="text-center py-8 text-gray-500 dark:text-gray-400">
        No tags created yet. Create your first tag above.
      </div>

      <!-- List View -->
      <div v-else-if="tagsViewMode === 'list'" class="space-y-3">
        <div
          v-for="tag in paginatedTags"
          :key="tag.name"
          class="flex items-center justify-between p-3 border border-gray-200 dark:border-gray-700 rounded-lg"
        >
          <div class="flex-1">
            <!-- Show tag name or edit input -->
            <div v-if="editingTag && editingTag.name === tag.name" class="flex items-center">
              <input
  :data-tag-name="tag.name"
  v-model="editingTagName"
  @keyup.enter="saveEditTag"
  @keyup.escape="cancelEditTag"
  @blur="saveEditTag"
  class="font-medium text-gray-900 dark:text-white bg-transparent border-b border-gray-300 dark:border-gray-600 focus:border-blue-500 focus:outline-none flex-1"
  placeholder="Tag name"
/>
              <button
                @click="saveEditTag"
                class="ml-2 p-1 bg-green-600 text-white text-xs rounded hover:bg-green-700"
                title="Save"
              >
                ✓
              </button>
              <button
                @click="cancelEditTag"
                class="ml-1 p-1 bg-gray-600 text-white text-xs rounded hover:bg-gray-700"
                title="Cancel"
              >
                ✕
              </button>
            </div>
            <div v-else>
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

          <div class="flex gap-1 p-2 flex-shrink-0">
            <button
              @click="viewTagProjects(tag)"
              class="p-1 bg-blue-600 text-white text-xs rounded hover:bg-blue-700 inline-flex items-center justify-center transition-colors"
              title="View Projects"
            >
              <Folder class="w-3 h-3" />
            </button>
            <button
              @click="startEditTag(tag)"
              class="p-1 bg-yellow-600 text-white text-xs rounded hover:bg-yellow-700 inline-flex items-center justify-center transition-colors"
              title="Edit Tag"
            >
              <Edit2 class="w-3 h-3" />
            </button>
            <button
              v-if="tagBelongsToTaxonomy(tag)"
              @click="startAidedEditTag(tag)"
              class="p-1 bg-purple-600 text-white text-xs rounded hover:bg-purple-700 inline-flex items-center justify-center transition-colors"
              title="Aided Edit"
            >
              <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-3 7h3m-3 4h3m-6-4h.01M9 16h.01"></path>
              </svg>
            </button>
            <button
              @click="startCloneTag(tag)"
              class="p-1 bg-indigo-600 text-white text-xs rounded hover:bg-indigo-700 inline-flex items-center justify-center transition-colors"
              title="Clone Tag"
            >
              <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012-2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z"></path>
              </svg>
            </button>
            <button
              v-if="tag.projectsCount > 0"
              @click="startCopyProjectsToTag(tag)"
              class="p-1 bg-teal-600 text-white text-xs rounded hover:bg-teal-700 inline-flex items-center justify-center transition-colors"
              title="Copy Projects to Tag"
            >
              <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-2a2 2 0 00-2-2h-2M8 7a2 2 0 002 2h2a2 2 0 002-2m-3 7h3m-3 4h3m-6-4h.01M9 16h.01"></path>
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 21l-4-4 4-4M4 13l4 4 4 4"></path>
              </svg>
            </button>
            <button
              @click="handleDeleteTag(tag)"
              class="p-1 bg-red-600 text-white text-xs rounded hover:bg-red-700 inline-flex items-center justify-center transition-colors"
              title="Delete"
            >
              <Trash2 class="w-3 h-3" />
            </button>
          </div>
        </div>
      </div>

      <!-- Pagination Controls for List View -->
      <div v-if="tagsViewMode === 'list' && totalPages > 1" class="flex items-center justify-between mb-6 px-4">
        <div class="flex items-center space-x-4">
          <div class="text-sm text-gray-700 dark:text-gray-300">
            Showing {{ paginatedTags.length }} of {{ totalTags }} tags
          </div>
          <div class="flex items-center space-x-2">
            <label class="text-sm text-gray-600 dark:text-gray-400">Page size:</label>
            <select
              v-model="pageSize"
              @change="setPageSize(pageSize)"
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
            @click="previousPage"
            :disabled="!hasPreviousPage"
            class="px-3 py-1 text-sm border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
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
            :disabled="!hasNextPage"
            class="px-3 py-1 text-sm border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
            </svg>
          </button>
        </div>
      </div>

      <!-- Grid View -->
      <div v-else-if="tagsViewMode === 'grid'" class="overflow-y-auto" style="height: 400px;">
        <vue3-datagrid
          :columns="gridColumns"
          :source="tags"
          :row-height="60"
          :virtual="true"
          :page-size="20"
          :theme="isDarkMode ? 'darkCompact' : 'compact'"
          :filter="true"
          :resize="true"
          :autoSizeColumn="{ mode: 'autoSizeOnTextOverlap' }"
          :stretch="true"
          :readonly="true"
        />
      </div>

      <!-- Deck View (Current Default) -->
      <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        <div
          v-for="tag in paginatedTags"
          :key="tag.name"
          class="bg-white dark:bg-gray-700 rounded-lg shadow p-4 border border-gray-200 dark:border-gray-600 hover:shadow-md transition-shadow flex flex-col"
        >
          <div class="flex-1">
            <!-- Show tag name or edit input -->
            <div v-if="editingTag && editingTag.name === tag.name" class="flex items-center">
              <input
  :data-tag-name="tag.name"
  v-model="editingTagName"
  @keyup.enter="saveEditTag"
  @keyup.escape="cancelEditTag"
  @blur="saveEditTag"
  class="font-medium text-gray-900 dark:text-white bg-transparent border-b border-gray-300 dark:border-gray-600 focus:border-blue-500 focus:outline-none flex-1"
  placeholder="Tag name"
/>
              <button
                @click="saveEditTag"
                class="ml-2 p-1 bg-green-600 text-white text-xs rounded hover:bg-green-700"
                title="Save"
              >
                ✓
              </button>
              <button
                @click="cancelEditTag"
                class="ml-1 p-1 bg-gray-600 text-white text-xs rounded hover:bg-gray-700"
                title="Cancel"
              >
                ✕
              </button>
            </div>
            <div v-else>
              <div class="font-medium text-gray-900 dark:text-white mb-2 flex items-center flex-wrap gap-2">
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

          <div class="flex justify-end gap-1 pt-2 mt-2 border-t border-gray-200 dark:border-gray-600">
            <button
              @click="viewTagProjects(tag)"
              class="p-1 bg-blue-600 text-white text-xs rounded hover:bg-blue-700 inline-flex items-center justify-center transition-colors"
              title="View Projects"
            >
              <Folder class="w-3 h-3" />
            </button>
            <button
              @click="startEditTag(tag)"
              class="p-1 bg-yellow-600 text-white text-xs rounded hover:bg-yellow-700 inline-flex items-center justify-center transition-colors"
              title="Edit Tag"
            >
              <Edit2 class="w-3 h-3" />
            </button>
            <button
              v-if="tagBelongsToTaxonomy(tag)"
              @click="startAidedEditTag(tag)"
              class="p-1 bg-purple-600 text-white text-xs rounded hover:bg-purple-700 inline-flex items-center justify-center transition-colors"
              title="Aided Edit"
            >
              <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-3 7h3m-3 4h3m-6-4h.01M9 16h.01"></path>
              </svg>
            </button>
            <button
              @click="startCloneTag(tag)"
              class="p-1 bg-indigo-600 text-white text-xs rounded hover:bg-indigo-700 inline-flex items-center justify-center transition-colors"
              title="Clone Tag"
            >
              <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012-2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z"></path>
              </svg>
            </button>
            <button
              v-if="tag.projectsCount > 0"
              @click="startCopyProjectsToTag(tag)"
              class="p-1 bg-teal-600 text-white text-xs rounded hover:bg-teal-700 inline-flex items-center justify-center transition-colors"
              title="Copy Projects to Tag"
            >
              <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-2a2 2 0 00-2-2h-2M8 7a2 2 0 002 2h2a2 2 0 002-2m-3 7h3m-3 4h3m-6-4h.01M9 16h.01"></path>
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 21l-4-4 4-4M4 13l4 4 4 4"></path>
              </svg>
            </button>
            <button
              @click="handleDeleteTag(tag)"
              class="p-1 bg-red-600 text-white text-xs rounded hover:bg-red-700 inline-flex items-center justify-center transition-colors"
              title="Delete"
            >
              <Trash2 class="w-3 h-3" />
            </button>
          </div>
        </div>
      </div>
    </div>


    <!-- Projects Modal -->
    <div v-if="showProjectsModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-white dark:bg-gray-800 rounded-lg shadow-xl max-w-2xl w-full mx-4 max-h-[80vh] overflow-y-auto">
        <div class="p-6">
          <div class="flex justify-between items-center mb-4">
            <h3 class="text-lg font-semibold text-gray-900 dark:text-white">
              Projects with tag: {{ selectedTag?.name }}
            </h3>
            <div class="text-sm text-gray-600 dark:text-gray-400">
              Click project names to view in Dependency Track UI
            </div>
            <button
              @click="closeProjectsModal"
              class="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
            >
              ✕
            </button>
          </div>

          <div v-if="tagProjects.length === 0" class="text-center py-8 text-gray-500 dark:text-gray-400">
            No projects found with this tag.
          </div>

          <div v-else class="space-y-3">
            <div
              v-for="project in tagProjects"
              :key="project.uuid"
              class="p-3 border border-gray-200 dark:border-gray-700 rounded-lg"
            >
              <div class="flex items-start justify-between">
                <div class="flex-1 min-w-0">
                  <div class="font-medium text-gray-900 dark:text-white mb-1">
                    <a
                      :href="buildDTProjectUrl(project.uuid)"
                      target="_blank"
                      class="text-blue-600 hover:text-blue-800 hover:underline"
                      title="View in Dependency Track"
                    >
                      {{ project.name }}
                    </a>
                  </div>
                  <div class="text-sm text-gray-600 dark:text-gray-400 flex items-center flex-wrap gap-2">
                    <span>Version: {{ project.version }}</span>
                    <a
                      :href="buildDTProjectUrl(project.uuid)"
                      target="_blank"
                      rel="noopener noreferrer"
                      class="text-xs text-blue-600 dark:text-blue-400 hover:text-blue-800 dark:hover:text-blue-300 flex items-center"
                      title="View in Dependency-Track"
                    >
                      <svg class="w-3 h-3 mr-1" fill="currentColor" viewBox="0 0 20 20">
                        <path d="M11 3a1 1 0 100 2h2.586l-6.293 6.293a1 1 0 101.414 1.414L15 6.414V9a1 1 0 102 0V4a1 1 0 00-1-1h-3z"/>
                        <path d="M5 5a2 2 0 00-2 2v8a2 2 0 002 2h8a2 2 0 002-2v-3a1 1 0 10-2 0v3H5V7h3a1 1 0 000-2H5z"/>
                      </svg>
                      DT
                    </a>
                    <span v-if="project.tags && project.tags.length > 0">
                      Tags: {{ project.tags.join(', ') }}
                    </span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Create Tag Modal (Aided Edit) -->
    <div v-if="showCreateTagModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-white dark:bg-gray-800 rounded-lg shadow-xl max-w-4xl w-full mx-4 max-h-[80vh] overflow-y-auto">
        <div class="p-6">
          <div class="flex justify-between items-center mb-4">
            <h3 class="text-lg font-semibold text-gray-900 dark:text-white">
              {{ editingTag ? 'Edit Tag' : 'Create Tag' }} for {{ selectedTaxonomy?.name }}
            </h3>
            <button
              @click="closeCreateTagModal"
              class="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
            >
              ✕
            </button>
          </div>

          <!-- Pattern Display -->
          <div class="mb-4 p-3 bg-gray-100 dark:bg-gray-700 rounded-lg">
            <div class="text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Pattern:</div>
            <code class="text-sm bg-gray-200 dark:bg-gray-600 px-3 py-2 rounded text-gray-800 dark:text-gray-200 font-mono break-all hover:bg-gray-300 dark:hover:bg-gray-600 transition-colors">{{ selectedTaxonomy?.regex_pattern }}</code>
          </div>

          <!-- Dynamic Tag Builder -->
          <div class="space-y-4">
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300">
              Build Tag
            </label>

            <div class="flex flex-wrap items-center gap-2 p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
              <template v-for="(part, index) in tagBuilderParts" :key="index">
                <!-- Static text part -->
                <span v-if="part.type === 'static'" class="text-gray-700 dark:text-gray-300 font-medium">
                  {{ part.value }}
                </span>

                <!-- Dropdown for capture group with existing tags -->
                <select
                  v-else-if="part.type === 'dropdown'"
                  v-model="part.value"
                  class="px-3 py-2 border border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-white rounded-md shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
                >
                  <option value="">Select {{ part.name }}...</option>
                  <option v-for="option in part.options" :key="option" :value="option">
                    {{ option }}
                  </option>
                </select>

                <!-- Text field for capture group without existing tags -->
                <input
                  v-else-if="part.type === 'text'"
                  v-model="part.value"
                  type="text"
                  :placeholder="`Enter ${part.name}...`"
                  class="px-3 py-2 border border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-white rounded-md shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
                />
              </template>
            </div>

            <!-- Generated Tag Preview -->
            <div class="mt-4">
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Generated Tag
              </label>
              <div class="p-3 bg-gray-100 dark:bg-gray-800 rounded-md">
                <span class="font-mono text-gray-900 dark:text-white">
                  {{ generatedTag || 'Complete all fields to see tag...' }}
                </span>
              </div>
            </div>
          </div>

          <!-- Action Buttons -->
          <div class="mt-6 flex gap-2">
            <button
              @click="createOrUpdateTag"
              :disabled="!canCreateTag"
              class="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
            >
              {{ editingTag ? 'Update Tag' : 'Create Tag' }}
            </button>
            <button
              @click="closeCreateTagModal"
              class="px-4 py-2 bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-md hover:bg-gray-300 dark:hover:bg-gray-600 transition-colors"
            >
              Cancel
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Clone Tag Modal -->
    <div v-if="showCloneTagModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-white dark:bg-gray-800 rounded-lg shadow-xl max-w-4xl w-full mx-4 max-h-[80vh] overflow-y-auto">
        <div class="p-6">
          <div class="flex justify-between items-center mb-4">
            <h3 class="text-lg font-semibold text-gray-900 dark:text-white">Clone Tag: {{ cloningTag?.name }}</h3>
            <button
              @click="closeCloneTagModal"
              class="text-gray-400 hover:text-gray-500 dark:text-gray-500 dark:hover:text-gray-400"
            >
              <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>

          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <!-- Tag Input - Only show when no capture groups -->
            <div v-if="!hasCaptureGroups">
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-300">
                New Tag Name
                <span class="ml-2 text-xs text-gray-500 dark:text-gray-400">
                  (e.g., env:prod, cust:acme, myapp:1.0.0)
                </span>
              </label>
              <input
                ref="cloneTagInput"
                data-clone-tag-input
                v-model="cloneTagName"
                type="text"
                class="mt-1 block w-full rounded-md border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-white shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
                placeholder="Enter new tag name..."
                @input="validateCloneTag"
              />
              <div v-if="cloneTagValidation.message" :class="[
                'mt-1 text-xs',
                cloneTagValidation.valid ? 'text-green-600 dark:text-green-400' : 'text-red-600 dark:text-red-400'
              ]">
                {{ cloneTagValidation.message }}
              </div>
            </div>

            <!-- Project Linking Option -->
            <div v-if="cloningTag.projectsCount" class="bg-gray-50 dark:bg-gray-700 rounded-lg p-4">
              <h3 class="text-sm font-semibold text-gray-900 dark:text-white mb-3">Project Linking</h3>
              <div class="space-y-3">
                <div class="flex items-center">
                  <input
                    id="linkProjects"
                    v-model="linkProjects"
                    type="checkbox"
                    class="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 dark:border-gray-600 rounded dark:bg-gray-700"
                  />
                  <label for="linkProjects" class="ml-2 text-sm text-gray-700 dark:text-gray-300">
                    Link projects from original tag
                  </label>
                </div>
                <div v-if="cloningTag" class="text-xs text-gray-500 dark:text-gray-400">
                  Original tag is linked to {{ cloningTag.projectsCount || 0 }} projects
                </div>
              </div>
            </div>
          </div>

          <!-- Taxonomy Patterns (if original tag belongs to taxonomy) -->
          <div v-if="cloningTag && cloningTag.taxonomy" class="mt-4 bg-gray-50 dark:bg-gray-700 rounded-lg p-4">
            <h3 class="text-sm font-semibold text-gray-900 dark:text-white mb-3">Taxonomy Pattern</h3>
            <div class="flex items-start mb-4">
              <span class="font-medium text-gray-700 dark:text-gray-300 text-sm mr-2 min-w-0">
                {{ taxonomies.find(t => t.id === cloningTag.taxonomy)?.name || cloningTag.taxonomy }}:
              </span>
              <code class="text-xs bg-gray-100 dark:bg-gray-600 px-2 py-1 rounded text-gray-800 dark:text-gray-200 break-all">
                {{ taxonomies.find(t => t.id === cloningTag.taxonomy)?.regex_pattern || 'Pattern not found' }}
              </code>
            </div>

            <!-- Dynamic Tag Builder for Clone - Only show when there are capture groups -->
            <div v-if="hasCaptureGroups" class="space-y-4">
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-300">
                Build Clone
              </label>

              <div class="flex flex-wrap items-center gap-2 p-4 bg-gray-50 dark:bg-gray-600 rounded-lg">
                <template v-for="(part, index) in tagBuilderParts" :key="index">
                  <!-- Static text part -->
                  <span v-if="part.type === 'static'" class="text-gray-700 dark:text-gray-300 font-medium">
                    {{ part.value }}
                  </span>

                  <!-- Dropdown for capture group with existing tags -->
                  <select
                    v-else-if="part.type === 'dropdown'"
                    v-model="part.value"
                    :data-tag-builder-field="index === 0 ? 'first' : null"
                    class="px-3 py-2 border border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-white rounded-md shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
                  >
                    <option value="">Select {{ part.name }}...</option>
                    <option v-for="option in part.options" :key="option" :value="option">
                      {{ option }}
                    </option>
                  </select>

                  <!-- Text field for capture group without existing tags -->
                  <input
                    v-else-if="part.type === 'text'"
                    v-model="part.value"
                    :data-tag-builder-field="index === 0 ? 'first' : null"
                    type="text"
                    :placeholder="'Enter ' + part.name + '...'"
                    class="px-3 py-2 border border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-white rounded-md shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
                  />
                </template>
              </div>

              <!-- Generated Tag Preview -->
              <div class="mt-4 p-3 bg-gray-100 dark:bg-gray-700 rounded-lg">
                <div class="text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Preview:</div>
                <code class="text-sm bg-gray-200 dark:bg-gray-600 px-3 py-2 rounded text-gray-800 dark:text-gray-200 font-mono break-all">
                  {{ generatedTag || 'Start building your tag...' }}
                </code>
                <div class="mt-2 text-xs text-gray-500 dark:text-gray-400">
                  Debug: tagBuilderParts = {{ JSON.stringify(tagBuilderParts) }}
                </div>
              </div>
            </div>
          </div>

          <!-- Action Buttons -->
          <div class="mt-6 flex justify-end gap-2">
            <button
              @click="closeCloneTagModal"
              class="px-4 py-2 bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-md hover:bg-gray-300 dark:hover:bg-gray-600 transition-colors"
            >
              Cancel
            </button>
            <!-- Show simple clone button when no capture groups -->
            <button
              v-if="!hasCaptureGroups"
              @click="cloneTag"
              :disabled="!cloneTagValidation.valid || !cloneTagName.trim()"
              class="px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
            >
              Clone Tag
            </button>
            <!-- Show tag builder clone button when has capture groups -->
            <button
              v-else
              @click="cloneTagFromBuilder"
              :disabled="!canCreateTag"
              class="px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
            >
              Clone Tag
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Copy Projects to Tag Modal -->
    <div v-if="showCopyProjectsModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-[60] p-4">
      <div class="bg-white dark:bg-gray-800 rounded-lg shadow-xl w-full max-w-2xl mx-auto max-h-[calc(100vh-2rem)] overflow-y">
        <div class="p-6">
          <div class="flex justify-between items-center mb-4">
            <h3 class="text-lg font-semibold text-gray-900 dark:text-white">
              Copy Projects from "{{ sourceTag?.name }}" to Another Tag
            </h3>
            <button
              @click="closeCopyProjectsModal"
              class="text-gray-400 hover:text-gray-600 dark:text-gray-500 dark:hover:text-gray-300"
            >
              <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>

          <!-- Source Tag Display -->
          <div class="mb-4 p-3 bg-gray-50 dark:bg-gray-700 rounded">
            <div class="text-sm text-gray-600 dark:text-gray-400 mb-1">Source Tag:</div>
            <div class="font-medium text-gray-900 dark:text-white">{{ sourceTag?.name }}</div>
          </div>

          <!-- Target Tag Selection -->
          <div class="space-y-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Select Target Tag
              </label>
              <div class="relative">
                <input
                  v-model="targetTagSearch"
                  @input="filterTargetTags"
                  @focus="showTargetTagDropdown = true"
                  @blur="hideTargetTagDropdown"
                  type="text"
                  placeholder="Search and select a tag..."
                  class="w-full px-4 py-3 text-base border border-gray-300 dark:border-gray-600 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
                />

                <!-- Dropdown for filtered tags - uses full viewport -->
                <div v-if="showTargetTagDropdown" class="absolute z-[60] w-full mt-1 bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-md shadow-lg">
                  <div class="max-h-96 overflow-y-auto">
                    <div
                      v-for="tag in filteredTargetTags"
                      :key="tag.name"
                      @click="selectTargetTag(tag)"
                      class="px-4 py-3 hover:bg-gray-100 dark:hover:bg-gray-600 cursor-pointer text-gray-900 dark:text-white border-b border-gray-100 dark:border-gray-600 last:border-b-0"
                    >
                      <div class="font-medium">{{ tag.name }}</div>
                      <span v-if="tag.projectsCount" class="text-sm text-gray-500 dark:text-gray-400">
                        {{ tag.projectsCount }} projects
                      </span>
                    </div>
                    <div v-if="filteredTargetTags.length === 0" class="px-4 py-3 text-gray-500 dark:text-gray-400">
                      No tags found
                    </div>
                  </div>
                </div>
              </div>

              <!-- Selected target tag display -->
              <div v-if="targetTag" class="mt-2 p-2 bg-blue-50 dark:bg-blue-900/20 rounded border border-blue-200 dark:border-blue-800">
                <div class="text-sm text-blue-600 dark:text-blue-400">Selected target tag:</div>
                <div class="font-medium text-blue-900 dark:text-blue-300">{{ targetTag.name }}</div>
              </div>
            </div>

            <div v-if="copyProjectsValidation.message" class="text-sm" :class="copyProjectsValidation.valid ? 'text-green-600 dark:text-green-400' : 'text-red-600 dark:text-red-400'">
              {{ copyProjectsValidation.message }}
            </div>
          </div>

          <div class="flex justify-end space-x-3 mt-6">
            <button
              @click="closeCopyProjectsModal"
              class="px-4 py-2 bg-gray-600 text-white rounded-md hover:bg-gray-700 transition-colors"
            >
              Cancel
            </button>
            <button
              @click="confirmCopyProjectsToTag"
              :disabled="!sourceTag || !targetTag"
              class="px-4 py-2 bg-teal-600 text-white rounded-md hover:bg-teal-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Copy Projects
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, nextTick, onMounted, watch } from 'vue'
import { storeToRefs } from 'pinia'
import { useTaxonomyStore } from '../stores/taxonomies'
import { useToast } from '../composables/useToast'
import { buildDTProjectUrl } from '../config.js'
import { useRouter } from 'vue-router'
import { useTagStore } from '../stores/tags.js'
import { List as ListIcon, Grid as GridIcon, Square as SquareIcon, Folder, Trash2, Edit2 } from 'lucide-vue-next'
import Vue3Datagrid, { VGridVueTemplate } from '@revolist/vue3-datagrid'
import {parseRegExpLiteral} from 'regexpp'
import axios from 'axios'

// URL encoding utility
const encodeTagName = (tagName) => {
  return encodeURIComponent(tagName)
}

export default {
  name: 'TagCenter',
  components: {
    Vue3Datagrid,
    VGridVueTemplate,
    ListIcon,
    GridIcon,
    SquareIcon,
    Folder,
    Trash2,
    Edit2
  },
  setup() {
    const router = useRouter()
    const tagStore = useTagStore()
    const taxonomyStore = useTaxonomyStore()
    const { showSuccess, showError } = useToast()

    // Use taxonomy store
    const { taxonomies, loading: taxonomiesLoading } = storeToRefs(taxonomyStore)
    const { getTaxonomyBadgeStyle, getTagTaxonomy, loadTaxonomies } = taxonomyStore

    // Use tag store
    const {
      tags,
      isLoading: tagsLoading,
      error: tagsError,
      currentPage,
      pageSize,
      totalTags,
      totalPages,
      searchQuery,
      filteredTags,
      paginatedTags,
      hasPreviousPage,
      hasNextPage
    } = storeToRefs(tagStore)

    const {
      loadTags,
      createTag,
      updateTag,
      deleteTag,
      setSearchQuery,
      setTaxonomyFilter,
      setPageSize,
      goToPage,
      nextPage,
      previousPage,
      clearFilters
    } = tagStore

    // Create Tag Modal state
    const showCreateTagModal = ref(false)
    const selectedTaxonomy = ref(null)
    const tagBuilderParts = ref([])
    const editingTag = ref(null)
    const editInput = ref(null) // Ref for edit input focus

    // Clone Tag Modal state
    const showCloneTagModal = ref(false)
    const cloningTag = ref(null)
    const cloneTagName = ref('')
    const cloneTagValidation = ref({ valid: false, message: '' })
    const linkProjects = ref(false)

    // Local state not in store
    const projects = ref([])
    const newTag = ref('')
    const tagValidation = ref({ valid: false, message: '' })
    const showProjectsModal = ref(false)
    const selectedTag = ref(null)
    const tagProjects = ref([])
    const tagsViewMode = ref('deck') // 'list', 'grid', or 'deck'
    const editingTagName = ref('')

    // Dark mode detection
    const isDarkMode = computed(() => {
      if (typeof window !== 'undefined') {
        return document.documentElement.classList.contains('dark')
      }
      return false
    })

    // Grid columns for tags grid view
    const gridColumns = computed(() => [
      {
        prop: 'taxonomy',
        name: 'Taxonomy',
        sortable: true
      },
      {
        prop: 'name',
        name: 'Tag',
        sortable: true
      },
      {
        prop: 'projectsCount',
        name: 'Projects Count',
        sortable: true
      },
      /* ,
      {
        prop: 'actions',
        name: 'Actions',
        sortable: false,
        cellTemplate: VGridVueTemplate(TagActionsCell)
      } */
    ])

    // Tag actions cell template
    const TagActionsCell = {
      template: (props) => {
        const taxonomy = props.model.taxonomy ?
          (taxonomies.value.find(t => t.id === props.model.taxonomy) ||
          { name: props.model.taxonomy }) :
          { name: 'No taxonomy' };

        return {
          template: `
            <div class="flex gap-2">
              <button @click="viewProjects" class="px-2 py-1 text-xs bg-blue-600 text-white rounded hover:bg-blue-700">View</button>
              <button @click="removeTag" class="px-2 py-1 text-xs bg-red-600 text-white rounded hover:bg-red-700">Delete</button>
            </div>
          `,
          methods: {
            viewProjects: () => {
              // Emit event to parent or call directly
              console.log('View projects for tag:', props.model.name)
            },
            edit: () => {
              console.log('Edit tag:', props.model.name)
            },
            removeTag: () => {
              console.log('Delete tag:', props.model.name)
            }
          }
        }
      }
    }

    // Methods
    const loadProjects = async () => {
      try {
        // Load projects from DT API directly
        const response = await axios.get('/api/v1/project')

        projects.value = response.data.map(project => ({
          id: project.uuid, // Use uuid as id
          uuid: project.uuid,
          name: project.name,
          version: project.version,
          displayName: project.version ? `${project.name}:${project.version}` : `${project.name}`,
          tags: project.tags || []
        }))
      } catch (error) {
        console.error('Error loading projects:', error)
        projects.value = []
      }
    }

    const validateTag = () => {
      if (!newTag.value.trim()) {
        tagValidation.value = { valid: false, message: 'Tag is required' }
        return
      }

      const tag = newTag.value.trim()

      // Check for duplicates first
      if (tags.value.some(existing => existing.name === tag)) {
        tagValidation.value = {
          valid: false,
          message: '❌ Tag already exists'
        }
        return
      }

      // Check if tag matches any taxonomy regex_patternattern
      const matchingTaxonomy = taxonomies.value.find(taxonomy => {
        try {
          // Use native RegExp for JS regex compatibility
          const regex = new RegExp(taxonomy.regex_pattern)
          const matches = regex.test(tag)
          return matches
        } catch (error) {
          console.error('Invalid regex regex_pattern:', taxonomy.regex_pattern, error)
          return false
        }
      })

      if (matchingTaxonomy) {
        tagValidation.value = {
          valid: true,
          message: `✅ Matches ${matchingTaxonomy.name} taxonomy (${matchingTaxonomy.id})`
        }
      } else {
        tagValidation.value = {
          valid: true,
          message: '✅ Custom tag'
        }
      }
    }

    const selectSuggestedTag = (tag) => {
      newTag.value = tag
      validateTag()
    }

    const handleCreateTag = async () => {
      if (!tagValidation.value.valid || !newTag.value.trim()) return

      try {
        const response = await tagStore.createTag({
          name: newTag.value.trim()
        })

        if (response) {
          // Add new tag to our list
          tags.value.push(response)
          newTag.value = ''
          tagValidation.value = { valid: false, message: '' }
          // Close the modal after successful creation
          showCreateTagModal.value = false
        }
      } catch (error) {
        console.error('Error creating tag:', error)
        tagValidation.value = {
          valid: false,
          message: `❌ Error: ${tagStore.error || error.message}`
        }
      }
    }


    const handleDeleteTag = async (tag) => {
      if (!confirm(`Are you sure you want to delete tag "${tag.name}"?`)) return

      try {
        await axios.delete(`/api/tag/${encodeTagName(tag.name)}`)

        // Remove the tag from our list
        const index = tags.value.findIndex(t => t.name === tag.name)
        if (index > -1) {
          tags.value.splice(index, 1)
          showSuccess('Tag deleted successfully')
        }
      } catch (error) {
        console.error('Error deleting tag:', error)
        showError('Failed to delete tag', 'Please try again.')
      }
    }

    const viewTagProjects = async (tag) => {
      selectedTag.value = tag
      showProjectsModal.value = true

      try {
        const response = await axios.get(`/api/tag/${encodeTagName(tag.name)}/project`)
        tagProjects.value = response.data
      } catch (error) {
        console.error('Error loading tag projects:', error)
        tagProjects.value = []
      }
    }

    const closeProjectsModal = () => {
      showProjectsModal.value = false
      selectedTag.value = null
      tagProjects.value = []
    }

    const clearForm = () => {
      newTag.value = ''
      tagValidation.value = { valid: false, message: '' }
    }


    const refreshTags = () => {
      loadTags()
      loadProjects()
    }

    const formatDate = (dateString) => {
      return new Date(dateString).toLocaleString()
    }

    // Clone Tag functionality
    const startCloneTag = async (tag) => {
      console.log('🔧 Clone Tag clicked for tag:', tag)
      cloningTag.value = tag
      cloneTagName.value = ''
      cloneTagValidation.value = { valid: false, message: '' }
      linkProjects.value = false

      // Initialize tag builder if tag has taxonomy
      if (tag.taxonomy) {
        try {
          console.log('🔧 Available taxonomies:', taxonomies.value.map(t => ({ name: t.name, id: t.id })))
          console.log('🔧 Available taxonomy names:', taxonomies.value.map(t => `'${t.name}'`).join(', '))
          console.log('🔧 Looking for taxonomy:', `'${tag.taxonomy}'`)
          console.log('🔧 Tag taxonomy type:', typeof tag.taxonomy)
          console.log('🔧 Tag taxonomy length:', tag.taxonomy.length)

          // Find the taxonomy object by ID (since tag.taxonomy contains the ID, not the name)
          const taxonomy = taxonomies.value.find(t => t.id === tag.taxonomy)
          if (!taxonomy) {
            console.error('Taxonomy not found by ID:', tag.taxonomy)
            // Try finding by name as fallback
            const taxonomyByName = taxonomies.value.find(t => t.name === tag.taxonomy)
            if (taxonomyByName) {
              console.log('🔧 Found taxonomy by name instead:', taxonomyByName)
              // Use the found taxonomy and proceed with the same logic
              selectedTaxonomy.value = taxonomyByName // Set selectedTaxonomy for parseTaxonomyPattern
              const parts = parseTaxonomyPattern(taxonomyByName.regex_pattern)
              await loadTagValuesForDropdowns(parts)
              const regex = new RegExp(taxonomyByName.regex_pattern)
              const match = tag.name.match(regex)

              if (match) {
                tagBuilderParts.value = parts.map((part) => {
                  if (part.type === 'static') {
                    return part
                  } else if (part.type === 'dropdown' || part.type === 'text') {
                    const currentValue = match.groups?.[part.name] || ''
                    return {
                      ...part,
                      value: currentValue
                    }
                  }
                  return part
                })
              } else {
                tagBuilderParts.value = parts
              }
              console.log('🔧 Clone tag builder initialized (fallback):', tagBuilderParts.value)
            } else {
              tagBuilderParts.value = []
            }
          } else {
            console.log('🔧 Found taxonomy by ID:', taxonomy)
            // Set selectedTaxonomy for parseTaxonomyPattern to use
            selectedTaxonomy.value = taxonomy
            // Parse taxonomy pattern to extract parts
            const parts = parseTaxonomyPattern(taxonomy.regex_pattern)

            // Load dropdown options for parts
            await loadTagValuesForDropdowns(parts)

            // Parse the original tag to pre-populate values
            const regex = new RegExp(taxonomy.regex_pattern)
            console.log('🔧 Regex pattern:', taxonomy.regex_pattern)
            console.log('🔧 Testing against tag:', tag.name)
            const match = tag.name.match(regex)
            console.log('🔧 Regex match result:', match)

            if (match) {
              console.log('🔧 Match groups:', match.groups)
              console.log('🔧 Parts before mapping:', parts)
              // Pre-populate tag builder parts with original tag values
              tagBuilderParts.value = parts.map((part) => {
                if (part.type === 'static') {
                  return part
                } else if (part.type === 'dropdown' || part.type === 'text') {
                  // Use named capture group value from match.groups
                  const currentValue = match.groups?.[part.name] || ''
                  console.log(`🔧 Setting ${part.name} to: "${currentValue}"`)
                  return {
                    ...part,
                    value: currentValue
                  }
                }
                return part
              })
              console.log('🔧 Tag builder parts after mapping:', tagBuilderParts.value)
            } else {
              // If no match, just load empty parts with dropdown options
              tagBuilderParts.value = parts
            }

            console.log('🔧 Clone tag builder initialized:', tagBuilderParts.value)
          }

          console.log('🔧 Clone tag builder initialized:', tagBuilderParts.value)
        } catch (error) {
          console.error('Error initializing clone tag builder:', error)
          tagBuilderParts.value = []
        }
      } else {
        // Clear tag builder if no taxonomy
        tagBuilderParts.value = []
      }

      showCloneTagModal.value = true

      // Focus the first field after modal opens
      nextTick(() => {
        if (!hasCaptureGroups.value) {
          // Focus simple text input
          const input = document.querySelector('[data-clone-tag-input]')
          if (input) {
            input.focus()
          }
        } else {
          // Focus first tag builder field
          const firstField = document.querySelector('[data-tag-builder-field="first"]')
          if (firstField) {
            firstField.focus()
          }
        }
      })
    }

    const validateCloneTag = () => {
      const tagName = cloneTagName.value.trim()

      if (!tagName) {
        cloneTagValidation.value = { valid: false, message: 'Tag name is required' }
        return
      }

      // Check if tag already exists
      if (tags.value.some(t => t.name === tagName)) {
        cloneTagValidation.value = { valid: false, message: 'Tag already exists' }
        return
      }

      cloneTagValidation.value = { valid: true, message: 'Tag name is valid' }
    }

    const closeCloneTagModal = () => {
      showCloneTagModal.value = false
      cloningTag.value = null
      cloneTagName.value = ''
      cloneTagValidation.value = { valid: false, message: '' }
      linkProjects.value = false
    }

    // Copy Projects to Tag functionality
    const showCopyProjectsModal = ref(false)
    const sourceTag = ref(null)
    const targetTag = ref(null)
    const copyProjectsValidation = ref({ valid: false, message: '' })

    // Searchable dropdown state
    const targetTagSearch = ref('')
    const showTargetTagDropdown = ref(false)
    const filteredTargetTags = ref([])

    const filterTargetTags = () => {
      const searchTerm = targetTagSearch.value.toLowerCase()
      const sourceTagName = sourceTag.value?.name || ''

      filteredTargetTags.value = tags.value.filter(tag => {
        const isNotSourceTag = tag.name !== sourceTagName
        const matchesSearch = tag.name.toLowerCase().includes(searchTerm)
        return isNotSourceTag && matchesSearch
      })
    }

    const selectTargetTag = (tag) => {
      targetTag.value = tag
      targetTagSearch.value = tag.name
      showTargetTagDropdown.value = false
    }

    const hideTargetTagDropdown = () => {
      // Delay hiding to allow click events to register
      setTimeout(() => {
        showTargetTagDropdown.value = false
      }, 200)
    }

    const startCopyProjectsToTag = (tag) => {
      console.log('🔗 Starting copy projects to tag for:', tag)
      // Handle both reactive proxy and regular objects
      const tagObj = tag.name ? tag : { name: tag, taxonomy: tag.taxonomy, projectsCount: tag.projectsCount }
      sourceTag.value = tagObj
      targetTag.value = null
      targetTagSearch.value = ''
      copyProjectsValidation.value = { valid: true, message: '' }
      showCopyProjectsModal.value = true

      // Initialize filtered tags
      filterTargetTags()
    }

    const confirmCopyProjectsToTag = async () => {
      if (!sourceTag.value || !targetTag.value) {
        copyProjectsValidation.value = { valid: false, message: 'Please select a target tag' }
        return
      }

      // Handle both reactive proxy and regular objects
      const sourceTagName = sourceTag.value.name ? sourceTag.value.name : sourceTag.value
      const targetTagName = targetTag.value.name ? targetTag.value.name : targetTag.value

      if (sourceTagName === targetTagName) {
        copyProjectsValidation.value = { valid: false, message: 'Cannot copy projects to the same tag' }
        return
      }

      try {
        // Get all projects that have the source tag
        const sourceTagProjects = await axios.get(`/api/tag/${encodeURIComponent(sourceTagName)}/project`)
        const projectsToCopy = sourceTagProjects.data || []

        if (projectsToCopy.length === 0) {
          copyProjectsValidation.value = { valid: false, message: 'No projects found to copy' }
          return
        }

        // Use the generic proxy endpoint to add target tag to all projects
        await axios.post(`/api/v1/tag/${encodeURIComponent(targetTagName)}/project`, projectsToCopy.map(project => project.uuid))

        showSuccess(`Successfully copied ${projectsToCopy.length} projects from "${sourceTagName}" to "${targetTagName}"`)
        closeCopyProjectsModal()
        await loadTags() // Refresh tags to update project counts
      } catch (error) {
        console.error('Error copying projects:', error)
        copyProjectsValidation.value = {
          valid: false,
          message: `❌ Error: ${error.response?.data?.message || error.message || 'Unknown error'}`
        }
      }
    }

    const closeCopyProjectsModal = () => {
      showCopyProjectsModal.value = false
      sourceTag.value = null
      targetTag.value = null
      targetTagSearch.value = ''
      showTargetTagDropdown.value = false
      copyProjectsValidation.value = { valid: false, message: '' }
    }

    const cloneTagFromBuilder = async () => {
      if (!canCreateTag.value || !generatedTag.value) {
        return
      }

      try {
        const newTagName = generatedTag.value

        // Create new tag
        const response = await tagStore.createTag({
          name: newTagName
        })

        if (response) {
          // Add new tag to our list
          tags.value.push(response)

          // If linking projects is enabled, get projects from original tag and link them
          if (linkProjects.value && cloningTag.value && cloningTag.value.projectsCount > 0) {
            try {
              const projectsResponse = await axios.get(`/api/tag/${encodeTagName(cloningTag.value.name)}/project`)
              const projects = projectsResponse.data

              if (projects && projects.length > 0) {
                // Link each project to new tag using the correct DT API endpoint
                const projectUuids = projects.map(p => p.uuid)
                await axios.post(`/api/v1/tag/${encodeTagName(newTagName)}/project`, projectUuids)

                showSuccess(`Tag "${newTagName}" created and linked to ${projects.length} projects`)
              } else {
                showSuccess(`Tag "${newTagName}" created successfully`)
              }
            } catch (error) {
              console.error('Error linking projects:', error)
              showSuccess(`Tag "${newTagName}" created but failed to link some projects`)
            }
          } else {
            showSuccess(`Tag "${newTagName}" created successfully`)
          }

          // Close modal and refresh tags
          closeCloneTagModal()
          await loadTags()
        }
      } catch (error) {
        console.error('Error cloning tag:', error)
        showError('Failed to clone tag', 'Please try again.')
      }
    }

    const cloneTag = async () => {
      if (!cloneTagValidation.value.valid || !cloneTagName.value.trim()) {
        return
      }

      try {
        const newTagName = cloneTagName.value.trim()

        // Create the new tag
        const response = await tagStore.createTag({
          name: newTagName
        })

        if (response) {
          // Add new tag to our list
          tags.value.push(response)

          // If linking projects is enabled, get projects from original tag and link them
          if (linkProjects.value && cloningTag.value && cloningTag.value.projectsCount > 0) {
            try {
              const projectsResponse = await axios.get(`/api/tag/${encodeTagName(cloningTag.value.name)}/project`)
              const projects = projectsResponse.data

              if (projects && projects.length > 0) {
                // Link each project to new tag using the correct DT API endpoint
                const projectUuids = projects.map(p => p.uuid)
                await axios.post(`/api/v1/tag/${encodeTagName(newTagName)}/project`, projectUuids)

                showSuccess(`Tag "${newTagName}" created and linked to ${projects.length} projects`)
              } else {
                showSuccess(`Tag "${newTagName}" created successfully`)
              }
            } catch (error) {
              console.error('Error linking projects:', error)
              showSuccess(`Tag "${newTagName}" created but failed to link some projects`)
            }
          } else {
            showSuccess(`Tag "${newTagName}" created successfully`)
          }

          // Close modal and refresh tags
          closeCloneTagModal()
          await loadTags()
        }
      } catch (error) {
        console.error('Error cloning tag:', error)
        cloneTagValidation.value = {
          valid: false,
          message: `❌ Error: ${tagStore.error || error.message}`
        }
      }
    }

    // Edit tag functionality
    const startEditTag = (tag) => {
      console.log('🔧 Starting edit for tag:', tag)

      editingTag.value = tag
      editingTagName.value = tag.name

      // focus the editor after DOM update using Vue refs
      nextTick(() => {
        // Try multiple approaches to find and focus the input
        const attempts = [
          () => document.querySelector(`input[data-tag-name="${tag.name}"]`),
          () => document.querySelector(`input[data-tag-name="${tag.name}"]`),
          () => document.querySelector('input[data-tag-name="' + tag.name + '"]')
        ]

        for (const attempt of attempts) {
          const input = attempt()
          if (input) {
            input.focus()
            // input.select()
            return
          }
        }

        console.log('🔧 Input not found, trying alternative approach')
      })
    }

    const cancelEditTag = () => {
      editingTag.value = null
      editingTagName.value = ''
    }

    const saveEditTag = async () => {
      if (!editingTag.value || !editingTagName.value.trim()) {
        return
      }

      try {
        await axios.put(`/api/tag/${encodeTagName(editingTag.value.name)}`, {
          name: editingTagName.value.trim()
        })

        // Update the tag in the local state
        const tagIndex = tags.value.findIndex(t => t.name === editingTag.value.name)
        if (tagIndex !== -1) {
          tags.value[tagIndex].name = editingTagName.value.trim()
        }

        // Reset editing state
        editingTag.value = null
        editingTagName.value = ''
        showSuccess('Tag updated successfully')
      } catch (error) {
        console.error('Error updating tag:', error)
        showError('Failed to update tag', 'Please try again.')
      }
    }

    // Lifecycle
    onMounted(() => {
      loadTaxonomies()
      loadTags()
      loadProjects()
    })

    // Computed properties for tag creation
    const generatedTag = computed(() => {
      if (!tagBuilderParts.value.length) return ''
      return tagBuilderParts.value.map(part => {
        if (part.type === 'static') return part.value
        return part.value || ''
      }).join('')
    })

    const canCreateTag = computed(() => {
      const taxonomy = taxonomies.value.find(t => t.id === cloningTag.value?.taxonomy)
      // check that generatedTag is compatible with the tag pattern
      return generatedTag.value.length > 0 && taxonomy && new RegExp(taxonomy.regex_pattern).test(generatedTag.value)
    })

    // Check if tag has capture groups (for showing simple vs advanced clone)
    const hasCaptureGroups = computed(() => {
      return tagBuilderParts.value.some(part =>
        part.type === 'text' || part.type === 'dropdown'
      )
    })

    // Methods for aided editing
    const tagBelongsToTaxonomy = (tag) => {
      return tag.taxonomy && tag.taxonomy.trim() !== ''
    }

    const startAidedEditTag = async (tag) => {
      console.log('🔧 Aided Edit clicked for tag:', tag)
      console.log('🔧 Current tagBuilderParts before Aided Edit:', tagBuilderParts.value)
      try {
        // Find taxonomy that matches this tag pattern
        const matchingTaxonomy = taxonomies.value.find(taxonomy => {
          const regex = new RegExp(taxonomy.regex_pattern)
          return regex.test(tag.name)
        })

        console.log('🔧 Matching taxonomy:', matchingTaxonomy)

        if (!matchingTaxonomy) {
          showError('No matching taxonomy found for this tag')
          return
        }

        selectedTaxonomy.value = matchingTaxonomy
        editingTag.value = tag

        console.log('🔧 Set selectedTaxonomy and editingTag')

        // Parse the tag using the taxonomy pattern to pre-populate fields
        const regex = new RegExp(matchingTaxonomy.regex_pattern)
        const match = tag.name.match(regex)

        console.log('🔧 Regex match result:', match)

        if (match) {
          // Parse taxonomy pattern to extract parts
          const parts = parseTaxonomyPattern(matchingTaxonomy.regex_pattern)

          console.log('🔧 Parsed parts:', parts)

          // Load dropdown options for parts
          await loadTagValuesForDropdowns(parts)

          // Pre-populate tag builder parts with existing tag values
          tagBuilderParts.value = parts.map((part) => {
            if (part.type === 'static') {
              return part
            } else if (part.type === 'dropdown' || part.type === 'text') {
              // Use the named capture group value from match.groups
              const currentValue = match.groups?.[part.name] || ''
              return {
                ...part,
                value: currentValue
              }
            }
            return part
          })

          console.log('🔧 Final tagBuilderParts:', tagBuilderParts.value)
        } else {
          // If no match, just load empty parts with dropdown options
          const parts = parseTaxonomyPattern(matchingTaxonomy.regex_pattern)
          await loadTagValuesForDropdowns(parts)
          tagBuilderParts.value = parts
        }

        showCreateTagModal.value = true
        console.log('🔧 Modal should be open now')
      } catch (error) {
        console.error('Error starting aided edit:', error)
        showError('Failed to open edit modal')
      }
    }

    const parseTaxonomyPattern = (pattern) => {
      const parts = []

      // use regexpp to process the regex pattern in a semantic fashion so that the parts are properly extracted
      // i.e. this pattern '/^(?!(?:notThis|notThat):)(?<grpA>[\\w-]+):(?<grpB>[\\d\\w\\.-]+)$/'
      // becomes [{type: 'static'}, {type: 'text', value: ':'}, {type: 'group', name: 'grpA', ...}, {type: 'static', value: ':'}, {type: 'group', name: 'grpB', ...}]
      const ast = parseRegExpLiteral(`/${pattern}/`);

      // The 'alternatives' array contains the top-level branches of the regex
      // We assume a single path for this specific use case
      const elements = ast.pattern.alternatives[0].elements;

      elements.forEach(node => {
        // Process each node and build the parts array
        switch (node.type) {
            case "CapturingGroup":
                parts.push({
                    type: 'group',
                    name: node.name // This is the 'grpA' or 'grpB'
                });
                // Check if this capture group has a corresponding relation
                const hasRelation = selectedTaxonomy.value?.relations?.some(rel => rel.group === node.name)

                // Add capture group part
                parts.push({
                  type: hasRelation ? 'dropdown' : 'text', // Use dropdown only if relation exists
                  name: node.name,
                  value: '',
                  options: [],
                  pattern: node.pattern
                })
                break;

            case "Character":
                // add a new static part if previous one wasn't static, otherwise append to the previous
                if (parts.length > 0 && parts[parts.length - 1].type === 'static') {
                    parts[parts.length - 1].value += String.fromCodePoint(node.value)
                } else {
                    parts.push({
                        type: 'static',
                        value: String.fromCodePoint(node.value)
                    })
                }
                break;

            case "CharacterClass":
            case "CharacterSet":
                // These represent things like [\w-] or \d
                // For "generate" logic, you likely treat these as static placeholders
                // or templates rather than literal strings.
                parts.push({
                    type: 'text',
                    value: node.raw
                });
                break;

            case "Assertion":
                // Handles ^, $, lookaheads, etc.
                // We mark them as static/meta or ignore them for generation logic.
                if (node.kind === "lookahead" || node.kind === "lookbehind") {
                    // You could recurse here if you need to find groups inside lookarounds
                    parts.push({ type: 'assertion', kind: node.kind, raw: node.raw });
                }
                break;

            default:
                // Handle Quantifiers (+, *) or other types if necessary
                break;
        }
      })


      return parts
    }

    const loadTagValuesForDropdowns = async (parts) => {
      for (const part of parts) {
        if (part.type === 'dropdown' && part.name) {
          // For associative taxonomies get tags from related taxonomies
          if (selectedTaxonomy.value.relations && selectedTaxonomy.value.relations.length > 0) {
            // Find related taxonomy for this part
            const relation = selectedTaxonomy.value.relations.find(rel => rel.group === part.name)
            if (relation && relation.targets) {
              const targetTaxonomyId = relation.targets

              // Get tags from related taxonomy
              const response = await axios.get(`/api/taxonomies/${targetTaxonomyId}/tag`)
              const relatedTags = response.data || []

              // Add to dropdown options
              part.options = relatedTags.map(tag => ({
                value: tag.name,
                text: tag.name
              })).filter(Boolean)
            }
          }
        }
      }
    }

    const closeCreateTagModal = () => {
      showCreateTagModal.value = false
      selectedTaxonomy.value = null
      tagBuilderParts.value = []
      editingTag.value = null
    }

    const createOrUpdateTag = async () => {
      if (!canCreateTag.value || !generatedTag.value) return

      try {
        if (editingTag.value) {
          // Update existing tag (Aided Edit mode)
          if (!selectedTaxonomy.value) {
            showError('No taxonomy selected for editing')
            return
          }

          await axios.put(`/api/tag/${encodeTagName(editingTag.value.name)}`, {
            name: generatedTag.value,
            taxonomy_id: selectedTaxonomy.value.id
          })
          showSuccess(`Tag "${generatedTag.value}" updated successfully!`)
        } else {
          // Create new tag (regular Create mode)
          const response = await tagStore.createTag({
            name: generatedTag.value
          })

          if (response) {
            // Add new tag to our list
            tags.value.push(response)
            newTag.value = ''
            tagValidation.value = { valid: false, message: '' }
          }
        }

        // Close modal after successful operation
        closeCreateTagModal()
      } catch (error) {
        console.error('Error creating/updating tag:', error)
        showError('Failed to save tag')
      }
    }

    return {
      // Tag store state
      tags,
      tagsLoading,
      tagsError,
      currentPage,
      pageSize,
      totalTags,
      totalPages,
      searchQuery,
      filteredTags,
      paginatedTags,
      hasPreviousPage,
      hasNextPage,

      // Tag store methods
      loadTags,
      setSearchQuery,
      setTaxonomyFilter,
      setPageSize,
      goToPage,
      nextPage,
      previousPage,
      clearFilters,

      // Local state
      projects,
      newTag,
      tagValidation,
      showProjectsModal,
      selectedTag,
      tagProjects,
      tagsViewMode,
      showCreateTagModal,
      editingTag,
      editingTagName,

      // Copy Projects to Tag state
      showCopyProjectsModal,
      sourceTag,
      targetTag,
      copyProjectsValidation,
      targetTagSearch,
      showTargetTagDropdown,
      filteredTargetTags,
      startCopyProjectsToTag,
      confirmCopyProjectsToTag,
      closeCopyProjectsModal,
      filterTargetTags,
      selectTargetTag,
      hideTargetTagDropdown,

      // Taxonomy store functions
      taxonomies,
      getTagTaxonomy,
      getTaxonomyBadgeStyle,
      // Clone Tag state
      showCloneTagModal,
      cloningTag,
      cloneTagName,
      cloneTagValidation,
      linkProjects,
      isDarkMode,
      gridColumns,
      validateTag,
      selectSuggestedTag,
      handleCreateTag,
      handleDeleteTag,
      clearForm,
      viewTagProjects,
      startEditTag,
      startAidedEditTag,
      startCloneTag,
      validateCloneTag,
      cloneTag,
      cloneTagFromBuilder,
      closeCloneTagModal,
      tagBelongsToTaxonomy,
      cancelEditTag,
      saveEditTag,
      refreshTags,
      formatDate,
      closeProjectsModal,
      buildDTProjectUrl,

      // Tag store state
      tags,
      tagsLoading,
      tagsError,
      currentPage,
      pageSize,
      totalTags,
      totalPages,
      searchQuery,
      filteredTags,
      paginatedTags,
      hasPreviousPage,
      hasNextPage,

      // Tag store methods
      loadTags,
      setSearchQuery,
      setTaxonomyFilter,
      setPageSize,
      goToPage,
      nextPage,
      previousPage,
      clearFilters,

      // Local state
      projects,
      newTag,
      tagValidation,
      showProjectsModal,
      selectedTag,
      tagProjects,
      tagsViewMode,
      showCreateTagModal,
      editingTag,
      editingTagName,

      // Taxonomy store functions
      taxonomies,
      getTagTaxonomy,
      getTaxonomyBadgeStyle,
      selectedTaxonomy,

      // Clone Tag state
      showCloneTagModal,
      cloningTag,
      cloneTagName,
      cloneTagValidation,
      linkProjects,

      // Other functions
      isDarkMode,
      gridColumns,
      validateTag,
      selectSuggestedTag,
      handleCreateTag,
      handleDeleteTag,
      clearForm,
      viewTagProjects,
      startEditTag,
      startAidedEditTag,
      startCloneTag,
      validateCloneTag,
      cloneTag,
      cloneTagFromBuilder,
      closeCloneTagModal,
      tagBelongsToTaxonomy,
      cancelEditTag,
      saveEditTag,
      refreshTags,
      formatDate,
      closeProjectsModal,
      createOrUpdateTag,
      parseTaxonomyPattern,
      loadTagValuesForDropdowns,
      buildDTProjectUrl
    }
  }
}
</script>
