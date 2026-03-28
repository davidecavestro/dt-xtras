<template>
  <div class="px-4 py-6 sm:px-0">
    <!-- Row 1: Tree (1/3) + Selected Node + Related Projects (2/3) -->
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <!-- Tree Panel (1/3) -->
      <div class="bg-white dark:bg-gray-800 shadow overflow-hidden sm:rounded-md">
        <div class="p-4 border-b border-gray-200 dark:border-gray-700">
          <div class="flex justify-between items-center mb-3">
            <h3 class="text-lg font-medium text-gray-900 dark:text-white">Navigation Tree</h3>
            <button
              @click="clearSelection"
              v-if="selectedTreeNode"
              class="text-xs px-2 py-1 bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-300 rounded hover:bg-gray-200 dark:hover:bg-gray-600"
            >
              Clear Selection
            </button>
          </div>
          <input
            v-model="searchQuery"
            placeholder="Search tags, projects..."
            class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
          />
        </div>
        
        <div class="p-4 max-h-96 overflow-y-auto">
          <div v-if="loading" class="text-center py-4">
            <div class="inline-block animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600"></div>
          </div>
          
          <div v-else-if="treeData.length === 0" class="text-center py-4 text-gray-500 dark:text-gray-400">
            No tree data available
          </div>
          
          <div v-else class="space-y-1">
            <TreeNode
              v-for="node in filteredTreeData"
              :key="node.id"
              :node="node"
              :selected-node="selectedTreeNode"
              :expanded-nodes="expandedNodes"
              :search-query="searchQuery"
              @select="selectTreeNode"
              @toggle="toggleTreeNode"
            />
          </div>
        </div>
      </div>

      <!-- Selected Node + Related Projects (2/3) -->
      <div v-if="selectedTreeNode" class="bg-white dark:bg-gray-800 shadow overflow-hidden sm:rounded-md">
        <div class="p-4">
          <!-- Selected Node Info -->
          <h4 class="text-sm font-medium text-gray-900 dark:text-white mb-2">Selected Node</h4>
          <div class="text-xs text-gray-600 dark:text-gray-400 space-y-1 mb-4">
            <div><strong>Type:</strong> {{ selectedTreeNode.type }}</div>
            <div><strong>Name:</strong> {{ selectedTreeNode.name }}</div>
            <div v-if="selectedTreeNode.projectsCount !== undefined">
              <strong>Projects:</strong> {{ selectedTreeNode.projectsCount }}
            </div>
          </div>
          
          <!-- Related Projects -->
          <div class="border-t border-gray-200 dark:border-gray-700 pt-4">
            <h3 class="text-lg leading-6 font-medium text-gray-900 dark:text-white mb-4">Related Projects</h3>
            <div class="text-sm text-gray-600 dark:text-gray-400 mb-4">
              {{ relatedProjects.length }} projects found for "{{ selectedTreeNode.name }}"
            </div>
            
            <!-- Projects List -->
            <div v-if="relatedProjects.length === 0" class="text-center py-8">
              <FolderOpen class="mx-auto h-12 w-12 text-gray-400" />
              <h3 class="mt-2 text-sm font-medium text-gray-900 dark:text-white">No related projects found</h3>
              <p class="mt-1 text-sm text-gray-500 dark:text-gray-400">
                Try selecting a different node or check your connections.
              </p>
            </div>
            
            <div v-else class="max-h-96 overflow-y-auto space-y-2">
              <div 
                v-for="project in relatedProjects" 
                :key="project.uuid"
                class="p-3 bg-white dark:bg-gray-800 rounded hover:bg-gray-100 dark:hover:bg-gray-600 cursor-pointer border border-gray-200 dark:border-gray-600"
              >
                <div class="flex justify-between items-start mb-2">
                  <div class="flex-1">
                    <div class="text-sm font-medium text-gray-900 dark:text-white">{{ project.name }}</div>
                    <div class="text-xs text-gray-500 dark:text-gray-400">{{ project.version || 'latest' }}</div>
                  </div>
                  <div class="text-right">
                    <div class="text-xs text-gray-500 dark:text-gray-400">
                      {{ project.tags.join(', ') }}
                    </div>
                  </div>
                </div>
                
                <!-- Security Info -->
                <div v-if="project.metrics" class="flex flex-wrap gap-2 text-xs">
                  <span v-if="project.metrics.critical > 0" class="px-2 py-1 bg-red-100 dark:bg-red-900 text-red-800 dark:text-red-200 rounded">
                    🔴 {{ project.metrics.critical }} Critical
                  </span>
                  <span v-if="project.metrics.high > 0" class="px-2 py-1 bg-orange-100 dark:bg-orange-900 text-orange-800 dark:text-orange-200 rounded">
                    🟠 {{ project.metrics.high }} High
                  </span>
                  <span v-if="project.metrics.medium > 0" class="px-2 py-1 bg-yellow-100 dark:bg-yellow-900 text-yellow-800 dark:text-yellow-200 rounded">
                    🟡 {{ project.metrics.medium }} Medium
                  </span>
                  <span v-if="project.metrics.low > 0" class="px-2 py-1 bg-blue-100 dark:bg-blue-900 text-blue-800 dark:text-blue-200 rounded">
                    🔵 {{ project.metrics.low }} Low
                  </span>
                  <span v-if="getProjectVulnerabilities(project.metrics) === 0" class="px-2 py-1 bg-green-100 dark:bg-green-900 text-green-800 dark:text-green-200 rounded">
                    ✅ No Vulnerabilities
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Row 2: Security Dashboard (3/3) -->
    <div class="bg-white dark:bg-gray-800 shadow overflow-hidden sm:rounded-md">
      <div class="flex justify-between items-center mb-6 p-6">
        <div>
          <h2 class="text-2xl font-bold text-gray-900 dark:text-white">Security Dashboard</h2>
          <p v-if="selectedTreeNode" class="text-sm text-gray-600 dark:text-gray-400 mt-1">
            Filtered by: {{ selectedTreeNode.name }} ({{ selectedTreeNode.type }})
          </p>
        </div>
        <button
          @click="refreshData"
          :disabled="loading"
          class="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 flex items-center gap-2"
        >
          <RefreshCw v-if="loading" class="animate-spin w-4 h-4" />
          <span v-else>Refresh</span>
        </button>
      </div>

      <div v-if="loading" class="text-center py-8">
        <div class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        <p class="mt-2 text-gray-600 dark:text-gray-400">Loading security data...</p>
      </div>

      <div v-else-if="error" class="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-md p-4">
        <div class="flex items-center">
          <AlertCircle class="h-5 w-5 text-red-400" />
          <div class="ml-3">
            <h3 class="text-sm font-medium text-red-800 dark:text-red-200">Error loading data</h3>
            <div class="mt-2 text-sm text-red-700 dark:text-red-300">{{ error }}</div>
          </div>
        </div>
      </div>

      <div v-else-if="!filteredSecurityData || filteredSecurityData.length === 0" class="text-center py-8">
        <div class="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
        <h3 class="mt-2 text-sm font-medium text-gray-900 dark:text-white">No security data available</h3>
        <p class="mt-1 text-gray-600 dark:text-gray-400">Try adjusting your filters or check your connection.</p>
      </div>

      <div v-else class="px-4 py-5 sm:px-6">
        <!-- Security Overview -->
        <div class="flex justify-between items-center mb-6">
          <h3 class="text-lg leading-6 font-medium text-gray-900 dark:text-white">Security Overview</h3>
          <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <div class="bg-blue-50 dark:bg-blue-900/20 p-4 rounded-lg">
              <div class="text-center">
                <div class="text-3xl font-bold text-blue-600 dark:text-blue-300">{{ totalVulnerabilities }}</div>
                <div class="text-sm text-blue-600 dark:text-blue-400">Total Vulnerabilities</div>
              </div>
            </div>

            <div class="bg-orange-50 dark:bg-orange-900/20 p-4 rounded-lg">
              <div class="text-center">
                <div class="text-3xl font-bold text-orange-600 dark:text-orange-300">{{ criticalVulns }}</div>
                <div class="text-sm text-orange-600 dark:text-orange-400">Critical</div>
              </div>
            </div>

            <div class="bg-red-50 dark:bg-red-900/20 p-4 rounded-lg">
              <div class="text-center">
                <div class="text-3xl font-bold text-red-600 dark:text-red-300">{{ highVulns }}</div>
                <div class="text-sm text-red-600 dark:text-red-400">High</div>
              </div>
            </div>

            <div class="bg-yellow-50 dark:bg-yellow-900/20 p-4 rounded-lg">
              <div class="text-center">
                <div class="text-3xl font-bold text-yellow-600 dark:text-yellow-300">{{ mediumVulns }}</div>
                <div class="text-sm text-yellow-600 dark:text-yellow-400">Medium</div>
              </div>
            </div>

            <div class="bg-green-50 dark:bg-green-900/20 p-4 rounded-lg">
              <div class="text-center">
                <div class="text-3xl font-bold text-green-600 dark:text-green-300">{{ lowVulns }}</div>
                <div class="text-sm text-green-600 dark:text-green-400">Low</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
